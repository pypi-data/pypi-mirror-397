"""
Semantic caching service for NEXUS-AIDOS-BRAIN.

Provides intelligent response caching with embedding-based similarity matching.
"""

import json
import hashlib
import time
import logging
import redis
from typing import Optional, Dict, Any, Tuple
import numpy as np

from nexus_aidos.retrieval.embeddings import EmbeddingGenerator
from nexus_aidos.utils.workspace import get_workspace_key

logger = logging.getLogger(__name__)


class SemanticCache:
    """
    Semantic caching service with Redis backend.
    
    Features:
    - Exact match caching for identical queries
    - Semantic similarity matching for similar queries
    - Workspace isolation
    - Configurable similarity threshold
    - TTL-based expiration
    """
    
    def __init__(
        self,
        redis_url: str,
        similarity_threshold: float = 0.85,
        embedding_model: str = "all-MiniLM-L6-v2",
        ttl: int = 2592000  # 30 days
    ):
        """
        Initialize semantic cache.
        
        Args:
            redis_url: Redis connection URL
            similarity_threshold: Minimum similarity score for cache hits (0.0-1.0)
            embedding_model: Embedding model for semantic matching
            ttl: Time-to-live in seconds for cached entries
        """
        self.redis_url = redis_url
        self.similarity_threshold = similarity_threshold
        self.ttl = ttl
        
        # Redis connection
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Embedding generator
        self.embedding_gen = EmbeddingGenerator(embedding_model)
        
        logger.info(
            f"SemanticCache initialized - threshold: {similarity_threshold}, "
            f"model: {embedding_model}"
        )
    
    def _generate_cache_key(
        self,
        query: str,
        workspace_id: str,
        endpoint_type: str = "chat"
    ) -> str:
        """
        Generate cache key for exact match.
        
        Args:
            query: Query string
            workspace_id: Workspace identifier
            endpoint_type: Type of endpoint (chat, completion, etc.)
        
        Returns:
            Cache key string
        """
        # Create hash of query for exact matching
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return get_workspace_key(workspace_id, f"cache:{endpoint_type}", query_hash)
    
    def _get_exact_match(
        self,
        cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get cached response by exact key match.
        
        Args:
            cache_key: Cache key
        
        Returns:
            Cached data or None
        """
        try:
            data = self.redis_client.get(cache_key)
            if not data:
                return None
            
            cached = json.loads(data)
            logger.info(f"Exact cache hit for key: {cache_key}")
            return cached
        
        except Exception as e:
            logger.error(f"Error getting exact match: {e}")
            return None
    
    def _find_semantic_match(
        self,
        query: str,
        workspace_id: str,
        endpoint_type: str = "chat"
    ) -> Tuple[Optional[Dict[str, Any]], float]:
        """
        Find semantically similar cached response.
        
        Args:
            query: Query string
            workspace_id: Workspace identifier
            endpoint_type: Type of endpoint
        
        Returns:
            Tuple of (cached_data, similarity_score)
        """
        try:
            # Generate query embedding
            query_emb = self.embedding_gen.encode(query)
            
            # Get all cache keys for this workspace and endpoint
            pattern = get_workspace_key(workspace_id, f"cache:{endpoint_type}", "*")
            keys = self.redis_client.keys(pattern)
            
            if not keys:
                logger.debug("No cached entries found for semantic matching")
                return None, 0.0
            
            best_match = None
            best_similarity = 0.0
            
            # Compare with each cached entry
            for key in keys:
                data = self.redis_client.get(key)
                if not data:
                    continue
                
                entry = json.loads(data)
                cached_emb = entry.get("embedding")
                
                if not cached_emb:
                    continue
                
                # Compute cosine similarity
                similarity = self.embedding_gen.similarity(
                    query_emb,
                    np.array(cached_emb)
                )
                
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match = entry
            
            # Check if best match meets threshold
            if best_similarity >= self.similarity_threshold:
                logger.info(
                    f"Semantic cache hit - similarity: {best_similarity:.4f}"
                )
                return best_match, best_similarity
            
            logger.debug(
                f"No semantic match above threshold "
                f"(best: {best_similarity:.4f}, threshold: {self.similarity_threshold})"
            )
            return None, best_similarity
        
        except Exception as e:
            logger.error(f"Error in semantic matching: {e}")
            return None, 0.0
    
    def get(
        self,
        query: str,
        workspace_id: str,
        endpoint_type: str = "chat"
    ) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        """
        Get cached response (tries exact match first, then semantic).
        
        Args:
            query: Query string
            workspace_id: Workspace identifier
            endpoint_type: Type of endpoint
        
        Returns:
            Tuple of (response_data, cache_type)
            cache_type is "exact", "semantic", or None
        """
        # Try exact match first
        cache_key = self._generate_cache_key(query, workspace_id, endpoint_type)
        exact = self._get_exact_match(cache_key)
        
        if exact:
            return exact.get("response"), "exact"
        
        # Try semantic match
        semantic, score = self._find_semantic_match(query, workspace_id, endpoint_type)
        
        if semantic:
            return semantic.get("response"), f"semantic ({score:.2f})"
        
        return None, None
    
    def store(
        self,
        query: str,
        response: Dict[str, Any],
        workspace_id: str,
        endpoint_type: str = "chat",
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store response in cache with embedding.
        
        Args:
            query: Query string
            response: Response data to cache
            workspace_id: Workspace identifier
            endpoint_type: Type of endpoint
            metadata: Optional metadata to store
        
        Returns:
            True if stored successfully
        """
        try:
            # Generate cache key and embedding
            cache_key = self._generate_cache_key(query, workspace_id, endpoint_type)
            embedding = self.embedding_gen.encode(query).tolist()
            
            # Prepare cache entry
            entry = {
                "query": query,
                "response": response,
                "embedding": embedding,
                "timestamp": time.time(),
                "workspace_id": workspace_id,
                "endpoint_type": endpoint_type,
            }
            
            if metadata:
                entry["metadata"] = metadata
            
            # Store in Redis with TTL
            self.redis_client.setex(
                cache_key,
                self.ttl,
                json.dumps(entry)
            )
            
            logger.info(f"Stored response in cache: {cache_key}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to store in cache: {e}")
            return False
    
    def clear_workspace(self, workspace_id: str) -> int:
        """
        Clear all cache entries for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            Number of entries deleted
        """
        try:
            pattern = get_workspace_key(workspace_id, "cache:*", "*")
            keys = self.redis_client.keys(pattern)
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries for workspace {workspace_id}")
                return deleted
            
            return 0
        
        except Exception as e:
            logger.error(f"Failed to clear workspace cache: {e}")
            return 0
    
    def get_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get cache statistics for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            Dictionary with cache statistics
        """
        try:
            pattern = get_workspace_key(workspace_id, "cache:*", "*")
            keys = self.redis_client.keys(pattern)
            
            return {
                "total_entries": len(keys),
                "workspace_id": workspace_id,
                "similarity_threshold": self.similarity_threshold,
                "ttl": self.ttl
            }
        
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
