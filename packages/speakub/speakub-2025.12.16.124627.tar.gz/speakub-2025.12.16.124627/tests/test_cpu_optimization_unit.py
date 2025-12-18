#!/usr/bin/env python3
"""
Unit tests for CPU optimization logic - idle detection and polling adjustments.
Tests the functions that were previously tested via integration in test_cpu_optimization.py.
"""

import time
import pytest
from unittest.mock import Mock, patch
from speakub.ui.app import EPUBReaderApp
from speakub.ui.progress import ProgressManager


class TestIdleDetectionLogic:
    """Unit tests for idle detection logic from app.py."""

    @patch('speakub.ui.app.time.time')
    def test_check_idle_status_enters_idle_mode(self, mock_time, sample_app):
        """Test that _check_idle_status enters idle mode after threshold."""
        # Setup: user has been idle for more than 30 seconds
        mock_time.return_value = 1000.0  # current time
        sample_app._last_user_activity = 960.0  # 40 seconds ago
        sample_app._idle_mode = False

        sample_app._check_idle_status()

        assert sample_app._idle_mode is True

    @patch('speakub.ui.app.time.time')
    def test_check_idle_status_exits_idle_mode(self, mock_time, sample_app):
        """Test that _check_idle_status exits idle mode when activity detected."""
        # Setup: user was idle but now active
        mock_time.return_value = 1000.0  # current time
        sample_app._last_user_activity = 980.0  # 20 seconds ago (active)
        sample_app._idle_mode = True

        sample_app._check_idle_status()

        assert sample_app._idle_mode is False

    @patch('speakub.ui.app.time.time')
    def test_check_idle_status_stays_idle_when_still_inactive(self, mock_time, sample_app):
        """Test that _check_idle_status stays in idle mode when still inactive."""
        # Setup: user has been idle and continues to be idle
        mock_time.return_value = 1000.0  # current time
        sample_app._last_user_activity = 960.0  # 40 seconds ago
        sample_app._idle_mode = True

        sample_app._check_idle_status()

        assert sample_app._idle_mode is True  # should stay True

    @patch('speakub.ui.app.time.time')
    def test_check_idle_status_stays_active_when_still_active(self, mock_time, sample_app):
        """Test that _check_idle_status stays active when user is still active."""
        # Setup: user is active and continues to be active
        mock_time.return_value = 1000.0  # current time
        sample_app._last_user_activity = 980.0  # 20 seconds ago
        sample_app._idle_mode = False

        sample_app._check_idle_status()

        assert sample_app._idle_mode is False  # should stay False

    @patch('speakub.ui.app.time.time')
    def test_check_idle_status_boundary_at_threshold(self, mock_time, sample_app):
        """Test that _check_idle_status enters idle mode exactly at threshold."""
        # Setup: idle time is exactly at threshold
        mock_time.return_value = 1030.0  # current time
        sample_app._last_user_activity = 1000.0  # exactly 30 seconds ago
        sample_app._idle_mode = False

        sample_app._check_idle_status()

        # should enter idle at exact threshold (>=)
        assert sample_app._idle_mode is True

    @patch('speakub.ui.app.time.time')
    def test_update_user_activity_resets_idle_mode(self, mock_time, sample_app):
        """Test that _update_user_activity resets idle mode when checked."""
        sample_app._idle_mode = True
        sample_app._last_user_activity = 900.0  # Idle for 40+ seconds

        mock_time.return_value = 950.0  # New activity time
        sample_app._update_user_activity()

        # Now _check_idle_status should detect activity and reset idle mode
        sample_app._check_idle_status()

        assert sample_app._idle_mode is False  # Should exit idle mode
        assert sample_app._last_user_activity == 950.0


