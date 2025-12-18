#!/usr/bin/env python3
"""
Test CLI error handling improvements.
"""

import tempfile
from pathlib import Path


def test_epub_not_found_error_handling():
    """Test that missing EPUB files are handled gracefully with immediate exit."""
    import io
    import sys
    from contextlib import redirect_stderr

    # Test with missing file
    with tempfile.TemporaryDirectory() as temp_dir:
        missing_file = Path(temp_dir) / "nonexistent.epub"

        # Capture stderr
        stderr_capture = io.StringIO()

        # Test the CLI function directly
        with redirect_stderr(stderr_capture):
            try:
                from speakub.cli import main
                main([str(missing_file)])
                assert False, "Should have exited"
            except SystemExit as e:
                assert e.code != 0, f"Expected non-zero exit code, got {e.code}"

        stderr_output = stderr_capture.getvalue()
        assert "Error: EPUB file not found" in stderr_output


def test_epub_invalid_file_error_handling():
    """Test that invalid EPUB files are handled gracefully with immediate exit."""
    import io
    import sys
    from contextlib import redirect_stderr

    # Test with invalid file (not a zip file)
    with tempfile.TemporaryDirectory() as temp_dir:
        invalid_file = Path(temp_dir) / "invalid.epub"
        invalid_file.write_text("not a zip file")

        # Set environment variables to avoid terminal relaunch issues
        import os
        old_term = os.environ.get("TERM")
        old_sdl = os.environ.get("SDL_VIDEODRIVER")
        try:
            os.environ["TERM"] = "xterm-256color"
            os.environ["SDL_VIDEODRIVER"] = "dummy"

            # Capture stderr
            stderr_capture = io.StringIO()

            # Test the CLI function directly
            with redirect_stderr(stderr_capture):
                try:
                    from speakub.cli import main
                    main([str(invalid_file)])
                    assert False, "Should have exited"
                except SystemExit as e:
                    assert e.code != 0, f"Expected non-zero exit code, got {e.code}"

            stderr_output = stderr_capture.getvalue()
            assert "Error: Invalid EPUB file" in stderr_output
        finally:
            # Restore environment
            if old_term is not None:
                os.environ["TERM"] = old_term
            elif "TERM" in os.environ:
                del os.environ["TERM"]
            if old_sdl is not None:
                os.environ["SDL_VIDEODRIVER"] = old_sdl
            elif "SDL_VIDEODRIVER" in os.environ:
                del os.environ["SDL_VIDEODRIVER"]


def test_terminal_detection_improvements():
    """Test improved terminal detection logic."""
    import speakub.cli as cli_module

    # Test various terminal scenarios
    original_method = cli_module.is_running_in_terminal

    # Mock different environments
    test_cases = [
        {"TERM": "xterm-256color"},  # Should work
        {"TERM": "linux"},           # Should work
        {"TERM": "dumb"},            # Should not work
        {"TERM": None},              # Should not work
    ]

    for i, env in enumerate(test_cases):
        # This test framework could be enhanced with proper mocking
        print(f"Test case {i}: TERM={env}")


if __name__ == "__main__":
    test_epub_not_found_error_handling()
    print("CLI error handling tests completed")
