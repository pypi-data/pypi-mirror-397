"""Memory backends and base classes."""

from abc import ABC, abstractmethod
from typing import List, Optional

from ceylonai_next.ceylonai_next import (
    PyMemoryEntry,
    PyMemoryQuery,
    PyInMemoryBackend,
    PyRedisBackend,
)


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
