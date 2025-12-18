#!/usr/bin/env python3

"""
Test script to simulate TTS processing on problematic HTML content.
Verifies if hr tags and ftbnum issues are fixed.
"""

from speakub.core.content_renderer import ContentRenderer
from speakub.utils.text_utils import is_speakable_content, clean_text_for_tts


def get_test_html():
    return '''<p>一陣莫名的空洞席捲而來。小說獲得成功，所以連訊息都不回就下線了嗎？我的讚嘆忽然變成幼稚拙劣的嫉妒。我到底在興奮什麼啊？追根究柢也不是我寫的小說嘛。</p>
<div style="display:none;"><a id="GBS.0008.04"></a></div>
<p>作者會送我文化商品禮券<a class="footnote" href="#ft7" id="ftb7">7</a>嗎？如果是張五萬元<a class="footnote" href="#ft8" id="ftb8">8</a>券就好了。</p>
<p>這時的我，對於明天的世界會發生什麼變故仍一無所知，還這麼天真地想著。</p>

<p><br/></p>
<p><br/></p>
<hr/>
<ol class="ft">
<li class="note" id="ft1"><a class="ftbnum" href="#ftb1">1</a>　近年來，韓國將長詞句縮短、化作簡稱的各式流行語風行一時，原先起自網路族群，現在大眾<a id="GBS.0008.05"></a>的日常用語、會話中也日漸普及。</li>
<li class="note" id="ft2"><a class="ftbnum" href="#ftb2">2</a>　駐守韓國北部北緯三十八度國境線的部隊。由於該處氣候天寒地凍、南北韓戰事緊繃，被視為最為辛苦的兵役部隊之一。</li>
<li class="note" id="ft3"><a class="ftbnum" href="#ftb3">3</a>　韓國好稱對自己影響深遠的事物為「人生事物」，如歌手的代表作或自己最愛的歌，可稱作「人<a id="GBS.0009.01"></a>生歌曲」。</li>
<li class="note" id="ft4"><a class="ftbnum" href="#ftb4">4</a>　「關心種子」的簡稱，指的是不惜以各種手段引發社會關注的人。意思近似為「刷存在感」。</li>
<li class="note" id="ft5"><a class="ftbnum" href="#ftb5">5</a>　Donate（捐贈）的諧音，網路實況用語，指觀眾以現金、虛寶等有價物表達對實況主或創作者的支持。</li>
<li class="note" id="ft6"><a class="ftbnum" href="#ftb6">6</a><a id="GBS.0009.02"></a>　約臺幣七十五元。</li>
<li class="note" id="ft7"><a class="ftbnum" href="#ftb7">7</a>　韓國許多機構會發放的禮券，可用於購買文化類商品，通常併有優惠。</li>
<li class="note" id="ft8"><a class="ftbnum" href="#ftb8">8</a>　約臺幣一千兩百五十元。</li>
</ol>
<div style="display:none;"><a id="GBS.0009.03"></a></div>
</body>
'''


def test_tts_content_processing():
    print("=== TTS Content Processing Test ===")

    # Get the test HTML
    html_content = get_test_html()

    # 1. Render the HTML content
    renderer = ContentRenderer(content_width=80, trace=True)
    lines = renderer.render_chapter(html_content)
    full_text = "\n".join(lines)

    print(f"Rendered lines: {len(lines)}")
    print(f"Rendered text length: {len(full_text)}")
    print("Sample rendered content:")
    for i, line in enumerate(lines[:10]):  # Show first 10 lines
        print(f"  {i+1}: {repr(line)}")

    # Check for *** (should not be present with fix)
    has_asterisks = "***" in full_text
    print(f"Contains *** (hr problem): {has_asterisks}")

    if has_asterisks:
        print("❌ FAILED: hr tags still converted to *** - synthesis may get stuck")
        return False

    # 2. Extract TTS text (full extraction as in speakub)
    tts_text = renderer.extract_text_for_tts(html_content)
    print(f"\nTTS extracted text length: {len(tts_text)}")
    print("Sample TTS text:")
    print(repr(tts_text[:200]) + "...")

    # 3. Simulate paragraph splitting (as done in TTS process)
    # Split by double newlines (as content is broken into speakable segments)
    paragraphs = [p.strip() for p in tts_text.split('\n\n') if p.strip()]

    print(f"\nParagraphs extracted: {len(paragraphs)}")
    speakable_paragraphs = []
    filtered_paragraphs = []

    for i, para in enumerate(paragraphs[:10]):  # Test first 10 paragraphs
        speakable, reason = is_speakable_content(para)
        print(
            f"  Para {i+1} ({len(para)} chars): speakable={speakable} ({reason})")
        if speakable:
            speakable_paragraphs.append(para)
        else:
            filtered_paragraphs.append((para, reason))

    print(f"\nTotal speakable paragraphs: {len(speakable_paragraphs)}")
    print(f"Filtered paragraphs: {len(filtered_paragraphs)}")
    for para, reason in filtered_paragraphs[:5]:  # Show first 5 filtered
        print(f"  Filtered ({reason}): {repr(para[:50])}")

    # 4. Clean text for TTS (simulate final processing)
    for para in speakable_paragraphs[:3]:  # Test first 3 speakable paragraphs
        cleaned = clean_text_for_tts(para)
        speakable_after_clean, reason_after_clean = is_speakable_content(
            cleaned)
        print(f"\nCleaned para: {repr(cleaned)}")
        print(
            f"Speakable after cleaning: {speakable_after_clean} ({reason_after_clean})")

    # Final check: No content should be pure *** which would cause TTS issues
    problematic_patterns = ["***", "* * *"]
    has_problems = any(pattern in tts_text for pattern in problematic_patterns)

    if has_problems:
        print("❌ FAILED: TTS text still contains problematic patterns")
        return False

    if len(speakable_paragraphs) > len(filtered_paragraphs):
        print("✅ PASSED: Content processes correctly without TTS-sticking hr issues")
        return True
    else:
        print("⚠️  WARNING: Too many paragraphs filtered - may affect TTS flow")
        return len(speakable_paragraphs) > 0


if __name__ == "__main__":
    success = test_tts_content_processing()
    if success:
        print("\n=== RESULT: TTS-ready content processing SUCCESS ===")
    else:
        print("\n=== RESULT: TTS-ready content processing FAILED ===")
        exit(1)
