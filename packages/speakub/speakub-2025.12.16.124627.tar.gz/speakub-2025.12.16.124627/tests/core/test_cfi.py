"""
Tests for epubkit CFI functionality (used by SpeakUB)
"""

import pytest
from unittest.mock import Mock

from epubkit import (
    CFI,
    CFIGenerator,
    CFIResolver,
)
from epubkit.cfi import CFIPart


class TestCFIPart:
    """Test CFIPart class"""

    def test_cfipart_creation(self):
        """Test CFIPart object creation"""
        part = CFIPart(index=2, id="test-id", offset=10)
        assert part.index == 2
        assert part.id == "test-id"
        assert part.offset == 10
        assert part.temporal is None
        assert part.spatial == []
        assert part.text == []
        assert part.side is None

    def test_cfipart_repr(self):
        """Test CFIPart string representation"""
        part = CFIPart(index=2, id="test-id", offset=10)
        repr_str = repr(part)
        assert "CFIPart" in repr_str
        assert "index=2" in repr_str
        assert "id=test-id" in repr_str
        assert "offset=10" in repr_str


class TestCFI:
    """Test CFI class methods"""

    def test_is_cfi_valid(self):
        """Test CFI validation"""
        assert CFI.is_cfi(
            "epubcfi(/6/4[chap01]!/4[body01]/10[para05]/3:10)") is True
        assert CFI.is_cfi("invalid-cfi") is False
        assert CFI.is_cfi("epubcfi()") is True

    def test_wrap_unwrap(self):
        """Test CFI wrapping and unwrapping"""
        inner = "/6/4[chap01]!/4[body01]/10[para05]/3:10"
        wrapped = CFI.wrap(inner)
        assert wrapped == f"epubcfi({inner})"

        # Test wrapping already wrapped CFI
        already_wrapped = f"epubcfi({inner})"
        assert CFI.wrap(already_wrapped) == already_wrapped

        # Test unwrapping
        assert CFI.unwrap(wrapped) == inner
        # Unwrapping unwrapped should return as-is
        assert CFI.unwrap(inner) == inner

    def test_escape_cfi(self):
        """Test CFI character escaping"""
        test_string = "test[string]with(special)chars^caret"
        escaped = CFI.escape_cfi(test_string)
        assert "^[" in escaped
        assert "^]" in escaped
        assert "^(" in escaped
        assert "^)" in escaped
        assert "^^" in escaped  # Caret should be escaped

    def test_tokenize_simple_cfi(self):
        """Test tokenization of simple CFI"""
        cfi = "/6/4[chap01]/10:5"
        tokens = CFI.tokenize(cfi)

        expected_tokens = [
            ("/", 6),
            ("/", 4),
            ("[", "chap01"),
            ("/", 10),
            (":", 5),
        ]

        assert tokens == expected_tokens

    def test_tokenize_complex_cfi(self):
        """Test tokenization of complex CFI with indirection"""
        cfi = "/6/4[chap01]!/4[body01]/10[para05]/3:10"
        tokens = CFI.tokenize(cfi)

        # Should contain indirection marker
        assert ("!", None) in tokens

    def test_parse_tokens(self):
        """Test parsing tokens into CFI parts"""
        tokens = [
            ("/", 6),
            ("/", 4),
            ("[", "chap01"),
            ("/", 10),
            (":", 5),
        ]

        parts = CFI.parse_tokens(tokens)
        assert len(parts) == 3

        assert parts[0].index == 6
        assert parts[1].index == 4
        assert parts[1].id == "chap01"
        assert parts[2].index == 10
        assert parts[2].offset == 5

    def test_parse_simple_cfi(self):
        """Test parsing simple CFI"""
        cfi = "epubcfi(/6/4[chap01]/10:5)"
        parsed = CFI.parse(cfi)

        assert isinstance(parsed, list)
        assert len(parsed) == 1  # One path
        assert len(parsed[0]) == 3  # Three parts

    def test_parse_range_cfi(self):
        """Test parsing range CFI"""
        cfi = "epubcfi(/6/4[chap01],/6/4[chap01]/10,/6/4[chap01]/20)"
        parsed = CFI.parse(cfi)

        assert isinstance(parsed, dict)
        assert "parent" in parsed
        assert "start" in parsed
        assert "end" in parsed

    def test_part_to_string(self):
        """Test converting CFI part back to string"""
        part = CFIPart(index=4, id="chap01", offset=10)
        part_str = CFI.part_to_string(part)

        assert part_str == "/4[chap01]:10"

    def test_to_string_simple(self):
        """Test converting parsed CFI back to string"""
        # Create a simple parsed CFI
        parts = [
            CFIPart(index=6),
            CFIPart(index=4, id="chap01"),
            CFIPart(index=10, offset=5)
        ]
        parsed = [parts]

        cfi_str = CFI.to_string(parsed)
        assert cfi_str.startswith("epubcfi(")
        assert cfi_str.endswith(")")

    def test_to_string_range(self):
        """Test converting range CFI back to string"""
        parent_parts = [CFIPart(index=6), CFIPart(index=4, id="chap01")]
        start_parts = [CFIPart(index=10, offset=5)]
        end_parts = [CFIPart(index=20, offset=15)]

        parsed = {
            "parent": [parent_parts],
            "start": [start_parts],
            "end": [end_parts]
        }

        cfi_str = CFI.to_string(parsed)
        assert cfi_str.startswith("epubcfi(")
        assert "," in cfi_str  # Should contain commas for range

    def test_collapse_range_cfi(self):
        """Test collapsing range CFI to single point"""
        parent_parts = [CFIPart(index=6), CFIPart(index=4, id="chap01")]
        start_parts = [CFIPart(index=10, offset=5)]
        end_parts = [CFIPart(index=20, offset=15)]

        range_cfi = {
            "parent": [parent_parts],
            "start": [start_parts],
            "end": [end_parts]
        }

        # Collapse to start
        collapsed = CFI.collapse(range_cfi, to_end=False)
        assert len(collapsed) == 2  # parent + start
        assert collapsed[1][0].index == 10

        # Collapse to end
        collapsed = CFI.collapse(range_cfi, to_end=True)
        assert len(collapsed) == 2  # parent + end
        assert collapsed[1][0].index == 20

    def test_compare_cfi(self):
        """Test CFI comparison"""
        cfi1 = "epubcfi(/6/4[chap01]/10)"
        cfi2 = "epubcfi(/6/4[chap01]/20)"
        cfi3 = "epubcfi(/6/4[chap02]/10)"

        assert CFI.compare(cfi1, cfi2) == -1  # cfi1 < cfi2
        assert CFI.compare(cfi2, cfi1) == 1   # cfi2 > cfi1
        assert CFI.compare(cfi1, cfi1) == 0   # cfi1 == cfi1

        # Test with different chapters
        assert CFI.compare(cfi1, cfi3) == -1  # Different chapter IDs


