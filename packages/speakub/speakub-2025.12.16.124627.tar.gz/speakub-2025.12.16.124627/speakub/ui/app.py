#!/usr/bin/env python3
"""
Main SpeakUB Application - Textual UI
"""

# Re-add necessary imports that are actually used
import asyncio
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from bs4 import BeautifulSoup
from textual.app import App, ComposeResult, SystemCommand
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static, Tree

from speakub import TTS_AVAILABLE
from speakub.core.exceptions import ConfigurationException as ConfigurationError
from speakub.core.progress_tracker import ProgressTracker
from speakub.tts.integration import TTSIntegration
from speakub.ui.actions import SpeakUBActions
from speakub.ui.epub_manager import EPUBManager
from speakub.ui.panel_titles import PanelTitle
from speakub.ui.progress import ProgressManager
from speakub.ui.ui_utils import UIUtils
from speakub.ui.voice_selector_panel import VoiceSelectorPanel
from speakub.ui.widgets.content_widget import ContentDisplay, ViewportContent
from speakub.utils.config import ConfigManager
from speakub.utils.event_bus import SpeakUBEvents, event_bus
from speakub.utils.idle_detector import get_idle_detector, update_global_activity
from speakub.utils.notification_manager import NotificationManager

if TTS_AVAILABLE:
    try:
        from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
    except Exception:
        EdgeTTSProvider = None  # type: ignore
    try:
        from speakub.ui.widgets.tts_widget import TTSRichWidget  # type: ignore
    except Exception:
        TTSRichWidget = None  # type: ignore


logger = logging.getLogger(__name__)


