"""
NOSTROMO-CORE
=============

Core domain logic for MU-TH-UR 6000 chatbot.

Provides ChatEngine, LLM adapters, and the MU-TH-UR theme.
"""

from nostromo_core.engine import ChatEngine
from nostromo_core.models import ChatResponse, Message, Session

__version__ = "0.1.0"
__all__ = ["ChatEngine", "Message", "ChatResponse", "Session"]
