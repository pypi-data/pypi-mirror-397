#!/usr/bin/env python3
"""
AsyncBridge 操作測試套件 - AsyncBridge Operations Test Suite

驗證AsyncBridge操作的分類正確性，確保關鍵操作同步等待，背景操作fire-and-forget。
防止UI/播放不同步問題。
"""

from speakub.tts.integration import AsyncBridge
import asyncio
import time
import pytest
from unittest.mock import Mock, patch, AsyncMock

# 確保可以匯入SpeakUB模組
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestAsyncBridgeCriticalOperations:
    """關鍵操作測試 - 必須同步等待"""

    def setup_method(self):
        """測試前準備"""
        # 創建模擬的TTSIntegration
        self.mock_tts_integration = Mock()
        self.mock_tts_integration._get_event_loop.return_value = asyncio.new_event_loop()

        # 創建AsyncBridge實例
        self.bridge = AsyncBridge(self.mock_tts_integration)

    def teardown_method(self):
        """測試後清理"""
        if hasattr(self, 'bridge') and self.bridge._event_loop:
            try:
                self.bridge._event_loop.close()
            except:
                pass

    @pytest.mark.asyncio
    async def test_run_coroutine_critical_operation(self):
        """測試關鍵操作的同步等待"""
        # 模擬一個異步操作
        async def mock_critical_operation():
            await asyncio.sleep(0.01)  # 模擬真實操作
            return "critical_result"

        # 執行關鍵操作
        start_time = time.time()
        result = self.bridge.run_coroutine(
            mock_critical_operation(), timeout=1.0)
        end_time = time.time()

        # 驗證結果
        assert result == "critical_result"

        # 驗證確實等待了操作完成（至少10ms）
        assert end_time - start_time >= 0.01

        # 驗證統計更新
        stats = self.bridge.get_bridge_stats()
        assert stats["coroutine_operations"]["total"] == 1
        assert stats["coroutine_operations"]["successful"] == 1

    def test_run_coroutine_timeout_handling(self):
        """測試關鍵操作超時處理"""
        async def slow_operation():
            await asyncio.sleep(2.0)  # 超過超時時間

        # 設定較短的超時
        with pytest.raises(asyncio.TimeoutError):
            self.bridge.run_coroutine(slow_operation(), timeout=0.1)

        # 驗證統計包含失敗
        stats = self.bridge.get_bridge_stats()
        assert stats["coroutine_operations"]["total"] == 1
        assert stats["coroutine_operations"]["successful"] == 0

    def test_event_operations_critical(self):
        """測試事件操作的關鍵性"""
        mock_event = AsyncMock()

        # 測試事件設置
        result = self.bridge.event_set(mock_event)
        assert result == True  # 在有事件循環時應成功

        # 驗證事件被調用
        mock_event.set.assert_called_once()

        # 測試事件清除
        mock_event.reset_mock()
        result = self.bridge.event_clear(mock_event)
        assert result == True

        mock_event.clear.assert_called_once()


class TestAsyncBridgeBackgroundOperations:
    """背景操作測試 - Fire-and-forget"""

    def setup_method(self):
        """測試前準備"""
        self.mock_tts_integration = Mock()
        self.mock_tts_integration._get_event_loop.return_value = asyncio.new_event_loop()
        self.bridge = AsyncBridge(self.mock_tts_integration)

    def teardown_method(self):
        """測試後清理"""
        if hasattr(self, 'bridge') and self.bridge._event_loop:
            try:
                self.bridge._event_loop.close()
            except:
                pass

    @pytest.mark.asyncio
    async def test_run_async_task_background_operation(self):
        """測試背景操作的fire-and-forget特性"""
        operation_completed = False

        async def mock_background_operation():
            nonlocal operation_completed
            await asyncio.sleep(0.1)
            operation_completed = True

        # 啟動背景操作（不等待）
        start_time = time.time()
        result = self.bridge.run_async_task(mock_background_operation())
        end_time = time.time()

        # 驗證立即返回（不等待操作完成）
        assert result == True
        assert end_time - start_time < 0.05  # 應在50ms內返回

        # 等待操作實際完成
        await asyncio.sleep(0.2)
        assert operation_completed == True

    def test_delegate_to_async_task_background(self):
        """測試委派異步任務的背景特性"""
        async def mock_task():
            await asyncio.sleep(0.1)
            return "task_result"

        # 委派任務
        result = self.bridge.delegate_to_async_task(mock_task(), "test_task")
        assert result == True

        # 驗證任務被添加到活躍任務集合
        assert hasattr(self.mock_tts_integration, '_tts_active_tasks')


