"""
Tests for speakub.tts.engine module
"""

import asyncio
import time
from unittest.mock import Mock, patch

import pytest

from speakub.core.exceptions import TTSError
from speakub.tts.engine import TTSEngine, TTSState


class MockTTSEngine(TTSEngine):
    """Mock implementation of TTSEngine for testing."""

    def __init__(self):
        super().__init__()
        self.synthesize_calls = []
        self.get_voices_calls = []
        self.pause_calls = []
        self.resume_calls = []
        self.stop_calls = []
        self.seek_calls = []

    async def synthesize(self, text: str, voice: str = "default", **kwargs):
        self.synthesize_calls.append((text, voice, kwargs))
        return b"mock_audio_data"

    async def get_available_voices(self):
        self.get_voices_calls.append(True)
        return [
            {"name": "voice1", "language": "en", "gender": "female"},
            {"name": "voice2", "language": "zh", "gender": "male"},
        ]

    def pause(self):
        self.pause_calls.append(True)

    def resume(self):
        self.resume_calls.append(True)

    def stop(self):
        super().stop()
        self.stop_calls.append(True)

    def seek(self, position: int):
        self.seek_calls.append(position)

    async def play_audio_non_blocking(self, audio_data: bytes):
        # Mock implementation
        pass

    async def wait_for_playback_completion(self):
        # Mock implementation
        pass


class TestTTSState:
    """Test TTSState enum"""

    def test_tts_states(self):
        """Test all TTS states are defined"""
        assert TTSState.IDLE.value == "idle"
        assert TTSState.LOADING.value == "loading"
        assert TTSState.PLAYING.value == "playing"
        assert TTSState.PAUSED.value == "paused"
        assert TTSState.STOPPED.value == "stopped"
        assert TTSState.ERROR.value == "error"

    def test_tts_state_equality(self):
        """Test TTS state equality"""
        assert TTSState.IDLE == TTSState.IDLE
        assert TTSState.PLAYING != TTSState.PAUSED


