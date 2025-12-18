"""
Content display widget for the EPUB reader.
"""

from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from rich.text import Text
from textual.binding import Binding
from textual.widgets import Static

if TYPE_CHECKING:
    from speakub.core.content_renderer import ContentRenderer


class ViewportContent:
    """
    [v2.0 Refactored Version]
    Manages viewport content with dynamic sizing and logical-line navigation.
    Owns raw HTML and re-renders when dimensions change.
    """

    def __init__(
        self,
        initial_html_content: str,
        renderer: "ContentRenderer",
        initial_width: int,
        initial_height: int,
        enable_paragraph_protection: bool = False,
        enable_defensive_wrap: bool = True,
        defer_pagination: bool = False,  # Keep default as False for compatibility
        cache_key: Optional[str] = None,
    ):
        # --- Core Properties ---
        self._html_content = initial_html_content
        self._renderer = renderer
        self.enable_paragraph_protection = enable_paragraph_protection
        self.enable_defensive_wrap = enable_defensive_wrap
        self._cache_key = cache_key

        # --- Dynamic State Properties ---
        self.content_lines: List[str] = []
        self.paragraphs: List[Dict] = []
        self.line_to_paragraph_map: Dict[int, Dict] = {}
        self.logical_lines: List[Dict] = []
        self.line_to_logical: Dict[int, int] = {}

        self.current_width: int = initial_width
        self.viewport_height: int = initial_height

        self.current_page: int = 0
        self.cursor_in_page: int = 0

        # --- Initialize Rendering ---
        if not defer_pagination:
            # Perform first layout and pagination
            self._rerender_and_repaginate(is_initial=True)
        else:
            # Defer pagination: only render, do not paginate
            import logging

            logger = logging.getLogger(__name__)
            logger.debug("Deferring pagination during initialization")
            self._render_content_only()
            # Initialize pagination state (will be completed later via update_dimensions)
            self.total_lines = len(self.content_lines)
            self.total_pages = (
                1  # Temporary value, will be updated in update_dimensions
            )

    def _rerender_and_repaginate(
        self, read_percentage: float = 0.0, is_initial: bool = False
    ):
        """
        Internal core method: re-render text, rebuild internal structures, rebuild paginator, and restore position.
        """
        import logging

        logger = logging.getLogger(__name__)

        logger.debug(
            "🔄 _rerender_and_repaginate called - is_initial: %s, width: %s",
            is_initial,
            self.current_width,
        )

        # 1. Re-render, generate fresh content_lines
        old_lines_count = len(self.content_lines) if self.content_lines else 0

        if not is_initial:
            logger.debug(f"📝 Re-rendering content with width {self.current_width}")
            # Capture renderer raw output and log a small sample for
            # diagnostic comparison with any post-wrap processing.
            raw_lines = self._renderer.render_chapter(
                self._html_content, width=self.current_width, cache_key=self._cache_key
            )
            try:
                sample = [ln for ln in raw_lines if ln and ln.strip()][:3]
            except Exception:
                sample = []
            logger.debug(
                "📝 Renderer raw: %d lines, sample=%r",
                len(raw_lines),
                sample,
            )
            self.content_lines = raw_lines
            logger.debug(
                "📝 Re-rendered %d -> %d lines",
                old_lines_count,
                len(self.content_lines),
            )
        else:
            # First render, avoid duplicate work
            if not self.content_lines:
                logger.debug(f"📝 Initial rendering with width {self.current_width}")
                raw_lines = self._renderer.render_chapter(
                    self._html_content,
                    width=self.current_width,
                    cache_key=self._cache_key,
                )
                try:
                    sample = [ln for ln in raw_lines if ln and ln.strip()][:3]
                except Exception:
                    sample = []
                logger.debug(
                    "📝 Renderer raw (initial): %d lines, sample=%r",
                    len(raw_lines),
                    sample,
                )
                self.content_lines = raw_lines
                logger.debug(f"📝 Initial render: {len(self.content_lines)} lines")

        # 2. Rebuild all internal structures that depend on content_lines
        self._build_paragraph_map()
        self._build_logical_line_map()
        self._build_content_line_map()

        # 3. Calculate total lines
        self.total_lines = len(self.content_lines)
        old_pages = getattr(self, "total_pages", 0)
        self.total_pages = max(
            1,
            (self.total_lines + self.viewport_height - 1) // self.viewport_height,
        )

        logger.debug(
            "📊 Pagination: lines=%s, height=%s, pages=%s->%s",
            self.total_lines,
            self.viewport_height,
            old_pages,
            self.total_pages,
        )

        # 4. Restore position based on "reading percentage" anchor
        target_line_index = 0
        if self.total_lines > 0:
            target_line_index = int(self.total_lines * read_percentage)
            target_line_index = max(0, min(target_line_index, self.total_lines - 1))

        # 5. Use unified method to set final position
        self.set_cursor_by_global_line(target_line_index)

        logger.debug(
            "✅ _rerender_and_repaginate completed - cursor at line %s",
            target_line_index,
        )

    def _render_content_only(self):
        """
        Only render content, do not perform pagination calculations.
        Used for deferred pagination cases.
        """
        import logging

        logger = logging.getLogger(__name__)

        logger.debug(f"📝 Rendering content only with width {self.current_width}")

        # Render content
        raw_lines = self._renderer.render_chapter(
            self._html_content, width=self.current_width, cache_key=self._cache_key
        )
        self.content_lines = raw_lines

        # Build content structure (but do not calculate pagination)
        self._build_paragraph_map()
        self._build_logical_line_map()
        self._build_content_line_map()

        logger.debug(f"📝 Content rendered: {len(self.content_lines)} lines")

    def update_dimensions(
        self,
        new_width: int,
        new_height: int,
        is_initial: bool = False,
    ) -> bool:
        """
        External callers only call this method to update dimensions.
        Returns True indicating a width change that requires redrawing occurred.
        """
        import logging

        logger = logging.getLogger(__name__)

        width_changed = new_width != self.current_width
        height_changed = new_height != self.viewport_height

        logger.debug(
            "🔄 update_dimensions called - width: %s->%s (%s), " "height: %s->%s (%s)",
            self.current_width,
            new_width,
            width_changed,
            self.viewport_height,
            new_height,
            height_changed,
        )

        if not width_changed and not height_changed:
            logger.debug("❌ update_dimensions skipped - no changes")
            return False

        # --- Save current reading progress "relative anchor" ---
        read_percentage = 0.0
        if getattr(self, "total_lines", 0) > 0:
            read_percentage = self.get_cursor_global_position() / self.total_lines

        logger.debug(
            "📊 Current state - lines: %s, pages: %s, cursor: %s",
            getattr(self, "total_lines", 0),
            getattr(self, "total_pages", 0),
            self.get_cursor_global_position(),
        )

        # Update dimension state
        self.current_width = new_width
        self.viewport_height = new_height

        # --- Decide processing method based on change type ---
        if width_changed:
            # Width changed: need to re-render content
            self._rerender_and_repaginate(
                read_percentage=read_percentage, is_initial=is_initial
            )

            # Defensive post-wrap: attempt to re-split paragraphs using
            # renderer splitter to handle cases where html2text output
            # looks width-insensitive.
            try:
                if not is_initial:
                    raw_lines = self._renderer.render_chapter(
                        self._html_content, width=self.current_width
                    )

                    logger.debug(
                        "📝 Defensive post-wrap: renderer returned %d raw_lines",
                        len(raw_lines),
                    )

                    paragraphs: List[str] = []
                    cur_para: List[str] = []
                    for ln in raw_lines:
                        if not ln or not ln.strip():
                            if cur_para:
                                paragraphs.append(" ".join(p.strip() for p in cur_para))
                                cur_para = []
                        else:
                            cur_para.append(ln)
                    if cur_para:
                        paragraphs.append(" ".join(p.strip() for p in cur_para))

                    rewrapped_lines: List[str] = []
                    for idx, para in enumerate(paragraphs):
                        if not para:
                            rewrapped_lines.append("")
                            continue
                        try:
                            para_lines = self._renderer._split_text_by_width(
                                para, self.current_width
                            )
                        except Exception:
                            para_lines = [para]
                        rewrapped_lines.extend(para_lines)
                        if idx != len(paragraphs) - 1:
                            rewrapped_lines.append("")

                    if rewrapped_lines:
                        try:
                            sample_raw = [ln for ln in raw_lines if ln and ln.strip()][
                                :3
                            ]
                        except Exception:
                            sample_raw = []
                        try:
                            sample_re = [
                                ln for ln in rewrapped_lines if ln and ln.strip()
                            ][:3]
                        except Exception:
                            sample_re = []
                        logger.debug(
                            "📝 Defensive post-wrap: rewrapped %d -> "
                            "sample_raw=%r sample_re=%r",
                            len(rewrapped_lines),
                            sample_raw,
                            sample_re,
                        )
                        self.content_lines = rewrapped_lines
                        self._build_paragraph_map()
                        self._build_logical_line_map()
                        self._build_content_line_map()
                        self.total_lines = len(self.content_lines)
                        self.total_pages = max(
                            1,
                            (self.total_lines + self.viewport_height - 1)
                            // self.viewport_height,
                        )
            except Exception:
                # keep renderer output if defensive rewrap fails
                pass
        elif height_changed:
            # Height changed: only need to recalculate page count, no re-rendering
            old_pages = getattr(self, "total_pages", 0)
            self.total_pages = max(
                1,
                (getattr(self, "total_lines", 0) + self.viewport_height - 1)
                // self.viewport_height,
            )
            logger.debug(
                "📊 Height changed - pages: %s->%s",
                old_pages,
                self.total_pages,
            )

        logger.debug(
            "✅ update_dimensions completed - new lines: %s, new pages: %s",
            getattr(self, "total_lines", 0),
            getattr(self, "total_pages", 0),
        )

        return width_changed

    def set_cursor_by_global_line(self, global_line_index: int) -> bool:
        """
        Set cursor position based on global line number.
        """
        if self.total_lines == 0:
            return False

        # Ensure line number is within valid range
        global_line_index = max(0, min(global_line_index, self.total_lines - 1))

        # Calculate page number and position within page
        page = global_line_index // self.viewport_height
        cursor_in_page = global_line_index % self.viewport_height

        # Boundary check
        page = min(page, self.total_pages - 1)
        viewport_lines = len(self.get_current_viewport_lines())
        cursor_in_page = min(cursor_in_page, max(0, viewport_lines - 1))

        self.current_page = page
        self.cursor_in_page = cursor_in_page
        return True

    def _is_content_line(self, line: str) -> bool:
        return bool(line and line.replace("&nbsp;", "").strip())

    def _build_content_line_map(self):
        self.content_line_indices = []
        self.line_to_content_index = {}
        content_index = 0
        for line_idx, line in enumerate(self.content_lines):
            if self._is_content_line(line):
                self.content_line_indices.append(line_idx)
                self.line_to_content_index[line_idx] = content_index
                content_index += 1
        self.total_content_lines = len(self.content_line_indices)

    def _build_paragraph_map(self):
        self.line_to_paragraph_map = {}
        self.paragraphs = []
        current_paragraph_lines = []
        paragraph_idx = 0
        for line_idx, line in enumerate(self.content_lines):
            if self._is_content_line(line):
                current_paragraph_lines.append(line_idx)
            else:
                if current_paragraph_lines:
                    para_info = {
                        "start": current_paragraph_lines[0],
                        "end": current_paragraph_lines[-1],
                        "lines": current_paragraph_lines,
                        "index": paragraph_idx,
                    }
                    self.paragraphs.append(para_info)
                    for p_line_idx in current_paragraph_lines:
                        self.line_to_paragraph_map[p_line_idx] = para_info
                    paragraph_idx += 1
                    current_paragraph_lines = []
        if current_paragraph_lines:
            para_info = {
                "start": current_paragraph_lines[0],
                "end": current_paragraph_lines[-1],
                "lines": current_paragraph_lines,
                "index": paragraph_idx,
            }
            self.paragraphs.append(para_info)
            for p_line_idx in current_paragraph_lines:
                self.line_to_paragraph_map[p_line_idx] = para_info

    def get_paragraph_text(self, para_info: dict) -> str:
        # Step 1: This is the most important part of the original code,
        # it builds the para_lines list from para_info.
        # This is the part that was missing in your current version.
        para_lines = []
        for line_idx in para_info["lines"]:
            if line_idx < len(self.content_lines):
                line_text = self.content_lines[line_idx].strip()
                if line_text:
                    para_lines.append(line_text)

        # If para_lines is empty, return an empty string directly to avoid errors.
        if not para_lines:
            return ""

        # Step 2: This is the "perfect solution" logic I suggested before,
        # but now it can safely handle the para_lines list that has been
        # correctly created in the previous step.
        result = ""
        for i, line in enumerate(para_lines):
            result += line
            # If not the last line
            if i < len(para_lines) - 1:
                # Determine if a space needs to be added between lines
                # (handling English word breaks)
                # Rule: If the current line ends with an English letter and
                # the next line starts with an English letter, add a space
                if line.endswith(
                    (
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                        "m",
                        "n",
                        "o",
                        "p",
                        "q",
                        "r",
                        "s",
                        "t",
                        "u",
                        "v",
                        "w",
                        "x",
                        "y",
                        "z",
                        "A",
                        "B",
                        "C",
                        "D",
                        "E",
                        "F",
                        "G",
                        "H",
                        "I",
                        "J",
                        "K",
                        "L",
                        "M",
                        "N",
                        "O",
                        "P",
                        "Q",
                        "R",
                        "S",
                        "T",
                        "U",
                        "V",
                        "W",
                        "X",
                        "Y",
                        "Z",
                    )
                ) and para_lines[i + 1].startswith(
                    (
                        "a",
                        "b",
                        "c",
                        "d",
                        "e",
                        "f",
                        "g",
                        "h",
                        "i",
                        "j",
                        "k",
                        "l",
                        "m",
                        "n",
                        "o",
                        "p",
                        "q",
                        "r",
                        "s",
                        "t",
                        "u",
                        "v",
                        "w",
                        "x",
                        "y",
                        "z",
                        "A",
                        "B",
                        "C",
                        "D",
                        "E",
                        "F",
                        "G",
                        "H",
                        "I",
                        "J",
                        "K",
                        "L",
                        "M",
                        "N",
                        "O",
                        "P",
                        "Q",
                        "R",
                        "S",
                        "T",
                        "U",
                        "V",
                        "W",
                        "X",
                        "Y",
                        "Z",
                    )
                ):
                    result += " "

        return result

    def _find_next_content_line(self, current_global_pos: int) -> Optional[int]:
        for content_line_idx in self.content_line_indices:
            if content_line_idx > current_global_pos:
                return content_line_idx
        return None

    def _find_prev_content_line(self, current_global_pos: int) -> Optional[int]:
        for content_line_idx in reversed(self.content_line_indices):
            if content_line_idx < current_global_pos:
                return content_line_idx
        return None

    def _build_logical_line_map(self):
        self.logical_lines = []
        self.line_to_logical = {}
        current_paragraph = []
        logical_idx = 0
        for i, line in enumerate(self.content_lines):
            if not self._is_content_line(line):
                if current_paragraph:
                    self.logical_lines.append(
                        {
                            "lines": current_paragraph,
                            "start_line": current_paragraph[0],
                            "end_line": current_paragraph[-1],
                            "is_paragraph": True,
                        }
                    )
                    for line_idx in current_paragraph:
                        self.line_to_logical[line_idx] = logical_idx
                    logical_idx += 1
                    current_paragraph = []
            else:
                current_paragraph.append(i)
        if current_paragraph:
            self.logical_lines.append(
                {
                    "lines": current_paragraph,
                    "start_line": current_paragraph[0],
                    "end_line": current_paragraph[-1],
                    "is_paragraph": True,
                }
            )
            for line_idx in current_paragraph:
                self.line_to_logical[line_idx] = logical_idx

    def get_current_viewport_lines(self) -> List[str]:
        start_idx = self.current_page * self.viewport_height
        end_idx = min(start_idx + self.viewport_height, self.total_lines)
        return self.content_lines[start_idx:end_idx]

    def get_cursor_global_position(self) -> int:
        return self.current_page * self.viewport_height + self.cursor_in_page

    def get_chapter_line_info(self) -> Dict[str, int]:
        """Get line number information within chapter, avoid pagination calculation dependency"""
        global_pos = self.get_cursor_global_position()
        # Calculate relative line number within chapter (counting from 1)
        chapter_line = global_pos + 1
        return {
            "chapter_line": chapter_line,  # e.g. "line 245"
            "global_line": global_pos,
            "chapter_percentage": int((global_pos / self.total_lines) * 100)
            if self.total_lines > 0
            else 0,
        }

    def get_viewport_info(self) -> Dict[str, int]:
        return {
            "current_page": self.current_page,
            "total_pages": self.total_pages,
            "cursor_in_page": self.cursor_in_page,
            "lines_in_current_viewport": len(self.get_current_viewport_lines()),
            "global_cursor": self.get_cursor_global_position(),
            "viewport_height": self.viewport_height,
            "total_content_lines": self.total_content_lines,
        }

    def move_cursor_down(self) -> Tuple[bool, bool]:
        current_global_pos = self.get_cursor_global_position()
        current_logical_idx = self.line_to_logical.get(current_global_pos)
        if current_logical_idx is None:
            return self._move_cursor_down_content_fallback()
        next_logical_idx = current_logical_idx + 1
        if next_logical_idx >= len(self.logical_lines):
            return False, True
        next_logical = self.logical_lines[next_logical_idx]
        next_line_pos = next_logical["start_line"]
        next_page = next_line_pos // self.viewport_height
        next_cursor = next_line_pos % self.viewport_height
        page_changed = self.current_page != next_page
        self.current_page = next_page
        self.cursor_in_page = next_cursor
        return page_changed, False

    def move_cursor_up(self) -> Tuple[bool, bool]:
        current_global_pos = self.get_cursor_global_position()
        current_logical_idx = self.line_to_logical.get(current_global_pos)
        if current_logical_idx is None:
            return self._move_cursor_up_content_fallback()
        prev_logical_idx = current_logical_idx - 1
        if prev_logical_idx < 0:
            return False, True
        prev_logical = self.logical_lines[prev_logical_idx]
        prev_line_pos = prev_logical["start_line"]
        prev_page = prev_line_pos // self.viewport_height
        prev_cursor = prev_line_pos % self.viewport_height
        page_changed = self.current_page != prev_page
        self.current_page = prev_page
        self.cursor_in_page = prev_cursor
        return page_changed, False

    def _move_cursor_down_content_fallback(self) -> Tuple[bool, bool]:
        current_global_pos = self.get_cursor_global_position()
        next_content_line = self._find_next_content_line(current_global_pos)
        if next_content_line is None:
            return False, True
        next_page = next_content_line // self.viewport_height
        next_cursor = next_content_line % self.viewport_height
        return self._change_to_page(next_page, next_cursor), False

    def _move_cursor_up_content_fallback(self) -> Tuple[bool, bool]:
        current_global_pos = self.get_cursor_global_position()
        prev_content_line = self._find_prev_content_line(current_global_pos)
        if prev_content_line is None:
            return False, True
        prev_page = prev_content_line // self.viewport_height
        prev_cursor = prev_content_line % self.viewport_height
        return self._change_to_page(prev_page, prev_cursor), False

    def _change_to_page(self, page_num: int, cursor_pos: int) -> bool:
        page_changed = self.current_page != page_num
        if 0 <= page_num < self.total_pages:
            self.current_page = page_num
            page_lines = len(self.get_current_viewport_lines())
            self.cursor_in_page = max(0, min(cursor_pos, page_lines - 1))
            return page_changed
        return False

    def jump_to_page(self, page_num: int) -> bool:
        return self._change_to_page(page_num, 0)

    def page_down(self) -> Tuple[bool, bool]:
        if self.current_page < self.total_pages - 1:
            next_page = self.current_page + 1
            start_idx = next_page * self.viewport_height
            end_idx = min(start_idx + self.viewport_height, self.total_lines)
            first_content_cursor = 0
            for line_idx in range(start_idx, end_idx):
                if line_idx < len(self.content_lines) and self._is_content_line(
                    self.content_lines[line_idx]
                ):
                    first_content_cursor = line_idx - start_idx
                    break
            self._change_to_page(next_page, first_content_cursor)
            return True, False
        else:
            return False, True

    def page_up(self) -> Tuple[bool, bool]:
        if self.current_page > 0:
            prev_page = self.current_page - 1
            start_idx = prev_page * self.viewport_height
            end_idx = min(start_idx + self.viewport_height, self.total_lines)
            first_content_cursor = 0
            for line_idx in range(start_idx, end_idx):
                if line_idx < len(self.content_lines) and self._is_content_line(
                    self.content_lines[line_idx]
                ):
                    first_content_cursor = line_idx - start_idx
                    break
            self._change_to_page(prev_page, first_content_cursor)
            return True, False
        else:
            return False, True


