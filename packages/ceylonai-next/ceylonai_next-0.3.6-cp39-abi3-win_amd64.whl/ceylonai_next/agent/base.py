"""Base agent classes."""

import inspect
from typing import Optional, Any

from ceylonai_next.ceylonai_next import (
    PyAgent,
    PyAgentContext,
    _PyAction,
    PyToolInvoker,
)
from ceylonai_next._utils.schema import generate_schema_from_signature


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

    def __new__(cls, name, description, input_schema=None, output_schema=None):
        if input_schema is None:
            input_schema = generate_schema_from_signature(cls.execute)
        return super().__new__(cls, name, description, input_schema, output_schema)


class FunctionalAction(PyAction):
    """Action wrapper for regular Python functions.

    Automatically generates input schema from function type hints.

    Example:
        def get_weather(location: str) -> str:
            return f"Weather in {location}: Sunny"

        action = FunctionalAction(get_weather, "get_weather", "Get weather info")
    """

    def __new__(cls, func, name, description, input_schema=None, output_schema=None):
        # If input_schema is not provided, generate it from the function
        if input_schema is None:
            input_schema = generate_schema_from_signature(func)
        # Create the instance using the parent's __new__
        instance = super().__new__(cls, name, description, input_schema, output_schema)
        # Store the function on the instance
        instance.func = func
        return instance

    def execute(self, context, inputs):
        """Execute the wrapped function with the given inputs."""
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
    """Python agent with decorator-based action registration.

    Example:
        agent = Agent("my_agent")

        @agent.action(description="Calculate sum of two numbers")
        def add(a: int, b: int) -> int:
            return a + b

        mesh = LocalMesh("mesh")
        mesh.add_agent(agent)
    """

    def __init__(self, name: str = "agent"):
        """Create a new agent.

        Args:
            name: The agent name (default: "agent")
        """
        super().__init__()
        self._agent_name = name
        self.tool_invoker = PyToolInvoker()

    def name(self) -> str:
        """Return the agent name."""
        return self._agent_name

    def action(self, name: Optional[str] = None, description: str = ""):
        """Decorator to register a function as an action.

        Args:
            name: Action name (defaults to function name)
            description: Action description for LLM

        Returns:
            Decorator function
        """

        def decorator(func):
            action_name = name or func.__name__
            action_desc = description or func.__doc__ or ""

            action = FunctionalAction(func, action_name, action_desc)
            self.tool_invoker.register(action)
            return func

        return decorator

    def on_message(
        self, message: Any, context: Optional[PyAgentContext] = None
    ) -> Optional[str]:
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

    def send_message(self, message: str) -> str:
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

    def last_response(self) -> Optional[str]:
        """Get the last response from the agent.

        Returns:
            The last response string, or None if no messages sent yet
        """
        return self.get_last_response()
