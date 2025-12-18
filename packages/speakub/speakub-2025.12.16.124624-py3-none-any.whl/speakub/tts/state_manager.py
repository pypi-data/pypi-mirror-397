#!/usr/bin/env python3
"""TTS State Manager - Manages TTS engine state and transitions."""

import logging
from enum import Enum
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class TTSState(Enum):
    """TTS playback states."""

    IDLE = "idle"
    LOADING = "loading"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class TTSStateManager:
    """Manages TTS engine state and state transitions."""

    # Valid state transitions
    VALID_TRANSITIONS = {
        TTSState.IDLE: {TTSState.LOADING, TTSState.ERROR},
        TTSState.LOADING: {TTSState.PLAYING, TTSState.ERROR, TTSState.IDLE},
        TTSState.PLAYING: {TTSState.PAUSED, TTSState.STOPPED, TTSState.ERROR},
        TTSState.PAUSED: {TTSState.PLAYING, TTSState.STOPPED, TTSState.ERROR},
        TTSState.STOPPED: {TTSState.IDLE, TTSState.ERROR},
        TTSState.ERROR: {TTSState.IDLE, TTSState.LOADING},
    }

    def __init__(self):
        """Initialize state manager."""
        self._state = TTSState.IDLE
        self._on_state_changed: Optional[Callable[[TTSState], None]] = None

    @property
    def state(self) -> TTSState:
        """Get current state."""
        return self._state

    @property
    def on_state_changed(self) -> Optional[Callable[[TTSState], None]]:
        """Get state changed callback."""
        return self._on_state_changed

    @on_state_changed.setter
    def on_state_changed(self, callback: Optional[Callable[[TTSState], None]]) -> None:
        """Set state changed callback."""
        self._on_state_changed = callback

    def transition(self, new_state: TTSState) -> bool:
        """
        Attempt to transition to a new state.

        Args:
            new_state: The target state

        Returns:
            bool: True if transition was valid and performed, False otherwise
        """
        if not self.is_valid_transition(self._state, new_state):
            logger.warning(
                f"Invalid state transition: {self._state.value} → {new_state.value}"
            )
            return False

        old_state = self._state
        self._state = new_state
        logger.debug(
            f"State transition: {old_state.value} → {new_state.value}")

        # Notify listeners
        if self._on_state_changed:
            try:
                self._on_state_changed(new_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")

        return True

    def is_valid_transition(self, from_state: TTSState, to_state: TTSState) -> bool:
        """
        Check if a state transition is valid.

        Args:
            from_state: Current state
            to_state: Target state

        Returns:
            bool: True if transition is valid
        """
        if from_state == to_state:
            return True
        return to_state in self.VALID_TRANSITIONS.get(from_state, set())

    def get_state(self) -> TTSState:
        """Get current state."""
        return self._state

    def is_idle(self) -> bool:
        """Check if engine is idle."""
        return self._state == TTSState.IDLE

    def is_playing(self) -> bool:
        """Check if engine is playing."""
        return self._state == TTSState.PLAYING

    def is_paused(self) -> bool:
        """Check if engine is paused."""
        return self._state == TTSState.PAUSED

    def is_loading(self) -> bool:
        """Check if engine is loading."""
        return self._state == TTSState.LOADING

    def is_stopped(self) -> bool:
        """Check if engine is stopped."""
        return self._state == TTSState.STOPPED

    def is_error(self) -> bool:
        """Check if engine is in error state."""
        return self._state == TTSState.ERROR

    def reset(self) -> None:
        """Reset state to IDLE without notifying listeners."""
        self._state = TTSState.IDLE
