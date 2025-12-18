"""
Tests for speakub.tts.playback_manager module
"""

import threading
from unittest.mock import AsyncMock, Mock, patch

import pytest

from speakub.tts.playback_manager import PlaybackManager


class MockAppInterface:
    """Mock implementation of AppInterface for testing."""

    def __init__(self):
        self.tts_status = "IDLE"
        self.tts_engine = None
        self.tts_smooth_mode = False

    def set_tts_status(self, status):
        self.tts_status = status


class MockTTSIntegration:
    """Mock TTS integration for testing."""

    def __init__(self):
        self.app = MockAppInterface()
        self.tts_stop_requested = threading.Event()
        self.tts_pause_requested = threading.Event()
        self.tts_lock = threading.RLock()
        self.tts_thread_active = False


class MockPlaylistManager:
    """Mock playlist manager for testing."""

    def __init__(self):
        self._predictive_controller = Mock()
        self._predictive_controller.resume_scheduling = Mock()
        self._predictive_controller.pause_scheduling = Mock()

    def reset(self):
        pass


class TestPlaybackManager:
    """Test PlaybackManager class"""

    def test_initialization(self):
        """Test playback manager initialization"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        assert manager.tts_integration == integration
        assert manager.app == integration.app
        assert manager.playlist_manager == playlist_manager
        assert manager.stop_event == integration.tts_stop_requested
        assert manager.lock == integration.tts_lock
        assert manager._current_task is None
        assert manager._task_lock is not None

    @patch('speakub.tts.ui.runners.tts_runner_serial')
    @patch('asyncio.create_task')
    def test_start_playback_serial_mode(self, mock_create_task, mock_runner):
        """Test starting playback in serial mode"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up serial mode (not smooth mode)
        integration.app.tts_smooth_mode = False

        # Mock asyncio.create_task
        mock_task = Mock()
        mock_create_task.return_value = mock_task

        manager.start_playback()

        assert integration.app.tts_status == "PLAYING"
        assert integration.tts_thread_active is True
        assert manager._current_task == mock_task
        mock_create_task.assert_called_once()

    @patch('speakub.tts.ui.runners.tts_runner_parallel')
    @patch('asyncio.create_task')
    @patch('asyncio.run_coroutine_threadsafe')
    def test_start_playback_parallel_mode(self, mock_run_coroutine,
                                          mock_create_task, mock_runner):
        """Test starting playback in parallel mode"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up parallel mode (smooth mode)
        integration.app.tts_smooth_mode = True

        # Mock TTS engine with event loop
        mock_engine = Mock()
        mock_event_loop = Mock()
        mock_event_loop.is_closed.return_value = False
        mock_engine._event_loop = mock_event_loop
        integration.app.tts_engine = mock_engine

        # Mock playlist manager batch preload
        playlist_manager.start_batch_preload = AsyncMock()

        # Mock asyncio.create_task
        mock_task = Mock()
        mock_create_task.return_value = mock_task

        manager.start_playback()

        assert integration.app.tts_status == "PLAYING"
        assert integration.tts_thread_active is True
        assert manager._current_task == mock_task
        mock_run_coroutine.assert_called_once()
        mock_create_task.assert_called_once()

    def test_start_playback_already_playing(self):
        """Test starting playback when already playing"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up as already playing
        integration.tts_thread_active = True

        # Mock is_playing to return True
        with patch.object(manager, 'is_playing', return_value=True):
            manager.start_playback()

            # Should not change status or start new playback
            assert integration.app.tts_status == "IDLE"

    def test_stop_playback_not_active(self):
        """Test stopping playback when not active"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up as not active
        integration.tts_thread_active = False
        integration.app.tts_status = "IDLE"

        manager.stop_playback()

        assert integration.app.tts_status == "STOPPED"

    def test_stop_playback_pause_mode(self):
        """Test stopping playback in pause mode"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up as active
        integration.tts_thread_active = True
        integration.app.tts_status = "PLAYING"

        # Mock TTS engine
        mock_engine = Mock()
        integration.app.tts_engine = mock_engine

        manager.stop_playback(is_pause=True)

        assert integration.app.tts_status == "PAUSED"
        assert integration.tts_thread_active is False
        mock_engine.pause.assert_called_once()

    def test_stop_playback_stop_mode(self):
        """Test stopping playback in stop mode"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up as active
        integration.tts_thread_active = True
        integration.app.tts_status = "PLAYING"

        # Mock TTS engine
        mock_engine = Mock()
        integration.app.tts_engine = mock_engine

        # Mock playlist manager
        playlist_manager.reset = Mock()

        manager.stop_playback(is_pause=False)

        assert integration.app.tts_status == "STOPPED"
        assert integration.tts_thread_active is False
        mock_engine.stop.assert_called_once()
        playlist_manager.reset.assert_called_once()

    def test_pause_playback(self):
        """Test pausing playback"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up as active
        integration.tts_thread_active = True

        # Mock TTS engine
        mock_engine = Mock()
        integration.app.tts_engine = mock_engine

        manager.pause_playback()

        assert integration.app.tts_status == "PAUSED"
        assert integration.tts_pause_requested.is_set()
        mock_engine.pause.assert_called_once()

    def test_pause_playback_not_active(self):
        """Test pausing playback when not active"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Set up as not active
        integration.tts_thread_active = False

        manager.pause_playback()

        # Should not change status
        assert integration.app.tts_status == "IDLE"

    def test_is_playing_not_playing(self):
        """Test is_playing when not playing"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        assert manager.is_playing() is False

    def test_is_playing_with_active_task(self):
        """Test is_playing with active task"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Mock active task
        mock_task = Mock()
        mock_task.done.return_value = False
        manager._current_task = mock_task
        integration.tts_thread_active = True

        assert manager.is_playing() is True

    def test_is_playing_with_completed_task(self):
        """Test is_playing with completed task"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Mock completed task
        mock_task = Mock()
        mock_task.done.return_value = True
        manager._current_task = mock_task

        assert manager.is_playing() is False

    @patch('asyncio.create_task')
    def test_shutdown(self, mock_create_task):
        """Test shutdown"""
        integration = MockTTSIntegration()
        playlist_manager = MockPlaylistManager()

        manager = PlaybackManager(integration, playlist_manager)

        # Mock task
        mock_task = Mock()
        mock_task.done.return_value = False
        manager._current_task = mock_task
        integration.tts_thread_active = True

        # Mock create_task for shutdown_async
        mock_shutdown_task = Mock()
        mock_create_task.return_value = mock_shutdown_task

        manager.shutdown()

        # Should cancel the current task via the async shutdown
        assert integration.app.tts_status == "STOPPED"
        mock_create_task.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
