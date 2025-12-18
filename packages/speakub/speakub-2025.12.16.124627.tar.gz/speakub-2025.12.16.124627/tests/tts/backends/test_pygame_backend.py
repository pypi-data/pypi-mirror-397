"""
Tests for speakub.tts.backends.pygame_backend module
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from speakub.tts.backends.pygame_backend import PygameBackend


class TestPygameBackend:
    """Test PygameBackend class"""

    def test_initialization(self):
        """Test backend initialization"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            assert backend.player == mock_player
            assert backend._current_file is None
            mock_player_class.assert_called_once()

    def test_play_success(self):
        """Test successful audio playback"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Mock successful file loading and playback
            mock_player.load_file.return_value = True
            mock_player.play_and_wait = Mock()

            # Mock temp file creation
            with patch('tempfile.mkstemp', return_value=(42, "/tmp/test.mp3")):
                with patch('os.fdopen') as mock_fdopen:
                    mock_file = Mock()
                    mock_fdopen.return_value.__enter__ = mock_file
                    mock_fdopen.return_value.__exit__ = Mock(return_value=None)

                    backend.play(b"test_audio_data", speed=1.2, volume=0.8)

                    # Verify temp file was written
                    mock_file.write.assert_called_once_with(b"test_audio_data")

                    # Verify player methods were called
                    mock_player.load_file.assert_called_once_with(
                        "/tmp/test.mp3")
                    mock_player.set_volume.assert_called_once_with(0.8)
                    mock_player.play_and_wait.assert_called_once()

    def test_play_file_load_failure(self):
        """Test playback when file loading fails"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Mock file loading failure
            mock_player.load_file.return_value = False

            with patch('tempfile.mkstemp', return_value=(42, "/tmp/test.mp3")):
                with patch('os.fdopen') as mock_fdopen:
                    mock_file = Mock()
                    mock_fdopen.return_value.__enter__ = mock_file
                    mock_fdopen.return_value.__exit__ = Mock(return_value=None)

                    with pytest.raises(RuntimeError, match="Failed to load audio file"):
                        backend.play(b"test_audio_data")

    def test_play_temp_file_creation_failure(self):
        """Test playback when temp file creation fails"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            with patch('tempfile.mkstemp', side_effect=OSError("Temp file error")):
                with pytest.raises(RuntimeError, match="Pygame playback failed"):
                    backend.play(b"test_audio_data")

    def test_play_with_exception_during_playback(self):
        """Test playback when exception occurs during playback"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Mock successful file loading but playback failure
            mock_player.load_file.return_value = True
            mock_player.play_and_wait = Mock(
                side_effect=Exception("Playback error"))

            with patch('tempfile.mkstemp', return_value=(42, "/tmp/test.mp3")):
                with patch('os.fdopen') as mock_fdopen:
                    mock_file = Mock()
                    mock_fdopen.return_value.__enter__ = mock_file
                    mock_fdopen.return_value.__exit__ = Mock(return_value=None)

                    with pytest.raises(RuntimeError, match="Pygame playback failed"):
                        backend.play(b"test_audio_data")

    def test_pause(self):
        """Test audio pause functionality"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            backend.pause()

            mock_player.pause.assert_called_once()

    def test_resume(self):
        """Test audio resume functionality"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            backend.resume()

            mock_player.resume.assert_called_once()

    def test_stop(self):
        """Test audio stop functionality"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            backend.stop()

            mock_player.stop.assert_called_once()

    def test_set_volume(self):
        """Test volume setting"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            backend.set_volume(0.8)

            mock_player.set_volume.assert_called_once_with(0.8)

    def test_get_volume(self):
        """Test volume getting"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            mock_player.get_volume.return_value = 0.8

            assert backend.get_volume() == 0.8
            mock_player.get_volume.assert_called_once()

    def test_set_speed(self):
        """Test speed setting (should be ignored)"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Speed setting should be ignored for pygame backend
            backend.set_speed(1.5)

            # No methods should be called on the player
            mock_player.set_speed.assert_not_called()

    def test_get_speed(self):
        """Test speed getting (always returns 1.0)"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            assert backend.get_speed() == 1.0

    def test_is_playing(self):
        """Test playing status check"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Test playing
            mock_player.is_playing = True
            assert backend.is_playing() is True

            # Test not playing
            mock_player.is_playing = False
            assert backend.is_playing() is False

    def test_can_resume(self):
        """Test resume capability check"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Test can resume
            mock_player.is_paused = True
            assert backend.can_resume() is True

            # Test cannot resume
            mock_player.is_paused = False
            assert backend.can_resume() is False

    def test_cleanup(self):
        """Test backend cleanup"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            backend.cleanup()

            mock_player.cleanup.assert_called_once()

    def test_play_temp_file_cleanup_on_success(self):
        """Test that temp file is cleaned up after successful playback"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Mock successful playback
            mock_player.load_file.return_value = True
            mock_player.play_and_wait = Mock()

            temp_path = None
            with patch('tempfile.mkstemp') as mock_mkstemp:
                with patch('os.fdopen') as mock_fdopen:
                    with patch('os.unlink') as mock_unlink:
                        # Set up temp file
                        temp_path = "/tmp/test.mp3"
                        mock_mkstemp.return_value = (42, temp_path)

                        mock_file = Mock()
                        mock_fdopen.return_value.__enter__ = mock_file
                        mock_fdopen.return_value.__exit__ = Mock(
                            return_value=None)

                        backend.play(b"test_audio_data")

                        # Verify cleanup was called
                        mock_unlink.assert_called_with(temp_path)

    def test_play_temp_file_cleanup_on_failure(self):
        """Test that temp file is cleaned up after failed playback"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Mock failed playback
            mock_player.load_file.return_value = False

            temp_path = None
            with patch('tempfile.mkstemp') as mock_mkstemp:
                with patch('os.fdopen') as mock_fdopen:
                    with patch('os.unlink') as mock_unlink:
                        # Set up temp file
                        temp_path = "/tmp/test.mp3"
                        mock_mkstemp.return_value = (42, temp_path)

                        mock_file = Mock()
                        mock_fdopen.return_value.__enter__ = mock_file
                        mock_fdopen.return_value.__exit__ = Mock(
                            return_value=None)

                        with pytest.raises(RuntimeError):
                            backend.play(b"test_audio_data")

                        # Verify cleanup was called
                        mock_unlink.assert_called_with(temp_path)

    def test_play_speed_parameter_ignored(self):
        """Test that speed parameter is ignored in play method"""
        with patch('speakub.tts.backends.pygame_backend.AudioPlayer') as mock_player_class:
            mock_player = Mock()
            mock_player_class.return_value = mock_player

            backend = PygameBackend()

            # Mock successful playback
            mock_player.load_file.return_value = True
            mock_player.play_and_wait = Mock()

            with patch('tempfile.mkstemp', return_value=(42, "/tmp/test.mp3")):
                with patch('os.fdopen') as mock_fdopen:
                    mock_file = Mock()
                    mock_fdopen.return_value.__enter__ = mock_file
                    mock_fdopen.return_value.__exit__ = Mock(return_value=None)

                    # Pass speed parameter - should be ignored
                    backend.play(b"test_audio_data", speed=2.0, volume=0.5)

                    # Verify only volume was set, speed was ignored
                    mock_player.set_volume.assert_called_once_with(0.5)
                    # Speed-related methods should not be called
                    assert not hasattr(
                        mock_player, 'set_speed') or not mock_player.set_speed.called


if __name__ == '__main__':
    pytest.main([__file__])
