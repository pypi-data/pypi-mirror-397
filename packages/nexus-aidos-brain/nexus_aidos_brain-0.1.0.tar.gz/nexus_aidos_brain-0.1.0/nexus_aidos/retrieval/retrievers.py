"""
Custom LangChain retrievers for document retrieval.

Provides flexible retriever implementations for various vector stores.
"""

import logging
from typing import List, Dict, Any, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun

logger = logging.getLogger(__name__)


class QdrantRetriever(BaseRetriever):
    """
    Custom LangChain retriever that wraps Qdrant vector store.
    
    This retriever integrates with an external RAG service or Qdrant client
    to fetch relevant documents based on semantic similarity.
    """
    
    qdrant_client: Any
    collection_name: str
    workspace_id: str
    embedding_model: Any
    top_k: int = 5
    threshold: float = 0.5
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        qdrant_client,
        collection_name: str,
        workspace_id: str,
        embedding_model,
        top_k: int = 5,
        threshold: float = 0.5,
        **kwargs
    ):
        """
        Initialize Qdrant retriever.
        
        Args:
            qdrant_client: Qdrant client instance
            collection_name: Name of the Qdrant collection
            workspace_id: Workspace ID for filtering documents
            embedding_model: Sentence transformer model for embeddings
            top_k: Number of documents to retrieve
            threshold: Similarity threshold for filtering results
        """
        super().__init__(
            qdrant_client=qdrant_client,
            collection_name=collection_name,
            workspace_id=workspace_id,
            embedding_model=embedding_model,
            top_k=top_k,
            threshold=threshold,
            **kwargs
        )
        logger.info(
            f"QdrantRetriever initialized - workspace: {workspace_id}, "
            f"top_k: {top_k}, threshold: {threshold}"
        )
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents from Qdrant.
        
        Args:
            query: Search query
            run_manager: Optional callback manager
        
        Returns:
            List of LangChain Document objects
        """
        logger.info(f"Retrieving documents for query: '{query[:100]}...'")
        
        try:
            # Generate query embedding
            query_vector = self.embedding_model.encode(query).tolist()
            
            # Search in Qdrant with workspace filter
            search_result = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter={
                    "must": [
                        {
                            "key": "workspace_id",
                            "match": {"value": self.workspace_id}
                        }
                    ]
                },
                limit=self.top_k,
                score_threshold=self.threshold
            )
            
            logger.info(f"Retrieved {len(search_result)} documents from Qdrant")
            
            # Convert to LangChain Documents
            docs = []
            for idx, result in enumerate(search_result):
                payload = result.payload
                doc = Document(
                    page_content=payload.get('text', ''),
                    metadata={
                        "filename": payload.get("filename", "unknown"),
                        "similarity": result.score,
                        "chunk_index": payload.get("chunk_index", 0),
                        "workspace_id": payload.get("workspace_id", ""),
                        "source": f"{payload.get('filename', 'unknown')} (chunk {payload.get('chunk_index', 0)})"
                    }
                )
                docs.append(doc)
                logger.info(
                    f"  Doc {idx+1}: {payload.get('filename')} "
                    f"(similarity: {result.score:.4f})"
                )
            
            return docs
        
        except Exception as e:
            logger.error(f"Error in QdrantRetriever: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []


class CustomRAGRetriever(BaseRetriever):
    """
    Custom LangChain retriever that wraps an existing RAG service.
    
    This retriever is designed to integrate with legacy RAG services
    that have a retrieve_context() method.
    """
    
    rag_service: Any
    workspace_id: str
    top_k: int = 5
    threshold: float = 0.5
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(
        self,
        rag_service,
        workspace_id: str,
        top_k: int = 5,
        threshold: float = 0.5,
        **kwargs
    ):
        """
        Initialize custom RAG retriever.
        
        Args:
            rag_service: Instance of RAGService with retrieve_context method
            workspace_id: Workspace ID for filtering documents
            top_k: Number of documents to retrieve
            threshold: Similarity threshold for filtering results
        """
        super().__init__(
            rag_service=rag_service,
            workspace_id=workspace_id,
            top_k=top_k,
            threshold=threshold,
            **kwargs
        )
        logger.info(
            f"CustomRAGRetriever initialized - workspace: {workspace_id}, "
            f"top_k: {top_k}, threshold: {threshold}"
        )
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> List[Document]:
        """
        Retrieve relevant documents using RAG service.
        
        Args:
            query: Search query
            run_manager: Optional callback manager
        
        Returns:
            List of LangChain Document objects
        """
        logger.info(f"Retrieving documents for query: '{query[:100]}...'")
        
        try:
            # Call RAG service retrieve_context method
            contexts = self.rag_service.retrieve_context(
                query=query,
                workspace_id=self.workspace_id,
                top_k=self.top_k,
                similarity_threshold=self.threshold
            )
            
            logger.info(f"Retrieved {len(contexts)} contexts from RAG service")
            
            # Convert to LangChain Documents
            docs = []
            for idx, ctx in enumerate(contexts):
                doc = Document(
                    page_content=ctx['text'],
                    metadata={
                        "filename": ctx.get("filename", "unknown"),
                        "similarity": ctx.get("similarity", 0.0),
                        "chunk_index": ctx.get("chunk_index", 0),
                        "source": f"{ctx.get('filename', 'unknown')} (chunk {ctx.get('chunk_index', 0)})"
                    }
                )
                docs.append(doc)
                logger.info(
                    f"  Doc {idx+1}: {ctx.get('filename')} "
                    f"(similarity: {ctx.get('similarity', 0):.4f})"
                )
            
            return docs
        
        except Exception as e:
            logger.error(f"Error in CustomRAGRetriever: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return []
