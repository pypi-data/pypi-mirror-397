#!/usr/bin/env python3
"""
Unified Resource Monitoring Interface for SpeakUB.
Combines memory monitoring, file cleanup, and performance tracking.
"""

import asyncio
import logging
import threading
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol

from speakub.utils.file_utils import (
    MEMORY_CRITICAL_THRESHOLD_MB,
    MEMORY_WARNING_THRESHOLD_MB,
)

logger = logging.getLogger(__name__)


@dataclass
class ResourceMetrics:
    """Unified resource metrics."""

    memory_mb: float
    memory_growth_rate: float
    temp_files_count: int
    temp_files_size_mb: float
    cache_hit_rate: float
    system_memory_available_gb: float
    timestamp: float


class ResourceMonitorProtocol(Protocol):
    """Protocol for resource monitoring components."""

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        ...

    def cleanup_resources(self) -> int:
        """Clean up resources, return number of items cleaned."""
        ...

    def start_monitoring(self) -> None:
        """Start monitoring."""
        ...

    def stop_monitoring(self) -> None:
        """Stop monitoring."""
        ...


class UnifiedResourceMonitor:
    """
    Unified resource monitoring interface that combines multiple monitoring components.
    """

    def __init__(self):
        self._monitors: List[ResourceMonitorProtocol] = []
        self._lock = threading.RLock()
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._alert_callbacks: List[Callable[[str, Dict[str, Any]], None]] = []

    def add_monitor(self, monitor: ResourceMonitorProtocol) -> None:
        """Add a resource monitor component."""
        with self._lock:
            if monitor not in self._monitors:
                self._monitors.append(monitor)
                logger.debug(f"Added monitor: {type(monitor).__name__}")

    def remove_monitor(self, monitor: ResourceMonitorProtocol) -> None:
        """Remove a resource monitor component."""
        with self._lock:
            if monitor in self._monitors:
                self._monitors.remove(monitor)
                logger.debug(f"Removed monitor: {type(monitor).__name__}")

    async def start_monitoring(self, interval_seconds: int = 30) -> None:
        """Start unified monitoring."""
        with self._lock:
            if self._monitoring:
                return

            self._monitoring = True
            self._monitor_task = asyncio.create_task(
                self._monitor_loop(interval_seconds)
            )

            # Start individual monitors
            for monitor in self._monitors:
                try:
                    await monitor.start_monitoring()
                except Exception as e:
                    logger.debug(
                        f"Failed to start monitor {type(monitor).__name__}: {e}"
                    )

            logger.info("Unified resource monitoring started")

    async def stop_monitoring(self) -> None:
        """Stop unified monitoring."""
        with self._lock:
            if not self._monitoring:
                return

            self._monitoring = False
            if self._monitor_task:
                self._monitor_task.cancel()
                try:
                    await self._monitor_task
                except asyncio.CancelledError:
                    pass

            # Stop individual monitors
            for monitor in self._monitors:
                try:
                    await monitor.stop_monitoring()
                except Exception as e:
                    logger.debug(
                        f"Failed to stop monitor {type(monitor).__name__}: {e}"
                    )

            logger.info("Unified resource monitoring stopped")

    async def _monitor_loop(self, interval: int) -> None:
        """Main monitoring loop."""
        while self._monitoring:
            try:
                self._collect_and_check_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.debug(f"Unified monitoring error: {e}")
                await asyncio.sleep(5)

    def _collect_and_check_metrics(self) -> None:
        """Collect metrics from all monitors and check for alerts."""
        all_metrics = {}

        with self._lock:
            for monitor in self._monitors:
                try:
                    metrics = monitor.get_metrics()
                    all_metrics.update(metrics)
                except Exception as e:
                    logger.debug(
                        f"Failed to get metrics from {type(monitor).__name__}: {e}"
                    )

        # Check for alerts
        self._check_resource_alerts(all_metrics)

    def _check_resource_alerts(self, metrics: Dict[str, Any]) -> None:
        """Check metrics against alert thresholds."""
        # Memory alerts
        memory_mb = metrics.get("memory_rss_mb", 0)
        if memory_mb > MEMORY_CRITICAL_THRESHOLD_MB:  # Critical threshold
            self._trigger_alert(
                "CRITICAL_MEMORY",
                f"Memory usage {memory_mb:.1f}MB exceeds critical threshold",
                {"memory_mb": memory_mb, "type": "memory"},
            )
        elif memory_mb > MEMORY_WARNING_THRESHOLD_MB:  # Warning threshold
            self._trigger_alert(
                "WARNING_MEMORY",
                f"Memory usage {memory_mb:.1f}MB exceeds warning threshold",
                {"memory_mb": memory_mb, "type": "memory"},
            )

        # File system alerts
        temp_files_count = metrics.get("temp_files_count", 0)
        if temp_files_count > 1000:  # Too many temp files
            self._trigger_alert(
                "TEMP_FILES_HIGH",
                f"Too many temporary files: {temp_files_count}",
                {"temp_files_count": temp_files_count, "type": "filesystem"},
            )

    def _trigger_alert(
        self, alert_type: str, message: str, data: Dict[str, Any]
    ) -> None:
        """Trigger resource alert."""
        alert_data = {
            "type": alert_type,
            "message": message,
            "timestamp": time.time(),
            **data,
        }

        logger.warning(f"[{alert_type}] {message}")

        # Call callbacks
        for callback in self._alert_callbacks[:]:
            try:
                callback(alert_type, alert_data)
            except Exception as e:
                logger.debug(f"Alert callback error: {e}")

    def add_alert_callback(
        self, callback: Callable[[str, Dict[str, Any]], None]
    ) -> None:
        """Add alert callback."""
        with self._lock:
            if callback not in self._alert_callbacks:
                self._alert_callbacks.append(callback)

    def get_unified_metrics(self) -> ResourceMetrics:
        """Get unified resource metrics."""
        all_metrics = {}

        with self._lock:
            for monitor in self._monitors:
                try:
                    metrics = monitor.get_metrics()
                    all_metrics.update(metrics)
                except Exception as e:
                    logger.debug(
                        f"Failed to get metrics from {type(monitor).__name__}: {e}"
                    )

        return ResourceMetrics(
            memory_mb=all_metrics.get("memory_rss_mb", 0.0),
            memory_growth_rate=all_metrics.get("memory_growth_rate_mb_per_min", 0.0),
            temp_files_count=all_metrics.get("temp_files_count", 0),
            temp_files_size_mb=all_metrics.get("total_temp_files_size_mb", 0.0),
            cache_hit_rate=all_metrics.get("cache_hit_rate", 0.0),
            system_memory_available_gb=all_metrics.get(
                "system_memory_available_gb", 0.0
            ),
            timestamp=time.time(),
        )

    def cleanup_all_resources(self) -> Dict[str, int]:
        """Clean up resources across all monitors."""
        results = {}

        with self._lock:
            for monitor in self._monitors:
                try:
                    cleaned = monitor.cleanup_resources()
                    results[type(monitor).__name__] = cleaned
                except Exception as e:
                    logger.debug(f"Failed to cleanup {type(monitor).__name__}: {e}")
                    results[type(monitor).__name__] = 0

        total_cleaned = sum(results.values())  # noqa: F841
        logger.info(f"Unified cleanup completed: {results}")

        return results

    def get_system_cpu_usage(self, interval: float = 0.1) -> float:
        """Get unified system CPU usage."""
        try:
            import psutil

            return psutil.cpu_percent(interval=interval)
        except ImportError:
            logger.debug("psutil not available for CPU monitoring")
            return 0.0

    def get_system_memory_info(self) -> Dict[str, float]:
        """Get unified system memory information."""
        try:
            import psutil

            memory = psutil.virtual_memory()
            process = psutil.Process()
            return {
                "system_memory_percent": memory.percent,
                "system_memory_available_gb": memory.available / (1024**3),
                "process_memory_mb": process.memory_info().rss / (1024**2),
                "system_memory_total_gb": memory.total / (1024**3),
            }
        except ImportError:
            logger.debug("psutil not available for memory monitoring")
            return {
                "system_memory_percent": 0.0,
                "system_memory_available_gb": 0.0,
                "process_memory_mb": 0.0,
                "system_memory_total_gb": 0.0,
            }

    def get_system_info(self) -> Dict[str, Any]:
        """Get unified system information."""
        return {
            "cpu_percent": self.get_system_cpu_usage(),
            **self.get_system_memory_info(),
            "timestamp": time.time(),
        }


