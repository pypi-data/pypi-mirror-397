"""
NexusEngine - Main conversational AI engine for NEXUS-AIDOS-BRAIN.

Provides unified interface for all AI operations including chat, RAG, memory, and caching.
"""

import logging
from typing import Dict, Any, Optional, List

from nexus_aidos.config import EngineConfig
from nexus_aidos.core.pipeline import RAGPipeline
from nexus_aidos.memory.redis_memory import RedisMemoryManager
from nexus_aidos.cache.semantic_cache import SemanticCache
from nexus_aidos.utils.workspace import validate_workspace_id

logger = logging.getLogger(__name__)


class NexusEngine:
    """
    Main conversational AI engine for Nexus ecosystem.
    
    Orchestrates:
    - Conversation management
    - RAG pipelines
    - Memory persistence
    - Semantic caching
    - Multi-workspace isolation
    
    This is the primary entry point for all AI operations in the Nexus system.
    """
    
    def __init__(self, config: EngineConfig):
        """
        Initialize Nexus Engine.
        
        Args:
            config: Engine configuration
        """
        self.config = config
        
        logger.info("=" * 80)
        logger.info("Initializing NEXUS-AIDOS-BRAIN Engine")
        logger.info("=" * 80)
        logger.info(f"Configuration: {config.to_dict()}")
        
        # Initialize core components
        self.memory_manager = RedisMemoryManager(
            redis_url=config.redis_url,
            openrouter_api_key=config.openrouter_api_key
        )
        logger.info("✓ Memory Manager initialized")
        
        self.cache = SemanticCache(
            redis_url=config.redis_url,
            similarity_threshold=config.cache_threshold,
            ttl=config.redis_ttl
        )
        logger.info("✓ Semantic Cache initialized")
        
        # Store for active RAG pipelines (workspace-based)
        self._rag_pipelines: Dict[str, RAGPipeline] = {}
        
        logger.info("=" * 80)
        logger.info("NEXUS-AIDOS-BRAIN Engine initialized successfully")
        logger.info("=" * 80)
    
    def chat(
        self,
        message: str,
        workspace_id: str,
        use_rag: bool = False,
        use_cache: bool = True,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Main chat interface.
        
        Args:
            message: User message
            workspace_id: Workspace identifier
            use_rag: Enable RAG for this request
            use_cache: Enable caching
            model: Override default model
            temperature: Override default temperature
            **kwargs: Additional parameters
        
        Returns:
            Response dictionary with answer and metadata
        """
        # Validate workspace
        if not validate_workspace_id(workspace_id):
            raise ValueError(f"Invalid workspace_id: {workspace_id}")
        
        logger.info(f"\n{'='*80}")
        logger.info(f"Chat Request - Workspace: {workspace_id}")
        logger.info(f"Message: {message[:100]}...")
        logger.info(f"RAG: {use_rag}, Cache: {use_cache}")
        logger.info(f"{'='*80}")
        
        try:
            # Check cache first
            if use_cache:
                cached, cache_type = self.cache.get(
                    query=message,
                    workspace_id=workspace_id,
                    endpoint_type="chat"
                )
                
                if cached:
                    logger.info(f"✓ Cache hit: {cache_type}")
                    return {
                        "answer": cached.get("answer", ""),
                        "cache_hit": cache_type,
                        "workspace_id": workspace_id
                    }
            
            # Use RAG if enabled
            if use_rag:
                rag_service = kwargs.get("rag_service")
                if not rag_service:
                    raise ValueError("rag_service is required when use_rag=True")
                
                # Get or create RAG pipeline for workspace
                if workspace_id not in self._rag_pipelines:
                    self._rag_pipelines[workspace_id] = RAGPipeline(
                        config=self.config,
                        rag_service=rag_service,
                        workspace_id=workspace_id,
                        model=model or self.config.default_model,
                        temperature=temperature or self.config.default_temperature,
                        use_cache=use_cache
                    )
                
                pipeline = self._rag_pipelines[workspace_id]
                response = pipeline.ask(message, return_metadata=True)
                
                return {
                    "answer": response.get("answer", ""),
                    "source_documents": response.get("source_documents", []),
                    "num_sources": response.get("num_sources", 0),
                    "workspace_id": workspace_id,
                    "rag_enabled": True
                }
            
            # Simple chat without RAG
            # This would typically call an LLM directly
            # For now, return a placeholder response
            answer = "Chat without RAG not fully implemented. Please enable use_rag=True or integrate with LLM service."
            
            # Save to memory
            self.memory_manager.save_turn(
                workspace_id=workspace_id,
                user_message=message,
                assistant_response=answer
            )
            
            # Cache response
            if use_cache:
                self.cache.store(
                    query=message,
                    response={"answer": answer},
                    workspace_id=workspace_id,
                    endpoint_type="chat"
                )
            
            return {
                "answer": answer,
                "workspace_id": workspace_id,
                "rag_enabled": False
            }
        
        except Exception as e:
            logger.error(f"Error in chat(): {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "answer": f"Error: {str(e)}",
                "error": str(e),
                "workspace_id": workspace_id
            }
    
    def get_conversation_context(
        self,
        workspace_id: str,
        window_size: int = 5,
        use_summary: bool = True
    ) -> str:
        """
        Get formatted conversation context for a workspace.
        
        Args:
            workspace_id: Workspace identifier
            window_size: Number of recent messages
            use_summary: Include conversation summary
        
        Returns:
            Formatted context string
        """
        return self.memory_manager.get_formatted_context(
            workspace_id=workspace_id,
            window_size=window_size,
            use_summary=use_summary
        )
    
    def clear_workspace_memory(self, workspace_id: str) -> bool:
        """
        Clear all memory for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            True if successful
        """
        # Clear memory manager
        success = self.memory_manager.clear_workspace_memory(workspace_id)
        
        # Clear RAG pipeline if exists
        if workspace_id in self._rag_pipelines:
            self._rag_pipelines[workspace_id].clear_memory()
            del self._rag_pipelines[workspace_id]
        
        logger.info(f"Cleared memory for workspace: {workspace_id}")
        return success
    
    def clear_workspace_cache(self, workspace_id: str) -> int:
        """
        Clear all cache for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            Number of entries deleted
        """
        deleted = self.cache.clear_workspace(workspace_id)
        
        # Clear pipeline cache if exists
        if workspace_id in self._rag_pipelines:
            self._rag_pipelines[workspace_id].clear_cache()
        
        logger.info(f"Cleared {deleted} cache entries for workspace: {workspace_id}")
        return deleted
    
    def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get statistics for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "workspace_id": workspace_id,
            "memory": {
                "message_count": self.memory_manager.get_message_count(workspace_id)
            },
            "cache": self.cache.get_stats(workspace_id)
        }
        
        # Add RAG pipeline stats if exists
        if workspace_id in self._rag_pipelines:
            stats["rag_pipeline"] = self._rag_pipelines[workspace_id].get_stats()
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all components.
        
        Returns:
            Health status dictionary
        """
        health = {
            "engine": "healthy",
            "components": {
                "memory_manager": "healthy",
                "cache": "healthy",
            },
            "config": self.config.to_dict()
        }
        
        try:
            # Test Redis connection
            self.cache.redis_client.ping()
            health["components"]["redis"] = "healthy"
        except Exception as e:
            health["components"]["redis"] = f"unhealthy: {str(e)}"
            health["engine"] = "degraded"
        
        return health
