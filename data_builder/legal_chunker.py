import re
from langchain_core.documents import Document


# ---------- REGEX PATTERNS ----------
ARTICLE_PATTERN = r"(Article\s+\d+[A-Z]?)"
SECTION_PATTERN = r"(Section\s+\d+[A-Z]?)"
PRINCIPLE_PATTERN = r"(APP\s+\d+|IPP\s+\d+)"
CLAUSE_PATTERN = r"(\(\d+\)|\([a-z]\))"


# ---------- MAIN CHUNKER ----------
class LegalChunker:

    def __init__(self, law_name, jurisdiction):
        self.law_name = law_name
        self.jurisdiction = jurisdiction

    def chunk(self, text: str):
        if "GDPR" in self.law_name or "AI Act" in self.law_name:
            return self._chunk_by_article(text)
        elif "DPDP" in self.law_name:
            return self._chunk_by_section(text)
        elif "CCPA" in self.law_name:
            return self._chunk_by_section(text)
        else:
            return self._chunk_by_principle(text)

    # ---------- ARTICLE-BASED ----------
    def _chunk_by_article(self, text):
        splits = re.split(ARTICLE_PATTERN, text)
        documents = []

        for i in range(1, len(splits), 2):
            article_id = splits[i]
            article_text = splits[i + 1]

            clause_chunks = self._split_clauses(article_text)

            for clause in clause_chunks:
                documents.append(
                    Document(
                        page_content=clause["text"],
                        metadata={
                            "law": self.law_name,
                            "jurisdiction": self.jurisdiction,
                            "article": article_id,
                            "clause": clause["clause"]
                        }
                    )
                )
        return documents

    # ---------- SECTION-BASED ----------
    def _chunk_by_section(self, text):
        splits = re.split(SECTION_PATTERN, text)
        documents = []

        for i in range(1, len(splits), 2):
            section_id = splits[i]
            section_text = splits[i + 1]

            documents.append(
                Document(
                    page_content=section_text.strip(),
                    metadata={
                        "law": self.law_name,
                        "jurisdiction": self.jurisdiction,
                        "section": section_id
                    }
                )
            )
        return documents

    # ---------- PRINCIPLE-BASED ----------
    def _chunk_by_principle(self, text):
        splits = re.split(PRINCIPLE_PATTERN, text)
        documents = []

        for i in range(1, len(splits), 2):
            principle_id = splits[i]
            principle_text = splits[i + 1]

            documents.append(
                Document(
                    page_content=principle_text.strip(),
                    metadata={
                        "law": self.law_name,
                        "jurisdiction": self.jurisdiction,
                        "principle": principle_id
                    }
                )
            )
        return documents

    # ---------- CLAUSE SPLITTING ----------
    def _split_clauses(self, article_text):
        clauses = re.split(CLAUSE_PATTERN, article_text)
        clause_chunks = []

        for i in range(1, len(clauses), 2):
            clause_chunks.append({
                "clause": clauses[i],
                "text": clauses[i + 1].strip()
            })

        if not clause_chunks:
            clause_chunks.append({"clause": None, "text": article_text.strip()})

        return clause_chunks
