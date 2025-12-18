#!/usr/bin/env python3
"""TTS Error Recovery Manager - Manages error handling and circuit breaker logic."""

import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


class TTSErrorRecoveryManager:
    """Manages TTS engine error recovery and circuit breaker pattern."""

    def __init__(
        self,
        max_consecutive_errors: int = 3,
        error_reset_timeout: float = 60.0,
        circuit_open_duration: float = 300.0,
    ):
        """
        Initialize error recovery manager.

        Args:
            max_consecutive_errors: Maximum consecutive errors before circuit opens
            error_reset_timeout: Time (seconds) to reset error count after success
            circuit_open_duration: How long circuit stays open (seconds)
        """
        self._error_count = 0
        self._consecutive_failures = 0
        self._last_error_time = 0.0
        self._circuit_breaker_until = 0.0
        self._recovery_attempts = 0

        self._max_consecutive_errors = max_consecutive_errors
        self._error_reset_timeout = error_reset_timeout
        self._circuit_open_duration = circuit_open_duration

    def record_error(self, timestamp: Optional[float] = None) -> None:
        """
        Record an error occurrence.

        Args:
            timestamp: Error timestamp (defaults to current time)
        """
        if timestamp is None:
            timestamp = time.time()

        self._error_count += 1
        self._consecutive_failures += 1
        self._last_error_time = timestamp
        self._recovery_attempts = 0

        logger.warning(
            f"TTS error recorded: {self._consecutive_failures} consecutive failures, "
            f"total {self._error_count}"
        )

        # Open circuit if too many consecutive errors
        if self._consecutive_failures >= self._max_consecutive_errors:
            self._open_circuit()

    def reset_on_success(self) -> None:
        """Reset error tracking on successful operation."""
        self._consecutive_failures = 0
        self._recovery_attempts = 0
        logger.debug("TTS recovery successful - error counters reset")

    def is_circuit_open(self) -> bool:
        """
        Check if circuit breaker is open.

        Returns:
            bool: True if circuit is open
        """
        if self._circuit_breaker_until == 0.0:
            return False

        current_time = time.time()
        if current_time >= self._circuit_breaker_until:
            # Circuit has cooled down
            self._circuit_breaker_until = 0.0
            self._consecutive_failures = 0
            logger.info("Circuit breaker reset - ready for retry")
            return False

        return True

    def get_retry_delay(self) -> float:
        """
        Get recommended retry delay (exponential backoff).

        Returns:
            float: Delay in seconds
        """
        if self.is_circuit_open():
            remaining = self._circuit_breaker_until - time.time()
            return max(remaining, 0.0)

        # Exponential backoff: 1s, 2s, 4s, 8s, etc. (capped at 30s)
        delay = min(2 ** self._recovery_attempts, 30.0)
        return delay

    def increment_recovery_attempts(self) -> None:
        """Increment recovery attempt counter."""
        self._recovery_attempts += 1

    def get_error_count(self) -> int:
        """Get total error count."""
        return self._error_count

    def get_consecutive_failures(self) -> int:
        """Get consecutive failure count."""
        return self._consecutive_failures

    def get_last_error_time(self) -> float:
        """Get timestamp of last error."""
        return self._last_error_time

    def _open_circuit(self) -> None:
        """Open the circuit breaker."""
        self._circuit_breaker_until = time.time() + self._circuit_open_duration
        logger.error(
            f"Circuit breaker opened - will retry after "
            f"{self._circuit_open_duration}s"
        )

    def reset(self) -> None:
        """Reset all error tracking."""
        self._error_count = 0
        self._consecutive_failures = 0
        self._last_error_time = 0.0
        self._circuit_breaker_until = 0.0
        self._recovery_attempts = 0
        logger.debug("Error recovery manager reset")

    def get_status(self) -> dict:
        """
        Get current status.

        Returns:
            dict: Status information
        """
        return {
            "error_count": self._error_count,
            "consecutive_failures": self._consecutive_failures,
            "last_error_time": self._last_error_time,
            "circuit_open": self.is_circuit_open(),
            "circuit_breaker_until": self._circuit_breaker_until,
            "recovery_attempts": self._recovery_attempts,
            "retry_delay": self.get_retry_delay(),
        }
