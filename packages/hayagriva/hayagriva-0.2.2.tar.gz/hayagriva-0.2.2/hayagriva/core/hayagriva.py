# hayagriva/core/hayagriva.py

from __future__ import annotations
from typing import Iterable, List, Optional

from hayagriva.config import HayagrivaConfig
from hayagriva.core.chunker import (
    WordChunker,
    RecursiveChunker,
    SemanticChunker,
    HierarchicalChunker
)
from hayagriva.core.context_builder import build_context
from hayagriva.core.embeddings import SentenceTransformerEmbeddings
from hayagriva.core.generator import OpenAIGenerator
from hayagriva.core.pipeline import build_prompt
from hayagriva.core.retriever import Retriever
from hayagriva.core.vectorstore import FaissVectorStore
from hayagriva.core.weaviate_store import WeaviateVectorStore
from hayagriva.utils.logger import get_logger
from hayagriva.utils.validator import ensure_texts

logger = get_logger(__name__)


class Hayagriva:
    """High-level interface for the RAG framework."""

    def __init__(self, config: Optional[HayagrivaConfig] = None) -> None:
        self.config = config or HayagrivaConfig()

        # Core components
        self.embedder = SentenceTransformerEmbeddings(
            self.config.models.embedding_model
        )

        # Initialize Chunker based on strategy
        strategy = self.config.chunking.strategy
        if strategy == "recursive":
            self.chunker = RecursiveChunker(self.config.chunking)
        elif strategy == "semantic":
            self.chunker = SemanticChunker(self.config.chunking, embedder=self.embedder)
        elif strategy == "hierarchical":
            self.chunker = HierarchicalChunker(self.config.chunking)
        else:
            self.chunker = WordChunker(self.config.chunking)
        
        if self.config.vector_store == "weaviate":
            self.vector_store = WeaviateVectorStore(self.config.weaviate)
        else:
            self.vector_store = FaissVectorStore()
            
        self.retriever = Retriever(
            self.embedder, self.vector_store, self.config.retrieval
        )

        # Backend selection
        if self.config.backend == "openai":
            from .generator import OpenAIGenerator
            self.generator = OpenAIGenerator(
                api_key=self.config.api_key,
                model=self.config.model,
            )

        elif self.config.backend == "groq":
            from .groq_generator import GroqGenerator
            self.generator = GroqGenerator(
                api_key=self.config.api_key,
                model=self.config.model,
            )

        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")

        self._documents: List[str] = []

    def add_documents(self, documents: Iterable[str]) -> None:
        texts = ensure_texts(documents)
        self._documents.extend(texts)

        chunks, metadata = self.chunker.chunk(texts)
        logger.info("Chunked %d documents into %d chunks", len(texts), len(chunks))

        self.retriever.add(chunks, metadata)

    def ask(self, question: str) -> str:
        """Answer a question using retrieval + generation."""

        results = self.retriever.retrieve(question)
        contexts = [chunk for chunk, _ in results]

        context_block = build_context(contexts)
        prompt = build_prompt(question, contexts)

        logger.info("Built prompt with context length %d", len(context_block))

        result = self.generator.generate(prompt)

        if hasattr(result, "__iter__") and not isinstance(result, str):
            for token in result:
                yield token
        else:
            yield result

    def get_index_size(self) -> int:
        if hasattr(self.vector_store, "chunks"):
            return len(self.vector_store.chunks)
        return 0

    @property
    def documents(self) -> List[str]:
        return list(self._documents)