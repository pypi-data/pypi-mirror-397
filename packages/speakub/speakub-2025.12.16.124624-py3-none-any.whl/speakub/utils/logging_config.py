"""
Centralized logging configuration for SpeakUB.
"""

import logging
import logging.handlers
import os
import sys
from typing import Dict, Optional

from speakub.utils.config import CONFIG_DIR

# Hierarchical logging level mappings for component-specific filtering
COMPONENT_LEVELS: Dict[str, str] = {
    # UI components - can be muted in non-debug mode
    "speakub.ui": "WARNING",  # UI interactions, widget updates
    "speakub.ui.widgets": "WARNING",  # Widget-specific interactions
    "speakub.ui.screens": "WARNING",  # Screen transitions and updates
    # Core business logic - always detailed
    "speakub.core": "DEBUG",  # EPUB parsing, content rendering
    "epubkit": "INFO",  # External EPUB library logging
    "speakub.tts": "DEBUG",  # TTS synthesis, playback, engine mgmt
    "speakub.tts.backends": "INFO",  # Audio backend operations
    "speakub.tts.reservoir": "INFO",  # Predictive batch operations
    "speakub.utils": "INFO",  # Utility functions, config management
    # Event bus operations (usually noisy)
    "speakub.utils.event_bus": "WARNING",
    # Default fallback
    "speakub": "INFO",
}

# Runtime adjustable logging levels for fine-grained control
RUNTIME_LOG_LEVELS: Dict[str, str] = {
    # Performance monitoring
    "performance": "WARNING",  # Memory, CPU, and performance logs
    "network": "INFO",  # Network operations and retries
    "synthesis": "INFO",  # TTS synthesis operations
    "playback": "INFO",  # Audio playback operations
    # Error categories
    "errors": "ERROR",  # All error-level logs
    "warnings": "WARNING",  # Warning-level logs
    "debug": "DEBUG",  # Debug-level logs
}


def apply_component_levels(debug_mode: bool = False) -> None:
    """
    Apply component-specific logging levels using inheritance mechanism.

    Args:
        debug_mode: Whether debug mode is enabled
    """
    for component, default_level in COMPONENT_LEVELS.items():
        component_logger = logging.getLogger(component)

        if (
            debug_mode
            or component.startswith("speakub.core")
            or component.startswith("speakub.tts")
        ):
            # In debug mode or for core/TTS: allow DEBUG and above
            component_logger.setLevel(logging.DEBUG)
        else:
            # For UI and other components: use component-specific level
            # UI components get WARNING+ to mute DEBUG noise
            level_value = getattr(logging, default_level.upper(), logging.INFO)
            component_logger.setLevel(level_value)


def get_environment_log_profile() -> Dict[str, str]:
    """
    Get logging profile based on detected environment.
    Returns appropriate log levels for production/development environments.

    Returns:
        Dict mapping categories to log levels
    """
    import os

    # Check for environment indicators
    is_production = (
        os.getenv("ENV") == "production" or
        os.getenv("PRODUCTION") == "true" or
        not os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
    )

    if is_production:
        return {
            "performance": "WARNING",  # Minimal performance logs in production
            "network": "WARNING",      # Only warnings/errors for network
            "synthesis": "INFO",       # Basic synthesis info
            "playback": "INFO",        # Basic playback info
            "errors": "ERROR",         # Only errors
            "warnings": "WARNING",     # Warnings and above
            "debug": "WARNING",        # No debug logs in production
        }
    else:
        return {
            "performance": "DEBUG",    # Detailed performance logs in development
            "network": "INFO",         # Network operations visible
            "synthesis": "DEBUG",      # Detailed synthesis logs
            "playback": "DEBUG",       # Detailed playback logs
            "errors": "ERROR",         # Errors always shown
            "warnings": "WARNING",     # Warnings and above
            "debug": "DEBUG",          # Debug logs enabled
        }


def apply_environment_log_levels() -> None:
    """
    Automatically apply appropriate log levels based on environment detection.
    This implements the "grand unified plan" Level 1 foundation.
    """
    profile = get_environment_log_profile()

    for category, level in profile.items():
        set_runtime_log_level(category, level)

    logger = logging.getLogger("speakub.utils.logging_config")
    env_type = "production" if profile["debug"] == "WARNING" else "development"
    logger.info(f"Applied {env_type} logging profile: {profile}")


