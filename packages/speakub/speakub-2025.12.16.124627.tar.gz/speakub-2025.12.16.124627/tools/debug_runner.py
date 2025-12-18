#!/usr/bin/env python3
"""
SpeakUB Debug Runner (Log 目錄版)
功能：按 'x' 鍵將 TUI 畫面記憶體傾印到 ~/.config/speakub/logs/
"""

import sys
import os
import time
from pathlib import Path

# --- 1. 設定路徑 ---
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from speakub.ui.app import EPUBReaderApp
    from speakub.cli import main as cli_main
except ImportError as e:
    print(f"❌ 無法匯入 SpeakUB: {e}", file=sys.stderr)
    sys.exit(1)

# ==========================================
# 2. 核心匯出功能 (修改路徑邏輯)
# ==========================================


def dump_full_chapter(self):
    """
    匯出動作的實作。
    """
    print("🔥 [DEBUG] 觸發匯出動作！正在讀取記憶體...", file=sys.stderr)

    vc = self.viewport_content
    if not vc:
        self.notify("⚠️ 錯誤：尚未載入任何章節內容", severity="warning")
        return

    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")

        # 取得章節資訊作為檔名
        chap_title = "Unknown"
        if self.current_chapter:
            chap_title = "".join(c for c in self.current_chapter.get(
                'title', 'Chap') if c.isalnum() or c in (' ', '-', '_')).strip()

        filename = f"dump_{chap_title}_{timestamp}.txt"

        # --- 📍 修改路徑邏輯開始 ---
        # 設定目標目錄: ~/.config/speakub/logs/
        log_dir = Path.home() / ".config" / "speakub" / "logs"

        # 確保目錄存在，如果不存在就自動建立
        log_dir.mkdir(parents=True, exist_ok=True)

        output_path = log_dir / filename
        # --- 修改路徑邏輯結束 ---

        # 抓取記憶體中的內容
        lines_in_memory = vc.content_lines
        current_cursor = vc.get_cursor_global_position()

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"=== SpeakUB Chapter Memory Dump ===\n")
            f.write(f"Time: {timestamp}\n")
            f.write(f"Source: {self.current_chapter.get('src', 'Unknown')}\n")
            f.write(f"Lines: {len(lines_in_memory)}\n")
            f.write("-" * 60 + "\n")

            for idx, line in enumerate(lines_in_memory):
                pointer = ">> " if idx == current_cursor else "   "
                f.write(f"{pointer}[{idx:05d}] |{line}|\n")

        # 成功通知
        self.notify(f"已儲存至 Logs: {filename}",
                    severity="information", timeout=5)
        print(f"✅ [DEBUG] 檔案已儲存至: {output_path}", file=sys.stderr)

    except Exception as e:
        error_msg = f"匯出失敗: {e}"
        self.notify(error_msg, severity="error")
        print(f"❌ [DEBUG] {error_msg}", file=sys.stderr)

# ==========================================
# 3. 注入邏輯
# ==========================================


def inject_hooks():
    original_on_mount = EPUBReaderApp.on_mount

    async def hooked_on_mount(self):
        await original_on_mount(self)

        # 動態綁定按鍵 'x'
        self.bind("x", "debug_export", description="💾 Dump", show=True)
        self.bind("X", "debug_export", show=False)
        self.bind("f12", "debug_export", show=False)

        print(
            "🔧 [System] Debug keys injected. Press 'x' to dump text.", file=sys.stderr)

    EPUBReaderApp.on_mount = hooked_on_mount
    EPUBReaderApp.action_debug_export = dump_full_chapter

    print(f"🚀 除錯工具已啟動。", file=sys.stderr)
    print(
        f"📂 匯出路徑設定為: {Path.home() / '.config/speakub/logs/'}", file=sys.stderr)
    print("---------------------------------------------------", file=sys.stderr)

    cli_main()


if __name__ == "__main__":
    inject_hooks()
