# Document RAG System (Local)

A local Retrieval-Augmented Generation (RAG) system built with:

- FastAPI
- FAISS
- HuggingFace embeddings (all-MiniLM-L6-v2)
- Ollama (LLaMA 3 7B)

## Features

- Upload PDF / Excel
- Automatic text chunking
- Local vector search
- Grounded QA
- Returns answer + sources

## Run

```bash
uvicorn app:app --reload