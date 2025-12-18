#!/usr/bin/env python3
"""
TTS integration for SpeakUB
"""

from speakub.ui.protocols import AppInterface
from speakub.utils.text_utils import correct_chinese_pronunciation, is_speakable_content

# --- 新增開始 ---
try:
    from edge_tts.exceptions import NoAudioReceived
except ImportError:
    # 如果 edge-tts 未安裝，定義一個虛設的異常類別以避免 NameError
    class NoAudioReceived(Exception):
        pass


import asyncio
import functools
import logging
import threading
import time
from enum import Enum
from typing import Any, Dict, Optional

from speakub.core.exceptions import (
    AudioSynthesisError,
    NetworkAPIError,
    NetworkConnectionError,
    NetworkError,
    NetworkTimeoutError,
    TTSError,
    TTSPlaybackError,
    TTSProviderError,
    TTSSynthesisError,
    TTSVoiceError,
)
from speakub.tts.circuit_breaker import CircuitBreaker, CircuitBreakerOpenException, CircuitBreakerState
from speakub.tts.engine_factory import TTSEngineFactory
from speakub.tts.engine_params_manager import EngineParamsManager
from speakub.tts.error_category_helper import ErrorCategoryHelper
from speakub.tts.playback_coordinator import PlaybackCoordinator
from speakub.tts.playback_manager import PlaybackManager
from speakub.tts.playlist_manager import PlaylistManager
from speakub.tts.shutdown_coordinator import ShutdownCoordinator, CleanupMode
from speakub.tts.tts_state_machine import TTSStateMachine, TTSState
from speakub.tts.ui.network import NetworkManager

# --- 新增結束 ---
from speakub.tts.ui.runners import find_and_play_next_chapter_worker
from speakub.utils.event_bus import SpeakUBEvents, event_bus
from speakub.utils.system_utils import play_warning_sound
from speakub.utils.deadlock_detector import get_deadlock_detector, LockType

logger = logging.getLogger(__name__)


def blocking_operation(func):
    """
    Decorator to mark functions that perform blocking operations.
    These should be executed in thread pools when called from async contexts.
    """
    func._is_blocking = True
    return func


# TTS availability check
try:
    import edge_tts  # noqa: F401

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

# gTTS availability check
try:
    from gtts import gTTS  # noqa: F401

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Nanmai TTS availability check
try:
    import requests  # noqa: F401

    # 移除 pydub 依賴檢查，因為它現在是可選的
    # from pydub import AudioSegment  # noqa: F401

    NANMAI_AVAILABLE = True
except ImportError:
    NANMAI_AVAILABLE = False


if TTS_AVAILABLE:
    try:
        from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
    except Exception:
        EdgeTTSProvider = None

if GTTS_AVAILABLE:
    try:
        from speakub.tts.engines.gtts_provider import GTTSProvider
    except Exception:
        GTTSProvider = None

if NANMAI_AVAILABLE:
    try:
        from speakub.tts.engines.nanmai_tts_provider import NanmaiTTSProvider
    except Exception:
        NanmaiTTSProvider = None


class AsyncBridge:
    """
    中央橋接器 - 統一處理同步與異步間的通訊。

    目的：減少 run_coroutine_threadsafe 的使用，統一橋接邏輯。

    功能：
    - 事件橋接：從同步上下文操作異步事件
    - 任務委派：將同步操作委派給異步任務
    - 協程執行：安全地執行異步協程並返回結果
    - 狀態同步：確保事件狀態的一致性

    使用模式：
    - 事件操作：bridge.event_set(event)
    - 任務委派：await bridge.run_async(coro)
    - 協程執行：result = bridge.run_coroutine(coro, timeout=1.0)
    - 狀態檢查：bridge.is_event_loop_available()
    """

    def __init__(self, tts_integration: "TTSIntegration"):
        self.tts_integration = tts_integration
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._bridge_operations = 0
        self._successful_operations = 0
        self._coroutine_operations = 0
        self._successful_coroutines = 0

    def get_event_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """獲取或更新事件循環引用"""
        if self._event_loop is None or self._event_loop.is_closed():
            try:
                self._event_loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, try to get event loop from integration
                self._event_loop = self.tts_integration._get_event_loop()
        return self._event_loop

    def is_event_loop_available(self) -> bool:
        """檢查事件循環是否可用"""
        loop = self.get_event_loop()
        return loop is not None and not loop.is_closed()

    def event_set(self, event: asyncio.Event) -> bool:
        """橋接到異步事件 set 操作"""
        return self._bridge_event_operation(event, "set")

    def event_clear(self, event: asyncio.Event) -> bool:
        """橋接到異步事件 clear 操作"""
        return self._bridge_event_operation(event, "clear")

    def _bridge_event_operation(self, event: asyncio.Event, action: str) -> bool:
        """通用事件橋接操作"""
        if not self.is_event_loop_available():
            logger.warning(f"Event loop not available for bridging {action}")
            return False

        async def _do_action():
            if action == "set":
                event.set()
            elif action == "clear":
                event.clear()

        try:
            self._bridge_operations += 1
            future = asyncio.run_coroutine_threadsafe(
                _do_action(), self._event_loop)
            result = future.result(timeout=1.0)  # 1 second timeout
            self._successful_operations += 1
            logger.debug(f"Bridged {action} to async event: {event}")
            return True
        except asyncio.TimeoutError:
            logger.error(
                f"Timeout bridging {action} to async event after 1 second")
            return False
        except Exception as e:
            logger.error(f"Error bridging {action} to async event: {e}")
            return False

    async def run_async(self, coro) -> Any:
        """在異步上下文中運行協程"""
        try:
            return await coro
        except Exception as e:
            logger.error(f"Error running async operation: {e}")
            raise

    def delegate_to_async_task(self, coro, task_name: str = "async_task") -> bool:
        """將協程委派給異步任務執行"""
        if not self.is_event_loop_available():
            logger.warning("Event loop not available for task delegation")
            return False

        try:
            task = asyncio.run_coroutine_threadsafe(coro, self._event_loop)
            # 將任務添加到活躍任務集合中
            if hasattr(self.tts_integration, "_tts_active_tasks"):
                # 創建一個包裝任務來跟踪
                async def _track_task():
                    try:
                        await task
                    except Exception as e:
                        logger.warning(f"Async task {task_name} failed: {e}")

                tracked_task = self._event_loop.create_task(_track_task())
                self.tts_integration._tts_active_tasks.add(tracked_task)

            logger.debug(f"Delegated operation to async task: {task_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delegate async task {task_name}: {e}")
            return False

    def run_coroutine(self, coro, timeout: float = 1.0) -> Any:
        """執行異步協程並返回結果（同步橋接）"""
        if not self.is_event_loop_available():
            logger.warning(
                f"[BRIDGE] Event loop not available for coroutine execution "
                f"(operations: {self._coroutine_operations})")
            raise RuntimeError(
                "Event loop not available for coroutine execution")

        start_time = time.time()
        self._coroutine_operations += 1

        try:
            # CPU Optimization: Check if we're already in the event loop
            try:
                current_loop = asyncio.get_running_loop()
                if current_loop == self._event_loop:
                    # Already in the event loop, execute directly
                    logger.debug(
                        f"[BRIDGE] Already in event loop, executing coroutine directly "
                        f"(op #{self._coroutine_operations})")
                    task = asyncio.create_task(coro)
                    result = asyncio.wait_for(task, timeout=timeout)
                    duration = time.time() - start_time
                    self._successful_coroutines += 1
                    logger.debug(
                        f"[BRIDGE] Direct execution completed in {duration:.3f}s "
                        f"(success rate: {self._successful_coroutines}/{self._coroutine_operations})")
                    return result
            except RuntimeError:
                # Not in an event loop, use threadsafe method
                pass

            # Use threadsafe method as fallback
            logger.debug(
                f"[BRIDGE] Using threadsafe execution (op #{self._coroutine_operations})")
            future = asyncio.run_coroutine_threadsafe(coro, self._event_loop)
            result = future.result(timeout=timeout)
            duration = time.time() - start_time
            self._successful_coroutines += 1
            logger.debug(
                f"[BRIDGE] Threadsafe execution completed in {duration:.3f}s "
                f"with timeout {timeout}s "
                f"(success rate: {self._successful_coroutines}/{self._coroutine_operations})")
            return result
        except asyncio.TimeoutError:
            duration = time.time() - start_time
            logger.warning(
                f"[BRIDGE] Coroutine execution timeout after {duration:.3f}s "
                f"(configured timeout: {timeout}s, op #{self._coroutine_operations})")
            raise
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                f"[BRIDGE] Error executing coroutine after {duration:.3f}s: {e} "
                f"(op #{self._coroutine_operations})")
            raise

    def run_async_task(
        self, coro, timeout: float = 5.0, task_name: str = "async_task"
    ) -> bool:
        """執行異步任務但不等待結果（非阻塞）"""
        if not self.is_event_loop_available():
            logger.warning(
                f"Event loop not available for async task: {task_name}")
            return False

        try:
            # 創建任務但不等待
            task = self._event_loop.create_task(coro, name=task_name)
            # 如果有任務追蹤，添加到集合中
            if hasattr(self.tts_integration, "_tts_active_tasks"):
                self.tts_integration._tts_active_tasks.add(task)
            logger.debug(f"Started async task: {task_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to start async task {task_name}: {e}")
            return False

    def get_bridge_stats(self) -> dict:
        """獲取橋接統計信息"""
        success_rate = (
            (self._successful_operations / self._bridge_operations * 100)
            if self._bridge_operations > 0
            else 0
        )
        coroutine_success_rate = (
            (self._successful_coroutines / self._coroutine_operations * 100)
            if self._coroutine_operations > 0
            else 0
        )

        return {
            "event_operations": {
                "total": self._bridge_operations,
                "successful": self._successful_operations,
                "success_rate": f"{success_rate:.1f}%",
            },
            "coroutine_operations": {
                "total": self._coroutine_operations,
                "successful": self._successful_coroutines,
                "success_rate": f"{coroutine_success_rate:.1f}%",
            },
            "event_loop_available": self.is_event_loop_available(),
        }


