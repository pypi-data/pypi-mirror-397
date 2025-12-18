#!/usr/bin/env python3
"""
死鎖預防測試套件 - Deadlock Prevention Test Suite

驗證SpeakUB的鎖定使用規範遵守情況，防止死鎖風險。
基於階段一建立的監控系統進行測試驗證。
"""

from speakub.utils.deadlock_detector import get_deadlock_detector, LockType
import asyncio
import threading
import time
import pytest
from unittest.mock import Mock, patch, MagicMock

# 確保可以匯入SpeakUB模組
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDeadlockPrevention:
    """死鎖預防測試類"""

    def setup_method(self):
        """測試前準備"""
        # 重置全域檢測器
        detector = get_deadlock_detector()
        # 清除所有監控鎖定
        detector.monitors.clear()
        detector._dependency_graph.clear()

    def teardown_method(self):
        """測試後清理"""
        detector = get_deadlock_detector()
        detector.monitors.clear()
        detector._dependency_graph.clear()

    def test_lock_hierarchy_registration(self):
        """測試鎖定層次結構正確註冊"""
        detector = get_deadlock_detector()

        # 註冊三層鎖定結構
        detector.register_lock(
            "_tts_lock", threading.RLock(), LockType.THREADING_RLOCK)
        detector.register_lock(
            "_async_tts_lock", asyncio.Lock(), LockType.ASYNCIO_LOCK)
        detector.register_lock(
            "_status_lock", threading.Lock(), LockType.THREADING_LOCK)

        # 驗證註冊成功
        assert len(detector.monitors) == 3
        assert "_tts_lock" in detector.monitors
        assert "_async_tts_lock" in detector.monitors
        assert "_status_lock" in detector.monitors

        # 驗證鎖定類型正確
        assert detector.monitors["_tts_lock"].lock_type == LockType.THREADING_RLOCK
        assert detector.monitors["_async_tts_lock"].lock_type == LockType.ASYNCIO_LOCK
        assert detector.monitors["_status_lock"].lock_type == LockType.THREADING_LOCK

    def test_lock_acquire_release_tracking(self):
        """測試鎖定獲取和釋放的正確追蹤"""
        detector = get_deadlock_detector()
        test_lock = threading.RLock()
        detector.register_lock("test_lock", test_lock,
                               LockType.THREADING_RLOCK)

        # 模擬鎖定操作
        detector.record_lock_event("test_lock", "acquire", 12345)
        detector.record_lock_event("test_lock", "acquire", 12345)  # RLock允許重入

        # 驗證統計
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["test_lock"]

        assert lock_stats["acquire_count"] == 2
        assert lock_stats["is_held"] == True
        assert lock_stats["holding_thread"] == 12345

        # 釋放鎖定
        detector.record_lock_event("test_lock", "release", 12345)
        detector.record_lock_event("test_lock", "release", 12345)

        # 驗證釋放後狀態
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["test_lock"]

        assert lock_stats["is_held"] == False
        assert lock_stats["holding_thread"] is None

    def test_lock_contention_detection(self):
        """測試鎖定競爭的檢測"""
        detector = get_deadlock_detector()
        test_lock = threading.Lock()
        detector.register_lock("test_lock", test_lock, LockType.THREADING_LOCK)

        # 模擬競爭場景
        detector.record_lock_event("test_lock", "acquire", 111)
        detector.record_lock_event("test_lock", "wait", 222)  # 另一個線程等待
        detector.record_lock_event("test_lock", "wait", 333)  # 第三個線程等待

        # 驗證競爭統計
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["test_lock"]

        assert lock_stats["wait_count"] == 2
        assert lock_stats["holding_thread"] == 111
        assert len(lock_stats["waiting_threads"]) == 2
        assert 222 in lock_stats["waiting_threads"]
        assert 333 in lock_stats["waiting_threads"]

    def test_lock_holding_time_limits(self):
        """測試鎖定持有時間限制的檢查"""
        detector = get_deadlock_detector()
        test_lock = threading.Lock()
        detector.register_lock("test_lock", test_lock, LockType.THREADING_LOCK)

        # 模擬長時間持有
        detector.record_lock_event("test_lock", "acquire", 111)

        # 模擬時間流逝（直接修改時間戳以測試）
        monitor = detector.monitors["test_lock"]
        monitor.last_acquire_time = time.time() - 2.0  # 2秒前獲取

        # 檢查異常
        anomalies = monitor.check_anomalies()
        assert len(anomalies) > 0
        assert "held for 2.000s" in anomalies[0]

        # 驗證整體統計包含警告
        stats = detector.get_monitoring_stats()
        assert len(stats["warnings"]) > 0

    def test_invalid_lock_event_handling(self):
        """測試無效鎖定事件的處理"""
        detector = get_deadlock_detector()

        # 嘗試記錄未註冊鎖定的事件
        detector.record_lock_event("nonexistent_lock", "acquire", 111)

        # 不應拋出異常，但應記錄警告（通過mock驗證）
        # 此測試確保系統穩定性

    def test_monitoring_stats_computation(self):
        """測試監控統計的正確計算"""
        detector = get_deadlock_detector()

        # 註冊多個鎖定
        locks = {
            "lock1": threading.RLock(),
            "lock2": asyncio.Lock(),
            "lock3": threading.Lock()
        }

        for name, lock_obj in locks.items():
            lock_type = LockType.THREADING_RLOCK if isinstance(lock_obj, threading.RLock) \
                else LockType.ASYNCIO_LOCK if isinstance(lock_obj, asyncio.Lock) \
                else LockType.THREADING_LOCK
            detector.register_lock(name, lock_obj, lock_type)

        # 模擬一些操作
        detector.record_lock_event("lock1", "acquire", 111)
        detector.record_lock_event("lock2", "acquire", 222)
        detector.record_lock_event("lock3", "wait", 333)

        # 驗證統計計算
        stats = detector.get_monitoring_stats()

        assert stats["summary"]["total_locks"] == 3
        assert stats["summary"]["total_acquires"] == 2
        assert stats["summary"]["total_waits"] == 1
        assert stats["monitoring_enabled"] == True

    @pytest.mark.asyncio
    async def test_async_lock_monitoring(self):
        """測試異步鎖定的監控"""
        detector = get_deadlock_detector()
        async_lock = asyncio.Lock()
        detector.register_lock("async_lock", async_lock, LockType.ASYNCIO_LOCK)

        # 模擬異步鎖定操作
        await async_lock.acquire()
        detector.record_lock_event(
            "async_lock", "acquire", threading.get_ident())

        # 驗證狀態
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["async_lock"]

        assert lock_stats["is_held"] == True
        assert lock_stats["acquire_count"] == 1

        # 釋放鎖定
        async_lock.release()
        detector.record_lock_event(
            "async_lock", "release", threading.get_ident())

        # 驗證釋放後狀態
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["async_lock"]

        assert lock_stats["is_held"] == False

    def test_deadlock_pattern_detection(self):
        """測試死鎖模式檢測"""
        detector = get_deadlock_detector()
        test_lock = threading.Lock()
        detector.register_lock("test_lock", test_lock, LockType.THREADING_LOCK)

        # 建立長時間持有的情況
        detector.record_lock_event("test_lock", "acquire", 111)

        # 模擬等待者
        detector.record_lock_event("test_lock", "wait", 222)

        # 將獲取時間設為超過1秒
        monitor = detector.monitors["test_lock"]
        monitor.last_acquire_time = time.time() - 2.0

        # 觸發死鎖檢測
        warnings = detector._detect_deadlock_patterns()

        assert len(warnings) > 0
        assert "Potential deadlock" in warnings[0]
        assert "held by thread 111" in warnings[0]
        assert "with 1 waiting threads" in warnings[0]

    def test_monitoring_enable_disable(self):
        """測試監控的啟用和禁用"""
        detector = get_deadlock_detector()
        test_lock = threading.Lock()
        detector.register_lock("test_lock", test_lock, LockType.THREADING_LOCK)

        # 預設啟用
        assert detector._monitoring_enabled == True

        # 禁用監控
        detector._monitoring_enabled = False
        detector.record_lock_event("test_lock", "acquire", 111)

        # 驗證未記錄
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["test_lock"]
        assert lock_stats["acquire_count"] == 0

        # 重新啟用
        detector._monitoring_enabled = True
        detector.record_lock_event("test_lock", "acquire", 111)

        # 驗證記錄恢復
        stats = detector.get_monitoring_stats()
        lock_stats = stats["locks"]["test_lock"]
        assert lock_stats["acquire_count"] == 1

    def test_event_history_management(self):
        """測試事件歷史記錄管理"""
        detector = get_deadlock_detector()
        test_lock = threading.Lock()
        detector.register_lock("test_lock", test_lock, LockType.THREADING_LOCK)

        # 生成多個事件
        for i in range(150):  # 超過預設限制100
            detector.record_lock_event("test_lock", "acquire", 111)
            detector.record_lock_event("test_lock", "release", 111)

        # 驗證事件數量被限制
        monitor = detector.monitors["test_lock"]
        assert len(monitor.events) <= 100  # 應維持在限制內

        # 驗證最新事件被保留
        latest_events = monitor.events[-10:]  # 最後10個事件
        # 應該都是最近的操作


