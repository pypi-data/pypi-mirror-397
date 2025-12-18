"""
Pygame Audio Backend - For EdgeTTS playback.
"""

import asyncio
import os
import tempfile
from typing import Optional

from ..audio_player import AudioPlayer
from .base import AudioBackend


class PygameBackend(AudioBackend):
    """Pygame-based audio backend for EdgeTTS.

    Uses pygame mixer for audio playback with volume control.
    Speed control is handled by EdgeTTS API, not playback layer.
    """

    def __init__(self):
        """Initialize pygame backend."""
        self.player = AudioPlayer()
        self._current_file: Optional[str] = None

    def play(self, audio_data: bytes, speed: float = 1.0, volume: float = 1.0) -> None:
        """Play audio data using pygame.

        Args:
            audio_data: Raw audio bytes
            speed: Ignored (handled by EdgeTTS API)
            volume: Volume level (0.0-1.0)
        """
        # Create temp file
        fd, temp_path = tempfile.mkstemp(suffix=".mp3")
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(audio_data)

            if self.player.load_file(temp_path):
                self._current_file = temp_path
                self.set_volume(volume)
                self.player.play_and_wait()
            else:
                raise RuntimeError("Failed to load audio file")

        except Exception as e:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
            raise RuntimeError(f"Pygame playback failed: {e}")
        finally:
            # Cleanup temp file
            if self._current_file and os.path.exists(self._current_file):
                try:
                    os.unlink(self._current_file)
                except OSError:
                    pass
            self._current_file = None

    def pause(self) -> None:
        """Pause playback."""
        self.player.pause()

    def resume(self) -> None:
        """Resume playback."""
        self.player.resume()

    def stop(self) -> None:
        """Stop playback."""
        self.player.stop()

    def set_volume(self, volume: float) -> None:
        """Set playback volume (0.0-1.0)."""
        self.player.set_volume(volume)

    def get_volume(self) -> float:
        """Get current volume level."""
        return self.player.get_volume()

    def set_speed(self, speed: float) -> None:
        """Set playback speed (ignored for pygame backend)."""
        # Speed is handled by EdgeTTS API, not playback
        pass

    def get_speed(self) -> float:
        """Get current playback speed (always 1.0 for pygame)."""
        return 1.0

    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self.player.is_playing

    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        return self.player.is_paused

    def cleanup(self) -> None:
        """Clean up resources."""
        self.player.cleanup()
