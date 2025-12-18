#!/usr/bin/env python3
"""
Test script to verify predictive mode fix works correctly.
Tests the mode lock mechanism to ensure dual activation is prevented.
"""

import asyncio
import time
from unittest.mock import Mock, patch

from speakub.tts.playlist_manager import PlaylistManager


class TestAppInterface:
    """Test implementation of AppInterface."""

    def __init__(self):
        self.tts_status = "IDLE"
        self.tts_engine = None
        self.tts_smooth_mode = True
        self.tts_volume = 100
        self.tts_rate = 0
        self.tts_pitch = "+0Hz"
        self.notify = Mock()


class TestTTSIntegration:
    """Test TTS integration."""

    def __init__(self):
        self.app = TestAppInterface()
        self.tts_stop_requested = Mock()
        self.tts_stop_requested.is_set = Mock(return_value=False)
        self.tts_lock = Mock()
        self.tts_lock.__enter__ = Mock(return_value=None)
        self.tts_lock.__exit__ = Mock(return_value=None)


def test_mode_lock_functionality():
    """Test that mode lock prevents dual activation."""
    print("=" * 60)
    print("Testing Predictive Mode Dual Activation Fix")
    print("=" * 60)

    # Create test instances
    integration = TestTTSIntegration()
    manager = PlaylistManager(integration)

    print(f"Initial active mode: {manager._active_mode}")
    assert manager._active_mode is None, "Initial mode should be None"

    async def run_test():
        try:
            # Mock configuration for predictive mode
            with patch('speakub.utils.config.ConfigManager.get') as mock_get:
                mock_get.side_effect = lambda key, default=None: {
                    "tts.preloading_mode": "predictive",
                    "tts.preferred_engine": "edge-tts",
                    "tts.batch_size": 5,
                    "tts.max_queue_size": 20,
                    "tts.dynamic_batch_adjustment": True,
                    "tts.batch_adjustment_window": 10
                }.get(key, default)

                # Mock predictive controller
                call_count = 0

                async def mock_start_monitoring():
                    nonlocal call_count
                    call_count += 1
                    return None

                manager._predictive_controller.start_monitoring = mock_start_monitoring

                print("\n🔄 Test 1: First start_batch_preload() call")
                print(f"Before call - Active mode: {manager._active_mode}")
                print(f"Before call - call_count: {call_count}")

                # First call - should activate predictive mode
                await manager.start_batch_preload()

                print(f"After call - Active mode: {manager._active_mode}")
                print(f"After call - call_count: {call_count}")

                assert manager._active_mode == "predictive", "Should activate predictive mode"
                assert call_count == 1, "Should call controller start once"

                print(
                    "\n🔄 Test 2: Second start_batch_preload() call (should be blocked)")
                print(f"Before call - Active mode: {manager._active_mode}")
                print(f"Before call - call_count: {call_count}")

                # Second call - should be blocked by mode lock
                await manager.start_batch_preload()

                print(f"After call - Active mode: {manager._active_mode}")
                print(f"After call - call_count: {call_count}")

                assert manager._active_mode == "predictive", "Mode should remain predictive"
                assert call_count == 1, "Should NOT call controller start again"

                print("\n✅ Test 3: Reset functionality")
                print(f"Before reset - Active mode: {manager._active_mode}")

                # Test reset functionality
                manager.reset()

                print(f"After reset - Active mode: {manager._active_mode}")
                assert manager._active_mode is None, "Mode should be reset to None"

                print("\n✅ Test 4: Verify reset allows new activation")
                print(f"Before call - Active mode: {manager._active_mode}")

                # Should allow new activation after reset
                await manager.start_batch_preload()

                print(f"After call - Active mode: {manager._active_mode}")
                assert manager._active_mode == "predictive", "Should activate again after reset"
                assert call_count == 2, "Should call controller after reset"

                print("\n" + "=" * 60)
                print("🎉 ALL TESTS PASSED - Predictive Mode Fix Working!")
                print("=" * 60)
                print("\nSummary:")
                print("✅ Mode lock prevents dual activation")
                print("✅ Subsequent calls are properly blocked")
                print("✅ Reset allows proper reactivation")
                print("✅ Original 'massive content scan' bug should be fixed")

        except Exception as e:
            print(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False

        return True

    # Run the test
    result = asyncio.run(run_test())
    return result


if __name__ == "__main__":
    success = test_mode_lock_functionality()
    exit(0 if success else 1)
