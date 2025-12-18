# Hayagriva – Modular Retrieval-Augmented Generation Framework

![Hayagriva](hayagriva.png)

सर्वविद्याप्रसूत्यर्थं हयग्रीवोऽवतारतः
वेदान् संरक्ष्य जगतां हितकारी सदा भवेत्

"To restore and protect all knowledge, Hayagriva has manifested. He safeguards the Vedas for the good of the world."

Hayagriva is a lightweight, modular Retrieval-Augmented Generation (RAG) framework designed to combine large language models with efficient document retrieval. It focuses on accuracy, grounded responses, and ease of integration. The framework supports programmatic use, making it suitable for developers, researchers, and production-oriented teams.

---

## Key Features

### Retrieval-Augmented Generation

Built around a clean abstraction that connects LLMs with contextual retrieval to produce grounded answers.

Supports major LLM providers including Groq and OpenAI, with planned expansion to Anthropic, Gemini, DeepSeek, and local GGUF-based models.

### Advanced Retrieval Strategies

Hayagriva supports multiple retrieval strategies to ensure the most relevant context is found:

* **Vector Search**: Dense retrieval using semantic embeddings.
* **BM25**: Sparse retrieval using keyword matching.
* **Hybrid Search**: Combines vector and keyword search with configurable weighting (alpha).

### Advanced Chunking Strategies

Hayagriva supports multiple chunking strategies to optimize retrieval:

* **Word (Default)**: Simple sliding window based on word count.
* **Recursive**: Splits text by separators (e.g., paragraphs, newlines) to preserve semantic structure.
* **Semantic**: Uses embeddings to split text based on topic shifts (requires an embedding model).
* **Hierarchical**: Creates parent chunks for context and child chunks for precise retrieval.

### Modular Vector Stores

Choose the vector store that fits your needs:

* **FAISS**: Lightweight, in-memory vector store for quick prototyping and small datasets.
* **Weaviate**: Production-grade vector database support for scalability and persistence.

### Flexible Document Handling

Documents can be added programmatically or ingested through the CLI. Supports:

* Text files
* Markdown files
* Directory-level ingestion

Automatic chunking and metadata assignment provide efficient retrieval.

---

## Installation

### Default (Lightweight)
Installs core libraries only. Suitable if you bring your own embeddings or vector store.
```bash
pip install hayagriva
```

### CPU Support (Recommended for Local Testing)
Installs `sentence-transformers` and `faiss-cpu`.
```bash
pip install "hayagriva[cpu]"
```

### GPU Support
Installs `sentence-transformers` and `faiss-gpu`.
```bash
pip install "hayagriva[cuda]"
```

---

## Python Usage

### Basic Example (FAISS + Vector Search)

```python
from hayagriva import Hayagriva, HayagrivaConfig

config = HayagrivaConfig(
    backend="groq",
    api_key="YOUR_GROQ_KEY",
    model="llama-3.1-8b-instant",
)

rag = Hayagriva(config)
rag.add_documents(["Hayagriva restores forgotten knowledge."])

response = "".join(rag.ask("Who retrieved the lost Vedas?"))
print(response)
```

### Advanced Example (Weaviate + Hybrid Search)

```python
from hayagriva import Hayagriva, HayagrivaConfig
from hayagriva.config import WeaviateConfig

# Configure Weaviate
weaviate_config = WeaviateConfig(
    url="http://localhost:8080",
    index_name="HayagrivaDocs"
)

# Configure Hayagriva with Weaviate and Hybrid Search
config = HayagrivaConfig(
    backend="groq",
    api_key="YOUR_GROQ_KEY",
    vector_store="weaviate",
    weaviate=weaviate_config,
    retrieval=type("RetrievalConfig", (), {
        "strategy": "hybrid",  # "vector", "bm25", or "hybrid"
        "alpha": 0.5,          # 0.5 = equal weight
        "top_k": 4
    })(),
    chunking=type("ChunkingConfig", (), {
        "strategy": "recursive",  # "word", "recursive", "semantic", "hierarchical"
        "chunk_size": 500,
        "overlap": 50
    })()
)

rag = Hayagriva(config)
rag.add_documents(["Hayagriva is an avatar of Vishnu."])

for token in rag.ask("Who is Hayagriva?"):
    print(token, end="", flush=True)
```

---

## CLI Usage

### Ingest Files

```bash
hayagriva ingest ./docs
```

### Query

```bash
hayagriva query "What is RAG?"
```

---

## Requirements

* Python 3.10+
* sentence-transformers
* faiss-cpu
* weaviate-client
* API key for Groq or OpenAI

---

## Roadmap

### Expanded LLM Provider Support

* Anthropic Claude
* Google Gemini
* DeepSeek
* Local GGUF models and llama.cpp

### Additional Vector Database Integration

* Pinecone
* ChromaDB
* Additional pluggable backends

### Memory-Augmented Chat

* Multi-turn memory
* Embedding-based long-term memory
* Summarization-based memory compression

---

## Use Cases

* Building retrieval-augmented assistants
* Knowledge-base and enterprise search
* Research and benchmarking of RAG pipelines
* Lightweight production deployments
* Internal document Q&A systems

---

## Contributing

Contributions to model integrations, retrieval modules, and documentation are welcome. Submit issues or pull requests.

---

## Support

For questions, bugs, or feature requests, open an issue on the project repository.
