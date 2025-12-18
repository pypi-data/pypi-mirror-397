#!/usr/bin/env python3
"""
TTS Command Queue - HMI 命令模式實現
隔離 HMI 事件與後台處理
"""

import logging
import queue
import threading
import time
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class TTSCommandQueue:
    """
    TTS 命令隊列 - 實現 HMI 命令模式

    目的：
    - HMI 層只負責發送命令，不等待執行
    - 後台線程負責處理命令
    - 確保 UI 響應性

    設計原則：
    - HMI 事件處理必須 < 16ms
    - 命令是非阻塞的
    - 命令處理是線程安全的
    """

    def __init__(self, max_queue_size: int = 100):
        self.command_queue: queue.Queue[Tuple[str, Dict[str, Any]]] = queue.Queue(
            maxsize=max_queue_size
        )
        self._shutdown_event = threading.Event()
        self._command_thread: Optional[threading.Thread] = None
        self._command_handlers: Dict[str, Callable] = {}

    def register_handler(self, command: str, handler: Callable) -> None:
        """註冊命令處理器"""
        self._command_handlers[command] = handler
        logger.debug(f"Registered command handler: {command}")

    def send_command(self, command: str, **kwargs) -> bool:
        """
        發送命令到隊列（非阻塞）

        Args:
            command: 命令名稱
            **kwargs: 命令參數

        Returns:
            bool: 是否成功發送
        """
        try:
            self.command_queue.put((command, kwargs), block=False, timeout=0.1)
            logger.debug(f"Command sent: {command}")
            return True
        except queue.Full:
            logger.warning(f"Command queue full, dropping command: {command}")
            return False

    def start_processing(self) -> None:
        """啟動命令處理線程"""
        if self._command_thread and self._command_thread.is_alive():
            logger.warning("Command processing thread already running")
            return

        def process_commands():
            """命令處理循環"""
            logger.info("Command processing thread started")

            while not self._shutdown_event.is_set():
                try:
                    # 非阻塞等待命令
                    command, kwargs = self.command_queue.get(timeout=0.1)

                    # 處理命令
                    self._handle_command(command, kwargs)

                    # 標記任務完成
                    self.command_queue.task_done()

                except queue.Empty:
                    # 沒有命令，繼續等待
                    continue
                except Exception as e:
                    logger.error(f"Error processing command: {e}")

            logger.info("Command processing thread stopped")

        self._command_thread = threading.Thread(
            target=process_commands, name="TTS-Command-Processor", daemon=True
        )
        self._command_thread.start()

    def stop_processing(self, timeout: float = 2.0) -> None:
        """停止命令處理"""
        logger.info("Stopping command processing...")

        self._shutdown_event.set()

        if self._command_thread and self._command_thread.is_alive():
            self._command_thread.join(timeout=timeout)
            if self._command_thread.is_alive():
                logger.warning("Command processing thread did not stop gracefully")

    def get_queue_status(self) -> Dict[str, Any]:
        """獲取隊列狀態"""
        return {
            "queue_size": self.command_queue.qsize(),
            "max_size": self.command_queue.maxsize,
            "handlers_registered": len(self._command_handlers),
            "is_processing": self._command_thread.is_alive()
            if self._command_thread
            else False,
        }

    def _handle_command(self, command: str, kwargs: Dict[str, Any]) -> None:
        """處理單個命令"""
        handler = self._command_handlers.get(command)
        if handler:
            try:
                logger.debug(f"Executing command: {command} with args: {kwargs}")
                handler(**kwargs)
            except Exception as e:
                logger.error(f"Command execution failed: {command}, error: {e}")
        else:
            logger.warning(f"No handler registered for command: {command}")


