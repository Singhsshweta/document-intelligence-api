from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from backend.qa import DocumentQA

app = FastAPI()

# ✅ Enable CORS (allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize QA system
qa_system = DocumentQA()


# ---------- Request Model ----------
class ChatRequest(BaseModel):
    question: str
    role: Optional[str] = None  # ✅ optional role support


# ---------- Root ----------
@app.get("/")
def root():
    return {"message": "Financial Document QA API is running 🚀"}


# ---------- Upload ----------
@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()

        qa_system.add_file(file.filename, content)

        return {
            "status": "success",
            "filename": file.filename
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ---------- Ask (ChatGPT-style) ----------
@app.post("/ask")
async def ask_question(request: ChatRequest):
    try:
        # ✅ Prevent empty queries
        if not request.question.strip():
            return {
                "status": "error",
                "message": "Question cannot be empty"
            }

        result = qa_system.answer_question(
            question=request.question,
            role=request.role  # ✅ pass role
        )

        return {
            "status": "success",
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ---------- List Uploaded Documents ----------
@app.get("/documents")
def list_documents():
    try:
        docs = qa_system.get_indexed_docs()

        return {
            "status": "success",
            "documents": docs
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }