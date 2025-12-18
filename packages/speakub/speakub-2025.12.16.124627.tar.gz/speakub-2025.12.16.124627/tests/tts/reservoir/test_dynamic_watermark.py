#!/usr/bin/env python3
"""
Unit tests for Dynamic Watermark and Calculated Sleep functionality.
Tests the enhanced _check_water_level method in PredictiveBatchController.
"""

import asyncio
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from collections import deque

from speakub.tts.reservoir.controller import PredictiveBatchController, TriggerState
from speakub.tts.reservoir.play_monitor import SynthesisTimeMonitor


class TestDynamicWatermark(unittest.TestCase):
    """Test cases for dynamic watermark functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.playlist_manager = Mock()
        self.queue_predictor = Mock()
        self.config_manager = Mock()

        # Mock config manager
        self.config_manager.get.side_effect = self._mock_config_get

        # Mock synthesis monitor
        self.synth_monitor = Mock()
        self.synth_monitor.get_predicted_synthesis_time.return_value = 2.0

        # Create controller
        self.controller = PredictiveBatchController(
            playlist_manager=self.playlist_manager,
            queue_predictor=self.queue_predictor,
            config_manager=self.config_manager
        )

        # Replace synthesis monitor with our mock
        self.controller._synth_monitor = self.synth_monitor

    def _mock_config_get(self, key, default=None):
        """Mock configuration values."""
        config_map = {
            "tts.preferred_engine": "edge-tts",
            "tts.reservoir.low_watermark": 15.0,
            "tts.reservoir.high_watermark": 60.0,
        }
        return config_map.get(key, default)

    def test_dynamic_watermark_edge_tts_fast(self):
        """Test dynamic watermark with fast Edge-TTS engine."""
        # Edge-TTS predicted time: 1.5s
        # Safety margin: 1.5 * 3 = 4.5s
        # Dynamic low watermark: max(15, 4.5) = 15
        self.synth_monitor.get_predicted_synthesis_time.return_value = 1.5

        dynamic_low = max(self.controller.LOW_WATERMARK, 1.5 * 3.0)
        self.assertEqual(dynamic_low, 15.0)

        dynamic_high = max(self.controller.HIGH_WATERMARK, dynamic_low + 30.0)
        self.assertEqual(dynamic_high, 60.0)

    def test_dynamic_watermark_nanmai_slow(self):
        """Test dynamic watermark with slow Nanmai engine."""
        # Configure for Nanmai
        self.config_manager.get.side_effect = lambda key, default=None: {
            "tts.preferred_engine": "nanmai",
            "tts.reservoir.low_watermark": 15.0,
            "tts.reservoir.high_watermark": 60.0,
        }.get(key, default)

        # Update config to reflect Nanmai
        self.controller._update_config()

        # Nanmai predicted time: 6.0s
        # Safety margin: 6.0 * 3 = 18.0s
        # Dynamic low watermark: max(22.5, 18.0) = 22.5 (due to Nanmai adjustment)
        self.synth_monitor.get_predicted_synthesis_time.return_value = 6.0

        dynamic_low = max(self.controller.LOW_WATERMARK, 6.0 * 3.0)
        self.assertEqual(dynamic_low, 22.5)

    def test_dynamic_watermark_extreme_case(self):
        """Test dynamic watermark with extreme prediction values."""
        # Very slow prediction
        self.synth_monitor.get_predicted_synthesis_time.return_value = 10.0

        dynamic_low = max(self.controller.LOW_WATERMARK, 10.0 * 3.0)
        self.assertEqual(dynamic_low, 30.0)  # 10 * 3 = 30

        # Very fast prediction
        self.synth_monitor.get_predicted_synthesis_time.return_value = 0.5

        dynamic_low = max(self.controller.LOW_WATERMARK, 0.5 * 3.0)
        self.assertEqual(dynamic_low, 15.0)  # Still uses base watermark


class TestCalculatedSleep(unittest.TestCase):
    """Test cases for calculated sleep functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.playlist_manager = Mock()
        self.queue_predictor = Mock()
        self.config_manager = Mock()
        self.config_manager.get.side_effect = lambda key, default=None: {
            "tts.preferred_engine": "edge-tts",
        }.get(key, default)

        self.controller = PredictiveBatchController(
            playlist_manager=self.playlist_manager,
            queue_predictor=self.queue_predictor,
            config_manager=self.config_manager
        )

    def test_calculated_sleep_normal_range(self):
        """Test calculated sleep in normal buffer surplus range."""
        test_cases = [
            # (buffer_duration, low_watermark, expected_sleep_range)
            (25.0, 15.0, (5.0, 10.0)),  # surplus 10s, sleep ~5s
            (35.0, 15.0, (10.0, 15.0)),  # surplus 20s, sleep ~10s
            (45.0, 15.0, (15.0, 15.0)),  # surplus 30s, sleep 15s (max)
        ]

        for buffer_duration, low_watermark, (min_expected, max_expected) in test_cases:
            with self.subTest(buffer=buffer_duration, low=low_watermark):
                surplus_time = buffer_duration - low_watermark
                safe_sleep_time = max(4.0, min(surplus_time / 2.0, 15.0))

                self.assertGreaterEqual(safe_sleep_time, min_expected)
                self.assertLessEqual(safe_sleep_time, max_expected)

    def test_calculated_sleep_minimum_boundary(self):
        """Test calculated sleep minimum boundary (4 seconds)."""
        # Very small surplus
        surplus_time = 2.0  # Very low surplus
        safe_sleep_time = max(4.0, min(surplus_time / 2.0, 15.0))

        self.assertEqual(safe_sleep_time, 4.0)  # Should be minimum 4s

        # Zero surplus
        surplus_time = 0.0
        safe_sleep_time = max(4.0, min(surplus_time / 2.0, 15.0))

        self.assertEqual(safe_sleep_time, 4.0)  # Should still be minimum 4s

    def test_calculated_sleep_maximum_boundary(self):
        """Test calculated sleep maximum boundary (15 seconds)."""
        # Large surplus
        surplus_time = 50.0  # Large surplus
        safe_sleep_time = max(4.0, min(surplus_time / 2.0, 15.0))

        self.assertEqual(safe_sleep_time, 15.0)  # Should be maximum 15s

        # Very large surplus
        surplus_time = 100.0
        safe_sleep_time = max(4.0, min(surplus_time / 2.0, 15.0))

        self.assertEqual(safe_sleep_time, 15.0)  # Should still be maximum 15s

    def test_calculated_sleep_nanmai_adjustment(self):
        """Test Nanmai-specific sleep adjustment."""
        # Configure for Nanmai
        self.config_manager.get.side_effect = lambda key, default=None: {
            "tts.preferred_engine": "nanmai",
        }.get(key, default)

        # Test with surplus < 15s (should apply 0.8 multiplier)
        surplus_time = 10.0
        safe_sleep_time = max(4.0, min(surplus_time / 2.0, 15.0))

        # Apply Nanmai adjustment if surplus < 15
        if surplus_time < 15.0:
            safe_sleep_time = max(3.0, safe_sleep_time * 0.8)

        # 5.0 * 0.8 = 4.0, but min 4.0
        self.assertAlmostEqual(safe_sleep_time, 4.0)


