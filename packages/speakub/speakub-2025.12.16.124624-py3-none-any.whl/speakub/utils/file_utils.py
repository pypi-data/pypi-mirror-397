#!/usr/bin/env python3
"""
This module provides enhanced file and memory management utilities for the EPUB reader.
Provides safe temporary file management, memory monitoring, and automatic resource cleanup.
"""

import atexit
import logging
import os
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

import psutil

# Set up logging
logger = logging.getLogger(__name__)

# Global resource tracking
_temp_files: List[str] = []
_temp_dirs: List[str] = []
_resource_locks: Dict[str, threading.RLock] = {}
_cleanup_callbacks: List[Callable] = []

# Configuration
MAX_TEMP_FILE_AGE_HOURS = 24
TEMP_DIR_MAX_SIZE_MB = 500
# Increased from 200MB to 512MB for TTS application
MEMORY_WARNING_THRESHOLD_MB = 512
# Increased from 400MB to 800MB for TTS application
MEMORY_CRITICAL_THRESHOLD_MB = 800


class ResourceManager:
    """Centralized resource management with automatic cleanup."""

    def __init__(self):
        """Initialize resource manager."""
        self._memory_monitor_active = False
        self._memory_monitor_thread: Optional[threading.Thread] = None
        self._memory_monitor_event = threading.Event()
        self._memory_stats = {
            "peak_memory_mb": 0.0,
            "current_memory_mb": 0.0,
            "warning_count": 0,
            "critical_count": 0,
        }
        self._lock = threading.RLock()

        # Register cleanup on exit
        atexit.register(self.cleanup_all_resources)

    def start_memory_monitoring(self, interval_seconds: int = 30) -> None:
        """
        Start background memory monitoring.

        Args:
            interval_seconds: Monitoring interval
        """
        with self._lock:
            if self._memory_monitor_active:
                return

            self._memory_monitor_active = True
            self._memory_monitor_thread = threading.Thread(
                target=self._monitor_memory_loop,
                args=(interval_seconds,),
                name="MemoryMonitor",
                daemon=True,
            )
            self._memory_monitor_thread.start()
            logger.info("Memory monitoring started")

    def stop_memory_monitoring(self) -> None:
        """Stop background memory monitoring."""
        with self._lock:
            if not self._memory_monitor_active:
                return

            self._memory_monitor_active = False
            # Signal the monitoring thread to wake up immediately
            self._memory_monitor_event.set()
            if self._memory_monitor_thread and self._memory_monitor_thread.is_alive():
                self._memory_monitor_thread.join(timeout=5.0)
            logger.info("Memory monitoring stopped")

    def _monitor_memory_loop(self, interval: int) -> None:
        """Background memory monitoring loop."""
        while self._memory_monitor_active:
            try:
                self._check_memory_usage()
                # Use interruptible wait instead of blocking sleep
                self._memory_monitor_event.wait(timeout=interval)
                # Clear the event for next iteration
                self._memory_monitor_event.clear()
            except Exception as e:
                logger.debug(f"Memory monitoring error: {e}")
                # Use interruptible wait for error backoff as well
                self._memory_monitor_event.wait(timeout=5)
                self._memory_monitor_event.clear()

    def _check_memory_usage(self) -> None:
        """Check current memory usage and log warnings if needed."""
        try:
            from speakub.utils.resource_monitor import get_unified_resource_monitor

            # Use unified resource monitor
            unified_monitor = get_unified_resource_monitor()
            system_info = unified_monitor.get_system_info()
            memory_mb = system_info.get("process_memory_mb", 0.0)

            with self._lock:
                self._memory_stats["current_memory_mb"] = memory_mb
                self._memory_stats["peak_memory_mb"] = max(
                    self._memory_stats["peak_memory_mb"], memory_mb
                )

            # Check thresholds
            if memory_mb > MEMORY_CRITICAL_THRESHOLD_MB:
                self._memory_stats["critical_count"] += 1
                logger.warning(
                    f"Critical memory usage: {memory_mb:.1f}MB "
                    f"(limit: {MEMORY_CRITICAL_THRESHOLD_MB}MB)"
                )
                self._trigger_memory_cleanup()
            elif memory_mb > MEMORY_WARNING_THRESHOLD_MB:
                self._memory_stats["warning_count"] += 1
                logger.warning(
                    f"High memory usage: {memory_mb:.1f}MB "
                    f"(warning: {MEMORY_WARNING_THRESHOLD_MB}MB)"
                )

        except Exception as e:
            logger.debug(f"Memory check error: {e}")

    def _trigger_memory_cleanup(self) -> None:
        """Trigger memory cleanup operations."""
        try:
            # Force garbage collection
            import gc

            collected = gc.collect()
            logger.debug(f"Garbage collection collected {collected} objects")

            # Clean up old temp files
            self.cleanup_temp_files_by_age()

        except Exception as e:
            logger.debug(f"Memory cleanup error: {e}")

    @contextmanager
    def managed_temp_file(
        self, suffix: str = "", prefix: str = "", delete: bool = True
    ):
        """
        Context manager for temporary files with automatic cleanup.

        Args:
            suffix: File extension
            prefix: File prefix
            delete: Whether to delete on exit

        Yields:
            str: Path to temporary file
        """
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix, prefix=prefix, dir=get_temp_dir()
        )
        os.close(fd)  # Close file descriptor, keep path

        # Track file if we should delete it
        if delete:
            with self._lock:
                _temp_files.append(temp_path)

        try:
            yield temp_path
        finally:
            if delete and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                    logger.debug(f"Auto-cleaned temp file: {temp_path}")
                except OSError as e:
                    logger.debug(f"Failed to clean temp file {temp_path}: {e}")

    @contextmanager
    def managed_temp_dir(self, delete: bool = True):
        """
        Context manager for temporary directories with automatic cleanup.

        Args:
            delete: Whether to delete on exit

        Yields:
            str: Path to temporary directory
        """
        temp_dir = tempfile.mkdtemp(dir=get_temp_dir())

        # Track directory if we should delete it
        if delete:
            with self._lock:
                _temp_dirs.append(temp_dir)

        try:
            yield temp_dir
        finally:
            if delete and os.path.exists(temp_dir):
                try:
                    import shutil

                    shutil.rmtree(temp_dir)
                    logger.debug(f"Auto-cleaned temp directory: {temp_dir}")
                except OSError as e:
                    logger.debug(f"Failed to clean temp dir {temp_dir}: {e}")

    def register_cleanup_callback(self, callback: Callable) -> None:
        """
        Register a callback to be called during cleanup.

        Args:
            callback: Function to call during cleanup
        """
        with self._lock:
            _cleanup_callbacks.append(callback)

    def cleanup_temp_files_by_age(
        self, max_age_hours: int = MAX_TEMP_FILE_AGE_HOURS
    ) -> int:
        """
        Clean up temporary files older than specified age.

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            int: Number of files cleaned up
        """
        return cleanup_temp_files_by_age(max_age_hours)

    def cleanup_temp_files_by_size(
        self, max_size_mb: int = TEMP_DIR_MAX_SIZE_MB
    ) -> int:
        """
        Clean up oldest temporary files until directory size is below limit.

        Args:
            max_size_mb: Maximum directory size in MB

        Returns:
            int: Number of files cleaned up
        """
        return cleanup_temp_files_by_size(max_size_mb)

    def get_resource_stats(self) -> Dict[str, Any]:
        """Get comprehensive resource usage statistics."""
        with self._lock:
            temp_dir_stats = {
                "temp_files_count": len(_temp_files),
                "temp_dirs_count": len(_temp_dirs),
                "total_temp_files_size_mb": (
                    sum(os.path.getsize(f) for f in _temp_files if os.path.exists(f))
                    / (1024 * 1024)
                    if _temp_files
                    else 0
                ),
            }

        # Get system memory information
        try:
            from speakub.utils.resource_monitor import get_unified_resource_monitor

            # Use unified resource monitor
            unified_monitor = get_unified_resource_monitor()
            system_info = unified_monitor.get_system_info()
            system_memory_available_gb = system_info.get(
                "system_memory_available_gb", 0.0
            )
        except Exception:
            system_memory_available_gb = 0.0

        return {
            **self._memory_stats,
            **temp_dir_stats,
            "temp_dir_path": get_temp_dir(),
            "cleanup_callbacks_count": len(_cleanup_callbacks),
            "resource_locks_count": len(_resource_locks),
            "system_memory_available_gb": system_memory_available_gb,
        }

    def cleanup_all_resources(self) -> None:
        """Clean up all tracked resources."""
        logger.debug("Starting comprehensive resource cleanup")

        # Clean up temporary files
        cleanup_temp_files()

        # Clean up temporary directories (modify the global list)
        for temp_dir in _temp_dirs[:]:
            try:
                if os.path.exists(temp_dir):
                    import shutil

                    shutil.rmtree(temp_dir)
                    logger.debug(f"Cleaned up temp directory: {temp_dir}")
            except OSError as e:
                logger.debug(f"Failed to clean temp dir {temp_dir}: {e}")

        # Call cleanup callbacks first
        for callback in _cleanup_callbacks[:]:
            try:
                callback()
            except Exception as e:
                logger.debug(f"Cleanup callback error: {e}")

        # Clear tracking lists
        _temp_files.clear()
        _temp_dirs.clear()
        _cleanup_callbacks.clear()

        logger.debug("Resource cleanup completed")


