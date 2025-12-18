#!/usr/bin/env python3
"""
Test script for the unified TTS error handler.
"""

from speakub.tts.ui.error_handler import (
    TTSRunnerErrorHandler,
    TTSErrorType,
    TTSErrorSeverity,
    TTSErrorAction,
    TTSRunnerError,
    handle_runner_error
)
import asyncio
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))


class MockApp:
    """Mock app for testing."""

    def __init__(self):
        self.notifications = []
        self.tts_status = "IDLE"

    def notify(self, message, title="", severity="info"):
        self.notifications.append({
            "message": message,
            "title": title,
            "severity": severity
        })

    def set_tts_status(self, status):
        self.tts_status = status


class MockTTSIntegration:
    """Mock TTS integration for testing."""

    def __init__(self):
        self.app = MockApp()
        self.lock = Mock()
        self.lock.__enter__ = Mock(return_value=None)
        self.lock.__exit__ = Mock(return_value=None)

    async def set_tts_status_safe(self, status):
        self.app.set_tts_status(status)


async def test_error_classification():
    """Test error classification logic."""
    print("Testing error classification...")

    handler = TTSRunnerErrorHandler()

    # Test MemoryError classification
    error = MemoryError("Out of memory")
    runner_error = handler._classify_error(error, "test_context")

    assert runner_error.error_type == TTSErrorType.MEMORY
    assert runner_error.severity == TTSErrorSeverity.CRITICAL
    assert not runner_error.recoverable
    print("✓ MemoryError classification")

    # Test network error classification
    error = ConnectionError("Connection refused")
    runner_error = handler._classify_error(error, "test_context")

    assert runner_error.error_type == TTSErrorType.NETWORK
    assert runner_error.severity in [
        TTSErrorSeverity.MEDIUM, TTSErrorSeverity.HIGH]
    print("✓ Network error classification")

    # Test timeout error classification
    error = asyncio.TimeoutError("Operation timed out")
    runner_error = handler._classify_error(error, "test_context")

    print(
        f"Debug: TimeoutError type={runner_error.error_type}, severity={runner_error.severity}, recoverable={runner_error.recoverable}")
    assert runner_error.error_type == TTSErrorType.TIMEOUT
    assert runner_error.severity == TTSErrorSeverity.HIGH
    assert runner_error.recoverable
    print("✓ Timeout error classification")

    # Test TTS-specific error classification
    class MockTTSError(Exception):
        pass

    # Mock a TTS-related class name
    error = MockTTSError("TTS synthesis failed")
    error.__class__.__name__ = "TTSSynthesisError"
    runner_error = handler._classify_error(error, "test_context")

    assert runner_error.error_type == TTSErrorType.TTS_SYNTHESIS
    assert runner_error.severity == TTSErrorSeverity.HIGH
    assert runner_error.recoverable
    print("✓ TTS-specific error classification")


async def test_action_determination():
    """Test action determination logic."""
    print("\nTesting action determination...")

    handler = TTSRunnerErrorHandler()

    # Test critical error -> STOP action
    from speakub.tts.ui.error_handler import TTSRunnerError
    critical_error = TTSRunnerError(
        MemoryError("Critical error"),
        TTSErrorType.MEMORY,
        TTSErrorSeverity.CRITICAL,
        "test",
        recoverable=False
    )

    action = handler._determine_action(critical_error)
    assert action == TTSErrorAction.STOP
    print("✓ Critical error -> STOP action")

    # Test recoverable network error -> RETRY action
    network_error = TTSRunnerError(
        ConnectionError("Network error"),
        TTSErrorType.NETWORK,
        TTSErrorSeverity.MEDIUM,
        "test",
        recoverable=True
    )

    action = handler._determine_action(network_error)
    assert action == TTSErrorAction.RETRY
    print("✓ Network error -> RETRY action")

    # Test too many network errors -> PAUSE action
    handler._error_counts[TTSErrorType.NETWORK] = 10
    recent_errors = [network_error] * 6  # More than 5 recent network errors
    handler._recent_errors = recent_errors

    action = handler._determine_action(network_error)
    assert action == TTSErrorAction.PAUSE
    print("✓ Too many network errors -> PAUSE action")


async def test_error_handling_integration():
    """Test the complete error handling flow."""
    print("\nTesting complete error handling flow...")

    # Test with MemoryError
    tts_integration = MockTTSIntegration()

    try:
        raise MemoryError("Test memory error")
    except Exception as e:
        action = await handle_runner_error(
            e,
            "test_memory_error",
            tts_integration
        )

        assert action == TTSErrorAction.STOP
        assert tts_integration.app.tts_status == "STOPPED"
        assert len(tts_integration.app.notifications) > 0
        print("✓ MemoryError handling")

    # Reset for next test
    tts_integration.app.notifications.clear()

    # Test with network error
    try:
        raise ConnectionError("Test connection error")
    except Exception as e:
        action = await handle_runner_error(
            e,
            "test_network_error",
            tts_integration
        )

        assert action == TTSErrorAction.RETRY
        assert len(tts_integration.app.notifications) > 0
        print("✓ NetworkError handling")


async def test_error_statistics():
    """Test error statistics tracking."""
    print("\nTesting error statistics...")

    handler = TTSRunnerErrorHandler()

    # Add some errors
    memory_error = TTSRunnerError(
        MemoryError(
            "test"), TTSErrorType.MEMORY, TTSErrorSeverity.CRITICAL, "test"
    )
    network_error = TTSRunnerError(
        ConnectionError(
            "test"), TTSErrorType.NETWORK, TTSErrorSeverity.MEDIUM, "test"
    )

    handler._update_error_stats(memory_error)
    handler._update_error_stats(network_error)
    handler._update_error_stats(network_error)  # Add another network error

    stats = handler.get_error_stats()

    assert stats["error_counts"]["memory"] == 1
    assert stats["error_counts"]["network"] == 2
    assert stats["recent_errors_count"] == 3
    print("✓ Error statistics tracking")


async def main():
    """Run all tests."""
    print("SpeakUB Unified TTS Error Handler Test")
    print("=" * 50)

    try:
        await test_error_classification()
        await test_action_determination()
        await test_error_handling_integration()
        await test_error_statistics()

        print("\n" + "=" * 50)
        print("✅ All unified error handler tests passed!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
