import csv,io,json,os,sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime,timezone
from app.models import Adjudication,AnnotationCorrection,AnnotationCreate,Codebook,Item
from dotenv import load_dotenv

load_dotenv()
DB_PATH=Path(os.getenv("DATABASE_PATH","./annotation-qa.db"))
DEFAULT_CODEBOOK={"version":"1.0","definitions":{"correct":"Answer is accurate and supported.","incorrect":"Answer contains a material error.","incomplete":"Answer omits requested or necessary information.","misleading":"Answer is technically plausible but creates a false impression or omits critical context.","ambiguous":"Available context does not support a single confident label."}}

@contextmanager
def db():
    DB_PATH.parent.mkdir(parents=True,exist_ok=True);c=sqlite3.connect(DB_PATH);c.row_factory=sqlite3.Row
    try:yield c;c.commit()
    except Exception:c.rollback();raise
    finally:c.close()

def now():return datetime.now(timezone.utc).isoformat()
def initialize():
    with db() as c:
        c.execute("PRAGMA foreign_keys=ON")
        c.executescript("""CREATE TABLE IF NOT EXISTS items(record_id TEXT PRIMARY KEY,content TEXT NOT NULL,category TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS codebooks(version TEXT PRIMARY KEY,definitions_json TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS annotations(id INTEGER PRIMARY KEY AUTOINCREMENT,record_id TEXT NOT NULL REFERENCES items(record_id),annotator_id TEXT NOT NULL,review_role TEXT NOT NULL,label TEXT NOT NULL,scores_json TEXT NOT NULL,explanation TEXT NOT NULL,codebook_version TEXT NOT NULL,created_at TEXT NOT NULL,UNIQUE(record_id,annotator_id,review_role));
        CREATE TABLE IF NOT EXISTS adjudications(record_id TEXT PRIMARY KEY REFERENCES items(record_id),actor_id TEXT NOT NULL,final_label TEXT NOT NULL,rationale TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT,record_id TEXT NOT NULL,actor_id TEXT NOT NULL,action TEXT NOT NULL,before_json TEXT,after_json TEXT NOT NULL,created_at TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_annotations_record ON annotations(record_id);""")
        c.execute("INSERT OR IGNORE INTO codebooks VALUES(?,?,?)",(DEFAULT_CODEBOOK["version"],json.dumps(DEFAULT_CODEBOOK["definitions"]),now()))

def import_items(items:list[Item]):
    ids=[x.record_id for x in items]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate record IDs in this import")
    with db() as c:
        existing={r[0] for r in c.execute("SELECT record_id FROM items WHERE record_id IN ("+",".join("?" for _ in ids)+")",ids)} if ids else set()
        if existing:raise ValueError("Record ID already exists: "+", ".join(sorted(existing)))
        for item in items:
            c.execute("INSERT INTO items VALUES(?,?,?,?)",(item.record_id,item.content,item.category,now()))
            c.execute("INSERT INTO audit_log(record_id,actor_id,action,before_json,after_json,created_at) VALUES(?,?,?,?,?,?)",(item.record_id,"import","record_imported",None,item.model_dump_json(),now()))
    return len(items)

def list_records(search="",category=""):
    q="SELECT * FROM items WHERE (content LIKE ? OR record_id LIKE ?)";args=[f"%{search}%"]*2
    if category:q+=" AND category=?";args.append(category)
    q+=" ORDER BY created_at,record_id"
    with db() as c:
        records=[dict(r) for r in c.execute(q,args)]
        for r in records:
            r["annotations"]=[dict(a) for a in c.execute("SELECT * FROM annotations WHERE record_id=? ORDER BY created_at,id",(r["record_id"],))]
            for a in r["annotations"]:a["scores"]=json.loads(a.pop("scores_json"))
            final=c.execute("SELECT * FROM adjudications WHERE record_id=?",(r["record_id"],)).fetchone();r["adjudication"]=dict(final) if final else None
    return records

def create_annotation(payload:AnnotationCreate):
    with db() as c:
        if not c.execute("SELECT 1 FROM items WHERE record_id=?",(payload.record_id,)).fetchone():raise KeyError("Record not found")
        if not c.execute("SELECT 1 FROM codebooks WHERE version=?",(payload.codebook_version,)).fetchone():raise ValueError("Unknown codebook version")
        rows=c.execute("SELECT annotator_id,review_role FROM annotations WHERE record_id=?",(payload.record_id,)).fetchall()
        if any(r["annotator_id"]==payload.annotator_id and r["review_role"]==payload.review_role for r in rows):raise ValueError("This reviewer already annotated the record; use correction to update a prior label")
        if payload.review_role=="reviewer" and any(r["review_role"]=="annotator" and r["annotator_id"]==payload.annotator_id for r in rows):raise ValueError("Second review must be completed by a different annotator")
        cur=c.execute("INSERT INTO annotations(record_id,annotator_id,review_role,label,scores_json,explanation,codebook_version,created_at) VALUES(?,?,?,?,?,?,?,?)",(payload.record_id,payload.annotator_id,payload.review_role,payload.label,payload.scores.model_dump_json(),payload.explanation,payload.codebook_version,now()))
        after={"id":cur.lastrowid,**payload.model_dump()}
        c.execute("INSERT INTO audit_log(record_id,actor_id,action,after_json,created_at) VALUES(?,?,?,?,?)",(payload.record_id,payload.annotator_id,"annotation_added",json.dumps(after),now()))
        return cur.lastrowid

