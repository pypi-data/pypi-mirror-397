#!/usr/bin/env python3
"""
TTS runners and workers for SpeakUB.
"""

import asyncio
import logging
import socket
import time
from typing import TYPE_CHECKING

from speakub.core.exceptions import (
    NetworkAPIError,
    NetworkConnectionError,
    NetworkTimeoutError,
    TTSPlaybackError,
    TTSProviderError,
    TTSSynthesisError,
    TTSVoiceError,
)
from speakub.utils.config import ConfigManager, get_smooth_synthesis_delay
from speakub.utils.text_utils import (
    analyze_punctuation_content,
    correct_chinese_pronunciation,
)

# --- 新增開始 ---
try:
    from edge_tts.exceptions import NoAudioReceived
except ImportError:
    # 如果 edge-tts 未安裝，定義一個虛設的異常類別以避免 NameError
    class NoAudioReceived(Exception):
        pass


from speakub.tts.ui.error_handler import handle_runner_error
from speakub.tts.ui.playlist import tts_load_next_chapter_async

# --- 新增結束 ---

if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration

logger = logging.getLogger(__name__)


# --- 新增：階段三 async 支援 - 完全異步化 ---
async def tts_runner_parallel_async(tts_integration: "TTSIntegration") -> None:
    """Async version of tts_runner_parallel using asyncio.Event (階段三：完全異步化)."""
    app = tts_integration.app
    playlist_manager = tts_integration.playlist_manager

    # 標記停止原因
    stopped_due_to_engine_switch = False

    with tts_integration.tts_lock:
        tts_integration.tts_thread_active = True

    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # [🔥 關鍵：Engine Switch 檢查點] 如果引擎正在切換，停止當前 Runner
            # 防止平行 Runner 在引擎切換期間造成混亂
            if getattr(tts_integration, '_engine_switching', False):
                logger.info(
                    "Async parallel runner: Engine switch detected, stopping runner (STOPPED). Next engine will continue from this point.")
                stopped_due_to_engine_switch = True
                break

            # [🔥 關鍵：Mode Switch 檢查點] 如果模式已切換到 Serial，立刻終止
            # 防止 Parallel Runner 在模式切換後繼續執行
            if not app.tts_smooth_mode:
                logger.info(
                    "Async parallel runner: Mode switched to Serial at main loop, self-terminating.")
                break
            with tts_integration.tts_lock:
                exhausted = playlist_manager.is_exhausted()

            if exhausted:
                success = await tts_load_next_chapter_async(playlist_manager)

                # [🔥 關鍵修復：Post-Await 身分驗證]
                # 在 await 之後，世界可能已經變了，必須確認自己是否還有執行的權限

                # 1. 檢查引擎切換
                if getattr(tts_integration, '_engine_switching', False):
                    logger.info(
                        "Async parallel runner: Engine switch detected after chapter load, aborting.")
                    stopped_due_to_engine_switch = True
                    break

                # 2. 檢查模式切換
                if not app.tts_smooth_mode:
                    logger.info(
                        "Async parallel runner: Detected mode switch to Serial after chapter load, self-terminating.")
                    break

                # 3. 檢查停止訊號
                if tts_integration._async_tts_stop_requested.is_set():
                    logger.info(
                        "Async parallel runner: Stop requested after chapter load, aborting.")
                    break

                if not success:
                    logger.info(
                        "Async runner: Playlist exhausted, no more chapters to load, stopping playback"
                    )
                    app.notify("TTS playback completed.", title="TTS")
                    app.set_tts_status("STOPPED")
                    break
                else:
                    # Wait for playlist to be ready and start initial preloading
                    wait_start_time = time.time()
                    while (
                        time.time() - wait_start_time < 5.0
                    ):  # Wait up to 5 seconds for playlist
                        with tts_integration.tts_lock:
                            current_item = playlist_manager.get_current_item()
                            if current_item:  # Playlist has items
                                break
                        await asyncio.sleep(0.05)

                    # Now restart batch preloading for the new chapter
                    if (
                        app.tts_engine
                        and hasattr(app.tts_engine, "_event_loop")
                        and app.tts_engine._event_loop
                        and not app.tts_engine._event_loop.is_closed()
                    ):
                        try:
                            # 使用統一的橋接器替換直接的 run_coroutine_threadsafe
                            tts_integration.async_bridge.run_async_task(
                                playlist_manager.start_batch_preload(),
                                timeout=2.0,
                                task_name="batch_preload_async_runner",
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to start batch preload in async runner: {e}"
                            )

                    # Wait for batch preloading to start processing items
                    wait_start_time = time.time()
                    while (
                        time.time() - wait_start_time < 5.0
                    ):  # Wait up to 5 seconds for preloaded items
                        with tts_integration.tts_lock:
                            current_item = playlist_manager.get_current_item()
                            # Preloaded item available
                            if current_item and len(current_item) == 3:
                                break
                        await asyncio.sleep(0.05)
                    continue

            with tts_integration.tts_lock:
                if playlist_manager.is_exhausted():
                    break
                current_item = playlist_manager.get_current_item()

            if not current_item:
                break

            if len(current_item) == 3:
                audio = current_item[2]
                if audio == b"CONTENT_FILTERED":
                    # 這個段落被預先過濾為無法發音，改為插入適當的停頓來維持文章節奏
                    text_content = current_item[0]
                    from speakub.utils.text_utils import analyze_punctuation_content

                    pause_type, pause_duration = analyze_punctuation_content(
                        text_content
                    )
                    logger.info(
                        f"Inserting {pause_type} pause ({pause_duration:.1f}s) for non-speakable content: '{text_content[:20]}...'"
                    )

                    # 插入停頓而不是跳過 - 使用 async sleep
                    if pause_duration > 0:
                        await asyncio.sleep(pause_duration)
                        logger.debug(
                            "Async pause completed for punctuation content")

                    # 停頓完成後前進到下一個項目
                    with tts_integration.tts_lock:
                        playlist_manager.advance_index()
                    continue  # 繼續播放循環

                with tts_integration.tts_lock:
                    line_num = current_item[1]
                    if app.viewport_content:
                        page, cursor = divmod(
                            line_num, app.viewport_content.viewport_height
                        )
                        app.viewport_content.current_page = min(
                            page, app.viewport_content.total_pages - 1
                        )
                        lines = len(
                            app.viewport_content.get_current_viewport_lines())
                        app.viewport_content.cursor_in_page = max(
                            0, min(cursor, lines - 1)
                        )
                        # 使用异步执行器更新UI，避免阻塞异步播放任务
                        from asyncio import get_event_loop, to_thread

                        try:
                            await get_event_loop().run_in_executor(
                                None, lambda: app._update_content_display()
                            )
                        except Exception:
                            logger.debug(
                                f"UI update failed in parallel runner: {e}")

                if (
                    app.tts_engine
                    and hasattr(app.tts_engine, "_event_loop")
                    and app.tts_engine._event_loop
                ):
                    playback_completed = False
                    try:
                        # 🔧 **Timer Mode**: 通知 Controller 這項目的持續時間，做定時器觸發
                        if app.tts_smooth_mode and hasattr(playlist_manager, '_predictive_controller'):
                            controller = playlist_manager._predictive_controller
                            if hasattr(controller, 'notify_batch_started'):
                                # 使用 mutagen 計算真實播放時間或估算
                                item_duration = 0.0
                                if hasattr(controller, '_calculate_precise_duration'):
                                    precise_duration = controller._calculate_precise_duration(
                                        audio)
                                    if precise_duration and precise_duration > 0:
                                        item_duration = precise_duration
                                        logger.debug(
                                            f"Timer Mode: Calculated precise duration {item_duration:.2f}s")
                                    else:
                                        # 回到估算：檔案大小 / 比特率
                                        item_duration = len(audio) / 16000.0
                                        logger.debug(
                                            f"Timer Mode: Estimated duration {item_duration:.2f}s")
                                else:
                                    item_duration = len(audio) / 16000.0

                                # 通知 Controller 設置定時器
                                await controller.notify_batch_started(item_duration)

                        # 新方案：不等待播放完成，只啟動播放並在背景中監控
                        # 當需要中斷時，直接停止播放器實例

                        # 啟動音頻播放（非阻塞，背景執行）
                        background_play_future = asyncio.run_coroutine_threadsafe(
                            app.tts_engine.play_audio(audio),
                            app.tts_engine._event_loop,
                        )

                        # 不調用 blocking 的 .result()，而是創建一個監控任務
                        async def monitor_audio_playback_until_completion(
                            tts_integration, future
                        ):
                            """監控音頻播放直到完成"""
                            try:
                                await asyncio.to_thread(lambda: future.result())
                                return "completed"
                            except Exception:
                                logger.debug(
                                    f"Audio playback monitoring failed: {e}")
                                return "failed"

                        play_monitor_task = asyncio.create_task(
                            monitor_audio_playback_until_completion(
                                tts_integration, background_play_future
                            )
                        )
                        tts_integration._tts_active_tasks.add(
                            play_monitor_task)

                        # 同時創建控制信號監控任務
                        async def monitor_control_signals():
                            while True:
                                if tts_integration._async_tts_stop_requested.is_set():
                                    return ("stop_requested", "stop")
                                elif (
                                    tts_integration._async_tts_pause_requested.is_set()
                                ):
                                    return ("pause_requested", "pause")
                                # CPU 優化：將輪詢頻率從 0.1s 降低到 0.5s
                                # 對 UI 響應影響極小，但能大幅降低 CPU 使用率
                                await asyncio.sleep(0.5)

                        control_monitor_task = asyncio.create_task(
                            monitor_control_signals()
                        )
                        tts_integration._tts_active_tasks.add(
                            control_monitor_task)

                        # 等待其中一個任務完成
                        done, pending = await asyncio.wait(
                            [play_monitor_task, control_monitor_task],
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        # 清理掛起的任務
                        for task in pending:
                            task.cancel()
                            try:
                                await task
                            except asyncio.CancelledError:
                                pass

                        # 處理結果
                        if play_monitor_task in done:
                            # 播放正常完成
                            playback_completed = True
                            logger.debug(
                                "Parallel audio playback completed normally")
                        else:
                            # 被控制信號中斷 - 立即停止播放器
                            control_signal = None
                            action_type = None
                            for task in done:
                                if task != play_monitor_task and not task.cancelled():
                                    try:
                                        control_signal, action_type = task.result()
                                    except Exception:
                                        pass
                                    break

                            logger.info(
                                f"Parallel playback interrupted by {control_signal}"
                            )

                            # 立即停止當前的音頻播放
                            try:
                                if (
                                    hasattr(app.tts_engine, "stop")
                                    and app.tts_engine.stop
                                ):
                                    # 如果TTS引擎有stop方法，調用它
                                    stop_future = asyncio.run_coroutine_threadsafe(
                                        app.tts_engine.stop(),
                                        app.tts_engine._event_loop,
                                    )
                                    try:
                                        stop_future.result(
                                            timeout=0.1)  # 等待最多0.1秒
                                    except Exception:
                                        pass  # 停止失敗也無所謂
                                elif (
                                    hasattr(app.tts_engine, "audio_player")
                                    and app.tts_engine.audio_player
                                ):
                                    # 嘗試停止audio_player
                                    try:
                                        app.tts_engine.audio_player.stop()
                                        logger.debug(
                                            "Stopped audio player directly")
                                    except Exception:
                                        logger.debug(
                                            f"Could not stop audio player: {e}"
                                        )
                            except Exception:
                                logger.debug(f"Error stopping TTS engine: {e}")

                            # 取消播放監控任務
                            play_monitor_task.cancel()
                            try:
                                await play_monitor_task
                            except asyncio.CancelledError:
                                pass

                            # 對於停止請求，我們不視為正常播放完成
                            # 對於暫停請求，我們也不視為正常播放完成（因為要中斷）
                            playback_completed = False

                        # 清理任務集
                        tts_integration._tts_active_tasks.discard(
                            play_monitor_task)
                        tts_integration._tts_active_tasks.discard(
                            control_monitor_task)

                    except Exception as e:
                        # Use unified error handler for all exceptions
                        await handle_runner_error(
                            e,
                            "async_parallel_runner_playback",
                            tts_integration,
                            playlist_manager,
                            playlist_manager.get_current_index()
                            if hasattr(playlist_manager, "get_current_index")
                            else None,
                        )
                        break

                    # Only advance to next item if playback completed and not paused/stopped
                    if (
                        playback_completed
                        and not tts_integration._async_tts_stop_requested.is_set()
                        and not tts_integration._async_tts_pause_requested.is_set()
                    ):
                        with tts_integration.tts_lock:
                            # Record playback event for predictive monitoring
                            if hasattr(playlist_manager, "record_playback_event"):
                                text_length = (
                                    len(current_item[0])
                                    if len(current_item) >= 1
                                    else 0
                                )
                                # Note: We don't have exact play time here, using estimated
                                # In a full implementation, this would be measured from the audio player
                                # Use SimpleReservoirController's estimation method
                                if hasattr(playlist_manager, "_predictive_controller"):
                                    estimated_duration = playlist_manager._predictive_controller._estimate_play_duration(
                                        "x" * text_length  # Approximate text length for estimation
                                    )
                                else:
                                    # Fallback estimation: ~3 chars per second
                                    estimated_duration = text_length / 3.0
                                playlist_manager.record_playback_event(
                                    playlist_manager.get_current_index(),
                                    estimated_duration,
                                    text_length,
                                )

                            playlist_manager.advance_index()

                    else:
                        logger.debug(
                            "Async runner: Playback completed but not advancing"
                        )
            else:
                # 檢查播放列表是否已經耗盡
                if playlist_manager.is_exhausted():
                    logger.info(
                        "Async runner: Playlist exhausted during playback wait, stopping playback"
                    )
                    app.notify("TTS playback completed.", title="TTS")
                    app.set_tts_status("STOPPED")
                    break

                # === 🟢 增強版修復：智慧型緩衝區欠載預測與處理 ===
                # Phase 1: Smart content analysis and early detection
                (
                    skip_wait,
                    pause_duration,
                    predicted_underrun,
                ) = await _analyze_content_for_underrun(
                    tts_integration, playlist_manager
                )

                if skip_wait:
                    # Handle non-speakable content immediately
                    if pause_duration > 0:
                        logger.debug(
                            f"Executing immediate pause of {pause_duration}s for skipped content"
                        )
                        await asyncio.sleep(pause_duration)

                    with tts_integration.tts_lock:
                        playlist_manager.advance_index()
                    continue

                # Phase 2: Adaptive prefetching based on prediction
                if predicted_underrun and hasattr(
                    playlist_manager, "_predictive_controller"
                ):
                    await _trigger_adaptive_prefetching(
                        tts_integration, playlist_manager
                    )

                # === 🟢 修復結束 ===

                # === 🎯 Project Empty Cup: 區分初始緩衝與真正 underrun ===
                # 檢查是否為初始緩衝（播放剛開始的正常等待）
                if tts_integration._is_initial_buffering:
                    logger.info(
                        "TTS Initial buffering: Waiting for first audio chunk..."
                    )
                    # 這是正常等待，不記錄 Underrun
                else:
                    # 這才是真正的斷流，使用 notify 彈出訊息
                    app.notify("TTS Underrun detected! (Playback stalled)",
                               title="TTS Warning", severity="warning")

                    # 在 debug 模式下同時記錄到 log
                    if hasattr(app, '_debug') and app._debug:
                        logger.debug(
                            "TTS Underrun detected! (Playback stalled)")
                    # 這才是真正的斷流，需要記錄並觸發懲罰機制

                # Phase 2 Optimization 2: Track underrun wait time for smarter penalties
                underrun_start_time = time.time()

                try:
                    # 階段三：使用真正的不阻塞 await，而非同步適配器的輪詢
                    # 增加超時時間以處理長中文內容
                    await asyncio.wait_for(
                        tts_integration._async_tts_audio_ready.wait(), timeout=90.0
                    )

                    # Calculate wait time for underrun penalty scaling
                    wait_time = time.time() - underrun_start_time

                    # v4.0 "Reservoir": Notify predictive controller of underrun with severity
                    if hasattr(
                        tts_integration.playlist_manager, "_predictive_controller"
                    ):
                        # 只在非初始緩衝時通知 underrun（真正的性能問題）
                        if not tts_integration._is_initial_buffering:
                            tts_integration.playlist_manager._predictive_controller.notify_underrun(
                                wait_time
                            )

                    logger.debug(
                        f"Async runner: Buffer wait resolved in {wait_time:.1f}s"
                    )

                    # 第一次成功收到音頻後，關閉初始緩衝狀態
                    if tts_integration._is_initial_buffering:
                        tts_integration._is_initial_buffering = False
                        logger.debug(
                            "Initial buffering completed, switching to normal underrun detection"
                        )

                except asyncio.TimeoutError:
                    # Get info about what was being synthesized when timeout occurred
                    current_pending_item = None
                    with tts_integration.tts_lock:
                        playlist_manager = tts_integration.playlist_manager
                        current_idx = playlist_manager.get_current_index()
                        if current_idx < playlist_manager.get_playlist_length():
                            item = playlist_manager.get_item_at(current_idx)
                            if item and len(item) == 2:  # Unsynthesized item
                                current_pending_item = item

                    timeout_content = (
                        current_pending_item[0][:100]
                        if current_pending_item
                        else "Unknown"
                    )
                    logger.error(
                        f"Async runner: TTS synthesis timed out after 90 seconds at position {current_idx}. "
                        f"Pending content: '{timeout_content}...'"
                    )
                    logger.debug(
                        f"Debug: TTS synthesis timeout at position {current_idx}, pending content: '{current_pending_item[0][:100]}{'...' if len(current_pending_item[0]) > 100 else ''}'"
                        if current_pending_item
                        else "Debug: TTS synthesis timeout - no pending content info available"
                    )
                    app.notify(
                        "TTS synthesis timed out. Please check your network connection.",
                        title="TTS Error",
                        severity="error",
                    )
                    app.set_tts_status("STOPPED")
                    break

                # 收到信號，繼續循環
                # 階段三：清除事件以便下次等待
                tts_integration._async_tts_audio_ready.clear()
                continue

    finally:
        with tts_integration.tts_lock:
            # 如果因為引擎切換或停止訊號而停止，設置為 STOPPED
            if (
                (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
                and app.tts_status == "PLAYING"
            ):
                app.set_tts_status("STOPPED")


# --- 新增結束 ---


# --- 新增：階段三 serial 模式 async 支援 ---
async def tts_runner_serial_async(tts_integration: "TTSIntegration") -> None:
    """Async version of tts_runner_serial using asyncio.Event (階段三：序列模式 async 化)."""
    app = tts_integration.app
    playlist_manager = tts_integration.playlist_manager

    # 標記停止原因
    stopped_due_to_engine_switch = False

    with tts_integration.tts_lock:
        tts_integration.tts_thread_active = True

    try:
        while not tts_integration._async_tts_stop_requested.is_set():
            # [🔥 關鍵：Main Loop 檢查點] 如果模式已切換到 Smooth，立刻終止
            # 防止 Serial Runner 在 await 完成後繼續執行
            if app.tts_smooth_mode:
                logger.info(
                    "Async serial runner: Mode switched to Smooth at main loop, self-terminating.")
                break

            # [🔥 關鍵：Engine Switch 檢查點] 如果引擎正在切換，停止當前 Runner
            # 當前車完全停止（STOPPED），乘客下車交給下一輛車
            # 下一輛車從停下的位置繼續行駛
            if getattr(tts_integration, '_engine_switching', False):
                logger.info(
                    "Async serial runner: Engine switch detected, stopping runner (STOPPED). Next engine will continue from this point.")
                stopped_due_to_engine_switch = True
                break

            if app.tts_status != "PLAYING":
                break

            with tts_integration.tts_lock:
                exhausted = playlist_manager.is_exhausted()

            if exhausted:
                # [Pre-check] 進入耗時操作前，先檢查一次停止訊號
                if tts_integration._async_tts_stop_requested.is_set():
                    break

                try:
                    # 執行耗時的章節載入操作 (這裡會釋放控制權 await)
                    success = await tts_load_next_chapter_async(playlist_manager)

                    # =========================================================
                    # [🔥 關鍵修復：Post-Await 身分驗證]
                    # 在 await 之後，世界可能已經變了，必須確認自己是否還有權限執行
                    # =========================================================

                    # 1. 檢查停止訊號 (防止單純停止後繼續跑)
                    if tts_integration._async_tts_stop_requested.is_set():
                        logger.info(
                            "Async serial runner: Stop requested after chapter load, aborting.")
                        break

                    # 2. 檢查模式一致性 (防止切換模式後的殭屍復活)
                    # 我是 Serial Runner (Non-smooth)，如果現在 App 變成了 Smooth Mode，
                    # 代表新的 Smooth Runner 已經啟動了，我必須立刻消失。
                    if app.tts_smooth_mode:
                        logger.info(
                            "Async serial runner: Detected mode switch to Smooth, self-terminating.")
                        break

                    # =========================================================

                    if not success:
                        logger.info(
                            "Async serial runner: Playlist exhausted, no more chapters to load, stopping playback"
                        )
                        app.notify("TTS playback completed.", title="TTS")
                        app.set_tts_status("STOPPED")
                        break
                    else:
                        # 只有通過上述所有檢查，才允許跳回迴圈開頭處理新章節
                        continue
                except Exception:
                    logger.error(
                        f"Async serial runner failed to load next chapter: {e}"
                    )
                    app.notify(
                        f"TTS chapter load failed: {e}",
                        title="TTS Error",
                        severity="error",
                    )
                    break

            with tts_integration.tts_lock:
                current_item = playlist_manager.get_current_item()
                if not current_item:
                    break
                text, line_num = current_item[0], current_item[1]

                if app.viewport_content:
                    page, cursor = divmod(
                        line_num, app.viewport_content.viewport_height
                    )
                    app.viewport_content.current_page = min(
                        page, app.viewport_content.total_pages - 1
                    )
                    lines = len(
                        app.viewport_content.get_current_viewport_lines())
                    app.viewport_content.cursor_in_page = max(
                        0, min(cursor, lines - 1))
                    # UI更新需要在非阻塞方式下执行，使用线程池避免阻塞异步任务
                    await asyncio.get_event_loop().run_in_executor(
                        None, lambda: app._update_content_display()
                    )

            if app.tts_engine:
                playback_completed = False
                synthesis_retry_count = 0  # ⭐ 新增：同一項目的重試計數
                max_retries = 3  # ⭐ 同一項目最多重試 3 次

                while synthesis_retry_count < max_retries:
                    try:
                        # 必須在使用 TTS 合成前先移除註腳干擾
                        from speakub.core.content_renderer import ContentRenderer

                        content_renderer = ContentRenderer()
                        tts_cleaned_text = content_renderer.extract_text_for_tts(
                            text)

                        # 事件驅動方式：同時等待TTS播放完成或停止/暫停請求
                        # 使用asyncio.wait實現非阻塞的響應式控制
                        speak_task = asyncio.create_task(
                            asyncio.to_thread(
                                tts_integration.speak_with_engine, tts_cleaned_text
                            )
                        )
                        tts_integration._tts_active_tasks.add(speak_task)

                        # 創建一個虛擬的停止事件等待器（因為asyncio.Event無法直接用於wait）
                        async def wait_for_stop_signal():
                            """等待停止或暫停信號"""
                            while True:
                                if (
                                    tts_integration._async_tts_stop_requested.is_set()
                                    or tts_integration._async_tts_pause_requested.is_set()
                                ):
                                    return "stop_requested"
                                await asyncio.sleep(0.05)  # 短暫檢查間隔

                        stop_waiter_task = asyncio.create_task(
                            wait_for_stop_signal())
                        tts_integration._tts_active_tasks.add(stop_waiter_task)

                        # 使用asyncio.wait實現事件驅動響應
                        done, pending = await asyncio.wait(
                            [speak_task, stop_waiter_task],
                            return_when=asyncio.FIRST_COMPLETED,
                        )

                        # 清理掛起的任務
                        for task in pending:
                            task.cancel()
                            try:
                                await task
                            except asyncio.CancelledError:
                                pass

                        # 根據完成的情況處理結果
                        if speak_task in done and not speak_task.cancelled():
                            # 🔴 **關鍵修復**：檢查任務是否拋出異常，而不是假設完成就成功
                            try:
                                # 嘗試獲取任務結果，如果有異常會在這裡拋出
                                speak_task.result()
                                # TTS播放正常完成（無異常）
                                playback_completed = True
                                logger.debug("TTS playback completed normally")
                                break  # ⭐ 成功 → 跳出重試迴圈
                            except Exception as e:
                                # 任務完成但有異常 → 重試或停止
                                # ⭐ 特殊處理：circuit breaker 打開時不應該重試，應該立即暫停
                                from speakub.tts.circuit_breaker import CircuitBreakerOpenException

                                if isinstance(e, CircuitBreakerOpenException):
                                    logger.error(
                                        f"Circuit breaker is OPEN - TTS service temporarily disabled: {e}"
                                    )
                                    playback_completed = False
                                    # Circuit breaker 已經呼叫了 stop_speaking，但確保狀態設定正確
                                    app.set_tts_status("PLAYING")
                                    await asyncio.sleep(0.1)
                                    app.set_tts_status("PAUSED")
                                    break  # 不要重試，立即暫停

                                synthesis_retry_count += 1
                                logger.error(
                                    f"TTS playback failed (attempt {synthesis_retry_count}/{max_retries}): {e}"
                                )

                                if synthesis_retry_count >= max_retries:
                                    # ⭐ 達到重試次數 → 暫停並停止
                                    logger.error(
                                        f"🚨 CRITICAL: TTS synthesis failed {max_retries} times for item. "
                                        f"Pausing playback at: {text[:50]}..."
                                    )
                                    playback_completed = False
                                    # 確保狀態轉換有效：先到 PLAYING 再到 PAUSED
                                    app.set_tts_status("PLAYING")
                                    await asyncio.sleep(0.1)  # 短暫延遲確保狀態轉換
                                    app.set_tts_status("PAUSED")
                                    break  # ⭐ 停止重試，結束項目處理
                                else:
                                    # ⭐ 未達重試次數 → 重試
                                    logger.info(
                                        f"Retrying synthesis for item (attempt {synthesis_retry_count}/{max_retries})..."
                                    )
                                    # 清理任務後繼續迴圈
                                    tts_integration._tts_active_tasks.discard(
                                        speak_task)
                                    tts_integration._tts_active_tasks.discard(
                                        stop_waiter_task)
                                    # ⭐ 重試前需遵守 smooth_synthesis_delay 設定，避免 IP 被 ban
                                    from speakub.utils.config import get_smooth_synthesis_delay
                                    delay = get_smooth_synthesis_delay(
                                        app.tts_engine)
                                    logger.debug(
                                        f"Applying smooth_synthesis_delay ({delay}s) before retry")
                                    await asyncio.sleep(delay)
                                    continue
                        else:
                            # 被停止信號中斷
                            stop_reason = (
                                "stop_requested"
                                in [task.result() for task in done if task != speak_task]
                                if done
                                else "unknown"
                            )
                            logger.info(
                                f"TTS playback interrupted by {stop_reason}")
                            if speak_task in pending:
                                speak_task.cancel()
                                try:
                                    await speak_task
                                except asyncio.CancelledError:
                                    logger.debug(
                                        "TTS task cancelled due to stop/pause")
                            break  # ⭐ 被用戶停止 → 跳出重試迴圈

                        # 清理任務集
                        tts_integration._tts_active_tasks.discard(speak_task)
                        tts_integration._tts_active_tasks.discard(
                            stop_waiter_task)

                    except asyncio.CancelledError:
                        # 任務被取消，繼續到下一個檢查點
                        logger.debug(
                            "Serial async runner: Speech was cancelled")

                        # [🔥 FIX] Check if this is an engine switch cancellation
                        if getattr(tts_integration, '_engine_switching', False):
                            stopped_due_to_engine_switch = True
                            logger.info(
                                "Async serial runner: Cancelled due to engine switch.")

                        # Must exit the runner to prevent continuing with an invalid state (empty playlist)
                        # Returning here ensures we hit the finally block immediately
                        return

                    except (
                        socket.gaierror,
                        socket.timeout,
                        ConnectionError,
                        OSError,
                    ) as e:
                        tts_integration.network_manager.handle_network_error(
                            e, "async_serial_runner"
                        )
                        break
                    except Exception:
                        # Let speak_with_engine handle all TTS-related errors
                        break

                # Only advance to next item if playback completed and not paused
                if (
                    playback_completed
                    and not tts_integration._async_tts_stop_requested.is_set()
                ):
                    with tts_integration.tts_lock:
                        playlist_manager.advance_index()

    finally:
        with tts_integration.tts_lock:
            # 如果因為引擎切換而停止，或停止信號被設置，則設置為 STOPPED
            if (
                (stopped_due_to_engine_switch or tts_integration._async_tts_stop_requested.is_set())
                and app.tts_status == "PLAYING"
            ):
                app.set_tts_status("STOPPED")


# --- 新增結束 ---


# Legacy synchronous runners removed in Stage 4 - replaced by async versions


def find_and_play_next_chapter_worker(tts_integration: "TTSIntegration") -> None:
    """Worker to find and play next chapter."""
    app = tts_integration.app
    if tts_integration.playlist_manager.load_next_chapter():
        tts_integration.start_tts_thread()
    else:
        app.call_from_thread(
            app.notify, "No more content to read.", title="TTS")
        app.set_tts_status("STOPPED")


# Legacy synchronous parallel runner removed in Stage 4 - replaced by async version


def tts_pre_synthesis_worker(tts_integration: "TTSIntegration") -> None:
    """Worker thread that synthesizes text ahead of time for smooth mode."""
    app = tts_integration.app
    playlist_manager = tts_integration.playlist_manager
    config_manager = ConfigManager()  # Create local ConfigManager instance
    while not tts_integration.tts_stop_requested.is_set():
        try:
            text_to_synthesize = None
            target_index = -1
            with tts_integration.tts_lock:
                current_idx = playlist_manager.get_current_index()
                limit = min(playlist_manager.get_playlist_length(),
                            current_idx + 3)
            for i in range(current_idx, limit):
                with tts_integration.tts_lock:
                    item = playlist_manager.get_item_at(i)
                    if item and len(item) == 2:
                        text_to_synthesize = item[0]
                        target_index = i
                        break
            if (
                text_to_synthesize
                and app.tts_engine
                and hasattr(app.tts_engine, "synthesize")
                and hasattr(app.tts_engine, "_event_loop")
                and app.tts_engine._event_loop
            ):
                # --- 新增內容預先過濾邏輯 ---
                # Only apply filtering to engines that need it (Edge-TTS, Nanmai)
                # gTTS can handle all content correctly, so skip filtering for it
                current_engine = config_manager.get(
                    "tts.preferred_engine", "edge-tts")
                needs_filtering = current_engine in ("edge-tts", "nanmai")

                if needs_filtering:
                    from speakub.utils.text_utils import is_speakable_content

                    speakable, reason = is_speakable_content(
                        text_to_synthesize)
                    if not speakable:
                        logger.info(
                            f"Skipping non-speakable content in pre-synthesis (reason: {reason})"
                        )
                        # Mark as filtered out content - will be skipped silently during playback
                        with tts_integration.tts_lock:
                            item = playlist_manager.get_item_at(target_index)
                            if item and len(item) == 2:
                                new_item = (item[0], item[1],
                                            b"CONTENT_FILTERED")
                                playlist_manager.update_item_at(
                                    target_index, new_item)
                        tts_integration.tts_synthesis_ready.set()
                        continue  # Skip synthesis for non-speakable content
                else:
                    # --- 原有的合成邏輯 ---
                    # Initialize variables at function scope to avoid "cannot access local variable" errors
                    audio_data = b"ERROR"
                    synthesis_success = False
                    last_synthesis_error = (
                        None  # Track the last error for pause notification
                    )

                    # Apply retry logic for very short fragments
                    max_retries = 4 if reason == "very_short_fragment" else 2
                    retry_delay = 0.5

                    for attempt in range(max_retries):
                        try:
                            rate_str = f"{app.tts_rate:+}%"
                            volume_str = f"{app.tts_volume - 100:+}%"

                            # 必須在使用 TTS 合成前先移除註腳干擾
                            from speakub.core.content_renderer import ContentRenderer

                            content_renderer = ContentRenderer()
                            tts_cleaned_text = content_renderer.extract_text_for_tts(
                                text_to_synthesize
                            )
                            corrected_text = correct_chinese_pronunciation(
                                tts_cleaned_text
                            )
                            # Add delay before synthesis to prevent rate limiting
                            # Use engine-specific delay if available
                            current_engine = config_manager.get(
                                "tts.preferred_engine", "edge-tts"
                            )
                            synthesis_delay = get_smooth_synthesis_delay(
                                current_engine)
                            time.sleep(synthesis_delay)
                            future = asyncio.run_coroutine_threadsafe(
                                app.tts_engine.synthesize(
                                    corrected_text,
                                    rate=rate_str,
                                    volume=volume_str,
                                    pitch=app.tts_pitch,
                                ),
                                app.tts_engine._event_loop,
                            )
                            audio_data = future.result(timeout=60)
                            if audio_data is not None and audio_data != b"ERROR":
                                synthesis_success = True
                                break  # Success, exit retry loop
                            else:
                                if (
                                    attempt < max_retries - 1
                                ):  # Don't delay on last attempt
                                    time.sleep(retry_delay)
                        except (
                            socket.gaierror,
                            socket.timeout,
                            ConnectionError,
                            OSError,
                        ) as e:
                            tts_integration.network_manager.handle_network_error(
                                e, "synthesis_worker"
                            )
                            break
                        except NoAudioReceived as e:
                            # Check if this is expected behavior for non-speakable content
                            from speakub.utils.text_utils import is_speakable_content

                            current_speakable, current_reason = is_speakable_content(
                                text_to_synthesize
                            )

                            if not current_speakable:
                                # This is expected - Edge-TTS correctly returns no audio for punctuation-only content
                                logger.debug(
                                    f"No audio received for non-speakable content (reason: {current_reason}): '{text_to_synthesize[:20]}...'"
                                )
                                # Mark as filtered content - will be skipped silently during playback
                                with tts_integration.tts_lock:
                                    item = playlist_manager.get_item_at(
                                        target_index)
                                    if item and len(item) == 2:
                                        new_item = (
                                            item[0],
                                            item[1],
                                            b"CONTENT_FILTERED",
                                        )
                                        playlist_manager.update_item_at(
                                            target_index, new_item
                                        )
                                tts_integration.tts_synthesis_ready.set()
                                break  # Exit retry loop successfully
                            else:
                                # Unexpected NoAudioReceived for speakable content - this is an error
                                logger.warning(
                                    f"Attempt {attempt + 1}/{max_retries}: "
                                    f"EdgeTTS returned no audio for speakable content during pre-synthesis (reason: {reason}). "
                                    f"{'Retrying' if attempt < max_retries - 1 else 'Marking as failed'}"
                                )
                                logger.debug(
                                    f"Debug: Batch synthesis failed at position {target_index}, failed content: '{text_to_synthesize[:100]}{'...' if len(text_to_synthesize) > 100 else ''}'"
                                )
                                last_synthesis_error = e
                                if attempt < max_retries - 1:
                                    time.sleep(retry_delay)
                                else:
                                    audio_data = b"FAILED_SYNTHESIS"
                                    synthesis_success = False
                        except Exception as e:
                            logger.warning(
                                f"Synthesis error in pre-synthesis worker (attempt {attempt + 1}): {e}"
                            )
                            logger.debug(
                                f"Debug: Batch synthesis failed at position {target_index}, failed content: '{text_to_synthesize[:100]}{'...' if len(text_to_synthesize) > 100 else ''}'"
                            )
                            last_synthesis_error = e
                            if attempt < max_retries - 1:
                                time.sleep(retry_delay)
                            else:
                                audio_data = b"FAILED_SYNTHESIS"
                                synthesis_success = False

                    # 如果所有重試都失敗，通知使用者並將狀態設為 STOPPED
                    if not synthesis_success:
                        logger.error(
                            f"All synthesis retries failed at index {target_index}. Stopping playback."
                        )
                        if last_synthesis_error:
                            app.notify(
                                f"TTS synthesis failed after multiple retries and has been stopped.\nError: {type(last_synthesis_error).__name__}",
                                title="TTS Error",
                                severity="error",
                            )
                        # 將狀態設為 STOPPED 並退出 worker
                        app.set_tts_status("STOPPED")
                        break

                # 只有在內容可發音時才更新播放列表
                # (不可發音的內容已在 NoAudioReceived 處理中被標記為 CONTENT_FILTERED)
                # 並且合成必須成功 (如果失敗，上面的 break 已經終止了 worker)
                if speakable and synthesis_success:
                    with tts_integration.tts_lock:
                        item = playlist_manager.get_item_at(target_index)
                        if item and len(item) == 2:
                            new_item = (item[0], item[1], audio_data)
                            playlist_manager.update_item_at(
                                target_index, new_item)
                    tts_integration.tts_synthesis_ready.set()
            else:
                tts_integration.tts_data_available.clear()
                data_available = tts_integration.tts_data_available.wait(
                    timeout=0.2)
                if not data_available:
                    time.sleep(0.1)
        except (socket.gaierror, socket.timeout) as e:
            logger.error("Network error in TTS pre-synthesis worker: %s", e)
            time.sleep(1)
        except asyncio.TimeoutError as e:
            logger.error(
                "TTS synthesis timeout in pre-synthesis worker: %s", e)
            time.sleep(1)
        except Exception:
            logger.exception("Unexpected error in TTS pre-synthesis worker")
            time.sleep(1)


# === 增強版緩衝區欠載處理輔助函數 ===


async def _analyze_content_for_underrun(
    tts_integration: "TTSIntegration", playlist_manager
) -> tuple[bool, float, bool]:
    """
    智慧型內容分析，用於預測和處理緩衝區欠載。

    Returns:
        tuple: (skip_wait, pause_duration, predicted_underrun)
        - skip_wait: 是否應跳過等待（處理不可發音內容）
        - pause_duration: 停頓時間（如果適用）
        - predicted_underrun: 是否預測會發生欠載
    """
    skip_wait = False
    pause_duration = 0.0
    predicted_underrun = False

    try:
        with tts_integration.tts_lock:
            current_item = playlist_manager.get_current_item()
            if not current_item or len(current_item) != 2:
                return skip_wait, pause_duration, predicted_underrun

            text_content = current_item[0]

        # Phase 1: Check for non-speakable content (immediate handling)
        from speakub.utils.text_utils import (
            analyze_punctuation_content,
            is_speakable_content,
        )

        speakable, reason = is_speakable_content(text_content)

        if not speakable:
            logger.info(
                f"[SmartAnalysis] Detected non-speakable content: '{text_content[:20]}...' "
                f"(reason: {reason}). Handling immediately."
            )

            # Calculate pause duration for punctuation content
            _, pause_duration = analyze_punctuation_content(text_content)
            skip_wait = True

            # Mark as filtered content
            with tts_integration.tts_lock:
                new_item = (current_item[0],
                            current_item[1], b"CONTENT_FILTERED")
                playlist_manager.update_item_at(
                    playlist_manager.get_current_index(), new_item
                )

            return skip_wait, pause_duration, predicted_underrun

        # Phase 2: Predict potential underrun based on content characteristics
        predicted_underrun = _predict_underrun_risk(
            text_content, tts_integration)

        if predicted_underrun:
            logger.debug(
                f"[SmartAnalysis] Predicted underrun risk for content: '{text_content[:30]}...'"
            )

    except Exception as e:
        logger.warning(f"Error in content analysis for underrun: {e}")
        # On error, default to normal processing
        predicted_underrun = True

    return skip_wait, pause_duration, predicted_underrun


def _predict_underrun_risk(
    text_content: str, tts_integration: "TTSIntegration"
) -> bool:
    """
    基於內容特性預測欠載風險。

    Returns:
        True if underrun is predicted, False otherwise
    """
    try:
        # Factor 1: Content length (very short content may cause issues)
        if len(text_content.strip()) < 3:
            return True

        # Factor 2: Special characters that may cause synthesis issues
        special_chars_ratio = sum(
            1 for c in text_content if not c.isalnum() and not c.isspace()
        ) / len(text_content)
        if special_chars_ratio > 0.5:  # High special character ratio
            return True

        # Factor 3: Check for problematic patterns
        problematic_patterns = [
            r"^[^\w]*$",  # Only non-word characters
            r"^\d+(\.\d+)?[^\w]*$",  # Numbers with minimal text
            r"^[^\w\s]{3,}$",  # Sequences of symbols
        ]

        import re

        for pattern in problematic_patterns:
            if re.match(pattern, text_content.strip()):
                return True

        # Factor 4: Historical underrun patterns (if available)
        if hasattr(tts_integration.playlist_manager, "_predictive_controller"):
            controller = tts_integration.playlist_manager._predictive_controller
            if hasattr(controller, "predict_underrun_risk"):
                try:
                    return controller.predict_underrun_risk(text_content)
                except Exception:
                    pass  # Fall back to static analysis

    except Exception as e:
        logger.debug(f"Error predicting underrun risk: {e}")

    return False  # Default: no predicted risk


async def _trigger_adaptive_prefetching(
    tts_integration: "TTSIntegration", playlist_manager
) -> None:
    """
    基於欠載預測觸發適應性預先擷取。
    """
    try:
        if not hasattr(playlist_manager, "_predictive_controller"):
            return

        controller = playlist_manager._predictive_controller

        # Increase prefetch intensity when underrun is predicted
        if hasattr(controller, "increase_prefetch_intensity"):
            await asyncio.to_thread(controller.increase_prefetch_intensity)

        # Trigger immediate prefetch for upcoming items
        if hasattr(controller, "trigger_immediate_prefetch"):
            # Prefetch next 5 items
            await asyncio.to_thread(controller.trigger_immediate_prefetch, 5)

        logger.debug(
            "Adaptive prefetching triggered due to predicted underrun")

    except Exception as e:
        logger.warning(f"Error triggering adaptive prefetching: {e}")


# === 增強版緩衝區欠載處理輔助函數結束 ===
