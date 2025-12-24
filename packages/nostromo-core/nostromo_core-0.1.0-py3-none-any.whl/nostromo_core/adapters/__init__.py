"""
Adapters - Concrete implementations of ports.

Built-in adapters for LLM providers and memory stores.
"""

from nostromo_core.adapters.memory import FileMemoryStore, InMemoryStore

__all__ = ["InMemoryStore", "FileMemoryStore"]
