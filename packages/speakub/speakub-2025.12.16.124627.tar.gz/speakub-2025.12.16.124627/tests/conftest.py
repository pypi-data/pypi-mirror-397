"""
Shared test fixtures and utilities for SpeakUB tests.
"""

import pytest
from unittest.mock import Mock, MagicMock


class MockConfigManager:
    """Mock ConfigManager for testing that provides consistent default behavior."""

    def __init__(self, **overrides):
        """Initialize with optional overrides."""
        self._data = {
            "language": "en",
            "font_size": 12,
            "tts": {
                "rate": 0,
                "volume": 100,
                "pitch": "+0Hz",
                "preferred_engine": "edge-tts",
                "smooth_mode": False,
                "smooth_synthesis_delay": 1.2,
            },
            "edge-tts": {
                "volume": 1.0,
                "playback_speed": 1.0,
                "smooth_synthesis_delay": 1.2,
            },
            "nanmai": {
                "volume": 1.0,
                "playback_speed": 1.0,
                "smooth_synthesis_delay": 1.2,
            },
            "gtts": {
                "volume": 1.0,
                "playback_speed": 1.5,
                "smooth_synthesis_delay": 1.5,
            },
            "cache": {
                "auto_detect_hardware": True,
                "chapter_cache_size": 50,
                "width_cache_size": 1000,
            },
            "network": {
                "recovery_timeout_minutes": 30,
                "connectivity_test_host": "8.8.8.8",
            },
        }
        # Apply overrides
        self._deep_update(self._data, overrides)

    def _deep_update(self, base, update):
        """Deep update nested dictionaries."""
        if update is None or not isinstance(update, dict):
            return

        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, key=None, default=None):
        """Get configuration value."""
        if key is None:
            return self._data

        # Navigate nested dictionary
        keys = key.split(".")
        current = self._data

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set_override(self, key, value):
        """Set runtime override."""
        keys = key.split(".")
        current = self._data

        # Navigate to parent of target key
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value

    def clear_override(self, key):
        """Clear runtime override."""
        keys = key.split(".")
        current = self._data

        try:
            for k in keys[:-1]:
                current = current[k]
            del current[keys[-1]]
        except KeyError:
            pass

    def set(self, key, value):
        """Set and persist configuration value."""
        self.set_override(key, value)


@pytest.fixture
def mock_config_manager():
    """Provide a mock ConfigManager with default test values."""
    return MockConfigManager()


@pytest.fixture
def mock_config_manager_custom():
    """Provide a mock ConfigManager with custom test values."""
    return MockConfigManager(
        tts={
            "rate": 10,
            "volume": 80,
            "preferred_engine": "nanmai",
            "smooth_mode": True,
        }
    )


@pytest.fixture
def mock_app_interface(mock_config_manager):
    """Provide a mock AppInterface for testing."""
    app = Mock()
    app.tts_engine = Mock()
    app.tts_status = "IDLE"
    app.tts_rate = 0
    app.tts_volume = 100
    app.tts_pitch = "+0Hz"
    app.tts_smooth_mode = False
    app.notify = Mock()
    return app
