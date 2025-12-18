#!/usr/bin/env python3
"""
TTSEngineManager - Manages TTS engine lifecycle and switching.
"""

import asyncio
import logging
from typing import TYPE_CHECKING, Dict, Optional

from speakub.utils.config import ConfigManager

if TYPE_CHECKING:
    from .engine import TTSEngine

logger = logging.getLogger(__name__)


class TTSEngineManager:
    """Manages TTS engine lifecycle including loading, switching, and unloading."""

    def __init__(self, config_manager=None):
        """Initialize the engine manager."""
        self.config_manager = config_manager or ConfigManager()
        self._current_engine: Optional["TTSEngine"] = None
        self._available_engines = {
            "edge-tts": "EdgeTTSProvider",
            "gtts": "GTTSProvider",
            "nanmai": "NanmaiTTSProvider",
        }

    def get_current_engine(self) -> Optional["TTSEngine"]:
        """Get the currently active TTS engine."""
        return self._current_engine

    def set_engine(self, engine: "TTSEngine") -> None:
        """Set the current engine directly."""
        self._current_engine = engine

    async def switch_engine(
        self, new_engine_name: str, tts_integration=None, old_engine=None
    ) -> bool:
        """
        Switch to a new TTS engine, handling complete lifecycle cleanup.

        Args:
            new_engine_name: Name of the new engine (e.g., "edge-tts", "gtts", "nanmai")
            tts_integration: TTSIntegration instance for app access
            old_engine: The current engine to cleanup (optional)

        Returns:
            bool: True if switch was successful
        """
        logger.info(f"Switching to TTS engine: {new_engine_name}")

        # [🔥 關鍵修復] 設置引擎切換標記，防止 Serial Runner 在切換期間跳章
        if tts_integration:
            tts_integration._engine_switching = True

        try:
            app = tts_integration.app if tts_integration else None

            # [🔥 關鍵修復] STOPPED 就是立即清除解除當前任務
            # 不要等待，立即清理
            if old_engine and app:
                try:
                    logger.info(
                        "Engine switching: STOPPED - clearing active tasks immediately"
                    )

                    # 立即清除所有活躍的 speak_task，不等待
                    if hasattr(tts_integration, '_tts_active_tasks') and tts_integration._tts_active_tasks:
                        pending_tasks = list(tts_integration._tts_active_tasks)
                        if pending_tasks:
                            logger.info(
                                f"Clearing {len(pending_tasks)} active TTS tasks immediately"
                            )
                            # 強制取消所有任務
                            for task in pending_tasks:
                                if not task.done():
                                    task.cancel()

                            # 清空列表
                            tts_integration._tts_active_tasks.clear()
                            logger.info("All active tasks cleared")

                    # 現在乘客已下車，可以進行引擎切換
                    logger.info(
                        "Tasks cleared: engine switch can proceed")

                except Exception as e:
                    logger.warning(
                        f"Error during task clearing: {e}")

            # Perform deep cleanup of old engine
            await self._cleanup_engine(
                old_engine or self._current_engine, tts_integration
            )

            # Reset Predictive Controller for engine switch (關鍵修復)
            if tts_integration and hasattr(tts_integration, "playlist_manager"):
                playlist_manager = tts_integration.playlist_manager
                controller = getattr(
                    playlist_manager, "_predictive_controller", None)
                if controller and hasattr(controller, "reset_for_engine_switch"):
                    controller.reset_for_engine_switch(new_engine_name)
                    logger.debug(
                        f"Reset Predictive Controller for {new_engine_name}")

            # Update configuration
            self.config_manager.set_override(
                "tts.preferred_engine", new_engine_name)
            self.config_manager.save_to_file()

            # [🔥 關鍵限制] GTTS 只能在 non-smooth mode 下運作
            # 確保引擎相容性約束不被打破
            if new_engine_name == "gtts":
                if hasattr(app, "tts_smooth_mode") and app.tts_smooth_mode:
                    logger.warning(
                        "GTTS does not support smooth mode, disabling smooth mode")
                    app.tts_smooth_mode = False
                    self.config_manager.set_override("tts.smooth_mode", False)
                    self.config_manager.save_to_file()
                    if app:
                        app.notify(
                            "Smooth mode disabled (not supported by GTTS)",
                            severity="information",
                        )

            # Re-setup TTS with new engine if integration provided
            if tts_integration:
                await tts_integration.setup_tts()

            return True

        except Exception as e:
            logger.error(f"Failed to switch TTS engine: {e}")
            if app:
                app.notify(f"Failed to switch engine: {e}", severity="error")
            return False

        finally:
            # [🔥 關鍵修復] 只清除引擎切換標記
            # 車子已停下，乘客已下車，新引擎準備好
            # 等待使用者決定要不要繼續播放（按下 PLAY）
            # 不由腳本自動執行，由使用者控制
            if tts_integration:
                tts_integration._engine_switching = False
                logger.info(
                    "Engine switching completed: ready for user to resume playback if desired.")

    async def _cleanup_engine(
        self, engine: Optional["TTSEngine"], tts_integration=None
    ) -> None:
        """
        Perform comprehensive cleanup of a TTS engine.

        Args:
            engine: The engine to cleanup
            tts_integration: TTSIntegration instance for app access
        """
        if not engine:
            return

        logger.debug(
            f"Performing comprehensive cleanup for {type(engine).__name__}")

        try:
            # CRITICAL FIX: Reset playlist manager FIRST to prevent stale task results
            # When tasks from the old engine complete after cleanup, their results should be ignored
            if tts_integration and hasattr(tts_integration, "playlist_manager"):
                playlist_manager = tts_integration.playlist_manager

                # Stop predictive controller and reset playlist BEFORE engine cleanup
                controller = getattr(
                    playlist_manager, "_predictive_controller", None)
                if controller and hasattr(controller, "stop_monitoring"):
                    await controller.stop_monitoring()
                    logger.debug(
                        "Predictive controller for old engine stopped.")

                # Reset playlist manager FIRST to cancel tasks and clear cache ASAP
                if hasattr(playlist_manager, "reset"):
                    playlist_manager.reset()
                    logger.debug(
                        "Reset playlist manager for old engine (before engine cleanup)"
                    )

            # Now it is safe to cleanup engine resources
            if hasattr(engine, "cleanup_resources"):
                await engine.cleanup_resources()
            else:
                # Fallback cleanup
                if hasattr(engine, "stop"):
                    engine.stop()
                if hasattr(engine, "stop_async_loop"):
                    engine.stop_async_loop()

            # Clear the engine reference
            if self._current_engine is engine:
                self._current_engine = None

            logger.debug("Engine cleanup completed successfully")

        except Exception as e:
            logger.warning(f"Error during engine cleanup: {e}")

    def get_engine_class(self, engine_name: str):
        """Get the engine class for a given engine name."""
        try:
            # Import dynamically to avoid circular imports
            if engine_name == "edge-tts":
                from .edge_tts_provider import EdgeTTSProvider

                return EdgeTTSProvider
            elif engine_name == "gtts":
                from .gtts_provider import GTTSProvider

                return GTTSProvider
            elif engine_name == "nanmai":
                from .nanmai_tts_provider import NanmaiTTSProvider

                return NanmaiTTSProvider
            else:
                raise ValueError(f"Unknown engine: {engine_name}")
        except ImportError as e:
            logger.error(f"Failed to import engine {engine_name}: {e}")
            return None

    async def initialize_engine(self, engine_name: str, config_manager=None):
        """Create and initialize a new TTS engine."""
        EngineClass = self.get_engine_class(engine_name)
        if not EngineClass:
            raise ValueError(f"Engine {engine_name} not available")

        try:
            engine = EngineClass(config_manager=config_manager)
            # Perform any initialization if needed
            # await engine.initialize()  # If needed in future
            logger.info(f"Successfully initialized {engine_name} engine")
            return engine
        except Exception as e:
            logger.error(f"Failed to initialize {engine_name} engine: {e}")
            raise
