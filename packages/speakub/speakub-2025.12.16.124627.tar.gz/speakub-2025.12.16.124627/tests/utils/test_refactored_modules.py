"""
Tests for refactored modules: FileValidator
Note: CacheManager and ChapterLoader tests removed in V32 cleanup.
"""

import pytest
from unittest.mock import patch, MagicMock
import os

from speakub.core.file_validator import FileValidator
from speakub.core.exceptions import FileSizeException, SecurityException


class TestFileValidator:
    """Test FileValidator class"""

    def test_security_limits(self):
        """Test security limit constants"""
        assert FileValidator.MAX_FILE_SIZE == 500 * 1024 * 1024
        assert FileValidator.MAX_PATH_LENGTH == 1000

    @patch('os.path.exists', return_value=True)
    @patch('os.path.isfile', return_value=True)
    @patch('os.path.getsize')
    def test_validate_epub_file_large_file(self, mock_getsize, mock_isfile, mock_exists):
        """Test large file detection"""
        mock_getsize.return_value = FileValidator.MAX_FILE_SIZE + 1

        with pytest.raises(FileSizeException):
            FileValidator.validate_epub_file("large.epub")

    def test_validate_chapter_path_empty(self):
        """Test empty chapter path validation"""
        with pytest.raises(ValueError, match="cannot be empty"):
            FileValidator.validate_chapter_path("")

    def test_validate_chapter_path_traversal(self):
        """Test path traversal detection in chapter paths"""
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\windows\\system32\\config",
            "/absolute/path"
        ]

        for path in dangerous_paths:
            with pytest.raises(SecurityException):
                FileValidator.validate_chapter_path(path)

    def test_validate_chapter_path_normal(self):
        """Test normal path validation passes"""
        normal_paths = [
            "chapter01.html",
            "section/chapter02.xhtml",
            "OEBPS/folder/file.htm"
        ]

        for path in normal_paths:
            # Should not raise any exception
            FileValidator.validate_chapter_path(path)


if __name__ == '__main__':
    pytest.main([__file__])
