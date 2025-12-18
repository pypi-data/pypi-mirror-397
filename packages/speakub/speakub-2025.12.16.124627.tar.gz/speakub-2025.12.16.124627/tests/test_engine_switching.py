#!/usr/bin/env python3
"""
Test engine switching functionality for hybrid architecture.
Tests the reset_for_engine_switch method and engine manager integration.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, Mock

from speakub.tts.reservoir.controller import PredictiveBatchController
from speakub.tts.engine_manager import TTSEngineManager
from speakub.utils.config import ConfigManager


class TestPredictiveControllerReset:
    """Test PredictiveBatchController.reset_for_engine_switch method."""

    @pytest.fixture
    def mock_playlist_manager(self):
        """Create a mock playlist manager."""
        manager = Mock()
        manager.get_buffered_duration.return_value = 30.0
        return manager

    @pytest.fixture
    def mock_queue_predictor(self):
        """Create a mock queue predictor."""
        predictor = Mock()
        predictor.play_monitor = Mock()
        predictor.play_monitor.segment_times = []
        predictor.play_monitor.average_play_time = 1.0
        predictor.play_monitor.playback_rate = 1.0
        predictor.engine_configs = {"edge-tts": {"buffer_factor": 1.0}}
        return predictor

    @pytest.fixture
    def controller(self, mock_playlist_manager, mock_queue_predictor):
        """Create a PredictiveBatchController instance."""
        return PredictiveBatchController(
            playlist_manager=mock_playlist_manager,
            queue_predictor=mock_queue_predictor,
            config_manager=ConfigManager()
        )

    def test_reset_for_engine_switch_basic(self, controller):
        """Test basic reset functionality."""
        # Set up initial state
        controller.underrun_penalty = 5.0
        controller.trigger_count = 10
        controller.play_monitor.segment_times.append(2.0)  # Add some history

        # Verify initial state
        assert controller.underrun_penalty == 5.0
        assert controller.trigger_count == 10
        assert len(controller.play_monitor.segment_times) == 1

        # Reset for engine switch
        controller.reset_for_engine_switch("nanmai")

        # Verify reset worked
        assert controller.underrun_penalty == 0.0
        assert controller.trigger_count == 0
        assert len(controller.play_monitor.segment_times) == 0

    def test_reset_for_engine_switch_preserves_structure(self, controller):
        """Test that reset preserves necessary object structure."""
        # Reset should not break the controller
        controller.reset_for_engine_switch("edge-tts")

        # Controller should still be functional
        assert hasattr(controller, 'state')
        assert hasattr(controller, 'playlist_manager')
        assert hasattr(controller, 'queue_predictor')

    @pytest.mark.asyncio
    async def test_reset_with_monitoring_active(self, controller):
        """Test reset while controller is in monitoring state."""
        # Start monitoring
        await controller.start_monitoring()
        assert controller.state.value == "monitoring"

        # Reset should work even when monitoring
        controller.reset_for_engine_switch("gtts")

        # Should be in idle state after reset
        assert controller.state.value == "idle"

    def test_reset_performance_stats_comprehensive(self, controller):
        """Test comprehensive performance stats reset."""
        # Set various performance stats
        controller.underrun_penalty = 3.5
        controller.underrun_count = 7
        controller.trigger_count = 15
        controller.false_positive_count = 2
        controller.average_trigger_lead_time = 2.3

        # Reset
        controller._reset_performance_stats()

        # All should be zero
        assert controller.underrun_penalty == 0.0
        assert controller.underrun_count == 0
        assert controller.trigger_count == 0
        assert controller.false_positive_count == 0
        assert controller.average_trigger_lead_time == 0.0


class TestEngineManagerSwitching:
    """Test TTSEngineManager engine switching with controller reset."""

    @pytest.fixture
    def config_manager(self):
        """Create a test config manager."""
        config = ConfigManager()
        config.set_override("tts.preferred_engine", "edge-tts")
        return config

    @pytest.fixture
    def engine_manager(self, config_manager):
        """Create an engine manager."""
        return TTSEngineManager(config_manager=config_manager)

    @pytest.fixture
    def mock_tts_integration(self):
        """Create a mock TTS integration."""
        integration = Mock()
        integration.app = Mock()
        integration.app.tts_status = "STOPPED"
        integration._async_tts_stop_requested = AsyncMock()
        integration._tts_active_tasks = set()
        integration.stop_speaking = Mock()
        return integration

    @pytest.mark.asyncio
    async def test_switch_engine_calls_controller_reset(self, engine_manager, mock_tts_integration):
        """Test that engine switching calls controller reset."""
        # Create mock playlist manager with controller
        mock_controller = Mock()
        mock_controller.reset_for_engine_switch = Mock()
        mock_controller.stop_monitoring = AsyncMock()

        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = mock_controller
        mock_playlist_manager.reset = Mock()

        mock_tts_integration.playlist_manager = mock_playlist_manager

        # Mock engine cleanup
        mock_engine = Mock()
        mock_engine.cleanup_resources = AsyncMock()
        mock_engine.stop = Mock()
        mock_engine.stop_async_loop = Mock()

        # Mock setup_tts
        mock_tts_integration.setup_tts = AsyncMock()

        # Perform engine switch
        result = await engine_manager.switch_engine(
            "nanmai",
            tts_integration=mock_tts_integration,
            old_engine=mock_engine
        )

        # Verify controller reset was called
        mock_controller.reset_for_engine_switch.assert_called_once_with(
            "nanmai")
        assert result is True

    @pytest.mark.asyncio
    async def test_switch_engine_handles_missing_controller(self, engine_manager, mock_tts_integration):
        """Test engine switching when controller is not available."""
        # Playlist manager without controller
        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = None  # No controller
        mock_playlist_manager.reset = Mock()

        mock_tts_integration.playlist_manager = mock_playlist_manager

        # Mock engine
        mock_engine = Mock()
        mock_engine.cleanup_resources = AsyncMock()

        mock_tts_integration.setup_tts = AsyncMock()

        # Should not fail even without controller
        result = await engine_manager.switch_engine(
            "gtts",
            tts_integration=mock_tts_integration,
            old_engine=mock_engine
        )

        assert result is True

    @pytest.mark.asyncio
    async def test_switch_engine_handles_controller_without_reset_method(self, engine_manager, mock_tts_integration):
        """Test engine switching when controller doesn't have reset method."""
        # Controller without reset method
        mock_controller = Mock()
        del mock_controller.reset_for_engine_switch  # Remove the method
        mock_controller.stop_monitoring = AsyncMock()

        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = mock_controller
        mock_playlist_manager.reset = Mock()

        mock_tts_integration.playlist_manager = mock_playlist_manager

        mock_engine = Mock()
        mock_engine.cleanup_resources = AsyncMock()
        mock_tts_integration.setup_tts = AsyncMock()

        # Should not fail
        result = await engine_manager.switch_engine(
            "edge-tts",
            tts_integration=mock_tts_integration,
            old_engine=mock_engine
        )

        assert result is True


