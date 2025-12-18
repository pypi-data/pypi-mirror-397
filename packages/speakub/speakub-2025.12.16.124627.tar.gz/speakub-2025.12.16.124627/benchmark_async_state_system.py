#!/usr/bin/env python3
"""
階段一實施的基準測試：雙重狀態系統效能評估
測試舊 threading.Event 系統 vs 新 asyncio.Event + 同步系統的效能
"""

import asyncio
import threading
import time
import statistics
from speakub.tts.integration import TTSIntegration
from speakub.ui.protocols import AppInterface
from speakub.utils.config import ConfigManager


class MockApp(AppInterface):
    """Mock app for testing"""

    def __init__(self):
        self.tts_status = "STOPPED"
        self.tts_engine = None
        self.tts_volume = 50
        self.tts_rate = 0
        self.tts_pitch = "+0Hz"
        self.tts_smooth_mode = True
        self.viewport_content = None


def benchmark_legacy_events():
    """測試原始 threading.Event 效能"""
    print("🧵 測試舊的 threading.Event 系統效能...")

    # 建立事件
    events = [threading.Event() for _ in range(10)]

    # 測試迴圈
    iterations = 10000
    start_time = time.perf_counter()

    for i in range(iterations):
        for event in events:
            if i % 2 == 0:
                event.set()
            else:
                event.clear()
            event.is_set()

    end_time = time.perf_counter()
    latency = (end_time - start_time) / iterations * 1000  # ms per operation

    print(f"平均延遲: {latency:.2f}ms")


async def benchmark_async_events():
    """測試純 asyncio.Event 效能"""
    print("🔄 測試新的 asyncio.Event 系統效能...")

    # 建立事件
    events = [asyncio.Event() for _ in range(10)]

    # 測試迴圈
    iterations = 10000
    start_time = time.perf_counter()

    for i in range(iterations):
        for event in events:
            if i % 2 == 0:
                event.set()
            else:
                event.clear()
            event.is_set()

    end_time = time.perf_counter()
    latency = (end_time - start_time) / iterations * 1000  # ms per operation

    print(f"平均延遲: {latency:.2f}ms")


async def benchmark_dual_sync_system():
    """測試雙重狀態同步系統效能"""
    print("🔄🔄 測試雙重狀態同步系統效能...")

    # 建立 TTSIntegration (包含同步機制)
    app = MockApp()
    config_manager = ConfigManager()
    tts_integration = TTSIntegration(app, config_manager)

    # 啟用 async 狀態系統
    tts_integration.enable_async_state_system(True)

    # 測試同步操作
    iterations = 1000  # 減少迭代次數，因為同步更耗時
    start_time = time.perf_counter()

    for i in range(iterations):
        # 模擬 threading.Event 操作
        if i % 2 == 0:
            tts_integration.tts_stop_requested.set()
            tts_integration.tts_pause_requested.set()
            tts_integration.tts_audio_ready.set()
        else:
            tts_integration.tts_stop_requested.clear()
            tts_integration.tts_pause_requested.clear()
            tts_integration.tts_audio_ready.clear()

        # 檢查狀態
        tts_integration.tts_stop_requested.is_set()
        tts_integration.tts_pause_requested.is_set()
        tts_integration.tts_audio_ready.is_set()

        # 小延遲讓同步機制工作
        await asyncio.sleep(0.001)

    end_time = time.perf_counter()
    latency = (end_time - start_time) / iterations * 1000  # ms per operation

    # 關閉同步系統
    tts_integration.enable_async_state_system(False)

    print(f"平均延遲: {latency:.2f}ms")


async def main():
    """主基準測試函數"""
    print("🚀 階段一雙重狀態系統基準測試\n")

    # 多次測試取得平均值
    num_runs = 5

    legacy_latencies = []
    async_latencies = []
    dual_latencies = []

    for run in range(num_runs):
        print(f"\n🔄 執行測試運行 {run + 1}/{num_runs}")

        print("\n" + "="*50)
        legacy_latencies.append(benchmark_legacy_events())

        print("\n" + "="*50)
        async_latencies.append(await benchmark_async_events())

        print("\n" + "="*50)
        dual_latencies.append(await benchmark_dual_sync_system())

        # 運行間短暫休息
        await asyncio.sleep(0.1)

    print("\n🎯 基準測試結果總結")
    print("="*60)

    print(
        f"🧵 threading.Event:     avg={statistics.mean(legacy_latencies):.3f}ms, std={statistics.stdev(legacy_latencies):.3f}ms")
    print(
        f"🔄 asyncio.Event:       avg={statistics.mean(async_latencies):.3f}ms, std={statistics.stdev(async_latencies):.3f}ms")
    print(
        f"🔄🔄 Dual Sync System: avg={statistics.mean(dual_latencies):.3f}ms, std={statistics.stdev(dual_latencies):.3f}ms")

    # 計算改進百分比
    legacy_avg = statistics.mean(legacy_latencies)
    async_avg = statistics.mean(async_latencies)
    dual_avg = statistics.mean(dual_latencies)

    async_improvement = (legacy_avg - async_avg) / legacy_avg * 100
    dual_overhead = (dual_avg - legacy_avg) / legacy_avg * 100

    print("\n🎯 效能改進總結:")
    print(f"   • asyncio.Event 改進: {async_improvement:.1f}% 較快")

    print("\n📊 效能分析:")
    print(f"   • 雙重同步系統額外負擔: {dual_overhead:.1f}%")
    print(f"   • 淨效益: {async_improvement - dual_overhead:.1f}%")
    print(f"   • 基準測試在 {num_runs} 次運行中執行完成")
    print("\n✅ 階段一雙重狀態系統實施完成！")


if __name__ == "__main__":
    asyncio.run(main())
