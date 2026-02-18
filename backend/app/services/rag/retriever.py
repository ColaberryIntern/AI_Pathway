"""RAG retriever for context-aware responses."""
import logging

from app.services.rag.vector_store import get_vector_store

logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retriever for RAG-based context augmentation."""

    def __init__(self):
        self.vector_store = get_vector_store()

    async def retrieve_skills(
        self,
        query: str,
        n_results: int = 10,
        domain_filter: str | None = None,
    ) -> list[dict]:
        """Retrieve relevant skills for a query."""
        return self.vector_store.search_skills(query, n_results, domain_filter)

    async def retrieve_similar_jds(
        self,
        jd_text: str,
        n_results: int = 5,
    ) -> list[dict]:
        """Retrieve similar job descriptions."""
        results = self.vector_store.query("job_descriptions", jd_text, n_results)
        return self._format_results(results)

    async def retrieve_learning_content(
        self,
        skill_id: str,
        industry: str | None = None,
        n_results: int = 5,
    ) -> list[dict]:
        """Retrieve learning content for a skill."""
        query = f"Learning content for skill {skill_id}"
        where = {"industry": industry} if industry else None
        results = self.vector_store.query("learning_content", query, n_results, where)
        return self._format_results(results)

    async def retrieve_similar_paths(
        self,
        profile_summary: str,
        n_results: int = 3,
    ) -> list[dict]:
        """Retrieve similar learning paths for reference."""
        results = self.vector_store.query("user_paths", profile_summary, n_results)
        return self._format_results(results)

    def _format_results(self, results: dict) -> list[dict]:
        """Format query results into a list of documents."""
        documents = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                doc = {
                    "id": doc_id,
                    "content": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                }
                if results["distances"]:
                    doc["relevance_score"] = 1 - results["distances"][0][i]
                documents.append(doc)
        return documents


class _NoOpRetriever(RAGRetriever):
    """Fallback when vector store / embeddings are unavailable."""

    def __init__(self):
        self.vector_store = None

    async def retrieve_skills(self, *a, **kw):
        return []

    async def retrieve_similar_jds(self, *a, **kw):
        return []

    async def retrieve_learning_content(self, *a, **kw):
        return []

    async def retrieve_similar_paths(self, *a, **kw):
        return []


_retriever_instance = None


def get_retriever() -> RAGRetriever:
    """Get singleton retriever instance."""
    global _retriever_instance
    if _retriever_instance is None:
        try:
            _retriever_instance = RAGRetriever()
        except Exception as exc:
            logger.warning(
                "RAG retriever unavailable (%s) — using no-op fallback. "
                "Agents will work without RAG context.",
                exc,
            )
            _retriever_instance = _NoOpRetriever()
    return _retriever_instance