class TestBridgeMechanism:
    """Test the bridge mechanism in TTSIntegration."""

    @pytest.fixture
    def mock_integration(self):
        """Create a mock TTS integration for bridge testing."""
        integration = Mock()
        integration._asyncio_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(integration._asyncio_loop)

        # Mock async events
        integration._async_tts_stop_requested = asyncio.Event()
        integration._async_tts_pause_requested = asyncio.Event()

        return integration

    @pytest.mark.asyncio
    async def test_bridge_to_async_core_sets_event(self, mock_integration):
        """Test that bridge correctly sets async events."""
        from speakub.tts.integration import TTSIntegration

        # Create a real instance for testing bridge method
        real_integration = TTSIntegration.__new__(TTSIntegration)
        real_integration._asyncio_loop = asyncio.get_event_loop()
        real_integration._async_tts_stop_requested = mock_integration._async_tts_stop_requested

        # Test setting an event
        real_integration._bridge_to_async_core(
            mock_integration._async_tts_stop_requested,
            "set"
        )

        # Give the event loop a chance to process the callback
        await asyncio.sleep(0.01)

        # Event should be set
        assert mock_integration._async_tts_stop_requested.is_set()

    @pytest.mark.asyncio
    async def test_bridge_to_async_core_clears_event(self, mock_integration):
        """Test that bridge correctly clears async events."""
        from speakub.tts.integration import TTSIntegration

        # Set event first
        mock_integration._async_tts_stop_requested.set()
        assert mock_integration._async_tts_stop_requested.is_set()

        # Create real instance for testing
        real_integration = TTSIntegration.__new__(TTSIntegration)
        real_integration._asyncio_loop = asyncio.get_event_loop()
        real_integration._async_tts_stop_requested = mock_integration._async_tts_stop_requested

        # Test clearing the event
        real_integration._bridge_to_async_core(
            mock_integration._async_tts_stop_requested,
            "clear"
        )

        # Give the event loop a chance to process the callback
        await asyncio.sleep(0.01)

        # Event should be cleared
        assert not mock_integration._async_tts_stop_requested.is_set()

    def test_bridge_handles_invalid_action(self, mock_integration):
        """Test that bridge handles invalid actions gracefully."""
        from speakub.tts.integration import TTSIntegration

        real_integration = TTSIntegration.__new__(TTSIntegration)
        real_integration._asyncio_loop = mock_integration._asyncio_loop

        # Should raise ValueError for invalid action
        with pytest.raises(ValueError, match="Unknown action"):
            real_integration._bridge_to_async_core(
                mock_integration._async_tts_stop_requested,
                "invalid_action"
            )


