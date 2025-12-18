#!/usr/bin/env python3
"""
Debug the is_speakable_content function for the problematic text.
"""

from speakub.utils.text_utils import is_speakable_content
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


def debug_speakable():
    """Debug speakable content check."""
    test_text = "『……！』"
    print(f"Testing text: '{test_text}'")
    print("Unicode analysis:")

    for i, char in enumerate(test_text):
        print(f"  {i}: '{char}' U+{ord(char):04X}")

    print()
    speakable, reason = is_speakable_content(test_text)
    print(f"Speakable result: {speakable} (reason: {reason})")

    # Test the regex directly
    import re
    speakable_pattern = re.compile(
        r"[a-zA-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\uff00-\uffef]+"
    )
    matches = speakable_pattern.findall(test_text)
    print(f"Regex matches: {matches}")


if __name__ == "__main__":
    debug_speakable()
