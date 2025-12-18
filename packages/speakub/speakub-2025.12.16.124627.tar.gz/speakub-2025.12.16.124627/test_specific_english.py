#!/usr/bin/env python3
"""
Test the specific English line example that the user provided.
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

# The specific test case from the user
TEST_TEXT = "Ｙｅｓ或Ｎｏ，英文字母Ｙ和Ｎ在振宇眼前慢慢閃爍，彷彿在等待他的回答。"


async def test_specific_case():
    """Test the specific English line case."""
    print("Testing specific English line case")
    print("=" * 50)
    print(f"Test text: {TEST_TEXT}")
    print()

    # Test speakable content check
    print("1. Speakable content check:")
    speakable, reason = is_speakable_content(TEST_TEXT)
    print(f"   Speakable: {speakable} (reason: {reason})")
    print()

    if not speakable:
        print("❌ CONTENT WOULD BE FILTERED - This is the issue!")
        print("The text filtering logic considers this full English line as non-speakable.")
        return

    # Test text cleaning
    print("2. Text cleaning:")
    cleaned_text = clean_text_for_tts(TEST_TEXT)
    print(f"   Original: {TEST_TEXT}")
    print(f"   Cleaned:  {cleaned_text}")
    print()

    # Check speakable after cleaning
    speakable_after_clean, reason_after_clean = is_speakable_content(
        cleaned_text)
    print("3. Speakable after cleaning:")
    print(
        f"   Speakable: {speakable_after_clean} (reason: {reason_after_clean})")
    print()

    if not speakable_after_clean:
        print("❌ CONTENT WOULD BE FILTERED AFTER CLEANING - This is the issue!")
        print("The text gets modified during cleaning and then filtered out.")
        return

    # Try synthesis (but skip if network issues)
    print("4. TTS Synthesis test:")
    try:
        print("   Initializing EdgeTTSProvider...")
        provider = EdgeTTSProvider()

        # Check if required voice exists
        voices = await provider.get_available_voices()
        voice = "zh-CN-XiaochenMultilingualNeural"
        voice_exists = any(v.get('short_name') == voice for v in voices)

        if not voice_exists:
            print(f"   ❌ Voice '{voice}' not available")
            return

        provider.set_voice(voice)
        print(f"   ✓ Voice set to: {voice}")

        print("   Starting synthesis (this may take time)...")
        audio_data = await provider.synthesize(cleaned_text, voice=voice)

        if audio_data and len(audio_data) > 0:
            print("   ✅ Synthesis successful!")
            print(f"   Audio size: {len(audio_data)} bytes")

            # Save for verification
            output_file = Path("test_specific_english.mp3")
            with open(output_file, "wb") as f:
                f.write(audio_data)
            print(f"   ✓ Audio saved to: {output_file}")

        else:
            print("   ❌ Synthesis failed: No audio data")

    except Exception as e:
        print(f"   ❌ Synthesis error: {e}")
        print(f"   Error type: {type(e).__name__}")


async def main():
    """Main function."""
    print("SpeakUB Specific English Line Test")
    print("===================================")
    print()

    await test_specific_case()

    print()
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
