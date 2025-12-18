"""
RAG Pipeline - Conversational RAG with memory and caching.

Provides high-level interface for RAG operations.
"""

import logging
from typing import Dict, Any, Optional

from nexus_aidos.config import EngineConfig, RAGConfig
from nexus_aidos.retrieval.retrievers import CustomRAGRetriever, QdrantRetriever
from nexus_aidos.chains.rag_chain import ConversationalRAGChain
from nexus_aidos.memory.redis_memory import RedisMemoryManager
from nexus_aidos.cache.semantic_cache import SemanticCache

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    High-level RAG pipeline with conversation memory and caching.
    
    Provides simple interface for:
    - Document-aware question answering
    - Conversation context management
    - Response caching
    - Source tracking
    """
    
    def __init__(
        self,
        config: EngineConfig,
        rag_service: Any,
        workspace_id: str,
        model: str = "google/gemini-2.5-flash-lite",
        temperature: float = 0.7,
        top_k: int = 5,
        threshold: float = 0.5,
        memory_k: int = 3,
        use_prompt_enhancement: bool = True,
        use_cache: bool = True
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            config: Engine configuration
            rag_service: RAG service instance with retrieve_context method
            workspace_id: Workspace identifier
            model: LLM model to use
            temperature: LLM temperature
            top_k: Number of documents to retrieve
            threshold: Similarity threshold
            memory_k: Number of conversation turns
            use_prompt_enhancement: Enable query enhancement
            use_cache: Enable semantic caching
        """
        self.config = config
        self.workspace_id = workspace_id
        self.model = model
        self.use_cache = use_cache
        
        logger.info(f"Initializing RAGPipeline for workspace: {workspace_id}")
        
        # Initialize retriever
        self.retriever = CustomRAGRetriever(
            rag_service=rag_service,
            workspace_id=workspace_id,
            top_k=top_k,
            threshold=threshold
        )
        
        # Initialize conversational chain
        self.chain = ConversationalRAGChain(
            retriever=self.retriever,
            model=model,
            temperature=temperature,
            memory_k=memory_k,
            use_prompt_enhancement=use_prompt_enhancement,
            openrouter_api_key=config.openrouter_api_key
        )
        
        # Initialize cache if enabled
        if use_cache:
            self.cache = SemanticCache(
                redis_url=config.redis_url,
                similarity_threshold=config.cache_threshold
            )
            logger.info("Semantic cache enabled")
        else:
            self.cache = None
        
        # Initialize memory manager
        self.memory = RedisMemoryManager(
            redis_url=config.redis_url,
            openrouter_api_key=config.openrouter_api_key
        )
        
        logger.info("RAGPipeline initialized successfully")
    
    def ask(
        self,
        question: str,
        return_metadata: bool = False,
        bypass_cache: bool = False
    ) -> str | Dict[str, Any]:
        """
        Ask a question using RAG pipeline.
        
        Args:
            question: User question
            return_metadata: Return full metadata
            bypass_cache: Skip cache lookup/storage
        
        Returns:
            Answer string or metadata dict
        """
        try:
            # Check cache first
            if self.use_cache and not bypass_cache and self.cache:
                cached, cache_type = self.cache.get(
                    query=question,
                    workspace_id=self.workspace_id,
                    endpoint_type="rag"
                )
                
                if cached:
                    logger.info(f"Cache hit: {cache_type}")
                    if return_metadata:
                        return {
                            "answer": cached.get("answer", ""),
                            "cache_hit": cache_type,
                            "source_documents": cached.get("source_documents", []),
                            "num_sources": len(cached.get("source_documents", []))
                        }
                    return cached.get("answer", "")
            
            # Ask using chain
            response = self.chain.ask(question, return_metadata=True)
            
            # Store in cache
            if self.use_cache and not bypass_cache and self.cache:
                self.cache.store(
                    query=question,
                    response=response,
                    workspace_id=self.workspace_id,
                    endpoint_type="rag"
                )
            
            # Save to memory
            self.memory.save_turn(
                workspace_id=self.workspace_id,
                user_message=question,
                assistant_response=response.get("answer", "")
            )
            
            if return_metadata:
                return response
            return response.get("answer", "")
        
        except Exception as e:
            logger.error(f"Error in RAGPipeline.ask(): {e}")
            if return_metadata:
                return {
                    "answer": f"Error: {str(e)}",
                    "error": str(e),
                    "source_documents": [],
                    "num_sources": 0
                }
            return f"Error: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.chain.clear_memory()
        self.memory.clear_workspace_memory(self.workspace_id)
        logger.info(f"Cleared memory for workspace: {self.workspace_id}")
    
    def clear_cache(self):
        """Clear cache for this workspace."""
        if self.cache:
            deleted = self.cache.clear_workspace(self.workspace_id)
            logger.info(f"Cleared {deleted} cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "workspace_id": self.workspace_id,
            "model": self.model,
            "memory": self.chain.get_memory_stats(),
        }
        
        if self.cache:
            stats["cache"] = self.cache.get_stats(self.workspace_id)
        
        return stats
