# Import from the native Rust extension module explicitly
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
import asyncio
import inspect
import json
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

# Define the public API
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


def _generate_schema_from_signature(func):
    """
    Generates a JSON schema from a function's type hints.
    """
    sig = inspect.signature(func)
    properties = {}
    required = []

    type_map = {
        str: "string",
        int: "integer",
        float: "number",
        bool: "boolean",
        list: "array",
        dict: "object",
    }

    for name, param in sig.parameters.items():
        if name == "self":
            continue

        param_type = "string"  # Default to string
        if param.annotation != inspect.Parameter.empty:
            if param.annotation in type_map:
                param_type = type_map[param.annotation]
            # Handle Optional, List, etc. later if needed

        properties[name] = {"type": param_type}

        if param.default == inspect.Parameter.empty:
            required.append(name)

    schema = {
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required

    return json.dumps(schema)


class PyAction(_PyAction):
    def __new__(cls, name, description, input_schema=None, output_schema=None):
        if input_schema is None:
            input_schema = _generate_schema_from_signature(cls.execute)
        return super().__new__(cls, name, description, input_schema, output_schema)


class FunctionalAction(PyAction):
    def __new__(cls, func, name, description, input_schema=None, output_schema=None):
        # If input_schema is not provided, generate it from the function
        if input_schema is None:
            input_schema = _generate_schema_from_signature(func)
        # Create the instance using the parent's __new__
        instance = super().__new__(cls, name, description, input_schema, output_schema)
        # Store the function on the instance
        instance.func = func
        return instance

    def execute(self, context, inputs):
        # We need to map inputs to function arguments
        # For now, we assume inputs is a dict matching arguments
        # We also need to pass context if the function expects it

        sig = inspect.signature(self.func)
        kwargs = {}

        for name, param in sig.parameters.items():
            if name == "context":
                kwargs["context"] = context
            elif name in inputs:
                kwargs[name] = inputs[name]
            elif param.default != inspect.Parameter.empty:
                continue  # Use default
            else:
                # Missing argument
                pass

        return self.func(**kwargs)


class Agent(PyAgent):
    def __init__(self, name="agent"):
        super().__init__()
        self._agent_name = name
        self.tool_invoker = PyToolInvoker()

    def name(self):
        return self._agent_name

    def action(self, name=None, description=""):
        def decorator(func):
            action_name = name or func.__name__
            action_desc = description or func.__doc__ or ""

            action = FunctionalAction(func, action_name, action_desc)
            self.tool_invoker.register(action)
            return func

        return decorator

    def on_message(self, message, context=None):
        """Handle incoming message. Override this method to process messages.

        Can be a synchronous method or an async method (async def).

        To return a response, return it from this method and it will be
        stored in last_response.

        Args:
            message: The message content (bytes or string)
            context: Optional PyAgentContext

        Returns:
            Response string that will be stored
        """
        # Default implementation does nothing
        # Subclasses should override this
        return None

    def send_message(self, message):
        """Send a message to the agent and get the response.

        This wraps on_message and returns the response.

        Args:
            message: Message string to send

        Returns:
            Response from the agent's on_message handler
        """
        # Create a dummy context
        context = PyAgentContext("python")

        # Call on_message (which can be overridden by subclasses)
        response = self.on_message(message, context)

        # Store the response in Rust
        self.set_last_response(response)

        return response if response is not None else "Message received"

    def last_response(self):
        """Get the last response from the agent.

        Returns:
            The last response string, or None if no messages sent yet
        """
        return self.get_last_response()


class LocalMesh(PyLocalMesh):
    """LocalMesh with LlmAgent support.

    Example:
        mesh = LocalMesh("my_mesh")
        agent = Agent("my_agent")
        mesh.add_agent(agent)
        mesh.send_to("my_agent", "Hello")
        mesh.process_messages()  # Process pending messages (Rust-managed)
    """

    def add_llm_agent(self, agent):
        """Add an LlmAgent to the mesh.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        # Unwrap the internal _agent (PyLlmAgent) for the Rust binding
        return super().add_llm_agent(agent._agent)


class DistributedMesh(PyDistributedMesh):
    """DistributedMesh with LlmAgent support.

    Example:
        mesh = DistributedMesh("my_mesh", 9000)
        agent = Agent("my_agent")
        mesh.add_agent(agent)
        mesh.process_messages()  # Process pending messages (Rust-managed)
    """

    def add_llm_agent(self, agent):
        """Add an LlmAgent to the mesh.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        # Unwrap the internal _agent (PyLlmAgent) for the Rust binding
        return super().add_llm_agent(agent._agent)


# LlmConfig alias - use PyLlmConfig.builder() for configuration
LlmConfig = PyLlmConfig


class LlmAgent(Agent):
    """Python wrapper for LlmAgent with fluent builder API.

    Example:
        # Builder style
        agent = LlmAgent("my_agent", "ollama::gemma3:latest")
        agent.with_system_prompt("You are a helpful assistant.")
        agent.build()

        # Config style
        config = LlmConfig.builder().provider("ollama").model("llama2").build()
        agent = LlmAgent("my_agent", config)

        # Connect to mesh (after building)
        mesh = LocalMesh("my_mesh")
        mesh.add_llm_agent(agent)
    """

    def __new__(cls, *args, **kwargs):
        """Override __new__ to bypass PyAgent initialization."""
        return Agent.__new__(cls)

    def __init__(self, name, model_or_config, memory=None):
        """Create a new LLM agent.

        Args:
            name: Agent name (str)
            model_or_config: Model string (str) OR LlmConfig object
            memory: InMemoryBackend object (optional)
        """
        self._agent_name = name

        if isinstance(model_or_config, (LlmConfig, PyLlmConfig)):
            self._agent = PyLlmAgent.with_config(name, model_or_config)
        else:
            self._agent = PyLlmAgent(name, model_or_config)

        if memory:
            self._agent.with_memory(memory)

    def name(self):
        """Return the agent name."""
        return self._agent_name

    # Builder methods - delegate to Rust PyLlmAgent
    def with_api_key(self, api_key):
        """Set the API key for the LLM provider."""
        self._agent.with_api_key(api_key)
        return self

    def with_system_prompt(self, prompt):
        """Set the system prompt for the agent."""
        self._agent.with_system_prompt(prompt)
        return self

    def with_temperature(self, temp):
        """Set the temperature for generation (0.0 - 2.0)."""
        self._agent.with_temperature(temp)
        return self

    def with_max_tokens(self, tokens):
        """Set the maximum number of tokens to generate."""
        self._agent.with_max_tokens(tokens)
        return self

    def with_memory(self, memory):
        """Set the memory backend for the agent."""
        self._agent.with_memory(memory)
        return self

    def build(self):
        """Build the agent. Must be called before sending messages."""
        self._agent.build()
        return self

    def is_built(self):
        """Check if the agent has been built."""
        return self._agent.is_built()

    # Message methods - async-first pattern
    async def send_message(self, message):
        """Send a message to the agent asynchronously (default).

        This is the primary async method. Use await mesh.send_message(...).
        For blocking calls, use send_message_sync().
        """
        return await self._agent.send_message(message)

    def send_message_sync(self, message):
        """Send a message to the agent synchronously (blocking).

        Use this only when you can't use async/await.
        """
        return self._agent.send_message_sync(message)

    async def query(self, message):
        """Alias for send_message (async)."""
        return await self.send_message(message)

    # Action registration - Python-specific due to decorator pattern
    def register_action(self, action):
        """Register a Python action with the agent."""
        self._agent.add_action(action)
        return self

    def action(self, name=None, description=""):
        """Decorator to register a function as an action.

        Example:
            @agent.action(description="Get weather")
            def get_weather(location: str):
                return "Sunny"
        """

        def decorator(func):
            action_name = name or func.__name__
            action_desc = description or func.__doc__ or ""
            action = FunctionalAction(func, action_name, action_desc)
            self.register_action(action)
            return func

        return decorator

    # ReAct methods - delegate to Rust
    def with_react(self, config=None):
        """Enable ReAct (Reason + Act) mode."""
        if config is None:
            config = PyReActConfig()
        self._agent.with_react(config)
        return self

    def send_message_react(self, message):
        """Send a message using ReAct reasoning mode."""
        return self._agent.send_message_react(message)


# ReAct Framework - use Rust implementations directly
# These aliases maintain backward compatibility with existing code
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

    Extend this class to create custom memory implementations that can be used
    with LlmAgent. Useful for integrating vector databases, cloud storage, etc.

    Example:
        class VectorMemory(Memory):
            def __init__(self):
                self.vectors = {}

            def store(self, entry: MemoryEntry) -> str:
                # Store with vector embedding
                self.vectors[entry.id] = entry
                return entry.id

            def get(self, id: str) -> Optional[MemoryEntry]:
                return self.vectors.get(id)

            def search(self, query: MemoryQuery) -> List[MemoryEntry]:
                # Implement vector similarity search
                return list(self.vectors.values())

            def delete(self, id: str) -> bool:
                if id in self.vectors:
                    del self.vectors[id]
                    return True
                return False

            def clear(self):
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
        pass

    @abstractmethod
    def get(self, id: str) -> Optional[MemoryEntry]:
        """Retrieve a memory entry by ID."""
        pass

    @abstractmethod
    def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search for memory entries matching the query."""
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete a memory entry. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def clear(self):
        """Clear all memory entries."""
        pass

    @abstractmethod
    def count(self) -> int:
        """Return the number of entries in memory."""
        pass


# Logging aliases
LoggingConfig = PyLoggingConfig
LoggingHandle = PyLoggingHandle
init_logging = init_logging_py


# Mesh Request/Result aliases for cleaner Python API
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

    def __init__(self, mesh, interval_ms: int = 100):
        """Create a message processor.

        Args:
            mesh: LocalMesh or DistributedMesh instance
            interval_ms: Processing interval in milliseconds (default: 100)
        """
        self.mesh = mesh
        self.interval = interval_ms / 1000.0
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start background processing loop."""
        self._running = True
        self._task = asyncio.create_task(self._process_loop())

    async def stop(self):
        """Stop background processing."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _process_loop(self):
        """Internal processing loop."""
        while self._running:
            self.mesh.process_messages()
            await asyncio.sleep(self.interval)

    async def __aenter__(self):
        await self.start()
        return self

    async def __aexit__(self, *args):
        await self.stop()
