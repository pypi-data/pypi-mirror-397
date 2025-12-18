#!/usr/bin/env python3
"""
Unit tests for Dependency Injection in Reservoir TTS Components.

This module tests the dependency injection support added to the reservoir system,
ensuring components can be properly injected during testing.
"""

import pytest
from unittest.mock import MagicMock, patch
from speakub.tts.reservoir.controller import PredictiveBatchController
# Note: NetworkMonitor and ResourceManager removed in Reservoir v6.0


class MockQueuePredictor:
    """Mock queue predictor for testing."""

    def __init__(self, play_monitor=None):
        self.play_monitor = play_monitor or MagicMock()


class MockPlaylistManager:
    """Mock playlist manager for testing."""

    def __init__(self):
        self.app = None


def test_predictive_controller_uses_injected_network_monitor():
    """Test that PredictiveBatchController correctly uses an injected NetworkMonitor."""
    mock_network_monitor = MagicMock(spec=NetworkMonitor)
    mock_network_monitor.get_latency_factor.return_value = 1.5

    controller = PredictiveBatchController(
        playlist_manager=MockPlaylistManager(),
        queue_predictor=MockQueuePredictor(),
        network_monitor=mock_network_monitor
    )

    # Verify the injected monitor is used
    assert controller.network_monitor is mock_network_monitor

    # Test that injected monitor methods are callable
    assert callable(controller.network_monitor.get_latency_factor)
    controller.network_monitor.get_latency_factor.assert_not_called()


def test_predictive_controller_uses_injected_resource_manager():
    """Test that PredictiveBatchController correctly uses an injected ResourceManager."""
    mock_resource_manager = MagicMock(spec=ResourceManager)
    mock_resource_manager.get_cpu_pressure_factor.return_value = 2.0
    mock_resource_manager.get_memory_pressure_factor.return_value = 1.5

    controller = PredictiveBatchController(
        playlist_manager=MockPlaylistManager(),
        queue_predictor=MockQueuePredictor(),
        resource_manager=mock_resource_manager
    )

    # Verify the injected manager is used
    assert controller.resource_manager is mock_resource_manager

    # Test integration with safety buffer calculation
    with patch.object(controller, '_calculate_dynamic_safety_buffer') as mock_calc:
        mock_calc.return_value = 2.5
        controller._calculate_risk_lead_time()
        # Should call the calculation method which uses resource manager
        mock_calc.assert_called()


def test_predictive_controller_creates_defaults_when_none_injected():
    """Test that PredictiveBatchController creates default instances when none are injected."""
    controller = PredictiveBatchController(
        playlist_manager=MockPlaylistManager(),
        queue_predictor=MockQueuePredictor()
    )

    # Should create default instances
    assert isinstance(controller.network_monitor, NetworkMonitor)
    assert isinstance(controller.resource_manager, ResourceManager)

    # Should not be None
    assert controller.network_monitor is not None
    assert controller.resource_manager is not None


def test_dependency_injection_preserves_functionality():
    """Test that dependency injection doesn't break existing functionality."""
    mock_network_monitor = MagicMock(spec=NetworkMonitor)
    mock_network_monitor.get_latency_factor.return_value = 1.0

    mock_resource_manager = MagicMock(spec=ResourceManager)
    mock_resource_manager.get_cpu_pressure_factor.return_value = 1.0
    mock_resource_manager.get_memory_pressure_factor.return_value = 1.0
    mock_resource_manager.should_reduce_batch_size.return_value = False
    mock_resource_manager.is_system_under_pressure.return_value = False

    controller = PredictiveBatchController(
        playlist_manager=MockPlaylistManager(),
        queue_predictor=MockQueuePredictor(),
        network_monitor=mock_network_monitor,
        resource_manager=mock_resource_manager
    )

    # Test that safety buffer calculation works with injected dependencies
    # This tests the integration between injected components and business logic
    buffer = controller._calculate_dynamic_safety_buffer()

    # Should return a valid buffer value
    assert isinstance(buffer, float)
    assert buffer >= 0

    # Injected monitors should have been called during calculation
    mock_network_monitor.get_latency_factor.assert_called()
    mock_resource_manager.get_cpu_pressure_factor.assert_called()
    mock_resource_manager.get_memory_pressure_factor.assert_called()


