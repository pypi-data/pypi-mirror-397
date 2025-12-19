"""Ceylon AI Agent Framework.

A Rust-based agent mesh framework for building local and distributed AI agent systems.

This package provides:
- Agent classes for building AI agents with actions
- Mesh networking for agent communication (local and distributed)
- LLM integration with fluent builder API
- Memory backends for persistent agent memory
- ReAct framework for reasoning and acting
- Logging configuration

Example:
    from ceylonai_next import Agent, LlmAgent, LocalMesh

    # Create a simple agent
    agent = Agent("my_agent")

    @agent.action(description="Add two numbers")
    def add(a: int, b: int) -> int:
        return a + b

    # Create an LLM agent
    llm_agent = LlmAgent("assistant", "ollama::llama2")
    llm_agent.with_system_prompt("You are a helpful assistant.")
    llm_agent.build()

    # Connect to a mesh
    mesh = LocalMesh("my_mesh")
    mesh.add_agent(agent)
    mesh.add_llm_agent(llm_agent)
"""

# =============================================================================
# RUST NATIVE BINDINGS (from ceylonai_next.ceylonai_next)
# =============================================================================
from ceylonai_next.ceylonai_next import (
    # Mesh components
    PyLocalMesh,
    PyDistributedMesh,
    PyMeshRequest,
    PyMeshResult,
    # Agent components
    PyAgent,
    PyAgentContext,
    PyAgentMessageProcessor,
    # Action/Tool components
    _PyAction,
    PyToolInvoker,
    # LLM components
    PyLlmAgent,
    PyLlmConfig,
    # Memory components
    PyMemoryEntry,
    PyMemoryQuery,
    PyInMemoryBackend,
    PyRedisBackend,
    # ReAct framework components
    PyReActConfig,
    PyReActStep,
    PyReActResult,
    # Registry components
    PyAgentMetadata,
    PyInMemoryRegistry,
    # Logging components
    PyLoggingConfig,
    PyLoggingHandle,
    init_logging_py,
    # Metrics
    get_metrics,
)

# =============================================================================
# PYTHON WRAPPER CLASSES (from submodules)
# =============================================================================

# Agent components
from ceylonai_next.agent import (
    Agent,
    PyAction,
    FunctionalAction,
    LlmAgent,
    LlmConfig,
)

# Mesh components
from ceylonai_next.mesh import (
    LocalMesh,
    DistributedMesh,
    AsyncMessageProcessor,
)

# Memory components
from ceylonai_next.memory import (
    Memory,
    MemoryEntry,
    MemoryQuery,
    InMemoryBackend,
    RedisBackend,
)

# ReAct framework
from ceylonai_next.react import (
    ReActConfig,
    ReActStep,
    ReActResult,
)

# Logging
from ceylonai_next.logging import (
    LoggingConfig,
    LoggingHandle,
    init_logging,
)

# Types
from ceylonai_next.types import (
    MeshRequest,
    MeshResult,
)

# =============================================================================
# PUBLIC API
# =============================================================================
__all__ = [
    # Rust native bindings (re-exported)
    "PyLocalMesh",
    "PyDistributedMesh",
    "PyMeshRequest",
    "PyMeshResult",
    "PyAgent",
    "PyAgentContext",
    "PyAgentMessageProcessor",
    "_PyAction",
    "PyToolInvoker",
    "PyLlmAgent",
    "PyLlmConfig",
    "PyMemoryEntry",
    "PyMemoryQuery",
    "PyInMemoryBackend",
    "PyRedisBackend",
    "PyReActConfig",
    "PyReActStep",
    "PyReActResult",
    "PyAgentMetadata",
    "PyInMemoryRegistry",
    "PyLoggingConfig",
    "PyLoggingHandle",
    "init_logging_py",
    "get_metrics",
    # Python wrappers
    "PyAction",
    "FunctionalAction",
    "Agent",
    "LocalMesh",
    "DistributedMesh",
    "LlmConfig",
    "LlmAgent",
    "ReActConfig",
    "ReActStep",
    "ReActResult",
    "MemoryEntry",
    "MemoryQuery",
    "InMemoryBackend",
    "RedisBackend",
    "Memory",
    "LoggingConfig",
    "LoggingHandle",
    "init_logging",
    "MeshRequest",
    "MeshResult",
    "AsyncMessageProcessor",
]

__version__ = "0.3.5"