class EPUBReaderApp(App):
    """Main SpeakUB Application using Textual UI.

    This class implements the AppInterface protocol.
    """

    CSS = """
    #app-container {
        layout: horizontal;
        height: 100%;
        width: 100%;
    }

    #main-app-column {
        layout: vertical;
        width: 100fr;
    }

    #voice-panel {
        width: 60;
        border-left: solid $accent;
        layout: vertical;
    }
    #voice-panel.hidden {
        display: none;
    }
    #voice-table {
        height: 1fr;
        margin: 1 0;
    }

    /* Voice selector panel layout fixes */
    #voice-panel-title {
        /* 讓標題只佔用必要的空間 */
        height: auto;
    }

    #engine-selector-top {
        /* 讓按鈕容器只佔用必要的空間 */
        height: auto;
        /* 可以稍微調整一下邊距讓它看起來更好 */
        padding: 0 1;
        margin-bottom: 0;
    }

    #btn-nanmai {
        margin-top: 0;
        margin-left: 1;
        margin-right: 1;
    }

    .main-container {
        layout: horizontal;
        height: 1fr;
    }

    .toc-panel {
        width: 24fr;
        border: solid $primary;
        padding: 0 0;
        margin: 0 0;
    }
    .content-panel {
        width: 76fr;
        border: solid $secondary;
        padding: 0 0;
        margin: 0 0;
    }
    #content-container { height: 100%; overflow: hidden; }
    #content-display { height: 100%; padding: 1; overflow: hidden; }
    .toc-panel.focused { border: solid $accent; }
    .content-panel.focused { border: solid $accent; }
    #voice-panel.focused { border-left: solid $warning; }



    #tts-footer {
        height: auto;
        min-height: 1;
        max-height: 3;
        padding: 0 1;
        margin: 0 0;
        background: $surface;
        border: solid $accent;
    }
    #tts-footer > #tts-status { text-align: left; width: 1fr; }
    #tts-footer > #tts-controls { text-align: center; width: 2fr; }
    #tts-footer > #tts-page { text-align: right; width: 1fr; }
    .panel-title { background: $boost; padding: 0 1; height: 1; }
    Tree { padding: 0 0; margin: 0 0; }
    Input { margin: 0 1; padding: 0 1; width: 6; }
    Static { margin: 0 1; padding: 0 1; }
    """

    BINDINGS = [
        Binding("q", "quit", "⏻"),
        Binding("tab", "switch_focus", "Switch Focus"),
        Binding("f1", "toggle_toc", "⇄ TOC"),
        Binding("f2", "toggle_tts", "⇄ TTS"),
        Binding("v", "toggle_voice_panel", "⇄ Voices"),
        Binding("m", "toggle_smooth_tts", "⇄ Smooth TTS"),
        Binding("space", "tts_play_pause", "▶ ❚❚ "),
        Binding("s", "tts_stop", "🚫 TTS"),
        Binding("+", "increase_volume", "🔊 "),
        Binding("=", "increase_volume", "Vol Up", show=False),
        Binding("-", "decrease_volume", "🔉 "),
        Binding("]", "increase_speed", "🗲 Up"),
        Binding("[", "decrease_speed", "🗲 Down"),
        Binding("p", "increase_pitch", "🎼 Up"),
        Binding("o", "decrease_pitch", "🎼 Down"),
        Binding("b", "add_bookmark", "🔖 Add Bookmark"),
        Binding("f3", "show_bookmarks", "📑 Bookmarks"),
        Binding("f4", "toggle_debug", "🐞 Debug"),
    ]

    # ... (rest of __init__ and compose methods remain unchanged) ...
    def __init__(
        self,
        epub_path: str,
        debug: bool = False,
        log_file: Optional[str] = None,
        fallback_viewport_height: int = 25,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.epub_path = epub_path
        self.log_file = log_file
        self._debug = bool(debug)
        self.fallback_viewport_height = fallback_viewport_height

        self.current_focus = "toc"
        self.toc_visible = True
        self.tts_visible = True
        self.toc_data: Optional[Dict] = None
        self.current_chapter: Optional[Dict] = None
        self.current_chapter_soup: Optional[BeautifulSoup] = None
        self.viewport_content: Optional[ViewportContent] = None
        self.current_viewport_height = fallback_viewport_height
        self._widgets_ready = False

        # Refactored to use private attributes with properties to match AppInterface
        self._tts_engine: Optional["EdgeTTSProvider"] = None
        self.tts_widget: Optional["TTSRichWidget"] = None
        self._tts_status: str = "STOPPED"
        self.now_reading_text = "..."

        # Load TTS configuration from centralized config
        try:
            config_mgr = ConfigManager()
            tts_config = config_mgr.get("tts", {})
            self.tts_rate = tts_config["rate"]
            self.tts_volume = tts_config["volume"]
            self.tts_pitch = tts_config["pitch"]
            self.tts_smooth_mode = tts_config["smooth_mode"]
            logger.debug(f"TTS configuration loaded: {tts_config}")
        except (ConfigurationError, KeyError) as e:
            logger.warning(f"Failed to load TTS config, using defaults: {e}")
            # Fallback to default values
            self.tts_rate = 0
            self.tts_volume = 100
            self.tts_pitch = "+0Hz"
            self.tts_smooth_mode = False
        except Exception:
            # Include traceback
            logger.exception("Unexpected error loading TTS config")
            raise  # Re-raise unexpected errors

        self.config_manager = ConfigManager()  # ConfigManager instance holder
        self.actions = SpeakUBActions(self, self.config_manager)
        self.epub_manager = EPUBManager(self, self.config_manager)
        self.progress_manager = ProgressManager(
            self, self._update_tts_progress)
        self.tts_integration = TTSIntegration(self, self.config_manager)
        self.ui_utils = UIUtils(self)
        self.progress_tracker: Optional[ProgressTracker] = None
        self.chapter_manager = None
        self.notification_manager = NotificationManager(self)

        # After component initialization, reconfigure logging based on CLI debug parameter
        if self._debug:
            from speakub.utils.logging_config import set_debug_mode

            set_debug_mode(True)

        # Initialize idle detector integration
        self._idle_detector = get_idle_detector()
        self._idle_detector.add_idle_callback(self._on_idle_mode_changed)

        # Thread ID for thread-safe operations
        import threading

        self._thread_id = threading.get_ident()

    # --- Start: Property implementations for AppInterface ---
    @property
    def tts_engine(self) -> Optional["EdgeTTSProvider"]:
        return self._tts_engine

    @tts_engine.setter
    def tts_engine(self, value: Optional["EdgeTTSProvider"]) -> None:
        self._tts_engine = value

    @property
    def tts_status(self) -> str:
        return self._tts_status

    @tts_status.setter
    def tts_status(self, value: str) -> None:
        # Optional: Add validation here in the future
        old_status = self._tts_status
        self._tts_status = value
        # Publish event if status changed
        if old_status != value:
            event_bus.publish_sync(
                SpeakUBEvents.TTS_STATE_CHANGED,
                {"old_status": old_status, "new_status": value},
            )

    def set_tts_status(self, status: str) -> None:
        """Thread-safe method to set TTS status from background threads."""
        import threading

        if self._thread_id == threading.get_ident():
            # We're already on the main thread, set directly
            self.tts_status = status
        else:
            # We're on a background thread, use call_from_thread
            def update_status():
                self.tts_status = status

            self.call_from_thread(update_status)

    # --- End: Property implementations for AppInterface ---

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Horizontal(id="app-container"):
            with Vertical(id="main-app-column"):
                yield Header(show_clock=False, id="main-header")

                with Horizontal(classes="main-container"):
                    with Vertical(classes="toc-panel", id="toc-panel"):
                        yield PanelTitle(
                            "Table of Contents",
                            classes="panel-title",
                            id="toc-panel-title",
                        )
                        yield Tree("Loading...", id="toc-tree")

                    with Vertical(classes="content-panel", id="content-panel"):
                        yield PanelTitle(
                            "Chapter Content",
                            classes="panel-title",
                            id="content-panel-title",
                        )
                        with Container(id="content-container"):
                            yield ContentDisplay(
                                "Select a chapter to begin reading...",
                                id="content-display",
                            )

                with Horizontal(id="tts-footer"):
                    yield Static("TTS: IDLE", id="tts-status")
                    yield Static(
                        "-- | Vol: 70% | Speed: 0% | Pitch: +0Hz",
                        id="tts-controls",
                    )
                    yield Static("", id="tts-page")

                yield Footer()

            yield VoiceSelectorPanel(id="voice-panel", classes="hidden")

    async def on_mount(self) -> None:
        logger.debug("on_mount started")

        # Configure asyncio logging to reduce noise during shutdown
        # Suppress "Task was destroyed but it is pending" warnings unless in debug mode
        if not self._debug:
            asyncio_logger = logging.getLogger("asyncio")
            asyncio_logger.setLevel(logging.WARNING)
            # Suppress the specific "Task was destroyed" message
            asyncio_logger.addFilter(
                lambda record: "Task was destroyed but it is pending"
                not in record.getMessage()
            )

        # Clean up orphaned temporary files on startup
        if TTS_AVAILABLE:
            try:
                from speakub.tts.engines.edge_tts_provider import cleanup_orphaned_tts_files

                cleaned = cleanup_orphaned_tts_files(max_age_hours=24)
                if cleaned > 0:
                    logger.info(
                        f"Startup cleanup: removed {cleaned} orphaned TTS files"
                    )
            except Exception as e:
                logger.warning(f"Startup cleanup failed: {e}")

        content_display = self.query_one("#content-display", ContentDisplay)
        content_display.app_ref = self
        content_display.can_focus = True
        self._widgets_ready = True
        self.set_timer(0.1, self._delayed_viewport_calculation)
        await self.tts_integration.setup_tts()
        await self.epub_manager.load_epub()
        await self.progress_manager.start_progress_tracking()
        self.ui_utils.update_panel_focus()

        # Start intelligent notification system
        self.notification_manager.start_monitoring()

        # CPU optimization: idle mode detection is now handled by centralized IdleDetector

        # Start consolidated monitoring system - single source of truth
        await self._start_consolidated_monitoring()

        # Debug: Log current TTS engine and voice configuration
        from speakub.utils.config import get_current_tts_config_summary

        logger.debug(f"App Debug: {get_current_tts_config_summary()}")

        # Set initial header debug indicator based on startup debug state
        self._update_header_debug_indicator()

        logger.debug("on_mount finished")

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Provide system commands to the command palette."""
        yield from super().get_system_commands(screen)

        yield SystemCommand(
            "Toggle Voice Panel",
            "Show/hide the TTS voice selector",
            self.action_toggle_voice_panel,
        )

    async def _populate_voice_list(self) -> None:
        """Fetch TTS voice list, filter, and populate the voice selector panel."""
        logger = logging.getLogger(__name__)

        # Debug: Check TTS engine status
        logger.debug(f"TTS engine available: {self.tts_engine is not None}")
        if self.tts_engine:
            logger.debug(f"TTS engine type: {type(self.tts_engine)}")
            logger.debug(
                f"TTS engine has get_available_voices: {hasattr(self.tts_engine, 'get_available_voices')}"
            )

        if self.tts_engine and hasattr(self.tts_engine, "get_available_voices"):
            try:
                logger.debug("Fetching voices from TTS engine...")
                voices = await self.tts_engine.get_available_voices()
                logger.debug(
                    f"Retrieved {len(voices) if voices else 0} voices")

                voice_panel = self.query_one(VoiceSelectorPanel)

                if voices:
                    # Check current engine type to determine filtering
                    from speakub.utils.config import ConfigManager

                    config_mgr = ConfigManager()
                    current_engine = config_mgr.get(
                        "tts.preferred_engine", "edge-tts")
                    logger.debug(f"Current engine: {current_engine}")

                    current_voice = self.tts_engine.get_current_voice()
                    logger.debug(f"Current voice: {current_voice}")

                    if current_engine == "gtts":
                        # gTTS: show all available voices (pre-defined)
                        logger.debug("Updating voices for gTTS")
                        voice_panel.update_voices(voices, current_voice)
                    else:
                        # Edge-TTS: filter for female Chinese voices
                        from speakub.utils.voice_filter_utils import (
                            filter_female_chinese_voices,
                        )

                        female_chinese_voices = filter_female_chinese_voices(
                            voices)
                        logger.debug(
                            f"Filtered to {len(female_chinese_voices) if female_chinese_voices else 0} female Chinese voices"
                        )

                        # --- Key modification: Get current voice and pass to panel ---
                        if female_chinese_voices:
                            voice_panel.update_voices(
                                female_chinese_voices, current_voice
                            )
                        else:
                            self.notify(
                                "No female Chinese voices found. Displaying all available voices.",
                                severity="warning",
                            )
                            voice_panel.update_voices(voices, current_voice)
                else:
                    logger.warning("No voices returned from TTS engine")
                    self.notify("No TTS voices found.", severity="warning")
            except Exception as e:
                logger.error(f"Error fetching voices: {e}")
                self.notify(f"Error fetching voices: {e}", severity="error")
        else:
            logger.error(
                "TTS engine not available or doesn't have get_available_voices method"
            )
            self.notify("TTS engine not ready. Please try again.",
                        severity="warning")

    # ... (all other methods remain unchanged) ...
    def action_toggle_voice_panel(self) -> None:
        """Toggles the visibility of the voice selector panel."""
        voice_panel = self.query_one(VoiceSelectorPanel)
        panel_is_visible = not voice_panel.has_class("hidden")

        if panel_is_visible:
            # Hide voice panel
            voice_panel.add_class("hidden")
            self.query_one("#main-app-column").styles.width = "100fr"
            self.query_one("#content-display").focus()
        else:
            # Show voice panel
            self.run_worker(self._populate_voice_list, exclusive=True)
            self.query_one("#main-app-column").styles.width = "1fr"
            voice_panel.remove_class("hidden")
            voice_panel.focus()

    def _delayed_viewport_calculation(self) -> None:
        """Calculate viewport height and trigger re-pagination if viewport_content exists."""
        import logging

        logger = logging.getLogger(__name__)

        old_height = self.current_viewport_height
        new_height = self.ui_utils.calculate_viewport_height()

        # Update the app's viewport height
        self.current_viewport_height = new_height

        logger.debug(
            f"Delayed viewport calculation: height {old_height} -> {new_height}"
        )

        # If we have an existing viewport_content, trigger re-pagination with the new height
        if self.viewport_content and new_height != old_height:
            logger.debug(
                "Triggering re-pagination due to delayed viewport calculation")
            # Use update_dimensions to handle the height change properly
            layout_changed = self.viewport_content.update_dimensions(
                self.ui_utils.calculate_content_width(), new_height
            )
            if layout_changed:
                self.ui_utils.update_content_display()
                logger.debug("Content display updated after re-pagination")

    def on_resize(self, event) -> None:
        # Only start debounce timer when widgets are ready and have content
        if self._widgets_ready and self.viewport_content:
            self.set_timer(0.3, self._handle_resize)

    async def _handle_resize(self) -> None:
        """
        [Final Fix Version] Actual resize processing logic after debounce delay.
        """
        logger.debug(
            f"🔄 _handle_resize called - widgets_ready: {self._widgets_ready}, viewport_content: {self.viewport_content is not None}"
        )

        if not self._widgets_ready or not self.viewport_content:
            logger.debug(
                "❌ _handle_resize skipped - widgets not ready or no viewport_content"
            )
            return

        # Step 1: Only calculate new dimensions, do not perform any operations
        new_height = self.ui_utils.calculate_viewport_height()
        new_width = self.ui_utils.calculate_content_width()

        logger.debug(
            f"📏 Calculated dimensions - width: {new_width}, height: {new_height}"
        )

        # Step 2: Pass new dimensions to ViewportContent all at once
        old_pages = self.viewport_content.total_pages
        layout_changed = self.viewport_content.update_dimensions(
            new_width, new_height)

        logger.debug(
            f"🔄 update_dimensions result - layout_changed: {layout_changed}, pages: {old_pages} -> {self.viewport_content.total_pages}"
        )

        # Step 3: Update app-level state (if needed)
        self.current_viewport_height = new_height

        # Step 4: Trigger UI refresh
        self.ui_utils.update_content_display()

        # Step 5: Force update TTS page display regardless of layout_changed
        # Because page calculation may have issues, ensure display is correct
        await self.tts_integration.update_tts_progress()

        logger.debug(
            f"✅ _handle_resize completed - final pages: {self.viewport_content.total_pages}"
        )

        if layout_changed:
            self.notify("Layout updated.", timeout=1)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        if event.node.data:
            self.run_worker(self.epub_manager.load_chapter(event.node.data))

    def on_voice_selector_panel_voice_selected(
        self, message: VoiceSelectorPanel.VoiceSelected
    ) -> None:
        """Handles the voice selected event from the panel."""
        # Check current engine type to determine which engine to set voice on
        from speakub.utils.config import ConfigManager

        config_mgr = ConfigManager()
        current_engine = config_mgr.get("tts.preferred_engine", "edge-tts")

        success = False
        if current_engine == "gtts":
            # For gTTS, use the existing engine instance if it's GTTSProvider
            try:
                from speakub.tts.engines.gtts_provider import GTTSProvider

                if isinstance(self.tts_engine, GTTSProvider):
                    # Use the actual running engine instance
                    success = self.tts_engine.set_voice(
                        message.voice_short_name)
                else:
                    # Fallback: create a temporary provider to set the voice (for config update)
                    gtts_provider = GTTSProvider()
                    success = gtts_provider.set_voice(message.voice_short_name)

                if success:
                    # Update the configuration with the selected voice
                    config_mgr.set_override(
                        "gtts.default_voice", message.voice_short_name
                    )
            except Exception as e:
                self.notify(f"Failed to set gTTS voice: {e}", severity="error")
                return
        elif current_engine == "nanmai":
            # For Nanmai TTS, use the existing engine instance if it's NanmaiTTSProvider
            try:
                from speakub.tts.engines.nanmai_tts_provider import NanmaiTTSProvider

                if isinstance(self.tts_engine, NanmaiTTSProvider):
                    # Use the actual running engine instance
                    success = self.tts_engine.set_voice(
                        message.voice_short_name)
                else:
                    # Fallback: create a temporary provider to set the voice (for config update)
                    nanmai_provider = NanmaiTTSProvider()
                    success = nanmai_provider.set_voice(
                        message.voice_short_name)

                if success:
                    # Update the configuration with the selected voice
                    config_mgr.set_override(
                        "nanmai.default_voice", message.voice_short_name
                    )
            except Exception as e:
                self.notify(
                    f"Failed to set Nanmai voice: {e}", severity="error")
                return
        else:
            # For Edge-TTS, use the existing engine
            if self.tts_engine and hasattr(self.tts_engine, "set_voice"):
                success = self.tts_engine.set_voice(message.voice_short_name)
                if success:
                    # Update the configuration with the selected voice
                    config_mgr.set_override(
                        "edge-tts.voice", message.voice_short_name)
                    config_mgr.save_to_file()

        if success:
            self.notify(f"TTS voice set to: {message.voice_short_name}")
            self.action_toggle_voice_panel()
        else:
            self.notify(
                f"Failed to set voice: {message.voice_short_name}", severity="error"
            )

    def action_quit(self) -> None:
        """Quit the application."""
        self.actions.action_quit()

    def action_switch_focus(self) -> None:
        """Switch focus between panels."""
        self.actions.action_switch_focus()

    def action_toggle_smooth_tts(self) -> None:
        """Toggle smooth TTS mode."""
        self.actions.action_toggle_smooth_tts()

    def action_toggle_toc(self) -> None:
        """Toggle table of contents visibility."""
        self.actions.action_toggle_toc()

    def action_toggle_tts(self) -> None:
        """Toggle TTS functionality."""
        self.actions.action_toggle_tts()

    def action_increase_volume(self) -> None:
        self.actions.action_increase_volume()

    def action_decrease_volume(self) -> None:
        self.actions.action_decrease_volume()

    def action_increase_speed(self) -> None:
        self.actions.action_increase_speed()

    def action_decrease_speed(self) -> None:
        self.actions.action_decrease_speed()

    def action_increase_pitch(self) -> None:
        self.actions.action_increase_pitch()

    def action_decrease_pitch(self) -> None:
        self.actions.action_decrease_pitch()

    def action_content_up(self) -> None:
        self.actions.action_content_up()

    def action_content_down(self) -> None:
        self.actions.action_content_down()

    def action_content_page_up(self) -> None:
        self.actions.action_content_page_up()

    def action_content_page_down(self) -> None:
        self.actions.action_content_page_down()

    def action_content_home(self) -> None:
        self.actions.action_content_home()

    def action_content_end(self) -> None:
        self.actions.action_content_end()

    def action_tts_play_pause(self) -> None:
        self.actions.action_tts_play_pause()

    def action_tts_stop(self) -> None:
        self.actions.action_tts_stop()

    def action_add_bookmark(self) -> None:
        self.actions.action_add_bookmark()

    def action_show_bookmarks(self) -> None:
        self.actions.action_show_bookmarks()

    def _update_header_debug_indicator(self) -> None:
        """Update the app title to show debug mode indicator."""
        if self._debug:
            self.title = "SpeakUB 🐞 DEBUG MODE ON"
        else:
            self.title = "SpeakUB"

    def action_toggle_debug(self) -> None:
        """Dynamically toggle Debug mode"""
        # 1. Toggle state
        self._debug = not self._debug

        # [🔥 Added repair code]
        # If Debug is enabled and no log file exists, create one dynamically
        if self._debug and not self.log_file:
            self._setup_dynamic_log_file()
        # [Repair end]

        # 2. Determine new level
        new_level = logging.DEBUG if self._debug else logging.WARNING

        # 3. Set Root Logger
        root_logger = logging.getLogger()
        root_logger.setLevel(new_level)

        # 4. Synchronize all Handlers (including screen and file)
        for handler in root_logger.handlers:
            handler.setLevel(new_level)

        # 5. Update trace properties of internal components
        self._update_components_trace_state(self._debug)

        # 6. Update persistent visual indicator
        self._update_header_debug_indicator()

        # 7. UI notification
        state_text = "ON" if self._debug else "OFF"
        severity = "warning" if self._debug else "information"

        msg = f"Debug Mode: {state_text}"
        if self._debug and self.log_file:
            msg += f"\nLogging to: {os.path.basename(self.log_file)}"

        self.notify(msg, title="System Status", severity=severity, timeout=3)
        logger.info(f"Debug mode toggled to {state_text}")

    def _setup_dynamic_log_file(self) -> None:
        """Create a log file dynamically when user enables Debug mode and no log file exists"""
        try:
            log_dir = Path.home() / ".local/share/speakub/logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file_path = log_dir / f"speakub-dynamic-{ts}.log"

            file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
            file_handler.setFormatter(formatter)

            root_logger = logging.getLogger()
            root_logger.addHandler(file_handler)

            # Update app's log_file attribute for UI display
            self.log_file = str(log_file_path)
            logger.info(f"Dynamic log file created at: {self.log_file}")

        except Exception as e:
            self.notify(f"Failed to create log file: {e}", severity="error")
            logger.exception("Failed to create dynamic log file")

    def _update_components_trace_state(self, trace_enabled: bool) -> None:
        """Synchronize Debug state to underlying processing units"""
        # Update EPUB Manager related components
        if hasattr(self, "epub_manager") and self.epub_manager:
            if self.epub_manager.epub_parser:
                self.epub_manager.epub_parser.trace = trace_enabled
            if self.epub_manager.content_renderer:
                self.epub_manager.content_renderer.trace = trace_enabled
            if self.epub_manager.chapter_manager:
                self.epub_manager.chapter_manager.trace = trace_enabled
            if self.epub_manager.progress_tracker:
                self.epub_manager.progress_tracker.trace = trace_enabled

        # Update current Viewport
        if self.viewport_content and hasattr(self.viewport_content, "_renderer"):
            self.viewport_content._renderer.trace = trace_enabled

    def _setup_granular_debug_logging(self) -> None:
        """
        Set up granular Debug logging, filter UI noise but keep detailed core logic messages.
        Includes Textual framework filtering because Textual internal events are very numerous.
        """
        # Define log levels for each module (hierarchical filtering)
        logging_config = {
            # --- 🤫 Quiet Area (INFO/WARNING) ---
            # Project UI components (reduce rendering loop noise)
            "speakub.ui.widgets": logging.INFO,
            "speakub.ui.voice_selector_panel": logging.INFO,
            "speakub.ui.progress": logging.INFO,
            "speakub.ui.ui_utils": logging.INFO,
            "speakub.ui.actions": logging.INFO,
            # Textual framework (its DEBUG messages are very numerous and unimportant)
            "textual": logging.WARNING,
            # Third-party libraries
            "asyncio": logging.WARNING,  # Asyncio loops
            "gtts": logging.WARNING,
            "urllib3": logging.WARNING,
            "multipart": logging.WARNING,
            # --- 🗣️ Detailed Area (DEBUG) ---
            # Core business logic
            "speakub.core": logging.DEBUG,
            # TTS engines and scheduling (most important debug information)
            "speakub.tts": logging.DEBUG,
            # Resource and performance monitoring
            "speakub.utils.resource_monitor": logging.DEBUG,
            "speakub.utils.performance_monitor": logging.DEBUG,
            # App main controller
            "speakub.ui.app": logging.DEBUG,
        }

        # Apply configuration
        for logger_name, level in logging_config.items():
            logging.getLogger(logger_name).setLevel(level)

        logger.info("Granular debug logging enabled: UI=INFO, Core=DEBUG")

    def _reset_logging_levels(self) -> None:
        """
        Reset all project-related loggers to NOTSET, making them automatically inherit Root Logger (WARNING) settings.
        Uses Python logging inheritance mechanism, which is more flexible than hardcoding.
        """
        # Namespace prefixes that need to be reset
        prefixes_to_reset = ["speakub", "textual",
                             "asyncio", "gtts", "urllib3"]

        # Traverse all registered loggers
        loggers = [logging.getLogger(name)
                   for name in logging.root.manager.loggerDict]

        for lg in loggers:
            # If it's a logger we care about, reset it to NOTSET (inherit parent settings)
            if any(lg.name.startswith(prefix) for prefix in prefixes_to_reset):
                lg.setLevel(logging.NOTSET)

        logger.info(
            "Reset logging levels to production defaults (Inherit from Root=WARNING)"
        )

    def stop_speaking(self, is_pause: bool = False):
        self.tts_integration.stop_speaking(is_pause)

    def _get_line_from_cfi(self, cfi: str) -> int:
        return self.progress_manager.get_line_from_cfi(cfi)

    def _get_cfi_from_line(self, line_num: int) -> str:
        return self.progress_manager.get_cfi_from_line(line_num)

    def _save_progress(self) -> None:
        self.progress_manager.save_progress()

    def _update_user_activity(self) -> None:
        """Update last user activity timestamp and exit idle mode if active."""
        update_global_activity()
        self.progress_manager._update_user_activity()

    def _on_idle_mode_changed(self, idle_active: bool) -> None:
        """Handle idle mode changes from centralized idle detector."""
        logger.debug(f"App idle mode changed: {idle_active}")
        # The idle detector now handles all notifications automatically

    def _update_panel_focus(self) -> None:
        self.ui_utils.update_panel_focus()

    def _update_panel_titles(self) -> None:
        self.ui_utils.update_panel_titles()

    def _update_content_display(self) -> None:
        self.ui_utils.update_content_display()

    def _calculate_content_width(self) -> int:
        return self.ui_utils.calculate_content_width()

    async def _update_toc_tree(self, toc_data: dict) -> None:
        await self.ui_utils.update_toc_tree(toc_data)

    async def _update_tts_progress(self) -> None:
        await self.tts_integration.update_tts_progress()

    async def _setup_tts(self) -> None:
        await self.tts_integration.setup_tts()

    def _prepare_tts_playlist(self):
        self.tts_integration.prepare_tts_playlist()

    def _start_tts_thread(self):
        self.tts_integration.start_tts_thread()

    def _speak_with_engine(self, text: str) -> None:
        self.tts_integration.speak_with_engine(text)

    def _find_next_chapter(self) -> Optional[dict]:
        return self.actions.find_next_chapter()

    def _find_prev_chapter(self) -> Optional[dict]:
        return self.actions.find_prev_chapter()

    async def _start_consolidated_monitoring(self) -> None:
        """Start consolidated monitoring system - single source of truth."""
        try:
            # CPU Optimization: Consolidated monitoring system replaces multiple independent monitors
            from speakub.utils.file_utils import get_resource_manager
            from speakub.utils.resource_monitor import (
                NetworkMonitorAdapter,
                PerformanceMonitorAdapter,
                ResourceManagerAdapter,
                get_unified_resource_monitor,
            )

            # Get unified monitor instance (singleton)
            unified_monitor = get_unified_resource_monitor()

            # Add ResourceManager adapter (file/temp management)
            rm = get_resource_manager()
            rm_adapter = ResourceManagerAdapter(rm)
            unified_monitor.add_monitor(rm_adapter)

            # Add PerformanceMonitor adapter (CPU/memory monitoring)
            try:
                from speakub.utils.performance_monitor import get_performance_monitor

                pm = get_performance_monitor()
                pm_adapter = PerformanceMonitorAdapter(pm)
                unified_monitor.add_monitor(pm_adapter)

                # Connect idle mode to performance monitor
                self._connect_idle_to_performance_monitor(pm)
                pm.start_monitoring()

                logger.debug(
                    "PerformanceMonitor integrated into consolidated monitoring"
                )
            except Exception as e:
                logger.debug(f"PerformanceMonitor not available: {e}")

            # Note: NetworkMonitor was removed in Reservoir v6.0
            # Water level control now handles network issues automatically
            logger.debug("NetworkMonitor not used in Reservoir v6.0")

            # Start unified monitoring with optimized interval
            # CPU Optimization: Reduced from 60s to 30s for better responsiveness
            await unified_monitor.start_monitoring(interval_seconds=30)

            # Consolidated alert handler
            def consolidated_alert_handler(alert_type: str, alert_data: dict) -> None:
                """Handle all resource alerts through unified system."""
                if alert_type == "CRITICAL_MEMORY":
                    self.notify(
                        f"Critical memory usage: {alert_data.get('memory_mb', 'N/A')}MB. "
                        "Consider restarting the application.",
                        title="Memory Critical",
                        severity="error",
                    )
                elif alert_type == "WARNING_MEMORY":
                    logger.debug(
                        f"High memory: {alert_data.get('memory_mb', 'N/A')}MB")
                elif alert_type == "TEMP_FILES_HIGH":
                    logger.warning(
                        f"High temp files: {alert_data.get('temp_files_count', 0)}"
                    )
                elif alert_type == "HIGH_CPU":
                    logger.debug(f"High CPU usage detected")
                elif alert_type == "NETWORK_ISSUES":
                    logger.debug(f"Network issues detected")

            unified_monitor.add_alert_callback(consolidated_alert_handler)

            # Store reference for cleanup
            self._unified_resource_monitor = unified_monitor

            # Register deferred idle mode callbacks for reservoir controller
            if hasattr(self, "tts_integration") and self.tts_integration:
                if (
                    hasattr(self.tts_integration, "playlist_manager")
                    and self.tts_integration.playlist_manager
                ):
                    pm = self.tts_integration.playlist_manager
                    if (
                        hasattr(pm, "predictive_controller")
                        and pm.predictive_controller
                    ):
                        try:
                            pm.predictive_controller.register_idle_mode_callback()
                            logger.debug(
                                "Reservoir controller idle mode callback registered"
                            )
                        except Exception as e:
                            logger.debug(
                                f"Failed to register reservoir idle mode callback: {e}"
                            )

            logger.info(
                "Consolidated monitoring system initialized - single source of truth"
            )

        except Exception as e:
            logger.warning(
                f"Failed to initialize consolidated monitoring: {e}")

    def _connect_idle_to_performance_monitor(self, performance_monitor) -> None:
        """Connect idle mode detection to performance monitor."""
        self._performance_monitor = performance_monitor

    def _cleanup(self) -> None:
        """Clean up application resources with comprehensive asyncio task cancellation."""
        try:
            # Clean up components in reverse order of initialization
            self.tts_integration.cleanup()
            self.progress_manager.cleanup()
            self.epub_manager.close_epub()

            # Final event loop cleanup after component cleanup
            self._cleanup_event_loop()

        except Exception as e:
            # Handle any cleanup errors gracefully
            logger.warning(f"Error during application cleanup: {e}")

    def _cleanup_event_loop(self) -> None:
        """Clean up SpeakUB asyncio tasks, avoiding Textual framework tasks."""
        try:
            # Get current event loop
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running loop, try to get the event loop
                loop = asyncio.get_event_loop()

            if loop and not loop.is_closed():
                # Only cancel tasks that are explicitly created by SpeakUB components,
                # not Textual framework timers or other internal tasks
                speakub_tasks = []

                # Collect tasks from our tracked task sets (if they still exist)
                if hasattr(self, "tts_integration") and self.tts_integration:
                    # Tasks tracked by TTSIntegration
                    for task in self.tts_integration._tts_active_tasks:
                        if not task.done() and not task.cancelled():
                            speakub_tasks.append(task)

                # Also collect tasks from playlist manager if available
                if hasattr(self, "tts_integration") and self.tts_integration:
                    if (
                        hasattr(self.tts_integration, "playlist_manager")
                        and self.tts_integration.playlist_manager
                    ):
                        pm = self.tts_integration.playlist_manager
                        # Collect preload tasks
                        speakub_tasks.extend(
                            [
                                t
                                for t in pm._preload_tasks
                                if not t.done() and not t.cancelled()
                            ]
                        )
                        # Collect batch preload task
                        if (
                            pm._batch_preload_task
                            and not pm._batch_preload_task.done()
                            and not pm._batch_preload_task.cancelled()
                        ):
                            speakub_tasks.append(pm._batch_preload_task)
                        # Collect synthesis tasks
                        speakub_tasks.extend(
                            [
                                t
                                for t in pm._synthesis_tasks
                                if not t.done() and not t.cancelled()
                            ]
                        )

                # Collect progress save timer
                if hasattr(self, "progress_manager") and self.progress_manager:
                    if (
                        hasattr(self.progress_manager, "_progress_save_timer")
                        and self.progress_manager._progress_save_timer
                    ):
                        if (
                            not self.progress_manager._progress_save_timer.done()
                            and not self.progress_manager._progress_save_timer.cancelled()
                        ):
                            speakub_tasks.append(
                                self.progress_manager._progress_save_timer
                            )

                if speakub_tasks:
                    logger.debug(
                        f"Cancelling {len(speakub_tasks)} SpeakUB asyncio tasks during shutdown"
                    )

                    # Cancel SpeakUB tasks
                    for task in speakub_tasks:
                        try:
                            task.cancel()
                        except Exception as e:
                            logger.debug(
                                f"Error cancelling SpeakUB task {task}: {e}")

                    # Don't wait for cancellation completion as Textual handles its own cleanup
                    # Just log any issues for debugging
                    if self._debug:
                        remaining = [
                            t
                            for t in speakub_tasks
                            if not t.done() and not t.cancelled()
                        ]
                        if remaining:
                            logger.debug(
                                f"Some SpeakUB tasks may not have cancelled: {len(remaining)}"
                            )

        except Exception as cleanup_error:
            logger.debug(
                f"Error during SpeakUB event loop cleanup: {cleanup_error}")
