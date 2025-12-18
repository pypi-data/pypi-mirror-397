"""
Tests for speakub.utils.config module
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from speakub.utils.config import (
    ConfigManager,
    DEFAULT_CONFIG,
    detect_hardware_profile,
    get_adaptive_cache_config,
    get_cache_config,
    get_cache_sizes_for_profile,
    get_network_config,
    get_smooth_synthesis_delay,
    get_tts_config,
    load_config,
    load_pronunciation_corrections,
    save_config,
    save_pronunciation_corrections,
    save_tts_config,
    validate_tts_config,
)


class TestConfigManager:
    """Test ConfigManager class"""

    def test_config_manager_initialization(self):
        """Test ConfigManager initialization"""
        manager = ConfigManager()

        assert manager._overrides == {}
        assert manager._config_cache is None
        assert manager._config_mtime is None

    def test_get_full_config(self):
        """Test getting full configuration"""
        manager = ConfigManager()

        config = manager.get()

        assert isinstance(config, dict)
        assert "tts" in config
        assert "language" in config

    def test_get_specific_key(self):
        """Test getting specific configuration key"""
        manager = ConfigManager()

        language = manager.get("language")

        assert language == "en"

    def test_get_nested_key(self):
        """Test getting nested configuration key"""
        manager = ConfigManager()

        tts_rate = manager.get("tts.rate")

        # Should return the configured value (may be from user config, not just defaults)
        assert isinstance(tts_rate, int)
        assert tts_rate >= 0  # Rate should be non-negative

    def test_get_nonexistent_key(self):
        """Test getting nonexistent key"""
        manager = ConfigManager()

        value = manager.get("nonexistent.key", "default")

        assert value == "default"

    def test_set_override(self):
        """Test setting runtime override"""
        manager = ConfigManager()

        manager.set_override("test.key", "test_value")

        assert manager._overrides["test"]["key"] == "test_value"

        # Test that override takes effect
        value = manager.get("test.key")
        assert value == "test_value"

    def test_clear_override(self):
        """Test clearing runtime override"""
        manager = ConfigManager()

        manager.set_override("test.key", "test_value")
        manager.clear_override("test.key")

        assert "test" not in manager._overrides

    def test_deep_update(self):
        """Test deep dictionary update"""
        manager = ConfigManager()

        base = {"a": {"b": 1, "c": 2}}
        update = {"a": {"b": 3, "d": 4}}

        manager._deep_update(base, update)

        assert base == {"a": {"b": 3, "c": 2, "d": 4}}

    @patch.dict(os.environ, {"SPEAKUB_TTS_RATE": "10", "SPEAKUB_LANGUAGE": "zh"})
    def test_apply_env_overrides(self):
        """Test environment variable overrides"""
        manager = ConfigManager()

        config = {"tts": {"rate": 0}, "language": "en"}

        manager._apply_env_overrides(config)

        assert config["tts"]["rate"] == 10
        assert config["language"] == "zh"

    def test_parse_env_value(self):
        """Test environment variable value parsing"""
        manager = ConfigManager()

        assert manager._parse_env_value("true") is True
        assert manager._parse_env_value("false") is False
        assert manager._parse_env_value("42") == 42
        assert manager._parse_env_value("3.14") == 3.14
        assert manager._parse_env_value("hello") == "hello"

    def test_set_nested_value(self):
        """Test setting nested dictionary value"""
        manager = ConfigManager()

        config = {}

        manager._set_nested_value(config, "a.b.c", "value")

        assert config == {"a": {"b": {"c": "value"}}}


class TestHardwareDetection:
    """Test hardware detection functions"""

    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    def test_detect_hardware_profile_low_end(self, mock_cpu_freq, mock_cpu_count, mock_memory):
        """Test low-end hardware detection"""
        mock_memory.return_value.total = 2 * (1024**3)  # 2GB
        mock_cpu_count.return_value = 2
        mock_cpu_freq.return_value.max = 2000

        profile = detect_hardware_profile()

        assert profile == "low_end"

    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    def test_detect_hardware_profile_mid_range(self, mock_cpu_freq, mock_cpu_count, mock_memory):
        """Test mid-range hardware detection"""
        mock_memory.return_value.total = 6 * (1024**3)  # 6GB
        mock_cpu_count.return_value = 4
        mock_cpu_freq.return_value.max = 3000

        profile = detect_hardware_profile()

        assert profile == "mid_range"

    @patch('psutil.virtual_memory')
    @patch('psutil.cpu_count')
    @patch('psutil.cpu_freq')
    def test_detect_hardware_profile_high_end(self, mock_cpu_freq, mock_cpu_count, mock_memory):
        """Test high-end hardware detection"""
        mock_memory.return_value.total = 16 * (1024**3)  # 16GB
        mock_cpu_count.return_value = 8
        mock_cpu_freq.return_value.max = 4000

        profile = detect_hardware_profile()

        assert profile == "high_end"

    def test_get_cache_sizes_for_profile(self):
        """Test cache size retrieval for different profiles"""
        low_end = get_cache_sizes_for_profile("low_end")
        assert low_end == {"chapter_cache_size": 10, "width_cache_size": 200}

        mid_range = get_cache_sizes_for_profile("mid_range")
        assert mid_range == {"chapter_cache_size": 25, "width_cache_size": 500}

        high_end = get_cache_sizes_for_profile("high_end")
        assert high_end == {"chapter_cache_size": 50, "width_cache_size": 1000}

        unknown = get_cache_sizes_for_profile("unknown")
        assert unknown == {"chapter_cache_size": 25,
                           "width_cache_size": 500}  # mid_range default

    @patch('speakub.utils.config.detect_hardware_profile')
    def test_get_adaptive_cache_config(self, mock_detect):
        """Test adaptive cache configuration"""
        mock_detect.return_value = "high_end"

        config = get_adaptive_cache_config()

        assert config == {"chapter_cache_size": 50, "width_cache_size": 1000}


class TestCacheConfig:
    """Test cache configuration functions"""

    def test_get_cache_config_auto_detect(self):
        """Test cache config with auto-detection"""
        config = {
            "cache": {
                "auto_detect_hardware": True,
                "chapter_cache_size": 30,  # Manual override
            }
        }

        with patch('speakub.utils.config.get_adaptive_cache_config') as mock_adaptive:
            mock_adaptive.return_value = {
                "chapter_cache_size": 50, "width_cache_size": 1000}

            result = get_cache_config(config)

            assert result["chapter_cache_size"] == 30  # Manual override
            assert result["width_cache_size"] == 1000  # Auto-detected

    def test_get_cache_config_manual(self):
        """Test cache config with manual settings"""
        config = {
            "cache": {
                "auto_detect_hardware": False,
                "chapter_cache_size": 30,
                "width_cache_size": 500,
            }
        }

        result = get_cache_config(config)

        assert result["chapter_cache_size"] == 30
        assert result["width_cache_size"] == 500


class TestTTSConfig:
    """Test TTS configuration functions"""

    def test_get_tts_config(self):
        """Test TTS config retrieval"""
        config = {"tts": {"rate": 10, "volume": 80}}

        tts_config = get_tts_config(config)

        assert tts_config["rate"] == 10
        assert tts_config["volume"] == 80
        # Should include defaults for missing keys
        assert "smooth_mode" in tts_config

    def test_validate_tts_config(self):
        """Test TTS config validation"""
        config = {
            "rate": 150,  # Too high
            "volume": -10,  # Too low
            "pitch": "+100Hz",  # Too high
            "smooth_mode": "not_boolean",  # Wrong type
        }

        validated = validate_tts_config(config)

        assert validated["rate"] == 100  # Clamped
        assert validated["volume"] == 0  # Clamped
        assert validated["pitch"] == "+50Hz"  # Clamped
        assert validated["smooth_mode"] is True  # Converted to bool

    def test_get_smooth_synthesis_delay_engine_specific(self):
        """Test smooth synthesis delay with engine-specific setting"""
        config = {
            "nanmai": {"smooth_synthesis_delay": 0.8},
            "tts": {"smooth_synthesis_delay": 1.2}
        }

        delay = get_smooth_synthesis_delay("nanmai", config)

        assert delay == 0.8

    def test_get_smooth_synthesis_delay_global_fallback(self):
        """Test smooth synthesis delay with global fallback"""
        config = {
            "tts": {"smooth_synthesis_delay": 1.2}
        }

        delay = get_smooth_synthesis_delay("edge-tts", config)

        assert delay == 1.2

    def test_get_smooth_synthesis_delay_default_fallback(self):
        """Test smooth synthesis delay with default fallback"""
        config = {}

        delay = get_smooth_synthesis_delay("gtts", config)

        assert delay == 1.2


class TestNetworkConfig:
    """Test network configuration functions"""

    def test_get_network_config(self):
        """Test network config retrieval"""
        config = {
            "network": {
                "recovery_timeout_minutes": 60,
                "connectivity_test_host": "1.1.1.1"
            }
        }

        network_config = get_network_config(config)

        assert network_config["recovery_timeout_minutes"] == 60
        assert network_config["connectivity_test_host"] == "1.1.1.1"
        # Should include defaults for missing keys
        assert "recovery_check_interval" in network_config


class TestPronunciationCorrections:
    """Test pronunciation corrections functions"""

    def test_save_pronunciation_corrections_empty(self):
        """Test saving empty pronunciation corrections"""
        with tempfile.TemporaryDirectory() as temp_dir:
            corrections_file = os.path.join(temp_dir, "corrections.json")

            with patch('speakub.utils.config.CORRECTIONS_FILE', corrections_file):
                save_pronunciation_corrections({})

                assert os.path.exists(corrections_file)

                with open(corrections_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                assert "_instructions" in data
                assert "_examples" in data

    def test_save_pronunciation_corrections_with_data(self):
        """Test saving pronunciation corrections with data"""
        corrections = {"生長": "生掌", "長": "常"}

        with tempfile.TemporaryDirectory() as temp_dir:
            corrections_file = os.path.join(temp_dir, "corrections.json")

            with patch('speakub.utils.config.CORRECTIONS_FILE', corrections_file):
                save_pronunciation_corrections(corrections)

                loaded = load_pronunciation_corrections()

                assert loaded == corrections

    def test_load_pronunciation_corrections_nonexistent_file(self):
        """Test loading corrections from nonexistent file"""
        with patch('speakub.utils.config.CORRECTIONS_FILE', "/nonexistent/file.json"):
            corrections = load_pronunciation_corrections()

            assert corrections == {}

    def test_load_pronunciation_corrections_invalid_json(self):
        """Test loading corrections from invalid JSON file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            corrections_file = os.path.join(temp_dir, "corrections.json")

            with open(corrections_file, 'w') as f:
                f.write("invalid json")

            with patch('speakub.utils.config.CORRECTIONS_FILE', corrections_file):
                corrections = load_pronunciation_corrections()

                assert corrections == {}

    def test_load_pronunciation_corrections_invalid_structure(self):
        """Test loading corrections from file with invalid structure"""
        with tempfile.TemporaryDirectory() as temp_dir:
            corrections_file = os.path.join(temp_dir, "corrections.json")

            with open(corrections_file, 'w') as f:
                json.dump(["not", "a", "dict"], f)

            with patch('speakub.utils.config.CORRECTIONS_FILE', corrections_file):
                corrections = load_pronunciation_corrections()

                assert corrections == {}


