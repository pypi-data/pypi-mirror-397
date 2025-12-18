#!/usr/bin/env python3
"""
Unit tests for predictive_preloader.py module.
"""

import time
from unittest.mock import patch, MagicMock, call
import pytest
from speakub.utils.predictive_preloader import (
    ReadingPatternAnalyzer,
    PredictivePreloader,
    get_predictive_preloader,
    init_predictive_preloader,
    cleanup_predictive_preloader,
)


class TestReadingPatternAnalyzer:
    """Test cases for ReadingPatternAnalyzer class."""

    def test_reading_pattern_analyzer_initialization(self):
        """Test ReadingPatternAnalyzer initialization."""
        analyzer = ReadingPatternAnalyzer(max_history=10)

        assert analyzer.max_history == 10
        assert len(analyzer.reading_history) == 0
        assert analyzer.pattern_weights == {}

    def test_record_chapter_access(self):
        """Test recording chapter access."""
        analyzer = ReadingPatternAnalyzer()

        with patch("speakub.utils.predictive_preloader.time.time", return_value=1000.0):
            analyzer.record_chapter_access(5)

        assert len(analyzer.reading_history) == 1
        assert analyzer.reading_history[0]["index"] == 5
        assert analyzer.reading_history[0]["timestamp"] == 1000.0

    def test_record_chapter_access_with_timestamp(self):
        """Test recording chapter access with custom timestamp."""
        analyzer = ReadingPatternAnalyzer()

        analyzer.record_chapter_access(3, timestamp=500.0)

        assert analyzer.reading_history[0]["index"] == 3
        assert analyzer.reading_history[0]["timestamp"] == 500.0

    def test_predict_next_chapters_insufficient_history(self):
        """Test predicting next chapters with insufficient history."""
        analyzer = ReadingPatternAnalyzer()

        # Only one access
        analyzer.record_chapter_access(0)

        predictions = analyzer.predict_next_chapters(0, 10, 3)

        # Should return sequential predictions
        assert predictions == [1, 2, 3]

    def test_predict_next_chapters_sequential_pattern(self):
        """Test predicting next chapters with strong sequential pattern."""
        analyzer = ReadingPatternAnalyzer()

        # Record sequential reading
        for i in range(10):
            analyzer.record_chapter_access(i)

        predictions = analyzer.predict_next_chapters(9, 15, 3)

        # Should predict sequential continuation
        assert predictions == [10, 11, 12]

    def test_predict_next_chapters_jump_pattern(self):
        """Test predicting next chapters with jump patterns."""
        analyzer = ReadingPatternAnalyzer()

        # Record some sequential reading
        for i in range(5):
            analyzer.record_chapter_access(i)

        # Record a jump back pattern
        analyzer.record_chapter_access(2)  # Jump back to chapter 2
        analyzer.record_chapter_access(3)
        analyzer.record_chapter_access(4)

        predictions = analyzer.predict_next_chapters(4, 10, 2)

        # Should include sequential prediction
        assert 5 in predictions

    def test_predict_next_chapters_beyond_total(self):
        """Test predicting next chapters beyond total chapters."""
        analyzer = ReadingPatternAnalyzer()

        predictions = analyzer.predict_next_chapters(8, 10, 3)

        # Should not predict beyond total
        for pred in predictions:
            assert pred < 10

    def test_update_pattern_weights(self):
        """Test updating pattern weights."""
        analyzer = ReadingPatternAnalyzer()

        # Record sequential transitions
        analyzer.record_chapter_access(0)
        analyzer.record_chapter_access(1)
        analyzer.record_chapter_access(2)

        # Check that sequential pattern was recorded
        assert "sequential_1" in analyzer.pattern_weights
        assert analyzer.pattern_weights["sequential_1"] == 2

    def test_calculate_sequential_score_insufficient_data(self):
        """Test calculating sequential score with insufficient data."""
        analyzer = ReadingPatternAnalyzer()

        analyzer.record_chapter_access(0)
        analyzer.record_chapter_access(1)

        score = analyzer._calculate_sequential_score(1)

        # Should return moderate confidence
        assert score == 0.5

    def test_calculate_sequential_score_strong_pattern(self):
        """Test calculating sequential score with strong pattern."""
        analyzer = ReadingPatternAnalyzer()

        # All sequential transitions
        for i in range(5):
            analyzer.record_chapter_access(i)

        score = analyzer._calculate_sequential_score(4)

        # Should return high score
        assert score == 1.0

    def test_predict_jump_patterns(self):
        """Test predicting jump patterns."""
        analyzer = ReadingPatternAnalyzer()

        # Record a jump pattern
        analyzer.record_chapter_access(5)
        analyzer.record_chapter_access(2)  # Jump back
        analyzer.record_chapter_access(3)

        predictions = analyzer._predict_jump_patterns(2, 10)

        # Should predict chapter 3 based on pattern
        assert 3 in predictions


