#!/usr/bin/env python3
"""
Unit tests for security.py module.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from speakub.utils.security import InputValidator, TextSanitizer, PathValidator


class TestInputValidator:
    """Test cases for InputValidator class."""

    def test_validate_epub_path_valid(self):
        """Test validating a valid EPUB path."""
        # Create a minimal valid EPUB file (ZIP with mimetype)
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            import zipfile
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('mimetype', 'application/epub+zip')
            temp_path = f.name

        try:
            with patch("speakub.utils.config.ConfigManager") as mock_config:
                mock_config.return_value.get.return_value = 100  # 100MB max
                result = InputValidator.validate_epub_path(temp_path)
                assert result is True
        finally:
            os.unlink(temp_path)

    def test_validate_epub_path_nonexistent(self):
        """Test validating a nonexistent EPUB path."""
        result = InputValidator.validate_epub_path("/nonexistent/file.epub")
        assert result is False

    def test_validate_epub_path_directory(self):
        """Test validating a directory instead of file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = InputValidator.validate_epub_path(temp_dir)
            assert result is False

    def test_validate_epub_path_wrong_extension(self):
        """Test validating a file with wrong extension."""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            result = InputValidator.validate_epub_path(temp_path)
            assert result is False
        finally:
            os.unlink(temp_path)

    def test_validate_epub_path_empty_file(self):
        """Test validating an empty EPUB file."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            # Don't write anything - file remains empty
            temp_path = f.name

        try:
            result = InputValidator.validate_epub_path(temp_path)
            assert result is False
        finally:
            os.unlink(temp_path)

    def test_validate_epub_path_too_large(self):
        """Test validating an EPUB file that's too large."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            # Write content larger than default max (50MB)
            f.write(b"x" * (60 * 1024 * 1024))  # 60MB
            temp_path = f.name

        try:
            with patch("speakub.utils.config.ConfigManager") as mock_config:
                mock_config.return_value.get.return_value = 50  # 50MB max
                result = InputValidator.validate_epub_path(temp_path)
                assert result is False
        finally:
            os.unlink(temp_path)

    def test_validate_epub_path_not_readable(self):
        """Test validating an EPUB file that's not readable."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            f.write(b"test content")
            temp_path = f.name

        try:
            # Make file unreadable
            os.chmod(temp_path, 0o000)
            result = InputValidator.validate_epub_path(temp_path)
            assert result is False
        finally:
            # Restore permissions for cleanup
            try:
                os.chmod(temp_path, 0o644)
                os.unlink(temp_path)
            except:
                pass

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        result = InputValidator.sanitize_filename("normal_file.txt")
        assert result == "normal_file.txt"

    def test_sanitize_filename_dangerous_chars(self):
        """Test sanitization of dangerous characters."""
        result = InputValidator.sanitize_filename('file<>:|?"*.txt')
        assert result == "file________.txt"

    def test_sanitize_filename_leading_dots(self):
        """Test removal of leading dots."""
        result = InputValidator.sanitize_filename("...hidden_file")
        assert result == "hidden_file"

    def test_sanitize_filename_too_long(self):
        """Test truncation of overly long filenames."""
        long_name = "a" * 300
        result = InputValidator.sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith("a" * (255 - len(".txt"))
                               )  # Assuming no extension

    def test_sanitize_filename_empty(self):
        """Test sanitization of empty filename."""
        result = InputValidator.sanitize_filename("")
        assert result == "unnamed_file"

    def test_sanitize_filename_only_dots(self):
        """Test sanitization of filename with only dots."""
        result = InputValidator.sanitize_filename("...")
        assert result == "unnamed_file"

    def test_sanitize_path_basic(self):
        """Test basic path sanitization."""
        result = InputValidator._sanitize_path("normal/path/file.epub")
        assert result == "normal/path/file.epub"

    def test_sanitize_path_parent_dirs(self):
        """Test removal of parent directory references."""
        result = InputValidator._sanitize_path("../../../etc/passwd")
        assert ".." not in result

    def test_sanitize_path_double_slashes(self):
        """Test normalization of double slashes."""
        result = InputValidator._sanitize_path("path//to//file")
        assert "//" not in result

    def test_has_suspicious_content_valid_epub(self):
        """Test checking valid EPUB content."""
        # Create a minimal valid EPUB structure
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            # Create a simple ZIP file with mimetype
            import zipfile
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('mimetype', 'application/epub+zip')
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0"?><container><rootfiles><rootfile/></rootfiles></container>')
            temp_path = f.name

        try:
            result = InputValidator._has_suspicious_content(Path(temp_path))
            assert result is False
        finally:
            os.unlink(temp_path)

    def test_has_suspicious_content_invalid_mimetype(self):
        """Test checking EPUB with invalid mimetype."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            import zipfile
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('mimetype', 'application/zip')  # Wrong mimetype
            temp_path = f.name

        try:
            result = InputValidator._has_suspicious_content(Path(temp_path))
            assert result is True
        finally:
            os.unlink(temp_path)

    def test_has_suspicious_content_suspicious_extension(self):
        """Test checking EPUB with suspicious file extensions."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            import zipfile
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('mimetype', 'application/epub+zip')
                zf.writestr('malicious.exe', 'evil content')
            temp_path = f.name

        try:
            result = InputValidator._has_suspicious_content(Path(temp_path))
            assert result is True
        finally:
            os.unlink(temp_path)

    def test_has_suspicious_content_too_many_files(self):
        """Test checking EPUB with too many files."""
        with tempfile.NamedTemporaryFile(suffix=".epub", delete=False) as f:
            import zipfile
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('mimetype', 'application/epub+zip')
                # Create many files
                for i in range(11000):  # More than default max of 10000
                    zf.writestr(f'file{i}.txt', f'content {i}')
            temp_path = f.name

        try:
            with patch("speakub.utils.config.ConfigManager") as mock_config:
                mock_config.return_value.get.return_value = 10000
                result = InputValidator._has_suspicious_content(
                    Path(temp_path))
                assert result is True
        finally:
            os.unlink(temp_path)


class TestTextSanitizer:
    """Test cases for TextSanitizer class."""

    def test_sanitize_tts_text_normal(self):
        """Test sanitizing normal TTS text."""
        text = "This is normal text for TTS."
        result = TextSanitizer.sanitize_tts_text(text)
        assert result == text

    def test_sanitize_tts_text_non_string(self):
        """Test sanitizing non-string input."""
        result = TextSanitizer.sanitize_tts_text(123)
        assert result == "123"

    def test_sanitize_tts_text_too_long(self):
        """Test sanitizing text that's too long."""
        long_text = "a" * (TextSanitizer.MAX_TEXT_LENGTH + 1000)
        result = TextSanitizer.sanitize_tts_text(long_text)

        assert len(result) <= TextSanitizer.MAX_TEXT_LENGTH
        assert "[Text truncated for TTS]" in result

    def test_sanitize_tts_text_control_chars(self):
        """Test removing control characters."""
        text = "Hello\x00world\x01test\x1f"
        result = TextSanitizer.sanitize_tts_text(text)
        assert "\x00" not in result
        assert "\x01" not in result
        assert "\x1f" not in result
        assert "Helloworldtest" in result

    def test_sanitize_tts_text_whitespace(self):
        """Test normalizing whitespace."""
        text = "Hello   world\t\t\ttest\n\n\n\nmore"
        result = TextSanitizer.sanitize_tts_text(text)
        assert "   " not in result
        assert "\t\t\t" not in result
        assert "\n\n\n\n" not in result
        assert result.count("\n") <= 2  # Max consecutive newlines

    def test_sanitize_tts_text_empty_after_processing(self):
        """Test handling text that becomes empty after sanitization."""
        text = "\x00\x01\x02"  # Only control characters
        result = TextSanitizer.sanitize_tts_text(text)
        assert result == "Empty text"

    def test_validate_tts_text_valid(self):
        """Test validating valid TTS text."""
        text = "This is valid text."
        result = TextSanitizer.validate_tts_text(text)
        assert result is True

    def test_validate_tts_text_empty(self):
        """Test validating empty TTS text."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TextSanitizer.validate_tts_text("")

    def test_validate_tts_text_whitespace_only(self):
        """Test validating whitespace-only TTS text."""
        with pytest.raises(ValueError, match="cannot be empty"):
            TextSanitizer.validate_tts_text("   \n\t   ")

    def test_validate_tts_text_wrong_type(self):
        """Test validating non-string TTS text."""
        with pytest.raises(TypeError, match="must be string"):
            TextSanitizer.validate_tts_text(123)

    def test_validate_tts_text_too_long(self):
        """Test validating text that's too long."""
        long_text = "a" * (TextSanitizer.MAX_TEXT_LENGTH + 1)
        with pytest.raises(ValueError, match="too long"):
            TextSanitizer.validate_tts_text(long_text)

    def test_validate_tts_text_malicious(self):
        """Test validating text with malicious content."""
        malicious_text = 'Hello <script>alert("xss")</script> world'
        with pytest.raises(ValueError, match="malicious content"):
            TextSanitizer.validate_tts_text(malicious_text)

    def test_contains_malicious_patterns_safe(self):
        """Test checking safe text for malicious patterns."""
        safe_text = "This is safe text with <b>bold</b> tags."
        result = TextSanitizer._contains_malicious_patterns(safe_text)
        assert result is False

    def test_contains_malicious_patterns_script(self):
        """Test detecting script tags."""
        malicious_text = '<script>alert("xss")</script>'
        result = TextSanitizer._contains_malicious_patterns(malicious_text)
        assert result is True

    def test_contains_malicious_patterns_javascript_url(self):
        """Test detecting JavaScript URLs."""
        malicious_text = 'javascript:alert("xss")'
        result = TextSanitizer._contains_malicious_patterns(malicious_text)
        assert result is True

    def test_contains_malicious_patterns_event_handler(self):
        """Test detecting event handlers."""
        malicious_text = '<a onclick="alert(\'xss\')">link</a>'
        result = TextSanitizer._contains_malicious_patterns(malicious_text)
        assert result is True