class TTSStateManager:
    """
    TTS 狀態管理器 - 線程安全的狀態同步

    實現觀察者模式，在不同線程間安全同步狀態。
    支持狀態驗證、歷史記錄和錯誤恢復。
    """

    VALID_STATES = {"IDLE", "PLAYING", "PAUSED", "STOPPED", "ERROR"}
    VALID_TRANSITIONS = {
        "IDLE": {"PLAYING", "STOPPED"},
        "PLAYING": {"PAUSED", "STOPPED", "ERROR"},
        "PAUSED": {"PLAYING", "STOPPED", "ERROR"},
        "STOPPED": {"PLAYING", "IDLE", "ERROR"},
        "ERROR": {"IDLE", "STOPPED"},
    }

    def __init__(self):
        self._state = "IDLE"
        self._lock = threading.Lock()
        self._observers: list[Callable[[str, str], None]] = []
        self._state_history: list[Tuple[str, float]] = []  # (state, timestamp)
        self._max_history = 50  # 保留最近50個狀態變化

    def set_state(self, new_state: str) -> bool:
        """
        設置狀態並通知觀察者

        Args:
            new_state: 新狀態

        Returns:
            bool: 是否成功設置狀態
        """
        if new_state not in self.VALID_STATES:
            logger.error(f"Invalid state: {new_state}")
            return False

        with self._lock:
            current_state = self._state

            # 驗證狀態轉換
            valid_transitions = self.VALID_TRANSITIONS.get(current_state, set())
            if new_state not in valid_transitions:
                logger.warning(
                    f"Invalid state transition: {current_state} -> {new_state}"
                )
                # 允許無效轉換，但記錄警告

            self._state = new_state

            # 記錄狀態歷史
            self._record_state_change(current_state, new_state)

        # 在鎖外通知，避免阻塞
        self._notify_observers(current_state, new_state)
        logger.debug(f"State changed: {current_state} -> {new_state}")

        return True

    def get_state(self) -> str:
        """獲取當前狀態"""
        with self._lock:
            return self._state

    def add_observer(self, callback: Callable[[str, str], None]) -> None:
        """添加狀態變化觀察者"""
        with self._lock:
            if callback not in self._observers:
                self._observers.append(callback)
                logger.debug(f"Added state observer: {callback}")

    def remove_observer(self, callback: Callable[[str, str], None]) -> None:
        """移除狀態變化觀察者"""
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)
                logger.debug(f"Removed state observer: {callback}")

    def get_state_history(self) -> list[Tuple[str, float]]:
        """獲取狀態變化歷史"""
        with self._lock:
            return self._state_history.copy()

    def get_state_stats(self) -> Dict[str, Any]:
        """獲取狀態統計信息"""
        with self._lock:
            stats = {}
            total_time = 0

            if self._state_history:
                # 計算每個狀態的持續時間
                for i, (state, timestamp) in enumerate(self._state_history):
                    if i < len(self._state_history) - 1:
                        next_timestamp = self._state_history[i + 1][1]
                        duration = next_timestamp - timestamp
                    else:
                        # 當前狀態的持續時間
                        duration = time.time() - timestamp

                    stats[state] = stats.get(state, 0) + duration
                    total_time += duration

                # 計算百分比
                for state in stats:
                    percentage = (
                        (stats[state] / total_time * 100) if total_time > 0 else 0
                    )
                    stats[state] = {"duration": stats[state], "percentage": percentage}

            return {
                "current_state": self._state,
                "total_transitions": len(self._state_history),
                "state_breakdown": stats,
                "observers_count": len(self._observers),
            }

    def reset(self) -> None:
        """重置狀態管理器"""
        with self._lock:
            old_state = self._state
            self._state = "IDLE"
            self._state_history.clear()
            self._state_history.append(("IDLE", time.time()))

        if old_state != "IDLE":
            self._notify_observers(old_state, "IDLE")
            logger.info("State manager reset to IDLE")

    def _record_state_change(self, old_state: str, new_state: str) -> None:
        """記錄狀態變化"""
        self._state_history.append((new_state, time.time()))

        # 限制歷史記錄長度
        if len(self._state_history) > self._max_history:
            self._state_history = self._state_history[-self._max_history :]

    def _notify_observers(self, old_state: str, new_state: str) -> None:
        """通知所有觀察者狀態變化"""
        observers_copy = self._observers.copy()  # 避免迭代時修改

        for observer in observers_copy:
            try:
                observer(old_state, new_state)
            except Exception as e:
                logger.error(f"Observer notification failed: {e}")
                # 移除故障的觀察者
                try:
                    self.remove_observer(observer)
                except Exception:
                    pass  # 忽略移除失敗


# 全局實例
_command_queue_instance: Optional[TTSCommandQueue] = None
_state_manager_instance: Optional[TTSStateManager] = None


def get_command_queue() -> TTSCommandQueue:
    """獲取全局命令隊列實例"""
    global _command_queue_instance
    if _command_queue_instance is None:
        _command_queue_instance = TTSCommandQueue()
    return _command_queue_instance


def get_state_manager() -> TTSStateManager:
    """獲取全局狀態管理器實例"""
    global _state_manager_instance
    if _state_manager_instance is None:
        _state_manager_instance = TTSStateManager()
    return _state_manager_instance