class TestPredictivePreloader:
    """Test cases for PredictivePreloader class."""

    def test_predictive_preloader_initialization(self):
        """Test PredictivePreloader initialization."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config") as mock_config:
            mock_config.side_effect = lambda key, default: {
                "performance.predictive_preloading": True,
                "performance.preload_delay_ms": 500
            }.get(key, default)

            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer, max_cache_size=5)

        assert preloader.epub_parser == mock_epub_parser
        assert preloader.content_renderer == mock_content_renderer
        assert preloader.max_cache_size == 5
        assert preloader.enabled is True
        assert preloader.preloaded_cache == {}
        assert preloader.preloading_tasks == set()

    def test_start_preloader(self):
        """Test starting the preloader."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        with patch("speakub.utils.predictive_preloader.threading.Thread") as mock_thread:
            mock_thread_instance = MagicMock()
            mock_thread.return_value = mock_thread_instance

            preloader.start()

            assert preloader._preloader_thread is not None
            mock_thread.assert_called_once()

    def test_start_preloader_disabled(self):
        """Test starting preloader when disabled."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=False):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        preloader.start()

        # Should not start thread
        assert preloader._preloader_thread is None

    def test_stop_preloader(self):
        """Test stopping the preloader."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        mock_thread = MagicMock()
        preloader._preloader_thread = mock_thread

        preloader.stop()

        assert preloader._preloader_thread is None
        assert preloader.preloaded_cache == {}
        assert preloader.preloading_tasks == set()
        mock_thread.join.assert_called_once_with(timeout=2.0)

    def test_record_chapter_access(self):
        """Test recording chapter access."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        preloader.record_chapter_access(5)

        # Should have recorded in pattern analyzer
        assert len(preloader.pattern_analyzer.reading_history) == 1

    def test_record_chapter_access_disabled(self):
        """Test recording chapter access when disabled."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=False):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        preloader.record_chapter_access(5)

        # Should not record when disabled
        assert len(preloader.pattern_analyzer.reading_history) == 0

    def test_get_preloaded_content_available(self):
        """Test getting available preloaded content."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        test_content = ["line1", "line2"]
        preloader.preloaded_cache[5] = (test_content, time.time())

        result = preloader.get_preloaded_content(5)

        assert result == test_content
        assert 5 not in preloader.preloaded_cache  # Should be removed after use

    def test_get_preloaded_content_not_available(self):
        """Test getting preloaded content when not available."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        result = preloader.get_preloaded_content(5)

        assert result is None

    def test_preload_chapters(self):
        """Test preloading chapters."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        chapter_sources = ["chap1.xhtml", "chap2.xhtml", "chap3.xhtml"]
        predictions = [1, 2]

        preloader.preload_chapters(predictions, chapter_sources)

        # Should add to preloading tasks
        assert 1 in preloader.preloading_tasks
        assert 2 in preloader.preloading_tasks

    def test_preload_chapter_sync(self):
        """Test synchronously preloading a chapter."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        # Mock epub parser and content renderer
        mock_epub_parser.read_chapter.return_value = "<html>test</html>"
        mock_content_renderer.render_chapter.return_value = ["line1", "line2"]

        chapter_src = "chapter1.xhtml"

        with patch("speakub.utils.predictive_preloader.time.time", return_value=1000.0):
            preloader.preload_chapter_sync(1, chapter_src)

        # Should have called epub parser and content renderer
        mock_epub_parser.read_chapter.assert_called_once_with(chapter_src)
        mock_content_renderer.render_chapter.assert_called_once_with(
            "<html>test</html>")

        # Should have stored in cache
        assert 1 in preloader.preloaded_cache
        content, timestamp = preloader.preloaded_cache[1]
        assert content == ["line1", "line2"]
        assert timestamp == 1000.0

        # Should have removed from preloading tasks
        assert 1 not in preloader.preloading_tasks

    def test_preload_chapter_sync_disabled(self):
        """Test preloading chapter when disabled."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=False):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        preloader.preload_chapter_sync(1, "chapter1.xhtml")

        # Should not have called epub parser
        mock_epub_parser.read_chapter.assert_not_called()

    def test_cleanup_cache_expired(self):
        """Test cleaning up expired cache entries."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        # Add some cache entries with old timestamps
        current_time = time.time()
        preloader.preloaded_cache = {
            1: (["content1"], current_time - 400),  # Expired (5+ min)
            2: (["content2"], current_time - 100),  # Not expired
        }

        preloader._cleanup_cache()

        # Should only keep non-expired entry
        assert 1 not in preloader.preloaded_cache
        assert 2 in preloader.preloaded_cache

    def test_cleanup_cache_size_limit(self):
        """Test cleaning up cache when over size limit."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer, max_cache_size=2)

        current_time = time.time()
        # Add more entries than max_cache_size
        preloader.preloaded_cache = {
            1: (["content1"], current_time - 100),
            2: (["content2"], current_time - 200),  # Oldest
            3: (["content3"], current_time - 150),
        }

        preloader._cleanup_cache()

        # Should keep only 2 entries, removing the oldest
        assert len(preloader.preloaded_cache) == 2
        assert 2 not in preloader.preloaded_cache  # Oldest should be removed

    def test_get_cache_stats(self):
        """Test getting cache statistics."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        with patch("speakub.utils.predictive_preloader.get_config", return_value=True):
            preloader = PredictivePreloader(
                mock_epub_parser, mock_content_renderer)

        preloader.preloaded_cache = {1: (["content"], time.time())}
        preloader.preloading_tasks = {2, 3}

        stats = preloader.get_cache_stats()

        assert stats["cache_size"] == 1
        assert stats["max_cache_size"] == 3
        assert stats["preloading_tasks"] == 2
        assert stats["enabled"] is True


