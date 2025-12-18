"""
Playback Coordinator Module

Coordinates playback between playlist manager, playback manager, and TTS integration.
Handles starting, pausing, resuming, and stopping playback with unified resource management.
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PlaybackCoordinator:
    """Coordinates TTS playback operations across multiple managers."""

    def __init__(self, integration, playlist_manager, playback_manager, shutdown_coordinator):
        """
        Initialize the playback coordinator.

        Args:
            integration: TTSIntegration instance
            playlist_manager: PlaylistManager instance
            playback_manager: PlaybackManager instance
            shutdown_coordinator: ShutdownCoordinator instance
        """
        self.integration = integration
        self.playlist_manager = playlist_manager
        self.playback_manager = playback_manager
        self.shutdown_coordinator = shutdown_coordinator

    def pause_playback(self) -> None:
        """
        Pause playback without cleanup.

        Pauses both playback manager and predictive scheduling if available.
        """
        self.playback_manager.stop_playback(is_pause=True)
        self._pause_predictive_scheduling()
        logger.debug("Playback paused")

    def resume_playback(self) -> None:
        """
        Resume playback from pause.

        Resumes playback manager and predictive scheduling if available.
        """
        self._resume_predictive_scheduling()
        logger.debug("Playback resumed")

    def stop_playback_with_cleanup(self, cleanup_mode=None) -> None:
        """
        Stop playback with full resource cleanup.

        Args:
            cleanup_mode: Optional cleanup mode (FAST/GRACEFUL)
        """
        # Stop playback first
        self.playback_manager.stop_playback(is_pause=False)

        if cleanup_mode:
            self.shutdown_coordinator.set_cleanup_mode(cleanup_mode)

        # Perform unified cleanup
        loop = self._get_event_loop()
        if loop and not loop.is_closed():
            try:
                # Check if already in event loop
                try:
                    asyncio.get_running_loop()
                    in_event_loop = True
                except RuntimeError:
                    in_event_loop = False

                if in_event_loop:
                    # Already in event loop, create task
                    task = loop.create_task(
                        self.shutdown_coordinator.unified_cleanup(
                            self.integration)
                    )
                    self.integration._tts_active_tasks.add(task)
                    logger.debug("Started unified cleanup task")
                else:
                    # Not in event loop, run synchronously
                    cleanup_stats = loop.run_until_complete(
                        self.shutdown_coordinator.unified_cleanup(
                            self.integration)
                    )
                    logger.info(f"Unified cleanup completed: {cleanup_stats}")

            except Exception as e:
                logger.warning(f"Unified cleanup failed: {e}")
                # Fallback to basic cleanup
                self._basic_cleanup()
        else:
            logger.warning("No event loop available, using basic cleanup")
            self._basic_cleanup()

    def _pause_predictive_scheduling(self) -> None:
        """Pause predictive content controller if available."""
        if (
            hasattr(self.playlist_manager, "_predictive_controller")
            and self.playlist_manager._predictive_controller
        ):
            try:
                self.playlist_manager._predictive_controller.pause_scheduling()
                logger.debug("Paused predictive scheduling")
            except Exception as e:
                logger.warning(f"Failed to pause predictive scheduling: {e}")

    def _resume_predictive_scheduling(self) -> None:
        """Resume predictive content controller if available."""
        if (
            hasattr(self.playlist_manager, "_predictive_controller")
            and self.playlist_manager._predictive_controller
        ):
            try:
                self.playlist_manager._predictive_controller.resume_scheduling()
                logger.debug("Resumed predictive scheduling")
            except Exception as e:
                logger.warning(f"Failed to resume predictive scheduling: {e}")

    def _basic_cleanup(self) -> None:
        """Perform basic cleanup when unified cleanup is not available."""
        try:
            self._cancel_all_tasks()
            self.playlist_manager.reset()
            self.integration._reset_async_events()
            logger.debug("Basic cleanup completed")
        except Exception as e:
            logger.warning(f"Error in basic cleanup: {e}")

    def _cancel_all_tasks(self) -> None:
        """Cancel all active TTS tasks."""
        if hasattr(self.playlist_manager, "_cancel_preload_tasks"):
            self.playlist_manager._cancel_preload_tasks()
        if hasattr(self.playlist_manager, "_cancel_batch_preload_task"):
            self.playlist_manager._cancel_batch_preload_task()
        if hasattr(self.playlist_manager, "_cancel_synthesis_tasks"):
            self.playlist_manager._cancel_synthesis_tasks()

        for task in list(self.integration._tts_active_tasks):
            if not task.done():
                try:
                    task.cancel()
                except Exception as e:
                    logger.warning(f"Error cancelling task: {e}")

        self.integration._tts_active_tasks.clear()
        logger.debug("All tasks cancelled")

    def _get_event_loop(self) -> Optional[asyncio.AbstractEventLoop]:
        """Get or create the event loop."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            try:
                return asyncio.get_event_loop()
            except RuntimeError:
                logger.warning("Could not get event loop")
                return None
