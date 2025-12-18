"""
Test for MPV Backend resource fixes.
"""
import tempfile
import unittest.mock as mock

from speakub.tts.backends.mpv_backend import MPVBackend


class TestMPVResourceFix:
    """Test MPV Backend resource management fixes."""

    def test_temp_file_cleanup_on_play_failure(self):
        """Test that temporary files are cleaned up even if play fails."""
        with mock.patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with mock.patch('mpv.MPV', create=True):
                backend = MPVBackend()

                # Mock _start_playback to raise an exception
                backend._start_playback = mock.Mock(
                    side_effect=RuntimeError("Play failed"))
                backend._wait_for_completion = mock.Mock()

                with mock.patch('os.unlink') as mock_unlink:
                    try:
                        backend.play(b"fake audio data")
                    except RuntimeError:
                        pass  # Expected

                    # Verify cleanup was called despite play failure
                    mock_unlink.assert_called_once()

                backend.cleanup()

    def test_successful_play_cleanup(self):
        """Test that temporary files are cleaned up on successful play."""
        with mock.patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with mock.patch('mpv.MPV', create=True):
                backend = MPVBackend()

                # Mock successful play
                backend._start_playback = mock.Mock()
                backend._wait_for_completion = mock.Mock()

                with mock.patch('os.unlink') as mock_unlink:
                    backend.play(b"fake audio data")
                    mock_unlink.assert_called_once()

                backend.cleanup()

    def test_async_circuit_breaker_works(self):
        """Test that async circuit breaker works correctly."""
        import asyncio
        import pytest
        from speakub.tts.integration import CircuitBreaker

        async def run_test():
            breaker = CircuitBreaker(failure_threshold=2)

            # Test success
            await breaker.call_async(asyncio.sleep, 0.001)
            assert breaker._failure_count == 0

            # Test failure that trips circuit
            with pytest.raises(RuntimeError):
                await breaker.call_async(lambda: (_ for _ in ()).throw(RuntimeError('test')))
                await breaker.call_async(lambda: (_ for _ in ()).throw(RuntimeError('test')))

            # Circuit should be open now
            assert breaker.state.value == "open"

        asyncio.run(run_test())
