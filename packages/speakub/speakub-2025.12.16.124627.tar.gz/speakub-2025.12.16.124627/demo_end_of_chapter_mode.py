#!/usr/bin/env python3
"""
示範 END_OF_CHAPTER_MODE 控制邏輯如何運作的簡單腳本
"""


def simulate_end_of_chapter_logic(candidates):
    """
    模擬修正後的 END_OF_CHAPTER_MODE 邏輯

    Args:
        candidates: 候選項目列表，格式為 [(index, text), ...]

    Returns:
        (selected_items, strategy_name)
    """
    if not candidates:
        return [], "EMPTY"

    # 🔧 **章節結尾優化 - END_OF_CHAPTER_MODE**:
    # 項目數量觸發邏輯：直接全選 < 20 個項目
    if len(candidates) < 20:
        # 全選所有候選項目以確保章節結尾內容及時處理
        return candidates[:], "END_OF_CHAPTER_MODE"
    else:
        # 正常批次邏輯 (此處僅作示範)
        selected = candidates[:5]  # 取前5個作為預設
        return selected, "NORMAL_MODE"


def demo_end_of_chapter_mode():
    """示範不同場景下的 END_OF_CHAPTER_MODE 行為"""

    print("🎯 END_OF_CHAPTER_MODE 控制邏輯示範")
    print("=" * 50)

    # 測試案例
    test_cases = [
        {
            "name": "章節結尾 - 少量項目 (應該全選)",
            "candidates": [
                (1, "第一句話"),
                (2, "第二句話"),
                (3, "第三句話"),
            ],
        },
        {
            "name": "章節結尾 - 較多項目但總字符數很少 (應該全選)",
            "candidates": [
                (i, f"第{i}句話") for i in range(1, 16)
            ],
        },
        {
            "name": "章節結尾 - 字符數過多 (應該只選前5個)",
            "candidates": [
                (i, "這是" + "非常長的文字內容" * 10 + f"句{i}") for i in range(1, 11)
            ],
        },
        {
            "name": "正常情況 - 大量項目 (不會觸發 END_OF_CHAPTER_MODE)",
            "candidates": [
                (i, "這是" + "非常長的文字內容" * 2 + f"句{i}") for i in range(1, 25)
            ],
        },
    ]

    for test_case in test_cases:
        print(f"\n📋 測試案例: {test_case['name']}")
        print("-" * 40)

        selected, strategy = simulate_end_of_chapter_logic(
            test_case['candidates'])

        print(f"候選項目數量: {len(test_case['candidates'])}")
        print(f"策略名稱: {strategy}")
        print(f"選中項目數量: {len(selected)}")
        print(f"選中項目內容:")
        for i, (idx, text) in enumerate(selected):
            print(
                f"  {i+1}. [{idx}] {text[:50]}{'...' if len(text) > 50 else ''}")

        total_chars = sum(len(text) for _, text in selected)
        print(f"總字符數: {total_chars}")


if __name__ == "__main__":
    demo_end_of_chapter_mode()
