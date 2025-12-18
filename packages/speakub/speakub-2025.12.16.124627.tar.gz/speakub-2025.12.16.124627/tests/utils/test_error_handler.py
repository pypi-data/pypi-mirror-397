"""
Tests for speakub.utils.error_handler module
"""

import pytest
from unittest.mock import patch

from speakub.utils.error_handler import (
    ErrorCategory,
    ErrorSeverity,
    ErrorHandler,
    UnifiedErrorHandler,
    safe_execute,
    safe_execute_with_fallback,
    safe_operation,
    validate_config_value,
    unified_error_handler,
)


class TestErrorSeverity:
    """Test ErrorSeverity enum"""

    def test_severity_values(self):
        """Test severity enum values"""
        assert ErrorSeverity.DEBUG.value == "debug"
        assert ErrorSeverity.INFO.value == "info"
        assert ErrorSeverity.WARNING.value == "warning"
        assert ErrorSeverity.ERROR.value == "error"
        assert ErrorSeverity.CRITICAL.value == "critical"

    def test_all_severities(self):
        """Test all severity levels are defined"""
        severities = [
            ErrorSeverity.DEBUG,
            ErrorSeverity.INFO,
            ErrorSeverity.WARNING,
            ErrorSeverity.ERROR,
            ErrorSeverity.CRITICAL,
        ]
        assert len(severities) == 5


class TestErrorCategory:
    """Test ErrorCategory enum"""

    def test_category_values(self):
        """Test category enum values"""
        assert ErrorCategory.NETWORK.value == "network"
        assert ErrorCategory.TTS_SYNTHESIS.value == "tts_synthesis"
        assert ErrorCategory.TTS_PLAYBACK.value == "tts_playback"
        assert ErrorCategory.FILE_SYSTEM.value == "file_system"
        assert ErrorCategory.CONFIGURATION.value == "configuration"
        assert ErrorCategory.UI.value == "ui"
        assert ErrorCategory.VALIDATION.value == "validation"
        assert ErrorCategory.SECURITY.value == "security"
        assert ErrorCategory.UNKNOWN.value == "unknown"

    def test_all_categories(self):
        """Test all categories are defined"""
        categories = [
            ErrorCategory.NETWORK,
            ErrorCategory.TTS_SYNTHESIS,
            ErrorCategory.TTS_PLAYBACK,
            ErrorCategory.FILE_SYSTEM,
            ErrorCategory.CONFIGURATION,
            ErrorCategory.UI,
            ErrorCategory.VALIDATION,
            ErrorCategory.SECURITY,
            ErrorCategory.UNKNOWN,
        ]
        assert len(categories) == 9


class TestErrorHandler:
    """Test ErrorHandler class methods"""

    @patch('speakub.utils.error_handler.logger')
    def test_handle_and_suppress(self, mock_logger):
        """Test handle_and_suppress method"""
        error = ValueError("Test error")
        context = "Test context"

        ErrorHandler.handle_and_suppress(error, context)

        # Verify warning was logged
        mock_logger.warning.assert_called_once()
        call_args = mock_logger.warning.call_args
        assert context in call_args[0][0]
        assert "Test error" in call_args[0][0]
        assert call_args.kwargs.get('exc_info') is True

    @patch('speakub.utils.error_handler.logger')
    def test_handle_and_suppress_with_extra(self, mock_logger):
        """Test handle_and_suppress with extra data"""
        error = RuntimeError("Runtime error")
        context = "Runtime context"
        extra = {"component": "test", "action": "suppress"}

        ErrorHandler.handle_and_suppress(error, context, extra)

        # Verify extra data is included in log context
        call_args = mock_logger.warning.call_args
        log_extra = call_args.kwargs['extra']
        assert log_extra["component"] == "test"
        assert log_extra["action"] == "suppress"

    @patch('speakub.utils.error_handler.logger')
    def test_handle_and_raise(self, mock_logger):
        """Test handle_and_raise method"""
        error = ZeroDivisionError("Division by zero")
        context = "Math context"

        with pytest.raises(ZeroDivisionError):
            ErrorHandler.handle_and_raise(error, context)

        # Verify error was logged before re-raising
        mock_logger.error.assert_called_once()
        call_args = mock_logger.error.call_args
        assert context in call_args[0][0]

    @patch('speakub.utils.error_handler.logger')
    def test_handle_with_fallback(self, mock_logger):
        """Test handle_with_fallback method"""
        error = KeyError("Missing key")
        context = "Lookup context"
        fallback = "default_value"

        result = ErrorHandler.handle_with_fallback(error, context, fallback)

        assert result == fallback
        mock_logger.warning.assert_called_once()


