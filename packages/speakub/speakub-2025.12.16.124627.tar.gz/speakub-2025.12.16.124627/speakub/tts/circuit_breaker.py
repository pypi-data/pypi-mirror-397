#!/usr/bin/env python3
"""
Circuit Breaker Pattern Implementation for TTS Operations

This module provides resilient failure handling for TTS operations
by implementing the circuit breaker pattern. It prevents cascading
failures by temporarily stopping calls to failing services.
"""

import asyncio
import logging
import threading
import time
from enum import Enum
from typing import Any, Callable, Optional, Tuple, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitBreakerState(Enum):
    """Circuit breaker states for service health management."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerOpenException(Exception):
    """Exception raised when circuit breaker is open and rejects calls."""

    pass


class CircuitBreaker:
    """
    Circuit breaker pattern implementation for TTS operations.

    Prevents cascading failures by temporarily stopping calls to failing services.
    Uses three states:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Service failing, requests rejected immediately
    - HALF_OPEN: Testing recovery, limited requests allowed

    Example:
        ```python
        breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60.0)
        try:
            result = breaker.call(some_tts_function, arg1, arg2)
        except CircuitBreakerOpenException:
            # Handle circuit open - service unavailable
            use_fallback()
        ```
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: Tuple[type, ...] = (Exception,),
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit (default: 5)
            recovery_timeout: Seconds to wait before attempting recovery (default: 60.0)
            expected_exception: Tuple of exception types to catch (default: (Exception,))
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.success_count = 0
        self.next_attempt_time: Optional[float] = None

        self._lock = threading.Lock()

    def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """
        Execute function with circuit breaker protection (synchronous).

        Args:
            func: Function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: If circuit is open
            Original exception: If function fails
        """
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() < self.next_attempt_time:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker is OPEN. Next retry at {self.next_attempt_time}"
                    )
                else:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(
                        "Circuit breaker entering HALF_OPEN state for testing")

            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

    async def call_async(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute async function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for function
            **kwargs: Keyword arguments for function

        Returns:
            Function result

        Raises:
            CircuitBreakerOpenException: If circuit is open
            Original exception: If function fails
        """
        with self._lock:
            if self.state == CircuitBreakerState.OPEN:
                if time.time() < self.next_attempt_time:
                    raise CircuitBreakerOpenException(
                        f"Circuit breaker is OPEN. Next retry at {self.next_attempt_time}"
                    )
                else:
                    self.state = CircuitBreakerState.HALF_OPEN
                    logger.info(
                        "Circuit breaker entering HALF_OPEN state for testing")

            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure()
                raise e

    def _on_success(self) -> None:
        """Handle successful call."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 3:  # Require 3 consecutive successes
                self._reset()
                logger.info(
                    "Circuit breaker CLOSED after successful recovery test")
        # Reset failure count on success in CLOSED state
        self.failure_count = 0

    def _on_failure(self) -> None:
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            # Failed during recovery test, go back to OPEN
            self._trip()
            logger.warning(
                "Circuit breaker test failed, returning to OPEN state")
        elif self.failure_count >= self.failure_threshold:
            # Too many failures, trip the circuit
            self._trip()
            logger.warning(
                f"Circuit breaker tripped after {self.failure_count} failures"
            )

    def _trip(self) -> None:
        """Trip the circuit breaker to OPEN state."""
        self.state = CircuitBreakerState.OPEN
        self.next_attempt_time = time.time() + self.recovery_timeout
        self.success_count = 0

    def _reset(self) -> None:
        """Reset circuit breaker to CLOSED state."""
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.next_attempt_time = None

    def get_state(self) -> dict:
        """
        Get current circuit breaker state information.

        Returns:
            Dictionary with state, failure_count, last_failure_time, 
            next_attempt_time, and success_count
        """
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "next_attempt_time": self.next_attempt_time,
            "success_count": self.success_count,
        }
