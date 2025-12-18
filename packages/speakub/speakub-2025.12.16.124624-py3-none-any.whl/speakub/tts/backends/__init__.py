"""
Audio Backends - Unified audio playback interfaces.
"""

from .base import AudioBackend
from .mpv_backend import MPVBackend
from .pygame_backend import PygameBackend


def get_audio_backend(backend_type: str) -> AudioBackend:
    """Get audio backend instance by type.

    Args:
        backend_type: "mpv" or "pygame"

    Returns:
        AudioBackend instance

    Raises:
        ValueError: If backend_type is not supported
    """
    if backend_type == "mpv":
        return MPVBackend()
    elif backend_type == "pygame":
        return PygameBackend()
    else:
        raise ValueError(f"Unsupported backend type: {backend_type}")
