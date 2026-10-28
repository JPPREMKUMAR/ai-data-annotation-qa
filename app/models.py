from typing import Literal,get_args
from pydantic import BaseModel,Field,field_validator,model_validator

Label=Literal["correct","incorrect","incomplete","misleading","ambiguous"]
Category=Literal["factuality","completeness","ambiguity","instruction-following","general"]

class Item(BaseModel):
    record_id:str=Field(min_length=1,max_length=100)
    content:str=Field(min_length=1,max_length=10000)
    category:Category="general"

class ItemImport(BaseModel):
    records:list[Item]=Field(min_length=1,max_length=2000)

class Scores(BaseModel):
    correctness:int=Field(ge=1,le=5)
    completeness:int=Field(ge=1,le=5)
    instruction_adherence:int=Field(ge=1,le=5)
    evidence_quality:int=Field(ge=1,le=5)

class AnnotationCreate(BaseModel):
    record_id:str
    annotator_id:str=Field(min_length=1,max_length=100)
    review_role:Literal["annotator","reviewer"]
    label:Label
    scores:Scores
    explanation:str=Field(min_length=10,max_length=4000)
    codebook_version:str="1.0"

    @field_validator("explanation")
    @classmethod
    def explanation_not_blank(cls,value):
        if not value.strip():raise ValueError("Explanation cannot be blank")
        return value.strip()

class AnnotationCorrection(BaseModel):
    label:Label
    actor_id:str=Field(min_length=1,max_length=100)
    reason:str=Field(min_length=10,max_length=2000)

class Adjudication(BaseModel):
    record_id:str
    actor_id:str=Field(min_length=1,max_length=100)
    final_label:Label
    rationale:str=Field(min_length=10,max_length=3000)

class Codebook(BaseModel):
    version:str=Field(min_length=1,max_length=40)
    definitions:dict[Label,str]

    @model_validator(mode="after")
    def require_all_labels(self):
        if set(self.definitions)!=set(get_args(Label)) or any(not text.strip() for text in self.definitions.values()):
            raise ValueError("Codebook must define every allowed label with nonblank text")
        return self
