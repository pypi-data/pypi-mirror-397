#!/usr/bin/env python3
"""
Unit tests for resource_monitor.py module.
"""

import time
from unittest.mock import patch, MagicMock, call
import pytest
from speakub.utils.resource_monitor import (
    UnifiedResourceMonitor,
    ResourceMetrics,
    ResourceMonitorProtocol,
    ResourceManagerAdapter,
    PerformanceMonitorAdapter,
    get_unified_resource_monitor,
)


class TestUnifiedResourceMonitor:
    """Test cases for UnifiedResourceMonitor class."""

    def test_unified_resource_monitor_initialization(self):
        """Test UnifiedResourceMonitor initialization."""
        monitor = UnifiedResourceMonitor()

        assert monitor._monitors == []
        assert monitor._monitoring is False
        assert monitor._monitor_thread is None
        assert monitor._alert_callbacks == []

    def test_add_monitor(self):
        """Test adding a monitor."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)

        monitor.add_monitor(mock_monitor)

        assert mock_monitor in monitor._monitors

    def test_add_monitor_duplicate(self):
        """Test adding duplicate monitor."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)

        monitor.add_monitor(mock_monitor)
        monitor.add_monitor(mock_monitor)  # Add again

        assert len(monitor._monitors) == 1

    def test_remove_monitor(self):
        """Test removing a monitor."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)

        monitor.add_monitor(mock_monitor)
        monitor.remove_monitor(mock_monitor)

        assert mock_monitor not in monitor._monitors

    def test_remove_nonexistent_monitor(self):
        """Test removing nonexistent monitor."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)

        monitor.remove_monitor(mock_monitor)

        # Should not raise error
        assert mock_monitor not in monitor._monitors

    @patch("speakub.utils.resource_monitor.threading.Thread")
    @patch("speakub.utils.resource_monitor.logger")
    def test_start_monitoring(self, mock_logger, mock_thread):
        """Test starting monitoring."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)
        monitor.add_monitor(mock_monitor)

        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        monitor.start_monitoring(interval_seconds=60)

        assert monitor._monitoring is True
        mock_thread.assert_called_once()
        mock_monitor.start_monitoring.assert_called_once()
        mock_logger.info.assert_called_with(
            "Unified resource monitoring started")

    def test_start_monitoring_already_started(self):
        """Test starting monitoring when already started."""
        monitor = UnifiedResourceMonitor()
        monitor._monitoring = True

        monitor.start_monitoring()

        # Should not start again
        assert monitor._monitoring is True

    @patch("speakub.utils.resource_monitor.logger")
    def test_stop_monitoring(self, mock_logger):
        """Test stopping monitoring."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)
        monitor.add_monitor(mock_monitor)

        mock_thread = MagicMock()
        monitor._monitor_thread = mock_thread
        monitor._monitoring = True

        monitor.stop_monitoring()

        assert monitor._monitoring is False
        mock_thread.join.assert_called_with(timeout=5.0)
        mock_monitor.stop_monitoring.assert_called_once()
        mock_logger.info.assert_called_with(
            "Unified resource monitoring stopped")

    def test_stop_monitoring_not_started(self):
        """Test stopping monitoring when not started."""
        monitor = UnifiedResourceMonitor()

        monitor.stop_monitoring()

        # Should not raise error
        assert monitor._monitoring is False

    @patch("speakub.utils.resource_monitor.time.sleep")
    def test_monitor_loop(self, mock_sleep):
        """Test the monitoring loop."""
        monitor = UnifiedResourceMonitor()
        monitor._monitoring = True

        # Mock _collect_and_check_metrics to stop monitoring
        monitor._collect_and_check_metrics = MagicMock()
        monitor._collect_and_check_metrics.side_effect = lambda: setattr(
            monitor, '_monitoring', False)

        monitor._monitor_loop(30)

        monitor._collect_and_check_metrics.assert_called_once()
        mock_sleep.assert_called_with(30)

    def test_monitor_loop_with_exception(self, mock_sleep):
        """Test monitoring loop with exception."""
        monitor = UnifiedResourceMonitor()
        monitor._monitoring = True

        # Mock _collect_and_check_metrics to raise exception and then stop
        monitor._collect_and_check_metrics = MagicMock(
            side_effect=[Exception("Test error"), None])
        monitor._collect_and_check_metrics.side_effect = [
            Exception("Test error"), lambda: setattr(monitor, '_monitoring', False)]

        monitor._monitor_loop(30)

        # Should sleep briefly on error
        mock_sleep.assert_has_calls([call(5), call(30)])

    def test_collect_and_check_metrics(self):
        """Test collecting and checking metrics."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)
        mock_monitor.get_metrics.return_value = {"memory_rss_mb": 100}
        monitor.add_monitor(mock_monitor)

        # Mock _check_resource_alerts
        monitor._check_resource_alerts = MagicMock()

        monitor._collect_and_check_metrics()

        mock_monitor.get_metrics.assert_called_once()
        monitor._check_resource_alerts.assert_called_once_with(
            {"memory_rss_mb": 100})

    def test_check_resource_alerts_memory_critical(self):
        """Test checking resource alerts for critical memory."""
        monitor = UnifiedResourceMonitor()

        # Mock _trigger_alert
        monitor._trigger_alert = MagicMock()

        metrics = {"memory_rss_mb": 450}
        monitor._check_resource_alerts(metrics)

        monitor._trigger_alert.assert_called_once()
        args = monitor._trigger_alert.call_args[0]
        assert args[0] == "CRITICAL_MEMORY"
        assert "450" in args[1]

    def test_check_resource_alerts_memory_warning(self):
        """Test checking resource alerts for warning memory."""
        monitor = UnifiedResourceMonitor()

        # Mock _trigger_alert
        monitor._trigger_alert = MagicMock()

        metrics = {"memory_rss_mb": 250}
        monitor._check_resource_alerts(metrics)

        monitor._trigger_alert.assert_called_once()
        args = monitor._trigger_alert.call_args[0]
        assert args[0] == "WARNING_MEMORY"
        assert "250" in args[1]

    def test_check_resource_alerts_temp_files_high(self):
        """Test checking resource alerts for high temp files count."""
        monitor = UnifiedResourceMonitor()

        # Mock _trigger_alert
        monitor._trigger_alert = MagicMock()

        metrics = {"temp_files_count": 1500}
        monitor._check_resource_alerts(metrics)

        monitor._trigger_alert.assert_called_once()
        args = monitor._trigger_alert.call_args[0]
        assert args[0] == "TEMP_FILES_HIGH"
        assert "1500" in args[1]

    def test_trigger_alert(self):
        """Test triggering alerts."""
        monitor = UnifiedResourceMonitor()
        callback = MagicMock()
        monitor.add_alert_callback(callback)

        with patch("speakub.utils.resource_monitor.logger") as mock_logger:
            with patch("speakub.utils.resource_monitor.time.time", return_value=1000.0):
                monitor._trigger_alert(
                    "TEST_ALERT", "Test message", {"key": "value"})

        mock_logger.warning.assert_called_once_with(
            "[TEST_ALERT] Test message")
        callback.assert_called_once()
        args = callback.call_args[0]
        assert args[0] == "TEST_ALERT"
        assert args[1]["type"] == "TEST_ALERT"
        assert args[1]["message"] == "Test message"
        assert args[1]["timestamp"] == 1000.0
        assert args[1]["key"] == "value"

    def test_add_alert_callback(self):
        """Test adding alert callback."""
        monitor = UnifiedResourceMonitor()
        callback = MagicMock()

        monitor.add_alert_callback(callback)

        assert callback in monitor._alert_callbacks

    def test_add_alert_callback_duplicate(self):
        """Test adding duplicate alert callback."""
        monitor = UnifiedResourceMonitor()
        callback = MagicMock()

        monitor.add_alert_callback(callback)
        monitor.add_alert_callback(callback)  # Add again

        assert len(monitor._alert_callbacks) == 1

    def test_get_unified_metrics(self):
        """Test getting unified metrics."""
        monitor = UnifiedResourceMonitor()
        mock_monitor = MagicMock(spec=ResourceMonitorProtocol)
        mock_monitor.get_metrics.return_value = {
            "memory_rss_mb": 100.0,
            "memory_growth_rate_mb_per_min": 2.5,
            "temp_files_count": 50,
            "total_temp_files_size_mb": 25.0,
            "cache_hit_rate": 0.85,
            "system_memory_available_gb": 4.0,
        }
        monitor.add_monitor(mock_monitor)

        with patch("speakub.utils.resource_monitor.time.time", return_value=1000.0):
            result = monitor.get_unified_metrics()

        assert isinstance(result, ResourceMetrics)
        assert result.memory_mb == 100.0
        assert result.memory_growth_rate == 2.5
        assert result.temp_files_count == 50
        assert result.temp_files_size_mb == 25.0
        assert result.cache_hit_rate == 0.85
        assert result.system_memory_available_gb == 4.0
        assert result.timestamp == 1000.0

    def test_cleanup_all_resources(self):
        """Test cleaning up all resources."""
        monitor = UnifiedResourceMonitor()
        mock_monitor1 = MagicMock(spec=ResourceMonitorProtocol)
        mock_monitor1.cleanup_resources.return_value = 5
        mock_monitor2 = MagicMock(spec=ResourceMonitorProtocol)
        mock_monitor2.cleanup_resources.return_value = 3

        monitor.add_monitor(mock_monitor1)
        monitor.add_monitor(mock_monitor2)

        with patch("speakub.utils.resource_monitor.logger") as mock_logger:
            result = monitor.cleanup_all_resources()

        assert result["MagicMock"] == 5  # First monitor
        # Second monitor (overwrites due to same name)
        assert result["MagicMock"] == 3
        mock_logger.info.assert_called_once()


class TestResourceManagerAdapter:
    """Test cases for ResourceManagerAdapter class."""

    def test_resource_manager_adapter_initialization(self):
        """Test ResourceManagerAdapter initialization."""
        mock_resource_manager = MagicMock()
        adapter = ResourceManagerAdapter(mock_resource_manager)

        assert adapter.resource_manager == mock_resource_manager

    def test_get_metrics(self):
        """Test getting metrics from adapter."""
        mock_resource_manager = MagicMock()
        mock_resource_manager.get_resource_stats.return_value = {
            "memory_mb": 100}
        adapter = ResourceManagerAdapter(mock_resource_manager)

        result = adapter.get_metrics()

        assert result == {"memory_mb": 100}
        mock_resource_manager.get_resource_stats.assert_called_once()

    def test_cleanup_resources(self):
        """Test cleaning up resources through adapter."""
        mock_resource_manager = MagicMock()
        mock_resource_manager.cleanup_temp_files_by_age.return_value = 5
        mock_resource_manager.cleanup_temp_files_by_size.return_value = 3
        adapter = ResourceManagerAdapter(mock_resource_manager)

        result = adapter.cleanup_resources()

        assert result == 8  # 5 + 3
        mock_resource_manager.cleanup_temp_files_by_age.assert_called_once()
        mock_resource_manager.cleanup_temp_files_by_size.assert_called_once()

    def test_start_monitoring(self):
        """Test starting monitoring through adapter."""
        mock_resource_manager = MagicMock()
        adapter = ResourceManagerAdapter(mock_resource_manager)

        adapter.start_monitoring()

        mock_resource_manager.start_memory_monitoring.assert_called_once()

    def test_stop_monitoring(self):
        """Test stopping monitoring through adapter."""
        mock_resource_manager = MagicMock()
        adapter = ResourceManagerAdapter(mock_resource_manager)

        adapter.stop_monitoring()

        mock_resource_manager.stop_memory_monitoring.assert_called_once()


class TestPerformanceMonitorAdapter:
    """Test cases for PerformanceMonitorAdapter class."""

    def test_performance_monitor_adapter_initialization(self):
        """Test PerformanceMonitorAdapter initialization."""
        mock_performance_monitor = MagicMock()
        adapter = PerformanceMonitorAdapter(mock_performance_monitor)

        assert adapter.performance_monitor == mock_performance_monitor

    def test_get_metrics(self):
        """Test getting metrics from adapter."""
        mock_performance_monitor = MagicMock()
        mock_performance_monitor.get_current_metrics.return_value = {
            "cpu_usage": 50}
        adapter = PerformanceMonitorAdapter(mock_performance_monitor)

        result = adapter.get_metrics()

        assert result == {"cpu_usage": 50}
        mock_performance_monitor.get_current_metrics.assert_called_once()

    def test_cleanup_resources(self):
        """Test cleaning up resources through adapter."""
        mock_performance_monitor = MagicMock()
        adapter = PerformanceMonitorAdapter(mock_performance_monitor)

        result = adapter.cleanup_resources()

        assert result == 0  # PerformanceMonitor doesn't manage resources directly

    def test_start_monitoring(self):
        """Test starting monitoring through adapter."""
        import asyncio
        mock_performance_monitor = MagicMock()
        adapter = PerformanceMonitorAdapter(mock_performance_monitor)

        asyncio.run(adapter.start_monitoring())

        mock_performance_monitor.start_monitoring.assert_called_once()

    def test_stop_monitoring(self):
        """Test stopping monitoring through adapter."""
        mock_performance_monitor = MagicMock()
        adapter = PerformanceMonitorAdapter(mock_performance_monitor)

        adapter.stop_monitoring()

        mock_performance_monitor.stop_monitoring.assert_called_once()


class TestGlobalFunctions:
    """Test cases for global functions."""

    def test_get_unified_resource_monitor(self):
        """Test getting the global unified resource monitor."""
        monitor = get_unified_resource_monitor()

        assert isinstance(monitor, UnifiedResourceMonitor)
        # Should return the same instance
        monitor2 = get_unified_resource_monitor()
        assert monitor is monitor2


class TestDataClasses:
    """Test cases for data classes."""

    def test_resource_metrics_creation(self):
        """Test ResourceMetrics data class."""
        with patch("speakub.utils.resource_monitor.time.time", return_value=1000.0):
            metrics = ResourceMetrics(
                memory_mb=100.0,
                memory_growth_rate=2.5,
                temp_files_count=50,
                temp_files_size_mb=25.0,
                cache_hit_rate=0.85,
                system_memory_available_gb=4.0,
                timestamp=1000.0
            )

        assert metrics.memory_mb == 100.0
        assert metrics.memory_growth_rate == 2.5
        assert metrics.temp_files_count == 50
        assert metrics.temp_files_size_mb == 25.0
        assert metrics.cache_hit_rate == 0.85
        assert metrics.system_memory_available_gb == 4.0
        assert metrics.timestamp == 1000.0


if __name__ == "__main__":
    pytest.main([__file__])
