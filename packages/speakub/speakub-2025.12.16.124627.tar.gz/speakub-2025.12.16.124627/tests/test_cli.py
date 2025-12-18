"""
Tests for speakub.cli module
"""

import argparse
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from speakub.cli import is_running_in_terminal, main, relaunch_in_terminal


class TestIsRunningInTerminal:
    """Test is_running_in_terminal function"""

    def test_running_in_real_terminal(self):
        """Test detection of real terminal"""
        with patch('sys.stdout.isatty', return_value=True), \
                patch('sys.stderr.isatty', return_value=True), \
                patch.dict(os.environ, {'TERM': 'xterm-256color'}):
            assert is_running_in_terminal() is True

    def test_not_running_in_terminal(self):
        """Test detection when not in terminal"""
        with patch('sys.stdout.isatty', return_value=False), \
                patch('sys.stderr.isatty', return_value=False), \
                patch.dict(os.environ, {'TERM': 'dumb'}):
            assert is_running_in_terminal() is False

    def test_xterm_256color_detection(self):
        """Test xterm-256color TERM detection"""
        with patch('sys.stdout.isatty', return_value=False), \
                patch('sys.stderr.isatty', return_value=False), \
                patch.dict(os.environ, {'TERM': 'xterm-256color'}):
            assert is_running_in_terminal() is True

    def test_common_terminal_types(self):
        """Test detection of common terminal types"""
        terminal_types = ['xterm', 'screen', 'tmux', 'linux',
                          'alacritty', 'rxvt', 'konsole', 'gnome', 'xfce']

        for term_type in terminal_types:
            with patch('sys.stdout.isatty', return_value=False), \
                    patch('sys.stderr.isatty', return_value=False), \
                    patch.dict(os.environ, {'TERM': term_type}):
                assert is_running_in_terminal(
                ) is True, f"Failed for TERM={term_type}"

    def test_debug_output(self, capsys):
        """Test debug output functionality"""
        with patch('sys.stdout.isatty', return_value=True), \
                patch('sys.stderr.isatty', return_value=True), \
                patch.dict(os.environ, {'TERM': 'xterm'}):
            is_running_in_terminal(debug=True)
            captured = capsys.readouterr()
            assert 'DEBUG:' in captured.err


class TestRelaunchInTerminal:
    """Test relaunch_in_terminal function"""

    @patch('speakub.utils.system_utils.find_terminal_emulator')
    @patch('subprocess.Popen')
    def test_successful_relaunch(self, mock_popen, mock_find_terminal):
        """Test successful relaunch in terminal"""
        mock_find_terminal.return_value = ('xterm', ['xterm'])
        mock_popen.return_value = Mock()

        with patch('sys.exit') as mock_exit:
            relaunch_in_terminal(['test.epub'])
            mock_popen.assert_called_once()
            mock_exit.assert_called_once_with(0)

    @patch('speakub.utils.system_utils.find_terminal_emulator', return_value=None)
    @patch('subprocess.run')
    def test_no_terminal_found(self, mock_run, mock_find_terminal):
        """Test behavior when no terminal emulator is found"""
        mock_run.return_value = Mock()

        with pytest.raises(SystemExit) as exc_info:
            relaunch_in_terminal(['test.epub'])

        assert exc_info.value.code == 1

    @patch('speakub.utils.system_utils.find_terminal_emulator')
    @patch('subprocess.Popen', side_effect=Exception('Launch failed'))
    def test_launch_failure(self, mock_popen, mock_find_terminal):
        """Test handling of launch failure"""
        mock_find_terminal.return_value = ('xterm', ['xterm'])

        with patch('sys.exit') as mock_exit, \
                patch('sys.stderr'):
            relaunch_in_terminal(['test.epub'])
            mock_exit.assert_called_once_with(1)


