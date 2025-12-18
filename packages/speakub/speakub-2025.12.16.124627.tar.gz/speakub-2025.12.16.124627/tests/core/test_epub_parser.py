"""
Tests for speakub.core.epubkit_adapter module
"""

import os
import tempfile
import zipfile
from unittest.mock import Mock

import pytest

from speakub.core.epubkit_adapter import EPUBParserAdapter as EPUBParser


class TestEPUBParserAdapter:
    """Test EPUBParserAdapter class"""

    def test_parser_initialization(self):
        """Test EPUBParserAdapter initialization"""
        # Create a temporary EPUB file for testing
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            parser = EPUBParser(temp_path)
            assert parser.epub_path == temp_path
            assert parser.trace is False
            assert parser._epub is None
            assert parser._toc_data is None
        finally:
            os.unlink(temp_path)

    def test_parser_initialization_with_trace(self):
        """Test EPUBParserAdapter initialization with trace enabled"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            parser = EPUBParser(temp_path, trace=True)
            assert parser.trace is True
        finally:
            os.unlink(temp_path)

    def test_context_manager(self):
        """Test context manager functionality"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            # Create a minimal valid EPUB structure
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                # Add container.xml
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                            '  <rootfiles>\n'
                            '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
                            '  </rootfiles>\n'
                            '</container>')

                # Add minimal OPF
                zf.writestr('OEBPS/content.opf',
                            '<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">\n'
                            '  <metadata>\n'
                            '    <title>Test Book</title>\n'
                            '  </metadata>\n'
                            '  <manifest>\n'
                            '    <item id="chapter1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>\n'
                            '  </manifest>\n'
                            '  <spine>\n'
                            '    <itemref idref="chapter1"/>\n'
                            '  </spine>\n'
                            '</package>')

                # Add a chapter
                zf.writestr('OEBPS/chapter1.xhtml',
                            '<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<html><body><p>Test content</p></body></html>')

        try:
            parser = EPUBParser(temp_file.name)

            # Test context manager
            with parser:
                assert parser._epub is not None
                assert parser._toc_data is not None

            # After exiting context, should be closed
            assert parser._epub is None
            assert parser._toc_data is None

        finally:
            os.unlink(temp_file.name)

    def test_cache_functionality(self):
        """Test caching functionality"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            # Create a minimal valid EPUB structure
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">\n'
                            '  <rootfiles>\n'
                            '    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>\n'
                            '  </rootfiles>\n'
                            '</container>')

                zf.writestr('OEBPS/content.opf',
                            '<?xml version="1.0" encoding="UTF-8"?>\n'
                            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">\n'
                            '  <metadata><title>Test</title></metadata>\n'
                            '  <manifest><item id="ch1" href="ch1.xhtml" media-type="application/xhtml+xml"/></manifest>\n'
                            '  <spine><itemref idref="ch1"/></spine>\n'
                            '</package>')

                zf.writestr('OEBPS/ch1.xhtml',
                            '<html><body><p>Content</p></body></html>')

        try:
            parser = EPUBParser(temp_file.name)

            with parser:
                # Test cache stats
                cache_stats = parser.get_cache_stats()

                # Verify cache stats structure
                assert isinstance(cache_stats, dict)
                assert 'epub_path' in cache_stats
                assert 'cache_enabled' in cache_stats
                assert 'toc_cached' in cache_stats

                # Test cache clearing
                parser.clear_caches()
                # epubkit handles its own caching, so no direct verification

        finally:
            os.unlink(temp_file.name)

    def test_statistics(self):
        """Test statistics functionality"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            parser = EPUBParser(temp_path)
            # Parser is not opened
            stats = parser.get_statistics()

            # Should return error for unopened EPUB
            assert isinstance(stats, dict)
            assert 'error' in stats
            assert stats['error'] == 'EPUB not opened'

        finally:
            os.unlink(temp_path)

    def test_statistics_opened(self):
        """Test statistics functionality with opened EPUB"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            # Create minimal EPUB
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0"?><container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
                zf.writestr('content.opf',
                            '<?xml version="1.0"?>\n'
                            '<package>\n'
                            '  <metadata><title>Test Book</title></metadata>\n'
                            '  <manifest>\n'
                            '    <item id="ch1" href="chapter1.xhtml"/>\n'
                            '    <item id="ch2" href="chapter2.xhtml"/>\n'
                            '  </manifest>\n'
                            '  <spine>\n'
                            '    <itemref idref="ch1"/>\n'
                            '    <itemref idref="ch2"/>\n'
                            '  </spine>\n'
                            '</package>')

        try:
            parser = EPUBParser(temp_file.name)

            with parser:
                stats = parser.get_statistics()

                # Check that basic keys are present
                expected_keys = [
                    'epub_path', 'opf_found', 'zip_files', 'chapters_found', 'toc_source'
                ]

                for key in expected_keys:
                    assert key in stats

                # Check values
                assert stats['epub_path'] == temp_file.name
                assert stats['opf_found'] is True
                assert stats['chapters_found'] == 2

        finally:
            os.unlink(temp_file.name)

    def test_read_chapter(self):
        """Test chapter reading functionality"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            # Create EPUB with a chapter
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0"?><container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
                zf.writestr('content.opf',
                            '<?xml version="1.0"?>\n'
                            '<package>\n'
                            '  <metadata><title>Test Book</title></metadata>\n'
                            '  <manifest>\n'
                            '    <item id="ch1" href="chapter1.xhtml"/>\n'
                            '  </manifest>\n'
                            '  <spine>\n'
                            '    <itemref idref="ch1"/>\n'
                            '  </spine>\n'
                            '</package>')

                zf.writestr('chapter1.xhtml',
                            '<html><body><p>Test content</p></body></html>')

        try:
            parser = EPUBParser(temp_file.name)

            with parser:
                content = parser.read_chapter('chapter1.xhtml')
                assert 'Test content' in content

        finally:
            os.unlink(temp_file.name)

    def test_toc_parsing(self):
        """Test table of contents parsing"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            # Create minimal EPUB with spine
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0"?><container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
                zf.writestr('content.opf',
                            '<?xml version="1.0"?>\n'
                            '<package>\n'
                            '  <metadata><title>Test Book</title></metadata>\n'
                            '  <manifest>\n'
                            '    <item id="ch1" href="chapter1.xhtml"/>\n'
                            '    <item id="ch2" href="chapter2.xhtml"/>\n'
                            '  </manifest>\n'
                            '  <spine>\n'
                            '    <itemref idref="ch1"/>\n'
                            '    <itemref idref="ch2"/>\n'
                            '  </spine>\n'
                            '</package>')

        try:
            parser = EPUBParser(temp_file.name)

            with parser:
                toc = parser.parse_toc()

                # Verify TOC structure
                assert isinstance(toc, dict)
                assert 'spine_order' in toc or 'chapters' in toc

        finally:
            os.unlink(temp_file.name)

    def test_compatibility_methods(self):
        """Test compatibility methods"""
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as temp_file:
            # Create minimal EPUB
            with zipfile.ZipFile(temp_file.name, 'w') as zf:
                zf.writestr('META-INF/container.xml',
                            '<?xml version="1.0"?><container><rootfiles><rootfile full-path="content.opf"/></rootfiles></container>')
                zf.writestr('content.opf',
                            '<?xml version="1.0"?>\n'
                            '<package>\n'
                            '  <metadata><title>Test Book</title></metadata>\n'
                            '  <manifest>\n'
                            '    <item id="ch1" href="chapter1.xhtml"/>\n'
                            '  </manifest>\n'
                            '  <spine>\n'
                            '    <itemref idref="ch1"/>\n'
                            '  </spine>\n'
                            '</package>')

        try:
            parser = EPUBParser(temp_file.name)

            with parser:
                # Test compatibility methods
                assert parser.is_path_safe('chapter1.xhtml') is True
                assert parser.is_path_safe('../etc/passwd') is False

                spine_order = parser.get_spine_order()
                assert isinstance(spine_order, list)
                assert len(spine_order) > 0

                raw_chapters = parser.get_raw_chapters()
                assert isinstance(raw_chapters, list)
                assert len(raw_chapters) > 0

        finally:
            os.unlink(temp_file.name)


if __name__ == '__main__':
    pytest.main([__file__])
