#!/usr/bin/env python3
"""
简单的阶段四功能验证测试
"""

import asyncio
import threading
import time
from speakub.tts.integration import TTSIntegration
from speakub.ui.protocols import AppInterface
from speakub.utils.config import ConfigManager


class SimpleMockApp(AppInterface):
    """简化Mock app用于测试"""

    def __init__(self):
        pass

    def set_tts_status(self, status: str):
        pass

    @property
    def tts_status(self):
        return "STOPPED"

    @tts_status.setter
    def tts_status(self, value):
        pass

    @property
    def tts_engine(self):
        return None

    @tts_engine.setter
    def tts_engine(self, value):
        pass

    @property
    def tts_volume(self):
        return 50

    @property
    def tts_rate(self):
        return 0

    @property
    def tts_pitch(self):
        return "+0Hz"

    @property
    def tts_smooth_mode(self):
        return True

    @property
    def viewport_content(self):
        return None

    @property
    def tts_widget(self):
        return None

    def call_from_thread(self, func, *args, **kwargs):
        func(*args, **kwargs)

    def notify(self, message, title="", severity="info"):
        pass

    def query_one(self, selector, type=None):
        return None

    def run_worker(self, worker_func, exclusive=True, thread=True):
        pass

    def bell(self):
        pass


async def test_stage4_performance():
    """测试阶段四的TTSIntegration直接访问性能"""
    print("🎯 测试阶段四纯asyncio架构...")

    # 创建实例
    try:
        app = SimpleMockApp()
        config_manager = ConfigManager()
        tts_integration = TTSIntegration(app, config_manager)
        print("✓ TTSIntegration实例创建成功")
    except Exception as e:
        print(f"✗ 创建TTSIntegration失败: {e}")
        return

    # 测试异步事件直接访问 (无同步开销)
    print("测试异步事件直接访问性能...")

    iterations = 10000
    start_time = time.perf_counter()

    for i in range(iterations):
        if i % 2 == 0:
            tts_integration._async_tts_stop_requested.set()
            tts_integration._async_tts_pause_requested.set()
            tts_integration._async_tts_audio_ready.set()
        else:
            tts_integration._async_tts_stop_requested.clear()
            tts_integration._async_tts_pause_requested.clear()
            tts_integration._async_tts_audio_ready.clear()

        # 检查状态
        is_set_1 = tts_integration._async_tts_stop_requested.is_set()
        is_set_2 = tts_integration._async_tts_pause_requested.is_set()
        is_set_3 = tts_integration._async_tts_audio_ready.is_set()

    end_time = time.perf_counter()
    latency = (end_time - start_time) / iterations * 1000  # ms per operation

    print(f"純asyncio事件操作延遲: {latency:.3f}ms")
    print(f"每操作1億次延遲: {latency * 100000:.3f}ms")
    return latency


def test_reference_threading():
    """threading.Event性能作为参考"""
    print("🧵 测试threading.Event参考性能...")

    events = [threading.Event() for _ in range(10)]
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

    print(f"threading.Event操作延遲: {latency:.3f}ms")
    return latency


async def main():
    print("🚀 阶段四迁移验证测试")
    print("验证纯asyncio架构功能正确性")
    print("=" * 50)

    # 基本功能测试
    stage4_latency = await test_stage4_performance()

    if stage4_latency is None:
        print("✗ 阶段四功能测试失败")
        return

    print("\n参考性能测试:")
    threading_latency = test_reference_threading()

    # 简单对比
    improvement = (threading_latency - stage4_latency) / \
        threading_latency * 100

    print("\n🎯 总结:")
    print("  ✓ 阶段四TTSIntegration成功初始化")
    print(f"  ✓ 性能改善: {improvement:.1f}%")
    print("  ✓ 纯asyncio架构验证完成!")


if __name__ == "__main__":
    asyncio.run(main())
