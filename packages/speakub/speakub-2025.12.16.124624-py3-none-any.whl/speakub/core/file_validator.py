"""
File Validator - EPUB file validation and security checks
Simplified for SpeakUB V32: Delegates structural validation to epubkit.
"""

import logging
import os

# Import exceptions locally to avoid circular imports if necessary,
# though ideally these should come from speakub.core.exceptions
try:
    from speakub.core.exceptions import FileSizeException, SecurityException
except ImportError:
    class FileSizeException(Exception): pass
    class SecurityException(Exception): pass

logger = logging.getLogger(__name__)

class FileValidator:
    """EPUB file validation and security checks."""

    # Security limits
    MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_PATH_LENGTH = 1000

    @classmethod
    def validate_epub_file(cls, epub_path: str) -> None:
        """
        Validate EPUB file basic security checks.

        Note: Deep structural validation (mimetype, container.xml) is now
        delegated to epubkit during the open process.
        """
        if not os.path.exists(epub_path):
            raise FileNotFoundError(f"File not found: {epub_path}")

        if not os.path.isfile(epub_path):
            raise SecurityException(f"Path is not a file: {epub_path}")

        # Security check: file size limit
        file_size = os.path.getsize(epub_path)
        if file_size > cls.MAX_FILE_SIZE:
            raise FileSizeException(
                f"EPUB file too large: {file_size} bytes (max: {cls.MAX_FILE_SIZE})"
            )

        # Basic extension check
        if not epub_path.lower().endswith('.epub'):
            logger.warning(f"File {epub_path} does not have .epub extension")

    @classmethod
    def validate_chapter_path(cls, src: str) -> None:
        """Validate chapter path for security (Path Traversal)."""
        from urllib.parse import unquote

        if not src:
            raise ValueError("Chapter source path cannot be empty")

        # URL decode
        decoded_src = unquote(src)

        # Dangerous patterns check
        DANGEROUS_PATTERNS = [
            "..",  # Parent directory reference
            "../",  # Unix parent directory
            "..\\",  # Windows parent directory
        ]

        decoded_lower = decoded_src.lower()
        for pattern in DANGEROUS_PATTERNS:
            if pattern in decoded_lower:
                raise SecurityException(f"Path traversal detected: {decoded_src}")

        # Absolute path check
        if decoded_src.startswith("/") or (
            len(decoded_src) > 1 and decoded_src[1] == ":"
        ):
            raise SecurityException(f"Absolute path not allowed: {decoded_src}")
