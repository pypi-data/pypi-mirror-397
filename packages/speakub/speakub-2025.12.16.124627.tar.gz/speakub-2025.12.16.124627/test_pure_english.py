#!/usr/bin/env python3
"""
Test pure English content to see if it gets filtered.
"""

from speakub.utils.text_utils import is_speakable_content, clean_text_for_tts
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Test cases - pure English content
TEST_CASES = [
    "Yes or No",
    "YES OR NO",
    "yes or no",
    "Hello world!",
    "Full English text without any Chinese characters at all.",
    "YES",  # Just YES
    "NO",   # Just NO
    "Y",    # Single letter
    "N",    # Single letter
]


def test_pure_english():
    """Test pure English content filtering."""
    print("Testing Pure English Content Filtering")
    print("=" * 50)
    print()

    for i, test_text in enumerate(TEST_CASES, 1):
        print(f"Test Case {i}: '{test_text}'")
        print("-" * 30)

        # Check speakable
        speakable, reason = is_speakable_content(test_text)
        print(f"Speakable: {speakable} (reason: {reason})")

        if not speakable:
            print("❌ THIS WOULD BE FILTERED OUT!")
        else:
            print("✅ This would be processed normally")

            # Show cleaning
            cleaned = clean_text_for_tts(test_text)
            if cleaned != test_text:
                print(f"Cleaned: '{cleaned}'")

        print()


def main():
    """Main function."""
    test_pure_english()

    print("=" * 50)
    print("Analysis:")
    print("- If pure English text gets filtered, that's the issue")
    print("- If it passes filtering, then Edge-TTS handles it correctly")


if __name__ == "__main__":
    main()
