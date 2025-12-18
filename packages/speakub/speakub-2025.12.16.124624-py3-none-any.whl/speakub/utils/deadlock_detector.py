#!/usr/bin/env python3
"""
死鎖檢測器 - Deadlock Detector

用於監控SpeakUB中的鎖定競爭和潛在死鎖風險。
基於保守策略：監控先行，優化後行。
"""

import asyncio
import logging
import threading
import time
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class LockType(Enum):
    """鎖定類型枚舉"""
    THREADING_RLOCK = "threading.RLock"
    THREADING_LOCK = "threading.Lock"
    ASYNCIO_LOCK = "asyncio.Lock"


@dataclass
class LockEvent:
    """鎖定事件記錄"""
    lock_name: str
    lock_type: LockType
    thread_id: int
    action: str  # "acquire", "release", "waiting"
    timestamp: float
    stack_trace: Optional[str] = None


@dataclass
class LockMonitor:
    """單個鎖定的監控器"""

    def __init__(self, name: str, lock_obj, lock_type: LockType):
        self.name = name
        self.lock_obj = lock_obj
        self.lock_type = lock_type
        self.acquire_count = 0
        self.wait_count = 0
        self.contention_time = 0.0
        self.last_acquire_time: Optional[float] = None
        self.holding_thread: Optional[int] = None
        self.waiting_threads: Set[int] = set()
        self.events: List[LockEvent] = []
        self.max_events = 100  # 保留最近100個事件

    def record_acquire(self, thread_id: int) -> None:
        """記錄鎖定獲取"""
        now = time.time()
        self.acquire_count += 1
        self.last_acquire_time = now
        self.holding_thread = thread_id

        if self.waiting_threads:
            wait_time = now - (self.last_acquire_time or now)
            self.contention_time += wait_time
            self.waiting_threads.clear()

        self._add_event("acquire", thread_id, now)

    def record_release(self, thread_id: int) -> None:
        """記錄鎖定釋放"""
        now = time.time()
        if self.holding_thread == thread_id:
            self.holding_thread = None

        self._add_event("release", thread_id, now)

    def record_wait(self, thread_id: int) -> None:
        """記錄鎖定等待"""
        self.wait_count += 1
        self.waiting_threads.add(thread_id)

        self._add_event("waiting", thread_id, time.time())

    def get_stats(self) -> Dict:
        """獲取統計信息"""
        total_operations = self.acquire_count + self.wait_count
        avg_contention = (
            self.contention_time / self.acquire_count
            if self.acquire_count > 0 else 0
        )

        return {
            "name": self.name,
            "type": self.lock_type.value,
            "acquire_count": self.acquire_count,
            "wait_count": self.wait_count,
            "contention_time": self.contention_time,
            "avg_contention_ms": avg_contention * 1000,
            "holding_thread": self.holding_thread,
            "waiting_threads": list(self.waiting_threads),
            "is_held": self.holding_thread is not None,
            "total_operations": total_operations,
        }

    def check_anomalies(self) -> List[str]:
        """檢查異常情況"""
        warnings = []

        # 長時間持有檢查
        if self.holding_thread and self.last_acquire_time:
            hold_time = time.time() - self.last_acquire_time
            thresholds = {
                LockType.THREADING_RLOCK: 0.1,  # 100ms
                LockType.THREADING_LOCK: 0.01,  # 10ms
                LockType.ASYNCIO_LOCK: 0.5,     # 500ms
            }

            threshold = thresholds.get(self.lock_type, 0.1)
            if hold_time > threshold:
                warnings.append(
                    f"Lock {self.name} held for {hold_time:.3f}s "
                    f"(threshold: {threshold:.3f}s)"
                )

        # 高競爭檢查
        if self.acquire_count > 0:
            wait_ratio = self.wait_count / self.acquire_count
            if wait_ratio > 0.1:  # 10%等待率
                warnings.append(
                    f"High contention on {self.name}: "
                    f"{self.wait_count}/{self.acquire_count} waits "
                    f"({wait_ratio:.1%})"
                )

        return warnings

    def _add_event(self, action: str, thread_id: int, timestamp: float) -> None:
        """添加事件記錄"""
        event = LockEvent(
            lock_name=self.name,
            lock_type=self.lock_type,
            thread_id=thread_id,
            action=action,
            timestamp=timestamp,
        )

        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.pop(0)


