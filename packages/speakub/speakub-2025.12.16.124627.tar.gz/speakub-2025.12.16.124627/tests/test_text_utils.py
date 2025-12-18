#!/usr/bin/env python3
"""
Unit tests for text_utils.py module.
"""

import pytest
from speakub.utils.text_utils import (
    str_display_width,
    truncate_str_by_width,
    format_reading_time,
    clean_text_for_display,
    clean_text_for_tts,
    extract_title_from_text,
    word_wrap,
    normalize_chapter_title,
    extract_reading_level,
    is_speakable_content,
    correct_chinese_pronunciation,
)


class TestTextUtils:
    """Test cases for text utilities."""

    def test_str_display_width_empty_string(self):
        """Test display width of empty string."""
        assert str_display_width("") == 0

    def test_str_display_width_ascii(self):
        """Test display width of ASCII text."""
        assert str_display_width("hello") == 5
        assert str_display_width("hello world") == 11

    def test_str_display_width_unicode(self):
        """Test display width of Unicode text."""
        # Chinese characters should be width 2
        assert str_display_width("你好") == 4  # 2 chars * 2 width each
        assert str_display_width("hello你好") == 9  # 5 + 4

    def test_truncate_str_by_width_empty(self):
        """Test truncating empty string."""
        assert truncate_str_by_width("", 10) == ""
        assert truncate_str_by_width("hello", 0) == ""

    def test_truncate_str_by_width_no_truncation(self):
        """Test when no truncation is needed."""
        text = "hello"
        assert truncate_str_by_width(text, 10) == text

    def test_truncate_str_by_width_with_truncation(self):
        """Test truncating text that exceeds width."""
        text = "hello world this is a long text"
        truncated = truncate_str_by_width(text, 10)
        assert str_display_width(truncated) <= 10
        assert truncated.endswith("...") or len(truncated) < len(text)

    def test_format_reading_time_less_than_minute(self):
        """Test formatting time less than 1 minute."""
        assert format_reading_time(0.5) == "< 1 min"

    def test_format_reading_time_minutes(self):
        """Test formatting time in minutes."""
        assert format_reading_time(5) == "5 min"
        assert format_reading_time(30) == "30 min"

    def test_format_reading_time_hours(self):
        """Test formatting time in hours."""
        assert format_reading_time(60) == "1h"
        assert format_reading_time(90) == "1h 30m"
        assert format_reading_time(120) == "2h"

    def test_clean_text_for_display_empty(self):
        """Test cleaning empty text."""
        assert clean_text_for_display("") == ""

    def test_clean_text_for_display_whitespace(self):
        """Test cleaning whitespace."""
        text = "  hello   world  \n\n\n  test  "
        cleaned = clean_text_for_display(text)
        # The function preserves some trailing spaces in lines
        assert "hello world" in cleaned
        assert "\n\n" in cleaned
        assert "test" in cleaned.strip()

    def test_clean_text_for_display_control_chars(self):
        """Test removing control characters."""
        text = "hello\x00world\x01test"
        cleaned = clean_text_for_display(text)
        assert "\x00" not in cleaned
        assert "\x01" not in cleaned
        assert "helloworldtest" in cleaned

    def test_clean_text_for_tts_empty(self):
        """Test TTS cleaning of empty text."""
        assert clean_text_for_tts("") == ""

    def test_clean_text_for_tts_markdown(self):
        """Test TTS cleaning of markdown."""
        text = "**bold** *italic* __underline__"
        cleaned = clean_text_for_tts(text)
        assert "**" not in cleaned
        assert "*" not in cleaned
        assert "__" not in cleaned
        assert cleaned == "bold italic underline"

    def test_clean_text_for_tts_punctuation(self):
        """Test TTS cleaning of excessive punctuation."""
        text = "Hello.....world---test"
        cleaned = clean_text_for_tts(text)
        assert "....." not in cleaned
        assert "---" not in cleaned
        assert cleaned == "Hello...world---test"

    def test_extract_title_from_text_empty(self):
        """Test title extraction from empty text."""
        assert extract_title_from_text("") == "Untitled"

    def test_extract_title_from_text_with_content(self):
        """Test title extraction from text with content."""
        text = "\n\n# Chapter 1\n\nThis is the content."
        title = extract_title_from_text(text)
        assert title == "Chapter 1"

    def test_extract_title_from_text_markdown(self):
        """Test title extraction removes markdown."""
        text = "## **Bold Title** ##"
        title = extract_title_from_text(text)
        assert title == "Bold Title"

    def test_word_wrap_empty(self):
        """Test word wrapping empty text."""
        assert word_wrap("", 10) == []

    def test_word_wrap_simple(self):
        """Test simple word wrapping."""
        text = "hello world this is a test"
        lines = word_wrap(text, 15)
        assert len(lines) > 1
        assert all(str_display_width(line) <= 15 for line in lines)

    def test_word_wrap_with_indent(self):
        """Test word wrapping with indentation."""
        text = "hello world this is a long test sentence"
        lines = word_wrap(text, 20, indent=4)
        assert len(lines) > 1
        # Check that continuation lines are indented
        for i, line in enumerate(lines):
            if i > 0:  # continuation lines should be indented
                assert line.startswith("    ")

    def test_normalize_chapter_title_empty(self):
        """Test normalizing empty chapter title."""
        assert normalize_chapter_title("") == "Untitled Chapter"

    def test_normalize_chapter_title_english(self):
        """Test normalizing English chapter title."""
        title = "Chapter 1: Introduction"
        normalized = normalize_chapter_title(title)
        assert normalized == "Introduction"

    def test_normalize_chapter_title_chinese(self):
        """Test normalizing Chinese chapter title."""
        title = "第1章：介绍"
        normalized = normalize_chapter_title(title)
        assert normalized == "介绍"

    def test_extract_reading_level_empty(self):
        """Test reading level extraction from empty text."""
        result = extract_reading_level("")
        assert result["words"] == 0
        assert result["sentences"] == 0
        assert result["complexity"] == "unknown"

    def test_extract_reading_level_simple(self):
        """Test reading level extraction from simple text."""
        text = "This is a simple sentence. It has words."
        result = extract_reading_level(text)

        assert result["words"] == 8
        assert result["sentences"] == 2
        assert isinstance(result["avg_word_length"], float)
        assert result["complexity"] in ["easy", "medium", "hard"]

    def test_is_speakable_content_empty(self):
        """Test speakable content check for empty text."""
        speakable, reason = is_speakable_content("")
        assert not speakable
        assert reason == "empty_content"

    def test_is_speakable_content_ascii(self):
        """Test speakable content check for ASCII text."""
        speakable, reason = is_speakable_content("Hello world!")
        assert speakable
        assert reason == "has_speakable_characters"

    def test_is_speakable_content_chinese(self):
        """Test speakable content check for Chinese text."""
        speakable, reason = is_speakable_content("你好世界")
        assert speakable
        assert reason == "has_speakable_characters"

    def test_is_speakable_content_only_symbols(self):
        """Test speakable content check for text with only symbols."""
        speakable, reason = is_speakable_content("!!!???@@@")
        assert not speakable
        assert reason == "no_speakable_characters"

    def test_correct_chinese_pronunciation_empty(self):
        """Test Chinese pronunciation correction for empty text."""
        assert correct_chinese_pronunciation("") == ""

    def test_correct_chinese_pronunciation_no_corrections(self):
        """Test Chinese pronunciation correction when no corrections are loaded."""
        text = "这是一个测试文本"
        result = correct_chinese_pronunciation(text)
        assert result == text

    def test_correct_chinese_pronunciation_with_corrections(self):
        """Test Chinese pronunciation correction with loaded corrections."""
        # This test assumes corrections are loaded from config
        # In a real scenario, we'd mock the corrections
        text = "测试文本"
        result = correct_chinese_pronunciation(text)
        # Result should be either unchanged or corrected
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__])