# Adapter classes for existing monitors


class ResourceManagerAdapter(ResourceMonitorProtocol):
    """Adapter for ResourceManager to work with unified interface."""

    def __init__(self, resource_manager):
        self.resource_manager = resource_manager

    def get_metrics(self) -> Dict[str, Any]:
        return self.resource_manager.get_resource_stats()

    def cleanup_resources(self) -> int:
        # Clean up temp files by age and size
        age_cleaned = self.resource_manager.cleanup_temp_files_by_age()
        size_cleaned = self.resource_manager.cleanup_temp_files_by_size()
        return age_cleaned + size_cleaned

    async def start_monitoring(self) -> None:
        self.resource_manager.start_memory_monitoring()

    async def stop_monitoring(self) -> None:
        self.resource_manager.stop_memory_monitoring()


class PerformanceMonitorAdapter(ResourceMonitorProtocol):
    """Adapter for PerformanceMonitor to work with unified interface."""

    def __init__(self, performance_monitor):
        self.performance_monitor = performance_monitor

    def get_metrics(self) -> Dict[str, Any]:
        return self.performance_monitor.get_current_metrics()

    def cleanup_resources(self) -> int:
        # PerformanceMonitor doesn't directly manage resources
        # but we can trigger its cleanup logic
        return 0

    async def start_monitoring(self) -> None:
        self.performance_monitor.start_monitoring()

    async def stop_monitoring(self) -> None:
        self.performance_monitor.stop_monitoring()


