"""LLM-powered agent classes."""

from typing import Optional, Any

from ceylonai_next.ceylonai_next import (
    PyLlmAgent,
    PyLlmConfig,
    PyReActConfig,
)
from ceylonai_next.agent.base import Agent, FunctionalAction


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

    def __init__(self, name: str, model_or_config: Any, memory: Any = None):
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

    def name(self) -> str:
        """Return the agent name."""
        return self._agent_name

    # Builder methods - delegate to Rust PyLlmAgent
    def with_api_key(self, api_key: str) -> "LlmAgent":
        """Set the API key for the LLM provider."""
        self._agent.with_api_key(api_key)
        return self

    def with_system_prompt(self, prompt: str) -> "LlmAgent":
        """Set the system prompt for the agent."""
        self._agent.with_system_prompt(prompt)
        return self

    def with_temperature(self, temp: float) -> "LlmAgent":
        """Set the temperature for generation (0.0 - 2.0)."""
        self._agent.with_temperature(temp)
        return self

    def with_max_tokens(self, tokens: int) -> "LlmAgent":
        """Set the maximum number of tokens to generate."""
        self._agent.with_max_tokens(tokens)
        return self

    def with_memory(self, memory: Any) -> "LlmAgent":
        """Set the memory backend for the agent."""
        self._agent.with_memory(memory)
        return self

    def build(self) -> "LlmAgent":
        """Build the agent. Must be called before sending messages."""
        self._agent.build()
        return self

    def is_built(self) -> bool:
        """Check if the agent has been built."""
        return self._agent.is_built()

    # Message methods - async-first pattern
    async def send_message(self, message: str) -> str:
        """Send a message to the agent asynchronously (default).

        This is the primary async method. Use await mesh.send_message(...).
        For blocking calls, use send_message_sync().
        """
        return await self._agent.send_message(message)

    def send_message_sync(self, message: str) -> str:
        """Send a message to the agent synchronously (blocking).

        Use this only when you can't use async/await.
        """
        return self._agent.send_message_sync(message)

    async def query(self, message: str) -> str:
        """Alias for send_message (async)."""
        return await self.send_message(message)

    # Action registration - Python-specific due to decorator pattern
    def register_action(self, action) -> "LlmAgent":
        """Register a Python action with the agent."""
        self._agent.add_action(action)
        return self

    def action(self, name: Optional[str] = None, description: str = ""):
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
    def with_react(self, config: Optional[PyReActConfig] = None) -> "LlmAgent":
        """Enable ReAct (Reason + Act) mode."""
        if config is None:
            config = PyReActConfig()
        self._agent.with_react(config)
        return self

    def send_message_react(self, message: str):
        """Send a message using ReAct reasoning mode."""
        return self._agent.send_message_react(message)
