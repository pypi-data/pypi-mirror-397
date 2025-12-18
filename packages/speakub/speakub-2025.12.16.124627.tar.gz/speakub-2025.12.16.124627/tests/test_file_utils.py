#!/usr/bin/env python3
"""
Unit tests for file_utils.py module.
"""

import os
import tempfile
import time
import pytest
from pathlib import Path

from speakub.utils.file_utils import (
    ensure_directory,
    get_temp_dir,
    register_temp_file,
    unregister_temp_file,
    cleanup_temp_files,
    cleanup_temp_files_by_age,
    cleanup_temp_files_by_size,
    get_resource_manager,
    ResourceManager,
)


class TestFileUtils:
    """Test cases for file utilities."""

    def test_ensure_directory_creates_new_directory(self):
        """Test that ensure_directory creates a new directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_path = os.path.join(temp_dir, "new_test_dir")

            # Directory should not exist initially
            assert not os.path.exists(test_path)

            # Ensure directory
            ensure_directory(test_path)

            # Directory should now exist
            assert os.path.exists(test_path)
            assert os.path.isdir(test_path)

    def test_ensure_directory_existing_directory(self):
        """Test that ensure_directory works with existing directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Directory already exists
            assert os.path.exists(temp_dir)

            # Should not raise error
            ensure_directory(temp_dir)

            # Directory should still exist
            assert os.path.exists(temp_dir)

    def test_get_temp_dir_returns_valid_path(self):
        """Test that get_temp_dir returns a valid directory path."""
        temp_dir = get_temp_dir()

        # Should return a string path
        assert isinstance(temp_dir, str)

        # Directory should exist
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)

        # Should be within system temp directory
        system_temp = tempfile.gettempdir()
        assert temp_dir.startswith(system_temp)

        # Should contain 'speakub' in path
        assert "speakub" in temp_dir

    def test_register_and_unregister_temp_file(self):
        """Test registering and unregistering temporary files."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Register the file
            register_temp_file(temp_path)

            # File should be in tracking list
            from speakub.utils.file_utils import _temp_files
            assert temp_path in _temp_files

            # Unregister the file
            unregister_temp_file(temp_path)

            # File should not be in tracking list
            assert temp_path not in _temp_files

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_cleanup_temp_files_removes_registered_files(self):
        """Test that cleanup_temp_files removes registered temporary files."""
        # Create multiple temporary files
        temp_files = []
        for i in range(3):
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_path = temp_file.name
                temp_files.append(temp_path)
                register_temp_file(temp_path)

        # Verify files exist and are registered
        for temp_path in temp_files:
            assert os.path.exists(temp_path)

        from speakub.utils.file_utils import _temp_files
        for temp_path in temp_files:
            assert temp_path in _temp_files

        # Clean up temp files
        cleanup_temp_files()

        # Files should be removed and unregistered
        for temp_path in temp_files:
            assert not os.path.exists(temp_path)
            assert temp_path not in _temp_files

    def test_cleanup_temp_files_by_age(self):
        """Test cleanup of old temporary files."""
        temp_dir = Path(get_temp_dir())

        # Create some test files with different ages
        old_file = temp_dir / "old_test_file.txt"
        new_file = temp_dir / "new_test_file.txt"

        # Create old file (simulate old timestamp)
        old_file.write_text("old content")
        old_timestamp = time.time() - (25 * 3600)  # 25 hours ago
        os.utime(old_file, (old_timestamp, old_timestamp))

        # Create new file
        new_file.write_text("new content")

        try:
            # Clean up files older than 24 hours
            cleaned_count = cleanup_temp_files_by_age(max_age_hours=24)

            # Old file should be cleaned up
            assert not old_file.exists()
            assert cleaned_count >= 1

            # New file should still exist
            assert new_file.exists()

        finally:
            # Clean up remaining files
            if new_file.exists():
                new_file.unlink()

    def test_cleanup_temp_files_by_size(self):
        """Test cleanup of files when directory exceeds size limit."""
        temp_dir = Path(get_temp_dir())

        # Create test files
        files = []
        for i in range(5):
            file_path = temp_dir / f"size_test_{i}.txt"
            # Create file with ~1MB content
            content = "x" * (1024 * 1024)  # 1MB
            file_path.write_text(content)
            files.append(file_path)

        try:
            # Set very low size limit (1MB total)
            cleaned_count = cleanup_temp_files_by_size(max_size_mb=1)

            # Some files should have been cleaned up
            assert cleaned_count > 0

            # Check remaining files
            remaining_files = [f for f in files if f.exists()]
            total_size = sum(
                f.stat().st_size for f in remaining_files) / (1024 * 1024)

            # Total size should be under limit
            assert total_size <= 1.1  # Allow some tolerance

        finally:
            # Clean up remaining files
            for file_path in files:
                if file_path.exists():
                    file_path.unlink()

    def test_resource_manager_managed_temp_file(self):
        """Test ResourceManager.managed_temp_file context manager."""
        manager = ResourceManager()

        with manager.managed_temp_file(suffix=".txt", prefix="test_") as temp_path:
            # File should exist during context
            assert os.path.exists(temp_path)
            assert temp_path.endswith(".txt")
            assert "test_" in os.path.basename(temp_path)

            # Write something to the file
            with open(temp_path, 'w') as f:
                f.write("test content")

            # Verify content
            with open(temp_path, 'r') as f:
                assert f.read() == "test content"

        # File should be automatically cleaned up after context
        assert not os.path.exists(temp_path)

    def test_resource_manager_managed_temp_dir(self):
        """Test ResourceManager.managed_temp_dir context manager."""
        manager = ResourceManager()

        with manager.managed_temp_dir() as temp_dir:
            # Directory should exist during context
            assert os.path.exists(temp_dir)
            assert os.path.isdir(temp_dir)

            # Create a file in the directory
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test content")

            # Verify file exists
            assert os.path.exists(test_file)

        # Directory should be automatically cleaned up after context
        assert not os.path.exists(temp_dir)

    def test_resource_manager_memory_monitoring(self):
        """Test ResourceManager memory monitoring functionality."""
        manager = ResourceManager()

        # Start monitoring
        manager.start_memory_monitoring(interval_seconds=1)

        # Let it run for a bit
        time.sleep(2)

        # Stop monitoring
        manager.stop_memory_monitoring()

        # Check that monitoring thread stopped
        assert not manager._memory_monitor_active

        # Get stats
        stats = manager.get_resource_stats()

        # Should have memory stats
        assert "current_memory_mb" in stats
        assert "peak_memory_mb" in stats
        assert isinstance(stats["current_memory_mb"], (int, float))
        assert isinstance(stats["peak_memory_mb"], (int, float))

    def test_resource_manager_cleanup_callbacks(self):
        """Test ResourceManager cleanup callback functionality."""
        manager = ResourceManager()

        callback_called = False

        def test_callback():
            nonlocal callback_called
            callback_called = True

        # Register callback
        manager.register_cleanup_callback(test_callback)

        # Trigger cleanup
        manager.cleanup_all_resources()

        # Callback should have been called
        assert callback_called

    def test_resource_manager_stats(self):
        """Test ResourceManager statistics reporting."""
        manager = ResourceManager()

        stats = manager.get_resource_stats()

        # Check required fields
        required_fields = [
            "peak_memory_mb",
            "current_memory_mb",
            "warning_count",
            "critical_count",
            "temp_files_count",
            "temp_dirs_count",
            "total_temp_files_size_mb",
            "temp_dir_path",
            "cleanup_callbacks_count",
            "resource_locks_count",
        ]

        for field in required_fields:
            assert field in stats
            assert isinstance(stats[field], (int, float, str))


if __name__ == "__main__":
    pytest.main([__file__])
