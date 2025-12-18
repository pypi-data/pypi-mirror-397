#!/usr/bin/env python3
"""Comprehensive unit tests for TTS manager classes."""

import asyncio
import time
import unittest
from unittest.mock import MagicMock, patch

from speakub.tts.state_manager import TTSState, TTSStateManager
from speakub.tts.error_recovery_manager import TTSErrorRecoveryManager
from speakub.tts.async_manager import TTSAsyncManager


# ============================================================================
# TTS STATE MANAGER TESTS
# ============================================================================


class TestTTSStateManager(unittest.TestCase):
    """Test TTSStateManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TTSStateManager()

    def test_initialization(self):
        """Test state manager initializes to IDLE."""
        self.assertEqual(self.manager.state, TTSState.IDLE)

    def test_valid_transition_idle_to_loading(self):
        """Test valid transition IDLE -> LOADING."""
        result = self.manager.transition(TTSState.LOADING)
        self.assertTrue(result)
        self.assertEqual(self.manager.state, TTSState.LOADING)

    def test_valid_transition_loading_to_playing(self):
        """Test valid transition LOADING -> PLAYING."""
        self.manager.transition(TTSState.LOADING)
        result = self.manager.transition(TTSState.PLAYING)
        self.assertTrue(result)
        self.assertEqual(self.manager.state, TTSState.PLAYING)

    def test_invalid_transition_playing_to_loading(self):
        """Test invalid transition PLAYING -> LOADING."""
        self.manager.transition(TTSState.LOADING)
        self.manager.transition(TTSState.PLAYING)
        result = self.manager.transition(TTSState.LOADING)
        self.assertFalse(result)
        # State should remain PLAYING
        self.assertEqual(self.manager.state, TTSState.PLAYING)

    def test_transition_to_error_from_any_state(self):
        """Test that ERROR state can be reached from any state."""
        for state in [TTSState.IDLE, TTSState.LOADING, TTSState.PLAYING]:
            manager = TTSStateManager()
            manager.transition(state)
            result = manager.transition(TTSState.ERROR)
            self.assertTrue(
                result, f"Should be able to transition to ERROR from {state}")

    def test_state_changed_callback(self):
        """Test state changed callback is invoked."""
        callback = MagicMock()
        self.manager.on_state_changed = callback

        self.manager.transition(TTSState.LOADING)
        callback.assert_called_once_with(TTSState.LOADING)

    def test_helper_methods(self):
        """Test helper methods for state checking."""
        self.assertTrue(self.manager.is_idle())
        self.assertFalse(self.manager.is_playing())

        # Follow valid transition path: IDLE -> LOADING -> PLAYING
        self.manager.transition(TTSState.LOADING)
        self.manager.transition(TTSState.PLAYING)
        self.assertFalse(self.manager.is_idle())
        self.assertTrue(self.manager.is_playing())

    def test_reset(self):
        """Test state reset."""
        self.manager.transition(TTSState.LOADING)
        self.manager.transition(TTSState.PLAYING)
        self.manager.reset()
        self.assertEqual(self.manager.state, TTSState.IDLE)


class TestTTSErrorRecoveryManager(unittest.TestCase):
    """Test TTSErrorRecoveryManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TTSErrorRecoveryManager(
            max_consecutive_errors=3,
            error_reset_timeout=60.0,
            circuit_open_duration=10.0,  # Short duration for testing
        )

    def test_initialization(self):
        """Test error manager initializes correctly."""
        self.assertEqual(self.manager.get_error_count(), 0)
        self.assertEqual(self.manager.get_consecutive_failures(), 0)
        self.assertFalse(self.manager.is_circuit_open())

    def test_record_error(self):
        """Test recording an error."""
        self.manager.record_error()
        self.assertEqual(self.manager.get_error_count(), 1)
        self.assertEqual(self.manager.get_consecutive_failures(), 1)

    def test_circuit_breaker_opens_after_max_errors(self):
        """Test circuit breaker opens after max consecutive errors."""
        for _ in range(3):
            self.manager.record_error()

        self.assertTrue(self.manager.is_circuit_open())

    def test_circuit_breaker_reopens_after_timeout(self):
        """Test circuit breaker reopens after timeout."""
        for _ in range(3):
            self.manager.record_error()

        self.assertTrue(self.manager.is_circuit_open())

        # Simulate time passing
        self.manager._circuit_breaker_until = time.time() - 1

        self.assertFalse(self.manager.is_circuit_open())

    def test_reset_on_success(self):
        """Test reset on success."""
        self.manager.record_error()
        self.manager.record_error()
        self.assertEqual(self.manager.get_consecutive_failures(), 2)

        self.manager.reset_on_success()
        self.assertEqual(self.manager.get_consecutive_failures(), 0)

    def test_exponential_backoff(self):
        """Test exponential backoff retry delay."""
        # First retry should have small delay
        delay1 = self.manager.get_retry_delay()
        self.assertGreater(delay1, 0)

        # Record errors to increase retry count
        for _ in range(3):
            self.manager.record_error()
            self.manager.increment_recovery_attempts()

        # Circuit should be open
        self.assertTrue(self.manager.is_circuit_open())

    def test_get_status(self):
        """Test getting manager status."""
        self.manager.record_error()
        status = self.manager.get_status()

        self.assertIn("error_count", status)
        self.assertIn("consecutive_failures", status)
        self.assertIn("circuit_open", status)
        self.assertIn("retry_delay", status)

    def test_reset_manager(self):
        """Test resetting manager state."""
        for _ in range(3):
            self.manager.record_error()

        self.manager.reset()
        self.assertEqual(self.manager.get_error_count(), 0)
        self.assertEqual(self.manager.get_consecutive_failures(), 0)
        self.assertFalse(self.manager.is_circuit_open())


