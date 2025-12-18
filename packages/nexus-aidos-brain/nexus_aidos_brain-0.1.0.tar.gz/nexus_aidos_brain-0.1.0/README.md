# NEXUS-AIDOS-BRAIN 🧠

**The Core Conversational AI Engine for the Nexus Ecosystem**

NEXUS-AIDOS-BRAIN is a production-ready Python library that provides the foundational AI capabilities for building intelligent conversational systems. Built on LangChain and LangGraph, it offers a modular, extensible architecture for implementing RAG (Retrieval-Augmented Generation), memory management, semantic caching, and multi-agent workflows.

## 🌟 Features

### Core Capabilities
- **🔗 Conversational RAG Pipeline**: Context-aware document retrieval with conversation memory
- **🧠 Multi-tier Memory Management**: Redis-backed conversation history with buffer and summary modes
- **⚡ Semantic Caching**: Intelligent response caching with embedding-based similarity matching
- **🎯 Custom Retrievers**: Flexible retrieval architecture supporting multiple vector stores (Qdrant)
- **🤖 Agent Orchestration**: LangGraph-based multi-agent workflows with state management
- **📊 Workspace Isolation**: Multi-tenant support with workspace-based data segregation

### Advanced Features
- **Query Enhancement**: Prompt-style context injection without additional LLM calls
- **Source Tracking**: Complete provenance tracking for retrieved documents
- **Configurable Chunking**: Token-based text chunking with overlap for optimal retrieval
- **OpenRouter Integration**: Support for 200+ LLM models via OpenRouter
- **Production Ready**: Comprehensive logging, error handling, and monitoring

## 🏗️ Architecture

```
nexus_aidos/
├── core/              # Core conversational engine
│   ├── engine.py      # Main conversational engine
│   └── pipeline.py    # RAG pipeline orchestration
├── memory/            # Memory management
│   ├── redis_memory.py    # Redis-backed conversation memory
│   └── buffer_memory.py   # Buffer and summary memory
├── retrieval/         # Document retrieval
│   ├── retrievers.py      # Custom retriever implementations
│   └── embeddings.py      # Embedding generation
├── cache/             # Caching services
│   ├── semantic_cache.py  # Semantic similarity caching
│   └── exact_cache.py     # Exact match caching
├── chains/            # LangChain components
│   ├── rag_chain.py       # Conversational RAG chain
│   └── query_transform.py # Query transformation
├── config/            # Configuration management
│   └── settings.py        # Configuration classes
└── utils/             # Utilities
    ├── logging.py         # Logging utilities
    └── workspace.py       # Workspace utilities
```

## 🚀 Quick Start

### Installation

```bash
pip install -e ./NEXUS-AIDOS-BRAIN
```

### Basic Usage

```python
from nexus_aidos import NexusEngine
from nexus_aidos.config import EngineConfig

# Initialize the engine
config = EngineConfig(
    redis_url="redis://localhost:6379",
    qdrant_url="https://your-qdrant-instance.com",
    qdrant_api_key="your-api-key",
    openrouter_api_key="your-openrouter-key"
)

engine = NexusEngine(config)

# Simple conversation
response = engine.chat(
    message="What is the revenue growth?",
    workspace_id="workspace_123"
)
print(response["answer"])
```

### RAG-Enhanced Conversation

```python
from nexus_aidos import RAGPipeline

# Initialize RAG pipeline
rag = RAGPipeline(
    workspace_id="workspace_123",
    model="gpt-4o",
    top_k=5,
    threshold=0.5
)

# Ask questions with context
response = rag.ask(
    "What were the key findings?",
    return_metadata=True
)

print(f"Answer: {response['answer']}")
print(f"Sources: {len(response['source_documents'])} documents")
```

## 📖 Documentation

- [Full API Reference](docs/API.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [Integration Guide](docs/INTEGRATION.md)
- [Examples](examples/)

## 🏢 Integration with NEXUSBRAIN

This library is designed to integrate seamlessly with the NEXUSBRAIN project:

```python
# In your Flask app (server/app.py)
from nexus_aidos import NexusEngine
from nexus_aidos.config import EngineConfig

# Initialize engine
config = EngineConfig.from_env()
nexus_engine = NexusEngine(config)

@app.route('/api/chat', methods=['POST'])
def chat():
    workspace_id = request.user.get('workspace_id')
    message = request.json.get('message')
    
    response = nexus_engine.chat(
        message=message,
        workspace_id=workspace_id,
        use_rag=True,
        use_cache=True
    )
    
    return jsonify(response)
```

---

**Made with ❤️ by the Nexus AI Hub Team**
