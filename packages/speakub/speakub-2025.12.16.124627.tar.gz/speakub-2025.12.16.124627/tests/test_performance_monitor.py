#!/usr/bin/env python3
"""
Unit tests for performance_monitor.py module.
"""

import time
from unittest.mock import patch, MagicMock, call
import pytest
from speakub.utils.performance_monitor import (
    PerformanceMonitor,
    CacheMetrics,
    ExtendedMemoryMetrics,
    MemoryMetrics,
    PerformanceMetrics,
    create_performance_monitor,
)


class TestPerformanceMonitor:
    """Test cases for PerformanceMonitor class."""

    def test_performance_monitor_initialization(self):
        """Test PerformanceMonitor initialization."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        assert monitor.app == mock_app
        assert monitor._monitoring is False
        assert monitor._monitor_task is None
        assert isinstance(monitor.metrics_history, dict)
        assert monitor.monitor_interval == 30
        assert monitor.max_history_size == 100
        # Updated to sync with file_utils.py
        assert monitor.memory_warning_threshold_mb == 512
        # Updated to sync with file_utils.py
        assert monitor.memory_critical_threshold_mb == 800
        assert monitor.memory_alert_callbacks == []

    @patch("speakub.utils.performance_monitor.threading.Thread")
    @patch("speakub.utils.performance_monitor.logger")
    def test_start_monitoring(self, mock_logger, mock_thread):
        """Test starting performance monitoring."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        monitor.start_monitoring()

        assert monitor._monitoring is True
        mock_thread.assert_called_once()
        mock_logger.info.assert_called_with("Performance monitoring started")

    @patch("speakub.utils.performance_monitor.logger")
    def test_start_monitoring_already_started(self, mock_logger):
        """Test starting monitoring when already started."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)
        monitor._monitoring = True

        monitor.start_monitoring()

        # Should not start again
        mock_logger.info.assert_not_called()

    @patch("speakub.utils.performance_monitor.logger")
    def test_stop_monitoring(self, mock_logger):
        """Test stopping performance monitoring."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        mock_task = MagicMock()
        monitor._monitor_task = mock_task
        monitor._monitoring = True

        monitor.stop_monitoring()

        assert monitor._monitoring is False
        mock_task.cancel.assert_called_once()
        mock_logger.info.assert_called_with("Performance monitoring stopped")

    def test_stop_monitoring_not_started(self):
        """Test stopping monitoring when not started."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        monitor.stop_monitoring()

        # Should not raise error
        assert monitor._monitoring is False

    @patch("speakub.utils.performance_monitor.time.sleep")
    @patch("speakub.utils.performance_monitor.logger")
    def test_monitor_loop(self, mock_logger, mock_sleep):
        """Test the monitoring loop."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)
        monitor._monitoring = True

        # Mock _collect_metrics to avoid actual collection
        monitor._collect_metrics = MagicMock()

        # Stop monitoring after first iteration
        def stop_monitoring():
            monitor._monitoring = False

        monitor._collect_metrics.side_effect = stop_monitoring

        monitor._monitor_loop()

        monitor._collect_metrics.assert_called_once()
        mock_sleep.assert_called_with(30)

    @patch("speakub.utils.performance_monitor.time.sleep")
    @patch("speakub.utils.performance_monitor.logger")
    def test_monitor_loop_with_exception(self, mock_logger, mock_sleep):
        """Test monitoring loop with exception."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)
        monitor._monitoring = True

        # Mock _collect_metrics to raise exception first, then set flag to stop
        call_count = 0

        def mock_collect():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Test error")
            else:
                monitor._monitoring = False

        monitor._collect_metrics = MagicMock(side_effect=mock_collect)

        monitor._monitor_loop()

        # Should log error and continue
        mock_logger.error.assert_called()
        # Should sleep briefly on error
        mock_sleep.assert_has_calls([call(5)])

    @patch("speakub.utils.performance_monitor.time.time")
    def test_add_metric(self, mock_time):
        """Test adding metrics to history."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        mock_time.return_value = 1000.0

        monitor._add_metric("test_metric", 42)

        assert "test_metric" in monitor.metrics_history
        assert len(monitor.metrics_history["test_metric"]) == 1
        assert monitor.metrics_history["test_metric"][0] == (1000.0, 42)

    def test_add_metric_history_limit(self):
        """Test that metric history is limited."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)
        monitor.max_history_size = 3

        # Add more metrics than the limit
        for i in range(5):
            monitor._add_metric("test_metric", i)

        # Should only keep the last 3
        assert len(monitor.metrics_history["test_metric"]) == 3
        assert [value for _, value in monitor.metrics_history["test_metric"]] == [
            2, 3, 4]

    def test_get_cache_stats_with_viewport(self):
        """Test getting cache stats with viewport content."""
        mock_app = MagicMock()
        mock_viewport = MagicMock()
        mock_viewport.get_cache_stats.return_value = {
            "hit_rate": 0.85, "size": 100}
        mock_app.viewport_content = mock_viewport

        monitor = PerformanceMonitor(mock_app)

        result = monitor._get_cache_stats()
        assert result == {"hit_rate": 0.85, "size": 100}

    def test_get_cache_stats_no_viewport(self):
        """Test getting cache stats without viewport content."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        result = monitor._get_cache_stats()
        assert result == {}

    @patch("speakub.utils.performance_monitor.psutil.Process")
    def test_get_memory_info(self, mock_process):
        """Test getting memory information."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1024 * 1024 * 100  # 100MB
        mock_memory_info.vms = 1024 * 1024 * 200  # 200MB

        mock_process_instance = MagicMock()
        mock_process_instance.memory_info.return_value = mock_memory_info
        mock_process.return_value = mock_process_instance

        result = monitor._get_memory_info()

        assert result.rss == 1024 * 1024 * 100
        assert result.vms == 1024 * 1024 * 200

    @patch("speakub.utils.performance_monitor.psutil.virtual_memory")
    def test_get_system_memory(self, mock_virtual_memory):
        """Test getting system memory information."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        mock_memory = MagicMock()
        mock_memory.total = 16 * 1024**3  # 16GB
        mock_memory.available = 8 * 1024**3  # 8GB
        mock_memory.percent = 50.0

        mock_virtual_memory.return_value = mock_memory

        result = monitor._get_system_memory()

        assert result.total == 16 * 1024**3
        assert result.available == 8 * 1024**3
        assert result.percent == 50.0

    def test_get_tts_state_with_engine(self):
        """Test getting TTS state with TTS engine."""
        mock_app = MagicMock()
        mock_tts_engine = MagicMock()
        mock_tts_engine.get_current_state.return_value = "playing"
        mock_app.tts_engine = mock_tts_engine

        monitor = PerformanceMonitor(mock_app)

        result = monitor._get_tts_state()
        assert result == "playing"

    def test_get_tts_state_no_engine(self):
        """Test getting TTS state without TTS engine."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        result = monitor._get_tts_state()
        assert result is None

    def test_get_tts_state_engine_error(self):
        """Test getting TTS state when engine raises error."""
        mock_app = MagicMock()
        mock_tts_engine = MagicMock()
        mock_tts_engine.get_current_state.side_effect = Exception(
            "Engine error")
        mock_app.tts_engine = mock_tts_engine

        monitor = PerformanceMonitor(mock_app)

        result = monitor._get_tts_state()
        assert result == "unknown"

    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_cache_stats")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_memory_info")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_system_memory")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_extended_memory_metrics")
    def test_get_current_metrics(self, mock_extended, mock_system_mem, mock_mem_info, mock_cache_stats):
        """Test getting current metrics."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        # Mock cache stats
        mock_cache_stats.return_value = {
            "size": 100,
            "max_size": 200,
            "hit_rate": 0.85,
            "hits": 85,
            "misses": 15
        }

        # Mock memory info
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1024 * 1024 * 100  # 100MB
        mock_memory_info.vms = 1024 * 1024 * 150  # 150MB
        mock_mem_info.return_value = mock_memory_info

        # Mock system memory
        mock_system_memory = MagicMock()
        mock_system_memory.total = 16 * 1024**3  # 16GB
        mock_system_memory.available = 8 * 1024**3  # 8GB
        mock_system_memory.percent = 50.0
        mock_system_mem.return_value = mock_system_memory

        # Mock extended metrics
        mock_extended.return_value = {
            "growth_rate": 2.5,
            "leaks_suspected": False,
            "gc_collections": 42,
            "efficiency_score": 85.0
        }

        # Mock TTS state
        mock_app.tts_status = "PLAYING"

        result = monitor.get_current_metrics()

        assert result["cache_size"] == 100
        assert result["cache_hit_rate"] == 0.85
        assert result["memory_rss_mb"] == 100.0
        assert result["memory_vms_mb"] == 150.0
        assert result["system_memory_total_gb"] == 16.0
        assert result["system_memory_available_gb"] == 8.0
        assert result["memory_growth_rate_mb_per_min"] == 2.5
        assert result["tts_status"] == "PLAYING"

    def test_get_extended_memory_metrics_insufficient_data(self):
        """Test extended memory metrics with insufficient data."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        result = monitor._get_extended_memory_metrics()

        assert result["growth_rate"] == 0.0
        assert result["leaks_suspected"] is False
        assert result["gc_collections"] == 0
        assert result["efficiency_score"] == 100.0

    def test_get_extended_memory_metrics_with_data(self):
        """Test extended memory metrics with sufficient data."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        # Add memory history data
        base_time = time.time()
        monitor.metrics_history["memory_usage_mb"] = [
            # 10 readings, 5MB increase each
            (base_time + i * 60, 100.0 + i * 5) for i in range(10)
        ]

        with patch("speakub.utils.performance_monitor.PerformanceMonitor._get_system_memory") as mock_sys_mem:
            mock_system_memory = MagicMock()
            mock_system_memory.available = 1024 * 1024 * 1024  # 1GB available
            mock_sys_mem.return_value = mock_system_memory

            result = monitor._get_extended_memory_metrics()

            assert result["growth_rate"] > 0  # Should detect growth
            assert result["leaks_suspected"] is True  # Continuous increase
            assert result["gc_collections"] >= 0
            assert isinstance(result["efficiency_score"], float)

    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_memory_info")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_system_memory")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_extended_memory_metrics")
    def test_get_extended_memory_metrics_structured(self, mock_extended, mock_sys_mem, mock_mem_info):
        """Test getting structured extended memory metrics."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        # Mock memory info
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1024 * 1024 * 100
        mock_memory_info.vms = 1024 * 1024 * 150
        mock_mem_info.return_value = mock_memory_info

        # Mock system memory
        mock_system_memory = MagicMock()
        mock_system_memory.total = 16 * 1024**3
        mock_system_memory.available = 8 * 1024**3
        mock_sys_mem.return_value = mock_system_memory

        # Mock extended metrics
        mock_extended.return_value = {
            "growth_rate": 2.5,
            "leaks_suspected": True,
            "gc_collections": 42,
            "efficiency_score": 75.0
        }

        # Add some memory history for peak calculation
        monitor.metrics_history["memory_usage_mb"] = [(time.time(), 120.0)]

        result = monitor.get_extended_memory_metrics()

        assert isinstance(result, ExtendedMemoryMetrics)
        assert result.rss_mb == 100.0
        assert result.vms_mb == 150.0
        assert result.system_total_gb == 16.0
        assert result.system_available_gb == 8.0
        assert result.memory_growth_rate == 2.5
        assert result.memory_leaks_suspected is True
        assert result.gc_collections == 42
        assert result.memory_efficiency_score == 75.0

    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_cache_stats")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_memory_info")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_system_memory")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor._get_tts_state")
    def test_get_structured_metrics(self, mock_tts_state, mock_sys_mem, mock_mem_info, mock_cache_stats):
        """Test getting structured performance metrics."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        # Mock cache stats
        mock_cache_stats.return_value = {
            "size": 100,
            "max_size": 200,
            "hit_rate": 0.85,
            "hits": 85,
            "misses": 15
        }

        # Mock memory info
        mock_memory_info = MagicMock()
        mock_memory_info.rss = 1024 * 1024 * 100
        mock_memory_info.vms = 1024 * 1024 * 150
        mock_mem_info.return_value = mock_memory_info

        # Mock system memory
        mock_system_memory = MagicMock()
        mock_system_memory.total = 16 * 1024**3
        mock_system_memory.available = 8 * 1024**3
        mock_sys_mem.return_value = mock_system_memory

        # Mock TTS state
        mock_tts_state.return_value = "playing"

        result = monitor.get_structured_metrics()

        assert isinstance(result, PerformanceMetrics)
        assert isinstance(result.cache, CacheMetrics)
        assert isinstance(result.memory, MemoryMetrics)
        assert result.cache.hit_rate == 0.85
        assert result.memory.rss_mb == 100.0
        assert result.tts_state == "playing"

    def test_get_metrics_summary(self):
        """Test getting metrics summary."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        # Add some test data
        base_time = time.time()
        monitor.metrics_history = {
            "cache_hit_rate": [(base_time, 0.8), (base_time + 60, 0.9)],
            "memory_usage_mb": [(base_time, 100), (base_time + 60, 120)],
            "tts_state_changes": [(base_time, 1), (base_time + 60, 2)],
        }

        result = monitor.get_metrics_summary()

        assert "avg_cache_hit_rate" in result
        assert "avg_memory_mb" in result
        assert "peak_memory_mb" in result
        assert "tts_state_change_count" in result
        assert result["avg_cache_hit_rate"] == 0.85
        assert result["avg_memory_mb"] == 110.0
        assert result["peak_memory_mb"] == 120.0
        assert result["tts_state_change_count"] == 2

    def test_add_memory_alert_callback(self):
        """Test adding memory alert callback."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        callback = MagicMock()
        monitor.add_memory_alert_callback(callback)

        assert callback in monitor.memory_alert_callbacks

    def test_add_memory_alert_callback_duplicate(self):
        """Test adding duplicate memory alert callback."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        callback = MagicMock()
        monitor.add_memory_alert_callback(callback)
        monitor.add_memory_alert_callback(callback)  # Add again

        assert len(monitor.memory_alert_callbacks) == 1

    def test_remove_memory_alert_callback(self):
        """Test removing memory alert callback."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        callback = MagicMock()
        monitor.add_memory_alert_callback(callback)
        monitor.remove_memory_alert_callback(callback)

        assert callback not in monitor.memory_alert_callbacks

    def test_set_memory_thresholds(self):
        """Test setting memory thresholds."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        monitor.set_memory_thresholds(
            warning_mb=150, critical_mb=300, growth_rate_threshold=5.0)

        assert monitor.memory_warning_threshold_mb == 150
        assert monitor.memory_critical_threshold_mb == 300
        assert monitor.memory_growth_rate_threshold == 5.0

    @patch("speakub.utils.performance_monitor.PerformanceMonitor.get_extended_memory_metrics")
    @patch("speakub.utils.performance_monitor.PerformanceMonitor.get_current_metrics")
    def test_get_memory_health_status(self, mock_current_metrics, mock_extended_metrics):
        """Test getting memory health status."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        # Mock extended metrics
        mock_extended = MagicMock()
        mock_extended.memory_leaks_suspected = False
        mock_extended.memory_growth_rate = 1.0
        mock_extended.memory_efficiency_score = 80.0
        mock_extended_metrics.return_value = mock_extended

        # Mock current metrics
        mock_current_metrics.return_value = {
            "memory_rss_mb": 200,
            "system_memory_total_gb": 8,
        }

        result = monitor.get_memory_health_status()

        assert "health_score" in result
        assert "status" in result
        assert "recommendations" in result
        assert isinstance(result["health_score"], float)
        assert result["status"] in ["good", "warning", "critical"]

    def test_generate_memory_recommendations(self):
        """Test generating memory recommendations."""
        mock_app = MagicMock()
        monitor = PerformanceMonitor(mock_app)

        extended = MagicMock()
        extended.memory_leaks_suspected = True
        extended.memory_growth_rate = 15.0
        extended.memory_efficiency_score = 30.0

        recommendations = monitor._generate_memory_recommendations(
            25.0, extended)

        assert len(recommendations) > 0
        assert any("leak" in rec.lower() for rec in recommendations)
        assert any("growth" in rec.lower() for rec in recommendations)
        assert any("efficiency" in rec.lower() for rec in recommendations)

    def test_create_performance_monitor(self):
        """Test creating performance monitor instance."""
        mock_app = MagicMock()
        monitor = create_performance_monitor(mock_app)

        assert isinstance(monitor, PerformanceMonitor)
        assert monitor.app == mock_app


