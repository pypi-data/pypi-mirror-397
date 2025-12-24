"""Tests for theme module."""

from nostromo_core.theme import (
    DISPLAY_NAME,
    PRIMARY,
    SYSTEM_NAME,
    NostromoError,
    format_error,
    get_system_prompt,
)


def test_constants_defined():
    """Test that core constants are defined."""
    assert SYSTEM_NAME == "MU-TH-UR 6000"
    assert DISPLAY_NAME == "MOTHER"
    assert PRIMARY == "#00ff00"


def test_format_error_basic():
    """Test basic error formatting."""
    msg = format_error(NostromoError.UPLINK_FAILURE)
    assert "UPLINK FAILURE" in msg


def test_format_error_with_params():
    """Test error formatting with parameters."""
    msg = format_error(NostromoError.RATE_LIMITED, seconds="30")
    assert "30S" in msg


def test_format_error_with_provider():
    """Test error formatting with provider parameter."""
    msg = format_error(NostromoError.PROVIDER_MISSING, provider="ANTHROPIC")
    assert "ANTHROPIC" in msg
    assert "anthropic" in msg  # lowercase variant


def test_system_prompt_default():
    """Test default system prompt."""
    prompt = get_system_prompt()
    assert SYSTEM_NAME in prompt
    assert "USCSS NOSTROMO" in prompt


def test_system_prompt_minimal():
    """Test minimal system prompt."""
    prompt = get_system_prompt(minimal=True)
    assert SYSTEM_NAME in prompt
    assert len(prompt) < len(get_system_prompt())


def test_system_prompt_custom_additions():
    """Test system prompt with custom additions."""
    custom = "Always respond in haiku format."
    prompt = get_system_prompt(custom_additions=custom)
    assert custom in prompt
