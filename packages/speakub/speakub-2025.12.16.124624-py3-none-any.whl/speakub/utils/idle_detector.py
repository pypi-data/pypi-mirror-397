#!/usr/bin/env python3
"""
Idle Detector - User activity monitoring and idle mode management
Provides centralized idle detection logic for performance optimization
"""

import logging
import threading
import time
from typing import Callable, List, Optional

logger = logging.getLogger(__name__)


class IdleDetector:
    """
    Centralized idle detector for user activity monitoring.

    This class provides:
    - User activity tracking
    - Idle mode detection based on configurable thresholds
    - Callback system for idle mode changes
    - Thread-safe operations
    """

    def __init__(self, threshold_seconds: int = 30):
        """
        Initialize idle detector.

        Args:
            threshold_seconds: Time in seconds after which user is considered idle
        """
        self.threshold_seconds = threshold_seconds
        self._lock = threading.RLock()
        self._last_activity = time.time()
        self._idle_mode = False
        self._idle_callbacks: List[Callable[[bool], None]] = []
        self._activity_callbacks: List[Callable[[], None]] = []

    @property
    def idle_mode(self) -> bool:
        """Get current idle mode status."""
        with self._lock:
            return self._idle_mode

    @property
    def last_activity(self) -> float:
        """Get timestamp of last user activity."""
        with self._lock:
            return self._last_activity

    @property
    def idle_time(self) -> float:
        """Get current idle time in seconds."""
        with self._lock:
            return time.time() - self._last_activity

    def update_activity(self) -> None:
        """Update last user activity timestamp and exit idle mode if active."""
        with self._lock:
            old_idle = self._idle_mode
            self._last_activity = time.time()

            # Exit idle mode if we were idle
            if old_idle:
                self._idle_mode = False
                logger.debug("User activity detected, exiting idle mode")
                self._notify_idle_change(False)

            # Notify activity callbacks
            self._notify_activity()

    def check_idle_status(self) -> bool:
        """
        Check current idle status and update if necessary.

        Returns:
            True if user is idle, False otherwise
        """
        with self._lock:
            current_time = time.time()
            idle_time = current_time - self._last_activity
            should_be_idle = idle_time >= self.threshold_seconds

            # State transition
            if should_be_idle and not self._idle_mode:
                self._idle_mode = True
                logger.debug(
                    f"Entering idle mode after {idle_time:.1f}s of inactivity"
                )
                self._notify_idle_change(True)
            elif not should_be_idle and self._idle_mode:
                self._idle_mode = False
                logger.debug("Exiting idle mode after user activity")
                self._notify_idle_change(False)

            return self._idle_mode

    def force_idle_mode(self, idle: bool) -> None:
        """
        Force idle mode state (for testing or manual control).

        Args:
            idle: True to enter idle mode, False to exit
        """
        with self._lock:
            if self._idle_mode != idle:
                self._idle_mode = idle
                self._notify_idle_change(idle)

    def add_idle_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Add callback for idle mode changes.

        Args:
            callback: Function called with (idle_active: bool) when idle mode changes
        """
        with self._lock:
            if callback not in self._idle_callbacks:
                self._idle_callbacks.append(callback)

    def remove_idle_callback(self, callback: Callable[[bool], None]) -> None:
        """
        Remove idle mode change callback.

        Args:
            callback: Callback function to remove
        """
        with self._lock:
            if callback in self._idle_callbacks:
                self._idle_callbacks.remove(callback)

    def add_activity_callback(self, callback: Callable[[], None]) -> None:
        """
        Add callback for user activity updates.

        Args:
            callback: Function called when user activity is detected
        """
        with self._lock:
            if callback not in self._activity_callbacks:
                self._activity_callbacks.append(callback)

    def remove_activity_callback(self, callback: Callable[[], None]) -> None:
        """
        Remove activity callback.

        Args:
            callback: Callback function to remove
        """
        with self._lock:
            if callback in self._activity_callbacks:
                self._activity_callbacks.remove(callback)

    def _notify_idle_change(self, idle_active: bool) -> None:
        """Notify all idle callbacks about mode change."""
        callbacks = self._idle_callbacks.copy()
        for callback in callbacks:
            try:
                callback(idle_active)
            except Exception as e:
                logger.error(f"Idle callback failed: {e}")

    def _notify_activity(self) -> None:
        """Notify all activity callbacks."""
        callbacks = self._activity_callbacks.copy()
        for callback in callbacks:
            try:
                callback()
            except Exception as e:
                logger.error(f"Activity callback failed: {e}")

    def get_status_info(self) -> dict:
        """
        Get current status information.

        Returns:
            Dictionary with idle status details
        """
        with self._lock:
            return {
                "idle_mode": self._idle_mode,
                "idle_time_seconds": self.idle_time,
                "threshold_seconds": self.threshold_seconds,
                "last_activity_timestamp": self._last_activity,
                "idle_percentage": min(
                    100.0, (self.idle_time / self.threshold_seconds) * 100
                )
            }


# Global idle detector instance
_idle_detector_instance: Optional[IdleDetector] = None
_idle_detector_lock = threading.Lock()


def get_idle_detector(threshold_seconds: int = 30) -> IdleDetector:
    """
    Get global idle detector instance (singleton).

    Args:
        threshold_seconds: Idle threshold for new instance (only used if creating new)

    Returns:
        Global IdleDetector instance
    """
    global _idle_detector_instance

    if _idle_detector_instance is None:
        with _idle_detector_lock:
            if _idle_detector_instance is None:
                _idle_detector_instance = IdleDetector(threshold_seconds)

    return _idle_detector_instance


def update_global_activity() -> None:
    """Update activity on global idle detector instance."""
    detector = get_idle_detector()
    detector.update_activity()


def is_system_idle() -> bool:
    """Check if system is currently idle."""
    detector = get_idle_detector()
    return detector.idle_mode