# Global resource manager instance
_resource_manager = ResourceManager()


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    return _resource_manager


def ensure_directory(path: str) -> None:
    """
    Ensures that a directory exists. If it doesn't, it creates it.

    Args:
        path (str): The path to the directory.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
            logger.debug(f"Created directory: {path}")
        except OSError as e:
            logger.error(f"Error creating directory {path}: {e}")
            raise


def get_temp_dir() -> str:
    """
    Gets the path to a temporary directory for the application.

    Returns:
        str: The path to the temporary directory.
    """
    temp_dir = os.path.join(tempfile.gettempdir(), "speakub")
    ensure_directory(temp_dir)
    return temp_dir


def register_temp_file(temp_file: str) -> None:
    """
    Register a temporary file for cleanup.

    Args:
        temp_file: Path to temporary file
    """
    with _resource_manager._lock:
        if temp_file not in _temp_files:
            _temp_files.append(temp_file)


def unregister_temp_file(temp_file: str) -> None:
    """
    Unregister a temporary file from cleanup tracking.

    Args:
        temp_file: Path to temporary file
    """
    with _resource_manager._lock:
        if temp_file in _temp_files:
            _temp_files.remove(temp_file)


def cleanup_temp_files() -> None:
    """
    Removes all temporary files created during the session.
    """
    cleaned_count = 0

    with _resource_manager._lock:
        # Copy to avoid modification during iteration
        for temp_file in _temp_files[:]:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    logger.debug(f"Removed temporary file: {temp_file}")
                    cleaned_count += 1
            except OSError as e:
                logger.error(f"Error removing temporary file {temp_file}: {e}")

        _temp_files.clear()

    logger.info(f"Cleaned up {cleaned_count} temporary files")


def cleanup_temp_files_by_age(max_age_hours: int = MAX_TEMP_FILE_AGE_HOURS) -> int:
    """
    Clean up temporary files older than specified age.

    Args:
        max_age_hours: Maximum age in hours

    Returns:
        int: Number of files cleaned up
    """
    temp_dir = Path(get_temp_dir())
    max_age_seconds = max_age_hours * 3600
    current_time = time.time()
    cleaned_count = 0

    try:
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                try:
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old temp file: {file_path}")
                except OSError as e:
                    logger.debug(f"Failed to clean up {file_path}: {e}")
    except Exception as e:
        logger.debug(f"Error during temp file cleanup by age: {e}")

    return cleaned_count


def cleanup_temp_files_by_size(max_size_mb: int = TEMP_DIR_MAX_SIZE_MB) -> int:
    """
    Clean up oldest temporary files until directory size is below limit.

    Args:
        max_size_mb: Maximum directory size in MB

    Returns:
        int: Number of files cleaned up
    """
    temp_dir = Path(get_temp_dir())
    max_size_bytes = max_size_mb * 1024 * 1024
    cleaned_count = 0

    try:
        # Get all files with their modification times
        files_with_mtime = []
        for file_path in temp_dir.glob("*"):
            if file_path.is_file():
                try:
                    mtime = file_path.stat().st_mtime
                    size = file_path.stat().st_size
                    files_with_mtime.append((file_path, mtime, size))
                except OSError:
                    continue

        # Sort by modification time (oldest first)
        files_with_mtime.sort(key=lambda x: x[1])

        # Calculate total size
        total_size = sum(size for _, _, size in files_with_mtime)

        # Remove oldest files until under limit
        for file_path, _, size in files_with_mtime:
            if total_size <= max_size_bytes:
                break

            try:
                file_path.unlink()
                total_size -= size
                cleaned_count += 1
                logger.debug(f"Cleaned up temp file for size: {file_path}")
            except OSError as e:
                logger.debug(f"Failed to clean up {file_path}: {e}")

    except Exception as e:
        logger.debug(f"Error during temp file cleanup by size: {e}")

    return cleaned_count


# Backward compatibility
def track_temp_file(temp_file: str) -> None:
    """Alias for register_temp_file."""
    register_temp_file(temp_file)


# Example usage (for testing)
if __name__ == "__main__":
    # Test ensure_directory
    test_dir = os.path.join(get_temp_dir(), "test_dir")
    print(f"Ensuring directory exists: {test_dir}")
    ensure_directory(test_dir)
    print(f"Directory exists: {os.path.exists(test_dir)}")

    # Test get_temp_dir
    app_temp_dir = get_temp_dir()
    print(f"Application temporary directory: {app_temp_dir}")
    print(f"Temp dir exists: {os.path.exists(app_temp_dir)}")

    # Clean up test directory
    if os.path.exists(test_dir):
        os.rmdir(test_dir)
        print(f"Cleaned up test directory: {test_dir}")

    print("File utils test complete.")