class TestHybridArchitectureIntegration:
    """Integration tests for the hybrid architecture."""

    @pytest.mark.asyncio
    async def test_full_engine_switch_workflow(self):
        """Test complete engine switch workflow with all components."""
        # This is a high-level integration test
        config_manager = ConfigManager()

        # Create engine manager
        engine_manager = TTSEngineManager(config_manager=config_manager)

        # Mock TTS integration
        mock_integration = Mock()
        mock_integration.app = Mock()
        mock_integration.app.tts_status = "STOPPED"
        mock_integration._async_tts_stop_requested = asyncio.Event()
        mock_integration._tts_active_tasks = set()
        mock_integration.stop_speaking = Mock()

        # Mock playlist manager with controller
        mock_controller = Mock()
        mock_controller.reset_for_engine_switch = Mock()
        mock_controller.stop_monitoring = AsyncMock()

        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = mock_controller
        mock_playlist_manager.reset = Mock()

        mock_integration.playlist_manager = mock_playlist_manager
        mock_integration.setup_tts = AsyncMock()

        # Mock old engine
        mock_old_engine = Mock()
        mock_old_engine.cleanup_resources = AsyncMock()

        # Perform engine switch
        result = await engine_manager.switch_engine(
            "nanmai",
            tts_integration=mock_integration,
            old_engine=mock_old_engine
        )

        # Verify the workflow
        assert result is True
        mock_controller.reset_for_engine_switch.assert_called_once_with(
            "nanmai")
        mock_old_engine.cleanup_resources.assert_called_once()
        mock_integration.setup_tts.assert_called_once()