class TestLockHierarchyCompliance:
    """鎖定層次結構遵守性測試"""

    def setup_method(self):
        """測試前準備"""
        self.detector = get_deadlock_detector()
        self.detector.monitors.clear()

        # 註冊標準的三層鎖定結構
        self.tts_lock = threading.RLock()
        self.async_lock = asyncio.Lock()
        self.status_lock = threading.Lock()

        self.detector.register_lock(
            "_tts_lock", self.tts_lock, LockType.THREADING_RLOCK)
        self.detector.register_lock(
            "_async_tts_lock", self.async_lock, LockType.ASYNCIO_LOCK)
        self.detector.register_lock(
            "_status_lock", self.status_lock, LockType.THREADING_LOCK)

    def test_valid_lock_acquisition_order(self):
        """測試有效的鎖定獲取順序"""
        # 單獨獲取各層鎖定應是安全的
        with self.tts_lock:
            self.detector.record_lock_event("_tts_lock", "acquire", 111)
            # 模擬操作
            time.sleep(0.001)
            self.detector.record_lock_event("_tts_lock", "release", 111)

        with self.status_lock:
            self.detector.record_lock_event("_status_lock", "acquire", 111)
            time.sleep(0.001)
            self.detector.record_lock_event("_status_lock", "release", 111)

    def test_lock_holding_time_compliance(self):
        """測試鎖定持有時間的遵守情況"""
        # 測試狀態層鎖定的時間限制 (< 10ms)
        start_time = time.time()
        with self.status_lock:
            self.detector.record_lock_event("_status_lock", "acquire", 111)
            # 模擬快速操作
            time.sleep(0.001)  # 1ms，符合限制
            self.detector.record_lock_event("_status_lock", "release", 111)

        # 驗證沒有異常（因為時間在限制內）
        stats = self.detector.get_monitoring_stats()
        warnings = stats.get("warnings", [])
        time_warnings = [
            w for w in warnings if "held for" in w and "_status_lock" in w]
        assert len(time_warnings) == 0  # 不應有時間警告

    def test_lock_contention_under_load(self):
        """測試負載下的鎖定競爭"""
        import concurrent.futures

        results = []

        def worker(worker_id):
            """模擬工作者線程"""
            try:
                # 嘗試獲取狀態鎖（應快速）
                with self.status_lock:
                    self.detector.record_lock_event(
                        "_status_lock", "acquire", worker_id)
                    time.sleep(0.0001)  # 非常短的操作
                    self.detector.record_lock_event(
                        "_status_lock", "release", worker_id)
                return True
            except Exception as e:
                return False

        # 啟動多個並發工作者
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            results = [f.result()
                       for f in concurrent.futures.as_completed(futures)]

        # 驗證所有操作成功
        assert all(results)

        # 檢查統計
        stats = self.detector.get_monitoring_stats()
        lock_stats = stats["locks"]["_status_lock"]

        assert lock_stats["acquire_count"] == 10
        # 競爭應該很低，因為操作很快


