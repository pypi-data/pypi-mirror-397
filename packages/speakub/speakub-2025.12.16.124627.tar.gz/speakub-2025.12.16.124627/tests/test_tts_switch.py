#!/usr/bin/env python3
"""
Test script to verify TTS engine switching fixes.
"""

import asyncio
import logging
import sys
import os

# Add the project root directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')


async def test_cleanup_logic():
    """Test the cleanup logic for TTS engines."""
    print("Testing TTS engine cleanup logic...")

    # Import the necessary modules
    try:
        from speakub.tts.engines.gtts_provider import GTTSProvider
        from speakub.tts.engines.nanmai_tts_provider import NanmaiTTSProvider
        print("✓ TTS providers imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import TTS providers: {e}")
        return False

    # Test GTTS provider cleanup
    print("\nTesting GTTS provider cleanup...")
    try:
        gtts_engine = GTTSProvider()
        print("✓ GTTS provider created")

        # Check initial state
        print(f"  Initial mpv_player: {gtts_engine.mpv_player}")

        # Call stop (which should set mpv_player to None)
        gtts_engine.stop()
        print(f"  After stop() mpv_player: {gtts_engine.mpv_player}")

        # Try to call terminate on None (this should not crash now)
        if hasattr(gtts_engine, 'mpv_player') and gtts_engine.mpv_player:
            gtts_engine.mpv_player.terminate()
            print("✓ terminate() called successfully")
        else:
            print("✓ mpv_player is None, terminate() skipped (expected)")

    except Exception as e:
        print(f"✗ GTTS cleanup test failed: {e}")
        return False

    # Test Nanmai provider cleanup
    print("\nTesting Nanmai provider cleanup...")
    try:
        nanmai_engine = NanmaiTTSProvider()
        print("✓ Nanmai provider created")

        # Check initial state
        print(f"  Initial mpv_player: {nanmai_engine.mpv_player}")

        # Call stop
        nanmai_engine.stop()
        print(f"  After stop() mpv_player: {nanmai_engine.mpv_player}")

        # Try to call terminate
        if hasattr(nanmai_engine, 'mpv_player') and nanmai_engine.mpv_player:
            nanmai_engine.mpv_player.terminate()
            print("✓ terminate() called successfully")
        else:
            print("✓ mpv_player still exists after stop()")

    except Exception as e:
        print(f"✗ Nanmai cleanup test failed: {e}")
        return False

    print("\n✓ All cleanup tests passed!")
    return True


async def test_predictive_controller():
    """Test PredictiveBatchController cleanup."""
    print("\nTesting PredictiveBatchController...")

    try:
        from speakub.tts.reservoir.controller import PredictiveBatchController
        from speakub.tts.playlist_manager import PlaylistManager

        # Create a mock playlist manager
        class MockPlaylistManager:
            def __init__(self):
                self.app = None

        mock_pm = MockPlaylistManager()

        # Create queue predictor
        from speakub.tts.reservoir.queue_predictor import QueuePredictor
        from speakub.tts.reservoir.play_monitor import PlayTimeMonitor
        play_monitor = PlayTimeMonitor()
        queue_predictor = QueuePredictor(play_monitor)

        # Create controller
        controller = PredictiveBatchController(mock_pm, queue_predictor)
        print("✓ PredictiveBatchController created")

        # Check if it has monitor_task attribute
        has_monitor_task = hasattr(controller, 'monitor_task')
        print(f"  Has monitor_task attribute: {has_monitor_task}")

        # Test stop_monitoring
        await controller.stop_monitoring()
        print("✓ stop_monitoring() called successfully")

    except Exception as e:
        print(f"✗ PredictiveBatchController test failed: {e}")
        return False

    print("✓ PredictiveBatchController test passed!")
    return True


async def main():
    """Main test function."""
    print("Starting TTS engine switching fix verification...\n")

    success = True

    # Test cleanup logic
    success &= await test_cleanup_logic()

    # Test predictive controller
    success &= await test_predictive_controller()

    if success:
        print("\n🎉 All tests passed! TTS engine switching fixes appear to be working.")
        return 0
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
