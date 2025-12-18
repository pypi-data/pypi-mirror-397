#!/usr/bin/env python3
"""
Test script to check if Edge-TTS has issues with synthesizing full English lines.
Specifically tests the example: "Ｙｅｓ或Ｎｏ，英文字母Ｙ和Ｎ在振宇眼前慢慢閃爍，彷彿在等待他的回答。"
"""

from speakub.utils.text_utils import is_speakable_content, clean_text_for_tts
from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
import asyncio
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Test cases for full English lines
TEST_CASES = [
    "Ｙｅｓ或Ｎｏ，英文字母Ｙ和Ｎ在振宇眼前慢慢閃爍，彷彿在等待他的回答。",
    "Yes or No, the English letters Y and N slowly flickered before Zhen Yu's eyes, as if waiting for his answer.",
    "YES OR NO",
    "yes or no",
    "Hello world!",
    "This is a full English sentence with Chinese characters mixed in: 你好世界",
    "Full English text without any Chinese characters at all.",
    "ＹＥＳ",  # Full-width English
    "YES",    # Regular English
    "ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ",  # Full-width alphabet
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",  # Regular alphabet
]


async def test_edge_tts_english_lines():
    """Test Edge-TTS synthesis with various English line examples."""
    print("SpeakUB Edge-TTS English Lines Synthesis Test")
    print("=" * 80)

    try:
        # Initialize EdgeTTSProvider
        print("Initializing EdgeTTSProvider...")
        provider = EdgeTTSProvider()
        print("✓ EdgeTTSProvider initialized successfully")

        # Get available voices
        print("Fetching available voices...")
        voices = await provider.get_available_voices()
        print(f"✓ Found {len(voices)} available voices")

        # Must use the specific voice as requested
        voice = "zh-CN-XiaochenMultilingualNeural"
        voice_exists = any(v.get('short_name') == voice for v in voices)
        if not voice_exists:
            print(
                f"✗ ERROR: Required voice '{voice}' not found in available voices")
            print(
                f"Available voices: {[v.get('short_name') for v in voices[:10]]}")
            return

        provider.set_voice(voice)
        print(f"✓ Set voice to: {voice}")
        print()

        # Test each case
        for i, test_text in enumerate(TEST_CASES, 1):
            print(f"Test Case {i}: {test_text}")
            print("-" * 60)

            # First check if content is considered speakable
            speakable, reason = is_speakable_content(test_text)
            print(f"Speakable check: {speakable} (reason: {reason})")

            if not speakable:
                print("⚠ SKIPPED: Content filtered as non-speakable")
                print()
                continue

            # Clean text for TTS
            cleaned_text = clean_text_for_tts(test_text)
            print(f"Cleaned text: '{cleaned_text}'")

            # Check speakable again after cleaning
            speakable_after_clean, reason_after_clean = is_speakable_content(
                cleaned_text)
            print(
                f"Speakable after clean: {speakable_after_clean} (reason: {reason_after_clean})")

            if not speakable_after_clean:
                print("⚠ SKIPPED: Content filtered as non-speakable after cleaning")
                print()
                continue

            # Attempt synthesis
            try:
                print("Starting synthesis...")
                audio_data = await provider.synthesize(cleaned_text, voice=voice)

                if audio_data and len(audio_data) > 0:
                    print("✓ Synthesis successful!")
                    print(f"  Audio data size: {len(audio_data)} bytes")
                    print(f"  Text length: {len(cleaned_text)} characters")

                    # Save audio file for verification
                    output_file = Path(f"test_english_{i}.mp3")
                    with open(output_file, "wb") as f:
                        f.write(audio_data)
                    print(f"✓ Audio saved to: {output_file}")

                else:
                    print("✗ Synthesis failed: No audio data generated")

            except Exception as e:
                print(f"✗ Synthesis failed with error: {e}")
                print(f"  Error type: {type(e).__name__}")

            print()

    except Exception as e:
        print(f"✗ Test setup failed with error: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("Testing Edge-TTS synthesis with full English lines")
    print("This tests whether full English text gets skipped or has synthesis errors")
    print()

    await test_edge_tts_english_lines()

    print("=" * 80)
    print("Test completed. Check the generated MP3 files to verify audio output.")


if __name__ == "__main__":
    asyncio.run(main())
