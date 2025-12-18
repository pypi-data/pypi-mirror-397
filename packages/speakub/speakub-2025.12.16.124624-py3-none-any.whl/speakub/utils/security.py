"""
Security utilities for SpeakUB.
"""

import logging
import os
from pathlib import Path
from typing import Union

# Type alias for path parameters that accept both string and Path objects
PathOrStr = Union[str, Path]

logger = logging.getLogger(__name__)


class InputValidator:
    """Enhanced input validation utilities for security."""

    @staticmethod
    def validate_epub_path(path: str) -> bool:
        """
        More comprehensive validation for EPUB file paths.

        Args:
            path: Path to the EPUB file

        Returns:
            bool: True if path is valid, False otherwise
        """
        try:
            # First, sanitize the path to prevent injection attacks
            sanitized = InputValidator._sanitize_path(path)

            epub_path = Path(sanitized)

            # Check if path exists and is a file
            if not epub_path.exists():
                logger.warning(f"EPUB path does not exist: {path}")
                return False

            if not epub_path.is_file():
                logger.warning(f"EPUB path is not a file: {path}")
                return False

            # Check file extension
            if epub_path.suffix.lower() != ".epub":
                logger.warning(f"File does not have .epub extension: {path}")
                return False

            # Check file size
            file_size = epub_path.stat().st_size
            if file_size == 0:
                logger.warning(f"EPUB file is empty: {path}")
                return False

            # Maximum file size from config
            from speakub.utils.config import ConfigManager

            config_mgr = ConfigManager()
            max_size_mb = config_mgr.get("epub_security.max_file_size_mb", 50)
            size_mb = file_size / (1024 * 1024)
            if size_mb > max_size_mb:
                logger.warning(
                    f"EPUB file size {size_mb:.1f}MB exceeds "
                    f"maximum {max_size_mb}MB: {path}"
                )
                return False

            # Check if file is readable
            if not os.access(epub_path, os.R_OK):
                logger.warning(f"EPUB file is not readable: {path}")
                return False

            # Verify file is not malicious based on extension and content
            if InputValidator._has_suspicious_content(epub_path):
                logger.warning(
                    f"EPUB file contains suspicious content: {path}")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating EPUB path {path}: {e}")
            return False

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other security issues.

        Args:
            filename: Original filename (may include path components)

        Returns:
            str: Sanitized filename
        """
        import re

        # First, extract just the filename component to prevent path traversal
        filename_only = os.path.basename(filename)

        # Remove path traversal attempts
        filename_only = filename_only.replace("..", "")

        # Remove or replace dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename_only)

        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip(". ")

        # Limit length to prevent issues on most filesystems
        MAX_FILENAME_LENGTH = 255
        if len(sanitized) > MAX_FILENAME_LENGTH:
            name, ext = os.path.splitext(sanitized)
            if ext:
                ext_len = len(ext)
                name = name[: MAX_FILENAME_LENGTH - ext_len]
                sanitized = name + ext
            else:
                sanitized = sanitized[:MAX_FILENAME_LENGTH]

        # Ensure we have a non-empty filename
        if not sanitized:
            sanitized = "unnamed_file"

        return sanitized

    @staticmethod
    def _sanitize_path(path: str) -> str:
        """Internal method to sanitize file paths."""
        # Basic sanitization to prevent path traversal
        path = path.strip()

        # Remove dangerous patterns
        path = path.replace("..", "")
        path = path.replace("//", "/")

        return path

    @staticmethod
    def _has_suspicious_content(file_path: Path) -> bool:
        """Check EPUB file for suspicious content patterns."""
        try:
            # Basic ZIP validation for EPUB files
            from zipfile import BadZipFile, ZipFile

            with ZipFile(file_path, "r") as zip_file:
                # Check for mimetype file (EPUB standard)
                if "mimetype" not in zip_file.namelist():
                    return True

                # Verify mimetype content
                with zip_file.open("mimetype") as f:
                    mimetype = f.read().decode("utf-8", errors="ignore")
                    if mimetype.strip() != "application/epub+zip":
                        return True

                # Check for suspicious file extensions in ZIP
                from speakub.utils.config import ConfigManager

                config_mgr = ConfigManager()
                max_files = config_mgr.get(
                    "epub_security.max_files_in_zip", 10000)

                if len(zip_file.namelist()) > max_files:
                    logger.warning(
                        f"EPUB contains too many files: {len(zip_file.namelist())} > {max_files}"
                    )
                    return True

                suspicious_extensions = [
                    ".exe", ".bat", ".cmd", ".sh", ".js", ".vbs"]
                for filename in zip_file.namelist():
                    file_ext = Path(filename).suffix.lower()
                    if file_ext in suspicious_extensions:
                        logger.warning(
                            f"Suspicious file extension found: {filename}")
                        return True

        except (BadZipFile, Exception) as e:
            logger.warning(f"Error validating EPUB structure: {e}")
            return True

        return False


class TextSanitizer:
    """TTS text input sanitization and validation."""

    # Maximum allowed text length for TTS synthesis
    MAX_TEXT_LENGTH = 50000  # ~10 pages of text

    @staticmethod
    def sanitize_tts_text(text: str) -> str:
        """
        Sanitize text for TTS synthesis.

        Args:
            text: Raw text input

        Returns:
            str: Sanitized text safe for TTS processing
        """
        if not isinstance(text, str):
            logger.warning(f"TTS input is not string: {type(text)}")
            text = str(text)

        # Truncate excessively long text
        if len(text) > TextSanitizer.MAX_TEXT_LENGTH:
            logger.warning(
                f"TTS text too long: {len(text)} > "
                f"{TextSanitizer.MAX_TEXT_LENGTH}, truncating"
            )
            text = (
                text[: TextSanitizer.MAX_TEXT_LENGTH - 200]
                + "\n[Text truncated for TTS]"
            )

        # Remove or replace potentially problematic characters
        import re

        # Remove HTML tags and scripts for security
        text = re.sub(r"<[^>]+>", "", text)  # Remove HTML tags
        text = re.sub(
            r"<script[^>]*>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL
        )  # Remove script tags

        # Remove common JavaScript keywords and function calls
        text = re.sub(
            r"\b(alert|eval|javascript|vbscript|onload|onerror)\b",
            "",
            text,
            flags=re.IGNORECASE,
        )

        # Remove null bytes and control characters (except newlines and tabs)
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Normalize excessive whitespace but preserve paragraph structure
        # Multiple spaces/tabs to single space
        text = re.sub(r"[ \t]+", " ", text)

        # Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # Remove excessive consecutive newlines (max 2)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        # Final length check after processing
        if len(text) == 0:
            logger.warning("TTS text is empty after sanitization")
            text = "Empty text"

        if len(text) > TextSanitizer.MAX_TEXT_LENGTH:
            # This should rarely happen after processing, but as a safety net
            logger.error(
                "Sanitized text still too long, truncating to maximum length")
            text = text[: TextSanitizer.MAX_TEXT_LENGTH]

        # Only log when text is unusually large to reduce log verbosity
        # Most TTS segments are small, so we only log significant ones
        if len(text) > 1000:
            logger.debug(
                f"TTS text sanitized: {len(text)} characters (large segment)")
        elif len(text) == 0:
            logger.warning("TTS text became empty after sanitization")

        return text

    @staticmethod
    def validate_tts_text(text: str) -> bool:
        """
        Validate text for TTS processing.

        Args:
            text: Text to validate

        Returns:
            bool: True if valid, raises exception if invalid
        """
        if not isinstance(text, str):
            raise TypeError(f"TTS text must be string, got {type(text)}")

        if not text or not text.strip():
            raise ValueError("TTS text cannot be empty")

        if len(text) > TextSanitizer.MAX_TEXT_LENGTH:
            raise ValueError(
                f"TTS text too long: {len(text)} > " f"{TextSanitizer.MAX_TEXT_LENGTH}"
            )

        # Check for potentially dangerous content
        if TextSanitizer._contains_malicious_patterns(text):
            raise ValueError("TTS text contains potentially malicious content")

        return True

    @staticmethod
    def _contains_malicious_patterns(text: str) -> bool:
        """Check for malicious patterns in text."""
        # Basic checks for common malicious patterns
        suspicious_patterns = [
            r"<script[^>]*>.*?</script>",  # JavaScript injection
            r"javascript:",  # JavaScript URLs
            r"vbscript:",  # VBScript
            r'on\w+\s*=.*["\'][^"\']*["\']',  # Event handlers
        ]

        import re

        for pattern in suspicious_patterns:
            if re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                logger.warning(
                    f"Detected malicious pattern in TTS text: {pattern}")
                return True

        return False


class PathValidator:
    """Unified path security validation."""

    @staticmethod
    def validate_epub_path(path: PathOrStr) -> Path:
        """Validate EPUB file path."""
        resolved = Path(path).resolve()

        # Must be within user's home directory
        if not resolved.is_relative_to(Path.home()):
            raise ValueError(f"Path outside home directory: {path}")

        # Must be a file and exist
        if not resolved.is_file():
            raise FileNotFoundError(f"EPUB file not found: {path}")

        return resolved

    @staticmethod
    def validate_chapter_path(path: str) -> str:
        """Validate chapter internal path."""
        if ".." in path or path.startswith("/"):
            raise ValueError(f"Path traversal attempt: {path}")

        # Normalize path
        normalized = Path(path).as_posix()
        return normalized
