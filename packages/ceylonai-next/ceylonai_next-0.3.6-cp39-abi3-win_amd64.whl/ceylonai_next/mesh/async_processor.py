"""Async message processor for background message handling."""

import asyncio
from typing import Optional, Union


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