class TestAsyncBridgeOperationClassification:
    """AsyncBridge操作分類測試"""

    def setup_method(self):
        """測試前準備 - 模擬TTSIntegration環境"""
        self.detector = get_deadlock_detector()
        self.detector.monitors.clear()

        # 創建模擬的AsyncBridge
        from speakub.tts.integration import AsyncBridge
        self.bridge = AsyncBridge(None)  # 不需要真實的tts_integration進行基本測試

    def test_critical_operation_requires_wait(self):
        """測試關鍵操作需要等待"""
        # 關鍵操作應拋出異常如果事件循環不可用
        with pytest.raises(RuntimeError, match="Event loop not available"):
            # 這應該拋出異常，因為沒有事件循環
            self.bridge.run_coroutine(asyncio.sleep(0.001), timeout=1.0)

    def test_background_operation_fire_and_forget(self):
        """測試背景操作的fire-and-forget特性"""
        # 背景操作在事件循環不可用時應正常返回False
        result = self.bridge.run_async_task(asyncio.sleep(0.001))
        assert result == False  # 因為沒有事件循環

    def test_bridge_statistics_tracking(self):
        """測試橋接統計追蹤"""
        # 初始統計應為空
        stats = self.bridge.get_bridge_stats()
        assert stats["event_operations"]["total"] == 0
        assert stats["coroutine_operations"]["total"] == 0

        # 即使操作失敗，嘗試也應被計數（通過模擬）

    @pytest.mark.asyncio
    async def test_operation_success_rates(self):
        """測試操作成功率計算"""
        # 在有事件循環的情況下測試
        # 創建一個真實的AsyncBridge實例進行測試
        from speakub.tts.integration import TTSIntegration, AppInterface
        from speakub.utils.config import ConfigManager

        # 模擬最小化設置
        app_mock = Mock(spec=AppInterface)
        config_mock = Mock(spec=ConfigManager)
        config_mock.get.return_value = "default"

        # 注意：這個測試可能需要更完整的模擬環境
        # 在實際環境中，TTSIntegration會有完整的事件循環設置

        # 驗證統計計算邏輯（通過直接測試）
        bridge = AsyncBridge(None)

        # 模擬一些操作統計
        bridge._bridge_operations = 10
        bridge._successful_operations = 8
        bridge._coroutine_operations = 5
        bridge._successful_coroutines = 4

        stats = bridge.get_bridge_stats()

        assert stats["event_operations"]["total"] == 10
        assert stats["event_operations"]["successful"] == 8
        assert abs(stats["event_operations"]["success_rate"] - 80.0) < 0.1

        assert stats["coroutine_operations"]["total"] == 5
        assert stats["coroutine_operations"]["successful"] == 4
        assert abs(stats["coroutine_operations"]["success_rate"] - 80.0) < 0.1


