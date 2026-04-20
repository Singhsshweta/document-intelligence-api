from pydantic import BaseModel, Field
from typing import List, Optional


# -------------------------------
# BASE RESPONSE
# -------------------------------
class BaseResponse(BaseModel):
    status: str = Field(..., description="success or error")
    message: Optional[str] = Field(
        default=None,
        description="Optional message (used for errors or info)"
    )


# -------------------------------
# REQUEST MODELS
# -------------------------------
class ChatRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="User query"
    )

    role: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Custom assistant role or instructions"
    )

    top_k: Optional[int] = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of documents to retrieve"
    )

    documents: Optional[List[str]] = Field(
        default=None,
        description="Filter by selected document names"
    )


# -------------------------------
# RESPONSE MODELS
# -------------------------------
class Source(BaseModel):
    text: str = Field(..., description="Snippet of source text")
    # Fix #11: source can be None if metadata is missing — must be Optional
    source: Optional[str] = Field(default=None, description="Document name")


class ChatResponse(BaseResponse):
    answer: str = Field(..., description="Generated answer")
    sources: List[Source] = Field(
        default_factory=list,
        description="List of source snippets"
    )


class UploadResponse(BaseResponse):
    filename: str = Field(..., description="Uploaded file name")


class DocumentInfo(BaseModel):
    name: str = Field(..., description="Document name")
    type: str = Field(..., description="File type (pdf/excel)")
    size: int = Field(..., description="Character length of extracted text")


class DocumentListResponse(BaseResponse):
    documents: List[DocumentInfo] = Field(default_factory=list)
    count: int = Field(..., description="Total number of documents")


class ClearResponse(BaseResponse):
    pass


class DeleteResponse(BaseResponse):
    pass