#!/usr/bin/env python3
"""
SpeakUB Threading Model Manager
Clearly define responsibilities and communication mechanisms for each thread
"""

import asyncio
import logging
import threading
import time
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


class ThreadType(Enum):
    """Thread type definitions"""

    MAIN_UI = "main_ui"  # Main UI thread (Textual)
    ASYNC_WORKER = "async_worker"  # Async worker thread (TTS synthesis)
    PLAYBACK_HMI = "playback_hmi"  # Playback HMI thread (MPV/Pygame)
    COMMAND_COORDINATOR = "command_coordinator"  # Command coordinator thread


class SpeakUBThreadingModel:
    """
    SpeakUB Threading Model Manager

    Responsible for:
    1. Clearly define responsibilities of each thread
    2. Provide thread-safe communication mechanisms
    3. Monitor thread health status
    4. Ensure HMI layer responsiveness

    Thread model:
    - Main Thread: Textual UI (synchronous HMI)
    - Async Worker Thread: TTS synthesis (async I/O)
    - Playback Thread: Audio playback (blocking HMI)
    - Command Thread: Coordinator (command processing)
    """

    def __init__(self):
        # Thread references
        self.main_thread: threading.Thread = threading.main_thread()
        self.async_worker_thread: Optional[threading.Thread] = None
        self.playback_thread: Optional[threading.Thread] = None
        self.command_thread: Optional[threading.Thread] = None

        # Event loop reference
        self.async_loop: Optional[asyncio.AbstractEventLoop] = None

        # Thread health monitoring
        self._thread_health: Dict[ThreadType, Dict[str, Any]] = {}
        self._health_check_interval = 30.0  # Check every 30 seconds
        self._health_monitor_active = False

        # Initialize thread health status
        for thread_type in ThreadType:
            self._thread_health[thread_type] = {
                "last_seen": time.time(),
                "is_alive": False,
                "cpu_percent": 0.0,
                "memory_mb": 0.0,
                "error_count": 0,
                "last_error": None,
            }

        # Lock for thread-safe operations
        self._health_lock = threading.Lock()

    def start_async_worker(self) -> None:
        """Start async worker thread"""
        if self.async_worker_thread and self.async_worker_thread.is_alive():
            logger.warning("Async worker thread already running")
            return

        def run_async_loop():
            """Main loop for async worker thread"""
            try:
                self.async_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.async_loop)

                # Update thread health status
                self._update_thread_health(ThreadType.ASYNC_WORKER, alive=True)

                logger.info("Async worker thread started")
                self.async_loop.run_forever()
            except Exception as e:
                logger.error(f"Async worker thread error: {e}")
                self._update_thread_health(ThreadType.ASYNC_WORKER, error=str(e))
            finally:
                logger.info("Async worker thread stopped")

        self.async_worker_thread = threading.Thread(
            target=run_async_loop, name="TTS-Async-Worker", daemon=True
        )
        self.async_worker_thread.start()

        # Wait for thread to fully start
        time.sleep(0.1)

    def start_command_coordinator(self, command_processor: Callable) -> None:
        """Start command coordinator thread"""
        if self.command_thread and self.command_thread.is_alive():
            logger.warning("Command coordinator thread already running")
            return

        def run_command_loop():
            """Main loop for command coordinator thread"""
            try:
                self._update_thread_health(ThreadType.COMMAND_COORDINATOR, alive=True)
                logger.info("Command coordinator thread started")
                command_processor()  # Run command processor
            except Exception as e:
                logger.error(f"Command coordinator thread error: {e}")
                self._update_thread_health(ThreadType.COMMAND_COORDINATOR, error=str(e))
            finally:
                logger.info("Command coordinator thread stopped")

        self.command_thread = threading.Thread(
            target=run_command_loop, name="TTS-Command-Coordinator", daemon=True
        )
        self.command_thread.start()

    def start_playback_thread(self, playback_processor: Callable) -> None:
        """Start playback HMI thread"""
        if self.playback_thread and self.playback_thread.is_alive():
            logger.warning("Playback thread already running")
            return

        def run_playback_loop():
            """Main loop for playback thread"""
            try:
                self._update_thread_health(ThreadType.PLAYBACK_HMI, alive=True)
                logger.info("Playback HMI thread started")
                playback_processor()  # Run playback processor
            except Exception as e:
                logger.error(f"Playback thread error: {e}")
                self._update_thread_health(ThreadType.PLAYBACK_HMI, error=str(e))
            finally:
                logger.info("Playback HMI thread stopped")

        self.playback_thread = threading.Thread(
            target=run_playback_loop, name="TTS-Playback-HMI", daemon=True
        )
        self.playback_thread.start()

    def is_main_thread(self) -> bool:
        """Check if in main UI thread"""
        return threading.current_thread() == self.main_thread

    def is_async_worker_thread(self) -> bool:
        """Check if in async worker thread"""
        return threading.current_thread() == self.async_worker_thread

    def is_playback_thread(self) -> bool:
        """Check if in playback HMI thread"""
        return threading.current_thread() == self.playback_thread

    def is_command_thread(self) -> bool:
        """Check if in command coordinator thread"""
        return threading.current_thread() == self.command_thread

    def is_hmi_thread(self) -> bool:
        """Check if in any HMI thread (must remain synchronous)"""
        current = threading.current_thread()
        return current in [self.main_thread, self.playback_thread]

    def get_current_thread_type(self) -> Optional[ThreadType]:
        """Get current thread type"""
        if self.is_main_thread():
            return ThreadType.MAIN_UI
        elif self.is_async_worker_thread():
            return ThreadType.ASYNC_WORKER
        elif self.is_playback_thread():
            return ThreadType.PLAYBACK_HMI
        elif self.is_command_thread():
            return ThreadType.COMMAND_COORDINATOR
        return None

    def call_async_worker(self, coro, timeout: float = 5.0):
        """Safely call async worker thread from other threads"""
        if not self.async_loop or self.async_loop.is_closed():
            raise RuntimeError("Async worker loop not available")

        future = asyncio.run_coroutine_threadsafe(coro, self.async_loop)
        return future.result(timeout=timeout)

    def call_from_async_worker(self, func: Callable, *args, **kwargs):
        """Safely call main thread from async worker thread"""
        # Use Textual's call_from_thread or similar mechanism
        # Needs integration with specific App instance
        raise NotImplementedError("Needs integration with specific UI framework")

    def start_health_monitoring(self) -> None:
        """Start thread health monitoring"""
        if self._health_monitor_active:
            return

        self._health_monitor_active = True

        def health_monitor_loop():
            """Health monitoring loop"""
            while self._health_monitor_active:
                try:
                    self._perform_health_check()
                except Exception as e:
                    logger.error(f"Health monitoring error: {e}")

                time.sleep(self._health_check_interval)

        monitor_thread = threading.Thread(
            target=health_monitor_loop, name="Thread-Health-Monitor", daemon=True
        )
        monitor_thread.start()
        logger.info("Thread health monitoring started")

    def stop_health_monitoring(self) -> None:
        """Stop thread health monitoring"""
        self._health_monitor_active = False

    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all threads"""
        with self._health_lock:
            status = {}
            for thread_type, health in self._thread_health.items():
                status[thread_type.value] = health.copy()
            return status

    def _update_thread_health(
        self,
        thread_type: ThreadType,
        alive: Optional[bool] = None,
        error: Optional[str] = None,
        cpu_percent: Optional[float] = None,
        memory_mb: Optional[float] = None,
    ):
        """Update thread health status"""
        with self._health_lock:
            health = self._thread_health[thread_type]
            health["last_seen"] = time.time()

            if alive is not None:
                health["is_alive"] = alive

            if error is not None:
                health["error_count"] += 1
                health["last_error"] = error

            if cpu_percent is not None:
                health["cpu_percent"] = cpu_percent

            if memory_mb is not None:
                health["memory_mb"] = memory_mb

    def _perform_health_check(self) -> None:
        """Perform thread health check"""
        try:
            import psutil

            current_process = psutil.Process()

            # Check main thread
            if self.main_thread.is_alive():
                self._update_thread_health(ThreadType.MAIN_UI, alive=True)

            # Check async worker thread
            if self.async_worker_thread and self.async_worker_thread.is_alive():
                self._update_thread_health(ThreadType.ASYNC_WORKER, alive=True)

            # Check playback thread
            if self.playback_thread and self.playback_thread.is_alive():
                self._update_thread_health(ThreadType.PLAYBACK_HMI, alive=True)

            # Check command thread
            if self.command_thread and self.command_thread.is_alive():
                self._update_thread_health(ThreadType.COMMAND_COORDINATOR, alive=True)

            # Update process-level resource usage
            memory_mb = current_process.memory_info().rss / 1024 / 1024
            cpu_percent = current_process.cpu_percent(interval=1.0)

            # Allocate to each thread (approximate values)
            for thread_type in ThreadType:
                self._update_thread_health(
                    thread_type, memory_mb=memory_mb, cpu_percent=cpu_percent
                )

        except ImportError:
            # psutil not available, only check if threads are alive
            logger.debug("psutil not available, basic health check only")

            for thread_type in ThreadType:
                thread = getattr(self, f"{thread_type.value}_thread", None)
                if thread and thread.is_alive():
                    self._update_thread_health(thread_type, alive=True)

        except Exception as e:
            logger.error(f"Health check failed: {e}")

    def shutdown(self) -> None:
        """Shutdown threading model manager"""
        logger.info("Shutting down threading model")

        self.stop_health_monitoring()

        # Stop async loop
        if self.async_loop and not self.async_loop.is_closed():
            self.async_loop.stop()

        # Wait for threads to end (give reasonable time)
        threads_to_wait = [
            self.async_worker_thread,
            self.playback_thread,
            self.command_thread,
        ]

        for thread in threads_to_wait:
            if thread and thread.is_alive():
                thread.join(timeout=2.0)
                if thread.is_alive():
                    logger.warning(f"Thread {thread.name} did not stop gracefully")

        logger.info("Threading model shutdown complete")


# Global threading model instance
_threading_model_instance: Optional[SpeakUBThreadingModel] = None


def get_threading_model() -> SpeakUBThreadingModel:
    """Get global threading model instance"""
    global _threading_model_instance
    if _threading_model_instance is None:
        _threading_model_instance = SpeakUBThreadingModel()
    return _threading_model_instance


def init_threading_model() -> SpeakUBThreadingModel:
    """Initialize threading model"""
    model = get_threading_model()
    model.start_health_monitoring()
    return model