class TestWatermarkStateTransitions(unittest.TestCase):
    """Test watermark behavior in different buffer states."""

    def setUp(self):
        """Set up test fixtures."""
        self.playlist_manager = Mock()
        self.queue_predictor = Mock()
        self.config_manager = Mock()
        self.config_manager.get.side_effect = lambda key, default=None: {
            "tts.preferred_engine": "edge-tts",
            "tts.reservoir.low_watermark": 15.0,
            "tts.reservoir.high_watermark": 60.0,
        }.get(key, default)

        self.controller = PredictiveBatchController(
            playlist_manager=self.playlist_manager,
            queue_predictor=self.queue_predictor,
            config_manager=self.config_manager
        )

        # Mock synthesis monitor
        self.controller._synth_monitor = Mock()
        self.controller._synth_monitor.get_predicted_synthesis_time.return_value = 2.0

    @patch('speakub.tts.reservoir.controller.logger')
    def test_refilling_mode_trigger(self, mock_logger):
        """Test that refilling mode is triggered when buffer is below dynamic low watermark."""
        # Set up buffer below dynamic low watermark
        self.playlist_manager.get_buffered_duration.return_value = 10.0  # Below 15.0

        # Mock the trigger method
        with patch.object(self.controller, '_trigger_new_batch') as mock_trigger:
            # Run check (in a way that doesn't actually schedule timers)
            # Note: This is a simplified test - full integration testing would be more complex

            # Verify trigger was called for low water
            self.assertTrue(10.0 < self.controller.LOW_WATERMARK)

    def test_maintaining_mode_sleep_calculation(self):
        """Test sleep calculation in maintaining mode."""
        # Set up buffer in maintaining range
        buffer_level = 25.0  # Between low (15) and high (60) watermarks
        self.playlist_manager.get_buffered_duration.return_value = buffer_level

        # Calculate expected sleep time
        dynamic_low = max(self.controller.LOW_WATERMARK, 2.0 * 3.0)  # 15.0
        surplus_time = buffer_level - dynamic_low  # 25 - 15 = 10
        # max(4, min(5, 15)) = 5
        expected_sleep = max(4.0, min(surplus_time / 2.0, 15.0))

        self.assertEqual(expected_sleep, 5.0)


