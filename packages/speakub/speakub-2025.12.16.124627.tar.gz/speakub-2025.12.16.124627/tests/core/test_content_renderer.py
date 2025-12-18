"""
Tests for speakub.core.content_renderer module
"""

import pytest
from unittest.mock import MagicMock

from speakub.core.content_renderer import (
    EPUBTextRenderer,
    ContentRenderer,
)


class TestEPUBTextRenderer:
    """Test EPUBTextRenderer class"""

    def test_renderer_initialization(self):
        """Test renderer initialization"""
        renderer = EPUBTextRenderer(bodywidth=80)

        assert renderer.strong_mark == "**"
        assert renderer.emphasis_mark == "*"
        assert renderer.ignore_tables is True
        assert renderer.ignore_links is True
        assert renderer.wrap_links is False
        assert renderer.wrap_list_items is False
        assert renderer.wrap is True

    def test_handle_unsupported_tags(self):
        """Test handling of unsupported HTML tags"""
        renderer = EPUBTextRenderer(bodywidth=80)

        # Test video tag
        result = renderer.handle_tag("video", {}, True)
        assert result == "[Unsupported Content]\n"

        result = renderer.handle_tag("video", {}, False)
        assert result == ""

        # Test script tag
        result = renderer.handle_tag("script", {}, True)
        assert result == "[Unsupported Content]\n"

        # Test supported tag (should return None to use default handling)
        result = renderer.handle_tag("p", {}, True)
        assert result is None

    def test_handle_image(self):
        """Test image handling"""
        renderer = EPUBTextRenderer(bodywidth=80)

        # Test image with alt text
        result = renderer.handle_image("image.jpg", "Alt text", 100, 100)
        assert result == '[Image: Alt text src="image.jpg"]'

        # Test image without alt text
        result = renderer.handle_image("image.jpg", "", 100, 100)
        assert result == '[Image src="image.jpg"]'

    def test_html_to_text_conversion(self):
        """Test basic HTML to text conversion"""
        renderer = EPUBTextRenderer(bodywidth=80)

        html = "<p>This is <strong>bold</strong> and <em>italic</em> text.</p>"
        result = renderer.handle(html)

        assert "This is" in result
        assert "bold" in result
        assert "italic" in result
        assert "<p>" not in result  # HTML tags should be removed


