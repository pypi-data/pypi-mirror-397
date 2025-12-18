#!/usr/bin/env python3
"""
Tests for retry_utils module.
"""

import pytest
from unittest.mock import patch, MagicMock

from speakub.utils.retry_utils import (
    calculate_retry_delay,
    get_dns_retry_delay,
    get_network_retry_delay,
    get_content_retry_delay,
    should_retry_network_error,
    should_retry_content_error,
)


class TestRetryDelayCalculation:
    """Test retry delay calculation functions"""

    def test_calculate_retry_delay_basic(self):
        """Test basic retry delay calculation"""
        # Test without jitter
        delay = calculate_retry_delay(0, 1.0, use_jitter=False)
        assert delay == 1.0

        delay = calculate_retry_delay(1, 2.0, use_jitter=False)
        assert delay == 4.0  # 2.0 * (2^1)

        delay = calculate_retry_delay(2, 1.5, use_jitter=False)
        assert delay == 6.0  # 1.5 * (2^2)

    def test_calculate_retry_delay_with_jitter(self):
        """Test retry delay calculation with jitter"""
        # Test with jitter - should be within range
        for attempt in range(3):
            delay = calculate_retry_delay(attempt, 1.0, use_jitter=True)
            base_delay = 1.0 * (2 ** attempt)
            assert 0.5 * base_delay <= delay <= 1.5 * base_delay

    def test_calculate_retry_delay_max_limit(self):
        """Test retry delay with maximum limit"""
        delay = calculate_retry_delay(
            10, 10.0, use_jitter=False, max_delay=50.0)
        assert delay == 50.0  # Should be capped

    def test_calculate_retry_delay_validation(self):
        """Test retry delay input validation"""
        with pytest.raises(ValueError, match="Attempt must be non-negative"):
            calculate_retry_delay(-1, 1.0)

        with pytest.raises(ValueError, match="Base delay must be positive"):
            calculate_retry_delay(0, 0.0)

        with pytest.raises(ValueError, match="Jitter range min must be less than max"):
            calculate_retry_delay(0, 1.0, jitter_range=(1.5, 0.5))


class TestNetworkRetryDelay:
    """Test network-specific retry delay functions"""

    @patch('speakub.utils.config.ConfigManager')
    def test_get_dns_retry_delay(self, mock_config_manager):
        """Test DNS retry delay with config"""
        mock_config = MagicMock()
        mock_config.get.side_effect = lambda key: {
            "retry_policies.network": {
                "dns_delay": 7.0,
                "use_jitter": True,
                "jitter_range": [0.8, 1.2],
                "exponential_factor": 1.5,
            }
        }.get(key.split('.')[0] if '.' in key else key, {}).get(key.split('.')[1] if '.' in key else None, None)
        mock_config_manager.return_value = mock_config

        delay = get_dns_retry_delay(1, mock_config_manager)
        # Should use DNS delay (7.0) instead of base delay
        expected_base = 7.0 * (1.5 ** 1)  # 7.0 * 1.5 = 10.5
        assert 0.8 * expected_base <= delay <= 1.2 * expected_base

    @patch('speakub.utils.config.ConfigManager')
    def test_get_network_retry_delay(self, mock_config_manager):
        """Test general network retry delay"""
        mock_config = MagicMock()
        mock_config.get.return_value = {
            "base_delay": 3.0,
            "use_jitter": False,
            "exponential_factor": 2.0,
        }
        mock_config_manager.return_value = mock_config

        delay = get_network_retry_delay(2, mock_config_manager)
        expected = 3.0 * (2.0 ** 2)  # 3.0 * 4 = 12.0
        assert delay == expected


class TestContentRetryDelay:
    """Test content-specific retry delay functions"""

    @patch('speakub.utils.config.ConfigManager')
    def test_get_content_retry_delay(self, mock_config_manager):
        """Test content retry delay (no exponential backoff)"""
        mock_config = MagicMock()
        mock_config.get.return_value = {
            "delay": 4.0,
            "use_jitter": False,
        }
        mock_config_manager.return_value = mock_config

        delay = get_content_retry_delay(5, mock_config_manager)
        assert delay == 4.0  # Should not use exponential backoff


class TestRetryDecisionLogic:
    """Test retry decision logic"""

    @patch('speakub.utils.config.ConfigManager')
    def test_should_retry_network_error(self, mock_config_manager):
        """Test network retry decision"""
        mock_config = MagicMock()
        mock_config.get.return_value = 3  # max_attempts
        mock_config_manager.return_value = mock_config

        assert should_retry_network_error(0, mock_config_manager) == True
        assert should_retry_network_error(1, mock_config_manager) == True
        assert should_retry_network_error(2, mock_config_manager) == True
        assert should_retry_network_error(3, mock_config_manager) == False

    @patch('speakub.utils.config.ConfigManager')
    def test_should_retry_content_error_normal(self, mock_config_manager):
        """Test content retry decision for normal content"""
        mock_config = MagicMock()
        mock_config.get.return_value = {
            "normal_attempts": 2,
            "short_text_attempts": 4,
        }
        mock_config_manager.return_value = mock_config

        # Normal content
        assert should_retry_content_error(
            0, "normal", mock_config_manager) == True
        assert should_retry_content_error(
            1, "normal", mock_config_manager) == True
        assert should_retry_content_error(
            2, "normal", mock_config_manager) == False

    @patch('speakub.utils.config.ConfigManager')
    def test_should_retry_content_error_short_text(self, mock_config_manager):
        """Test content retry decision for short text"""
        mock_config = MagicMock()
        mock_config.get.return_value = {
            "normal_attempts": 2,
            "short_text_attempts": 4,
        }
        mock_config_manager.return_value = mock_config

        # Short text content
        assert should_retry_content_error(
            0, "very_short_fragment", mock_config_manager) == True
        assert should_retry_content_error(
            1, "very_short_fragment", mock_config_manager) == True
        assert should_retry_content_error(
            2, "very_short_fragment", mock_config_manager) == True
        assert should_retry_content_error(
            3, "very_short_fragment", mock_config_manager) == True
        assert should_retry_content_error(
            4, "very_short_fragment", mock_config_manager) == False


class TestIntegrationWithConfig:
    """Test integration with actual config system"""

    def test_calculate_retry_delay_real_config(self):
        """Test that our functions work with real config"""
        # Test that functions can be called without config manager
        delay = get_network_retry_delay(1)
        assert isinstance(delay, float)
        assert delay > 0

        delay = get_content_retry_delay(1)
        assert isinstance(delay, float)
        assert delay > 0

        delay = get_dns_retry_delay(1)
        assert isinstance(delay, float)
        assert delay > 0

    def test_retry_decisions_real_config(self):
        """Test retry decisions with real config"""
        assert should_retry_network_error(0) == True
        assert should_retry_network_error(10) == False  # Should exceed max

        assert should_retry_content_error(0, "normal") == True
        assert should_retry_content_error(
            10, "normal") == False  # Should exceed max

        assert should_retry_content_error(0, "very_short_fragment") == True
        assert should_retry_content_error(
            10, "very_short_fragment") == False  # Should exceed max


if __name__ == '__main__':
    pytest.main([__file__])
