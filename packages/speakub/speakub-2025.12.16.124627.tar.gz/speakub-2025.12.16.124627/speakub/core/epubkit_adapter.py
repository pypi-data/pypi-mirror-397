"""
Adapter to bridge epubkit with existing SpeakUB interfaces.
"""

import os
from typing import Any, Dict, List, Optional

import epubkit


class EPUBParserAdapter:
    """
    Adapter class that makes epubkit. EPUB compatible with
    the existing ModernEPUBParser interface used by SpeakUB.
    """

    def __init__(self, epub_path: str, trace: bool = False):
        self.epub_path = epub_path
        self.trace = trace
        self._epub: Optional[epubkit.EPUB] = None
        self._toc_data: Optional[Dict] = None

    def open(self) -> None:
        """Open the EPUB file using epubkit."""
        self._epub = epubkit.open(self.epub_path, trace=self.trace)
        # Cache TOC data for compatibility
        self._toc_data = self._epub.toc

    def read_chapter(self, src: str) -> str:
        """Read chapter content by src path."""
        if not self._epub:
            raise RuntimeError("EPUB not opened")
        return self._epub.read_chapter(src)

    def parse_toc(self) -> Dict:
        """Parse and return table of contents."""
        if not self._epub:
            raise RuntimeError("EPUB not opened")
        return self._epub.toc

    def close(self) -> None:
        """Close the EPUB and clean up resources."""
        if self._epub:
            self._epub.close()
            self._epub = None
        self._toc_data = None

    def clear_caches(self) -> None:
        """Clear any internal caches."""
        # epubkit handles its own caching, no action needed
        pass

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for compatibility."""
        return {
            "epub_path": self.epub_path,
            "cache_enabled": True,
            "toc_cached": self._toc_data is not None,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get parser statistics for compatibility."""
        if not self._epub:
            return {"error": "EPUB not opened"}

        toc = self._epub.toc
        return {
            "epub_path": self.epub_path,
            "opf_found": True,  # epubkit always finds OPF or equivalent
            "zip_files": len(self._epub.toc.get("spine_order", [])),
            "chapters_found": len(self._epub.spine),
            "toc_source": toc.get("toc_source", "unknown"),
        }

    # Context manager support
    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    # Additional compatibility methods
    @property
    def toc_data(self) -> Optional[Dict]:
        """Access to cached TOC data."""
        return self._toc_data

    def is_path_safe(self, path: str) -> bool:
        """Check if a path is safe (compatibility method)."""
        if not path:
            return False
        # Basic safety checks
        return not path.startswith('/') and '..' not in path

    def get_spine_order(self) -> List[str]:
        """Get spine order for compatibility."""
        if not self._epub:
            return []
        return [chapter.get("src", "") for chapter in self._epub.spine]

    def get_raw_chapters(self) -> List[Dict]:
        """Get raw chapters for compatibility."""
        if not self._epub:
            return []
        return self._epub.spine.copy()
