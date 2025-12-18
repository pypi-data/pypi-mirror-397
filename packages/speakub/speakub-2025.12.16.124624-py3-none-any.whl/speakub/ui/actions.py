#!/usr/bin/env python3
# Action handlers for SpeakUB Application

import logging
from typing import TYPE_CHECKING, Optional

from speakub.utils.config import ConfigManager, save_tts_config

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from speakub.ui.app import EPUBReaderApp


class SpeakUBActions:
    """Handles user actions for the SpeakUB application."""

    def __init__(self, app: "EPUBReaderApp", config_manager: ConfigManager):
        self.app = app
        self.config_manager = config_manager

    def _save_tts_config(self) -> None:
        """Save current TTS configuration to config file."""
        try:
            from speakub.utils.config import get_tts_config

            # Load existing TTS config to preserve advanced settings
            tts_config = get_tts_config()
            # Update only the UI-controlled settings
            tts_config.update(
                {
                    "rate": self.app.tts_rate,
                    "volume": self.app.tts_volume,
                    "pitch": self.app.tts_pitch,
                    "smooth_mode": self.app.tts_smooth_mode,
                }
            )
            save_tts_config(tts_config)
        except Exception as e:
            self.app.notify(
                f"Failed to save TTS config: {e}", severity="warning")

    def action_quit(self) -> None:
        """Quit the application."""
        # Stop TTS first if it's playing (like pressing 's' then 'q')
        if self.app.tts_status in ["PLAYING", "PAUSED"]:
            logger.info("Stopping TTS before exit...")
            self.app.stop_speaking(is_pause=False)

        self.app._save_progress()
        self.app._cleanup()
        self.app.exit()

    def action_switch_focus(self) -> None:
        """Switch focus between panels."""
        self.app._update_user_activity()
        focus_order = ["toc", "content"]
        idx = (focus_order.index(self.app.current_focus) + 1) % len(focus_order)
        self.app.current_focus = focus_order[idx]
        self.app._update_panel_focus()

    def action_toggle_smooth_tts(self) -> None:
        """Toggle smooth TTS mode."""
        self.app._update_user_activity()

        # ⭐ Check engine type - Use injected config manager
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            self.app.notify(
                "Smooth mode is not available for gTTS engine", severity="warning"
            )
            return

        # Original Edge-TTS smooth mode logic
        if self.app.tts_status != "STOPPED":
            self.app.stop_speaking()
        self.app.tts_smooth_mode = not self.app.tts_smooth_mode
        self._save_tts_config()
        self.app.notify(
            f"Smooth TTS Mode: {'ON' if self.app.tts_smooth_mode else 'OFF'}"
        )

    def action_toggle_toc(self) -> None:
        """Toggle table of contents visibility."""
        self.app._update_user_activity()
        self.app.toc_visible = not self.app.toc_visible
        self.app.query_one("#toc-panel").display = self.app.toc_visible

    def action_toggle_tts(self) -> None:
        """Toggle TTS panel visibility."""
        self.app._update_user_activity()
        self.app.tts_visible = not self.app.tts_visible
        self.app.query_one("#tts-footer").display = self.app.tts_visible

    # This is the actions.py code where engine.set_volume() is called

    def _adjust_engine_property(self, property_name: str, delta: float) -> None:
        """
        Adjust engine property with automatic limit handling.
        Uses background thread for MPV-based engines to prevent UI stuttering.
        """
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts")

        # 1. Calculate target value (universal logic, unchanged)
        new_val = 0.0

        # Prefer getting current value from App state
        if property_name == "volume":
            current_val = self.app.tts_volume / 100.0
        elif property_name == "speed":
            current_val = 1.0 + (self.app.tts_rate / 100.0)
        else:
            return

        # Get limits - use simple defaults to avoid config type issues
        if property_name == "volume":
            prop_min, prop_max = 0.0, 1.5
        elif property_name == "speed":
            prop_min, prop_max = 0.5, 3.0
        else:
            prop_min, prop_max = 0.0, 2.0

        # Calculate new value with clamping
        new_val = max(prop_min, min(prop_max, current_val + delta))

        # 2. Optimistic UI update (eyes see numbers change immediately)
        if property_name == "volume":
            self.app.tts_volume = int(new_val * 100)
        elif property_name == "speed":
            self.app.tts_rate = int((new_val - 1.0) * 100)

        logger.debug(
            f"UI {property_name} updated: {current_val:.1f} -> {new_val:.1f}")

        # Trigger immediate UI refresh
        self.app.call_next(self.app._update_tts_progress)

        # 3. Apply to engine (divided processing)
        if not self.app.tts_engine:
            return

        if current_engine == "edge-tts" or current_engine not in ("nanmai", "gtts"):
            # Edge-TTS route: sync execution (Pygame is fast, no change)
            try:
                getattr(self.app.tts_engine, f"set_{property_name}")(new_val)
                logger.debug(
                    f"Direct engine {property_name} update successful")
            except Exception as e:
                logger.warning(f"Engine update failed: {e}")
        else:
            # MPV-based engines (Nanmai, GTTS) route: background execution (avoid IPC blocking TUI)
            def background_mpv_update():
                try:
                    if self.app.tts_engine:  # Double check engine still exists
                        getattr(self.app.tts_engine,
                                f"set_{property_name}")(new_val)
                        logger.debug(
                            f"Background MPV {property_name} update successful")
                    else:
                        logger.warning(
                            "Engine became unavailable during background update")
                except Exception as e:
                    logger.warning(f"Background MPV update failed: {e}")
                    # Could add error handling/notification here if needed

            # Use Textual's run_worker for thread management
            self.app.run_worker(
                background_mpv_update,
                thread=True,
                name=f"mpv_{property_name}_update",
                group="engine_adjustments"  # Group for coordinated cancellation if needed
            )

            logger.debug(f"Queued background MPV {property_name} adjustment")

    def action_increase_volume(self) -> None:
        """Increase TTS volume."""
        self.app._update_user_activity()
        self._adjust_engine_property("volume", delta=0.1)
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_decrease_volume(self) -> None:
        """Decrease TTS volume."""
        self.app._update_user_activity()
        self._adjust_engine_property("volume", delta=-0.1)
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_increase_speed(self) -> None:
        """Increase TTS speed."""
        self.app._update_user_activity()
        self._adjust_engine_property("speed", delta=0.1)
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_decrease_speed(self) -> None:
        """Decrease TTS speed."""
        self.app._update_user_activity()
        self._adjust_engine_property("speed", delta=-0.1)
        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_increase_pitch(self) -> None:
        """Increase TTS pitch."""
        self.app._update_user_activity()

        # Check current engine type
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS does not support pitch adjustment
            self.app.notify(
                "gTTS does not support pitch adjustment", severity="warning"
            )
            return
        elif current_engine == "nanmai":
            # NanmaiTTS does not support pitch adjustment
            self.app.notify(
                "NanmaiTTS does not support pitch adjustment", severity="warning"
            )
            return
        elif current_engine == "edge-tts":
            # Edge-TTS: use engine-specific pitch adjustment
            if self.app.tts_engine and hasattr(self.app.tts_engine, "set_pitch"):
                # Get current pitch from engine
                current_pitch = self.app.tts_engine.get_pitch()
                val = int(current_pitch.replace("+", "").replace("Hz", ""))
                new_val = min(50, val + 5)
                new_pitch = f"+{new_val}Hz" if new_val >= 0 else f"{new_val}Hz"

                # Set new pitch on engine
                self.app.tts_engine.set_pitch(new_pitch)

                # Update global UI value for consistency
                self.app.tts_pitch = new_pitch
                logger.debug(
                    f"Edge-TTS pitch increased: {current_pitch} -> {new_pitch}"
                )
        else:
            # Fallback: use traditional global pitch
            val = int(self.app.tts_pitch.replace("+", "").replace("Hz", ""))
            new_val = min(50, val + 5)
            self.app.tts_pitch = f"+{new_val}Hz" if new_val >= 0 else f"{new_val}Hz"

        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_decrease_pitch(self) -> None:
        """Decrease TTS pitch."""
        self.app._update_user_activity()

        # Check current engine type
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts")

        if current_engine == "gtts":
            # gTTS does not support pitch adjustment
            self.app.notify(
                "gTTS does not support pitch adjustment", severity="warning"
            )
            return
        elif current_engine == "nanmai":
            # NanmaiTTS does not support pitch adjustment
            self.app.notify(
                "NanmaiTTS does not support pitch adjustment", severity="warning"
            )
            return
        elif current_engine == "edge-tts":
            # Edge-TTS: use engine-specific pitch adjustment
            if self.app.tts_engine and hasattr(self.app.tts_engine, "set_pitch"):
                # Get current pitch from engine
                current_pitch = self.app.tts_engine.get_pitch()
                val = int(current_pitch.replace("+", "").replace("Hz", ""))
                new_val = val - 5
                new_pitch = f"+{new_val}Hz" if new_val >= 0 else f"{new_val}Hz"

                # Set new pitch on engine
                self.app.tts_engine.set_pitch(new_pitch)

                # Update global UI value for consistency
                self.app.tts_pitch = new_pitch
                logger.debug(
                    f"Edge-TTS pitch decreased: {current_pitch} -> {new_pitch}"
                )
        else:
            # Fallback: use traditional global pitch
            val = int(self.app.tts_pitch.replace("Hz", ""))
            new_val = val - 5
            self.app.tts_pitch = f"+{new_val}Hz" if new_val >= 0 else f"{new_val}Hz"

        self._save_tts_config()
        self.app.call_next(self.app._update_tts_progress)

    def action_content_up(self) -> None:
        """Move content cursor up."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_start = self.app.viewport_content.move_cursor_up()
        if at_chapter_start:
            prev_chapter = self.find_prev_chapter()
            if prev_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        prev_chapter, from_end=True)
                )
        self.app._update_content_display()

    def action_content_down(self) -> None:
        """Move content cursor down."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_end = self.app.viewport_content.move_cursor_down()
        if at_chapter_end:
            next_chapter = self.find_next_chapter()
            if next_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        next_chapter, from_start=True)
                )
        self.app._update_content_display()

    def action_content_page_up(self) -> None:
        """Move content cursor up by page."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_start = self.app.viewport_content.page_up()
        if at_chapter_start:
            prev_chapter = self.find_prev_chapter()
            if prev_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        prev_chapter, from_end=True)
                )
        self.app._update_content_display()

    def action_content_page_down(self) -> None:
        """Move content cursor down by page."""
        if not self.app.viewport_content:
            return
        self.app._update_user_activity()
        if self.app.tts_status == "PLAYING":
            self.app.stop_speaking()
        _, at_chapter_end = self.app.viewport_content.page_down()
        if at_chapter_end:
            next_chapter = self.find_next_chapter()
            if next_chapter:
                self.app.run_worker(
                    self.app.epub_manager.load_chapter(
                        next_chapter, from_start=True)
                )
        self.app._update_content_display()

    def action_content_home(self) -> None:
        """Jump to chapter start."""
        if self.app.viewport_content:
            self.app._update_user_activity()
            if self.app.tts_status == "PLAYING":
                self.app.stop_speaking()
            self.app.viewport_content.jump_to_page(0)
            self.app._update_content_display()

    def action_content_end(self) -> None:
        """Jump to chapter end."""
        if self.app.viewport_content:
            self.app._update_user_activity()
            if self.app.tts_status == "PLAYING":
                self.app.stop_speaking()
            info = self.app.viewport_content.get_viewport_info()
            self.app.viewport_content.jump_to_page(info["total_pages"] - 1)
            lines = len(self.app.viewport_content.get_current_viewport_lines())
            self.app.viewport_content.cursor_in_page = max(0, lines - 1)
            self.app._update_content_display()

    def action_tts_play_pause(self):
        """Intelligent play/pause logic, compatible with two engines"""
        self.app._update_user_activity()

        if self.app.tts_status == "PLAYING":
            # Playing → Pause (same logic for both engines)
            self.app.tts_integration.playback_manager.stop_playback(
                is_pause=True)
            self.app.set_tts_status("PAUSED")

        elif self.app.tts_status == "PAUSED":
            # ⭐ Key modification: Choose resume method based on engine type
            if self._should_use_engine_resume():
                self._resume_via_engine()
            else:
                self._resume_via_playback_manager()

        elif self.app.tts_status == "STOPPED":
            # Stopped state → Start playing
            if self.app.tts_integration.network_manager.network_error_occurred:
                self.app.tts_integration.network_manager.reset_network_error_state()
            self.app.tts_integration.playlist_manager.generate_playlist()
            if self.app.tts_integration.playlist_manager.has_items():
                self.app.tts_integration.playback_manager.start_playback()
            else:
                # Original logic for finding next chapter
                import functools

                from speakub.tts.ui.runners import find_and_play_next_chapter_worker

                worker_func = functools.partial(
                    find_and_play_next_chapter_worker, self.app.tts_integration
                )
                self.app.run_worker(worker_func, exclusive=True, thread=True)

    def _should_use_engine_resume(self) -> bool:
        """Determine whether to use engine's resume() method"""
        if not self.app.tts_engine:
            return False

        if hasattr(self.app.tts_engine, "can_resume"):
            can_resume = self.app.tts_engine.can_resume()
            logger.debug(f"Engine can_resume: {can_resume}")
            return can_resume

        return False

    def _resume_via_engine(self):
        """Resume playback using engine's resume() method"""
        try:
            if self.app.tts_integration.network_manager.network_error_occurred:
                self.app.tts_integration.network_manager.reset_network_error_state()

            self.app.tts_engine.resume()
            self.app.set_tts_status("PLAYING")
            logger.debug("TTS resumed via engine.resume()")

        except Exception as e:
            logger.error(f"Failed to resume via engine: {e}")
            self._resume_via_playback_manager()

    def _resume_via_playback_manager(self):
        """Refactored into clear steps"""
        self._reset_network_on_resume()
        self._start_playback_safely()

    def _reset_network_on_resume(self):
        """Check and reset network error state"""
        if self.app.tts_integration.network_manager.network_error_occurred:
            self.app.tts_integration.network_manager.reset_network_error_state()

    def _start_playback_safely(self):
        """Safely start playback, handle potential errors"""
        try:
            self.app.tts_integration.playback_manager.start_playback()
            logger.debug("TTS resumed via PlaybackManager.start_playback()")
        except Exception as e:
            logger.error(f"Failed to resume via PlaybackManager: {e}")
            self.app.notify(f"Resume failed: {e}", severity="error")

    def action_tts_stop(self):
        """Stop TTS."""
        self.app.stop_speaking(is_pause=False)

    def find_next_chapter(self) -> Optional[dict]:
        """Find the next chapter."""
        return self.app.epub_manager.get_next_chapter()

    def find_prev_chapter(self) -> Optional[dict]:
        """Find the previous chapter."""
        return self.app.epub_manager.get_previous_chapter()

    def action_add_bookmark(self) -> None:
        """Add a bookmark for the current position."""
        if not self.app.viewport_content or not self.app.current_chapter:
            self.app.notify(
                "Cannot add bookmark: No content loaded", severity="warning"
            )
            return

        # 1. Get current basic info
        from speakub.core.bookmarks import bookmark_manager

        # Determine book title
        book_title = "Unknown Book"
        if self.app.toc_data:
            book_title = self.app.toc_data.get("book_title", "Unknown Book")

        # Chapter info
        chapter_title = self.app.current_chapter.get(
            "title", "Untitled Chapter")
        chapter_src = self.app.current_chapter.get("src", "")

        # 2. Get position info
        global_line = self.app.viewport_content.get_cursor_global_position()

        # Get CFI if possible - improved error handling
        cfi = None
        if hasattr(self.app, "progress_manager") and self.app.progress_manager:
            try:
                cfi = self.app.progress_manager.get_cfi_from_line(global_line)
            except Exception as e:
                logger.debug(f"CFI generation not available: {e}")
                # Don't warn or block bookmark creation

        # 3. Save bookmark (always succeeds now)
        bookmark = bookmark_manager.add_bookmark(
            epub_path=self.app.epub_path,
            epub_title=book_title,
            chapter_title=chapter_title,
            chapter_src=chapter_src,
            global_line=global_line,
            cfi=cfi,
        )

        self.app.notify(
            f"Bookmark added at {bookmark.display_position}", severity="success"
        )

    def action_show_bookmarks(self) -> None:
        """Show bookmarks list."""
        from speakub.ui.screens.bookmarks import BookmarkScreen

        def handle_bookmark_select(bookmark):
            if bookmark:
                # Stop TTS immediately when bookmark is selected to prevent sync issues
                if self.app.tts_status == "PLAYING":
                    logger.info(
                        "Stopping TTS immediately when bookmark selected to maintain sync")
                    self.app.stop_speaking(is_pause=False)
                self.app.run_worker(self._restore_bookmark(bookmark))

        self.app.push_screen(BookmarkScreen(
            self.app.epub_path), handle_bookmark_select)

    async def _restore_bookmark(self, bookmark):
        """Restore reading position from a bookmark object."""
        try:
            # 1. Check if chapter manager is available
            if (
                not hasattr(self.app, "chapter_manager")
                or self.app.chapter_manager is None
            ):
                # Try to ensure chapter manager is initialized
                if hasattr(self.app, "epub_manager") and self.app.epub_manager:
                    # The epub_manager may have initialized chapter_manager
                    # but app.chapter_manager might not be assigned yet
                    if (
                        hasattr(self.app.epub_manager, "chapter_manager")
                        and self.app.epub_manager.chapter_manager
                    ):
                        self.app.chapter_manager = self.app.epub_manager.chapter_manager
                    else:
                        self.app.notify(
                            "Error: Book navigation unavailable", severity="error"
                        )
                        return

            if not self.app.chapter_manager:
                self.app.notify(
                    "Error: Book navigation unavailable", severity="error")
                return

            # 2. Find chapter
            target_chapter = self.app.chapter_manager.find_chapter_by_src(
                bookmark.chapter_src
            )

            if not target_chapter:
                self.app.notify(
                    "Error: Chapter not found in this book", severity="error"
                )
                return

            self.app.notify(
                f"Jumping to bookmark: {bookmark.chapter_title}...",
                severity="information",
            )

            # 3. Load chapter
            # We pass the CFI directly to load_chapter which handles CFI positioning
            if bookmark.cfi:
                await self.app.epub_manager.load_chapter(
                    target_chapter, cfi=bookmark.cfi
                )
            else:
                # Fallback to line based positioning
                await self.app.epub_manager.load_chapter(target_chapter)
                # Manually set cursor if load_chapter didn't handle it
                if self.app.viewport_content:
                    self.app.viewport_content.set_cursor_by_global_line(
                        bookmark.global_line_position
                    )
                    self.app.ui_utils.update_content_display()

            # 4. Force focus to content
            self.app.current_focus = "content"
            self.app.ui_utils.update_panel_focus()

        except Exception as e:
            logger.error(f"Failed to restore bookmark: {e}")
            self.app.notify(
                f"Failed to jump to bookmark: {e}", severity="error")
