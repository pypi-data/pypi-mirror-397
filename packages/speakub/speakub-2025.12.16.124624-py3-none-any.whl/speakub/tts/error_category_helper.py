"""
Error Category Helper Module

Simple helper for categorizing and handling TTS errors.
"""

import logging
from typing import Dict

from speakub.core.exceptions import (
    AudioSynthesisError,
    NetworkError,
    TTSError,
)

logger = logging.getLogger(__name__)


class ErrorCategoryHelper:
    """Helper class for error categorization and notification."""

    # Error categorization keywords
    NETWORK_KEYWORDS = ["network", "connection",
                        "timeout", "unreachable", "dns"]
    SYNTHESIS_KEYWORDS = ["audio", "synthesis", "voice",
                          "playback", "tts", "failed", "no audio"]

    @classmethod
    def categorize_error(cls, error_msg: str, full_error: str) -> Dict:
        """
        Categorize error based on message content.

        Args:
            error_msg: Error message in lowercase
            full_error: Full error message for notification

        Returns:
            dict: Error details with type, notification, title, and exception
        """
        if any(keyword in error_msg for keyword in cls.NETWORK_KEYWORDS):
            return {
                "type": "network",
                "notification": f"網路連接錯誤: {full_error}",
                "title": "網路錯誤",
                "exception": NetworkError,
            }
        elif any(keyword in error_msg for keyword in cls.SYNTHESIS_KEYWORDS):
            return {
                "type": "synthesis",
                "notification": f"音頻合成錯誤: {full_error}",
                "title": "TTS 錯誤",
                "exception": AudioSynthesisError,
            }
        else:
            return {
                "type": "general_tts",
                "notification": f"TTS 錯誤: {full_error}",
                "title": "TTS 錯誤",
                "exception": TTSError,
            }

    @classmethod
    def is_synthesis_error(cls, error_msg: str) -> bool:
        """Check if error is synthesis-related."""
        return any(keyword in error_msg for keyword in cls.SYNTHESIS_KEYWORDS)

    @classmethod
    def is_network_error(cls, error_msg: str) -> bool:
        """Check if error is network-related."""
        return any(keyword in error_msg for keyword in cls.NETWORK_KEYWORDS)