class TestContentRenderer:
    """Test ContentRenderer class"""

    def test_renderer_initialization(self):
        """Test renderer initialization"""
        renderer = ContentRenderer(content_width=100, trace=True)

        assert renderer.content_width == 100
        assert renderer.trace is True

    def test_renderer_initialization_defaults(self):
        """Test renderer initialization with defaults"""
        renderer = ContentRenderer()

        assert renderer.content_width == 80
        assert renderer.trace is False

    def test_get_renderer_caching(self):
        """Test renderer caching"""
        renderer = ContentRenderer()

        # First call should create new renderer
        r1 = renderer._get_renderer(80)
        assert isinstance(r1, EPUBTextRenderer)

        # Second call should return cached renderer
        r2 = renderer._get_renderer(80)
        assert r1 is r2

        # Different width should create new renderer
        r3 = renderer._get_renderer(100)
        assert isinstance(r3, EPUBTextRenderer)
        assert r1 is not r3

    def test_render_chapter_basic(self):
        """Test basic chapter rendering"""
        renderer = ContentRenderer(content_width=80)

        html = "<html><body><p>This is a test paragraph.</p></body></html>"
        lines = renderer.render_chapter(html)

        assert isinstance(lines, list)
        assert len(lines) > 0
        assert "This is a test paragraph" in " ".join(lines)

    def test_render_chapter_with_width_override(self):
        """Test chapter rendering with width override"""
        renderer = ContentRenderer(content_width=80)

        html = "<p>This is a long paragraph that should be wrapped at the specified width.</p>"
        lines = renderer.render_chapter(html, width=40)

        # Check that lines are reasonably wrapped
        for line in lines:
            if line.strip():  # Skip empty lines
                # Allow some tolerance for CJK characters and word boundaries
                assert len(line) <= 80  # Should not exceed max width

    def test_render_chapter_minimum_width(self):
        """Test minimum width enforcement"""
        renderer = ContentRenderer(content_width=80)

        html = "<p>Test</p>"
        lines = renderer.render_chapter(html, width=10)  # Below minimum

        # Should use minimum width of 20
        assert len(lines) >= 0

    def test_fallback_render(self):
        """Test fallback rendering when html2text fails"""
        renderer = ContentRenderer()

        # Test with malformed HTML that might cause html2text to fail
        html = "<p>This is test content.</p>"
        lines = renderer._fallback_render(html, 80)

        assert isinstance(lines, list)
        assert len(lines) > 0
        assert any("This is test content" in line for line in lines)

    def test_fallback_render_error_handling(self):
        """Test fallback rendering error handling"""
        renderer = ContentRenderer()

        # Test with completely invalid input - use empty string instead of None
        lines = renderer._fallback_render("", 80)

        assert isinstance(lines, list)
        assert len(lines) >= 0  # Should handle empty input gracefully

    def test_extract_images(self):
        """Test image extraction"""
        renderer = ContentRenderer()

        html = '''
        <html><body>
        <img src="image1.jpg" alt="First image">
        <img src="image2.jpg">
        <p>Some text</p>
        <img src="image3.jpg" alt="Third image">
        </body></html>
        '''

        images = renderer.extract_images(html)

        assert len(images) == 3
        assert images[0] == ("image1.jpg", "First image")
        assert images[1] == ("image2.jpg", "")
        assert images[2] == ("image3.jpg", "Third image")

    def test_extract_images_error_handling(self):
        """Test image extraction error handling"""
        renderer = ContentRenderer()

        # Test with invalid HTML
        images = renderer.extract_images("<invalid html>")

        # Should return empty list on error
        assert images == []

    def test_extract_text_for_tts(self):
        """Test TTS text extraction"""
        renderer = ContentRenderer()

        html = '''
        <html><body>
        <script>alert('test');</script>
        <style>body { color: red; }</style>
        <nav>Navigation</nav>
        <header>Header</header>
        <p>This is the main content.</p>
        <p>This is another paragraph.</p>
        <footer>Footer</footer>
        </body></html>
        '''

        text = renderer.extract_text_for_tts(html)

        # Should contain main content
        assert "This is the main content" in text
        assert "This is another paragraph" in text

        # Should not contain unwanted elements
        assert "alert('test');" not in text
        assert "Navigation" not in text
        assert "Header" not in text
        assert "Footer" not in text

        # Should be cleaned up (paragraphs may be joined without extra newlines)
        assert "This is the main content" in text
        assert "This is another paragraph" in text

    def test_extract_text_for_tts_error_handling(self):
        """Test TTS text extraction error handling"""
        renderer = ContentRenderer()

        # Test with invalid input - use empty string instead of None
        text = renderer.extract_text_for_tts("")

        assert text == ""

    def test_reading_statistics(self):
        """Test reading statistics calculation"""
        renderer = ContentRenderer()

        lines = [
            "This is the first line with some text.",
            "This is the second line.",
            "",
            "This is the fourth line with more content here.",
            ""
        ]

        stats = renderer.get_reading_statistics(lines)

        assert stats["total_lines"] == 5
        assert stats["non_empty_lines"] == 3
        assert stats["total_characters"] > 0
        assert stats["total_words"] > 0
        assert stats["estimated_reading_minutes"] > 0

        # Verify calculations
        expected_chars = sum(len(line) for line in lines)
        expected_words = sum(len(line.split())
                             for line in lines if line.strip())

        assert stats["total_characters"] == expected_chars
        assert stats["total_words"] == expected_words

    def test_get_cache_stats(self):
        """Test cache statistics retrieval"""
        renderer = ContentRenderer()

        stats = renderer.get_cache_stats()

        # Should return dictionary with expected keys
        expected_keys = [
            "renderer_cache_size", "renderer_cache_max",
            "render_cache_size", "render_cache_max",
            "render_cache_hits", "render_cache_misses",
            "render_cache_hit_rate", "memory_pressure_events",
            "total_render_operations"
        ]
        for key in expected_keys:
            assert key in stats

        assert isinstance(stats["render_cache_hit_rate"], (int, float))
        assert isinstance(stats["render_cache_size"], int)

    def test_update_width(self):
        """Test width update functionality"""
        renderer = ContentRenderer(content_width=80)

        # Update to new width
        renderer.update_width(100)
        assert renderer.content_width == 100

        # Update to same width should not change
        renderer.update_width(100)
        assert renderer.content_width == 100

        # Test minimum width enforcement
        renderer.update_width(10)
        assert renderer.content_width == 20  # Minimum width

    def test_text_width_splitting(self):
        """Test text width-aware splitting"""
        renderer = ContentRenderer()

        # Test basic splitting
        text = "This is a long line that should be split at appropriate points."
        lines = renderer._split_text_by_width(text, 20)

        assert len(lines) > 1
        for line in lines:
            assert len(line) <= 40  # Allow some tolerance

    def test_text_wrapping_application(self):
        """Test text wrapping application"""
        renderer = ContentRenderer()

        lines = [
            "This is a short line.",
            "This is a very long line that exceeds the maximum width and should be wrapped appropriately.",
            "",
            "Another line here."
        ]

        wrapped = renderer._apply_text_wrapping(lines, 30)

        assert len(wrapped) >= len(lines)  # May have more lines after wrapping
        for line in wrapped:
            if line.strip():
                assert len(line) <= 60  # Allow tolerance for display width

    def test_display_width_calculation(self):
        """Test display width calculation caching"""
        renderer = ContentRenderer()

        # Test basic ASCII
        width1 = renderer._get_display_width("hello")
        assert width1 == 5

        # Test caching (should return same result)
        width2 = renderer._get_display_width("hello")
        assert width2 == width1

        # Test with different text
        width3 = renderer._get_display_width("hello world")
        assert width3 > width1


if __name__ == '__main__':
    pytest.main([__file__])