# 性能基準測試
class TestPerformanceBenchmarks:
    """性能基準測試"""

    def test_lock_monitoring_overhead(self):
        """測試鎖定監控的性能開銷"""
        detector = get_deadlock_detector()
        test_lock = threading.Lock()
        detector.register_lock(
            "perf_test_lock", test_lock, LockType.THREADING_LOCK)

        # 測量無監控的基準性能
        start_time = time.time()
        for _ in range(1000):
            with test_lock:
                pass  # 空操作
        baseline_time = time.time() - start_time

        # 測量有監控的性能
        start_time = time.time()
        for _ in range(1000):
            detector.record_lock_event("perf_test_lock", "acquire", 111)
            with test_lock:
                pass  # 空操作
            detector.record_lock_event("perf_test_lock", "release", 111)
        monitored_time = time.time() - start_time

        # 監控開銷應小於10%
        overhead_ratio = (monitored_time - baseline_time) / baseline_time
        assert overhead_ratio < 0.1, f"監控開銷過高: {overhead_ratio:.1%}"

    def test_memory_usage_with_monitoring(self):
        """測試啟用監控時的記憶體使用"""
        import psutil
        process = psutil.Process()

        # 測量基準記憶體使用
        baseline_memory = process.memory_info().rss

        # 啟動監控系統
        detector = get_deadlock_detector()
        for i in range(100):  # 模擬大量鎖定
            lock_name = f"test_lock_{i}"
            test_lock = threading.Lock()
            detector.register_lock(lock_name, test_lock,
                                   LockType.THREADING_LOCK)

        # 測量監控後的記憶體使用
        monitored_memory = process.memory_info().rss
        memory_increase = monitored_memory - baseline_memory

        # 記憶體增加應合理（每鎖定少於1KB）
        memory_per_lock = memory_increase / 100
        assert memory_per_lock < 1024, f"記憶體開銷過高: {memory_per_lock} bytes per lock"


if __name__ == "__main__":
    pytest.main([__file__])