class ContentDisplay(Static):
    BINDINGS = [
        Binding("up", "cursor_up", "Cursor Up", show=False),
        Binding("down", "cursor_down", "Cursor Down", show=False),
        Binding("pageup", "cursor_page_up", "Page Up", show=False),
        Binding("pagedown", "cursor_page_down", "Page Down", show=False),
        Binding("home", "cursor_home", "Go to Top", show=False),
        Binding("end", "cursor_end", "Go to Bottom", show=False),
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.viewport_content: Optional[ViewportContent] = None
        self.app_ref = None

    def set_viewport_content(self, viewport_content: ViewportContent):
        self.viewport_content = viewport_content
        self._update_display()

    def _update_display(self):
        if not self.viewport_content:
            self.update("Select a chapter to begin reading...")
            return
        viewport_lines = self.viewport_content.get_current_viewport_lines()
        if not viewport_lines:
            self.update("No content available...")
            return
        content_text = Text()
        current_global_cursor = self.viewport_content.get_cursor_global_position()
        for idx, line in enumerate(viewport_lines):
            line_str = line.rstrip()
            if idx < len(viewport_lines) - 1:
                line_str += "\n"
            global_line_idx = (
                self.viewport_content.current_page
                * self.viewport_content.viewport_height
                + idx
            )
            should_highlight = False
            cursor_logical_idx = self.viewport_content.line_to_logical.get(
                current_global_cursor
            )
            if cursor_logical_idx is not None:
                cursor_logical = self.viewport_content.logical_lines[cursor_logical_idx]
                if (
                    cursor_logical["is_paragraph"]
                    and cursor_logical["start_line"]
                    <= global_line_idx
                    <= cursor_logical["end_line"]
                ):
                    should_highlight = True
            if not should_highlight and idx == self.viewport_content.cursor_in_page:
                should_highlight = True
            if should_highlight:
                content_text.append(line_str, style="reverse")
            else:
                content_text.append(line_str)
        self.update(content_text)

    def action_cursor_up(self):
        if self.app_ref:
            self.app_ref.action_content_up()

    def action_cursor_down(self):
        if self.app_ref:
            self.app_ref.action_content_down()

    def action_cursor_page_up(self):
        if self.app_ref:
            self.app_ref.action_content_page_up()

    def action_cursor_page_down(self):
        if self.app_ref:
            self.app_ref.action_content_page_down()

    def action_cursor_home(self):
        if self.app_ref:
            self.app_ref.action_content_home()

    def action_cursor_end(self):
        if self.app_ref:
            self.app_ref.action_content_end()
