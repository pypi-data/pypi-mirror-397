#!/usr/bin/env python3
"""
SpeakUB Reservoir v6.0 場景測試腳本

測試目標：
1. 短句連發場景 (核心問題場景)
2. 長段落場景
3. 混合內容場景
4. 水位變化監控
"""

from speakub.tts.reservoir.controller import PredictiveBatchController, TriggerState
import asyncio
import logging
import time
from typing import List, Tuple
from unittest.mock import MagicMock, AsyncMock

# 設定日誌
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 模擬組件


class MockPlaylistManager:
    """模擬 PlaylistManager 用於測試"""

    def __init__(self, playlist_items: List[Tuple[str, int, bytes]]):
        self.playlist = playlist_items
        self.current_index = 0
        self._buffered_duration = 0.0

    def get_buffered_duration(self) -> float:
        """返回當前緩衝持續時間"""
        return self._buffered_duration

    def set_buffered_duration(self, duration: float):
        """設定緩衝持續時間 (測試用)"""
        self._buffered_duration = duration

    def _has_synthesis_work_remaining(self) -> bool:
        """檢查是否還有合成工作"""
        return self.current_index < len(self.playlist)

    async def _get_next_batch_optimal(self) -> List[Tuple[int, str]]:
        """模擬 Fusion 返回的批次"""
        if not self._has_synthesis_work_remaining():
            return []

        # 模擬短句批次 (核心測試場景)
        batch_size = 15  # Fusion 為短句返回 15 個
        batch = []
        for i in range(batch_size):
            if self.current_index + i < len(self.playlist):
                item = self.playlist[self.current_index + i]
                if len(item) >= 2:
                    batch.append((self.current_index + i, item[0]))

        # 推進指針
        self.current_index += len(batch)
        return batch

    async def _process_batch(self, batch_items: List[Tuple[int, str]]) -> None:
        """模擬批次處理"""
        logger.info(f"處理批次: {len(batch_items)} 個項目")

        total_duration = 0.0
        for _, text in batch_items:
            # 估算每個項目的播放時間 (簡化模型)
            estimated_duration = len(text) * 0.1  # 假設 0.1 秒每字元
            total_duration += estimated_duration

        # 更新緩衝持續時間
        self._buffered_duration += total_duration
        logger.info(".1f")
        await asyncio.sleep(0.1)  # 模擬處理時間


class MockQueuePredictor:
    """模擬 QueuePredictor"""

    def __init__(self):
        pass

    def estimate_batch_duration(self, batch_items: List[Tuple[int, str]]) -> float:
        """估算批次持續時間"""
        total = 0.0
        for _, text in batch_items:
            total += len(text) * 0.1  # 簡化估算
        return total


# 匯入實際的控制器


