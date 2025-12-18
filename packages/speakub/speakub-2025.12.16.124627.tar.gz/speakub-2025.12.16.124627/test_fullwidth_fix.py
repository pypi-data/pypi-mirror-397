#!/usr/bin/env python3
"""
Test for the full-width Latin character fix in is_speakable_content.
This test should be added to the main test suite.
"""

import pytest
from speakub.utils.text_utils import is_speakable_content


class TestFullWidthCharacterSupport:
    """Test full-width Latin character support in speakable content detection."""

    def test_fullwidth_latin_characters_speakable(self):
        """Test that full-width Latin characters are considered speakable."""
        # Individual full-width characters
        assert is_speakable_content("Ｙ") == (True, "has_speakable_characters")
        assert is_speakable_content("Ｎ") == (True, "has_speakable_characters")
        assert is_speakable_content("ｅ") == (True, "has_speakable_characters")
        assert is_speakable_content("ｓ") == (True, "has_speakable_characters")

        # Full-width words
        assert is_speakable_content("Ｙｅｓ") == (
            True, "has_speakable_characters")
        assert is_speakable_content("Ｎｏ") == (True, "has_speakable_characters")
        assert is_speakable_content("ＹＥＳ") == (
            True, "has_speakable_characters")

        # Mixed full-width and Chinese
        assert is_speakable_content("Ｙｅｓ或Ｎｏ") == (
            True, "has_speakable_characters")

        # Full-width alphabet
        assert is_speakable_content("ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ") == (
            True, "has_speakable_characters")
        assert is_speakable_content("ａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ") == (
            True, "has_speakable_characters")

    def test_regular_ascii_still_works(self):
        """Test that regular ASCII characters still work."""
        assert is_speakable_content("Yes") == (
            True, "has_speakable_characters")
        assert is_speakable_content("NO") == (True, "has_speakable_characters")
        assert is_speakable_content("Hello world!") == (
            True, "has_speakable_characters")

    def test_chinese_characters_still_work(self):
        """Test that Chinese characters still work."""
        assert is_speakable_content("你好世界") == (
            True, "has_speakable_characters")
        assert is_speakable_content("英文字母") == (
            True, "has_speakable_characters")

    def test_mixed_content_works(self):
        """Test that mixed ASCII, full-width, and Chinese content works."""
        # The original user example
        test_text = "Ｙｅｓ或Ｎｏ，英文字母Ｙ和Ｎ在振宇眼前慢慢閃爍，彷彿在等待他的回答。"
        assert is_speakable_content(test_text) == (
            True, "has_speakable_characters")

        # Other mixed examples
        assert is_speakable_content("Yes or Ｙｅｓ, both work!") == (
            True, "has_speakable_characters")
        assert is_speakable_content("Regular and 全形 characters") == (
            True, "has_speakable_characters")

    def test_non_speakable_content_still_filtered(self):
        """Test that non-speakable content is still properly filtered."""
        assert is_speakable_content("") == (False, "empty_content")
        assert is_speakable_content(
            "!!!???@@@") == (False, "no_speakable_characters")
        assert is_speakable_content("1234567890") == (
            True, "has_speakable_characters")  # Numbers are allowed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
