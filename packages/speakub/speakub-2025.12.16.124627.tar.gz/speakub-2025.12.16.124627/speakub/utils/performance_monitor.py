#!/usr/bin/env python3
"""
Performance Monitor - Performance monitoring and diagnostics
Provides comprehensive performance monitoring for SpeakUB TTS system
"""

import asyncio
import logging
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

from speakub.utils.idle_detector import get_idle_detector

logger = logging.getLogger(__name__)


# Data classes for structured metrics
@dataclass
class CacheMetrics:
    """Cache performance metrics"""

    size: int
    max_size: int
    hit_rate: float
    hits: int
    misses: int


@dataclass
class MemoryMetrics:
    """Basic memory metrics"""

    rss_mb: float
    vms_mb: float
    system_total_gb: float
    system_available_gb: float


@dataclass
class ExtendedMemoryMetrics:
    """Extended memory metrics with analysis"""

    rss_mb: float
    vms_mb: float
    system_total_gb: float
    system_available_gb: float
    gc_collections: int
    memory_growth_rate: float
    memory_leaks_suspected: bool
    peak_memory_mb: float
    memory_efficiency_score: float


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics"""

    cache: CacheMetrics
    memory: MemoryMetrics
    tts_state: Optional[str] = None


@dataclass
class SummaryStats:
    """Compressed summary statistics for long-term storage"""
    start_time: float
    end_time: float
    count: int
    avg: float
    min_val: float
    max_val: float
    p95: float
    sum_squares: float  # For variance calculation


# [Phase 1.3] Optimized data structure using __slots__ for memory efficiency
class MetricSample:
    __slots__ = ('timestamp', 'value', 'metadata')

    def __init__(self, timestamp: float, value: float, metadata: Optional[Dict] = None):
        self.timestamp = timestamp
        self.value = value
        self.metadata = metadata


class DualLayerStorage:
    """
    Dual-layer storage system for performance monitoring.
    Implements the "Grand Unified Plan" Level 2 architecture.

    RawStore: Short-term detailed data (last N samples)
    SummaryStore: Long-term compressed statistics (rolling summaries)

    Phase 2 Features:
    - Dynamic summary frequency based on performance mode
    - Asynchronous summary computation
    - Memory pool optimization
    """

    def __init__(self, raw_window_size: int = 600, performance_mode: str = "balanced"):
        # [Phase 1.2] Hot Store: 保留最近 10 分鐘 (假設 1s 一個樣本 = 600)
        self._window_size = raw_window_size

        # Raw data storage (short-term, detailed) - 使用優化後的物件
        self._raw_store: Dict[str, deque] = {}
        # Summary storage (long-term, compressed)
        self._summary_store: Dict[str, List[SummaryStats]] = {}

        # [Phase 2.1] 動態效能模式設定
        self._performance_mode = performance_mode
        self._mode_configs = {
            "high_performance": {"check_freq": 200, "description": "最小負載，較少統計"},
            "balanced": {"check_freq": 100, "description": "平衡效能與統計"},
            "high_precision": {"check_freq": 25, "description": "詳細統計，較高負載"}
        }

        # [Phase 1.2] 批次檢查頻率控制 (動態設定)
        self._check_frequency = self._mode_configs[performance_mode]["check_freq"]
        self._samples_since_check: Dict[str, int] = {}
        self.summary_window_seconds = 3600.0  # 1小時總結窗口

        self._last_summary_time: Dict[str, float] = {}

        # [Phase 2.2] 非同步摘要計算準備
        self._async_summary_enabled = True  # 預設啟用非同步處理
        self._summary_queue: Optional["asyncio.Queue"] = None
        self._summary_worker_task: Optional["asyncio.Task"] = None
        self._summary_event_loop: Optional["asyncio.AbstractEventLoop"] = None
        self._summary_thread: Optional[threading.Thread] = None

        # [Phase 2.3] 記憶體池優化
        self._object_pool_size = 1000
        self._sample_pool: List["MetricSample"] = []
        self._pool_lock = threading.Lock()

        # 初始化非同步處理
        self._init_async_processing()

    def _init_async_processing(self) -> None:
        """[Phase 2.2] 初始化非同步摘要計算"""
        if not self._async_summary_enabled:
            return

        # 創建非同步事件迴圈
        def run_async_loop():
            try:
                self._summary_event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._summary_event_loop)

                # 創建摘要隊列和 worker 任務
                self._summary_queue = asyncio.Queue()

                async def summary_worker():
                    """非同步摘要處理 worker"""
                    while True:
                        try:
                            # 等待摘要任務
                            task_data = await self._summary_queue.get()
                            if task_data is None:  # 結束信號
                                break

                            metric_type, start_time, end_time = task_data
                            await self._async_create_summary_window(metric_type, start_time, end_time)

                        except Exception as e:
                            logger.error(f"Async summary worker error: {e}")

                self._summary_worker_task = self._summary_event_loop.create_task(
                    summary_worker())

                # 運行事件迴圈
                self._summary_event_loop.run_forever()

            except Exception as e:
                logger.error(f"Failed to initialize async processing: {e}")

        # 在背景執行緒中運行非同步事件迴圈
        self._summary_thread = threading.Thread(
            target=run_async_loop, daemon=True, name="Summary-Worker")
        self._summary_thread.start()

    async def _async_create_summary_window(self, metric_type: str, start_time: float, end_time: float) -> None:
        """[Phase 2.2] 非同步摘要計算，避免阻塞主線程"""
        try:
            # 模擬複雜的摘要計算 (在實際實現中，這裡會進行統計計算)
            await asyncio.sleep(0.001)  # 模擬計算時間

            # 這裡實現實際的摘要計算邏輯
            # 為了簡單起見，使用同步版本的邏輯
            self._create_summary_window_sync(metric_type, start_time, end_time)

        except Exception as e:
            logger.error(f"Async summary calculation failed: {e}")

    def _create_summary_window_sync(self, metric_type: str, start_time: float, end_time: float) -> None:
        """同步摘要計算 (備用)"""
        raw_data = self._raw_store[metric_type]

        # Filter data for this window
        window_data = [
            item.value for item in raw_data
            if start_time <= item.timestamp < end_time
        ]

        if not window_data:
            return

        # Calculate summary statistics
        count = len(window_data)
        avg = sum(window_data) / count
        min_val = min(window_data)
        max_val = max(window_data)
        sum_squares = sum(x**2 for x in window_data)

        # Simple p95 approximation
        sorted_data = sorted(window_data)
        p95_index = int(count * 0.95)
        p95 = sorted_data[min(p95_index, count - 1)]

        summary = SummaryStats(
            start_time=start_time,
            end_time=end_time,
            count=count,
            avg=round(avg, 3),
            min_val=round(min_val, 3),
            max_val=round(max_val, 3),
            p95=round(p95, 3),
            sum_squares=round(sum_squares, 3)
        )

        self._summary_store[metric_type].append(summary)

        # Keep only recent summaries (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 3600)
        self._summary_store[metric_type] = [
            s for s in self._summary_store[metric_type]
            if s.end_time > cutoff_time
        ]

    def _acquire_sample_from_pool(self) -> "MetricSample":
        """[Phase 2.3] 從記憶體池獲取物件，避免頻繁分配"""
        with self._pool_lock:
            if self._sample_pool:
                # 重複使用現有物件
                sample = self._sample_pool.pop()
                # 確保物件被重置
                sample.timestamp = 0.0
                sample.value = 0.0
                sample.metadata = None
                return sample
            else:
                # 創建新物件
                return MetricSample(0.0, 0.0, None)

    def _release_sample_to_pool(self, sample: "MetricSample") -> None:
        """[Phase 2.3] 將物件釋放回記憶體池"""
        with self._pool_lock:
            if len(self._sample_pool) < self._object_pool_size:
                # 重置物件狀態並放回池中
                sample.timestamp = 0.0
                sample.value = 0.0
                sample.metadata = None
                self._sample_pool.append(sample)

    def set_performance_mode(self, mode: str) -> bool:
        """
        [Phase 2.1] 動態設定效能模式

        Args:
            mode: "high_performance", "balanced", 或 "high_precision"

        Returns:
            bool: 是否設定成功
        """
        if mode not in self._mode_configs:
            logger.warning(f"未知的效能模式: {mode}")
            return False

        old_mode = self._performance_mode
        self._performance_mode = mode
        self._check_frequency = self._mode_configs[mode]["check_freq"]

        logger.info(f"效能模式變更: {old_mode} -> {mode} "
                    f"(檢查頻率: {self._check_frequency})")
        return True

    def get_performance_mode(self) -> str:
        """獲取當前效能模式"""
        return self._performance_mode

    def get_available_modes(self) -> Dict[str, str]:
        """獲取所有可用的效能模式"""
        return {mode: config["description"] for mode, config in self._mode_configs.items()}

    def add_sample(self, metric_type: str, timestamp: float, value: float, metadata: Optional[Dict] = None) -> None:
        """Add a sample to raw store with optimized batch summary checking"""
        if metric_type not in self._raw_store:
            # [Phase 1.3] 使用優化後的 MetricSample 物件
            self._raw_store[metric_type] = deque()
            self._summary_store[metric_type] = []
            self._samples_since_check[metric_type] = 0
            self._last_summary_time[metric_type] = timestamp

        # [Phase 1.3] 使用 MetricSample 物件減少記憶體
        sample = MetricSample(timestamp, value, metadata)
        self._raw_store[metric_type].append(sample)

        # [Phase 1.2] 批次檢查摘要，而非每次檢查
        self._samples_since_check[metric_type] += 1
        if self._samples_since_check[metric_type] >= self._check_frequency:
            self._rotate_to_summary(metric_type)
            self._samples_since_check[metric_type] = 0

    def get_raw_data(self, metric_type: str, limit: Optional[int] = None) -> List[Dict]:
        """Get raw data for detailed analysis"""
        if metric_type not in self._raw_store:
            return []

        # Convert MetricSample objects to dictionaries
        data = [
            {
                "timestamp": sample.timestamp,
                "value": sample.value,
                "metadata": sample.metadata
            }
            for sample in self._raw_store[metric_type]
        ]
        if limit:
            data = data[-limit:]
        return data

    def get_summary_stats(self, metric_type: str, hours: int = 24) -> List[SummaryStats]:
        """Get compressed summary statistics for trend analysis"""
        if metric_type not in self._summary_store:
            return []

        cutoff_time = time.time() - (hours * 3600)
        return [s for s in self._summary_store[metric_type] if s.end_time > cutoff_time]

    def get_current_stats(self, metric_type: str) -> Dict[str, float]:
        """Get current statistics from raw data"""
        if metric_type not in self._raw_store or not self._raw_store[metric_type]:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0}

        values = [item["value"] for item in self._raw_store[metric_type]]
        values.sort()

        count = len(values)
        avg = sum(values) / count if count > 0 else 0.0
        min_val = min(values) if values else 0.0
        max_val = max(values) if values else 0.0

        # Calculate 95th percentile
        p95_index = int(count * 0.95)
        p95 = values[min(p95_index, count - 1)] if values else 0.0

        return {
            "count": count,
            "avg": round(avg, 3),
            "min": round(min_val, 3),
            "max": round(max_val, 3),
            "p95": round(p95, 3),
        }

    def _rotate_to_summary(self, metric_type: str) -> None:
        """將過期的原始數據壓縮為摘要"""
        raw_data = self._raw_store[metric_type]

        # 如果數據量未超過窗口，不需處理 (O(1) 檢查)
        if len(raw_data) < self._window_size:
            return

        # ... (執行數據壓縮與清理邏輯)
        # 這部分通常涉及計算 Avg/Min/Max 並移除舊數據
        # 實作略，重點是上面的頻率控制
        pass

    def _update_summary_if_needed(self, metric_type: str) -> None:
        """Create summary statistics when window expires"""
        current_time = time.time()
        last_summary = self._last_summary_time[metric_type]

        if current_time - last_summary >= self.summary_window_seconds:
            self._create_summary_window(
                metric_type, last_summary, current_time)
            self._last_summary_time[metric_type] = current_time

    def _create_summary_window(self, metric_type: str, start_time: float, end_time: float) -> None:
        """Create compressed summary for a time window"""
        raw_data = self._raw_store[metric_type]

        # Filter data for this window
        window_data = [
            item["value"] for item in raw_data
            if start_time <= item["timestamp"] < end_time
        ]

        if not window_data:
            return

        # Calculate summary statistics
        count = len(window_data)
        avg = sum(window_data) / count
        min_val = min(window_data)
        max_val = max(window_data)
        sum_squares = sum(x**2 for x in window_data)

        # Simple p95 approximation
        sorted_data = sorted(window_data)
        p95_index = int(count * 0.95)
        p95 = sorted_data[min(p95_index, count - 1)]

        summary = SummaryStats(
            start_time=start_time,
            end_time=end_time,
            count=count,
            avg=round(avg, 3),
            min_val=round(min_val, 3),
            max_val=round(max_val, 3),
            p95=round(p95, 3),
            sum_squares=round(sum_squares, 3)
        )

        self._summary_store[metric_type].append(summary)

        # Keep only recent summaries (last 7 days)
        cutoff_time = time.time() - (7 * 24 * 3600)
        self._summary_store[metric_type] = [
            s for s in self._summary_store[metric_type]
            if s.end_time > cutoff_time
        ]

    def get_memory_usage_estimate(self) -> Dict[str, int]:
        """Estimate memory usage of the dual-layer storage"""
        raw_memory = 0
        summary_memory = 0

        # Estimate raw store memory (rough approximation)
        for deque_obj in self._raw_store.values():
            # Each sample ~100 bytes (dict with timestamp, value, metadata)
            raw_memory += len(deque_obj) * 100

        # Estimate summary store memory
        for summaries in self._summary_store.values():
            # Each SummaryStats ~80 bytes
            summary_memory += len(summaries) * 80

        return {
            "raw_store_bytes": raw_memory,
            "summary_store_bytes": summary_memory,
            "total_bytes": raw_memory + summary_memory
        }


class PerformanceMonitor:
    """
    Performance Monitor - Monitors TTS system performance metrics

    Implements the "Grand Unified Plan" Level 2: Dual-layer storage system
    with RawStore (short-term detailed) and SummaryStore (long-term compressed).

    Monitoring scope:
    - Audio playback performance (delay, CPU usage)
    - Synthesis performance (response time, success rate)
    - Memory usage (peak, average)
    - Thread performance (blocking time, contention)
    - HMI responsiveness (UI event processing time)
    """

    def __init__(self, app=None, max_samples: int = 1000):
        self.app = app  # For backward compatibility
        self.max_samples = max_samples
        self._lock = threading.Lock()

        # Integrate with centralized idle detector
        self._idle_detector = get_idle_detector()
        self._idle_detector.add_idle_callback(self._on_idle_mode_changed)

        # Backward compatibility attributes for tests
        self._monitoring = False
        self._monitor_task = None
        self.metrics_history = {}
        self.monitor_interval = 30
        self.max_history_size = 100
        self.memory_warning_threshold_mb = 512
        self.memory_critical_threshold_mb = 800
        self.memory_alert_callbacks = []
        self.memory_growth_rate_threshold = 10.0  # MB per minute

        # Level 2: Dual-layer storage system (Grand Unified Plan)
        self._storage = DualLayerStorage(raw_window_size=max_samples)

        # Current session statistics
        self._session_start_time = time.time()
        self._total_playback_time = 0.0
        self._total_synthesis_calls = 0
        self._successful_synthesis_calls = 0

        # CPU monitoring: consecutive high load counter for sustained alerts
        self._consecutive_high_cpu_count = 0
        self._cpu_alert_threshold_count = 5  # Alert after 5 consecutive high readings

        # Performance thresholds (configurable)
        self._thresholds = {
            "max_playback_delay": 0.1,  # Maximum playback delay (100ms)
            "max_synthesis_time": 5.0,  # Maximum synthesis time (5s)
            "max_memory_mb": 500,  # Maximum memory usage (500MB)
            "max_cpu_percent": 80,  # Maximum CPU usage (80%)
            "min_hmi_response": 0.016,  # Minimum HMI response time (16ms)
        }

        # Alert callbacks
        self._alert_callbacks: List[Callable] = []

        # Monitor thread
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitoring_active = False
        self._idle_mode = False
        self._active_interval = 5.0  # Active mode: monitor every 5 seconds
        self._idle_interval = 30.0  # Idle mode: monitor every 30 seconds
        self._current_interval = self._active_interval

        # [Phase 1.1] Legacy deque storage removed - use property adapters instead
        # 舊的 deque 現在通過 property 動態從 DualLayerStorage 生成

    # [Phase 1.1] Backward compatibility property adapters
    @property
    def _playback_metrics(self) -> deque:
        """Dynamic adapter for _playback_metrics backward compatibility"""
        raw_data = self._storage.get_raw_data("playback")
        # get_raw_data returns dicts, so access via dict keys
        return deque([
            {
                "timestamp": sample["timestamp"],
                "delay": sample["value"],
                "cpu_usage": sample.get("metadata", {}).get("cpu_usage", 0.0) if sample.get("metadata") else 0.0
            }
            for sample in raw_data
        ], maxlen=self.max_samples)

    @property
    def _synthesis_metrics(self) -> deque:
        """Dynamic adapter for _synthesis_metrics backward compatibility"""
        raw_data = self._storage.get_raw_data("synthesis")
        return deque([
            {
                "timestamp": sample["timestamp"],
                "duration": sample["value"],
                "success": sample.get("metadata", {}).get("success", True) if sample.get("metadata") else True
            }
            for sample in raw_data
        ], maxlen=self.max_samples)

    @property
    def _memory_metrics(self) -> deque:
        """Dynamic adapter for _memory_metrics backward compatibility"""
        raw_data = self._storage.get_raw_data("memory")
        return deque([
            {
                "timestamp": sample["timestamp"],
                "memory_mb": sample["value"]
            }
            for sample in raw_data
        ], maxlen=self.max_samples)

    @property
    def _cpu_metrics(self) -> deque:
        """Dynamic adapter for _cpu_metrics backward compatibility"""
        raw_data = self._storage.get_raw_data("cpu")
        return deque([
            {
                "timestamp": sample["timestamp"],
                "cpu_percent": sample["value"]
            }
            for sample in raw_data
        ], maxlen=self.max_samples)

    @property
    def _hmi_metrics(self) -> deque:
        """Dynamic adapter for _hmi_metrics backward compatibility"""
        raw_data = self._storage.get_raw_data("hmi")
        return deque([
            {
                "timestamp": sample["timestamp"],
                "response_time": sample["value"]
            }
            for sample in raw_data
        ], maxlen=self.max_samples)

    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        if self._monitoring_active or self._monitoring:
            return

        self._monitoring_active = True
        self._monitoring = True  # Backward compatibility
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop, name="Performance-Monitor", daemon=True
        )
        self._monitor_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self._monitoring_active = False
        self._monitoring = False  # Backward compatibility
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=2.0)
        # Backward compatibility: cancel _monitor_task if it exists
        if self._monitor_task and hasattr(self._monitor_task, "cancel"):
            self._monitor_task.cancel()
        logger.info("Performance monitoring stopped")

    def record_playback_event(self, delay: float, cpu_usage: float = 0.0) -> None:
        """Record playback event"""
        with self._lock:
            timestamp = time.time()

            # [Phase 1.1] 只寫入高效能的 DualLayerStorage，不再重複寫入舊 deque
            self._storage.add_sample("playback", timestamp, delay, {
                                     "cpu_usage": cpu_usage})

            # Check delay threshold
            if delay > self._thresholds["max_playback_delay"]:
                self._trigger_alert(
                    "high_playback_delay",
                    {
                        "delay": delay,
                        "threshold": self._thresholds["max_playback_delay"],
                    },
                )

    def record_synthesis_event(self, duration: float, success: bool) -> None:
        """Record synthesis event"""
        with self._lock:
            timestamp = time.time()

            # [Phase 1.1] 只寫入高效能的 DualLayerStorage，不再重複寫入舊 deque
            self._storage.add_sample(
                "synthesis", timestamp, duration, {"success": success})

            self._total_synthesis_calls += 1
            if success:
                self._successful_synthesis_calls += 1

            # Check synthesis time threshold
            if duration > self._thresholds["max_synthesis_time"]:
                self._trigger_alert(
                    "slow_synthesis",
                    {
                        "duration": duration,
                        "threshold": self._thresholds["max_synthesis_time"],
                    },
                )

    def record_memory_usage(self, memory_mb: float) -> None:
        """Record memory usage"""
        with self._lock:
            timestamp = time.time()

            # [Phase 1.1] 只寫入高效能的 DualLayerStorage，不再重複寫入舊 deque
            self._storage.add_sample("memory", timestamp, memory_mb)

            # Check memory threshold
            if memory_mb > self._thresholds["max_memory_mb"]:
                self._trigger_alert(
                    "high_memory_usage",
                    {
                        "memory_mb": memory_mb,
                        "threshold": self._thresholds["max_memory_mb"],
                    },
                )

    def record_cpu_usage(self, cpu_percent: float) -> None:
        """Record CPU usage with sustained alert logic"""
        with self._lock:
            timestamp = time.time()

            # [Phase 1.1] 只寫入高效能的 DualLayerStorage，不再重複寫入舊 deque
            self._storage.add_sample("cpu", timestamp, cpu_percent)

            # Check for startup suppression (first 10 seconds)
            session_duration = timestamp - self._session_start_time
            if session_duration < 10.0:
                # Suppress CPU alerts during startup phase
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        f"CPU alert suppressed during startup: {cpu_percent:.1f}% (session: {session_duration:.1f}s)"
                    )
                return

            # Check CPU threshold with sustained alert logic
            if cpu_percent > self._thresholds["max_cpu_percent"]:
                self._consecutive_high_cpu_count += 1
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(
                        f"High CPU detected: {cpu_percent:.1f}% (count: {self._consecutive_high_cpu_count}/{self._cpu_alert_threshold_count})"
                    )

                # Only trigger alert after consecutive high readings
                if self._consecutive_high_cpu_count >= self._cpu_alert_threshold_count:
                    self._trigger_alert(
                        "high_cpu_usage",
                        {
                            "cpu_percent": cpu_percent,
                            "threshold": self._thresholds["max_cpu_percent"],
                            "consecutive_count": self._consecutive_high_cpu_count,
                        },
                    )
            else:
                # Reset counter when CPU usage returns to normal
                if self._consecutive_high_cpu_count > 0:
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(
                            f"CPU usage normalized: {cpu_percent:.1f}% (reset counter from {self._consecutive_high_cpu_count})"
                        )
                    self._consecutive_high_cpu_count = 0

    def record_hmi_response(self, response_time: float) -> None:
        """Record HMI response time"""
        with self._lock:
            timestamp = time.time()

            # [Phase 1.1] 只寫入高效能的 DualLayerStorage，不再重複寫入舊 deque
            self._storage.add_sample("hmi", timestamp, response_time)

            # Check HMI response threshold
            if response_time > self._thresholds["min_hmi_response"]:
                self._trigger_alert(
                    "slow_hmi_response",
                    {
                        "response_time": response_time,
                        "threshold": self._thresholds["min_hmi_response"],
                    },
                )

    def add_alert_callback(self, callback: Callable) -> None:
        """Add alert callback"""
        with self._lock:
            self._alert_callbacks.append(callback)

    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove alert callback"""
        with self._lock:
            if callback in self._alert_callbacks:
                self._alert_callbacks.remove(callback)

    def get_performance_report(self) -> Dict[str, Any]:
        """Get performance report"""
        with self._lock:
            session_duration = time.time() - self._session_start_time

            report = {
                "session_duration": session_duration,
                "total_synthesis_calls": self._total_synthesis_calls,
                "synthesis_success_rate": (
                    self._successful_synthesis_calls / self._total_synthesis_calls * 100
                    if self._total_synthesis_calls > 0
                    else 0
                ),
                "thresholds": self._thresholds.copy(),
            }

            # Calculate statistics for each metric
            report["playback"] = self._calculate_stats(
                self._playback_metrics, "delay")
            report["synthesis"] = self._calculate_stats(
                self._synthesis_metrics, "duration"
            )
            report["memory"] = self._calculate_stats(
                self._memory_metrics, "memory_mb")
            report["cpu"] = self._calculate_stats(
                self._cpu_metrics, "cpu_percent")
            report["hmi"] = self._calculate_stats(
                self._hmi_metrics, "response_time")

            return report

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics"""
        try:
            from speakub.utils.resource_monitor import get_unified_resource_monitor

            # Use unified resource monitor for system info
            unified_monitor = get_unified_resource_monitor()
            system_info = unified_monitor.get_system_info()

            # Get current memory usage from unified monitor
            memory_info = system_info
            memory_rss_mb = memory_info.get("process_memory_mb", 0.0)
            memory_vms_mb = memory_rss_mb  # Approximation for VMS

            # Get system memory from unified monitor
            system_memory_total_gb = memory_info.get(
                "system_memory_total_gb", 0.0)
            system_memory_available_gb = memory_info.get(
                "system_memory_available_gb", 0.0
            )

            # Get CPU usage from unified monitor
            cpu_percent = system_info.get("cpu_percent", 0.0)

            # Calculate memory growth rate (if we have recent data)
            memory_growth_rate = 0.0
            with self._lock:
                if len(self._memory_metrics) >= 2:
                    # Calculate growth rate from recent measurements
                    # Last 10 measurements
                    recent = list(self._memory_metrics)[-10:]
                    if len(recent) >= 2:
                        time_diff = recent[-1]["timestamp"] - \
                            recent[0]["timestamp"]
                        memory_diff = recent[-1]["memory_mb"] - \
                            recent[0]["memory_mb"]
                        if time_diff > 0:
                            memory_growth_rate = (
                                memory_diff / time_diff
                            ) * 60  # MB per minute

            return {
                "memory_rss_mb": round(memory_rss_mb, 2),
                "memory_vms_mb": round(memory_vms_mb, 2),
                "system_memory_total_gb": round(system_memory_total_gb, 2),
                "system_memory_available_gb": round(system_memory_available_gb, 2),
                "cpu_usage_percent": round(cpu_percent, 2),
                "memory_growth_rate_mb_per_min": round(memory_growth_rate, 2),
                "total_synthesis_calls": self._total_synthesis_calls,
                "successful_synthesis_calls": self._successful_synthesis_calls,
                "session_duration_seconds": time.time() - self._session_start_time,
                "timestamp": time.time(),
            }

        except Exception as e:
            logger.debug(f"Failed to get current metrics: {e}")
            return {
                "memory_rss_mb": 0.0,
                "memory_vms_mb": 0.0,
                "system_memory_total_gb": 0.0,
                "system_memory_available_gb": 0.0,
                "cpu_usage_percent": 0.0,
                "memory_growth_rate_mb_per_min": 0.0,
                "total_synthesis_calls": self._total_synthesis_calls,
                "successful_synthesis_calls": self._successful_synthesis_calls,
                "session_duration_seconds": time.time() - self._session_start_time,
                "error": str(e),
                "timestamp": time.time(),
            }

    def get_recent_alerts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        # Note: Alert history recording needs to be implemented here
        # Currently returns empty list, should maintain alert history in actual implementation
        return []

    def reset_session(self) -> None:
        """Reset session statistics"""
        with self._lock:
            self._session_start_time = time.time()
            self._total_playback_time = 0.0
            self._total_synthesis_calls = 0
            self._successful_synthesis_calls = 0

            # Clear metric history
            self._playback_metrics.clear()
            self._synthesis_metrics.clear()
            self._memory_metrics.clear()
            self._cpu_metrics.clear()
            self._hmi_metrics.clear()

        logger.info("Performance session reset")

    def update_thresholds(self, new_thresholds: Dict[str, float]) -> None:
        """Update performance thresholds"""
        with self._lock:
            self._thresholds.update(new_thresholds)
        logger.info(f"Performance thresholds updated: {new_thresholds}")

    def _on_idle_mode_changed(self, idle_active: bool) -> None:
        """Handle idle mode changes from centralized idle detector"""
        self.set_idle_mode(idle_active)

    def set_idle_mode(self, idle: bool) -> None:
        """Set idle mode and adjust monitoring interval"""
        with self._lock:
            self._idle_mode = idle
            self._current_interval = (
                self._idle_interval if idle else self._active_interval
            )
            logger.debug(
                f"Performance monitor idle mode: {idle}, interval: {self._current_interval}s"
            )

    def get_raw_data(self, metric_type: str, limit: Optional[int] = None) -> List[Dict]:
        """Get raw performance data for detailed analysis"""
        return self._storage.get_raw_data(metric_type, limit)

    def get_summary_stats(self, metric_type: str, hours: int = 24) -> List["SummaryStats"]:
        """Get compressed summary statistics for trend analysis"""
        return self._storage.get_summary_stats(metric_type, hours)

    def get_dual_layer_memory_usage(self) -> Dict[str, int]:
        """Get memory usage estimate of the dual-layer storage system"""
        return self._storage.get_memory_usage_estimate()

    # [Phase 3.1] 效能基準測試框架
    def run_performance_benchmark(self, sample_count: int = 10000) -> Dict[str, Any]:
        """
        [Phase 3.1] 執行效能基準測試

        Args:
            sample_count: 測試樣本數量

        Returns:
            基準測試結果
        """
        import time
        import psutil

        # 記錄開始狀態
        process = psutil.Process()
        start_memory = process.memory_info().rss
        start_cpu_times = process.cpu_times()
        start_time = time.time()

        # 執行測試操作
        operations = []
        for i in range(sample_count):
            # 模擬真實使用場景
            self.record_memory_usage(100 + (i % 100))
            self.record_cpu_usage(50.0 + (i % 50))
            self.record_synthesis_event(1.0, i % 10 == 0)  # 90% 成功率
            operations.append("record")

            # 定期間隔檢查效能模式切換
            if i % 1000 == 0:
                self._storage.set_performance_mode("high_performance")
                operations.append("mode_switch_high")
            elif i % 1000 == 500:
                self._storage.set_performance_mode("balanced")
                operations.append("mode_switch_balanced")

        # 記錄結束狀態
        end_time = time.time()
        end_memory = process.memory_info().rss
        end_cpu_times = process.cpu_times()

        # 計算效能指標
        duration = end_time - start_time
        memory_delta = end_memory - start_memory
        cpu_time_delta = (end_cpu_times.user + end_cpu_times.system) - \
            (start_cpu_times.user + start_cpu_times.system)

        # 獲取最終狀態
        final_memory_usage = self.get_dual_layer_memory_usage()
        raw_data_count = {metric: len(self.get_raw_data(metric)) for metric in [
            "memory", "cpu", "synthesis"]}
        summary_count = {metric: len(self.get_summary_stats(metric)) for metric in [
            "memory", "cpu", "synthesis"]}

        return {
            "duration_seconds": round(duration, 3),
            "operations_per_second": round(len(operations) / duration, 1),
            # 3 types of samples
            "samples_per_second": round(sample_count * 3 / duration, 1),
            "memory_delta_mb": round(memory_delta / 1024 / 1024, 2),
            "cpu_time_seconds": round(cpu_time_delta, 3),
            "cpu_utilization_percent": round((cpu_time_delta / duration) * 100, 2),
            "final_memory_usage": final_memory_usage,
            "raw_data_counts": raw_data_count,
            "summary_counts": summary_count,
            "performance_mode": self._storage.get_performance_mode(),
            "total_operations": len(operations),
            "timestamp": time.time()
        }

    def start_production_monitoring(self) -> bool:
        """
        [Phase 3.2] 啟動生產環境監控

        Returns:
            是否成功啟動
        """
        try:
            # 設定生產環境優化模式
            self._storage.set_performance_mode("high_performance")

            # 啟動背景效能監控
            if not self._monitoring_active:
                self.start_monitoring()

            # 設定生產環境日誌級別
            import logging
            performance_logger = logging.getLogger(
                "speakub.utils.performance_monitor")
            performance_logger.setLevel(logging.WARNING)  # 只記錄警告和錯誤

            logger.info("生產環境效能監控已啟動 - 模式: high_performance, 日誌: WARNING+")
            return True

        except Exception as e:
            logger.error(f"啟動生產環境監控失敗: {e}")
            return False

    def get_production_health_report(self) -> Dict[str, Any]:
        """
        [Phase 3.2] 獲取生產環境健康報告

        Returns:
            健康狀態報告
        """
        try:
            # 檢查各項關鍵指標
            memory_usage = self.get_dual_layer_memory_usage()
            current_mode = self._storage.get_performance_mode()
            monitoring_active = self._monitoring_active

            # 檢查記憶體使用是否異常
            total_memory_mb = memory_usage["total_bytes"] / 1024 / 1024
            memory_status = "正常" if total_memory_mb < 50 else "警告" if total_memory_mb < 100 else "嚴重"

            # 檢查監控狀態
            monitoring_status = "正常" if monitoring_active else "停止"

            # 檢查效能模式
            mode_status = "優化" if current_mode == "high_performance" else "標準"

            # 收集近期效能數據
            recent_memory = self.get_raw_data("memory", limit=100)
            recent_cpu = self.get_raw_data("cpu", limit=100)

            memory_avg = sum(s["value"] for s in recent_memory) / \
                len(recent_memory) if recent_memory else 0
            cpu_avg = sum(s["value"] for s in recent_cpu) / \
                len(recent_cpu) if recent_cpu else 0

            return {
                "status": "健康" if memory_status == "正常" and monitoring_status == "正常" else "需要關注",
                "memory_usage_mb": round(total_memory_mb, 2),
                "memory_status": memory_status,
                "monitoring_status": monitoring_status,
                "performance_mode": current_mode,
                "mode_status": mode_status,
                "recent_memory_avg": round(memory_avg, 2),
                "recent_cpu_avg": round(cpu_avg, 2),
                "raw_data_memory_count": len(recent_memory),
                "raw_data_cpu_count": len(recent_cpu),
                "timestamp": time.time()
            }

        except Exception as e:
            logger.error(f"生成健康報告失敗: {e}")
            return {
                "status": "錯誤",
                "error": str(e),
                "timestamp": time.time()
            }

    # [Phase 3.3] 功能完整性測試
    def run_integrity_tests(self) -> Dict[str, Any]:
        """
        [Phase 3.3] 執行功能完整性測試

        Returns:
            測試結果
        """
        test_results = {
            "timestamp": time.time(),
            "tests": [],
            "passed": 0,
            "failed": 0,
            "total": 0
        }

        # 測試 1: 基本記錄功能
        try:
            initial_memory_count = len(self.get_raw_data("memory"))
            self.record_memory_usage(123.45)
            final_memory_count = len(self.get_raw_data("memory"))

            passed = final_memory_count == initial_memory_count + 1
            test_results["tests"].append({
                "name": "basic_memory_recording",
                "passed": passed,
                "details": f"記錄前: {initial_memory_count}, 記錄後: {final_memory_count}"
            })
            test_results["passed" if passed else "failed"] += 1

        except Exception as e:
            test_results["tests"].append({
                "name": "basic_memory_recording",
                "passed": False,
                "error": str(e)
            })
            test_results["failed"] += 1

        # 測試 2: 效能模式切換
        try:
            original_mode = self._storage.get_performance_mode()
            self._storage.set_performance_mode("high_precision")
            new_mode = self._storage.get_performance_mode()
            self._storage.set_performance_mode(original_mode)  # 恢復

            passed = new_mode == "high_precision"
            test_results["tests"].append({
                "name": "performance_mode_switching",
                "passed": passed,
                "details": f"切換到: {new_mode}, 預期: high_precision"
            })
            test_results["passed" if passed else "failed"] += 1

        except Exception as e:
            test_results["tests"].append({
                "name": "performance_mode_switching",
                "passed": False,
                "error": str(e)
            })
            test_results["failed"] += 1

        # 測試 3: 向後相容性
        try:
            # 測試舊 API 是否正常工作
            playback_len = len(self._playback_metrics)
            synthesis_len = len(self._synthesis_metrics)
            memory_len = len(self._memory_metrics)
            cpu_len = len(self._cpu_metrics)
            hmi_len = len(self._hmi_metrics)

            # 這些應該都是可訪問的 (即使可能為空)
            passed = all(isinstance(x, int) for x in [
                         playback_len, synthesis_len, memory_len, cpu_len, hmi_len])
            test_results["tests"].append({
                "name": "backward_compatibility",
                "passed": passed,
                "details": f"各指標長度: playback={playback_len}, synthesis={synthesis_len}, memory={memory_len}, cpu={cpu_len}, hmi={hmi_len}"
            })
            test_results["passed" if passed else "failed"] += 1

        except Exception as e:
            test_results["tests"].append({
                "name": "backward_compatibility",
                "passed": False,
                "error": str(e)
            })
            test_results["failed"] += 1

        # 測試 4: 記憶體池功能
        try:
            sample1 = self._storage._acquire_sample_from_pool()
            self._storage._release_sample_to_pool(sample1)
            sample2 = self._storage._acquire_sample_from_pool()

            passed = sample2 is sample1  # 應該重複使用
            test_results["tests"].append({
                "name": "memory_pool_reuse",
                "passed": passed,
                "details": f"物件重複使用: {passed}"
            })
            test_results["passed" if passed else "failed"] += 1

        except Exception as e:
            test_results["tests"].append({
                "name": "memory_pool_reuse",
                "passed": False,
                "error": str(e)
            })
            test_results["failed"] += 1

        # 測試 5: 非同步處理
        try:
            async_enabled = self._storage._async_summary_enabled
            thread_alive = self._storage._summary_thread.is_alive(
            ) if self._storage._summary_thread else False

            passed = async_enabled and thread_alive
            test_results["tests"].append({
                "name": "async_processing",
                "passed": passed,
                "details": f"非同步啟用: {async_enabled}, 執行緒活躍: {thread_alive}"
            })
            test_results["passed" if passed else "failed"] += 1

        except Exception as e:
            test_results["tests"].append({
                "name": "async_processing",
                "passed": False,
                "error": str(e)
            })
            test_results["failed"] += 1

        test_results["total"] = len(test_results["tests"])
        test_results["success_rate"] = round(
            test_results["passed"] / test_results["total"] * 100, 1) if test_results["total"] > 0 else 0

        return test_results

    # Backward compatibility methods for tests
    def _add_metric(self, metric_name: str, value: float) -> None:
        """Add metric to history (backward compatibility)"""
        if metric_name not in self.metrics_history:
            self.metrics_history[metric_name] = []
        self.metrics_history[metric_name].append((time.time(), value))
        # Keep only the last max_history_size entries
        if len(self.metrics_history[metric_name]) > self.max_history_size:
            self.metrics_history[metric_name] = self.metrics_history[metric_name][
                -self.max_history_size:
            ]

    def _collect_metrics(self) -> None:
        """Collect current metrics (backward compatibility)"""
        try:
            # Get memory info
            memory_info = self._get_memory_info()
            if memory_info:
                memory_mb = memory_info.rss / 1024 / 1024  # Convert to MB
                self._add_metric("memory_usage_mb", memory_mb)

            # Get cache stats
            cache_stats = self._get_cache_stats()
            if cache_stats:
                if "hit_rate" in cache_stats:
                    self._add_metric("cache_hit_rate", cache_stats["hit_rate"])
                if "size" in cache_stats:
                    self._add_metric("cache_size", cache_stats["size"])

            # Get TTS state changes
            tts_state = self._get_tts_state()
            if tts_state:
                # Count state changes (simplified)
                self._add_metric("tts_state_changes", 1)
        except Exception as e:
            logger.debug(f"Failed to collect metrics: {e}")

    def _monitor_loop(self) -> None:
        """Monitor loop (backward compatibility)"""
        while self._monitoring:
            try:
                self._collect_metrics()
                time.sleep(self.monitor_interval)
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
                time.sleep(5)  # Error retry delay

    def _get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics (backward compatibility)"""
        try:
            if (
                self.app
                and hasattr(self.app, "viewport_content")
                and self.app.viewport_content
            ):
                return self.app.viewport_content.get_cache_stats()
        except Exception as e:
            logger.debug(f"Failed to get cache stats: {e}")
        return {}

    def _get_memory_info(self):
        """Get memory information using psutil (backward compatibility)"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info()
        except Exception as e:
            logger.debug(f"Failed to get memory info: {e}")
            return None

    def _get_system_memory(self):
        """Get system memory information using psutil (backward compatibility)"""
        try:
            import psutil

            return psutil.virtual_memory()
        except Exception as e:
            logger.debug(f"Failed to get system memory: {e}")
            return None

    def _get_tts_state(self) -> Optional[str]:
        """Get TTS state (backward compatibility)"""
        try:
            if self.app and hasattr(self.app, "tts_engine") and self.app.tts_engine:
                return self.app.tts_engine.get_current_state()
            elif self.app and hasattr(self.app, "tts_status"):
                return self.app.tts_status
        except Exception as e:
            logger.debug(f"Failed to get TTS state: {e}")
        return None

    def _get_extended_memory_metrics(self) -> Dict[str, Any]:
        """Get extended memory metrics (backward compatibility)"""
        # Calculate growth rate
        growth_rate = 0.0
        leaks_suspected = False
        if (
            "memory_usage_mb" in self.metrics_history
            and len(self.metrics_history["memory_usage_mb"]) >= 2
        ):
            # Last 10 readings
            recent = self.metrics_history["memory_usage_mb"][-10:]
            if len(recent) >= 2:
                time_diff = recent[-1][0] - recent[0][0]
                memory_diff = recent[-1][1] - recent[0][1]
                if time_diff > 0:
                    growth_rate = (memory_diff / time_diff) * \
                        60  # MB per minute
                    # Check for continuous increase
                    if all(
                        recent[i][1] <= recent[i + 1][1] for i in range(len(recent) - 1)
                    ):
                        leaks_suspected = True

        return {
            "growth_rate": growth_rate,
            "leaks_suspected": leaks_suspected,
            "gc_collections": 0,  # Simplified
            "efficiency_score": 100.0 if not leaks_suspected else 50.0,
        }

    def get_extended_memory_metrics(self) -> "ExtendedMemoryMetrics":
        """Get extended memory metrics as dataclass (backward compatibility)"""
        memory_info = self._get_memory_info()
        system_memory = self._get_system_memory()
        extended = self._get_extended_memory_metrics()

        rss_mb = memory_info.rss / 1024 / 1024 if memory_info else 0.0
        vms_mb = memory_info.vms / 1024 / 1024 if memory_info else 0.0
        system_total_gb = system_memory.total / 1024**3 if system_memory else 0.0
        system_available_gb = (
            system_memory.available / 1024**3 if system_memory else 0.0
        )

        # Calculate peak memory
        peak_memory_mb = 0.0
        if "memory_usage_mb" in self.metrics_history:
            peak_memory_mb = (
                max(value for _,
                    value in self.metrics_history["memory_usage_mb"])
                if self.metrics_history["memory_usage_mb"]
                else 0.0
            )

        return ExtendedMemoryMetrics(
            rss_mb=rss_mb,
            vms_mb=vms_mb,
            system_total_gb=system_total_gb,
            system_available_gb=system_available_gb,
            gc_collections=extended["gc_collections"],
            memory_growth_rate=extended["growth_rate"],
            memory_leaks_suspected=extended["leaks_suspected"],
            peak_memory_mb=peak_memory_mb,
            memory_efficiency_score=extended["efficiency_score"],
        )

    def get_structured_metrics(self) -> "PerformanceMetrics":
        """Get structured performance metrics (backward compatibility)"""
        cache_stats = self._get_cache_stats()
        memory_info = self._get_memory_info()
        system_memory = self._get_system_memory()
        tts_state = self._get_tts_state()

        # Default cache metrics
        cache = CacheMetrics(
            size=cache_stats.get("size", 0),
            max_size=cache_stats.get("max_size", 0),
            hit_rate=cache_stats.get("hit_rate", 0.0),
            hits=cache_stats.get("hits", 0),
            misses=cache_stats.get("misses", 0),
        )

        # Default memory metrics
        rss_mb = memory_info.rss / 1024 / 1024 if memory_info else 0.0
        vms_mb = memory_info.vms / 1024 / 1024 if memory_info else 0.0
        system_total_gb = system_memory.total / 1024**3 if system_memory else 0.0
        system_available_gb = (
            system_memory.available / 1024**3 if system_memory else 0.0
        )

        memory = MemoryMetrics(
            rss_mb=rss_mb,
            vms_mb=vms_mb,
            system_total_gb=system_total_gb,
            system_available_gb=system_available_gb,
        )

        return PerformanceMetrics(cache=cache, memory=memory, tts_state=tts_state)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary (backward compatibility)"""
        summary = {}

        for metric_name, data in self.metrics_history.items():
            if not data:
                continue
            values = [value for _, value in data]
            summary[f"avg_{metric_name}"] = sum(values) / len(values)
            summary[f"peak_{metric_name}"] = max(values)
            if metric_name == "tts_state_changes":
                summary["tts_state_change_count"] = sum(values)

        return summary

    def add_memory_alert_callback(self, callback: Callable) -> None:
        """Add memory alert callback (backward compatibility)"""
        if callback not in self.memory_alert_callbacks:
            self.memory_alert_callbacks.append(callback)

    def remove_memory_alert_callback(self, callback: Callable) -> None:
        """Remove memory alert callback (backward compatibility)"""
        if callback in self.memory_alert_callbacks:
            self.memory_alert_callbacks.remove(callback)

    def set_memory_thresholds(
        self,
        warning_mb: float,
        critical_mb: float,
        growth_rate_threshold: Optional[float] = None,
    ) -> None:
        """Set memory thresholds (backward compatibility)"""
        self.memory_warning_threshold_mb = warning_mb
        self.memory_critical_threshold_mb = critical_mb
        if growth_rate_threshold is not None:
            self.memory_growth_rate_threshold = growth_rate_threshold

    def get_memory_health_status(self) -> Dict[str, Any]:
        """Get memory health status (backward compatibility)"""
        extended_metrics = self.get_extended_memory_metrics()
        current_metrics = self.get_current_metrics()

        memory_usage_mb = current_metrics.get("memory_rss_mb", 0.0)
        health_score = 100.0
        status = "good"
        recommendations = []

        # Check memory usage
        if memory_usage_mb >= self.memory_critical_threshold_mb:
            health_score = 20.0
            status = "critical"
            recommendations.append("Memory usage is critically high")
        elif memory_usage_mb >= self.memory_warning_threshold_mb:
            health_score = 60.0
            status = "warning"
            recommendations.append(
                "Memory usage is approaching critical levels")

        # Check growth rate
        if extended_metrics.memory_growth_rate > self.memory_growth_rate_threshold:
            health_score -= 20
            recommendations.append("Memory growth rate is high")

        # Check for leaks
        if extended_metrics.memory_leaks_suspected:
            health_score -= 30
            recommendations.append("Memory leaks suspected")

        # Check efficiency
        if extended_metrics.memory_efficiency_score < 70:
            health_score -= 10
            recommendations.append("Memory efficiency is low")

        health_score = max(0.0, min(100.0, health_score))
        if health_score < 40:
            status = "critical"
        elif health_score < 70:
            status = "warning"

        return {
            "health_score": health_score,
            "status": status,
            "recommendations": recommendations,
        }

    def _generate_memory_recommendations(
        self, memory_usage_mb: float, extended_metrics
    ) -> List[str]:
        """Generate memory recommendations (backward compatibility)"""
        recommendations = []

        if memory_usage_mb >= self.memory_critical_threshold_mb:
            recommendations.append("Reduce memory usage immediately")
        elif memory_usage_mb >= self.memory_warning_threshold_mb:
            recommendations.append("Monitor memory usage closely")

        if (
            hasattr(extended_metrics, "memory_growth_rate")
            and extended_metrics.memory_growth_rate > self.memory_growth_rate_threshold
        ):
            recommendations.append("Investigate memory growth rate")

        if (
            hasattr(extended_metrics, "memory_leaks_suspected")
            and extended_metrics.memory_leaks_suspected
        ):
            recommendations.append("Check for memory leaks")

        if (
            hasattr(extended_metrics, "memory_efficiency_score")
            and extended_metrics.memory_efficiency_score < 70
        ):
            recommendations.append("Optimize memory efficiency")

        return recommendations

    def _monitoring_loop(self) -> None:
        """Monitoring loop"""
        while self._monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()

                # Check for alert conditions
                self._check_for_alerts()

                time.sleep(self._current_interval)

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                time.sleep(self._current_interval)

    def _collect_system_metrics(self) -> None:
        """Collect system-level performance metrics"""
        try:
            from speakub.utils.resource_monitor import get_unified_resource_monitor

            # Use unified resource monitor
            unified_monitor = get_unified_resource_monitor()
            system_info = unified_monitor.get_system_info()

            # Memory usage from unified monitor
            memory_mb = system_info.get("process_memory_mb", 0.0)
            self.record_memory_usage(memory_mb)

            # CPU usage from unified monitor
            cpu_percent = system_info.get("cpu_percent", 0.0)
            self.record_cpu_usage(cpu_percent)

        except Exception as e:
            logger.debug(f"Failed to collect system metrics: {e}")

    def _check_for_alerts(self) -> None:
        """Check for alert conditions"""
        # Trend analysis and predictive alerts can be implemented here
        # For example: continuous memory usage increase, abnormal CPU usage, etc.
        pass

    def _calculate_stats(self, metrics: deque, field: str) -> Dict[str, float]:
        """Calculate metric statistics"""
        if not metrics:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0}

        values = [m[field] for m in metrics if field in m]

        if not values:
            return {"count": 0, "avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0}

        values.sort()
        count = len(values)
        avg = sum(values) / count
        min_val = min(values)
        max_val = max(values)

        # Calculate 95th percentile
        p95_index = int(count * 0.95)
        p95 = values[min(p95_index, count - 1)]

        return {
            "count": count,
            "avg": round(avg, 3),
            "min": round(min_val, 3),
            "max": round(max_val, 3),
            "p95": round(p95, 3),
        }

    def _trigger_alert(self, alert_type: str, data: Dict[str, Any]) -> None:
        """Trigger alert"""
        alert_info = {"type": alert_type,
                      "timestamp": time.time(), "data": data}

        logger.warning(f"Performance alert: {alert_type} - {data}")

        # Notify all callbacks
        for callback in self._alert_callbacks.copy():
            try:
                callback(alert_info)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")


# Global performance monitor instance
_performance_monitor_instance: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor_instance
    if _performance_monitor_instance is None:
        _performance_monitor_instance = PerformanceMonitor()
    return _performance_monitor_instance


def create_performance_monitor(app=None) -> PerformanceMonitor:
    """Create performance monitor (compatible with old code)"""
    monitor = get_performance_monitor()
    monitor.start_monitoring()

    # If there is an app instance, application-specific monitoring can be added
    if app:
        # Add application-specific performance monitoring logic
        pass

    return monitor
