# 🧠 AI Document Analyst (RAG + Structured Data)

An AI-powered system that allows users to upload documents (PDF/Excel) and ask questions using a hybrid approach combining:

* 📄 Retrieval-Augmented Generation (RAG)
* 📊 Structured data analysis (Excel)

This project demonstrates how to build a **full-stack AI application** with document understanding and intelligent querying.

---

# 🚀 Features

## 📂 Document Management

* Upload **PDF** and **Excel (.xls/.xlsx)** files
* Select specific documents for querying
* Delete individual documents
* Clear all documents

## 🤖 Intelligent Query Handling

### 1. RAG-based QA (Unstructured Data)

* Ask questions about uploaded PDFs
* Uses embeddings + vector search (FAISS)

### 2. Structured Data Analysis (Excel)

Supports basic operations:

* Sum / Total
* Average / Mean
* Max / Min

### 3. Query Classification

Automatically detects query type:

* 💬 Chitchat (e.g., "hello")
* 📊 Structured (Excel calculations)
* 📄 RAG (document-based questions)

---

## 🧾 Source Attribution

* Shows which document(s) were used to generate answers

---

## 🎭 Custom Role Prompting

* Users can define assistant behavior via prompt
* Example:

  * “You are a financial analyst”
  * “Explain like a teacher”

---

## 💬 Chat Interface

* Chat-style UI
* User & AI messages
* Error handling
* Source indicators

---

# 🏗️ Project Structure

```bash
project/
│
├── backend/
│   ├── main.py        # FastAPI API
│   ├── qa.py          # Core AI logic
│   ├── schemas.py     # Request/response models
│
├── frontend/
│   ├── app.py         # NiceGUI UI
│
└── README.md
```

---

# ⚙️ Tech Stack

## Backend

* FastAPI
* LangChain
* FAISS (vector store)
* HuggingFace Embeddings (`all-MiniLM-L6-v2`)
* Ollama (`llama3:8b`)
* Pandas (Excel processing)
* PyPDF2 (PDF parsing)

## Frontend

* NiceGUI
* Async requests

---

# 🔄 System Workflow

1. Upload a document (PDF or Excel)
2. Backend:

   * Extracts text
   * Splits into chunks
   * Stores embeddings in FAISS
3. Ask a question
4. System classifies query:

   * Chitchat → LLM response
   * Structured → Pandas operations
   * RAG → Retrieval + LLM
5. Returns answer + sources

---

# 🧪 Example Queries

### 📊 Excel Queries

* "What is the total of column X?"
* "Give me the average sales"

### 📄 Document Queries

* "Summarize this document"
* "What are the key points?"

### 💬 Chitchat

* "Hello"
* "What can you do?"

---

# ⚡ Setup Instructions

## 1. Clone Repository

```bash
git clone https://github.com/Singhsshweta/document-intelligence-api.git
cd project
```

---

## 2. Create Virtual Environment

```bash
python -m venv venv
```

### Activate

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

```bash
pip install fastapi uvicorn nicegui requests pandas PyPDF2 \
langchain langchain-community langchain-core \
langchain-huggingface langchain-ollama \
faiss-cpu
```

---

## 4. Install & Run Ollama

Download:
👉 https://ollama.com

Then:

```bash
ollama pull llama3:8b
ollama serve
```

---

## 5. Run Backend

```bash
cd backend
uvicorn main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

## 6. Run Frontend

Open new terminal:

```bash
cd frontend
python app.py
```

Frontend runs at:

```
http://127.0.0.1:8080
```

---

# 🖥️ Usage

1. Open frontend in browser
2. Upload documents
3. Select documents in sidebar
4. Ask questions
5. View answers with sources

---

# ⚠️ Current Limitations

* No persistent storage (data resets on restart)
* Single-user system
* No authentication
* Limited Excel query support
* No streaming responses

---

# 🚀 Future Improvements

* Financial-specific analysis
* Multi-user support
* Persistent vector database
* Streaming responses
* Advanced table querying via LLM
* UI improvements (document preview, highlights)

---

# 📌 Note

Although the UI mentions "Financial Analyst",
this version is a **general-purpose document QA system**.

---

# 👨‍💻 Summary

This project demonstrates:

* RAG pipeline implementation
* Hybrid AI (unstructured + structured)
* Full-stack AI application design

---
