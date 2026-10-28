import json
from pathlib import Path
import pytest
from pydantic import ValidationError
from app import storage
from app.models import Adjudication,AnnotationCorrection,AnnotationCreate,Codebook,Item,ItemImport

def add_record(record_id="r1"):
    storage.import_items([Item(record_id=record_id,content="Prompt: Evaluate this response.\nResponse: Example.",category="factuality")])

def annotation(record_id="r1",who="ann-1",role="annotator",label="correct"):
    return AnnotationCreate(record_id=record_id,annotator_id=who,review_role=role,label=label,scores={"correctness":4,"completeness":4,"instruction_adherence":5,"evidence_quality":3},explanation="The response matches the request and the label is supported.",codebook_version="1.0")

def test_duplicate_ids_rejected_within_and_across_imports():
    item=Item(record_id="r1",content="Example content",category="general")
    with pytest.raises(ValueError,match="Duplicate"):
        storage.import_items([item,item])
    storage.import_items([item])
    with pytest.raises(ValueError,match="already exists"):
        storage.import_items([item])

def test_csv_and_jsonl_upload_parsing():
    from app.main import parse_import
    csv_payload=parse_import("records.csv",b"record_id,content,category\ncsv-1,Example prompt and answer,general")
    jsonl_payload=parse_import("records.jsonl",b'{"record_id":"j-1","content":"A prompt and answer","category":"ambiguity"}\n')
    assert csv_payload.records[0].record_id=="csv-1"
    assert jsonl_payload.records[0].category=="ambiguity"
    with pytest.raises(ValueError):parse_import("bad.csv",b"record_id,content,category\nx,Text,not-a-category")

def test_independent_review_and_disagreement_metrics():
    add_record();storage.create_annotation(annotation())
    with pytest.raises(ValueError,match="different annotator"):
        storage.create_annotation(annotation(who="ann-1",role="reviewer",label="incorrect"))
    storage.create_annotation(annotation(who="ann-2",role="reviewer",label="incorrect"))
    report=storage.report()
    assert report["independently_double_reviewed"]==1
    assert report["disagreement_rate"]==1.0
    assert report["cohens_kappa"]==0.0

def test_correction_and_adjudication_are_audited():
    add_record();annotation_id=storage.create_annotation(annotation())
    storage.correct_annotation(annotation_id,AnnotationCorrection(label="incomplete",actor_id="reviewer-lead",reason="The required caveat is absent from this response."))
    storage.adjudicate(Adjudication(record_id="r1",actor_id="lead",final_label="incomplete",rationale="The missing caveat makes the response incomplete for this request."))
    history=storage.audit("r1")
    assert [row["action"] for row in history]==["record_imported","annotation_added","annotation_corrected","adjudicated"]
    assert json.loads(history[2]["before_json"])["label"]=="correct"
    assert storage.list_records()[0]["adjudication"]["final_label"]=="incomplete"

def test_missingness_codebook_and_json_csv_exports():
    add_record();storage.import_items([Item(record_id="r2",content="Another example content",category="general")])
    report=storage.report()
    assert report["records_missing_annotation"]==2
    assert report["missingness_rate"]==1.0
    assert "record_id,content,category" in storage.export_csv()
    assert len(storage.export_json())==2
    definitions=storage.DEFAULT_CODEBOOK["definitions"]
    storage.create_codebook(Codebook(version="1.1",definitions=definitions))
    assert {b["version"] for b in storage.codebooks()}=={"1.0","1.1"}

def test_invalid_score_and_incomplete_codebook_rejected():
    with pytest.raises(ValidationError):
        AnnotationCreate(record_id="r",annotator_id="a",review_role="annotator",label="correct",scores={"correctness":6,"completeness":3,"instruction_adherence":3,"evidence_quality":3},explanation="Reason long enough for this annotation.")
    with pytest.raises(ValidationError,match="every allowed label"):
        Codebook(version="1.1",definitions={"correct":"good"})

def test_golden_labels_cover_requested_example_types():
    path=Path(__file__).parents[1]/"data"/"gold_labels.jsonl"
    records=[json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    assert {r["label"] for r in records}=={"correct","incorrect","incomplete","misleading","ambiguous"}