class TestGlobalFunctions:
    """Test cases for global functions."""

    @patch("speakub.utils.predictive_preloader._preloader_instance", None)
    def test_get_predictive_preloader_none(self):
        """Test getting preloader when none exists."""
        result = get_predictive_preloader()
        assert result is None

    @patch("speakub.utils.predictive_preloader._preloader_instance")
    def test_get_predictive_preloader_exists(self, mock_instance):
        """Test getting preloader when one exists."""
        result = get_predictive_preloader()
        assert result == mock_instance

    @patch("speakub.utils.predictive_preloader.PredictivePreloader")
    @patch("speakub.utils.predictive_preloader._preloader_instance", None)
    def test_init_predictive_preloader(self, mock_preloader_class):
        """Test initializing predictive preloader."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()
        mock_instance = MagicMock()
        mock_preloader_class.return_value = mock_instance

        result = init_predictive_preloader(
            mock_epub_parser, mock_content_renderer)

        assert result == mock_instance
        mock_preloader_class.assert_called_once_with(
            mock_epub_parser, mock_content_renderer)
        mock_instance.start.assert_called_once()

    @patch("speakub.utils.predictive_preloader._preloader_instance")
    def test_init_predictive_preloader_already_exists(self, mock_instance):
        """Test initializing preloader when one already exists."""
        mock_epub_parser = MagicMock()
        mock_content_renderer = MagicMock()

        result = init_predictive_preloader(
            mock_epub_parser, mock_content_renderer)

        # Should return existing instance without creating new one
        assert result == mock_instance

    @patch("speakub.utils.predictive_preloader._preloader_instance")
    def test_cleanup_predictive_preloader(self, mock_instance):
        """Test cleaning up predictive preloader."""
        cleanup_predictive_preloader()

        mock_instance.stop.assert_called_once()

        # Import to check the global variable
        from speakub.utils.predictive_preloader import _preloader_instance
        assert _preloader_instance is None

    def test_cleanup_predictive_preloader_none(self):
        """Test cleaning up when no preloader exists."""
        # Set to None first
        from speakub.utils.predictive_preloader import _preloader_instance
        _preloader_instance = None

        # Should not raise error
        cleanup_predictive_preloader()


if __name__ == "__main__":
    pytest.main([__file__])
