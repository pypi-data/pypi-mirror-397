#!/usr/bin/env python3
"""
Test script to check if the three texts are considered speakable content.
"""

from speakub.utils.text_utils import is_speakable_content
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


test_texts = ['『……王？』', '『嚇……！』', '「嗚……」']

print("Testing speakable content detection:")
print("=" * 50)

for text in test_texts:
    speakable, reason = is_speakable_content(text)
    print(f'Text: {text}')
    print(f'  Speakable: {speakable}')
    print(f'  Reason: {reason}')

    # Calculate ratio manually for verification
    total_chars = len(text.strip())
    speakable_count = 0
    for char in text:
        if ('\u4e00' <= char <= '\u9fff' or  # CJK Unified Ideographs
            '\u3040' <= char <= '\u309f' or  # Hiragana
            '\u30a0' <= char <= '\u30ff' or  # Katakana
            '\uac00' <= char <= '\ud7af' or  # Korean syllables
                char.isalnum()):  # Alphanumeric
            speakable_count += 1

    ratio = speakable_count / total_chars if total_chars > 0 else 0
    print(
        f'  Total chars: {total_chars}, Speakable chars: {speakable_count}, Ratio: {ratio:.2f}')
    print()
