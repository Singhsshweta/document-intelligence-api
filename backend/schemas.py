# backend/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional

class QuestionRequest(BaseModel):
    question: str
    top_k: int = Field(default=3, ge=1, le=10)
    documents: Optional[List[str]] = None
    role: Optional[str] = None


class QuestionResponse(BaseModel):
    answer: str
    sources: List[str]