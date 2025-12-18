# 檔案: speakub/tts/batching_strategy.py

import logging
from typing import Any, Dict, List, Optional, Tuple
from collections import deque
import time

from speakub.utils.config import ConfigManager

logger = logging.getLogger(__name__)


class BatchDecisionMonitor:
    """監控和追蹤批次決策過程，用於性能分析和優化"""

    def __init__(self, window_size: int = 100):
        self._decisions: deque = deque(maxlen=window_size)
        self._decision_lock = None  # 非同步上下文中不使用鎖

    def record_decision(
        self,
        strategy_name: str,
        batch_size: int,
        total_chars: int,
        engine: str = "unknown",
        decision_time_ms: float = 0.0
    ) -> None:
        """記錄一次批次決策"""
        decision = {
            "timestamp": time.time(),
            "strategy": strategy_name,
            "batch_size": batch_size,
            "total_chars": total_chars,
            "engine": engine,
            "decision_time_ms": decision_time_ms,
        }
        self._decisions.append(decision)
        logger.debug(
            f"[{engine}] Batch decision: {strategy_name}, size={batch_size}, chars={total_chars}"
        )

    def get_statistics(self) -> Dict[str, Any]:
        """獲取決策統計信息"""
        if not self._decisions:
            return {"total_decisions": 0}

        stats = {
            "total_decisions": len(self._decisions),
            "strategy_distribution": {},
            "avg_batch_size": 0,
            "avg_chars_per_batch": 0,
            "engine_distribution": {},
        }

        total_batch_size = 0
        total_chars = 0

        for decision in self._decisions:
            strategy = decision["strategy"]
            stats["strategy_distribution"][strategy] = \
                stats["strategy_distribution"].get(strategy, 0) + 1

            engine = decision["engine"]
            stats["engine_distribution"][engine] = \
                stats["engine_distribution"].get(engine, 0) + 1

            total_batch_size += decision["batch_size"]
            total_chars += decision["total_chars"]

        stats["avg_batch_size"] = total_batch_size / len(self._decisions)
        stats["avg_chars_per_batch"] = total_chars / len(self._decisions)

        return stats

    def get_recent_decisions(self, count: int = 10) -> List[Dict[str, Any]]:
        """獲取最近的決策記錄"""
        return list(self._decisions)[-count:]


