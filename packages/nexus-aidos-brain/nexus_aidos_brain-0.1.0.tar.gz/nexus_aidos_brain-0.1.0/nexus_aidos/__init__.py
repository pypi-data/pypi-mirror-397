"""
NEXUS-AIDOS-BRAIN: Core Conversational AI Engine for Nexus Ecosystem

A production-ready library for building intelligent conversational systems with:
- Conversational RAG (Retrieval-Augmented Generation)
- Multi-tier memory management
- Semantic caching
- Multi-agent orchestration
- Workspace isolation

Built on LangChain and LangGraph.
"""

__version__ = "0.1.0"
__author__ = "Nexus AI Hub Team"

from nexus_aidos.core.engine import NexusEngine
from nexus_aidos.core.pipeline import RAGPipeline
from nexus_aidos.config.settings import EngineConfig
from nexus_aidos.memory.redis_memory import RedisMemoryManager
from nexus_aidos.cache.semantic_cache import SemanticCache

__all__ = [
    'NexusEngine',
    'RAGPipeline',
    'EngineConfig',
    'RedisMemoryManager',
    'SemanticCache',
    '__version__',
]