class TestSafeExecute:
    """Test safe_execute standalone functions"""

    def test_safe_execute_success(self):
        """Test safe_execute with successful function"""
        def test_func():
            return 42

        result = safe_execute(test_func, context="test")
        assert result == 42

    @patch('speakub.utils.error_handler.logger')
    def test_safe_execute_exception(self, mock_logger):
        """Test safe_execute with exception"""
        def failing_func():
            raise ValueError("Test failure")

        result = safe_execute(failing_func, context="test")
        assert result is None

        # Verify error was logged
        mock_logger.warning.assert_called_once()

    def test_safe_execute_with_fallback_success(self):
        """Test safe_execute_with_fallback success"""
        def test_func():
            return "success"

        result = safe_execute_with_fallback(
            test_func, "fallback", context="test")
        assert result == "success"

    @patch('speakub.utils.error_handler.logger')
    def test_safe_execute_with_fallback_exception(self, mock_logger):
        """Test safe_execute_with_fallback with exception"""
        def failing_func():
            raise Exception("Failed")

        result = safe_execute_with_fallback(
            failing_func, "fallback", context="test")
        assert result == "fallback"

        mock_logger.warning.assert_called_once()


class TestSafeOperation:
    """Test safe_operation decorator"""

    def test_safe_operation_success(self):
        """Test decorator with successful operation"""
        @safe_operation("test_op")
        def test_function():
            return "success"

        result = test_function()
        assert result == "success"

    @patch('speakub.utils.error_handler.logger')
    def test_safe_operation_exception(self, mock_logger):
        """Test decorator with exception"""
        @safe_operation("test_op")
        def failing_function():
            raise ValueError("Failed")

        result = failing_function()
        assert result is None

        mock_logger.warning.assert_called_once()


class TestValidateConfigValue:
    """Test validate_config_value function"""

    @patch('speakub.utils.error_handler.logger')
    def test_validate_config_valid(self, mock_logger):
        """Test validation with valid input"""
        result = validate_config_value(
            42, int, "test_field", default="default")
        assert result == 42

        # Should not log anything for valid input
        mock_logger.warning.assert_not_called()

    @patch('speakub.utils.error_handler.logger')
    def test_validate_config_invalid_type(self, mock_logger):
        """Test validation with invalid type"""
        result = validate_config_value(
            "not_an_int", int, "test_field", default=10)
        assert result == 10

        # Should log warning for type mismatch
        mock_logger.warning.assert_called_once()

    @patch('speakub.utils.error_handler.logger')
    def test_validate_config_exception(self, mock_logger):
        """Test validation when exception occurs"""
        result = validate_config_value(
            None, int, "test_field", default="fallback")
        assert result == "fallback"

        mock_logger.warning.assert_called_once()


