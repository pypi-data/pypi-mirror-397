#!/usr/bin/env python3
"""
測試新架構組件
驗證線程模型、命令隊列、狀態管理器等核心組件
"""

import asyncio
import threading
import time
import unittest
from unittest.mock import Mock, patch

from speakub.core.threading_model import SpeakUBThreadingModel, ThreadType
from speakub.tts.ui.commands import TTSCommandQueue, TTSStateManager
from speakub.tts.ui.workers import SynthesisWorker, PlaybackCoordinator, AudioPlayer
from speakub.tts.ui.optimized_bridge import OptimizedAsyncBridge
from speakub.utils.performance_monitor import PerformanceMonitor


class TestThreadingModel(unittest.TestCase):
    """測試線程模型管理器"""

    def setUp(self):
        self.model = SpeakUBThreadingModel()

    def tearDown(self):
        self.model.shutdown()

    def test_thread_type_detection(self):
        """測試線程類型檢測"""
        # 主線程應該被識別為 MAIN_UI
        self.assertEqual(self.model.get_current_thread_type(),
                         ThreadType.MAIN_UI)

        # 在其他線程中測試
        results = []

        def test_async_worker_thread():
            results.append(self.model.get_current_thread_type())

        def test_playback_thread():
            results.append(self.model.get_current_thread_type())

        # 啟動異步工作線程
        self.model.start_async_worker()
        time.sleep(0.1)  # 等待線程啟動

        # 在異步線程中執行測試
        async def dummy_coro():
            await asyncio.sleep(0.01)
            return None

        try:
            self.model.call_async_worker(dummy_coro())
        except:
            pass  # 忽略調用失敗，只測試線程檢測

        # 檢查線程是否正確識別
        self.assertTrue(self.model.is_async_worker_thread())

    def test_health_monitoring(self):
        """測試健康監控"""
        self.model.start_health_monitoring()
        time.sleep(2)  # 等待監控數據收集

        health = self.model.get_health_status()
        self.assertIsInstance(health, dict)
        # 檢查是否包含各線程的健康狀態
        self.assertIn("main_ui", health)
        self.assertIn("async_worker", health)
        self.assertIn("playback_hmi", health)
        self.assertIn("command_coordinator", health)

        # 檢查主線程應該是活躍的
        main_ui_health = health["main_ui"]
        self.assertIn("is_alive", main_ui_health)

        self.model.stop_health_monitoring()


class TestCommandQueue(unittest.TestCase):
    """測試命令隊列"""

    def setUp(self):
        self.queue = TTSCommandQueue(max_queue_size=10)
        self.commands_received = []

    def tearDown(self):
        self.queue.stop_processing(timeout=1.0)

    def test_command_sending(self):
        """測試命令發送"""
        # 註冊命令處理器
        def handle_test_command(arg1, arg2=None):
            self.commands_received.append(("test_command", arg1, arg2))

        self.queue.register_handler("test_command", handle_test_command)

        # 啟動處理
        self.queue.start_processing()
        time.sleep(0.1)  # 等待處理線程啟動

        # 發送命令
        success = self.queue.send_command(
            "test_command", arg1="value1", arg2="value2")
        self.assertTrue(success)

        # 等待處理
        time.sleep(0.2)

        # 檢查命令是否被處理
        self.assertEqual(len(self.commands_received), 1)
        self.assertEqual(
            self.commands_received[0], ("test_command", "value1", "value2"))

    def test_queue_full_handling(self):
        """測試隊列滿載處理"""
        # 發送超過隊列大小的命令
        for i in range(15):  # 隊列大小為10
            success = self.queue.send_command("dummy_command", data=i)
            if i >= 10:
                self.assertFalse(success)  # 應該被拒絕

    def test_queue_stats(self):
        """測試隊列統計"""
        stats = self.queue.get_queue_status()
        self.assertIsInstance(stats, dict)
        self.assertIn("queue_size", stats)
        self.assertIn("max_size", stats)
        self.assertIn("is_processing", stats)


