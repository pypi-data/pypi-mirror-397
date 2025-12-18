# speakub/tts/engines/__init__.py
"""
TTS Engines Module

Unified interface for all TTS engine implementations.
Supports Edge-TTS, Google Text-to-Speech (GTTS), and Nanmai TTS.
"""

from .edge_tts_provider import EdgeTTSProvider
from .gtts_provider import GTTSProvider
from .nanmai_tts_provider import NanmaiTTSProvider

__all__ = [
    "EdgeTTSProvider",
    "GTTSProvider",
    "NanmaiTTSProvider",
]
