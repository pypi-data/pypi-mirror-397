"""
Tests for speakub.desktop module
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from speakub.desktop import check_desktop_installed, install_desktop_entry


class TestInstallDesktopEntry:
    """Test install_desktop_entry function"""

    @patch('speakub.desktop.find_terminal_emulator')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.chmod')
    def test_successful_installation_xterm(self, mock_chmod, mock_write_text, mock_mkdir, mock_find_terminal):
        """Test successful desktop entry installation with xterm"""
        mock_find_terminal.return_value = ('xterm', ['xterm'])

        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')
            result = install_desktop_entry()

            assert result is True
            mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
            mock_write_text.assert_called_once()
            mock_chmod.assert_called_once_with(0o755)

            # Check the content written
            call_args = mock_write_text.call_args[0][0]
            assert 'Exec=xterm -e speakub %f' in call_args
            assert 'Terminal=false' in call_args

    @patch('speakub.desktop.find_terminal_emulator')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.chmod')
    def test_successful_installation_gnome_terminal(self, mock_chmod, mock_write_text, mock_mkdir, mock_find_terminal):
        """Test successful desktop entry installation with gnome-terminal"""
        mock_find_terminal.return_value = (
            'gnome-terminal', ['gnome-terminal'])

        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')
            result = install_desktop_entry()

            assert result is True
            call_args = mock_write_text.call_args[0][0]
            assert 'Exec=gnome-terminal -- speakub %f' in call_args

    @patch('speakub.desktop.find_terminal_emulator')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.chmod')
    def test_successful_installation_alacritty(self, mock_chmod, mock_write_text, mock_mkdir, mock_find_terminal):
        """Test successful desktop entry installation with alacritty"""
        mock_find_terminal.return_value = ('alacritty', ['alacritty'])

        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/tmp/test_home')
            result = install_desktop_entry()

            assert result is True
            call_args = mock_write_text.call_args[0][0]
            assert 'Exec=alacritty -e speakub %f' in call_args

    @patch('speakub.desktop.find_terminal_emulator', return_value=None)
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.chmod')
    def test_fallback_to_alacritty(self, mock_chmod, mock_write_text, mock_mkdir, mock_find_terminal):
        """Test fallback to alacritty when no terminal is found"""
        with patch('pathlib.Path.home') as mock_home, \
                patch('sys.stderr'):
            mock_home.return_value = Path('/tmp/test_home')
            result = install_desktop_entry()

            assert result is True
            call_args = mock_write_text.call_args[0][0]
            assert 'Exec=alacritty -e speakub %f' in call_args

    @patch('speakub.desktop.find_terminal_emulator')
    @patch('pathlib.Path.mkdir', side_effect=Exception('Permission denied'))
    def test_installation_failure(self, mock_mkdir, mock_find_terminal):
        """Test handling of installation failure"""
        mock_find_terminal.return_value = ('xterm', ['xterm'])

        with patch('pathlib.Path.home') as mock_home, \
                patch('sys.stderr'):
            mock_home.return_value = Path('/tmp/test_home')
            result = install_desktop_entry()

            assert result is False

    def test_desktop_file_content(self):
        """Test the content of the generated desktop file"""
        with patch('speakub.desktop.find_terminal_emulator') as mock_find_terminal, \
                patch('pathlib.Path.mkdir'), \
                patch('pathlib.Path.chmod'), \
                patch('pathlib.Path.home') as mock_home:

            mock_find_terminal.return_value = ('xterm', ['xterm'])
            mock_home.return_value = Path('/tmp/test_home')

            # Capture the content written to the file
            written_content = None

            def capture_write_text(content):
                nonlocal written_content
                written_content = content

            with patch('pathlib.Path.write_text', side_effect=capture_write_text):
                install_desktop_entry()

            # Verify the desktop file content
            assert written_content is not None
            assert '[Desktop Entry]' in written_content
            assert 'Type=Application' in written_content
            assert 'Name=SpeakUB' in written_content
            assert 'Comment=EPUB Reader with TTS' in written_content
            assert 'Terminal=false' in written_content
            assert 'Categories=Office;Education;' in written_content
            assert 'MimeType=application/epub+zip;' in written_content
            assert 'Icon=book' in written_content


class TestCheckDesktopInstalled:
    """Test check_desktop_installed function"""

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.home')
    def test_desktop_entry_exists(self, mock_home, mock_exists):
        """Test when desktop entry exists"""
        mock_home.return_value = Path('/tmp/test_home')
        mock_exists.return_value = True

        result = check_desktop_installed()
        assert result is True

        # Verify the correct path was checked
        expected_path = Path(
            '/tmp/test_home/.local/share/applications/speakub.desktop')
        mock_exists.assert_called_once_with()

    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.home')
    def test_desktop_entry_not_exists(self, mock_home, mock_exists):
        """Test when desktop entry does not exist"""
        mock_home.return_value = Path('/tmp/test_home')
        mock_exists.return_value = False

        result = check_desktop_installed()
        assert result is False

        mock_exists.assert_called_once_with()


if __name__ == '__main__':
    pytest.main([__file__])
