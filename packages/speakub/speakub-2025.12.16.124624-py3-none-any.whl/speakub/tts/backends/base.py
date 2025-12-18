"""
Base Audio Backend - Abstract interface for audio playback.
"""

from abc import ABC, abstractmethod
from typing import Optional


class AudioBackend(ABC):
    """Abstract base class for audio backends.

    Provides unified interface for different audio playback systems.
    """

    @abstractmethod
    def play(self, audio_data: bytes, speed: float = 1.0, volume: float = 1.0) -> None:
        """Play audio data.

        Args:
            audio_data: Raw audio bytes
            speed: Playback speed (0.5-3.0)
            volume: Playback volume (0.0-1.5 for MPV, 0.0-1.0 for pygame)
        """
        pass

    @abstractmethod
    def pause(self) -> None:
        """Pause playback."""
        pass

    @abstractmethod
    def resume(self) -> None:
        """Resume playback."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop playback."""
        pass

    @abstractmethod
    def set_volume(self, volume: float) -> None:
        """Set playback volume.

        Args:
            volume: Volume level (0.0-1.5 for MPV, 0.0-1.0 for pygame)
        """
        pass

    @abstractmethod
    def get_volume(self) -> float:
        """Get current volume level."""
        pass

    @abstractmethod
    def set_speed(self, speed: float) -> None:
        """Set playback speed.

        Args:
            speed: Speed multiplier (0.5-3.0)
        """
        pass

    @abstractmethod
    def get_speed(self) -> float:
        """Get current playback speed."""
        pass

    @abstractmethod
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        pass

    @abstractmethod
    def can_resume(self) -> bool:
        """Check if playback can be resumed from paused state."""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources."""
        pass