class DeadlockDetector:
    """
    死鎖檢測器主類

    功能：
    - 監控所有已註冊的鎖定
    - 檢測潛在死鎖模式
    - 生成鎖定依賴圖
    - 提供實時統計和警告
    """

    def __init__(self):
        self.monitors: Dict[str, LockMonitor] = {}
        self._monitoring_enabled = True
        self._check_interval = 1.0  # 每秒檢查一次
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # 死鎖檢測狀態
        self._dependency_graph: Dict[int, Set[int]] = {}
        self._last_check_time = time.time()

    def register_lock(self, name: str, lock_obj, lock_type: LockType) -> None:
        """註冊鎖定進行監控"""
        if name in self.monitors:
            logger.warning(f"Lock {name} already registered, replacing")

        self.monitors[name] = LockMonitor(name, lock_obj, lock_type)
        logger.debug(f"Registered lock monitoring: {name} ({lock_type.value})")

    def unregister_lock(self, name: str) -> None:
        """取消註冊鎖定監控"""
        if name in self.monitors:
            del self.monitors[name]
            logger.debug(f"Unregistered lock monitoring: {name}")

    def record_lock_event(self, lock_name: str, action: str, thread_id: Optional[int] = None) -> None:
        """記錄鎖定事件"""
        if not self._monitoring_enabled:
            return

        if lock_name not in self.monitors:
            logger.warning(f"Unknown lock {lock_name} in event recording")
            return

        monitor = self.monitors[lock_name]
        thread_id = thread_id or threading.get_ident()

        if action == "acquire":
            monitor.record_acquire(thread_id)
        elif action == "release":
            monitor.record_release(thread_id)
        elif action == "wait":
            monitor.record_wait(thread_id)

    def get_monitoring_stats(self) -> Dict:
        """獲取完整的監控統計"""
        lock_stats = {}
        all_warnings = []

        for name, monitor in self.monitors.items():
            lock_stats[name] = monitor.get_stats()
            all_warnings.extend(monitor.check_anomalies())

        # 整體統計
        total_acquires = sum(stat["acquire_count"]
                             for stat in lock_stats.values())
        total_waits = sum(stat["wait_count"] for stat in lock_stats.values())
        total_contention = sum(stat["contention_time"]
                               for stat in lock_stats.values())

        return {
            "monitoring_enabled": self._monitoring_enabled,
            "locks": lock_stats,
            "summary": {
                "total_locks": len(self.monitors),
                "total_acquires": total_acquires,
                "total_waits": total_waits,
                "total_contention_time": total_contention,
                "avg_contention_per_acquire": (
                    total_contention / total_acquires if total_acquires > 0 else 0
                ),
            },
            "warnings": all_warnings,
            "deadlock_detection": self._detect_deadlock_patterns(),
            "timestamp": time.time(),
        }

    def start_monitoring(self) -> None:
        """啟動背景監控線程"""
        if self._monitor_thread and self._monitor_thread.is_alive():
            logger.warning("Monitoring thread already running")
            return

        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            name="DeadlockMonitor",
            daemon=True
        )
        self._monitor_thread.start()
        logger.info("Deadlock monitoring started")

    def stop_monitoring(self) -> None:
        """停止監控"""
        self._stop_event.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
            if self._monitor_thread.is_alive():
                logger.warning("Monitoring thread did not stop cleanly")
        logger.info("Deadlock monitoring stopped")

    def _monitoring_loop(self) -> None:
        """監控循環"""
        while not self._stop_event.is_set():
            try:
                self._perform_monitoring_check()
                self._stop_event.wait(self._check_interval)
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    def _perform_monitoring_check(self) -> None:
        """執行監控檢查"""
        # 檢查異常
        all_warnings = []
        for monitor in self.monitors.values():
            all_warnings.extend(monitor.check_anomalies())

        if all_warnings:
            logger.warning(
                f"Lock anomalies detected: {len(all_warnings)} issues")
            for warning in all_warnings[:5]:  # 只記錄前5個
                logger.warning(f"  - {warning}")

        # 死鎖模式檢測
        deadlock_warnings = self._detect_deadlock_patterns()
        if deadlock_warnings:
            logger.error(
                f"Potential deadlock patterns detected: {len(deadlock_warnings)}")
            for warning in deadlock_warnings:
                logger.error(f"  - {warning}")

        # 定期記錄統計（每60秒）
        if time.time() - self._last_check_time > 60:
            stats = self.get_monitoring_stats()
            logger.info(
                f"Lock monitoring stats: {stats['summary']['total_acquires']} acquires, "
                f"{len(stats['warnings'])} warnings, "
                f"{stats['summary']['avg_contention_per_acquire']*1000:.1f}ms avg contention"
            )
            self._last_check_time = time.time()

    def _detect_deadlock_patterns(self) -> List[str]:
        """檢測潛在死鎖模式"""
        warnings = []

        # 簡單的循環等待檢測
        # 在生產環境中，這應該使用更複雜的算法

        # 檢查是否有鎖定長時間持有且有等待者
        for monitor in self.monitors.values():
            if (monitor.holding_thread and
                monitor.waiting_threads and
                    monitor.last_acquire_time):

                hold_time = time.time() - monitor.last_acquire_time
                if hold_time > 1.0:  # 超過1秒
                    waiting_count = len(monitor.waiting_threads)
                    warnings.append(
                        f"Potential deadlock: {monitor.name} held by thread "
                        f"{monitor.holding_thread} for {hold_time:.1f}s "
                        f"with {waiting_count} waiting threads"
                    )

        return warnings


# 全域死鎖檢測器實例
deadlock_detector = DeadlockDetector()


def get_deadlock_detector() -> DeadlockDetector:
    """獲取全域死鎖檢測器實例"""
    return deadlock_detector


def monitor_lock(lock_name: str, lock_type: LockType):
    """
    裝飾器：為鎖定添加監控

    使用示例：
    @monitor_lock("my_lock", LockType.THREADING_LOCK)
    def my_function():
        with my_lock:
            # 代碼
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            detector = get_deadlock_detector()
            detector.record_lock_event(lock_name, "wait")
            try:
                result = func(*args, **kwargs)
                detector.record_lock_event(lock_name, "acquire")
                return result
            finally:
                detector.record_lock_event(lock_name, "release")
        return wrapper
    return decorator