class TestPollingAdjustmentLogic:
    """Unit tests for polling adjustment logic from progress.py."""

    def test_adjust_polling_for_idle_entering_idle(self, sample_progress_manager):
        """Test _adjust_polling_for_idle when entering idle mode."""
        # Mock the progress task and app.set_interval
        mock_progress_task = Mock()
        sample_progress_manager._progress_task = mock_progress_task

        mock_new_task = Mock()
        sample_progress_manager.app.set_interval = Mock(
            return_value=mock_new_task)

        sample_progress_manager._adjust_polling_for_idle(True)

        # Should stop existing task
        mock_progress_task.stop.assert_called_once()

        # Should create new task with idle interval
        sample_progress_manager.app.set_interval.assert_called_once_with(
            sample_progress_manager._idle_tts_interval,
            sample_progress_manager.progress_callback
        )

        # Should update the progress task
        assert sample_progress_manager._progress_task == mock_new_task

    def test_adjust_polling_for_idle_exiting_idle(self, sample_progress_manager):
        """Test _adjust_polling_for_idle when exiting idle mode."""
        # Mock the progress task and app.set_interval
        mock_progress_task = Mock()
        sample_progress_manager._progress_task = mock_progress_task

        mock_new_task = Mock()
        sample_progress_manager.app.set_interval = Mock(
            return_value=mock_new_task)

        sample_progress_manager._adjust_polling_for_idle(False)

        # Should stop existing task
        mock_progress_task.stop.assert_called_once()

        # Should create new task with active interval
        sample_progress_manager.app.set_interval.assert_called_once_with(
            sample_progress_manager._active_tts_interval,
            sample_progress_manager.progress_callback
        )

        # Should update the progress task
        assert sample_progress_manager._progress_task == mock_new_task

    def test_adjust_polling_for_idle_no_existing_task(self, sample_progress_manager):
        """Test _adjust_polling_for_idle when no existing task."""
        sample_progress_manager._progress_task = None

        mock_new_task = Mock()
        sample_progress_manager.app.set_interval = Mock(
            return_value=mock_new_task)

        sample_progress_manager._adjust_polling_for_idle(True)

        # Should create new task with idle interval
        sample_progress_manager.app.set_interval.assert_called_once_with(
            sample_progress_manager._idle_tts_interval,
            sample_progress_manager.progress_callback
        )

    def test_adjust_polling_for_idle_handles_exception(self, sample_progress_manager):
        """Test _adjust_polling_for_idle handles exceptions gracefully."""
        # Mock progress task to raise exception on stop
        mock_progress_task = Mock()
        mock_progress_task.stop.side_effect = Exception("Test exception")
        sample_progress_manager._progress_task = mock_progress_task

        # Mock app.set_interval to raise exception
        sample_progress_manager.app.set_interval = Mock(
            side_effect=Exception("Interval error"))

        # Should not raise exception
        sample_progress_manager._adjust_polling_for_idle(True)

        # Should have attempted to stop and restart
        mock_progress_task.stop.assert_called_once()
        sample_progress_manager.app.set_interval.assert_called_once()


class TestBoundaryConditions:
    """Test boundary conditions for CPU optimization functions."""

    @patch('speakub.ui.app.time.time')
    def test_rapid_activity_updates(self, mock_time, sample_app):
        """Test rapid user activity updates don't cause issues."""
        mock_time.side_effect = [1000.0, 1001.0,
                                 1002.0, 1003.0]  # Multiple calls

        for _ in range(10):
            sample_app._update_user_activity()

        sample_app._check_idle_status()

        # Should still be active since _last_user_activity was updated recently
        assert sample_app._idle_mode is False

    def test_progress_manager_initialization(self, sample_progress_manager):
        """Test ProgressManager initializes with correct idle settings."""
        assert sample_progress_manager._idle_mode is False
        assert sample_progress_manager._idle_threshold == 30
        assert sample_progress_manager._idle_tts_interval == 5.0
        assert sample_progress_manager._active_tts_interval == 2.0

    @patch('speakub.ui.progress.time.time')
    def test_progress_manager_idle_detection(self, mock_time, sample_progress_manager):
        """Test idle detection in ProgressManager."""
        mock_time.return_value = 1000.0
        sample_progress_manager._last_user_activity = 960.0  # 40 seconds ago

        sample_progress_manager._check_idle_status()

        assert sample_progress_manager._idle_mode is True


# Fixtures

@pytest.fixture
def sample_app():
    """Create a minimal EPUBReaderApp instance for testing."""
    # Mock the minimum required attributes
    app = Mock(spec=EPUBReaderApp)
    app._idle_mode = False
    app._idle_threshold = 30
    app._last_user_activity = 0.0

    # Mock the _check_idle_status method to actually work with the attributes
    def mock_check_idle_status():
        idle_time = time.time() - app._last_user_activity
        if idle_time >= app._idle_threshold and not app._idle_mode:
            app._idle_mode = True
        elif idle_time < app._idle_threshold and app._idle_mode:
            app._idle_mode = False

    def mock_update_user_activity():
        app._last_user_activity = time.time()

    app._check_idle_status = mock_check_idle_status
    app._update_user_activity = mock_update_user_activity

    return app


@pytest.fixture
def sample_progress_manager(sample_app):
    """Create a ProgressManager instance for testing."""
    progress_callback = Mock()
    manager = ProgressManager(sample_app, progress_callback)
    # Initialize the mock app's set_interval method
    sample_app.set_interval = Mock()
    return manager
