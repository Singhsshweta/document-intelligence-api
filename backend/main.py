from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from backend.qa import DocumentQA
from backend.schemas import (
    ChatRequest,
    ChatResponse,
    UploadResponse,
    DocumentListResponse,
    ClearResponse
)

# -------------------------------
# App Init
# -------------------------------
app = FastAPI(
    title="AI Financial Document Analyst API",
    description="RAG + Structured Data Hybrid AI System",
    version="2.1"
)

# -------------------------------
# CORS (restrict in production)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Initialize QA System
# -------------------------------
qa_system = DocumentQA()


# -------------------------------
# Health Check
# -------------------------------
@app.get("/")
def root():
    return {
        "message": "AI Financial Document Analyst API is running 🚀",
        "features": [
            "RAG-based QA",
            "Structured Data Analysis",
            "Query Classification",
            "Insight Generation"
        ]
    }


# -------------------------------
# Upload File
# -------------------------------
@app.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()

        if not file.filename:
            return {
                "status": "error",
                "filename": "",
                "message": "Invalid file"
            }

        qa_system.add_file(file.filename, content)

        return {
            "status": "success",
            "filename": file.filename,
            "message": "File indexed successfully"
        }

    except Exception as e:
        return {
            "status": "error",
            "filename": file.filename if file else "",
            "message": str(e)
        }


# -------------------------------
# Ask Question
# -------------------------------
@app.post("/ask", response_model=ChatResponse)
async def ask_question(request: ChatRequest):
    try:
        # Validation
        if not request.question.strip():
            return {
                "status": "error",
                "answer": "",
                "sources": []
            }

        result = qa_system.answer_question(
            question=request.question,
            top_k=request.top_k,
            documents=request.documents,
            role=request.role
        )

        return {
            "status": "success",
            "answer": result.get("answer", ""),
            "sources": result.get("sources", [])
        }

    except Exception as e:
        return {
            "status": "error",
            "answer": str(e),
            "sources": []
        }


# -------------------------------
# List Documents
# -------------------------------
@app.get("/documents", response_model=DocumentListResponse)
def list_documents():
    try:
        docs = qa_system.get_indexed_docs()

        return {
            "status": "success",
            "documents": docs,
            "count": len(docs)
        }

    except Exception as e:
        return {
            "status": "error",
            "documents": [],
            "count": 0
        }


# -------------------------------
# Delete Single Document
# -------------------------------
@app.delete("/document/{name}")
def delete_document(name: str):
    try:
        # Remove from docs
        qa_system.docs = [
            d for d in qa_system.docs if d["name"] != name
        ]

        # Fix #9: Also remove from structured_data (was missing)
        qa_system.structured_data = [
            d for d in qa_system.structured_data if d["name"] != name
        ]

        # Fix #3: _passages is now actually populated, so this filter works
        qa_system._passages = [
            p for p in qa_system._passages if p["source"] != name
        ]

        # Fix #2: _build_vectorstore() is now defined in qa.py
        qa_system._vectorstore = None
        qa_system._build_vectorstore()

        return {
            "status": "success",
            "message": f"{name} deleted"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# -------------------------------
# Clear All (useful for testing)
# -------------------------------
@app.delete("/clear", response_model=ClearResponse)
def clear_documents():
    try:
        qa_system.docs = []
        qa_system._passages = []
        qa_system._vectorstore = None
        qa_system.structured_data = []

        return {
            "status": "success",
            "message": "All documents cleared"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }