"""
MCP Agent Example

This example demonstrates how to create an agent that integrates with MCP (Model Context Protocol) servers.
MCP allows agents to connect to external tools and services for enhanced capabilities.

Features demonstrated:
- MCP server integration with automatic memory management
- External tool access with conversation history
- Enhanced agent capabilities through MCP tools
- Automatic tool discovery and integration
- Session-based memory for tool interactions

Common MCP servers:
- filesystem: Access to local file system operations
- fetch: HTTP requests and web scraping
- github: GitHub API integration
- postgres: Database operations

Usage:
    python agent_with_mcp.py

The agent will start a web server on http://localhost:8102
Try using MCP tools, then reload - the agent remembers your previous tool interactions!

Requirements: 
- uv add agent-framework[llamaindex]
- uv add llama-index-tools-mcp
- MCP server installed (e.g., uvx install @modelcontextprotocol/server-filesystem)

Learn more about MCP: https://modelcontextprotocol.io/
"""
import asyncio
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Any, Dict, Optional

# Load environment variables from a `.env` file located at the project root (one level
# above the `agents/` directory). Fall back to default loader if no explicit .env file
# is found.
env_path = Path(__file__).resolve().parents[1] / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from agent_framework.implementations import LlamaIndexAgent
from agent_framework.storage.file_system_management import FileStorageFactory
from agent_framework.memory import MemoryConfig
from agent_framework.tools import (
    CreateFileTool,
    ListFilesTool,
    ReadFileTool,
    CreatePDFFromMarkdownTool,
    CreatePDFFromHTMLTool,
    ChartToImageTool,
    GetFilePathTool,
    CreatePDFWithImagesTool,
    MermaidToImageTool,
    TableToImageTool,
    WebSearchTool,
)


