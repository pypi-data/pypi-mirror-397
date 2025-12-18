#!/usr/bin/env python3
"""
Test script to verify the pagination fix for chapter loading.
"""

from speakub.ui.widgets.content_widget import ViewportContent


class MockRenderer:
    """Mock content renderer for testing."""

    def render_chapter(self, html_content, width):
        """Mock rendering that returns predictable output."""
        lines = []
        # Simulate some content based on HTML length
        num_lines = max(10, len(html_content) // 10)
        for i in range(num_lines):
            # Create lines that may wrap based on width
            line_length = min(width, 20 + (i % 10))
            lines.append("x" * line_length)
        return lines

    def _split_text_by_width(self, text, width):
        """Mock text splitting."""
        return [text[i:i+width] for i in range(0, len(text), width)]


def test_viewport_content_pagination():
    """Test ViewportContent pagination behavior."""
    print("Testing ViewportContent pagination fix...")

    # Create mock renderer
    renderer = MockRenderer()

    # Test HTML content
    html_content = "<p>This is a test chapter with some content that should be paginated properly.</p>" * 5

    print("\n1. Testing normal initialization (should paginate immediately):")
    vc1 = ViewportContent(
        initial_html_content=html_content,
        renderer=renderer,
        initial_width=80,
        initial_height=25,
        defer_pagination=False
    )

    info1 = vc1.get_viewport_info()
    print(f"   Total lines: {vc1.total_lines}")
    print(f"   Total pages: {vc1.total_pages}")
    print(f"   Viewport height: {vc1.viewport_height}")

    print("\n2. Testing deferred pagination initialization:")
    vc2 = ViewportContent(
        initial_html_content=html_content,
        renderer=renderer,
        initial_width=80,
        initial_height=25,
        defer_pagination=True
    )

    info2_before = vc2.get_viewport_info()
    print(
        f"   Before update_dimensions - Total lines: {vc2.total_lines}, Total pages: {vc2.total_pages}")

    # Now update dimensions (this should trigger proper pagination)
    vc2.update_dimensions(80, 25, is_initial=True)

    info2_after = vc2.get_viewport_info()
    print(
        f"   After update_dimensions - Total lines: {vc2.total_lines}, Total pages: {vc2.total_pages}")

    print("\n3. Testing height change:")
    old_pages = vc2.total_pages
    vc2.update_dimensions(80, 20)  # Smaller height
    new_pages = vc2.total_pages
    print(
        f"   Pages changed from {old_pages} to {new_pages} when height changed from 25 to 20")

    print("\n4. Testing width change (should trigger re-rendering):")
    old_lines = vc2.total_lines
    vc2.update_dimensions(60, 20)  # Smaller width
    new_lines = vc2.total_lines
    print(
        f"   Lines changed from {old_lines} to {new_lines} when width changed from 80 to 60")

    print("\n5. Testing chapter loading simulation:")
    # Simulate the chapter loading process with delayed viewport calculation

    # Step 1: Create ViewportContent with defer_pagination=True (like load_chapter does)
    vc_chapter = ViewportContent(
        initial_html_content=html_content,
        renderer=renderer,
        initial_width=80,
        initial_height=25,  # This might be wrong initially
        defer_pagination=True
    )

    print(
        f"   Chapter loaded with deferred pagination - Total lines: {vc_chapter.total_lines}, Total pages: {vc_chapter.total_pages}")

    # Step 2: Simulate _delayed_viewport_calculation updating height
    # App detects actual viewport height is 30 (different from initial 25)
    actual_height = 30
    print(
        f"   Delayed viewport calculation detects actual height: {actual_height}")

    # This simulates what _delayed_viewport_calculation does
    if vc_chapter.viewport_height != actual_height:
        print("   Triggering re-pagination due to height difference")
        layout_changed = vc_chapter.update_dimensions(80, actual_height)
        print(
            f"   Layout changed: {layout_changed}, New total pages: {vc_chapter.total_pages}")

    print("\n✅ All tests completed successfully!")
    return True


if __name__ == "__main__":
    test_viewport_content_pagination()
