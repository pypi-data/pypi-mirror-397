"""
Tests for speakub.tts.edge_tts_provider module
"""

import asyncio
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from speakub.core.exceptions import TTSError
from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider, cleanup_orphaned_tts_files
from speakub.tts.engine import TTSState


class TestEdgeTTSProvider:
    """Test EdgeTTSProvider class"""

    def test_initialization_with_edge_tts_available(self):
        """Test provider initialization when edge-tts is available"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            # Mock config to return default values
            with patch('speakub.utils.config.ConfigManager') as mock_config_class:
                mock_config = mock_config_class.return_value
                mock_config.get.side_effect = lambda key, default=None: {
                    "edge-tts.voice": "zh-TW-HsiaoChenNeural",
                    "edge-tts.volume": 1.0,
                    "edge-tts.playback_speed": 1.0,
                    "edge-tts.pitch": "+0Hz"
                }.get(key, default)

                provider = EdgeTTSProvider(config_manager=mock_config)

                assert provider._current_voice == "zh-TW-HsiaoChenNeural"
                assert provider._tts_volume == 1.0
                assert provider._tts_speed == 1.0
                assert provider._tts_pitch == "+0Hz"
                assert provider.get_current_state() == "idle"
                assert provider._voices_cache is None

    def test_initialization_without_edge_tts(self):
        """Test provider initialization failure when edge-tts is not available"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', False):
            with pytest.raises(ImportError, match="edge-tts package not installed"):
                EdgeTTSProvider()

    def test_state_transition_valid(self):
        """Test valid state transitions"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

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
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # IDLE -> PLAYING (invalid)
            assert provider._transition_state(TTSState.PLAYING) is False
            assert provider._audio_state == TTSState.IDLE

    def test_get_current_state(self):
        """Test getting current state"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            assert provider.get_current_state() == "idle"

            provider._audio_state = TTSState.PLAYING
            assert provider.get_current_state() == "playing"

    @patch('speakub.utils.security.TextSanitizer.validate_tts_text')
    @patch('speakub.utils.security.TextSanitizer.sanitize_tts_text')
    @pytest.mark.asyncio
    async def test_synthesize_success(self, mock_sanitize, mock_validate):
        """Test successful text synthesis"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            mock_sanitize.return_value = "sanitized text"
            mock_validate.return_value = None

            # Mock edge_tts.Communicate
            mock_communicate = Mock()
            mock_chunk = {"type": "audio", "data": b"audio_data"}
            mock_communicate.stream.return_value = [mock_chunk]

            with patch('edge_tts.Communicate', return_value=mock_communicate):
                result = await provider.synthesize("test text", "en-US-AriaNeural")

                assert result == b"audio_data"
                mock_validate.assert_called_once_with("test text")
                mock_sanitize.assert_called_once_with("test text")

    @pytest.mark.asyncio
    async def test_synthesize_empty_text(self):
        """Test synthesis with empty text"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            result = await provider.synthesize("", "en-US-AriaNeural")

            assert result == b""

    @pytest.mark.asyncio
    async def test_synthesize_validation_failure(self):
        """Test synthesis with validation failure"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            with patch('speakub.utils.security.TextSanitizer.validate_tts_text',
                       side_effect=ValueError("Invalid text")):
                with pytest.raises(ValueError, match="Invalid text"):
                    await provider.synthesize("invalid text", "en-US-AriaNeural")

    @pytest.mark.asyncio
    async def test_synthesize_edge_tts_unavailable(self):
        """Test synthesis when edge-tts is not available"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', False):
            provider = EdgeTTSProvider()

            with pytest.raises(RuntimeError, match="Edge TTS not available"):
                await provider.synthesize("test text", "en-US-AriaNeural")

    @pytest.mark.asyncio
    async def test_get_available_voices_success(self):
        """Test successful voice list retrieval"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            mock_voice = {
                "Name": "Test Voice",
                "ShortName": "en-US-TestNeural",
                "Gender": "Female",
                "Locale": "en-US",
                "DisplayName": "Test Voice",
                "LocalName": "Test",
                "StyleList": ["style1"],
                "SampleRateHertz": 24000,
                "VoiceType": "Neural"
            }

            with patch('edge_tts.list_voices', return_value=[mock_voice]):
                voices = await provider.get_available_voices()

                assert len(voices) == 1
                assert voices[0]["name"] == "Test Voice"
                assert voices[0]["short_name"] == "en-US-TestNeural"
                assert voices[0]["gender"] == "Female"
                assert voices[0]["locale"] == "en-US"

                # Test caching
                voices2 = await provider.get_available_voices()
                assert voices2 == voices

    @pytest.mark.asyncio
    async def test_get_available_voices_failure(self):
        """Test voice list retrieval failure"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            with patch('edge_tts.list_voices', side_effect=Exception("API error")):
                voices = await provider.get_available_voices()

                assert voices == []

    @pytest.mark.asyncio
    async def test_get_available_voices_unavailable(self):
        """Test voice list when edge-tts is not available"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', False):
            provider = EdgeTTSProvider()

            voices = await provider.get_available_voices()

            assert voices == []

    def test_get_voices_by_language(self):
        """Test filtering voices by language"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Set up mock voices cache
            provider._voices_cache = [
                {"name": "English Voice", "locale": "en-US"},
                {"name": "Chinese Voice", "locale": "zh-CN"},
                {"name": "Japanese Voice", "locale": "ja-JP"},
            ]

            en_voices = provider.get_voices_by_language("en")
            assert len(en_voices) == 1
            assert en_voices[0]["locale"] == "en-US"

            zh_voices = provider.get_voices_by_language("zh")
            assert len(zh_voices) == 1
            assert zh_voices[0]["locale"] == "zh-CN"

    def test_get_voices_by_language_no_cache(self):
        """Test filtering voices when cache is not available"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # No cache
            voices = provider.get_voices_by_language("en")
            assert voices == []

    def test_set_voice_valid(self):
        """Test setting valid voice"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Test default voice
            assert provider.set_voice("zh-TW-HsiaoChenNeural") is True
            assert provider.get_current_voice() == "zh-TW-HsiaoChenNeural"

            # Test valid voice format
            assert provider.set_voice("en-US-AriaNeural") is True
            assert provider.get_current_voice() == "en-US-AriaNeural"

    def test_set_voice_invalid(self):
        """Test setting invalid voice"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Test invalid voice
            assert provider.set_voice("invalid-voice") is False
            assert provider.set_voice("") is False
            assert provider.set_voice("invalid") is False

    def test_get_current_voice(self):
        """Test getting current voice"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            assert provider.get_current_voice() == "zh-TW-HsiaoChenNeural"

    @patch('speakub.utils.file_utils.get_resource_manager')
    @patch('speakub.utils.file_utils.register_temp_file')
    @pytest.mark.asyncio
    async def test_play_audio_non_blocking_new_file(self, mock_register, mock_get_manager):
        """Test non-blocking audio playback with new file"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Mock resource manager
            mock_manager = Mock()
            mock_manager.managed_temp_file.return_value.__enter__ = Mock(
                return_value="/tmp/test.mp3")
            mock_manager.managed_temp_file.return_value.__exit__ = Mock(
                return_value=None)
            mock_get_manager.return_value = mock_manager

            # Mock audio player
            provider.audio_player.load_file = Mock()
            provider.audio_player.play = Mock()

            await provider.play_audio_non_blocking(b"test_audio_data")

            # Verify temp file was created and registered
            mock_register.assert_called_once_with("/tmp/test.mp3")
            provider.audio_player.load_file.assert_called_once_with(
                "/tmp/test.mp3")

    @pytest.mark.asyncio
    async def test_play_audio_non_blocking_reuse_file(self):
        """Test non-blocking audio playback reusing existing file"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Set up existing file
            provider._current_audio_file = "/tmp/existing.mp3"
            provider._is_paused = False

            # Mock audio player
            provider.audio_player.load_file = Mock()
            provider.audio_player.play = Mock()

            await provider.play_audio_non_blocking(b"test_audio_data")

            # Should not create new file
            provider.audio_player.load_file.assert_not_called()

    @pytest.mark.asyncio
    async def test_wait_for_playback_completion(self):
        """Test waiting for playback completion"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Mock audio player
            provider.audio_player.wait_for_completion = AsyncMock()

            await provider.wait_for_playback_completion()

            provider.audio_player.wait_for_completion.assert_called_once()

    @pytest.mark.asyncio
    async def test_play_audio_backward_compatibility(self):
        """Test backward compatible play_audio method"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Mock the split methods
            provider.play_audio_non_blocking = AsyncMock()
            provider.wait_for_playback_completion = AsyncMock()

            await provider.play_audio(b"test_audio")

            provider.play_audio_non_blocking.assert_called_once_with(
                b"test_audio")
            provider.wait_for_playback_completion.assert_called_once()

    def test_pause(self):
        """Test audio pause functionality"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Set up playing state
            provider._audio_state = TTSState.PLAYING
            provider.audio_player.pause = Mock()

            provider.pause()

            assert provider._audio_state == TTSState.PAUSED
            assert provider._is_paused is True
            provider.audio_player.pause.assert_called_once()

    def test_can_resume(self):
        """Test resume capability check"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Not paused
            assert provider.can_resume() is False

            # Paused but no player - don't modify audio_player directly
            provider._is_paused = True
            original_player = provider.audio_player
            provider.audio_player = None
            try:
                assert provider.can_resume() is False
            finally:
                provider.audio_player = original_player

            # Paused with player but not busy
            provider.audio_player = Mock()
            provider.audio_player.is_busy.return_value = False
            assert provider.can_resume() is False

            # Paused with busy player
            provider.audio_player.is_busy.return_value = True
            assert provider.can_resume() is True

    def test_resume(self):
        """Test audio resume functionality"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Set up paused state
            provider._audio_state = TTSState.PAUSED
            provider._is_paused = True
            provider.audio_player = Mock()
            provider.audio_player.is_busy.return_value = True
            provider.audio_player.resume = Mock()

            provider.resume()

            assert provider._audio_state == TTSState.PLAYING
            provider.audio_player.resume.assert_called_once()

    def test_stop(self):
        """Test audio stop functionality"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Set up playing state
            provider._audio_state = TTSState.PLAYING
            provider.audio_player.stop = Mock()

            # Create a temp file to test cleanup
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                provider._current_audio_file = temp_file.name

            provider.stop()

            assert provider._audio_state == TTSState.STOPPED
            assert provider._is_paused is False
            assert provider._current_audio_file is None
            provider.audio_player.stop.assert_called_once()

            # File should be cleaned up
            assert not os.path.exists(temp_file.name)

    def test_seek(self):
        """Test audio seek functionality"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            provider.audio_player.seek = Mock()

            provider.seek(1000)

            provider.audio_player.seek.assert_called_once_with(1000)

    @patch('speakub.utils.config.get_config')
    @patch('speakub.utils.config.save_config')
    def test_set_volume(self, mock_save_config, mock_get_config):
        """Test volume setting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            mock_get_config.return_value = 1.0  # volume_max

            provider.set_volume(0.8)

            assert provider.get_volume() == 0.8
            mock_save_config.assert_called()

    def test_get_volume(self):
        """Test volume getting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            assert provider.get_volume() == 1.0

    @patch('speakub.utils.config.get_config')
    @patch('speakub.utils.config.save_config')
    def test_set_speed(self, mock_save_config, mock_get_config):
        """Test speed setting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            mock_get_config.return_value = 2.0  # speed_max

            provider.set_speed(1.5)

            assert provider.get_speed() == 1.5
            mock_save_config.assert_called()

    def test_get_speed(self):
        """Test speed getting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            assert provider.get_speed() == 1.0

    @patch('speakub.utils.config.get_config')
    @patch('speakub.utils.config.save_config')
    def test_set_pitch_valid(self, mock_save_config, mock_get_config):
        """Test valid pitch setting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            mock_get_config.return_value = 50  # pitch_max

            provider.set_pitch("+10Hz")

            assert provider.get_pitch() == "+10Hz"
            mock_save_config.assert_called()

    def test_set_pitch_invalid(self):
        """Test invalid pitch setting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            # Invalid format
            provider.set_pitch("invalid")
            assert provider.get_pitch() == "+0Hz"  # Should remain unchanged

            # Out of range
            provider.set_pitch("+100Hz")
            assert provider.get_pitch() == "+0Hz"  # Should remain unchanged

    def test_get_pitch(self):
        """Test pitch getting"""
        with patch('speakub.tts.engines.edge_tts_provider.EDGE_TTS_AVAILABLE', True):
            provider = EdgeTTSProvider()

            assert provider.get_pitch() == "+0Hz"

    def test_cleanup_orphaned_tts_files(self):
        """Test cleanup of orphaned TTS files"""
        # Create some test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create old file (simulate 48 hours ago)
            old_file = os.path.join(temp_dir, "tmp_old.mp3")
            with open(old_file, 'w') as f:
                f.write("test")

            # Set old modification time
            import time
            old_time = time.time() - (48 * 3600)  # 48 hours ago
            os.utime(old_file, (old_time, old_time))

            # Create new file
            new_file = os.path.join(temp_dir, "tmp_new.mp3")
            with open(new_file, 'w') as f:
                f.write("test")

            with patch('tempfile.gettempdir', return_value=temp_dir):
                cleaned_count = cleanup_orphaned_tts_files(max_age_hours=24)

                assert cleaned_count == 1
                assert not os.path.exists(old_file)
                assert os.path.exists(new_file)

    def test_cleanup_orphaned_tts_files_error(self):
        """Test cleanup error handling"""
        with patch('tempfile.gettempdir', side_effect=Exception("Permission denied")):
            cleaned_count = cleanup_orphaned_tts_files()

            assert cleaned_count == 0


if __name__ == '__main__':
    pytest.main([__file__])
