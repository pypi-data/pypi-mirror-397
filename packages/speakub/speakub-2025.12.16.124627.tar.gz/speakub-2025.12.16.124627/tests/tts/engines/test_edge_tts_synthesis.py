#!/usr/bin/env python3
"""
Test script for Edge-TTS synthesis in SpeakUB.
Tests synthesis of Chinese text to verify Edge-TTS functionality.
"""

from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test text
TEST_TEXT = "就交gěi你選擇了。"


async def test_edge_tts_synthesis():
    """Test Edge-TTS synthesis with the specified text."""
    print(f"Testing Edge-TTS synthesis with text: {TEST_TEXT}")
    print("=" * 60)

    try:
        # Initialize EdgeTTSProvider
        print("Initializing EdgeTTSProvider...")
        provider = EdgeTTSProvider()
        print("✓ EdgeTTSProvider initialized successfully")

        # Get available voices (optional verification)
        print("Fetching available voices...")
        voices = await provider.get_available_voices()
        print(f"✓ Found {len(voices)} available voices")

        # List Chinese voices
        chinese_voices = [v for v in voices if v.get(
            'locale', '').startswith('zh-')]
        print(f"✓ Found {len(chinese_voices)} Chinese voices:")
        for v in chinese_voices[:10]:  # Show first 10
            short_name = v.get('short_name', 'Unknown')
            display_name = v.get('display_name', 'Unknown')
            print(f"  - {short_name}: {display_name}")
        if len(chinese_voices) > 10:
            print(f"  ... and {len(chinese_voices) - 10} more")

        # Set voice to Chinese (Mainland China)
        voice = "zh-CN-XiaochenMultilingualNeural"
        voice_exists = any(v.get('short_name') == voice for v in voices)
        if not voice_exists:
            print(f"⚠ Warning: Voice '{voice}' not found in available voices")
            # Fallback to a known Chinese voice
            fallback_voice = "zh-CN-XiaoxiaoNeural"
            print(f"  Using fallback voice: {fallback_voice}")
            voice = fallback_voice

        provider.set_voice(voice)
        print(f"✓ Set voice to: {voice}")

        # Perform synthesis
        print("Starting synthesis...")
        audio_data = await provider.synthesize(TEST_TEXT, voice=voice)

        # Check results
        if audio_data and len(audio_data) > 0:
            print("✓ Synthesis successful!")
            print(f"  - Audio data size: {len(audio_data)} bytes")
            print(f"  - Text length: {len(TEST_TEXT)} characters")

            # Optional: Save audio file for manual verification
            output_file = Path("test_edge_tts_output.mp3")
            with open(output_file, "wb") as f:
                f.write(audio_data)
            print(f"✓ Audio saved to: {output_file}")

            return True
        else:
            print("✗ Synthesis failed: No audio data generated")
            return False

    except Exception as e:
        print(f"✗ Synthesis failed with error: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("SpeakUB Edge-TTS Synthesis Test")
    print("===============================")
    print()

    success = await test_edge_tts_synthesis()

    print()
    print("=" * 60)
    if success:
        print("TEST RESULT: PASSED ✓")
        print("Edge-TTS synthesis is working correctly.")
    else:
        print("TEST RESULT: FAILED ✗")
        print("Edge-TTS synthesis encountered issues.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
