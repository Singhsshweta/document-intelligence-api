import os
import io
import re
import traceback
from typing import List, Dict, Any

import pandas as pd
from PyPDF2 import PdfReader

from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.embeddings.huggingface import HuggingFaceEmbeddings


class DocumentQA:
    def __init__(self):
        self.docs = []
        self._passages = []
        self._vectorstore = None
        self._qa_chain = None

        self.index_path = "data/faiss_index"

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # ✅ DEFAULT ROLE
        self.default_role = "You are a helpful financial assistant."

        # Load existing index
        if os.path.exists(os.path.join(self.index_path, "index.faiss")):
            try:
                self._vectorstore = FAISS.load_local(
                    self.index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self._qa_chain = self._get_qa_chain(self._vectorstore)
            except Exception:
                print("⚠️ Failed to load FAISS index")

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
            traceback.print_exc()
            return ""

    def _extract_text_from_excel_bytes(self, b: bytes) -> str:
        try:
            sheets_text = []

            with io.BytesIO(b) as bio:
                xls = pd.read_excel(bio, sheet_name=None, engine="openpyxl")

                for sheet_name, df in xls.items():
                    df = df.fillna("")
                    rows = df.astype(str).values.tolist()

                    text_rows = [
                        ", ".join([
                            f"{col}: {val}"
                            for col, val in zip(df.columns, row)
                        ])
                        for row in rows
                    ]

                    df_text = f"Sheet: {sheet_name}\n" + "\n".join(text_rows)
                    sheets_text.append(df_text)

            return "\n\n".join(sheets_text)

        except Exception:
            traceback.print_exc()
            return ""

    # ---------- Public API ----------
    def add_file(self, filename: str, file_bytes: bytes):
        try:
            _lower = filename.lower()

            if _lower.endswith(".pdf"):
                text = self._extract_text_from_pdf_bytes(file_bytes)
                ftype = "pdf"

            elif _lower.endswith((".xls", ".xlsx")):
                text = self._extract_text_from_excel_bytes(file_bytes)
                ftype = "excel"

            else:
                raise ValueError("Unsupported file type")

            text = self._clean_text(text)

            if not text.strip():
                raise ValueError("Could not extract text from file")

            self.docs.append({
                "name": filename,
                "text": text,
                "type": ftype,
                "size": len(text)
            })

            self._split_into_passages()
            self._build_vectorstore()

        except Exception as e:
            print("\n🔥 ERROR IN add_file 🔥")
            traceback.print_exc()
            raise e

    def get_indexed_docs(self):
        return [
            {
                "name": d["name"],
                "type": d["type"],
                "size": d["size"]
            }
            for d in self.docs
        ]

    # ---------- Processing ----------
    def _clean_text(self, text: str):
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s+\n", "\n\n", text)
        return text.strip()

    def _split_into_passages(self, max_chars: int = 1000):
        self._passages = []

        for d in self.docs:
            text = d["text"]

            segments = re.split(r"\n{2,}", text)

            for seg in segments:
                if len(seg) > 20:
                    self._passages.append({
                        "text": seg,
                        "source": d["name"]
                    })

    # ---------- Vectorstore ----------
    def _build_vectorstore(self):
        try:
            if not self._passages:
                return

            texts = [p["text"] for p in self._passages]
            metadatas = [{"source": p["source"]} for p in self._passages]

            self._vectorstore = FAISS.from_texts(
                texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )

            self._vectorstore.save_local(self.index_path)

            self._qa_chain = self._get_qa_chain(self._vectorstore)

        except Exception:
            print("\n🔥 VECTORSTORE ERROR 🔥")
            traceback.print_exc()

    # ---------- QA Chain ----------
    def _get_qa_chain(self, vectorstore):

        llm = Ollama(model="llama3:8b")

        template = """
{role}

Answer ONLY using the context below.

Context:
{context}

Question:
{question}

Answer:
"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question", "role"]
        )

        return RetrievalQA.from_chain_type(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt}
        )

    # ---------- Answer ----------
    def answer_question(self, question, top_k=3, documents=None, role=None):

        try:
            if not self._qa_chain:
                return {
                    "answer": "No documents indexed yet.",
                    "sources": []
                }

            self._qa_chain.retriever.search_kwargs["k"] = top_k

            # ✅ Use default or custom role
            final_role = role.strip() if role else self.default_role

            result = self._qa_chain({
                "query": question,
                "role": final_role
            })

            docs = result.get("source_documents", [])

            if documents:
                docs = [
                    d for d in docs
                    if d.metadata.get("source") in documents
                ]

            sources = [
                {
                    "text": d.page_content[:200],
                    "source": d.metadata.get("source")
                }
                for d in docs
            ]

            return {
                "answer": result.get("result", ""),
                "sources": sources
            }

        except Exception:
            print("\n🔥 ERROR IN answer_question 🔥")
            traceback.print_exc()

            return {
                "answer": "Internal error occurred",
                "sources": []
            }