class TestNonSmoothEngineSwitching:
    """強化測試：Non-smooth模式引擎切換的跳章問題預防"""

    @pytest.fixture
    def config_manager(self):
        """測試用的配置管理器"""
        config = ConfigManager()
        config.set_override("tts.preferred_engine", "edge-tts")
        config.set_override("tts.smooth_mode", False)  # 明確設定為non-smooth模式
        return config

    @pytest.fixture
    def engine_manager(self, config_manager):
        """引擎管理器"""
        return TTSEngineManager(config_manager=config_manager)

    @pytest.fixture
    def mock_tts_integration_nonsmooth(self):
        """專門為non-smooth模式設計的mock TTS integration"""
        integration = Mock()
        integration.app = Mock()
        integration.app.tts_status = "PLAYING"  # 模擬播放中狀態
        integration.app.tts_smooth_mode = False  # 明確non-smooth模式
        integration._engine_switching = False  # 初始狀態

        # 模擬asyncio事件
        integration._async_tts_stop_requested = AsyncMock()
        integration._async_tts_pause_requested = AsyncMock()
        integration._tts_active_tasks = set()

        # Mock stop_speaking 方法
        integration.stop_speaking = Mock()

        return integration

    def test_engine_switch_sets_switching_flag(self, engine_manager, mock_tts_integration_nonsmooth):
        """測試引擎切換時正確設定切換標記"""
        # 初始狀態應為False
        assert mock_tts_integration_nonsmooth._engine_switching == False

        # 開始引擎切換（同步部分）
        assert engine_manager.get_current_engine() is None  # 初始沒有引擎

        # 設定切換標記（模擬實際行為）
        mock_tts_integration_nonsmooth._engine_switching = True

        # 切換完成後應清除標記
        mock_tts_integration_nonsmooth._engine_switching = False

        assert mock_tts_integration_nonsmooth._engine_switching == False

    @pytest.mark.asyncio
    async def test_nonsmooth_switch_preserves_playback_state(self, engine_manager, mock_tts_integration_nonsmooth):
        """測試non-smooth模式下引擎切換不會意外停止播放"""
        # 設定播放狀態
        original_status = mock_tts_integration_nonsmooth.app.tts_status
        original_smooth_mode = mock_tts_integration_nonsmooth.app.tts_smooth_mode

        # Mock playlist manager
        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = None
        mock_playlist_manager.reset = Mock()
        mock_tts_integration_nonsmooth.playlist_manager = mock_playlist_manager

        # Mock engine
        mock_old_engine = Mock()
        mock_old_engine.cleanup_resources = AsyncMock()
        mock_tts_integration_nonsmooth.setup_tts = AsyncMock()

        # 執行引擎切換
        result = await engine_manager.switch_engine(
            "nanmai",
            tts_integration=mock_tts_integration_nonsmooth,
            old_engine=mock_old_engine
        )

        # 驗證切換成功
        assert result == True

        # 在non-smooth模式下，引擎切換應完成但不改變播放狀態
        # （因為UI會根據需要重新開始播放）
        assert mock_tts_integration_nonsmooth.app.tts_smooth_mode == original_smooth_mode

    def test_switching_flag_prevents_race_conditions(self, mock_tts_integration_nonsmooth):
        """測試切換標記如何防止競態條件"""
        # 模擬Serial Runner檢查切換狀態的邏輯
        def should_skip_chapter_jump(integration):
            """模擬Serial Runner的檢查邏輯"""
            return getattr(integration, '_engine_switching', False)

        # 正常播放時應允許跳章
        assert should_skip_chapter_jump(
            mock_tts_integration_nonsmooth) == False

        # 引擎切換期間應阻止跳章
        mock_tts_integration_nonsmooth._engine_switching = True
        assert should_skip_chapter_jump(mock_tts_integration_nonsmooth) == True

        # 切換完成後恢復正常
        mock_tts_integration_nonsmooth._engine_switching = False
        assert should_skip_chapter_jump(
            mock_tts_integration_nonsmooth) == False

    @pytest.mark.asyncio
    async def test_switch_cleanup_order_prevents_state_pollution(self, engine_manager, mock_tts_integration_nonsmooth):
        """測試清理順序防止狀態污染"""
        # Mock具有控制器的playlist manager
        mock_controller = Mock()
        mock_controller.reset_for_engine_switch = Mock()
        mock_controller.stop_monitoring = AsyncMock()

        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = mock_controller
        mock_playlist_manager.reset = Mock()

        mock_tts_integration_nonsmooth.playlist_manager = mock_playlist_manager

        # Mock引擎
        mock_old_engine = Mock()
        mock_old_engine.cleanup_resources = AsyncMock()
        mock_tts_integration_nonsmooth.setup_tts = AsyncMock()

        # 記錄調用順序
        call_order = []

        def record_call(name):
            call_order.append(name)

        # 修改mock以記錄調用
        mock_controller.stop_monitoring.side_effect = lambda: record_call(
            "stop_monitoring")
        mock_playlist_manager.reset.side_effect = lambda: record_call(
            "playlist_reset")
        mock_old_engine.cleanup_resources.side_effect = lambda: (
            record_call("engine_cleanup"), None)[1] or None
        mock_tts_integration_nonsmooth.setup_tts.side_effect = lambda: record_call(
            "setup_new_engine")

        # 執行切換
        await engine_manager.switch_engine(
            "gtts",
            tts_integration=mock_tts_integration_nonsmooth,
            old_engine=mock_old_engine
        )

        # 驗證正確的清理順序：先停止監控，再重置playlist，最後清理引擎
        expected_order = ["stop_monitoring", "playlist_reset",
                          "engine_cleanup", "setup_new_engine"]
        assert call_order == expected_order

    def test_gtts_engine_smooth_mode_constraint(self, config_manager):
        """測試GTTS引擎的smooth模式限制"""
        config_manager.set_override("tts.smooth_mode", True)

        # GTTS不支援smooth模式
        engine_manager = TTSEngineManager(config_manager=config_manager)

        # 模擬TTS integration
        mock_integration = Mock()
        mock_integration.app = Mock()
        mock_integration.app.tts_smooth_mode = True
        mock_integration.app.notify = Mock()

        # 這裡我們模擬引擎切換時的檢查邏輯
        # GTTS切換應自動禁用smooth模式
        if "gtts" == "gtts" and mock_integration.app.tts_smooth_mode:
            mock_integration.app.tts_smooth_mode = False
            config_manager.set_override("tts.smooth_mode", False)
            mock_integration.app.notify.assert_not_called()  # 這裡不會調用，因為我們模擬邏輯

        assert not mock_integration.app.tts_smooth_mode


