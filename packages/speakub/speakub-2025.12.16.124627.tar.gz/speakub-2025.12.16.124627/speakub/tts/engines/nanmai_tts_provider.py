#!/usr/bin/env python3
"""
NanmaiTTS Provider - 納米AI TTS implementation for SpeakUB.
Updated to use asyncio-based MPV backend with modern threading.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

try:
    import aiohttp

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from pydub import AudioSegment

    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

from speakub.tts.backends import get_audio_backend
from speakub.tts.engine import TTSEngine, TTSError, TTSState
from speakub.utils.config import ConfigManager

logger = logging.getLogger(__name__)


class NanmaiTTSProvider(TTSEngine):
    """Nanmai AI TTS provider with bitrate adjustment support."""

    # Available voices
    AVAILABLE_VOICES = [
        {
            "name": "DeepSeek",
            "short_name": "DeepSeek",
            "gender": "Male",
            "locale": "zh-CN",
            "display_name": "DeepSeek",
            "local_name": "DeepSeek",
        },
        {
            "name": "Kimi",
            "short_name": "Kimi",
            "gender": "Female",
            "locale": "zh-CN",
            "display_name": "Kimi",
            "local_name": "Kimi",
        },
    ]

    def __init__(self, config_manager=None):
        """Initialize Nanmai TTS provider with modern asyncio backend."""
        super().__init__()
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests package not installed. Install with: pip install requests"
            )

        # Dependency injection
        if config_manager is not None:
            self._config_manager = config_manager
        else:
            from speakub.utils.config import ConfigManager

            self._config_manager = ConfigManager()

        # Initialize modern audio backend
        self.audio_backend = get_audio_backend("mpv")

        # Load configuration with Nanmai-specific defaults
        self._current_volume = self._config_manager.get("nanmai.volume", 1.0)
        self._current_speed = self._config_manager.get(
            "nanmai.playback_speed", 0.8  # Nanmai default 0.8x
        )
        self._current_voice = self._config_manager.get(
            "nanmai.default_voice", "DeepSeek"
        )

        # Nanmai-specific settings
        self.bitrate = self._config_manager.get("nanmai.bitrate", "64k")

        # Sync settings to backend
        self.audio_backend.set_volume(self._current_volume)
        self.audio_backend.set_speed(self._current_speed)

        # State tracking for backward compatibility (delegate to state manager)
        self._is_paused = False
        self._current_audio_file = None

        # Nanmai-specific memory monitoring
        self._memory_cleanup_threshold = 150.0
        self._play_count_since_last_cleanup = 0
        self._cleanup_interval = 50  # Increased from 10 to 50, reduce frequent GC

        # Session management for connection reuse and performance optimization
        # Aiohttp: Use async ClientSession instead of requests.Session
        self._aiohttp_session: Optional[aiohttp.ClientSession] = None
        # Fallback: Keep requests session for backward compatibility
        self._session = None
        self._session_creation_time = None
        self._session_timeout = 300  # 5 minutes session timeout

        # Cache available voices
        self._voices_cache = self.AVAILABLE_VOICES.copy()

        logger.debug(
            f"NanmaiTTS initialized with voice: {self._current_voice}, "
            f"volume: {self._current_volume}, speed: {self._current_speed}, "
            f"bitrate: {self.bitrate}"
        )

    def _convert_fullwidth_to_halfwidth(self, text: str) -> str:
        """
        Convert full-width ASCII characters to half-width equivalents.

        NanmaiTTS-specific: The API doesn't support full-width characters,
        so we convert them to standard ASCII before sending to the API.
        """
        result = []
        for char in text:
            code = ord(char)
            # Full-width ASCII range: U+FF01 to U+FF5E (punctuation and letters)
            # Full-width space: U+3000
            if 0xFF01 <= code <= 0xFF5E:
                # Convert to half-width by subtracting 0xFEE0
                halfwidth_code = code - 0xFEE0
                result.append(chr(halfwidth_code))
            elif code == 0x3000:  # Full-width space
                result.append(" ")
            else:
                result.append(char)
        return "".join(result)

    async def synthesize(self, text: str, voice: str = "default", **kwargs) -> bytes:
        """
        Synthesize text using Nanmai AI TTS.
        Supports bitrate adjustment for file size optimization.
        """
        if not REQUESTS_AVAILABLE:
            raise RuntimeError("Requests not available")

        # Validate and sanitize TTS text input
        from speakub.utils.security import TextSanitizer

        try:
            TextSanitizer.validate_tts_text(text)
            text = TextSanitizer.sanitize_tts_text(text)
            # NanmaiTTS-specific: Convert full-width characters to half-width
            text = self._convert_fullwidth_to_halfwidth(text)
        except ValueError as e:
            logger.error(f"TTS text validation failed: {e}")
            raise

        if not text or not text.strip():
            logger.warning("Empty text after sanitization")
            return b""

        if voice == "default":
            voice = self._current_voice

        # Add delay before API call to prevent rate limiting
        # Keep at 1.0s to avoid server-side blocking with high intensity usage
        await asyncio.sleep(1.0)

        # Call Nanmai AI API (always MP3 format for best compatibility)
        audio_data = await self._call_nanmai_api(text, voice)

        # Apply bitrate adjustment based on configuration
        enable_transcoding = self._config_manager.get(
            "nanmai.enable_ffmpeg_transcoding", True
        )
        if enable_transcoding and self.bitrate and self.bitrate != "original":
            audio_data = self._adjust_bitrate_sync(audio_data, self.bitrate)

        return audio_data

    def _get_session(self) -> requests.Session:
        """Get or create a reusable requests session with timeout management."""
        import time

        current_time = time.time()

        # Create new session if none exists or if timeout exceeded
        if (
            self._session is None
            or self._session_creation_time is None
            or current_time - self._session_creation_time > self._session_timeout
        ):
            if self._session is not None:
                logger.debug("Closing expired session for renewal")
                self._session.close()

            self._session = requests.Session()
            self._session_creation_time = current_time

            # Configure session defaults for security and performance
            self._session.max_redirects = 0  # Security: no redirects
            self._session.verify = True  # SSL verification

            logger.debug("Created new requests session for Nanmai API")

        return self._session

    async def _get_aiohttp_session(self) -> aiohttp.ClientSession:
        """
        [Aiohttp] Get or create a reusable async ClientSession.
        Uses lazy initialization since sessions cannot be created in __init__.
        """
        if self._aiohttp_session is None or self._aiohttp_session.closed:
            # Configure session with proper timeouts and limits
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=10,  # Limit concurrent connections
                limit_per_host=5,  # Limit per host
                ttl_dns_cache=300,  # DNS cache TTL
            )

            self._aiohttp_session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                trust_env=True,  # Allow system proxy settings
            )

            logger.debug("Created new aiohttp ClientSession for Nanmai API")

        return self._aiohttp_session

    def _sync_post_request(self, session, url, headers, data, timeout):
        """Synchronously executed request function, ensure using with statement to release resources immediately"""
        # Use with to ensure connection is released back to pool after request ends
        with session.post(url, headers=headers, data=data, timeout=timeout) as response:
            self._validate_response(response)  # validate
            # Read content to memory immediately, so response object can be destroyed
            content = response.content
            return content

    async def _call_nanmai_api_aiohttp(
        self, text: str, voice: str, audio_type: str = "mp3"
    ) -> bytes:
        """
        [Aiohttp] Call Nanmai AI TTS API using fully async HTTP client.
        Supports proper cancellation and resource management.
        """
        # Validate voice parameter to prevent injection
        if not voice or not isinstance(voice, str) or len(voice.strip()) == 0:
            raise ValueError("Invalid voice parameter")

        # Construct URL safely - voice is validated to be alphanumeric
        safe_voice = voice.strip()
        url = f"https://bot.n.cn/api/tts/v1?roleid={safe_voice}"

        # Prepare data with validation
        data = aiohttp.FormData()
        data.add_field("text", text)  # Already sanitized by TextSanitizer
        data.add_field("audio_type", audio_type)
        data.add_field("format", "stream")

        # Get headers (contains authorization tokens)
        headers = self._get_headers()

        logger.debug(
            f"[Aiohttp] Calling Nanmai AI API: voice={safe_voice}, "
            f"text_length={len(text)}, timeout=30s"
        )

        # Get async session
        session = await self._get_aiohttp_session()

        try:
            # Make async request - this can be cancelled by asyncio.cancel()!
            async with session.post(url, data=data, headers=headers) as response:
                # Handle HTTP errors
                if response.status != 200:
                    error_text = await response.text()
                    raise RuntimeError(
                        f"Nanmai API Error {response.status}: {error_text}"
                    )

                # Read response content
                content = await response.read()

                # Check response size for DoS protection
                if len(content) > 50 * 1024 * 1024:  # 50MB limit
                    logger.error(f"Response too large: {len(content)} bytes")
                    raise RuntimeError("API response too large")

                # Validate content type
                content_type = response.headers.get("content-type", "").lower()
                if not content_type.startswith("audio/") and "mp3" not in content_type:
                    logger.warning(f"Unexpected content type: {content_type}")

                logger.debug(
                    f"[Aiohttp] Response received: {len(content)} bytes")
                return content

        except asyncio.CancelledError:
            logger.info("[Aiohttp] Request cancelled by user")
            raise  # Re-raise to allow proper cancellation handling
        except aiohttp.ClientError as e:
            logger.error(f"[Aiohttp] Network error: {e}")
            raise RuntimeError(f"Network connection failed: {e}") from e
        except Exception as e:
            logger.error(f"[Aiohttp] API call failed: {e}")
            raise RuntimeError(f"Nanmai AI TTS synthesis failed: {e}") from e

    async def _call_nanmai_api(
        self, text: str, voice: str, audio_type: str = "mp3"
    ) -> bytes:
        """
        Call Nanmai AI TTS API with fallback support.
        Uses aiohttp when available, falls back to requests.
        """
        # Prefer aiohttp for better cancellation support
        if AIOHTTP_AVAILABLE:
            try:
                return await self._call_nanmai_api_aiohttp(text, voice, audio_type)
            except Exception as e:
                logger.warning(
                    f"Aiohttp request failed, falling back to requests: {e}")
                # Fall through to requests implementation

        # Fallback to requests implementation
        try:
            # Validate voice parameter to prevent injection
            if not voice or not isinstance(voice, str) or len(voice.strip()) == 0:
                raise ValueError("Invalid voice parameter")

            # Construct URL safely - voice is validated to be alphanumeric
            # Voice parameter is limited to predefined values (DeepSeek, Kimi)
            safe_voice = voice.strip()
            url = f"https://bot.n.cn/api/tts/v1?roleid={safe_voice}"

            # Prepare data with validation
            data = {
                "text": text,  # Already sanitized by TextSanitizer
                "audio_type": audio_type,
                "format": "stream",
            }

            # Get headers (contains authorization tokens)
            headers = self._get_headers()

            logger.debug(
                f"[Requests] Calling Nanmai AI API: voice={safe_voice}, "
                f"text_length={len(text)}, timeout=30s"
            )

            # Get reusable session for connection pooling
            session = self._get_session()

            # Make request with enhanced timeout and retry logic
            try:
                response_content = await asyncio.to_thread(
                    self._sync_post_request,
                    session,
                    url,
                    headers,
                    data,
                    (10, 30),  # (connect timeout, read timeout)
                )
            except requests.exceptions.Timeout:
                logger.warning("[Requests] API timeout (30s), retrying...")
                # Single retry with shorter timeout using same session
                response_content = await asyncio.to_thread(
                    self._sync_post_request,
                    session,
                    url,
                    headers,
                    data,
                    (5, 15),  # Shorter timeout for retry
                )

            # Check response size for DoS protection
            if len(response_content) > 50 * 1024 * 1024:  # 50MB limit
                logger.error(
                    f"Response too large: {len(response_content)} bytes")
                raise RuntimeError("API response too large")

            logger.debug(
                f"[Requests] Response received: {len(response_content)} bytes")
            return response_content

        except requests.exceptions.SSLError as e:
            logger.error(f"[Requests] SSL certificate validation failed: {e}")
            raise RuntimeError("SSL certificate validation failed") from e
        except requests.exceptions.ConnectionError as e:
            logger.error(f"[Requests] Network connection failed: {e}")
            raise RuntimeError("Network connection failed") from e
        except requests.exceptions.Timeout as e:
            logger.error(f"[Requests] Request timeout: {e}")
            raise RuntimeError("Request timeout after retry") from e
        except Exception as e:
            logger.error(f"[Requests] API call failed: {e}")
            raise RuntimeError(f"Nanmai AI TTS synthesis failed: {e}") from e

    def _validate_response(self, response) -> None:
        """Validate API response for security."""
        response.raise_for_status()  # Check HTTP status

        # Check Content-Type for expected audio format (MP3 only)
        content_type = response.headers.get("content-type", "").lower()
        if not content_type.startswith("audio/") and "mp3" not in content_type:
            logger.warning(f"Unexpected content type: {content_type}")

        # Check content length
        content_length = response.headers.get("content-length")
        if content_length and int(content_length) != len(response.content):
            logger.warning("Content-Length mismatch")

    def _get_headers(self) -> dict:
        """Generate API headers (replicated from test script)."""
        # This is a simplified version - in production, you'd want to
        # cache these or use a more robust token generation
        import hashlib
        import random
        import time
        from datetime import datetime

        UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

        def _e(nt: str) -> int:
            HASH_MASK_1 = 268435455
            HASH_MASK_2 = 266338304
            at = 0
            for st in reversed(nt):
                st = ord(st)
                at = (at << 6 & HASH_MASK_1) + st + (st << 14)
                it = at & HASH_MASK_2
                if it != 0:
                    at ^= it >> 21
            return at

        def generate_mid() -> str:
            def generate_unique_hash():
                nt = f"chrome1.0zh-CNWin32{UA}1920x108024https://bot.n.cn/chat"
                at = len(nt)
                it = 1
                while it:
                    nt += chr(it ^ at)
                    it -= 1
                    at += 1
                return (round(random.random() * 2147483647) ^ _e(nt)) * 2147483647

            return f"{_e('https://bot.n.cn')}{generate_unique_hash()}{time.time() + random.random() + random.random()}".replace(
                ".", "e"
            )[
                :32
            ]

        def get_iso8601_time() -> str:
            return datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00")

        device = "Web"
        ver = "1.2"
        time_str = get_iso8601_time()
        access_token = generate_mid()
        zm_ua = hashlib.md5(UA.encode("utf-8")).hexdigest()

        return {
            "device-platform": device,
            "timestamp": time_str,
            "access-token": access_token,
            "zm-token": hashlib.md5(
                f"{device}{time_str}{ver}{access_token}{zm_ua}".encode()
            ).hexdigest(),
            "zm-ver": ver,
            "zm-ua": zm_ua,
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def _adjust_bitrate_sync(self, audio_data: bytes, bitrate: str) -> bytes:
        """Synchronously adjust audio bitrate using pydub with managed temp files."""
        if bitrate == "original" or not PYDUB_AVAILABLE:
            if bitrate != "original":
                logger.warning(
                    "pydub not available, skipping bitrate adjustment")
            return audio_data

        # Use managed temp files for safe automatic cleanup
        from speakub.utils.file_utils import get_resource_manager

        resource_manager = get_resource_manager()

        try:
            # Always MP3 format since API returns MP3
            input_format = "mp3"
            output_format = "mp3"

            # Create temporary files for processing using managed context
            with resource_manager.managed_temp_file(
                suffix=f".{input_format}"
            ) as tmp_in_path:
                with open(tmp_in_path, "wb") as f:
                    f.write(audio_data)

                with resource_manager.managed_temp_file(
                    suffix=f".{output_format}"
                ) as tmp_out_path:
                    # Load MP3 and export with adjusted bitrate
                    # Suppress ffmpeg output to prevent screen flooding in debug mode
                    audio = AudioSegment.from_mp3(
                        tmp_in_path, parameters=["-loglevel", "quiet"]
                    )

                    audio.export(
                        tmp_out_path,
                        format=output_format,
                        bitrate=bitrate,
                        parameters=["-loglevel", "quiet"],
                    )

                    # Read back the converted audio
                    with open(tmp_out_path, "rb") as f:
                        converted_data = f.read()

                    logger.debug(
                        f"Bitrate adjusted to {bitrate}, original: {len(audio_data)} bytes, converted: {len(converted_data)} bytes"
                    )

                    # Explicitly delete audio object to free memory
                    del audio
                    return converted_data

        except Exception as e:
            logger.warning(
                f"Bitrate adjustment failed: {e}, returning original audio")
            return audio_data

    async def get_available_voices(self) -> List[Dict[str, Any]]:
        """Get list of available Nanmai TTS voices."""
        return self._voices_cache.copy()

    def set_voice(self, voice_name: str) -> bool:
        """Set the current voice."""
        if not voice_name:
            return False

        valid_voices = [v["short_name"] for v in self.AVAILABLE_VOICES]
        if voice_name in valid_voices:
            self._current_voice = voice_name
            return True
        return False

    def get_current_voice(self) -> str:
        """Get the currently selected voice."""
        return self._current_voice

    def set_bitrate(self, bitrate: str) -> None:
        """Set the bitrate for audio compression with validation."""
        valid_bitrates = [
            "original",
            "32k",
            "48k",
            "64k",
            "96k",
            "128k",
            "192k",
            "256k",
            "320k",
        ]
        if bitrate in valid_bitrates:
            self.bitrate = bitrate
            self._config_manager.set("nanmai.bitrate", self.bitrate)
            logger.debug(f"Bitrate set to: {bitrate}")
        else:
            logger.warning(
                f"Invalid bitrate: {bitrate}, keeping current: {self.bitrate}"
            )

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
        """Wait for current playback to complete."""
        pass  # AudioBackend.play is already blocking

    async def play_audio(self, audio_data: bytes) -> None:
        """Play audio data using modern asyncio backend with memory management."""
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

            # Changed to use memory threshold to trigger cleanup, instead of fixed count
            # Only trigger GC when memory exceeds 80% of warning value
            import psutil

            process = psutil.Process()
            mem_mb = process.memory_info().rss / 1024 / 1024

            memory_warning_threshold = self._config_manager.get(
                "nanmai.memory_warning_threshold_mb", 400
            )

            if mem_mb > memory_warning_threshold * 0.8:
                logger.debug(
                    f"Memory usage {mem_mb:.1f}MB > {memory_warning_threshold * 0.8:.1f}MB "
                    f"({memory_warning_threshold}MB * 0.8), triggering cleanup"
                )
                self._perform_memory_cleanup()
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
        """Seek not supported by NanmaiTTS."""
        logger.warning("Seek operation not supported by NanmaiTTS provider")

    # ===== MODERN CONFIGURATION METHODS =====

    def _get_volume_limits(self) -> tuple[float, float]:
        """Get Nanmai-specific volume limits."""
        return self._config_manager.get(
            "nanmai.volume_min", 0.0
        ), self._config_manager.get("nanmai.volume_max", 1.5)

    def _get_speed_limits(self) -> tuple[float, float]:
        """Get Nanmai-specific speed limits."""
        return self._config_manager.get(
            "nanmai.speed_min", 0.5
        ), self._config_manager.get("nanmai.speed_max", 3.0)

    def set_volume(self, volume: float) -> None:
        """Set playback volume with configuration limits."""
        volume_min, volume_max = self._get_volume_limits()
        self._current_volume = max(volume_min, min(volume_max, volume))
        logger.debug(
            f"NanmaiTTS volume set to {self._current_volume} "
            f"(range: {volume_min}-{volume_max})"
        )

        try:
            self.audio_backend.set_volume(self._current_volume)
            self._config_manager.set("nanmai.volume", self._current_volume)
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
            f"NanmaiTTS speed set to {self._current_speed} "
            f"(range: {speed_min}-{speed_max})"
        )

        try:
            self.audio_backend.set_speed(self._current_speed)
            self._config_manager.set(
                "nanmai.playback_speed", self._current_speed)
            logger.debug("Speed saved to config")
        except Exception as e:
            logger.warning(f"Failed to update speed: {e}")

    def get_speed(self) -> float:
        """Get current speed level."""
        try:
            return self.audio_backend.get_speed()
        except Exception:
            return self._current_speed

    def set_pitch(self, pitch: str) -> None:
        """Set TTS pitch (not supported by Nanmai AI)."""
        logger.warning("Nanmai AI TTS does not support pitch adjustment")

    def _get_char_limit(self) -> int:
        """Get Nanmai-specific character limit for batching."""
        return 150

    def _get_batch_size_preference(self) -> int:
        """Get preferred batch size for Nanmai."""
        return 3  # Nanmai prefers smaller batches

    def _supports_batch_merging(self) -> bool:
        """
        Nanmai API supports merging, BUT we disable it to ensure TUI cursor synchronization.
        If set to True, the TUI cannot highlight text sentence-by-sentence.
        """
        return False

    def _needs_text_sanitization(self) -> bool:
        """Nanmai requires text sanitization (full-width to half-width conversion)."""
        return True

    def _get_rate_limit_cooldown(self) -> float:
        """Get rate limiting cooldown period for Nanmai."""
        return 1.0  # 1 second delay between requests

    def get_pitch(self) -> str:
        """Get current TTS pitch (always default)."""
        return "+0Hz"

    def get_current_state(self) -> str:
        """Get current TTS state for debugging."""
        return self._state_manager.state.value

    def _perform_memory_cleanup(self) -> None:
        """Perform memory cleanup operations."""
        try:
            # Reset play count
            self._play_count_since_last_cleanup = 0

            # Force garbage collection
            import gc

            collected_objects = gc.collect()

            logger.debug(
                f"NanmaiTTS memory cleanup completed: {collected_objects} objects collected"
            )
        except Exception as e:
            logger.warning(f"Memory cleanup failed: {e}")

    async def cleanup_resources(self) -> None:
        """Clean up all NanmaiTTS engine resources."""
        logger.debug("Cleaning up NanmaiTTS engine resources")

        try:
            # Stop async loop if running
            self.stop_async_loop()

            # Clean up audio backend
            if hasattr(self, "audio_backend") and self.audio_backend:
                if hasattr(self.audio_backend, "cleanup"):
                    await asyncio.to_thread(self.audio_backend.cleanup)
                elif hasattr(self.audio_backend, "stop"):
                    self.audio_backend.stop()

            # Close aiohttp session first (async operation)
            if hasattr(self, "_aiohttp_session") and self._aiohttp_session is not None:
                try:
                    if not self._aiohttp_session.closed:
                        await self._aiohttp_session.close()
                    self._aiohttp_session = None
                    logger.debug("Aiohttp session closed during cleanup")
                except Exception as e:
                    logger.warning(f"Error closing aiohttp session: {e}")

            # Close requests session to free connections
            if hasattr(self, "_session") and self._session is not None:
                try:
                    self._session.close()
                    self._session = None
                    self._session_creation_time = None
                    logger.debug("Requests session closed during cleanup")
                except Exception as e:
                    logger.warning(f"Error closing requests session: {e}")

            # Force garbage collection
            import gc

            collected = gc.collect()

            # Reset internal state
            self._play_count_since_last_cleanup = 0
            self._current_audio_file = None

            logger.debug(
                f"NanmaiTTS cleanup completed: {collected} objects collected")

        except Exception as e:
            logger.warning(f"Error during NanmaiTTS cleanup: {e}")
            # Don't raise - cleanup should not fail the operation
