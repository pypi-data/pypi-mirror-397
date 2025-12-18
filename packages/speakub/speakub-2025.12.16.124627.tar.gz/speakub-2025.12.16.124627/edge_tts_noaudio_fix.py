#!/usr/bin/env python3
"""
修復 Edge-TTS NoAudioReceived 錯誤處理，讓純標點符號內容不會記錄為 ERROR
"""

from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))


def fix_edge_tts_noaudio_error_handling():
    """
    修復 EdgeTTSProvider 中的 NoAudioReceived 錯誤處理邏輯
    """
    print("修復 Edge-TTS NoAudioReceived 錯誤處理")
    print("=" * 50)

    # 問題分析
    print("問題分析：")
    print("- 當 Edge-TTS 收到純標點符號內容時，返回 'No audio received' 錯誤")
    print("- 這個錯誤被記錄為 ERROR 等級，但實際上是預期的行為")
    print("- 對於純標點符號內容，應該視為正常情況，不記錄錯誤")
    print()

    # 修復建議
    print("修復建議：")
    print("1. 在 EdgeTTSProvider.synthesize() 中添加 NoAudioReceived 錯誤的特殊處理")
    print("2. 檢查內容是否為純標點符號，如果是則不記錄為錯誤")
    print("3. 只對包含可發音字符但仍然失敗的內容記錄錯誤")
    print()

    # 顯示當前代碼位置
    print("需要修改的文件：")
    print("- speakub/tts/edge_tts_provider.py")
    print("- 位置：在 synthesize() 方法的異常處理區塊")
    print()

    # 顯示修復代碼
    print("修復代碼範例：")
    print("""
try:
    # ... 合成邏輯 ...
except NoAudioReceived as e:
    # 檢查這是否是純標點符號內容的預期行為
    from speakub.utils.text_utils import is_speakable_content
    speakable, reason = is_speakable_content(text)

    if not speakable:
        # 純標點符號內容，預期沒有音頻，這是正常行為
        logger.debug(f"No audio received for non-speakable content (reason: {reason}): '{text[:20]}...'")
        return b""  # 返回空音頻數據，視為成功處理
    else:
        # 包含可發音字符但仍然失敗，這才是真正的錯誤
        sanitized_error = _sanitize_tts_error_message(str(e))
        logger.error(f"TTS synthesis failed with audio: {sanitized_error}")
        raise RuntimeError(f"TTS synthesis failed: {sanitized_error}") from e
""")


def main():
    """主函數"""
    fix_edge_tts_noaudio_error_handling()

    print("=" * 50)
    print("總結：")
    print("- 純標點符號內容的 'No audio received' 應該視為正常行為")
    print("- 只有包含文字但合成仍然失敗的情況才記錄為錯誤")
    print("- 這樣可以避免 log 中出現不必要的 ERROR 訊息")


if __name__ == "__main__":
    main()
