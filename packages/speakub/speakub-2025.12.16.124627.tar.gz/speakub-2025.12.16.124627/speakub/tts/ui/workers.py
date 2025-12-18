#!/usr/bin/env python3
"""
TTS Workers - 分離的後台工作器
實現明確的層次隔離
"""

import asyncio
import logging
import threading
from typing import TYPE_CHECKING, Optional

from speakub.core.threading_model import get_threading_model
from speakub.tts.ui.commands import get_command_queue, get_state_manager

if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration

logger = logging.getLogger(__name__)


class SynthesisWorker:
    """
    後台合成工作器 - 純異步 I/O 處理

    責任：
    - 處理 TTS 合成（異步 I/O）
    - 管理合成隊列
    - 不涉及任何 HMI 操作

    線程：異步工作線程
    """

    def __init__(self, tts_integration: "TTSIntegration"):
        self.tts_integration = tts_integration
        self.audio_queue = asyncio.Queue()
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """啟動合成工作器"""
        if self.running:
            return

        self.running = True
        self._task = asyncio.create_task(self._synthesis_loop())
        logger.info("Synthesis worker started")

    async def stop(self) -> None:
        """停止合成工作器"""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Synthesis worker stopped")

    async def _synthesis_loop(self) -> None:
        """合成循環 - 只處理 I/O"""
        while self.running:
            try:
                # 等待下一個要合成的文本
                text_item = await self._get_next_text()

                if not text_item:
                    await asyncio.sleep(0.1)
                    continue

                text, line_num = text_item

                # 異步合成（I/O bound）
                audio_data = await self._synthesize_text(text)

                if audio_data:
                    # 放入隊列，交給播放協調器處理
                    await self.audio_queue.put((audio_data, line_num))
                    logger.debug(f"Synthesized audio for line {line_num}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Synthesis error: {e}")
                await asyncio.sleep(1.0)  # 錯誤後暫停

    async def _get_next_text(self):
        """獲取下一個要合成的文本"""
        # 從 playlist manager 獲取待合成項目
        with self.tts_integration.tts_lock:
            playlist_manager = self.tts_integration.playlist_manager
            current_idx = playlist_manager.get_current_index()

            # 查找下一個未合成的項目
            for i in range(current_idx, playlist_manager.get_playlist_length()):
                item = playlist_manager.get_item_at(i)
                if item and len(item) == 2:  # (text, line_num)
                    return item

        return None

    async def _synthesize_text(self, text: str) -> Optional[bytes]:
        """異步合成文本"""
        try:
            if not self.tts_integration.app.tts_engine:
                return None

            # 在線程池中執行同步合成（因為 TTS 引擎可能是同步的）
            audio_data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._sync_synthesize(text)
            )

            return audio_data

        except Exception as e:
            logger.error(f"Text synthesis failed: {e}")
            return None

    def _sync_synthesize(self, text: str) -> Optional[bytes]:
        """同步合成（在線程池中執行）"""
        try:
            # 清理文本
            from speakub.core.content_renderer import ContentRenderer

            content_renderer = ContentRenderer()
            cleaned_text = content_renderer.extract_text_for_tts(text)

            # 修正發音
            from speakub.utils.text_utils import correct_chinese_pronunciation

            corrected_text = correct_chinese_pronunciation(cleaned_text)

            # 準備參數
            kwargs = self.tts_integration._prepare_tts_engine_kwargs()

            # 合成
            self.tts_integration._execute_tts_synthesis(corrected_text, kwargs)

            # 注意：這裡需要修改，因為 _execute_tts_synthesis 不返回值
            # 實際實現需要根據具體的 TTS 引擎調整
            return b"dummy_audio_data"  # 臨時返回值

        except Exception as e:
            logger.error(f"Sync synthesis failed: {e}")
            return None