class ReservoirV6Tester:
    """Reservoir v6.0 測試器"""

    def __init__(self):
        self.test_results = []

    async def test_scenario(self, name: str, initial_buffer: float, playlist_items):
        """測試特定場景"""
        logger.info(f"\n{'='*50}")
        logger.info(f"開始測試場景: {name}")
        logger.info(f"初始緩衝: {initial_buffer:.1f}秒")
        logger.info(f"播放列表項目數: {len(playlist_items)}")

        # 建立模擬組件
        playlist_manager = MockPlaylistManager(playlist_items)
        playlist_manager.set_buffered_duration(initial_buffer)
        queue_predictor = MockQueuePredictor()

        # 建立控制器
        controller = PredictiveBatchController(
            playlist_manager=playlist_manager,
            queue_predictor=queue_predictor
        )

        # 記錄測試數據
        test_data = {
            'scenario': name,
            'initial_buffer': initial_buffer,
            'start_time': time.time(),
            'trigger_count': 0,
            'buffer_history': [initial_buffer],
            'actions': []
        }

        # 監控控制器狀態
        original_trigger = controller._trigger_new_batch

        async def monitored_trigger(recursive=False):
            test_data['trigger_count'] += 1
            test_data['actions'].append({
                'time': time.time() - test_data['start_time'],
                'action': 'trigger_batch',
                'recursive': recursive,
                'buffer_before': playlist_manager.get_buffered_duration()
            })
            logger.info(f"觸發批次處理 (遞歸: {recursive})")

            await original_trigger(recursive)

            test_data['actions'].append({
                'time': time.time() - test_data['start_time'],
                'action': 'batch_completed',
                'buffer_after': playlist_manager.get_buffered_duration()
            })
            test_data['buffer_history'].append(
                playlist_manager.get_buffered_duration())

        controller._trigger_new_batch = monitored_trigger

        # 開始監控
        await controller.start_monitoring()

        # 模擬播放消耗
        consumption_rate = 2.0  # 每秒消耗 2 秒的緩衝
        test_duration = 30  # 測試 30 秒

        for i in range(test_duration):
            await asyncio.sleep(1)

            # 消耗緩衝
            current_buffer = playlist_manager.get_buffered_duration()
            consumption = min(consumption_rate, current_buffer)
            new_buffer = current_buffer - consumption
            playlist_manager.set_buffered_duration(new_buffer)

            # 記錄水位
            test_data['buffer_history'].append(new_buffer)

            # 模擬事件驅動檢查
            if i % 3 == 0:  # 每3秒檢查一次
                await controller.plan_and_schedule_next_trigger()

            logger.debug(f"Buffer level: {new_buffer:.1f}s")
        # 停止測試
        await controller.stop_monitoring()

        test_data['end_time'] = time.time()
        test_data['duration'] = test_data['end_time'] - test_data['start_time']
        test_data['final_buffer'] = playlist_manager.get_buffered_duration()

        self.test_results.append(test_data)
        logger.info(f"場景 '{name}' 測試完成")
        logger.info(f"最終緩衝: {test_data['final_buffer']:.1f}秒")
        logger.info(f"觸發次數: {test_data['trigger_count']}")
        logger.info(f"測試持續時間: {test_data['duration']:.1f}秒")

    def generate_report(self):
        """生成測試報告"""
        print("\n" + "="*80)
        print("SPEAKUB RESERVOIR v6.0 場景測試報告")
        print("="*80)

        for result in self.test_results:
            print(f"\n場景: {result['scenario']}")
            print("-" * 40)
            print(f"初始緩衝: {result['initial_buffer']:.1f}秒")
            print(f"最終緩衝: {result['final_buffer']:.1f}秒")
            print(f"觸發次數: {result['trigger_count']}")
            print(f"測試持續時間: {result['duration']:.1f}秒")

            # 分析水位穩定性
            buffer_history = result['buffer_history']
            if len(buffer_history) > 1:
                min_buffer = min(buffer_history)
                max_buffer = max(buffer_history)
                avg_buffer = sum(buffer_history) / len(buffer_history)
                stability = 1 - (max_buffer - min_buffer) / (
                    max_buffer + 1)  # 穩定性指標

                print(f"緩衝範圍: {min_buffer:.1f} - {max_buffer:.1f}秒")
                print(f"平均緩衝: {avg_buffer:.1f}秒")
                print(f"穩定性指標: {stability:.3f}")
            # 分析動作
            refill_actions = [a for a in result['actions']
                              if a['action'] == 'trigger_batch']
            completed_actions = [a for a in result['actions']
                                 if a['action'] == 'batch_completed']

            print(f"補水動作: {len(refill_actions)} 次")
            print(f"完成動作: {len(completed_actions)} 次")

            # 評估場景表現
            if "短句" in result['scenario']:
                if result['trigger_count'] >= 3 and min(buffer_history) >= 10:
                    print("✅ 短句場景: 通過 - 成功維持水位")
                else:
                    print("❌ 短句場景: 失敗 - 水位波動過大")
            elif "長段落" in result['scenario']:
                if result['trigger_count'] <= 2 and max(buffer_history) >= 50:
                    print("✅ 長段落場景: 通過 - 一次補滿後休眠")
                else:
                    print("❌ 長段落場景: 失敗 - 補水過於頻繁")
            elif "混合" in result['scenario']:
                stability_score = 1 - \
                    (max_buffer - min_buffer) / (max_buffer + 1)
                if stability_score > 0.7:
                    print("✅ 混合場景: 通過 - 良好適應性")
                else:
                    print("❌ 混合場景: 失敗 - 適應性不足")


async def main():
    """主測試函數"""
    tester = ReservoirV6Tester()

    # 測試場景 1: 短句連發 (核心問題場景)
    short_sentences = [("嗯", i, None) for i in range(50)]  # 50 個短句
    await tester.test_scenario("短句連發場景", 5.0, short_sentences)

    # 測試場景 2: 長段落
    long_paragraphs = [
        ("這是一個很長的段落，用於測試系統在遇到長內容時的行為。系統應該能夠一次處理這個長段落，並且在補充緩衝後進入休眠狀態，而不是頻繁地觸發小批次處理。" * 3, i, None) for i in range(3)]
    await tester.test_scenario("長段落場景", 10.0, long_paragraphs)

    # 測試場景 3: 混合內容
    mixed_content = []
    # 添加一些短句
    mixed_content.extend([("是", i, None) for i in range(20)])
    # 添加長段落
    mixed_content.extend(
        [("這是一個混合場景的長段落測試。系統需要能夠適應從短句突然轉換到長段落的內容變化，並保持穩定的緩衝水位。" * 2, i + 20, None) for i in range(5)])
    # 再添加一些短句
    mixed_content.extend([("好", i + 25, None) for i in range(15)])

    await tester.test_scenario("混合內容場景", 8.0, mixed_content)

    # 生成報告
    tester.generate_report()

    print("\n" + "="*80)
    print("效能監控建議")
    print("="*80)
    print("1. 水位變化曲線: 記錄 buffer_history 中的數據點")
    print("2. 觸發頻率: 監控 trigger_count 在不同場景下的表現")
    print("3. 系統負載: 觀察 CPU/記憶體使用率是否降低")
    print("4. 用戶體驗: 測試實際播放時是否有斷流情況")

    print("\n參數調優建議:")
    print("- LOW_WATERMARK (15s): 可根據網路速度調整")
    print("- HIGH_WATERMARK (60s): 可根據記憶體限制調整")
    print("- 遞歸觸發延遲 (0.1s): 可調整以平衡響應速度和系統負載")


if __name__ == "__main__":
    asyncio.run(main())
