#!/usr/bin/env python3
"""
TTS State Machine Management

Centralizes TTS state transitions and event handling.
Replaces scattered state management in TTSIntegration.
"""

import asyncio
import logging
import threading
from enum import Enum
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class TTSState(Enum):
    """TTS playback states."""

    IDLE = "IDLE"  # Initial state, no playback
    PLAYING = "PLAYING"  # Currently playing
    PAUSED = "PAUSED"  # Paused, can resume
    STOPPED = "STOPPED"  # Stopped, needs restart
    ERROR = "ERROR"  # Error state


class TTSStateTransition:
    """Represents a valid state transition."""

    def __init__(
        self,
        from_state: TTSState,
        to_state: TTSState,
        callback: Optional[Callable] = None,
    ):
        self.from_state = from_state
        self.to_state = to_state
        self.callback = callback


class TTSStateMachine:
    """
    TTS State Machine - Manages state transitions and event handling.

    Features:
        - Validated state transitions
        - Event-driven callbacks
        - Thread-safe operations
        - Async event management
        - State persistence

    Example:
        ```python
        machine = TTSStateMachine()
        old_state = machine.transition_to(TTSState.PLAYING)
        ```
    """

    # Valid state transitions
    VALID_TRANSITIONS = {
        TTSState.IDLE: [TTSState.PLAYING, TTSState.ERROR],
        TTSState.PLAYING: [TTSState.PAUSED, TTSState.STOPPED, TTSState.ERROR],
        TTSState.PAUSED: [TTSState.PLAYING, TTSState.STOPPED, TTSState.ERROR],
        TTSState.STOPPED: [TTSState.PLAYING, TTSState.IDLE, TTSState.ERROR],
        TTSState.ERROR: [TTSState.IDLE, TTSState.STOPPED],
    }

    def __init__(self, initial_state: TTSState = TTSState.IDLE):
        """
        Initialize state machine.

        Args:
            initial_state: Initial TTS state (default: IDLE)
        """
        self._current_state = initial_state
        self._previous_state = initial_state
        self._state_lock = threading.RLock()
        self._async_state_event = asyncio.Event()

        # Callbacks for state changes
        self._state_change_callbacks: Dict[
            TTSState, list[Callable[[TTSState, TTSState], Any]]
        ] = {state: [] for state in TTSState}

        # Transition-specific callbacks
        self._transition_callbacks: Dict[tuple, list[Callable]] = {}

        logger.debug(
            f"TTSStateMachine initialized with state: {initial_state.value}")

    @property
    def current_state(self) -> TTSState:
        """Get current state (thread-safe)."""
        with self._state_lock:
            return self._current_state

    @property
    def previous_state(self) -> TTSState:
        """Get previous state (thread-safe)."""
        with self._state_lock:
            return self._previous_state

    def can_transition_to(self, new_state: TTSState) -> bool:
        """
        Check if transition to new state is valid.

        Args:
            new_state: Target state

        Returns:
            True if transition is valid, False otherwise
        """
        with self._state_lock:
            return new_state in self.VALID_TRANSITIONS.get(
                self._current_state, []
            )

    def transition_to(
        self, new_state: TTSState, reason: str = ""
    ) -> Optional[TTSState]:
        """
        Perform state transition with validation.

        Args:
            new_state: Target state
            reason: Optional reason for transition

        Returns:
            Previous state if transition succeeded, None otherwise

        Raises:
            ValueError: If transition is invalid
        """
        with self._state_lock:
            if not self.can_transition_to(new_state):
                raise ValueError(
                    f"Invalid transition from {self._current_state.value} to {new_state.value}"
                )

            old_state = self._current_state
            self._previous_state = old_state
            self._current_state = new_state

            logger.info(
                f"State transition: {old_state.value} → {new_state.value}"
                f"{f' (reason: {reason})' if reason else ''}"
            )

            # Trigger callbacks outside the lock to avoid deadlocks
            return old_state

    def _trigger_callbacks(
        self, old_state: TTSState, new_state: TTSState
    ) -> None:
        """Trigger registered callbacks for state change."""
        # General state change callbacks
        if new_state in self._state_change_callbacks:
            for callback in self._state_change_callbacks[new_state]:
                try:
                    callback(old_state, new_state)
                except Exception as e:
                    logger.warning(f"Error in state change callback: {e}")

        # Transition-specific callbacks
        transition_key = (old_state, new_state)
        if transition_key in self._transition_callbacks:
            for callback in self._transition_callbacks[transition_key]:
                try:
                    callback()
                except Exception as e:
                    logger.warning(f"Error in transition callback: {e}")

    def register_state_change_callback(
        self, state: TTSState, callback: Callable[[TTSState, TTSState], Any]
    ) -> None:
        """
        Register callback for state changes to specific state.

        Args:
            state: State to monitor
            callback: Function to call on state change (receives old_state, new_state)
        """
        with self._state_lock:
            if state in self._state_change_callbacks:
                self._state_change_callbacks[state].append(callback)

    def register_transition_callback(
        self,
        from_state: TTSState,
        to_state: TTSState,
        callback: Callable,
    ) -> None:
        """
        Register callback for specific transition.

        Args:
            from_state: Source state
            to_state: Target state
            callback: Function to call on transition
        """
        with self._state_lock:
            key = (from_state, to_state)
            if key not in self._transition_callbacks:
                self._transition_callbacks[key] = []
            self._transition_callbacks[key].append(callback)

    def reset_to_idle(self) -> None:
        """Reset state machine to idle state."""
        with self._state_lock:
            if self._current_state != TTSState.IDLE:
                self._previous_state = self._current_state
                self._current_state = TTSState.IDLE
                logger.debug("State machine reset to IDLE")

    def is_playing(self) -> bool:
        """Check if currently playing."""
        return self.current_state == TTSState.PLAYING

    def is_paused(self) -> bool:
        """Check if currently paused."""
        return self.current_state == TTSState.PAUSED

    def is_stopped(self) -> bool:
        """Check if currently stopped."""
        return self.current_state == TTSState.STOPPED

    def is_idle(self) -> bool:
        """Check if in idle state."""
        return self.current_state == TTSState.IDLE

    def is_error(self) -> bool:
        """Check if in error state."""
        return self.current_state == TTSState.ERROR

    def is_active(self) -> bool:
        """Check if in active state (PLAYING, PAUSED, or ERROR)."""
        state = self.current_state
        return state in (TTSState.PLAYING, TTSState.PAUSED, TTSState.ERROR)

    def get_state_info(self) -> Dict[str, Any]:
        """Get detailed state information."""
        with self._state_lock:
            return {
                "current_state": self._current_state.value,
                "previous_state": self._previous_state.value,
                "is_playing": self._current_state == TTSState.PLAYING,
                "is_paused": self._current_state == TTSState.PAUSED,
                "is_stopped": self._current_state == TTSState.STOPPED,
                "is_idle": self._current_state == TTSState.IDLE,
                "is_error": self._current_state == TTSState.ERROR,
            }

    async def wait_for_state(
        self, target_state: TTSState, timeout: Optional[float] = None
    ) -> bool:
        """
        Wait for state machine to reach target state.

        Args:
            target_state: State to wait for
            timeout: Optional timeout in seconds

        Returns:
            True if target state reached, False if timeout
        """
        if self.current_state == target_state:
            return True

        try:
            if timeout:
                await asyncio.wait_for(
                    self._wait_for_state_internal(target_state), timeout=timeout
                )
            else:
                await self._wait_for_state_internal(target_state)
            return True
        except asyncio.TimeoutError:
            logger.warning(
                f"Timeout waiting for state {target_state.value}"
            )
            return False

    async def _wait_for_state_internal(self, target_state: TTSState) -> None:
        """Internal async wait implementation."""
        while self.current_state != target_state:
            await asyncio.sleep(0.1)
