#!/usr/bin/env python3
"""
Test IdleDetector - Unit tests for idle detection functionality
"""

import time
import unittest
from unittest.mock import patch

from speakub.utils.idle_detector import (
    IdleDetector,
    get_idle_detector,
    is_system_idle,
    update_global_activity,
)


class TestIdleDetector(unittest.TestCase):
    """Test cases for IdleDetector class."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = IdleDetector(threshold_seconds=1)

    def tearDown(self):
        """Clean up test fixtures."""
        # Reset global instance between tests
        import speakub.utils.idle_detector as idle_module
        idle_module._idle_detector_instance = None

    def test_initial_state(self):
        """Test initial state of idle detector."""
        self.assertFalse(self.detector.idle_mode)
        self.assertEqual(self.detector.threshold_seconds, 1)
        self.assertIsInstance(self.detector.last_activity, float)
        self.assertGreater(self.detector.idle_time, 0)

    def test_update_activity_exits_idle_mode(self):
        """Test that update_activity exits idle mode."""
        # Force idle mode
        self.detector.force_idle_mode(True)
        self.assertTrue(self.detector.idle_mode)

        # Update activity should exit idle mode
        self.detector.update_activity()
        self.assertFalse(self.detector.idle_mode)

    def test_check_idle_status_enters_idle_mode(self):
        """Test that check_idle_status enters idle mode after threshold."""
        # Update activity to reset timer
        self.detector.update_activity()
        self.assertFalse(self.detector.idle_mode)

        # Wait for threshold to be exceeded
        time.sleep(1.1)

        # Check idle status should enter idle mode
        self.assertTrue(self.detector.check_idle_status())
        self.assertTrue(self.detector.idle_mode)

    def test_check_idle_status_exits_idle_mode(self):
        """Test that check_idle_status exits idle mode when active."""
        # Force idle mode
        self.detector.force_idle_mode(True)
        self.assertTrue(self.detector.idle_mode)

        # Update activity
        self.detector.update_activity()

        # Check idle status should exit idle mode
        self.assertFalse(self.detector.check_idle_status())
        self.assertFalse(self.detector.idle_mode)

    def test_force_idle_mode(self):
        """Test force_idle_mode method."""
        # Start with active mode
        self.assertFalse(self.detector.idle_mode)

        # Force idle mode
        self.detector.force_idle_mode(True)
        self.assertTrue(self.detector.idle_mode)

        # Force back to active mode
        self.detector.force_idle_mode(False)
        self.assertFalse(self.detector.idle_mode)

    def test_idle_callbacks(self):
        """Test idle mode change callbacks."""
        callback_calls = []

        def callback(idle_active):
            callback_calls.append(idle_active)

        # Add callback
        self.detector.add_idle_callback(callback)

        # Force idle mode change
        self.detector.force_idle_mode(True)
        self.assertEqual(callback_calls, [True])

        # Force another change
        self.detector.force_idle_mode(False)
        self.assertEqual(callback_calls, [True, False])

        # Remove callback
        self.detector.remove_idle_callback(callback)

        # Should not call callback anymore
        self.detector.force_idle_mode(True)
        self.assertEqual(callback_calls, [True, False])  # No new calls

    def test_activity_callbacks(self):
        """Test activity update callbacks."""
        callback_calls = []

        def callback():
            callback_calls.append(True)

        # Add callback
        self.detector.add_activity_callback(callback)

        # Update activity
        self.detector.update_activity()
        self.assertEqual(callback_calls, [True])

        # Update again
        self.detector.update_activity()
        self.assertEqual(callback_calls, [True, True])

        # Remove callback
        self.detector.remove_activity_callback(callback)

        # Should not call callback anymore
        self.detector.update_activity()
        self.assertEqual(callback_calls, [True, True])  # No new calls

    def test_get_status_info(self):
        """Test get_status_info method."""
        info = self.detector.get_status_info()

        required_keys = [
            "idle_mode", "idle_time_seconds", "threshold_seconds",
            "last_activity_timestamp", "idle_percentage"
        ]

        for key in required_keys:
            self.assertIn(key, info)

        self.assertIsInstance(info["idle_mode"], bool)
        self.assertIsInstance(info["idle_time_seconds"], float)
        self.assertEqual(info["threshold_seconds"], 1)
        self.assertIsInstance(info["last_activity_timestamp"], float)
        self.assertIsInstance(info["idle_percentage"], float)
        self.assertGreaterEqual(info["idle_percentage"], 0.0)
        self.assertLessEqual(info["idle_percentage"], 100.0)


class TestIdleDetectorGlobalFunctions(unittest.TestCase):
    """Test global idle detector functions."""

    def tearDown(self):
        """Clean up test fixtures."""
        # Reset global instance between tests
        import speakub.utils.idle_detector as idle_module
        idle_module._idle_detector_instance = None

    def test_get_idle_detector_singleton(self):
        """Test that get_idle_detector returns singleton instance."""
        detector1 = get_idle_detector()
        detector2 = get_idle_detector()

        self.assertIs(detector1, detector2)
        self.assertIsInstance(detector1, IdleDetector)

    def test_update_global_activity(self):
        """Test update_global_activity function."""
        # Force idle mode
        detector = get_idle_detector()
        detector.force_idle_mode(True)
        self.assertTrue(detector.idle_mode)

        # Update global activity should exit idle mode
        update_global_activity()
        self.assertFalse(detector.idle_mode)

    def test_is_system_idle(self):
        """Test is_system_idle function."""
        detector = get_idle_detector()

        # Should not be idle initially
        self.assertFalse(is_system_idle())

        # Force idle mode
        detector.force_idle_mode(True)
        # Check again with the same detector instance
        self.assertTrue(detector.idle_mode)
        self.assertTrue(is_system_idle())


class TestIdleDetectorIntegration(unittest.TestCase):
    """Integration tests for idle detector with time mocking."""

    def tearDown(self):
        """Clean up test fixtures."""
        # Reset global instance between tests
        import speakub.utils.idle_detector as idle_module
        idle_module._idle_detector_instance = None

    @patch('speakub.utils.idle_detector.time.time')
    def test_idle_detection_with_mocked_time(self, mock_time):
        """Test idle detection with mocked time."""
        # Start with time = 1000
        mock_time.return_value = 1000
        detector = IdleDetector(threshold_seconds=5)

        # Update activity
        detector.update_activity()
        self.assertFalse(detector.idle_mode)

        # Advance time by 3 seconds (still active)
        mock_time.return_value = 1003
        self.assertFalse(detector.check_idle_status())

        # Advance time by 3 more seconds (total 6s > 5s threshold)
        mock_time.return_value = 1006
        self.assertTrue(detector.check_idle_status())

        # Update activity again
        detector.update_activity()

        # Should exit idle mode
        self.assertFalse(detector.check_idle_status())

    def test_thread_safety(self):
        """Test thread safety of idle detector."""
        import concurrent.futures

        detector = IdleDetector(threshold_seconds=1)
        results = []

        def worker(worker_id):
            """Worker function for thread safety test."""
            try:
                # Each worker performs operations
                detector.update_activity()
                time.sleep(0.01)  # Small delay
                idle_status = detector.check_idle_status()
                results.append((worker_id, idle_status))
            except Exception as e:
                results.append((worker_id, f"error: {e}"))

        # Run multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(worker, i) for i in range(5)]
            concurrent.futures.wait(futures)

        # All operations should complete without errors
        self.assertEqual(len(results), 5)
        for worker_id, result in results:
            self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
