#!/usr/bin/env python3
"""
Simple Reservoir Controller (Reservoir v7.0 Lightweight)

這是一個極簡化的水位控制器，旨在取代過度工程化的 v6.0 架構。
核心理念：
1. 放棄基於數量的批次 (Batch Size)，改用基於時間的目標積累 (Target Duration)。
2. 移除獨立的資源/網絡監控，依賴簡單的迴圈和歷史平均。
3. 徹底解決「短句連發」導致的緩衝時間不足問題。
"""

from speakub.utils.config import ConfigManager
import asyncio
import logging
import time
from collections import deque
from typing import Deque, Tuple, Union, Optional

# Type alias for audio data types
AudioData = Union[bytes, str]


logger = logging.getLogger(__name__)

# 添加 mutagen 支持以支援 MP3 持續時間計算
_mutagen_available = False
try:
    from mutagen.mp3 import MP3  # noqa: F401
    _mutagen_available = True
    logger.debug(
        "Controller: mutagen loaded for MP3 duration calculation")
except ImportError:
    logger.debug(
        "Controller: mutagen unavailable, using fallback estimation")


# --- 兼容性 Stub ---
class DummyMonitor:
    """用於保持與舊代碼的兼容性 (如 record_synthesis 调用)"""

    def record_synthesis(self, *args, **kwargs): pass


class DummyPredictor:
    """用於保持與舊代碼的兼容性 (如 estimate_audio_duration 调用)"""

    def _estimate_audio_duration(self, audio_data) -> float:
        if not audio_data or not isinstance(audio_data, bytes):
            return 0.0
        # 粗略估算: 16KB/s (128kbps MP3)
        return len(audio_data) / 16000.0