def test_network_monitor_mocking_in_tests():
    """Test that NetworkMonitor can be properly mocked for testing."""
    mock_monitor = MagicMock(spec=NetworkMonitor)

    # Test basic mocking
    mock_monitor.record_latency.return_value = None
    mock_monitor.get_latency_factor.return_value = 1.2
    mock_monitor.should_reduce_preloading.return_value = False

    # Verify mock behavior
    mock_monitor.record_latency(1.5)
    mock_monitor.record_latency.assert_called_with(1.5)

    factor = mock_monitor.get_latency_factor()
    assert factor == 1.2

    should_reduce = mock_monitor.should_reduce_preloading()
    assert should_reduce is False


def test_predictive_controller_uses_injected_config_manager():
    """Test that PredictiveBatchController correctly uses an injected ConfigManager."""
    from speakub.utils.config import ConfigManager

    mock_config_manager = MagicMock(spec=ConfigManager)
    mock_config_manager.get.side_effect = lambda key, default=None: {
        "tts.reservoir": {"base_safety_buffer": 3.0, "resource_factor_weight": 0.5},
        "tts.predictive_config": {},
        "tts.preferred_engine": "edge-tts"
    }.get(key, default or {})

    controller = PredictiveBatchController(
        playlist_manager=MockPlaylistManager(),
        queue_predictor=MockQueuePredictor(),
        config_manager=mock_config_manager
    )

    # Verify the injected config manager is used
    assert controller._config_manager is mock_config_manager

    # Test that config is read correctly
    buffer = controller._calculate_dynamic_safety_buffer()
    assert isinstance(buffer, float)

    # Check that config manager was called for reservoir config
    mock_config_manager.get.assert_any_call("tts.reservoir", {})


def test_predictive_controller_fallback_config_behavior():
    """Test config fallback when reservoir config is empty."""
    from speakub.utils.config import ConfigManager

    mock_config_manager = MagicMock(spec=ConfigManager)
    mock_config_manager.get.side_effect = lambda key, default=None: {
        "tts.reservoir": {},  # Empty
        "tts.predictive_config": {"base_safety_buffer": 2.5, "resource_factor_weight": 0.5},
        "tts.preferred_engine": "edge-tts"
    }.get(key, default or {})

    controller = PredictiveBatchController(
        playlist_manager=MockPlaylistManager(),
        queue_predictor=MockQueuePredictor(),
        config_manager=mock_config_manager
    )

    # Should use fallback predictive_config
    buffer = controller._calculate_dynamic_safety_buffer()
    assert isinstance(buffer, float)

    # Both config paths should be queried
    mock_config_manager.get.assert_any_call("tts.reservoir", {})
    mock_config_manager.get.assert_any_call("tts.predictive_config", {})


def test_resource_manager_mocking_in_tests():
    """Test that ResourceManager can be properly mocked for testing."""
    mock_manager = MagicMock(spec=ResourceManager)

    # Test basic mocking
    mock_manager.record_cpu_usage.return_value = None
    mock_manager.record_memory_usage.return_value = None
    mock_manager.get_cpu_pressure_factor.return_value = 1.8
    mock_manager.get_memory_pressure_factor.return_value = 1.3
    mock_manager.should_reduce_batch_size.return_value = False
    mock_manager.get_adaptive_polling_interval.return_value = 10.0

    # Verify mock behavior
    mock_manager.record_cpu_usage(45.0)
    mock_manager.record_cpu_usage.assert_called_with(45.0)

    cpu_factor = mock_manager.get_cpu_pressure_factor()
    assert cpu_factor == 1.8

    memory_factor = mock_manager.get_memory_pressure_factor()
    assert memory_factor == 1.3

    should_reduce = mock_manager.should_reduce_batch_size()
    assert should_reduce is False

    interval = mock_manager.get_adaptive_polling_interval(5.0)
    assert interval == 10.0


if __name__ == "__main__":
    pytest.main([__file__])
