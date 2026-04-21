from rag.pageindex_store import PageIndexStore


class ComplianceRetriever:

    def __init__(self):
        self.store = PageIndexStore()

    def retrieve(
        self,
        query: str,
        law: str = None,
        jurisdiction: str = None,
        top_k: int = 5
    ):
        filters = {}

        if law:
            filters["law"] = law

        if jurisdiction:
            filters["jurisdiction"] = jurisdiction

        results = self.store.search(
            query=query,
            filters=filters,
            top_k=top_k
        )

        return results