import io
import re
import traceback
from typing import List, Dict, Any, Optional

import pandas as pd
from PyPDF2 import PdfReader

# Fix #1: Updated imports for newer LangChain
from langchain_ollama import OllamaLLM
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentQA:
    def __init__(self):
        self.docs = []
        self.structured_data = []
        self._passages = []  # Fix #3: will now actually be populated
        self._vectorstore = None

        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )

        # Fix #1: Use updated OllamaLLM class
        self.llm = OllamaLLM(model="llama3:8b")

        self.default_role = "You are a helpful financial analyst."

        # Fix #7: Use proper text splitter instead of raw char slicing
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=80,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        self.prompt = PromptTemplate(
            template="""
{role}

Use ONLY the context below to answer the question.
If the answer is not found, say "Not found in provided documents."

Context:
{context}

Question:
{question}

Answer:
""",
            input_variables=["context", "question", "role"]
        )

    # -------------------------------
    # FILE PROCESSING
    # -------------------------------
    def add_file(self, filename: str, file_bytes: bytes):
        try:
            ext = filename.lower()

            if ext.endswith(".pdf"):
                text = self._extract_text_from_pdf_bytes(file_bytes)
                ftype = "pdf"

            elif ext.endswith((".xls", ".xlsx")):
                df = pd.read_excel(io.BytesIO(file_bytes))

                self.structured_data.append({
                    "name": filename,
                    "dataframe": df
                })

                text = self._convert_df_to_text(df)
                ftype = "excel"

            else:
                raise ValueError("Unsupported file type")

            text = self._clean_text(text)

            self.docs.append({
                "name": filename,
                "text": text,
                "type": ftype,
                "size": len(text)
            })

            new_passages = self._split_into_passages(text, filename, ftype)
            self._passages.extend(new_passages)  # Fix #3: populate _passages
            self._add_to_vectorstore(new_passages)

        except Exception:
            traceback.print_exc()
            raise

    # -------------------------------
    # TEXT EXTRACTION
    # -------------------------------
    def _extract_text_from_pdf_bytes(self, b: bytes) -> str:
        reader = PdfReader(io.BytesIO(b))
        texts = []

        for i, page in enumerate(reader.pages, start=1):
            txt = page.extract_text()
            if txt:
                texts.append(f"[page {i}]\n{txt}")

        return "\n".join(texts)

    def _convert_df_to_text(self, df: pd.DataFrame) -> str:
        lines = []
        for col in df.columns:
            values = df[col].astype(str).tolist()
            lines.append(f"{col}: {', '.join(values)}")
        return "\n".join(lines)

    def _clean_text(self, text: str) -> str:
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s+\n", "\n\n", text)
        return text.strip()

    # -------------------------------
    # CHUNKING
    # -------------------------------
    def _split_into_passages(self, text: str, source: str, dtype: str) -> List[Dict]:
        """Fix #7: Use RecursiveCharacterTextSplitter instead of raw char offsets."""
        chunks = self.text_splitter.split_text(text)
        passages = []

        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 50:
                passages.append({
                    "text": chunk,
                    "source": source,  # Fix #3: store source at top level for easy filtering
                    "metadata": {
                        "source": source,
                        "type": dtype,
                        "chunk_id": i
                    }
                })

        return passages

    # -------------------------------
    # VECTOR STORE
    # -------------------------------
    def _add_to_vectorstore(self, passages: List[Dict]):
        if not passages:
            return

        texts = [p["text"] for p in passages]
        metadatas = [p["metadata"] for p in passages]

        if self._vectorstore:
            self._vectorstore.add_texts(texts, metadatas=metadatas)
        else:
            self._vectorstore = FAISS.from_texts(
                texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )

    def _build_vectorstore(self):
        """Fix #2: Implement the missing method called by main.py's delete endpoint."""
        if self._passages:
            texts = [p["text"] for p in self._passages]
            metadatas = [p["metadata"] for p in self._passages]
            self._vectorstore = FAISS.from_texts(
                texts,
                embedding=self.embeddings,
                metadatas=metadatas
            )
        else:
            self._vectorstore = None

    # -------------------------------
    # QUERY CLASSIFICATION
    # -------------------------------
    def _classify_query(self, question: str) -> str:
        """Fix #5: Only route to structured if structured data actually exists."""
        if self.structured_data:
            q = question.lower()
            if any(k in q for k in ["total", "sum", "average", "mean", "max", "min"]):
                return "structured"
            if any(k in q for k in ["compare", "difference", "vs"]):
                return "comparison"
        return "rag"

    # -------------------------------
    # STRUCTURED DATA HANDLING
    # -------------------------------
    def _handle_dataframe_query(self, question: str):
        if not self.structured_data:
            return {"answer": "No structured data available", "sources": []}

        df = self.structured_data[-1]["dataframe"]
        q = question.lower()

        try:
            if "total" in q or "sum" in q:
                result = df.sum(numeric_only=True)

            elif "average" in q or "mean" in q:
                result = df.mean(numeric_only=True)

            elif "max" in q:
                result = df.max(numeric_only=True)

            elif "min" in q:
                result = df.min(numeric_only=True)

            else:
                return {
                    "answer": "Structured query not supported",
                    "sources": []
                }

            result_str = result.to_string()

            # Fix #6: Only generate insight for structured results, not every long answer
            insight = self._generate_insight(result_str)

            return {
                "answer": f"{result_str}\n\n📊 Insight:\n{insight}" if insight else result_str,
                "sources": []
            }

        except Exception as e:
            return {"answer": str(e), "sources": []}

    # -------------------------------
    # INSIGHT GENERATION
    # -------------------------------
    def _generate_insight(self, text: str) -> str:
        prompt = f"""
You are a financial analyst.

Generate 1-2 concise business insights.

{text}
"""
        return self.llm.invoke(prompt)

    # -------------------------------
    # RAG WITH FILTERING
    # -------------------------------
    def _rag_answer(self, question: str, documents: Optional[List[str]], role: str, k: int):
        retriever = self._vectorstore.as_retriever(search_kwargs={"k": k})

        # Fix #4: Use invoke() instead of deprecated get_relevant_documents()
        docs = retriever.invoke(question)

        # Apply document filtering
        if documents:
            docs = [d for d in docs if d.metadata.get("source") in documents]

        if not docs:
            return {
                "answer": "No relevant information found.",
                "sources": []
            }

        context = "\n\n".join([d.page_content for d in docs])

        prompt_input = {
            "context": context,
            "question": question,
            "role": role
        }

        # Fix #6: Remove unconditional insight generation from RAG answers
        answer = self.llm.invoke(self.prompt.format(**prompt_input))

        sources = [
            {
                "text": d.page_content[:200],
                "source": d.metadata.get("source", "unknown")
            }
            for d in docs
        ]

        return {
            "answer": answer,
            "sources": sources
        }

    # -------------------------------
    # MAIN QA FUNCTION
    # -------------------------------
    def answer_question(self, question, top_k=3, documents=None, role=None):
        try:
            if not self._vectorstore:
                return {
                    "answer": "No documents indexed yet.",
                    "sources": []
                }

            query_type = self._classify_query(question)

            if query_type == "structured":
                return self._handle_dataframe_query(question)

            k = 5 if len(question) > 100 else top_k
            final_role = role.strip() if role else self.default_role

            return self._rag_answer(question, documents, final_role, k)

        except Exception:
            traceback.print_exc()
            return {
                "answer": "Internal error occurred",
                "sources": []
            }

    # -------------------------------
    # DOCUMENT LIST
    # -------------------------------
    def get_indexed_docs(self):
        return [
            {
                "name": d["name"],
                "type": d["type"],
                "size": d["size"]
            }
            for d in self.docs
        ]