class TestAsyncBridgeOperationClassification:
    """操作分類驗證測試"""

    def setup_method(self):
        """測試前準備"""
        self.mock_tts_integration = Mock()
        self.bridge = AsyncBridge(self.mock_tts_integration)

    def test_operation_requires_event_loop(self):
        """測試操作需要事件循環"""
        # 沒有事件循環時應拋出異常或返回False

        # 關鍵操作應拋出異常
        with pytest.raises(RuntimeError, match="Event loop not available"):
            self.bridge.run_coroutine(asyncio.sleep(0.001), timeout=1.0)

        # 背景操作應返回False
        result = self.bridge.run_async_task(asyncio.sleep(0.001))
        assert result == False

    def test_event_loop_detection(self):
        """測試事件循環檢測"""
        # 初始狀態下沒有事件循環
        assert not self.bridge.is_event_loop_available()

        # 設置事件循環後應可用
        loop = asyncio.new_event_loop()
        self.mock_tts_integration._get_event_loop.return_value = loop
        self.bridge._event_loop = loop

        assert self.bridge.is_event_loop_available()

        loop.close()


class TestAsyncBridgeStatisticsAndMonitoring:
    """統計和監控測試"""

    def setup_method(self):
        """測試前準備"""
        self.mock_tts_integration = Mock()
        self.bridge = AsyncBridge(self.mock_tts_integration)

    def test_initial_statistics(self):
        """測試初始統計狀態"""
        stats = self.bridge.get_bridge_stats()

        assert stats["event_operations"]["total"] == 0
        assert stats["event_operations"]["successful"] == 0
        assert stats["event_operations"]["success_rate"] == 0.0

        assert stats["coroutine_operations"]["total"] == 0
        assert stats["coroutine_operations"]["successful"] == 0
        assert stats["coroutine_operations"]["success_rate"] == 0.0

        assert stats["event_loop_available"] == False

    def test_statistics_accumulation(self):
        """測試統計累積"""
        # 模擬一些操作統計
        self.bridge._bridge_operations = 10
        self.bridge._successful_operations = 8
        self.bridge._coroutine_operations = 6
        self.bridge._successful_coroutines = 5

        stats = self.bridge.get_bridge_stats()

        assert stats["event_operations"]["total"] == 10
        assert stats["event_operations"]["successful"] == 8
        assert abs(stats["event_operations"]["success_rate"] - 80.0) < 0.1

        assert stats["coroutine_operations"]["total"] == 6
        assert stats["coroutine_operations"]["successful"] == 5
        assert abs(stats["coroutine_operations"]["success_rate"] - 83.33) < 0.1

    def test_success_rate_calculation_edge_cases(self):
        """測試成功率計算的邊界情況"""
        # 測試除零情況
        stats = self.bridge.get_bridge_stats()
        assert stats["event_operations"]["success_rate"] == 0.0
        assert stats["coroutine_operations"]["success_rate"] == 0.0

        # 測試100%成功率
        self.bridge._bridge_operations = 5
        self.bridge._successful_operations = 5

        stats = self.bridge.get_bridge_stats()
        assert stats["event_operations"]["success_rate"] == 100.0


class TestAsyncBridgeErrorHandling:
    """錯誤處理測試"""

    def setup_method(self):
        """測試前準備"""
        self.mock_tts_integration = Mock()
        self.mock_tts_integration._get_event_loop.return_value = asyncio.new_event_loop()
        self.bridge = AsyncBridge(self.mock_tts_integration)

    def teardown_method(self):
        """測試後清理"""
        if hasattr(self, 'bridge') and self.bridge._event_loop:
            try:
                self.bridge._event_loop.close()
            except:
                pass

    def test_coroutine_execution_error(self):
        """測試協程執行錯誤處理"""
        async def failing_operation():
            raise ValueError("Test error")

        # 應重新拋出異常
        with pytest.raises(ValueError, match="Test error"):
            self.bridge.run_coroutine(failing_operation(), timeout=1.0)

        # 驗證統計包含失敗
        stats = self.bridge.get_bridge_stats()
        assert stats["coroutine_operations"]["total"] == 1
        assert stats["coroutine_operations"]["successful"] == 0

    def test_event_operation_error(self):
        """測試事件操作錯誤處理"""
        mock_event = AsyncMock()
        mock_event.set.side_effect = Exception("Event error")

        # 應返回False表示失敗
        result = self.bridge.event_set(mock_event)
        assert result == False

        # 驗證統計包含失敗
        stats = self.bridge.get_bridge_stats()
        assert stats["event_operations"]["total"] == 1
        assert stats["event_operations"]["successful"] == 0


