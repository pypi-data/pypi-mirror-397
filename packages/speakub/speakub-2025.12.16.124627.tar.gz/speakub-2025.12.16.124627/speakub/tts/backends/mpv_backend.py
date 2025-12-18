"""
MPV Audio Backend - For GTTS and NanmaiTTS playback.
"""

import logging
import os
import tempfile
import threading
from typing import Optional

try:
    import mpv

    MPV_AVAILABLE = True
except ImportError:
    MPV_AVAILABLE = False

from .base import AudioBackend

logger = logging.getLogger(__name__)


class MPVBackend(AudioBackend):
    """MPV-based audio backend for GTTS and NanmaiTTS.

    Uses MPV player with scaletempo for speed control.
    Supports volume up to 150% for better audibility.
    """

    def __init__(self):
        """Initialize MPV backend."""
        if not MPV_AVAILABLE:
            raise ImportError("python-mpv required for MPV backend")

        self.mpv_player: Optional[mpv.MPV] = None
        self._current_file: Optional[str] = None
        self._is_paused = False
        self._playback_stop_event = threading.Event()
        self._temp_file_lock = threading.Lock()

        # Default settings
        self._target_volume = 1.5  # Default 150% for better audibility
        self._target_speed = 1.0

        # Initialize MPV
        self._initialize_mpv()

    def _initialize_mpv(self):
        """Initialize MPV player with ultra-minimal, fail-safe configuration."""
        try:
            # Ultra-minimal fail-safe MPV configuration for NanmaiTTS
            self.mpv_player = mpv.MPV()
            logger.debug("MPV backend initialized with minimal config")
            # 手动配置基础设置避免初始化冲突
            self.mpv_player.volume = self._target_volume * 100
            self.mpv_player.speed = self._target_speed

        except Exception as e:
            logger.error(f"Failed to initialize MPV: {e}")
            if "Invalid value for mpv option" in str(e):
                logger.warning("MPV option conflict detected, "
                               "attempting recovery...")
                try:
                    # 如果参数冲突，只使用默认MPV配置
                    self.mpv_player = mpv.MPV()
                    self.mpv_player.volume = self._target_volume * 100
                    self.mpv_player.speed = self._target_speed
                    logger.debug(
                        "MPV initialized with default config (recovery mode)")
                except Exception as e2:
                    logger.error(
                        f"MPV recovery initialization also failed: {e2}")
                    raise e2
            else:
                raise

    def play(self, audio_data: bytes, speed: float = 1.0, volume: float = 1.5) -> None:
        """Play audio data using MPV.

        Args:
            audio_data: Raw audio bytes
            speed: Playback speed (0.5-3.0)
            volume: Volume level (0.0-1.5, supports up to 150%)
        """
        self._playback_stop_event.clear()
        temp_path = None
        temp_fd = None

        try:
            with self._temp_file_lock:
                # Create temp file with proper cleanup handling
                temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
                try:
                    with os.fdopen(temp_fd, "wb") as f:
                        f.write(audio_data)
                    temp_fd = None  # Don't close again in finally
                    self._current_file = temp_path
                    logger.debug(f"Created temp file for MPV: {temp_path}")
                except Exception:
                    # Close fd if still open
                    if temp_fd is not None:
                        try:
                            os.close(temp_fd)
                        except OSError:
                            pass
                    # Remove temp file if it was created
                    if temp_path and os.path.exists(temp_path):
                        try:
                            os.unlink(temp_path)
                        except OSError:
                            pass
                    raise

            # Apply settings
            self.set_speed(speed)
            self.set_volume(volume)
            self._is_paused = False

            # Start playback
            self._start_playback()
            self._wait_for_completion()

        finally:
            # Cleanup - ensure temp file is always removed
            if temp_fd is not None:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass
            self._cleanup_current_file()

    def _start_playback(self) -> None:
        """Start MPV playback."""
        if not self.mpv_player or not self._current_file:
            raise RuntimeError("MPV player not initialized or no file")

        self.mpv_player.loadfile(self._current_file)
        self.mpv_player.pause = False

    def _wait_for_completion(self) -> None:
        """Wait for MPV playback to complete."""
        while True:
            if self._playback_stop_event.is_set():
                break

            try:
                if self.mpv_player.idle_active:
                    break
            except Exception:
                try:
                    if self.mpv_player.time_pos is None:
                        break
                except Exception:
                    break

            import time

            time.sleep(0.1)

    def pause(self) -> None:
        """Pause playback."""
        if self.mpv_player:
            self._playback_stop_event.set()
            self._is_paused = True
            self.mpv_player.pause = True
            logger.debug("MPV playback paused")

    def resume(self) -> None:
        """Resume playback."""
        if self.can_resume():
            self._playback_stop_event.clear()
            self._is_paused = False
            if self.mpv_player:
                self.mpv_player.pause = False
            logger.debug("MPV playback resumed")

    def stop(self) -> None:
        """Stop playback."""
        self._playback_stop_event.set()
        self._is_paused = False
        if self.mpv_player:
            try:
                self.mpv_player.stop()
                import time

                time.sleep(0.1)
                logger.debug("MPV playback stopped")
            except Exception as e:
                logger.warning(f"Error stopping MPV: {e}")
        self._cleanup_current_file()

    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0-1.5, supports up to 150%)."""
        self._target_volume = max(0.0, min(1.5, volume))
        if self.mpv_player:
            try:
                self.mpv_player.volume = round(self._target_volume * 100, 2)
                logger.debug("MPV volume set to "
                             f"{round(self._target_volume * 100, 2)}")
            except Exception as e:
                logger.warning(f"Failed to set MPV volume: {e}")

    def get_volume(self) -> float:
        """Get current volume level."""
        # Return target volume since MPV limits to 100%
        # We remember the intended volume level for UI consistency
        return self._target_volume

    def set_speed(self, speed: float) -> None:
        """Set playback speed (0.5-3.0)."""
        self._target_speed = max(0.5, min(3.0, speed))
        if self.mpv_player:
            try:
                self.mpv_player.speed = round(self._target_speed, 2)
                logger.debug("MPV speed set to "
                             f"{round(self._target_speed, 2)}")
            except Exception as e:
                logger.warning(f"Failed to set MPV speed: {e}")

    def get_speed(self) -> float:
        """Get current playback speed."""
        if self.mpv_player:
            try:
                return getattr(self.mpv_player, "speed", self._target_speed)
            except Exception:
                pass
        return self._target_speed

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        if self.mpv_player:
            try:
                return not self.mpv_player.idle_active and not self._is_paused
            except Exception:
                pass
        return False

    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        return (
            self.mpv_player is not None
            and self._is_paused
            and self._current_file is not None
            and os.path.exists(self._current_file)
        )

    def _cleanup_current_file(self) -> None:
        """Clean up current temp file."""
        if self._current_file and os.path.exists(self._current_file):
            try:
                os.unlink(self._current_file)
                logger.debug(f"Cleaned up temp file: {self._current_file}")
            except Exception as e:
                logger.debug(
                    f"Failed to delete temp file {self._current_file}: {e}")
        self._current_file = None

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop()
        self._cleanup_mpv_instance()

    def _cleanup_mpv_instance(self) -> None:
        """Properly cleanup MPV instance to prevent memory leaks."""
        if self.mpv_player:
            try:
                # Stop any current playback
                self.mpv_player.stop()
                # Clear any loaded file
                self.mpv_player.playlist_clear()
                # Quit MPV process
                self.mpv_player.quit()
                logger.debug("MPV instance properly cleaned up")
            except Exception as e:
                logger.warning(f"Error during MPV cleanup: {e}")
            finally:
                self.mpv_player = None

    def reset_mpv(self) -> None:
        """Reset MPV instance with fresh configuration (for memory recovery)."""
        self._cleanup_mpv_instance()
        # Re-initialize with current settings
        try:
            self._initialize_mpv()
            logger.debug("MPV instance reset for memory recovery")
        except Exception as e:
            logger.error(f"Failed to reset MPV: {e}")

    def get_memory_usage(self) -> float:
        """Get current memory usage of MPV process in MB."""
        try:
            import os

            import psutil

            # Try to get MPV process memory if possible
            current_process = psutil.Process(os.getpid())
            memory_mb = current_process.memory_info().rss / 1024 / 1024
            logger.debug(f"MPV backend memory usage: {memory_mb:.1f}MB")
            return memory_mb
        except ImportError:
            # psutil not available
            logger.debug("psutil not available for memory monitoring")
            return 0.0
        except Exception as e:
            logger.debug(f"Failed to get memory usage: {e}")
            return 0.0

    def should_cleanup(self, high_memory_threshold: float = 200.0) -> bool:
        """Check if MPV backend should be cleaned up due to high memory usage."""
        memory_mb = self.get_memory_usage()
        return memory_mb > high_memory_threshold
