#!/usr/bin/env python3
"""
Test suite for improved Fusion batching strategy implementation.

Tests the three-stage gear shifting logic with:
- LONG_PARAGRAPH_MODE: Long paragraph handling with hard caps
- SHORT_CONTENT_MODE: Fragmented short content aggregation
- PARAGRAPH_MODE: Standard stacking with 50-second rule
"""

from speakub.tts.fusion_reservoir.batching_strategy import FusionBatchingStrategy
import sys
import os
from typing import List, Tuple
from unittest.mock import Mock

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))


class MockConfigManager:
    """Mock configuration manager for testing"""

    def __init__(self, **overrides):
        self.defaults = {
            "tts.preferred_engine": "nanmai",
            "tts.fusion.char_limit": 200,
            "tts.batch_size": 5,
            "tts.fusion.max_short_items": 15,
            "tts.fusion.long_paragraph_max_items": 5,
        }
        self.defaults.update(overrides)

    def get(self, key: str, default=None):
        return self.defaults.get(key, default)


def test_long_paragraph_mode():
    """Test LONG_PARAGRAPH_MODE with hard caps and config limits"""
    print("=" * 60)
    print("Test 1: LONG_PARAGRAPH_MODE")
    print("=" * 60)

    config = MockConfigManager()
    strategy = FusionBatchingStrategy(config)

    # Test case 1: Long paragraph triggers mode
    test_string = "這是一個非常長的段落，包含了大量的文字內容超過兩百個字符的限制，測試長段落模式的觸發條件和處理邏輯。"
    candidates = [
        (0, test_string * 3),  # ~150 chars for nanmai
        (1, "短句1"),
        (2, "短句2"),
        (3, "短句3"),
        (4, "短句4"),
        (5, "短句5"),  # Should be limited by long_paragraph_max_items=5
        (6, "短句6"),  # Should not be included
    ]

    batch, strategy_name = strategy._select_fusion_batch(candidates)

    assert strategy_name == "LONG_PARAGRAPH_MODE", f"Expected LONG_PARAGRAPH_MODE, got {strategy_name}"
    assert len(
        batch) == 5, f"Expected 5 items (1 long + 4 short), got {len(batch)}"

    total_chars = sum(len(text) for _, text in batch)
    hard_cap = strategy.char_limit * 1.6
    assert total_chars <= hard_cap, f"Total chars {total_chars} exceeds hard cap {hard_cap}"

    print("✓ LONG_PARAGRAPH_MODE correctly triggered and limited")


def test_short_content_mode():
    """Test SHORT_CONTENT_MODE with config limits"""
    print("=" * 60)
    print("Test 2: SHORT_CONTENT_MODE")
    print("=" * 60)

    config = MockConfigManager()
    strategy = FusionBatchingStrategy(config)

    # Test case: 8+ short items with average length < 30
    candidates = [
        (i, f"短{i}") for i in range(20)  # 20 very short items
    ]

    batch, strategy_name = strategy._select_fusion_batch(candidates)

    assert strategy_name == "SHORT_CONTENT_MODE", f"Expected SHORT_CONTENT_MODE, got {strategy_name}"
    # max_short_items limit
    assert len(batch) <= 15, f"Expected <= 15 items, got {len(batch)}"

    total_chars = sum(len(text) for _, text in batch)
    short_cap = strategy.char_limit * 1.5
    assert total_chars <= short_cap, f"Total chars {total_chars} exceeds short cap {short_cap}"

    print("✓ SHORT_CONTENT_MODE correctly triggered and limited")


def test_paragraph_mode_with_50_second_rule():
    """Test PARAGRAPH_MODE with 50-second rule and checkpoint logic"""
    print("=" * 60)
    print("Test 3: PARAGRAPH_MODE (50-second rule)")
    print("=" * 60)

    config = MockConfigManager()
    strategy = FusionBatchingStrategy(config)

    # Test case: Normal content that should use 50-second rule
    candidates = [
        (0, "這是一個正常的句子，大約三十個字符左右。"),
        (1, "第二個句子，類似的長度。"),
        (2, "第三個句子。"),
        (3, "第四個句子。"),
        (4, "第五個句子。"),
        (5, "第六個句子。"),
    ]

    batch, strategy_name = strategy._select_fusion_batch(candidates)

    assert strategy_name == "PARAGRAPH_MODE", f"Expected PARAGRAPH_MODE, got {strategy_name}"

    total_chars = sum(len(text) for _, text in batch)
    min_chars_target = 50.0 * 2.5  # 125 chars

    # Should either have > 3 items OR >= 125 chars (50-second rule)
    assert len(batch) > 3 or total_chars >= min_chars_target, \
        f"Failed 50-second rule: {len(batch)} items, {total_chars} chars"

    assert len(batch) <= strategy.base_batch_size, \
        f"Exceeded base_batch_size limit: {len(batch)} > {strategy.base_batch_size}"

    print("✓ PARAGRAPH_MODE correctly applied 50-second rule")


