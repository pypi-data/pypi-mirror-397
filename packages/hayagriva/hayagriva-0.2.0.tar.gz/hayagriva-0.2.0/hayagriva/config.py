"""Configuration utilities for Hayagriva."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ModelConfig:
    """Configuration for embedding and generation models."""

    embedding_model: str = "all-MiniLM-L6-v2"
    llm_model: str = "gpt-4o"
    vector_store: str = "faiss"
    openai_api_key: Optional[str] = None


@dataclass
class ChunkingConfig:
    """Configuration for the text chunker."""

    chunk_size: int = 200
    overlap: int = 20


@dataclass
class RetrievalConfig:
    """Configuration for retrieval behavior."""

    top_k: int = 4
    similarity_threshold: float = 0.0
    strategy: str = "vector"  # "vector", "bm25", "hybrid"
    alpha: float = 0.5        # 0.0 = sparse (bm25), 1.0 = dense (vector)


@dataclass
class WeaviateConfig:
    """Configuration for Weaviate vector store."""
    
    url: str = "http://localhost:8080"
    api_key: Optional[str] = None
    index_name: str = "HayagrivaDocs"


@dataclass
class HayagrivaConfig:
    def __init__(
        self,
        backend="openai",
        api_key=None,
        model="gpt-4o-mini",
        vector_store="faiss",
        weaviate=None,
        chunking=None,
        models=None,
        retrieval=None,
    ):
        self.backend = backend        # "openai" or "groq"
        self.api_key = api_key        # API key for chosen backend
        self.model = model            # model name for backend
        self.vector_store = vector_store # "faiss" or "weaviate"

        # Existing config objects
        self.chunking = chunking or {}
        self.models = models or type("ModelConfig", (), {
            "embedding_model": "all-MiniLM-L6-v2",
        })()
        self.retrieval = retrieval or {}
        self.weaviate = weaviate or WeaviateConfig()