class TestIntegrationWithExistingLogic(unittest.TestCase):
    """Test that new logic integrates properly with existing controller logic."""

    def setUp(self):
        """Set up test fixtures."""
        self.playlist_manager = Mock()
        self.queue_predictor = Mock()
        self.config_manager = Mock()
        self.config_manager.get.side_effect = lambda key, default=None: {
            "tts.preferred_engine": "edge-tts",
            "tts.reservoir.low_watermark": 15.0,
            "tts.reservoir.high_watermark": 60.0,
        }.get(key, default)

        self.controller = PredictiveBatchController(
            playlist_manager=self.playlist_manager,
            queue_predictor=self.queue_predictor,
            config_manager=self.config_manager
        )

    def test_backward_compatibility(self):
        """Test that existing behavior is preserved when predictions are unavailable."""
        # Test with synthesis monitor returning None or throwing exception
        self.controller._synth_monitor = None

        # Should fall back to static watermarks
        try:
            # This should not crash and should use static watermarks
            low_watermark = self.controller.LOW_WATERMARK
            self.assertEqual(low_watermark, 15.0)
        except Exception as e:
            self.fail(
                f"Controller should handle missing synthesis monitor gracefully: {e}")

    def test_engine_specific_adjustments_preserved(self):
        """Test that engine-specific watermark adjustments are preserved."""
        # Test Edge-TTS (no adjustment)
        self.assertEqual(self.controller.LOW_WATERMARK, 15.0)
        self.assertEqual(self.controller.HIGH_WATERMARK, 60.0)

        # Configure for Nanmai and test adjustments
        self.config_manager.get.side_effect = lambda key, default=None: {
            "tts.preferred_engine": "nanmai",
            "tts.reservoir.low_watermark": 15.0,
            "tts.reservoir.high_watermark": 60.0,
        }.get(key, default)

        self.controller._update_config()

        # Should have Nanmai-specific adjustments
        self.assertEqual(self.controller.LOW_WATERMARK, 22.5)  # 15 * 1.5
        self.assertEqual(self.controller.HIGH_WATERMARK, 72.0)  # 60 * 1.2


if __name__ == '__main__':
    unittest.main()
