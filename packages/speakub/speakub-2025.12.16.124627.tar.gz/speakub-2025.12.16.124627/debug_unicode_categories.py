#!/usr/bin/env python3
"""
Debug Unicode categories for problematic characters.
"""

import unicodedata
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


def analyze_unicode_categories():
    """Analyze Unicode categories for problematic characters."""

    # Test cases from the log
    test_cases = [
        "［……］",  # The problematic content from log
        "『……！』",  # Previously tested
        "……",     # Just ellipsis
        "［",     # Left bracket only
        "］",     # Right bracket only
        "！",     # Full-width exclamation
        "Hello",  # Normal text
        "你好",   # Chinese text
    ]

    print("Unicode Category Analysis")
    print("=" * 50)

    for text in test_cases:
        print(f"\nText: '{text}'")
        print("-" * 30)

        categories = []
        for char in text:
            category = unicodedata.category(char)
            name = unicodedata.name(char, 'UNKNOWN')
            categories.append(category)
            print(f"  '{char}' (U+{ord(char):04X}): {category} - {name}")

        # Check if all characters are punctuation/symbols
        all_punct = all(cat in ['Po', 'Ps', 'Pe', 'Pc', 'Pd', 'Pi',
                        'Pf', 'Sm', 'Sc', 'Sk', 'So'] for cat in categories)
        print(f"All punctuation/symbols: {all_punct}")

        # Check my speakable logic
        from speakub.utils.text_utils import is_speakable_content
        speakable, reason = is_speakable_content(text)
        print(f"Speakable: {speakable} (reason: {reason})")


if __name__ == "__main__":
    analyze_unicode_categories()
