#!/usr/bin/env python3
"""
Phase 2 Integration Test
Verify that PlaylistManager can instantiate with SimpleReservoirController
"""

from speakub.tts.reservoir.simple_controller import SimpleReservoirController
from speakub.tts.playlist_manager import PlaylistManager
import unittest
from unittest.mock import MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../../..')))


class TestPhase2Integration(unittest.TestCase):
    def test_instantiation(self):
        print("Testing PlaylistManager instantiation with SimpleReservoirController...")

        # Mock dependencies
        mock_integration = MagicMock()
        mock_app = MagicMock()
        mock_integration.app = mock_app

        # Instantiate
        pm = PlaylistManager(mock_integration)

        # Verify controller type
        self.assertIsInstance(pm._predictive_controller,
                              SimpleReservoirController)
        print("✅ Controller type verification passed")

        # Verify method existence (compatibility check)
        self.assertTrue(hasattr(pm._predictive_controller, "notify_underrun"))
        self.assertTrue(
            hasattr(pm._predictive_controller, "record_playback_event"))
        self.assertTrue(hasattr(pm._predictive_controller, "start_monitoring"))
        self.assertTrue(
            hasattr(pm._predictive_controller, "_trigger_new_batch"))
        self.assertTrue(hasattr(pm._predictive_controller, "queue_predictor"))
        print("✅ Compatibility interface verification passed")


if __name__ == '__main__':
    unittest.main()
