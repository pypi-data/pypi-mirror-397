"""
Theme constants - Colors, names, and ASCII art.

These values define the MU-TH-UR 6000 visual identity
and are used by all adapters (CLI, API, Web).
"""

# =============================================================================
# IDENTITY
# =============================================================================

SYSTEM_NAME = "MU-TH-UR 6000"
DISPLAY_NAME = "MOTHER"
SHIP_NAME = "USCSS NOSTROMO"
INTERFACE_VERSION = "2037"

# =============================================================================
# COLORS (Phosphor Green CRT Aesthetic)
# =============================================================================

# Primary green - main text color
PRIMARY = "#00ff00"

# Dimmed green - borders, secondary elements
PRIMARY_DIM = "#005500"

# Background - near black
BACKGROUND = "#0a0a0a"

# Border color
BORDER = "#003300"

# Error - amber/orange like warning lights
ERROR = "#ff3300"

# Warning - yellow/amber
WARNING = "#ffaa00"

# Success - bright green
SUCCESS = "#00ff00"

# Info - cyan-ish green
INFO = "#00ffaa"

# =============================================================================
# ASCII ART
# =============================================================================

HEADER_ART = r"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   ███╗   ███╗██╗   ██╗████████╗██╗  ██╗██╗   ██╗██████╗      ██████╗  ██████╗ ║
║   ████╗ ████║██║   ██║╚══██╔══╝██║  ██║██║   ██║██╔══██╗    ██╔════╝ ██╔═████╗║
║   ██╔████╔██║██║   ██║   ██║   ███████║██║   ██║██████╔╝    ███████╗ ██║██╔██║║
║   ██║╚██╔╝██║██║   ██║   ██║   ██╔══██║██║   ██║██╔══██╗    ██╔═══██╗████╔╝██║║
║   ██║ ╚═╝ ██║╚██████╔╝   ██║   ██║  ██║╚██████╔╝██║  ██║    ╚██████╔╝╚██████╔╝║
║   ╚═╝     ╚═╝ ╚═════╝    ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝     ╚═════╝  ╚═════╝ ║
║                                                                              ║
║                        INTERFACE 2037 - USCSS NOSTROMO                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

HEADER_COMPACT = r"""
╔══════════════════════════════════════════════════════════════╗
║  MU-TH-UR 6000 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ USCSS NOSTROMO ║
╚══════════════════════════════════════════════════════════════╝
"""

BOOT_SEQUENCE = [
    "INITIALIZING MU-TH-UR 6000...",
    "LOADING CORE SYSTEMS...",
    "ESTABLISHING UPLINK...",
    "INTERFACE READY.",
    "",
    "GOOD MORNING, CREW.",
]

SHUTDOWN_SEQUENCE = [
    "",
    "TERMINATING SESSION...",
    "UPLINK CLOSED.",
    "MU-TH-UR 6000 OFFLINE.",
]

# =============================================================================
# UI ELEMENTS
# =============================================================================

PROMPT_PREFIX = "▶"
RESPONSE_PREFIX = "◀"
CURSOR_CHAR = "█"
DIVIDER = "─" * 60

# Status indicators
STATUS_OK = "●"
STATUS_ERROR = "○"
STATUS_PENDING = "◌"
