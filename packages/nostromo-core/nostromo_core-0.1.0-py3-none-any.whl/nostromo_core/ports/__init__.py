"""
Ports - Abstract interfaces for external dependencies.

These define the contracts that adapters must implement.
"""

from nostromo_core.ports.llm import AbstractLLMProvider
from nostromo_core.ports.memory import AbstractMemoryStore

__all__ = ["AbstractLLMProvider", "AbstractMemoryStore"]
