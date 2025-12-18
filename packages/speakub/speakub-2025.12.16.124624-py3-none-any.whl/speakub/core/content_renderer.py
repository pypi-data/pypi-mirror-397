#!/usr/bin/env python3
"""
Content Renderer - Converts HTML content to text for display.
"""

import re
import zlib
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

import html2text
from bs4 import BeautifulSoup, Tag

try:
    from cachetools import TTLCache

    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

from speakub.utils.text_utils import (
    str_display_width,
    trace_log,
)

# Remove custom AdaptiveCache, use standard cachetools.TTLCache


class EPUBTextRenderer(html2text.HTML2Text):
    """Custom html2text renderer for EPUB content."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.strong_mark = "**"
        self.emphasis_mark = "*"
        self.ignore_tables = True
        self.ignore_links = True
        # NOTE: self.body_width is set by parent __init__ via 'bodywidth'
        # in kwargs. We no longer force it to 0.
        self.wrap_links = False
        self.wrap_list_items = False
        # Ensure text wrapping is enabled
        self.wrap = True

    # type: ignore[no-untyped-def]

    def handle_tag(self, tag: str, attrs: dict, start: bool) -> Optional[str]:
        """Handle HTML tags with custom formatting for better footnote display."""
        # 1. Handle unsupported tags (existing logic)
        unsupported_tags = ["video", "audio",
                            "script", "iframe", "svg", "canvas"]

        if tag in unsupported_tags:
            if start:
                return "[Unsupported Content]\n"
            else:
                return ""

        # --- New fix start ---
        # 2. Use preprocessing stage for footnote formatting, handle_tag method now mainly handles unsupported tags
        # --- New fix end ---

        return super().handle_tag(tag, attrs, start)

    def handle_image(self, src: str, alt: str, width: int, height: int) -> str:
        """Handle image tags with better formatting."""
        alt_text = alt.strip() if alt else ""
        if alt_text:
            return f'[Image: {alt_text} src="{src}"]'
        else:
            return f'[Image src="{src}"]'


class ContentRenderer:
    """Renders HTML content to formatted text."""

    def __init__(self, content_width: int = 80, trace: bool = False):
        """
        Initialize content renderer.

        Args:
            content_width: Target width for text wrapping
            trace: Enable trace logging
        """
        self.content_width = content_width
        self.trace = trace

        # Use TTLCache for renderer caching if available
        if CACHETOOLS_AVAILABLE:
            self._renderer_cache = TTLCache(
                maxsize=100, ttl=300)  # 5 minutes TTL
        else:
            # Fallback to simple dict-based cache (no TTL)
            self._renderer_cache = {}

        # Render result cache for expensive rendering operations
        if CACHETOOLS_AVAILABLE:
            self._render_cache = TTLCache(
                maxsize=200, ttl=600
            )  # 10 minutes TTL for rendered content, increased capacity
        else:
            self._render_cache = {}

        # Cache management and monitoring
        self._cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "memory_pressure_events": 0,
        }
        self._memory_check_interval = 30  # Check memory every 30 renders
        self._render_count = 0

        # Width calculation cache is handled by @lru_cache decorator (no manual cache needed)

    def _get_renderer(self, width: int) -> EPUBTextRenderer:
        """Get or create a renderer for the specified width from cache."""
        if CACHETOOLS_AVAILABLE:
            # TTLCache automatically handles TTL
            if width not in self._renderer_cache:
                self._renderer_cache[width] = EPUBTextRenderer(bodywidth=width)
            return self._renderer_cache[width]
        else:
            # Simple dict fallback - no TTL
            if width not in self._renderer_cache:
                self._renderer_cache[width] = EPUBTextRenderer(bodywidth=width)
            return self._renderer_cache[width]

    def _check_memory_pressure(self) -> bool:
        """Check if system is under memory pressure and adjust cache sizes."""
        self._render_count += 1
        if self._render_count % self._memory_check_interval != 0:
            return False

        try:
            import psutil

            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # High memory pressure threshold
            if memory_percent > 80.0:
                self._cache_stats["memory_pressure_events"] += 1
                self._reduce_cache_sizes()
                trace_log(
                    f"[INFO] Memory pressure detected ({memory_percent:.1f}%), reduced cache sizes",
                    self.trace,
                )
                return True
            elif (
                memory_percent < 60.0
                and len(self._render_cache)
                < getattr(self._render_cache, "maxsize", 50) * 0.8
            ):
                # Low memory pressure, can increase cache size slightly
                self._increase_cache_sizes()
                trace_log(
                    f"[INFO] Memory available ({memory_percent:.1f}%), increased cache sizes",
                    self.trace,
                )
        except ImportError:
            # psutil not available, skip memory checks
            pass
        except Exception as e:
            trace_log(f"[WARN] Memory check failed: {e}", self.trace)

        return False

    def _reduce_cache_sizes(self):
        """Reduce cache sizes under memory pressure."""
        if hasattr(self._render_cache, "maxsize"):
            current_max = getattr(self._render_cache, "maxsize", 50)
            # Reduce to 70%, minimum 10
            new_max = max(10, int(current_max * 0.7))
            if hasattr(self._render_cache, "_TTLCache__maxsize"):
                self._render_cache._TTLCache__maxsize = new_max
            trace_log(
                f"[INFO] Reduced render cache maxsize: {current_max} -> {new_max}",
                self.trace,
            )

        # Evict oldest entries if cache is too full
        if hasattr(self._render_cache, "maxsize") and len(self._render_cache) > getattr(
            self._render_cache, "maxsize", 50
        ):
            # TTLCache doesn't have direct eviction method, rely on TTL
            pass

    def _increase_cache_sizes(self):
        """Increase cache sizes when memory is available."""
        if hasattr(self._render_cache, "maxsize"):
            current_max = getattr(self._render_cache, "maxsize", 50)
            # Increase to 120%, maximum 100
            new_max = min(100, int(current_max * 1.2))
            if hasattr(self._render_cache, "_TTLCache__maxsize"):
                self._render_cache._TTLCache__maxsize = new_max
            trace_log(
                f"[INFO] Increased render cache maxsize: {current_max} -> {new_max}",
                self.trace,
            )

    def render_chapter(
        self,
        html_content: str,
        width: Optional[int] = None,
        cache_key: Optional[str] = None,
    ) -> List[str]:
        """
        Render HTML chapter content to text lines.

        Args:
            html_content: Raw HTML content
            width: Override default content width
            cache_key: Optional cache key for rendered content

        Returns:
            List of text lines
        """
        render_width = width or self.content_width
        render_width = max(20, render_width)  # Minimum width

        # Check memory pressure periodically
        self._check_memory_pressure()

        # Check render cache first if cache_key provided
        if cache_key and hasattr(self, "_render_cache"):
            cache_entry_key = f"{cache_key}_{render_width}"
            cached_result = self._render_cache.get(cache_entry_key)
            if cached_result is not None:
                self._cache_stats["hits"] += 1
                trace_log(
                    f"[INFO] Render cache hit for {cache_key}", self.trace)
                # Decompress if needed
                return self._decompress_if_needed(cached_result)
            else:
                self._cache_stats["misses"] += 1

        # Try primary renderer (html2text)
        try:
            # Preprocess HTML to handle problematic elements
            processed_html = self._preprocess_html_for_parsing(html_content)
            renderer = self._get_renderer(render_width)
            processed_text = renderer.handle(processed_html)

            # Clean up the text and split into lines
            processed_text = processed_text.strip()
            lines = processed_text.split("\n")

            # Apply manual text wrapping to ensure width compliance
            lines = self._apply_text_wrapping(lines, render_width)

            trace_log(f"[INFO] Rendered {len(lines)} lines", self.trace)

            # Cache the result if cache_key provided
            if cache_key and hasattr(self, "_render_cache"):
                cache_entry_key = f"{cache_key}_{render_width}"
                # Compress large content to save memory
                cached_content = self._compress_if_large(lines)
                self._render_cache[cache_entry_key] = cached_content

            return lines

        except Exception as e:
            trace_log(
                f"[WARN] html2text failed: {e}. Using fallback.", self.trace)
            result = self._fallback_render(html_content, render_width)

            # Cache fallback result too
            if cache_key and hasattr(self, "_render_cache"):
                cache_entry_key = f"{cache_key}_{render_width}"
                self._render_cache[cache_entry_key] = result

            return result

    def _compress_if_large(self, lines: List[str]) -> List[str]:
        """
        Compress rendered content if it's large to save memory.

        Args:
            lines: Rendered text lines

        Returns:
            Original lines or compressed data (with special marker)
        """
        # Only compress if content is large (more than 1000 lines or significant text)
        total_chars = sum(len(line) for line in lines)
        if len(lines) < 1000 and total_chars < 50000:
            return lines

        try:
            # Join lines and compress
            text_content = "\n".join(lines)
            compressed = zlib.compress(text_content.encode("utf-8"))

            # Only use compression if it actually saves space
            if len(compressed) < len(text_content.encode("utf-8")) * 0.8:
                # Store as special marker + compressed data
                return ["__COMPRESSED__"] + [compressed.hex()]
            else:
                return lines
        except Exception as e:
            trace_log(f"[WARN] Compression failed: {e}", self.trace)
            return lines

    def _decompress_if_needed(self, cached_content: List[str]) -> List[str]:
        """
        Decompress cached content if it was compressed.

        Args:
            cached_content: Cached content (possibly compressed)

        Returns:
            Decompressed lines
        """
        if not cached_content or cached_content[0] != "__COMPRESSED__":
            return cached_content

        try:
            # Extract compressed data
            compressed_hex = "".join(cached_content[1:])
            compressed = bytes.fromhex(compressed_hex)

            # Decompress
            decompressed = zlib.decompress(compressed).decode("utf-8")
            return decompressed.split("\n")
        except Exception as e:
            trace_log(f"[WARN] Decompression failed: {e}", self.trace)
            return []

    def _preprocess_html_for_parsing(self, html_content: str) -> str:
        """Preprocess HTML to fix known issues before parsing.

        Problems addressed:
        - Suppress ftbnum anchor contents to prevent footnote number duplication
        - Format footnote references for better visual display
        - Handle footnote lists to preserve original numbering for display
        - Other HTML cleanup as needed
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Handle footnote lists (class="ft") - preserve original numbering for display before clearing
            for ol_tag in soup.find_all("ol", class_="ft"):
                for li_tag in ol_tag.find_all("li", recursive=False):
                    ftbnum_anchor = li_tag.find("a", class_="ftbnum")
                    if ftbnum_anchor and ftbnum_anchor.get_text(strip=True):
                        # Extract and preserve the original number before clearing
                        original_num = ftbnum_anchor.get_text(
                            strip=True).strip()
                        # Unicode space to match original formatting
                        li_tag.insert(0, f"{original_num}　")
                # Convert to plain text formatting to avoid html2text auto-numbering
                for li_tag in ol_tag.find_all("li", recursive=False):
                    li_tag.name = "p"
                ol_tag.unwrap()

            # Suppress contents of ftbnum class anchors to prevent duplicate numbering (TTS safety)
            for ftbnum_anchor in soup.find_all("a", class_="ftbnum"):
                # Clear the contents but keep the tag to avoid layout issues
                ftbnum_anchor.clear()

            # --- New processing start ---
            # Format footnote references for better visual recognition
            # "7" becomes "〘7〙", using Unicode brackets to avoid conflicts with image references []
            for footnote_anchor in soup.find_all("a", class_="footnote"):
                if footnote_anchor.string:  # Ensure content exists
                    # Wrap original content with Unicode brackets to avoid confusion during TTS processing with image references
                    footnote_anchor.string = f"〘{footnote_anchor.string}〙"
            # --- New processing end ---

            # Replace hr tags with newlines to avoid TTS issues with "***"
            for hr_tag in soup.find_all("hr"):
                hr_tag.replace_with("\n\n")

            # Remove <ol> and <li> tags from lists that already have numbering in <span class="tcy"> elements
            # to prevent html2text from adding duplicate numbering
            for ol_tag in soup.find_all("ol"):
                # Check if all <li> elements start with <span class="tcy">number.</span>
                if all(
                    li.contents
                    and isinstance(li.contents[0], Tag)
                    and li.contents[0].name == "span"
                    and li.contents[0].get("class") == ["tcy"]
                    and re.match(r"^\d+\.$", li.contents[0].get_text(strip=True))
                    for li in ol_tag.find_all("li", recursive=False)
                ):
                    # Replace <li> with <p> to preserve structure but prevent list formatting
                    for li in ol_tag.find_all("li", recursive=False):
                        li.name = "p"
                    ol_tag.unwrap()

            return str(soup)
        except Exception as e:
            trace_log(f"[WARN] HTML preprocessing failed: {e}", self.trace)
            return html_content

    def _fallback_render(self, html_content: str, width: int) -> List[str]:
        """Fallback renderer using BeautifulSoup with improved CJK text handling."""
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "header", "footer"]):
                element.decompose()

            text = soup.get_text()

            # Clean up whitespace while preserving structure
            text = re.sub(r"\s+", " ", text)  # Normalize whitespace
            text = text.strip()

            lines = []

            # Split into paragraphs
            paragraphs = text.split("\n")

            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    lines.append("")
                    continue

                # Use the new width-aware splitting method
                paragraph_lines = self._split_text_by_width(paragraph, width)
                lines.extend(paragraph_lines)

            trace_log(f"[INFO] Fallback: {len(lines)} lines", self.trace)
            return lines

        except Exception as e:
            trace_log(f"[ERROR] Fallback renderer failed: {e}", self.trace)
            return [f"Error: Could not render chapter content. {e}"]

    # The following methods remain unchanged but are kept for completeness

    @lru_cache(maxsize=1000)
    def _get_display_width(self, text: str) -> int:
        return str_display_width(text)

    def _split_text_by_width(self, text: str, width: int) -> List[str]:
        if not text.strip():
            return [""]
        lines = []
        start = 0
        while start < len(text):
            end = self._find_split_point(text, start, width)
            lines.append(text[start:end])
            start = end
        return lines if lines else [""]

    def _find_split_point(self, text: str, start: int, max_width: int) -> int:
        left, right = start, min(start + max_width * 2, len(text))
        best = start + 1
        while left <= right:
            mid = (left + right) // 2
            width = self._get_display_width(text[start:mid])
            if width <= max_width:
                best = mid
                left = mid + 1
            else:
                right = mid - 1
        return best

    def _apply_text_wrapping(self, lines: List[str], width: int) -> List[str]:
        """Apply text wrapping to ensure all lines comply with width limit."""
        wrapped_lines = []
        for line in lines:
            if not line.strip():
                wrapped_lines.append(line)
                continue
            # Use display width aware splitting for better CJK support
            wrapped = self._split_text_by_width(line, width)
            if wrapped:
                wrapped_lines.extend(wrapped)
            else:
                wrapped_lines.append(line)  # Keep original if wrapping fails
        return wrapped_lines

    def extract_images(self, html_content: str) -> List[Tuple[str, str]]:
        """
        Extract image information from HTML content.

        Args:
            html_content: Raw HTML content

        Returns:
            List of tuples (image_src, alt_text)
        """
        images = []
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            for img in soup.find_all("img"):
                src = img.get("src", "")
                alt = img.get("alt", "")
                if src:
                    images.append((src, alt))
        except Exception as e:
            trace_log(f"[WARN] Failed to extract images: {e}", self.trace)

        return images

    def extract_text_for_tts(self, html_content: str) -> str:
        """
        Extract clean text for TTS processing with footnote filtering.

        Args:
            html_content: Raw HTML content

        Returns:
            Clean text suitable for TTS
        """
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Remove unwanted elements
            for element in soup(
                ["script", "style", "nav", "header", "footer", "aside"]
            ):
                element.decompose()

            # Remove inline footnote references (e.g.: <a class="footnote">7</a>)
            # These numbers are meaningful when reading, but inserting them in the middle of sentences when listening destroys semantics
            for element in soup.find_all("a", class_="footnote"):
                element.decompose()  # Completely remove the node and content

            # Remove superscript tags (usually also footnotes, e.g. <sup>1</sup>)
            for element in soup.find_all("sup"):
                element.decompose()

            # Remove numbering of the footnote list itself (e.g.: <a class="ftbnum">1</a>)
            # Avoid TTS reading "one... in recent years..." such list numbering
            for element in soup.find_all("a", class_="ftbnum"):
                element.decompose()

            # Handle ordered lists with existing numbering in <span class="tcy"> elements
            # to prevent TTS from reading duplicate numbers
            for ol_tag in soup.find_all("ol"):
                # Check if all <li> elements start with <span class="tcy">number.</span>
                has_tcy_numbering = True
                for li in ol_tag.find_all("li", recursive=False):
                    if not (
                        li.contents
                        and isinstance(li.contents[0], Tag)
                        and li.contents[0].name == "span"
                        and li.contents[0].get("class") == ["tcy"]
                        and re.match(r"^\d+\.$", li.contents[0].get_text(strip=True))
                    ):
                        has_tcy_numbering = False
                        break
                if has_tcy_numbering:
                    # Replace <li> with <p> to preserve structure but prevent list formatting
                    for li in ol_tag.find_all("li", recursive=False):
                        li.name = "p"
                    ol_tag.unwrap()

            # Get clean text
            text = soup.get_text()

            # Clean up whitespace and formatting
            text = re.sub(r"\s+", " ", text)  # Normalize whitespace
            # Normalize paragraph breaks
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = text.strip()

            return text

        except Exception as e:
            trace_log(f"[ERROR] Failed to extract TTS text: {e}", self.trace)
            return ""

    def get_reading_statistics(self, lines: List[str]) -> dict[str, int | float]:
        """
        Calculate reading statistics for content.

        Args:
            lines: Rendered text lines

        Returns:
            Dictionary with reading statistics
        """
        total_chars = sum(len(line) for line in lines)
        total_words = sum(len(line.split()) for line in lines if line.strip())
        non_empty_lines = sum(1 for line in lines if line.strip())

        # Rough estimates for reading time (words per minute)
        reading_wpm = 200  # Average reading speed
        estimated_minutes = max(1, total_words / reading_wpm)

        return {
            "total_lines": len(lines),
            "non_empty_lines": non_empty_lines,
            "total_characters": total_chars,
            "total_words": total_words,
            "estimated_reading_minutes": round(estimated_minutes, 1),
        }

    def get_cache_stats(self) -> Dict[str, float]:
        """Get comprehensive cache statistics for monitoring."""
        render_cache_size = (
            len(self._render_cache) if hasattr(self, "_render_cache") else 0
        )
        render_cache_max = (
            getattr(self._render_cache, "maxsize", 50)
            if hasattr(self, "_render_cache")
            else 50
        )

        total_requests = self._cache_stats["hits"] + \
            self._cache_stats["misses"]
        hit_rate = (
            (self._cache_stats["hits"] /
             total_requests) if total_requests > 0 else 0.0
        )

        return {
            "renderer_cache_size": len(self._renderer_cache),
            "renderer_cache_max": getattr(self._renderer_cache, "maxsize", 100),
            "render_cache_size": render_cache_size,
            "render_cache_max": render_cache_max,
            "render_cache_hits": self._cache_stats["hits"],
            "render_cache_misses": self._cache_stats["misses"],
            "render_cache_hit_rate": hit_rate,
            "memory_pressure_events": self._cache_stats["memory_pressure_events"],
            "total_render_operations": self._render_count,
        }

    def update_width(self, new_width: int) -> None:
        """Update the content width and clear cache."""
        if self.content_width == new_width:
            return
        self.content_width = max(20, new_width)
        # No need to clear cache explicitly. The next call to render_chapter
        # will use the new width and _get_renderer will handle it.
