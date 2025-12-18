#!/usr/bin/env python3
"""
Test script for the ordered list numbering fix.
"""

from speakub.core.content_renderer import ContentRenderer

# Sample HTML with the problematic pattern
test_html = """
<p>Here is a list:</p>
<ol>
<li><span class="tcy">1.</span>所有地鐵站的「旗座」皆有可供占據的「旗幟」。<br/>
＊唯有各站「代表」能持有旗幟。</li>
<li><span class="tcy">2.</span>必須防範其他地鐵站隊伍並守護旗座。若站內旗座被插入他站隊伍之旗幟，地鐵站即遭搶奪，且被搶奪隊伍之待遇將由占領該旗座的<a id="GBS.0385.01"></a>隊伍任意決定。</li>
<li><span class="tcy">3.</span>可以將旗幟插入其他地鐵站的旗座之中。唯地鐵站代表擁有插旗權限，若代表因武力衝突死亡，則權限轉讓給首位拿到旗幟的成員。若旗幟遭到其他地鐵站搶奪，被搶奪隊伍之待遇將由奪走該旗幟的隊伍任意決定。</li>
</ol>
<p>End of test.</p>
"""


def test_ol_fix():
    renderer = ContentRenderer(trace=True)

    print("=== Testing problematic OL with TCY spans ===")
    # First, test the preprocessing
    processed_html = renderer._preprocess_html_for_parsing(test_html)
    print("Processed HTML:")
    print(processed_html)
    print("\n" + "="*50 + "\n")

    # Then render
    lines = renderer.render_chapter(test_html)

    print("Rendered output:")
    for line in lines:
        print(repr(line))

    # Check if there are any lines starting with numbers that would indicate duplicate numbering
    duplicate_found = False
    for line in lines:
        if line.strip().startswith(('1. ', '2. ', '3. ')):
            print(f"Potential duplicate numbering found: {line}")
            duplicate_found = True

    if not duplicate_found:
        print("No duplicate numbering detected - fix appears to work!")
    else:
        print("Duplicate numbering still present.")

    print("\n" + "="*60 + "\n")

    # Test normal OL without TCY spans
    normal_ol_html = """
<p>Normal list:</p>
<ol>
<li>First item</li>
<li>Second item</li>
<li>Third item</li>
</ol>
<p>End.</p>
"""

    print("=== Testing normal OL (should remain as list) ===")
    processed_normal = renderer._preprocess_html_for_parsing(normal_ol_html)
    print("Processed HTML:")
    print(processed_normal)
    print("\n" + "="*50 + "\n")

    normal_lines = renderer.render_chapter(normal_ol_html)
    print("Rendered output:")
    for line in normal_lines:
        print(repr(line))

    # Check if normal list still has numbering
    has_numbering = any(
        "1." in line or "2." in line or "3." in line for line in normal_lines)
    if has_numbering:
        print("Normal list numbering preserved - no regression!")
    else:
        print("Normal list numbering lost - regression detected!")


if __name__ == "__main__":
    test_ol_fix()