def test_mode_precedence():
    """Test that modes are applied in correct priority order"""
    print("=" * 60)
    print("Test 4: Mode Precedence")
    print("=" * 60)

    config = MockConfigManager()
    strategy = FusionBatchingStrategy(config)

    # Test LONG_PARAGRAPH_MODE takes precedence
    long_first_candidates = [
        (0, "超長段落" * 50),  # Very long first
        (1, "短"),
        (2, "短"),
    ]

    batch, strategy_name = strategy._select_fusion_batch(long_first_candidates)
    assert strategy_name == "LONG_PARAGRAPH_MODE", "LONG_PARAGRAPH_MODE should take precedence"

    # Test SHORT_CONTENT_MODE when long paragraph condition not met
    short_candidates = [
        (0, "正常句子"),  # Not long enough to trigger LONG mode
        (1, "短"),
        (2, "短"),
        (3, "短"),
        (4, "短"),
        (5, "短"),  # 6 items >= 5, average < 30
    ]

    batch, strategy_name = strategy._select_fusion_batch(short_candidates)
    assert strategy_name == "SHORT_CONTENT_MODE", "SHORT_CONTENT_MODE should trigger for short content"

    print("✓ Mode precedence working correctly")


def test_hard_caps_and_safety_limits():
    """Test hard caps and safety limits across all modes"""
    print("=" * 60)
    print("Test 5: Hard Caps and Safety Limits")
    print("=" * 60)

    config = MockConfigManager()
    strategy = FusionBatchingStrategy(config)

    # Test LONG_PARAGRAPH_MODE hard cap
    long_candidates = [
        (0, "長" * 180),  # 180 chars, > 200*0.9
        (1, "長" * 50),   # Another 50 chars
        # This would exceed hard cap (180+50+50=280 > 200*1.6=320? Wait 320>280)
        (2, "長" * 50),
    ]  # Actually 280 < 320, so all should be included, but limited by max_items

    batch, strategy_name = strategy._select_fusion_batch(long_candidates)
    total_chars = sum(len(text) for _, text in batch)
    hard_cap = strategy.char_limit * 1.6

    assert total_chars <= hard_cap, f"LONG mode exceeded hard cap: {total_chars} > {hard_cap}"
    assert len(
        batch) <= strategy.long_paragraph_max_items, "Exceeded long_paragraph_max_items"

    # Test SHORT_CONTENT_MODE cap
    short_candidates = [(i, "短" * 20) for i in range(20)]  # Many short items
    batch, strategy_name = strategy._select_fusion_batch(short_candidates)
    total_chars = sum(len(text) for _, text in batch)
    short_cap = strategy.char_limit * 1.5

    assert total_chars <= short_cap, f"SHORT mode exceeded cap: {total_chars} > {short_cap}"

    print("✓ All hard caps and safety limits working correctly")


def test_edge_cases():
    """Test edge cases and boundary conditions"""
    print("=" * 60)
    print("Test 6: Edge Cases")
    print("=" * 60)

    config = MockConfigManager()
    strategy = FusionBatchingStrategy(config)

    # Empty candidates
    batch, strategy_name = strategy._select_fusion_batch([])
    assert strategy_name == "EMPTY", "Empty candidates should return EMPTY"

    # Single item
    batch, strategy_name = strategy._select_fusion_batch([(0, "單一項目")])
    assert len(batch) == 1, "Single item should be selected"

    # Exactly at boundaries
    boundary_candidates = [
        (0, "長" * int(200 * 0.9)),  # Exactly 90% of char_limit
        (1, "短"),
    ]
    batch, strategy_name = strategy._select_fusion_batch(boundary_candidates)
    assert strategy_name == "LONG_PARAGRAPH_MODE", "Should trigger LONG mode at boundary"

    print("✓ Edge cases handled correctly")


def run_all_tests():
    """Run all test functions"""
    print("\n" + "=" * 80)
    print("FUSION BATCHING STRATEGY IMPROVED - COMPREHENSIVE TESTS")
    print("=" * 80 + "\n")

    try:
        test_long_paragraph_mode()
        test_short_content_mode()
        test_paragraph_mode_with_50_second_rule()
        test_mode_precedence()
        test_hard_caps_and_safety_limits()
        test_edge_cases()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED!")
        print("🎉 Improved Fusion batching strategy is working correctly")
        print("=" * 80)
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
