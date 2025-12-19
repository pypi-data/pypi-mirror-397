"""Type stubs for ceylonai_next - Ceylon AI Agent Framework.

This module provides type hints for both the native Rust bindings
and the Python wrapper classes.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, TypeVar

# Type aliases for better readability
T = TypeVar("T")
ActionFunc = Callable[..., Any]

# =============================================================================
# RUST NATIVE BINDINGS (from ceylonai_next.ceylonai_next)
# =============================================================================

class PyAgent:
    """Base agent class from Rust bindings."""
    def __new__(cls, /, *_args: Any, **_kwargs: Any) -> "PyAgent": ...
    def act(self, action_name: str, inputs: Any) -> Any: ...
    def get_last_response(self) -> Optional[str]: ...
    def name(self) -> str: ...
    def set_last_response(self, response: Optional[str]) -> None: ...

class PyAgentContext:
    """Agent context for mesh operations."""
    def __new__(cls, mesh_name: str) -> "PyAgentContext": ...
    @property
    def mesh_name(self) -> str: ...

class PyAgentMessageProcessor:
    """Processes pending messages for an agent."""
    @property
    def agent_name(self) -> str: ...
    def has_pending(self) -> bool: ...
    def pending_count(self) -> int: ...
    def process_pending(self) -> int: ...

class PyAgentMetadata:
    """Metadata for agent registration."""
    def __new__(cls, id: str, name: str, address: str) -> "PyAgentMetadata": ...
    @property
    def address(self) -> str: ...
    @property
    def id(self) -> str: ...
    @property
    def name(self) -> str: ...

class PyDistributedMesh:
    """Distributed mesh for multi-node agent communication."""
    def __new__(cls, name: str, port: int) -> "PyDistributedMesh": ...
    def add_agent(self, agent: "PyAgent") -> PyAgentMessageProcessor: ...
    def add_llm_agent(self, agent: "PyLlmAgent") -> str: ...
    def broadcast(self, payload: str, exclude: Optional[str] = None) -> Any: ...
    def collect_results(self, reminder_interval: float = 30.0) -> Any: ...
    def collect_results_sync(self, reminder_interval: float = 30.0) -> Any: ...
    def connect_peer(self, agent_name: str, url: str) -> Any: ...
    def get_pending(self) -> Any: ...
    def get_results(self) -> Any: ...
    def has_pending(self) -> bool: ...
    def peek_results(self) -> Any: ...
    def process_messages(self) -> int: ...
    def query(
        self,
        target: str,
        payload: str,
        timeout: float = 60.0,
        reminder_interval: float = 30.0,
    ) -> Any: ...
    def query_sync(
        self,
        target: str,
        payload: str,
        timeout: float = 60.0,
        reminder_interval: float = 30.0,
    ) -> "PyMeshResult": ...
    def send_reminders(self, older_than_secs: float = 30.0) -> Any: ...
    def send_to(self, target: str, payload: str) -> Any: ...
    def send_to_sync(self, target: str, payload: str) -> Any: ...
    def start(self) -> Any: ...
    def stop(self) -> Any: ...
    def submit(self, target: str, payload: str) -> Any: ...
    def submit_sync(self, target: str, payload: str) -> str: ...
    def wait_for(
        self, request_id: str, timeout: float = 60.0, reminder_interval: float = 30.0
    ) -> Any: ...
    def wait_for_sync(
        self, request_id: str, timeout: float = 60.0, reminder_interval: float = 30.0
    ) -> "PyMeshResult": ...
    @staticmethod
    def with_registry(
        name: str, port: int, registry: "PyInMemoryRegistry"
    ) -> "PyDistributedMesh": ...

class PyInMemoryBackend:
    """In-memory storage backend for agent memory."""
    def __new__(cls) -> "PyInMemoryBackend": ...
    def __repr__(self) -> str: ...
    def clear(self) -> Any: ...
    def count(self) -> int: ...
    def delete(self, id: str) -> bool: ...
    def get(self, id: str) -> Optional["PyMemoryEntry"]: ...
    def search(self, query: "PyMemoryQuery") -> List["PyMemoryEntry"]: ...
    def store(self, entry: "PyMemoryEntry") -> str: ...
    @staticmethod
    def with_max_entries(max: int) -> "PyInMemoryBackend": ...
    @staticmethod
    def with_ttl_seconds(seconds: int) -> "PyInMemoryBackend": ...

class PyInMemoryRegistry:
    """Registry for agent discovery."""
    def __new__(cls) -> "PyInMemoryRegistry": ...
    def get_agent(self, agent_id: str) -> Optional["PyAgentMetadata"]: ...
    def register(self, metadata: "PyAgentMetadata") -> Any: ...

class PyLlmAgent:
    """LLM-powered agent from Rust bindings."""
    def __new__(cls, name: str, model: str) -> "PyLlmAgent": ...
    def add_action(self, action: "_PyAction") -> "PyLlmAgent": ...
    def add_tool(self, action: "_PyAction") -> "PyLlmAgent": ...
    def build(self) -> "PyLlmAgent": ...
    def is_built(self) -> bool: ...
    def query(self, message: str) -> Any: ...
    def register_action(self, action: "_PyAction") -> Any: ...
    def send_message(self, message: str) -> Any: ...
    def send_message_react(self, message: str) -> "PyReActResult": ...
    def send_message_sync(self, message: str) -> str: ...
    def with_api_key(self, api_key: str) -> "PyLlmAgent": ...
    @staticmethod
    def with_config(name: str, config: "PyLlmConfig") -> "PyLlmAgent": ...
    def with_max_tokens(self, max_tokens: int) -> "PyLlmAgent": ...
    def with_memory(self, memory: Any) -> "PyLlmAgent": ...
    def with_react(self, config: "PyReActConfig") -> Any: ...
    def with_system_prompt(self, prompt: str) -> "PyLlmAgent": ...
    def with_temperature(self, temperature: float) -> "PyLlmAgent": ...

class PyLlmConfig:
    """Configuration builder for LLM agents."""
    def base_url(self, base_url: str) -> "PyLlmConfig": ...
    def build(self) -> "PyLlmConfig": ...
    @staticmethod
    def builder() -> "PyLlmConfig": ...
    def max_tokens(self, max_tokens: int) -> "PyLlmConfig": ...
    def model(self, model: str) -> "PyLlmConfig": ...
    def provider(self, provider: str) -> "PyLlmConfig": ...
    def temperature(self, temperature: float) -> "PyLlmConfig": ...

class PyLocalMesh:
    """Local mesh for single-process agent communication."""
    def __new__(cls, name: str) -> "PyLocalMesh": ...
    def add_agent(self, agent: "PyAgent") -> PyAgentMessageProcessor: ...
    def add_llm_agent(self, agent: "PyLlmAgent") -> str: ...
    def broadcast(self, payload: str, exclude: Optional[str] = None) -> Any: ...
    def collect_results(self, reminder_interval: float = 30.0) -> Any: ...
    def collect_results_sync(self, reminder_interval: float = 30.0) -> Any: ...
    def get_pending(self) -> Any: ...
    def get_results(self) -> Any: ...
    def has_pending(self) -> bool: ...
    def peek_results(self) -> Any: ...
    def process_messages(self) -> int: ...
    def query(
        self,
        target: str,
        payload: str,
        timeout: float = 60.0,
        reminder_interval: float = 30.0,
    ) -> Any: ...
    def query_sync(
        self,
        target: str,
        payload: str,
        timeout: float = 60.0,
        reminder_interval: float = 30.0,
    ) -> "PyMeshResult": ...
    def send_reminders(self, older_than_secs: float = 30.0) -> Any: ...
    def send_to(self, target: str, payload: str) -> Any: ...
    def send_to_sync(self, target: str, payload: str) -> Any: ...
    def start(self) -> Any: ...
    def submit(self, target: str, payload: str) -> Any: ...
    def submit_sync(self, target: str, payload: str) -> str: ...
    def wait_for(
        self, request_id: str, timeout: float = 60.0, reminder_interval: float = 30.0
    ) -> Any: ...
    def wait_for_sync(
        self, request_id: str, timeout: float = 60.0, reminder_interval: float = 30.0
    ) -> "PyMeshResult": ...

class PyLoggingConfig:
    """Configuration for logging."""
    def __new__(
        cls, log_level: str, log_file_path: Optional[str], json_output: bool
    ) -> "PyLoggingConfig": ...

class PyLoggingHandle:
    """Handle to control logging lifecycle."""

    ...

class PyMemoryEntry:
    """A single entry in agent memory."""
    def __new__(cls, content: str) -> "PyMemoryEntry": ...
    def __repr__(self) -> str: ...
    @property
    def content(self) -> str: ...
    @property
    def created_at(self) -> str: ...
    @property
    def expires_at(self) -> Optional[str]: ...
    @property
    def id(self) -> str: ...
    def is_expired(self) -> bool: ...
    @property
    def metadata(self) -> Dict[str, Any]: ...
    def with_metadata(self, key: str, value: Any) -> "PyMemoryEntry": ...
    def with_ttl_seconds(self, seconds: int) -> "PyMemoryEntry": ...

class PyMemoryQuery:
    """Query builder for memory search."""
    def __new__(cls) -> "PyMemoryQuery": ...
    def __repr__(self) -> str: ...
    def with_filter(self, key: str, value: Any) -> "PyMemoryQuery": ...
    def with_limit(self, limit: int) -> "PyMemoryQuery": ...

class PyMeshRequest:
    """Represents a pending mesh request."""
    def __repr__(self) -> str: ...
    @property
    def elapsed_seconds(self) -> float: ...
    @property
    def id(self) -> str: ...
    @property
    def payload(self) -> str: ...
    @property
    def reminder_count(self) -> int: ...
    @property
    def target(self) -> str: ...

class PyMeshResult:
    """Result from a mesh operation."""
    def __repr__(self) -> str: ...
    @property
    def duration_ms(self) -> int: ...
    @property
    def request_id(self) -> str: ...
    @property
    def response(self) -> str: ...
    @property
    def target(self) -> str: ...

class PyReActConfig:
    """Configuration for ReAct (Reason + Act) mode."""
    def __new__(cls) -> "PyReActConfig": ...
    def with_action_prefix(self, prefix: str) -> "PyReActConfig": ...
    def with_max_iterations(self, max_iterations: int) -> "PyReActConfig": ...
    def with_thought_prefix(self, prefix: str) -> "PyReActConfig": ...

class PyReActResult:
    """Result from ReAct reasoning."""
    def __repr__(self) -> str: ...
    @property
    def answer(self) -> str: ...
    @property
    def finish_reason(self) -> str: ...
    def get_steps(self) -> List["PyReActStep"]: ...
    @property
    def iterations(self) -> int: ...
    def print_trace(self) -> None: ...

class PyReActStep:
    """A single step in ReAct reasoning."""
    def __repr__(self) -> str: ...
    @property
    def action(self) -> Optional[str]: ...
    @property
    def action_input(self) -> Optional[str]: ...
    @property
    def iteration(self) -> int: ...
    @property
    def observation(self) -> Optional[str]: ...
    @property
    def thought(self) -> str: ...

class PyRedisBackend:
    """Redis storage backend for agent memory."""
    def __new__(cls, redis_url: str) -> "PyRedisBackend": ...
    def __repr__(self) -> str: ...
    def clear(self) -> Any: ...
    def count(self) -> int: ...
    def delete(self, id: str) -> bool: ...
    def get(self, id: str) -> Optional["PyMemoryEntry"]: ...
    def search(self, query: "PyMemoryQuery") -> List["PyMemoryEntry"]: ...
    def store(self, entry: "PyMemoryEntry") -> str: ...
    def with_prefix(self, prefix: str) -> "PyRedisBackend": ...
    def with_ttl_seconds(self, seconds: int) -> "PyRedisBackend": ...

class PyToolInvoker:
    """Invokes registered tools/actions."""
    def __new__(cls) -> "PyToolInvoker": ...
    def invoke(self, name: str, inputs: str) -> str: ...
    def register(self, action: "_PyAction") -> Any: ...

class _PyAction:
    """Base action class from Rust bindings."""
    def __new__(
        cls,
        name: str,
        description: str,
        input_schema: str,
        output_schema: Optional[str] = None,
    ) -> "_PyAction": ...
    def execute(self, _context: PyAgentContext, _inputs: Any) -> Any: ...
    def metadata(self) -> str: ...

def get_metrics() -> Dict[str, Any]:
    """Get current metrics from the runtime."""
    ...

def init_logging_py(config: PyLoggingConfig) -> PyLoggingHandle:
    """Initialize logging with the given configuration."""
    ...

# =============================================================================
# PYTHON WRAPPER CLASSES
# =============================================================================

class PyAction(_PyAction):
    """Python-friendly action class with automatic schema generation.

    Subclass this and implement the `execute` method to create custom actions.

    Example:
        class WeatherAction(PyAction):
            def __init__(self):
                super().__init__("get_weather", "Get weather for a location")

            def execute(self, context: PyAgentContext, inputs: dict) -> str:
                location = inputs.get("location", "unknown")
                return f"Weather in {location}: Sunny, 25°C"
    """
    def __new__(
        cls,
        name: str,
        description: str,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None,
    ) -> "PyAction": ...

class FunctionalAction(PyAction):
    """Action wrapper for regular Python functions.

    Automatically generates input schema from function type hints.

    Example:
        def get_weather(location: str) -> str:
            return f"Weather in {location}: Sunny"

        action = FunctionalAction(get_weather, "get_weather", "Get weather info")
    """

    func: Callable[..., Any]

    def __new__(
        cls,
        func: Callable[..., Any],
        name: str,
        description: str,
        input_schema: Optional[str] = None,
        output_schema: Optional[str] = None,
    ) -> "FunctionalAction": ...
    def execute(self, context: PyAgentContext, inputs: Dict[str, Any]) -> Any: ...

class Agent(PyAgent):
    """Python agent with decorator-based action registration.

    Example:
        agent = Agent("my_agent")

        @agent.action(description="Calculate sum of two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        mesh = LocalMesh("mesh")
        mesh.add_agent(agent)
    """

    tool_invoker: PyToolInvoker

    def __init__(self, name: str = "agent") -> None: ...
    def name(self) -> str: ...
    def action(
        self,
        name: Optional[str] = None,
        description: str = "",
    ) -> Callable[[ActionFunc], ActionFunc]:
        """Decorator to register a function as an action.

        Args:
            name: Action name (defaults to function name)
            description: Action description for LLM

        Returns:
            Decorator function
        """
        ...

    def on_message(
        self, message: Any, context: Optional[PyAgentContext] = None
    ) -> Optional[str]:
        """Handle incoming message. Override this in subclasses.

        Can be synchronous or async (async def).

        Args:
            message: The message content
            context: Optional agent context

        Returns:
            Response string or None
        """
        ...

    def send_message(self, message: str) -> str:
        """Send a message to the agent and get response."""
        ...

    def last_response(self) -> Optional[str]:
        """Get the last response from the agent."""
        ...

class LocalMesh(PyLocalMesh):
    """Local mesh with Python agent and LlmAgent support.

    Example:
        mesh = LocalMesh("my_mesh")
        agent = Agent("my_agent")
        mesh.add_agent(agent)
        mesh.send_to("my_agent", "Hello")
        mesh.process_messages()
    """
    def add_llm_agent(self, agent: "LlmAgent") -> str:
        """Add an LlmAgent to the mesh.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        ...

class DistributedMesh(PyDistributedMesh):
    """Distributed mesh with Python agent and LlmAgent support.

    Example:
        mesh = DistributedMesh("my_mesh", 9000)
        agent = Agent("my_agent")
        mesh.add_agent(agent)
        mesh.process_messages()
    """
    def add_llm_agent(self, agent: "LlmAgent") -> str:
        """Add an LlmAgent to the mesh.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        ...

# LlmConfig is an alias for PyLlmConfig
LlmConfig = PyLlmConfig

class LlmAgent(Agent):
    """Python wrapper for LLM agents with fluent builder API.

    Example:
        # Builder style
        agent = LlmAgent("my_agent", "ollama::gemma3:latest")
        agent.with_system_prompt("You are a helpful assistant.")
        agent.build()

        # Config style
        config = LlmConfig.builder().provider("ollama").model("llama2").build()
        agent = LlmAgent("my_agent", config)

        # Send messages
        response = await agent.send_message("Hello!")
        # Or synchronously
        response = agent.send_message_sync("Hello!")
    """

    _agent: PyLlmAgent

    def __init__(
        self,
        name: str,
        model_or_config: str | LlmConfig | PyLlmConfig,
        memory: Optional[Any] = None,
    ) -> None:
        """Create a new LLM agent.

        Args:
            name: Agent name
            model_or_config: Model string (e.g., "ollama::llama2") or LlmConfig
            memory: Optional memory backend
        """
        ...

    def name(self) -> str: ...

    # Builder methods
    def with_api_key(self, api_key: str) -> "LlmAgent":
        """Set the API key for the LLM provider."""
        ...

    def with_system_prompt(self, prompt: str) -> "LlmAgent":
        """Set the system prompt for the agent."""
        ...

    def with_temperature(self, temp: float) -> "LlmAgent":
        """Set the temperature for generation (0.0 - 2.0)."""
        ...

    def with_max_tokens(self, tokens: int) -> "LlmAgent":
        """Set the maximum number of tokens to generate."""
        ...

    def with_memory(self, memory: Any) -> "LlmAgent":
        """Set the memory backend for the agent."""
        ...

    def build(self) -> "LlmAgent":
        """Build the agent. Must be called before sending messages."""
        ...

    def is_built(self) -> bool:
        """Check if the agent has been built."""
        ...

    # Message methods
    async def send_message(self, message: str) -> str:
        """Send a message to the agent asynchronously (default).

        This is the primary async method. Use `await agent.send_message(...)`.
        For blocking calls, use `send_message_sync()`.
        """
        ...

    def send_message_sync(self, message: str) -> str:
        """Send a message to the agent synchronously (blocking).

        Use this only when you can't use async/await.
        """
        ...

    async def query(self, message: str) -> str:
        """Alias for send_message (async)."""
        ...

    # Action registration
    def register_action(self, action: _PyAction) -> "LlmAgent":
        """Register a Python action with the agent."""
        ...

    def action(
        self,
        name: Optional[str] = None,
        description: str = "",
    ) -> Callable[[ActionFunc], ActionFunc]:
        """Decorator to register a function as an action.

        Example:
            @agent.action(description="Get weather")
            def get_weather(location: str) -> str:
                return "Sunny"
        """
        ...

    # ReAct methods
    def with_react(self, config: Optional[PyReActConfig] = None) -> "LlmAgent":
        """Enable ReAct (Reason + Act) mode."""
        ...

    def send_message_react(self, message: str) -> PyReActResult:
        """Send a message using ReAct reasoning mode."""
        ...

# ReAct Framework - aliases to Rust implementations
ReActConfig = PyReActConfig
ReActStep = PyReActStep
ReActResult = PyReActResult

# Memory component aliases
MemoryEntry = PyMemoryEntry
MemoryQuery = PyMemoryQuery
InMemoryBackend = PyInMemoryBackend
RedisBackend = PyRedisBackend

class Memory(ABC):
    """Abstract base class for custom memory backends.

    Extend this to create custom memory implementations for LlmAgent.
    Useful for integrating vector databases, cloud storage, etc.

    Example:
        class VectorMemory(Memory):
            def __init__(self):
                self.vectors = {}

            def store(self, entry: MemoryEntry) -> str:
                self.vectors[entry.id] = entry
                return entry.id

            def get(self, id: str) -> Optional[MemoryEntry]:
                return self.vectors.get(id)

            def search(self, query: MemoryQuery) -> List[MemoryEntry]:
                return list(self.vectors.values())

            def delete(self, id: str) -> bool:
                if id in self.vectors:
                    del self.vectors[id]
                    return True
                return False

            def clear(self) -> None:
                self.vectors.clear()

            def count(self) -> int:
                return len(self.vectors)

        # Use with agent
        agent = LlmAgent("agent", "model")
        agent.with_memory(VectorMemory())
    """

    @abstractmethod
    def store(self, entry: MemoryEntry) -> str:
        """Store a memory entry and return its ID."""
        ...

    @abstractmethod
    def get(self, id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID."""
        ...

    @abstractmethod
    def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search for memory entries matching the query."""
        ...

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a memory entry. Returns True if deleted."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory entries."""
        ...

    @abstractmethod
    def count(self) -> int:
        """Return the number of entries in memory."""
        ...

# Logging aliases
LoggingConfig = PyLoggingConfig
LoggingHandle = PyLoggingHandle

def init_logging(config: LoggingConfig) -> LoggingHandle:
    """Initialize logging with the given configuration."""
    ...

# Mesh aliases for cleaner API
MeshRequest = PyMeshRequest
MeshResult = PyMeshResult

class AsyncMessageProcessor:
    """Background processor for Python agent messages.

    Use as an async context manager to automatically process
    messages for Python agents in the background.

    Example:
        mesh = LocalMesh("my_mesh")
        agent = Agent("my_agent")
        mesh.add_agent(agent)

        async with AsyncMessageProcessor(mesh, interval_ms=100):
            await mesh.send_to("my_agent", "Hello")
            await asyncio.sleep(1)  # Agent processes messages in background
    """

    mesh: LocalMesh | DistributedMesh
    interval: float

    def __init__(
        self, mesh: LocalMesh | DistributedMesh, interval_ms: int = 100
    ) -> None:
        """Create a message processor.

        Args:
            mesh: LocalMesh or DistributedMesh instance
            interval_ms: Processing interval in milliseconds (default: 100)
        """
        ...

    async def start(self) -> None:
        """Start background processing loop."""
        ...

    async def stop(self) -> None:
        """Stop background processing."""
        ...

    async def __aenter__(self) -> "AsyncMessageProcessor": ...
    async def __aexit__(self, *args: Any) -> None: ...

# =============================================================================
# MODULE EXPORTS
# =============================================================================

__all__: List[str]
