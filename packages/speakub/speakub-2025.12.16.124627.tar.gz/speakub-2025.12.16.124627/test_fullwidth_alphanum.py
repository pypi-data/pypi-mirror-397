#!/usr/bin/env python3
"""
Test full-width alphanumeric characters to ensure they are speakable.
"""

from speakub.utils.text_utils import is_speakable_content
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


def test_fullwidth_alphanumeric():
    """Test that full-width letters and numbers are considered speakable."""

    test_cases = [
        # Full-width letters
        ("Ｙｅｓ", True, "Full-width letters"),
        ("Ｎｏ", True, "Full-width letters"),
        ("ＡＢＣ", True, "Full-width uppercase"),
        ("ａｂｃ", True, "Full-width lowercase"),
        ("Ｈｅｌｌｏ", True, "Full-width mixed case"),

        # Full-width numbers
        ("１２３", True, "Full-width numbers"),
        ("９８７", True, "Full-width numbers"),
        ("０", True, "Full-width zero"),

        # Mixed full-width alphanumeric
        ("Ｙｅｓ１２３", True, "Mixed full-width letters and numbers"),
        ("Ａ１Ｂ２", True, "Alternating full-width"),

        # Full-width punctuation (should be non-speakable)
        ("［……］", False, "Full-width brackets and ellipsis"),
        ("！？", False, "Full-width punctuation"),
        ("［", False, "Single full-width bracket"),
        ("…", False, "Ellipsis"),

        # Regular ASCII (should still work)
        ("Yes", True, "Regular ASCII letters"),
        ("123", True, "Regular ASCII numbers"),
        ("Hello123", True, "Mixed ASCII"),

        # Chinese characters (should still work)
        ("你好", True, "Chinese characters"),
        ("測試", True, "Chinese characters"),

        # Mixed content
        ("Yes你好", True, "ASCII + Chinese"),
        ("Ｙｅｓ你好", True, "Full-width + Chinese"),
        ("Ｙｅｓ１２３你好", True, "Full-width mixed + Chinese"),
    ]

    print("Testing Full-Width Alphanumeric Character Support")
    print("=" * 60)
    print()

    all_passed = True

    for text, expected_speakable, description in test_cases:
        speakable, reason = is_speakable_content(text)
        status = "✅ PASS" if speakable == expected_speakable else "❌ FAIL"

        if speakable != expected_speakable:
            all_passed = False

        print(
            f"{status} '{text}' - Expected: {expected_speakable}, Got: {speakable} ({reason})")
        print(f"      Description: {description}")

        # Show Unicode categories for debugging
        if speakable != expected_speakable:
            print("      Unicode analysis:")
            import unicodedata
            for char in text:
                cat = unicodedata.category(char)
                name = unicodedata.name(char, 'UNKNOWN')
                print(f"        '{char}' U+{ord(char):04X}: {cat} - {name}")
        print()

    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("Full-width alphanumeric characters are correctly identified as speakable.")
        print("Full-width punctuation is correctly identified as non-speakable.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please review the failing test cases above.")

    return all_passed


if __name__ == "__main__":
    test_fullwidth_alphanumeric()