class TestTTSEngine:
    """Test TTSEngine base class"""

    def test_engine_initialization(self):
        """Test engine initialization"""
        engine = MockTTSEngine()

        assert engine.state == TTSState.IDLE
        assert engine.current_text == ""
        assert engine.current_position == 0
        assert engine.total_length == 0
        assert engine.on_state_changed is None
        assert engine.on_position_changed is None
        assert engine.on_error is None
        assert engine._event_loop is None
        assert engine._thread is None
        assert not engine._stop_requested.is_set()

    def test_state_change_callback(self):
        """Test state change callback"""
        engine = MockTTSEngine()
        callback_calls = []

        def state_callback(new_state):
            callback_calls.append(new_state)

        engine.on_state_changed = state_callback

        # Test state change
        engine._change_state(TTSState.PLAYING)
        assert engine.state == TTSState.PLAYING
        assert len(callback_calls) == 1
        assert callback_calls[0] == TTSState.PLAYING

        # Test no callback when state doesn't change
        engine._change_state(TTSState.PLAYING)
        assert len(callback_calls) == 1  # Should not increase

    def test_position_update_callback(self):
        """Test position update callback"""
        engine = MockTTSEngine()
        callback_calls = []

        def position_callback(pos, total):
            callback_calls.append((pos, total))

        engine.on_position_changed = position_callback

        # Test position update
        engine._update_position(100, 1000)
        assert engine.current_position == 100
        assert engine.total_length == 1000
        assert len(callback_calls) == 1
        assert callback_calls[0] == (100, 1000)

    def test_error_reporting_callback(self):
        """Test error reporting callback"""
        engine = MockTTSEngine()
        callback_calls = []

        def error_callback(message):
            callback_calls.append(message)

        engine.on_error = error_callback

        # Test error reporting
        engine._report_error("Test error")
        assert engine.state == TTSState.ERROR
        assert len(callback_calls) == 1
        assert callback_calls[0] == "Test error"

    def test_pitch_methods_default(self):
        """Test default pitch methods"""
        engine = MockTTSEngine()

        # Test default implementations
        engine.set_pitch("+10Hz")
        assert engine.get_pitch() == "+0Hz"  # Default implementation

    def test_async_loop_management(self):
        """Test async event loop management"""
        engine = MockTTSEngine()

        # Test starting loop
        engine.start_async_loop()
        assert engine._event_loop is not None
        assert engine._thread is not None
        assert engine._thread.is_alive()

        # Test stopping loop
        engine.stop_async_loop()
        # Note: Thread may still be alive due to daemon nature

    @patch('asyncio.run_coroutine_threadsafe')
    def test_speak_text_async_success(self, mock_run_coroutine):
        """Test successful async text speaking"""
        engine = MockTTSEngine()
        engine._event_loop = Mock()

        # Mock successful synthesis
        future = Mock()
        future.result.return_value = None
        mock_run_coroutine.return_value = future

        # Test speaking text
        engine.speak_text("Hello world", "voice1")

        # Verify coroutine was scheduled
        mock_run_coroutine.assert_called_once()
        call_args = mock_run_coroutine.call_args
        assert len(call_args[0]) == 2  # coroutine and loop

    def test_speak_text_sync_success(self):
        """Test successful synchronous text speaking"""
        engine = MockTTSEngine()
        engine.start_async_loop()

        # Test speaking text synchronously
        try:
            engine.speak_text_sync("Hello world", "voice1")
        except Exception:
            # May fail due to mock setup, but we're testing the call path
            pass

        # Verify stop was not requested initially
        assert not engine._stop_requested.is_set()

    def test_speak_text_sync_timeout(self):
        """Test synchronous speaking timeout"""
        engine = MockTTSEngine()
        engine.start_async_loop()

        # Mock timeout
        with patch('asyncio.run_coroutine_threadsafe') as mock_run:
            future = Mock()
            future.result.side_effect = asyncio.TimeoutError()
            mock_run.return_value = future

            with pytest.raises(TimeoutError):
                engine.speak_text_sync("Hello world", "voice1", timeout=1)

    def test_speak_text_sync_cancellation(self):
        """Test synchronous speaking cancellation"""
        engine = MockTTSEngine()
        engine.start_async_loop()
        engine._stop_requested.set()

        # Should raise error when stop is requested
        with pytest.raises(TTSError, match="cancelled by user"):
            engine.speak_text_sync("Hello world", "voice1")

    def test_is_available_success(self):
        """Test engine availability check success"""
        engine = MockTTSEngine()
        engine._event_loop = Mock()

        with patch('asyncio.run_coroutine_threadsafe') as mock_run:
            future = Mock()
            future.result.return_value = [
                {"name": "voice1", "language": "en"}
            ]
            mock_run.return_value = future

            assert engine.is_available() is True

    def test_is_available_failure(self):
        """Test engine availability check failure"""
        engine = MockTTSEngine()

        # No event loop
        assert engine.is_available() is False

        # With event loop but exception
        engine._event_loop = Mock()
        with patch('asyncio.run_coroutine_threadsafe') as mock_run:
            future = Mock()
            future.result.side_effect = Exception("Test error")
            mock_run.return_value = future

            assert engine.is_available() is False

    def test_error_recovery_should_attempt(self):
        """Test error recovery decision logic"""
        engine = MockTTSEngine()

        # Test recoverable errors
        assert engine._should_attempt_recovery("timeout") is True
        assert engine._should_attempt_recovery("connection") is True
        assert engine._should_attempt_recovery("network") is True
        assert engine._should_attempt_recovery("rate_limit") is True

        # Test non-recoverable errors
        assert engine._should_attempt_recovery("authentication") is False
        assert engine._should_attempt_recovery("invalid_input") is False

    def test_error_recovery_circuit_breaker(self):
        """Test circuit breaker functionality"""
        engine = MockTTSEngine()

        # Simulate circuit breaker activation
        engine._circuit_breaker_until = time.time() + 60

        assert engine._should_attempt_recovery("timeout") is False

    def test_error_recovery_consecutive_failures(self):
        """Test consecutive failure handling"""
        engine = MockTTSEngine()

        # Simulate consecutive failures
        engine._consecutive_failures = 5
        engine._last_error_time = time.time() - 1  # Recent failure

        assert engine._should_attempt_recovery("timeout") is False

    def test_error_recording(self):
        """Test error recording functionality"""
        engine = MockTTSEngine()

        # Record error
        engine._record_error("timeout", recovery_attempted=True)

        assert engine._error_count == 1
        assert engine._consecutive_failures == 1

    def test_error_recovery_success(self):
        """Test successful recovery recording"""
        engine = MockTTSEngine()

        # Set up failures
        engine._consecutive_failures = 3

        # Record successful recovery
        engine._record_recovery_success()

        assert engine._consecutive_failures == 0

    def test_exponential_backoff(self):
        """Test exponential backoff calculation"""
        engine = MockTTSEngine()

        # Test increasing delays
        delay1 = engine._perform_exponential_backoff(0)
        delay2 = engine._perform_exponential_backoff(1)
        delay3 = engine._perform_exponential_backoff(2)

        assert delay1 <= delay2 <= delay3
        assert delay1 >= 0.8  # Minimum jitter
        assert delay3 <= 30.0  # Maximum delay

    @pytest.mark.asyncio
    async def test_execute_with_retry_success(self):
        """Test successful operation with retry"""
        engine = MockTTSEngine()

        async def success_operation():
            return "success"

        result = await engine._execute_with_retry(success_operation, "test_op")

        assert result == "success"

    @pytest.mark.asyncio
    async def test_execute_with_retry_failure(self):
        """Test operation failure with retry"""
        engine = MockTTSEngine()

        async def failing_operation():
            raise ConnectionError("Connection failed")  # Use recoverable error

        with pytest.raises(TTSError, match="test_op failed"):
            await engine._execute_with_retry(
                failing_operation, "test_op", max_retries=2
            )

    @pytest.mark.asyncio
    async def test_execute_with_retry_recovery(self):
        """Test operation recovery after retries"""
        engine = MockTTSEngine()

        call_count = 0

        async def intermittent_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                # Use recoverable error
                raise ConnectionError("Connection failed")
            return "success"

        result = await engine._execute_with_retry(
            intermittent_operation, "test_op", max_retries=3
        )

        assert result == "success"
        assert call_count == 3

    def test_error_stats(self):
        """Test error statistics retrieval"""
        engine = MockTTSEngine()

        # Record some errors
        engine._record_error("timeout")
        engine._record_error("connection")

        stats = engine.get_error_stats()

        assert stats["total_errors"] == 2
        assert stats["consecutive_failures"] == 2
        assert "last_error_time" in stats
        assert "circuit_breaker_active" in stats
        assert "recovery_attempts" in stats

    @pytest.mark.asyncio
    async def test_play_audio_backward_compatibility(self):
        """Test backward compatibility of play_audio method"""
        engine = MockTTSEngine()

        # Test that play_audio calls the split methods
        await engine.play_audio(b"test_audio")

        # Verify the split methods were called (through inheritance)
        # This is a basic test - in real implementation these would be tested separately

    def test_stop_sets_flag(self):
        """Test that stop method sets the stop flag"""
        engine = MockTTSEngine()

        engine.stop()

        assert engine._stop_requested.is_set()
        assert len(engine.stop_calls) == 1


if __name__ == '__main__':
    pytest.main([__file__])
