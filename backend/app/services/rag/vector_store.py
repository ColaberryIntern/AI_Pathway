"""Vector store implementation using ChromaDB."""
import json
from pathlib import Path
from typing import Any
import chromadb
from app.config import get_settings
from app.services.rag.embeddings import get_embedding_service


class VectorStore:
    """ChromaDB vector store for RAG."""

    def __init__(self):
        settings = get_settings()
        self.persist_directory = settings.chroma_persist_directory
        self.embedding_service = get_embedding_service()

        # Initialize ChromaDB client (v0.5+ API)
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
        )

        # Initialize collections
        self._init_collections()

    def _init_collections(self):
        """Initialize all required collections."""
        self.ontology_collection = self.client.get_or_create_collection(
            name="ontology_skills",
            metadata={"description": "Skills from the GenAI ontology"},
        )

        self.content_collection = self.client.get_or_create_collection(
            name="learning_content",
            metadata={"description": "Learning content templates and examples"},
        )

        self.jd_collection = self.client.get_or_create_collection(
            name="job_descriptions",
            metadata={"description": "Sample job descriptions"},
        )

        self.paths_collection = self.client.get_or_create_collection(
            name="user_paths",
            metadata={"description": "Previously generated learning paths"},
        )

    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ):
        """Add documents to a collection."""
        collection = self.client.get_collection(collection_name)
        embeddings = self.embedding_service.embed_texts(documents)

        collection.add(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: dict | None = None,
    ) -> dict:
        """Query a collection for similar documents."""
        collection = self.client.get_collection(collection_name)
        query_embedding = self.embedding_service.embed_query(query_text)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )

        return results

    def load_ontology(self, ontology_path: str):
        """Load ontology data into the vector store."""
        with open(ontology_path, "r") as f:
            ontology = json.load(f)

        skills = ontology.get("skills", [])
        domains = {d["id"]: d for d in ontology.get("domains", [])}

        documents = []
        metadatas = []
        ids = []

        for skill in skills:
            domain = domains.get(skill["domain"], {})
            doc_text = f"{skill['name']}. Domain: {domain.get('label', '')}. {domain.get('description', '')}"

            documents.append(doc_text)
            metadatas.append({
                "skill_id": skill["id"],
                "skill_name": skill["name"],
                "domain": skill["domain"],
                "domain_label": domain.get("label", ""),
                "level": skill.get("level", 1),
                "prerequisites": json.dumps(skill.get("prerequisites", [])),
            })
            ids.append(skill["id"])

        # Clear existing and add new
        try:
            self.client.delete_collection("ontology_skills")
        except:
            pass

        self.ontology_collection = self.client.create_collection(
            name="ontology_skills",
            metadata={"description": "Skills from the GenAI ontology"},
        )

        self.add_documents("ontology_skills", documents, metadatas, ids)

    def search_skills(
        self,
        query: str,
        n_results: int = 10,
        domain_filter: str | None = None,
    ) -> list[dict]:
        """Search for skills matching a query."""
        where = {"domain": domain_filter} if domain_filter else None
        results = self.query("ontology_skills", query, n_results, where)

        skills = []
        if results["ids"] and results["ids"][0]:
            for i, skill_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = results["distances"][0][i] if results["distances"] else 0
                skills.append({
                    "skill_id": skill_id,
                    "skill_name": metadata.get("skill_name", ""),
                    "domain": metadata.get("domain", ""),
                    "domain_label": metadata.get("domain_label", ""),
                    "level": metadata.get("level", 1),
                    "prerequisites": json.loads(metadata.get("prerequisites", "[]")),
                    "relevance_score": 1 - distance,
                })

        return skills


_vector_store_instance = None


def get_vector_store() -> VectorStore:
    """Get singleton vector store instance."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = VectorStore()
    return _vector_store_instance
