#!/usr/bin/env python3
"""
Retry utilities for SpeakUB TTS operations.

This module provides shared retry delay calculation utilities
that can be used across different retry scenarios while maintaining
scenario-specific logic.
"""

import logging
import random
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def calculate_retry_delay(
    attempt: int,
    base_delay: float,
    use_jitter: bool = False,
    jitter_range: Tuple[float, float] = (0.5, 1.5),
    exponential_factor: float = 2.0,
    max_delay: Optional[float] = None
) -> float:
    """
    Calculate retry delay with optional jitter and exponential backoff.

    This is a pure function that only handles delay calculation,
    leaving retry logic and sleep operations to the caller.

    Args:
        attempt: Current attempt number (0-based)
        base_delay: Base delay in seconds
        use_jitter: Whether to apply random jitter
        jitter_range: Range for jitter multiplier (min, max)
        exponential_factor: Factor for exponential backoff
        max_delay: Maximum allowed delay (optional)

    Returns:
        Calculated delay in seconds

    Examples:
        # Network retry with jitter
        delay = calculate_retry_delay(2, 2.0, use_jitter=True)

        # Content retry without jitter
        delay = calculate_retry_delay(1, 3.0, use_jitter=False)
    """
    if attempt < 0:
        raise ValueError("Attempt must be non-negative")

    if base_delay <= 0:
        raise ValueError("Base delay must be positive")

    if jitter_range[0] >= jitter_range[1]:
        raise ValueError("Jitter range min must be less than max")

    # Calculate exponential backoff
    delay = base_delay * (exponential_factor ** attempt)

    # Apply jitter if requested
    if use_jitter:
        jitter_multiplier = random.uniform(*jitter_range)
        delay *= jitter_multiplier

    # Apply maximum delay limit if specified
    if max_delay is not None and delay > max_delay:
        delay = max_delay
        logger.debug(f"Delay capped at maximum: {max_delay}s")

    logger.debug(
        f"Calculated retry delay: attempt={attempt}, "
        f"base_delay={base_delay}s, jitter={use_jitter}, "
        f"result={delay:.2f}s"
    )

    return delay


def get_dns_retry_delay(attempt: int, config_manager=None) -> float:
    """
    Get DNS-specific retry delay from configuration.

    DNS errors need longer delays due to propagation time.
    This combines config-driven parameters with DNS-specific logic.

    Args:
        attempt: Current attempt number (0-based)
        config_manager: ConfigManager instance (optional)

    Returns:
        Delay in seconds for DNS retry
    """
    if config_manager is None:
        from speakub.utils.config import ConfigManager
        config_manager = ConfigManager()

    network_config = config_manager.get("retry_policies.network", {})
    dns_delay = network_config.get("dns_delay", 5.0)

    # DNS errors use longer base delay
    return calculate_retry_delay(
        attempt=attempt,
        base_delay=dns_delay,
        use_jitter=network_config.get("use_jitter", True),
        jitter_range=network_config.get("jitter_range", [0.5, 1.5]),
        exponential_factor=network_config.get("exponential_factor", 2.0)
    )


def get_network_retry_delay(attempt: int, config_manager=None) -> float:
    """
    Get general network retry delay from configuration.

    For standard network errors that don't require DNS-level delays.

    Args:
        attempt: Current attempt number (0-based)
        config_manager: ConfigManager instance (optional)

    Returns:
        Delay in seconds for network retry
    """
    if config_manager is None:
        from speakub.utils.config import ConfigManager
        config_manager = ConfigManager()

    network_config = config_manager.get("retry_policies.network", {})
    base_delay = network_config.get("base_delay", 2.0)

    return calculate_retry_delay(
        attempt=attempt,
        base_delay=base_delay,
        use_jitter=network_config.get("use_jitter", True),
        jitter_range=network_config.get("jitter_range", [0.5, 1.5]),
        exponential_factor=network_config.get("exponential_factor", 2.0)
    )


def get_content_retry_delay(attempt: int, config_manager=None) -> float:
    """
    Get content-specific retry delay from configuration.

    For content processing retries that don't use jitter.

    Args:
        attempt: Current attempt number (0-based)
        config_manager: ConfigManager instance (optional)

    Returns:
        Delay in seconds for content retry
    """
    if config_manager is None:
        from speakub.utils.config import ConfigManager
        config_manager = ConfigManager()

    content_config = config_manager.get("retry_policies.content", {})
    delay = content_config.get("delay", 3.0)

    # Content retries don't use jitter by default
    return calculate_retry_delay(
        attempt=attempt,
        base_delay=delay,
        use_jitter=content_config.get("use_jitter", False),
        exponential_factor=1.0  # No exponential backoff for content
    )


def should_retry_network_error(attempt: int, config_manager=None) -> bool:
    """
    Determine if network error should be retried based on configuration.

    Args:
        attempt: Current attempt number (0-based)
        config_manager: ConfigManager instance (optional)

    Returns:
        True if should retry, False otherwise
    """
    if config_manager is None:
        from speakub.utils.config import ConfigManager
        config_manager = ConfigManager()

    max_attempts = config_manager.get("retry_policies.network.max_attempts", 3)
    return attempt < max_attempts


def should_retry_content_error(attempt: int, reason: str = "normal", config_manager=None) -> bool:
    """
    Determine if content error should be retried based on configuration.

    Args:
        attempt: Current attempt number (0-based)
        reason: Content analysis reason ("normal" or "very_short_fragment")
        config_manager: ConfigManager instance (optional)

    Returns:
        True if should retry, False otherwise
    """
    if config_manager is None:
        from speakub.utils.config import ConfigManager
        config_manager = ConfigManager()

    content_config = config_manager.get("retry_policies.content", {})

    if reason == "very_short_fragment":
        max_attempts = content_config.get("short_text_attempts", 4)
    else:
        max_attempts = content_config.get("normal_attempts", 2)

    return attempt < max_attempts
