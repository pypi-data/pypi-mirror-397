#!/usr/bin/env python3
"""
Unit tests for pausable_timer.py module.
"""

import asyncio
import time
from unittest.mock import patch, MagicMock, call
import pytest
from speakub.utils.pausable_timer import PausableTimer, TimerManager


class TestPausableTimer:
    """Test cases for PausableTimer class."""

    def test_pausable_timer_initialization(self):
        """Test PausableTimer initialization."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        assert timer.callback == callback
        assert timer.interval == 1.0
        assert timer._handle is None
        assert timer._start_time == 0.0
        assert timer._remaining_time == 0.0
        assert timer._is_paused is False
        assert timer._is_cancelled is False

    def test_pausable_timer_initialization_with_loop(self):
        """Test PausableTimer initialization with custom loop."""
        callback = MagicMock()
        loop = MagicMock()
        timer = PausableTimer(callback, 1.0, loop=loop)

        assert timer.loop == loop

    @patch("asyncio.get_event_loop")
    def test_pausable_timer_initialization_default_loop(self, mock_get_loop):
        """Test PausableTimer initialization with default loop."""
        callback = MagicMock()
        mock_loop = MagicMock()
        mock_get_loop.return_value = mock_loop

        timer = PausableTimer(callback, 1.0)

        mock_get_loop.assert_called_once()
        assert timer.loop == mock_loop

    @patch("speakub.utils.pausable_timer.time.time")
    def test_start_timer(self, mock_time):
        """Test starting the timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        mock_time.return_value = 1000.0

        timer.start()

        assert timer._start_time == 1000.0
        assert timer._remaining_time == 1.0
        assert timer._is_paused is False
        assert timer._is_cancelled is False
        assert timer._handle is not None

    def test_start_cancelled_timer(self):
        """Test starting a cancelled timer does nothing."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._is_cancelled = True

        timer.start()

        assert timer._handle is None

    @patch("speakub.utils.pausable_timer.time.time")
    def test_pause_timer(self, mock_time):
        """Test pausing the timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 2.0)
        mock_time.return_value = 1000.0

        timer.start()
        mock_time.return_value = 1001.0  # 1 second elapsed
        timer.pause()

        assert timer._is_paused is True
        assert timer._remaining_time == 1.0  # 2.0 - 1.0

    def test_pause_already_paused_timer(self):
        """Test pausing an already paused timer does nothing."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._is_paused = True

        timer.pause()

        # Should remain paused
        assert timer._is_paused is True

    def test_pause_cancelled_timer(self):
        """Test pausing a cancelled timer does nothing."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._is_cancelled = True

        timer.pause()

        # Should remain cancelled
        assert timer._is_cancelled is True

    @patch("speakub.utils.pausable_timer.time.time")
    def test_resume_timer(self, mock_time):
        """Test resuming the timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 2.0)
        mock_time.return_value = 1000.0

        timer.start()
        timer.pause()
        mock_time.return_value = 1005.0  # 5 seconds after pause

        timer.resume()

        assert timer._is_paused is False
        assert timer._start_time == 1005.0
        assert timer._handle is not None

    def test_resume_not_paused_timer(self):
        """Test resuming a timer that is not paused does nothing."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        timer.resume()

        # Should remain not paused
        assert timer._is_paused is False

    def test_resume_cancelled_timer(self):
        """Test resuming a cancelled timer does nothing."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._is_cancelled = True

        timer.resume()

        # Should remain cancelled
        assert timer._is_cancelled is True

    def test_cancel_timer(self):
        """Test cancelling the timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer.start()

        timer.cancel()

        assert timer._is_cancelled is True
        assert timer._is_paused is False
        assert timer._handle is None

    def test_reset_timer(self):
        """Test resetting the timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 2.0)
        timer.start()

        timer.reset(3.0)

        assert timer.interval == 3.0
        assert timer._remaining_time == 3.0
        assert timer._is_paused is False
        assert timer._is_cancelled is False

    def test_reset_cancelled_timer(self):
        """Test resetting a cancelled timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._is_cancelled = True

        timer.reset()

        # Reset should restart the timer, so it should not be cancelled anymore
        assert timer._is_cancelled is False
        assert timer._is_paused is False

    def test_is_active_timer(self):
        """Test checking if timer is active."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        # Not active initially
        assert timer.is_active() is False

        timer.start()
        # Active after start
        assert timer.is_active() is True

        timer.pause()
        # Not active when paused
        assert timer.is_active() is False

        timer.cancel()
        # Not active when cancelled
        assert timer.is_active() is False

    def test_is_paused_timer(self):
        """Test checking if timer is paused."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        assert timer.is_paused() is False

        timer.pause()
        assert timer.is_paused() is True

    @patch("speakub.utils.pausable_timer.time.time")
    def test_get_remaining_time_active(self, mock_time):
        """Test getting remaining time for active timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 2.0)
        mock_time.return_value = 1000.0

        timer.start()
        mock_time.return_value = 1001.0  # 1 second elapsed

        remaining = timer.get_remaining_time()
        assert remaining == 1.0

    def test_get_remaining_time_paused(self):
        """Test getting remaining time for paused timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 2.0)
        timer._remaining_time = 1.5
        timer._is_paused = True

        remaining = timer.get_remaining_time()
        assert remaining == 1.5

    def test_get_remaining_time_inactive(self):
        """Test getting remaining time for inactive timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        remaining = timer.get_remaining_time()
        assert remaining == 0.0

    @pytest.mark.asyncio
    async def test_callback_execution(self):
        """Test that callback is executed when timer expires."""
        callback = MagicMock()
        timer = PausableTimer(callback, 0.01)  # Very short interval

        timer.start()

        # Wait for callback to execute
        await asyncio.sleep(0.02)

        callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_callback_error_handling(self):
        """Test error handling in callback execution."""
        callback = MagicMock(side_effect=Exception("Callback error"))
        timer = PausableTimer(callback, 0.01)

        timer.start()

        # Wait for callback to execute
        await asyncio.sleep(0.02)

        callback.assert_called_once()
        # Timer should still be in valid state despite callback error

    def test_schedule_callback_cancelled(self):
        """Test _schedule_callback with cancelled timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._is_cancelled = True

        timer._schedule_callback()

        assert timer._handle is None

    def test_schedule_callback_zero_remaining(self):
        """Test _schedule_callback with zero remaining time."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer._remaining_time = 0.0

        timer._schedule_callback()

        assert timer._handle is None


class TestPausableTimerBoundaryConditions:
    """Test boundary conditions and robustness for PausableTimer."""

    @pytest.mark.asyncio
    async def test_pause_during_callback_execution(self):
        """Test pausing timer while callback is executing."""
        callback_executing = asyncio.Event()
        callback_completed = asyncio.Event()

        async def slow_callback():
            """A callback that takes some time to execute."""
            callback_executing.set()
            await asyncio.sleep(0.1)  # Simulate work
            callback_completed.set()

        timer = PausableTimer(slow_callback, 0.01)

        # Start timer
        timer.start()

        # Wait for callback to start executing
        await callback_executing.wait()

        # Pause while callback is still executing
        timer.pause()

        # Wait for callback to complete
        await callback_completed.wait()

        # Verify timer state: should be paused but not cancelled
        assert timer.is_paused()
        assert not timer._is_cancelled
        # Callback should have executed despite pause during execution
        assert callback_completed.is_set()

    @pytest.mark.asyncio
    async def test_resume_during_callback_execution(self):
        """Test resuming timer while callback is executing."""
        callback_executing = asyncio.Event()
        callback_completed = asyncio.Event()

        async def slow_callback():
            """A callback that takes some time to execute."""
            callback_executing.set()
            await asyncio.sleep(0.1)  # Simulate work
            callback_completed.set()

        timer = PausableTimer(slow_callback, 0.01)

        # Pause first, then start
        timer.pause()
        timer.start()

        # Wait for callback to be scheduled but paused
        await asyncio.sleep(0.02)  # Let timer scheduling happen

        # Resume while callback should be starting
        timer.resume()

        # Wait for completion
        await asyncio.sleep(0.2)

        # Callback should still execute normally
        assert callback_completed.is_set()

    @pytest.mark.asyncio
    async def test_cancel_during_callback_execution(self):
        """Test cancelling timer while callback is executing."""
        callback_started = asyncio.Event()
        callback_completed = asyncio.Event()

        async def interrupted_callback():
            """A callback that can be interrupted."""
            callback_started.set()
            try:
                await asyncio.sleep(0.2)  # Long work that might be interrupted
                callback_completed.set()
            except asyncio.CancelledError:
                # Handle cancellation gracefully
                return

        timer = PausableTimer(interrupted_callback, 0.01)

        # Start timer
        timer.start()

        # Wait for callback to start
        await callback_started.wait()

        # Cancel while callback is executing
        timer.cancel()

        # Wait a bit
        await asyncio.sleep(0.05)

        # Timer should be cancelled
        assert timer._is_cancelled
        assert timer._handle is None
        # Note: callback may or may not complete depending on timing

    @pytest.mark.asyncio
    async def test_multiple_pause_resume_cycles(self):
        """Test multiple rapid pause/resume cycles."""
        callback_called = False

        def counting_callback():
            nonlocal callback_called
            callback_called = True

        timer = PausableTimer(counting_callback, 0.05)

        # Start timer
        timer.start()

        # Rapid pause/resume cycles
        for _ in range(10):
            timer.pause()
            await asyncio.sleep(0.01)  # Small delay
            timer.resume()
            await asyncio.sleep(0.01)  # Small delay

        # Let timer operate normally for a while
        await asyncio.sleep(0.5)

        # Verify timer eventually executes callback (timing dependent)
        # The test mainly verifies no crashes during rapid state changes
        assert not timer._is_cancelled  # Should still be operational

    @pytest.mark.asyncio
    async def test_pause_after_cancel(self):
        """Test pausing a cancelled timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        # Cancel timer first
        timer.cancel()
        assert timer._is_cancelled

        # Pause cancelled timer - should not fail
        timer.pause()

        # Should remain cancelled
        assert timer._is_cancelled
        assert timer._handle is None

    @pytest.mark.asyncio
    async def test_resume_after_cancel(self):
        """Test resuming a cancelled timer."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        # Cancel timer first
        timer.cancel()
        assert timer._is_cancelled

        # Resume cancelled timer - should not fail or reactivate
        timer.resume()

        # Should remain cancelled
        assert timer._is_cancelled
        assert timer._handle is None

    def test_reset_while_paused(self):
        """Test resetting timer while it's paused."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)
        timer.start()
        timer.pause()

        # Reset while paused
        timer.reset(2.0)

        # Should be active with new interval, not paused
        assert timer.interval == 2.0
        assert not timer._is_paused
        assert not timer._is_cancelled

    @pytest.mark.asyncio
    async def test_callback_exception_handling(self):
        """Test that callback exceptions don't crash the timer system."""
        async def failing_callback():
            raise ValueError("Callback intentionally fails")

        timer = PausableTimer(failing_callback, 0.01)

        # Start timer - should not raise exception
        timer.start()

        # Wait for callback execution and exception
        await asyncio.sleep(0.05)

        # Timer should handle exception gracefully and not be corrupted
        assert not timer._is_cancelled  # Should still be usable
        # Could schedule another callback if desired

    @pytest.mark.asyncio
    async def test_loop_closure_robustness(self):
        """Test timer handles closed event loop gracefully."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        # Simulate closed loop scenario
        timer._handle = None  # No active handle

        # Operations should not fail
        timer.pause()  # Should be safe
        timer.resume()  # Should be safe
        timer.cancel()  # Should be safe

        assert timer._is_cancelled  # Cancel should work

    def test_get_remaining_time_edge_cases(self):
        """Test get_remaining_time in various edge cases."""
        callback = MagicMock()
        timer = PausableTimer(callback, 1.0)

        # Not started
        assert timer.get_remaining_time() == 0.0

        # Started but not elapsed
        timer.start()
        remaining = timer.get_remaining_time()
        assert remaining > 0.0 and remaining <= 1.0

        # Paused
        timer.pause()
        paused_remaining = timer.get_remaining_time()
        assert paused_remaining == timer._remaining_time

        # Cancelled
        timer.cancel()
        assert timer.get_remaining_time() == 0.0


class TestTimerManager:
    """Test cases for TimerManager class."""

    def test_timer_manager_initialization(self):
        """Test TimerManager initialization."""
        manager = TimerManager()

        assert manager.timers == []
        assert manager._is_paused is False

    def test_add_timer(self):
        """Test adding a timer to the manager."""
        manager = TimerManager()
        timer = MagicMock()

        manager.add_timer(timer)

        assert timer in manager.timers

    def test_remove_timer(self):
        """Test removing a timer from the manager."""
        manager = TimerManager()
        timer = MagicMock()

        manager.add_timer(timer)
        manager.remove_timer(timer)

        assert timer not in manager.timers
        timer.cancel.assert_called_once()

    def test_remove_nonexistent_timer(self):
        """Test removing a timer that doesn't exist."""
        manager = TimerManager()
        timer = MagicMock()

        manager.remove_timer(timer)

        # Should not raise error
        assert timer not in manager.timers

    @patch("speakub.utils.pausable_timer.logger")
    def test_pause_all_timers(self, mock_logger):
        """Test pausing all timers."""
        manager = TimerManager()
        timer1 = MagicMock()
        timer2 = MagicMock()

        manager.add_timer(timer1)
        manager.add_timer(timer2)

        manager.pause_all()

        assert manager._is_paused is True
        timer1.pause.assert_called_once()
        timer2.pause.assert_called_once()
        mock_logger.debug.assert_called_with("Paused 2 timers")

    def test_pause_all_already_paused(self):
        """Test pausing all timers when already paused."""
        manager = TimerManager()
        manager._is_paused = True
        timer = MagicMock()

        manager.add_timer(timer)
        manager.pause_all()

        # Should not pause timers again
        timer.pause.assert_not_called()

    @patch("speakub.utils.pausable_timer.logger")
    def test_resume_all_timers(self, mock_logger):
        """Test resuming all timers."""
        manager = TimerManager()
        manager._is_paused = True
        timer1 = MagicMock()
        timer2 = MagicMock()

        manager.add_timer(timer1)
        manager.add_timer(timer2)

        manager.resume_all()

        assert manager._is_paused is False
        timer1.resume.assert_called_once()
        timer2.resume.assert_called_once()
        mock_logger.debug.assert_called_with("Resumed 2 timers")

    def test_resume_all_not_paused(self):
        """Test resuming all timers when not paused."""
        manager = TimerManager()
        timer = MagicMock()

        manager.add_timer(timer)
        manager.resume_all()

        # Should not resume timers
        timer.resume.assert_not_called()

    @patch("speakub.utils.pausable_timer.logger")
    def test_cancel_all_timers(self, mock_logger):
        """Test cancelling all timers."""
        manager = TimerManager()
        timer1 = MagicMock()
        timer2 = MagicMock()

        manager.add_timer(timer1)
        manager.add_timer(timer2)

        manager.cancel_all()

        assert manager.timers == []
        assert manager._is_paused is False
        timer1.cancel.assert_called_once()
        timer2.cancel.assert_called_once()
        mock_logger.debug.assert_called_with("Cancelled all timers")

    def test_is_paused_manager(self):
        """Test checking if timer manager is paused."""
        manager = TimerManager()

        assert manager.is_paused() is False

        manager._is_paused = True
        assert manager.is_paused() is True


if __name__ == "__main__":
    pytest.main([__file__])
