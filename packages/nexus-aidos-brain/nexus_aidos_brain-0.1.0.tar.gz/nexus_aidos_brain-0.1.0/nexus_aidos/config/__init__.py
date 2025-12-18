"""
Configuration management for NEXUS-AIDOS-BRAIN.

Provides configuration classes for engine initialization and component setup.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class EngineConfig:
    """
    Main configuration class for NexusEngine.
    
    Attributes:
        redis_url: Redis connection URL for caching and memory
        qdrant_url: Qdrant vector store URL
        qdrant_api_key: Qdrant API key
        openrouter_api_key: OpenRouter API key for LLM access
        embedding_model: Sentence transformer model for embeddings
        cache_threshold: Similarity threshold for semantic cache (0.0-1.0)
        chunk_size: Token size for document chunking
        chunk_overlap: Token overlap between chunks
        memory_window_size: Number of recent messages to keep in memory
        default_model: Default LLM model to use
        default_temperature: Default temperature for LLM
        enable_logging: Enable detailed logging
    """
    
    # Required configurations
    redis_url: str
    qdrant_url: str
    qdrant_api_key: str
    openrouter_api_key: str
    
    # Optional configurations with defaults
    embedding_model: str = "all-MiniLM-L6-v2"
    cache_threshold: float = 0.85
    chunk_size: int = 350
    chunk_overlap: int = 50
    memory_window_size: int = 5
    default_model: str = "google/gemini-2.5-flash-lite"
    default_temperature: float = 0.7
    enable_logging: bool = True
    
    # Advanced settings
    max_retries: int = 3
    timeout: int = 30
    redis_ttl: int = 2592000  # 30 days
    
    def __post_init__(self):
        """Validate configuration after initialization."""
        if self.cache_threshold < 0.0 or self.cache_threshold > 1.0:
            raise ValueError("cache_threshold must be between 0.0 and 1.0")
        
        if self.chunk_size < 50:
            raise ValueError("chunk_size must be at least 50 tokens")
        
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        if self.memory_window_size < 1:
            raise ValueError("memory_window_size must be at least 1")
        
        if self.enable_logging:
            self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging for the library."""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        logging.basicConfig(
            level=logging.INFO,
            format=log_format
        )
        logger.info("NEXUS-AIDOS-BRAIN logging configured")
    
    @classmethod
    def from_env(cls, **kwargs) -> 'EngineConfig':
        """
        Create configuration from environment variables.
        
        Environment variables:
            REDIS_URL: Redis connection URL
            QDRANT_URL: Qdrant vector store URL
            QDRANT_API_KEY: Qdrant API key
            OPENROUTER_API_KEY: OpenRouter API key
            EMBEDDING_MODEL: Embedding model name
            CACHE_SIMILARITY_THRESHOLD: Cache similarity threshold
            CHUNK_SIZE: Document chunk size
            CHUNK_OVERLAP: Chunk overlap size
            MEMORY_WINDOW_SIZE: Memory window size
        
        Args:
            **kwargs: Override environment variables
        
        Returns:
            EngineConfig instance
        
        Raises:
            ValueError: If required environment variables are missing
        """
        config = {
            'redis_url': os.getenv('REDIS_URL'),
            'qdrant_url': os.getenv('QDRANT_URL'),
            'qdrant_api_key': os.getenv('QDRANT_API_KEY'),
            'openrouter_api_key': os.getenv('OPENROUTER_API_KEY'),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2'),
            'cache_threshold': float(os.getenv('CACHE_SIMILARITY_THRESHOLD', '0.85')),
            'chunk_size': int(os.getenv('CHUNK_SIZE', '350')),
            'chunk_overlap': int(os.getenv('CHUNK_OVERLAP', '50')),
            'memory_window_size': int(os.getenv('MEMORY_WINDOW_SIZE', '5')),
        }
        
        # Check required fields
        required = ['redis_url', 'qdrant_url', 'qdrant_api_key', 'openrouter_api_key']
        missing = [k for k in required if not config.get(k)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing.upper())}")
        
        # Override with provided kwargs
        config.update(kwargs)
        
        return cls(**config)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'redis_url': self.redis_url,
            'qdrant_url': self.qdrant_url,
            'qdrant_api_key': '***',  # Masked for security
            'openrouter_api_key': '***',  # Masked for security
            'embedding_model': self.embedding_model,
            'cache_threshold': self.cache_threshold,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'memory_window_size': self.memory_window_size,
            'default_model': self.default_model,
            'default_temperature': self.default_temperature,
        }


@dataclass
class RAGConfig:
    """Configuration for RAG pipeline."""
    
    workspace_id: str
    model: str = "google/gemini-2.5-flash-lite"
    temperature: float = 0.7
    top_k: int = 5
    threshold: float = 0.5
    memory_k: int = 3
    use_prompt_enhancement: bool = True
    
    def __post_init__(self):
        """Validate RAG configuration."""
        if self.top_k < 1:
            raise ValueError("top_k must be at least 1")
        
        if self.threshold < 0.0 or self.threshold > 1.0:
            raise ValueError("threshold must be between 0.0 and 1.0")
        
        if self.memory_k < 1:
            raise ValueError("memory_k must be at least 1")


@dataclass
class MemoryConfig:
    """Configuration for memory management."""
    
    workspace_id: str
    use_summary: bool = True
    window_size: int = 5
    ttl: int = 2592000  # 30 days
    
    def __post_init__(self):
        """Validate memory configuration."""
        if self.window_size < 1:
            raise ValueError("window_size must be at least 1")
        
        if self.ttl < 1:
            raise ValueError("ttl must be at least 1 second")


@dataclass
class CacheConfig:
    """Configuration for semantic cache."""
    
    similarity_threshold: float = 0.85
    ttl: int = 2592000  # 30 days
    enable_exact_match: bool = True
    enable_semantic_match: bool = True
    
    def __post_init__(self):
        """Validate cache configuration."""
        if self.similarity_threshold < 0.0 or self.similarity_threshold > 1.0:
            raise ValueError("similarity_threshold must be between 0.0 and 1.0")
        
        if self.ttl < 1:
            raise ValueError("ttl must be at least 1 second")