class TTSIntegration:
    """
    TTS 整合層 - 混合異步架構。

    這個類實現了混合異步架構，結合了：
    - Asyncio Event Loop（UI 層）
    - Thread Pool（TTS 工作層）
    - Event Bridge（協調層）

    設計決策:
        為什麼使用混合架構？
        1. 底層庫（Pygame, MPV）是同步的
        2. 純 Asyncio 在引擎切換時會導致狀態污染
        3. 同步屏障確保狀態清理的確定性

    關鍵組件:
        - playback_manager: 播放控制
        - playlist_manager: 播放列表和批次管理
        - network_manager: 網絡錯誤處理
        - async_bridge: 中央橋接器，統一 sync-async 通訊
    """

    def __init__(self, app: AppInterface, config_manager: "ConfigManager") -> None:
        self.app = app
        # [🔥 修改] 直接使用傳入的實例，不再自己 new
        self.config_manager = config_manager
        self._asyncio_loop: Optional[asyncio.AbstractEventLoop] = None

        # Runtime check to ensure the app object conforms to the protocol.
        # This will raise an error if EPUBReaderApp does not correctly implement the properties.
        if not isinstance(app, AppInterface):
            raise ValueError(
                "The 'app' object does not conform to AppInterface protocol."
            )

        # ============================================
        # 鎖定層次結構 - 混合架構鎖定管理
        # ============================================
        # 使用 asyncio 狀態管理，減少 threading 依賴
        self._tts_active_tasks: set[asyncio.Task] = set()

        # 鎖定使用文檔表格：
        # | 鎖定名稱 | 類型 | 用途 | 持有者 | 上下文 | 持有時間 | 層次優先權 | 備註 |
        # |----------|------|------|--------|--------|----------|------------|------|
        # | _tts_lock | threading.RLock | 保護 TTS 引擎操作、播放列表管理、錯誤處理邏輯 | PlaybackManager (共享) | 同步/異步 | < 100ms | 高 (同步層) | 播放核心優先權 |
        # | _async_tts_lock | asyncio.Lock | 保護異步 TTS 狀態轉換、任務管理 | TTSIntegration 內部 | 異步 | < 500ms | 中 (異步層) | 與同步鎖無重疊 |
        # | _status_lock | threading.Lock | 保護 TTS 狀態變更和訪問 | UI 層同步調用 | 同步 | < 10ms | 低 (狀態層) | 避免與其他鎖競爭 |
        #
        # 鎖定層次結構說明：
        # - 同步層 (_tts_lock): 最高優先權，確保播放核心線性流程的確定性
        # - 異步層 (_async_tts_lock): 中等優先權，處理狀態轉換和協調
        # - 狀態層 (_status_lock): 最低優先權，快速狀態訪問，避免阻塞 UI
        #
        # 死鎖預防規則：
        # 1. 永不允許 同步層 -> 異步層 的鎖定順序
        # 2. 狀態層鎖定應儘可能短暫，避免嵌套
        # 3. 共享鎖 (_tts_lock) 應謹慎使用，優先權高

        # 1. _tts_lock (threading.RLock) - 同步鎖，用於同步錯誤處理
        #    - 用途：保護 TTS 引擎操作、播放列表管理、錯誤處理邏輯
        #    - 持有者：PlaybackManager (共享使用)
        #    - 獲取順序：可在同步或異步上下文中獲取
        #    - 持有時間：短暫操作 (< 100ms)，避免長時間阻塞
        #    - 層次：同步層優先權，確保播放核心線性流程
        self._tts_lock = threading.RLock()  # 同步鎖，用於同步錯誤處理

        # 2. _async_tts_lock (asyncio.Lock) - 非同步鎖，用於 async 操作
        #    - 用途：保護異步 TTS 狀態轉換、任務管理
        #    - 持有者：TTSIntegration 內部 async 方法
        #    - 獲取順序：僅在異步上下文中獲取
        #    - 持有時間：中等操作 (< 500ms)
        #    - 層次：異步層，與同步鎖無重疊
        self._async_tts_lock = asyncio.Lock()  # 非同步鎖，用於 async 操作

        # 3. _status_lock (threading.Lock) - 狀態鎖，用於 Textual UI 的同步調用
        #    - 用途：保護 TTS 狀態變更和訪問
        #    - 持有者：UI 層同步調用
        #    - 獲取順序：可在任何上下文中獲取，但優先權低
        #    - 持有時間：非常短暫 (< 10ms)
        #    - 層次：狀態層，避免與其他鎖競爭
        self._status_lock = threading.Lock()  # 保留給 Textual UI 的同步調用

        # 鎖定監控 - 執行時期鎖定使用統計
        self._lock_monitoring = {
            "_tts_lock": {
                "acquires": 0,
                "contention_time": 0.0,
                "last_acquire_time": None,
            },
            "_async_tts_lock": {
                "acquires": 0,
                "contention_time": 0.0,
                "last_acquire_time": None,
            },
            "_status_lock": {
                "acquires": 0,
                "contention_time": 0.0,
                "last_acquire_time": None,
            },
        }

        # TTS 狀態標記（用於協調 asyncio 任務）
        self._tts_should_stop = False
        self._last_tts_error = None

        # 緩衝區狀態追蹤：區分初始緩衝與真正 underrun
        self._is_initial_buffering = False

        # 引擎切換狀態追蹤 - 防止 Serial Runner 在切換期間跳章
        self._engine_switching = False

        # ============================================
        # 異步核心層 (Async Core Layer)
        # 用於: Runner、異步工作流
        # ============================================
        self._async_tts_stop_requested = asyncio.Event()
        self._async_tts_pause_requested = asyncio.Event()
        self._async_tts_synthesis_ready = asyncio.Event()
        self._async_tts_playback_ready = asyncio.Event()
        self._async_tts_data_available = asyncio.Event()
        self._async_tts_audio_ready = asyncio.Event()
        self.tts_thread_active = False
        self.last_tts_error = None

        # ============================================
        # 同步橋接層 (Sync Bridge Layer)
        # 用於: UI 事件處理、同步調用
        # ============================================
        self._sync_ui_stop_signal = threading.Event()
        self._sync_ui_pause_signal = threading.Event()
        self._sync_ui_synthesis_ready = threading.Event()
        self._sync_ui_data_available = threading.Event()

        # ============================================
        # 向後兼容屬性 (Backward Compatibility)
        # 逐步遷移中，最終會移除
        # ============================================
        # 橋接到同步橋接層（保持向後兼容）
        self.tts_stop_requested = self._sync_ui_stop_signal
        self.tts_pause_requested = self._sync_ui_pause_signal
        self.tts_synthesis_ready = self._sync_ui_synthesis_ready
        self.tts_data_available = self._sync_ui_data_available

        # 直接引用異步事件（用於需要異步操作的場合）
        self.tts_audio_ready = self._async_tts_audio_ready

        # 初始化中央橋接器 - 統一處理 sync-async 通訊
        self.async_bridge = AsyncBridge(self)

        self.network_manager = NetworkManager(app)

        # 初始化協調式關閉管理器 - 必須在播放協調器之前初始化
        self.shutdown_coordinator = ShutdownCoordinator()
        # 註冊關鍵組件
        self.shutdown_coordinator.register_component("predictive_controller")
        self.shutdown_coordinator.register_component("playback_manager")
        self.shutdown_coordinator.register_component("playlist_manager")
        self.shutdown_coordinator.register_component("tts_engine")
        self.shutdown_coordinator.register_component("task_cleanup")

        # Initialize managers
        self.playlist_manager = PlaylistManager(self, self.config_manager)
        self.playback_manager = PlaybackManager(self, self.playlist_manager)

        # 初始化播放協調器 - 統一播放控制邏輯
        self.playback_coordinator = PlaybackCoordinator(
            integration=self,
            playlist_manager=self.playlist_manager,
            playback_manager=self.playback_manager,
            shutdown_coordinator=self.shutdown_coordinator
        )

        # Backward compatibility properties
        self.network_error_occurred = self.network_manager.network_error_occurred
        self.network_error_notified = self.network_manager.network_error_notified
        self.network_recovery_notified = self.network_manager.network_recovery_notified

        # Circuit breaker for TTS operations
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,  # Trip after 5 failures
            recovery_timeout=60.0,  # Wait 60 seconds before trying again
            expected_exception=(
                TTSProviderError,
                TTSSynthesisError,
                TTSVoiceError,
                TTSPlaybackError,
                NetworkError,
            ),
        )

        # 初始化狀態機 - 集中管理 TTS 狀態轉換
        self.state_machine = TTSStateMachine(initial_state=TTSState.IDLE)

        # 初始化引擎參數管理器 - 集中管理引擎特定參數
        self.engine_params_manager = EngineParamsManager(
            config_manager=self.config_manager,
            app=self.app
        )

        # 初始化引擎工廠 - 統一引擎選擇和初始化邏輯
        self.engine_factory = TTSEngineFactory(
            config_manager=self.config_manager)

        # ============================================
        # 死鎖檢測器初始化 - 階段一：風險評估與監控強化
        # ============================================
        # 註冊所有鎖定進行監控
        detector = get_deadlock_detector()
        detector.register_lock(
            "_tts_lock", self._tts_lock, LockType.THREADING_RLOCK)
        detector.register_lock(
            "_async_tts_lock", self._async_tts_lock, LockType.ASYNCIO_LOCK)
        detector.register_lock(
            "_status_lock", self._status_lock, LockType.THREADING_LOCK)

        # 啟動背景監控
        detector.start_monitoring()
        logger.info("Deadlock monitoring enabled for TTS integration")

    @property
    def tts_lock(self):
        """向后兼容提供鎖對象給其他模塊使用"""
        return self._tts_lock

    def get_lock_monitoring_stats(self) -> dict:
        """獲取鎖定監控統計信息"""
        stats = self._lock_monitoring.copy()
        total_acquires = sum(stat["acquires"] for stat in stats.values())
        total_contention_time = sum(stat["contention_time"]
                                    for stat in stats.values())

        # 計算平均競爭時間
        avg_contention = (
            total_contention_time / total_acquires if total_acquires > 0 else 0
        )

        # 識別性能瓶頸
        bottlenecks = []
        for lock_name, lock_stats in stats.items():
            if lock_stats["acquires"] > 0:
                avg_time = lock_stats["contention_time"] / \
                    lock_stats["acquires"]
                if avg_time > 0.01:  # 超過10ms的競爭時間
                    bottlenecks.append(
                        {
                            "lock": lock_name,
                            "avg_contention_ms": avg_time * 1000,
                            "total_acquires": lock_stats["acquires"],
                        }
                    )

        return {
            "monitoring_enabled": True,
            "lock_hierarchy": {
                "sync_layer": ["_tts_lock"],  # 最高優先權
                "async_layer": ["_async_tts_lock"],  # 中等優先權
                "status_layer": ["_status_lock"],  # 最低優先權
            },
            "stats": stats,
            "summary": {
                "total_acquires": total_acquires,
                "total_contention_time": total_contention_time,
                "avg_contention_time": avg_contention,
                "bottlenecks": bottlenecks,
            },
            "deadlock_prevention": {
                "rule_1": "永不允許 同步層 -> 異步層 的鎖定順序",
                "rule_2": "狀態層鎖定應儘可能短暫，避免嵌套",
                "rule_3": "共享鎖 (_tts_lock) 應謹慎使用，優先權高",
            },
        }

    def get_bridge_stats(self) -> dict:
        """獲取橋接統計信息"""
        return self.async_bridge.get_bridge_stats()

    def _get_event_loop(self) -> asyncio.AbstractEventLoop:
        """Get the event loop for asyncio operations."""
        if self._asyncio_loop is None:
            try:
                self._asyncio_loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, create a new one
                self._asyncio_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._asyncio_loop)
        return self._asyncio_loop

    # Bridge method: Safely operates async events from sync context with timeout
    def _bridge_to_async_core(self, event: asyncio.Event, action: str) -> None:
        """
        Bridge mechanism: from sync layer to async core with timeout protection.

        This method safely operates async events from sync context using
        run_coroutine_threadsafe with timeout for better reliability.
        """
        if not self._asyncio_loop or self._asyncio_loop.is_closed():
            logger.warning("Event loop not available for bridging")
            return

        async def _do_action():
            if action == "set":
                event.set()
            elif action == "clear":
                event.clear()
            else:
                raise ValueError(f"Unknown action: {action}")

        try:
            future = asyncio.run_coroutine_threadsafe(
                _do_action(), self._asyncio_loop)
            future.result(timeout=1.0)  # 1 second timeout
            logger.debug(f"Bridged {action} to async event: {event}")
        except asyncio.TimeoutError:
            logger.error(
                f"Timeout bridging {action} to async event after 1 second")
        except Exception as e:
            logger.error(f"Error bridging {action} to async event: {e}")

    def get_tts_status(self) -> str:
        """Get TTS status (thread-safe, delegates to state machine)."""
        return self.state_machine.current_state.value

    def set_tts_status_safe(self, new_status: str) -> str:
        """
        Set TTS status safely (thread-safe, delegates to state machine).

        Returns:
            The previous status value
        """
        try:
            new_state = TTSState(new_status)
            old_state = self.state_machine.transition_to(new_state)
            if old_state:
                # Publish status change event
                try:
                    from speakub.utils.event_bus import SpeakUBEvents, event_bus

                    event_bus.publish_sync(
                        SpeakUBEvents.TTS_STATE_CHANGED,
                        {
                            "old_status": old_state.value,
                            "new_status": new_state.value,
                        },
                    )
                except Exception as e:
                    logger.debug(f"Event publish failed: {e}")
                return old_state.value
        except ValueError as e:
            logger.error(f"Invalid TTS status: {new_status}: {e}")
            return self.get_tts_status()

    # Async method: Operates in asyncio event loop, handles async TTS setup
    async def setup_tts(self) -> None:
        """Set up TTS engine based on configuration."""
        try:
            engine = self.engine_factory.select_engine()
            if not engine:
                logger.warning("No TTS engine available")
                return

            self.app.tts_engine = engine
            logger.info(f"Using {engine.__class__.__name__}")

            # Initialize engine (async loop, idle mode, etc.)
            if self.engine_factory.initialize_engine(engine):
                # Notify managers about engine change for strategy updates
                self.engine_factory.notify_engine_switched(
                    self.app, self.playlist_manager)
            else:
                logger.warning("Engine initialization failed, but continuing")

        except Exception as e:
            logger.error(f"Failed to setup TTS: {e}")
            self.app.bell()

    async def update_tts_progress(self) -> None:
        """Update TTS progress display."""
        try:
            from textual.widgets import Static

            status_widget = self.app.query_one("#tts-status", Static)
            status = self.app.tts_status.upper()
            smooth = " (Smooth)" if self.app.tts_smooth_mode else ""

            # Phase 2: UI 狀態顯示優化 - 當初始緩衝時顯示 BUFFERING 而非 PLAYING
            if status == "PLAYING" and self._is_initial_buffering:
                status_text = f"TTS: BUFFERING...{smooth}"
            else:
                status_text = f"TTS: {status}{smooth}"
            status_widget.update(status_text)

            controls_widget = self.app.query_one("#tts-controls", Static)
            percent = None
            if status == "PLAYING" and self.playlist_manager.has_items():
                # Character-based progress calculation
                total_chars = 0
                played_chars = 0

                total_items = self.playlist_manager.get_playlist_length()
                current_index = self.playlist_manager.get_current_index()

                # Calculate total characters in playlist
                for i in range(total_items):
                    item = self.playlist_manager.get_item_at(i)
                    if item and len(item) >= 1:
                        text = item[0]
                        if isinstance(text, str):
                            total_chars += len(text)

                # Calculate played characters (up to current index)
                for i in range(current_index):
                    item = self.playlist_manager.get_item_at(i)
                    if item and len(item) >= 1:
                        text = item[0]
                        if isinstance(text, str):
                            played_chars += len(text)

                if total_chars > 0:
                    percent = int((played_chars / total_chars) * 100)
            p_disp = f"{percent}%" if percent is not None else "--"

            # 根據當前 TTS 引擎顯示對應的配置值
            current_engine = self.config_manager.get(
                "tts.preferred_engine", "edge-tts")

            if current_engine == "gtts":
                # GTTS: 顯示直接的音量和速度值
                v_val = self.config_manager.get("gtts.volume", 1.0)
                s_val = self.config_manager.get("gtts.playback_speed", 1.5)
                v_disp = f"{int(v_val * 100)}"
                s_disp = f"{s_val:.1f}"
                pitch_disp = "N/A"  # GTTS 不支持 pitch
            elif current_engine == "nanmai":
                # NanmaiTTS: 顯示直接的音量和速度值
                v_val = self.config_manager.get("nanmai.volume", 1.0)
                s_val = self.config_manager.get("nanmai.playback_speed", 0.8)
                v_disp = f"{int(v_val * 100)}"
                s_disp = f"{s_val:.1f}"
                pitch_disp = "N/A"  # NanmaiTTS 不支持 pitch
            elif current_engine == "edge-tts":
                # Edge-TTS: 顯示自己的配置值
                v_val = self.config_manager.get("edge-tts.volume", 1.0)
                s_val = self.config_manager.get("edge-tts.playback_speed", 1.0)
                v_disp = f"{int(v_val * 100)}"
                s_disp = f"{s_val:.1f}"
                pitch_disp = self.app.tts_pitch  # Edge-TTS 支持 pitch
            else:
                # 回退到全局設定（以防萬一）
                v_disp = f"{self.app.tts_volume}"
                s_disp = f"{self.app.tts_rate:+}"
                pitch_disp = self.app.tts_pitch

            controls_text = f"Vol: {v_disp}% | Speed: {s_disp}x | Pitch: {pitch_disp}"
            controls_widget.update(controls_text)

            page_widget = self.app.query_one("#tts-page", Static)
            page_text = ""
            if self.app.viewport_content:
                info = self.app.viewport_content.get_viewport_info()
                page_text = (
                    f"Page {info['current_page'] + 1}/{info['total_pages']} ({p_disp})"
                )
            page_widget.update(page_text)

            # Add debug info for current audio file
            try:
                if self.app.tts_engine and hasattr(self.app.tts_engine, "audio_player"):
                    audio_status = self.app.tts_engine.audio_player.get_status()
                    current_file = audio_status.get("current_file", "None")
                    if current_file and current_file != "None":
                        # Extract just the filename from the path for display
                        import os

                        filename = os.path.basename(current_file)
                        debug_info = f"File: {filename}"
                        # Update the TTS panel with debug info if it exists
                        try:
                            tts_panel = self.app.query_one(
                                "#tts-panel", type=type(None)
                            )
                            if tts_panel and hasattr(tts_panel, "update_status"):
                                # Get current status and add debug info
                                current_status = status_text
                                tts_panel.update_status(
                                    current_status, debug_info)
                        except Exception:
                            pass  # Ignore if panel doesn't exist or doesn't support debug info
            except Exception:
                pass  # Ignore debug info errors

        except Exception:
            import logging

            logging.exception("Error updating TTS progress display")

    # Sync method: Handles UI play/pause events
    def handle_tts_play_pause(self) -> None:
        """Handle TTS play/pause action with asyncio coordination."""
        # 直接處理，因為這是從同步 UI 調用的
        current_state = self.state_machine.current_state

        if current_state == TTSState.PLAYING:
            # 使用 asyncio.to_thread 將阻塞操作移到線程池
            loop = self._get_event_loop()
            task = loop.create_task(
                asyncio.to_thread(
                    self.playback_manager.stop_playback, is_pause=True)
            )
            self._tts_active_tasks.add(task)

            # Pause predictive controller scheduling during pause
            if (
                hasattr(self.playlist_manager, "_predictive_controller")
                and self.playlist_manager._predictive_controller
            ):
                try:
                    self.playlist_manager._predictive_controller.pause_scheduling()
                except Exception as e:
                    logger.warning(
                        f"Failed to pause predictive scheduling: {e}")

            self.set_tts_status_safe("PAUSED")

        elif current_state == TTSState.PAUSED:
            # 清除暫停狀態並恢復播放
            self._tts_should_stop = False
            if self.network_manager.network_error_occurred:
                self.network_manager.reset_network_error_state()
                if hasattr(self.app, "notify"):
                    self.app.notify(
                        "Restarting TTS playback...",
                        title="TTS Resume",
                        severity="information",
                    )

            # Resume predictive controller scheduling when resuming playback
            if (
                hasattr(self.playlist_manager, "_predictive_controller")
                and self.playlist_manager._predictive_controller
            ):
                try:
                    self.playlist_manager._predictive_controller.resume_scheduling()
                except Exception as e:
                    logger.warning(
                        f"Failed to resume predictive scheduling: {e}")

            # 啟動播放（使用線程池）
            loop = self._get_event_loop()
            task = loop.create_task(
                asyncio.to_thread(self.playback_manager.start_playback)
            )
            self._tts_active_tasks.add(task)

        elif current_state == TTSState.STOPPED:
            # 設置初始緩衝狀態 - 開始播放後的等待視為正常行為
            self._is_initial_buffering = True

            if self.network_manager.network_error_occurred:
                self.network_manager.reset_network_error_state()

            # 生成 playlist（同步操作，使用線程池）
            loop = self._get_event_loop()
            task = loop.create_task(
                asyncio.to_thread(self.playlist_manager.generate_playlist)
            )
            self._tts_active_tasks.add(task)

            # 等待 playlist 生成完成然後啟動播放
            async def _start_after_playlist():
                await task
                if self.playlist_manager.has_items():
                    await asyncio.to_thread(self.playback_manager.start_playback)
                else:
                    # 使用線程池執行 worker 函數
                    worker_func = functools.partial(
                        find_and_play_next_chapter_worker, self
                    )
                    await asyncio.to_thread(
                        lambda: self.app.run_worker(
                            worker_func, exclusive=True, thread=True
                        )
                    )

            task = loop.create_task(_start_after_playlist())
            self._tts_active_tasks.add(task)

        # 清理完成的任務
        self._tts_active_tasks = {
            t for t in self._tts_active_tasks if not t.done() or t.cancelled()
        }

    def stop_speaking(self, is_pause: bool = False) -> None:
        """
        Stop TTS playback with unified resource cleanup.

        Uses PlaybackCoordinator for consistent resource management.
        Falls back to fast mode for quick operations like engine switching.
        """
        if is_pause:
            self.playback_coordinator.pause_playback()
        else:
            self.playback_coordinator.stop_playback_with_cleanup(
                cleanup_mode=CleanupMode.FAST
            )

    def _reset_async_events(self) -> None:
        """Reset all async events to prevent state pollution from old engines."""
        # CRITICAL FIX: Clear all async events during reset to prevent
        # old engine state from affecting new engine behavior
        try:
            self._async_tts_stop_requested.clear()
            self._async_tts_pause_requested.clear()
            self._async_tts_synthesis_ready.clear()
            self._async_tts_playback_ready.clear()
            self._async_tts_data_available.clear()
            self._async_tts_audio_ready.clear()  # Prevent old buffer underrun waits
            logger.debug(
                "Async events reset completed to prevent engine state pollution"
            )
        except Exception as e:
            logger.warning(f"Error resetting async events: {e}")

    def _handle_network_error(self, error: Exception, context: str) -> None:
        """Handle network error (backward compatibility)."""
        self.network_manager.handle_network_error(error, context)

    def reset_network_error_state(self) -> None:
        """Reset network error state (backward compatibility)."""
        self.network_manager.reset_network_error_state()

    def _monitor_network_recovery(self) -> None:
        """Monitor network recovery (backward compatibility)."""
        self.network_manager.monitor_network_recovery()

    def speak_with_engine(self, text: str) -> None:
        """Speak text using TTS engine with intelligent retry logic and circuit breaker protection."""
        if not self.app.tts_engine:
            logger.warning("No TTS engine is available")
            return

        # Only apply speakable content filtering to engines that need it
        # gTTS can handle all content correctly, so skip filtering for it
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts")
        needs_filtering = current_engine in ("edge-tts", "nanmai")

        reason = "not_filtered"  # Default reason for engines that don't need filtering

        if needs_filtering:
            # Check if content is speakable
            speakable, reason = is_speakable_content(text)
            if not speakable:
                logger.info(
                    f"Non-speakable content detected (reason: {reason}), handling as pause"
                )
                # Handle punctuation/symbol-only content as pauses instead of skipping
                from speakub.utils.text_utils import analyze_punctuation_content

                pause_type, pause_duration = analyze_punctuation_content(text)
                logger.debug(
                    f"Inserting {pause_type} pause ({pause_duration:.1f}s) for '{text[:20]}...'"
                )
                if pause_duration > 0:
                    time.sleep(pause_duration)
                return  # Content handled as pause, no further processing needed

        # Add delay to prevent rate limiting before synthesis
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts")
        # Get synthesis delay directly from config
        synthesis_delay = self.config_manager.get(
            f"{current_engine}.smooth_synthesis_delay",
            self.config_manager.get("tts.smooth_synthesis_delay", 1.2),
        )
        time.sleep(synthesis_delay)

        # Use circuit breaker to protect against cascading failures
        text_snippet = text[:50] + "..." if len(text) > 50 else text
        try:
            self.circuit_breaker.call(self._synthesis_with_retry, text, reason)
        except CircuitBreakerOpenException as e:
            logger.warning(f"Circuit breaker prevented TTS call: {e}")
            # Notify user that TTS is temporarily disabled due to failures
            if hasattr(self.app, "notify"):
                self.app.notify(
                    f"TTS temporarily disabled due to repeated failures. Last failed content: '{text_snippet}'. Please try again later.",
                    title="TTS Circuit Breaker",
                    severity="warning",
                )
            # Pause playback if currently playing
            if self.state_machine.is_playing():
                self.stop_speaking(is_pause=True)
                self.set_tts_status_safe("PAUSED")
            # ⭐ 新增：拋出異常讓 runners.py 能夠檢測到 circuit breaker 打開
            raise e
        except Exception as e:
            # Re-raise other exceptions
            raise e

    def _synthesis_with_retry(self, text: str, reason: str) -> None:
        """Perform TTS synthesis with retry logic (called by circuit breaker)."""
        # Use unified retry configuration and utilities
        from speakub.utils.retry_utils import (
            should_retry_content_error,
            get_content_retry_delay
        )

        attempt = 0
        while should_retry_content_error(attempt, reason):
            try:
                # 1. 先清理文字 (移除 [7] 這種註腳)
                from speakub.utils.text_utils import clean_text_for_tts

                cleaned_text = clean_text_for_tts(text)
                # 2. 再修正發音
                corrected_text = correct_chinese_pronunciation(cleaned_text)

                kwargs = self.engine_params_manager.get_params_for_engine()
                self._execute_tts_synthesis(corrected_text, kwargs)

                return  # 如果成功，直接返回

            except (
                TTSProviderError,
                TTSSynthesisError,
                TTSVoiceError,
                TTSPlaybackError,
            ):
                # Re-raise already categorized TTS errors
                raise
            except TimeoutError as e:
                # Check if it's due to async manager being unavailable (engine switch)
                if "async manager unavailable" in str(e).lower():
                    logger.warning(
                        f"Engine switched during synthesis - async manager no longer available. "
                        f"Aborting synthesis of: {text[:30]}..."
                    )
                    # Don't retry - engine has been switched
                    raise TTSProviderError(
                        f"Engine unavailable (switched): {e}") from e
                else:
                    # Regular timeout - retry if possible
                    if should_retry_content_error(attempt + 1, reason):
                        retry_delay = get_content_retry_delay(attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}: "
                            f"TTS synthesis timed out. Retrying in {retry_delay:.2f}s..."
                        )
                        time.sleep(retry_delay)
                        attempt += 1
                    else:
                        raise
            except (NetworkTimeoutError, NetworkConnectionError, NetworkAPIError):
                self._handle_network_error(e, "TTS synthesis")
                raise NetworkError(f"TTS network error: {e}")
            except NoAudioReceived as e:
                if should_retry_content_error(attempt + 1, reason):
                    retry_delay = get_content_retry_delay(attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}: "
                        f"EdgeTTS returned no audio for content (reason: {reason}). Retrying in {retry_delay:.2f}s..."
                    )
                    time.sleep(retry_delay)
                    attempt += 1
                else:
                    # 如果所有重試都失敗了，檢查內容是否包含可發音文字
                    from speakub.utils.text_utils import is_speakable_content

                    speakable, speakable_reason = is_speakable_content(text)

                    if speakable and "has_speakable_characters" in speakable_reason:
                        # 對於包含文字但合成失敗的內容，處理為pause而不是raise異常
                        logger.warning(
                            f"Content '{text[:20]}...' has speakable characters but synthesis failed. "
                            f"Treating as pause instead of error to avoid skipping in non-smooth mode."
                        )
                        # 插入pause處理
                        from speakub.utils.text_utils import analyze_punctuation_content

                        pause_type, pause_duration = analyze_punctuation_content(
                            text)
                        logger.debug(
                            f"Inserting {pause_type} pause ({pause_duration:.1f}s) for failed synthesis of speakable content"
                        )
                        if pause_duration > 0:
                            time.sleep(pause_duration)
                        return  # 作為pause處理，直接返回不需要進度
                    else:
                        # 對於純符號內容的合失敗，重新拋出異常
                        logger.error(
                            f"All retries failed for NoAudioReceived error. Content reason: {reason}"
                        )
                        raise e
            except Exception as e:
                self._handle_generic_error(e, corrected_text)

    def _execute_tts_synthesis(self, text: str, kwargs: dict) -> None:
        """Execute TTS synthesis with provided parameters."""
        if hasattr(self.app.tts_engine, "speak_text_sync"):
            # Non-smooth mode: No client-side timeout, let server decide
            # Smooth mode: 60 second timeout for resource protection
            timeout = None if not self.app.tts_smooth_mode else 60
            self.app.tts_engine.speak_text_sync(
                text, timeout=timeout, **kwargs)

    def _handle_network_error_internal(self, error: Exception) -> None:
        """Handle network-related TTS errors."""
        if hasattr(self.app, "notify"):
            self.app.notify(f"網路連接錯誤: {str(error)}",
                            title="網路錯誤", severity="error")
        event_bus.publish_sync(
            SpeakUBEvents.ERROR_OCCURRED,
            {"error_type": "network", "message": str(error)},
        )

    def _handle_generic_error(self, error: Exception, text: str = "") -> None:
        """Handle and categorize generic TTS errors, letting circuit breaker manage error propagation."""
        error_msg = str(error).lower()

        # TTS-related errors: Let circuit breaker handle these properly
        # Circuit breaker will raise CircuitBreakerOpenException for too many failures
        if any(
            keyword in error_msg
            for keyword in [
                "audio",
                "synthesis",
                "voice",
                "playback",
                "tts",
                "failed",
                "no audio",
            ]
        ):
            # Log the TTS error with content context and full traceback
            text_snippet = text[:200] + "..." if len(text) > 200 else text
            logger.error(
                f"TTS Synthesis Error: Failed synthesizing content '{text_snippet}': {type(error).__name__}: {error}",
                exc_info=True,
            )
            # Force flush file handlers to ensure error is written immediately
            for handler in logging.getLogger().handlers:
                if isinstance(handler, logging.FileHandler):
                    handler.flush()
            # Raise TTS-specific errors for circuit breaker to handle
            if "synthesis" in error_msg:
                raise TTSSynthesisError(f"TTS synthesis failed: {error}")
            elif "voice" in error_msg:
                raise TTSVoiceError(f"TTS voice error: {error}")
            elif "playback" in error_msg:
                raise TTSPlaybackError(f"TTS playback failed: {error}")
            else:
                raise TTSError(f"TTS error: {error}")

        # For non-TTS errors, categorize and handle as before
        error_details = self._categorize_error(error_msg, str(error))
        text_snippet = text[:200] + "..." if len(text) > 200 else text
        logger.error(
            f"Non-TTS error for content '{text_snippet}': {error_details['type']}: {error}"
        )

        if hasattr(self.app, "notify"):
            content_info = f", content '{text[:50]}...'" if text else ""
            notification_msg = error_details["notification"] + content_info
            self.app.notify(
                notification_msg,
                title=error_details["title"],
                severity="error",
            )
        event_bus.publish_sync(
            SpeakUBEvents.ERROR_OCCURRED,
            {"error_type": error_details["type"], "message": str(error)},
        )
        raise error_details["exception"](
            f"TTS {error_details['type']} error: {error}")

    def _handle_synthesis_error(
        self, error: Exception, failed_index: Optional[int] = None
    ) -> None:
        """
        處理合成錯誤，強制清理所有背景 TTS 任務，並安全地將系統置於暫停狀態。
        """
        logger.error(
            f"Synthesis failed at index {failed_index}, initiating system pause and task cleanup."
        )

        # 創建任務委派給 async 處理器，避免同步 blocking
        loop = self._get_event_loop()
        if loop and not loop.is_closed():
            # 在事件循環中創建任務進行完全的 async 處理
            task = asyncio.create_task(
                self._async_handle_synthesis_error(error, failed_index)
            )
            self._tts_active_tasks.add(task)
            logger.debug("Created async task for synthesis error handling")
        else:
            logger.warning(
                "No event loop available, performing minimal error handling")
            # 後退支援：最小的錯誤處理但不使用 threading
            if self.state_machine.is_playing():
                self.set_tts_status_safe("PAUSED")

    async def _async_handle_synthesis_error(
        self, error: Exception, failed_index: Optional[int] = None
    ) -> None:
        """真正的 async 錯誤處理邏輯，使用 asyncio.Lock"""
        async with self._async_tts_lock:
            # ⭐ 修復：檢查是否已經有停止請求，避免重複執行錯誤處理
            # 如果已經有停止請求，說明錯誤處理已經執行過，直接返回
            if self._async_tts_stop_requested.is_set():
                logger.debug(
                    f"Synthesis error at index {failed_index}, but stop already requested - skipping duplicate handling"
                )
                return

            play_warning_sound()
            self.last_tts_error = str(error)

            # ⭐ 立即發送錯誤通知給用戶 - 避免 90 秒的 timeout 延遲
            try:
                # 使用 app.notify 而不是 NotificationManager
                if hasattr(self.app, "notify"):
                    self.app.notify(
                        "TTS synthesis failed - playback stopped",
                        title="TTS Error",
                        severity="error"
                    )
                logger.info(
                    "[IMMEDIATE NOTIFY] Error notification sent to user immediately")
            except Exception as e:
                # 1. 立即發出停止信號，要求所有 TTS 任務退出循環
                logger.debug(f"Failed to send immediate notification: {e}")
            self._async_tts_stop_requested.set()
            logger.info("Async stop event set for all TTS tasks.")

            # 1.5. 停止 Reservoir Controller 監控 (Smooth Mode 的關鍵修復)
            # 在合成失敗時必須停止 controller 的監控循環，防止它持續嘗試觸發合成
            if (
                hasattr(self, "playlist_manager")
                and hasattr(self.playlist_manager, "_predictive_controller")
                and self.playlist_manager._predictive_controller
            ):
                try:
                    controller = self.playlist_manager._predictive_controller
                    if controller.running:
                        logger.info(
                            "Stopping Reservoir Controller monitoring due to synthesis error in smooth mode"
                        )
                        await controller.stop_monitoring()
                except Exception as e:
                    logger.warning(
                        f"Error stopping Reservoir Controller during synthesis error: {e}"
                    )

            # Use asyncio.create_task for non-blocking cleanup
            try:
                # Handle all operations in event loop, all operations are non-blocking
                tasks_to_cancel = []
                for task in self._tts_active_tasks:
                    if not task.done() and not task.cancelled():
                        tasks_to_cancel.append(task)

                if tasks_to_cancel:
                    logger.info(
                        f"Cancelling {len(tasks_to_cancel)} active TTS tasks..."
                    )
                    # Use asyncio.gather for concurrent cancellation
                    cancel_tasks = [
                        asyncio.create_task(self._safe_cancel_task(task))
                        for task in tasks_to_cancel
                    ]
                    await asyncio.gather(*cancel_tasks, return_exceptions=True)

                self._tts_active_tasks.clear()
                self.tts_thread_active = False
                logger.info("All active TTS async tasks have been cancelled.")

            except Exception as e:
                logger.error(
                    f"An unexpected error occurred during async task cleanup: {e}"
                )

            # 2. 安全地暫停播放器硬體 (在 async 上下文中)
            if self.app.tts_engine and hasattr(self.app.tts_engine, "pause"):
                try:
                    self.app.tts_engine.pause()
                except Exception as e:
                    logger.warning(f"Error pausing TTS engine hardware: {e}")

            # 3. 更新 UI 狀態
            # ⭐ 修復：Smooth 模式用 STOPPED，非 smooth 模式用 PAUSED
            # 直接設置狀態，不依賴 state_machine（因為它沒有 setter）
            try:
                # 設置 UI 顯示 - 立即更新，不要等 timeout
                # ⭐ 重要：不要在狀態中包含 (Smooth)，讓 update_tts_progress() 處理
                if self.app.tts_smooth_mode:
                    self.app.tts_status = "STOPPED"
                else:
                    self.app.tts_status = "PAUSED"

                logger.info(
                    f"[IMMEDIATE] TTS status set to {self.app.tts_status} due to synthesis error")
            except Exception as e:
                logger.warning(f"Error setting TTS status: {e}")
            try:
                await self.update_tts_progress()
            except Exception as e:
                logger.warning(f"Error updating TTS progress: {e}")

            # 通知用戶
            error_type_name = type(error).__name__
            error_message = str(error)
            user_friendly_message = (
                f"TTS Error ({error_type_name}): {error_message}. Playback paused."
            )

            try:
                if hasattr(self.app, "notify"):
                    self.app.notify(
                        user_friendly_message,
                        title="TTS Paused due to Error",
                        severity="warning",
                    )
            except Exception as e:
                logger.warning(f"Error notifying user: {e}")

    async def _safe_cancel_task(self, task: asyncio.Task) -> None:
        """安全地取消任務的方法"""
        try:
            task.cancel()
            logger.debug(f"Cancelled async task: {task}")
        except Exception as e:
            logger.warning(f"Error cancelling async task: {e}")

    def _initiate_automatic_recovery(self) -> None:
        """
        Automatic recovery has been disabled. This method now only clears recovery flags
        and leaves TTS in paused state for user to decide next action.
        """
        # Clear recovery flags but do not attempt recovery
        self.cutoff_recovery_active = False
        self.failed_synthesis_indices.clear()

        logger.info(
            "Automatic recovery disabled. TTS remains paused for user intervention."
        )

    def _categorize_error(self, error_msg: str, full_error: str) -> dict:
        """Categorize error based on message content (delegated to helper)."""
        return ErrorCategoryHelper.categorize_error(error_msg, full_error)

    def _reset_failed_synthesis_items_after_recovery(self) -> None:
        """Reset FAILED_SYNTHESIS items to unprepared state after TTS recovery.

        After Edge-TTS cutoff recovery, items that were marked as FAILED_SYNTHESIS
        during the service error period should be reset so they can be re-synthesized
        with the now-recovered TTS service.
        """
        reset_count = 0
        with self.tts_lock:
            playlist_length = self.playlist_manager.get_playlist_length()
            for i in range(playlist_length):
                item = self.playlist_manager.get_item_at(i)
                if item and len(item) == 3 and item[2] == b"FAILED_SYNTHESIS":
                    # Reset to unprepared state: (text, line_num)
                    self.playlist_manager.update_item_at(i, (item[0], item[1]))
                    reset_count += 1

        if reset_count > 0:
            logger.info(
                f"Reset {reset_count} FAILED_SYNTHESIS items for re-synthesis after TTS recovery"
            )

    def _convert_tts_rate_to_mpv_speed(self, rate: int) -> float:
        """
        Convert TTS rate percentage (-100 to +100) to MPV playback speed (0.5 to 3.0).

        This function is used by all MPV-based TTS providers (GTTS, NanmaiTTS).
        Calibration based on Edge-TTS speed matching (latest empirical data):
        - Edge-TTS rate = +30% corresponds to MPV playback speed ~1.75-1.8x
        - Therefore, Edge-TTS rate changes affect MPV speed by factor of 2.5

        Args:
            rate: TTS rate adjustment percentage (-100 to +100)

        Returns:
            MPV playback speed multiplier (0.5 to 3.0)

        Examples:
        rate = 0   -> speed = 1.0   (normal speed)
        rate = +30 -> speed = 1.75  (matches Edge-TTS +30%, ~1.7-1.8x range)
        rate = +50 -> speed = 2.25
        rate = +100 -> speed = 3.5 (but clamped to 3.0)
        rate = -50 -> speed = -0.25 (but clamped to 0.5)
        """
        # Based on latest calibration: Edge-TTS 30% = MPV 1.75x
        # Coefficient: (1.75-1.0)/0.3 ≈ 2.5
        conversion_factor = 2.5
        speed = 1.0 + (rate / 100.0) * conversion_factor
        return max(0.5, min(3.0, speed))

    def cancel_pending_tasks(self) -> None:
        """取消所有掛起的 asyncio 任務以防止記憶體累積"""
        try:
            # Cancel tasks tracked in our active tasks set
            tasks_to_cancel = []
            for task in self._tts_active_tasks:
                if not task.done() and not task.cancelled():
                    tasks_to_cancel.append(task)

            if tasks_to_cancel:
                logger.debug(
                    f"Cancelling {len(tasks_to_cancel)} tracked TTS tasks...")
                for task in tasks_to_cancel:
                    try:
                        task.cancel()
                        logger.debug(
                            f"Cancelled tracked TTS task: {task.get_name() or str(task)}"
                        )
                    except Exception as e:
                        logger.warning(f"Failed to cancel tracked task: {e}")

            # Clear the tasks set to remove completed/cancelled tasks
            self._tts_active_tasks.clear()

            # Also cancel any other pending asyncio tasks (fallback)
            try:
                loop = asyncio.get_event_loop()
                if loop and not loop.is_closed():
                    all_tasks = asyncio.all_tasks(loop)
                    current_task = asyncio.current_task()
                    other_tasks = [
                        t
                        for t in all_tasks
                        if t != current_task and not t.done() and not t.cancelled()
                    ]

                    if other_tasks:
                        logger.debug(
                            f"Cancelling {len(other_tasks)} other pending tasks..."
                        )
                        for task in other_tasks:
                            try:
                                task.cancel()
                                logger.debug(
                                    f"Cancelled other task: {task.get_name() or str(task)}"
                                )
                            except Exception as e:
                                logger.warning(
                                    f"Failed to cancel other task: {e}")
            except Exception as e:
                logger.debug(f"Error cancelling other pending tasks: {e}")

        except Exception as e:
            logger.warning(f"Error cancelling pending tasks: {e}")

    def stop_predictive_controller(self) -> None:
        """Stop the predictive batch controller and cancel its tasks."""
        if hasattr(self, "playlist_manager") and self.playlist_manager:
            if (
                hasattr(self.playlist_manager, "_predictive_controller")
                and self.playlist_manager._predictive_controller
            ):
                try:
                    # 在同步上下文中直接停止，不要创建异步任务
                    # Stop monitoring synchronously
                    # 注意：这里可能需要修改PredictiveBatchController使其支持同步停止，或者简单忽略错误
                    logger.debug(
                        "Stopping predictive controller during cleanup")
                    # 暂时注释掉有问题的异步调用
                    # asyncio.create_task(
                    #     self.playlist_manager._predictive_controller.stop_monitoring())
                except Exception as e:
                    logger.warning(
                        f"Error during predictive controller cleanup: {e}")

    def cancel_playlist_manager_tasks(self) -> None:
        """Cancel all tasks managed by playlist manager."""
        if hasattr(self, "playlist_manager") and self.playlist_manager:
            try:
                # Cancel preload tasks, batch tasks, and synthesis tasks
                self.playlist_manager._cancel_preload_tasks()
                self.playlist_manager._cancel_batch_preload_task()
                self.playlist_manager._cancel_synthesis_tasks()
            except Exception as e:
                logger.warning(f"Error cancelling playlist manager tasks: {e}")

    def cleanup_orphaned_temp_files(self) -> int:
        """
        清理舊的 TTS 臨時檔案，防止檔案系統累積
        Phase 2: Centralized resource management - delegate to ResourceManager
        """
        try:
            from speakub.utils.file_utils import get_resource_manager

            # Delegate cleanup to ResourceManager, the single authority for resource cleanup
            resource_manager = get_resource_manager()

            # Clean up old TTS temp files (24 hours by default)
            max_age_hours = self.config_manager.get(
                "tts.temp_file_cleanup_age_hours", 24
            )
            cleaned_count = resource_manager.cleanup_temp_files_by_age(
                max_age_hours)

            if cleaned_count > 0:
                logger.info(
                    f"ResourceManager cleaned up {cleaned_count} orphaned TTS temp files"
                )

            return cleaned_count

        except Exception as e:
            logger.warning(
                f"Error during ResourceManager cleanup delegation: {e}")
            # ResourceManager is the authoritative cleanup system
            # No fallback implementation - ResourceManager should be fixed if issues occur
            logger.error(
                "ResourceManager failed - no fallback cleanup available")
            return 0

    def check_memory_usage(self) -> dict:
        """監控和報告記憶體使用狀態"""
        try:
            import logging

            import psutil

            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()

            memory_stats = {
                "process_rss_mb": memory_info.rss / 1024 / 1024,
                "process_vms_mb": memory_info.vms / 1024 / 1024,
                "system_memory_percent": system_memory.percent,
                "system_memory_available_gb": system_memory.available / (1024**3),
            }

            # 根據當前 TTS 引擎獲取對應的記憶體警告閾值
            current_engine = self.config_manager.get(
                "tts.preferred_engine", "edge-tts")
            memory_threshold = self.config_manager.get(
                f"{current_engine}.memory_warning_threshold_mb",
                self.config_manager.get(
                    "tts.memory_warning_threshold_mb", 200
                ),  # 回退到全域設定
            )

            # 如果記憶體使用超過閾值，記錄警告
            if memory_stats["process_rss_mb"] > memory_threshold:
                logger.debug(
                    f"High TTS process memory usage: {memory_stats['process_rss_mb']:.1f} MB "
                    f"(Threshold: {memory_threshold} MB, System memory: {memory_stats['system_memory_percent']:.1f}%)"
                )

            return memory_stats

        except ImportError:
            logger.warning("psutil not available for memory monitoring")
            return {}
        except Exception as e:
            logger.warning(f"Error checking memory usage: {e}")
            return {}

    def cleanup(self) -> None:
        """Clean up TTS resources using coordinated shutdown."""
        import logging

        logger.info("Starting coordinated TTS cleanup process...")

        # 檢查初始記憶體使用
        memory_before = self.check_memory_usage()
        logger.debug(
            "Memory usage before cleanup: {0:.1f} MB".format(
                memory_before.get("process_rss_mb", 0)
            )
        )

        # 檢查 TTS 是否實際在運行 - 如果已停止，只做最小清理
        tts_status = self.get_tts_status()
        if tts_status == "STOPPED":
            logger.info("TTS is already stopped, performing minimal cleanup")
            self._minimal_cleanup()
        else:
            # TTS 仍在運行，使用協調式關閉管理器進行優雅關閉
            try:
                # 檢查是否已在事件循環中執行，避免 run_until_complete 衝突
                try:
                    current_loop = asyncio.get_running_loop()
                    in_event_loop = True
                    logger.debug(
                        "Cleanup called from within event loop, using delegation"
                    )
                except RuntimeError:
                    in_event_loop = False
                    logger.debug("Cleanup called from outside event loop")

                if in_event_loop:
                    # 已在事件循環中，使用橋接器執行異步關閉
                    try:
                        shutdown_stats = self.async_bridge.run_coroutine(
                            self.shutdown_coordinator.graceful_shutdown(self),
                            timeout=10.0,  # 減少超時時間從 30 秒到 10 秒
                        )
                        logger.info(
                            f"Coordinated shutdown completed (async): {shutdown_stats}"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Async shutdown failed, falling back: {e}")
                        # 異步失敗時仍嘗試同步清理
                        self._kill_all_synthesis_tasks()
                        self.playlist_manager.reset()
                        self._reset_async_events()
                else:
                    # 不在事件循環中，使用傳統 run_until_complete
                    loop = self._get_event_loop()
                    if loop and not loop.is_closed():
                        # 在事件循環中運行協調式關閉
                        shutdown_stats = loop.run_until_complete(
                            self.shutdown_coordinator.graceful_shutdown(self)
                        )
                        logger.info(
                            f"Coordinated shutdown completed: {shutdown_stats}")
                    else:
                        logger.warning(
                            "No event loop available, falling back to legacy cleanup"
                        )
                        # 回退到舊的清理邏輯
                        self._kill_all_synthesis_tasks()
                        self.playlist_manager.reset()
                        self._reset_async_events()
            except Exception as e:
                logger.error(f"Error during TTS cleanup: {e}")
                # Ensure minimal cleanup is performed even if main cleanup fails
                self._minimal_cleanup()

        # 最終記憶體檢查
        memory_after = self.check_memory_usage()
        memory_reduction = memory_before.get("process_rss_mb", 0) - memory_after.get(
            "process_rss_mb", 0
        )

        logger.info("TTS cleanup process completed.")
        logger.debug(f"Memory reduction: {memory_reduction:.1f} MB")

    def _minimal_cleanup(self) -> None:
        """Minimal cleanup when TTS is already stopped."""
        logger.debug("Performing minimal TTS cleanup...")

        try:
            # Reset async events to prevent state pollution
            self._reset_async_events()

            # Clean up orphaned temp files only
            try:
                cleaned_count = self.cleanup_orphaned_temp_files()
                if cleaned_count > 0:
                    logger.debug(
                        f"Cleaned up {cleaned_count} orphaned temp files")
            except Exception as e:
                logger.warning(f"Error cleaning orphaned temp files: {e}")

            # Clean up any remaining tasks (should be minimal)
            self._tts_active_tasks.clear()

        except Exception as e:
            logger.warning(f"Error during minimal cleanup: {e}")

    def get_shutdown_stats(self) -> Dict[str, Any]:
        """獲取關閉統計信息"""
        return self.shutdown_coordinator.get_shutdown_stats()

    # Legacy temp file cleanup method has been removed.
    # ResourceManager is now the authoritative source for all resource cleanup.
    # If issues occur, ResourceManager should be investigated and fixed instead
    # of maintaining redundant cleanup logic.
