#!/usr/bin/env python3
"""
Shutdown Coordinator for Graceful System Shutdown

This module provides coordinated shutdown management for TTS systems,
ensuring all components are properly closed and resources cleaned up.
Supports both fast (force) and graceful shutdown modes.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration

logger = logging.getLogger(__name__)


class CleanupMode(Enum):
    """Cleanup operation modes."""

    FAST = "fast"  # Force reset mode
    GRACEFUL = "graceful"  # Coordinated graceful shutdown


class ShutdownCoordinator:
    """
    協調式關閉管理器 - 確保所有組件優雅關閉。

    Purpose:
        Replace violent resets with proper task cancellation for graceful system shutdown.

    Features:
        - Shutdown event coordination: Unified management of component closure order
        - Timeout protection: Prevents shutdown operations from blocking indefinitely
        - State tracking: Monitors shutdown progress and results
        - Error recovery: Handles shutdown failures gracefully

    Shutdown Sequence:
        1. Signal components to stop accepting new work
        2. Wait for in-progress work to complete or timeout
        3. Force cleanup remaining resources
        4. Verify cleanup completion

    Example:
        ```python
        coordinator = ShutdownCoordinator()
        coordinator.register_component("tts_engine")
        stats = await coordinator.unified_cleanup(tts_integration)
        ```
    """

    def __init__(self):
        """Initialize shutdown coordinator with default graceful mode."""
        self._shutdown_event = asyncio.Event()
        self._active_components: set[str] = set()
        self._shutdown_stats: Dict[str, Any] = {}
        self._shutdown_start_time: Optional[float] = None
        self._current_mode = CleanupMode.GRACEFUL  # Default to graceful mode

        # Mode-specific timeout configurations
        self._mode_configs = {
            CleanupMode.FAST: {
                "total_timeout": 2.0,  # Fast mode total timeout
                "component_timeouts": {
                    "predictive_controller": 0.5,
                    "playlist_manager": 0.5,
                    "playback_manager": 0.5,
                    "tts_engine": 1.0,
                    "task_cleanup": 0.5,
                },
                "force_cleanup_threshold": 0.8,  # Begin force cleanup at 80%
            },
            CleanupMode.GRACEFUL: {
                "total_timeout": 10.0,  # Graceful mode total timeout
                "component_timeouts": {
                    "predictive_controller": 3.0,
                    "playlist_manager": 2.0,
                    "playback_manager": 2.0,
                    "tts_engine": 3.0,
                    "task_cleanup": 2.0,
                },
                "force_cleanup_threshold": 0.5,  # Begin force cleanup at 50%
            },
        }

    def register_component(self, component_name: str) -> None:
        """
        Register a component that needs shutdown coordination.

        Args:
            component_name: Unique identifier for the component
        """
        self._active_components.add(component_name)
        logger.debug(f"Registered shutdown component: {component_name}")

    def unregister_component(self, component_name: str) -> None:
        """
        Unregister a component from shutdown coordination.

        Args:
            component_name: Unique identifier for the component
        """
        self._active_components.discard(component_name)
        logger.debug(f"Unregistered shutdown component: {component_name}")

    def set_cleanup_mode(self, mode: CleanupMode) -> None:
        """
        Set the cleanup mode for subsequent shutdown operations.

        Args:
            mode: CleanupMode.FAST for force reset or CleanupMode.GRACEFUL for coordinated shutdown
        """
        self._current_mode = mode
        logger.debug(f"ShutdownCoordinator cleanup mode set to: {mode.value}")

    def get_cleanup_mode(self) -> CleanupMode:
        """
        Get the current cleanup mode.

        Returns:
            Current CleanupMode setting
        """
        return self._current_mode

    def get_mode_config(self) -> Dict[str, Any]:
        """
        Get configuration for the current cleanup mode.

        Returns:
            Configuration dictionary with timeouts and thresholds
        """
        return self._mode_configs[self._current_mode]

    async def unified_cleanup(
        self, tts_integration: "TTSIntegration"
    ) -> Dict[str, Any]:
        """
        Unified cleanup entry point - executes appropriate cleanup strategy based on mode.

        Args:
            tts_integration: TTS integration instance to shutdown

        Returns:
            Dictionary with cleanup statistics and results
        """
        mode = self._current_mode
        config = self.get_mode_config()

        logger.info(
            f"Starting unified cleanup in {mode.value} mode (timeout: {config['total_timeout']}s)"
        )

        if mode == CleanupMode.FAST:
            return await self._fast_cleanup(tts_integration)
        else:
            return await self._graceful_cleanup(tts_integration)

    async def _fast_cleanup(self, tts_integration: "TTSIntegration") -> Dict[str, Any]:
        """Execute fast force cleanup mode."""
        start_time = time.time()

        try:
            logger.debug("Executing fast cleanup mode...")

            # 1. Immediately stop all async tasks
            await self._force_cancel_all_tasks(tts_integration)

            # 2. Reset critical state
            self._force_reset_states(tts_integration)

            # 3. Cleanup remaining resources
            await self._force_cleanup_remaining(tts_integration)

            duration = time.time() - start_time
            self._shutdown_stats.update(
                {
                    "mode": "fast",
                    "total_duration": duration,
                    "status": "completed",
                    "method": "force_reset",
                }
            )

            logger.info(f"Fast cleanup completed in {duration:.2f}s")
            return self._shutdown_stats.copy()

        except Exception as e:
            duration = time.time() - start_time
            self._shutdown_stats.update(
                {
                    "mode": "fast",
                    "total_duration": duration,
                    "status": "failed",
                    "error": str(e),
                }
            )
            logger.error(f"Fast cleanup failed: {e}")
            return self._shutdown_stats.copy()

    async def _graceful_cleanup(
        self, tts_integration: "TTSIntegration"
    ) -> Dict[str, Any]:
        """Execute graceful coordinated cleanup mode."""
        self._shutdown_start_time = time.time()
        config = self.get_mode_config()

        try:
            # Phase 1: Signal components to stop
            logger.info("Initiating graceful shutdown sequence...")
            await self._signal_shutdown(tts_integration)

            # Phase 2: Wait for components with timeout and force cleanup threshold
            await self._wait_for_components_with_fallback(tts_integration, config)

            # Phase 3: Force cleanup remaining resources
            await self._force_cleanup_remaining(tts_integration)

            # Phase 4: Validate and report
            shutdown_duration = time.time() - self._shutdown_start_time
            self._shutdown_stats.update(
                {
                    "mode": "graceful",
                    "total_duration": shutdown_duration,
                    "status": "completed",
                    "components_shutdown": len(self._active_components),
                }
            )

            logger.info(
                f"Graceful shutdown completed in {shutdown_duration:.2f}s")
            return self._shutdown_stats.copy()

        except Exception as e:
            shutdown_duration = time.time() - (self._shutdown_start_time or time.time())
            self._shutdown_stats.update(
                {
                    "mode": "graceful",
                    "total_duration": shutdown_duration,
                    "status": "failed",
                    "error": str(e),
                }
            )
            logger.error(
                f"Graceful shutdown failed after {shutdown_duration:.2f}s: {e}"
            )
            return self._shutdown_stats.copy()

    async def graceful_shutdown(
        self, tts_integration: "TTSIntegration"
    ) -> Dict[str, Any]:
        """
        Backward compatible method - delegates to unified_cleanup in graceful mode.

        Args:
            tts_integration: TTS integration instance to shutdown

        Returns:
            Dictionary with shutdown statistics
        """
        original_mode = self._current_mode
        self.set_cleanup_mode(CleanupMode.GRACEFUL)
        try:
            return await self.unified_cleanup(tts_integration)
        finally:
            self._current_mode = original_mode

    async def _signal_shutdown(self, tts_integration: "TTSIntegration") -> None:
        """Signal all components to begin shutdown."""
        logger.debug("Signaling all components to begin shutdown...")

        # Set global shutdown event
        self._shutdown_event.set()
        tts_integration._async_tts_stop_requested.set()

        # Notify critical components to begin shutdown
        if hasattr(tts_integration.playlist_manager, "_predictive_controller"):
            try:
                await tts_integration.async_bridge.run_coroutine(
                    tts_integration.playlist_manager._predictive_controller.stop_monitoring(),
                    timeout=self._component_timeouts().get(
                        "predictive_controller", 2.0
                    ),
                )
                logger.debug("Signaled predictive controller to stop")
            except Exception as e:
                logger.warning(f"Failed to signal predictive controller: {e}")

        # Stop playback manager
        try:
            await tts_integration.async_bridge.run_coroutine(
                tts_integration.playback_manager.stop_playback_async(
                    is_pause=False),
                timeout=self._component_timeouts().get("playback_manager", 2.0),
            )
            logger.debug("Signaled playback manager to stop")
        except Exception as e:
            logger.warning(f"Failed to signal playback manager: {e}")

    async def _wait_for_components_with_fallback(
        self, tts_integration: "TTSIntegration", config: Dict[str, Any]
    ) -> None:
        """Wait for components to complete shutdown with automatic fallback."""
        logger.debug(
            "Waiting for components to complete shutdown with fallback...")

        total_timeout = config["total_timeout"]
        force_cleanup_threshold = config["force_cleanup_threshold"]
        start_time = time.time()

        # Phase 1: Try graceful shutdown
        try:
            await asyncio.wait_for(
                self._wait_for_task_cleanup(tts_integration),
                timeout=self._component_timeouts().get("task_cleanup", 2.0),
            )
            logger.debug("Task cleanup completed gracefully")
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            if elapsed < total_timeout * force_cleanup_threshold:
                logger.warning(
                    "Task cleanup timed out, will force cleanup later")
            else:
                logger.warning(
                    "Task cleanup timed out early, forcing cleanup now")
                await self._force_cancel_all_tasks(tts_integration)

        # Phase 2: Wait for player to stop
        try:
            await asyncio.wait_for(
                self._wait_for_player_stop(tts_integration),
                timeout=self._component_timeouts().get("tts_engine", 3.0),
            )
            logger.debug("TTS engine shutdown completed gracefully")
        except asyncio.TimeoutError:
            logger.warning("TTS engine shutdown timed out")

    async def _force_cancel_all_tasks(self, tts_integration: "TTSIntegration") -> None:
        """Force cancel all active tasks."""
        logger.debug("Force cancelling all active tasks...")

        tasks_to_cancel = []
        for task in list(tts_integration._tts_active_tasks):
            if not task.done() and not task.cancelled():
                tasks_to_cancel.append(task)

        if tasks_to_cancel:
            logger.info(
                f"Force cancelling {len(tasks_to_cancel)} active tasks")
            # Cancel all tasks concurrently
            cancel_tasks = [
                asyncio.create_task(self._safe_cancel_task(task))
                for task in tasks_to_cancel
            ]
            await asyncio.gather(*cancel_tasks, return_exceptions=True)

        tts_integration._tts_active_tasks.clear()
        logger.debug("Force task cancellation completed")

    def _force_reset_states(self, tts_integration: "TTSIntegration") -> None:
        """Force reset critical state."""
        logger.debug("Force resetting critical states...")

        # Reset playlist
        try:
            tts_integration.playlist_manager.reset()
            logger.debug("Force reset playlist manager")
        except Exception as e:
            logger.warning(f"Error resetting playlist manager: {e}")

        # Force stop Reservoir Controller if running (critical for smooth mode)
        try:
            if (
                hasattr(tts_integration, "playlist_manager")
                and hasattr(tts_integration.playlist_manager, "_predictive_controller")
                and tts_integration.playlist_manager._predictive_controller
            ):
                controller = tts_integration.playlist_manager._predictive_controller
                if controller.running:
                    logger.debug(
                        "Force stopping Reservoir Controller during fast cleanup")
                    controller.running = False
                    # 無法在同步上下文中 await stop_monitoring，所以直接設置 running = False
        except Exception as e:
            logger.warning(f"Error force-stopping Reservoir Controller: {e}")

        # Reset async events
        try:
            tts_integration._reset_async_events()
            logger.debug("Force reset async events")
        except Exception as e:
            logger.warning(f"Error resetting async events: {e}")

    async def _wait_for_components_shutdown(
        self, tts_integration: "TTSIntegration"
    ) -> None:
        """Wait for component shutdown (backward compatible)."""
        config = self.get_mode_config()
        await self._wait_for_components_with_fallback(tts_integration, config)

    async def _safe_cancel_task(self, task: asyncio.Task) -> None:
        """Safely cancel a task."""
        try:
            task.cancel()
            logger.debug(f"Cancelled task: {task}")
        except Exception as e:
            logger.warning(f"Error cancelling task: {e}")

    def _component_timeouts(self) -> Dict[str, float]:
        """Get component timeout configuration (backward compatible)."""
        return self._mode_configs[self._current_mode]["component_timeouts"]

    async def _wait_for_task_cleanup(self, tts_integration: "TTSIntegration") -> None:
        """Wait for async task cleanup to complete."""
        if not hasattr(tts_integration, "_tts_active_tasks"):
            return

        active_tasks = tts_integration._tts_active_tasks.copy()
        if not active_tasks:
            return

        logger.debug(
            f"Waiting for {len(active_tasks)} active tasks to complete...")

        # Cancel all active tasks
        for task in active_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete or timeout
        done, pending = await asyncio.wait(
            active_tasks, timeout=self._component_timeouts().get("task_cleanup", 2.0)
        )

        # Force cleanup remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        tts_integration._tts_active_tasks.clear()
        logger.debug(
            f"Cleaned up {len(done)} tasks, force-cancelled {len(pending)} tasks"
        )

    async def _wait_for_player_stop(self, tts_integration: "TTSIntegration") -> None:
        """Wait for player to completely stop."""
        if not hasattr(tts_integration, "app") or not tts_integration.app.tts_engine:
            return

        # Wait for player state to be stopped
        max_wait = self._component_timeouts().get("tts_engine", 3.0)
        start_time = time.time()

        while time.time() - start_time < max_wait:
            try:
                # Try to stop player
                if hasattr(tts_integration.app.tts_engine, "stop"):
                    # Check method type
                    stop_method = tts_integration.app.tts_engine.stop
                    if asyncio.iscoroutinefunction(stop_method):
                        # Is coroutine, call directly
                        await tts_integration.async_bridge.run_coroutine(
                            stop_method(), timeout=0.5
                        )
                    else:
                        # Is sync method, use thread pool
                        await tts_integration.async_bridge.run_coroutine(
                            asyncio.to_thread(stop_method), timeout=0.5
                        )
                break
            except Exception:
                await asyncio.sleep(0.1)

    async def _force_cleanup_remaining(self, tts_integration: "TTSIntegration") -> None:
        """Force cleanup remaining resources."""
        logger.debug("Performing force cleanup of remaining resources...")

        # Force stop Reservoir Controller if still running (critical for smooth mode)
        try:
            if (
                hasattr(tts_integration, "playlist_manager")
                and hasattr(tts_integration.playlist_manager, "_predictive_controller")
                and tts_integration.playlist_manager._predictive_controller
            ):
                controller = tts_integration.playlist_manager._predictive_controller
                if controller.running:
                    logger.info(
                        "Force stopping Reservoir Controller during cleanup")
                    try:
                        await asyncio.wait_for(
                            controller.stop_monitoring(),
                            timeout=2.0
                        )
                        logger.debug("Reservoir Controller stopped gracefully")
                    except asyncio.TimeoutError:
                        logger.warning(
                            "Reservoir Controller stop timed out, forcing stop")
                        controller.running = False
        except Exception as e:
            logger.warning(f"Error stopping Reservoir Controller: {e}")

        # Cleanup playlist manager
        try:
            tts_integration.playlist_manager.reset()
            logger.debug("Force-cleaned playlist manager")
        except Exception as e:
            logger.warning(f"Error during playlist manager cleanup: {e}")

        # Reset async events
        try:
            tts_integration._reset_async_events()
            logger.debug("Reset async events")
        except Exception as e:
            logger.warning(f"Error resetting async events: {e}")

        # Cleanup temporary files
        try:
            cleaned_count = tts_integration.cleanup_orphaned_temp_files()
            if cleaned_count > 0:
                logger.debug(f"Cleaned up {cleaned_count} orphaned temp files")
        except Exception as e:
            logger.warning(f"Error cleaning temp files: {e}")

    def get_shutdown_stats(self) -> Dict[str, Any]:
        """
        Get shutdown statistics.

        Returns:
            Dictionary with shutdown mode, duration, status, and other metrics
        """
        return self._shutdown_stats.copy()
