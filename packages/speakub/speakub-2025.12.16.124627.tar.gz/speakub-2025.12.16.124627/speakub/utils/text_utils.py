#!/usr/bin/env python3
"""
Text processing utilities.
"""

import re
import unicodedata
from functools import lru_cache
from typing import Dict

from wcwidth import wcswidth

from speakub.utils.config import load_pronunciation_corrections

# Pre-compiled regex patterns for better performance
_CONTROL_CHARS_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
_WHITESPACE_PATTERN = re.compile(r"[ \t]+")
_MULTIPLE_NEWLINES_PATTERN = re.compile(r"\n\s*\n\s*\n+")
_IMAGE_REF_PATTERN = re.compile(r"\[Image[^\]]*\]")
_UNSUPPORTED_CONTENT_PATTERN = re.compile(r"\[.*?Content\]")
_BOLD_PATTERN = re.compile(r"\*\*(.*?)\*\*")
_ITALIC_PATTERN = re.compile(r"\*(.*?)\*")
_UNDERLINE_PATTERN = re.compile(r"_{2,}")
_MULTIPLE_DOTS_PATTERN = re.compile(r"[.]{3,}")
_MULTIPLE_DASHES_PATTERN = re.compile(r"[-]{3,}")
_SENTENCE_PAUSE_PATTERN = re.compile(r"([.!?])\s*\n\s*")
_COLON_PAUSE_PATTERN = re.compile(r":\s*\n")
_MARKDOWN_CHARS_PATTERN = re.compile(r"[#*_`]+")
_CHAPTER_PREFIX_PATTERN = re.compile(
    r"^(Chapter\s+\d+[:\-\s]*)", re.IGNORECASE)
_CHINESE_CHAPTER_PREFIX_PATTERN = re.compile(r"^(第\s*\d+\s*[章节][:\-\s]*)")
_SENTENCE_ENDINGS_PATTERN = re.compile(r"[.!?]+")

# --- New Pattern Added ---
# Matches footnote reference format like 〘1〙, 〘12〙, 〘999〙 (using Unicode brackets to avoid confusion with image references [])
_FOOTNOTE_REF_PATTERN = re.compile(r"〘\d+〙")

# Load user-defined correction dictionary
_corrections_map: Dict[str, str] = load_pronunciation_corrections()

# Core logic: Pre-process sorted correction keys at module load time
# Sort keys by length from longest to shortest
_sorted_correction_keys = sorted(
    _corrections_map.keys(), key=len, reverse=True)


class TrieNode:
    """Trie node for efficient string matching and replacement."""

    def __init__(self):
        self.children = {}
        self.replacement = None
        self.is_end = False


class CorrectionTrie:
    """Trie-based data structure for efficient pronunciation corrections."""

    def __init__(self):
        self.root = TrieNode()
        self._build_trie()

    def _build_trie(self):
        """Build the trie from the corrections map."""
        for key, replacement in _corrections_map.items():
            node = self.root
            for char in key:
                if char not in node.children:
                    node.children[char] = TrieNode()
                node = node.children[char]
            node.is_end = True
            node.replacement = replacement

    def find_and_replace(self, text: str) -> str:
        """
        Find all correction patterns in text and replace them efficiently.

        Args:
            text: Input text to process

        Returns:
            Text with corrections applied
        """
        if not text:
            return text

        result = []
        i = 0
        text_len = len(text)

        while i < text_len:
            # Try to find the longest matching pattern starting at position i
            match_found = False
            match_length = 0
            replacement = None

            # Start from root and traverse
            node = self.root
            j = i

            while j < text_len and node:
                char = text[j]
                if char in node.children:
                    node = node.children[char]
                    j += 1

                    # Check if we have a complete match
                    if node.is_end:
                        match_found = True
                        match_length = j - i
                        replacement = node.replacement
                else:
                    break

            if match_found and replacement is not None:
                # Apply the replacement
                result.append(replacement)
                i += match_length
            else:
                # No match, append current character
                result.append(text[i])
                i += 1

        return "".join(result)


