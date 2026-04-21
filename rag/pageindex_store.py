import os
from typing import List
from langchain_core.documents import Document
from pageindex_open import PIO


class PageIndexStore:
    """
    Vectorless storage using PageIndex SDK.
    Stores structured legal chunks with metadata.
    """

    def __init__(self, index_dir: str = "pageindex_store"):
        self.index_dir = index_dir
        os.makedirs(self.index_dir, exist_ok=True)

        self.pio = None
    # -------------------------
    # STORE DOCUMENTS.
    # -------------------------
    def store_file(self, file_path: str):
        """
        In pageindex-open, the path to the PDF is usually passed to PIO.
        """
        # Configure for local Ollama
        self.pio = PIO(
            file_path,                    # Pass the PDF file path directly
            model_name="llama3.2:1b",          # The model you pulled in Ollama
            api_base="http://localhost:11434" # Local Ollama endpoint
        )
        
        # This builds the hierarchical reasoning tree locally
        self.pio.build_index()
        
        # Save the tree structure
        self.pio.save(self.index_dir)
        print(f"✅ Document {file_path} indexed locally using Ollama.")

   # def store_documents(self, documents: List[Document]):

        #for doc in documents:
        #    self.index.add_text(
        #        text=doc.page_content,
        #        metadata=doc.metadata
        #    )

        #self.index.save_to_disk(self.index_dir)
        #print(f"Stored {len(documents)} documents {self.index_dir}.")

    # -------------------------
    # SEARCH
    # -------------------------
    def search(self, query: str, top_k: int = 5):
        if not self.pio:
            raise ValueError("Index not initialized. Run store_file() first.")
        
        # Local reasoning-based retrieval
        return self.pio.query(query, top_k=top_k)
    #def search(self, query: str, filters: dict = None, top_k: int = 5):
     #   results = self.index.search(
      #      query=query,
       ##    top_k=top_k
        #)
        #return results