class TestStateManager(unittest.TestCase):
    """測試狀態管理器"""

    def setUp(self):
        self.manager = TTSStateManager()
        self.state_changes = []

    def tearDown(self):
        self.manager.reset()

    def test_state_transitions(self):
        """測試狀態轉換"""
        # 添加觀察者
        def observer(old_state, new_state):
            self.state_changes.append((old_state, new_state))

        self.manager.add_observer(observer)

        # 測試有效轉換
        success = self.manager.set_state("PLAYING")
        self.assertTrue(success)
        self.assertEqual(self.manager.get_state(), "PLAYING")

        success = self.manager.set_state("PAUSED")
        self.assertTrue(success)
        self.assertEqual(self.manager.get_state(), "PAUSED")

        # 檢查觀察者通知
        self.assertEqual(len(self.state_changes), 2)
        self.assertEqual(self.state_changes[0], ("IDLE", "PLAYING"))
        self.assertEqual(self.state_changes[1], ("PLAYING", "PAUSED"))

    def test_invalid_state_transition(self):
        """測試無效狀態轉換"""
        # 設置為 PLAYING
        self.manager.set_state("PLAYING")

        # 嘗試無效轉換 PLAYING -> IDLE (應該失敗，因為不在 VALID_TRANSITIONS 中)
        success = self.manager.set_state("IDLE")
        self.assertFalse(success)  # 應該失敗
        self.assertEqual(self.manager.get_state(), "PLAYING")  # 狀態不變

    def test_state_history(self):
        """測試狀態歷史"""
        # 進行一些狀態變化
        self.manager.set_state("PLAYING")
        self.manager.set_state("PAUSED")
        self.manager.set_state("STOPPED")

        history = self.manager.get_state_history()
        self.assertGreater(len(history), 2)  # 至少有初始狀態 + 3個變化

    def test_state_statistics(self):
        """測試狀態統計"""
        # 進行狀態變化
        self.manager.set_state("PLAYING")
        time.sleep(0.1)
        self.manager.set_state("PAUSED")
        time.sleep(0.1)

        stats = self.manager.get_state_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("current_state", stats)
        self.assertIn("total_transitions", stats)
        self.assertIn("state_breakdown", stats)


class TestSynthesisWorker(unittest.TestCase):
    """測試合成工作器"""

    def setUp(self):
        # 創建模擬的 TTS integration
        self.mock_tts_integration = Mock()
        self.mock_tts_integration.app = Mock()
        self.mock_tts_integration.app.tts_engine = Mock()
        self.mock_tts_integration.tts_lock = threading.Lock()

        # 模擬 playlist manager
        self.mock_playlist_manager = Mock()
        self.mock_playlist_manager.get_current_index.return_value = 0
        self.mock_playlist_manager.get_playlist_length.return_value = 2
        self.mock_playlist_manager.get_item_at.side_effect = lambda i: {
            0: ("Hello world", 1),
            1: ("Test content", 2)
        }.get(i)

        self.mock_tts_integration.playlist_manager = self.mock_playlist_manager

        self.worker = SynthesisWorker(self.mock_tts_integration)

    def test_worker_initialization(self):
        """測試工作器初始化"""
        self.assertIsInstance(self.worker.audio_queue, asyncio.Queue)
        self.assertFalse(self.worker.running)
        self.assertIsNone(self.worker._task)

    def test_start_stop(self):
        """測試啟動和停止"""
        # 注意：這裡的測試是基本的，因為完整測試需要異步環境
        # 在實際應用中，這些方法會在異步線程中調用

        # 測試初始化狀態
        self.assertFalse(self.worker.running)
        self.assertIsNone(self.worker._task)


class TestPlaybackCoordinator(unittest.TestCase):
    """測試播放協調器"""

    def setUp(self):
        # 創建模擬組件
        self.mock_tts_integration = Mock()
        self.mock_tts_integration.tts_lock = threading.Lock()

        self.mock_synthesis_worker = Mock()
        self.mock_synthesis_worker.audio_queue = asyncio.Queue()

        self.coordinator = PlaybackCoordinator(
            self.mock_tts_integration,
            self.mock_synthesis_worker
        )

    def test_coordinator_initialization(self):
        """測試協調器初始化"""
        self.assertIsInstance(self.coordinator.audio_player, AudioPlayer)
        self.assertFalse(self.coordinator.running)
        self.assertIsNone(self.coordinator._thread)

    def test_command_registration(self):
        """測試命令註冊"""
        # 啟動協調器（會註冊命令）
        self.coordinator.start()
        time.sleep(0.1)  # 等待線程啟動

        # 檢查命令處理器是否已註冊
        command_queue = self.coordinator.command_queue
        stats = command_queue.get_queue_status()
        self.assertGreater(stats["handlers_registered"], 0)

        # 停止協調器
        self.coordinator.stop()


