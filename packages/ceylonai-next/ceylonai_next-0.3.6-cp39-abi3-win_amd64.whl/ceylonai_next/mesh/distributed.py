"""Distributed mesh for multi-node agent communication."""

from ceylonai_next.ceylonai_next import PyDistributedMesh


class DistributedMesh(PyDistributedMesh):
    """DistributedMesh with LlmAgent support.

    Example:
        mesh = DistributedMesh("my_mesh", 9000)
        agent = Agent("my_agent")
        mesh.add_agent(agent)
        mesh.process_messages()  # Process pending messages (Rust-managed)
    """

    def add_llm_agent(self, agent) -> str:
        """Add an LlmAgent to the mesh.

        Args:
            agent: An LlmAgent instance (must be built first)

        Returns:
            The agent name for reference
        """
        # Unwrap the internal _agent (PyLlmAgent) for the Rust binding
        return super().add_llm_agent(agent._agent)