# Global trie instance for efficient corrections
_correction_trie = CorrectionTrie()


def trace_log(message: str, enabled: bool) -> None:
    """
    Print trace message if tracing is enabled.

    Args:
        message: Message to log
        enabled: Whether tracing is enabled
    """
    if enabled:
        print(message)


def str_display_width(text: str) -> int:
    """
    Get the display width of a string, handling Unicode characters.

    Args:
        text: Text to measure

    Returns:
        Display width in terminal columns
    """
    if not text:
        return 0

    width = wcswidth(text)
    return width if width is not None and width >= 0 else len(text)


def truncate_str_by_width(text: str, max_width: int) -> str:
    """
    Truncate string to fit within specified display width.

    Args:
        text: Text to truncate
        max_width: Maximum display width

    Returns:
        Truncated text
    """
    if not text or max_width <= 0:
        return ""

    if str_display_width(text) <= max_width:
        return text

    # Binary search for the right length
    left, right = 0, len(text)
    result = ""

    while left <= right:
        mid = (left + right) // 2
        substring = text[:mid]
        width = str_display_width(substring)

        if width <= max_width:
            result = substring
            left = mid + 1
        else:
            right = mid - 1

    return result


def format_reading_time(minutes: float) -> str:
    """
    Format reading time in a human-readable format.

    Args:
        minutes: Reading time in minutes

    Returns:
        Formatted time string
    """
    if minutes < 1:
        return "< 1 min"
    elif minutes < 60:
        return f"{int(minutes)} min"
    else:
        hours = int(minutes // 60)
        remaining_mins = int(minutes % 60)
        if remaining_mins == 0:
            return f"{hours}h"
        else:
            return f"{hours}h {remaining_mins}m"


def clean_text_for_display(text: str) -> str:
    """
    Clean text for display by normalizing whitespace and removing control characters.

    Args:
        text: Raw text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Remove control characters except newlines and tabs
    text = _CONTROL_CHARS_PATTERN.sub("", text)

    # Normalize whitespace
    # Multiple spaces/tabs to single space
    text = _WHITESPACE_PATTERN.sub(" ", text)
    # Multiple newlines to double
    text = _MULTIPLE_NEWLINES_PATTERN.sub("\n\n", text)

    return text.strip()


def clean_text_for_tts(text: str) -> str:
    """
    Clean text specifically for TTS processing.

    Args:
        text: Raw text

    Returns:
        Text suitable for TTS
    """
    if not text:
        return ""

    # Remove image references and other non-readable elements
    text = _IMAGE_REF_PATTERN.sub("", text)
    text = _UNSUPPORTED_CONTENT_PATTERN.sub("", text)  # [Unsupported Content]

    # --- Fix Added ---
    # Remove visual footnote references (e.g., [7], [8])
    # This solves the problem of including visual markers when capturing content from screen text
    text = _FOOTNOTE_REF_PATTERN.sub("", text)
    # --- Fix Ended ---

    # Clean up markdown-style formatting
    text = _BOLD_PATTERN.sub(r"\1", text)  # **bold** -> text
    text = _ITALIC_PATTERN.sub(r"\1", text)  # *italic* -> text
    text = _UNDERLINE_PATTERN.sub("", text)  # Remove underlines

    # Clean up excessive punctuation
    text = _MULTIPLE_DOTS_PATTERN.sub("...", text)  # Multiple dots
    text = _MULTIPLE_DASHES_PATTERN.sub("---", text)  # Multiple dashes

    # Normalize whitespace
    text = clean_text_for_display(text)

    # Add pauses for better TTS flow
    # Pause after sentences at line end
    text = _SENTENCE_PAUSE_PATTERN.sub(r"\1\n\n", text)
    text = _COLON_PAUSE_PATTERN.sub(":\n\n", text)  # Pause after colons

    return text


def extract_title_from_text(text: str, max_length: int = 50) -> str:
    """
    Extract a suitable title from text content.

    Args:
        text: Text content
        max_length: Maximum title length

    Returns:
        Extracted title
    """
    if not text:
        return "Untitled"

    lines = text.strip().split("\n")

    # Look for the first non-empty line as title
    for line in lines:
        line = line.strip()
        if line:
            # Clean up the title
            title = _MARKDOWN_CHARS_PATTERN.sub("", line)  # Remove markdown
            title = title.strip()

            if title:
                return truncate_str_by_width(title, max_length)

    return "Untitled"


def word_wrap(text: str, width: int, indent: int = 0) -> list[str]:
    """
    Wrap text to specified width with optional indentation.

    Args:
        text: Text to wrap
        width: Maximum line width
        indent: Indentation for wrapped lines

    Returns:
        List of wrapped lines
    """
    if not text or width <= 0:
        return []

    words = text.split()
    lines: list[str] = []
    current_line: list[str] = []
    current_length = 0
    indent_str = " " * indent

    for word in words:
        word_length = str_display_width(word)

        # Check if word fits on current line
        spaces_needed = len(current_line)  # spaces between words
        line_indent = indent if lines else 0  # first line might not be indented

        if current_length + spaces_needed + word_length + line_indent <= width:
            current_line.append(word)
            current_length += word_length
        else:
            # Finish current line and start new one
            if current_line:
                prefix = indent_str if lines else ""  # indent continuation lines
                lines.append(prefix + " ".join(current_line))

            # Handle very long words
            if word_length > width - indent:
                # Split the word
                while word:
                    max_chars = width - indent
                    if len(word) <= max_chars:
                        current_line = [word]
                        current_length = word_length
                        break
                    else:
                        # Find good break point
                        break_point = max_chars
                        lines.append(indent_str + word[:break_point])
                        word = word[break_point:]

                current_line = []
                current_length = 0
            else:
                current_line = [word]
                current_length = word_length

    # Add final line
    if current_line:
        prefix = indent_str if lines else ""
        lines.append(prefix + " ".join(current_line))

    return lines


def normalize_chapter_title(title: str) -> str:
    """
    Normalize chapter title for consistent display.

    Args:
        title: Raw chapter title

    Returns:
        Normalized title
    """
    if not title:
        return "Untitled Chapter"

    # Remove excessive whitespace
    title = " ".join(title.split())

    # Remove common prefixes that might be redundant
    title = _CHAPTER_PREFIX_PATTERN.sub("", title)
    # Remove Chinese chapter prefixes (e.g., "Chapter 1", "Section 2")
    title = _CHINESE_CHAPTER_PREFIX_PATTERN.sub("", title)

    # Clean up remaining text
    title = title.strip(" :-")

    return title if title else "Untitled Chapter"


def extract_reading_level(text: str) -> dict[str, float | int | str]:
    """
    Estimate reading level and complexity of text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with reading statistics
    """
    if not text:
        return {
            "words": 0,
            "sentences": 0,
            "avg_word_length": 0,
            "complexity": "unknown",
        }

    # Count words and sentences
    words = len(text.split())
    sentences = len(_SENTENCE_ENDINGS_PATTERN.findall(text))

    if words == 0:
        return {
            "words": 0,
            "sentences": 0,
            "avg_word_length": 0,
            "complexity": "unknown",
        }

    # Calculate average word length
    word_lengths = [len(word.strip(".,!?;:")) for word in text.split()]
    avg_word_length = sum(word_lengths) / \
        len(word_lengths) if word_lengths else 0

    # Simple complexity estimation
    if sentences == 0:
        words_per_sentence = 0
    else:
        words_per_sentence = words / sentences

    # Rough complexity categories
    if avg_word_length < 4 and words_per_sentence < 15:
        complexity = "easy"
    elif avg_word_length < 6 and words_per_sentence < 20:
        complexity = "medium"
    else:
        complexity = "hard"

    return {
        "words": words,
        "sentences": sentences,
        "avg_word_length": float(round(avg_word_length, 1)),
        "words_per_sentence": float(round(words_per_sentence, 1)),
        "complexity": complexity,
    }


def is_speakable_content(text: str) -> tuple[bool, str]:
    """
    Check if text contains speakable characters.

    Considers content speakable if it contains ANY alphanumeric characters
    or CJK (Chinese, Japanese, Korean) characters.

    Only considers content non-speakable if it contains NO letters, numbers,
    or CJK characters at all (pure punctuation/symbols only).
    """
    import re

    if not text:
        return False, "empty_content"

    # Step 1: Find all characters that match our broad pattern
    # This includes full-width characters, but we'll filter them in step 2
    broad_pattern = re.compile(
        r"[a-zA-Z0-9\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af\uff00-\uffef]+"
    )
    broad_matches = broad_pattern.findall(text)

    if not broad_matches:
        return False, "no_speakable_characters"

    # Step 2: Filter matches to only include truly speakable characters
    # Exclude punctuation marks, brackets, etc. even if they're full-width
    truly_speakable_chars = []
    for match in broad_matches:
        # Check each character in the match
        speakable_in_match = []
        for char in match:
            category = unicodedata.category(char)
            # Only allow letters (L*), numbers (Nd), and CJK characters
            # Exclude punctuation (Po, Ps, Pe, Pc, etc.) and symbols
            if (
                category.startswith("L")
                or category == "Nd"  # Letters
                or "\u4e00" <= char <= "\u9fff"  # Decimal numbers
                or "\u3040" <= char <= "\u309f"  # CJK Unified Ideographs
                # Katakana (exclude punctuation)
                or ("\u30a0" <= char <= "\u30ff" and not category.startswith("P"))
                or "\uac00" <= char <= "\ud7af"  # Korean syllables
            ):
                speakable_in_match.append(char)

        if speakable_in_match:
            truly_speakable_chars.append("".join(speakable_in_match))

    if not truly_speakable_chars:
        return False, "no_speakable_characters"

    # Step 3: Simple logic - if there are ANY alphanumeric/CJK characters, consider speakable
    has_any_text_content = False
    for match in truly_speakable_chars:
        for char in match:
            # Check if character is alphanumeric or CJK
            if (
                char.isalnum()
                or  # Letters and numbers
                # CJK Unified Ideographs (Chinese)
                "\u4e00" <= char <= "\u9fff"
                or "\u3040" <= char <= "\u309f"
                or "\u30a0" <= char <= "\u30ff"  # Hiragana (Japanese)
                or "\uac00" <= char <= "\ud7af"  # Katakana (Japanese)
            ):  # Korean syllables
                has_any_text_content = True
                break
        if has_any_text_content:
            break

    if has_any_text_content:
        return True, "has_speakable_characters"

    # If no text content at all, consider non-speakable
    return False, "no_text_content_only_symbols"


def analyze_punctuation_content(text: str) -> tuple[str, float]:
    """
    Analyze punctuation-only content to determine appropriate pause duration.

    Args:
        text: Text containing only punctuation/symbols

    Returns:
        tuple: (pause_type, duration_seconds)
            pause_type: "fixed_pause"
            duration_seconds: Fixed pause duration of 1.5 seconds
    """
    if not text:
        return "none", 0.0

    # Fixed pause duration for all punctuation content
    return "fixed_pause", 1.5


@lru_cache(maxsize=5000)
def str_display_width(text: str) -> int:
    """
    Get the display width of a string, handling Unicode characters.
    CPU Optimization: Increased cache size for better performance with CJK text.

    Args:
        text: Text to measure

    Returns:
        Display width in terminal columns
    """
    if not text:
        return 0

    width = wcswidth(text)
    return width if width is not None and width >= 0 else len(text)


@lru_cache(maxsize=1000)
def correct_chinese_pronunciation(text: str) -> str:
    """
    Correct Chinese pronunciation using Trie-based efficient string replacement.

    Uses Unicode NFC normalization to handle composed/decomposed forms.
    CPU Optimization: Replaced O(N*M) string replacement with O(N) Trie-based matching.
    """
    if not text:
        return text

    # Normalize text to NFC form to handle composed/decomposed Unicode
    normalized_text = unicodedata.normalize("NFC", text)

    # Use efficient Trie-based replacement
    corrected_text = _correction_trie.find_and_replace(normalized_text)

    return corrected_text
