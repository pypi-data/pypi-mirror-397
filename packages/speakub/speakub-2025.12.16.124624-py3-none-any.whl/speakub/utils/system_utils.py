#!/usr/bin/env python3
"""
System utilities for SpeakUB
"""

import logging
import os
import shutil
import subprocess
from functools import lru_cache
from typing import List, Optional, Tuple

from speakub.utils.error_handler import (
    ErrorCategory,
    ErrorSeverity,
    UnifiedErrorHandler,
)

logger = logging.getLogger(__name__)


def find_terminal_emulator() -> Optional[Tuple[str, List[str]]]:
    """
    Find an available terminal emulator and return the launch command
    Returns (terminal_name, command_args) or None
    """
    # Terminal emulator list, in order of preference
    terminals = [
        ("xterm", ["xterm", "-e"]),
        ("xfce4-terminal", ["xfce4-terminal", "-e"]),
        ("foot", ["foot", "-e"]),
        ("alacritty", ["alacritty", "-e"]),
        ("kitty", ["kitty", "-e"]),
        ("wezterm", ["wezterm", "start", "--"]),
        ("gnome-terminal", ["gnome-terminal", "--"]),
        ("konsole", ["konsole", "-e"]),
        ("urxvt", ["urxvt", "-e"]),
        ("st", ["st", "-e"]),
    ]

    # First check the system default terminal ($TERMINAL environment variable)
    default_term = os.environ.get("TERMINAL")
    if default_term:
        for term_name, cmd_args in terminals:
            if term_name == default_term:
                try:
                    result = subprocess.run(
                        ["which", term_name], capture_output=True, timeout=1
                    )
                    if result.returncode == 0:
                        return (term_name, cmd_args)
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    continue

    # If no default terminal or not found, check in order of preference
    for term_name, cmd_args in terminals:
        # Check if the terminal can be found
        try:
            result = subprocess.run(
                ["which", term_name], capture_output=True, timeout=1
            )
            if result.returncode == 0:
                return (term_name, cmd_args)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            continue

    return None


def play_warning_sound() -> None:
    """
    Play a system warning sound asynchronously.

    This function checks if the paplay command and sound file exist, and if they do,
    it uses subprocess.Popen to play the sound in the background without blocking the main program.

    🔄 Gradual Migration: Future versions may use AudioBackend interface for unified handling.
    """
    sound_file = "/usr/share/sounds/freedesktop/stereo/phone-outgoing-busy.oga"
    player_command = "paplay"

    # 1. Check if player command exists
    if not shutil.which(player_command):
        logger.debug(f"'{player_command}' command not found. Skipping warning sound.")
        return

    # 2. Check if sound file exists
    if not os.path.exists(sound_file):
        logger.debug(f"Warning sound file not found at '{sound_file}'. Skipping.")
        return

    try:
        # 3. Use Popen to run in background for asynchronous playback
        #    Redirect output to avoid printing messages in terminal
        command = [player_command, sound_file]
        subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        logger.debug(f"Playing warning sound: {sound_file}")
    except Exception as e:
        UnifiedErrorHandler.handle_error(
            e,
            f"Failed to play warning sound using {player_command}",
            ErrorCategory.TTS_PLAYBACK,
            ErrorSeverity.WARNING,
        )