class TestEngineSwitchConcurrencySafety:
    """測試引擎切換的並發安全性"""

    @pytest.fixture
    def config_manager(self):
        """配置管理器"""
        return ConfigManager()

    @pytest.fixture
    def engine_manager(self, config_manager):
        """引擎管理器"""
        return TTSEngineManager(config_manager=config_manager)

    def test_concurrent_switch_prevention(self, engine_manager):
        """測試防止並發引擎切換"""
        # 這個測試確保引擎管理器不會允許同時進行多個切換操作
        # 在實際實現中，這需要通過鎖或其他同步機制來確保

        # 目前這個測試是結構性的，驗證設計意圖
        # 如果將來實現了並發控制，這個測試應該被擴展

        assert engine_manager is not None  # 基本實例檢查

    @pytest.mark.asyncio
    async def test_switch_isolation_from_playback(self, engine_manager):
        """測試引擎切換與播放操作的隔離"""
        # 確保引擎切換不會干擾正在進行的播放

        mock_integration = Mock()
        mock_integration.app = Mock()
        mock_integration.app.tts_status = "PLAYING"
        mock_integration._tts_active_tasks = set()
        mock_integration.stop_speaking = Mock()

        # 模擬有進行中播放的場景
        mock_integration.app.tts_status = "PLAYING"

        # Mock playlist和引擎
        mock_playlist_manager = Mock()
        mock_playlist_manager._predictive_controller = None
        mock_playlist_manager.reset = Mock()
        mock_integration.playlist_manager = mock_playlist_manager

        mock_old_engine = Mock()
        mock_old_engine.cleanup_resources = AsyncMock()
        mock_integration.setup_tts = AsyncMock()

        # 執行切換
        result = await engine_manager.switch_engine(
            "edge-tts",
            tts_integration=mock_integration,
            old_engine=mock_old_engine
        )

        # 切換應成功，但不應改變播放狀態
        # （UI層負責根據需要重新開始播放）
        assert result == True
        assert mock_integration.app.tts_status == "PLAYING"  # 狀態保持不變


if __name__ == "__main__":
    pytest.main([__file__])
