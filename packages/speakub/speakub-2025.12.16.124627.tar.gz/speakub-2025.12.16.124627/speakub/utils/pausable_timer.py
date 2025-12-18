"""
Pausable Timer utility for event-driven scheduling.
Allows timers to be paused and resumed, useful for TTS playback control.
"""

import asyncio
import logging
import time
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class PausableTimer:
    """
    A timer that can be paused and resumed, useful for scheduling events
    that should be suspended during playback pauses.
    """

    def __init__(
        self,
        callback: Callable,
        interval: float,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        """
        Initialize the pausable timer.

        Args:
            callback: Function to call when timer expires
            interval: Time interval in seconds
            loop: Event loop to use (defaults to current loop)
        """
        self.callback = callback
        self.interval = interval
        self.loop = loop or asyncio.get_event_loop()
        self._handle: Optional[asyncio.Handle] = None
        self._start_time: float = 0.0
        self._remaining_time: float = 0.0
        self._is_paused: bool = False
        self._is_cancelled: bool = False

    def start(self) -> None:
        """Start the timer."""
        if self._is_cancelled:
            return

        self._start_time = time.time()
        self._remaining_time = self.interval
        self._is_paused = False
        self._schedule_callback()

    def pause(self) -> None:
        """Pause the timer, preserving remaining time."""
        if self._is_paused or self._is_cancelled:
            return

        if self._handle and not self._handle.cancelled():
            self._handle.cancel()

        elapsed = time.time() - self._start_time
        self._remaining_time = max(0.0, self.interval - elapsed)
        self._is_paused = True

        logger.debug(f"Timer paused with {self._remaining_time:.2f}s remaining")

    def resume(self) -> None:
        """Resume the timer from where it was paused."""
        if not self._is_paused or self._is_cancelled:
            return

        self._start_time = time.time()
        self._is_paused = False
        self._schedule_callback()

        logger.debug(f"Timer resumed with {self._remaining_time:.2f}s remaining")

    def cancel(self) -> None:
        """Cancel the timer permanently."""
        self._is_cancelled = True
        self._is_paused = False

        if self._handle and not self._handle.cancelled():
            self._handle.cancel()
            self._handle = None

        # Reduced log noise - Timer cancellation is normal operation
        # logger.debug("Timer cancelled")

    def reset(self, new_interval: Optional[float] = None) -> None:
        """Reset the timer with optional new interval."""
        if self._handle and not self._handle.cancelled():
            self._handle.cancel()

        if new_interval is not None:
            self.interval = new_interval

        self._remaining_time = self.interval
        self._is_paused = False
        self._is_cancelled = False

        if not self._is_cancelled:
            self.start()

    def is_active(self) -> bool:
        """Check if timer is currently active (not paused or cancelled)."""
        return (
            not self._is_paused and not self._is_cancelled and self._handle is not None
        )

    def is_paused(self) -> bool:
        """Check if timer is paused."""
        return self._is_paused

    def get_remaining_time(self) -> float:
        """Get remaining time until callback execution."""
        if self._is_paused:
            return self._remaining_time
        elif self._handle and not self._handle.cancelled():
            elapsed = time.time() - self._start_time
            return max(0.0, self.interval - elapsed)
        else:
            return 0.0

    def _schedule_callback(self) -> None:
        """Schedule the callback to be called after remaining time."""
        if self._is_cancelled or self._remaining_time <= 0:
            return

        self._handle = self.loop.call_later(
            self._remaining_time, self._wrapped_callback
        )

    def _wrapped_callback(self) -> None:
        """Wrapped callback that handles timer state."""
        if self._is_cancelled:
            return

        # Reset for potential reuse
        self._handle = None

        try:
            self.callback()
        except Exception as e:
            logger.error(f"Error in timer callback: {e}")


class TimerManager:
    """
    Manages multiple pausable timers with pause/resume coordination.
    """

    def __init__(self):
        self.timers: list[PausableTimer] = []
        self._is_paused: bool = False

    def add_timer(self, timer: PausableTimer) -> None:
        """Add a timer to be managed."""
        self.timers.append(timer)

    def remove_timer(self, timer: PausableTimer) -> None:
        """Remove a timer from management."""
        if timer in self.timers:
            timer.cancel()
            self.timers.remove(timer)

    def pause_all(self) -> None:
        """Pause all managed timers."""
        if self._is_paused:
            return

        self._is_paused = True
        for timer in self.timers:
            timer.pause()

        logger.debug(f"Paused {len(self.timers)} timers")

    def resume_all(self) -> None:
        """Resume all managed timers."""
        if not self._is_paused:
            return

        self._is_paused = False
        for timer in self.timers:
            timer.resume()

        logger.debug(f"Resumed {len(self.timers)} timers")

    def cancel_all(self) -> None:
        """Cancel all managed timers."""
        for timer in self.timers:
            timer.cancel()
        self.timers.clear()
        self._is_paused = False

        logger.debug("Cancelled all timers")

    def is_paused(self) -> bool:
        """Check if timer manager is paused."""
        return self._is_paused