class TestAgent(LlamaIndexAgent):
    """An agent with MCP (Model Context Protocol) integration and automatic memory.
    
    This agent can connect to MCP servers to access external tools and services.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="test-agent-v1",
            name="Multi-Skills Test Agent",
            description="A multi-skilled assistant with MCP integration, file storage, and PDF generation capabilities."
        )
        # Store session context for potential use in tools
        self.current_user_id = "default_user"
        self.current_session_id = None
        # MCP tools storage
        self.mcp_tools = []
        self.mcp_clients = {}
        self._mcp_initialized = False
        self.file_storage = None
        self.tools_files_storage= [
            CreateFileTool(),
            ListFilesTool(),
            ReadFileTool(),
            CreatePDFFromMarkdownTool(),
            CreatePDFFromHTMLTool(),
            ChartToImageTool(),
            GetFilePathTool(),
            CreatePDFWithImagesTool(),
            MermaidToImageTool(),
            TableToImageTool(),
        ]
        # Web search tool (no file storage needed)
        self.web_search_tool = WebSearchTool()
    def get_memory_config(self):
        """
        Enable both Memori and Graphiti with performance optimizations.
        
        Optimization settings (enabled by default in hybrid mode):
        - async_store=True: Memory storage runs in background, doesn't block responses
        - passive_injection_primary_only=True: Only queries fast Memori for auto-context
        
        These defaults provide the best balance of speed and functionality.
        Set to False if you need synchronous storage or want passive injection
        to include Graphiti's complex relationships.
        """
        return MemoryConfig.hybrid(
            memori_database_url="sqlite:///hybrid_agent_memory.db",
            graphiti_use_falkordb=True,
            passive_injection=false,
            # Performance optimizations (these are the defaults, shown explicitly)
            async_store=True,  # Fire-and-forget storage for faster responses
        )
    async def _ensure_file_storage(self):
        """Ensure file storage is initialized."""
        if self.file_storage is None:
            self.file_storage = await FileStorageFactory.create_storage_manager()
    
    
    async def configure_session(self, session_configuration: Dict[str, Any]) -> None:
        """Capture session context."""
        self.current_user_id = session_configuration.get('user_id', 'default_user')
        self.current_session_id = session_configuration.get('session_id')
         # Ensure file storage is initialized before injecting into tools
        await self._ensure_file_storage()
        #Initialize file storage tools
        for tool in self.tools_files_storage:
            tool.set_context(file_storage=self.file_storage,
                            user_id=self.current_user_id,
                            session_id=self.current_session_id)
        # Call parent to continue normal configuration                
        await super().configure_session(session_configuration)
    
    async def _initialize_mcp_tools(self):
        """Initialize MCP tools from configured servers."""
        if self._mcp_initialized:
            return
        
        try:
            from llama_index.tools.mcp import BasicMCPClient, McpToolSpec
        except ImportError:
            print("⚠️ llama-index-tools-mcp not available. Install with: uv add llama-index-tools-mcp")
            self.mcp_tools = []
            return
        
        print("🔌 Initializing MCP tools...")
        self.mcp_tools = []
        
        # Get MCP server configuration (returns a list of configs)
        mcp_configs = self._get_mcp_server_config()
        if not mcp_configs:
            print("ℹ️ No MCP server configured")
            return
        
        # Iterate over all MCP server configurations
        for idx, mcp_config in enumerate(mcp_configs):
            try:
                server_name = mcp_config.get("name", f"mcp_server_{idx}")
                print(f"🔌 Connecting to MCP server: {server_name}...")
                cmd = mcp_config["command"]
                args = mcp_config["args"]
                env = mcp_config.get("env", {})
                
                client = BasicMCPClient(cmd, args=args, env=env)
                self.mcp_clients[server_name] = client
                
                # Use official LlamaIndex MCP approach
                mcp_tool_spec = McpToolSpec(client=client)
                function_tools = await mcp_tool_spec.to_tool_list_async()
                
                if function_tools:
                    self.mcp_tools.extend(function_tools)
                    print(f"✅ MCP server '{server_name}': {len(function_tools)} tools loaded")
                else:
                    print(f"⚠️ No tools found from MCP server '{server_name}'")
            except Exception as e:
                print(f"❌ Failed to connect to MCP server '{server_name}': {e}")
        
        self._mcp_initialized = True
        print(f"📊 MCP Tools initialized: {len(self.mcp_tools)} tools available")
    
    def _get_mcp_server_config(self) -> Optional[List[Dict[str, Any]]]:
        """Get MCP server configuration with environment variables.
        
        Returns a list of MCP server configurations. Each configuration is a dict with:
        - command: The command to run (e.g., "uvx")
        - args: List of arguments
        - env: Dictionary of environment variables
        """
        # This is an example with a mcp server with python 
        return [
            {
                "command": "uvx",
                "args": ["mcp-run-python","stdio"],
            }]
    


    def get_agent_prompt(self) -> str:
        """Define the agent's system prompt."""
        return "You are an Assistant with multiple capacity. You have to choose the right tools to response the user demands."
    async def get_welcome_message(self) -> str:
        """Return a welcome message for new sessions."""
        return f"Bonjour ! Je suis {self.name}.\n\n{self.description}"
    
    def get_agent_tools(self) -> List[callable]:
        """Define the built-in tools available to the agent.
        
        Note: MCP tools are added in initialize_agent(), memory tools are added by the framework.
        This method only returns the agent's own tools.
        """
        tools = [tool.get_tool_function() for tool in self.tools_files_storage]
        # Add web search (doesn't need file storage context)
        tools.append(self.web_search_tool.get_tool_function())
        return tools
    
    async def initialize_agent(self, model_name: str, system_prompt: str, tools: List[callable], **kwargs) -> None:
        """Initialize the agent and load MCP tools first.
        
        Note: The 'tools' parameter already contains agent tools + memory tools (added by framework).
        We just need to add MCP tools to this list.
        """
        # Load MCP tools BEFORE creating the agent
        await self._initialize_mcp_tools()
        
        # Add MCP tools to the tools already provided by the framework
        # (which includes get_agent_tools() + memory tools)
        all_tools = list(tools) + self.mcp_tools
        
        # Call parent with all tools
        await super().initialize_agent(model_name, system_prompt, all_tools, **kwargs)



def main():
    """Start the MCP agent server with UI."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable not set")
        print("Please set it with: export OPENAI_API_KEY=your-key-here")
        return
    
    # Import server function
    from agent_framework import create_basic_agent_server
    
    # Get port from environment or use default
    port = int(os.getenv("AGENT_PORT", "8203"))
    
    print("=" * 60)
    print("🚀 Starting MCP multi skills Server")
    print("=" * 60)
    print(f"📊 Model: {os.getenv('DEFAULT_MODEL', 'gpt-5')}")
    print(f"🌐 Server: http://localhost:{port}")
    print(f"🎨 UI: http://localhost:{port}/ui")
    print("=" * 60)
    
    # Start the server
    create_basic_agent_server(
        agent_class=TestAgent,
        host="0.0.0.0",
        port=port,
        reload=False
    )


if __name__ == "__main__":
    asyncio.run(main())