def setup_logging(
    level: str = "INFO",
    debug_mode: bool = False,
    log_to_file: bool = True,
    log_to_console: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    log_format: Optional[str] = None,
    auto_apply_environment_profile: bool = True,
) -> None:
    """
    Set up centralized logging configuration with hierarchical component levels.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        debug_mode: Whether debug mode is enabled (affects component filtering)
        log_to_file: Whether to log to file
        log_to_console: Whether to log to console
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
        log_format: Custom log format string
    """
    # Create logger
    logger = logging.getLogger("speakub")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Clear existing handlers
    logger.handlers.clear()

    # Default format
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        log_dir = os.path.join(CONFIG_DIR, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "speakub.log")

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Apply component-specific levels using inheritance mechanism
    apply_component_levels(debug_mode)

    # Set the root logger level to prevent duplicate messages
    root_logger = logging.getLogger()
    # Only show warnings and above from other libraries
    root_logger.setLevel(logging.WARNING)


def set_debug_mode(enabled: bool) -> None:
    """
    Dynamically toggle debug mode, affecting component-level filtering.
    Uses inheritance mechanism to propagate changes to all child loggers.

    Args:
        enabled: Whether to enable debug mode
    """
    # Apply component levels with new debug mode
    apply_component_levels(debug_mode=enabled)

    # Force logging system to re-evaluate all speakub loggers
    # This ensures inheritance-based level filtering is applied immediately
    for logger_name in list(logging.root.manager.loggerDict.keys()):
        if logger_name.startswith("speakub"):
            logger = logging.getLogger(logger_name)
            # Trigger re-evaluation by temporarily changing and restoring level
            current_level = logger.level
            logger.setLevel(current_level)


def set_runtime_log_level(category: str, level: str) -> bool:
    """
    Dynamically adjust logging level for a specific category at runtime.

    Args:
        category: Log category from RUNTIME_LOG_LEVELS
        level: New logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        True if successful, False if category not found
    """
    if category not in RUNTIME_LOG_LEVELS:
        return False

    try:
        level_value = getattr(logging, level.upper(), logging.INFO)
        RUNTIME_LOG_LEVELS[category] = level.upper()

        # Apply to relevant loggers based on category
        if category == "performance":
            # Performance-related loggers
            for logger_name in [
                "speakub.utils.resource_monitor",
                "speakub.utils.performance_monitor",
            ]:
                logging.getLogger(logger_name).setLevel(level_value)

        elif category == "network":
            # Network-related loggers
            for logger_name in [
                "speakub.tts.nanmai_tts_provider",
                "speakub.tts.edge_tts_provider",
                "speakub.utils.network",
            ]:
                logging.getLogger(logger_name).setLevel(level_value)

        elif category == "synthesis":
            # TTS synthesis loggers
            for logger_name in ["speakub.tts.engine", "speakub.tts.integration"]:
                logging.getLogger(logger_name).setLevel(level_value)

        elif category == "playback":
            # Audio playback loggers
            for logger_name in ["speakub.tts.backends", "speakub.tts.playback_manager"]:
                logging.getLogger(logger_name).setLevel(level_value)

        elif category in ["errors", "warnings", "debug"]:
            # Apply to all speakub loggers
            root_logger = logging.getLogger("speakub")
            root_logger.setLevel(level_value)

            # Re-apply component levels to maintain hierarchy
            apply_component_levels()

        return True
    except Exception:
        return False


def get_runtime_log_levels() -> Dict[str, str]:
    """
    Get current runtime logging levels.

    Returns:
        Dictionary of current runtime log levels
    """
    return RUNTIME_LOG_LEVELS.copy()


def reset_runtime_log_levels() -> None:
    """
    Reset runtime logging levels to defaults and reapply configuration.
    """
    global RUNTIME_LOG_LEVELS
    RUNTIME_LOG_LEVELS = {
        "performance": "WARNING",
        "network": "INFO",
        "synthesis": "INFO",
        "playback": "INFO",
        "errors": "ERROR",
        "warnings": "WARNING",
        "debug": "DEBUG",
    }

    # Reapply current debug mode setting
    apply_component_levels()


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name under the speakub hierarchy.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"speakub.{name}")


# NOTE: Removed automatic setup_logging() call to prevent duplicate handlers
# Logging setup is now controlled by cli.py to avoid conflicts
