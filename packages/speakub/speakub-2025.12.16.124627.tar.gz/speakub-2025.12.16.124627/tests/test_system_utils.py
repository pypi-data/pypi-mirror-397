#!/usr/bin/env python3
"""
Unit tests for system_utils.py module.
"""

import os
import subprocess
import tempfile
from unittest.mock import patch, MagicMock
import pytest
from speakub.utils.system_utils import (
    find_terminal_emulator,
    play_warning_sound,
    play_warning_sound_with_backend,
)


class TestSystemUtils:
    """Test cases for system utilities."""

    @patch("subprocess.run")
    @patch.dict(os.environ, {"TERMINAL": "xterm"})
    def test_find_terminal_emulator_with_env_var(self, mock_subprocess_run):
        """Test finding terminal emulator when TERMINAL env var is set."""
        # Mock successful 'which xterm' command
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_subprocess_run.return_value = mock_result

        result = find_terminal_emulator()

        assert result is not None
        assert result[0] == "xterm"
        assert result[1] == ["xterm", "-e"]

        # Verify subprocess.run was called with correct arguments
        mock_subprocess_run.assert_called_with(
            ["which", "xterm"], capture_output=True, timeout=1
        )

    @patch("subprocess.run")
    @patch.dict(os.environ, {"TERMINAL": "nonexistent"})
    def test_find_terminal_emulator_env_var_not_found(self, mock_subprocess_run):
        """Test finding terminal when env var points to nonexistent terminal."""
        # Mock failed 'which nonexistent' command
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess_run.return_value = mock_result

        result = find_terminal_emulator()

        # Should fall back to checking other terminals
        # This will depend on what's available in the test environment
        # We just verify it's not None and has the expected structure
        if result is not None:
            assert isinstance(result[0], str)
            assert isinstance(result[1], list)

    @patch("subprocess.run")
    def test_find_terminal_emulator_no_env_var(self, mock_subprocess_run):
        """Test finding terminal emulator when no TERMINAL env var is set."""
        # Mock subprocess.run to simulate different scenarios
        def mock_run(cmd, **kwargs):
            result = MagicMock()
            if cmd[1] == "xterm":
                result.returncode = 0  # xterm found
            else:
                result.returncode = 1  # others not found
            return result

        mock_subprocess_run.side_effect = mock_run

        result = find_terminal_emulator()

        assert result is not None
        assert result[0] == "xterm"
        assert result[1] == ["xterm", "-e"]

    @patch("subprocess.run")
    def test_find_terminal_emulator_none_found(self, mock_subprocess_run):
        """Test when no terminal emulator is found."""
        # Mock all 'which' commands to fail
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_subprocess_run.return_value = mock_result

        result = find_terminal_emulator()

        assert result is None

    @patch("subprocess.run")
    def test_find_terminal_emulator_timeout(self, mock_subprocess_run):
        """Test handling of timeout when checking for terminals."""
        from subprocess import TimeoutExpired

        mock_subprocess_run.side_effect = TimeoutExpired(["which", "xterm"], 1)

        # Should continue to next terminal or return None
        result = find_terminal_emulator()

        # Result depends on what other terminals might be available
        # We just verify it doesn't crash
        assert result is None or isinstance(result, tuple)

    @patch("shutil.which")
    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_play_warning_sound_success(self, mock_popen, mock_exists, mock_which):
        """Test successful warning sound playback."""
        mock_which.return_value = "/usr/bin/paplay"
        mock_exists.return_value = True

        play_warning_sound()

        # Verify Popen was called with correct arguments
        mock_popen.assert_called_once()
        args, kwargs = mock_popen.call_args
        assert args[0] == [
            "paplay", "/usr/share/sounds/freedesktop/stereo/phone-outgoing-busy.oga"]
        assert kwargs["stdout"] == subprocess.DEVNULL
        assert kwargs["stderr"] == subprocess.DEVNULL

    @patch("shutil.which")
    def test_play_warning_sound_no_player(self, mock_which):
        """Test warning sound when player command is not found."""
        mock_which.return_value = None

        # Should not raise an exception
        play_warning_sound()

    @patch("shutil.which")
    @patch("os.path.exists")
    def test_play_warning_sound_no_sound_file(self, mock_exists, mock_which):
        """Test warning sound when sound file doesn't exist."""
        mock_which.return_value = "/usr/bin/paplay"
        mock_exists.return_value = False

        # Should not raise an exception
        play_warning_sound()

    @patch("shutil.which")
    @patch("os.path.exists")
    @patch("subprocess.Popen")
    def test_play_warning_sound_popen_exception(self, mock_popen, mock_exists, mock_which):
        """Test warning sound when Popen raises an exception."""
        mock_which.return_value = "/usr/bin/paplay"
        mock_exists.return_value = True
        mock_popen.side_effect = Exception("Test exception")

        # Should not raise an exception (logs warning instead)
        play_warning_sound()

    @patch("os.path.exists")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("speakub.tts.backends.get_audio_backend")
    @patch("threading.Thread")
    def test_play_warning_sound_with_backend_success(self, mock_thread, mock_get_backend, mock_open, mock_exists):
        """Test successful warning sound playback with backend."""
        mock_exists.return_value = True

        # Mock file reading
        mock_file = MagicMock()
        mock_file.read.return_value = b"audio_data"
        mock_open.return_value.__enter__.return_value = mock_file

        # Mock backend
        mock_backend = MagicMock()
        mock_get_backend.return_value = mock_backend

        # Mock thread
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        play_warning_sound_with_backend()

        # Verify backend was obtained
        mock_get_backend.assert_called_once_with("pygame")

        # Verify thread was started
        mock_thread.assert_called_once()
        mock_thread_instance.start.assert_called_once()

    @patch("os.path.exists")
    def test_play_warning_sound_with_backend_no_file(self, mock_exists):
        """Test backend warning sound when file doesn't exist."""
        mock_exists.return_value = False

        # Should not raise an exception
        play_warning_sound_with_backend()

    @patch("os.path.exists")
    @patch("builtins.open")
    def test_play_warning_sound_with_backend_file_error(self, mock_open, mock_exists):
        """Test backend warning sound when file reading fails."""
        mock_exists.return_value = True
        mock_open.side_effect = Exception("File read error")

        # Should not raise an exception (falls back to play_warning_sound)
        with patch("speakub.utils.system_utils.play_warning_sound") as mock_fallback:
            play_warning_sound_with_backend()
            mock_fallback.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__])
