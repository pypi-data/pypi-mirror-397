"""
Redis-backed conversation memory manager for NEXUS-AIDOS-BRAIN.

Provides persistent conversation memory with workspace isolation.
Suppresses LangChain deprecation warnings as per project standards.
"""

import os
import logging
import warnings
from typing import Dict, List, Optional

# Suppress LangChain deprecation warnings (stable API usage)
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', message='.*langchain.*')

from langchain.memory import ConversationSummaryMemory, ConversationBufferWindowMemory, CombinedMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

# Set tokenizers parallelism to avoid fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logger = logging.getLogger(__name__)


class RedisMemoryManager:
    """
    Manages conversation memory using Redis with LangChain integration.
    
    Features:
    - Workspace-isolated conversation history
    - Combined buffer and summary memory
    - Direct Redis persistence (avoids duplicate saves)
    - Configurable window size and TTL
    """
    
    def __init__(
        self,
        redis_url: str,
        openrouter_api_key: Optional[str] = None,
        summarization_model: str = "google/gemini-2.5-flash-lite"
    ):
        """
        Initialize Redis memory manager.
        
        Args:
            redis_url: Redis connection URL
            openrouter_api_key: OpenRouter API key for summarization
            summarization_model: Model to use for conversation summarization
        """
        self.redis_url = redis_url
        self.openrouter_api_key = openrouter_api_key or os.getenv("OPENROUTER_API_KEY")
        self.summarization_model = summarization_model
        
        logger.info(f"Initialized RedisMemoryManager with Redis: {self.redis_url}")
    
    def get_memory_for_workspace(
        self,
        workspace_id: str,
        use_summary: bool = True,
        window_size: int = 5
    ) -> CombinedMemory:
        """
        Get or create memory instance for a workspace.
        
        Args:
            workspace_id: Workspace identifier
            use_summary: Whether to use conversation summarization
            window_size: Number of recent messages to keep verbatim
        
        Returns:
            CombinedMemory instance with Redis-backed storage
        """
        try:
            # Create Redis message history for this workspace
            redis_history = RedisChatMessageHistory(
                session_id=f"workspace:{workspace_id}",
                url=self.redis_url,
                key_prefix="langchain:chat_history:",
            )
            
            # Create window memory for recent messages
            window_memory = ConversationBufferWindowMemory(
                k=window_size,
                chat_memory=redis_history,
                return_messages=True,
                memory_key="recent_history",
                input_key="input",
                output_key="output"
            )
            
            memories = [window_memory]
            
            # Add summarization memory if enabled
            if use_summary and self.openrouter_api_key:
                try:
                    llm = ChatOpenAI(
                        model=self.summarization_model,
                        temperature=0,
                        openai_api_key=self.openrouter_api_key,
                        openai_api_base="https://openrouter.ai/api/v1",
                        default_headers={
                            "HTTP-Referer": "https://nexusaihub.com",
                            "X-Title": "Nexus AI Hub"
                        }
                    )
                    
                    summary_memory = ConversationSummaryMemory(
                        llm=llm,
                        chat_memory=redis_history,
                        return_messages=True,
                        memory_key="conversation_summary",
                        input_key="input",
                        output_key="output"
                    )
                    
                    memories.append(summary_memory)
                    logger.info(f"Created summarization memory for workspace {workspace_id}")
                except Exception as e:
                    logger.warning(f"Failed to create summarization memory: {e}")
            
            # Combine memories
            combined_memory = CombinedMemory(memories=memories)
            logger.info(f"Created memory for workspace {workspace_id} (window={window_size}, summary={use_summary})")
            
            return combined_memory
        
        except Exception as e:
            logger.error(f"Failed to create memory for workspace {workspace_id}: {e}")
            raise
    
    def save_turn(
        self,
        workspace_id: str,
        user_message: str,
        assistant_response: str,
        ttl: int = 2592000  # 30 days
    ) -> bool:
        """
        Save a conversation turn directly to Redis.
        
        IMPORTANT: Saves directly to avoid duplicate storage when using CombinedMemory.
        
        Args:
            workspace_id: Workspace identifier
            user_message: User's message
            assistant_response: Assistant's response
            ttl: Time-to-live in seconds
        
        Returns:
            True if saved successfully
        """
        try:
            redis_history = RedisChatMessageHistory(
                session_id=f"workspace:{workspace_id}",
                url=self.redis_url,
                key_prefix="langchain:chat_history:",
                ttl=ttl
            )
            
            # Add messages
            redis_history.add_message(HumanMessage(content=user_message))
            redis_history.add_message(AIMessage(content=assistant_response))
            
            logger.info(f"Saved conversation turn for workspace {workspace_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save conversation for workspace {workspace_id}: {e}")
            return False
    
    def get_conversation_context(
        self,
        workspace_id: str,
        use_summary: bool = True,
        window_size: int = 5
    ) -> Dict[str, any]:
        """
        Retrieve conversation context for a workspace.
        
        Args:
            workspace_id: Workspace identifier
            use_summary: Whether to include summary
            window_size: Number of recent messages
        
        Returns:
            Dictionary with conversation context
        """
        try:
            memory = self.get_memory_for_workspace(
                workspace_id=workspace_id,
                use_summary=use_summary,
                window_size=window_size
            )
            
            context = memory.load_memory_variables({})
            logger.info(f"Retrieved context for workspace {workspace_id}")
            
            return context
        
        except Exception as e:
            logger.error(f"Failed to retrieve context for workspace {workspace_id}: {e}")
            return {}
    
    def get_formatted_context(
        self,
        workspace_id: str,
        use_summary: bool = True,
        window_size: int = 5,
        include_recent: bool = True
    ) -> str:
        """
        Get formatted conversation context as a string.
        
        Args:
            workspace_id: Workspace identifier
            use_summary: Whether to include summary
            window_size: Number of recent messages
            include_recent: Whether to include recent message history
        
        Returns:
            Formatted context string
        """
        try:
            context = self.get_conversation_context(
                workspace_id=workspace_id,
                use_summary=use_summary,
                window_size=window_size
            )
            
            formatted_parts = []
            
            # Add conversation summary
            if use_summary and "conversation_summary" in context:
                summary = context["conversation_summary"]
                if summary:
                    formatted_parts.append(f"Conversation Summary:\n{summary}")
            
            # Add recent message history
            if include_recent and "recent_history" in context:
                recent = context["recent_history"]
                if recent:
                    recent_messages = []
                    for msg in recent:
                        role = msg.type if hasattr(msg, 'type') else 'unknown'
                        content = msg.content if hasattr(msg, 'content') else str(msg)
                        recent_messages.append(f"{role.capitalize()}: {content}")
                    
                    if recent_messages:
                        formatted_parts.append(f"Recent Conversation:\n" + "\n".join(recent_messages))
            
            formatted_context = "\n\n".join(formatted_parts)
            logger.info(f"Formatted context for workspace {workspace_id}: {len(formatted_context)} chars")
            
            return formatted_context
        
        except Exception as e:
            logger.error(f"Failed to format context for workspace {workspace_id}: {e}")
            return ""
    
    def clear_workspace_memory(self, workspace_id: str) -> bool:
        """
        Clear all conversation memory for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            True if cleared successfully
        """
        try:
            redis_history = RedisChatMessageHistory(
                session_id=f"workspace:{workspace_id}",
                url=self.redis_url,
                key_prefix="langchain:chat_history:"
            )
            
            redis_history.clear()
            logger.info(f"Cleared memory for workspace {workspace_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Failed to clear memory for workspace {workspace_id}: {e}")
            return False
    
    def get_message_count(self, workspace_id: str) -> int:
        """
        Get the number of messages stored for a workspace.
        
        Args:
            workspace_id: Workspace identifier
        
        Returns:
            Number of messages
        """
        try:
            redis_history = RedisChatMessageHistory(
                session_id=f"workspace:{workspace_id}",
                url=self.redis_url,
                key_prefix="langchain:chat_history:"
            )
            
            messages = redis_history.messages
            count = len(messages)
            
            logger.info(f"Workspace {workspace_id} has {count} messages")
            return count
        
        except Exception as e:
            logger.error(f"Failed to get message count for workspace {workspace_id}: {e}")
            return 0
