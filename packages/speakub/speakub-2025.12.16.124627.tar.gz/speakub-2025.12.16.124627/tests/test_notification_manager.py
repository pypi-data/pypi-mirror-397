#!/usr/bin/env python3
"""
Unit tests for notification_manager.py module.
"""

import time
from unittest.mock import patch, MagicMock, call
import pytest
from speakub.utils.notification_manager import NotificationManager


class TestNotificationManager:
    """Test cases for NotificationManager class."""

    def test_notification_manager_initialization(self):
        """Test NotificationManager initialization."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        assert manager.app == mock_app
        assert manager._last_notifications == {}
        assert isinstance(manager._notification_cooldowns, dict)
        assert manager._performance_history == []
        assert manager._user_activity_patterns == {}

    @patch("speakub.utils.notification_manager.logger")
    def test_start_monitoring(self, mock_logger):
        """Test start_monitoring method."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        manager.start_monitoring()

        # Verify set_interval calls
        expected_calls = [
            call(60.0, manager._check_system_health),
            call(120.0, manager._check_tts_performance),
            call(180.0, manager._check_resource_usage),
            call(300.0, manager._check_user_patterns),
        ]
        mock_app.set_interval.assert_has_calls(expected_calls)
        mock_logger.debug.assert_called_with(
            "Intelligent notification system started")

    def test_can_send_notification_first_time(self):
        """Test _can_send_notification for first-time notification."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Should allow first notification
        assert manager._can_send_notification("test_type") is True

    def test_can_send_notification_within_cooldown(self):
        """Test _can_send_notification within cooldown period."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Send notification
        manager._send_notification("test", notification_type="test_type")

        # Should not allow immediate resend
        assert manager._can_send_notification("test_type") is False

    def test_can_send_notification_after_cooldown(self):
        """Test _can_send_notification after cooldown period."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Send notification
        manager._send_notification("test", notification_type="test_type")

        # Manually set last notification time to be old enough
        # 70 seconds ago
        manager._last_notifications["test_type"] = time.time() - 70

        # Should allow after cooldown
        assert manager._can_send_notification("test_type") is True

    @patch("speakub.utils.notification_manager.time.time")
    def test_send_notification_allowed(self, mock_time):
        """Test _send_notification when allowed."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        mock_time.return_value = 1000.0

        manager._send_notification("test message", "warning", "test_type")

        # Verify notification was sent
        mock_app.notify.assert_called_once_with(
            "test message", severity="warning", timeout=5)
        assert manager._last_notifications["test_type"] == 1000.0

    def test_send_notification_blocked(self):
        """Test _send_notification when blocked by cooldown."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Send first notification
        manager._send_notification(
            "test message", notification_type="test_type")

        # Try to send again immediately
        manager._send_notification(
            "test message 2", notification_type="test_type")

        # Should only be called once
        assert mock_app.notify.call_count == 1

    @patch("speakub.utils.file_utils.get_resource_manager")
    def test_check_system_health_high_memory(self, mock_get_rm):
        """Test _check_system_health with high memory usage."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        mock_rm = MagicMock()
        mock_rm.get_resource_stats.return_value = {
            'memory_rss_mb': 450,
            'temp_files_count': 5
        }
        mock_get_rm.return_value = mock_rm

        manager._check_system_health()

        # Should send warning notification
        mock_app.notify.assert_called_once()
        args, kwargs = mock_app.notify.call_args
        assert "High memory usage" in args[0]
        assert kwargs["severity"] == "warning"

    @patch("speakub.utils.file_utils.get_resource_manager")
    def test_check_system_health_many_temp_files(self, mock_get_rm):
        """Test _check_system_health with many temp files."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        mock_rm = MagicMock()
        mock_rm.get_resource_stats.return_value = {
            'memory_rss_mb': 200,
            'temp_files_count': 25
        }
        mock_get_rm.return_value = mock_rm

        manager._check_system_health()

        # Should send info notification about temp files
        mock_app.notify.assert_called_once()
        args, kwargs = mock_app.notify.call_args
        assert "temporary files" in args[0]
        assert kwargs["severity"] == "info"

    @patch("speakub.utils.file_utils.get_resource_manager")
    def test_check_system_health_exception(self, mock_get_rm):
        """Test _check_system_health with exception."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        mock_get_rm.side_effect = Exception("Test exception")

        # Should not raise exception
        manager._check_system_health()

        # Should not send notification
        mock_app.notify.assert_not_called()

    def test_check_tts_performance_no_integration(self):
        """Test _check_tts_performance without TTS integration."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # App without TTS integration
        manager._check_tts_performance()

        # Should not send any notifications
        mock_app.notify.assert_not_called()

    def test_check_tts_performance_large_queue(self):
        """Test _check_tts_performance with large queue."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Mock TTS integration
        mock_tts_integration = MagicMock()
        mock_playlist_manager = MagicMock()
        mock_playlist_manager.get_preloading_stats.return_value = {
            'queue_size': 15,
            'batch_size': 5
        }
        mock_tts_integration.playlist_manager = mock_playlist_manager
        mock_app.tts_integration = mock_tts_integration

        manager._check_tts_performance()

        # Should send notification about large queue
        mock_app.notify.assert_called_once()
        args, kwargs = mock_app.notify.call_args
        assert "Large TTS queue" in args[0]

    def test_check_tts_performance_circuit_breaker_open(self):
        """Test _check_tts_performance with open circuit breaker."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Mock TTS integration with circuit breaker
        mock_tts_integration = MagicMock()
        mock_cb = MagicMock()
        mock_cb.get_state.return_value = {'state': 'open'}
        mock_tts_integration.circuit_breaker = mock_cb
        mock_app.tts_integration = mock_tts_integration

        # Ensure no cooldown for this notification type
        manager._last_notifications = {}

        manager._check_tts_performance()

        # Should send warning about circuit breaker
        mock_app.notify.assert_called_once()
        args, kwargs = mock_app.notify.call_args
        assert "circuit breaker is open" in args[0]
        assert kwargs["severity"] == "warning"

    @patch("speakub.utils.file_utils.get_resource_manager")
    def test_check_resource_usage_low_memory(self, mock_get_rm):
        """Test _check_resource_usage with low system memory."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        mock_rm = MagicMock()
        mock_rm.get_resource_stats.return_value = {
            'total_temp_files_size_mb': 100,
            'system_memory_available_gb': 0.3
        }
        mock_get_rm.return_value = mock_rm

        manager._check_resource_usage()

        # Should send error notification about low memory
        mock_app.notify.assert_called_once()
        args, kwargs = mock_app.notify.call_args
        assert "Low system memory" in args[0]
        assert kwargs["severity"] == "error"

    def test_check_user_patterns_tts_stopped(self):
        """Test _check_user_patterns with TTS stopped."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        mock_app.tts_status = "STOPPED"

        # Mock inactive time
        with patch.object(manager, '_get_user_inactive_time', return_value=400):
            manager._check_user_patterns()

        # Should send notification to resume
        mock_app.notify.assert_called_once()
        args, kwargs = mock_app.notify.call_args
        assert "Ready to continue reading" in args[0]

    def test_get_user_inactive_time(self):
        """Test _get_user_inactive_time method."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Currently returns 0.0
        result = manager._get_user_inactive_time()
        assert result == 0.0

    def test_detect_reading_speed_pattern(self):
        """Test _detect_reading_speed_pattern method."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Currently returns False
        result = manager._detect_reading_speed_pattern()
        assert result is False

    def test_record_tts_performance(self):
        """Test record_tts_performance method."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        performance_data = {"synthesis_time": 1.5, "success": True}

        with patch("speakub.utils.notification_manager.time.time", return_value=1000.0):
            manager.record_tts_performance(performance_data)

        assert len(manager._performance_history) == 1
        entry = manager._performance_history[0]
        assert entry["synthesis_time"] == 1.5
        assert entry["timestamp"] == 1000.0

    def test_record_tts_performance_limit_history(self):
        """Test record_tts_performance limits history size."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        # Add 101 entries
        for i in range(101):
            manager.record_tts_performance({"test": i})

        # Should only keep last 100
        assert len(manager._performance_history) == 100

    def test_get_performance_insights_empty_history(self):
        """Test get_performance_insights with empty history."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        result = manager.get_performance_insights()
        assert result == {}

    def test_get_performance_insights_with_data(self):
        """Test get_performance_insights with performance data."""
        mock_app = MagicMock()
        manager = NotificationManager(mock_app)

        current_time = time.time()

        # Add some performance data within last hour
        manager._performance_history = [
            {"synthesis_time": 1.0, "timestamp": current_time - 100},
            {"synthesis_time": 2.0, "timestamp": current_time - 200},
            {"synthesis_time": 3.0, "timestamp": current_time - 3700},  # Too old
        ]

        result = manager.get_performance_insights()

        assert "avg_synthesis_time" in result
        assert result["avg_synthesis_time"] == 1.5  # Average of 1.0 and 2.0
        assert result["total_requests"] == 2
        assert result["performance_trend"] == "stable"


if __name__ == "__main__":
    pytest.main([__file__])