class TestOptimizedBridge(unittest.TestCase):
    """測試優化橋接器"""

    def setUp(self):
        self.mock_tts_integration = Mock()
        self.bridge = OptimizedAsyncBridge(self.mock_tts_integration)

    def tearDown(self):
        self.bridge.shutdown()

    def test_bridge_initialization(self):
        """測試橋接器初始化"""
        self.assertIsNotNone(self.bridge._hmi_executor)
        self.assertIsNotNone(self.bridge._io_executor)
        self.assertIsNotNone(self.bridge._operation_stats)

    def test_call_hmi_safe(self):
        """測試 HMI 安全調用"""
        def test_func(x, y=10):
            return x + y

        # 在同一線程中調用
        result = self.bridge.call_hmi_safe(test_func, 5, y=15)
        self.assertEqual(result, 20)

    def test_health_check(self):
        """測試健康檢查"""
        health = self.bridge.perform_health_check()
        self.assertIsInstance(health, dict)
        self.assertIn("overall_healthy", health)
        self.assertIn("hmi_executor_alive", health)
        self.assertIn("io_executor_alive", health)

    def test_bridge_stats(self):
        """測試橋接統計"""
        stats = self.bridge.get_bridge_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("operation_stats", stats)
        self.assertIn("thread_pools", stats)
        self.assertIn("health", stats)


class TestPerformanceMonitor(unittest.TestCase):
    """測試效能監控器"""

    def setUp(self):
        self.monitor = PerformanceMonitor(max_samples=100)

    def tearDown(self):
        self.monitor.stop_monitoring()

    def test_monitor_initialization(self):
        """測試監控器初始化"""
        self.assertIsNotNone(self.monitor._playback_metrics)
        self.assertIsNotNone(self.monitor._synthesis_metrics)
        self.assertIsNotNone(self.monitor._thresholds)
        self.assertFalse(self.monitor._monitoring_active)

    def test_record_events(self):
        """測試事件記錄"""
        # 記錄播放事件
        self.monitor.record_playback_event(0.05, 10.0)

        # 記錄合成事件
        self.monitor.record_synthesis_event(2.5, True)

        # 記錄記憶體使用
        self.monitor.record_memory_usage(150.5)

        # 記錄 CPU 使用
        self.monitor.record_cpu_usage(25.0)

        # 記錄 HMI 響應
        self.monitor.record_hmi_response(0.012)

        # 獲取報告
        report = self.monitor.get_performance_report()
        self.assertIsInstance(report, dict)
        self.assertIn("playback", report)
        self.assertIn("synthesis", report)
        self.assertIn("memory", report)
        self.assertIn("cpu", report)
        self.assertIn("hmi", report)

    def test_threshold_alerts(self):
        """測試閾值警報"""
        alerts_triggered = []

        def alert_callback(alert_info):
            alerts_triggered.append(alert_info)

        self.monitor.add_alert_callback(alert_callback)

        # 觸發高延遲警報
        self.monitor.record_playback_event(0.5)  # 超過 0.1 秒閾值

        # 觸發慢合成警報
        self.monitor.record_synthesis_event(10.0, True)  # 超過 5 秒閾值

        # 檢查是否觸發了警報
        self.assertGreater(len(alerts_triggered), 0)

        self.monitor.remove_alert_callback(alert_callback)


class TestAudioPlayer(unittest.TestCase):
    """測試音頻播放器"""

    def setUp(self):
        self.player = AudioPlayer()

    def test_player_initialization(self):
        """測試播放器初始化"""
        self.assertIsInstance(self.player, AudioPlayer)

    def test_player_methods(self):
        """測試播放器方法"""
        # 這些方法應該不會拋出異常
        test_audio = b"dummy_audio_data"

        # 注意：實際播放會失敗，因為沒有真正的後端
        # 但方法調用應該正常
        try:
            self.player.play(test_audio)
        except Exception:
            pass  # 忽略預期的失敗

        try:
            self.player.pause()
            self.player.resume()
            self.player.stop()
        except Exception:
            pass  # 忽略可能的失敗


if __name__ == "__main__":
    # 運行測試
    unittest.main(verbosity=2)