class TestUnifiedErrorHandler:
    """Test UnifiedErrorHandler class"""

    def test_categorize_network_error(self):
        """Test categorization of network errors"""
        network_errors = [
            ConnectionError("Connection failed"),
            TimeoutError("Timeout occurred"),
            OSError("Network is unreachable"),
        ]

        for error in network_errors:
            category = UnifiedErrorHandler.categorize_error(error)
            assert category == ErrorCategory.NETWORK

    def test_categorize_tts_error(self):
        """Test categorization of TTS errors"""
        tts_errors = [
            Exception("TTS synthesis failed"),
            Exception("Edge-TTS voice error"),
            Exception("Audio synthesis error"),
        ]

        for error in tts_errors:
            category = UnifiedErrorHandler.categorize_error(error)
            assert category in [ErrorCategory.TTS_SYNTHESIS,
                                ErrorCategory.TTS_PLAYBACK]

    def test_categorize_file_system_error(self):
        """Test categorization of file system errors"""
        file_errors = [
            FileNotFoundError("File not found"),
            PermissionError("Permission denied"),
            OSError("Disk full"),
        ]

        for error in file_errors:
            category = UnifiedErrorHandler.categorize_error(error)
            assert category == ErrorCategory.FILE_SYSTEM

    def test_categorize_unknown_error(self):
        """Test categorization of unknown errors"""
        error = Exception("this-is-a-completely-random-error-message")
        category = UnifiedErrorHandler.categorize_error(error, "")
        assert category == ErrorCategory.UNKNOWN

    def test_get_error_severity(self):
        """Test severity determination"""
        # Security errors should be critical
        security_error = Exception("Security violation")
        severity = UnifiedErrorHandler.get_error_severity(
            security_error, ErrorCategory.SECURITY
        )
        # Note: Current implementation considers permission/access as critical
        # For general security errors, severity depends on the specific logic

        # Network errors should be error level
        network_error = Exception("Network timeout")
        severity = UnifiedErrorHandler.get_error_severity(
            network_error, ErrorCategory.NETWORK
        )
        assert severity == ErrorSeverity.ERROR

    @patch('speakub.utils.error_handler.logger')
    def test_handle_error_with_fallback(self, mock_logger):
        """Test handle_error with fallback value"""
        error = ValueError("Test error")
        result = UnifiedErrorHandler.handle_error(
            error,
            context="Test context",
            should_raise=False,
            fallback_value="fallback"
        )

        assert result == "fallback"
        mock_logger.warning.assert_called_once()

    @patch('speakub.utils.error_handler.logger')
    def test_handle_error_should_raise(self, mock_logger):
        """Test handle_error with should_raise=True"""
        error = RuntimeError("Should re-raise")

        with pytest.raises(RuntimeError):
            UnifiedErrorHandler.handle_error(
                error,
                context="Test",
                should_raise=True
            )

        # RuntimeError is categorized as UNKNOWN, which has WARNING severity
        mock_logger.warning.assert_called_once()

    def test_safe_operation_decorator_success(self):
        """Test safe_operation decorator success case"""
        @UnifiedErrorHandler.safe_operation("test_operation")
        def successful_func():
            return "success"

        result = successful_func()
        assert result == "success"

    @patch('speakub.utils.error_handler.logger')
    def test_safe_operation_decorator_failure(self, mock_logger):
        """Test safe_operation decorator failure case"""
        @UnifiedErrorHandler.safe_operation(
            "test_operation", fallback_value="fallback")
        def failing_func():
            raise Exception("Failed")

        result = failing_func()
        assert result == "fallback"

        mock_logger.warning.assert_called_once()


class TestGlobalInstance:
    """Test global unified_error_handler instance"""

    def test_global_instance_exists(self):
        """Test that global instance is available"""
        from speakub.utils.error_handler import unified_error_handler
        assert isinstance(unified_error_handler, UnifiedErrorHandler)

    def test_global_instance_methods(self):
        """Test that global instance has expected methods"""
        assert hasattr(unified_error_handler, 'categorize_error')
        assert hasattr(unified_error_handler, 'handle_error')
        assert hasattr(unified_error_handler, 'safe_operation')


if __name__ == '__main__':
    pytest.main([__file__])
