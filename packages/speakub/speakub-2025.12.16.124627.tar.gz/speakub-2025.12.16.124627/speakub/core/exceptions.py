#!/usr/bin/env python3
"""
Unified exception handling for SpeakUB.
"""

import logging
import time
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SpeakUBException(Exception):
    """Base exception with logging support"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message)
        self.details = details or {}
        self.timestamp = time.time()
        logger.error(
            f"{self.__class__.__name__}: {message}", extra={"details": self.details}
        )


class ParsingException(SpeakUBException):
    """Parsing-related errors"""

    pass


class ConfigurationException(SpeakUBException):
    """Configuration-related errors"""

    pass


class SecurityException(SpeakUBException):
    """Security-related errors"""

    pass


class FileSizeException(SpeakUBException):
    """File size-related errors"""

    pass


class TTSError(Exception):
    """TTS-related errors base class"""

    pass


class NetworkError(TTSError):
    """Network connection errors"""

    pass


class AudioSynthesisError(TTSError):
    """Audio synthesis errors"""

    pass


# Legacy TTS exceptions for backward compatibility (keeping original names)
class TTSException(SpeakUBException):
    """Base class for TTS-related errors"""

    pass


class TTSSynthesisError(TTSException):
    """Errors during text-to-speech synthesis"""

    pass


class TTSProviderError(TTSException):
    """Errors with TTS provider configuration or initialization"""

    pass


class TTSVoiceError(TTSException):
    """Errors related to voice selection or configuration"""

    pass


class TTSPlaybackError(TTSException):
    """Errors during audio playback"""

    pass


class NetworkException(SpeakUBException):
    """Base class for network-related errors"""

    pass


class NetworkTimeoutError(NetworkException):
    """Network request timeout errors"""

    pass


class NetworkConnectionError(NetworkException):
    """Network connectivity errors"""

    pass


class NetworkAPIError(NetworkException):
    """API-specific network errors"""

    pass


class CacheException(SpeakUBException):
    """Cache-related errors"""

    pass
