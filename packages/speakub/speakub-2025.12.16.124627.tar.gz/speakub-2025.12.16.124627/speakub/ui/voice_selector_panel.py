import asyncio
import logging
from typing import Any, Dict, List

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.message import Message
from textual.widgets import Button, DataTable, Static

from speakub.tts import TTSEngineManager

# TTS availability checks
try:
    import edge_tts  # noqa: F401

    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False

try:
    from gtts import gTTS  # noqa: F401

    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import requests  # noqa: F401

    NANMAI_AVAILABLE = True
except ImportError:
    NANMAI_AVAILABLE = False


class VoiceSelectorPanel(Vertical):
    """A side panel for selecting TTS voices."""

    class VoiceSelected(Message):
        """Sent when a voice is selected."""

        def __init__(self, voice_short_name: str) -> None:
            self.voice_short_name = voice_short_name
            super().__init__()

    def compose(self) -> ComposeResult:
        """Compose the voice selector panel components."""
        yield Static(
            "TTS Voice Selection", classes="panel-title", id="voice-panel-title"
        )

        # Add engine selector buttons
        with Horizontal(id="engine-selector-top"):
            yield Button("Edge-TTS", id="btn-edge-tts", variant="primary")
            yield Button("gTTS", id="btn-gtts")

        yield Button("Nanmai", id="btn-nanmai")

        yield DataTable(id="voice-table", cursor_type="row")

    def on_mount(self) -> None:
        """Set up the table columns."""
        table = self.query_one(DataTable)
        table.add_columns("Voice Name")

        # Initialize filter state
        self._filter_enabled = True

        # Initialize voice cache for preloaded voice lists
        self._voice_cache: Dict[str, List[Dict[str, Any]]] = {}
        self._cache_lock = asyncio.Lock()

        # Initialize TTS Engine Manager
        self.engine_manager = TTSEngineManager()

    # --- Key modification 1: Add current_voice_short_name parameter ---
    def update_voices(
        self, voices: List[Dict[str, Any]], current_voice_short_name: str
    ) -> None:
        """Populate the table with available voices and mark the current voice."""
        table = self.query_one(DataTable)
        table.clear()

        sorted_voices = sorted(voices, key=lambda v: v.get("short_name", ""))

        for voice in sorted_voices:
            short_name = voice.get("short_name", "N/A")

            # --- Key modification 2: Check if it's the current voice and add marker ---
            display_text = ""
            if short_name == current_voice_short_name:
                # If it's the current voice, add marker at the front
                display_text = f"☛ {short_name}"
            else:
                # Otherwise, add spaces to maintain alignment
                display_text = f"  {short_name}"

            # key still uses original short_name
            table.add_row(display_text, key=short_name)

    async def on_button_pressed(self, event) -> None:
        """Handle engine selection button press."""
        if event.button.id == "btn-edge-tts":
            self._switch_engine("edge-tts")
        elif event.button.id == "btn-gtts":
            self._switch_engine("gtts")
        elif event.button.id == "btn-nanmai":
            self._switch_engine("nanmai")

    def _switch_engine(self, engine: str) -> None:
        """Switch TTS engine and update UI."""
        # Check TTS status and handle smooth mode
        if hasattr(self.app, "tts_status") and self.app.tts_status in [
            "PLAYING",
            "PAUSED",
        ]:
            # Display warning and stop playback
            self.app.notify(
                "Switching engine will stop current playback", severity="warning"
            )
            # Automatically stop playback to avoid inconsistencies
            if hasattr(self.app, "tts_integration"):
                self.app.tts_integration.stop_speaking(is_pause=False)

        # Check if engine supports Smooth mode
        engine_supports_smooth = engine in [
            "edge-tts",
            "nanmai",
        ]  # gTTS does not support Smooth mode
        if (
            not engine_supports_smooth
            and hasattr(self.app, "tts_smooth_mode")
            and self.app.tts_smooth_mode
        ):
            # Disable Smooth mode when switching to unsupported engine
            self.app.tts_smooth_mode = False
            # Save config
            from speakub.utils.config import ConfigManager

            config_mgr = ConfigManager()
            config_mgr.set_override("tts.smooth_mode", False)
            config_mgr.save_to_file()
            self.app.notify(
                "Smooth mode disabled (not supported by this engine)",
                severity="information",
            )

        # Update button styles
        edge_btn = self.query_one("#btn-edge-tts", Button)
        gtts_btn = self.query_one("#btn-gtts", Button)
        nanmai_btn = self.query_one("#btn-nanmai", Button)

        if engine == "edge-tts":
            edge_btn.variant = "primary"
            gtts_btn.variant = "default"
            nanmai_btn.variant = "default"
        elif engine == "gtts":
            edge_btn.variant = "default"
            gtts_btn.variant = "primary"
            nanmai_btn.variant = "default"
        elif engine == "nanmai":
            edge_btn.variant = "default"
            gtts_btn.variant = "default"
            nanmai_btn.variant = "primary"

        # Use engine manager to switch engine
        if hasattr(self.app, "tts_integration"):
            import asyncio

            old_engine = getattr(self.app, "tts_engine", None)
            asyncio.create_task(self._switch_engine_async(engine, old_engine))

    async def _switch_engine_async(self, engine: str, old_engine=None) -> None:
        """Asynchronously switch TTS engine."""
        try:
            success = await self.engine_manager.switch_engine(
                engine, tts_integration=self.app.tts_integration, old_engine=old_engine
            )
            if success:
                # Update voices for the new engine
                await self._update_voices_for_engine(engine)
                self.app.notify(
                    f"Switched to {engine.upper()} engine", severity="information"
                )
            else:
                self.app.notify("Failed to switch engine", severity="error")
        except Exception as e:
            self.app.notify(f"Failed to switch engine: {e}", severity="error")

    async def _update_voices_for_engine(self, engine: str) -> None:
        """Update voices list for the specified engine with preloaded voice lists."""
        logger = logging.getLogger(__name__)
        try:
            voices = None
            current_voice = None

            async with self._cache_lock:
                # Check if voices are cached for this engine
                if engine in self._voice_cache:
                    voices = self._voice_cache[engine]
                    logger.debug(f"Using cached voices for {engine}")
                else:
                    # Fetch voices and cache them
                    if hasattr(self.app, "tts_engine") and self.app.tts_engine:
                        voices = await self.app.tts_engine.get_available_voices()
                        # Cache the voices for future use
                        self._voice_cache[engine] = voices
                        logger.debug(f"Cached voices for {engine}")
                    else:
                        self.app.notify("No TTS engine available", severity="warning")
                        return

            if voices is not None:
                # Get current voice
                if hasattr(self.app, "tts_engine") and self.app.tts_engine:
                    current_voice = self.app.tts_engine.get_current_voice()

                # Apply filter if enabled and for Edge-TTS
                if self._filter_enabled and engine == "edge-tts":
                    from speakub.utils.voice_filter_utils import (
                        filter_female_chinese_voices,
                    )

                    voices = filter_female_chinese_voices(voices)

                # Update the voice table
                self.update_voices(voices, current_voice)
            else:
                self.app.notify("No voices available", severity="warning")

        except Exception as e:
            logger.error(f"Error updating voices for {engine}: {e}")
            self.app.notify(f"Error updating voices: {e}", severity="error")

    async def preload_voice_lists(self) -> None:
        """Preload voice lists for all engines asynchronously."""
        logger = logging.getLogger(__name__)
        engines = ["edge-tts", "gtts", "nanmai"]

        for engine in engines:
            try:
                # Create a temporary engine instance to fetch voices
                # This is done in background to avoid blocking UI
                if engine == "edge-tts" and TTS_AVAILABLE:
                    from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider

                    temp_engine = EdgeTTSProvider()
                elif engine == "gtts" and GTTS_AVAILABLE:
                    from speakub.tts.engines.gtts_provider import GTTSProvider

                    temp_engine = GTTSProvider()
                elif engine == "nanmai" and NANMAI_AVAILABLE:
                    from speakub.tts.engines.nanmai_tts_provider import NanmaiTTSProvider

                    temp_engine = NanmaiTTSProvider()
                else:
                    continue

                # Fetch and cache voices
                voices = await temp_engine.get_available_voices()
                async with self._cache_lock:
                    self._voice_cache[engine] = voices
                logger.debug(f"Preloaded voices for {engine}")

                # Clean up temporary engine
                if hasattr(temp_engine, "stop_async_loop"):
                    temp_engine.stop_async_loop()

            except Exception as e:
                logger.warning(f"Failed to preload voices for {engine}: {e}")

    async def on_data_table_row_selected(self, event) -> None:
        """Handle voice selection event."""
        if event.row_key.value:
            self.post_message(self.VoiceSelected(event.row_key.value))