class FusionBatchingStrategy:
    """
    實作 Fusion v3.5 適應性批次邏輯，透過分析內容特性來決定最佳批次大小。
    增強版：
    - 加入章節完整性保護，避免批次跨越章節邊界
    - 引擎感知的動態參數調整（Edge-TTS vs Nanmai vs GTTS）
    - 批次決策監控和性能指標收集
    """

    def __init__(self, config_manager: ConfigManager, engine=None):
        self._config_manager = config_manager
        self._current_engine = engine

        # 初始化決策監控器
        self._decision_monitor = BatchDecisionMonitor()

        # 載入引擎特定的參數
        self._update_engine_parameters()

    def _update_engine_parameters(self) -> None:
        """從引擎物件讀取參數，移除硬編碼的引擎名稱判斷"""
        if self._current_engine and hasattr(self._current_engine, 'engine_parameters'):
            # 使用新的統一參數介面
            params = self._current_engine.engine_parameters
            self.char_limit = params['char_limit']
            self.batch_size_preference = params['batch_size_preference']
            self.supports_batch_merging = params['supports_batch_merging']
            self.needs_text_sanitization = params['needs_text_sanitization']
            self.rate_limit_cooldown = params['rate_limit_cooldown']
        else:
            # 後備：從配置檔案讀取 (向後相容性)
            self.char_limit = self._config_manager.get(
                "tts.fusion.char_limit", 200)
            self.batch_size_preference = self._config_manager.get(
                "tts.batch_size", 5)
            self.supports_batch_merging = False
            self.needs_text_sanitization = True
            self.rate_limit_cooldown = 1.0

        # 通用參數
        self.base_batch_size = self._config_manager.get(
            "tts.batch_size", 5)
        self.max_short_items = self._config_manager.get(
            "tts.fusion.max_short_items", 15)
        self.long_paragraph_max_items = self._config_manager.get(
            "tts.fusion.long_paragraph_max_items", 5)

        engine_name = getattr(self._current_engine, '__class__',
                              lambda: 'Unknown').__name__ if self._current_engine else "Unknown"
        logger.info(
            f"FusionBatchingStrategy configured for {engine_name}: "
            f"char_limit={self.char_limit}, batch_size={self.base_batch_size}, "
            f"max_short_items={self.max_short_items}, long_paragraph_max_items={self.long_paragraph_max_items}"
        )

    def set_engine(self, engine) -> None:
        """切換引擎時動態更新參數"""
        if engine != self._current_engine:
            self._current_engine = engine
            self._update_engine_parameters()
            engine_name = getattr(
                engine, '__class__', lambda: 'Unknown').__name__ if engine else "Unknown"
            logger.info(f"Batching strategy switched to {engine_name}")

    def get_decision_monitor(self) -> BatchDecisionMonitor:
        """獲取決策監控器"""
        return self._decision_monitor

    def select_batch(
        self, candidates: List[Tuple[int, str]]
    ) -> Tuple[List[Tuple[int, str]], str]:
        """
        分析候選項目並根據 Fusion 策略選出最佳批次。
        根據當前引擎動態調整參數，並記錄決策用於性能分析。

        Args:
            candidates: 待處理的項目列表，格式為 (index, text)。

        Returns:
            一個包含 (選定的批次, 策略名稱) 的元組。
        """
        if not candidates:
            return [], "EMPTY"

        # 使用 Fusion 邏輯選擇批次
        batch, strategy_name = self._select_fusion_batch(candidates)

        # 記錄決策
        total_chars = sum(len(text) for _, text in batch)
        engine_name = getattr(
            self._current_engine, '__class__', lambda: 'Unknown').__name__ if self._current_engine else "Unknown"
        self._decision_monitor.record_decision(
            strategy_name, len(batch), total_chars,
            engine=engine_name
        )

        return batch, strategy_name

    def _select_fusion_batch(
        self, candidates: List[Tuple[int, str]]
    ) -> Tuple[List[Tuple[int, str]], str]:
        """
        Fusion 策略選擇核心：三段變速邏輯 (Three-Stage Gear Shifting)
        完全對應 config.yaml 設定值，並包含效率優化。
        """
        # 0. 基礎數據分析
        first_item_len = len(candidates[0][1])

        # 共用的硬上限 (Hard Cap)：防止單次請求過大導致 Timeout
        # 設定為 char_limit 的 1.6 倍 (例如 150 * 1.6 = 240字)
        HARD_CAP = self.char_limit * 1.6

        # ==============================================================================
        # 優先級 1: LONG_PARAGRAPH_MODE (巨石處理)
        # ==============================================================================
        # 觸發條件: "隊列首項" 非常長 (超過 char_limit 的 90%)
        # ------------------------------------------------------------------------------
        if first_item_len > (self.char_limit * 0.9):
            strategy = "LONG_PARAGRAPH_MODE"
            selected = []
            current_chars = 0

            for idx, text in candidates:
                text_len = len(text)

                # 1. [Config 限制] 遵守 long_paragraph_max_items (例如 5)
                # 即使長度還夠，數量到了也要停。
                if len(selected) >= self.long_paragraph_max_items:
                    break

                # 2. [安全閥] 硬上限檢查
                # 這裡的邏輯是：第一個長文(例如 140字)一定會被加入(因為 selected 為空)。
                # 但後面的小尾巴如果會導致總量爆表(>240)，就不准加。
                if selected and (current_chars + text_len > HARD_CAP):
                    break

                selected.append((idx, text))
                current_chars += text_len

            return selected, strategy

        # ==============================================================================
        # 優先級 2: SHORT_CONTENT_MODE (碎沙處理 - 嚴格連續性檢測 + 效益門檻)
        # ==============================================================================
        # [🔥 最終優化] 加入最小效益門檻，避免低效短批次
        # ------------------------------------------------------------------------------
        SHORT_ITEM_THRESHOLD = 30  # 短句定義
        MIN_CONSECUTIVE_SHORT = 3  # 至少連續幾個

        # 🔧 優化：增加最小效益門檻 (50秒)
        # 如果短模式抓不到 50 秒的量，就不要啟動，交給 PARAGRAPH_MODE 去混搭長句
        MIN_DURATION = 50.0
        CHARS_PER_SEC = 2.5
        MIN_CHARS_TARGET = MIN_DURATION * CHARS_PER_SEC  # 125字

        # 1. [偵測與模擬]
        # 不只數數量，還順便算一下如果啟動了能抓多少字
        consecutive_count = 0
        potential_chars = 0

        for _, text in candidates:
            if len(text) <= SHORT_ITEM_THRESHOLD:
                consecutive_count += 1
                potential_chars += len(text)
            else:
                break  # 遇到不短的就停

        # 2. [決策]
        # 啟動條件 A: 連續數量非常多 (>= 5)，那即使字數少也值得打包 (減少 Overhead)
        # 啟動條件 B: 連續數量有達標 (>= 3) 且 總字數也夠多 (>= 125)，效益足夠
        FORCE_SHORT_MODE_COUNT = 5  # 如果有 5 個以上短句，無條件啟動

        if (consecutive_count >= FORCE_SHORT_MODE_COUNT) or \
           (consecutive_count >= MIN_CONSECUTIVE_SHORT and potential_chars >= MIN_CHARS_TARGET):

            strategy = "SHORT_CONTENT_MODE"
            selected = []
            current_chars = 0

            # 短模式專用上限：允許稍微多一點 (1.5倍)
            SHORT_MODE_CAP = self.char_limit * 1.5

            for idx, text in candidates:
                text_len = len(text)

                # A. [中斷機制] 核心！
                # 雖然進入了短模式，但如果碰到一個 "不短" 的句子 (>30)，
                # 必須立刻停止，把這個句子留給 PARAGRAPH_MODE。
                if text_len > SHORT_ITEM_THRESHOLD:
                    break

                # B. [數量限制] 這是短模式的優勢，可以吞很多 (例如 15)
                if len(selected) >= self.max_short_items:
                    break

                # C. [總量安全閥]
                if current_chars + text_len > SHORT_MODE_CAP:
                    break

                selected.append((idx, text))
                current_chars += text_len

            return selected, strategy

        # ==============================================================================
        # 優先級 3: PARAGRAPH_MODE (標準堆疊 - 兜底模式)
        # ==============================================================================
        # 觸發條件: 上述兩者皆非 (一般敘述文、混合內容)。
        # [🔥 最終修正] 時間是絕對指標，數量只是安全閥
        # ------------------------------------------------------------------------------
        strategy = "PARAGRAPH_MODE"
        selected = []
        current_chars = 0

        # 參數設定
        MIN_DURATION = 50.0     # 50秒 (絕對指標)
        CHARS_PER_SEC = 2.5     # Nanmai 估算速度
        MIN_CHARS_TARGET = MIN_DURATION * CHARS_PER_SEC  # 125字

        # [🔥 修正] 數量上限
        # 既然 4 items 可能只有 14.8s，那我們就不能在 4 或 5 就停下來。
        # 我們給它一個足夠大的空間，讓它有機會去湊滿 50秒。
        # 使用 max_short_items (通常是15) 作為數量安全閥
        SAFETY_ITEM_LIMIT = self.max_short_items

        for idx, text in candidates:
            text_len = len(text)

            # 1. [強制停止] 數量安全閥
            # 只有當數量真的太多 (例如 >= 15)，為了避免處理負擔才停。
            # 這樣 "4 items" 絕對不會被攔下來。
            if len(selected) >= SAFETY_ITEM_LIMIT:
                break

            # 2. [Pre-check] 硬上限檢查 (字數防爆)
            if selected and (current_chars + text_len > HARD_CAP):
                break

            # 3. [Action] 加入
            selected.append((idx, text))
            current_chars += text_len

            # 4. [Post-check] 唯一的達標檢查：時間/字數
            # [🔥 核心修正] 移除 "OR len > 3" 的條件
            # 現在只有 "字數/時間達標" 才能觸發停止。
            #
            # 驗證案例 (4 items, 37 chars, ~14.8s):
            # -> 37 < 125 ? 是。 -> 繼續迴圈！ (補第 5 個)
            if current_chars >= MIN_CHARS_TARGET:
                break

        return selected, strategy
