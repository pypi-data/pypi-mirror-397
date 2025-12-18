#!/usr/bin/env python3
# TTS Engine - Abstract base for text-to-speech functionality (REFACTORED).

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional

from speakub.core.exceptions import TTSError
from speakub.tts.state_manager import TTSState, TTSStateManager
from speakub.tts.error_recovery_manager import TTSErrorRecoveryManager
from speakub.tts.async_manager import TTSAsyncManager

logger = logging.getLogger(__name__)


class TTSEngine(ABC):
    """
    Abstract base class for TTS engines.

    Uses composition to delegate responsibility:
    - TTSStateManager: State transitions and state machine logic
    - TTSErrorRecoveryManager: Error tracking and circuit breaker
    - TTSAsyncManager: Event loop and async execution
    """

    def __init__(self):
        """Initialize TTS engine with manager classes."""
        # Manager instances for separated concerns
        self._state_manager = TTSStateManager()
        self._error_manager = TTSErrorRecoveryManager()
        self._async_manager = TTSAsyncManager()

        # Legacy attributes for backward compatibility
        self.current_text = ""
        self.current_position = 0
        self.total_length = 0
        self.on_state_changed: Optional[Callable[[TTSState], None]] = None
        self.on_position_changed: Optional[Callable[[int, int], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None

        # CPU Optimization: Idle mode support
        self._idle_mode = False

        # Wire up state manager callback
        self._state_manager.on_state_changed = self._on_state_changed_internal

    # ============================================================================
    # ENGINE PARAMETERS INTERFACE - NEW: Unified parameter access
    # ============================================================================

    @property
    def engine_parameters(self) -> Dict[str, Any]:
        """
        Unified engine parameter interface.
        Provides standardized access to engine-specific parameters.
        """
        return {
            'char_limit': self._get_char_limit(),
            'batch_size_preference': self._get_batch_size_preference(),
            'supports_batch_merging': self._supports_batch_merging(),
            'needs_text_sanitization': self._needs_text_sanitization(),
            'rate_limit_cooldown': self._get_rate_limit_cooldown(),
        }

    @abstractmethod
    def _get_char_limit(self) -> int:
        """Get engine-specific character limit for batching."""
        pass

    @abstractmethod
    def _get_batch_size_preference(self) -> int:
        """Get preferred batch size for this engine."""
        pass

    @abstractmethod
    def _supports_batch_merging(self) -> bool:
        """Check if engine supports merging multiple texts into single API call."""
        pass

    @abstractmethod
    def _needs_text_sanitization(self) -> bool:
        """Check if engine requires text sanitization."""
        pass

    @abstractmethod
    def _get_rate_limit_cooldown(self) -> float:
        """Get rate limiting cooldown period in seconds."""
        pass

    # ============================================================================
    # STATE MANAGEMENT PROPERTIES AND METHODS
    # ============================================================================

    @property
    def state(self) -> TTSState:
        """Get current state (backward compatible property)."""
        return self._state_manager.state

    @state.setter
    def state(self, new_state: TTSState) -> None:
        """Set state via state manager."""
        self._state_manager.transition(new_state)

    def _on_state_changed_internal(self, new_state: TTSState) -> None:
        """Internal callback when state changes."""
        if self.on_state_changed:
            try:
                self.on_state_changed(new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")

    def _change_state(self, new_state: TTSState) -> None:
        """Change TTS state and notify listeners (uses state manager)."""
        self._state_manager.transition(new_state)

    def _transition_state(self, new_state: TTSState) -> bool:
        """Transition to new state and return success status."""
        return self._state_manager.transition(new_state)

    def _update_position(self, position: int, total: int) -> None:
        """Update position and notify listeners."""
        self.current_position = position
        self.total_length = total
        if self.on_position_changed:
            try:
                self.on_position_changed(position, total)
            except Exception as e:
                logger.error(f"Error in position change callback: {e}")

    def _report_error(self, error_message: str) -> None:
        """Report error and notify listeners."""
        self._state_manager.transition(TTSState.ERROR)
        self._error_manager.record_error()
        if self.on_error:
            try:
                self.on_error(error_message)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")

    # ============================================================================
    # ASYNC MANAGEMENT METHODS
    # ============================================================================

    @property
    def _event_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """
        Get the event loop from async manager.

        This property provides backward compatibility with code that expects
        to access _event_loop directly on the engine.
        """
        return self._async_manager._event_loop if self._async_manager else None

    def start_async_loop(self) -> None:
        """Start the async event loop in a separate thread."""
        self._async_manager.start_loop()

    def stop_async_loop(self) -> None:
        """Stop the async event loop."""
        self._async_manager.stop_loop()

    # ============================================================================
    # ERROR RECOVERY METHODS
    # ============================================================================

    def _should_attempt_recovery(self, error_type: str) -> bool:
        """
        Determine if error recovery should be attempted.

        Args:
            error_type: Type of error encountered

        Returns:
            bool: True if recovery should be attempted
        """
        # Check circuit breaker
        if self._error_manager.is_circuit_open():
            logger.warning("Circuit breaker active, skipping recovery")
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

        return any(
            err_key in error_type.lower() for err_key in recoverable_errors
        )

    def _record_error(self, error_type: str, recovery_attempted: bool = False):
        """Record error for recovery tracking (delegates to error manager)."""
        self._error_manager.record_error()
        if recovery_attempted:
            self._error_manager.increment_recovery_attempts()

    def _record_recovery_success(self):
        """Record successful recovery (delegates to error manager)."""
        self._error_manager.reset_on_success()

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error recovery statistics (from error manager)."""
        return self._error_manager.get_status()

    # ============================================================================
    # CPU OPTIMIZATION METHODS
    # ============================================================================

    def set_idle_mode(self, idle: bool) -> None:
        """Set idle mode for CPU optimization."""
        self._idle_mode = idle
        logger.debug(f"TTS engine idle mode: {idle}")

    # ============================================================================
    # PITCH CONTROL METHODS
    # ============================================================================

    def set_pitch(self, pitch: str) -> None:
        """
        Set TTS pitch.

        Args:
            pitch: Pitch value (e.g., "+10Hz", "-5Hz", "+0Hz")
        """
        # Default implementation - subclasses should override
        pass

    def get_pitch(self) -> str:
        """Get current TTS pitch."""
        # Default implementation - subclasses should override
        return "+0Hz"

    # ============================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ============================================================================

    @abstractmethod
    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text to audio.

        Args:
            text: Text to synthesize
            voice: Voice name
            **kwargs: Additional synthesis parameters

        Returns:
            bytes: Audio data
        """
        pass

    @abstractmethod
    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available voices."""
        pass

    @abstractmethod
    def pause(self) -> None:
        """Pause audio playback."""
        pass

    @abstractmethod
    def resume(self) -> None:
        """Resume audio playback."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop audio playback."""
        pass

    @abstractmethod
    def seek(self, position: int) -> None:
        """Seek to position in audio."""
        pass

    @abstractmethod
    async def cleanup_resources(self) -> None:
        """Clean up all resources used by this TTS engine."""
        pass

    @abstractmethod
    async def play_audio_non_blocking(self, audio_data: bytes) -> None:
        """Start playing audio data without blocking."""
        pass

    @abstractmethod
    async def wait_for_playback_completion(self) -> None:
        """Wait for the currently playing audio to complete."""
        pass

    # ============================================================================
    # HIGH-LEVEL API METHODS
    # ============================================================================

    async def speak_text_async(
        self, text: str, voice: str = "default", **kwargs
    ) -> None:
        """
        Speak text with smart caching.

        Args:
            text: Text to speak
            voice: Voice name
            **kwargs: Additional parameters
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

            # Play audio
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

        Args:
            text: Text to speak
            voice: Voice name
            **kwargs: Additional parameters
        """
        self._async_manager.start_loop()
        self._async_manager.run_coroutine_async(
            self.speak_text_async(text, voice, **kwargs)
        )

    def speak_text_sync(self, text: str, voice: str = "default",
                        timeout: Optional[float] = 60, **kwargs) -> None:
        """
        Speak text and block until playback is complete (synchronous wrapper).

        Args:
            text: Text to speak
            voice: Voice name
            timeout: Timeout in seconds, None for no timeout
            **kwargs: Additional parameters
        """
        self._async_manager.start_loop()

        try:
            result = self._async_manager.run_coroutine_threadsafe(
                self.speak_text_async(text, voice, **kwargs), timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            timeout_msg = ("TTS synthesis timed out (server-side)"
                           if timeout is None else f"TTS synthesis timed out after {timeout}s")
            self._report_error(timeout_msg)
            raise TimeoutError("TTS playback timed out")
        except Exception as e:
            error_msg = f"TTS playback failed: {e}"
            self._report_error(error_msg)
            raise TTSError(error_msg) from e

    def is_available(self) -> bool:
        """Check if TTS engine is available."""
        try:
            if self._async_manager.is_running():
                voices = self._async_manager.run_coroutine_threadsafe(
                    self.get_available_voices(), timeout=5.0
                )
                return len(voices) > 0
            return False
        except Exception:
            return False

    # Keep backward compatibility - default implementation uses the split methods
    async def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data and wait for completion (backward compatibility).

        Args:
            audio_data: Audio data to play
        """
        await self.play_audio_non_blocking(audio_data)
        await self.wait_for_playback_completion()

    # ============================================================================
    # DIAGNOSTIC METHODS
    # ============================================================================

    def get_diagnostics(self) -> Dict[str, Any]:
        """Get complete diagnostic information."""
        return {
            "state": self._state_manager.state.value,
            "error_stats": self._error_manager.get_status(),
            "async_stats": self._async_manager.get_status(),
            "idle_mode": self._idle_mode,
            "current_text": self.current_text,
            "current_position": self.current_position,
            "total_length": self.total_length,
        }
