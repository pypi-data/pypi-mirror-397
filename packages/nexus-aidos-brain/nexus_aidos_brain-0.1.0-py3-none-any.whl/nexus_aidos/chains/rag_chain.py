"""
Conversational RAG chain implementation for NEXUS-AIDOS-BRAIN.

Provides LangChain-based conversational retrieval with memory and context awareness.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

logger = logging.getLogger(__name__)


def build_prompt_query(user_question: str, chat_history: List[Tuple[str, str]]) -> str:
    """
    Build a prompt-style query that includes conversation context.
    This is done WITHOUT an LLM call - just string formatting.
    
    Args:
        user_question: Current user question
        chat_history: List of (user_msg, assistant_msg) tuples
    
    Returns:
        Enhanced query string for retrieval
    """
    # If no history, just return the question
    if not chat_history or len(chat_history) == 0:
        logger.debug("No chat history - using raw question")
        return user_question
    
    # Build history summary from last 3 turns
    recent_history = chat_history[-3:] if len(chat_history) > 3 else chat_history
    history_lines = []
    
    for user_msg, assistant_msg in recent_history:
        history_lines.append(f"User: {user_msg}")
        history_lines.append(f"Assistant: {assistant_msg}")
    
    history_summary = "\n".join(history_lines)
    
    # Create prompt-enhanced query
    prompt_query = f"""You are retrieving information from a knowledge base.
Use the previous conversation only if it clarifies the current question.
Otherwise, focus on the latest query.

Previous conversation (optional):
{history_summary}

User's current question:
{user_question}

Return only information directly relevant to the user's question."""
    
    logger.debug(f"Built prompt query with {len(recent_history)} conversation turns")
    return prompt_query


class ConversationalRAGChain:
    """
    Conversational RAG chain using LangChain.
    
    Features:
    - Custom retriever integration
    - Conversation memory
    - Query enhancement
    - Source tracking
    """
    
    def __init__(
        self,
        retriever,
        model: str = "google/gemini-2.5-flash-lite",
        temperature: float = 0.7,
        memory_k: int = 3,
        use_prompt_enhancement: bool = True,
        openrouter_api_key: Optional[str] = None
    ):
        """
        Initialize conversational RAG chain.
        
        Args:
            retriever: LangChain retriever instance
            model: LLM model to use
            temperature: LLM temperature
            memory_k: Number of conversation turns to keep
            use_prompt_enhancement: Whether to enhance queries with context
            openrouter_api_key: OpenRouter API key
        """
        self.retriever = retriever
        self.model = model
        self.memory_k = memory_k
        self.use_prompt_enhancement = use_prompt_enhancement
        
        logger.info(f"Initializing ConversationalRAGChain")
        logger.info(f"  Model: {model}")
        logger.info(f"  Memory: {memory_k} turns")
        logger.info(f"  Prompt enhancement: {use_prompt_enhancement}")
        
        # Initialize LLM
        api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OpenRouter API key is required")
        
        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            model_kwargs={
                "extra_headers": {
                    "HTTP-Referer": "https://nexusaihub.com",
                    "X-Title": "Nexus AI Hub"
                }
            }
        )
        logger.info(f"LLM initialized: {model}")
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
            k=memory_k
        )
        logger.info(f"Memory initialized with k={memory_k}")
        
        # Build conversational retrieval chain
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.retriever,
            memory=self.memory,
            return_source_documents=True,
            verbose=True,
            output_key="answer"
        )
        logger.info("ConversationalRetrievalChain initialized")
    
    def _get_chat_history_tuples(self) -> List[Tuple[str, str]]:
        """
        Extract chat history as list of (user, assistant) tuples.
        
        Returns:
            List of conversation tuples
        """
        try:
            messages = self.memory.chat_memory.messages
            history = []
            user_msg = None
            
            for msg in messages:
                if msg.type == "human":
                    user_msg = msg.content
                elif msg.type == "ai" and user_msg is not None:
                    history.append((user_msg, msg.content))
                    user_msg = None
            
            return history
        
        except Exception as e:
            logger.warning(f"Failed to extract chat history: {e}")
            return []
    
    def ask(
        self,
        question: str,
        return_metadata: bool = False
    ) -> str | Dict[str, Any]:
        """
        Ask a question using conversational RAG.
        
        Args:
            question: User question
            return_metadata: If True, return dict with answer and metadata
        
        Returns:
            Answer string or dict with answer and metadata
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"New question: {question}")
        logger.info(f"{'='*80}")
        
        try:
            # Build prompt-enhanced query if enabled
            query = question
            if self.use_prompt_enhancement:
                chat_history = self._get_chat_history_tuples()
                query = build_prompt_query(question, chat_history)
                logger.info(f"Prompt-enhanced query built (length: {len(query)} chars)")
            
            # Run the chain
            response = self.qa_chain({"question": query})
            
            answer = response.get("answer", "")
            source_docs = response.get("source_documents", [])
            
            logger.info(f"\nAnswer generated:")
            logger.info(f"  Length: {len(answer)} chars")
            logger.info(f"  Sources: {len(source_docs)} documents")
            
            # Log source details
            if source_docs:
                logger.info(f"\nSource documents:")
                for idx, doc in enumerate(source_docs):
                    filename = doc.metadata.get("filename", "unknown")
                    similarity = doc.metadata.get("similarity", 0.0)
                    logger.info(f"  {idx+1}. {filename} (similarity: {similarity:.4f})")
            
            # Return based on metadata flag
            if return_metadata:
                return {
                    "answer": answer,
                    "source_documents": [
                        {
                            "filename": doc.metadata.get("filename", "unknown"),
                            "similarity": doc.metadata.get("similarity", 0.0),
                            "chunk_index": doc.metadata.get("chunk_index", 0),
                            "text": doc.page_content
                        }
                        for doc in source_docs
                    ],
                    "num_sources": len(source_docs),
                    "query_enhanced": self.use_prompt_enhancement,
                    "original_question": question
                }
            
            return answer
        
        except Exception as e:
            logger.error(f"Error in ask(): {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            if return_metadata:
                return {
                    "answer": f"Error: {str(e)}",
                    "source_documents": [],
                    "num_sources": 0,
                    "error": str(e)
                }
            return f"Error: {str(e)}"
    
    def clear_memory(self):
        """Clear conversation memory."""
        self.memory.clear()
        logger.info("Conversation memory cleared")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dict with memory info
        """
        try:
            messages = self.memory.chat_memory.messages
            return {
                "total_messages": len(messages),
                "conversation_turns": len(messages) // 2,
                "memory_k": self.memory_k,
                "has_history": len(messages) > 0
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "total_messages": 0,
                "conversation_turns": 0,
                "memory_k": self.memory_k,
                "has_history": False,
                "error": str(e)
            }
