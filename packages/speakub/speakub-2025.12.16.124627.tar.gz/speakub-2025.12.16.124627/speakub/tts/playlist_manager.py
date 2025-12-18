"""
Playlist Manager for TTS in SpeakUB.
Handles playlist generation and indexing.
"""

from speakub.tts.ui.playlist import prepare_tts_playlist, tts_load_next_chapter
from speakub.tts.fusion_reservoir import FusionBatchingStrategy
import asyncio
import logging
import time
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

# Type alias for complex playlist item types
PlaylistItem = Union[Tuple[str, int], Tuple[str, int, Union[bytes, str]]]


if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration
    # Updated type checking import
    from speakub.tts.fusion_reservoir.controller import SimpleReservoirController
else:
    # Import at runtime for actual usage - SWITCHED TO V7.0
    from speakub.tts.fusion_reservoir.controller import SimpleReservoirController

logger = logging.getLogger(__name__)


class PlaylistManager:
    """Manages TTS playlist generation and indexing with batch preloading support."""

    def __init__(self, tts_integration: "TTSIntegration", config_manager=None):
        self.tts_integration = tts_integration
        self.app = tts_integration.app
        # Type alias simplifies complex Union types
        self.playlist: List[PlaylistItem] = []
        self.current_index: int = 0
        # Currently active TTS engine
        self.current_engine: Optional[str] = None
        self._preload_tasks: List[asyncio.Task] = []
        self._preload_lock = asyncio.Lock()

        # Use provided ConfigManager or create new one for backward compatibility
        if config_manager is not None:
            self._config_manager = config_manager
        else:
            from speakub.utils.config import ConfigManager

            self._config_manager = ConfigManager()

        # Batch preloading attributes
        self._playback_queue: asyncio.Queue = asyncio.Queue()
        self._batch_preload_task: Optional[asyncio.Task] = None
        # Track synthesis tasks for cleanup
        self._synthesis_tasks: List[asyncio.Task] = []
        self._batch_size: int = self._config_manager.get("tts.batch_size", 5)
        self._max_queue_size: int = self._config_manager.get(
            "tts.max_queue_size", 20)
        self._dynamic_adjustment: bool = self._config_manager.get(
            "tts.dynamic_batch_adjustment", True
        )
        self._adjustment_window: int = self._config_manager.get(
            "tts.batch_adjustment_window", 10
        )

        # Performance monitoring
        self._synthesis_times: deque = deque(maxlen=self._adjustment_window)
        self._batch_start_time: float = 0.0
        self._last_adjustment_time: float = time.time()

        # --- RESERVOIR V7.0 MIGRATION ---
        # Replaced complex components with single SimpleReservoirController
        # self._play_monitor = PlayTimeMonitor()
        # self._queue_predictor = QueuePredictor(self._play_monitor)

        # Instantiating Lightweight Controller
        self._predictive_controller = SimpleReservoirController(
            self, self._config_manager)

        # For backward compatibility, expose queue_predictor property from controller
        # (SimpleController has a dummy queue_predictor)
        self._queue_predictor = self._predictive_controller.queue_predictor
        self._play_monitor = None  # Deprecated

        # Subscribe controller to idle mode changes
        self._predictive_controller.subscribe_to_idle_mode(self.app)

        # Closed-loop resource control: Subscribe to resource pressure events
        from speakub.utils.event_bus import event_bus

        self._event_bus = event_bus
        self._event_bus.subscribe(
            "tts_resource_pressure", self._handle_resource_pressure_event
        )
        # Subscribe to rate limiting detection events
        self._event_bus.subscribe(
            "tts_rate_limiting_detected", self._handle_rate_limiting_event
        )

        # Mode management for preventing dual activation (v4.0 fix)
        self._active_mode = None  # "predictive", "batch", or None
        self._mode_lock = asyncio.Lock()

        # Initialize batching strategy with current engine awareness
        current_engine_name = self._config_manager.get(
            "tts.preferred_engine", "edge-tts")
        # Note: At initialization, we don't have engine instance yet, so pass None
        # Engine instance will be set later when TTS integration initializes
        self.batching_strategy = FusionBatchingStrategy(
            self._config_manager, engine=None
        )

        # Sequential synthesis pointer for CPU optimization (v5.0 Reservoir Fix)
        self._next_synthesis_idx: Optional[int] = None

        # CPU optimization: Cached sanitized text storage
        self._sanitized_cache: Dict[str, Dict] = {}

        # CPU optimization: Buffered duration cache to avoid O(N) recalculation
        self._buffered_duration_cache: float = 0.0
        self._buffered_duration_cache_valid: bool = False

    def generate_playlist(self) -> None:
        """Generate TTS playlist from current content."""
        # The prepare_tts_playlist function will now populate self.playlist directly.
        with self.tts_integration.tts_lock:
            prepare_tts_playlist(self)

    def load_next_chapter(self) -> bool:
        """Load next chapter for TTS."""
        # The tts_load_next_chapter function will now operate on this manager.
        return tts_load_next_chapter(self)

    def get_current_item(self) -> Optional[PlaylistItem]:
        """Get current playlist item."""
        if 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None

    def get_item_at(self, index: int) -> Optional[PlaylistItem]:
        """Get playlist item at a specific index."""
        if 0 <= index < len(self.playlist):
            return self.playlist[index]
        return None

    def update_item_at(self, index: int, item: Tuple) -> None:
        """Update a playlist item at a specific index, e.g., with synthesized audio."""
        if 0 <= index < len(self.playlist):
            self.playlist[index] = item

    def advance_index(self) -> None:
        """Advance playlist index."""
        self.current_index += 1

        # CPU optimization: Invalidate buffered duration cache when playback advances
        self._buffered_duration_cache_valid = False

        # Phase 4: HMI Event-driven - Trigger water level check after playback consumption
        if hasattr(self, "_predictive_controller"):
            asyncio.create_task(
                self._predictive_controller.plan_and_schedule_next_trigger()
            )

    def is_exhausted(self) -> bool:
        """Check if playlist is exhausted."""
        return self.current_index >= len(self.playlist)

    def has_items(self) -> bool:
        """Check if the playlist has any items."""
        return len(self.playlist) > 0

    def get_playlist_length(self) -> int:
        """Return the total number of items in the playlist."""
        return len(self.playlist)

    def get_current_index(self) -> int:
        """Return the current playlist index."""
        return self.current_index

    def set_current_index(self, new_index: int) -> None:
        """Set current playlist index with pointer invalidation for CPU optimization.

        Args:
            new_index: New current index value
        """
        with self.tts_integration.tts_lock:
            # Invalidate cached synthesis pointer if jumping more than 1 position
            # This prevents stale pointer state during user seek operations
            if abs(new_index - self.current_index) > 1:
                logger.debug(
                    f"Index jump detected ({self.current_index} -> {new_index}), "
                    f"invalidating synthesis pointer"
                )
                self._next_synthesis_idx = None

            self.current_index = new_index

            # ✅ 新增：重置指針並強制喚醒
            # 因為用戶跳轉了，原本的合成進度可能失效，重置為當前位置
            self._next_synthesis_idx = new_index

            if hasattr(self, "_predictive_controller"):
                self._predictive_controller.wake_up_now()

    def reset(self) -> None:
        """Reset playlist and index with aggressive cleanup for engine switching."""
        # AGGRESSIVE CLEANUP: Stop all async operations immediately
        self._cancel_preload_tasks()
        self._cancel_batch_preload_task()
        self._cancel_synthesis_tasks()

        # ENGINE SWITCHING FIX: Reset all state to prevent stale data pollution
        self.playlist = []
        self.current_index = 0
        self._next_synthesis_idx = None  # v5.0 Reservoir Fix
        self._active_mode = None  # v4.0 fix
        self._keep_alive_scheduled = False
        self._sanitized_cache.clear()  # TTS ENGINE SWITCHING FIX
        self._batch_start_time = 0.0
        self._last_adjustment_time = time.time()

        # ✅ 新增：強制重置控制器狀態
        # 這解決了切換引擎後系統認為「還有任務在跑」而拒絕工作的問題
        if hasattr(self, "_predictive_controller"):
            self._predictive_controller.hard_reset()

        # ✅ 新增：記錄重設時間，用於 controller 的冷卻期檢查
        # 防止 reset() 後立即觸發 refill，避免 playlist 還沒準備好就開始合成
        self._reset_time = time.time()

        # Reset performance tracking
        self._synthesis_times.clear()

        # Reset synthesis window cache
        self._synthesis_window_cache = {
            "last_processed_idx": -1,
            "next_candidate_search": 0,
            "zone_end": 0,
            "zone_size": 50,
            "skip_zones": set(),
            "scan_calls": 0,
        }

        # Clear all queues aggressively
        while not self._playback_queue.empty():
            try:
                self._playback_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        logger.debug(
            "Playlist manager reset completed with aggressive cleanup")

    def _cancel_preload_tasks(self) -> None:
        """Cancel all ongoing preload tasks."""
        for task in self._preload_tasks:
            if not task.done():
                task.cancel()
        self._preload_tasks.clear()

    def _cancel_batch_preload_task(self) -> None:
        """Cancel the batch preload task if running."""
        if self._batch_preload_task and not self._batch_preload_task.done():
            self._batch_preload_task.cancel()
            self._batch_preload_task = None

    def _cancel_synthesis_tasks(self) -> None:
        """Cancel all ongoing synthesis tasks."""
        for task in self._synthesis_tasks:
            if not task.done():
                task.cancel()
        self._synthesis_tasks.clear()

    async def start_preload_task(self) -> None:
        """Start an asynchronous preload task for the next unsynthesized item."""
        async with self._preload_lock:
            # Check if we already have too many tasks
            self._cleanup_completed_tasks()
            if len(self._preload_tasks) >= 2:  # Limit concurrent preload tasks
                return

            # Find the next item that needs synthesis
            target_index = -1
            text_to_synthesize = None

            with self.tts_integration.tts_lock:
                current_idx = (
                    self.get_current_index()
                )  # noqa: F841 # Reserved for debugging
                limit = min(self.get_playlist_length(), current_idx + 3)
                for i in range(current_idx, limit):
                    item = self.get_item_at(i)
                    if item and len(item) == 2:  # Unynthesized item
                        text_to_synthesize = item[0]
                        target_index = i
                        break

            if text_to_synthesize and self.app.tts_engine:
                # Create preload task
                task = asyncio.create_task(
                    self._preload_synthesis(target_index, text_to_synthesize)
                )
                self._preload_tasks.append(task)
                logger.debug(f"Started preload task for index {target_index}")

    async def _preload_synthesis(self, target_index: int, text: str) -> None:
        """Asynchronously preload synthesis for a specific item."""
        try:
            # Check if content is speakable
            from speakub.utils.text_utils import is_speakable_content

            speakable, reason = is_speakable_content(text)
            if not speakable:
                logger.info(
                    f"Skipping non-speakable content in preload (reason: {reason})"
                )
                with self.tts_integration.tts_lock:
                    item = self.get_item_at(target_index)
                    if item and len(item) == 2:
                        new_item = (item[0], item[1], b"CONTENT_FILTERED")
                        self.update_item_at(target_index, new_item)
                return

            # Perform synthesis
            rate_str = f"{self.app.tts_rate:+}%"
            volume_str = f"{self.app.tts_volume - 100:+}%"
            from speakub.utils.text_utils import correct_chinese_pronunciation

            corrected_text = correct_chinese_pronunciation(text)

            # Add delay to prevent rate limiting
            from speakub.utils.config import get_smooth_synthesis_delay

            current_engine = self._config_manager.get(
                "tts.preferred_engine", "edge-tts"
            )
            synthesis_delay = get_smooth_synthesis_delay(current_engine)
            await asyncio.sleep(synthesis_delay)

            # Synthesize audio
            if self.app.tts_engine and hasattr(self.app.tts_engine, "synthesize"):
                audio_data = await self.app.tts_engine.synthesize(
                    corrected_text,
                    rate=rate_str,
                    volume=volume_str,
                    pitch=self.app.tts_pitch,
                )
            else:
                logger.warning("TTS engine does not support synthesis")
                return

            if audio_data and audio_data != b"ERROR":
                with self.tts_integration.tts_lock:
                    item = self.get_item_at(target_index)
                    if item and len(item) == 2:
                        new_item = (item[0], item[1], audio_data)
                        self.update_item_at(target_index, new_item)
                logger.debug(
                    f"Preloaded synthesis completed for index {target_index}")
            else:
                logger.warning(
                    f"Preload synthesis failed for index " f"{target_index}")

        except asyncio.CancelledError:
            logger.debug(f"Preload task cancelled for index {target_index}")
            raise
        except Exception as e:
            logger.error(
                f"Error in preload synthesis for index {target_index}: {e}")

    def _cleanup_completed_tasks(self) -> None:
        """Remove completed tasks from the task list."""
        self._preload_tasks = [
            task for task in self._preload_tasks if not task.done()]

    async def start_batch_preload(self) -> None:
        """Start batch preloading of TTS items with mode lock protection."""
        async with self._mode_lock:
            # Allow execution to detect any potential Fusion interference through normal logs

            # v4.0 fix: Prevent dual mode activation
            if self._active_mode is not None:
                logger.debug(
                    f"Mode already active ({self._active_mode}), skipping start_batch_preload"
                )
                return

            preloading_mode = self._config_manager.get(
                "tts.preloading_mode", "predictive"
            )
            original_mode = preloading_mode  # Track original setting for logging
            current_engine = self._config_manager.get(
                "tts.preferred_engine", "edge-tts"
            )

            # Predictive mode requires smooth mode to be enabled AND engine to support it
            engine_supports_smooth = current_engine in [
                "edge-tts",
                "nanmai",
            ]  # gTTS doesn't support smooth mode

            if preloading_mode == "predictive" and (
                not self.app.tts_smooth_mode or not engine_supports_smooth
            ):
                if not self.app.tts_smooth_mode:
                    logger.warning(
                        "Predictive preloading mode requires smooth mode to be enabled. Falling back to batch mode."
                    )
                elif not engine_supports_smooth:
                    logger.warning(
                        f"Predictive preloading mode is not supported for {current_engine} engine. Falling back to batch mode."
                    )
                preloading_mode = "batch"

            if preloading_mode == "predictive":
                # Use predictive batch controller
                await self._predictive_controller.start_monitoring()
                self._active_mode = "predictive"
                logger.info(
                    f"Started predictive batch controller (configured: {original_mode})"
                )
                # Manually trigger the first batch to kickstart the predictive chain.
                asyncio.create_task(
                    self._predictive_controller._trigger_new_batch())
            elif preloading_mode == "batch":
                # Use optimized batch preloading
                if self._batch_preload_task and not self._batch_preload_task.done():
                    logger.debug("Batch preload task already active, skipping")
                    return

                self._batch_preload_task = asyncio.create_task(
                    self._batch_preload_worker()
                )
                self._active_mode = "batch"
                logger.info(
                    f"Started batch preload worker (fallback from: {original_mode})"
                )
            else:
                logger.debug("Batch preloading disabled")

    async def _batch_preload_worker(self) -> None:
        """Worker task for batch preloading."""
        try:
            while not self.tts_integration.tts_stop_requested.is_set():
                # Get batch of items to preload
                batch_items = await self._get_next_batch()

                # If there are items, process them. If not, wait for the next trigger.
                if batch_items:
                    await self._process_batch(batch_items)
                else:
                    # No re-triggering logic here. The controller is responsible.
                    # A short sleep prevents busy-waiting in edge cases.
                    await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            logger.debug("Batch preload worker cancelled")
            raise
        except Exception as e:
            logger.error(f"Error in batch preload worker: {e}")

    async def _schedule_next_check_if_needed(self, was_empty_batch: bool):
        """確保控制器持續監視，即使當前沒有項目"""
        if was_empty_batch and hasattr(self, "_predictive_controller"):
            # 即使延遲檢查沒有項目，也要讓控制器保持活躍狀態
            # 這樣預載就不會停止，而是持續循環
            logger.debug(
                "Scheduling keep-alive check to maintain continuous monitoring"
            )
            asyncio.create_task(
                self._predictive_controller.plan_and_schedule_next_trigger(
                    0.5)  # 短延遲檢查
            )

    async def _get_next_batch(self) -> List[Tuple[int, str]]:
        """Get next batch of items that need synthesis using Optimal Cut-point Batching for smooth mode engines."""
        # Check if optimal batching should be used
        if self._should_use_optimal_batching():
            return await self._get_next_batch_optimal()
        else:
            return []

    def _should_use_optimal_batching(self) -> bool:
        """Check if optimal batching should be used for current engine."""
        smooth_mode = self._config_manager.get("tts.smooth_mode", False)

        # Always use Fusion in smooth mode if enabled
        if smooth_mode:
            fusion_enabled = self._config_manager.get(
                "tts.fusion.enabled", True)
            logger.debug(
                f"Fusion batching check: smooth_mode={smooth_mode}, fusion_enabled={fusion_enabled}"
            )
            return fusion_enabled

        # Non-smooth mode: optimal batching disabled - simplified logic
        return False

    def _has_synthesis_work_remaining(self) -> bool:
        """Check if there's remaining synthesis work using sequential pointer (CPU optimization).

        In smooth mode with supported engines, this delegates to intelligent content validation
        that excludes content likely to be filtered as non-speakable.
        """
        # In smooth mode, use the intelligent version that considers content filtering
        if hasattr(self, "app") and self.app.tts_smooth_mode:
            return self._has_valid_synthesis_work_remaining()

        # For all other cases (non-smooth mode, legacy code, etc.), use the basic check
        with self.tts_integration.tts_lock:
            # Initialize pointer if not set
            if self._next_synthesis_idx is None:
                self._find_next_synthesis_position()

            # If pointer is None or exceeds playlist, no work remains
            if (
                self._next_synthesis_idx is None
                or self._next_synthesis_idx >= self.get_playlist_length()
            ):
                return False

            return True

    def _has_valid_synthesis_work_remaining(self) -> bool:
        """
        [Smooth Mode State Fix] 檢查除了會被內容篩選過濾掉的項目之外，
        是否還有真正需要合成的有效工作。

        解決問題：在TTS引擎切換後，smooth模式播放可能遇到buffer underrun，
        因為系統等待不會出現的合成內容。
        """
        with self.tts_integration.tts_lock:
            # 只在smooth模式才進行這個特殊檢查
            if not self.app.tts_smooth_mode:
                return self._has_synthesis_work_remaining()

            # 初始化指針
            if self._next_synthesis_idx is None:
                self._find_next_synthesis_position()

            if self._next_synthesis_idx is None:
                return False

            # 遍歷從指針位置開始的所有項目
            playlist_length = self.get_playlist_length()
            checked_items = 0
            filtered_items = 0

            for i in range(self._next_synthesis_idx, playlist_length):
                item = self.get_item_at(i)
                if item and len(item) == 2:  # 找到未合成的項目
                    text_content = item[0]
                    checked_items += 1

                    # 檢查這個內容是否會被TTS引擎接受
                    try:
                        from speakub.utils.text_utils import is_speakable_content

                        speakable, reason = is_speakable_content(text_content)

                        if speakable:
                            # 找到真正需要合成的內容 - 減少Log頻率，只在找到時記錄
                            if checked_items > 1:  # 只在檢查了多個項目後才記錄
                                logger.debug(
                                    f"Smooth mode: Found valid synthesis work at index {i} "
                                    f"(after checking {checked_items} items, filtered {filtered_items})"
                                )
                            return True
                        else:
                            # 內容會被跳過
                            filtered_items += 1
                            # 內容會被跳過，繼續檢查下一個
                            continue
                    except Exception as e:
                        logger.warning(
                            f"Smooth mode: Error checking content at index {i}: {e}, "
                            f"assuming it's valid work"
                        )
                        return True

            # 沒有找到任何有效內容 - 減少Log頻率，只在實際檢查了項目時記錄
            if checked_items > 0:
                logger.debug(
                    f"Smooth mode: No valid synthesis work found "
                    f"(checked {checked_items} items, all filtered)"
                )
            return False

    def _find_next_synthesis_position(self) -> None:
        """Find the next position that needs synthesis and set the pointer (CPU optimization)."""
        with self.tts_integration.tts_lock:
            playlist_length = self.get_playlist_length()

            # Synthesize from current position forward
            for i in range(self.current_index, playlist_length):
                item = self.get_item_at(i)
                if item and len(item) == 2:  # Found unsynthesized item
                    self._next_synthesis_idx = i
                    logger.debug(
                        f"Sequential synthesis pointer set to index {i}")
                    return

            # No work found
            self._next_synthesis_idx = None
            logger.debug("No synthesis work remaining, cleared pointer")

    def _detect_chapter_boundaries_in_range(
        self, start_idx: int, end_idx: int
    ) -> List[int]:
        """
        檢測指定範圍內的章節邊境。

        Args:
            start_idx: 起始索引
            end_idx: 結束索引

        Returns:
            章節邊境索引列表
        """
        boundaries = []

        # 章節標記模式
        chapter_patterns = [
            r"^第[一二三四五六七八九十\d]+章",
            r"^Chapter\s+\d+",
            r"^CHAPTER\s+\d+",
            r"^\d+\.\s+",
            r"^[IVXLCDM]+\.\s+",  # 羅馬數字
        ]

        import re

        for i in range(start_idx, end_idx):
            item = self.get_item_at(i)
            if not item or len(item) < 2:
                continue

            text = item[0].strip()
            if not text:
                continue

            # 檢查是否匹配章節模式
            for pattern in chapter_patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    boundaries.append(i)
                    break

            # 額外檢查：非常短的內容後跟較長內容，可能表示章節轉換
            if i > start_idx and i < end_idx - 1 and len(text) < 20:
                # 檢查前一個項目是否也很短
                prev_item = self.get_item_at(i - 1)
                if prev_item and len(prev_item) >= 2 and len(prev_item[0].strip()) < 30:
                    boundaries.append(i)

        return boundaries

    def _get_engine_target_chars(self) -> int:
        """Get target character count for current engine."""
        current_engine = self._config_manager.get(
            "tts.preferred_engine", "edge-tts")
        targets = self._config_manager.get(
            "tts.optimal_batching.target_batch_chars", {
                "edge-tts": 60, "nanmai": 40}
        )
        return targets.get(current_engine, 60)

    async def _get_next_batch_optimal(self) -> List[Tuple[int, str]]:
        """Reservoir v5.0: 狀態指針驅動的批次選擇，完全消除 CPU 空轉"""

        # 檢查 Fusion 是否啟用
        if not self._config_manager.get("tts.fusion.enabled", True):
            logger.debug("Fusion disabled, using simplified batching logic")
            # Return empty list for non-smooth mode
            return []

        current_queue_size = self._playback_queue.qsize()

        # Apply backpressure: don't preload if queue is too full
        if current_queue_size >= self._max_queue_size:
            logger.debug(
                f"Queue full ({current_queue_size}/{self._max_queue_size}), skipping preload"
            )
            return []

        with self.tts_integration.tts_lock:
            playlist_length = self.get_playlist_length()
            current_idx = self.get_current_index()

            # 🔄 Reservoir v5.0 核心改進：完全使用狀態指針驅動，避免跳躍式掃描
            # 初始化指針如果需要 - 非干擾式，僅在必要時設置
            if self._next_synthesis_idx is None:
                self._find_next_synthesis_position()

            # ✅ 新增 1. 本地跳過 (Local Skip)：徹底清理已處理項目
            with self.tts_integration.tts_lock:
                playlist_length = self.get_playlist_length()

            # Safety initialization
            if (
                self._next_synthesis_idx is None
                or self._next_synthesis_idx < self.current_index
            ):
                self._next_synthesis_idx = self.current_index

            # ✅ 新增 2. 本地追趕 (Local Catch-up)：跳過已處理項目
            while self._next_synthesis_idx < playlist_length:
                item = self.get_item_at(self._next_synthesis_idx)
                # 如果項目已合成 (長度為3) 或被過濾，就跳過
                if (
                    item
                    and len(item) >= 3
                    and (len(item) == 3 or item[2] == b"CONTENT_FILTERED")
                ):
                    self._next_synthesis_idx += 1
                else:
                    break  # 找到了真正的未處理項目

            # 🔧 Nanmai 模式修復：確保指針不會超出播放清單長度
            # 當所有項目都已處理完畢時，指針會等於 playlist_length
            if self._next_synthesis_idx >= playlist_length:
                logger.debug(
                    f"Nanmai mode: All items processed, pointer at {self._next_synthesis_idx} >= playlist_length {playlist_length}"
                )
                return []

            # 檢查指針是否有效
            if (
                self._next_synthesis_idx is None
                or self._next_synthesis_idx >= playlist_length
            ):
                logger.debug(
                    "Reservoir: No synthesis work remaining, pointer cleared")
                return []

            # 🎯 關鍵優化：直接從指針位置開始收集候選項目
            # 從指針開始向前收集連續的未合成項目作為候選
            candidates = []
            # [Optimization 2] 啟用硬體感知限制
            # 基礎收集限制為 20，但在低階設備上會自動降低
            base_limit = 20
            hardware_aware_limit = self._get_hardware_aware_batch_limit(
                base_limit)
            collect_limit = min(
                hardware_aware_limit, playlist_length - self._next_synthesis_idx
            )

            for i in range(
                self._next_synthesis_idx,
                min(playlist_length, self._next_synthesis_idx + collect_limit),
            ):
                item = self.get_item_at(i)
                if item and len(item) == 2:  # 未合成項目
                    candidates.append((i, item[0]))
                    # 只記錄前3個以減少日志
                    if len(candidates) <= 3:
                        logger.debug(
                            f"  Pointer candidate at {i}: '{item[0][:20]}...' ({len(item[0])} chars)"
                        )
                else:
                    # 遇到已合成的項目，停止收集（因為指針應該指向第一個未合成項目）
                    break

            # Reduce verbose logging - only log every 10th batch to avoid log spam
            if self._batch_start_time and (time.time() - self._batch_start_time) > 10:
                logger.debug(
                    f"Pointer-driven collection: from_idx={self._next_synthesis_idx}, "
                    f"collected {len(candidates)} candidates, queue_size={current_queue_size}/{self._max_queue_size}"
                )

            if not candidates:
                return []

            # 📈 使用批次策略選擇最佳批次
            # 注意：END_OF_CHAPTER_MODE 的檢測已經在 fusion_reservoir.controller 中實現
            selected, strategy_name = self.batching_strategy.select_batch(
                candidates
            )

            selected_chars = sum(len(text) for _, text in selected)
            # Reduce Fusion strategy logging frequency
            if len(selected) > 0:  # Only log when actually selecting items
                logger.debug(
                    f"Fusion strategy '{strategy_name}': {len(candidates)} candidates -> {len(selected)} selected "
                    f"({selected_chars} chars)"
                )

            # 簡單的指針推進邏輯 - 只推進到選中項目的結尾之後
            if selected:
                selected_indices = sorted([idx for idx, _ in selected])
                last_selected_idx = max(selected_indices)
                self._next_synthesis_idx = last_selected_idx + 1
                logger.debug(
                    f"Pointer advanced to {self._next_synthesis_idx} after batch selection "
                    f"({len(selected)} items processed)"
                )
            elif candidates:
                # 如果有候選人但未選擇任何項目，推進到候選人結尾以避免無限迴圈
                last_candidate_idx = max(idx for idx, _ in candidates)
                self._next_synthesis_idx = last_candidate_idx + 1
                logger.warning(
                    f"Batch strategy selected no items from {len(candidates)} candidates "
                    f"(strategy: {strategy_name}). Advanced pointer to {self._next_synthesis_idx} to prevent infinite loop."
                )

            return selected

    def _select_optimal_combination(
        self, candidates: List[Dict], target_chars: int
    ) -> List[Dict]:
        """選擇最接近目標容量的組合 using dynamic programming knapsack algorithm"""
        if not candidates:
            return []

        n = len(candidates)  # noqa: F841 # Reserved variable
        # DP table: dp[i][j] = True if we can achieve sum j using first i items
        # We use a set to track achievable sums for memory efficiency
        achievable = {0}

        # Track which items are used for each sum
        item_usage = {}  # sum -> list of item indices

        for i, item in enumerate(candidates):
            length = item["length"]
            new_achievable = set(achievable)  # Copy current achievable sums

            for current_sum in list(achievable):
                new_sum = current_sum + length
                if new_sum not in achievable:  # Avoid duplicates
                    new_achievable.add(new_sum)
                    # Track which items led to this sum
                    if new_sum not in item_usage:
                        item_usage[new_sum] = item_usage.get(
                            current_sum, []) + [i]

            achievable = new_achievable

        # Find the sum closest to target_chars
        best_sum = 0
        min_diff = float("inf")

        for achievable_sum in achievable:
            diff = abs(achievable_sum - target_chars)
            if diff < min_diff:
                min_diff = diff
                best_sum = achievable_sum

        # Get the items that make up the best sum
        if best_sum == 0:
            # No items selected, return first item as fallback
            return [candidates[0]]

        selected_indices = item_usage.get(best_sum, [])
        selected = [candidates[i] for i in selected_indices]

        return selected

    async def _process_batch(self, batch_items: List[Tuple[int, str]]) -> None:
        """Process a batch of items using standard individual processing."""
        if not batch_items:
            return

        # 移除舊的 Nanmai 合併判斷邏輯
        # 統一使用標準處理方式 (原 _process_batch_original)
        await self._process_batch_original(batch_items)

    async def _process_batch_original(self, batch_items: List[Tuple[int, str]]) -> None:
        """Original batch processing logic for non-Nanmai engines."""
        logger.debug(
            f"Processing batch of {len(batch_items)} items (original method)")

        # Create synthesis tasks for each item
        synthesis_tasks = []
        for index, text in batch_items:
            task = self._create_synthesis_task(index, text)
            synthesis_tasks.append(task)

        # Track synthesis tasks for cleanup
        self._synthesis_tasks.extend(synthesis_tasks)

        try:
            # Process tasks individually to allow for partial completion
            for (index, text), task in zip(batch_items, synthesis_tasks):
                try:
                    result = await task
                    if isinstance(result, tuple) and len(result) == 3:
                        audio_data, duration, text_length = result
                        if audio_data is not None:
                            logger.debug(
                                f"Batch synthesis completed for index {index}")
                        else:
                            logger.warning(
                                f"Batch synthesis failed for index {index}")
                    else:
                        logger.warning(
                            f"Unexpected result for index {index}: {result}")
                except Exception as e:
                    # Check if this is a SynthesisSkipped exception (expected behavior)
                    if hasattr(e, "reason") and "Synthesis skipped" in str(e):
                        logger.debug(
                            f"Batch synthesis skipped for index {index}"
                        )
                        # CPU optimization: Invalidate buffered duration cache when content is skipped
                        self._buffered_duration_cache_valid = False
                    else:
                        logger.error(
                            f"Error in batch synthesis for index {index}: {e}")

        finally:
            # Clean up completed synthesis tasks from the tracking list
            self._synthesis_tasks = [
                task for task in self._synthesis_tasks if not task.done()
            ]



    def _create_synthesis_task(self, index: int, text: str) -> asyncio.Task:
        """Create a synthesis task for a single item."""

        async def synthesize_item():
            start_time = time.time()
            corrected_text = text  # Initialize to avoid UnboundLocalError in exception handling
            try:
                # CPU optimization: Check cache first for pre-processed text
                if text in self._sanitized_cache:
                    cached_result = self._sanitized_cache[text]
                    speakable = cached_result["speakable"]
                    sanitized_text = cached_result["sanitized"]
                    reason = cached_result.get("reason", "cached")
                else:
                    # Check if content is speakable
                    from speakub.utils.security import TextSanitizer
                    from speakub.utils.text_utils import is_speakable_content

                    speakable, reason = is_speakable_content(text)
                    if speakable:
                        sanitized_text = TextSanitizer.sanitize_tts_text(text)
                    else:
                        sanitized_text = text  # Not sanitized if not speakable

                    # Cache the result to avoid repeated processing
                    self._sanitized_cache[text] = {
                        "speakable": speakable,
                        "reason": reason,
                        "sanitized": sanitized_text,
                    }

                if not speakable:
                    logger.info(
                        f"Skipping non-speakable content at index {index} (reason: {reason})"
                    )
                    with self.tts_integration.tts_lock:
                        item = self.get_item_at(index)
                        if item and len(item) == 2:
                            new_item = (item[0], item[1], b"CONTENT_FILTERED")
                            self.update_item_at(index, new_item)

                    # 🟢 新增：即使是跳過內容，也要發出信號喚醒可能在等待的 Runner
                    self.tts_integration.tts_audio_ready.set()

                    # CPU optimization: Invalidate buffered duration cache when content is filtered
                    self._buffered_duration_cache_valid = False

                    # Return result directly instead of raising exception (following H1V8_4 pattern)
                    return None, time.time() - start_time, len(text)

                # Prepare synthesis parameters
                rate_str = f"{self.app.tts_rate:+}%"
                volume_str = f"{self.app.tts_volume - 100:+}%"
                from speakub.utils.text_utils import (
                    clean_text_for_tts,
                    correct_chinese_pronunciation,
                )

                # 1. 先清理文字 (移除 [7] 這種註腳)
                cleaned_text = clean_text_for_tts(text)

                # 2. 再修正發音
                corrected_text = correct_chinese_pronunciation(cleaned_text)

                # Add delay to prevent rate limiting
                from speakub.utils.config import get_smooth_synthesis_delay

                current_engine = self._config_manager.get(
                    "tts.preferred_engine", "edge-tts"
                )
                synthesis_delay = get_smooth_synthesis_delay(current_engine)
                await asyncio.sleep(synthesis_delay)

                # Perform synthesis
                if self.app.tts_engine and hasattr(self.app.tts_engine, "synthesize"):
                    audio_data = await self.app.tts_engine.synthesize(
                        corrected_text,
                        rate=rate_str,
                        volume=volume_str,
                        pitch=self.app.tts_pitch,
                    )

                    duration = time.time() - start_time
                    if audio_data and audio_data != b"ERROR":
                        with self.tts_integration.tts_lock:
                            item = self.get_item_at(index)
                            if item and len(item) == 2:
                                new_item = (item[0], item[1], audio_data)
                                self.update_item_at(index, new_item)

                        # 發出信號，通知播放執行緒有新音訊可用
                        self.tts_integration.tts_audio_ready.set()
                        # 同時設定 async 事件，以支援 async runner
                        self.tts_integration._async_tts_audio_ready.set()

                        # Debug logging for successful synthesis
                        logger.debug(
                            f"Debug: Successfully synthesized item at position {index}: {len(audio_data)} bytes for text '{corrected_text[:100]}{'...' if len(corrected_text) > 100 else ''}'"
                        )

                        return audio_data, duration, len(corrected_text)
                    else:
                        logger.warning(f"Synthesis failed for index {index}")
                        logger.debug(
                            f"Debug: Batch synthesis failed at position {index}, failed content: '{corrected_text[:100]}{'...' if len(corrected_text) > 100 else ''}'"
                        )
                        return None, duration, len(corrected_text)
                else:
                    logger.warning("TTS engine does not support synthesis")
                    return None, time.time() - start_time, len(text)

            except Exception as e:
                logger.error(
                    f"TTS Synthesis Error: Error synthesizing item at index {index}, content '{corrected_text[:200]}...': {str(e)}",
                    exc_info=True,
                )
                logger.debug(
                    f"Debug: Batch synthesis failed at position {index}, failed content: '{corrected_text[:100]}{'...' if len(corrected_text) > 100 else ''}'"
                )
                # Force flush file handlers to ensure error is written immediately
                for handler in logging.getLogger().handlers:
                    if isinstance(handler, logging.FileHandler):
                        handler.flush()
                # Notify user of synthesis error with simplified message
                # Since smooth mode will retry failed items automatically, we use a less alarming message
                error_msg = "網路連線問題，系統將自動重試合成"
                try:
                    self.app.notify(
                        error_msg, title="TTS 暫時中斷", severity="warning"
                    )
                except Exception as notify_error:
                    logger.warning(
                        f"Failed to notify user of synthesis error: {notify_error}"
                    )
                return None, time.time() - start_time, len(text)

        return asyncio.create_task(synthesize_item())

    def _record_synthesis_time(self, avg_time: float) -> None:
        """Record synthesis time for performance monitoring."""
        self._synthesis_times.append(avg_time)

    def _adjust_batch_size(self) -> None:
        """Dynamically adjust batch size based on synthesis performance."""
        if len(self._synthesis_times) < self._adjustment_window:
            return  # Not enough data

        current_time = time.time()
        if (
            current_time - self._last_adjustment_time < 10.0
        ):  # Adjust at most every 10 seconds
            return

        # Calculate average synthesis time
        avg_time = sum(self._synthesis_times) / len(self._synthesis_times)

        # Get engine-specific target time
        current_engine = self._config_manager.get(
            "tts.preferred_engine", "edge-tts")
        engine_targets = {
            "edge-tts": 2.0,  # Fast engine
            "nanmai": 4.0,  # Slow engine
            "gtts": 3.0,  # Medium engine
        }
        target_time = engine_targets.get(current_engine, 2.0)

        if avg_time > target_time * 1.2:  # Too slow, reduce batch size
            new_batch_size = max(1, self._batch_size - 1)
            if new_batch_size != self._batch_size:
                logger.debug(
                    f"Reducing batch size from {self._batch_size} to {new_batch_size} (avg time: {avg_time:.2f}s, target: {target_time:.1f}s)"
                )
                self._batch_size = new_batch_size
                self._last_adjustment_time = current_time

        elif avg_time < target_time * 0.8:  # Fast enough, can increase batch size
            new_batch_size = min(20, self._batch_size + 1)  # Cap at 20
            if new_batch_size != self._batch_size:
                logger.debug(
                    f"Increasing batch size from {self._batch_size} to {new_batch_size} (avg time: {avg_time:.2f}s, target: {target_time:.1f}s)"
                )
                self._batch_size = new_batch_size
                self._last_adjustment_time = current_time

    def get_queue_size(self) -> int:
        """Get current playback queue size."""
        return self._playback_queue.qsize()

    def get_buffered_duration(self) -> float:
        """
        Get the cached total estimated duration of synthesized audio in the buffer.
        Uses incremental updates to avoid O(N) recalculation on every call.
        """
        # Return cached value if valid
        if self._buffered_duration_cache_valid:
            return self._buffered_duration_cache

        # Fallback to full calculation if cache is invalid
        total_duration = 0.0
        if not hasattr(self, "_predictive_controller"):
            return 0.0

        with self.tts_integration.tts_lock:
            for i in range(self.current_index, self.get_playlist_length()):
                item = self.get_item_at(i)
                # Check if the item is synthesized (has 3 elements, and the 3rd is bytes)
                if item and len(item) == 3 and isinstance(item[2], bytes):
                    audio_data = item[2]
                    if audio_data not in (
                        b"CONTENT_FILTERED",
                        b"ERROR",
                        b"FAILED_SYNTHESIS",
                    ):
                        duration = self._predictive_controller.queue_predictor._estimate_audio_duration(
                            audio_data
                        )
                        total_duration += duration
                else:
                    # Stop counting as soon as we hit a non-synthesized item
                    break

        # Update cache
        self._buffered_duration_cache = total_duration
        self._buffered_duration_cache_valid = True

        logger.debug(
            f"Calculated buffered audio duration: {total_duration:.2f}s (cache updated)"
        )
        return total_duration

    def get_buffered_item_count(self) -> int:
        """
        [Reservoir v5.6] 計算緩衝區中已合成但尚未播放的項目數量。
        用於基於計數的觸發邏輯 (Item-based Triggering)。
        """
        count = 0
        with self.tts_integration.tts_lock:
            # 從當前播放位置開始往後算
            for i in range(self.current_index, self.get_playlist_length()):
                item = self.get_item_at(i)
                # 檢查是否已合成 (長度為3且第三個元素是bytes)
                if item and len(item) == 3 and isinstance(item[2], bytes):
                    # 排除過濾掉的內容和錯誤，只計算有效播放項目
                    # 這樣可以避免把標點符號停頓當作有效的「存糧」
                    if item[2] not in (
                        b"CONTENT_FILTERED",
                        b"ERROR",
                        b"FAILED_SYNTHESIS",
                    ):
                        count += 1
                else:
                    # 一旦遇到未合成的項目就停止計算 (連續性原則)
                    break
        return count

    def _handle_resource_pressure_event(self, event_data: Dict) -> None:
        """
        Closed-loop resource control: Handle resource pressure events and adjust batch size.
        Subscribed to 'tts_resource_pressure' events from PredictiveBatchController.
        """
        try:
            cpu_factor = event_data.get("cpu_factor", 1.0)
            memory_factor = event_data.get("memory_factor", 1.0)
            should_reduce_batch = event_data.get("should_reduce_batch", False)

            logger.debug(
                f"Resource pressure event: CPU factor={cpu_factor:.2f}, "
                f"Memory factor={memory_factor:.2f}, reduce_batch={should_reduce_batch}"
            )

            if should_reduce_batch:
                # High pressure - reduce batch size immediately
                original_batch_size = self._batch_size
                new_batch_size = max(1, self._batch_size //
                                     2)  # Halve batch size

                if new_batch_size != original_batch_size:
                    self._batch_size = new_batch_size
                    logger.info(
                        f"Closed-loop control: Reduced batch size from {original_batch_size} to {new_batch_size} "
                        f"due to high resource pressure (CPU: {cpu_factor:.2f}, Memory: {memory_factor:.2f})"
                    )

                    # Notify user if possible
                    try:
                        message = f"TTS batch size auto-adjusted to {new_batch_size} due to system resource constraints."
                        self.app.notify(
                            message, title="TTS Resource Adjustment", severity="info"
                        )
                    except Exception:
                        pass  # Ignore notification errors

            elif cpu_factor > 1.5 or memory_factor > 1.5:
                # Moderate pressure - slightly reduce batch size
                original_batch_size = self._batch_size
                new_batch_size = max(1, self._batch_size - 1)

                if new_batch_size != original_batch_size:
                    self._batch_size = new_batch_size
                    logger.debug(
                        f"Closed-loop control: Slightly reduced batch size from {original_batch_size} to {new_batch_size} "
                        f"due to moderate resource pressure"
                    )

            elif cpu_factor <= 1.2 and memory_factor <= 1.2:
                # Low pressure - can potentially increase batch size slightly
                original_batch_size = self._batch_size
                max_batch_size = self._config_manager.get(
                    "tts.max_batch_size", 20)
                new_batch_size = min(max_batch_size, self._batch_size + 1)

                if new_batch_size != original_batch_size:
                    self._batch_size = new_batch_size
                    logger.debug(
                        f"Closed-loop control: Slightly increased batch size from {original_batch_size} to {new_batch_size} "
                        f"due to low resource pressure"
                    )

        except Exception as e:
            logger.error(f"Error handling resource pressure event: {e}")

    def _handle_rate_limiting_event(self, event_data: Dict) -> None:
        """
        Handle Edge TTS rate limiting detection events.
        Automatically reduces batch size to 3-5 when rate limiting is detected.
        """
        try:
            cooldown_period = event_data.get("cooldown_period", 2.5)

            logger.warning(
                f"Rate limiting detected in Edge TTS API (cooldown: {cooldown_period}s)"
            )

            # Immediate batch size reduction for rate limiting protection
            original_batch_size = self._batch_size

            # Reduce batch size to minimum safe value (3-5 range as specified)
            if self._batch_size > 5:
                new_batch_size = 5  # Cap at 5 for rate limiting
            elif self._batch_size > 3:
                new_batch_size = 3  # Minimum safe value
            else:
                new_batch_size = self._batch_size  # Already at minimum

            if new_batch_size != original_batch_size:
                self._batch_size = new_batch_size
                logger.warning(
                    f"Rate limiting protection: Reduced batch size from {original_batch_size} to {new_batch_size} "
                    "to prevent Edge TTS service blocking"
                )

                # Notify user about the automatic adjustment
                try:
                    message = f"Edge TTS 服務速率限制已激活，系統已將批量大小調整為 {new_batch_size} 以保護服務。"
                    self.app.notify(message, title="TTS 速率限制保護",
                                    severity="warning")
                except Exception as e:
                    logger.warning(
                        f"Failed to notify user about batch size adjustment: {e}"
                    )

            else:
                logger.debug(
                    f"Batch size already at safe level ({self._batch_size}) for rate limiting protection"
                )

        except Exception as e:
            logger.error(f"Error handling rate limiting event: {e}")

    def _get_hardware_aware_batch_limit(self, requested_limit: int) -> int:
        """根據硬體效能調整批次大小限制，防止過度擴展。

        Args:
            requested_limit: 請求的限制數量

        Returns:
            根據硬體效能調整後的限制數量
        """
        try:
            # 獲取硬體效能資訊
            from speakub.utils.system_utils import get_system_performance_rating

            performance_rating = get_system_performance_rating()

            # 根據效能等級調整限制
            if performance_rating == "low_end":
                # 效能差的電腦：限制批次大小避免資源壓力
                hardware_limit = min(requested_limit, 8)
                logger.debug(
                    f"Low-end hardware detected, limiting batch to {hardware_limit}"
                )
                return hardware_limit
            elif performance_rating == "mid_range":
                # 中等效能：允許中等擴展
                hardware_limit = min(requested_limit, 12)
                return hardware_limit
            else:
                # 高階效能：允許完整擴展
                return requested_limit

        except Exception as e:
            logger.debug(
                f"Could not determine hardware limits: {e}, using requested limit"
            )
            return requested_limit

    def get_batch_size(self) -> int:
        """Get current batch size."""
        return self._batch_size

    def record_playback_event(
        self, segment_id: int, duration: float, text_length: int
    ) -> None:
        """Record a playback event for performance monitoring."""
        self._predictive_controller.record_playback_event(
            segment_id, duration, text_length
        )

    def get_preloading_stats(self) -> dict:
        """Get preloading statistics for monitoring."""
        base_stats = {
            "queue_size": self._playback_queue.qsize(),
            "batch_size": self._batch_size,
            "synthesis_times_count": len(self._synthesis_times),
            "avg_synthesis_time": sum(self._synthesis_times)
            / len(self._synthesis_times)
            if self._synthesis_times
            else 0,
            "batch_preload_active": self._batch_preload_task is not None
            and not self._batch_preload_task.done(),
        }

        # Add predictive controller stats if available
        if hasattr(self, "_predictive_controller"):
            predictive_stats = self._predictive_controller.get_performance_stats()
            base_stats.update(
                {
                    "predictive_mode": True,
                    "predictive_state": predictive_stats.get("state"),
                    "predictive_active": predictive_stats.get("monitor_active"),
                    "trigger_count": predictive_stats.get("trigger_count"),
                    "play_monitor_stats": predictive_stats.get("play_monitor_stats"),
                }
            )

        # Add batching strategy decision monitoring stats
        if hasattr(self, "batching_strategy"):
            monitor = self.batching_strategy.get_decision_monitor()
            base_stats["batching_decisions"] = monitor.get_statistics()

        return base_stats

    def notify_engine_switched(self, new_engine) -> None:
        """
        通知 PlaylistManager 引擎已切換，更新批次策略參數。

        Args:
            new_engine: 新的 TTS 引擎實例 (TTSEngine)
        """
        # Update current engine
        self.current_engine = new_engine

        if hasattr(self, "batching_strategy"):
            self.batching_strategy.set_engine(new_engine)
            engine_name = getattr(
                new_engine, '__class__', lambda: 'Unknown').__name__ if new_engine else "Unknown"
            logger.info(
                f"PlaylistManager: Batching strategy updated for {engine_name}")

    def get_batching_statistics(self) -> Dict[str, Any]:
        """
        獲取批次決策統計信息，用於性能分析。

        Returns:
            包含決策分佈、平均批次大小等信息的字典
        """
        if hasattr(self, "batching_strategy"):
            monitor = self.batching_strategy.get_decision_monitor()
            return monitor.get_statistics()
        return {"error": "Batching strategy not available"}
