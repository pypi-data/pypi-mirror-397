"""
LlamaIndex Memory Adapter

This module provides an adapter between the framework's SessionStorage
and LlamaIndex's Memory system, allowing seamless integration of conversation
history into LlamaIndex agents.

The adapter:
- Loads conversation history from SessionStorage
- Converts MessageData to LlamaIndex ChatMessage format
- Creates a Memory object that can be used with LlamaIndex agents
- Keeps memory synchronized with SessionStorage
- Supports model-specific cache keys for proper tokenization on model changes

Version: 0.2.0
"""

import logging
from typing import Optional, List
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.memory import ChatMemoryBuffer

from ..session.session_storage import SessionStorageInterface, MessageData

logger = logging.getLogger(__name__)

# Global memory cache shared across all adapter instances
# Cache key format: {user_id}:{session_id}:{model_name} or {user_id}:{session_id} for backward compat
_GLOBAL_MEMORY_CACHE: dict[str, ChatMemoryBuffer] = {}



class LlamaIndexMemoryAdapter:
    """
    Adapter that bridges SessionStorage and LlamaIndex Memory.
    
    This adapter loads conversation history from SessionStorage and creates
    a LlamaIndex Memory object that can be used with agents.
    """
    
    def __init__(self, session_storage: SessionStorageInterface):
        """
        Initialize the memory adapter.
        
        Args:
            session_storage: The session storage backend to use
        """
        self.session_storage = session_storage
        # Use global cache instead of instance cache
        self._memory_cache = _GLOBAL_MEMORY_CACHE
    
    def _build_cache_key(
        self, user_id: str, session_id: str, model_name: Optional[str] = None
    ) -> str:
        """
        Build a cache key for memory storage.
        
        Args:
            user_id: The user identifier
            session_id: The session identifier
            model_name: Optional model name for model-specific caching
            
        Returns:
            Cache key string in format {user_id}:{session_id}:{model_name}
            or {user_id}:{session_id} if model_name is None
        """
        if model_name:
            return f"{user_id}:{session_id}:{model_name}"
        return f"{user_id}:{session_id}"

    def _invalidate_other_model_caches(
        self, user_id: str, session_id: str, current_model: str
    ) -> int:
        """
        Invalidate cache entries for the same session but different models.
        
        When a model changes mid-session, old cache entries with different
        tokenization should be invalidated to ensure proper memory handling.
        
        Args:
            user_id: The user identifier
            session_id: The session identifier
            current_model: The current model (entries for this model are kept)
            
        Returns:
            Number of cache entries invalidated
        """
        prefix = f"{user_id}:{session_id}:"
        current_key = f"{user_id}:{session_id}:{current_model}"
        legacy_key = f"{user_id}:{session_id}"
        
        keys_to_remove = []
        for key in self._memory_cache.keys():
            # Match keys for this session but different models
            if key.startswith(prefix) and key != current_key:
                keys_to_remove.append(key)
            # Also remove legacy key without model suffix
            elif key == legacy_key:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self._memory_cache[key]
            logger.info(f"🗑️ Invalidated cache entry: {key}")
        
        return len(keys_to_remove)

    async def get_memory_for_session(
        self, 
        session_id: str,
        user_id: str,
        model_name: Optional[str] = None,
        token_limit: int = 30000
    ) -> ChatMemoryBuffer:
        """
        Get or create a Memory object for a session.
        
        This method:
        1. Checks if memory is already cached (with model-specific key)
        2. Invalidates old cache entries for same session with different models
        3. If not cached, loads conversation history from SessionStorage
        4. Converts messages to LlamaIndex format
        5. Creates a Memory object with the history
        
        Args:
            session_id: The session identifier
            user_id: The user identifier
            model_name: Optional model name for model-specific caching.
                       When provided, cache key includes model for proper
                       tokenization handling on model changes.
            token_limit: Maximum tokens for short-term memory
            
        Returns:
            Memory object ready to use with LlamaIndex agents
        """
        # Build cache key (includes model if provided)
        cache_key = self._build_cache_key(user_id, session_id, model_name)
        
        # Invalidate old cache entries for different models if model is specified
        if model_name:
            invalidated = self._invalidate_other_model_caches(user_id, session_id, model_name)
            if invalidated > 0:
                logger.info(
                    f"🔄 Invalidated {invalidated} old cache entries for session {session_id} "
                    f"due to model change to {model_name}"
                )
        
        # Check cache
        if cache_key in self._memory_cache:
            logger.info(f"✅ Using cached memory for session {session_id} (model: {model_name or 'default'})")
            return self._memory_cache[cache_key]
        
        # Create new memory
        logger.info(f"🆕 Creating new memory for session {session_id} (model: {model_name or 'default'})")
        memory = ChatMemoryBuffer.from_defaults(
            token_limit=token_limit,
        )
        
        # Load conversation history from SessionStorage
        try:
            message_history = await self.session_storage.get_conversation_history(
                session_id=session_id,
                limit=100  # Load last 100 messages
            )
            
            if message_history:
                # Convert to LlamaIndex ChatMessage format
                chat_messages = self._convert_to_chat_messages(message_history)
                
                # Put messages into memory
                if chat_messages:
                    memory.put_messages(chat_messages)
                    logger.info(f"📚 Loaded {len(chat_messages)} messages into memory for session {session_id}")
                    logger.info(f"📝 First message: {chat_messages[0].content[:50]}..." if chat_messages else "")
                    
                    # Sanitize to ensure no empty tool_calls arrays
                    self.sanitize_memory_buffer(memory)
            else:
                logger.info(f"⚠️ No existing history for session {session_id}, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading conversation history for session {session_id}: {e}")
            # Continue with empty memory rather than failing
        
        # Cache the memory
        self._memory_cache[cache_key] = memory
        
        return memory
    
    def _convert_to_chat_messages(self, message_data_list: List[MessageData]) -> List[ChatMessage]:
        """
        Convert MessageData objects to LlamaIndex ChatMessage objects.
        
        Args:
            message_data_list: List of MessageData from SessionStorage
            
        Returns:
            List of ChatMessage objects for LlamaIndex
        """
        chat_messages = []
        
        for msg_data in message_data_list:
            # Determine role
            if msg_data.role == "user":
                role = MessageRole.USER
            elif msg_data.role == "assistant":
                role = MessageRole.ASSISTANT
            elif msg_data.role == "system":
                role = MessageRole.SYSTEM
            else:
                logger.warning(f"Unknown role '{msg_data.role}', defaulting to USER")
                role = MessageRole.USER
            
            # Get content - prefer text_content, fallback to response_text_main
            content = msg_data.text_content or msg_data.response_text_main or ""
            
            # Create ChatMessage with clean additional_kwargs
            # OpenAI rejects empty tool_calls arrays, so we never include them
            chat_message = ChatMessage(
                role=role,
                content=content,
                additional_kwargs={}
            )
            
            chat_messages.append(chat_message)
        
        return chat_messages

    def _sanitize_chat_messages(self, messages: List[ChatMessage]) -> List[ChatMessage]:
        """
        Sanitize ChatMessage objects to remove problematic additional_kwargs.
        
        OpenAI rejects messages with empty tool_calls arrays. This method
        cleans up any such problematic fields from existing messages.
        
        Args:
            messages: List of ChatMessage objects to sanitize
            
        Returns:
            List of sanitized ChatMessage objects
        """
        sanitized = []
        for msg in messages:
            # Check if additional_kwargs has problematic fields
            additional_kwargs = msg.additional_kwargs or {}
            
            # Remove empty tool_calls arrays (OpenAI rejects these)
            if 'tool_calls' in additional_kwargs:
                if not additional_kwargs['tool_calls']:
                    # Empty array - remove it
                    additional_kwargs = {
                        k: v for k, v in additional_kwargs.items()
                        if k != 'tool_calls'
                    }
                    logger.debug(f"Removed empty tool_calls from message with role {msg.role}")
            
            # Create new message with sanitized kwargs
            sanitized_msg = ChatMessage(
                role=msg.role,
                content=msg.content,
                additional_kwargs=additional_kwargs
            )
            sanitized.append(sanitized_msg)
        
        return sanitized

    def sanitize_memory_buffer(self, memory: ChatMemoryBuffer) -> None:
        """
        Sanitize all messages in a ChatMemoryBuffer in-place.
        
        This removes empty tool_calls arrays that OpenAI rejects.
        Call this before using memory with a different model.
        
        Args:
            memory: The ChatMemoryBuffer to sanitize
        """
        try:
            # Access the internal chat store
            chat_store = memory.chat_store
            store_key = memory.chat_store_key
            
            if hasattr(chat_store, 'store') and store_key in chat_store.store:
                messages = chat_store.store[store_key]
                sanitized = self._sanitize_chat_messages(messages)
                chat_store.store[store_key] = sanitized
                logger.info(f"🧹 Sanitized {len(messages)} messages in memory buffer")
        except Exception as e:
            logger.warning(f"Could not sanitize memory buffer: {e}")
    
    def clear_cache(
        self,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        model_name: Optional[str] = None
    ):
        """
        Clear memory cache.
        
        Args:
            session_id: If provided, clear only this session
            user_id: If provided, clear all sessions for this user
            model_name: If provided with session_id and user_id, clear only
                       the cache for that specific model. If not provided,
                       clears all model variants for the session.
        """
        if session_id and user_id:
            if model_name:
                # Clear specific model cache
                cache_key = self._build_cache_key(user_id, session_id, model_name)
                if cache_key in self._memory_cache:
                    del self._memory_cache[cache_key]
                    logger.info(f"Cleared memory cache for session {session_id} model {model_name}")
            else:
                # Clear all model variants for this session
                prefix = f"{user_id}:{session_id}"
                keys_to_remove = [
                    k for k in self._memory_cache.keys()
                    if k == prefix or k.startswith(f"{prefix}:")
                ]
                for key in keys_to_remove:
                    del self._memory_cache[key]
                logger.info(
                    f"Cleared memory cache for session {session_id} "
                    f"({len(keys_to_remove)} entries including all model variants)"
                )
        elif user_id:
            # Clear all sessions for user
            keys_to_remove = [k for k in self._memory_cache.keys() if k.startswith(f"{user_id}:")]
            for key in keys_to_remove:
                del self._memory_cache[key]
            logger.info(f"Cleared memory cache for user {user_id} ({len(keys_to_remove)} sessions)")
        else:
            # Clear all
            self._memory_cache.clear()
            logger.info("Cleared all memory cache")
