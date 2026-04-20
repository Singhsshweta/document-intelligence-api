# 🧠 AI Financial Document Analyst

A hybrid AI system that analyzes financial documents using both **LLM-based retrieval (RAG)** and **structured data processing**, generating accurate answers and business insights.

---

## 🚀 Features

* 📄 Upload PDF & Excel financial documents
* 🔍 Ask questions in natural language
* 🧠 Intelligent query classification (analysis / calculation / QA)
* 🔗 Hybrid reasoning:

  * RAG (unstructured text)
  * Pandas (structured data)
* 📊 Automatic business insights generation
* 📚 Source-based answers (with traceability)
* 💬 Interactive chat interface

---

## 🏗️ Architecture

Frontend (NiceGUI)
↓
FastAPI Backend
↓
Query Classifier (Rule + LLM)
↓
-

## | Structured Path | RAG Path |

↓               ↓
Pandas Engine   FAISS + LLM
↓               ↓
--------- Merge ----------
↓
Insight Generator (LLM)
↓
Final Response

---

## 🧠 How It Works

1. Upload financial documents (PDF/Excel)
2. System extracts:

   * Text → for RAG
   * Tables → for structured analysis
3. Query is classified:

   * Calculation / Analysis → Pandas
   * General QA → RAG pipeline
4. LLM generates:

   * Answer
   * Business insight

---

## 🛠️ Tech Stack

* Backend: FastAPI
* Frontend: NiceGUI
* LLM: LLaMA3 (via Ollama)
* Embeddings: Sentence Transformers
* Vector DB: FAISS
* Data Processing: Pandas

---

## ⚙️ Setup Instructions

### 1. Clone the repo

git clone https://github.com/Singhsshweta/financial-document-intelligence-api.git 
cd ai-financial-analyst

### 2. Install dependencies

pip install -r requirements.txt

### 3. Install & run Ollama

Download from: https://ollama.com/download

Run model:
ollama run llama3:8b

### 4. Run backend

uvicorn backend.main:app --reload 

### 5. Run frontend

python frontend/app.py

---

## 💡 Example Queries

* What is the total revenue?
* Compare revenue across regions
* What trends do you see in the data?
* Summarize the financial report

---

## 📊 Output Example

Answer: Revenue increased by 18% YoY
Insight: Indicates strong growth driven by Q4 performance

---

## 🎯 Key Highlights

* Built a hybrid AI system combining RAG and structured data analysis
* Implemented query routing for intelligent pipeline selection
* Developed end-to-end product (backend + UI + AI layer)
* Generated business-level insights, not just raw answers

---

## 🚀 Future Improvements

* Chart generation (visual analytics)
* Report export (PDF)
* Multi-document comparison
* Advanced query planning

---

## 👩‍💻 Author

Shweta Singh
LinkedIn: https://www.linkedin.com/in/shweta-singh-238775221
GitHub: https://github.com/Singhsshweta

---

## ⭐ If you like this project, give it a star!
