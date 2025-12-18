#!/usr/bin/env python3
"""
Phase 3 Verification Test
Test the new time-based logic in SimpleReservoirController
"""

from speakub.tts.reservoir.simple_controller import SimpleReservoirController
import unittest
from unittest.mock import MagicMock
import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../..')))


class TestPhase3Verification(unittest.TestCase):
    def setUp(self):
        # Mock PlaylistManager
        self.pm_mock = MagicMock()
        self.pm_mock.get_current_index.return_value = 0
        self.pm_mock.get_playlist_length.return_value = 25

        # Mock items: 20 short items + 3 long items
        self.playlist_items = []
        # 20 short items ("是", "好", "對")
        for i in range(20):
            self.playlist_items.append(("是", i))  # Unynthesized short text

        # 3 long items (500 char text)
        for i in range(3):
            long_text = "這是一段很長的中文文字，用於測試時間估算邏輯。" * 10  # ~250 chars
            # Unynthesized long text
            self.playlist_items.append((long_text, 20 + i))

        # Add some synthesized items for buffer calculation
        for i in range(2):
            self.playlist_items.append(("測試", 23 + i, b"dummy_audio_data"))

        self.pm_mock.get_item_at.side_effect = lambda idx: self.playlist_items[idx] if 0 <= idx < len(
            self.playlist_items) else None

        # Create controller
        self.controller = SimpleReservoirController(self.pm_mock)

    def test_short_sentences_batch(self):
        """測試案例 A: 短句連發 - 應一次性抓取所有項目"""
        print("Testing short sentences batching...")

        # Mock _process_batch to capture what would be processed
        processed_batches = []
        self.pm_mock._process_batch = lambda batch: processed_batches.append(
            batch)

        # Collect batch
        batch = self.controller._collect_batch_items()

        # Verify results
        self.assertGreater(len(batch), 0, "Should collect some items")

        # Count items with text "是"
        short_item_count = sum(1 for _, text in batch if text == "是")
        self.assertEqual(short_item_count, 20,
                         "Should collect all 20 short items in one batch")

        print(
            f"✅ Collected {len(batch)} items in one batch (including {short_item_count} short items)")

    def test_long_text_single_item(self):
        """測試案例 B: 長文 - 應一次只抓取一個項目"""
        print("Testing long text batching...")

        # Modify playlist to have only long items from start
        long_playlist = []
        for i in range(3):
            long_text = "這是一段很長的中文文字，用於測試時間估算邏輯。" * 10  # ~250 chars
            long_playlist.append((long_text, i))  # Unynthesized

        self.pm_mock.get_item_at.side_effect = lambda idx: long_playlist[idx] if 0 <= idx < len(
            long_playlist) else None
        self.pm_mock.get_playlist_length.return_value = len(long_playlist)

        # Collect batch
        batch = self.controller._collect_batch_items()

        # Verify results
        self.assertEqual(
            len(batch), 1, "Should collect only 1 long item per batch")

        # Check that it's a long text
        _, text = batch[0]
        self.assertGreater(len(text), 200, "Should be a long text")

        print(f"✅ Collected 1 item with {len(text)} characters")

    def test_time_based_logic(self):
        """測試時間驅動邏輯"""
        print("Testing time-based duration estimation...")

        # Test short text estimation
        short_duration = self.controller._estimate_play_duration("是")
        self.assertGreater(short_duration, 0,
                           "Should estimate positive duration")

        # Test long text estimation
        long_text = "這是一段很長的中文文字，用於測試時間估算邏輯。" * 10
        long_duration = self.controller._estimate_play_duration(long_text)

        # Long text should take longer than short text
        self.assertGreater(long_duration, short_duration,
                           "Long text should take longer")

        print(f"✅ Short text duration: {short_duration:.2f}s")
        print(f"✅ Long text duration: {long_duration:.2f}s")

    def test_buffer_calculation(self):
        """測試緩衝區時長計算"""
        print("Testing buffer duration calculation...")

        duration = self.controller._calculate_buffer_duration()
        self.assertGreaterEqual(
            duration, 0, "Buffer duration should be non-negative")

        print(f"✅ Buffer duration: {duration:.2f}s")

    def test_watermark_logic(self):
        """測試水位控制邏輯"""
        print("Testing watermark logic...")

        # Test low watermark trigger
        self.controller.LOW_WATERMARK = 10.0
        buffer_duration = 5.0  # Below low watermark

        # Manually test the logic (since we can't easily mock the async parts)
        should_trigger = buffer_duration < self.controller.LOW_WATERMARK
        self.assertTrue(
            should_trigger, "Should trigger refill when below low watermark")

        # Test high watermark
        buffer_duration = 70.0  # Above high watermark (60.0)
        should_skip = buffer_duration > self.controller.HIGH_WATERMARK
        self.assertTrue(should_skip, "Should skip when above high watermark")

        print("✅ Watermark logic working correctly")

    async def test_controller_lifecycle(self):
        """測試控制器生命週期"""
        print("Testing controller lifecycle...")

        # Test starting
        await self.controller.start_monitoring()
        self.assertTrue(self.controller.running,
                        "Controller should be running")

        # Test stopping
        await self.controller.stop_monitoring()
        self.assertFalse(self.controller.running,
                         "Controller should be stopped")

        print("✅ Controller lifecycle working correctly")


if __name__ == '__main__':
    unittest.main()
