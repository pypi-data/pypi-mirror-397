"""
Tests for speakub.tts.playlist_manager module
"""

import asyncio
import threading
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest

from speakub.tts.playlist_manager import PlaylistManager


class MockAppInterface:
    """Mock implementation of AppInterface for testing."""

    def __init__(self):
        self.tts_status = "IDLE"
        self.tts_engine = None
        self.tts_smooth_mode = False
        self.tts_volume = 100
        self.tts_rate = 0
        self.tts_pitch = "+0Hz"
        self.viewport_content = None  # Mock for playlist generation
        self.epub_manager = None  # Mock for epub_manager

    def notify(self, message, title=None, severity=None):
        pass


class MockTTSIntegration:
    """Mock TTS integration for testing."""

    def __init__(self):
        self.app = MockAppInterface()
        self.tts_stop_requested = threading.Event()
        self.tts_lock = threading.RLock()

    def __enter__(self):
        self.tts_lock.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.tts_lock.release()


class TestPlaylistManager:
    """Test PlaylistManager class"""

    def test_initialization(self):
        """Test playlist manager initialization"""
        integration = MockTTSIntegration()

        manager = PlaylistManager(integration)

        assert manager.tts_integration == integration
        assert manager.app == integration.app
        assert manager.playlist == []
        assert manager.current_index == 0
        assert len(manager._preload_tasks) == 0
        assert manager._batch_size == 5  # Default value
        assert manager._max_queue_size == 20  # Default value

    def test_playlist_operations(self):
        """Test basic playlist operations"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Test initial state
        assert manager.get_playlist_length() == 0
        assert manager.get_current_index() == 0
        assert not manager.has_items()
        assert manager.is_exhausted()

        # Add items to playlist
        manager.playlist = [("text1", 1), ("text2", 2), ("text3", 3)]

        assert manager.get_playlist_length() == 3
        assert manager.has_items()
        assert not manager.is_exhausted()

        # Test item access
        assert manager.get_current_item() == ("text1", 1)
        assert manager.get_item_at(1) == ("text2", 2)
        assert manager.get_item_at(10) is None

        # Test index advancement
        manager.advance_index()
        assert manager.get_current_index() == 1
        assert manager.get_current_item() == ("text2", 2)

        # Test exhaustion
        manager.current_index = 3
        assert manager.is_exhausted()

    def test_playlist_item_update(self):
        """Test playlist item updates"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        manager.playlist = [("text1", 1), ("text2", 2)]

        # Update item
        manager.update_item_at(1, ("text2", 2, b"audio_data"))

        assert manager.get_item_at(1) == ("text2", 2, b"audio_data")

        # Update out of bounds
        manager.update_item_at(10, ("invalid",))
        # Should not crash

    def test_reset(self):
        """Test playlist reset"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Set up state
        manager.playlist = [("text1", 1), ("text2", 2)]
        manager.current_index = 1

        # Mock tasks
        mock_task = Mock()
        mock_task.done.return_value = False
        manager._preload_tasks = [mock_task]
        manager._batch_preload_task = mock_task
        manager._synthesis_tasks = [mock_task]

        # Mock queue
        manager._playback_queue = asyncio.Queue()
        manager._playback_queue.put_nowait("item")

        manager.reset()

        assert manager.playlist == []
        assert manager.current_index == 0
        assert len(manager._preload_tasks) == 0
        assert manager._batch_preload_task is None
        assert len(manager._synthesis_tasks) == 0

        # Queue should be empty
        assert manager._playback_queue.empty()

        # Tasks should be cancelled
        mock_task.cancel.assert_called()

    def test_cleanup_completed_tasks(self):
        """Test cleanup of completed tasks"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Create mock tasks
        completed_task = Mock()
        completed_task.done.return_value = True

        running_task = Mock()
        running_task.done.return_value = False

        manager._preload_tasks = [completed_task, running_task]

        manager._cleanup_completed_tasks()

        assert len(manager._preload_tasks) == 1
        assert running_task in manager._preload_tasks

    @patch('speakub.utils.text_utils.is_speakable_content')
    @pytest.mark.asyncio
    async def test_preload_synthesis_success(self, mock_is_speakable):
        """Test successful preload synthesis"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        mock_is_speakable.return_value = (True, "normal content")

        # Mock TTS engine
        mock_engine = Mock()
        mock_engine.synthesize = AsyncMock(return_value=b"audio_data")
        integration.app.tts_engine = mock_engine

        # Add item to playlist
        manager.playlist = [("test text", 1)]

        await manager._preload_synthesis(0, "test text")

        # Check that synthesis was called
        mock_engine.synthesize.assert_called_once()

        # Check that playlist was updated
        assert len(manager.playlist[0]) == 3
        assert manager.playlist[0][2] == b"audio_data"

    @patch('speakub.utils.text_utils.is_speakable_content')
    @pytest.mark.asyncio
    async def test_preload_synthesis_not_speakable(self, mock_is_speakable):
        """Test preload synthesis with non-speakable content"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        mock_is_speakable.return_value = (False, "empty content")

        # Add item to playlist
        manager.playlist = [("test text", 1)]

        await manager._preload_synthesis(0, "test text")

        # Check that playlist was marked as filtered
        assert len(manager.playlist[0]) == 3
        assert manager.playlist[0][2] == b"CONTENT_FILTERED"

    @patch('speakub.utils.text_utils.is_speakable_content')
    @pytest.mark.asyncio
    async def test_preload_synthesis_failure(self, mock_is_speakable):
        """Test preload synthesis failure"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        mock_is_speakable.return_value = (True, "normal content")

        # Mock TTS engine to fail
        mock_engine = Mock()
        mock_engine.synthesize = AsyncMock(return_value=b"ERROR")
        integration.app.tts_engine = mock_engine

        # Add item to playlist
        manager.playlist = [("test text", 1)]

        await manager._preload_synthesis(0, "test text")

        # Playlist should not be updated
        assert len(manager.playlist[0]) == 2

    @patch('speakub.tts.playlist_manager.prepare_tts_playlist')
    def test_generate_playlist(self, mock_prepare):
        """Test playlist generation"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        manager.generate_playlist()

        mock_prepare.assert_called_once_with(manager)

    @patch('speakub.tts.ui.playlist.tts_load_next_chapter')
    def test_load_next_chapter(self, mock_load):
        """Test next chapter loading"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        mock_load.return_value = True

        result = manager.load_next_chapter()

        assert result is True
        mock_load.assert_called_once_with(manager)

    def test_get_preloading_stats(self):
        """Test preloading statistics"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Set up some state
        manager._batch_size = 8
        manager._synthesis_times = [1.0, 2.0, 3.0]

        # Mock predictive controller
        mock_controller = Mock()
        mock_controller.get_performance_stats.return_value = {
            "state": "active",
            "monitor_active": True,
            "trigger_count": 5,
            "play_monitor_stats": {}
        }
        manager._predictive_controller = mock_controller

        stats = manager.get_preloading_stats()

        assert stats["batch_size"] == 8
        assert stats["queue_size"] == 0
        assert stats["avg_synthesis_time"] == 2.0
        assert stats["predictive_mode"] is True
        assert stats["predictive_state"] == "active"

    def test_get_preloading_stats_no_predictive(self):
        """Test preloading statistics without predictive controller"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Remove predictive controller
        delattr(manager, '_predictive_controller')

        stats = manager.get_preloading_stats()

        assert stats["predictive_mode"] is False

    def test_record_playback_event(self):
        """Test playback event recording"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Mock predictive controller
        mock_controller = Mock()
        manager._predictive_controller = mock_controller

        manager.record_playback_event(1, 2.5, 100)

        mock_controller.record_playback_event.assert_called_once_with(
            1, 2.5, 100)

    def test_get_queue_size(self):
        """Test queue size retrieval"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        assert manager.get_queue_size() == 0

    def test_get_batch_size(self):
        """Test batch size retrieval"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        assert manager.get_batch_size() == 5  # Default value

    def test_should_use_optimal_batching_smooth_mode(self):
        """Test optimal batching check in smooth mode"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        integration.app.tts_smooth_mode = True

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.return_value = True  # fusion enabled

            assert manager._should_use_optimal_batching() is True

    def test_should_use_optimal_batching_non_smooth(self):
        """Test optimal batching check in non-smooth mode"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        integration.app.tts_smooth_mode = False

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "tts.preferred_engine": "edge-tts",
                "tts.optimal_batching.enabled": True
            }.get(key, default or False)

            assert manager._should_use_optimal_batching() is True

    def test_get_engine_target_chars(self):
        """Test engine target character retrieval"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.return_value = {"edge-tts": 60, "nanmai": 40}

            # Test edge-tts
            mock_config.side_effect = lambda key, default=None: {
                "tts.preferred_engine": "edge-tts",
                "tts.optimal_batching.target_batch_chars": {"edge-tts": 60, "nanmai": 40}
            }.get(key, default or {})

            assert manager._get_engine_target_chars() == 60

            # Test nanmai
            mock_config.side_effect = lambda key, default=None: {
                "tts.preferred_engine": "nanmai",
                "tts.optimal_batching.target_batch_chars": {"edge-tts": 60, "nanmai": 40}
            }.get(key, default or {})

            assert manager._get_engine_target_chars() == 40

    # Legacy test removed - _get_next_batch_legacy method has been deprecated
    # def test_get_next_batch_legacy(self):
    #     """Test legacy batch retrieval"""
    #     # Method removed in cleanup - use _get_next_batch_optimal instead

    # Legacy test removed - _get_next_batch_legacy method has been deprecated
    # def test_get_next_batch_legacy_queue_full(self):
    #     """Test legacy batch retrieval when queue is full"""
    #     # Method removed in cleanup - use _get_next_batch_optimal instead

    def test_adjust_batch_size_increase(self):
        """Test batch size increase"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Set up fast synthesis times
        manager._synthesis_times = [0.5] * 10  # All under target
        manager._batch_size = 5
        manager._last_adjustment_time = time.time() - 15  # Old enough

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.return_value = "edge-tts"

            manager._adjust_batch_size()

            assert manager._batch_size == 6  # Increased by 1

    def test_adjust_batch_size_decrease(self):
        """Test batch size decrease"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Set up slow synthesis times
        manager._synthesis_times = [3.0] * 10  # All over target
        manager._batch_size = 5
        manager._last_adjustment_time = time.time() - 15  # Old enough

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.return_value = "edge-tts"

            manager._adjust_batch_size()

            assert manager._batch_size == 4  # Decreased by 1

    def test_adjust_batch_size_no_change(self):
        """Test batch size no change when timing is right"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Set up synthesis times within acceptable range
        manager._synthesis_times = [2.0] * 10  # Close to target
        manager._batch_size = 5
        manager._last_adjustment_time = time.time() - 15

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.return_value = "edge-tts"

            manager._adjust_batch_size()

            assert manager._batch_size == 5  # No change

    def test_adjust_batch_size_insufficient_data(self):
        """Test batch size adjustment with insufficient data"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Not enough synthesis times
        manager._synthesis_times = [2.0] * 5  # Less than adjustment_window
        manager._batch_size = 5

        manager._adjust_batch_size()

        assert manager._batch_size == 5  # No change

    def test_adjust_batch_size_recent_adjustment(self):
        """Test batch size adjustment blocked by recent adjustment"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        manager._synthesis_times = [5.0] * 10
        manager._batch_size = 5
        manager._last_adjustment_time = time.time()  # Very recent

        manager._adjust_batch_size()

        assert manager._batch_size == 5  # No change due to timing

    def test_record_synthesis_time(self):
        """Test synthesis time recording"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        manager._record_synthesis_time(2.5)

        assert 2.5 in manager._synthesis_times

    @pytest.mark.asyncio
    async def test_start_preload_task_limit_reached(self):
        """Test preload task start when limit reached"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Add max preload tasks
        manager._preload_tasks = [Mock()] * 2

        await manager.start_preload_task()

        # Should not add more tasks
        assert len(manager._preload_tasks) == 2

    @pytest.mark.asyncio
    async def test_start_preload_task_no_unsynthesized(self):
        """Test preload task start when no unsynthesized items"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # All items synthesized
        manager.playlist = [("text1", 1, b"audio1"), ("text2", 2, b"audio2")]
        manager.current_index = 0

        await manager.start_preload_task()

        # Should not add tasks
        assert len(manager._preload_tasks) == 0

    @pytest.mark.asyncio
    async def test_start_batch_preload_predictive_mode(self):
        """Test batch preload start in predictive mode"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        integration.app.tts_smooth_mode = True

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "tts.preloading_mode": "predictive",
                "tts.preferred_engine": "edge-tts"
            }.get(key, default or "batch")

            # Mock predictive controller
            mock_controller = Mock()
            manager._predictive_controller = mock_controller
            mock_controller.start_monitoring = AsyncMock()

            await manager.start_batch_preload()

            mock_controller.start_monitoring.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_batch_preload_batch_mode(self):
        """Test batch preload start in batch mode"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.side_effect = lambda key, default=None: {
                "tts.preloading_mode": "batch",
                "tts.preferred_engine": "edge-tts"
            }.get(key, default or "batch")

            await manager.start_batch_preload()

            assert manager._batch_preload_task is not None

    @pytest.mark.asyncio
    async def test_start_batch_preload_already_running(self):
        """Test batch preload start when already running"""
        integration = MockTTSIntegration()
        manager = PlaylistManager(integration)

        # Set up already running task
        mock_task = Mock()
        mock_task.done.return_value = False
        manager._batch_preload_task = mock_task

        with patch('speakub.utils.config.get_config') as mock_config:
            mock_config.return_value = "batch"

            await manager.start_batch_preload()

            # Should not create new task
            assert manager._batch_preload_task == mock_task


if __name__ == '__main__':
    pytest.main([__file__])
