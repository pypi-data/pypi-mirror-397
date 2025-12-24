"""
Theme - MU-TH-UR 6000 visual identity and messaging.

Provides colors, constants, error messages, and prompts
that adapters use to maintain consistent aesthetic.
"""

from nostromo_core.theme.constants import (
    BACKGROUND,
    BORDER,
    DISPLAY_NAME,
    ERROR,
    HEADER_ART,
    HEADER_COMPACT,
    PRIMARY,
    PRIMARY_DIM,
    SHIP_NAME,
    SYSTEM_NAME,
    WARNING,
)
from nostromo_core.theme.errors import NostromoError, format_error
from nostromo_core.theme.prompts import get_system_prompt

__all__ = [
    # Constants
    "SYSTEM_NAME",
    "DISPLAY_NAME",
    "SHIP_NAME",
    "PRIMARY",
    "PRIMARY_DIM",
    "BACKGROUND",
    "BORDER",
    "ERROR",
    "WARNING",
    "HEADER_ART",
    "HEADER_COMPACT",
    # Errors
    "NostromoError",
    "format_error",
    # Prompts
    "get_system_prompt",
]
