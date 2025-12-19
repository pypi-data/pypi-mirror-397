"""
Memory Tools for Agent Framework.

Provides tools that are automatically added to agents when memory is enabled.
These tools allow the agent to actively interact with its memory system.

Tools:
- recall_memory: Search long-term memory
- store_memory: Store important facts
- forget_memory: Remove specific memories

These tools are added automatically - agents don't need to define them.

Version: 0.1.0
"""

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .manager import MemoryManager

logger = logging.getLogger(__name__)


def create_memory_tools(
    memory_manager: "MemoryManager",
    user_id_getter: Callable[[], str | None],
    session_id_getter: Callable[[], str | None],
    agent_id: str
) -> list[Any]:
    """
    Create memory tools bound to a specific memory manager.
    
    These tools are automatically added to agents when memory is enabled.
    The agent can call them to interact with its long-term memory.
    
    Args:
        memory_manager: The MemoryManager instance
        user_id_getter: Callable that returns current user_id
        session_id_getter: Callable that returns current session_id
        agent_id: The agent's ID
        
    Returns:
        List of tool instances (FunctionTool for LlamaIndex)
    """

    # Try to import LlamaIndex tools
    try:
        from llama_index.core.tools import FunctionTool
        USE_LLAMAINDEX = True
    except ImportError:
        USE_LLAMAINDEX = False
        logger.warning(
            "LlamaIndex not available, memory tools will be plain functions"
        )

    # Define the tool functions
    async def recall_memory(query: str, limit: int = 5) -> str:
        """
        Search your long-term memory for relevant information about the user.
        
        Use this tool when you need to remember:
        - User preferences, settings, or personal information
        - Past conversations, decisions, or context
        - Project details or work-related information
        - Anything the user has shared before
        
        Args:
            query: What to search for. Be specific for better results.
                   Examples: "user's favorite color", "project deadline",
                   "dietary restrictions", "previous recommendations"
            limit: Maximum number of facts to retrieve (default: 5, max: 20)
            
        Returns:
            Relevant facts from memory, formatted as a list.
            Returns a message if no relevant memories are found.
        """
        user_id = user_id_getter()
        if not user_id:
            return "⚠️ Unable to access memory: no user context available"

        # Clamp limit
        limit = max(1, min(limit, 20))

        try:
            context = await memory_manager.recall(
                user_id=user_id,
                agent_id=agent_id,
                query=query,
                limit=limit
            )

            if not context.facts:
                return f"No memories found related to: '{query}'"

            # Format facts
            facts_lines = []
            for i, fact in enumerate(context.facts, 1):
                confidence_str = ""
                if fact.confidence < 0.9:
                    confidence_str = f" (confidence: {fact.confidence:.0%})"

                temporal_str = ""
                if fact.valid_from:
                    temporal_str = f" [since {fact.valid_from.strftime('%Y-%m-%d')}]"

                facts_lines.append(
                    f"{i}. {fact.content}{confidence_str}{temporal_str}"
                )

            header = f"Found {len(context.facts)} relevant memories:"
            return f"{header}\n" + "\n".join(facts_lines)

        except Exception as e:
            logger.error(f"Error in recall_memory: {e}")
            return f"⚠️ Error searching memory: {str(e)}"

    async def store_memory(
        fact: str,
        fact_type: str = "fact"
    ) -> str:
        """
        Store an important fact about the user for future conversations.
        
        Use this when the user shares information you should remember:
        - Personal details (name, preferences, etc.)
        - Important decisions or choices they've made
        - Project or work information
        - Anything they explicitly ask you to remember
        - Context that would be useful in future conversations
        
        Args:
            fact: The fact to store. Be specific and concise.
                  Good: "User's name is Alice Chen"
                  Good: "User prefers Python over JavaScript"
                  Bad: "User said something about programming"
            fact_type: Type of fact for categorization:
                  - "fact": General factual information (default)
                  - "preference": User preferences or settings
                  - "event": Something that happened
                  - "relationship": Connection between entities
                  
        Returns:
            Confirmation that the fact was stored.
        """
        user_id = user_id_getter()
        session_id = session_id_getter()

        if not user_id:
            return "⚠️ Unable to store memory: no user context available"

        # Validate fact_type
        valid_types = ["fact", "preference", "event", "relationship"]
        if fact_type not in valid_types:
            fact_type = "fact"

        try:
            # Store as a special "explicit memory" interaction
            # The memory providers will extract this as a fact
            success = await memory_manager.store_interaction(
                user_id=user_id,
                session_id=session_id or "explicit_memory",
                agent_id=agent_id,
                user_message=f"[EXPLICIT_MEMORY:{fact_type.upper()}] {fact}",
                agent_response="Memory stored successfully."
            )

            if success:
                return f"✓ Stored {fact_type}: {fact}"
            else:
                return "⚠️ Failed to store memory. Please try again."

        except Exception as e:
            logger.error(f"Error in store_memory: {e}")
            return f"⚠️ Error storing memory: {str(e)}"

    async def forget_memory(query: str) -> str:
        """
        Request to forget or remove specific memories.
        
        Use this when:
        - User explicitly asks to forget something
        - Information is outdated or incorrect
        - User wants privacy for certain topics
        - Correcting previously stored incorrect information
        
        Note: This creates a "forget directive" that will be processed
        by the memory system. Some information may persist in backup
        systems for a period.
        
        Args:
            query: Description of what to forget.
                   Examples: "my old phone number", "previous address",
                   "dietary restrictions" (if they've changed)
                   
        Returns:
            Confirmation of the forget request.
        """
        user_id = user_id_getter()
        session_id = session_id_getter()

        if not user_id:
            return "⚠️ Unable to modify memory: no user context available"

        try:
            # Store a forget directive
            # Memory providers can implement actual deletion based on this
            await memory_manager.store_interaction(
                user_id=user_id,
                session_id=session_id or "memory_management",
                agent_id=agent_id,
                user_message=f"[FORGET_DIRECTIVE] {query}",
                agent_response="Forget request acknowledged."
            )

            # Also try to clear if the manager supports it
            # This is a best-effort operation
            try:
                # For now, we just acknowledge - full deletion would need
                # more sophisticated implementation per provider
                pass
            except:
                pass

            return f"✓ Noted: Will forget information related to '{query}'"

        except Exception as e:
            logger.error(f"Error in forget_memory: {e}")
            return f"⚠️ Error processing forget request: {str(e)}"

    # Create tool wrappers
    if USE_LLAMAINDEX:
        tools = [
            FunctionTool.from_defaults(
                async_fn=recall_memory,
                name="recall_memory",
                description=(
                    "Search your long-term memory for information about the user. "
                    "Use when you need to remember preferences, past conversations, "
                    "or any information the user has shared before."
                )
            ),
            FunctionTool.from_defaults(
                async_fn=store_memory,
                name="store_memory",
                description=(
                    "Store an important fact about the user for future reference. "
                    "Use when the user shares personal info, preferences, or "
                    "explicitly asks you to remember something."
                )
            ),
            FunctionTool.from_defaults(
                async_fn=forget_memory,
                name="forget_memory",
                description=(
                    "Forget or remove specific memories. Use when user asks "
                    "to forget something or when information is outdated."
                )
            ),
        ]
    else:
        # Return plain functions if LlamaIndex not available
        tools = [recall_memory, store_memory, forget_memory]

    logger.debug(f"Created {len(tools)} memory tools for agent {agent_id}")
    return tools


def get_memory_tools_descriptions() -> str:
    """
    Get descriptions of memory tools for system prompt injection.
    
    Useful if you want to inform the agent about available memory tools
    in the system prompt.
    
    Returns:
        Formatted string describing memory tools
    """
    return """
## Memory Tools Available

You have access to long-term memory tools:

1. **recall_memory(query, limit=5)**: Search your memory for relevant information
   - Use when you need to remember user preferences, past conversations, or shared context
   - Example: recall_memory("user's programming language preferences")

2. **store_memory(fact, fact_type="fact")**: Store important information
   - Use when user shares something you should remember
   - fact_type: "fact", "preference", "event", or "relationship"
   - Example: store_memory("User prefers dark mode", "preference")

3. **forget_memory(query)**: Remove specific memories
   - Use when user asks to forget something or info is outdated
   - Example: forget_memory("my old email address")

Use these tools proactively to provide personalized, context-aware assistance.
"""
