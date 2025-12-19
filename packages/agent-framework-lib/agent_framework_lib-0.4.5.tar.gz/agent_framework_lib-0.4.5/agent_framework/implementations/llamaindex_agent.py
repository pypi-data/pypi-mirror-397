"""
LlamaIndex-Based Agent Implementation

This implementation provides LlamaIndex-specific functionality:
- Session/config handling
- State management via LlamaIndex Context (serialize/deserialize)
- Non-streaming and streaming message processing
- Streaming event formatting aligned with modern UI expectations

Note: This implementation constructs a concrete LlamaIndex agent.
Subclasses must implement get_agent_prompt(), get_agent_tools(), and initialize_agent().
"""
from __future__ import annotations

from typing import Any, Dict, Optional, List, AsyncGenerator, Union
import json
from datetime import datetime
import logging

from ..core.base_agent import BaseAgent
from ..core.agent_interface import (
    StructuredAgentInput,
    StructuredAgentOutput,
    TextOutputPart,
    TextOutputStreamPart,
    AgentConfig,
)
from ..core.model_clients import client_factory
from ..utils.special_blocks import parse_special_blocks_from_text

logger = logging.getLogger(__name__)


class LlamaIndexAgent(BaseAgent):
    """
    Concrete implementation of BaseAgent for LlamaIndex framework.
    
    For a complete guide on creating LlamaIndex agents, see:
    - docs/CREATING_AGENTS.md - Comprehensive agent creation guide
    - examples/simple_agent.py - Basic LlamaIndex agent example
    - examples/agent_with_file_storage.py - Agent with file upload/download
    - examples/agent_with_mcp.py - Agent with MCP server integration
    - docs/TOOLS_AND_MCP_GUIDE.md - Adding tools and MCP servers

    Subclasses must provide:
    - get_agent_prompt() -> str
    - get_agent_tools() -> List[callable]
    - async initialize_agent(model_name: str, system_prompt: str, tools: List[callable], **kwargs) -> None
    - create_fresh_context() -> Any
    - serialize_context(ctx: Any) -> Dict[str, Any]
    - deserialize_context(state: Dict[str, Any]) -> Any
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        description: str,
        default_model: Optional[str] = None,
    ):
        """
        Initialize the LlamaIndex agent with required identity information.
        
        Args:
            agent_id: Unique identifier for the agent (used for session isolation)
            name: Human-readable name of the agent
            description: Description of the agent's purpose and capabilities
            default_model: Optional default model for backward compatibility.
                          When set, this model will be used if no model_preference
                          is provided in the request, bypassing the ModelRouter.
            
        Raises:
            ValueError: If agent_id, name, or description is empty
        """
        # LlamaIndex-specific runtime
        self._agent_instance: Optional[Any] = None
        # Memory management
        self._session_storage: Optional[Any] = None
        self._memory_adapter: Optional[Any] = None
        self._current_memory: Optional[Any] = None
        self._current_session_id: Optional[str] = None
        self._current_user_id: Optional[str] = None
        # Model tracking for change detection and backward compatibility
        self._current_model: Optional[str] = None
        self._default_model: Optional[str] = default_model
        super().__init__(agent_id=agent_id, name=name, description=description)
    
    def create_llm(
        self,
        model_name: str = None,
        agent_config: AgentConfig = None,
        **override_params
    ) -> Any:
        """
        Helper method to create a LlamaIndex LLM using the ModelClientFactory.
        
        This method simplifies LLM creation in initialize_agent() by handling
        provider-specific imports and parameter compatibility automatically.
        
        Example usage in initialize_agent():
            llm = self.create_llm(model_name, agent_config)
            self._agent_instance = ReActAgent.from_tools(
                tools=tools,
                llm=llm,
                system_prompt=system_prompt
            )
        
        Args:
            model_name: Name of the model (e.g., "gpt-4", "claude-3-opus")
            agent_config: Optional agent configuration with overrides
            **override_params: Additional parameters to override defaults
            
        Returns:
            Configured LlamaIndex LLM instance (OpenAI, Anthropic, or Gemini)
        """
        return client_factory.create_llamaindex_llm(
            model_name=model_name,
            agent_config=agent_config,
            **override_params
        )
    
    def set_session_storage(self, session_storage: Any) -> None:
        """
        Set the session storage backend for memory management.
        
        This should be called by the server/framework to provide access
        to conversation history for memory loading.
        
        Args:
            session_storage: SessionStorageInterface instance
        """
        self._session_storage = session_storage
        if session_storage:
            from .llamaindex_memory_adapter import LlamaIndexMemoryAdapter
            self._memory_adapter = LlamaIndexMemoryAdapter(session_storage)
            logger.info("Session storage and memory adapter configured")
    
    async def _load_memory_for_session(
        self, session_id: str, user_id: str, model_name: Optional[str] = None
    ) -> Optional[Any]:
        """
        Load memory for a specific session.
        
        Args:
            session_id: Session identifier
            user_id: User identifier
            model_name: Optional model name for model-specific caching.
                       When provided, ensures proper tokenization for the model.
            
        Returns:
            Memory object or None if not available
        """
        if not self._memory_adapter:
            logger.debug("No memory adapter available, memory disabled")
            return None
        
        try:
            memory = await self._memory_adapter.get_memory_for_session(
                session_id=session_id,
                user_id=user_id,
                model_name=model_name
            )
            logger.info(f"Loaded memory for session {session_id} (model: {model_name or 'default'})")
            return memory
        except Exception as e:
            logger.error(f"Failed to load memory for session {session_id}: {e}")
            return None

    # ----- Abstract hooks to implement in subclass -----
    def get_agent_prompt(self) -> str:  # pragma: no cover - abstract
        raise NotImplementedError

    def get_agent_tools(self) -> List[callable]:  # pragma: no cover - abstract
        raise NotImplementedError

    def _convert_to_function_tools(self, tools: List[callable]) -> List[Any]:
        """
        Convert callable tools to LlamaIndex FunctionTool instances.
        
        This ensures proper tool registration with:
        - Function name as tool name
        - Function docstring as tool description
        - Proper parameter schema inference
        
        Args:
            tools: List of callable functions to convert
            
        Returns:
            List of FunctionTool instances
        """
        from llama_index.core.tools import FunctionTool
        
        function_tools = []
        for tool in tools:
            if isinstance(tool, FunctionTool):
                # Already a FunctionTool, use as-is
                function_tools.append(tool)
            elif callable(tool):
                # Convert callable to FunctionTool
                tool_name = getattr(tool, "__name__", "unknown_tool")
                tool_description = getattr(tool, "__doc__", None) or f"Tool: {tool_name}"
                
                function_tool = FunctionTool.from_defaults(
                    fn=tool,
                    name=tool_name,
                    description=tool_description.strip()
                )
                function_tools.append(function_tool)
                logger.debug(f"Converted tool '{tool_name}' to FunctionTool with description: {tool_description[:100]}...")
            else:
                logger.warning(f"Skipping non-callable tool: {tool}")
        
        logger.info(f"Converted {len(function_tools)} tools to FunctionTool instances")
        return function_tools

    async def initialize_agent(
        self,
        model_name: str,
        system_prompt: str,
        tools: List[callable],
        **kwargs
    ) -> None:
        """
        Initialize the LlamaIndex agent with FunctionAgent (default implementation).
        
        This default implementation creates a FunctionAgent with the provided tools.
        Tools are automatically converted to FunctionTool instances with proper
        names and descriptions extracted from the function metadata.
        
        Subclasses can override this method to use different agent types or configurations.
        
        Default implementation:
            - Creates LLM using self.create_llm()
            - Converts tools to FunctionTool instances
            - Creates FunctionAgent with tools and system prompt
            - Stores agent in self._agent_instance
        
        To customize, override this method in your subclass:
            async def initialize_agent(self, model_name, system_prompt, tools, **kwargs):
                llm = self.create_llm(model_name)
                # Create your custom agent type
                self._agent_instance = YourCustomAgent(...)
        
        Args:
            model_name: Name of the model to use
            system_prompt: System prompt for the agent
            tools: List of callable tools for the agent (will be converted to FunctionTool)
            **kwargs: Additional configuration options
        """
        from llama_index.core.agent.workflow import FunctionAgent
        
        # Use the helper method to create LLM with automatic provider detection
        llm = self.create_llm(model_name)
        
        # Convert callable tools to FunctionTool instances
        function_tools = self._convert_to_function_tools(tools)
        
        # Create FunctionAgent with the FunctionTool instances
        self._agent_instance = FunctionAgent(
            tools=function_tools,
            llm=llm,
            system_prompt=system_prompt,
            verbose=kwargs.get('verbose', True)
        )
        
        logger.info(f"Initialized FunctionAgent with {len(function_tools)} FunctionTool(s)")
        
        # Provide default implementation of _run_agent_stream_internal for FunctionAgent
        # Subclasses can override if they use a different agent type
        if not hasattr(self, '_run_agent_stream_internal_impl'):
            self._run_agent_stream_internal_impl = self._default_run_agent_stream
    
    def _default_run_agent_stream(self, query: str, ctx: Any, **kwargs) -> Any:
        """
        Default implementation for running FunctionAgent with memory support.
        
        Args:
            query: User query
            ctx: Context object
            **kwargs: Additional arguments including optional 'memory'
        """
        # Extract memory if provided
        memory = kwargs.get('memory')
        
        # Run agent with or without memory
        if memory:
            return self._agent_instance.run(user_msg=query, ctx=ctx, memory=memory)
        else:
            return self._agent_instance.run(user_msg=query, ctx=ctx)

    def create_fresh_context(self) -> Any:
        """
        Create a fresh LlamaIndex Context.
        
        Default implementation works for standard LlamaIndex agents.
        Override only if you need custom context initialization.
        
        Returns:
            Fresh Context instance for the agent
        """
        from llama_index.core.workflow import Context
        return Context(self._agent_instance)

    def serialize_context(self, ctx: Any) -> Dict[str, Any]:
        """
        Serialize the context for state persistence.
        
        Default implementation uses JsonSerializer for standard LlamaIndex contexts.
        Override only if you need custom serialization logic.
        
        Args:
            ctx: Context object to serialize
            
        Returns:
            Dictionary representation of the context
        """
        from llama_index.core.workflow import JsonSerializer
        return ctx.to_dict(serializer=JsonSerializer())

    def deserialize_context(self, state: Dict[str, Any]) -> Any:
        """
        Deserialize the context from saved state.
        
        Default implementation uses JsonSerializer for standard LlamaIndex contexts.
        Override only if you need custom deserialization logic.
        
        Args:
            state: Dictionary representation of the context
            
        Returns:
            Restored Context instance
        """
        from llama_index.core.workflow import Context, JsonSerializer
        return Context.from_dict(self._agent_instance, state, serializer=JsonSerializer())
    
    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        """
        Configure session and load memory for the session.
        
        This override loads conversation history from SessionStorage
        when the session changes.
        
        Args:
            session_configuration: Configuration dict with user_id, session_id, etc.
        """
        # Extract session info
        user_id = session_configuration.get('user_id')
        session_id = session_configuration.get('session_id')
        
        # Check if session changed
        session_changed = (
            session_id != self._current_session_id or
            user_id != self._current_user_id
        )
        
        if session_changed and session_id and user_id:
            logger.info(f"🔄 Session changed to {session_id} for user {user_id}, loading memory")
            self._current_session_id = session_id
            self._current_user_id = user_id
            
            # Load memory for this session (with model if available)
            self._current_memory = await self._load_memory_for_session(
                session_id, user_id, self._current_model
            )
            if self._current_memory:
                logger.info(f"✅ Memory loaded successfully for session {session_id}")
            else:
                logger.warning(f"⚠️ No memory loaded for session {session_id}")
        
        # Call parent configure_session
        await super().configure_session(session_configuration)

    async def configure_session_with_model(
        self,
        session_configuration: Dict[str, Any],
        model_name: str,
    ) -> None:
        """
        Configure session with a specific model, handling model changes.
        
        This method extends configure_session to handle model changes mid-session.
        When the model changes, it invalidates the memory cache, rebuilds the agent
        with the new model, and reloads conversation history from SessionStorage.
        
        Args:
            session_configuration: Configuration dict with user_id, session_id, etc.
            model_name: The model to use for this session
        """
        user_id = session_configuration.get('user_id')
        session_id = session_configuration.get('session_id')
        
        # Detect model change
        model_changed = self._current_model != model_name
        
        if model_changed:
            logger.info(
                f"🔄 Model change: {self._current_model} → {model_name} for session {session_id}"
            )
            # Clear current memory to force reload with new model
            self._current_memory = None
        
        # Update current model
        self._current_model = model_name
        
        # Add model_name to session_configuration so configure_session rebuilds the agent
        config_with_model = {**session_configuration, 'model_name': model_name}
        
        # Call the standard configure_session which handles:
        # - Session changes and memory loading
        # - Agent rebuild when model_name is in config (sets _agent_built = False)
        await self.configure_session(config_with_model)
        
        # If model changed, ensure memory is reloaded with fresh tokenization
        if model_changed and session_id and user_id:
            self._current_memory = await self._load_memory_for_session(
                session_id, user_id, model_name
            )
            if self._current_memory:
                logger.info(f"✅ Memory reloaded for session {session_id} with model {model_name}")

    async def get_current_model(self, session_id: str = None) -> Optional[str]:
        """
        Get the current model being used by this agent.
        
        Args:
            session_id: Optional session ID (for interface compatibility)
        
        Returns:
            The current model name, or None if not set
        """
        return self._current_model

    def get_default_model(self) -> Optional[str]:
        """
        Get the default model configured for this agent (backward compatibility).
        
        Returns:
            The default model name, or None if not configured
        """
        return self._default_model

    async def run_agent(
        self,
        query: str,
        ctx: Any,
        stream: bool = False
    ) -> Union[str, AsyncGenerator]:
        """
        Execute the LlamaIndex agent with a query.
        
        Args:
            query: The user query to process
            ctx: The LlamaIndex Context object for conversation history
            stream: Whether to return streaming results
            
        Returns:
            If stream=False: Returns the final response as a string
            If stream=True: Returns an AsyncGenerator that yields LlamaIndex streaming events
        """
        if not self._agent_instance:
            raise RuntimeError("Agent not initialized. Call initialize_agent first.")
        
        # Pass memory to the agent run if available
        run_kwargs = {}
        if self._current_memory:
            # Sanitize memory before use to remove empty tool_calls arrays
            # that OpenAI rejects when changing models mid-session
            if self._memory_adapter:
                self._memory_adapter.sanitize_memory_buffer(self._current_memory)
            run_kwargs['memory'] = self._current_memory
            logger.info(f"🧠 Passing memory to agent for session {self._current_session_id}")
        
        # Get the streaming handler from subclass
        handler = self._run_agent_stream_internal(query, ctx, **run_kwargs)
        
        if stream:
            # Return an async generator that yields events from the handler
            return self._stream_events_wrapper(handler)
        else:
            # Use streaming runner but await the final result
            final_response = await handler
            return str(final_response)

    def _run_agent_stream_internal(self, query: str, ctx: Any, **kwargs) -> Any:
        """
        Internal method to run the agent in streaming mode.
        
        This method should be implemented by subclasses to return a handler
        that has both stream_events() method and is awaitable for the final result.
        
        Args:
            query: The user query
            ctx: The context object
            **kwargs: Additional arguments (e.g., memory=Memory object)
        
        Returns:
            A handler object with stream_events() method and awaitable for final response.
        """
        # Use default implementation if available (set by initialize_agent)
        if hasattr(self, '_run_agent_stream_internal_impl'):
            return self._run_agent_stream_internal_impl(query, ctx, **kwargs)
        
        raise NotImplementedError("Subclasses must implement _run_agent_stream_internal")

    async def _stream_events_wrapper(self, handler: Any) -> AsyncGenerator:
        """
        Wrapper to yield events from the LlamaIndex handler's stream_events() method.
        
        Args:
            handler: The LlamaIndex streaming handler
            
        Yields:
            LlamaIndex streaming events
        """
        async for event in handler.stream_events():
            yield event

    async def process_streaming_event(self, event: Any) -> Optional[Dict[str, Any]]:
        """
        Convert LlamaIndex streaming events to unified format.
        
        Args:
            event: LlamaIndex streaming event (AgentStream, ToolCallResult, etc.)
            
        Returns:
            Dictionary in unified format, or None if event should be skipped.
        """
        try:
            event_type = type(event).__name__
            
            # Token deltas
            if event_type == "AgentStream":
                chunk = getattr(event, "delta", "")
                if chunk:
                    return {
                        "type": "chunk",
                        "content": chunk,
                        "metadata": {
                            "source": "llamaindex_agent",
                            "timestamp": str(datetime.now()),
                        }
                    }
                return None
            
            # Tool results (emit request first so UI shows arguments)
            if event_type == "ToolCallResult":
                tool_name = getattr(event, "tool_name", "unknown_tool")
                tool_kwargs = getattr(event, "tool_kwargs", {})
                call_id = getattr(event, "call_id", "unknown")
                tool_output = str(getattr(event, "tool_output", ""))
                
                # First emit tool call
                tool_call_event = {
                    "type": "tool_call",
                    "content": "",
                    "metadata": {
                        "source": "llamaindex_agent",
                        "tool_name": tool_name,
                        "tool_arguments": tool_kwargs,
                        "call_id": call_id,
                        "timestamp": str(datetime.now()),
                    }
                }
                
                # Then emit tool result
                tool_result_event = {
                    "type": "tool_result",
                    "content": tool_output,
                    "metadata": {
                        "source": "llamaindex_agent",
                        "tool_name": tool_name,
                        "call_id": call_id,
                        "is_error": False,
                        "timestamp": str(datetime.now()),
                    }
                }
                
                # Return tool call first (result will be handled separately)
                # Note: This is a simplification - in practice, we'd need to yield both
                return tool_call_event
            
            # AgentOutput or lifecycle noise suppression
            if event_type in {"AgentOutput"}:
                return None
                
            # Agent loop started marker
            if event_type in {"AgentInput", "InputEvent"}:
                return {
                    "type": "activity",
                    "content": "Agent loop started",
                    "metadata": {
                        "source": "llamaindex_agent",
                        "timestamp": str(datetime.now()),
                    }
                }
            
            # Suppress lifecycle events
            if event_type in {"StopEvent", "StartEvent"}:
                return None
            
            # Fallback: concise other event
            event_str = str(event)
            if len(event_str) > 800 or "ChatMessage(" in event_str or "tool_kwargs=" in event_str:
                content = event_type
            else:
                content = event_str
                
            return {
                "type": "activity",
                "content": content,
                "metadata": {
                    "source": "llamaindex_agent",
                    "event_type": event_type,
                    "timestamp": str(datetime.now()),
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to process streaming event: {e}")
            return {
                "type": "error",
                "content": f"Failed to serialize event: {e}",
                "metadata": {
                    "timestamp": str(datetime.now()),
                }
            }

    async def handle_message_stream(
        self, session_id: str, agent_input: StructuredAgentInput
    ) -> AsyncGenerator[StructuredAgentOutput, None]:
        """
        Handle a user message in streaming mode with LlamaIndex-specific event handling.
        
        This override preserves the original LlamaIndex streaming behavior from LlamaIndexBasedAgent.
        """
        if not agent_input.query:
            yield StructuredAgentOutput(response_text="Input query cannot be empty.", parts=[])
            return

        await self._async_ensure_agent_built()

        ctx = self._state_ctx or self.create_fresh_context()
        
        # Build full query including file content from parts (same as non-streaming)
        full_query = self._build_full_query(agent_input)
        
        handler = self._run_agent_stream_internal(full_query, ctx)

        agent_loop_started_emitted = False

        async for event in handler.stream_events():
            # Token deltas
            if getattr(event, "__class__", type("", (), {})).__name__ == "AgentStream":
                chunk = getattr(event, "delta", "")
                if chunk:
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_CHUNK__{chunk}")],
                    )
                continue

            # Tool results (emit request first so UI shows arguments)
            if getattr(event, "__class__", type("", (), {})).__name__ == "ToolCallResult":
                try:
                    tool_name = getattr(event, "tool_name", "unknown_tool")
                    tool_kwargs = getattr(event, "tool_kwargs", {})
                    call_id = getattr(event, "call_id", "unknown")
                    tool_request = {
                        "type": "tool_request",
                        "source": "llamaindex_agent",
                        "tools": [
                            {"name": tool_name, "arguments": tool_kwargs, "id": call_id}
                        ],
                        "timestamp": str(datetime.now()),
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(tool_request)}")],
                    )
                except Exception:
                    pass

                tool_output = str(getattr(event, "tool_output", ""))
                tool_result = {
                    "type": "tool_result",
                    "source": "llamaindex_agent",
                    "results": [
                        {
                            "name": tool_name,
                            "content": tool_output,
                            "is_error": False,
                            "call_id": call_id,
                        }
                    ],
                    "timestamp": str(datetime.now()),
                }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(tool_result)}")],
                )
                agent_loop_started_emitted = False
                continue

            # AgentOutput or lifecycle noise suppression and loop marker
            event_type = type(event).__name__
            if event_type in {"AgentOutput"}:
                continue
            if event_type in {"AgentInput", "InputEvent"}:
                if not agent_loop_started_emitted:
                    loop_activity = {
                        "type": "message",
                        "source": "agent",
                        "content": "Agent loop started",
                        "timestamp": str(datetime.now()),
                    }
                    yield StructuredAgentOutput(
                        response_text="",
                        parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(loop_activity)}")],
                    )
                    agent_loop_started_emitted = True
                continue
            if event_type in {"StopEvent", "StartEvent"}:
                continue

            # Fallback: concise other event
            try:
                event_str = str(event)
                if len(event_str) > 800 or "ChatMessage(" in event_str or "tool_kwargs=" in event_str:
                    other = {
                        "type": "other",
                        "source": "llamaindex_agent",
                        "content": event_type,
                        "event_type": event_type,
                        "timestamp": str(datetime.now()),
                    }
                else:
                    other = {
                        "type": "other",
                        "source": "llamaindex_agent",
                        "content": event_str,
                        "event_type": event_type,
                        "timestamp": str(datetime.now()),
                    }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(other)}")],
                )
            except Exception as e:
                err = {
                    "type": "error",
                    "content": f"Failed to serialize event: {e}",
                    "timestamp": str(datetime.now()),
                }
                yield StructuredAgentOutput(
                    response_text="",
                    parts=[TextOutputStreamPart(text=f"__STREAM_ACTIVITY__{json.dumps(err)}")],
                )

        # Final result
        final_response = await handler
        self._state_ctx = ctx
        final_text = str(final_response)
        cleaned, parts = parse_special_blocks_from_text(final_text)
        yield StructuredAgentOutput(
            response_text=cleaned,
            parts=[TextOutputPart(text=cleaned), *parts],
        )

    async def get_metadata(self) -> Dict[str, Any]:
        """Return LlamaIndex-specific agent metadata including id, name, and description."""
        tools = self.get_agent_tools()
        tool_list = [
            {
                "name": getattr(t, "__name__", str(t)),
                "description": getattr(t, "__doc__", "Agent tool"),
                "type": "static",
            }
            for t in tools
        ]
        has_file_storage = False
        if not has_file_storage:
            # Scan agent attributes for AgentTool instances requiring file storage
            for attr_name in dir(self):
                if attr_name.startswith("_"):
                    continue
                attr = getattr(self, attr_name, None)
                if isinstance(attr, (list, tuple)):
                    for item in attr:
                        if hasattr(item, "get_tool_info"):
                            info = item.get_tool_info()
                            if info.get("requires_file_storage", False):
                                has_file_storage = True
                                break
                if has_file_storage:
                    break
        return {
            "id": self.agent_id,
            "name": self.name,
            "description": self.description,
            "capabilities": {
                "streaming": True,
                "tool_use": True,
                "reasoning": True,
                "model_choice": True,
                "multimodal": False,
                "file_storage": has_file_storage,
            },
            "defaultInputModes": ["text"],
            "defaultOutputModes": ["text", "structured"],
            "tools": tool_list,
            "tool_summary": {
                "total_tools": len(tools),
                "static_tools": len(tools),
            },
            "framework": "LlamaIndex",
        }
