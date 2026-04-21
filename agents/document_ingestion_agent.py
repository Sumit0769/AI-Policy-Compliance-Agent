import os
import tempfile
from typing import List
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader

from data_builder.text_cleaner import clean_text
from data_builder.legal_chunker import LegalChunker
from data_builder.metadata_builder import enrich_document
from rag.pageindex_store import PageIndexStore

class DocumentIngestionAgent:
    def __init__(self, raw_data_dir: str = "data/raw"):
        self.raw_data_dir = raw_data_dir
        # Ensure PageIndexStore is ready for file paths
        self.vector_store = PageIndexStore()

    def ingest(self):
        raw_docs = self._load_documents()
        legal_chunks = self._chunk_and_enrich(raw_docs)
        
        # 1. PageIndex local version needs a physical file to build its tree.
        # We combine your enriched legal chunks into a temporary markdown file.
        processed_text = "\n\n".join([c.page_content for c in legal_chunks])
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md", mode='w', encoding='utf-8') as tf:
            tf.write(processed_text)
            temp_path = tf.name

        try:
            # 2. Pass the path of the enriched content to PageIndex
            print(f"⏳ Indexing {len(legal_chunks)} legal chunks via local LLM...")
            self.vector_store.store_file(temp_path)
            print(f"✅ Successfully ingested legal chunks.")
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def _load_documents(self) -> List[Document]:
        documents = []
        if not os.path.exists(self.raw_data_dir):
            print(f"❌ Directory not found: {self.raw_data_dir}")
            return []

        for file in os.listdir(self.raw_data_dir):
            path = os.path.join(self.raw_data_dir, file)
            if file.endswith(".pdf"):
                loader = PyPDFLoader(path)
            elif file.endswith(".docx"):
                loader = Docx2txtLoader(path)
            else:
                continue

            docs = loader.load()
            for doc in docs:
                doc.page_content = clean_text(doc.page_content)
                doc.metadata["source_file"] = file
            documents.extend(docs)
        return documents

    def _chunk_and_enrich(self, documents: List[Document]) -> List[Document]:
        all_chunks = []
        for doc in documents:
            law_name, jurisdiction = self._infer_law(doc.metadata["source_file"])
            chunker = LegalChunker(law_name=law_name, jurisdiction=jurisdiction)
            chunks = chunker.chunk(doc.page_content)

            for chunk in chunks:
                enriched_chunk = enrich_document(chunk)
                enriched_chunk.metadata.update({
                    "law": law_name,
                    "jurisdiction": jurisdiction,
                    "source_file": doc.metadata["source_file"]
                })
                all_chunks.append(enriched_chunk)
        return all_chunks

    def _infer_law(self, filename: str):
        name = filename.lower()
        mapping = {
            "ai": ("EU AI Act", "EU"),
            "gdpr": ("GDPR", "EU"),
            "uk": ("UK GDPR & DPA 2018", "UK"),
            "dpdp": ("DPDP Act", "India"),
            "india": ("DPDP Act", "India"),
            "ccpa": ("CCPA", "California, USA"),
            "iso": ("ISO Standard", "Global")
        }
        for key, value in mapping.items():
            if key in name: return value
        return "Corporate Policy", "Internal"

if __name__ == "__main__":
    agent = DocumentIngestionAgent()
    agent.ingest()
