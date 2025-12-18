"""
Embedding generation utilities.

Provides wrapper for sentence transformers and embedding operations.
"""

import logging
from typing import List, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """
    Wrapper for generating embeddings using sentence transformers.
    
    Provides consistent interface for embedding generation across the library.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding generator.
        
        Args:
            model_name: Name of the sentence transformer model
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for embeddings. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        logger.info(
            f"EmbeddingGenerator initialized - model: {model_name}, "
            f"dim: {self.embedding_dim}"
        )
    
    def encode(
        self,
        text: str | List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        Generate embeddings for text.
        
        Args:
            text: Single text or list of texts
            batch_size: Batch size for processing
            show_progress: Whether to show progress bar
        
        Returns:
            Numpy array of embeddings
        """
        try:
            embeddings = self.model.encode(
                text,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def encode_queries(
        self,
        queries: List[str],
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generate embeddings for search queries.
        
        Args:
            queries: List of query strings
            batch_size: Batch size for processing
        
        Returns:
            Numpy array of query embeddings
        """
        return self.encode(queries, batch_size=batch_size)
    
    def encode_documents(
        self,
        documents: List[str],
        batch_size: int = 32
    ) -> np.ndarray:
        """
        Generate embeddings for documents.
        
        Args:
            documents: List of document texts
            batch_size: Batch size for processing
        
        Returns:
            Numpy array of document embeddings
        """
        return self.encode(documents, batch_size=batch_size)
    
    def get_embedding_dimension(self) -> int:
        """Get the dimensionality of embeddings."""
        return self.embedding_dim
    
    def similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Cosine similarity score (0.0 to 1.0)
        """
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Reshape if needed
            if embedding1.ndim == 1:
                embedding1 = embedding1.reshape(1, -1)
            if embedding2.ndim == 1:
                embedding2 = embedding2.reshape(1, -1)
            
            similarity = cosine_similarity(embedding1, embedding2)[0][0]
            return float(similarity)
        
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            raise
