from pydantic import BaseModel
from typing import List

class QuestionRequest(BaseModel):
    question: str
    top_k: int = 3

class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]
