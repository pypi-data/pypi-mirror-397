#!/usr/bin/env python3
"""TTS Async Manager - Manages async event loop and coroutine execution."""

import asyncio
import logging
import threading
from typing import Any, Awaitable, Callable, List, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TTSAsyncManager:
    """Manages TTS async event loop and coroutine execution in a separate thread."""

    def __init__(self):
        """Initialize async manager."""
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._loop_started = threading.Event()
        self._stop_requested = threading.Event()
        # Track pending futures for cleanup
        self._pending_futures: List[Any] = []
        self._futures_lock = threading.Lock()  # Lock for thread-safe access

    def start_loop(self) -> None:
        """Start the async event loop in a separate thread."""
        if self._thread and self._thread.is_alive():
            logger.debug("Async loop already running")
            return

        self._stop_requested.clear()
        self._loop_started.clear()

        def run_loop():
            """Run the event loop."""
            try:
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)
                self._loop_started.set()
                logger.debug("Async event loop started")
                self._event_loop.run_forever()
            except Exception as e:
                logger.error(f"Error in async event loop: {e}")
            finally:
                if self._event_loop:
                    self._event_loop.close()
                logger.debug("Async event loop closed")

        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()

        # Wait for loop to be ready
        if not self._loop_started.wait(timeout=5.0):
            logger.warning("Timeout waiting for async loop to start")

    def stop_loop(self) -> None:
        """Stop the async event loop."""
        self._stop_requested.set()

        if self._event_loop and self._event_loop.is_running():
            self._event_loop.call_soon_threadsafe(self._event_loop.stop)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                logger.warning("Async thread did not terminate within timeout")

        # Temporarily suppress concurrent.futures logger during cleanup to avoid verbose traces
        import logging
        import concurrent.futures
        cf_logger = logging.getLogger(concurrent.futures.__name__)
        original_level = cf_logger.level
        cf_logger.setLevel(logging.WARNING)

        try:
            # Cancel all pending futures to unblock waiting threads
            import time
            with self._futures_lock:
                for future in self._pending_futures:
                    if not future.done():
                        try:
                            future.cancel()
                            logger.debug(f"Cancelled pending future: {future}")
                        except RuntimeError as e:
                            # Expected error when loop is closed - futures are already cancelled by asyncio
                            if 'Event loop is closed' in str(e):
                                logger.debug(
                                    f"Future already cancelled by asyncio during loop shutdown: {future}")
                            else:
                                logger.warning(
                                    f"Unexpected RuntimeError cancelling future: {e}")
                        except Exception as e:
                            logger.warning(f"Error cancelling future: {e}")
                self._pending_futures.clear()

            # Give futures time to process cancellation
            time.sleep(0.1)
        finally:
            # Restore original logging level
            cf_logger.setLevel(original_level)

        self._event_loop = None
        self._thread = None
        self._loop_started.clear()
        logger.debug("Async event loop stopped")

    def is_running(self) -> bool:
        """Check if async loop is running."""
        if not self._event_loop:
            return False
        return self._event_loop.is_running()

    def run_coroutine_threadsafe(
        self, coro: Awaitable[T], timeout: Optional[float] = None
    ) -> T:
        """
        Run a coroutine in the event loop from another thread.

        Args:
            coro: Coroutine to run
            timeout: Optional timeout in seconds

        Returns:
            Result of the coroutine

        Raises:
            RuntimeError: If loop is not running or closed
            asyncio.TimeoutError: If timeout is exceeded
            CancelledError: If loop closes while waiting
        """
        if not self._event_loop or not self._event_loop.is_running():
            raise RuntimeError("Async event loop is not running")

        future = asyncio.run_coroutine_threadsafe(coro, self._event_loop)

        # Track this future for cleanup
        with self._futures_lock:
            self._pending_futures.append(future)

        try:
            return future.result(timeout=timeout)
        except asyncio.TimeoutError:
            logger.error(f"Coroutine timed out after {timeout}s")
            raise
        except (asyncio.CancelledError, Exception) as e:
            # Check if loop is still running - if not, it was closed during wait
            try:
                if self._event_loop and not self._event_loop.is_running():
                    logger.warning(
                        f"Coroutine cancelled - event loop closed: {type(e).__name__}")
                    future.cancel()
                    raise RuntimeError(
                        "Async event loop is not running") from e
            except:
                pass
            raise
        finally:
            # Remove from tracking once done
            with self._futures_lock:
                try:
                    self._pending_futures.remove(future)
                except ValueError:
                    pass

    def run_coroutine_async(
        self, coro: Awaitable[T], on_done: Optional[Callable[[Any], None]] = None
    ) -> None:
        """
        Schedule a coroutine to run in the event loop without waiting for result.

        Args:
            coro: Coroutine to run
            on_done: Optional callback when coroutine completes (receives result or exception)
        """
        if not self._event_loop or not self._event_loop.is_running():
            logger.error("Async event loop is not running")
            return

        future = asyncio.run_coroutine_threadsafe(coro, self._event_loop)

        if on_done:
            future.add_done_callback(on_done)

    def reset(self) -> None:
        """Reset async manager state."""
        self.stop_loop()
        self._stop_requested.clear()
        logger.debug("Async manager reset")

    def get_status(self) -> dict:
        """
        Get current status.

        Returns:
            dict: Status information
        """
        return {
            "loop_running": self.is_running(),
            "thread_alive": self._thread.is_alive() if self._thread else False,
            "stop_requested": self._stop_requested.is_set(),
        }