class TestMainFunction:
    """Test main function"""

    @patch('speakub.cli.is_running_in_terminal', return_value=True)
    @patch('speakub.desktop.check_desktop_installed', return_value=True)
    @patch('speakub.ui.app.EPUBReaderApp')
    @patch('speakub.core.file_validator.FileValidator.validate_epub_file')
    def test_main_with_valid_epub(self, mock_validate, mock_app_class, mock_check_desktop, mock_is_terminal):
        """Test main function with valid EPUB file"""
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance

        # Create a temporary EPUB file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with patch('sys.argv', ['speakub', temp_path]):
                main([temp_path])

            mock_validate.assert_called_once_with(temp_path)
            mock_app_class.assert_called_once_with(
                temp_path, debug=False, log_file=None)
            mock_app_instance.run.assert_called_once()
        finally:
            os.unlink(temp_path)

    @patch('speakub.cli.is_running_in_terminal', return_value=True)
    @patch('speakub.desktop.check_desktop_installed', return_value=True)
    def test_main_with_nonexistent_epub(self, mock_check_desktop, mock_is_terminal):
        """Test main function with nonexistent EPUB file"""
        with patch('sys.exit') as mock_exit, \
                patch('sys.stderr'):
            main(['nonexistent.epub'])
            mock_exit.assert_called_once_with(1)

    @patch('speakub.cli.is_running_in_terminal', return_value=False)
    @patch('speakub.desktop.check_desktop_installed', return_value=True)
    def test_main_not_in_terminal(self, mock_check_desktop, mock_is_terminal):
        """Test main function when not running in terminal"""
        with patch('sys.exit') as mock_exit, \
                patch('sys.stderr'):
            main(['test.epub'])
            mock_exit.assert_called_once_with(1)

    @patch('speakub.cli.is_running_in_terminal', return_value=True)
    @patch('speakub.desktop.check_desktop_installed', return_value=False)
    @patch('speakub.desktop.install_desktop_entry')
    @patch('speakub.ui.app.EPUBReaderApp')
    @patch('speakub.core.file_validator.FileValidator.validate_epub_file')
    def test_main_installs_desktop_entry(self, mock_validate, mock_app_class, mock_install_desktop, mock_check_desktop, mock_is_terminal):
        """Test that desktop entry is installed on first run"""
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with patch('sys.argv', ['speakub', temp_path]):
                main([temp_path])

            mock_install_desktop.assert_called_once()
        finally:
            os.unlink(temp_path)

    def test_main_help_option(self):
        """Test main function with --help option"""
        with pytest.raises(SystemExit):
            main(['--help'])

    @patch('speakub.core.file_validator.FileValidator.validate_epub_file')
    def test_main_debug_logging(self, mock_validate):
        """Test debug logging setup"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            with patch('speakub.cli.is_running_in_terminal', return_value=True), \
                    patch('speakub.desktop.check_desktop_installed', return_value=True), \
                    patch('speakub.ui.app.EPUBReaderApp') as mock_app_class, \
                    patch('pathlib.Path.mkdir'), \
                    patch('datetime.datetime') as mock_datetime:

                mock_datetime.now.return_value.strftime.return_value = '20231112_120000'
                mock_app_instance = Mock()
                mock_app_class.return_value = mock_app_instance

                main([temp_path, '--debug'])

                # Check that debug logging was configured
                mock_app_class.assert_called_once()
                call_args = mock_app_class.call_args
                assert call_args[1]['debug'] is True
                assert 'speakub-20231112_120000.log' in call_args[1]['log_file']
        finally:
            os.unlink(temp_path)

    @patch('speakub.cli.is_running_in_terminal', return_value=True)
    @patch('speakub.desktop.check_desktop_installed', return_value=True)
    @patch('speakub.ui.app.EPUBReaderApp')
    @patch('speakub.core.file_validator.FileValidator.validate_epub_file')
    def test_main_custom_log_file(self, mock_validate, mock_app_class, mock_check_desktop, mock_is_terminal):
        """Test main function with custom log file"""
        mock_app_instance = Mock()
        mock_app_class.return_value = mock_app_instance

        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            custom_log = '/tmp/custom.log'
            main([temp_path, '--log-file', custom_log])

            mock_app_class.assert_called_once_with(
                temp_path, debug=False, log_file=custom_log)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    pytest.main([__file__])
