#!/usr/bin/env python3
"""
測試 Reservoir Controller 在 non-smooth mode 下的優化行為

驗證修改後，controller 在 non-smooth mode 下完全不執行水位檢查邏輯。
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock

from speakub.tts.fusion_reservoir.controller import SimpleReservoirController
from speakub.utils.config import ConfigManager


@pytest.fixture
def mock_playlist_manager():
    """創建模擬的 PlaylistManager"""
    pm = Mock()
    pm.app = Mock()
    pm.app.tts_smooth_mode = True  # 預設 smooth mode
    pm.app.tts_status = "STOPPED"
    pm.get_current_index.return_value = 0
    pm.get_playlist_length.return_value = 10
    pm.get_item_at.return_value = ("測試文本", 1, b"audio_data")
    pm._process_batch = AsyncMock()
    return pm


@pytest.fixture
def mock_config():
    """創建模擬的配置管理器"""
    config = Mock(spec=ConfigManager)
    config.get.side_effect = lambda key, default=None: {
        "tts.reservoir.active_heartbeat": 0.5,
        "tts.reservoir.idle_heartbeat": 5.0,
        "tts.reservoir.engine_base_speeds": {
            "edge-tts": 3.5,
            "nanmai": 2.5,
            "gtts": 3.0,
        },
        "tts.reservoir.watermark_profiles": {
            "edge-tts": {"LOW": 12.0, "HIGH": 40.0, "TARGET": 18.0},
            "nanmai": {"LOW": 20.0, "HIGH": 60.0, "TARGET": 25.0},
            "gtts": {"LOW": 15.0, "HIGH": 45.0, "TARGET": 20.0},
        }
    }.get(key, default)
    return config


@pytest.fixture
def reservoir_controller(mock_playlist_manager, mock_config):
    """創建測試用的 Reservoir Controller"""
    return SimpleReservoirController(mock_playlist_manager, mock_config)


@pytest.mark.asyncio
async def test_monitor_loop_non_smooth_mode(reservoir_controller, mock_playlist_manager):
    """測試 non-smooth mode 下 monitor loop 的行為"""
    # 設置 non-smooth mode
    mock_playlist_manager.app.tts_smooth_mode = False

    # 模擬檢查方法調用
    original_check = reservoir_controller._should_check_water_level
    check_call_count = 0

    def count_checks():
        nonlocal check_call_count
        check_call_count += 1
        return original_check()

    reservoir_controller._should_check_water_level = count_checks

    # 啟動監控
    await reservoir_controller.start_monitoring()

    # 等待一段時間（足夠進行多次循環）
    await asyncio.sleep(2.1)

    # 停止監控
    await reservoir_controller.stop_monitoring()

    # 驗證：在 non-smooth mode 下沒有執行任何水位檢查
    assert check_call_count == 0, f"Expected 0 checks in non-smooth mode, got {check_call_count}"


@pytest.mark.asyncio
async def test_monitor_loop_smooth_mode_active(reservoir_controller, mock_playlist_manager):
    """測試 smooth mode 下活躍狀態的行為"""
    # 設置 smooth mode 和活躍狀態
    mock_playlist_manager.app.tts_smooth_mode = True
    mock_playlist_manager.app.tts_status = "PLAYING"

    # 模擬檢查和補水方法
    check_call_count = 0
    refill_call_count = 0

    original_check = reservoir_controller._should_check_water_level
    original_refill = reservoir_controller._check_and_refill

    def count_checks():
        nonlocal check_call_count
        check_call_count += 1
        return True  # 總是返回活躍

    async def count_refills():
        nonlocal refill_call_count
        refill_call_count += 1

    reservoir_controller._should_check_water_level = count_checks
    reservoir_controller._check_and_refill = count_refills

    # 啟動監控
    await reservoir_controller.start_monitoring()

    # 等待一段時間
    await asyncio.sleep(1.1)  # 應該進行多次活躍檢查

    # 停止監控
    await reservoir_controller.stop_monitoring()

    # 驗證：在 smooth mode 下正常執行檢查
    assert check_call_count > 0, "Should perform checks in smooth mode"
    assert refill_call_count > 0, "Should perform refills when active"


@pytest.mark.asyncio
async def test_monitor_loop_smooth_mode_idle(reservoir_controller, mock_playlist_manager):
    """測試 smooth mode 下閒置狀態的行為"""
    # 設置 smooth mode 和閒置狀態
    mock_playlist_manager.app.tts_smooth_mode = True
    mock_playlist_manager.app.tts_status = "STOPPED"

    check_call_count = 0

    def count_checks():
        nonlocal check_call_count
        check_call_count += 1
        return False  # 總是返回閒置

    reservoir_controller._should_check_water_level = count_checks

    # 啟動監控
    await reservoir_controller.start_monitoring()

    # 等待一段時間
    await asyncio.sleep(1.1)

    # 停止監控
    await reservoir_controller.stop_monitoring()

    # 驗證：檢查被調用但返回閒置
    assert check_call_count > 0, "Should still perform checks in smooth mode"


def test_should_check_water_level_no_app(reservoir_controller):
    """測試沒有 app 時的行為"""
    # 移除 app
    reservoir_controller.pm.app = None

    result = reservoir_controller._should_check_water_level()
    assert result is False


def test_should_check_water_level_triggering(reservoir_controller, mock_playlist_manager):
    """測試正在觸發時的行為"""
    mock_playlist_manager.app.tts_status = "PLAYING"
    reservoir_controller._is_triggering = True

    result = reservoir_controller._should_check_water_level()
    assert result is False


def test_mode_switch_behavior(reservoir_controller, mock_playlist_manager):
    """測試模式切換的行為"""
    # 初始 smooth mode
    mock_playlist_manager.app.tts_smooth_mode = True
    mock_playlist_manager.app.tts_status = "PLAYING"

    # 檢查應該正常工作
    result = reservoir_controller._should_check_water_level()
    assert result is True

    # 切換到 non-smooth mode
    mock_playlist_manager.app.tts_smooth_mode = False

    # _should_check_water_level 仍然會被調用，但 monitor_loop 會跳過
    # 這裡只是測試 _should_check_water_level 本身的邏輯
    result = reservoir_controller._should_check_water_level()
    assert result is True  # 方法本身不檢查 smooth mode


if __name__ == "__main__":
    # 簡單的手動測試
    print("Running manual tests for Reservoir non-smooth optimization...")

    async def run_manual_test():
        # 創建模擬對象
        pm = Mock()
        pm.app = Mock()
        pm.app.tts_smooth_mode = False  # 測試 non-smooth
        pm.app.tts_status = "STOPPED"
        pm.get_current_index.return_value = 0
        pm.get_playlist_length.return_value = 0
        pm._process_batch = AsyncMock()

        config = Mock()
        config.get.side_effect = lambda key, default=None: default

        controller = SimpleReservoirController(pm, config)

        # 測試 monitor loop
        await controller.start_monitoring()
        await asyncio.sleep(1.0)  # 短時間測試
        await controller.stop_monitoring()

        print("✅ Manual test completed - no exceptions in non-smooth mode")

    asyncio.run(run_manual_test())