class TestPathValidator:
    """Test cases for PathValidator class."""

    @patch("pathlib.Path.home")
    def test_validate_epub_path_valid(self, mock_home):
        """Test validating a valid EPUB path."""
        mock_home.return_value = Path("/home/user")

        with tempfile.NamedTemporaryFile(suffix=".epub", dir="/home/user", delete=False) as f:
            f.write(b"test")
            temp_path = f.name

        try:
            result = PathValidator.validate_epub_path(temp_path)
            assert isinstance(result, Path)
            assert result.exists()
            assert result.is_file()
        finally:
            os.unlink(temp_path)

    @patch("pathlib.Path.home")
    def test_validate_epub_path_outside_home(self, mock_home):
        """Test validating EPUB path outside home directory."""
        mock_home.return_value = Path("/home/user")

        with pytest.raises(ValueError, match="outside home directory"):
            PathValidator.validate_epub_path("/etc/passwd")

    def test_validate_epub_path_nonexistent(self):
        """Test validating nonexistent EPUB path."""
        with pytest.raises(FileNotFoundError, match="not found"):
            PathValidator.validate_epub_path("/nonexistent/file.epub")

    @patch("pathlib.Path.home")
    def test_validate_epub_path_directory(self, mock_home):
        """Test validating directory instead of file."""
        mock_home.return_value = Path("/tmp")

        with pytest.raises(FileNotFoundError, match="not found"):
            PathValidator.validate_epub_path("/tmp")

    def test_validate_chapter_path_valid(self):
        """Test validating valid chapter path."""
        result = PathValidator.validate_chapter_path("chapter1.xhtml")
        assert result == "chapter1.xhtml"

    def test_validate_chapter_path_with_subdir(self):
        """Test validating chapter path with subdirectory."""
        result = PathValidator.validate_chapter_path("OEBPS/chapter1.xhtml")
        assert result == "OEBPS/chapter1.xhtml"

    def test_validate_chapter_path_parent_traversal(self):
        """Test rejecting path with parent traversal."""
        with pytest.raises(ValueError, match="traversal attempt"):
            PathValidator.validate_chapter_path("../chapter1.xhtml")

    def test_validate_chapter_path_absolute(self):
        """Test rejecting absolute path."""
        with pytest.raises(ValueError, match="traversal attempt"):
            PathValidator.validate_chapter_path("/etc/passwd")

    def test_validate_chapter_path_normalized(self):
        """Test path normalization."""
        result = PathValidator.validate_chapter_path(
            "path/./to/../chapter.xhtml")
        assert result == "path/to/chapter.xhtml"


if __name__ == "__main__":
    pytest.main([__file__])
