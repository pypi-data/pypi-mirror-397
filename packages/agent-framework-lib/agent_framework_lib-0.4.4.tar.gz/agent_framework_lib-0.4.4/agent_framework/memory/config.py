"""
Memory Configuration for Agent Framework.

Provides Pydantic-based configuration for memory providers.
Configuration can be defined directly in agent classes or via environment variables.

Example in agent:
    ```python
    class MyAgent(LlamaIndexAgent):
        def get_memory_config(self) -> Optional[MemoryConfig]:
            return MemoryConfig(
                primary_provider="memori",
                secondary_provider="graphiti",  # Optional second provider
                memori=MemoriConfig(database_url="sqlite:///memory.db"),
                graphiti=GraphitiConfig(use_falkordb=True)
            )
    ```

Example via environment:
    ```bash
    export MEMORY_PRIMARY_PROVIDER=memori
    export MEMORI_DATABASE_URL=postgresql://localhost/memory
    ```

Version: 0.1.0
"""

import logging
import os
from typing import Literal

from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class MemoriConfig(BaseModel):
    """
    Configuration for Memori memory provider.
    
    Memori provides SQL-native memory storage with automatic fact extraction.
    Best for: Quick setup, simple memory needs, existing SQL infrastructure.
    
    Attributes:
        enabled: Whether Memori is enabled
        database_url: SQLAlchemy-style database URL
        api_key: Optional Memori API key for Advanced Augmentation
        llm_provider: LLM provider for fact extraction
    """

    enabled: bool = True

    # Database connection (SQLAlchemy-style URL)
    database_url: str = Field(
        default_factory=lambda: os.getenv(
            "MEMORI_DATABASE_URL",
            "sqlite:///agent_memory.db"
        ),
        description="SQLAlchemy database URL (sqlite, postgresql, mysql, etc.)"
    )

    # Memori API key for Advanced Augmentation (optional, free tier available)
    api_key: str | None = Field(
        default_factory=lambda: os.getenv("MEMORI_API_KEY"),
        description="Optional API key for Memori Advanced Augmentation"
    )

    # LLM provider for extraction (uses framework's model_config if not specified)
    llm_provider: Literal["openai", "anthropic", "gemini"] | None = Field(
        default=None,
        description="LLM provider for fact extraction (defaults to framework config)"
    )

    class Config:
        extra = "allow"  # Allow additional fields for forward compatibility


class GraphitiConfig(BaseModel):
    """
    Configuration for Graphiti memory provider.
    
    Graphiti provides temporal knowledge graph storage with bi-temporal model.
    Best for: Complex reasoning, temporal queries, entity relationships.
    
    Supports Neo4j or FalkorDB as graph database backend.
    
    Attributes:
        enabled: Whether Graphiti is enabled
        use_falkordb: Use FalkorDB instead of Neo4j (lighter weight)
        neo4j_*: Neo4j connection settings
        falkordb_*: FalkorDB connection settings
        llm_*: LLM settings for entity/fact extraction
        embedding_*: Embedding settings for semantic search
    """

    enabled: bool = True

    # Database backend choice
    use_falkordb: bool = Field(
        default_factory=lambda: os.getenv(
            "GRAPHITI_USE_FALKORDB", "false"
        ).lower() == "true",
        description="Use FalkorDB instead of Neo4j (simpler setup)"
    )

    # Neo4j connection settings
    neo4j_uri: str = Field(
        default_factory=lambda: os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        description="Neo4j connection URI"
    )
    neo4j_user: str = Field(
        default_factory=lambda: os.getenv("NEO4J_USER", "neo4j"),
        description="Neo4j username"
    )
    neo4j_password: str = Field(
        default_factory=lambda: os.getenv("NEO4J_PASSWORD", "password"),
        description="Neo4j password"
    )
    neo4j_database: str = Field(
        default_factory=lambda: os.getenv("NEO4J_DATABASE", "neo4j"),
        description="Neo4j database name"
    )

    # FalkorDB connection settings (alternative to Neo4j)
    falkordb_host: str = Field(
        default_factory=lambda: os.getenv("FALKORDB_HOST", "localhost"),
        description="FalkorDB host"
    )
    falkordb_port: int = Field(
        default_factory=lambda: int(os.getenv("FALKORDB_PORT", "6379")),
        description="FalkorDB port"
    )
    falkordb_password: str | None = Field(
        default_factory=lambda: os.getenv("FALKORDB_PASSWORD"),
        description="FalkorDB password (optional)"
    )

    # LLM settings for entity/fact extraction
    llm_provider: Literal["openai", "anthropic", "gemini"] | None = Field(
        default=None,
        description="LLM provider (defaults to framework config)"
    )
    llm_model: str = Field(
        default_factory=lambda: os.getenv("GRAPHITI_LLM_MODEL", "gpt-4o-mini"),
        description="LLM model for graph construction"
    )

    # Embedding settings
    embedding_model: str = Field(
        default_factory=lambda: os.getenv(
            "GRAPHITI_EMBEDDING_MODEL",
            "text-embedding-3-small"
        ),
        description="Embedding model for semantic search"
    )
    embedding_dim: int = Field(
        default_factory=lambda: int(os.getenv("GRAPHITI_EMBEDDING_DIM", "1536")),
        description="Embedding dimension"
    )

    class Config:
        extra = "allow"


