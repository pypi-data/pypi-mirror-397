#!/usr/bin/env python3
"""
Integration tests for TTS resource management and cleanup delegation.

Tests the integration between TTSIntegration and ResourceManager for unified
resource cleanup management.
"""

import tempfile
import os
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import pytest

from speakub.tts.integration import TTSIntegration
from speakub.utils.file_utils import get_resource_manager
from speakub.utils.config import ConfigManager


class TestTTSResourceManagementIntegration:
    """Integration tests for TTS and resource management."""

    def test_tts_cleanup_delegates_to_resource_manager(self):
        """Test that TTS cleanup_orphaned_temp_files delegates to ResourceManager."""
        # Create mock app conforming to AppInterface protocol
        mock_app = Mock()
        mock_app.tts_engine = None
        mock_app.tts_status = "STOPPED"
        mock_app.tts_smooth_mode = False
        mock_app.tts_volume = 100
        mock_app.tts_rate = 0
        mock_app.tts_pitch = "+0Hz"
        mock_app.viewport_content = None
        mock_app.tts_widget = None
        mock_app.query_one = Mock()
        mock_app.notify = Mock()
        mock_app.run_worker = Mock()
        mock_app.bell = Mock()

        # Create TTS Integration
        config_manager = ConfigManager()
        tts_integration = TTSIntegration(mock_app, config_manager)

        # Mock ResourceManager
        mock_rm = MagicMock()
        mock_rm.cleanup_temp_files_by_age.return_value = 42

        # Test delegation
        with patch('speakub.utils.file_utils.get_resource_manager', return_value=mock_rm):
            result = tts_integration.cleanup_orphaned_temp_files()

        assert result == 42
        mock_rm.cleanup_temp_files_by_age.assert_called_once_with(
            24)  # Default age


class TestUnifiedShutdownCoordinator:
    """Test the unified shutdown coordinator functionality."""

    def test_shutdown_coordinator_mode_configuration(self):
        """Test that ShutdownCoordinator properly configures different cleanup modes."""
        from speakub.tts.integration import ShutdownCoordinator

        coordinator = ShutdownCoordinator()

        # Test FAST mode configuration
        coordinator.set_cleanup_mode(ShutdownCoordinator.CleanupMode.FAST)
        fast_config = coordinator.get_mode_config()

        assert fast_config["total_timeout"] == 2.0
        assert fast_config["component_timeouts"]["predictive_controller"] == 0.5
        assert fast_config["force_cleanup_threshold"] == 0.8

        # Test GRACEFUL mode configuration
        coordinator.set_cleanup_mode(ShutdownCoordinator.CleanupMode.GRACEFUL)
        graceful_config = coordinator.get_mode_config()

        assert graceful_config["total_timeout"] == 10.0
        assert graceful_config["component_timeouts"]["predictive_controller"] == 3.0
        assert graceful_config["force_cleanup_threshold"] == 0.5

    def test_shutdown_coordinator_fast_mode_behavior(self):
        """Test that FAST mode performs immediate cleanup."""
        from speakub.tts.integration import ShutdownCoordinator
        import asyncio

        coordinator = ShutdownCoordinator()
        coordinator.set_cleanup_mode(ShutdownCoordinator.CleanupMode.FAST)

        # Create a mock TTS integration
        mock_tts = MagicMock()
        mock_tts._tts_active_tasks = set()
        mock_tts.playlist_manager.reset = MagicMock()
        mock_tts._reset_async_events = MagicMock()
        mock_tts.cleanup_orphaned_temp_files = MagicMock(return_value=5)

        async def test_fast_cleanup():
            result = await coordinator.unified_cleanup(mock_tts)

            # Verify FAST mode results
            assert result["mode"] == "fast"
            assert result["status"] == "completed"
            assert result["method"] == "force_reset"

            # Verify that cleanup methods were called
            mock_tts.playlist_manager.reset.assert_called_once()
            mock_tts._reset_async_events.assert_called_once()
            mock_tts.cleanup_orphaned_temp_files.assert_called_once()

        asyncio.run(test_fast_cleanup())

    def test_unified_stop_speaking_uses_fast_mode(self):
        """Test that stop_speaking uses FAST cleanup mode."""
        # Create mock app conforming to AppInterface protocol
        mock_app = Mock()
        mock_app.tts_engine = None
        mock_app.tts_status = "PLAYING"
        mock_app.tts_smooth_mode = False
        mock_app.tts_volume = 100
        mock_app.tts_rate = 0
        mock_app.tts_pitch = "+0Hz"
        mock_app.viewport_content = None
        mock_app.tts_widget = None
        mock_app.query_one = Mock()
        mock_app.notify = Mock()
        mock_app.run_worker = Mock()
        mock_app.bell = Mock()

        # Create TTS Integration
        config_manager = ConfigManager()
        tts_integration = TTSIntegration(mock_app, config_manager)

        # Mock the playback manager
        tts_integration.playback_manager.stop_playback = MagicMock()

        # Mock event loop to avoid actual async execution
        with patch.object(tts_integration, '_get_event_loop', return_value=None):
            # Call stop_speaking
            tts_integration.stop_speaking(is_pause=False)

            # Verify playback manager was called
            tts_integration.playback_manager.stop_playback.assert_called_once_with(
                is_pause=False)


if __name__ == "__main__":
    pytest.main([__file__])