class NetworkMonitorAdapter(ResourceMonitorProtocol):
    """Adapter for NetworkMonitor to work with unified interface."""

    def __init__(self, network_monitor):
        self.network_monitor = network_monitor

    def get_metrics(self) -> Dict[str, Any]:
        # Get basic network metrics from the monitor
        return {
            "network_latency_avg": sum(self.network_monitor.latency_history)
            / len(self.network_monitor.latency_history)
            if self.network_monitor.latency_history
            else 0.0,
            "network_failure_rate": self.network_monitor.failure_rate,
            "network_should_reduce_preloading": self.network_monitor.should_reduce_preloading(),
        }

    def cleanup_resources(self) -> int:
        # NetworkMonitor doesn't manage resources directly
        return 0

    async def start_monitoring(self) -> None:
        # NetworkMonitor doesn't have async start/stop methods
        pass

    async def stop_monitoring(self) -> None:
        # NetworkMonitor doesn't have async start/stop methods
        pass


# Global unified monitor instance
_unified_monitor = UnifiedResourceMonitor()


def get_unified_resource_monitor() -> UnifiedResourceMonitor:
    """Get the global unified resource monitor instance."""
    return _unified_monitor


# Phase 1: Basic memory monitoring utility function
def check_basic_memory_pressure() -> Dict[str, Any]:
    """
    Basic memory pressure check for resource leak detection.
    Phase 1 implementation - simple memory monitoring utility.
    """
    try:
        import psutil

        # Get basic memory stats
        memory = psutil.virtual_memory()
        process = psutil.Process()

        return {
            "system_memory_percent": memory.percent,
            "system_memory_available_gb": memory.available / (1024 * 1024 * 1024),
            "process_memory_mb": process.memory_info().rss / (1024 * 1024),
            "memory_pressure": "high"
            if memory.percent > 90
            else "medium"
            if memory.percent > 80
            else "low",
            "timestamp": time.time(),
        }
    except ImportError:
        # Fallback when psutil not available
        return {
            "system_memory_percent": 0.0,
            "system_memory_available_gb": 0.0,
            "process_memory_mb": 0.0,
            "memory_pressure": "unknown",
            "error": "psutil not available",
            "timestamp": time.time(),
        }
    except Exception as e:
        # Use unified error handler for logging
        logger.debug(f"Memory pressure check failed: {e}")
        return {
            "system_memory_percent": 0.0,
            "system_memory_available_gb": 0.0,
            "process_memory_mb": 0.0,
            "memory_pressure": "unknown",
            "error": str(e),
            "timestamp": time.time(),
        }