class TestAsyncBridgeIntegrationScenarios:
    """集成場景測試"""

    @pytest.mark.asyncio
    async def test_ui_update_scenario(self):
        """測試UI更新場景（關鍵操作）"""
        # 模擬UI更新需要同步等待
        ui_updated = False

        async def update_ui_async():
            nonlocal ui_updated
            await asyncio.sleep(0.01)  # 模擬UI更新時間
            ui_updated = True
            return "UI updated"

        mock_tts_integration = Mock()
        loop = asyncio.get_event_loop()
        mock_tts_integration._get_event_loop.return_value = loop

        bridge = AsyncBridge(mock_tts_integration)

        # UI更新必須等待完成
        result = bridge.run_coroutine(update_ui_async(), timeout=1.0)

        assert result == "UI updated"
        assert ui_updated == True

        bridge._event_loop.close()

    @pytest.mark.asyncio
    async def test_background_cleanup_scenario(self):
        """測試背景清理場景（fire-and-forget）"""
        # 模擬資源清理不需要等待
        cleanup_completed = False

        async def cleanup_resources_async():
            nonlocal cleanup_completed
            await asyncio.sleep(0.1)  # 模擬清理時間
            cleanup_completed = True

        mock_tts_integration = Mock()
        loop = asyncio.get_event_loop()
        mock_tts_integration._get_event_loop.return_value = loop

        bridge = AsyncBridge(mock_tts_integration)

        # 清理操作fire-and-forget
        start_time = time.time()
        result = bridge.run_async_task(cleanup_resources_async())
        immediate_time = time.time()

        assert result == True
        # 應立即返回，不等待清理完成
        assert immediate_time - start_time < 0.05

        # 清理應在背景繼續執行
        await asyncio.sleep(0.15)
        assert cleanup_completed == True

        bridge._event_loop.close()

    def test_mixed_operations_in_real_scenario(self):
        """測試真實場景中的混合操作"""
        # 這個測試模擬TTSIntegration中的典型使用模式

        mock_tts_integration = Mock()
        bridge = AsyncBridge(mock_tts_integration)

        # 關鍵操作：狀態變更（應拋出異常，因為沒有事件循環）
        with pytest.raises(RuntimeError):
            bridge.run_coroutine(asyncio.sleep(0.001), timeout=1.0)

        # 背景操作：統計收集（應返回False）
        result = bridge.run_async_task(asyncio.sleep(0.001))
        assert result == False

        # 檢查統計是否正確區分了操作類型
        stats = bridge.get_bridge_stats()
        assert stats["coroutine_operations"]["total"] == 1  # 關鍵操作嘗試
        assert stats["coroutine_operations"]["successful"] == 0  # 失敗


# 性能基準測試
class TestAsyncBridgePerformanceBenchmarks:
    """性能基準測試"""

    def setup_method(self):
        """測試前準備"""
        self.mock_tts_integration = Mock()
        loop = asyncio.new_event_loop()
        self.mock_tts_integration._get_event_loop.return_value = loop
        self.bridge = AsyncBridge(self.mock_tts_integration)

    def teardown_method(self):
        """測試後清理"""
        if hasattr(self, 'bridge') and self.bridge._event_loop:
            try:
                self.bridge._event_loop.close()
            except:
                pass

    @pytest.mark.asyncio
    async def test_bridge_operation_overhead(self):
        """測試橋接操作的性能開銷"""
        async def minimal_operation():
            return "result"

        # 測量直接異步調用的基準性能
        start_time = time.time()
        for _ in range(100):
            result = await minimal_operation()
            assert result == "result"
        direct_time = time.time() - start_time

        # 測量通過橋接器的性能
        start_time = time.time()
        for _ in range(100):
            result = self.bridge.run_coroutine(
                minimal_operation(), timeout=1.0)
            assert result == "result"
        bridge_time = time.time() - start_time

        # 橋接器的開銷應合理（不超過10倍）
        overhead_ratio = bridge_time / direct_time
        assert overhead_ratio < 10, f"橋接器開銷過高: {overhead_ratio:.1f}x"

    def test_bridge_statistics_memory_usage(self):
        """測試橋接統計的記憶體使用"""
        import psutil
        process = psutil.Process()

        # 測量基準記憶體
        baseline_memory = process.memory_info().rss

        # 創建橋接器並執行一些操作
        mock_tts_integration = Mock()
        bridge = AsyncBridge(mock_tts_integration)

        # 模擬統計累積
        bridge._bridge_operations = 1000
        bridge._successful_operations = 950
        bridge._coroutine_operations = 500
        bridge._successful_coroutines = 480

        # 測量記憶體使用
        stats_memory = process.memory_info().rss
        memory_increase = stats_memory - baseline_memory

        # 統計記憶體使用應合理（少於10MB）
        assert memory_increase < 10 * 1024 * \
            1024, f"統計記憶體使用過高: {memory_increase / 1024 / 1024:.1f}MB"


if __name__ == "__main__":
    pytest.main([__file__])
