#!/usr/bin/env python3
"""
Edge-TTS Provider - Microsoft Edge TTS implementation.
"""

import asyncio
import logging
import random  # Added for Jitter
import socket
import threading
from typing import Any, Dict, List, Optional

try:
    import aiohttp
    import edge_tts

    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Make aiohttp available even if edge_tts import succeeded but aiohttp failed
try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    aiohttp = None  # Use None to prevent attribute errors
    AIOHTTP_AVAILABLE = False

from speakub.tts.backends import get_audio_backend
from speakub.tts.engine import TTSEngine, TTSState

logger = logging.getLogger(__name__)


def _sanitize_tts_error_message(error_message: str) -> str:
    """
    Sanitize TTS error messages to remove sensitive authentication data.

    Args:
        error_message: The original error message

    Returns:
        Sanitized error message with sensitive data masked
    """
    import re

    # Mask subscription keys (API keys)
    error_message = re.sub(
        r"Ocp-Apim-Subscription-Key=[A-F0-9]{32}",
        "Ocp-Apim-Subscription-Key=***MASKED***",
        error_message,
    )

    # Mask Sec-MS-GEC headers (hex values followed by additional data)
    error_message = re.sub(
        r"Sec-MS-GEC=[A-F0-9]+", "Sec-MS-GEC=***MASKED***", error_message
    )

    # Mask Sec-MS-GEC-Version headers
    error_message = re.sub(
        r"Sec-MS-GEC-Version=[^&\s]+", "Sec-MS-GEC-Version=***MASKED***", error_message
    )

    return error_message


