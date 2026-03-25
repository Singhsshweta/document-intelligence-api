# qa.py
import os
import io
import re
from typing import List, Dict, Any, Tuple

import pandas as pd
from PyPDF2 import PdfReader

from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.embeddings.huggingface import HuggingFaceEmbeddings  # local embeddings


# ---------- DocumentQA Class ----------
class DocumentQA:
    def __init__(self):
        self.docs = []
        self._passages = []
        self._vectorstore = None
        self._qa_chain = None

        self.index_path = "data/faiss_index"

        # Load existing index if it exists
        if os.path.exists(self.index_path):
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self._vectorstore = FAISS.load_local(
                self.index_path,
                embeddings
            )
            self._qa_chain = self._get_qa_chain(self._vectorstore)


    # ---------- Extraction ----------
    def _extract_text_from_pdf_bytes(self, b: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(b))
            texts = []
            for page_num, page in enumerate(reader.pages, start=1):
                txt = page.extract_text()
                if txt:
                    texts.append(f"[page {page_num}]\n{txt}")
            return "\n".join(texts)
        except Exception:
            return ""

    def _extract_text_from_excel_bytes(self, b: bytes) -> str:
        try:
            sheets_text = []
            with io.BytesIO(b) as bio:
                xls = pd.read_excel(bio, sheet_name=None, engine="openpyxl")
                for sheet_name, df in xls.items():
                    df = df.fillna("")
                    rows = df.astype(str).values.tolist()
                    text_rows = [" | ".join(row) for row in rows]
                    df_text = f"Sheet: {sheet_name}\n" + "\n".join(text_rows)
                    sheets_text.append(df_text)
            return "\n\n".join(sheets_text)
        except Exception:
            return ""

    # ---------- Public API ----------
    def add_file(self, filename: str, file_bytes: bytes):
        _lower = filename.lower()
        if _lower.endswith(".pdf"):
            text = self._extract_text_from_pdf_bytes(file_bytes)
            ftype = "pdf"
        elif _lower.endswith((".xls", ".xlsx")):
            text = self._extract_text_from_excel_bytes(file_bytes)
            ftype = "excel"
        else:
            text = ""
            ftype = "unknown"

        text = self._clean_text(text)
        self.docs.append({"name": filename, "text": text, "type": ftype, "size": len(text)})
        self._split_into_passages()
        self._build_vectorstore()

    def get_indexed_docs(self) -> List[Dict[str, Any]]:
        return [{"name": d['name'], "type": d['type'], "size": d['size']} for d in self.docs]

    # ---------- Text processing ----------
    def _clean_text(self, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s+\n", "\n\n", text)
        return text.strip()

    def _split_into_passages(self, max_chars: int = 1000):
        passages = []
        for d in self.docs:
            text = d["text"]
            if "[page " in text:
                pages = re.split(r"(\[page \d+\])", text)
                blocks = []
                i = 0
                while i < len(pages):
                    if pages[i].startswith("[page "):
                        marker = pages[i]
                        content = pages[i+1] if i+1 < len(pages) else ""
                        blocks.append(marker + "\n" + content)
                        i += 2
                    else:
                        if pages[i].strip():
                            blocks.append(pages[i])
                        i += 1
                base_segments = blocks
            else:
                base_segments = [seg for seg in re.split(r"\n{2,}", text) if seg.strip()]

            # split long segments into smaller chunks
            for seg in base_segments:
                sentences = re.split(r'(?<=[.!?])\s+', seg)
                cur = ""
                for s in sentences:
                    if len(cur) + len(s) + 1 <= max_chars:
                        cur = cur + " " + s if cur else s
                    else:
                        if cur:
                            passages.append(cur.strip())
                        cur = s
                if cur:
                    passages.append(cur.strip())
        self._passages = [p for p in passages if len(p) > 20]

    # ---------- Vectorstore & QA chain ----------
    def _build_vectorstore(self):
        if not self.docs:
            self._vectorstore = None
            self._qa_chain = None
            return

        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        texts = []
        metadatas = []

        for d in self.docs:
            passages = self._passages
            for p in passages:
                texts.append(p)
                metadatas.append({
                    "source": d["name"]
                })

        self._vectorstore = FAISS.from_texts(
            texts,
            embedding=embeddings,
            metadatas=metadatas
        )

        self._vectorstore.save_local(self.index_path)
        self._qa_chain = self._get_qa_chain(self._vectorstore)

    def _get_qa_chain(self, vectorstore):
        llm = Ollama(model="llama3:8b")

        template = """
        {role}

        You are performing extractive question answering.

        Rules:
        - Answer ONLY from context
        - If not found say "I don't know"

        Context:
        {context}

        Question:
        {question}

        Answer:
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context","question","role"]
        )

        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

        return qa_chain

    # ---------- Answer ----------
    def answer_question(self, question: str, top_k: int = 3, documents=None, role=None):
        if not self._qa_chain:
            return {"answer": "No documents indexed yet. Upload PDFs/XLSX first.", "sources": []}

        # Update retriever's k dynamically
        self._qa_chain.retriever.search_kwargs["k"] = top_k

        result = self._qa_chain({"query": question})
        answer_text = result.get("result", "")
        sources = [getattr(doc, "page_content", str(doc))[:200] for doc in result.get("source_documents", [])]
        return {"answer": answer_text, "sources": sources}



# ---------- Example Usage ----------
if __name__ == "__main__":
    docqa = DocumentQA()

    # Example: add a PDF
    with open("financials.pdf", "rb") as f:
        docqa.add_file("financials.pdf", f.read())

    # Ask question
    res = docqa.answer_question("What is the revenue in 2023?")
    print("Answer:", res["answer"])
    print("Sources:", res["sources"])
