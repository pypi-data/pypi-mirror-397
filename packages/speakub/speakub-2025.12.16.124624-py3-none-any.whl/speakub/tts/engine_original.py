#!/usr/bin/env python3
# TTS Engine - Abstract base for text-to-speech functionality.

import asyncio
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from speakub.core.exceptions import TTSError

logger = logging.getLogger(__name__)


class TTSState(Enum):
    """TTS playback states."""

    IDLE = "idle"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class TTSEngine(ABC):
    """Abstract base class for TTS engines."""

    def __init__(self):
        """Initialize TTS engine."""
        self.state = TTSState.IDLE
        self.current_text = ""
        self.current_position = 0
        self.total_length = 0
        self.on_state_changed: Optional[Callable[[TTSState], None]] = None
        self.on_position_changed: Optional[Callable[[int, int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._stop_requested = threading.Event()

        # CPU Optimization: Idle mode support
        self._idle_mode = False

        # Enhanced error recovery tracking
        self._error_count = 0
        self._last_error_time = 0.0
        self._consecutive_failures = 0
        self._circuit_breaker_until = 0.0
        self._recovery_attempts = 0

    @abstractmethod
    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text to audio.
        """

    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available voices.
        """

    @abstractmethod
    def pause(self) -> None:
        """Pause audio playback."""

    @abstractmethod
    def resume(self) -> None:
        """Resume audio playback."""

    @abstractmethod
    def stop(self) -> None:
        """Stop audio playback."""
        self._stop_requested.set()

    @abstractmethod
    def seek(self, position: int) -> None:
        """
        Seek to position in audio.
        """

    @abstractmethod
    async def cleanup_resources(self) -> None:
        """
        Clean up all resources used by this TTS engine.
        This includes:
        - Stopping async event loops
        - Terminating audio players/MPV
        - Cleaning up temporary files
        - Releasing any other resources
        """
                # Import new managers
                from speakub.tts.state_manager import TTSState, TTSStateManager
                from speakub.tts.error_recovery_manager import TTSErrorRecoveryManager
                from speakub.tts.async_manager import TTSAsyncManager

    def set_pitch(self, pitch: str) -> None:
        """
        Set TTS pitch.

        Args:
            pitch: Pitch value (e.g., "+10Hz", "-5Hz", "+0Hz")
        """
        # Default implementation - subclasses should override

    def get_pitch(self) -> str:
        """Get current TTS pitch."""
        # Default implementation - subclasses should override
        return "+0Hz"

    def set_idle_mode(self, idle: bool) -> None:
        """Set idle mode for CPU optimization."""
        self._idle_mode = idle
        logger.debug(f"TTS engine idle mode: {idle}")

    def _change_state(self, new_state: TTSState) -> None:
        """Change TTS state and notify listeners."""
        if self.state != new_state:
            self.state = new_state
            if self.on_state_changed:
                self.on_state_changed(new_state)

    def _update_position(self, position: int, total: int) -> None:
        """Update position and notify listeners."""
        self.current_position = position
        self.total_length = total
        if self.on_position_changed:
            self.on_position_changed(position, total)

    def _report_error(self, error_message: str) -> None:
        """Report error and notify listeners."""
        self._change_state(TTSState.ERROR)
        if self.on_error:
            self.on_error(error_message)

    def start_async_loop(self) -> None:
        """Start the async event loop in a separate thread."""
        if self._thread and self._thread.is_alive():
            return

        def run_loop():
            self._event_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._event_loop)
            self._event_loop.run_forever()

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

        while self._event_loop is None:
            threading.Event().wait(0.01)

    def stop_async_loop(self) -> None:
        """Stop the async event loop."""
        if self._event_loop and self._event_loop.is_running():
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)

    async def speak_text_async(
        self, text: str, voice: str = "default", **kwargs
    ) -> None:
        """
        Speak text with smart caching.
        """
        # CPU Optimization: Skip TTS synthesis in idle mode
        if self._idle_mode:
            logger.debug("TTS synthesis skipped due to idle mode")
            return

        try:
            self._change_state(TTSState.LOADING)
            self.current_text = text

            # Only synthesize if text is different or we don't have audio
            if (
                not hasattr(self, "_current_text")
                or self._current_text != text
                or not hasattr(self, "_current_audio_file")
                or not self._current_audio_file
            ):
                audio_data = await self.synthesize(text, voice, **kwargs)
                if hasattr(self, "_current_text"):
                    self._current_text = text
            else:
                # Reuse existing audio file
                audio_data = None  # Signal to reuse existing file

            self._change_state(TTSState.PLAYING)

            # play_audio will handle file reuse
            if audio_data:
                await self.play_audio(audio_data)
            else:
                # Just resume playback
                await self.play_audio(b"")  # Empty data signals reuse

        except Exception as e:
            error_msg = f"TTS synthesis failed: {e}"
            self._report_error(error_msg)
            raise TTSError(error_msg) from e

    def speak_text(self, text: str, voice: str = "default", **kwargs) -> None:
        """
        Speak text (non-blocking wrapper).
        """
        if not self._event_loop:
            self.start_async_loop()

        if self._event_loop:
            asyncio.run_coroutine_threadsafe(
                self.speak_text_async(text, voice, **kwargs), self._event_loop
            )

    def speak_text_sync(self, text: str, voice: str = "default", **kwargs) -> None:
        """
        Speak text and block until playback is complete (synchronous wrapper).
        Optimized with better timeout handling and CPU usage reduction.
        """
        if not self._event_loop:
            self.start_async_loop()
        self._stop_requested.clear()

        if self._event_loop:
            future = asyncio.run_coroutine_threadsafe(
                self.speak_text_async(text, voice, **kwargs), self._event_loop
            )
            try:
                # Use a more reasonable timeout and add small sleep to reduce CPU usage
                # Segmented timeout to allow interruption
                for _ in range(12):  # 60s total timeout, checked every 5s
                    if self._stop_requested.is_set():
                        future.cancel()
                        raise TTSError("TTS operation cancelled by user.")
                    try:
                        return future.result(timeout=5)
                    except asyncio.TimeoutError:
                        continue  # Continue to next segment
                raise TimeoutError("TTS playback timed out after 60s")
            except asyncio.TimeoutError:
                self._report_error("TTS synthesis timed out after 60s")
                raise TimeoutError("TTS playback timed out")
            except Exception as e:
                error_msg = f"TTS playback failed: {e}"
                self._report_error(error_msg)
                raise TTSError(error_msg) from e

    def is_available(self) -> bool:
        """Check if TTS engine is available."""
        try:
            if self._event_loop:
                future = asyncio.run_coroutine_threadsafe(
                    self.get_available_voices(), self._event_loop
                )
                voices = future.result(timeout=5.0)
                return len(voices) > 0
            return False
        except Exception:
            return False

    # ***** START OF REDESIGN *****
    # Split play_audio into non-blocking start and wait methods for better concurrency control
    @abstractmethod
    async def play_audio_non_blocking(self, audio_data: bytes) -> None:
        """
        Start playing audio data without blocking.
        """

    @abstractmethod
    async def wait_for_playback_completion(self) -> None:
        """
        Wait for the currently playing audio to complete.
        """

    def _should_attempt_recovery(self, error_type: str) -> bool:
        """
        Determine if error recovery should be attempted.

        Args:
            error_type: Type of error encountered

        Returns:
            bool: True if recovery should be attempted
        """
        import time

        # Check circuit breaker
        current_time = time.time()
        if current_time < self._circuit_breaker_until:
            logger.warning(
                f"Circuit breaker active, skipping recovery. "
                f"Tries until {self._circuit_breaker_until}"
            )
            return False

        # Allow recovery for network and temporary errors
        recoverable_errors = {
            "timeout",
            "connection",
            "network",
            "rate_limit",
            "temporary",
            "unavailable",
            "overload",
        }

        error_is_recoverable = any(
            err_key in error_type.lower() for err_key in recoverable_errors
        )

        # Exponential backoff for consecutive failures
        if self._consecutive_failures > 0:
            max_failures = 3  # Allow up to 3 consecutive failures
            if self._consecutive_failures >= max_failures:
                time_since_last = current_time - self._last_error_time
                backoff_time = min(
                    300, 5 * (2 ** (self._consecutive_failures - max_failures))
                )
                if time_since_last < backoff_time:
                    logger.warning(
                        f"Too many consecutive failures ({self._consecutive_failures}), "
                        f"backing off for {backoff_time}s"
                    )
                    return False

        return error_is_recoverable

    def _record_error(self, error_type: str, recovery_attempted: bool = False):
        """Record error for recovery tracking."""
        import time

        current_time = time.time()
        self._error_count += 1
        self._last_error_time = current_time

        # Track consecutive failures
        self._consecutive_failures += 1

        # Trigger circuit breaker if too many failures
        if self._consecutive_failures >= 5:
            backoff_duration = min(600, 30 * (2 ** (self._consecutive_failures - 5)))
            self._circuit_breaker_until = current_time + backoff_duration
            logger.warning(
                f"Circuit breaker activated for {backoff_duration}s "
                f"due to {self._consecutive_failures} consecutive failures"
            )

        logger.debug(
            f"Error recorded: type={error_type}, attempts={self._recovery_attempts}, "
            f"failures={self._consecutive_failures}, recovery={recovery_attempted}"
        )

    def _record_recovery_success(self):
        """Record successful recovery."""
        self._consecutive_failures = 0  # Reset failure counter
        logger.debug("Recovery successful, resetting failure counter")

    def _perform_exponential_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff delay with smarter jitter thresholds."""
        import random
        import time

        base_delay = 1.0
        max_delay = 30.0

        # Smarter jitter thresholds based on attempt number
        # Early attempts: wider jitter to spread out initial retries
        # Later attempts: narrower jitter for more predictable delays
        if attempt < 2:
            jitter_min, jitter_max = 0.7, 1.3  # Wider range for early attempts
        elif attempt < 4:
            jitter_min, jitter_max = 0.8, 1.2  # Medium range
        else:
            # Narrow range for later attempts to avoid excessive delays
            jitter_min, jitter_max = 0.9, 1.1

        jitter = random.uniform(jitter_min, jitter_max)

        delay = min(base_delay * (2**attempt), max_delay) * jitter

        # Ensure we don't trigger circuit breaker
        if (
            hasattr(self, "_circuit_breaker_until")
            and time.time() < self._circuit_breaker_until
        ):
            delay = max(delay, self._circuit_breaker_until - time.time() + 1)

        return delay

    async def _execute_with_retry(
        self,
        operation_func,
        operation_name: str = "operation",
        max_retries: int = 3,
        *args,
        **kwargs,
    ):
        """
        Execute an operation with retry logic and error recovery.

        Args:
            operation_func: Async function to execute
            operation_name: Name for logging
            max_retries: Maximum retry attempts
            *args, **kwargs: Arguments for operation_func

        Returns:
            Result of operation_func

        Raises:
            TTSError: If all retries fail
        """
        import time

        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    # Wait before retry
                    backoff_delay = self._perform_exponential_backoff(attempt - 1)
                    logger.info(
                        f"Retry {attempt}/{max_retries} for {operation_name} "
                        f"after {backoff_delay:.1f}s delay"
                    )
                    await asyncio.sleep(backoff_delay)

                    # Reset circuit breaker state on retries
                    if attempt == 1 and hasattr(self, "_circuit_breaker_until"):
                        self._circuit_breaker_until = 0.0

                # Execute operation
                result = await operation_func(*args, **kwargs)

                if attempt > 0:
                    self._record_recovery_success()
                    logger.info(
                        f"Recovery successful for {operation_name} on attempt {attempt + 1}"
                    )

                return result

            except Exception as e:
                error_type = type(e).__name__.lower()
                error_msg = str(e)

                if attempt < max_retries:
                    should_retry = self._should_attempt_recovery(error_type)
                    if should_retry:
                        logger.warning(
                            f"{operation_name} failed with recoverable error: {error_msg} "
                            f"(attempt {attempt + 1}/{max_retries + 1})"
                        )
                        self._record_error(error_type, recovery_attempted=True)
                        continue
                    else:
                        logger.error(
                            f"{operation_name} failed with non-recoverable error: {error_msg}"
                        )
                        break
                else:
                    logger.error(
                        f"{operation_name} failed after {max_retries + 1} attempts: {error_msg}"
                    )

                # Record final error
                self._record_error(error_type, recovery_attempted=False)
                raise TTSError(f"{operation_name} failed: {error_msg}") from e

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error recovery statistics."""
        import time

        current_time = time.time()
        return {
            "total_errors": self._error_count,
            "consecutive_failures": self._consecutive_failures,
            "last_error_time": self._last_error_time,
            "time_since_last_error": (
                current_time - self._last_error_time if self._last_error_time else None
            ),
            "circuit_breaker_active": current_time < self._circuit_breaker_until,
            "circuit_breaker_remaining": (
                max(0, self._circuit_breaker_until - current_time)
                if current_time < self._circuit_breaker_until
                else 0
            ),
            "recovery_attempts": self._recovery_attempts,
        }

    # Keep backward compatibility - default implementation uses the split methods
    async def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data and wait for completion (backward compatibility).
        """
        await self.play_audio_non_blocking(audio_data)
        await self.wait_for_playback_completion()
