"""
Playback Manager for TTS in SpeakUB.
Handles playback thread lifecycle using asyncio for efficiency.
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration
    from speakub.tts.playlist_manager import PlaylistManager

logger = logging.getLogger(__name__)


class PlaybackManager:
    """Manages TTS playback thread lifecycle using asyncio.to_thread."""

    # Constants for better maintainability
    FUTURE_TIMEOUT_SECONDS = 2.0

    def __init__(
        self, tts_integration: "TTSIntegration", playlist_manager: "PlaylistManager"
    ):
        self.tts_integration = tts_integration
        self.app = tts_integration.app
        self.stop_event = tts_integration._async_tts_stop_requested
        self.playlist_manager = playlist_manager  # Direct reference
        self.lock = tts_integration._tts_lock

        # Migrate to asyncio: use Task instead of ThreadPoolExecutor
        # Remove ThreadPoolExecutor and use asyncio.to_thread for blocking operations
        self._current_task: asyncio.Task | None = None
        self._task_lock = asyncio.Lock()

    async def start_playback_async(self) -> None:
        """Start TTS playback using asyncio.to_thread."""
        async with self._task_lock:
            if (
                self.is_playing()
                or self._current_task
                and not self._current_task.done()
            ):
                return

            self.stop_event.clear()
            self.tts_integration._async_tts_pause_requested.clear()

            self.app.set_tts_status("PLAYING")
            self.tts_integration.tts_thread_active = True

            # 🔒 Fusion Reservoir 只在 smooth mode 下啟動
            if self.app.tts_smooth_mode:
                # v4.0 "Reservoir": Resume predictive controller timers on start/resume
                if hasattr(self.playlist_manager, "_predictive_controller"):
                    self.playlist_manager._predictive_controller.resume_scheduling()

                # ✅ 新增：Kickstart 控制器
                if hasattr(self.playlist_manager, "_predictive_controller"):
                    controller = self.playlist_manager._predictive_controller
                    await controller.start_monitoring()
                    # 立即觸發一次，不用等初始延遲
                    asyncio.create_task(
                        controller.plan_and_schedule_next_trigger(0.1))

            # Start the appropriate runner based on smooth mode
            if self.app.tts_smooth_mode:
                # Start batch preload worker first for smooth mode
                if (
                    self.app.tts_engine
                    and hasattr(self.app.tts_engine, "_event_loop")
                    and self.app.tts_engine._event_loop
                    and not self.app.tts_engine._event_loop.is_closed()
                ):
                    try:
                        # 使用統一的橋接器替換直接的 run_coroutine_threadsafe
                        self.tts_integration.async_bridge.run_async_task(
                            self.playlist_manager.start_batch_preload(),
                            timeout=2.0,
                            task_name="batch_preload_start",
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to start batch preload in start_playback: {e}"
                        )

                # Use async parallel runner for smooth mode
                from speakub.tts.ui.runners import tts_runner_parallel_async

                logger.debug("Using async parallel runner for smooth mode")
                self._current_task = asyncio.create_task(
                    tts_runner_parallel_async(self.tts_integration)
                )
            else:
                # Use async serial runner for standard mode
                from speakub.tts.ui.runners import tts_runner_serial_async

                logger.debug("Using async serial runner for standard mode")
                self._current_task = asyncio.create_task(
                    tts_runner_serial_async(self.tts_integration)
                )

    def start_playback(self) -> None:
        """Start TTS playback - wrapper for async method."""
        try:
            # Check if we're in an event loop
            loop = asyncio.get_running_loop()  # noqa: F841 # Future use possible
            # Create task for start_playback_async
            asyncio.create_task(self.start_playback_async())
        except RuntimeError:
            # No running loop, create new one
            asyncio.run(self.start_playback_async())

    async def stop_playback_async(self, is_pause: bool = False) -> None:
        """Stop TTS playback asynchronously."""
        async with self._task_lock:
            if (
                not self.tts_integration.tts_thread_active
                and self.app.tts_status != "PAUSED"
            ):
                return

            self.stop_event.set()

            if self.app.tts_engine:
                try:
                    # Distinguish between pause and stop operations
                    if is_pause:
                        # For pause, call pause() which only pauses playback without cleanup
                        if hasattr(self.app.tts_engine, "pause"):
                            self.app.tts_engine.pause()
                    else:
                        # For stop, call stop() which stops and cleans up resources
                        if hasattr(self.app.tts_engine, "stop"):
                            self.app.tts_engine.stop()
                except Exception as e:
                    logger.warning(f"Error in TTS engine operation: {e}")

            # Cancel the current task if it exists
            if self._current_task and not self._current_task.done():
                logger.debug("Cancelling TTS task...")
                self._current_task.cancel()
                try:
                    await asyncio.wait_for(
                        self._current_task, timeout=self.FUTURE_TIMEOUT_SECONDS
                    )
                except (asyncio.TimeoutError, asyncio.CancelledError):
                    logger.debug("TTS task cancelled or timed out")

            self.tts_integration.tts_thread_active = False
            self.app.set_tts_status("PAUSED" if is_pause else "STOPPED")

            if not is_pause:
                # Stop predictive controller before resetting playlist manager
                if (
                    hasattr(self.playlist_manager, "_predictive_controller")
                    and self.playlist_manager._predictive_controller
                    and self.app.tts_engine
                    and hasattr(self.app.tts_engine, "_event_loop")
                    and self.app.tts_engine._event_loop
                    and not self.app.tts_engine._event_loop.is_closed()
                ):
                    try:
                        # 使用統一的橋接器替換直接的 run_coroutine_threadsafe
                        self.tts_integration.async_bridge.run_async_task(
                            self.playlist_manager._predictive_controller.stop_monitoring(),
                            timeout=2.0,
                            task_name="predictive_controller_stop",
                        )
                        logger.debug(
                            "Stopped predictive controller during playback stop"
                        )
                    except Exception as e:
                        logger.warning(
                            f"Failed to stop predictive controller: {e}")

                self.playlist_manager.reset()
                self._current_task = None

    def stop_playback(self, is_pause: bool = False) -> None:
        """Stop TTS playback - wrapper for async method."""
        try:
            # Check if we're in an event loop
            loop = asyncio.get_running_loop()  # noqa: F841 # Future use possible
            # Create task for stop_playbook_async
            asyncio.create_task(self.stop_playback_async(is_pause))
        except RuntimeError:
            # No running loop, create new one
            asyncio.run(self.stop_playback_async(is_pause))

    def pause_playback(self) -> None:
        """Pause TTS playback - stop the task to simulate pause."""
        # For pause, simply call stop with is_pause=True
        # The task will be cancelled but TTS status will remain as PAUSED
        self.stop_playback(is_pause=True)

    def is_playing(self) -> bool:
        """Check if playback is active by checking current task."""
        return (
            self._current_task is not None
            and not self._current_task.done()
            and self.tts_integration.tts_thread_active
        )

    async def shutdown_async(self) -> None:
        """Shutdown playback manager asynchronously."""
        logger.debug("Shutting down TTS playback manager.")
        self.stop_event.set()

        # Cancel the current task if it exists
        if self._current_task and not self._current_task.done():
            logger.debug("Cancelling current TTS task during shutdown...")
            self._current_task.cancel()
            try:
                await asyncio.wait_for(
                    self._current_task, timeout=self.FUTURE_TIMEOUT_SECONDS
                )
            except (asyncio.TimeoutError, asyncio.CancelledError):
                logger.debug("TTS task cancelled during shutdown")

        # Reset state
        self.tts_integration.tts_thread_active = False
        self.app.set_tts_status("STOPPED")
        self._current_task = None

        logger.debug("TTS playback manager shutdown completed.")

    def shutdown(self) -> None:
        """Shutdown playback manager - wrapper for async method."""
        try:
            # Check if we're in an event loop
            loop = asyncio.get_running_loop()  # noqa: F841 # Future use possible
            # Create task for shutdown_async
            asyncio.create_task(self.shutdown_async())
        except RuntimeError:
            # No running loop, create new one
            asyncio.run(self.shutdown_async())
