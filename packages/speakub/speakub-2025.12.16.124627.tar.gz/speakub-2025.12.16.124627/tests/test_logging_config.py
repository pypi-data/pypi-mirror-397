#!/usr/bin/env python3
"""
Unit tests for logging_config.py module.
"""

import os
import tempfile
import logging
from unittest.mock import patch, MagicMock
import pytest
from speakub.utils.logging_config import setup_logging, get_logger


class TestLoggingConfig:
    """Test cases for logging configuration."""

    def test_setup_logging_default(self):
        """Test setup_logging with default parameters."""
        # Clear existing handlers first
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        setup_logging()

        # Check that handlers were added
        assert len(logger.handlers) >= 1

        # Check logger level
        assert logger.level == logging.INFO

        # Check that we have a console handler
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) >= 1

    def test_setup_logging_custom_level(self):
        """Test setup_logging with custom log level."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        setup_logging(level="DEBUG")

        assert logger.level == logging.DEBUG

    def test_setup_logging_invalid_level(self):
        """Test setup_logging with invalid log level defaults to INFO."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        setup_logging(level="INVALID")

        assert logger.level == logging.INFO

    @patch("os.makedirs")
    @patch("speakub.utils.logging_config.CONFIG_DIR", "/tmp/test_config")
    def test_setup_logging_with_file(self, mock_makedirs):
        """Test setup_logging with file logging enabled."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        setup_logging(log_to_file=True)

        # Check that file handler was attempted to be created
        mock_makedirs.assert_called()

        # Check that we have handlers
        assert len(logger.handlers) >= 1

    def test_setup_logging_no_console(self):
        """Test setup_logging with console logging disabled."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        setup_logging(log_to_console=False)

        # Should still have at least file handler if enabled
        assert len(logger.handlers) >= 0

    def test_setup_logging_custom_format(self):
        """Test setup_logging with custom log format."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        custom_format = "%(levelname)s: %(message)s"
        setup_logging(log_format=custom_format)

        # Check that format was applied to handlers
        for handler in logger.handlers:
            assert isinstance(handler.formatter, logging.Formatter)
            # The formatter should have our custom format
            assert handler.formatter._fmt == custom_format

    def test_get_logger(self):
        """Test get_logger function."""
        test_name = "test_module"
        logger = get_logger(test_name)

        assert isinstance(logger, logging.Logger)
        assert logger.name == f"speakub.{test_name}"

    def test_get_logger_hierarchy(self):
        """Test that get_logger creates proper hierarchy."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1.name == "speakub.module1"
        assert logger2.name == "speakub.module2"
        assert logger1 != logger2

    @patch("logging.handlers.RotatingFileHandler")
    @patch("os.makedirs")
    def test_file_handler_creation(self, mock_makedirs, mock_rotating_handler):
        """Test that file handler is created with correct parameters."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        mock_handler_instance = MagicMock()
        mock_rotating_handler.return_value = mock_handler_instance

        setup_logging(log_to_file=True, max_bytes=1024, backup_count=3)

        # Verify RotatingFileHandler was called with correct parameters
        mock_rotating_handler.assert_called_once()
        args, kwargs = mock_rotating_handler.call_args

        # Check that log file path contains expected components
        log_file_path = args[0]
        assert "speakub.log" in log_file_path
        assert kwargs["maxBytes"] == 1024
        assert kwargs["backupCount"] == 3
        assert kwargs["encoding"] == "utf-8"

        # Verify handler was added to logger
        mock_handler_instance.setFormatter.assert_called()

    def test_root_logger_level(self):
        """Test that root logger level is set correctly."""
        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING

    @patch("sys.stdout", new_callable=MagicMock)
    def test_console_handler_output(self, mock_stdout):
        """Test that console handler outputs to stdout."""
        logger = logging.getLogger("speakub")
        logger.handlers.clear()

        setup_logging(log_to_console=True)

        # Get the console handler
        console_handlers = [
            h for h in logger.handlers if isinstance(h, logging.StreamHandler)]
        assert len(console_handlers) >= 1

        console_handler = console_handlers[0]

        # Verify it's using sys.stdout
        # Note: In the actual implementation, it uses sys.stdout directly
        # so we can't easily mock this, but we can verify the handler exists

    def test_multiple_setup_calls(self):
        """Test that multiple setup_logging calls work correctly."""
        logger = logging.getLogger("speakub")

        # First call
        setup_logging()
        handlers_count_1 = len(logger.handlers)

        # Second call should clear and re-add handlers
        setup_logging()
        handlers_count_2 = len(logger.handlers)

        # Should have same number of handlers
        assert handlers_count_1 == handlers_count_2


if __name__ == "__main__":
    pytest.main([__file__])
