"""
Tests for speakub.tts.integration module
"""

import asyncio
import threading
import time
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from speakub.core.exceptions import TTSError, NetworkError, AudioSynthesisError
from speakub.tts.integration import (
    TTSIntegration,
    CircuitBreaker,
    CircuitBreakerOpenException,
    CircuitBreakerState,
)


class MockAppInterface:
    """Mock implementation of AppInterface for testing."""

    def __init__(self):
        self._tts_status = "IDLE"
        self._tts_engine = None
        self._tts_smooth_mode = False
        self._tts_volume = 100
        self._tts_rate = 0
        self._tts_pitch = "+0Hz"
        self._tts_widget = None
        self._viewport_content = None

    @property
    def tts_engine(self):
        return self._tts_engine

    @tts_engine.setter
    def tts_engine(self, value):
        self._tts_engine = value

    @property
    def tts_status(self):
        return self._tts_status

    @tts_status.setter
    def tts_status(self, value):
        self._tts_status = value

    @property
    def tts_smooth_mode(self):
        return self._tts_smooth_mode

    @property
    def tts_volume(self):
        return self._tts_volume

    @property
    def tts_rate(self):
        return self._tts_rate

    @property
    def tts_pitch(self):
        return self._tts_pitch

    @property
    def viewport_content(self):
        return self._viewport_content

    @property
    def tts_widget(self):
        return self._tts_widget

    def bell(self):
        pass

    def notify(self, message, title="", severity="information"):
        pass

    def call_from_thread(self, func, *args, **kwargs):
        func(*args, **kwargs)

    def run_worker(self, worker, *, name=None, group=None, exclusive=False, thread=False):
        pass

    def query_one(self, selector, expected_type=None):
        mock_widget = Mock()
        mock_widget.update = Mock()
        return mock_widget


