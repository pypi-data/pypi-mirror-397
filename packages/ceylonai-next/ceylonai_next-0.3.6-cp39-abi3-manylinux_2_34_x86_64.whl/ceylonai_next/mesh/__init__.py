"""Mesh networking components for ceylonai_next.

This module provides mesh classes for agent communication:
- LocalMesh: Single-process mesh for local agent communication
- DistributedMesh: Multi-node mesh for distributed agents
- AsyncMessageProcessor: Background message processing
"""

from ceylonai_next.mesh.local import LocalMesh
from ceylonai_next.mesh.distributed import DistributedMesh
from ceylonai_next.mesh.async_processor import AsyncMessageProcessor

__all__ = [
    "LocalMesh",
    "DistributedMesh",
    "AsyncMessageProcessor",
]
