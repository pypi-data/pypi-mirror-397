#!/usr/bin/env python3
"""
Test script for Edge-TTS synthesis of specific content.
Tests synthesis of three text samples to verify Edge-TTS functionality.
"""

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

# Test texts
TEST_TEXTS = [
    "『……王？』",
    "『嚇……！』",
    "「嗚……」"
]


async def test_edge_tts_content():
    """Test Edge-TTS synthesis with the specified texts."""
    print("Testing Edge-TTS synthesis with specific content")
    print("=" * 60)

    try:
        # Initialize EdgeTTSProvider
        print("Initializing EdgeTTSProvider...")
        provider = EdgeTTSProvider()
        print("✓ EdgeTTSProvider initialized successfully")

        # Set voice to Chinese (Taiwan) - likely appropriate for the content
        voice = "zh-TW-HsiaoChenNeural"
        provider.set_voice(voice)
        print(f"✓ Set voice to: {voice}")

        results = []

        for i, text in enumerate(TEST_TEXTS, 1):
            print(f"\n--- Testing Text {i}: {text} ---")
            try:
                # Perform synthesis
                print("Starting synthesis...")
                audio_data = await provider.synthesize(text, voice=voice)

                # Check results
                if audio_data and len(audio_data) > 0:
                    print("✓ Synthesis successful!")
                    print(f"  - Audio data size: {len(audio_data)} bytes")
                    print(f"  - Text length: {len(text)} characters")

                    # Save audio file for verification
                    output_file = Path(f"test_content_{i}.mp3")
                    with open(output_file, "wb") as f:
                        f.write(audio_data)
                    print(f"✓ Audio saved to: {output_file}")

                    results.append((text, True, len(audio_data), None))
                else:
                    print("✗ Synthesis failed: No audio data generated")
                    results.append((text, False, 0, "No audio data"))

            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                print(f"✗ Synthesis failed with error: {error_msg}")
                results.append((text, False, 0, error_msg))

        return results

    except Exception as e:
        print(f"✗ Initialization failed with error: {e}")
        print(f"  Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return []


async def main():
    """Main test function."""
    print("SpeakUB Edge-TTS Content Test")
    print("=============================")
    print()

    results = await test_edge_tts_content()

    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("=" * 60)

    all_passed = True
    for i, (text, success, audio_size, error) in enumerate(results, 1):
        status = "PASSED ✓" if success else "FAILED ✗"
        print(f"Text {i}: {status}")
        print(f"  Content: {text}")
        if success:
            print(f"  Audio size: {audio_size} bytes")
        else:
            print(f"  Error: {error}")
        print()

        if not success:
            all_passed = False

    print("=" * 60)
    if all_passed:
        print("OVERALL RESULT: ALL TESTS PASSED ✓")
        print("All content can be correctly synthesized by Edge-TTS.")
    else:
        print("OVERALL RESULT: SOME TESTS FAILED ✗")
        print("Some content cannot be correctly synthesized by Edge-TTS.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
