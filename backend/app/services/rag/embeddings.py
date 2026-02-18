"""Embedding service for generating vector representations using Vertex AI."""
from functools import lru_cache
import vertexai
from vertexai.language_models import TextEmbeddingModel
from app.config import get_settings


class EmbeddingService:
    """Service for generating text embeddings using Vertex AI."""

    def __init__(self):
        settings = get_settings()
        # Initialize Vertex AI
        vertexai.init(
            project=settings.gcp_project_id,
            location=settings.gcp_region,
        )
        # Use Vertex AI's text embedding model
        self.model = TextEmbeddingModel.from_pretrained("text-embedding-004")

    def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        embeddings = self.model.get_embeddings([text])
        return embeddings[0].values

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts."""
        # Vertex AI supports batch embedding
        # Process in batches of 250 (API limit)
        all_embeddings = []
        batch_size = 250
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = self.model.get_embeddings(batch)
            all_embeddings.extend([e.values for e in embeddings])
        return all_embeddings

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding for a search query."""
        return self.embed_text(query)


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Get cached embedding service instance."""
    return EmbeddingService()
