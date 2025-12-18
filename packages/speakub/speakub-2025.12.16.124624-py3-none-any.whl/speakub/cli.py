#!/usr/bin/env python3
"""
SpeakUB CLI - Entry point for the application
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def is_running_in_terminal(debug: bool = False) -> bool:
    """
    Check if running in a real terminal environment
    - Check if stdout/stderr are tty
    - If not tty, we need to relaunch in terminal
    - If tty, check if it's a proper terminal
    """
    # Basic check: at least stderr must be tty (for interactive apps)
    stdout_is_tty = sys.stdout.isatty()
    stderr_is_tty = sys.stderr.isatty()
    if debug:
        print(
            f"DEBUG: stdout.isatty()={stdout_is_tty}, "
            f"stderr.isatty()={stderr_is_tty}",
            file=sys.stderr,
        )

    # Check TERM environment variable
    term = os.environ.get("TERM", "")
    if debug:
        print(f"DEBUG: TERM={term}", file=sys.stderr)

    # Special case: if TERM is xterm-256color, assume we're in a
    # compatible environment
    # This handles cases like VSCode terminal, desktop integration,
    # and other GUI environments
    if term == "xterm-256color":
        if debug:
            print(
                "DEBUG: TERM is xterm-256color, assuming compatible terminal",
                file=sys.stderr,
            )
        return True

    # If stderr is a tty, we're likely in a terminal (even if TERM is unknown)
    if stderr_is_tty:
        if debug:
            print(
                "DEBUG: stderr is tty, assuming we're in a terminal",
                file=sys.stderr,
            )
        return True

    # Check for common terminal types that support TUI applications
    SUPPORTED_PREFIXES = (
        "xterm",
        "screen",
        "tmux",
        "linux",
        "alacritty",
        "rxvt",
        "konsole",
        "gnome",
        "xfce",
    )
    SUPPORTED_EXACT = ("alacritty", "kitty", "st", "foot")

    if term and (term.startswith(SUPPORTED_PREFIXES) or term in SUPPORTED_EXACT):
        if debug:
            print(
                f"DEBUG: TERM {term} indicates compatible terminal, " "assuming OK",
                file=sys.stderr,
            )
        return True

    # If TERM is set to something reasonable, assume it's a terminal
    if term and term not in ("dumb", "unknown"):
        if debug:
            print(
                f"DEBUG: TERM is set to {term}, assuming terminal", file=sys.stderr)
        return True

    if debug:
        print(
            f"DEBUG: Cannot determine terminal environment, "
            f"stderr_is_tty={stderr_is_tty}, TERM={term}",
            file=sys.stderr,
        )
    return False


def relaunch_in_terminal(original_args: List[str], debug: bool = False) -> None:
    """
    Relaunch the application in a terminal emulator

    Args:
        original_args: Original command line arguments
        debug: Whether debug output should be shown
    """
    if debug:
        print(
            f"DEBUG: Relaunching in terminal with args: {original_args}",
            file=sys.stderr,
        )
    from speakub.utils.system_utils import find_terminal_emulator

    terminal_info = find_terminal_emulator()

    if not terminal_info:
        if debug:
            print("DEBUG: No terminal emulator found", file=sys.stderr)
        # Unable to find terminal emulator, try to notify user with desktop notification
        try:
            subprocess.run(
                [
                    "notify-send",
                    "SpeakUB Error",
                    "No terminal emulator found. Please run from a terminal.",
                ],
                timeout=2,
            )
        except Exception:
            pass

        print("Error: No terminal emulator found.", file=sys.stderr)
        print("Please run SpeakUB from a terminal.", file=sys.stderr)
        sys.exit(1)

    term_name, term_cmd = terminal_info
    if debug:
        print(
            f"DEBUG: Found terminal: {term_name}, command: {term_cmd}", file=sys.stderr
        )

    # Build the complete launch command
    # Use current Python interpreter and script path
    python_exe = sys.executable
    script_path = os.path.abspath(sys.argv[0])

    # Check if we're running as a module (python -m speakub.cli)
    if script_path.endswith(".py") and "speakub/cli.py" in script_path:
        # Running as module, use python -m
        cmd_string = f"{python_exe} -m speakub.cli"
    else:
        # Running as installed script
        cmd_string = f"{python_exe} {script_path}"

    if original_args:
        # Use shlex.quote to properly escape arguments
        import shlex

        quoted_args = [shlex.quote(arg) for arg in original_args]
        cmd_string += " " + " ".join(quoted_args)

    # Use appropriate command format for each terminal
    # Wrap command to exit terminal after execution
    exit_cmd = f"{cmd_string}; exit"

    if term_name == "xfce4-terminal":
        # xfce4-terminal: execute without hold, terminal closes after exit
        full_cmd = ["xfce4-terminal", "-e", f"bash -c '{exit_cmd}'"]
    elif term_name == "xterm":
        # xterm: execute without -hold so terminal closes
        full_cmd = ["xterm", "-e", f"bash -c '{exit_cmd}'"]
    elif term_name in ("gnome-terminal", "konsole"):
        # These terminals work better with bash -c
        full_cmd = term_cmd + ["bash", "-c", exit_cmd]
    elif term_name == "alacritty":
        # Alacritty: use -e with shell
        full_cmd = ["alacritty", "-e", "bash", "-c", exit_cmd]
    elif term_name == "kitty":
        # Kitty: use -e with shell
        full_cmd = ["kitty", "-e", "bash", "-c", exit_cmd]
    else:
        # For other terminals, try the standard approach with exit
        full_cmd = term_cmd + ["bash", "-c", exit_cmd]
    if debug:
        print(f"DEBUG: Full command: {full_cmd}", file=sys.stderr)

    try:
        # Launch with Popen in background, don't wait for completion
        if debug:
            print("DEBUG: Launching subprocess...", file=sys.stderr)
        subprocess.Popen(
            full_cmd,
            start_new_session=True,  # Detach from current session
            # Don't redirect stdout/stderr so user can see any error messages
        )
        if debug:
            print(
                "DEBUG: Subprocess launched, exiting current process", file=sys.stderr
            )
        # Exit current process immediately
        sys.exit(0)
    except Exception as e:
        print(f"Error launching terminal ({term_name}): {e}", file=sys.stderr)
        sys.exit(1)


def main(argv: Optional[List[str]] = None) -> None:
    """Main entry point for SpeakUB."""

    # ===== Parse arguments first to get debug flag =====
    parser = argparse.ArgumentParser(description="SpeakUB")
    parser.add_argument(
        "epub", nargs="?", help="Path to EPUB file (optional if bookmarks exist)"
    )
    parser.add_argument("--debug", action="store_true",
                        help="Enable debug logging")
    parser.add_argument("--log-file", help="Path to log file")
    args = parser.parse_args(argv)

    # ===== Early validation: Check if EPUB file exists and is valid =====
    if args.epub:
        epub_path = Path(args.epub)
        if not epub_path.exists():
            from speakub.utils.user_friendly_errors import print_friendly_error

            error = FileNotFoundError(f"EPUB file not found: {args.epub}")
            print_friendly_error(error, "file access")
            sys.exit(1)

        # Perform comprehensive file validation before proceeding
        try:
            from speakub.core.file_validator import FileValidator

            FileValidator.validate_epub_file(str(epub_path))
        except Exception as e:
            from speakub.utils.user_friendly_errors import print_friendly_error

            print_friendly_error(e, "EPUB validation")
            sys.exit(1)

    # ===== Check if running in terminal =====
    if not is_running_in_terminal(args.debug):
        from speakub.utils.user_friendly_errors import print_friendly_error

        terminal_error: Exception = RuntimeError(
            "terminal environment required")
        print_friendly_error(terminal_error, "terminal detection")
        sys.exit(1)

    # ===== Import heavy modules after terminal check =====
    # ===== Auto-install desktop entry on first run =====
    from speakub.desktop import check_desktop_installed, install_desktop_entry
    from speakub.ui.app import EPUBReaderApp

    if not check_desktop_installed():
        try:
            install_desktop_entry()
        except Exception as e:
            # Use unified error handler for better logging
            from speakub.utils.error_handler import ErrorHandler

            ErrorHandler.handle_and_suppress(
                e, "Desktop entry installation failed", {"component": "cli"}
            )

    # =======================================================
    # 🔧 Fix Duplicate Logs
    # Force clear all existing Handlers (key to solving double display!)
    # =======================================================

    # Clear redundant Handler automatically generated by logging_config.py
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    speakub_logger = logging.getLogger("speakub")
    if speakub_logger.hasHandlers():
        speakub_logger.handlers.clear()
    # Ensure speakub messages propagate up to Root Logger,
    # unified display by Handlers set below
    speakub_logger.propagate = True

    # Apply logging_config component level settings (but do not add handlers)
    from speakub.utils.logging_config import apply_component_levels

    apply_component_levels(debug_mode=args.debug)

    if args.debug and not args.log_file:
        log_dir = Path.home() / ".local/share/speakub/logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.log_file = str(log_dir / f"speakub-{ts}.log")
        print(f"Debug logging to: {args.log_file}")

    # Set up new Handlers
    log_level = logging.DEBUG if args.debug else logging.WARNING
    handlers: List[logging.Handler] = []

    # Set up screen output (retain monitoring function)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    # Use concise format, display one line only
    console_formatter = logging.Formatter(
        "[%(levelname)s] %(name)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    handlers.append(console_handler)

    # Set up file output
    if args.log_file:
        try:
            file_handler = logging.FileHandler(
                Path(args.log_file).expanduser(), encoding="utf-8"
            )
            file_handler.setLevel(log_level)
            handlers.append(file_handler)
        except Exception:
            pass

    # Apply settings
    logging.basicConfig(
        level=log_level,
        handlers=handlers,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        force=True,  # 強制覆蓋
    )

    # Suppress gTTS and related library DEBUG messages
    logging.getLogger("gtts").setLevel(logging.WARNING)
    logging.getLogger("gtts.tts").setLevel(logging.WARNING)
    logging.getLogger("gtts.lang").setLevel(logging.ERROR)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

    # Debug: Log TTS engine configuration
    if args.debug:
        from speakub.utils.config import get_current_tts_config_summary

        logging.debug(f"CLI Debug: {get_current_tts_config_summary()}")

    # Handle EPUB file path - check bookmark status logic
    if args.epub:
        # EPUB path provided, use original logic
        epub_path = Path(args.epub)
    else:
        # No EPUB path provided, check bookmark status
        bookmarks_exist = check_bookmarks_exist()
        bookmarks_empty = check_bookmarks_empty()

        if args.debug:
            print(
                f"DEBUG: bookmarks_exist={bookmarks_exist}, "
                f"bookmarks_empty={bookmarks_empty}",
                file=sys.stderr,
            )

        if bookmarks_exist and not bookmarks_empty:
            # Bookmarks exist and not empty - let user select file from bookmarks
            selected_path = show_bookmarks_file_picker()
            if not selected_path:
                sys.exit(1)
            epub_path = Path(selected_path)
        else:
            # No bookmark file or bookmarks empty - same as original behavior,
            # require specified file
            from speakub.utils.user_friendly_errors import print_friendly_error

            bookmark_error: Exception = ValueError(
                "No EPUB file specified and no bookmarks found"
            )
            print_friendly_error(bookmark_error, "file selection")
            sys.exit(1)

    app = EPUBReaderApp(str(epub_path), debug=args.debug,
                        log_file=args.log_file)
    app.run()


def check_bookmarks_exist() -> bool:
    """Check if bookmarks.json file exists"""
    from speakub.core.bookmarks import BOOKMARK_FILE

    return os.path.exists(BOOKMARK_FILE)


def check_bookmarks_empty() -> bool:
    """Check if bookmark file has records"""
    from speakub.core.bookmarks import bookmark_manager

    try:
        bookmark_manager.load_bookmarks()
        return len(bookmark_manager.bookmarks) == 0
    except Exception:
        return True  # If loading fails, consider empty


def show_bookmarks_file_picker() -> Optional[str]:
    """Show bookmark-style file picker, let user select file from existing bookmarks"""
    from typing import Any, Dict

    from speakub.core.bookmarks import bookmark_manager

    # Get all unique EPUB files
    epub_files: Dict[str, Dict[str, Any]] = {}
    for bookmark in bookmark_manager.bookmarks:
        epub_path = str(bookmark.epub_path)  # Ensure epub_path is a string
        if epub_path not in epub_files:
            # Use filename (without extension) as display title, easier to identify
            filename = os.path.basename(epub_path).replace(".epub", "")
            epub_files[epub_path] = {"title": filename, "bookmark_count": 1}
        else:
            epub_files[epub_path]["bookmark_count"] += 1

    if not epub_files:
        print("No bookmark files available.", file=sys.stderr)
        return None

    # Display available files
    print("Available EPUB files from bookmarks:", file=sys.stderr)
    file_list = list(epub_files.items())
    for i, (epub_path, info) in enumerate(file_list, 1):
        print(
            f"{i}. {info['title']} ({info['bookmark_count']} bookmarks)",
            file=sys.stderr,
        )

    print(
        f"Enter number (1-{len(file_list)}) or 'q' to quit: ", end="", file=sys.stderr
    )

    try:
        # Simple text input interface
        choice = input().strip().lower()
        if choice == "q":
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(file_list):
                selected_path = file_list[index][0]
                print(
                    f"Selected: {epub_files[selected_path]['title']}", file=sys.stderr
                )
                return selected_path
            else:
                print("Invalid selection.", file=sys.stderr)
                return None
        except ValueError:
            print("Invalid input. Please enter a number or 'q'.", file=sys.stderr)
            return None

    except (EOFError, KeyboardInterrupt):
        print("Selection cancelled.", file=sys.stderr)
        return None


if __name__ == "__main__":
    main()
