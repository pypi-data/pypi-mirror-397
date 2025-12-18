#!/usr/bin/env python3
"""
User-Friendly Error Messages - Convert technical errors to user-friendly messages
"""

import re
from typing import Dict, Optional


class UserFriendlyErrors:
    """Convert technical error messages to user-friendly versions."""

    # Error message mappings - technical pattern -> user-friendly message
    ERROR_TRANSLATIONS: Dict[str, Dict[str, str]] = {
        # File system errors
        "file_not_found": {
            "pattern": r"EPUB file not found|No such file or directory|FileNotFoundError",
            "message": "Specified EPUB file not found",
            "suggestion": "Please check the file path and ensure the file exists",
        },
        "invalid_epub": {
            "pattern": r"Invalid EPUB file|File is not a zip file|BadZipFile",
            "message": "This is not a valid EPUB file",
            "suggestion": "Please ensure you selected the correct .epub file",
        },
        "file_too_large": {
            "pattern": r"EPUB file too large|file size.*exceeds",
            "message": "EPUB file is too large",
            "suggestion": "SpeakUB supports a maximum file size of 500MB",
        },
        "permission_denied": {
            "pattern": r"Permission denied|Access is denied",
            "message": "Permission denied accessing file",
            "suggestion": "Please check file permissions or copy the file "
            "to an accessible location",
        },
        # Network errors
        "network_unreachable": {
            "pattern": r"Network is unreachable|Connection refused|timeout",
            "message": "Network connection failed",
            "suggestion": "Please check your network connection or try again later",
        },
        "dns_resolution": {
            "pattern": r"Name resolution failure|DNS|nodename nor servname",
            "message": "Unable to resolve server address",
            "suggestion": "Please check your network connection and DNS settings",
        },
        "ssl_error": {
            "pattern": r"SSL|certificate|TLS",
            "message": "Secure connection error",
            "suggestion": "Network connection may have security issues, please try again later",
        },
        # TTS errors
        "tts_service_unavailable": {
            "pattern": r"edge-tts.*unavailable|Service unavailable|HTTP 503",
            "message": "Text-to-speech service temporarily unavailable",
            "suggestion": "Please try again later or switch to another TTS engine",
        },
        "tts_voice_not_available": {
            "pattern": r"Voice.*not available|Invalid voice",
            "message": "Selected voice is not available",
            "suggestion": "Please select another available voice in settings",
        },
        "tts_rate_limit": {
            "pattern": r"Rate limit|Too many requests|429",
            "message": "Text-to-speech requests too frequent",
            "suggestion": "Please wait a moment before continuing or reduce speech rate settings",
        },
        # Terminal errors
        "terminal_not_found": {
            "pattern": r"No terminal emulator found|terminal environment",
            "message": "Terminal environment required to run SpeakUB",
            "suggestion": "Please launch SpeakUB from a terminal or command line, "
            "not by double-clicking from file manager",
        },
        # Audio errors
        "audio_device_error": {
            "pattern": r"Audio device|No audio device|ALSA|pulseaudio",
            "message": "Audio device error",
            "suggestion": "Please check audio settings or restart audio services",
        },
        "audio_backend_error": {
            "pattern": r"pygame|mpv.*error|audio backend",
            "message": "Audio player error",
            "suggestion": "Please try switching audio backends or check system audio settings",
        },
        # Configuration errors
        "config_error": {
            "pattern": r"configuration|config.*error|settings",
            "message": "Configuration file error",
            "suggestion": "Please check configuration file or reset to default settings",
        },
        # System errors
        "memory_error": {
            "pattern": r"MemoryError|Out of memory",
            "message": "Insufficient memory",
            "suggestion": "Please close other programs or process smaller files",
        },
        "disk_space_error": {
            "pattern": r"No space left|Disk full",
            "message": "Insufficient disk space",
            "suggestion": "Please clean up disk space or save files to another disk",
        },
    }

    @classmethod
    def translate_error(
        cls, error: Exception, context: str = ""
    ) -> Optional[Dict[str, str]]:
        """
        Translate a technical error into user-friendly message.

        Args:
            error: The exception object
            context: Additional context about where the error occurred

        Returns:
            Dict with 'message' and 'suggestion' keys, or None if no translation found
        """
        error_text = f"{type(error).__name__}: {str(error)} {context}".lower()

        for error_key, translation in cls.ERROR_TRANSLATIONS.items():
            pattern = translation["pattern"]
            if re.search(pattern, error_text, re.IGNORECASE):
                return {
                    "message": translation["message"],
                    "suggestion": translation["suggestion"],
                }

        return None

    @classmethod
    def format_error_message(
        cls, error: Exception, context: str = "", show_technical: bool = False
    ) -> str:
        """
        Format an error message for user display.

        Args:
            error: The exception object
            context: Context about where the error occurred
            show_technical: Whether to include technical details

        Returns:
            Formatted error message
        """
        translation = cls.translate_error(error, context)

        if translation:
            message = f"❌ {translation['message']}\n💡 {translation['suggestion']}"
        else:
            # Fallback to generic message
            message = f"❌ An error occurred: {str(error)}\n💡 Please check settings or try again later"

        if show_technical:
            message += f"\n\nTechnical details: {type(error).__name__}: {str(error)}"

        return message

    @classmethod
    def print_error(
        cls, error: Exception, context: str = "", show_technical: bool = False
    ) -> None:
        """
        Print a user-friendly error message to stderr.

        Args:
            error: The exception object
            context: Context about where the error occurred
            show_technical: Whether to include technical details
        """
        message = cls.format_error_message(error, context, show_technical)
        print(message, file=__import__("sys").stderr)


# Convenience functions for common use cases
def print_friendly_error(error: Exception, context: str = "") -> None:
    """Print a user-friendly error message."""
    UserFriendlyErrors.print_error(error, context)


def get_friendly_error_message(error: Exception, context: str = "") -> str:
    """Get a user-friendly error message."""
    return UserFriendlyErrors.format_error_message(error, context)
