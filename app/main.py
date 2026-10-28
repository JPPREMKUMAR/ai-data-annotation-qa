import csv,io,json
from pathlib import Path
from fastapi import FastAPI,File,HTTPException,UploadFile
from fastapi.responses import StreamingResponse
from app.models import Adjudication,AnnotationCorrection,AnnotationCreate,Codebook,ItemImport
from app import storage

app=FastAPI(title="AI Data Annotation and Quality Assurance Dashboard",version="0.1.0",
            description="Synthetic annotation workflow with independent review, adjudication, and correction audit trail.")
storage.initialize()

def seed_if_empty():
    if storage.list_records():return
    records=[json.loads(line) for line in Path("data/records.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    storage.import_items([storage.Item.model_validate(r) for r in records])
seed_if_empty()

@app.get("/api/health")
def health():return {"status":"ok"}

@app.get("/api/items")
def items(search:str="",category:str=""):return storage.list_records(search,category)

@app.post("/api/items/import",status_code=201)
def import_items(payload:ItemImport):
    try:return {"imported":storage.import_items(payload.records)}
    except ValueError as exc:raise HTTPException(409,str(exc)) from exc

@app.post("/api/items/import-file",status_code=201)
async def import_file(file:UploadFile=File(...)):
    raw=await file.read(2_000_001)
    if len(raw)>2_000_000:raise HTTPException(413,"Import file exceeds 2 MB")
    try:payload=parse_import(file.filename or "",raw)
    except ValueError as exc:raise HTTPException(400,f"Invalid import: {exc}") from exc
    try:return {"imported":storage.import_items(payload.records)}
    except ValueError as exc:raise HTTPException(409,str(exc)) from exc

def parse_import(filename:str,raw:bytes):
    name=filename.lower()
    try:
        text=raw.decode("utf-8-sig")
        if name.endswith(".jsonl"):rows=[json.loads(line) for line in text.splitlines() if line.strip()]
        elif name.endswith(".json"):rows=json.loads(text)
        elif name.endswith(".csv"):rows=list(csv.DictReader(io.StringIO(text)))
        else:raise ValueError("Upload .csv, .json, or .jsonl")
        return ItemImport(records=rows)
    except (UnicodeDecodeError,json.JSONDecodeError,ValueError) as exc:raise ValueError(str(exc)) from exc

@app.post("/api/annotations",status_code=201)
def annotate(payload:AnnotationCreate):
    try:return {"annotation_id":storage.create_annotation(payload),"saved":True}
    except KeyError as exc:raise HTTPException(404,str(exc)) from exc
    except ValueError as exc:raise HTTPException(400,str(exc)) from exc

@app.patch("/api/annotations/{annotation_id}")
def correct(annotation_id:int,payload:AnnotationCorrection):
    if not storage.correct_annotation(annotation_id,payload):raise HTTPException(404,"Annotation not found")
    return {"corrected":True,"annotation_id":annotation_id}

@app.post("/api/adjudications")
def adjudicate(payload:Adjudication):
    try:storage.adjudicate(payload);return {"adjudicated":True,"record_id":payload.record_id}
    except KeyError as exc:raise HTTPException(404,str(exc)) from exc

@app.get("/api/audit/{record_id}")
def audit(record_id:str):return storage.audit(record_id)

@app.get("/api/codebooks")
def codebooks():return storage.codebooks()

@app.post("/api/codebooks",status_code=201)
def create_codebook(payload:Codebook):
    try:storage.create_codebook(payload)
    except Exception as exc:raise HTTPException(409,"Codebook version already exists") from exc
    return {"saved":True,"version":payload.version}

@app.get("/api/report")
def report():return storage.report()

@app.get("/api/export.json")
def export_json():return storage.export_json()

@app.get("/api/export.csv")
def export_csv():
    return StreamingResponse(iter([storage.export_csv()]),media_type="text/csv",headers={"Content-Disposition":"attachment; filename=annotation-review.csv"})