class TestDataClasses:
    """Test cases for data classes."""

    def test_cache_metrics_creation(self):
        """Test CacheMetrics data class."""
        metrics = CacheMetrics(size=100, max_size=200,
                               hit_rate=0.85, hits=85, misses=15)

        assert metrics.size == 100
        assert metrics.max_size == 200
        assert metrics.hit_rate == 0.85
        assert metrics.hits == 85
        assert metrics.misses == 15

    def test_memory_metrics_creation(self):
        """Test MemoryMetrics data class."""
        metrics = MemoryMetrics(
            rss_mb=100.0,
            vms_mb=150.0,
            system_total_gb=16.0,
            system_available_gb=8.0
        )

        assert metrics.rss_mb == 100.0
        assert metrics.vms_mb == 150.0
        assert metrics.system_total_gb == 16.0
        assert metrics.system_available_gb == 8.0

    def test_extended_memory_metrics_creation(self):
        """Test ExtendedMemoryMetrics data class."""
        metrics = ExtendedMemoryMetrics(
            rss_mb=100.0,
            vms_mb=150.0,
            system_total_gb=16.0,
            system_available_gb=8.0,
            gc_collections=42,
            memory_growth_rate=2.5,
            memory_leaks_suspected=True,
            peak_memory_mb=200.0,
            memory_efficiency_score=75.0
        )

        assert metrics.rss_mb == 100.0
        assert metrics.gc_collections == 42
        assert metrics.memory_growth_rate == 2.5
        assert metrics.memory_leaks_suspected is True
        assert metrics.peak_memory_mb == 200.0
        assert metrics.memory_efficiency_score == 75.0

    def test_performance_metrics_creation(self):
        """Test PerformanceMetrics data class."""
        cache_metrics = CacheMetrics(100, 200, 0.85, 85, 15)
        memory_metrics = MemoryMetrics(100.0, 150.0, 16.0, 8.0)

        metrics = PerformanceMetrics(
            cache=cache_metrics,
            memory=memory_metrics,
            tts_state="playing"
        )

        assert metrics.cache == cache_metrics
        assert metrics.memory == memory_metrics
        assert metrics.tts_state == "playing"

    def test_log_level_control_in_production(self):
        """測試生產環境下的日誌級別控制"""
        import logging
        from speakub.utils.logging_config import set_runtime_log_level

        # 模擬生產環境設定
        set_runtime_log_level("performance", "WARNING")

        monitor = PerformanceMonitor()
        logger = logging.getLogger("speakub.utils.performance_monitor")

        # 驗證日誌級別已被設定為 WARNING
        assert logger.level == logging.WARNING

        # 在生產環境下，DEBUG 日誌不應輸出
        with patch('speakub.utils.performance_monitor.logger') as mock_logger:
            # 這些調用在 WARNING 級別下不應記錄
            monitor.record_cpu_usage(50.0)  # 正常 CPU
            monitor._collect_system_metrics()

            # 檢查沒有 DEBUG 日誌被記錄
            debug_calls = [call for call in mock_logger.debug.call_args_list]
            assert len(debug_calls) == 0, f"生產環境下不應有 DEBUG 日誌: {debug_calls}"

    def test_memory_efficient_deque_management(self):
        """測試記憶體高效的 deque 管理"""
        import psutil
        import os

        monitor = PerformanceMonitor(max_samples=100)  # 限制樣本數

        # 記錄初始記憶體使用
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # 模擬大量數據收集
        for i in range(200):  # 超過 max_samples
            monitor.record_memory_usage(100.0 + i)
            monitor.record_cpu_usage(50.0)
            monitor.record_synthesis_event(1.0, True)

        # 驗證 deque 大小被限制
        assert len(monitor._memory_metrics) <= 100
        assert len(monitor._cpu_metrics) <= 100
        assert len(monitor._synthesis_metrics) <= 100

        # 記錄最終記憶體使用
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # 記憶體增加應在合理範圍內（考慮測試環境差異）
        # 這裡只做基本檢查，實際值取決於系統
        assert memory_increase < 50 * 1024 * 1024  # 少於 50MB 增加

    def test_estimate_duration_log_optimization(self):
        """測試 _estimate_play_duration 的日誌優化"""
        from speakub.tts.fusion_reservoir.controller import SimpleReservoirController

        # 創建控制器實例
        playlist_manager = MagicMock()
        controller = SimpleReservoirController(playlist_manager)

        # 添加足夠的歷史數據來觸發 DEBUG 日誌
        for i in range(15):
            controller.record_playback_event(0, 1.0, 10)

        with patch('speakub.tts.fusion_reservoir.controller.logger') as mock_logger:
            # 調用估算函數
            result = controller._estimate_play_duration("測試文本")

            # 驗證結果合理
            assert isinstance(result, float)
            assert result > 0

            # 在有歷史數據時應記錄 DEBUG 日誌
            debug_calls = mock_logger.debug.call_args_list
            if len(controller.play_history) >= 10:
                assert len(debug_calls) > 0, "有足夠歷史數據時應記錄 DEBUG 日誌"


if __name__ == "__main__":
    pytest.main([__file__])
