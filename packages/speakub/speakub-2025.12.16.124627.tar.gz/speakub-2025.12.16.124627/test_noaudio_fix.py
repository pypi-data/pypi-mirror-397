#!/usr/bin/env python3
"""
Test the NoAudioReceived error handling fix.
"""

from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


async def test_noaudio_fix():
    """Test the NoAudioReceived error handling fix."""
    print("Testing NoAudioReceived Error Handling Fix")
    print("=" * 50)

    # Test case 1: Non-speakable content should return empty audio without error
    print("Test 1: Non-speakable content (punctuation only)")
    test_text = "『……！』"

    try:
        provider = EdgeTTSProvider()

        # Mock the Edge-TTS to raise NoAudioReceived
        with patch('edge_tts.Communicate') as mock_communicate:
            mock_instance = Mock()
            mock_communicate.return_value = mock_instance
            mock_instance.stream = Mock()

            # Import the actual exception
            from edge_tts.exceptions import NoAudioReceived
            mock_instance.stream.side_effect = NoAudioReceived(
                "No audio was received. Please verify that your parameters are correct.")

            # This should not raise an exception and should return empty bytes
            result = await provider.synthesize(test_text, "zh-CN-XiaochenMultilingualNeural")

            if result == b"":
                print(
                    "✅ SUCCESS: Non-speakable content returned empty audio without error")
            else:
                print(
                    f"❌ FAILED: Expected empty audio, got {len(result)} bytes")

    except Exception as e:
        print(f"❌ FAILED: Exception raised for non-speakable content: {e}")

    print()

    # Test case 2: Speakable content with NoAudioReceived should still raise error
    print("Test 2: Speakable content with NoAudioReceived (should raise error)")
    test_text = "Hello world"

    try:
        provider = EdgeTTSProvider()

        # Mock the Edge-TTS to raise NoAudioReceived
        with patch('edge_tts.Communicate') as mock_communicate:
            mock_instance = Mock()
            mock_communicate.return_value = mock_instance
            mock_instance.stream = Mock()

            # Import the actual exception
            from edge_tts.exceptions import NoAudioReceived
            mock_instance.stream.side_effect = NoAudioReceived(
                "No audio was received. Please verify that your parameters are correct.")

            # This should raise an exception
            result = await provider.synthesize(test_text, "zh-CN-XiaochenMultilingualNeural")
            print(
                f"❌ FAILED: Expected exception, but got result: {len(result)} bytes")

    except RuntimeError as e:
        if "No audio received for speakable content" in str(e):
            print(
                "✅ SUCCESS: Speakable content with NoAudioReceived properly raised error")
        else:
            print(f"❌ FAILED: Wrong error message: {e}")
    except Exception as e:
        print(f"❌ FAILED: Unexpected exception: {e}")

    print()


def main():
    """Main function."""
    print("SpeakUB NoAudioReceived Error Handling Fix Test")
    print("=" * 50)
    print()

    # Run the async test
    asyncio.run(test_noaudio_fix())

    print("=" * 50)
    print("Test Summary:")
    print("- Non-speakable content (punctuation) should return empty audio")
    print("- Speakable content with NoAudioReceived should raise error")
    print("- This prevents ERROR logs for expected Edge-TTS behavior")


if __name__ == "__main__":
    main()