class TestConfigFileOperations:
    """Test configuration file operations"""

    def test_save_config(self):
        """Test saving configuration to file"""
        config = {"language": "zh", "font_size": 14}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")

            with patch('speakub.utils.config.CONFIG_FILE', config_file):
                save_config(config)

                assert os.path.exists(config_file)

                import yaml
                with open(config_file, 'r', encoding='utf-8') as f:
                    saved_config = yaml.safe_load(f)

                assert saved_config["language"] == "zh"
                assert saved_config["font_size"] == 14

    def test_load_config(self):
        """Test loading configuration from file"""
        config = {"language": "zh", "font_size": 14}

        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = os.path.join(temp_dir, "config.json")

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f)

            with patch('speakub.utils.config.CONFIG_FILE', config_file):
                loaded_config = load_config()

                assert loaded_config["language"] == "zh"
                assert loaded_config["font_size"] == 14

    def test_save_tts_config(self):
        """Test saving TTS configuration"""
        tts_config = {"rate": 10, "volume": 80}

        with patch('speakub.utils.config.load_config') as mock_load, \
                patch('speakub.utils.config.save_config') as mock_save:

            mock_load.return_value = {"existing": "config"}

            save_tts_config(tts_config)

            mock_save.assert_called_once()
            call_args = mock_save.call_args[0][0]
            assert call_args["tts"] == tts_config
            assert call_args["existing"] == "config"


if __name__ == '__main__':
    pytest.main([__file__])