class EdgeTTSProvider(TTSEngine):
    """Microsoft Edge TTS provider."""

    DEFAULT_VOICES = {
        "en-US": "en-US-AriaNeural",
        "zh-CN": "zh-CN-XiaoxiaoNeural",
        "zh-TW": "zh-TW-HsiaoChenNeural",
        "ja-JP": "ja-JP-NanamiNeural",
        "ko-KR": "ko-KR-SunHiNeural",
    }

    def __init__(self, config_manager=None):
        """Initialize Edge TTS provider."""
        super().__init__()

        if not EDGE_TTS_AVAILABLE:
            raise ImportError(
                "edge-tts package not installed. Install with: pip install edge-tts"
            )

        # Use provided ConfigManager or create new one for backward compatibility
        if config_manager is not None:
            self._config_manager = config_manager
        else:
            from speakub.utils.config import ConfigManager

            self._config_manager = ConfigManager()

        self.audio_backend = get_audio_backend("pygame")
        self._voices_cache: Optional[List[Dict[str, Any]]] = None
        self._current_voice = self._config_manager.get(
            "edge-tts.voice", self.DEFAULT_VOICES.get(
                "zh-TW", "zh-TW-HsiaoChenNeural")
        )

        # TTS synthesis parameters (used during synthesis, not playback)
        # 如果沒有引擎特定配置，則使用全局配置作為備用
        self._tts_volume = self._config_manager.get(
            # For synthesis
            "edge-tts.volume",
            self._config_manager.get("tts.volume", 100) / 100.0,
        )
        self._tts_speed = self._config_manager.get(
            "edge-tts.playback_speed", 1.0
        )  # For synthesis
        self._tts_pitch = self._config_manager.get(
            "edge-tts.pitch", "+0Hz"
        )  # For synthesis

        # State management is delegated to TTSEngine -> TTSStateManager
        # Keep a local paused flag and current audio buffer for compatibility
        self._current_audio_data: Optional[bytes] = None
        self._current_text: Optional[str] = None  # Text of current audio
        self._is_paused: bool = False

        # Rate limiting protection
        self._rate_limiting_active: bool = False
        self._rate_limit_cooldown: float = 1.0  # Default 1 second between requests

    def _transition_state(self, new_state: TTSState) -> bool:
        """Delegate state transition to the shared state manager."""
        try:
            return self._state_manager.transition(new_state)
        except Exception:
            logger.exception("Failed to transition state to %s", new_state)
            return False

    def _update_state(self, new_state: TTSState) -> None:
        """Update state via the shared manager (keeps behavior consistent)."""
        try:
            self._state_manager.transition(new_state)
            logger.debug(
                "TTS state updated: %s | paused=%s",
                new_state.value,
                self._is_paused,
                extra={"component": "tts", "action": "state_update"},
            )
        except Exception:
            logger.exception("Failed to update state to %s", new_state)

    def get_current_state(self) -> str:
        """Get current state for monitoring."""
        return self._state_manager.state.value

    def _on_audio_state_changed(self, player_state: str) -> None:
        """Handle audio player state changes."""
        state_mapping = {
            "playing": TTSState.PLAYING,
            "paused": TTSState.PAUSED,
            "stopped": TTSState.STOPPED,
            "finished": TTSState.IDLE,
            "error": TTSState.ERROR,
        }

        if player_state in state_mapping:
            self._change_state(state_mapping[player_state])

    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text using Edge TTS with network error retry logic.
        """
        if not EDGE_TTS_AVAILABLE:
            raise RuntimeError("Edge TTS not available")

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

        # Network error retry configuration - now from unified config
        from speakub.utils.retry_utils import (
            should_retry_network_error,
            get_dns_retry_delay,
            get_network_retry_delay
        )

        attempt = 0
        while should_retry_network_error(attempt, self._config_manager):
            try:
                # Use dynamic cooldown based on rate limiting status
                await asyncio.sleep(self._rate_limit_cooldown)

                # Use parameters from kwargs if provided (e.g., from app settings), otherwise use internal TTS synthesis parameters
                rate = kwargs.get(
                    "rate", f"{int((self._tts_speed - 1.0) * 100):+}%")
                pitch = kwargs.get("pitch", self._tts_pitch)
                volume = kwargs.get(
                    "volume", f"{int((self._tts_volume - 1.0) * 100):+}%"
                )

                communicate = edge_tts.Communicate(
                    text=text, voice=voice, rate=rate, pitch=pitch, volume=volume
                )

                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio" and "data" in chunk:
                        audio_data += chunk["data"]

                return audio_data

            except (asyncio.TimeoutError, socket.gaierror) as e:
                # Determine if it's a DNS error or standard network error
                error_str = str(e).lower()
                is_dns_error = (
                    isinstance(e, socket.gaierror)
                    or "name resolution" in error_str
                    or "getaddrinfo" in error_str
                )

                # Also check aiohttp specific DNS errors
                if AIOHTTP_AVAILABLE and aiohttp and not is_dns_error:
                    if isinstance(e, aiohttp.ClientConnectorDNSError):
                        is_dns_error = True
                    elif isinstance(
                        e, (aiohttp.ClientConnectorError, aiohttp.ClientError)
                    ):
                        pass  # Handled as generic network error below

                if should_retry_network_error(attempt + 1, self._config_manager):
                    # Strategy: DNS errors need longer wait times, others use standard delay
                    if is_dns_error:
                        current_delay = get_dns_retry_delay(
                            attempt, self._config_manager)
                        logger.warning(
                            "DNS Resolution Failure (Attempt %d): %s. "
                            "Sleeping %.2fs to allow network recovery...",
                            attempt + 1,
                            e,
                            current_delay,
                        )
                    else:
                        current_delay = get_network_retry_delay(
                            attempt, self._config_manager)
                        logger.warning(
                            "Network error (Attempt %d): %s. "
                            "Retrying in %.2fs...",
                            attempt + 1,
                            e,
                            current_delay,
                        )

                    await asyncio.sleep(current_delay)
                    attempt += 1
                else:
                    sanitized_error = _sanitize_tts_error_message(str(e))
                    max_attempts = self._config_manager.get(
                        "retry_policies.network.max_attempts", 3)
                    logger.error(
                        f"Max retries exceeded for network error: {sanitized_error}"
                    )
                    raise RuntimeError(
                        f"TTS synthesis failed after {max_attempts} attempts: {sanitized_error}"
                    ) from e

            except Exception as e:
                # Check for NoAudioReceived error (Edge-TTS returns this for non-speakable content)
                try:
                    from edge_tts.exceptions import NoAudioReceived

                    if isinstance(e, NoAudioReceived):
                        # Check if this is expected behavior for non-speakable content
                        from speakub.utils.text_utils import is_speakable_content

                        speakable, reason = is_speakable_content(text)

                        if not speakable:
                            # This is expected - Edge-TTS correctly returns no audio for punctuation-only content
                            logger.debug(
                                f"No audio received for non-speakable content (reason: {reason}): '{text[:20]}...'"
                            )
                            return b""  # Return empty audio data, treat as successful
                        else:
                            # Unexpected NoAudioReceived for speakable content - this is an error
                            sanitized_error = _sanitize_tts_error_message(
                                str(e))
                            logger.error(
                                f"TTS synthesis failed: No audio received for speakable content: {sanitized_error}"
                            )
                            raise RuntimeError(
                                f"TTS synthesis failed: {sanitized_error}"
                            ) from e
                except ImportError:
                    # If edge_tts.exceptions is not available, continue with normal error handling
                    pass

                # Check for rate limiting (401 errors)
                error_str = str(e).lower()
                if "401" in error_str and "invalid response status" in error_str:
                    logger.warning("Rate limiting detected in Edge TTS API")
                    # Activate rate limiting protection
                    await self._activate_rate_limit_protection()
                    raise RuntimeError(
                        "Edge TTS service rate limit exceeded") from e

                # For non-network errors, don't retry
                sanitized_error = _sanitize_tts_error_message(str(e))
                logger.error(f"TTS synthesis error: {sanitized_error}")
                raise

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """
        Get list of available Edge TTS voices.
        """
        if not EDGE_TTS_AVAILABLE:
            return []

        if self._voices_cache is None:
            try:
                voices = await edge_tts.list_voices()
                self._voices_cache = []

                for voice in voices:
                    voice_info = {
                        "name": voice.get("Name", ""),
                        "short_name": voice.get("ShortName", ""),
                        "gender": voice.get("Gender", ""),
                        "locale": voice.get("Locale", ""),
                        "display_name": voice.get(
                            "DisplayName", voice.get("FriendlyName", "")
                        ),
                        "local_name": voice.get(
                            "LocalName", voice.get("ShortName", "")
                        ),
                        "style_list": voice.get("StyleList", []),
                        "sample_rate_hertz": voice.get("SampleRateHertz", 24000),
                        "voice_type": voice.get("VoiceType", "Neural"),
                    }
                    self._voices_cache.append(voice_info)

            except Exception as e:
                print(f"DEBUG: Failed to get voices: {e}")
                import traceback

                traceback.print_exc()
                self._report_error(f"Failed to get voices: {e}")
                return []

        return self._voices_cache or []

    def get_voices_by_language(self, language: str) -> List[Dict[str, Any]]:
        """
        Get voices for a specific language.
        """
        if not self._voices_cache:
            # Don't try to fetch voices synchronously in test environment
            # Just return empty list and let caller handle it
            return []

        return [
            voice
            for voice in (self._voices_cache or [])
            if voice["locale"].startswith(language)
        ]

    def set_voice(self, voice_name: str) -> bool:
        """
        Set the current voice.
        """
        if not voice_name:
            return False

        # Check if it's a valid voice name format (contains language-region-voice pattern)
        # or if it's in our default voices
        if voice_name in self.DEFAULT_VOICES.values():
            self._current_voice = voice_name
            logger.debug(f"Edge-TTS voice set to {voice_name}")

            # 💾 Save voice setting to configuration
            try:
                self._config_manager.set("edge-tts.voice", voice_name)
                logger.debug(f"Saved Edge-TTS voice {voice_name} to config")
            except Exception as e:
                logger.warning(f"Failed to save Edge-TTS voice to config: {e}")

            return True

        # Check for valid voice name pattern: xx-XX-Name format
        if (
            voice_name
            and len(voice_name.split("-")) >= 3
            and voice_name.endswith("Neural")
        ):
            # Basic validation: xx-XX-NameNeural format
            parts = voice_name.split("-")
            if len(parts) >= 3 and len(parts[0]) == 2 and len(parts[1]) == 2:
                self._current_voice = voice_name
                logger.debug(f"Edge-TTS voice set to {voice_name}")

                # 💾 Save voice setting to configuration
                try:
                    self._config_manager.set("edge-tts.voice", voice_name)
                    logger.debug(
                        f"Saved Edge-TTS voice {voice_name} to config")
                except Exception as e:
                    logger.warning(
                        f"Failed to save Edge-TTS voice to config: {e}")

                return True

        return False

    def get_current_voice(self) -> str:
        """Get the currently selected voice."""
        return self._current_voice

    def speak_text_sync(self, text: str, voice: str = "default", **kwargs) -> None:
        """
        同步朗讀文字，專門為非平滑模式優化。
        在非平滑模式下，直接合成然後同步播放，不使用複雜的狀態管理。
        """
        import asyncio

        # 確保事件循環存在
        self.start_async_loop()

        if self._async_manager.is_running():
            # 準備 Edge-TTS 特定的參數
            rate = kwargs.get(
                "rate", f"{int((self._tts_speed - 1.0) * 100):+}%")
            pitch = kwargs.get("pitch", self._tts_pitch)
            volume = kwargs.get(
                "volume", f"{int((self._tts_volume - 1.0) * 100):+}%")

            # 創建同步合成和播放的任務
            async def sync_synthesis_and_play():
                try:
                    # 直接合成音頻數據
                    audio_data = await self.synthesize(text, voice, rate=rate, pitch=pitch, volume=volume)

                    if audio_data:
                        # 直接使用同步播放，這樣可以確保在非平滑模式下正常工作
                        await asyncio.to_thread(
                            self.audio_backend.play,
                            audio_data,
                            speed=1.0,  # 不使用合成時的速度調整
                            volume=1.0,  # 不使用合成時的音量調整
                        )
                        # 清理音頻數據
                        self._cleanup_current_data()
                        logger.debug(
                            f"Successfully synthesized and played text in non-smooth mode: {len(audio_data)} bytes")
                    else:
                        logger.warning(
                            "No audio data generated for text in non-smooth mode")

                except Exception as e:
                    logger.error(f"Error in speak_text_sync: {e}")
                    raise

            # 在事件循環中執行同步任務（使用 TTSAsyncManager）
            try:
                self._async_manager.run_coroutine_threadsafe(
                    sync_synthesis_and_play(), timeout=60.0
                )
            except asyncio.TimeoutError:
                logger.error("speak_text_sync timed out after 60 seconds")
                raise TimeoutError("TTS sync playback timed out")
            except RuntimeError as e:
                # Async loop was closed/not running (e.g., during engine switch)
                logger.warning(
                    f"Async manager not available (engine switch?): {e}")
                raise TimeoutError("TTS async manager unavailable") from e
            except Exception as e:
                logger.error(f"Error in speak_text_sync execution: {e}")
                raise

    async def play_audio_non_blocking(self, audio_data: bytes) -> None:
        """
        Start playing audio data without blocking using AudioBackend.
        """
        # Update state: preparing to play
        # Update state through manager
        self._change_state(
            TTSState.LOADING if not self._is_paused else TTSState.PLAYING)

        # Store current audio data for pause/resume
        if not self._is_paused or audio_data:
            self._current_audio_data = audio_data

        # Update state and start playback
        self._change_state(TTSState.PLAYING)
        self._is_paused = False

        # Ensure we have audio data to play
        if self._current_audio_data is None:
            logger.error("No audio data available for playback")
            self._update_state(TTSState.ERROR)
            return

        # Start audio playback in background thread (since PygameBackend.play is synchronous)
        await asyncio.to_thread(
            self.audio_backend.play,
            self._current_audio_data,
            speed=1.0,  # Volume/speed already applied during synthesis
            volume=1.0,
        )

        # AudioBackend.play completes automatically, update state
        if not self._is_paused:
            self._cleanup_current_data()
            self._change_state(TTSState.IDLE)

    async def wait_for_playback_completion(self) -> None:
        """
        Wait for playback completion (AudioBackend.play is already synchronous).
        """
        # PygameBackend.play is synchronous and blocking, so nothing to wait for
        pass

    async def play_audio(self, audio_data: bytes) -> None:
        """
        Play audio data and wait for completion using AudioBackend.
        """
        # Update state: preparing to play
        self._change_state(TTSState.LOADING)

        # Start playback synchronously
        await asyncio.to_thread(
            self.audio_backend.play, audio_data, speed=1.0, volume=1.0
        )

        # Cleanup and update state
        self._cleanup_current_data()
        self._change_state(TTSState.IDLE)

    def _cleanup_current_file(self) -> None:
        """Clean up the current temporary file (for backward compatibility)."""
        self._cleanup_current_data()

    def _cleanup_current_data(self) -> None:
        """Clean up current audio data."""
        self._current_audio_data = None
        self._current_text = None

    def pause(self) -> None:
        """Pause audio playback using AudioBackend."""
        if self._transition_state(TTSState.PAUSED):
            self.audio_backend.pause()
            self._is_paused = True
            logger.debug("Playback paused via AudioBackend")

    def can_resume(self) -> bool:
        """Check if playback can be resumed."""
        try:
            return self.audio_backend.can_resume()
        except Exception:
            return False

    def resume(self) -> None:
        """Resume audio playback using AudioBackend."""
        if self.can_resume():
            if self._transition_state(TTSState.PLAYING):
                self.audio_backend.resume()
                self._is_paused = False
                logger.debug("Playback resumed via AudioBackend")

    def stop(self) -> None:
        """Stop audio playback and clean up data."""
        if self._transition_state(TTSState.STOPPED):
            self.audio_backend.stop()
            self._is_paused = False
            self._cleanup_current_data()
            logger.debug("Playback stopped via AudioBackend")

    def seek(self, position: int) -> None:
        """
        Seek to position in audio (not supported by current AudioBackend).
        """
        logger.warning("Seek not supported by pygame AudioBackend")

    def set_volume(self, volume: float) -> None:
        """
        Set TTS synthesis volume (used during synthesis, not playback).
        """
        # 從配置獲取限制
        volume_min = self._config_manager.get("edge-tts.volume_min", 0.0)
        volume_max = self._config_manager.get("edge-tts.volume_max", 1.5)

        # 儲存音量設定（使用配置中的限制）
        self._tts_volume = max(volume_min, min(volume_max, volume))
        logger.debug(
            f"Edge-TTS synthesis volume set to {self._tts_volume} "
            f"(range: {volume_min}-{volume_max})"
        )

        # 💾 保存到 Edge-TTS 專用配置
        try:
            self._config_manager.set("edge-tts.volume", self._tts_volume)
            logger.debug(f"Saved Edge-TTS volume {self._tts_volume} to config")
        except Exception as e:
            logger.warning(f"Failed to save Edge-TTS volume to config: {e}")

    def get_volume(self) -> float:
        """Get current TTS synthesis volume level."""
        return self._tts_volume

    def set_speed(self, speed: float) -> None:
        """
        Set TTS synthesis speed (used during synthesis, not playback).
        """
        # 從配置獲取限制
        speed_min = self._config_manager.get("edge-tts.speed_min", 0.5)
        speed_max = self._config_manager.get("edge-tts.speed_max", 3.0)

        # 儲存速度設定（使用配置中的限制）
        self._tts_speed = max(speed_min, min(speed_max, speed))
        logger.debug(
            f"Edge-TTS synthesis speed set to {self._tts_speed} "
            f"(range: {speed_min}-{speed_max})"
        )

        # 💾 保存到 Edge-TTS 專用配置
        try:
            self._config_manager.set(
                "edge-tts.playback_speed", self._tts_speed)
            logger.debug(f"Saved Edge-TTS speed {self._tts_speed} to config")
        except Exception as e:
            logger.warning(f"Failed to save Edge-TTS speed to config: {e}")

    def get_speed(self) -> float:
        """Get current TTS synthesis speed."""
        return self._tts_speed

    def set_pitch(self, pitch: str) -> None:
        """
        Set TTS synthesis pitch (used during synthesis, not playback).

        Args:
            pitch: Pitch value (e.g., "+10Hz", "-5Hz", "+0Hz")
        """
        # 驗證音調格式
        if not isinstance(pitch, str) or not pitch.endswith("Hz"):
            logger.warning(f"Invalid pitch format: {pitch}")
            return

        # 從配置獲取限制
        pitch_min = self._config_manager.get("edge-tts.pitch_min", -50)
        pitch_max = self._config_manager.get("edge-tts.pitch_max", 50)

        # 解析音調值
        try:
            val = int(pitch.replace("Hz", "").replace("+", ""))
            if pitch_min <= val <= pitch_max:
                self._tts_pitch = pitch
                logger.debug(
                    f"Edge-TTS synthesis pitch set to {self._tts_pitch} "
                    f"(range: {pitch_min}Hz-{pitch_max}Hz)"
                )

                # 💾 保存到 Edge-TTS 專用配置
                try:
                    self._config_manager.set("edge-tts.pitch", self._tts_pitch)
                    logger.debug(
                        f"Saved Edge-TTS pitch {self._tts_pitch} to config")
                except Exception as e:
                    logger.warning(
                        f"Failed to save Edge-TTS pitch to config: {e}")
            else:
                logger.warning(
                    f"Pitch value {val} out of range [{pitch_min}, {pitch_max}]"
                )
        except ValueError:
            logger.warning(f"Invalid pitch value: {pitch}")

    def _get_char_limit(self) -> int:
        """Get Edge-TTS-specific character limit for batching."""
        return 200

    def _get_batch_size_preference(self) -> int:
        """Get preferred batch size for Edge-TTS."""
        return 5  # Edge-TTS can handle larger batches

    def _supports_batch_merging(self) -> bool:
        """Edge-TTS does not support merging multiple texts into single API call."""
        return False

    def _needs_text_sanitization(self) -> bool:
        """Edge-TTS requires basic text sanitization."""
        return True

    def _get_rate_limit_cooldown(self) -> float:
        """Get rate limiting cooldown period for Edge-TTS."""
        return self._rate_limit_cooldown

    def get_pitch(self) -> str:
        """Get current TTS synthesis pitch."""
        return self._tts_pitch

    async def _activate_rate_limit_protection(self) -> None:
        """
        Activate rate limiting protection measures.
        Increases request cooldown and notifies playlist manager to reduce batch size.
        """
        if not self._rate_limiting_active:
            # Increase cooldown period to 2.5 seconds (between 2-3 seconds as specified)
            self._rate_limit_cooldown = 2.5
            self._rate_limiting_active = True

            logger.warning(
                f"Activating TTS rate limit protection: cooldown set to {self._rate_limit_cooldown}s"
            )

            # Notify playlist manager to reduce batch size
            # Emit event through event bus to trigger batch size reduction
            try:
                from speakub.utils.event_bus import event_bus

                await event_bus.publish(
                    "tts_rate_limiting_detected",
                    {
                        "action": "reduce_batch_size",
                        "cooldown_period": self._rate_limit_cooldown,
                    },
                )
                logger.debug(
                    "Published rate limiting event to playlist manager")
            except Exception as e:
                logger.warning(f"Failed to emit rate limiting event: {e}")

        else:
            logger.debug("Rate limiting protection already active")

    async def cleanup_resources(self) -> None:
        """
        Clean up all EdgeTTS engine resources.
        EdgeTTS primarily uses synchronous operations and pygame backend.
        """
        logger.debug("Cleaning up EdgeTTS engine resources")

        try:
            # Stop async loop if running
            self.stop_async_loop()

            # Clean up audio backend
            if hasattr(self, "audio_backend") and self.audio_backend:
                if hasattr(self.audio_backend, "cleanup"):
                    await asyncio.to_thread(self.audio_backend.cleanup)
                elif hasattr(self.audio_backend, "stop"):
                    self.audio_backend.stop()

            # Clean up current audio data
            if hasattr(self, "_cleanup_current_data"):
                self._cleanup_current_data()

            # Clear voices cache to free memory
            if hasattr(self, "_voices_cache"):
                self._voices_cache = None

            logger.debug("EdgeTTS engine resources cleaned up successfully")

        except Exception as e:
            logger.warning(f"Error during EdgeTTS cleanup: {e}")
            # Don't raise - cleanup should not fail the operation


def cleanup_orphaned_tts_files(max_age_hours: int = 24) -> int:
    """
    Clean up old TTS temporary files from system temp directory.
    This is a safety net for files that weren't cleaned up properly.

    Args:
        max_age_hours: Remove files older than this many hours
    """
    import contextlib
    import tempfile
    import time
    from pathlib import Path

    temp_dir = Path(tempfile.gettempdir())
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600

    cleaned_count = 0
    cleaned_size = 0

    try:
        # Look for temporary MP3 files (pattern used by NamedTemporaryFile)
        for filepath in temp_dir.glob("tmp*.mp3"):
            try:
                file_age = current_time - filepath.stat().st_mtime
                if file_age > max_age_seconds:
                    file_size = filepath.stat().st_size
                    with contextlib.suppress(Exception):
                        filepath.unlink()
                    cleaned_count += 1
                    cleaned_size += file_size
            except Exception as e:
                logger.debug(f"Failed to clean up {filepath}: {e}")

        if cleaned_count > 0:
            logger.info(
                f"Cleaned up {cleaned_count} old TTS temporary files "
                f"({cleaned_size / 1024:.1f} KB total)"
            )
    except Exception as e:
        logger.warning(f"Error during temporary file cleanup: {e}")

    return cleaned_count