def play_warning_sound_with_backend() -> None:
    """
    🔄 Phase 2: Play warning sound using new AudioBackend interface.

    This is a demonstration function for gradual migration, reading sound file and playing with AudioBackend.
    Currently as a backup option, may completely replace play_warning_sound() in the future.
    """
    sound_file = "/usr/share/sounds/freedesktop/stereo/phone-outgoing-busy.oga"

    # Check if sound file exists
    if not os.path.exists(sound_file):
        logger.debug(f"Warning sound file not found at '{sound_file}'. Skipping.")
        return

    try:
        # Read sound file content
        with open(sound_file, "rb") as f:
            audio_data = f.read()

        # Play using new AudioBackend interface
        from speakub.tts.backends import get_audio_backend

        backend = get_audio_backend("pygame")  # Use pygame for system sounds

        # Run in background to avoid blocking
        import threading

        def play_async():
            try:
                backend.play(audio_data, volume=0.7)  # Moderate volume
                logger.debug(f"Played warning sound with AudioBackend: {sound_file}")
            except Exception as e:
                UnifiedErrorHandler.handle_error(
                    e,
                    "Failed to play with AudioBackend",
                    ErrorCategory.TTS_PLAYBACK,
                    ErrorSeverity.WARNING,
                )
            finally:
                backend.cleanup()

        thread = threading.Thread(target=play_async, daemon=True)
        thread.start()

    except Exception as e:
        UnifiedErrorHandler.handle_error(
            e,
            "Failed to play warning sound with AudioBackend",
            ErrorCategory.TTS_PLAYBACK,
            ErrorSeverity.WARNING,
        )
        # Fallback to old method on failure
        play_warning_sound()


@lru_cache(maxsize=1)
def get_system_performance_rating() -> str:
    """
    Evaluate overall system performance rating for dynamic resource adjustment.

    (Use lru_cache to ensure calculation only once, avoid log spam)

    Returns:
        str: Performance rating ("low_end", "mid_range", "high_end")
    """
    try:
        # Check memory size
        total_memory_gb = get_total_memory_gb()

        # Check CPU core count and frequency
        cpu_cores = get_cpu_core_count()
        cpu_frequency = get_cpu_frequency()

        # Simple performance scoring logic
        # 8GB memory as baseline
        memory_score = min(total_memory_gb / 8.0, 1.0)
        cpu_score = min(
            (cpu_cores * cpu_frequency) / (4 * 2.5), 1.0
        )  # 4 cores 2.5GHz as baseline

        overall_score = (memory_score + cpu_score) / 2.0

        logger.debug(
            f"System performance metrics: "
            f"memory={total_memory_gb:.1f}GB, "
            f"cpu_cores={cpu_cores}, "
            f"cpu_freq={cpu_frequency:.1f}GHz, "
            f"overall_score={overall_score:.2f}"
        )

        # Determine performance rating based on overall score
        if overall_score < 0.4:
            return "low_end"
        elif overall_score < 0.7:
            return "mid_range"
        else:
            return "high_end"

    except Exception as e:
        logger.warning(
            f"Failed to determine system performance: {e}, defaulting to mid_range"
        )
        return "mid_range"


def get_total_memory_gb() -> float:
    """Get total system memory capacity (GB)"""
    try:
        from speakub.utils.resource_monitor import get_unified_resource_monitor

        # Use unified resource monitor
        unified_monitor = get_unified_resource_monitor()
        system_info = unified_monitor.get_system_info()
        return system_info.get("system_memory_total_gb", 8.0)
    except Exception as e:
        logger.debug(f"Failed to get total memory: {e}, using fallback")
        # Fallback: estimate based on common system configurations
        return 8.0  # Assume 8GB as default


def get_cpu_core_count() -> int:
    """Get CPU core count"""
    # Note: CPU core count is not currently provided by unified monitor
    # This would need to be added to the unified monitor if needed
    try:
        import psutil

        return psutil.cpu_count(logical=False) or psutil.cpu_count(logical=True)
    except ImportError:
        logger.debug("psutil not available, using fallback CPU detection")
        return 4  # Assume 4 cores as default


def get_cpu_frequency() -> float:
    """Get CPU frequency (GHz)"""
    # Note: CPU frequency is not currently provided by unified monitor
    # This would need to be added to the unified monitor if needed
    try:
        import psutil

        freq_info = psutil.cpu_freq()
        return freq_info.max / 1000.0 if freq_info else 2.5
    except (ImportError, AttributeError):
        logger.debug("psutil CPU frequency not available, using fallback")
        return 2.5  # Assume 2.5GHz as default
