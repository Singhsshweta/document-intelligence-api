from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.qa import DocumentQA

app = FastAPI(
    title="Financial Document Intelligence API",
    description="Production-ready financial document Q&A system",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

qa_system = DocumentQA()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        qa_system.add_file(file.filename, content)
        return {"message": f"{file.filename} indexed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from backend.schemas import QuestionRequest, QuestionResponse

@app.post("/ask", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    try:
        result = qa_system.answer_question(
            request.question,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
