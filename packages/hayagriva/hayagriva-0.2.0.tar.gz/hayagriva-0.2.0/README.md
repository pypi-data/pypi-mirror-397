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

Configurable pipelines for:

* Embedding generation
* Vector indexing with FAISS
* Context-aware prompting
* Streamed or batched inference

### Modular and Lightweight Architecture

Hayagriva is intentionally minimal. Each component can be used independently:

* Document ingestion
* Embedding and indexing
* Query execution
* Reranking (planned)
* Model backends

This modularity allows seamless integration into applications, agent frameworks, backend systems, or research workflows.

### Flexible Document Handling

Documents can be added programmatically or ingested through the CLI. Supports:

* Text files
* Markdown files
* Directory-level ingestion

Automatic chunking and metadata assignment provide efficient retrieval.

### Streamlined CLI

Hayagriva provides a CLI to:

* Ingest files and build indexes
* Perform quick queries

---

## Installation

```bash
pip install hayagriva
```

---

## Python Usage

### Basic Example

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

### Streaming Example

```python
for token in rag.ask("Explain retrieval-augmented generation"):
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
* API key for Groq or OpenAI

---

## Roadmap

### Expanded LLM Provider Support

* Anthropic Claude
* Google Gemini
* DeepSeek
* Local GGUF models and llama.cpp

### External Vector Database Integration

* Pinecone
* Weaviate
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
