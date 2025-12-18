#!/usr/bin/env python3
"""
gTTS Provider - Google Text-to-Speech implementation.
Updated to use asyncio-based MPV backend with modern threading.
"""

import asyncio
import logging
import os
from typing import Any, Dict, List

try:
    from gtts import gTTS

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import mpv

    MPV_AVAILABLE = True
except ImportError:
    MPV_AVAILABLE = False

from speakub.tts.backends import get_audio_backend
from speakub.tts.engine import TTSEngine, TTSError, TTSState
from speakub.utils.config import ConfigManager

logger = logging.getLogger(__name__)


class GTTSProvider(TTSEngine):
    """Google Text-to-Speech provider."""

    # 預定義的中文女性語音
    FEMALE_CHINESE_VOICES = [
        {
            "name": "Google TTS - Chinese (Mandarin, Simplified)",
            "short_name": "gtts-zh-CN",
            "gender": "Female",
            "locale": "zh-CN",
            "display_name": "Chinese (Simplified)",
            "local_name": "中文（簡體）",
        },
        {
            "name": "Google TTS - Chinese (Mandarin, Traditional)",
            "short_name": "gtts-zh-TW",
            "gender": "Female",
            "locale": "zh-TW",
            "display_name": "Chinese (Traditional)",
            "local_name": "中文（繁體）",
        },
        {
            "name": "Google TTS - Chinese (Mandarin)",
            "short_name": "gtts-zh",
            "gender": "Female",
            "locale": "zh",
            "display_name": "Chinese (Mandarin)",
            "local_name": "中文（普通話）",
        },
    ]

    def __init__(self, audio_backend=None, config_manager=None):
        """Initialize gTTS provider with modern asyncio backend."""
        super().__init__()
        if not GTTS_AVAILABLE:
            raise ImportError(
                "gtts not installed. Install with: pip install gtts")

        # Dependency injection
        if config_manager is not None:
            self._config_manager = config_manager
        else:
            from speakub.utils.config import ConfigManager

            self._config_manager = ConfigManager()

        # Initialize modern audio backend
        if audio_backend is not None:
            self.audio_backend = audio_backend
        else:
            self.audio_backend = get_audio_backend("mpv")

        # Load configuration with GTTS-specific defaults
        self._current_volume = self._config_manager.get("gtts.volume", 1.0)
        self._current_speed = self._config_manager.get(
            "gtts.playback_speed", 1.5  # GTTS default 1.5x
        )
        self._current_voice = self._config_manager.get(
            "gtts.default_voice", "gtts-zh-TW"
        )

        # Sync settings to backend
        self.audio_backend.set_volume(self._current_volume)
        self.audio_backend.set_speed(self._current_speed)

        # State tracking for backward compatibility (delegate to state manager)
        self._is_paused = False
        self._current_audio_file = None

        logger.debug(
            f"GTTS initialized with voice: {self._current_voice}, "
            f"volume: {self._current_volume}, speed: {self._current_speed}"
        )

    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text using gTTS.
        Note: gTTS does not support rate, pitch, volume in synthesis.
        These are controlled during playback.
        """
        if not GTTS_AVAILABLE:
            raise RuntimeError("gTTS not available")

        # Validate and sanitize TTS text input
        from speakub.utils.security import TextSanitizer

        try:
            TextSanitizer.validate_tts_text(text)
            text = TextSanitizer.sanitize_tts_text(text)
        except ValueError as e:
            logger.error(f"TTS text validation failed: {e}")
            raise

        if not text or not text.strip():
            logger.warning("Empty text after sanitization")
            return b""

        if voice == "default":
            voice = self._current_voice

        # Extract language code from voice name
        lang = voice.split("-")[-1]  # e.g., "gtts-zh-TW" -> "TW"
        tld = "com"
        if lang == "TW":
            lang = "zh-TW"  # Keep original format as gTTS expects it
            tld = "com.tw"
        elif lang == "CN":
            lang = "zh-CN"  # Keep original format as gTTS expects it
            tld = "com"
        elif lang == "zh":
            lang = "zh"  # Keep as is for general Chinese
            tld = "com"

        logger.debug(
            f"Synthesizing text: '{text[:50]}...' with voice: {voice}, lang: {lang}"
        )

        # Generate speech with enhanced network security and error handling
        import logging

        # Save original levels for gtts library logging
        gtts_logger = logging.getLogger("gtts")
        gtts_lang_logger = logging.getLogger("gtts.lang")
        urllib3_logger = logging.getLogger("urllib3")

        original_gtts_level = gtts_logger.level
        original_gtts_lang_level = gtts_lang_logger.level
        original_urllib3_level = urllib3_logger.level

        # Suppress verbose gtts messages while maintaining our own logs
        gtts_logger.setLevel(logging.WARNING)
        gtts_lang_logger.setLevel(logging.ERROR)
        urllib3_logger.setLevel(logging.ERROR)

        # Network error retry configuration
        max_retries = 3
        retry_delay = 2.0  # Start with 2 seconds

        try:
            tts = None
            for attempt in range(max_retries + 1):
                try:
                    logger.debug(
                        "Creating gTTS instance with timeout protection...")

                    # Use asyncio.wait_for for timeout control
                    async def create_gtts_with_timeout():
                        try:
                            # Run gTTS creation in thread pool to avoid blocking
                            tts = await asyncio.to_thread(
                                lambda: gTTS(
                                    text=text,
                                    lang=lang,
                                    tld=tld,
                                    slow=False,
                                    timeout=25,  # 25s timeout for gTTS network operations
                                )
                            )
                            return tts
                        except Exception as e:
                            logger.error(f"gTTS creation failed: {e}")
                            raise RuntimeError(
                                f"gTTS synthesis failed: {e}") from e

                    # Wait for gTTS creation with 30s timeout
                    tts = await asyncio.wait_for(
                        create_gtts_with_timeout(), timeout=30.0
                    )

                    # If we get here, synthesis succeeded
                    break

                except asyncio.TimeoutError as e:
                    if attempt < max_retries:
                        logger.warning(
                            f"gTTS timeout on attempt {attempt+1}/{max_retries+1}: {e}. Retrying in {retry_delay}s..."
                        )
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                    else:
                        logger.error(
                            "gTTS operation timed out after all retries")
                        raise RuntimeError(
                            "gTTS network request timed out after retries"
                        ) from e

                except RuntimeError as e:
                    # Check if it's a network-related RuntimeError
                    error_str = str(e)
                    if any(
                        keyword in error_str.lower()
                        for keyword in [
                            "connection",
                            "timeout",
                            "network",
                            "dns",
                            "resolve",
                            "unreachable",
                        ]
                    ):
                        if attempt < max_retries:
                            logger.warning(
                                f"gTTS network error on attempt {attempt+1}/{max_retries+1}: {e}. Retrying in {retry_delay}s..."
                            )
                            await asyncio.sleep(retry_delay)
                            retry_delay *= 2  # Exponential backoff
                        else:
                            logger.error(
                                "Max retries exceeded for gTTS network error")
                            raise RuntimeError(
                                f"gTTS synthesis failed after {max_retries+1} attempts: {e}"
                            ) from e
                    else:
                        # Non-network error, don't retry
                        raise

                except Exception as e:
                    # For non-network or timeout errors, don't retry
                    logger.error(f"Unexpected error during gTTS creation: {e}")
                    raise RuntimeError(f"gTTS synthesis failed: {e}") from e
        finally:
            # Always restore original logging levels
            gtts_logger.setLevel(original_gtts_level)
            gtts_logger.setLevel(original_gtts_lang_level)
            urllib3_logger.setLevel(original_urllib3_level)

        # Use managed temp file for safe automatic cleanup
        from speakub.utils.file_utils import get_resource_manager

        resource_manager = get_resource_manager()

        with resource_manager.managed_temp_file(suffix=".mp3") as temp_file:
            # Save to temporary file and read bytes
            tts.save(temp_file)

            # ⭐ 修復：確保文件被完整寫入
            with open(temp_file, "rb") as f:
                audio_data = f.read()

            # ⭐ 修復：驗證音頻數據是否有效
            if len(audio_data) == 0:
                logger.error("Generated audio file is empty")
                raise RuntimeError("Failed to generate audio: empty file")

            logger.debug(f"Generated audio file size: {len(audio_data)} bytes")

        return audio_data

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available gTTS voices (pre-defined)."""
        return self.FEMALE_CHINESE_VOICES.copy()

    def get_voices_by_language(self, language: str) -> List[Dict[str, Any]]:
        """Get voices for a specific language."""
        return [
            voice
            for voice in self.FEMALE_CHINESE_VOICES
            if voice["locale"].startswith(language)
        ]

    def set_voice(self, voice_name: str) -> bool:
        """Set the current voice."""
        if not voice_name or not voice_name.startswith("gtts-"):
            return False
        # Validate voice
        valid_voices = [v["short_name"] for v in self.FEMALE_CHINESE_VOICES]
        if voice_name in valid_voices:
            self._current_voice = voice_name
            return True
        return False

    def get_current_voice(self) -> str:
        """Get the currently selected voice."""
        return self._current_voice

    # ===== MODERN ASYNCIO PLAYBACK METHODS =====

    async def play_audio_non_blocking(self, audio_data: bytes) -> None:
        """Start playing audio data (non-blocking with asyncio)."""
        await asyncio.to_thread(
            self.audio_backend.play,
            audio_data,
            self._current_speed,
            self._current_volume,
        )

    async def wait_for_playback_completion(self) -> None:
        """Wait for current playback to complete (async version)."""
        # AudioBackend.play is already blocking, nothing to wait for
        pass

    async def play_audio(self, audio_data: bytes) -> None:
        """Play audio data using asyncio backend."""
        logger.debug(
            f"Playing {len(audio_data)} bytes via modern asyncio backend")
        try:
            await asyncio.to_thread(
                self.audio_backend.play,
                audio_data,
                self._current_speed,
                self._current_volume,
            )
            logger.debug("Async playback completed")
        except Exception as e:
            logger.error(f"Async playback failed: {e}")
            raise TTSError(f"Audio playback failed: {e}")

    def pause(self) -> None:
        """Pause audio playback."""
        try:
            self.audio_backend.pause()
            self._change_state(TTSState.PAUSED)
            self._is_paused = True
            logger.debug("Audio playback paused")
        except Exception as e:
            logger.warning(f"Failed to pause: {e}")
            raise TTSError(f"Pause failed: {e}")

    def resume(self) -> None:
        """Resume audio playback."""
        try:
            self.audio_backend.resume()
            self._change_state(TTSState.PLAYING)
            self._is_paused = False
            logger.debug("Audio playback resumed")
        except Exception as e:
            logger.warning(f"Failed to resume: {e}")
            raise TTSError(f"Resume failed: {e}")

    def stop(self) -> None:
        """Stop audio playback and cleanup."""
        try:
            self.audio_backend.stop()
            self._change_state(TTSState.STOPPED)
            self._is_paused = False
            logger.debug("Audio playback stopped")
        except Exception as e:
            logger.warning(f"Failed to stop: {e}")
            raise TTSError(f"Stop failed: {e}")

    def _update_state(self, new_state: TTSState) -> None:
        """Update internal state via state manager (backward compatible)."""
        try:
            self._state_manager.transition(new_state)
        except Exception:
            logger.exception("Failed to update state to %s", new_state)

    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        try:
            return self.audio_backend.can_resume()
        except Exception:
            return False

    def seek(self, position: int) -> None:
        """Seek not supported by GTTS."""
        logger.warning("Seek operation not supported by GTTS provider")

    # ===== MODERN CONFIGURATION METHODS =====

    def _get_volume_limits(self) -> tuple[float, float]:
        """Get GTTS-specific volume limits."""
        return self._config_manager.get(
            "gtts.volume_min", 0.0
        ), self._config_manager.get("gtts.volume_max", 1.5)

    def _get_speed_limits(self) -> tuple[float, float]:
        """Get GTTS-specific speed limits."""
        return self._config_manager.get(
            "gtts.speed_min", 0.5
        ), self._config_manager.get("gtts.speed_max", 3.0)

    def set_volume(self, volume: float) -> None:
        """Set playback volume with configuration limits."""
        volume_min, volume_max = self._get_volume_limits()
        self._current_volume = max(volume_min, min(volume_max, volume))
        logger.debug(
            f"GTTS volume set to {self._current_volume} "
            f"(range: {volume_min}-{volume_max})"
        )

        try:
            self.audio_backend.set_volume(self._current_volume)
            self._config_manager.set("gtts.volume", self._current_volume)
            logger.debug("Volume saved to config")
        except Exception as e:
            logger.warning(f"Failed to update volume: {e}")

    def get_volume(self) -> float:
        """Get current volume level."""
        try:
            return self.audio_backend.get_volume()
        except Exception:
            return self._current_volume

    def set_speed(self, speed: float) -> None:
        """Set playback speed with configuration limits."""
        speed_min, speed_max = self._get_speed_limits()
        self._current_speed = max(speed_min, min(speed_max, speed))
        logger.debug(
            f"GTTS speed set to {self._current_speed} "
            f"(range: {speed_min}-{speed_max})"
        )

        try:
            self.audio_backend.set_speed(self._current_speed)
            self._config_manager.set(
                "gtts.playback_speed", self._current_speed)
            logger.debug("Speed saved to config")
        except Exception as e:
            logger.warning(f"Failed to update speed: {e}")

    def get_speed(self) -> float:
        """Get current speed level."""
        try:
            return self.audio_backend.get_speed()
        except Exception:
            return self._current_speed

    def _get_char_limit(self) -> int:
        """Get GTTS-specific character limit for batching."""
        return 100  # GTTS has lower limits, be conservative

    def _get_batch_size_preference(self) -> int:
        """Get preferred batch size for GTTS."""
        return 1  # GTTS works best with single items

    def _supports_batch_merging(self) -> bool:
        """GTTS does not support merging multiple texts into single API call."""
        return False

    def _needs_text_sanitization(self) -> bool:
        """GTTS requires text sanitization."""
        return True

    def _get_rate_limit_cooldown(self) -> float:
        """Get rate limiting cooldown period for GTTS."""
        return 2.0  # GTTS needs longer cooldown

    def get_current_state(self) -> str:
        """Get current TTS state for debugging."""
        return self._state_manager.state.value

    async def speak_text_async(
        self, text: str, voice: str = "default", **kwargs
    ) -> None:
        """Async text-to-speech with voice selection."""
        audio_data = await self.synthesize(text, voice, **kwargs)
        await self.play_audio(audio_data)

    async def cleanup_resources(self) -> None:
        """
        Clean up all GTTS engine resources.
        GTTS uses MPV backend, so delegate to backend cleanup.
        """
        logger.debug("Cleaning up GTTS engine resources")

        try:
            # Stop async loop if running
            self.stop_async_loop()

            # Clean up audio backend
            if hasattr(self.audio_backend, "cleanup"):
                await asyncio.to_thread(self.audio_backend.cleanup)
            elif hasattr(self.audio_backend, "stop"):
                self.audio_backend.stop()

            # Clean up any temporary files (GTTS uses managed temp files, should be auto-cleaned)

            logger.debug("GTTS engine resources cleaned up successfully")

        except Exception as e:
            logger.warning(f"Error during GTTS cleanup: {e}")
            # Don't raise - cleanup should not fail the operation


# 🔧 額外的診斷工具 - 可以加在調試時使用
def diagnose_gtts_state(provider):
    """診斷 GTTSProvider 的當前狀態"""
    print("=== gTTS Provider State Diagnosis ===")
    print(f"Current State: {provider.get_current_state()}")
    print(f"Is Paused (_is_paused): {provider._is_paused}")
    print(f"Has Audio Backend: {hasattr(provider, 'audio_backend')}")
    print(f"Current Audio File: {provider._current_audio_file}")
    if provider._current_audio_file:
        print(f"File Exists: {os.path.exists(provider._current_audio_file)}")
    print(f"Can Resume: {provider.can_resume()}")
    print("=" * 40)
