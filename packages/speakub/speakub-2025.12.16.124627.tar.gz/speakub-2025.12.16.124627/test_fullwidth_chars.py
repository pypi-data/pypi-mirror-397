#!/usr/bin/env python3
"""
Test full-width Latin characters to see if they are considered speakable.
"""

from speakub.utils.text_utils import is_speakable_content
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

# Test cases with full-width characters
TEST_CASES = [
    "Ｙｅｓ",  # Full-width Latin
    "Ｎｏ",    # Full-width Latin
    "Ｙ",     # Single full-width Y
    "Ｎ",     # Single full-width N
    "ＡＢＣ",  # Full-width alphabet
    "Ｙｅｓ或Ｎｏ",  # Mixed full-width and Chinese
    "Yes",   # Regular ASCII
    "NO",    # Regular ASCII
]


def test_fullwidth_characters():
    """Test full-width character filtering."""
    print("Testing Full-Width Character Filtering")
    print("=" * 50)
    print()

    for i, test_text in enumerate(TEST_CASES, 1):
        print(f"Test Case {i}: '{test_text}'")
        print("-" * 30)

        # Check Unicode codepoints
        codepoints = [f"U+{ord(c):04X}" for c in test_text]
        print(f"Unicode codepoints: {codepoints}")

        # Check speakable
        speakable, reason = is_speakable_content(test_text)
        print(f"Speakable: {speakable} (reason: {reason})")

        if not speakable:
            print("❌ THIS WOULD BE FILTERED OUT!")
            print("This is likely the root cause of the issue!")
        else:
            print("✅ This would be processed normally")

        print()


def analyze_regex_pattern():
    """Analyze the current regex pattern."""
    print("Analyzing Current Regex Pattern")
    print("=" * 30)

    # Current pattern from text_utils.py
    current_pattern = r"[a-zA-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]+"

    print(f"Current pattern: {current_pattern}")
    print()
    print("Pattern breakdown:")
    print("- a-zA-Z0-9: ASCII letters and numbers")
    print("- \\u4e00-\\u9fff: Chinese characters")
    print("- \\u3040-\\u309f: Hiragana (Japanese)")
    print("- \\u30a0-\\u30ff: Katakana (Japanese)")
    print("- \\uac00-\\ud7af: Korean characters")
    print()
    print("MISSING: Full-width Latin characters (U+FF00-U+FFEF)")
    print("This is why full-width English text gets filtered!")


def main():
    """Main function."""
    analyze_regex_pattern()
    print()
    test_fullwidth_characters()

    print("=" * 50)
    print("CONCLUSION:")
    print("- Full-width Latin characters (Ｙｅｓ, Ｎｏ) are NOT matched by the current regex")
    print("- This causes mixed Chinese-English text with full-width chars to be filtered")
    print("- Regular ASCII English works fine")
    print("- Need to add \\uff00-\\uffef to the regex pattern")


if __name__ == "__main__":
    main()
