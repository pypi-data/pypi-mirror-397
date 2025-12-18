#!/usr/bin/env python3
"""
Error Handler - Standardized error handling utilities for SpeakUB
"""

import logging
from enum import Enum
from typing import Any, Callable, Optional, TypeVar, Union

# Type alias for numeric validation parameters
NumericOrNone = Union[int, float, None]

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ErrorSeverity(Enum):
    """Error severity levels for consistent handling."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for better classification."""

    NETWORK = "network"
    TTS_SYNTHESIS = "tts_synthesis"
    TTS_PLAYBACK = "tts_playback"
    FILE_SYSTEM = "file_system"
    CONFIGURATION = "configuration"
    UI = "ui"
    VALIDATION = "validation"
    SECURITY = "security"
    UNKNOWN = "unknown"


class ErrorHandler:
    """Standardized error handling for SpeakUB components."""

    @staticmethod
    def handle_and_suppress(
        error: Exception, context: str, extra: Optional[dict] = None
    ) -> None:
        """
        Handle error by logging warning and suppressing it (continuing execution).

        Args:
            error: The exception that occurred
            context: Contextual information about where the error happened
            extra: Additional logging context
        """
        log_data = {
            "component": "error_handler",
            "action": "suppressed",
            "context": context,
        }
        if extra:
            log_data.update(extra)

        logger.warning(f"{context}: {error}", exc_info=True, extra=log_data)

    @staticmethod
    def handle_and_raise(error: Exception, context: str, extra: Optional[dict] = None):
        """
        Handle error by logging and re-raising it.

        Args:
            error: The exception to log and re-raise
            context: Contextual information about where the error happened
            extra: Additional logging context

        Raises:
            The original exception after logging
        """
        log_data = {
            "component": "error_handler",
            "action": "re_raised",
            "context": context,
        }
        if extra:
            log_data.update(extra)

        logger.error(f"{context}: {error}", exc_info=True, extra=log_data)
        raise error

    @staticmethod
    def handle_with_fallback(
        error: Exception, context: str, fallback: Any, extra: Optional[dict] = None
    ) -> Any:
        """
        Handle error by logging warning and returning a fallback value.

        Args:
            error: The exception that occurred
            context: Contextual information about where the error happened
            fallback: Fallback value to return
            extra: Additional logging context

        Returns:
            The fallback value
        """
        log_data = {
            "component": "error_handler",
            "action": "fallback",
            "context": context,
        }
        if extra:
            log_data.update(extra)

        logger.warning(
            f"{context}: {error}, using fallback", exc_info=True, extra=log_data
        )
        return fallback


def safe_execute(
    func: Callable[..., T], *args, context: str = "", **kwargs
) -> Optional[T]:
    """
    Execute a function with standardized error handling.

    Args:
        func: Function to execute
        context: Context for error logging
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function

    Returns:
        Function result or None if error occurred
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        ErrorHandler.handle_and_suppress(
            e, f"Error in {func.__name__}", {"context": context}
        )
        return None


def safe_execute_with_fallback(
    func: Callable[..., T], fallback: T, *args, context: str = "", **kwargs
) -> T:
    """
    Execute a function with fallback value on error.

    Args:
        func: Function to execute
        fallback: Value to return on error
        context: Context for error logging
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function

    Returns:
        Function result or fallback value
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        ErrorHandler.handle_with_fallback(
            e, f"Error in {func.__name__}", fallback, {"context": context}
        )
        return fallback


def safe_operation(operation_name: str):
    """
    Decorator for safe operations with standardized error handling.

    Args:
        operation_name: Name of the operation for logging
    """

    def decorator(func: Callable[..., T]) -> Callable[..., Optional[T]]:
        def wrapper(*args, **kwargs) -> Optional[T]:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                ErrorHandler.handle_and_suppress(
                    e,
                    f"Operation '{operation_name}' failed in {func.__name__}",
                    {"operation": operation_name},
                )
                return None

        return wrapper

    return decorator


def validate_config_value(
    value: Any,
    expected_type: type,
    field_name: str,
    default: Any = None,
    min_val: NumericOrNone = None,
    max_val: NumericOrNone = None,
) -> Any:
    """
    Validate and sanitize configuration values with range checking.

    Args:
        value: Value to validate
        expected_type: Expected type
        field_name: Field name for logging
        default: Default value if validation fails
        min_val: Minimum allowed value for numeric types
        max_val: Maximum allowed value for numeric types

    Returns:
        Validated value or default
    """
    try:
        if not isinstance(value, expected_type):
            logger.warning(
                f"Invalid type for {field_name}: expected {expected_type.__name__}, got {type(value).__name__}",
                extra={
                    "component": "config",
                    "action": "type_validation",
                    "field": field_name,
                },
            )
            return default

        # Range validation for numeric types
        if isinstance(value, (int, float)) and (
            min_val is not None or max_val is not None
        ):
            if min_val is not None and value < min_val:
                logger.warning(
                    f"Value for {field_name} below minimum: {value} < {min_val}, using {min_val}",
                    extra={
                        "component": "config",
                        "action": "range_validation",
                        "field": field_name,
                    },
                )
                return min_val
            if max_val is not None and value > max_val:
                logger.warning(
                    f"Value for {field_name} above maximum: {value} > {max_val}, using {max_val}",
                    extra={
                        "component": "config",
                        "action": "range_validation",
                        "field": field_name,
                    },
                )
                return max_val

        return value
    except Exception as e:
        ErrorHandler.handle_with_fallback(
            e,
            f"Failed to validate {field_name}",
            default,
            {"component": "config", "action": "validation_error", "field": field_name},
        )
        return default


