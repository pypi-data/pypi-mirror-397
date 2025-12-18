#!/usr/bin/env python3
"""
Unit tests for voice_filter_utils.py module.
"""

import pytest
from speakub.utils.voice_filter_utils import (
    filter_female_chinese_voices,
    filter_voices_by_criteria,
)


class TestFilterFemaleChineseVoices:
    """Test cases for filter_female_chinese_voices function."""

    def test_filter_female_chinese_voices_empty_list(self):
        """Test filtering empty voice list."""
        result = filter_female_chinese_voices([])
        assert result == []

    def test_filter_female_chinese_voices_no_matches(self):
        """Test filtering with no matching voices."""
        voices = [
            {"name": "Voice1", "gender": "male", "locale": "en-US"},
            {"name": "Voice2", "gender": "female", "locale": "en-GB"},
            {"name": "Voice3", "gender": "male", "locale": "zh-CN"},
        ]
        result = filter_female_chinese_voices(voices)
        assert result == []

    def test_filter_female_chinese_voices_matches(self):
        """Test filtering with matching voices."""
        voices = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "female", "locale": "zh-TW"},
            {"name": "Voice3", "gender": "male", "locale": "zh-CN"},
            {"name": "Voice4", "gender": "female", "locale": "en-US"},
        ]
        result = filter_female_chinese_voices(voices)

        expected = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "female", "locale": "zh-TW"},
        ]
        assert result == expected

    def test_filter_female_chinese_voices_case_insensitive_gender(self):
        """Test filtering with case-insensitive gender matching."""
        voices = [
            {"name": "Voice1", "gender": "Female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "FEMALE", "locale": "zh-TW"},
            {"name": "Voice3", "gender": "female", "locale": "zh-CN"},
        ]
        result = filter_female_chinese_voices(voices)

        assert len(result) == 3
        assert all(voice["gender"].lower() == "female" for voice in result)
        assert all(voice["locale"].startswith(("zh-CN", "zh-TW"))
                   for voice in result)

    def test_filter_female_chinese_voices_missing_fields(self):
        """Test filtering voices with missing gender or locale fields."""
        voices = [
            {"name": "Voice1", "gender": "female"},  # Missing locale
            {"name": "Voice2", "locale": "zh-CN"},  # Missing gender
            {"name": "Voice3"},  # Missing both
            {"name": "Voice4", "gender": "female", "locale": "zh-CN"},  # Complete
        ]
        result = filter_female_chinese_voices(voices)

        # Only the complete voice should match
        assert result == [
            {"name": "Voice4", "gender": "female", "locale": "zh-CN"}]


class TestFilterVoicesByCriteria:
    """Test cases for filter_voices_by_criteria function."""

    def test_filter_voices_by_criteria_empty_list(self):
        """Test filtering empty voice list."""
        result = filter_voices_by_criteria([])
        assert result == []

    def test_filter_voices_by_criteria_no_criteria(self):
        """Test filtering with no criteria specified."""
        voices = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "male", "locale": "en-US"},
        ]
        result = filter_voices_by_criteria(voices)
        assert result == voices

    def test_filter_voices_by_criteria_gender_only(self):
        """Test filtering by gender only."""
        voices = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "male", "locale": "en-US"},
            {"name": "Voice3", "gender": "Female", "locale": "zh-TW"},
        ]
        result = filter_voices_by_criteria(voices, gender="female")

        expected = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice3", "gender": "Female", "locale": "zh-TW"},
        ]
        assert result == expected

    def test_filter_voices_by_criteria_locale_only(self):
        """Test filtering by locale prefix only."""
        voices = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "male", "locale": "en-US"},
            {"name": "Voice3", "gender": "female", "locale": "zh-TW"},
            {"name": "Voice4", "gender": "male", "locale": "zh-HK"},
        ]
        result = filter_voices_by_criteria(voices, locale_prefix="zh")

        expected = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice3", "gender": "female", "locale": "zh-TW"},
            {"name": "Voice4", "gender": "male", "locale": "zh-HK"},
        ]
        assert result == expected

    def test_filter_voices_by_criteria_both_criteria(self):
        """Test filtering by both gender and locale prefix."""
        voices = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "male", "locale": "zh-CN"},
            {"name": "Voice3", "gender": "female", "locale": "en-US"},
            {"name": "Voice4", "gender": "female", "locale": "zh-TW"},
            {"name": "Voice5", "gender": "male", "locale": "zh-TW"},
        ]
        result = filter_voices_by_criteria(
            voices, gender="female", locale_prefix="zh")

        expected = [
            {"name": "Voice1", "gender": "female", "locale": "zh-CN"},
            {"name": "Voice4", "gender": "female", "locale": "zh-TW"},
        ]
        assert result == expected

    def test_filter_voices_by_criteria_case_insensitive_gender(self):
        """Test filtering with case-insensitive gender matching."""
        voices = [
            {"name": "Voice1", "gender": "Female", "locale": "zh-CN"},
            {"name": "Voice2", "gender": "MALE", "locale": "zh-CN"},
            {"name": "Voice3", "gender": "female", "locale": "zh-CN"},
        ]
        result = filter_voices_by_criteria(voices, gender="female")

        expected = [
            {"name": "Voice1", "gender": "Female", "locale": "zh-CN"},
            {"name": "Voice3", "gender": "female", "locale": "zh-CN"},
        ]
        assert result == expected

    def test_filter_voices_by_criteria_no_matches(self):
        """Test filtering with criteria that match no voices."""
        voices = [
            {"name": "Voice1", "gender": "male", "locale": "en-US"},
            {"name": "Voice2", "gender": "female", "locale": "en-GB"},
        ]
        result = filter_voices_by_criteria(
            voices, gender="female", locale_prefix="zh")
        assert result == []

    def test_filter_voices_by_criteria_missing_fields(self):
        """Test filtering voices with missing fields."""
        voices = [
            {"name": "Voice1", "gender": "female"},  # Missing locale
            {"name": "Voice2", "locale": "zh-CN"},  # Missing gender
            {"name": "Voice3"},  # Missing both
            {"name": "Voice4", "gender": "female", "locale": "zh-CN"},  # Complete
        ]

        # Filter by gender only
        result_gender = filter_voices_by_criteria(voices, gender="female")
        assert result_gender == [
            {"name": "Voice1", "gender": "female"},
            {"name": "Voice4", "gender": "female", "locale": "zh-CN"},
        ]

        # Filter by locale only
        result_locale = filter_voices_by_criteria(voices, locale_prefix="zh")
        assert result_locale == [
            {"name": "Voice2", "locale": "zh-CN"},
            {"name": "Voice4", "gender": "female", "locale": "zh-CN"},
        ]

        # Filter by both
        result_both = filter_voices_by_criteria(
            voices, gender="female", locale_prefix="zh")
        assert result_both == [
            {"name": "Voice4", "gender": "female", "locale": "zh-CN"}]


if __name__ == "__main__":
    pytest.main([__file__])
