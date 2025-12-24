"""
Thematic error messages for MU-TH-UR 6000.

All error messages maintain the retro computer aesthetic
of the original Aliens film.
"""

from enum import Enum

from nostromo_core.theme.constants import SYSTEM_NAME


class NostromoError(Enum):
    """
    Themed error codes and message templates.

    Use format_error() to generate the full message.
    """

    # Authentication & Authorization
    NO_AUTH = "UNABLE TO ACCESS {system}. CREW AUTHORIZATION REQUIRED."
    AUTH_FAILED = "AUTHORIZATION REJECTED. VERIFY CREW CREDENTIALS."
    VAULT_LOCKED = "VAULT ACCESS DENIED. INCORRECT AUTHORIZATION CODE."
    SESSION_EXPIRED = "SESSION EXPIRED. RE-AUTHENTICATION REQUIRED."
    PERMISSION_DENIED = "ACCESS DENIED. INSUFFICIENT CLEARANCE LEVEL."

    # Provider & Configuration
    PROVIDER_MISSING = "{provider} INTERFACE NOT INITIALIZED. RUN: nostromo configure --provider {provider_lower}"
    PROVIDER_ERROR = "{provider} INTERFACE MALFUNCTION. CHECK CONFIGURATION."
    CONFIG_CORRUPT = "CONFIGURATION CORRUPTED. RESTORE DEFAULT? [Y/N]"
    CONFIG_MISSING = "CONFIGURATION NOT FOUND. RUN: nostromo configure"
    INVALID_PROVIDER = "UNKNOWN PROVIDER: {provider}. SUPPORTED: ANTHROPIC, OPENAI."

    # Network & Connection
    UPLINK_FAILURE = "UPLINK FAILURE. UNABLE TO ESTABLISH CONNECTION."
    TIMEOUT = "CONNECTION TIMEOUT. RETRY TRANSMISSION."
    RATE_LIMITED = "INTERFACE LOCKOUT IN EFFECT. RETRY IN {seconds}S."

    # Processing
    PROCESSING_ERROR = "{system} PROCESSING ERROR. PLEASE REPHRASE QUERY."
    INVALID_INPUT = "INVALID INPUT FORMAT. CHECK SYNTAX AND RETRY."
    RESPONSE_ERROR = "RESPONSE DATA CORRUPTION DETECTED. RETRY QUERY."

    # Key Management
    KEY_MISSING = "API KEY NOT CONFIGURED FOR {provider}. RUN: nostromo configure --provider {provider_lower}"
    KEY_INVALID = "API KEY REJECTED BY {provider}. VERIFY CREDENTIALS."
    KEY_ROTATION_ABORT = "KEY ROTATION ABORTED. PREVIOUS KEY RETAINED."
    KEY_ROTATION_SUCCESS = "KEY ROTATION COMPLETE FOR {provider}. PREVIOUS KEY PURGED."

    # Session & History
    SESSION_NOT_FOUND = "SESSION {session_id} NOT FOUND IN MEMORY BANKS."
    HISTORY_CORRUPT = "HISTORY DATA CORRUPTED. CLEAR AND REINITIALIZE? [Y/N]"
    HISTORY_SAVE_FAILED = "FAILED TO PERSIST SESSION DATA. CHECK STORAGE ACCESS."

    # System
    SYSTEM_ERROR = "CRITICAL {system} ERROR. CONTACT WEYLAND-YUTANI SUPPORT."
    SHUTDOWN = "INITIATING SHUTDOWN SEQUENCE..."
    STARTUP = "INITIALIZING {system}..."

    # User Feedback
    GOODBYE = "TERMINATING UPLINK. SLEEP WELL."
    WELCOME = "GOOD MORNING, CREW. {system} ONLINE AND READY."
    CONFIRM_ACTION = "CONFIRM ACTION: {action}? [Y/N]"


def format_error(
    error: NostromoError,
    *,
    system: str = SYSTEM_NAME,
    **kwargs: str,
) -> str:
    """
    Format a themed error message.

    Args:
        error: The NostromoError enum value
        system: System name (default: MU-TH-UR 6000)
        **kwargs: Additional format parameters

    Returns:
        Formatted error message string

    Example:
        >>> format_error(NostromoError.RATE_LIMITED, seconds="30")
        'INTERFACE LOCKOUT IN EFFECT. RETRY IN 30S.'
    """
    # Build format dict with defaults
    format_dict: dict[str, str] = {
        "system": system,
        **kwargs,
    }

    # Add lowercase variants for providers
    if "provider" in format_dict:
        format_dict["provider_lower"] = format_dict["provider"].lower()

    return error.value.format(**format_dict)


def get_error_for_exception(exception: Exception) -> tuple[NostromoError, dict[str, str]]:
    """
    Map a Python exception to a themed error.

    Args:
        exception: The exception to map

    Returns:
        Tuple of (NostromoError, format_kwargs)
    """
    error_str = str(exception).lower()

    if "authentication" in error_str or "api_key" in error_str or "unauthorized" in error_str:
        return NostromoError.AUTH_FAILED, {}
    elif "rate" in error_str and "limit" in error_str:
        return NostromoError.RATE_LIMITED, {"seconds": "60"}
    elif "timeout" in error_str:
        return NostromoError.TIMEOUT, {}
    elif "connection" in error_str or "network" in error_str:
        return NostromoError.UPLINK_FAILURE, {}
    elif "permission" in error_str or "access" in error_str:
        return NostromoError.PERMISSION_DENIED, {}
    else:
        return NostromoError.PROCESSING_ERROR, {}
