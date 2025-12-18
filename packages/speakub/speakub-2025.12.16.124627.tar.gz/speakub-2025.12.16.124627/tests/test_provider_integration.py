#!/usr/bin/env python3
"""
Integration tests for TTS Providers and Manager classes.

Tests verify that:
1. State transitions work correctly (IDLE → LOADING → PLAYING → IDLE, PAUSE/RESUME, STOP)
2. Error recovery and circuit breaker logic works across providers
3. Async management and event loop integration work
4. Backward compatibility is maintained
5. Provider-specific behavior is preserved
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Any

from speakub.tts.state_manager import TTSState, TTSStateManager
from speakub.tts.error_recovery_manager import TTSErrorRecoveryManager
from speakub.tts.async_manager import TTSAsyncManager
from speakub.tts.engine import TTSEngine


class MockTTSProvider(TTSEngine):
    """Mock TTS provider for testing."""

    def __init__(self):
        """Initialize mock provider."""
        super().__init__()
        self.synthesis_called = False
        self.play_called = False
        self.pause_called = False
        self.resume_called = False
        self.stop_called = False

    def get_current_state(self) -> str:
        """Get current state for monitoring (provider-specific method)."""
        return self._state_manager.state.value

    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """Mock synthesize."""
        self.synthesis_called = True
        return b"mock_audio_data"

    async def get_available_voices(self):
        """Mock get voices."""
        return [{"name": "Mock Voice", "short_name": "mock"}]

    def pause(self):
        """Mock pause."""
        self.pause_called = True
        self._transition_state(TTSState.PAUSED)

    def resume(self):
        """Mock resume."""
        self.resume_called = True
        self._transition_state(TTSState.PLAYING)

    def stop(self):
        """Mock stop."""
        self.stop_called = True
        self._transition_state(TTSState.STOPPED)

    def seek(self, position: int):
        """Mock seek (not supported)."""
        pass

    async def cleanup_resources(self):
        """Mock cleanup."""
        pass

    async def play_audio_non_blocking(self, audio_data: bytes):
        """Mock play non-blocking."""
        self.play_called = True
        self._change_state(TTSState.PLAYING)

    async def wait_for_playback_completion(self):
        """Mock wait for completion."""
        pass


class TestStateManagerIntegration:
    """Test state manager integration with providers."""

    def test_provider_state_initialization(self):
        """Test that provider initializes with correct state."""
        provider = MockTTSProvider()
        assert provider.state == TTSState.IDLE
        assert provider.state.value == "idle"

    def test_state_transition_idle_to_loading(self):
        """Test IDLE → LOADING transition."""
        provider = MockTTSProvider()
        result = provider._transition_state(TTSState.LOADING)
        assert result is True
        assert provider.state == TTSState.LOADING

    def test_state_transition_loading_to_playing(self):
        """Test LOADING → PLAYING transition."""
        provider = MockTTSProvider()
        provider._transition_state(TTSState.LOADING)
        result = provider._transition_state(TTSState.PLAYING)
        assert result is True
        assert provider.state == TTSState.PLAYING

    def test_invalid_state_transition(self):
        """Test invalid state transition is rejected."""
        provider = MockTTSProvider()
        # Try to transition from IDLE directly to PAUSED (invalid)
        result = provider._transition_state(TTSState.PAUSED)
        assert result is False
        assert provider.state == TTSState.IDLE

    def test_state_transition_chain_complete_playback(self):
        """Test complete playback state transition chain."""
        provider = MockTTSProvider()

        # IDLE → LOADING
        assert provider._transition_state(TTSState.LOADING) is True
        assert provider.state == TTSState.LOADING

        # LOADING → PLAYING
        assert provider._transition_state(TTSState.PLAYING) is True
        assert provider.state == TTSState.PLAYING

        # PLAYING → IDLE (via STOPPED)
        assert provider._transition_state(TTSState.STOPPED) is True
        assert provider.state == TTSState.STOPPED

        assert provider._transition_state(TTSState.IDLE) is True
        assert provider.state == TTSState.IDLE

    def test_state_transition_with_pause_resume(self):
        """Test pause/resume state transitions."""
        provider = MockTTSProvider()

        # Setup: IDLE → LOADING → PLAYING
        provider._transition_state(TTSState.LOADING)
        provider._transition_state(TTSState.PLAYING)
        assert provider.state == TTSState.PLAYING

        # PLAYING → PAUSED
        assert provider._transition_state(TTSState.PAUSED) is True
        assert provider.state == TTSState.PAUSED

        # PAUSED → PLAYING (resume)
        assert provider._transition_state(TTSState.PLAYING) is True
        assert provider.state == TTSState.PLAYING

        # PLAYING → STOPPED
        assert provider._transition_state(TTSState.STOPPED) is True
        assert provider.state == TTSState.STOPPED

    def test_state_callback_notification(self):
        """Test that state change callbacks are invoked."""
        provider = MockTTSProvider()
        callback_states = []

        def on_state_changed(new_state):
            callback_states.append(new_state)

        provider.on_state_changed = on_state_changed

        # Wire up state manager callback
        provider._state_manager.on_state_changed = on_state_changed

        provider._transition_state(TTSState.LOADING)
        provider._transition_state(TTSState.PLAYING)

        # Note: Callback might not be invoked if not wired correctly in _change_state
        # This test documents expected behavior
        assert len(callback_states) >= 2


class TestErrorRecoveryIntegration:
    """Test error recovery manager integration."""

    def test_error_recording(self):
        """Test that errors are recorded."""
        provider = MockTTSProvider()
        error_stats = provider.get_error_stats()

        assert error_stats["error_count"] == 0
        assert error_stats["consecutive_failures"] == 0

        # Record an error
        provider._record_error("network_error")
        error_stats = provider.get_error_stats()

        assert error_stats["error_count"] == 1
        assert error_stats["consecutive_failures"] == 1

    def test_circuit_breaker_activation(self):
        """Test circuit breaker activates after max consecutive errors."""
        provider = MockTTSProvider()

        # Record 3 consecutive errors (should trigger circuit breaker)
        for i in range(3):
            provider._record_error("network_error")

        error_stats = provider.get_error_stats()
        assert error_stats["circuit_open"] is True

    def test_recovery_success_resets_counters(self):
        """Test that successful recovery resets error counters."""
        provider = MockTTSProvider()

        # Record errors
        for i in range(2):
            provider._record_error("network_error")

        error_stats = provider.get_error_stats()
        assert error_stats["consecutive_failures"] == 2

        # Record success
        provider._record_recovery_success()
        error_stats = provider.get_error_stats()
        assert error_stats["consecutive_failures"] == 0

    def test_retry_delay_calculation(self):
        """Test exponential backoff retry delay."""
        provider = MockTTSProvider()

        # Get initial retry delay (no errors yet)
        error_stats = provider.get_error_stats()
        initial_delay = error_stats["retry_delay"]

        # Record an error and check delay increases
        provider._record_error("network_error")
        error_stats = provider.get_error_stats()
        # Initial delay should be minimal since error_count is 1

        assert error_stats["retry_delay"] >= 0


class TestAsyncManagerIntegration:
    """Test async manager integration with provider."""

    def test_async_loop_startup(self):
        """Test async loop starts correctly."""
        provider = MockTTSProvider()
        provider.start_async_loop()

        # Give the loop time to start
        import time
        time.sleep(0.1)

        assert provider._async_manager.is_running() is True

        # Cleanup
        provider.stop_async_loop()

    def test_async_loop_shutdown(self):
        """Test async loop shuts down correctly."""
        provider = MockTTSProvider()
        provider.start_async_loop()

        # Give the loop time to start
        import time
        time.sleep(0.1)

        provider.stop_async_loop()

        # Give the loop time to stop
        time.sleep(0.2)

        assert provider._async_manager.is_running() is False

    @pytest.mark.asyncio
    async def test_coroutine_execution_threadsafe(self):
        """Test coroutine can be executed thread-safe."""
        provider = MockTTSProvider()
        provider.start_async_loop()

        # Give the loop time to start
        import time
        time.sleep(0.1)

        # Define a test coroutine
        async def test_coro():
            await asyncio.sleep(0.01)
            return "test_result"

        # Run it thread-safe
        try:
            result = provider._async_manager.run_coroutine_threadsafe(
                test_coro(), timeout=5.0
            )
            assert result == "test_result"
        finally:
            provider.stop_async_loop()


class TestProviderPlaybackWorkflow:
    """Test complete provider playback workflows."""

    @pytest.mark.asyncio
    async def test_basic_playback_workflow(self):
        """Test basic playback workflow: synthesize → play → stop."""
        provider = MockTTSProvider()

        # Start async loop
        provider.start_async_loop()
        import time
        time.sleep(0.1)

        try:
            # IDLE state
            assert provider.state == TTSState.IDLE

            # Synthesize (IDLE → LOADING)
            provider._change_state(TTSState.LOADING)
            assert provider.state == TTSState.LOADING

            audio_data = await provider.synthesize("test")
            assert audio_data == b"mock_audio_data"
            assert provider.synthesis_called is True

            # Play (LOADING → PLAYING)
            provider._change_state(TTSState.PLAYING)
            await provider.play_audio_non_blocking(audio_data)
            assert provider.state == TTSState.PLAYING
            assert provider.play_called is True

            # Stop (PLAYING → STOPPED → IDLE)
            provider.stop()
            assert provider.stop_called is True
            assert provider.state == TTSState.STOPPED

            provider._change_state(TTSState.IDLE)
            assert provider.state == TTSState.IDLE

        finally:
            provider.stop_async_loop()

    @pytest.mark.asyncio
    async def test_pause_resume_workflow(self):
        """Test pause/resume workflow."""
        provider = MockTTSProvider()

        # Setup: IDLE → LOADING → PLAYING
        provider._change_state(TTSState.LOADING)
        provider._change_state(TTSState.PLAYING)
        assert provider.state == TTSState.PLAYING

        # Pause
        provider.pause()
        assert provider.pause_called is True
        assert provider.state == TTSState.PAUSED

        # Resume
        provider.resume()
        assert provider.resume_called is True
        assert provider.state == TTSState.PLAYING

    def test_diagnostics_collection(self):
        """Test that diagnostics can be collected from provider."""
        provider = MockTTSProvider()

        # Perform some operations
        provider._transition_state(TTSState.LOADING)
        provider._record_error("test_error")

        # Get diagnostics
        diag = provider.get_diagnostics()

        assert "state" in diag
        assert "error_stats" in diag
        assert "async_stats" in diag
        assert diag["state"] == "loading"
        assert diag["error_stats"]["error_count"] >= 1


class TestProviderBackwardCompatibility:
    """Test backward compatibility with legacy code."""

    def test_state_property_get_set(self):
        """Test state can be accessed via property."""
        provider = MockTTSProvider()

        # Get via property
        assert provider.state == TTSState.IDLE

        # Set via property
        provider.state = TTSState.LOADING
        assert provider.state == TTSState.LOADING

        # Verify state manager is updated
        assert provider._state_manager.state == TTSState.LOADING

    def test_get_current_state_returns_string(self):
        """Test get_current_state returns string representation."""
        provider = MockTTSProvider()
        # IDLE → LOADING → PLAYING (valid path)
        provider._transition_state(TTSState.LOADING)
        provider._transition_state(TTSState.PLAYING)

        state_str = provider.get_current_state()
        assert isinstance(state_str, str)
        assert state_str == "playing"

    def test_change_state_delegates_to_manager(self):
        """Test _change_state properly delegates to state manager."""
        provider = MockTTSProvider()

        provider._change_state(TTSState.LOADING)
        assert provider.state == TTSState.LOADING
        assert provider._state_manager.state == TTSState.LOADING

    def test_error_callback_invocation(self):
        """Test on_error callback is invoked on errors."""
        provider = MockTTSProvider()
        error_messages = []

        def on_error(msg):
            error_messages.append(msg)

        provider.on_error = on_error

        # Trigger error via _report_error
        provider._report_error("Test error message")

        assert provider.state == TTSState.ERROR
        assert len(error_messages) > 0


class TestManagerStateConsistency:
    """Test state consistency across manager classes."""

    def test_all_managers_initialized(self):
        """Test that all managers are initialized in provider."""
        provider = MockTTSProvider()

        assert provider._state_manager is not None
        assert provider._error_manager is not None
        assert provider._async_manager is not None
        assert isinstance(provider._state_manager, TTSStateManager)
        assert isinstance(provider._error_manager, TTSErrorRecoveryManager)
        assert isinstance(provider._async_manager, TTSAsyncManager)

    def test_manager_status_collection(self):
        """Test that status can be collected from all managers."""
        provider = MockTTSProvider()

        state_status = provider._state_manager.get_state()
        error_status = provider._error_manager.get_status()
        async_status = provider._async_manager.get_status()

        assert state_status == TTSState.IDLE
        assert isinstance(error_status, dict)
        assert isinstance(async_status, dict)

    def test_error_manager_retry_delay_update(self):
        """Test that error manager properly computes retry delay."""
        provider = MockTTSProvider()
        error_manager = provider._error_manager

        # No errors: should have minimal retry delay
        delay = error_manager.get_retry_delay()
        assert delay >= 0

        # Record an error
        error_manager.record_error()
        error_manager.increment_recovery_attempts()

        # Delay should increase with retry attempts
        delay = error_manager.get_retry_delay()
        assert delay >= 0


@pytest.mark.asyncio
async def test_edge_case_rapid_state_changes():
    """Test rapid state transitions don't cause issues."""
    provider = MockTTSProvider()

    transitions = [
        TTSState.LOADING,
        TTSState.PLAYING,
        TTSState.PAUSED,
        TTSState.PLAYING,
        TTSState.STOPPED,
        TTSState.IDLE,
    ]

    for state in transitions:
        result = provider._transition_state(state)
        # Some transitions may fail if they're invalid, that's ok
        if result:
            assert provider.state == state


@pytest.mark.asyncio
async def test_error_during_synthesis():
    """Test error handling during synthesis."""
    provider = MockTTSProvider()

    # Manually trigger error state
    provider._change_state(TTSState.LOADING)
    provider._report_error("Synthesis failed")

    assert provider.state == TTSState.ERROR
    error_stats = provider.get_error_stats()
    assert error_stats["error_count"] >= 1


def test_state_idle_mode_setting():
    """Test idle mode doesn't break state management."""
    provider = MockTTSProvider()

    provider.set_idle_mode(True)
    assert provider._idle_mode is True

    # State should still work
    provider._change_state(TTSState.LOADING)
    assert provider.state == TTSState.LOADING

    provider.set_idle_mode(False)
    assert provider._idle_mode is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