class UnifiedErrorHandler:
    """
    Unified error handling system for SpeakUB.
    Provides consistent error classification, logging, and recovery strategies.
    """

    @staticmethod
    def categorize_error(error: Exception, context: str = "") -> ErrorCategory:
        """
        Categorize an error based on its type and context.

        Args:
            error: The exception to categorize
            context: Additional context information

        Returns:
            ErrorCategory enum value
        """
        error_msg = str(error).lower()
        error_type = type(error).__name__.lower()

        # Network-related errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in [
                "network",
                "connection",
                "timeout",
                "unreachable",
                "dns",
                "http",
                "ssl",
            ]
        ):
            return ErrorCategory.NETWORK

        # TTS synthesis errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in [
                "synthesis",
                "tts",
                "audio",
                "voice",
                "edge-tts",
                "gtts",
                "nanmai",
            ]
        ):
            return ErrorCategory.TTS_SYNTHESIS

        # TTS playback errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in ["playback", "player", "mpv", "pygame", "audio"]
        ):
            return ErrorCategory.TTS_PLAYBACK

        # File system errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in ["file", "directory", "path", "permission", "disk", "io"]
        ):
            return ErrorCategory.FILE_SYSTEM

        # Configuration errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in ["config", "setting", "parameter", "validation"]
        ):
            return ErrorCategory.CONFIGURATION

        # UI errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in ["ui", "widget", "panel", "display", "textual"]
        ):
            return ErrorCategory.UI

        # Validation errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in ["validate", "invalid", "format", "type"]
        ):
            return ErrorCategory.VALIDATION

        # Security errors
        if any(
            keyword in error_msg or keyword in error_type
            for keyword in ["security", "permission", "access", "auth"]
        ):
            return ErrorCategory.SECURITY

        return ErrorCategory.UNKNOWN

    @staticmethod
    def get_error_severity(error: Exception, category: ErrorCategory) -> ErrorSeverity:
        """
        Determine the severity of an error based on its category and content.

        Args:
            error: The exception
            category: Error category

        Returns:
            ErrorSeverity enum value
        """
        # Critical errors that should stop execution
        if category in [ErrorCategory.SECURITY, ErrorCategory.FILE_SYSTEM]:
            if "permission" in str(error).lower() or "access" in str(error).lower():
                return ErrorSeverity.CRITICAL

        # High-priority errors
        if category == ErrorCategory.NETWORK:
            return ErrorSeverity.ERROR

        # Medium-priority errors
        if category in [ErrorCategory.TTS_SYNTHESIS, ErrorCategory.TTS_PLAYBACK]:
            return ErrorSeverity.WARNING

        # Low-priority errors
        if category in [
            ErrorCategory.CONFIGURATION,
            ErrorCategory.UI,
            ErrorCategory.VALIDATION,
        ]:
            return ErrorSeverity.INFO

        # Default to warning for unknown errors
        return ErrorSeverity.WARNING

    @staticmethod
    def handle_error(
        error: Exception,
        context: str = "",
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        should_raise: bool = False,
        fallback_value: Any = None,
    ) -> Any:
        """
        Unified error handling method.

        Args:
            error: The exception that occurred
            context: Contextual information
            category: Error category (auto-detected if None)
            severity: Error severity (auto-detected if None)
            should_raise: Whether to re-raise the error
            fallback_value: Fallback value to return (if not raising)

        Returns:
            Fallback value if provided and not raising, None otherwise

        Raises:
            The original exception if should_raise is True
        """
        # Auto-categorize if not provided
        if category is None:
            category = UnifiedErrorHandler.categorize_error(error, context)

        # Auto-determine severity if not provided
        if severity is None:
            severity = UnifiedErrorHandler.get_error_severity(error, category)

        # Prepare logging context
        log_context = {
            "component": "unified_error_handler",
            "category": category.value,
            "severity": severity.value,
            "context": context,
            "error_type": type(error).__name__,
        }

        # Log based on severity
        log_message = f"[{category.value.upper()}] {context}: {error}"

        if severity == ErrorSeverity.DEBUG:
            logger.debug(log_message, extra=log_context)
        elif severity == ErrorSeverity.INFO:
            logger.info(log_message, extra=log_context)
        elif severity == ErrorSeverity.WARNING:
            logger.warning(log_message, exc_info=True, extra=log_context)
        elif severity == ErrorSeverity.ERROR:
            logger.error(log_message, exc_info=True, extra=log_context)
        elif severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, exc_info=True, extra=log_context)

        # Handle based on parameters
        if should_raise:
            raise error
        elif fallback_value is not None:
            return fallback_value
        else:
            return None

    @staticmethod
    def safe_operation(
        operation_name: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.WARNING,
        fallback_value: Any = None,
    ):
        """
        Decorator for operations with unified error handling.

        Args:
            operation_name: Name of the operation
            category: Error category for this operation
            severity: Error severity level
            fallback_value: Value to return on error
        """

        def decorator(func: Callable[..., T]) -> Callable[..., Any]:
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    context = f"Operation '{operation_name}' in {func.__name__}"
                    return UnifiedErrorHandler.handle_error(
                        e,
                        context,
                        category,
                        severity,
                        should_raise=False,
                        fallback_value=fallback_value,
                    )

            return wrapper

        return decorator


# Global instance for easy access
unified_error_handler = UnifiedErrorHandler()
