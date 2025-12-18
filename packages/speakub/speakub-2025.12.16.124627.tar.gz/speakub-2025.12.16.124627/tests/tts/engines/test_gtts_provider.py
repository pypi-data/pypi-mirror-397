"""
Tests for speakub.tts.gtts_provider module
"""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from speakub.core.exceptions import TTSError
from speakub.tts.engine import TTSState
from speakub.tts.engines.gtts_provider import GTTSProvider


class TestGTTSProvider:
    """Test GTTSProvider class"""

    def test_initialization_with_gtts_available(self):
        """Test provider initialization when gtts is available"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True), \
                patch('speakub.tts.backends.get_audio_backend') as mock_backend, \
                patch('speakub.tts.engines.gtts_provider.ConfigManager') as MockConfigManager:
            # Mock ConfigManager instance
            mock_config_manager = Mock()
            mock_config_manager.get.side_effect = lambda key, default=None: {
                "gtts.default_voice": "gtts-zh-TW",
                "gtts.volume": 1.0,
                "gtts.playback_speed": 1.5
            }.get(key, default)
            MockConfigManager.return_value = mock_config_manager

            # Mock audio backend
            mock_backend.return_value = Mock()

            provider = GTTSProvider()

            assert provider._current_voice == "gtts-zh-TW"
            assert provider._current_volume == 1.0
            assert provider._current_speed == 1.5
            assert provider._audio_state == TTSState.IDLE
            assert provider._is_paused is False
            assert provider._current_audio_file is None

    def test_initialization_without_gtts(self):
        """Test provider initialization failure when gtts is not available"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', False):
            with pytest.raises(ImportError, match="gtts not installed"):
                GTTSProvider()

    def test_state_transition_valid(self):
        """Test valid state transitions"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # IDLE -> LOADING
            assert provider._transition_state(TTSState.LOADING) is True
            assert provider._audio_state == TTSState.LOADING

            # LOADING -> PLAYING
            assert provider._transition_state(TTSState.PLAYING) is True
            assert provider._audio_state == TTSState.PLAYING

            # PLAYING -> PAUSED
            assert provider._transition_state(TTSState.PAUSED) is True
            assert provider._audio_state == TTSState.PAUSED

            # PAUSED -> STOPPED
            assert provider._transition_state(TTSState.STOPPED) is True
            assert provider._audio_state == TTSState.STOPPED

    def test_state_transition_invalid(self):
        """Test invalid state transitions"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # IDLE -> PLAYING (invalid)
            assert provider._transition_state(TTSState.PLAYING) is False
            assert provider._audio_state == TTSState.IDLE

    def test_get_current_state(self):
        """Test getting current state"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # GTTSProvider doesn't have get_current_state method, check _audio_state directly
            assert provider._audio_state == TTSState.IDLE

            provider._audio_state = TTSState.PLAYING
            assert provider._audio_state == TTSState.PLAYING

    @patch('speakub.utils.security.TextSanitizer.validate_tts_text')
    @patch('speakub.utils.security.TextSanitizer.sanitize_tts_text')
    @pytest.mark.asyncio
    async def test_synthesize_success(self, mock_sanitize, mock_validate):
        """Test successful text synthesis"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            mock_sanitize.return_value = "sanitized text"
            mock_validate.return_value = None

            # Mock gTTS
            mock_tts = Mock()
            mock_tts.save = Mock()

            with patch('gtts.gTTS', return_value=mock_tts), \
                    patch('speakub.utils.file_utils.get_resource_manager') as mock_get_manager:

                # Mock resource manager
                mock_manager = Mock()
                mock_manager.managed_temp_file.return_value.__enter__ = Mock(
                    return_value="/tmp/test.mp3")
                mock_manager.managed_temp_file.return_value.__exit__ = Mock(
                    return_value=None)
                mock_get_manager.return_value = mock_manager

                # Mock file reading
                with patch('builtins.open', create=True) as mock_open:
                    mock_file = Mock()
                    mock_file.read.return_value = b"audio_data"
                    mock_open.return_value.__enter__ = mock_file
                    mock_open.return_value.__exit__ = Mock(return_value=None)

                    result = await provider.synthesize("test text", "gtts-zh-TW")

                    assert result == b"audio_data"
                    mock_validate.assert_called_once_with("test text")
                    mock_sanitize.assert_called_once_with("test text")
                    mock_tts.save.assert_called_once_with("/tmp/test.mp3")

    @pytest.mark.asyncio
    async def test_synthesize_empty_text(self):
        """Test synthesis with empty text"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            result = await provider.synthesize("", "gtts-zh-TW")

            assert result == b""

    @pytest.mark.asyncio
    async def test_synthesize_validation_failure(self):
        """Test synthesis with validation failure"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            with patch('speakub.utils.security.TextSanitizer.validate_tts_text',
                       side_effect=ValueError("Invalid text")):
                with pytest.raises(ValueError, match="Invalid text"):
                    await provider.synthesize("invalid text", "gtts-zh-TW")

    @pytest.mark.asyncio
    async def test_synthesize_gtts_unavailable(self):
        """Test synthesis when gtts is not available"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', False):
            provider = GTTSProvider()

            with pytest.raises(RuntimeError, match="gTTS not available"):
                await provider.synthesize("test text", "gtts-zh-TW")

    @pytest.mark.asyncio
    async def test_synthesize_timeout(self):
        """Test synthesis timeout handling"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock gTTS to take longer than timeout
            def slow_gtts(*args, **kwargs):
                import time
                time.sleep(35)  # Longer than 30s timeout
                return Mock()

            with patch('gtts.gTTS', side_effect=slow_gtts):
                with pytest.raises(RuntimeError, match="timed out"):
                    await provider.synthesize("test text", "gtts-zh-TW")

    @pytest.mark.asyncio
    async def test_get_available_voices(self):
        """Test voice list retrieval"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            voices = await provider.get_available_voices()

            assert len(voices) == 3
            assert voices[0]["short_name"] == "gtts-zh-CN"
            assert voices[1]["short_name"] == "gtts-zh-TW"
            assert voices[2]["short_name"] == "gtts-zh"

    def test_get_voices_by_language(self):
        """Test filtering voices by language"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            zh_voices = provider.get_voices_by_language("zh")
            assert len(zh_voices) == 3

            en_voices = provider.get_voices_by_language("en")
            assert len(en_voices) == 0

    def test_set_voice_valid(self):
        """Test setting valid voice"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            assert provider.set_voice("gtts-zh-TW") is True
            assert provider.get_current_voice() == "gtts-zh-TW"

            assert provider.set_voice("gtts-zh-CN") is True
            assert provider.get_current_voice() == "gtts-zh-CN"

    def test_set_voice_invalid(self):
        """Test setting invalid voice"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            assert provider.set_voice("invalid-voice") is False
            assert provider.set_voice("") is False
            assert provider.set_voice("not-gtts") is False

    def test_get_current_voice(self):
        """Test getting current voice"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            assert provider.get_current_voice() == "gtts-zh-TW"

    @pytest.mark.asyncio
    async def test_play_audio_non_blocking(self):
        """Test non-blocking audio playback"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock play_audio
            provider.play_audio = AsyncMock()

            await provider.play_audio_non_blocking(b"test_audio")

            provider.play_audio.assert_called_once_with(b"test_audio")

    @pytest.mark.asyncio
    async def test_wait_for_playback_completion(self):
        """Test waiting for playback completion"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Should not raise any exception
            await provider.wait_for_playback_completion()

    @pytest.mark.asyncio
    async def test_play_audio_success(self):
        """Test successful audio playback"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend
            provider.audio_backend.play = Mock()

            await provider.play_audio(b"test_audio_data")

            provider.audio_backend.play.assert_called_once()
            call_args = provider.audio_backend.play.call_args
            assert call_args[0][0] == b"test_audio_data"
            assert "speed" in call_args[1]
            assert "volume" in call_args[1]

    @pytest.mark.asyncio
    async def test_play_audio_failure(self):
        """Test audio playback failure"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend to raise exception
            provider.audio_backend.play = Mock(
                side_effect=Exception("Playback failed"))

            with pytest.raises(Exception, match="Playback failed"):
                await provider.play_audio(b"test_audio_data")

    def test_pause(self):
        """Test audio pause functionality"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Set up playing state
            provider._audio_state = TTSState.PLAYING
            provider.audio_backend.pause = Mock()

            provider.pause()

            assert provider._audio_state == TTSState.PAUSED
            assert provider._is_paused is True
            provider.audio_backend.pause.assert_called_once()

    def test_resume(self):
        """Test audio resume functionality"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Set up paused state
            provider._audio_state = TTSState.PAUSED
            provider._is_paused = True
            provider.audio_backend.resume = Mock()

            provider.resume()

            assert provider._audio_state == TTSState.PLAYING
            assert provider._is_paused is False
            provider.audio_backend.resume.assert_called_once()

    def test_stop(self):
        """Test audio stop functionality"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Set up playing state
            provider._audio_state = TTSState.PLAYING
            provider.audio_backend.stop = Mock()

            # Create a temp file to test cleanup
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                provider._current_audio_file = temp_file.name  # type: ignore

            provider.stop()

            assert provider._audio_state == TTSState.STOPPED
            assert provider._is_paused is False
            assert provider._current_audio_file is None
            provider.audio_backend.stop.assert_called_once()

            # File should be cleaned up
            assert not os.path.exists(temp_file.name)

    def test_can_resume(self):
        """Test resume capability check"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend
            provider.audio_backend.can_resume = Mock(return_value=True)

            assert provider.can_resume() is True

            provider.audio_backend.can_resume = Mock(return_value=False)
            assert provider.can_resume() is False

    def test_can_resume_backend_error(self):
        """Test resume capability check with backend error"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend to raise exception
            provider.audio_backend.can_resume = Mock(
                side_effect=Exception("Backend error"))

            assert provider.can_resume() is False

    def test_seek(self):
        """Test seek functionality (not supported)"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Should not raise exception, just log warning
            provider.seek(1000)

    def test_set_volume(self):
        """Test volume setting"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True), \
                patch('speakub.tts.engines.gtts_provider.ConfigManager') as MockConfigManager:
            # Mock ConfigManager
            mock_config_manager = Mock()
            mock_config_manager.get.side_effect = lambda key, default=None: {
                "gtts.volume_min": 0.0,
                "gtts.volume_max": 1.5
            }.get(key, default)
            MockConfigManager.return_value = mock_config_manager

            provider = GTTSProvider()

            provider.set_volume(0.8)

            assert provider.get_volume() == 0.8
            mock_config_manager.set.assert_called_with("gtts.volume", 0.8)

    def test_get_volume(self):
        """Test volume getting"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend
            provider.audio_backend.get_volume = Mock(return_value=0.8)

            assert provider.get_volume() == 0.8

    def test_get_volume_backend_error(self):
        """Test volume getting with backend error"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend to raise exception
            provider.audio_backend.get_volume = Mock(
                side_effect=Exception("Backend error"))

            # Should return cached value
            assert provider.get_volume() == 1.0

    def test_set_speed(self):
        """Test speed setting"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True), \
                patch('speakub.tts.engines.gtts_provider.ConfigManager') as MockConfigManager:
            # Mock ConfigManager
            mock_config_manager = Mock()
            mock_config_manager.get.side_effect = lambda key, default=None: {
                "gtts.speed_min": 0.5,
                "gtts.speed_max": 3.0
            }.get(key, default)
            MockConfigManager.return_value = mock_config_manager

            provider = GTTSProvider()

            provider.set_speed(1.8)

            assert provider.get_speed() == 1.8
            mock_config_manager.set.assert_called_with(
                "gtts.playback_speed", 1.8)

    def test_get_speed(self):
        """Test speed getting"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend
            provider.audio_backend.get_speed = Mock(return_value=1.8)

            assert provider.get_speed() == 1.8

    def test_get_speed_backend_error(self):
        """Test speed getting with backend error"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock audio backend to raise exception
            provider.audio_backend.get_speed = Mock(
                side_effect=Exception("Backend error"))

            # Should return cached value
            assert provider.get_speed() == 1.5

    def test_speak_text_sync_success(self):
        """Test synchronous text speaking success"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock the async method
            provider._speak_text_async = AsyncMock()

            provider.speak_text_sync("Hello world")

            provider._speak_text_async.assert_called_once_with("Hello world")

    def test_speak_text_sync_error(self):
        """Test synchronous text speaking error"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock the async method to raise exception
            provider._speak_text_async = AsyncMock(
                side_effect=Exception("Synthesis failed"))

            with pytest.raises(Exception, match="Synthesis failed"):
                provider.speak_text_sync("Hello world")

    @pytest.mark.asyncio
    async def test_speak_text_async(self):
        """Test async text speaking"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Mock synthesize and play_audio
            provider.synthesize = AsyncMock(return_value=b"audio_data")
            provider.play_audio = AsyncMock()

            await provider._speak_text_async("Hello world")

            provider.synthesize.assert_called_once()
            provider.play_audio.assert_called_once_with(b"audio_data")

    def test_cleanup_current_file(self):
        """Test file cleanup functionality"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            # Create a temp file
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(b"test")
                temp_path = temp_file.name

            provider._current_audio_file = temp_path

            # Cleanup
            provider._cleanup_current_file()

            assert provider._current_audio_file is None
            assert not os.path.exists(temp_path)

    def test_cleanup_current_file_nonexistent(self):
        """Test file cleanup with nonexistent file"""
        with patch('speakub.tts.engines.gtts_provider.GTTS_AVAILABLE', True):
            provider = GTTSProvider()

            provider._current_audio_file = "/nonexistent/file.mp3"

            # Should not raise exception
            provider._cleanup_current_file()

            assert provider._current_audio_file is None


if __name__ == '__main__':
    pytest.main([__file__])