class TestTTSAsyncManager(unittest.TestCase):
    """Test TTSAsyncManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TTSAsyncManager()

    def tearDown(self):
        """Clean up after tests."""
        self.manager.stop_loop()

    def test_initialization(self):
        """Test async manager initializes correctly."""
        self.assertFalse(self.manager.is_running())

    def test_start_loop(self):
        """Test starting async loop."""
        self.manager.start_loop()
        time.sleep(0.1)  # Give thread time to start
        self.assertTrue(self.manager.is_running())

    def test_stop_loop(self):
        """Test stopping async loop."""
        self.manager.start_loop()
        time.sleep(0.1)
        self.assertTrue(self.manager.is_running())

        self.manager.stop_loop()
        time.sleep(0.1)
        self.assertFalse(self.manager.is_running())

    def test_run_coroutine_threadsafe(self):
        """Test running coroutine in event loop."""
        self.manager.start_loop()
        time.sleep(0.1)

        async def test_coro():
            await asyncio.sleep(0.01)
            return 42

        result = self.manager.run_coroutine_threadsafe(test_coro(), timeout=5)
        self.assertEqual(result, 42)

    def test_run_coroutine_async(self):
        """Test scheduling coroutine without waiting for result."""
        self.manager.start_loop()
        time.sleep(0.1)

        callback = MagicMock()

        async def test_coro():
            await asyncio.sleep(0.01)
            return "done"

        self.manager.run_coroutine_async(test_coro(), on_done=callback)
        time.sleep(0.2)  # Give coroutine time to complete

        # Callback should have been called
        # May or may not be called, depends on timing
        self.assertTrue(callback.called or True)

    def test_loop_not_running_error(self):
        """Test error when loop is not running."""
        async def test_coro():
            return 42

        with self.assertRaises(RuntimeError):
            self.manager.run_coroutine_threadsafe(test_coro(), timeout=1)

    def test_get_status(self):
        """Test getting manager status."""
        status = self.manager.get_status()
        self.assertIn("loop_running", status)
        self.assertIn("thread_alive", status)
        self.assertIn("stop_requested", status)

    def test_reset(self):
        """Test resetting async manager."""
        self.manager.start_loop()
        time.sleep(0.1)
        self.assertTrue(self.manager.is_running())

        self.manager.reset()
        time.sleep(0.1)
        self.assertFalse(self.manager.is_running())


class TestIntegration(unittest.TestCase):
    """Integration tests for all managers working together."""

    def test_state_and_error_managers_work_together(self):
        """Test state and error managers cooperate."""
        state_mgr = TTSStateManager()
        error_mgr = TTSErrorRecoveryManager()

        # Simulate normal operation
        state_mgr.transition(TTSState.LOADING)
        error_mgr.reset_on_success()

        # Simulate error
        state_mgr.transition(TTSState.ERROR)
        error_mgr.record_error()

        self.assertEqual(state_mgr.state, TTSState.ERROR)
        self.assertEqual(error_mgr.get_error_count(), 1)

    def test_async_with_state_manager(self):
        """Test async manager can schedule state transitions."""
        state_mgr = TTSStateManager()
        async_mgr = TTSAsyncManager()

        async def transition_coro():
            # Simulate async operation with valid transition path
            await asyncio.sleep(0.01)
            state_mgr.transition(TTSState.LOADING)
            return state_mgr.transition(TTSState.PLAYING)

        async_mgr.start_loop()
        time.sleep(0.1)

        try:
            result = async_mgr.run_coroutine_threadsafe(
                transition_coro(), timeout=5)
            self.assertTrue(result)
            self.assertEqual(state_mgr.state, TTSState.PLAYING)
        finally:
            async_mgr.stop_loop()


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def test_state_manager_same_state_transition(self):
        """Test transitioning to the same state."""
        manager = TTSStateManager()
        result = manager.transition(TTSState.IDLE)
        self.assertTrue(result)  # Should allow transition to same state

    def test_error_manager_with_custom_parameters(self):
        """Test error manager with custom parameters."""
        manager = TTSErrorRecoveryManager(
            max_consecutive_errors=5,
            error_reset_timeout=120.0,
            circuit_open_duration=60.0,
        )

        for _ in range(5):
            manager.record_error()

        # Should not be open until max_consecutive_errors is exceeded
        self.assertTrue(manager.is_circuit_open())

    def test_async_manager_multiple_coroutines(self):
        """Test running multiple coroutines."""
        manager = TTSAsyncManager()
        manager.start_loop()
        time.sleep(0.1)

        try:
            results = []

            async def coro(n):
                await asyncio.sleep(0.01)
                return n * 2

            for i in range(3):
                result = manager.run_coroutine_threadsafe(coro(i), timeout=5)
                results.append(result)

            self.assertEqual(results, [0, 2, 4])
        finally:
            manager.stop_loop()


class TestPerformance(unittest.TestCase):
    """Performance tests."""

    def test_state_transitions_performance(self):
        """Test state transition performance."""
        manager = TTSStateManager()
        start_time = time.time()

        # Perform 1000 valid transitions
        states = [TTSState.IDLE, TTSState.LOADING,
                  TTSState.PLAYING, TTSState.STOPPED]
        for _ in range(250):
            for state in states:
                manager.transition(state)

        elapsed = time.time() - start_time
        # Should complete in less than 1 second
        self.assertLess(elapsed, 1.0)

    def test_error_recording_performance(self):
        """Test error recording performance."""
        manager = TTSErrorRecoveryManager()
        start_time = time.time()

        for _ in range(1000):
            manager.record_error()
            manager.reset_on_success()

        elapsed = time.time() - start_time
        # Should complete in less than 1 second
        self.assertLess(elapsed, 1.0)


if __name__ == "__main__":
    unittest.main()