class MemoryConfig(BaseModel):
    """
    Main memory configuration for agents.
    
    Supports single provider or dual provider (hybrid) setup.
    When both providers are enabled, facts from both are merged during recall.
    
    Attributes:
        primary_provider: Main memory provider ("memori", "graphiti", or "none")
        secondary_provider: Optional secondary provider for hybrid setup
        memori: Memori-specific configuration
        graphiti: Graphiti-specific configuration
        auto_store_interactions: Automatically store all interactions
        recall_on_message: Auto-recall context before each message
        max_context_facts: Maximum facts to inject into context
        context_types: Types of facts to include in context
    """

    # Provider selection
    primary_provider: Literal["memori", "graphiti", "none"] = Field(
        default_factory=lambda: os.getenv("MEMORY_PRIMARY_PROVIDER", "none"),
        description="Primary memory provider"
    )

    secondary_provider: Literal["memori", "graphiti"] | None = Field(
        default_factory=lambda: os.getenv("MEMORY_SECONDARY_PROVIDER"),
        description="Optional secondary provider for hybrid memory"
    )

    # Provider-specific configurations
    memori: MemoriConfig = Field(
        default_factory=MemoriConfig,
        description="Memori provider configuration"
    )

    graphiti: GraphitiConfig = Field(
        default_factory=GraphitiConfig,
        description="Graphiti provider configuration"
    )

    # ===== Passive Injection Settings =====
    passive_injection: bool = Field(
        default_factory=lambda: os.getenv(
            "MEMORY_PASSIVE_INJECTION", "true"
        ).lower() == "true",
        description="Auto-inject relevant memory context before each message"
    )

    passive_injection_max_facts: int = Field(
        default_factory=lambda: int(os.getenv("MEMORY_PASSIVE_MAX_FACTS", "10")),
        description="Maximum facts to inject in passive mode"
    )

    passive_injection_min_confidence: float = Field(
        default_factory=lambda: float(os.getenv("MEMORY_PASSIVE_MIN_CONFIDENCE", "0.5")),
        description="Minimum relevance score for passive injection"
    )

    passive_injection_primary_only: bool = Field(
        default_factory=lambda: os.getenv(
            "MEMORY_PASSIVE_PRIMARY_ONLY", "true"
        ).lower() == "true",
        description="Only query primary provider for passive injection (faster)"
    )

    # ===== Async Storage Settings =====
    async_store: bool = Field(
        default_factory=lambda: os.getenv(
            "MEMORY_ASYNC_STORE", "true"
        ).lower() == "true",
        description="Store interactions asynchronously (fire-and-forget)"
    )

    async_store_max_concurrent: int = Field(
        default_factory=lambda: int(os.getenv("MEMORY_ASYNC_MAX_CONCURRENT", "10")),
        description="Maximum concurrent background store operations"
    )

    async_store_timeout: float = Field(
        default_factory=lambda: float(os.getenv("MEMORY_ASYNC_TIMEOUT", "40.0")),
        description="Timeout for pending tasks on shutdown (seconds)"
    )

    # ===== Behavior Settings =====
    auto_store_interactions: bool = Field(
        default_factory=lambda: os.getenv(
            "MEMORY_AUTO_STORE", "true"
        ).lower() == "true",
        description="Automatically store all interactions for fact extraction"
    )

    max_context_facts: int = Field(
        default_factory=lambda: int(os.getenv("MEMORY_MAX_CONTEXT_FACTS", "20")),
        description="Maximum facts to inject into prompt context"
    )

    context_types: list[str] | None = Field(
        default=None,
        description="Types of facts to include (None = all types)"
    )

    @classmethod
    def disabled(cls) -> "MemoryConfig":
        """Create a disabled memory config."""
        return cls(primary_provider="none")

    @classmethod
    def memori_simple(
        cls,
        database_url: str = "sqlite:///agent_memory.db",
        passive_injection: bool = True
    ) -> "MemoryConfig":
        """
        Create a simple Memori-only configuration.
        
        Args:
            database_url: Database URL for Memori storage
            passive_injection: Enable automatic context injection (default: True)
            
        Returns:
            MemoryConfig with Memori enabled
        """
        return cls(
            primary_provider="memori",
            passive_injection=passive_injection,
            memori=MemoriConfig(database_url=database_url)
        )

    @classmethod
    def graphiti_simple(
        cls,
        use_falkordb: bool = True,
        falkordb_host: str = "localhost",
        falkordb_port: int = 6379,
        passive_injection: bool = True
    ) -> "MemoryConfig":
        """
        Create a simple Graphiti-only configuration with FalkorDB.
        
        Args:
            use_falkordb: Use FalkorDB (recommended for simple setup)
            falkordb_host: FalkorDB host
            falkordb_port: FalkorDB port
            passive_injection: Enable automatic context injection (default: True)
            
        Returns:
            MemoryConfig with Graphiti enabled
        """
        return cls(
            primary_provider="graphiti",
            passive_injection=passive_injection,
            graphiti=GraphitiConfig(
                use_falkordb=use_falkordb,
                falkordb_host=falkordb_host,
                falkordb_port=falkordb_port
            )
        )

    @classmethod
    def hybrid(
        cls,
        memori_database_url: str = "sqlite:///agent_memory.db",
        graphiti_use_falkordb: bool = True,
        passive_injection: bool = True,
        async_store: bool = True,
        passive_injection_primary_only: bool = True
    ) -> "MemoryConfig":
        """
        Create a hybrid configuration with both Memori and Graphiti.
        
        Memori serves as primary (fast, simple facts).
        Graphiti serves as secondary (complex relationships, temporal).
        
        Args:
            memori_database_url: Memori database URL
            graphiti_use_falkordb: Use FalkorDB for Graphiti
            passive_injection: Enable automatic context injection (default: True)
            async_store: Enable fire-and-forget storage (default: True)
            passive_injection_primary_only: Only query primary for passive injection (default: True)
            
        Returns:
            MemoryConfig with both providers enabled
        """
        return cls(
            primary_provider="memori",
            secondary_provider="graphiti",
            passive_injection=passive_injection,
            async_store=async_store,
            passive_injection_primary_only=passive_injection_primary_only,
            memori=MemoriConfig(database_url=memori_database_url),
            graphiti=GraphitiConfig(use_falkordb=graphiti_use_falkordb)
        )

    @classmethod
    def from_env(cls) -> "MemoryConfig":
        """
        Create configuration from environment variables.
        
        Uses MEMORY_* environment variables.
        """
        return cls()  # Pydantic defaults handle env vars

    @property
    def is_enabled(self) -> bool:
        """Whether any memory provider is enabled."""
        return self.primary_provider != "none"

    @property
    def is_hybrid(self) -> bool:
        """Whether using dual provider setup."""
        return (
            self.primary_provider != "none"
            and self.secondary_provider is not None
        )

    def get_enabled_providers(self) -> list[str]:
        """Get list of enabled provider names."""
        providers = []
        if self.primary_provider != "none":
            providers.append(self.primary_provider)
        if self.secondary_provider:
            providers.append(self.secondary_provider)
        return providers

    class Config:
        extra = "allow"
