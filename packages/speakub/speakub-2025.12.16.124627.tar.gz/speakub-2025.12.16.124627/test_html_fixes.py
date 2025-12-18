#!/usr/bin/env python3

from speakub.core.content_renderer import ContentRenderer

# Test HTML with hr and ftbnum issues
html_content = """<p>一陣莫名的空洞席捲而來。小說獲得成功，所以連訊息都不回就下線了嗎？我的讚嘆忽然變成幼稚拙劣的嫉妒。我到底在興奮什麼啊？追根究柢也不是我寫的小說嘛。</p>
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
</html>"""

renderer = ContentRenderer(content_width=80, trace=True)
lines = renderer.render_chapter(html_content)
print("Rendered output:")
for i, line in enumerate(lines):
    print(f"{i+1:2d}: {repr(line)}")
