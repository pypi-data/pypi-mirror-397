"""
Tests for speakub.tts.backends.mpv_backend module
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from speakub.tts.backends.mpv_backend import MPVBackend


class TestMPVBackend:
    """Test MPVBackend class"""

    def test_initialization_with_mpv_available(self):
        """Test backend initialization when MPV is available"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                assert backend.mpv_player == mock_mpv
                assert backend._current_file is None
                assert backend._is_paused is False
                assert backend._target_volume == 1.5
                assert backend._target_speed == 1.0

                # Verify MPV was initialized with correct parameters
                mock_mpv_class.assert_called_once()
                call_kwargs = mock_mpv_class.call_args[1]
                assert call_kwargs["volume"] == 150.0  # 1.5 * 100
                assert call_kwargs["speed"] == 1.0

    def test_initialization_without_mpv(self):
        """Test backend initialization failure when MPV is not available"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', False):
            with pytest.raises(ImportError, match="python-mpv required"):
                MPVBackend()

    def test_play_success(self):
        """Test successful audio playback"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv.idle_active = True  # Simulate playback completion
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Mock temp file creation
                with patch('tempfile.mkstemp', return_value=(42, "/tmp/test.mp3")):
                    with patch('os.fdopen') as mock_fdopen:
                        mock_file = Mock()
                        mock_fdopen.return_value.__enter__ = mock_file
                        mock_fdopen.return_value.__exit__ = Mock(
                            return_value=None)

                        # Mock file cleanup
                        with patch.object(backend, '_cleanup_current_file'):
                            backend.play(b"test_audio_data",
                                         speed=1.2, volume=0.8)

                            # Verify temp file was written
                            mock_file.write.assert_called_once_with(
                                b"test_audio_data")

                            # Verify MPV settings were applied
                            assert mock_mpv.speed == 1.2
                            assert mock_mpv.volume == 80.0  # 0.8 * 100

                            # Verify playback was started
                            mock_mpv.loadfile.assert_called_once_with(
                                "/tmp/test.mp3")
                            assert mock_mpv.pause is False

    def test_play_mpv_initialization_failure(self):
        """Test playback when MPV initialization fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV', side_effect=Exception("MPV init failed")):
                backend = MPVBackend()

                with pytest.raises(Exception, match="MPV init failed"):
                    backend.play(b"test_audio_data")

    def test_play_temp_file_creation_failure(self):
        """Test playback when temp file creation fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                with patch('tempfile.mkstemp', side_effect=OSError("Temp file error")):
                    with pytest.raises(OSError, match="Temp file error"):
                        backend.play(b"test_audio_data")

    def test_pause(self):
        """Test audio pause functionality"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                backend.pause()

                assert backend._is_paused is True
                assert backend._playback_stop_event.is_set()
                assert mock_mpv.pause is True

    def test_resume(self):
        """Test audio resume functionality"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Set up paused state
                backend._is_paused = True
                backend._current_file = "/tmp/test.mp3"

                with patch('os.path.exists', return_value=True):
                    backend.resume()

                    assert backend._is_paused is False
                    assert not backend._playback_stop_event.is_set()
                    assert mock_mpv.pause is False

    def test_resume_not_paused(self):
        """Test resume when not paused"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Not paused
                backend._is_paused = False

                backend.resume()

                # Should not change pause state
                assert backend._is_paused is False
                assert mock_mpv.pause is False

    def test_stop(self):
        """Test audio stop functionality"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Set up playing state
                backend._current_file = "/tmp/test.mp3"

                with patch.object(backend, '_cleanup_current_file') as mock_cleanup:
                    backend.stop()

                    assert backend._is_paused is False
                    assert backend._playback_stop_event.is_set()
                    mock_mpv.stop.assert_called_once()
                    mock_cleanup.assert_called_once()

    def test_set_volume(self):
        """Test volume setting"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                backend.set_volume(0.8)

                assert backend._target_volume == 0.8
                assert mock_mpv.volume == 80.0

    def test_set_volume_bounds(self):
        """Test volume setting with bounds checking"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Test upper bound
                backend.set_volume(2.0)
                assert backend._target_volume == 1.5

                # Test lower bound
                backend.set_volume(-0.5)
                assert backend._target_volume == 0.0

    def test_set_volume_mpv_error(self):
        """Test volume setting when MPV operation fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                # Make volume setting fail
                mock_mpv.__setattr__ = Mock(side_effect=Exception("MPV error"))
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Should not raise exception
                backend.set_volume(0.8)
                assert backend._target_volume == 0.8

    def test_get_volume(self):
        """Test volume getting"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                backend._target_volume = 0.8

                assert backend.get_volume() == 0.8

    def test_set_speed(self):
        """Test speed setting"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                backend.set_speed(1.5)

                assert backend._target_speed == 1.5
                assert mock_mpv.speed == 1.5

    def test_set_speed_bounds(self):
        """Test speed setting with bounds checking"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Test upper bound
                backend.set_speed(4.0)
                assert backend._target_speed == 3.0

                # Test lower bound
                backend.set_speed(0.2)
                assert backend._target_speed == 0.5

    def test_set_speed_mpv_error(self):
        """Test speed setting when MPV operation fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                # Make speed setting fail
                mock_mpv.__setattr__ = Mock(side_effect=Exception("MPV error"))
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Should not raise exception
                backend.set_speed(1.5)
                assert backend._target_speed == 1.5

    def test_get_speed(self):
        """Test speed getting"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv.speed = 1.5
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                assert backend.get_speed() == 1.5

    def test_get_speed_mpv_error(self):
        """Test speed getting when MPV operation fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                # Make speed access fail
                mock_mpv.__getattr__ = Mock(side_effect=Exception("MPV error"))
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                backend._target_speed = 1.5

                # Should return cached value
                assert backend.get_speed() == 1.5

    def test_is_playing(self):
        """Test playing status check"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Test playing
                mock_mpv.idle_active = False
                backend._is_paused = False
                assert backend.is_playing() is True

                # Test idle
                mock_mpv.idle_active = True
                assert backend.is_playing() is False

                # Test paused
                mock_mpv.idle_active = False
                backend._is_paused = True
                assert backend.is_playing() is False

    def test_is_playing_mpv_error(self):
        """Test playing status check when MPV operation fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv.idle_active = Mock(side_effect=Exception("MPV error"))
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                assert backend.is_playing() is False

    def test_can_resume(self):
        """Test resume capability check"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Can resume: paused, has player, has file, file exists
                backend._is_paused = True
                backend._current_file = "/tmp/test.mp3"

                with patch('os.path.exists', return_value=True):
                    assert backend.can_resume() is True

                # Cannot resume: not paused
                backend._is_paused = False
                assert backend.can_resume() is False

                # Cannot resume: no player
                backend._is_paused = True
                backend.mpv_player = None
                assert backend.can_resume() is False

                # Cannot resume: no file
                backend.mpv_player = mock_mpv
                backend._current_file = None
                assert backend.can_resume() is False

                # Cannot resume: file doesn't exist
                backend._current_file = "/tmp/test.mp3"
                with patch('os.path.exists', return_value=False):
                    assert backend.can_resume() is False

    def test_cleanup_current_file(self):
        """Test file cleanup functionality"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Create a temp file
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name

                backend._current_file = temp_path

                # Cleanup
                backend._cleanup_current_file()

                assert backend._current_file is None
                assert not os.path.exists(temp_path)

    def test_cleanup_current_file_nonexistent(self):
        """Test file cleanup with nonexistent file"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                backend._current_file = "/nonexistent/file.mp3"

                # Should not raise exception
                backend._cleanup_current_file()

                assert backend._current_file is None

    def test_cleanup_current_file_error(self):
        """Test file cleanup when deletion fails"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                # Create a temp file and close it so we can delete it
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_path = temp_file.name

                # Delete the file manually to simulate deletion failure
                os.unlink(temp_path)

                backend._current_file = temp_path

                # Should not raise exception even if file doesn't exist
                backend._cleanup_current_file()

                assert backend._current_file is None

    def test_cleanup(self):
        """Test backend cleanup"""
        with patch('speakub.tts.backends.mpv_backend.MPV_AVAILABLE', True):
            with patch('mpv.MPV') as mock_mpv_class:
                mock_mpv = Mock()
                mock_mpv_class.return_value = mock_mpv

                backend = MPVBackend()

                with patch.object(backend, 'stop') as mock_stop:
                    backend.cleanup()

                    mock_stop.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
