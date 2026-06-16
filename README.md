# 🧠 AI Document Intelligence System (RAG + Structured Reasoning)

An end-to-end AI system that analyzes documents using a **hybrid approach combining Retrieval-Augmented Generation (RAG) and structured data reasoning**.

Unlike basic RAG apps, this system intelligently routes queries to the most appropriate pipeline — enabling both **contextual understanding** and **numerical analysis**.

---

## 🚀 Key Features

### 📂 Document Processing

* Upload PDF and Excel (.xls/.xlsx) files
* Automatic text extraction and chunking
* Vector indexing using FAISS

---

### 🧠 Intelligent Query Routing

Automatically classifies user queries into:

* 📊 **Structured Queries** → handled using Pandas (Excel analysis)
* 📄 **Unstructured Queries** → handled using RAG (LLM + FAISS)
* 💬 **General Queries** → handled directly by LLM

---

### 🔗 Hybrid AI Architecture

#### 1. RAG Pipeline (Unstructured Data)

* Embedding generation using Sentence Transformers
* Semantic search using FAISS
* Context-aware answer generation via LLM

#### 2. Structured Data Engine

* Direct DataFrame operations:

  * Sum / Total
  * Average / Mean
  * Max / Min
* Ensures accurate numerical results (no hallucination)

---

### 📊 Insight Generation

* Converts raw outputs into **business insights** using LLM
* Bridges gap between data → decision-making

---

### 📚 Source Attribution

* Displays document sources used in answers
* Improves transparency and trust

---

### 🎭 Role-Based Responses

* Custom system prompts:

  * “You are a financial analyst”
  * “Explain like a teacher”

---

## 🏗️ System Architecture

```
User Query
     ↓
Query Classifier (Rule + LLM)
     ↓
-------------------------------
| Structured | RAG | General |
-------------------------------
     ↓            ↓
 Pandas        FAISS + LLM
     ↓            ↓
     -------- Merge --------
               ↓
      Insight Generation (LLM)
               ↓
            Response
```

---

## ⚙️ Tech Stack

**Backend**

* FastAPI
* LangChain
* FAISS
* Sentence Transformers
* Ollama (LLaMA3)

**Data Processing**

* Pandas
* PyPDF2

**Frontend**

* NiceGUI

---

## 🔄 Workflow

1. Upload documents (PDF/Excel)
2. System:

   * Extracts text
   * Builds vector index
   * Stores structured data
3. User asks a query
4. Query is classified and routed:

   * Structured → Pandas
   * RAG → FAISS + LLM
5. System returns:

   * Answer
   * Sources
   * Business insight

---

## 🧪 Example Queries

### 📊 Structured

* “What is the total revenue?”
* “Give average sales by region”

### 📄 RAG

* “Summarize this document”
* “What are the key insights?”

### 💬 General

* “What can you do?”

---

## ⚡ Setup

```bash
git clone https://github.com/Singhsshweta/document-intelligence-api.git
cd document-intelligence-api

python -m venv venv
venv\Scripts\activate   # Windows

pip install -r requirements.txt
```

### Run Ollama

```bash
ollama run llama3:8b
```

### Run Backend

```bash
uvicorn backend.main:app --reload
```

### Run Frontend

```bash
python frontend/app.py
```

---

## ⚠️ Limitations

* No persistent storage
* Basic structured query support
* Single-user system

---

## 🚀 Future Work

* Advanced financial analytics
* Chart & report generation
* Persistent vector database
* Multi-document comparison

---

## 👩‍💻 Author

Shweta Singh
GitHub: https://github.com/Singhsshweta

---

## 💡 Key Takeaway

This project demonstrates how to design a **hybrid AI system that combines symbolic computation (Pandas) with neural retrieval (RAG)** to produce accurate and actionable results.

---

⭐ If you find this useful, consider starring the repo!