class TestCircuitBreaker:
    """Test CircuitBreaker class"""

    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initialization"""
        cb = CircuitBreaker()

        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0
        assert cb.success_count == 0
        assert cb.next_attempt_time is None

    def test_circuit_breaker_success(self):
        """Test successful operation"""
        cb = CircuitBreaker()

        def success_func():
            return "success"

        result = cb.call(success_func)

        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_breaker_failure_then_success(self):
        """Test failure followed by success"""
        cb = CircuitBreaker(failure_threshold=2)

        call_count = 0

        def failing_func():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise ValueError("Test error")
            return "success"

        # First two calls should fail
        with pytest.raises(ValueError):
            cb.call(failing_func)

        with pytest.raises(ValueError):
            cb.call(failing_func)

        # Third call should succeed
        result = cb.call(failing_func)
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_trip(self):
        """Test circuit breaker tripping"""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

        def failing_func():
            raise ValueError("Test error")

        # Trip the circuit breaker
        with pytest.raises(ValueError):
            cb.call(failing_func)

        with pytest.raises(ValueError):
            cb.call(failing_func)

        # Circuit should be open
        assert cb.state == CircuitBreakerState.OPEN

        # Should raise CircuitBreakerOpenException
        with pytest.raises(CircuitBreakerOpenException):
            cb.call(lambda: "success")

        # Wait for recovery timeout
        time.sleep(1.1)

        # Should allow call again (half-open state)
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_half_open_recovery(self):
        """Test half-open state recovery"""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        # Trip circuit
        def failing_func():
            raise ValueError("Test error")
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery
        time.sleep(1.1)

        # First success should close circuit
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED

    def test_circuit_breaker_half_open_failure(self):
        """Test half-open state failure"""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        # Trip circuit
        def failing_func():
            raise ValueError("Test error")
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery
        time.sleep(1.1)

        # Failure in half-open should go back to open
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == CircuitBreakerState.OPEN

    def test_circuit_breaker_get_state(self):
        """Test getting circuit breaker state"""
        cb = CircuitBreaker()

        state = cb.get_state()

        assert "state" in state
        assert "failure_count" in state
        assert "success_count" in state
        assert state["state"] == "closed"
        assert state["failure_count"] == 0


class TestTTSIntegration:
    """Test TTSIntegration class"""

    def test_tts_integration_initialization(self):
        """Test TTS integration initialization"""
        app = MockAppInterface()

        integration = TTSIntegration(app)

        assert integration.app == app
        assert isinstance(integration.circuit_breaker, CircuitBreaker)
        assert integration.tts_lock is not None
        assert not integration.tts_stop_requested.is_set()

    def test_get_set_tts_status(self):
        """Test TTS status management"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        # Test initial status
        assert integration.get_tts_status() == "IDLE"

        # Test setting status
        old_status = integration.set_tts_status_safe("PLAYING")
        assert old_status == "IDLE"
        assert integration.get_tts_status() == "PLAYING"
        assert app.tts_status == "PLAYING"

    @patch('speakub.tts.integration.TTS_AVAILABLE', True)
    @patch('speakub.tts.integration.GTTS_AVAILABLE', False)
    @patch('speakub.tts.integration.NANMAI_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_setup_tts_edge_tts(self):
        """Test TTS setup with Edge-TTS available"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        with patch('speakub.tts.integration.EdgeTTSProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            await integration.setup_tts()

            assert app.tts_engine == mock_provider
            mock_provider_class.assert_called_once()

    @patch('speakub.tts.integration.TTS_AVAILABLE', False)
    @patch('speakub.tts.integration.GTTS_AVAILABLE', True)
    @patch('speakub.tts.integration.NANMAI_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_setup_tts_gtts_fallback(self):
        """Test TTS setup with GTTS as fallback"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        with patch('speakub.tts.integration.GTTSProvider') as mock_provider_class:
            mock_provider = Mock()
            mock_provider_class.return_value = mock_provider

            await integration.setup_tts()

            assert app.tts_engine == mock_provider
            mock_provider_class.assert_called_once()

    @patch('speakub.tts.integration.TTS_AVAILABLE', False)
    @patch('speakub.tts.integration.GTTS_AVAILABLE', False)
    @patch('speakub.tts.integration.NANMAI_AVAILABLE', False)
    @pytest.mark.asyncio
    async def test_setup_tts_no_engines(self):
        """Test TTS setup when no engines are available"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        await integration.setup_tts()

        assert app.tts_engine is None

    def test_select_tts_engine_preferred(self):
        """Test TTS engine selection with preferred engine"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        with patch('speakub.utils.config.ConfigManager') as mock_config_class:
            mock_config = Mock()
            mock_config.get.return_value = "edge-tts"
            mock_config_class.return_value = mock_config

            with patch('speakub.tts.integration.TTS_AVAILABLE', True):
                with patch('speakub.tts.integration.EdgeTTSProvider') as mock_provider:
                    mock_provider.return_value = Mock()
                    engine = integration._select_tts_engine()

                    assert engine is not None
                    mock_provider.assert_called_once()

    def test_select_tts_engine_fallback(self):
        """Test TTS engine selection fallback"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        with patch('speakub.utils.config.ConfigManager') as mock_config_class:
            mock_config = Mock()
            mock_config.get.return_value = "nonexistent"
            mock_config_class.return_value = mock_config

            with patch('speakub.tts.integration.TTS_AVAILABLE', True):
                with patch('speakub.tts.integration.EdgeTTSProvider') as mock_provider:
                    mock_provider.return_value = Mock()
                    engine = integration._select_tts_engine()

                    assert engine is not None

    def test_initialize_tts_engine_with_async_loop(self):
        """Test TTS engine initialization with async loop"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_engine = Mock()
        mock_engine.start_async_loop = Mock()

        integration._initialize_tts_engine(mock_engine)

        mock_engine.start_async_loop.assert_called_once()

    def test_initialize_tts_engine_without_async_loop(self):
        """Test TTS engine initialization without async loop"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_engine = Mock()
        # Engine doesn't have start_async_loop method

        # Should not raise exception
        integration._initialize_tts_engine(mock_engine)

    @patch('speakub.utils.text_utils.is_speakable_content')
    def test_speak_with_engine_not_speakable(self, mock_is_speakable):
        """Test speaking with non-speakable content"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_is_speakable.return_value = (False, "empty content")

        integration.speak_with_engine("")

        # Should not attempt synthesis
        mock_is_speakable.assert_called_once_with("")

    @patch('speakub.utils.text_utils.is_speakable_content')
    @patch('speakub.utils.text_utils.correct_chinese_pronunciation')
    @patch('speakub.utils.text_utils.analyze_punctuation_content')
    @patch('time.sleep')
    def test_synthesis_with_retry_speakable_content_fallback(
        self, mock_sleep, mock_analyze, mock_correct, mock_is_speakable
    ):
        """Test that speakable content failing synthesis falls back to pause instead of error"""
        app = MockAppInterface()
        config_manager = Mock()
        integration = TTSIntegration(app, config_manager)

        # Setup mocks
        mock_is_speakable.return_value = (True, "has_speakable_characters")
        mock_correct.return_value = "corrected text"
        mock_analyze.return_value = ("pause", 1.5)

        mock_engine = Mock()
        mock_engine.speak_text_sync = Mock(
            side_effect=Exception("NoAudioReceived"))
        app.tts_engine = mock_engine

        integration._prepare_tts_engine_kwargs = Mock(return_value={})
        integration._execute_tts_synthesis = Mock(
            side_effect=Exception("NoAudioReceived"))

        # Should not raise exception, but call pause
        integration._synthesis_with_retry("噓──", "has_speakable_characters")

        # Should call analyze_punctuation_content for pause
        mock_analyze.assert_called_once_with("噓──")
        # Should call time.sleep with pause duration
        mock_sleep.assert_called_once_with(1.5)

    @patch('speakub.utils.text_utils.is_speakable_content')
    def test_speak_with_engine_no_engine(self, mock_is_speakable):
        """Test speaking without TTS engine"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_is_speakable.return_value = (True, "normal content")

        integration.speak_with_engine("test text")

        # Should not attempt synthesis
        mock_is_speakable.assert_called_once_with("test text")

    @patch('speakub.utils.text_utils.is_speakable_content')
    @patch('speakub.utils.text_utils.correct_chinese_pronunciation')
    def test_speak_with_engine_success(self, mock_correct, mock_is_speakable):
        """Test successful speaking with engine"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_is_speakable.return_value = (True, "normal content")
        mock_correct.return_value = "corrected text"

        mock_engine = Mock()
        app.tts_engine = mock_engine

        integration._prepare_tts_engine_kwargs = Mock(return_value={})
        integration._execute_tts_synthesis = Mock()

        integration.speak_with_engine("test text")

        mock_correct.assert_called_once_with("test text")
        integration._prepare_tts_engine_kwargs.assert_called_once()
        integration._execute_tts_synthesis.assert_called_once_with(
            "corrected text", {})

    def test_prepare_edge_tts_params(self):
        """Test Edge-TTS parameter preparation"""
        app = MockAppInterface()
        app._tts_rate = 10
        app._tts_volume = 80
        app._tts_pitch = "+5Hz"

        integration = TTSIntegration(app)

        params = integration._prepare_edge_tts_params()

        assert params["rate"] == "+10%"
        assert params["volume"] == "-20%"
        assert params["pitch"] == "+5Hz"

    @patch('speakub.utils.config.get_config')
    def test_prepare_mpv_engine_params_gtts(self, mock_get_config):
        """Test MPV engine parameter preparation for GTTS"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        def mock_get_config_func(key, default=None):
            return {
                "gtts.volume": 0.8,
                "gtts.playback_speed": 1.2,
            }.get(key, default or 1.0)

        mock_get_config.side_effect = mock_get_config_func

        mock_engine = Mock()
        app.tts_engine = mock_engine

        params = integration._prepare_mpv_engine_params("gtts")

        assert params == {}
        mock_engine.set_speed.assert_called_once_with(1.2)
        mock_engine.set_volume.assert_called_once_with(0.8)

    @patch('speakub.utils.config.get_config')
    def test_prepare_mpv_engine_params_nanmai(self, mock_get_config):
        """Test MPV engine parameter preparation for NanmaiTTS"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_get_config.side_effect = lambda key, default=None: {
            "nanmai.volume": 0.9,
            "nanmai.playback_speed": 0.8,
        }.get(key, default or 1.0)

        mock_engine = Mock()
        app.tts_engine = mock_engine

        params = integration._prepare_mpv_engine_params("nanmai")

        assert params == {}
        mock_engine.set_speed.assert_called_once_with(0.8)
        mock_engine.set_volume.assert_called_once_with(0.9)

    def test_execute_tts_synthesis_with_sync_method(self):
        """Test TTS synthesis execution with sync method"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_engine = Mock()
        app.tts_engine = mock_engine

        integration._execute_tts_synthesis("test text", {"param": "value"})

        mock_engine.speak_text_sync.assert_called_once_with(
            "test text", param="value")

    def test_execute_tts_synthesis_without_sync_method(self):
        """Test TTS synthesis execution without sync method"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_engine = Mock()
        # Remove speak_text_sync method
        del mock_engine.speak_text_sync
        app.tts_engine = mock_engine

        # Should not raise exception
        integration._execute_tts_synthesis("test text", {})

    def test_categorize_error_network(self):
        """Test error categorization for network errors"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        result = integration._categorize_error(
            "connection timeout", "Connection timeout")

        assert result["type"] == "network"
        assert result["title"] == "網路錯誤"
        assert result["exception"] == NetworkError

    def test_categorize_error_synthesis(self):
        """Test error categorization for synthesis errors"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        result = integration._categorize_error(
            "audio synthesis failed", "Synthesis failed")

        assert result["type"] == "synthesis"
        assert result["title"] == "TTS 錯誤"
        assert result["exception"] == AudioSynthesisError

    def test_categorize_error_general(self):
        """Test error categorization for general errors"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        result = integration._categorize_error(
            "unknown error", "Unknown error")

        assert result["type"] == "general_tts"
        assert result["title"] == "TTS 錯誤"
        assert result["exception"] == TTSError

    def test_convert_tts_rate_to_mpv_speed(self):
        """Test TTS rate to MPV speed conversion"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        # Test normal rate
        assert integration._convert_tts_rate_to_mpv_speed(0) == 1.0

        # Test positive rate
        assert integration._convert_tts_rate_to_mpv_speed(30) == 1.75

        # Test negative rate
        assert integration._convert_tts_rate_to_mpv_speed(-50) == 0.5

        # Test maximum rate
        assert integration._convert_tts_rate_to_mpv_speed(100) == 3.0

    @patch('asyncio.all_tasks')
    @patch('asyncio.current_task')
    def test_cancel_pending_tasks(self, mock_current_task, mock_all_tasks):
        """Test cancelling pending asyncio tasks"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_current_task.return_value = None

        mock_task1 = Mock()
        mock_task1.done.return_value = False
        mock_task1.get_name.return_value = "task1"

        mock_task2 = Mock()
        mock_task2.done.return_value = True  # Already done

        mock_all_tasks.return_value = [mock_task1, mock_task2]

        integration.cancel_pending_tasks()

        mock_task1.cancel.assert_called_once()
        mock_task2.cancel.assert_not_called()

    def test_cleanup_orphaned_temp_files(self):
        """Test cleanup of orphaned temporary files"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        # Create some test files
        import tempfile
        import os

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create old file (simulate 48 hours ago)
            old_file = os.path.join(temp_dir, "tmp_old.mp3")
            with open(old_file, 'w') as f:
                f.write("test")

            # Set old modification time
            old_time = time.time() - (48 * 3600)  # 48 hours ago
            os.utime(old_file, (old_time, old_time))

            # Create new file
            new_file = os.path.join(temp_dir, "tmp_new.mp3")
            with open(new_file, 'w') as f:
                f.write("test")

            with patch('tempfile.gettempdir', return_value=temp_dir):
                cleaned_count = integration.cleanup_orphaned_temp_files()

                assert cleaned_count == 1
                assert not os.path.exists(old_file)
                assert os.path.exists(new_file)

    @patch('psutil.Process')
    @patch('psutil.virtual_memory')
    def test_check_memory_usage(self, mock_virtual_memory, mock_process_class):
        """Test memory usage checking"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        # Mock process memory
        mock_process = Mock()
        mock_memory_info = Mock()
        mock_memory_info.rss = 100 * 1024 * 1024  # 100MB
        mock_memory_info.vms = 200 * 1024 * 1024  # 200MB
        mock_process.memory_info.return_value = mock_memory_info
        mock_process_class.return_value = mock_process

        # Mock system memory
        mock_system_memory = Mock()
        mock_system_memory.percent = 50.0
        mock_system_memory.available = 8 * (1024**3)  # 8GB
        mock_virtual_memory.return_value = mock_system_memory

        memory_stats = integration.check_memory_usage()

        assert memory_stats["process_rss_mb"] == 100.0
        assert memory_stats["process_vms_mb"] == 200.0
        assert memory_stats["system_memory_percent"] == 50.0
        assert memory_stats["system_memory_available_gb"] == 8.0

    @patch('psutil.Process')
    def test_check_memory_usage_no_psutil(self, mock_process_class):
        """Test memory usage checking when psutil is not available"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        mock_process_class.side_effect = ImportError("psutil not available")

        memory_stats = integration.check_memory_usage()

        assert memory_stats == {}

    def test_cleanup(self):
        """Test TTS integration cleanup"""
        app = MockAppInterface()
        integration = TTSIntegration(app)

        # Mock components
        integration.playback_manager = Mock()
        integration.playback_manager.shutdown = Mock()

        app.tts_engine = Mock()
        app.tts_status = "PLAYING"

        integration.cleanup()

        integration.playback_manager.shutdown.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