class PlaybackCoordinator:
    """
    播放協調器 - 專用線程處理 HMI 播放

    責任：
    - 在專用線程中處理音頻播放
    - 從合成工作器接收音頻數據
    - 執行 blocking 的 HMI 操作
    - 與 UI 狀態同步

    線程：專用播放線程
    """

    def __init__(
        self, tts_integration: "TTSIntegration", synthesis_worker: "SynthesisWorker"
    ):
        self.tts_integration = tts_integration
        self.synthesis_worker = synthesis_worker
        self.audio_player = AudioPlayer()
        self.running = False
        self._thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # 引用其他組件
        self.threading_model = get_threading_model()
        self.command_queue = get_command_queue()
        self.state_manager = get_state_manager()

    def start(self) -> None:
        """啟動播放協調器"""
        if self.running:
            return

        self.running = True
        self._shutdown_event.clear()

        self._thread = threading.Thread(
            target=self._playback_loop, name="TTS-Playback-Coordinator", daemon=True
        )
        self._thread.start()

        # 註冊命令處理器
        self.command_queue.register_handler(
            "toggle_playback", self._handle_toggle_playback
        )
        self.command_queue.register_handler("stop", self._handle_stop)
        self.command_queue.register_handler("pause", self._handle_pause)

        logger.info("Playback coordinator started")

    def stop(self) -> None:
        """停止播放協調器"""
        self.running = False
        self._shutdown_event.set()

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                logger.warning("Playback coordinator thread did not stop gracefully")

        logger.info("Playback coordinator stopped")

    def _playback_loop(self) -> None:
        """播放循環 - blocking 是正確的"""
        logger.info("Playback loop started")

        while not self._shutdown_event.is_set():
            try:
                # 等待音頻數據（blocking）
                audio_data, line_num = self._wait_for_audio()

                if not audio_data:
                    continue

                # 更新 UI 狀態（安全的方式）
                if line_num is not None:
                    self._update_ui_position(line_num)

                # HMI 播放 - blocking 是正確的！
                self.audio_player.play(audio_data)

                # 播放完成後推進
                self._advance_playlist()

            except Exception as e:
                logger.error(f"Playback error: {e}")
                threading.Event().wait(1.0)  # 錯誤後暫停

        logger.info("Playback loop stopped")

    def _wait_for_audio(self) -> tuple[Optional[bytes], Optional[int]]:
        """等待音頻數據"""
        try:
            # 從異步隊列獲取數據
            if self.threading_model.async_loop:
                future = asyncio.run_coroutine_threadsafe(
                    self.synthesis_worker.audio_queue.get(),
                    self.threading_model.async_loop,
                )
                return future.result(timeout=5.0)
            else:
                logger.error("Async loop not available")
                return None, None
        except Exception as e:
            logger.debug(f"Waiting for audio timed out: {e}")
            return None, None

    def _update_ui_position(self, line_num: int) -> None:
        """安全更新 UI 位置"""
        # 使用狀態管理器或者 call_from_thread 更新 UI
        # 這裡需要與具體 UI 框架集成
        pass

    def _advance_playlist(self) -> None:
        """推進播放列表"""
        with self.tts_integration.tts_lock:
            self.tts_integration.playlist_manager.advance_index()

    def _handle_toggle_playback(self) -> None:
        """處理播放/暫停切換"""
        current_state = self.state_manager.get_state()

        if current_state == "PLAYING":
            self._handle_pause()
        elif current_state in ["PAUSED", "IDLE"]:
            self._handle_resume()

    def _handle_stop(self) -> None:
        """處理停止"""
        self.audio_player.stop()
        self.state_manager.set_state("STOPPED")

    def _handle_pause(self) -> None:
        """處理暫停"""
        self.audio_player.pause()
        self.state_manager.set_state("PAUSED")

    def _handle_resume(self) -> None:
        """處理恢復"""
        # 恢復邏輯
        self.state_manager.set_state("PLAYING")


class AudioPlayer:
    """
    音頻播放器 - HMI 層組件

    責任：
    - 執行 blocking 的音頻播放
    - 提供播放控制接口
    - 在專用線程中運行
    """

    def __init__(self):
        self._current_audio_backend = None
        self._is_paused = False

    def play(self, audio_data: bytes) -> None:
        """播放音頻 - blocking 操作"""
        if not self._current_audio_backend:
            self._initialize_backend()

        if self._current_audio_backend:
            # blocking 播放 - 這是正確的！
            self._current_audio_backend.play(audio_data)
        else:
            logger.error("No audio backend available")

    def pause(self) -> None:
        """暫停播放"""
        if self._current_audio_backend:
            self._current_audio_backend.pause()
        self._is_paused = True

    def resume(self) -> None:
        """恢復播放"""
        if self._current_audio_backend:
            self._current_audio_backend.resume()
        self._is_paused = False

    def stop(self) -> None:
        """停止播放"""
        if self._current_audio_backend:
            self._current_audio_backend.stop()
        self._is_paused = False

    def _initialize_backend(self) -> None:
        """初始化音頻後端"""
        # 根據配置選擇後端
        # 這裡需要與 TTS integration 集成
        pass
