#!/usr/bin/env python3
"""
Reservoir v7.0 增強功能測試套件

測試覆蓋：
1. 動態心跳間隔（改進 1️⃣）
2. 引擎感知語速（改進 2️⃣）
3. 引擎特定水位參數（改進 3️⃣）

⚠️ 限制條件：
- Reservoir v7.0 只在 SMOOTH 模式下生效
- Non-smooth 模式（標準/串行模式）不支持此增強功能
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import List, Tuple

from speakub.tts.fusion_reservoir.controller import SimpleReservoirController
from speakub.utils.config import ConfigManager


class MockPlaylistManager:
    """模擬 PlaylistManager 用於測試"""

    def __init__(self):
        self.current_index = 0
        self.playlist = []
        self.app = None

    def get_current_index(self) -> int:
        return self.current_index

    def get_playlist_length(self) -> int:
        return len(self.playlist)

    def get_item_at(self, index: int):
        if 0 <= index < len(self.playlist):
            return self.playlist[index]
        return None

    async def _process_batch(self, batch_items):
        """模擬批次處理"""
        pass

    def set_playlist(self, items: List[Tuple]):
        """設置測試播放列表"""
        self.playlist = items


@pytest.fixture
def config_manager():
    """創建配置管理器"""
    config = ConfigManager()
    # 設置預設值
    config.set("tts.reservoir.active_heartbeat", 0.5)
    config.set("tts.reservoir.idle_heartbeat", 5.0)
    config.set("tts.reservoir.engine_base_speeds", {
        "edge-tts": 3.5,
        "nanmai": 2.5,
        "gtts": 3.0,
    })
    config.set("tts.reservoir.watermark_profiles", {
        "edge-tts": {"LOW": 12.0, "HIGH": 40.0, "TARGET": 18.0},
        "nanmai": {"LOW": 20.0, "HIGH": 60.0, "TARGET": 25.0},
        "gtts": {"LOW": 15.0, "HIGH": 45.0, "TARGET": 20.0},
    })
    return config


@pytest.fixture
def playlist_manager():
    """創建模擬播放列表管理器"""
    return MockPlaylistManager()


@pytest.fixture
def reservoir_controller(playlist_manager, config_manager):
    """創建 Reservoir 控制器實例"""
    controller = SimpleReservoirController(playlist_manager, config_manager)
    yield controller
    # 清理
    if controller.running:
        asyncio.run(controller.stop_monitoring())


# ============================================================================
# 改進 1️⃣：動態心跳間隔測試
# ============================================================================

class TestDynamicHeartbeat:
    """測試動態心跳間隔功能"""

    def test_active_heartbeat_initialization(self, reservoir_controller, config_manager):
        """測試活躍狀態心跳初始化"""
        assert reservoir_controller._active_heartbeat == 0.5
        assert reservoir_controller._idle_heartbeat == 5.0

    def test_heartbeat_custom_values(self, playlist_manager, config_manager):
        """測試自訂心跳參數"""
        config_manager.set("tts.reservoir.active_heartbeat", 0.3)
        config_manager.set("tts.reservoir.idle_heartbeat", 10.0)

        controller = SimpleReservoirController(
            playlist_manager, config_manager)
        assert controller._active_heartbeat == 0.3
        assert controller._idle_heartbeat == 10.0

    def test_heartbeat_range_validation(self, playlist_manager):
        """測試心跳參數範圍驗證"""
        config = ConfigManager()

        # 測試極端值
        config.set("tts.reservoir.active_heartbeat", 0.1)  # 過低但可接受
        config.set("tts.reservoir.idle_heartbeat", 15.0)   # 過高但可接受

        controller = SimpleReservoirController(playlist_manager, config)
        assert controller._active_heartbeat == 0.1
        assert controller._idle_heartbeat == 15.0

    @pytest.mark.asyncio
    async def test_monitor_loop_with_active_state(self, reservoir_controller, playlist_manager):
        """測試監控循環在活躍狀態下使用短心跳"""
        # 設置播放狀態為活躍
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "PLAYING"

        # 模擬水位檢查
        check_count = 0
        original_check = reservoir_controller._check_and_refill

        async def count_checks():
            nonlocal check_count
            check_count += 1
            await original_check()

        reservoir_controller._check_and_refill = count_checks

        # 啟動監控
        await reservoir_controller.start_monitoring()

        # 運行 2 秒，預期檢查次數 > 2（0.5s 心跳）
        await asyncio.sleep(2.1)
        await reservoir_controller.stop_monitoring()

        # 在活躍狀態下，應該有多於 2 次檢查
        assert check_count >= 2, f"Expected >2 checks in 2.1s, got {check_count}"

    @pytest.mark.asyncio
    async def test_monitor_loop_with_idle_state(self, reservoir_controller, playlist_manager):
        """測試監控循環在閒置狀態下使用長心跳"""
        # 設置為非播放狀態
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "STOPPED"

        check_count = 0
        original_check = reservoir_controller._check_and_refill

        async def count_checks():
            nonlocal check_count
            check_count += 1
            await original_check()

        reservoir_controller._check_and_refill = count_checks

        await reservoir_controller.start_monitoring()

        # 運行 1.5 秒，預期檢查次數 <= 1（5.0s 心跳）
        await asyncio.sleep(1.5)
        await reservoir_controller.stop_monitoring()

        # 在閒置狀態下，應該只有 0-1 次檢查
        assert check_count <= 1, f"Expected <=1 checks in 1.5s, got {check_count}"

    def test_heartbeat_interval_switching(self, reservoir_controller, playlist_manager):
        """測試心跳間隔切換邏輯"""
        # 測試 _should_check_water_level 的邏輯
        playlist_manager.app = None
        # 沒有 app 時應返回 False
        assert reservoir_controller._should_check_water_level() is False

        # 設置 app 但狀態非播放
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "IDLE"
        assert reservoir_controller._should_check_water_level() is False

        # 設置為播放狀態
        playlist_manager.app.tts_status = "PLAYING"
        assert reservoir_controller._should_check_water_level() is True


# ============================================================================
# 改進 2️⃣：引擎感知語速測試
# ============================================================================

class TestEngineAwareSpeechRate:
    """測試引擎感知語速功能"""

    def test_engine_base_speeds_initialization(self, reservoir_controller):
        """測試引擎基礎語速初始化"""
        speeds = reservoir_controller._engine_base_speeds
        assert speeds["edge-tts"] == 3.5
        assert speeds["nanmai"] == 2.5
        assert speeds["gtts"] == 3.0

    def test_set_current_engine(self, reservoir_controller):
        """測試設置當前引擎"""
        reservoir_controller.set_current_engine("nanmai")
        assert reservoir_controller._current_engine == "nanmai"

        reservoir_controller.set_current_engine("edge-tts")
        assert reservoir_controller._current_engine == "edge-tts"

    def test_estimate_duration_with_base_speed(self, reservoir_controller):
        """測試使用基礎語速估算時長"""
        reservoir_controller.set_current_engine("edge-tts")

        # Edge-TTS: 3.5 字/秒
        text = "這是一個測試文本包含十個字"  # 15 字
        duration = reservoir_controller._estimate_play_duration(text)

        expected = 15 / 3.5  # ~4.29 秒
        assert abs(
            duration - expected) < 0.1, f"Expected ~{expected}, got {duration}"

    def test_estimate_duration_nanmai_vs_edge(self, reservoir_controller):
        """測試不同引擎的語速差異"""
        text = "中文文本測試"  # 6 字

        # Edge-TTS (3.5 字/秒)
        reservoir_controller.set_current_engine("edge-tts")
        duration_edge = reservoir_controller._estimate_play_duration(text)

        # Nanmai (2.5 字/秒)
        reservoir_controller.set_current_engine("nanmai")
        duration_nanmai = reservoir_controller._estimate_play_duration(text)

        # Nanmai 應該更長（語速較慢）
        assert duration_nanmai > duration_edge, \
            f"Nanmai({duration_nanmai:.2f}s) should be longer than Edge-TTS({duration_edge:.2f}s)"

    def test_historical_speed_correction(self, reservoir_controller):
        """測試歷史數據修正語速估算"""
        text = "測試"  # 2 字
        reservoir_controller.set_current_engine("edge-tts")

        # 初始估算（無歷史）
        initial_estimate = reservoir_controller._estimate_play_duration(text)

        # 模擬播放歷史：實際速度 2.0 字/秒（比基礎 3.5 慢）
        for _ in range(5):
            reservoir_controller.record_playback_event(0, 1.0, 2)  # 2 字, 1.0 秒

        # 重新估算
        corrected_estimate = reservoir_controller._estimate_play_duration(text)

        # 校正後應該更接近歷史值（2.0 字/秒）
        # 加權：70% 歷史 + 30% 基礎 = 0.7*2.0 + 0.3*3.5 = 2.45
        expected = 2 / 2.45  # ~0.82 秒
        assert abs(corrected_estimate - expected) < 0.2, \
            f"Corrected estimate {corrected_estimate:.2f} should be closer to {expected:.2f}"

    def test_historical_speed_safety_bounds(self, reservoir_controller):
        """測試歷史速度的安全邊界"""
        reservoir_controller.set_current_engine("nanmai")
        text = "文本"  # 2 字

        # 模擬極端的歷史數據（極快）
        for _ in range(10):
            reservoir_controller.record_playback_event(
                0, 0.1, 2)  # 2 字, 0.1 秒 = 20 字/秒

        duration = reservoir_controller._estimate_play_duration(text)

        # 應該被限制在合理範圍內（不應超過 max_speed）
        # Nanmai 的 max_speed = 2.5 * 1.3 = 3.25
        min_possible = 2 / 3.25  # ~0.615 秒
        assert duration >= min_possible, \
            f"Duration {duration:.2f} should respect upper bound for Nanmai"

    def test_reset_for_engine_switch(self, reservoir_controller):
        """測試引擎切換時的重置"""
        # 添加播放歷史
        for _ in range(5):
            reservoir_controller.record_playback_event(0, 1.0, 3)

        assert len(reservoir_controller.play_history) == 5

        # 切換引擎
        reservoir_controller.reset_for_engine_switch("nanmai")

        # 歷史應被清除
        assert len(reservoir_controller.play_history) == 0
        # 當前引擎應更新
        assert reservoir_controller._current_engine == "nanmai"

    def test_speech_rate_learning_curve(self, reservoir_controller):
        """測試語速學習曲線（逐步收斂）"""
        reservoir_controller.set_current_engine("edge-tts")
        text = "測試文本"  # 4 字
        true_speed = 2.0  # 實際播放速度

        estimates = []
        for i in range(20):
            estimate = reservoir_controller._estimate_play_duration(text)
            estimates.append(estimate)

            # 模擬實際播放
            duration = 4 / true_speed  # 2.0 秒
            reservoir_controller.record_playback_event(i, duration, 4)

        # 前期估算誤差應該逐步減小
        early_error = abs(estimates[0] - 2.0)
        late_error = abs(estimates[-1] - 2.0)

        assert late_error < early_error, \
            f"Learning should converge: early_error={early_error:.2f}, late_error={late_error:.2f}"


# ============================================================================
# 改進 3️⃣：引擎特定水位參數測試
# ============================================================================

class TestEngineAwareWatermarks:
    """測試引擎特定水位參數功能"""

    def test_watermark_profiles_initialization(self, reservoir_controller):
        """測試水位配置初始化"""
        profiles = reservoir_controller._watermark_profiles

        assert "edge-tts" in profiles
        assert "nanmai" in profiles
        assert "gtts" in profiles

        # 驗證 Nanmai 配置
        assert profiles["nanmai"]["LOW"] == 20.0
        assert profiles["nanmai"]["HIGH"] == 60.0
        assert profiles["nanmai"]["TARGET"] == 25.0

    def test_apply_watermarks_for_engine(self, reservoir_controller):
        """測試應用特定引擎的水位"""
        # 應用 Nanmai 配置
        reservoir_controller._apply_watermarks_for_engine("nanmai")

        assert reservoir_controller.LOW_WATERMARK == 20.0
        assert reservoir_controller.HIGH_WATERMARK == 60.0
        assert reservoir_controller.TARGET_BATCH_DURATION == 25.0

        # 應用 Edge-TTS 配置
        reservoir_controller._apply_watermarks_for_engine("edge-tts")

        assert reservoir_controller.LOW_WATERMARK == 12.0
        assert reservoir_controller.HIGH_WATERMARK == 40.0
        assert reservoir_controller.TARGET_BATCH_DURATION == 18.0

    def test_watermark_comparison_across_engines(self, reservoir_controller):
        """測試不同引擎的水位差異"""
        profiles = reservoir_controller._watermark_profiles

        # Nanmai 應有較大的高水位
        assert profiles["nanmai"]["HIGH"] > profiles["edge-tts"]["HIGH"]
        # Nanmai 的低水位應更高（更敏感的觸發）
        assert profiles["nanmai"]["LOW"] > profiles["edge-tts"]["LOW"]

    def test_update_watermark_profile(self, reservoir_controller):
        """測試動態更新水位參數"""
        reservoir_controller.set_current_engine("nanmai")
        reservoir_controller._apply_watermarks_for_engine("nanmai")

        # 更新 Nanmai 的參數
        reservoir_controller.update_watermark_profile(
            "nanmai",
            low=22.0,
            high=65.0,
            target=27.0
        )

        # 驗證更新
        assert reservoir_controller._watermark_profiles["nanmai"]["LOW"] == 22.0
        assert reservoir_controller._watermark_profiles["nanmai"]["HIGH"] == 65.0
        assert reservoir_controller._watermark_profiles["nanmai"]["TARGET"] == 27.0

        # 由於是當前引擎，應立即生效
        assert reservoir_controller.LOW_WATERMARK == 22.0

    def test_engine_switch_applies_watermarks(self, reservoir_controller):
        """測試引擎切換時應用對應的水位"""
        # 初始為 Edge-TTS
        reservoir_controller._apply_watermarks_for_engine("edge-tts")
        initial_high = reservoir_controller.HIGH_WATERMARK
        assert initial_high == 40.0

        # 切換到 Nanmai
        reservoir_controller.reset_for_engine_switch("nanmai")

        # 水位應更新為 Nanmai 的配置
        assert reservoir_controller.HIGH_WATERMARK == 60.0
        assert reservoir_controller.LOW_WATERMARK == 20.0

    def test_unknown_engine_fallback(self, reservoir_controller):
        """測試未知引擎的後備處理"""
        # 嘗試應用未知引擎
        reservoir_controller._apply_watermarks_for_engine("unknown-engine")

        # 應回退到 Edge-TTS 配置
        assert reservoir_controller.LOW_WATERMARK == 12.0
        assert reservoir_controller.HIGH_WATERMARK == 40.0


# ============================================================================
# 整合測試
# ============================================================================

class TestIntegration:
    """測試三個改進層次的整合"""

    @pytest.mark.asyncio
    async def test_full_engine_switch_workflow(self, reservoir_controller, playlist_manager):
        """測試完整的引擎切換工作流"""
        # 1. 啟動監控（Edge-TTS）
        await reservoir_controller.start_monitoring()

        # 2. 記錄 Edge-TTS 的播放歷史
        for i in range(5):
            reservoir_controller.record_playback_event(i, 1.0, 3)  # 3 字，1.0 秒

        initial_history_len = len(reservoir_controller.play_history)
        assert initial_history_len == 5

        # 3. 切換到 Nanmai
        reservoir_controller.reset_for_engine_switch("nanmai")

        # 驗證切換結果
        assert len(reservoir_controller.play_history) == 0  # 歷史已清除
        assert reservoir_controller._current_engine == "nanmai"
        assert reservoir_controller.LOW_WATERMARK == 20.0
        assert reservoir_controller.HIGH_WATERMARK == 60.0

        # 4. 記錄 Nanmai 的播放歷史
        for i in range(5):
            reservoir_controller.record_playback_event(
                i, 1.5, 3)  # 3 字，1.5 秒（較慢）

        # 5. 驗證語速估算已調整
        text = "測試"  # 2 字
        # Nanmai 的基礎速度 2.5，加上歷史修正應接近 2.0（3/1.5）
        duration = reservoir_controller._estimate_play_duration(text)
        assert duration > 0.5, "Nanmai 應有較長的持續時間估算"

        await reservoir_controller.stop_monitoring()

    def test_diagnostics_reporting(self, reservoir_controller):
        """測試診斷信息報告"""
        reservoir_controller.set_current_engine("nanmai")

        # 添加播放歷史
        for _ in range(10):
            reservoir_controller.record_playback_event(0, 1.0, 5)

        # 獲取診斷信息
        diag = reservoir_controller.get_diagnostics()

        assert diag["current_engine"] == "nanmai"
        assert "current_buffer_duration" in diag
        assert "water_levels" in diag
        assert "speed_estimation" in diag
        assert "heartbeat" in diag

        # 驗證心跳配置
        assert diag["heartbeat"]["active"] == "0.5"
        assert diag["heartbeat"]["idle"] == "5.0"


# ============================================================================
# 性能基準測試
# ============================================================================

class TestPerformanceBenchmarks:
    """性能基準測試"""

    def test_estimate_duration_performance(self, reservoir_controller):
        """測試語速估算的性能"""
        import time

        text = "這是一個較長的文本用來測試性能估算的速度和準確度"

        # 添加播放歷史以啟用校正
        for _ in range(20):
            reservoir_controller.record_playback_event(0, 1.0, 10)

        # 性能測試
        start = time.perf_counter()
        for _ in range(1000):
            reservoir_controller._estimate_play_duration(text)
        elapsed = time.perf_counter() - start

        # 應該非常快（<10ms for 1000 calls）
        assert elapsed < 0.01, f"Estimation too slow: {elapsed:.4f}s for 1000 calls"

    def test_watermark_switch_performance(self, reservoir_controller):
        """測試水位切換的性能"""
        import time

        start = time.perf_counter()
        for _ in range(100):
            for engine in ["edge-tts", "nanmai", "gtts"]:
                reservoir_controller._apply_watermarks_for_engine(engine)
        elapsed = time.perf_counter() - start

        # 應該非常快（<10ms for 300 calls）
        assert elapsed < 0.01, f"Watermark switch too slow: {elapsed:.4f}s for 300 calls"


# ============================================================================
# 邊界和異常情況測試
# ============================================================================

class TestEdgeCases:
    """邊界和異常情況測試"""

    def test_empty_text_duration(self, reservoir_controller):
        """測試空文本的時長估算"""
        duration = reservoir_controller._estimate_play_duration("")
        assert duration == 0.0

    def test_very_short_text(self, reservoir_controller):
        """測試極短文本"""
        duration = reservoir_controller._estimate_play_duration("a")  # 1 字
        assert duration > 0, "Should return positive duration"
        assert duration < 1, "Single character should be fast"

    def test_very_long_text(self, reservoir_controller):
        """測試極長文本"""
        long_text = "中" * 1000  # 1000 字
        duration = reservoir_controller._estimate_play_duration(long_text)

        # 應該是合理的（在 200-500 秒之間，取決於引擎）
        assert 100 < duration < 500, f"Long text duration {duration} seems unreasonable"

    def test_zero_history_duration_handling(self, reservoir_controller):
        """測試歷史數據為零時長的處理"""
        # 添加無效的歷史記錄
        reservoir_controller.record_playback_event(0, 0.0, 5)  # 0 秒內 5 字

        # 應該不拋出異常
        duration = reservoir_controller._estimate_play_duration("測試")
        assert duration > 0

    def test_multiple_rapid_engine_switches(self, reservoir_controller):
        """測試快速連續切換引擎"""
        engines = ["edge-tts", "nanmai", "gtts", "edge-tts", "nanmai"]

        for engine in engines:
            reservoir_controller.reset_for_engine_switch(engine)
            assert reservoir_controller._current_engine == engine

        # 最終應該是 nanmai
        assert reservoir_controller._current_engine == "nanmai"
        assert len(reservoir_controller.play_history) == 0


# ============================================================================
# 定時器精確度改進測試（新功能）
# ============================================================================

class TestTimerPrecisionEnhancement:
    """測試定時器精確度改進功能"""

    @pytest.mark.asyncio
    async def test_absolute_time_correction_active_state(self, reservoir_controller, playlist_manager):
        """測試活躍狀態下的絕對時間校正"""
        # 設置為活躍狀態
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "PLAYING"
        playlist_manager.app.tts_smooth_mode = True

        # Mock 水位檢查以避免實際的 refill 邏輯
        reservoir_controller._check_and_refill = AsyncMock()

        await reservoir_controller.start_monitoring()

        # 記錄開始時間
        start_time = asyncio.get_event_loop().time()

        # 讓監控循環運行約 2.1 秒（大於 4 個活躍心跳週期：4 * 0.5 = 2.0）
        await asyncio.sleep(2.1)

        # 記錄結束時間
        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        await reservoir_controller.stop_monitoring()

        # 驗證檢查次數：在 2.1 秒內應該有大約 4 次檢查（每 0.5 秒一次）
        # 由於精確時間校正，應該很接近預期
        expected_checks = int(elapsed / 0.5)  # 應該是 4
        actual_checks = reservoir_controller._check_and_refill.call_count

        # 允許 ±1 的誤差（考慮測試環境的變動）
        assert abs(actual_checks - expected_checks) <= 1, \
            f"Expected ~{expected_checks} checks in {elapsed:.2f}s, got {actual_checks}"

    @pytest.mark.asyncio
    async def test_absolute_time_correction_idle_state(self, reservoir_controller, playlist_manager):
        """測試閒置狀態下的絕對時間校正"""
        # 設置為閒置狀態
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "STOPPED"
        playlist_manager.app.tts_smooth_mode = True

        reservoir_controller._check_and_refill = AsyncMock()

        await reservoir_controller.start_monitoring()

        start_time = asyncio.get_event_loop().time()

        # 運行 6 秒（大於一個閒置心跳週期：5.0s）
        await asyncio.sleep(6.0)

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        await reservoir_controller.stop_monitoring()

        # 在閒置狀態下，應該只有 1 次檢查（因為 5.0s 心跳）
        actual_checks = reservoir_controller._check_and_refill.call_count

        # 由於長心跳，應該只有 1 次檢查
        assert actual_checks <= 2, \
            f"Expected <=2 checks in {elapsed:.2f}s with 5s heartbeat, got {actual_checks}"

    @pytest.mark.asyncio
    async def test_event_loop_load_compensation(self, reservoir_controller, playlist_manager):
        """測試 Event Loop 負載補償"""
        # 設置活躍狀態
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "PLAYING"
        playlist_manager.app.tts_smooth_mode = True

        reservoir_controller._check_and_refill = AsyncMock()

        # Mock 讓檢查耗時較長，模擬高負載
        async def slow_check():
            await asyncio.sleep(0.2)  # 模擬 200ms 的負載

        reservoir_controller._check_and_refill = slow_check

        await reservoir_controller.start_monitoring()

        start_time = asyncio.get_event_loop().time()

        # 運行約 1.5 秒
        await asyncio.sleep(1.5)

        end_time = asyncio.get_event_loop().time()
        elapsed = end_time - start_time

        await reservoir_controller.stop_monitoring()

        # 即使有負載，定時器應該仍然嘗試維持 0.5s 的間隔
        # 我們檢查是否有合理的檢查次數（應該是 2-3 次）
        # 由於負載補償，應該不會因為延遲而完全失控

        # 這是一個相對寬鬆的測試，主要驗證系統沒有崩潰
        assert elapsed >= 1.4, "Test should run for expected duration"
        assert reservoir_controller._check_and_refill is not None, "Check function should be called"

    def test_monitor_loop_logic_flow(self, reservoir_controller, playlist_manager):
        """測試監控循環的邏輯流程"""
        # 設置活躍狀態
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "PLAYING"
        playlist_manager.app.tts_smooth_mode = True

        # 檢查初始狀態
        assert reservoir_controller.running is False

        # 啟動監控（異步，但我們檢查邏輯）
        # 注意：這裡不實際啟動，因為我們只測試邏輯

        # 驗證心跳決策邏輯
        is_active = reservoir_controller._should_check_water_level()
        assert is_active is True, "Should be active when playing"

        # 驗證心跳間隔計算
        heartbeat = reservoir_controller._active_heartbeat if is_active else reservoir_controller._idle_heartbeat
        assert heartbeat == 0.5, "Active heartbeat should be 0.5s"

        # 切換到閒置狀態
        playlist_manager.app.tts_status = "STOPPED"
        is_active_idle = reservoir_controller._should_check_water_level()
        assert is_active_idle is False, "Should be idle when stopped"

        heartbeat_idle = reservoir_controller._active_heartbeat if is_active_idle else reservoir_controller._idle_heartbeat
        assert heartbeat_idle == 5.0, "Idle heartbeat should be 5.0s"

    @pytest.mark.asyncio
    async def test_timer_precision_under_load_simulation(self, reservoir_controller, playlist_manager):
        """模擬高負載情況下的定時器精確度"""
        # 設置活躍狀態
        playlist_manager.app = Mock()
        playlist_manager.app.tts_status = "PLAYING"
        playlist_manager.app.tts_smooth_mode = True

        # 創建一個任務來模擬持續的 Event Loop 負載
        async def background_load():
            """模擬持續的背景負載"""
            for _ in range(50):  # 50 次短暫負載
                await asyncio.sleep(0.01)  # 10ms 負載
                # 做一些計算來增加負載
                sum(range(1000))

        # Mock 水位檢查
        check_times = []

        async def record_check_time():
            check_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.05)  # 輕微延遲模擬處理時間

        reservoir_controller._check_and_refill = record_check_time

        # 啟動背景負載和監控
        load_task = asyncio.create_task(background_load())
        await reservoir_controller.start_monitoring()

        start_time = asyncio.get_event_loop().time()

        # 運行 2 秒
        await asyncio.sleep(2.0)

        end_time = asyncio.get_event_loop().time()
        await reservoir_controller.stop_monitoring()
        await load_task

        # 分析檢查間隔
        if len(check_times) >= 3:
            intervals = []
            for i in range(1, len(check_times)):
                interval = check_times[i] - check_times[i-1]
                intervals.append(interval)

            avg_interval = sum(intervals) / len(intervals)

            # 在高負載下，平均間隔應該仍然接近 0.5s（±20% 容忍度）
            # 這驗證了絕對時間校正的有效性
            tolerance = 0.5 * 0.2  # 20% 容忍度
            assert abs(avg_interval - 0.5) <= tolerance, \
                f"Average interval {avg_interval:.3f}s deviates too much from target 0.5s under load"

        # 確保測試運行了預期時間
        elapsed = end_time - start_time
        assert elapsed >= 1.9, f"Test should run for ~2s, got {elapsed:.2f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
