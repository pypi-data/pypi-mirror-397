"""TTS module for SpeakUB."""

from .engine import TTSEngine
from .engine_manager import TTSEngineManager
from .integration import TTSIntegration

__all__ = ["TTSEngine", "TTSIntegration", "TTSEngineManager"]
