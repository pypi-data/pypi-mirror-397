#!/usr/bin/env python3
"""
EPUB management for SpeakUB
"""

from typing import TYPE_CHECKING, Dict, Optional

from bs4 import BeautifulSoup

from speakub.core.chapter_manager import ChapterManager
from speakub.core.content_renderer import ContentRenderer
from speakub.core.epubkit_adapter import EPUBParserAdapter as EPUBParser
from speakub.core.progress_tracker import ProgressTracker
from speakub.ui.widgets.content_widget import ViewportContent
from speakub.utils.config import ConfigManager

if TYPE_CHECKING:
    from speakub.ui.app import EPUBReaderApp


class EPUBManager:
    """Manages EPUB loading, parsing, and content access."""

    def __init__(self, app: "EPUBReaderApp", config_manager: ConfigManager):
        self.app = app
        self.config_manager = config_manager
        self.epub_parser: Optional[EPUBParser] = None
        self.content_renderer: Optional[ContentRenderer] = None
        self.chapter_manager: Optional[ChapterManager] = None
        self.progress_tracker: Optional[ProgressTracker] = None
        self.toc_data: Optional[Dict] = None
        self.current_chapter: Optional[Dict] = None
        self.current_chapter_soup: Optional[BeautifulSoup] = None

    async def load_epub(self) -> None:
        """Load and initialize EPUB file."""
        try:
            # Clean up any existing EPUB resources before loading new one
            if self.epub_parser:
                try:
                    self.epub_parser.clear_caches()
                except Exception as e:
                    import logging

                    logging.warning(f"Error clearing caches: {e}")

            self.epub_parser = EPUBParser(self.app.epub_path, trace=self.app._debug)
            self.epub_parser.open()
            self.toc_data = self.epub_parser.parse_toc()
            self.content_renderer = ContentRenderer(
                content_width=self.app.ui_utils.calculate_content_width(),
                trace=self.app._debug,
            )
            self.chapter_manager = ChapterManager(self.toc_data, trace=self.app._debug)
            self.progress_tracker = ProgressTracker(
                self.app.epub_path, trace=self.app._debug
            )
            self.app.progress_tracker = self.progress_tracker
            self.app.toc_data = self.toc_data

            await self.app.ui_utils.update_toc_tree(self.toc_data)
            self.app.ui_utils.update_panel_titles()
            await self.app.progress_manager.load_saved_progress()
            self.app.ui_utils.update_panel_titles()
        except Exception as e:
            import logging

            logging.exception("Error loading EPUB")
            self.app.notify(f"Error: {e}", severity="error")

    def close_epub(self) -> None:
        """Close EPUB parser and clean up resources."""
        if self.epub_parser:
            try:
                self.epub_parser.close()
            except Exception:
                pass

    async def load_chapter(
        self,
        chapter: dict,
        cfi: Optional[str] = None,
        from_start: bool = False,
        from_end: bool = False,
    ) -> None:
        """Load a specific chapter."""
        try:
            self.current_chapter = chapter
            self.app.current_chapter = chapter
            html_content = self.epub_parser.read_chapter(chapter["src"])
            self.current_chapter_soup = BeautifulSoup(html_content, "html.parser")

            # ===== ViewportContent creation method has changed =====
            enable_protection = self.config_manager.get(
                "reading.paragraph_protection", False
            )

            # Dimension validation: ensure using latest viewport height
            # If widgets are not ready yet, use fallback height
            if not self.app._widgets_ready:
                import logging

                logging.getLogger(__name__).warning(
                    "Widgets not ready during chapter load, using fallback viewport height"
                )

            current_width = self.app.ui_utils.calculate_content_width()
            current_height = self.app.ui_utils.calculate_viewport_height()

            # Update app's viewport height status
            self.app.current_viewport_height = current_height

            import logging

            logger = logging.getLogger(__name__)
            logger.debug(
                f"Loading chapter with dimensions - width: {current_width}, height: {current_height}"
            )

            # Use new constructor, pass raw data and dependencies
            self.app.viewport_content = ViewportContent(
                initial_html_content=html_content,
                renderer=self.content_renderer,
                initial_width=current_width,
                initial_height=current_height,
                enable_paragraph_protection=enable_protection,
                cache_key=chapter["src"],  # Use chapter src as cache key
            )

            cursor_position = 0
            if cfi and self.current_chapter_soup:
                try:
                    cursor_position = self.app.progress_manager.get_line_from_cfi(cfi)
                except Exception as e:
                    import logging

                    logging.warning(f"CFI resolution failed: {e}")
                    cursor_position = 0

            if from_end:
                info = self.app.viewport_content.get_viewport_info()
                self.app.viewport_content.jump_to_page(info["total_pages"] - 1)
                lines = len(self.app.viewport_content.get_current_viewport_lines())
                self.app.viewport_content.cursor_in_page = max(0, lines - 1)
            elif from_start:
                self.app.viewport_content.jump_to_page(0)
            else:
                page, cursor = divmod(cursor_position, self.app.current_viewport_height)
                self.app.viewport_content.jump_to_page(page)
                lines = len(self.app.viewport_content.get_current_viewport_lines())
                self.app.viewport_content.cursor_in_page = max(
                    0, min(cursor, lines - 1)
                )

            self.app.ui_utils.update_content_display()

            if self.app.tts_widget:
                self.app.tts_widget.set_text(
                    self.content_renderer.extract_text_for_tts(html_content)
                )

            self.app.title = f"SpeakUB - {self.toc_data.get('book_title', 'Book') if self.toc_data else 'Book'}"
            self.app.ui_utils.update_panel_titles()
        except Exception as e:
            import logging

            logging.exception("Error loading chapter")
            self.app.notify(f"Error: {e}", severity="error")

    def get_next_chapter(self) -> Optional[dict]:
        """Get the next chapter."""
        if not self.current_chapter or not self.chapter_manager:
            return None
        return self.chapter_manager.get_next_chapter(self.current_chapter)

    def get_previous_chapter(self) -> Optional[dict]:
        """Get the previous chapter."""
        if not self.current_chapter or not self.chapter_manager:
            return None
        return self.chapter_manager.get_previous_chapter(self.current_chapter)

    def get_next_chapter_content_lines(self) -> Optional[tuple[dict, list[str]]]:
        """
        Find the next chapter, render its content, and return both.
        This acts as a higher-level facade method.
        """
        next_chapter = self.get_next_chapter()
        if not next_chapter:
            return None

        if not self.epub_parser or not self.content_renderer:
            return None

        html = self.epub_parser.read_chapter(next_chapter["src"])
        lines = self.content_renderer.render_chapter(html)

        return next_chapter, lines
