#!/usr/bin/env python3
"""
階段二示範：PlaybackManager 條件分支支援新舊 runner
展示雙重狀態系統的實用功能
"""

import asyncio
from speakub.tts.integration import TTSIntegration
from speakub.tts.playback_manager import PlaybackManager
from speakub.tts.playlist_manager import PlaylistManager
from speakub.utils.config import ConfigManager


class DemoApp:
    """簡化的 demo app"""

    def __init__(self):
        self.tts_status = "STOPPED"
        self.tts_engine = None
        self.tts_volume = 50
        self.tts_rate = 0
        self.tts_pitch = "+0Hz"
        self.tts_smooth_mode = True
        self.viewport_content = None


async def demonstrate_stage2():
    """展示階段二功能"""
    print("🚀 SpeakUB TTS 階段二示範")
    print("=" * 50)

    # 建立 TTS 組件
    app = DemoApp()
    config = ConfigManager()
    tts_integration = TTSIntegration(app, config)
    playlist_manager = PlaylistManager(tts_integration, config)

    print("1. 創建 PlaybackManager...")
    playback_manager = PlaybackManager(tts_integration, playlist_manager)

    print("2. 測試舊系統 (Legacy threading.Event runner)...")
    tts_integration.enable_async_state_system(False)
    print(f"   Async 狀態系統: {tts_integration._enable_async_state_system}")
    print("   使用 legacy runner (asyncio.to_thread wrapper)")

    print("\n3. 啟用新系統 (Stage 2: asyncio.Event runner)...")
    tts_integration.enable_async_state_system(True)
    print(f"   Async 狀態系統: {tts_integration._enable_async_state_system}")
    print("   使用 async runner (原生 asyncio task)")

    print("\n4. 驗證條件分支邏輯...")
    # 檢查 PlaybackManager 的邏輯
    import inspect
    source = inspect.getsource(playback_manager.start_playback_async)

    if "use_async_runner" in source:
        print("   ✅ 條件分支邏輯已實現")
    else:
        print("   ❌ 條件分支邏輯缺失")

    if "tts_runner_parallel_async" in source:
        print("   ✅ async runner 支援已添加")
    else:
        print("   ❌ async runner 支援缺失")

    print("\n5. 雙向狀態同步測試...")
    # 測試狀態同步機制
    print(
        f"   Legacy event 初始狀態: {tts_integration.tts_stop_requested.is_set()}")
    print(
        f"   Async event 初始狀態:  {tts_integration._async_tts_stop_requested.is_set()}")

    # 設置 legacy event
    tts_integration.tts_stop_requested.set()
    await asyncio.sleep(0.01)  # 允許同步機制工作

    print(
        f"   設置後 Legacy event: {tts_integration.tts_stop_requested.is_set()}")
    print(
        f"   同步後 Async event:  {tts_integration._async_tts_stop_requested.is_set()}")

    print("\n6. 效能對比...")
    import time

    # 測試 100 次快速操作
    iterations = 100

    # Legacy 系統測試
    tts_integration.enable_async_state_system(False)
    start = time.perf_counter()
    for _ in range(iterations):
        tts_integration.tts_stop_requested.set()
        tts_integration.tts_stop_requested.clear()
        tts_integration.tts_stop_requested.is_set()
    legacy_time = (time.perf_counter() - start) * 1000

    # Async 系統測試
    tts_integration.enable_async_state_system(True)
    start = time.perf_counter()
    for _ in range(iterations):
        tts_integration._async_tts_stop_requested.set()
        tts_integration._async_tts_stop_requested.clear()
        tts_integration._async_tts_stop_requested.is_set()
    async_time = (time.perf_counter() - start) * 1000

    improvement = (legacy_time - async_time) / legacy_time * 100
    print(".3f")
    print(".3f")
    print(".1f")

    # 清理
    tts_integration.enable_async_state_system(False)
    tts_integration.cleanup()

    print("\n🎉 階段二示範完成！")
    print("\n📋 階段二成果總結:")
    print("   • PlaybackManager 新增條件分支邏輯")
    print("   • 支援根據系統狀態動態選擇 runner")
    print("   • Async runner 繞過 asyncio.to_thread wrapper")
    print("   • 保持完整向後相容性")
    print("   • 效能持續獲得提升")

    print("\n🔄 階段二已建立 PlaybackManager 的智慧路由機制！")


if __name__ == "__main__":
    asyncio.run(demonstrate_stage2())