class SimpleReservoirController:
    """
    輕量級 Reservoir 控制器
    負責監控 TTS 播放緩衝區水位，並在水位過低時觸發合成。
    """

    def __init__(self, playlist_manager, config_manager: Optional[ConfigManager] = None):
        self.pm = playlist_manager
        self.config = config_manager or ConfigManager()

        # --- 改進 1️⃣：動態心跳參數 ---
        # 活躍播放時的心跳間隔（秒）
        self._active_heartbeat = self.config.get(
            "tts.reservoir.active_heartbeat", 0.5)
        # 閒置時的心跳間隔（秒）
        self._idle_heartbeat = self.config.get(
            "tts.reservoir.idle_heartbeat", 5.0)

        # --- 改進 2️⃣：引擎基礎語速 ---
        # 各引擎的基礎字/秒速率
        self._engine_base_speeds = self.config.get(
            "tts.reservoir.engine_base_speeds",
            {
                "edge-tts": 3.5,   # 合成快
                "nanmai": 2.5,     # 合成較慢
            }
        )
        # 正確讀取嵌套的 TTS 配置
        tts_config = self.config.get("tts", {})
        self._current_engine = tts_config.get("preferred_engine", "edge-tts")

        # --- 改進 3️⃣：引擎特定水位參數 ---
        # 各引擎的水位配置
        self._watermark_profiles = self.config.get(
            "tts.reservoir.watermark_profiles",
            {
                "edge-tts": {"LOW": 12.0, "HIGH": 40.0, "TARGET": 18.0},
                "nanmai": {"LOW": 20.0, "HIGH": 60.0, "TARGET": 25.0},
            }
        )
        # 初始化為設定檔中的引擎配置（靜默應用，不顯示日誌）
        self._apply_watermarks_for_engine(self._current_engine, show_log=False)

        # --- 歷史記錄 (用於簡單估算) ---
        # 記錄 (char_count, seconds)
        self.play_history: Deque[Tuple[int, float]] = deque(maxlen=50)

        # --- 兼容性屬性 ---
        self.queue_predictor = DummyPredictor()
        self._synth_monitor = DummyMonitor()

        # --- 定時器模式狀態 ---
        self._pending_batch_trigger: Optional[asyncio.Task] = None  # 當前定時器任務
        self._current_batch_playing = False  # 是否有批次正在播放

        # --- 狀態控制 ---
        self.running = False
        self._monitor_task = None
        self._is_triggering = False  # 防止重入鎖
        self._chapter_exhausted = False  # 章節耗盡標記

        logger.info(
            f"SimpleReservoir initialized (Timer Mode): "
            f"active_heartbeat={self._active_heartbeat}s, "
            f"idle_heartbeat={self._idle_heartbeat}s, "
            f"preferred_engine={self._current_engine}, "
            f"watermarks({self._current_engine}): "
            f"LOW={self.LOW_WATERMARK:.1f}s, "
            f"HIGH={self.HIGH_WATERMARK:.1f}s, "
            f"TARGET={self.TARGET_BATCH_DURATION:.1f}s"
        )

    async def start_monitoring(self):
        """啟動監控循環"""
        if self.running:
            return

        self.running = True
        self._monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("Reservoir monitoring started")

    async def stop_monitoring(self):
        """停止監控循環"""
        self.running = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None
        logger.info("Reservoir monitoring stopped")

    # 兼容性接口：允許 PlaylistManager 調用 (雖然在新邏輯中可能不需要)
    def pause_scheduling(self): pass
    def resume_scheduling(self): pass
    async def plan_and_schedule_next_trigger(self, delay: float = 1.0): pass

    def subscribe_to_idle_mode(self, app): pass

    async def _trigger_new_batch(self, recursive=False, recursion_depth=0):
        """兼容性方法：觸發新批次"""
        await self._trigger_batch_refill()

    async def _monitor_loop(self):
        """核心監控循環：檢查水位 → 決策 → 精確定時休眠"""
        while self.running:
            try:
                # 檢查 smooth mode - 只在 smooth mode 下執行水位控制
                if not getattr(self.pm.app, 'tts_smooth_mode', False):
                    await asyncio.sleep(self._idle_heartbeat)
                    continue

                # 1. 根據播放狀態決策心跳間隔
                is_active = self._should_check_water_level()
                heartbeat = self._active_heartbeat if is_active else self._idle_heartbeat

                # 2. 記錄預期喚醒時間（絕對時間校正）
                expected_wake_time = asyncio.get_event_loop().time() + heartbeat

                # 3. 如果活躍，執行水位檢查和補水
                if is_active:
                    await self._check_and_refill()

                # 4. 計算實際延遲時間，考慮 Event Loop 負載進行校正
                actual_delay = max(0, expected_wake_time -
                                   asyncio.get_event_loop().time())
                await asyncio.sleep(actual_delay)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Reservoir monitor error: {e}", exc_info=True)
                await asyncio.sleep(5.0)  # 錯誤後冷卻

    def _should_check_water_level(self) -> bool:
        """判斷是否需要檢查水位"""
        # 如果正在合成中，暫時不檢查，避免重複觸發
        if self._is_triggering:
            return False

        # 如果章節已耗盡，不需要再檢查水位
        if self._chapter_exhausted:
            return False

        # 冷卻期檢查：reset() 後的 150ms 內不檢查
        # 防止 reset 清空 playlist 後立即觸發 refill，給新 playlist 時間準備
        if hasattr(self.pm, '_reset_time'):
            elapsed = time.time() - self.pm._reset_time
            if elapsed < 0.15:  # 150ms 冷卻期
                return False

        # 只有在 TTS 播放中或準備播放時才工作
        app = getattr(self.pm, "app", None)
        if app and hasattr(app, "tts_status"):
            return app.tts_status in ["PLAYING", "LOADING"]

        return False

    async def _check_and_refill(self):
        """檢查水位並執行補水邏輯"""
        buffer_duration = self._calculate_buffer_duration()

        # Hysteresis (遲滯) 邏輯
        if buffer_duration < self.LOW_WATERMARK:
            logger.debug(
                f"Low water ({buffer_duration:.1f}s < {self.LOW_WATERMARK}s). Triggering refill.")
            await self._trigger_batch_refill()

        elif buffer_duration > self.HIGH_WATERMARK:
            # 水位過高，依賴心跳循環自然降低
            pass

    def _calculate_buffer_duration(self) -> float:
        """輕量級緩衝區持續時間估算 (秒)

        快速估算當前緩衝區總持續時間，用於水位決策。
        不使用 mutagen 避免頻繁 I/O，而是用簡單的檔案大小/比特率估算。
        mutagen 只在合成優化階段用於分析實際播放時間。
        """
        total_duration = 0.0
        current_idx = self.pm.get_current_index()
        playlist_len = self.pm.get_playlist_length()

        # 優化：只掃描接下來的 N 個項目，避免 playlist 過長時的效能問題
        scan_limit = min(current_idx + 50, playlist_len)

        for i in range(current_idx, scan_limit):
            item = self.pm.get_item_at(i)

            # 檢查項目格式: (text, line_num, audio_bytes)
            if item and len(item) == 3:
                audio_data = item[2]
                if isinstance(audio_data, bytes):
                    if audio_data in [b"CONTENT_FILTERED", b"ERROR"]:
                        continue

                    # 輕量級估算: 檔案大小 / 估算比特率
                    # 假設 128kbps MP3 = 約 16KB/s
                    total_duration += len(audio_data) / 16000.0

            elif item and len(item) == 2:
                # 遇到未合成的項目，緩衝區計算中斷 (連續性原則)
                break

        return total_duration

    async def _trigger_batch_refill(self):
        """收集並處理批次，然後使用精確持續時間優化下一次水位"""
        if self._is_triggering:
            return

        self._is_triggering = True
        try:
            # 🔧 **第一階段 - 收集候選項目**
            candidates = self._collect_candidates()

            if not candidates:
                logger.debug("No synthesis candidates found")
                return

            # 🏛️ **第二階段 - 決定批次策略**
            # 檢查是否在章節末端（只用於決定是否全選）
            is_at_end_of_chapter = self._check_end_of_chapter()

            batch_items = []
            strategy_name = None

            # 如果在末端，全選所有候選項目（END_OF_CHAPTER_MODE）
            if is_at_end_of_chapter:
                batch_items = [(idx, txt) for idx, txt in candidates]
                strategy_name = "END_OF_CHAPTER_MODE"
                # 標記章節已耗盡，之後不再檢查水位
                self._chapter_exhausted = True
                logger.info(
                    "End of chapter reached. Reservoir locked until next chapter.")
                logger.debug(
                    f"At chapter end: selecting all {len(batch_items)} candidates (END_OF_CHAPTER_MODE)"
                )
            elif hasattr(self.pm, 'batching_strategy') and self.pm.batching_strategy:
                # 不在末端：使用 batching_strategy 智慧選擇
                result = self.pm.batching_strategy.select_batch(candidates)

                # ⚠️ 防御性檢查：select_batch 可能返回 None
                if result is None:
                    logger.debug(
                        "Batching strategy returned None, using fallback")
                    batch_items = candidates[:5]  # 後備：選前 5 個
                    strategy_name = "FALLBACK_STRATEGY_NONE"
                else:
                    selected_items, strategy_name = result
                    batch_items = [(idx, txt) for idx,
                                   txt in selected_items] if selected_items else []

                    if not batch_items:
                        # 策略選不出任何項目 → 返回
                        if len(candidates) > 0:
                            logger.debug(
                                f"Batching strategy selected no items from {len(candidates)} candidates")
                        return
            else:
                # 沒有 batching_strategy，使用後備邏輯
                batch_items = candidates[:5]  # 最多選5個
                strategy_name = "FALLBACK"
                logger.warning(
                    "No batching strategy available, using fallback selection")

            # 記錄日誌
            if batch_items:
                total_chars = sum(len(txt) for _, txt in batch_items)
                char_limit = getattr(self.pm.batching_strategy, 'char_limit',
                                     'N/A') if hasattr(self.pm, 'batching_strategy') else 'N/A'
                estimated_duration = sum(
                    self._estimate_play_duration(txt) for _, txt in batch_items)

                logger.debug(
                    f"Fusion strategy '{strategy_name}': {len(candidates)} candidates -> {len(batch_items)} selected items "
                    f"({total_chars} chars, char_limit={char_limit}, ~{estimated_duration:.1f}s)"
                )

            # 記錄批次開始前的指標
            pre_batch_target = self.TARGET_BATCH_DURATION

            # 調用 PlaylistManager 的處理方法 (這是與舊系統的對接點)
            await self.pm._process_batch(batch_items)

            # 處理後，使用精確持續時間優化下一次水位設定
            await self._optimize_watermarks_from_recent_batch(
                pre_batch_target, len(batch_items))

        except Exception as e:
            logger.error(f"Error triggering batch refill: {e}")
        finally:
            self._is_triggering = False

    def _check_end_of_chapter(self) -> bool:
        """檢查是否在章節末端

        🏛️ **只用於決定是否全選，不干涉其他模式**
        - 只在末端時觸發 END_OF_CHAPTER_MODE 全選
        - 不影響 PARAGRAPH_MODE, SHORT_CONTENT_MODE, LONG_PARAGRAPH_MODE
        """
        try:
            if hasattr(self.pm, 'app') and self.pm.app and hasattr(self.pm.app, 'viewport_content'):
                if self.pm.app.viewport_content:
                    viewport_info = self.pm.app.viewport_content.get_viewport_info()
                    current_page = viewport_info.get('current_page', -1)
                    total_pages = viewport_info.get('total_pages', 0)

                    # 末端判定：接近最後一頁（最後一頁或倒數第二頁）
                    if total_pages > 0 and current_page >= total_pages - 2:
                        return True
        except Exception as e:
            logger.debug(f"Failed to check end of chapter: {e}")

        return False

    def _collect_candidates(self):
        """收集候選項目，交由 batching_strategy 決定最終批次

        🏛️ **邏輯**:
        - 從當前指針開始掃描，直到末尾
        - 返回所有未合成項目，讓 batching_strategy 決定選多少
        - 不人為限制候選項目數量
        """
        candidates = []

        current_idx = self.pm.get_current_index()
        playlist_len = self.pm.get_playlist_length()

        # 如果列表為空，返回空
        if playlist_len == 0:
            return candidates

        # 掃描整個剩餘 playlist，收集所有未合成項目
        for i in range(current_idx, playlist_len):
            item = self.pm.get_item_at(i)
            if item and len(item) == 2:  # len==2 表示未合成 (text, duration)
                candidates.append((i, item[0]))

        return candidates

    def _collect_batch_items(self):
        """貪婪式收集項目直到滿足 TARGET_BATCH_DURATION"""
        batch = []
        accumulated_duration = 0.0

        current_idx = self.pm.get_current_index()
        playlist_len = self.pm.get_playlist_length()

        # 掃描指針：從 PlaylistManager 的指針開始，或者從當前播放位置開始
        # 為了簡單與健壯性，我們從當前位置往後掃描尋找第一個未合成的
        scan_idx = current_idx

        # 安全限制：一次最多抓取 50 個項目，防止極端情況 (如整本書都是單字)
        MAX_ITEMS_LIMIT = 50

        for i in range(scan_idx, playlist_len):
            item = self.pm.get_item_at(i)

            # 找到未合成項目 (len == 2)
            if item and len(item) == 2:
                text = item[0]
                # 估算這個文本的時長
                duration = self._estimate_play_duration(text)

                batch.append((i, text))
                accumulated_duration += duration

                # 如果累積時長已達標，停止收集
                if accumulated_duration >= self.TARGET_BATCH_DURATION:
                    break

                # 如果項目數量過多，強制停止
                if len(batch) >= MAX_ITEMS_LIMIT:
                    logger.debug("Hit max item limit for batch")
                    break

            # 如果遇到已合成項目，我們繼續往後找嗎？
            # 是的，因為可能是插在中間的未合成項目 (雖然少見)
            # 但為了效率，如果 batch 已經非空，遇到已合成項目可以考慮停止
            # 這裡保持簡單：繼續掃描直到隊列末尾或達標

        return batch

    async def _optimize_watermarks_from_recent_batch(self, pre_batch_target: float, pre_batch_size: int):
        """使用最近批次的精確持續時間來優化水位設定

        分析最近合成的項目，計算實際 vs 估算的準確度比，
        並據此調整 TARGET_BATCH_DURATION 使未來批次更準確。
        """
        if not _mutagen_available:
            return

        try:
            # 分析最近批次的實際持續時間
            current_idx = self.pm.get_current_index()
            batch_actual_duration = 0.0
            items_found = 0

            # 掃描最近的項目，尋找新合成的音訊
            # 檢查當前播放位置之後的項目 (這些是最可能新合成的)
            scan_end = min(current_idx + pre_batch_size +
                           5, self.pm.get_playlist_length())

            for check_idx in range(current_idx, scan_end):
                item = self.pm.get_item_at(check_idx)
                if item and len(item) == 3:  # 已合成的項目
                    audio_data = item[2]
                    if (isinstance(audio_data, bytes) and
                            audio_data not in [b"CONTENT_FILTERED", b"ERROR", b"FAILED_SYNTHESIS"]):

                        # 使用 mutagen 計算精確持續時間
                        precise_duration = self._calculate_precise_duration(
                            audio_data)
                        if precise_duration and precise_duration > 0:
                            batch_actual_duration += precise_duration
                            items_found += 1

            # 只有在找到足夠的樣本時才進行優化
            if items_found >= 2:
                # 估算我們預期的持續時間
                est_duration = pre_batch_target

                if est_duration > 0:
                    accuracy_ratio = batch_actual_duration / est_duration

                    # 基於準確度調整 TARGET_BATCH_DURATION (±10%)
                    if accuracy_ratio > 1.1:  # 估算過低 -> 增加目標
                        new_target = min(self.TARGET_BATCH_DURATION * 1.05,
                                         self.HIGH_WATERMARK * 0.8)
                    elif accuracy_ratio < 0.9:  # 估算過高 -> 減少目標
                        new_target = max(self.TARGET_BATCH_DURATION * 0.95,
                                         self.LOW_WATERMARK * 1.2)
                    else:
                        new_target = self.TARGET_BATCH_DURATION  # 保持不變

                    # 應用調整
                    if abs(new_target - self.TARGET_BATCH_DURATION) >= 0.5:  # 至少變化 0.5 秒才調整
                        old_target = self.TARGET_BATCH_DURATION
                        self.TARGET_BATCH_DURATION = new_target

                        logger.info(
                            f"Optimized TARGET_BATCH_DURATION: {old_target:.1f}s -> {new_target:.1f}s "
                            f"(actual: {batch_actual_duration:.1f}s vs estimated: {est_duration:.1f}s, "
                            f"ratio: {accuracy_ratio:.2f})"
                        )

        except Exception as e:
            logger.debug(f"Batch optimization failed: {e}")

    def _calculate_precise_duration(self, audio_data: AudioData) -> float:
        """精確計算 MP3 持續時間 (沒有錯誤處理，重複使用)"""
        if not _mutagen_available:
            return None

        try:
            if isinstance(audio_data, bytes):
                import io
                audio_buffer = io.BytesIO(audio_data)
                try:
                    audio = MP3(audio_buffer)
                    return audio.info.length if audio.info else 0.0
                except Exception:  # pylint: disable=broad-except
                    # 重試一次
                    audio_buffer.seek(0)
                    audio = MP3(audio_buffer)
                    return audio.info.length if audio.info else 0.0
            else:
                audio = MP3(audio_data)
                return audio.info.length if audio.info else 0.0

        except Exception:  # pylint: disable=broad-except
            return None

    def _get_current_engine(self) -> str:
        """獲取當前引擎類型"""
        # 始終返回當前設置的引擎名稱（字符串）
        return self._current_engine

    def set_current_engine(self, engine_type: str):
        """設置當前使用的引擎"""
        self._current_engine = engine_type
        logger.debug(f"Current TTS engine: {engine_type}")

    def _apply_watermarks_for_engine(self, engine_type: str, show_log: bool = True):
        """應用指定引擎的水位參數"""
        profile = self._watermark_profiles.get(
            engine_type,
            self._watermark_profiles.get("edge-tts")  # 預設
        )

        self.LOW_WATERMARK = profile["LOW"]
        self.HIGH_WATERMARK = profile["HIGH"]
        self.TARGET_BATCH_DURATION = profile["TARGET"]

        # 移除初始化日誌，避免誤導性信息
        # 日誌只在引擎切換時顯示

    def update_watermark_profile(self, engine_type: str,
                                 low: float = None, high: float = None,
                                 target: float = None):
        """動態更新指定引擎的水位參數（供實時優化使用）"""
        if engine_type not in self._watermark_profiles:
            logger.warning(f"Unknown engine: {engine_type}")
            return

        profile = self._watermark_profiles[engine_type]

        if low is not None:
            profile["LOW"] = low
        if high is not None:
            profile["HIGH"] = high
        if target is not None:
            profile["TARGET"] = target

        # 如果是當前引擎，立即應用
        if engine_type == self._get_current_engine():
            self._apply_watermarks_for_engine(engine_type)

        logger.info(f"Updated profile for {engine_type}: {profile}")

    def _estimate_play_duration(self, text: str) -> float:
        """估算文本播放時長 (秒)，考慮引擎差異和歷史校正"""
        if not text:
            return 0.0

        char_count = len(text)

        # 1. 根據當前引擎取得基礎語速
        current_engine = self._get_current_engine()
        base_speed = self._engine_base_speeds.get(current_engine, 3.0)

        # 2. 使用歷史平均修正基礎語速
        #    策略：歷史數據 70% + 基礎值 30%（加權平均）
        if len(self.play_history) >= 3:
            total_chars = sum(c for c, _ in self.play_history)
            total_seconds = sum(s for _, s in self.play_history)

            if total_seconds > 0:
                historical_speed = total_chars / total_seconds
                # 加權平均：相信歷史數據但不完全依賴
                avg_chars_per_sec = (
                    0.7 * historical_speed +
                    0.3 * base_speed
                )
            else:
                avg_chars_per_sec = base_speed
        else:
            # 歷史數據不足，使用基礎值
            avg_chars_per_sec = base_speed

        # 3. 安全邊界：限制估算值在合理範圍內
        #    防止歷史數據極端值導致估算偏差
        engine_base = self._engine_base_speeds.get(current_engine, 3.0)
        min_speed = engine_base * 0.7
        max_speed = engine_base * 1.3
        avg_chars_per_sec = max(min_speed, min(max_speed, avg_chars_per_sec))

        # 4. 調試日誌
        if len(self.play_history) >= 10:
            logger.debug(
                f"Duration estimate for '{text[:20]}...': "
                f"engine={current_engine}, base={base_speed:.2f}, "
                f"final={avg_chars_per_sec:.2f} chars/s"
            )

        return char_count / avg_chars_per_sec

    # --- 公開接口 (供 PlaylistManager 調用) ---

    def record_playback_event(self, segment_id: int, duration: float, text_length: int):
        """記錄實際播放事件，用於修正估算模型"""
        if duration > 0 and text_length > 0:
            self.play_history.append((text_length, duration))

    def notify_underrun(self, wait_time: float = None):
        """通知發生 Underrun (僅記錄 Log)"""
        logger.debug(f"Buffer underrun detected (wait: {wait_time}s)")
        # 可以在這裡實現緊急處置，例如暫時縮短 TARGET_BATCH_DURATION

    def reset_for_engine_switch(self, new_engine: str):
        """引擎切換時同時調整語速和水位"""
        logger.info("─────────────────────────────────────")
        logger.info(f"🔄 Switching TTS engine to: {new_engine}")
        logger.info("─────────────────────────────────────")

        # 1. 重置播放歷史（為新引擎重新學習語速）
        self.play_history.clear()
        self._is_triggering = False

        # 2. 應用新引擎的水位參數
        self._apply_watermarks_for_engine(new_engine)

        # 3. 設置當前引擎
        self.set_current_engine(new_engine)

        # 4. 強制立即檢查，快速適應新引擎
        logger.info(f"Triggering immediate buffer check for {new_engine}...")
        self.wake_up_now()

        logger.info("─────────────────────────────────────")

    def hard_reset(self):
        """強制重置"""
        self.play_history.clear()
        self._is_triggering = False
        self._chapter_exhausted = False  # 重置標記，準備迎接新章節
        self._cancel_pending_trigger()

    async def notify_batch_started(self, batch_total_duration: float):
        """
        通知Controller一個新批次開始播放，設置定時器準備下一個批次。

        這個方法實施定時器模式：計算距播放結束還有LOW_WATERMARK秒時觸發下一個批次合成。

        Args:
            batch_total_duration: 當前播放批次的總持續時間(秒)
        """
        if not self.running:
            return

        logger.debug(
            f"Timer Mode: Batch started ({batch_total_duration:.2f}s total). "
            f"Scheduling next batch at {max(0, batch_total_duration - self.LOW_WATERMARK):.2f}s"
        )

        # 取消之前的定時器
        self._cancel_pending_trigger()

        # 確保有合理的延遲時間
        trigger_delay = max(0, batch_total_duration - self.LOW_WATERMARK)

        if trigger_delay <= 0:
            # 批次太短，直接立刻觸發
            logger.debug("Timer Mode: Batch too short, triggering immediately")
            asyncio.create_task(self._trigger_batch_refill())
        else:
            # 設置新定時器
            self._current_batch_playing = True
            self._pending_batch_trigger = asyncio.create_task(
                self._timer_trigger_batch(trigger_delay)
            )
            logger.debug(
                f"Timer Mode: Trigger scheduled in {trigger_delay:.2f}s")

    async def _timer_trigger_batch(self, delay: float):
        """定時器任務：等待指定時間後觸發批次"""
        try:
            await asyncio.sleep(delay)
            if self.running and self._current_batch_playing:
                logger.debug(
                    "Timer Mode: Trigger fired, starting next batch synthesis")
                await self._trigger_batch_refill()
        except asyncio.CancelledError:
            logger.debug("Timer Mode: Trigger cancelled")
            raise

    def _cancel_pending_trigger(self):
        """取消當前的定時器任務"""
        if self._pending_batch_trigger and not self._pending_batch_trigger.done():
            self._pending_batch_trigger.cancel()
            logger.debug("Timer Mode: Previous trigger cancelled")

        self._pending_batch_trigger = None
        self._current_batch_playing = False

    def wake_up_now(self):
        """外部強制喚醒 (觸發緊急批次)"""
        if self.running:
            # 取消當前定時器並立即觸發
            self._cancel_pending_trigger()
            asyncio.create_task(self._trigger_batch_refill())

    def get_performance_stats(self):
        """返回基本狀態供 UI 顯示"""
        return {
            "state": "monitoring" if self.running else "idle",
            "history_samples": len(self.play_history),
            "monitor_active": self.running
        }

    def get_diagnostics(self) -> dict:
        """返回診斷信息，用於 UI 顯示和日誌分析"""
        current_engine = self._get_current_engine()
        buffer_duration = self._calculate_buffer_duration()

        if self.play_history:
            total_chars = sum(c for c, _ in self.play_history)
            total_seconds = sum(s for _, s in self.play_history)
            actual_speed = total_chars / max(total_seconds, 0.1)
        else:
            actual_speed = 0.0

        return {
            "current_engine": current_engine,
            "current_buffer_duration": f"{buffer_duration:.1f}s",
            "water_levels": {
                "low": f"{self.LOW_WATERMARK:.1f}s",
                "high": f"{self.HIGH_WATERMARK:.1f}s",
            },
            "speed_estimation": {
                "base_speed": f"{self._engine_base_speeds.get(current_engine, 3.0):.2f}",
                "actual_speed": f"{actual_speed:.2f}",
                "history_samples": len(self.play_history),
            },
            "heartbeat": {
                "active": f"{self._active_heartbeat}s",
                "idle": f"{self._idle_heartbeat}s",
            },
            "status": "monitoring" if self.running else "idle",
        }

    def log_performance_snapshot(self):
        """記錄性能快照（用於性能分析）"""
        diag = self.get_diagnostics()
        logger.info(
            f"[Reservoir Snapshot] "
            f"Engine: {diag['current_engine']}, "
            f"Buffer: {diag['current_buffer_duration']}, "
            f"Speed: {diag['speed_estimation']['actual_speed']} chars/s, "
            f"Heartbeat: active={diag['heartbeat']['active']}/idle={diag['heartbeat']['idle']}"
        )