class TestCFIGenerator:
    """Test CFIGenerator class"""

    def test_is_text_node(self):
        """Test text node detection"""
        from bs4 import NavigableString

        text_node = NavigableString("Hello world")
        assert CFIGenerator.is_text_node(text_node) is True

        # Empty text node
        empty_text = NavigableString("   ")
        assert CFIGenerator.is_text_node(empty_text) is False

    def test_is_element_node(self):
        """Test element node detection"""
        from bs4 import Tag

        # Create a mock element
        mock_element = Mock(spec=Tag)
        assert CFIGenerator.is_element_node(mock_element) is True

        # Test with non-element
        assert CFIGenerator.is_element_node("string") is False

    def test_get_child_nodes(self):
        """Test getting filtered child nodes"""
        from bs4 import BeautifulSoup, NavigableString, Tag

        html = "<div><p>Hello</p><span>World</span>   </div>"
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.div

        children = CFIGenerator.get_child_nodes(div)
        # Should include p, span (whitespace-only text node is filtered out)
        assert len(children) == 2

    def test_index_child_nodes(self):
        """Test indexing child nodes"""
        from bs4 import BeautifulSoup

        html = "<div><p>Hello</p><span>World</span></div>"
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.div

        indexed = CFIGenerator.index_child_nodes(div)

        # Should start with "before", end with "after"
        assert indexed[0] == "before"
        assert indexed[-1] == "after"
        assert len(indexed) >= 4  # before, p, span, after

    def test_clear_cache(self):
        """Test cache clearing"""
        # Add something to cache first
        from bs4 import BeautifulSoup
        html = "<div><p>test</p></div>"
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.div

        CFIGenerator.index_child_nodes(div)  # This should cache

        # Clear cache
        CFIGenerator.clear_cache()

        # Cache should be empty (though we can't easily verify this)

    def test_generate_cfi(self):
        """Test CFI generation from node"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <div id="content">
                    <p id="para1">Hello world</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        para = soup.find(id="para1")

        cfi = CFIGenerator.generate_cfi(0, para, 5)
        assert cfi.startswith("epubcfi(")
        assert cfi.endswith(")")


class TestCFIResolver:
    """Test CFIResolver class"""

    def test_resolve_simple_cfi(self):
        """Test resolving simple CFI"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <div id="content">
                    <p id="para1">Hello world</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Create a simple CFI pointing to the paragraph
        cfi = "epubcfi(/6/2[content]/4[para1])"

        result = CFIResolver.resolve_cfi(soup, cfi)

        assert result is not None
        assert "node" in result
        assert result["node"].get("id") == "para1"

    def test_resolve_invalid_cfi(self):
        """Test resolving invalid CFI"""
        from bs4 import BeautifulSoup

        html = "<html><body><p>test</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')

        result = CFIResolver.resolve_cfi(soup, "invalid-cfi")
        assert result is None

    def test_parts_to_node_with_id(self):
        """Test resolving CFI parts using element ID"""
        from bs4 import BeautifulSoup

        html = """
        <html>
            <body>
                <div id="content">
                    <p id="para1">Hello world</p>
                </div>
            </body>
        </html>
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Create parts that reference the element by ID
        parts = [CFIPart(index=2, id="content"), CFIPart(index=4, id="para1")]

        result = CFIResolver.parts_to_node(soup.html, parts)

        assert result is not None
        assert "node" in result
        assert result["node"].get("id") == "para1"


if __name__ == '__main__':
    pytest.main([__file__])
