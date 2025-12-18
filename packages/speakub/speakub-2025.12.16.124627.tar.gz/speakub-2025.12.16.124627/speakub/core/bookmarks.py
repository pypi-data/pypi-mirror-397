#!/usr/bin/env python3
"""
Bookmark management for SpeakUB.
Handles bookmark data structure, storage, and retrieval.
"""

import json
import logging
import os
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from speakub.utils.config import CONFIG_DIR

logger = logging.getLogger(__name__)

BOOKMARK_FILE = os.path.join(CONFIG_DIR, "bookmarks.json")


@dataclass
class Bookmark:
    """Data model for a single bookmark."""

    id: str
    epub_path: str
    epub_title: str
    chapter_title: str
    chapter_src: str
    display_position: str  # e.g., "Line 245"
    global_line_position: int
    cfi: Optional[str]
    created_at: str  # ISO format string

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Bookmark":
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BookmarkManager:
    """Manages bookmark CRUD operations."""

    def __init__(self):
        self.bookmarks: List[Bookmark] = []
        self.load_bookmarks()

    def load_bookmarks(self) -> None:
        """Load bookmarks from JSON file."""
        if not os.path.exists(BOOKMARK_FILE):
            self.bookmarks = []
            return

        try:
            with open(BOOKMARK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Handle versioning if needed, for now assume simple list structure
                raw_list = data.get("bookmarks", [])
                self.bookmarks = [Bookmark.from_dict(item) for item in raw_list]
            logger.debug(f"Loaded {len(self.bookmarks)} bookmarks")
        except Exception as e:
            logger.error(f"Failed to load bookmarks: {e}")
            self.bookmarks = []

    def save_bookmarks(self) -> None:
        """Save bookmarks to JSON file."""
        try:
            os.makedirs(CONFIG_DIR, exist_ok=True)
            data = {
                "version": "1.0",
                "bookmarks": [b.to_dict() for b in self.bookmarks],
            }
            with open(BOOKMARK_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("Bookmarks saved successfully")
        except Exception as e:
            logger.error(f"Failed to save bookmarks: {e}")

    def add_bookmark(
        self,
        epub_path: str,
        epub_title: str,
        chapter_title: str,
        chapter_src: str,
        global_line: int,
        cfi: Optional[str],
    ) -> Bookmark:
        """Create and save a new bookmark."""

        bookmark = Bookmark(
            id=str(uuid.uuid4()),
            epub_path=str(epub_path),
            epub_title=epub_title,
            chapter_title=chapter_title,
            chapter_src=chapter_src,
            display_position=f"Line {global_line + 1}",
            global_line_position=global_line,
            cfi=cfi,
            created_at=datetime.now().isoformat(),
        )

        # Insert at the beginning (newest first)
        self.bookmarks.insert(0, bookmark)
        self.save_bookmarks()
        return bookmark

    def delete_bookmark(self, bookmark_id: str) -> bool:
        """Delete a bookmark by ID."""
        original_len = len(self.bookmarks)
        self.bookmarks = [b for b in self.bookmarks if b.id != bookmark_id]

        if len(self.bookmarks) < original_len:
            self.save_bookmarks()
            return True
        return False

    def get_bookmarks_for_file(self, epub_path: str) -> List[Bookmark]:
        """Get all bookmarks for a specific EPUB file."""
        # Normalize path for comparison
        target_path = str(epub_path)
        return [b for b in self.bookmarks if str(b.epub_path) == target_path]


# Global instance
bookmark_manager = BookmarkManager()