def correct_annotation(annotation_id:int,payload:AnnotationCorrection):
    with db() as c:
        row=c.execute("SELECT * FROM annotations WHERE id=?",(annotation_id,)).fetchone()
        if not row:return False
        before=dict(row);c.execute("UPDATE annotations SET label=? WHERE id=?",(payload.label,annotation_id))
        after={**before,"label":payload.label,"correction_reason":payload.reason}
        c.execute("INSERT INTO audit_log(record_id,actor_id,action,before_json,after_json,created_at) VALUES(?,?,?,?,?,?)",(before["record_id"],payload.actor_id,"annotation_corrected",json.dumps(before),json.dumps(after),now()))
    return True

def adjudicate(payload:Adjudication):
    with db() as c:
        if not c.execute("SELECT 1 FROM items WHERE record_id=?",(payload.record_id,)).fetchone():raise KeyError("Record not found")
        before=c.execute("SELECT * FROM adjudications WHERE record_id=?",(payload.record_id,)).fetchone();before=dict(before) if before else None
        c.execute("INSERT INTO adjudications VALUES(?,?,?,?,?) ON CONFLICT(record_id) DO UPDATE SET actor_id=excluded.actor_id,final_label=excluded.final_label,rationale=excluded.rationale,created_at=excluded.created_at",(payload.record_id,payload.actor_id,payload.final_label,payload.rationale,now()))
        c.execute("INSERT INTO audit_log(record_id,actor_id,action,before_json,after_json,created_at) VALUES(?,?,?,?,?,?)",(payload.record_id,payload.actor_id,"adjudicated",json.dumps(before) if before else None,payload.model_dump_json(),now()))
    return True

def audit(record_id):
    with db() as c:return [dict(r) for r in c.execute("SELECT * FROM audit_log WHERE record_id=? ORDER BY id",(record_id,))]

def create_codebook(payload:Codebook):
    with db() as c:c.execute("INSERT INTO codebooks VALUES(?,?,?)",(payload.version,json.dumps(payload.definitions),now()))

def codebooks():
    with db() as c:return [{"version":r[0],"definitions":json.loads(r[1]),"created_at":r[2]} for r in c.execute("SELECT * FROM codebooks ORDER BY created_at")]

def report():
    records=list_records();labels={};missing=0;double=[];agree=0;observed=0
    allowed_categories={"factuality","completeness","ambiguity","instruction-following","general"}
    for r in records:
        ann=r["annotations"]
        if not ann:missing+=1
        for a in ann:labels[a["label"]]=labels.get(a["label"],0)+1
        if len(ann)>=2:
            first,second=ann[0]["label"],ann[1]["label"];double.append((first,second));observed+=1;agree+=int(first==second)
    po=agree/observed if observed else None
    if observed:
        left={l:sum(a==l for a,b in double)/observed for l in labels};right={l:sum(b==l for a,b in double)/observed for l in labels}
        pe=sum(left.get(l,0)*right.get(l,0) for l in labels);kappa=(po-pe)/(1-pe) if pe<1 else None
    else:kappa=None
    disagreements=sum(a!=b for a,b in double)
    return {"record_count":len(records),"annotation_count":sum(len(r["annotations"]) for r in records),"label_distribution":labels,
            "invalid_category_count":sum(r["category"] not in allowed_categories for r in records),
            "records_missing_annotation":missing,"missingness_rate":round(missing/len(records),3) if records else None,
            "independently_double_reviewed":observed,"disagreement_count":disagreements,
            "disagreement_rate":round(disagreements/observed,3) if observed else None,"cohens_kappa":round(kappa,3) if kappa is not None else None,
            "limitations":"Agreement measures consistency, not correctness; small samples and class imbalance can make kappa unstable."}

def export_json():return list_records()
def export_csv():
    rows=list_records();s=io.StringIO();w=csv.DictWriter(s,fieldnames=["record_id","content","category","created_at","annotations","adjudication"]);w.writeheader()
    for r in rows:w.writerow({**r,"annotations":json.dumps(r["annotations"]),"adjudication":json.dumps(r["adjudication"])})
    return s.getvalue()
