#!/usr/bin/env python3
"""
Optimized Async Bridge - 增強的橋接器
提供高效的 HMI ↔️ 業務邏輯通信
"""

import asyncio
import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from speakub.core.threading_model import get_threading_model

logger = logging.getLogger(__name__)


class OptimizedAsyncBridge:
    """
    優化異步橋接器 - 專門處理 HMI 線程安全

    特性：
    - 專用線程池用於 HMI 操作
    - 專用線程池用於 async I/O
    - 操作統計和性能監控
    - 自動故障恢復
    - 負載均衡
    """

    def __init__(self, tts_integration):
        self.tts_integration = tts_integration
        self.threading_model = get_threading_model()

        # 專用線程池
        self._hmi_executor = ThreadPoolExecutor(
            max_workers=2, thread_name_prefix="HMI-Bridge"  # HMI 操作通常只需要少量線程
        )
        self._io_executor = ThreadPoolExecutor(
            max_workers=4, thread_name_prefix="IO-Bridge"  # I/O 操作可以使用更多線程
        )

        # 性能監控
        self._operation_stats = {
            "hmi_calls": {"total": 0, "success": 0, "failed": 0, "avg_time": 0.0},
            "async_calls": {"total": 0, "success": 0, "failed": 0, "avg_time": 0.0},
            "sync_calls": {"total": 0, "success": 0, "failed": 0, "avg_time": 0.0},
        }
        self._stats_lock = threading.Lock()

        # 健康檢查
        self._last_health_check = time.time()
        self._health_check_interval = 60.0  # 每分鐘檢查一次

        # 故障恢復
        self._consecutive_failures = 0
        self._max_consecutive_failures = 5
        self._circuit_breaker_active = False

        logger.info("Optimized Async Bridge initialized")

    def call_hmi_safe(
        self, hmi_func: Callable, *args, timeout: float = 1.0, **kwargs
    ) -> Any:
        """
        安全調用 HMI 函數（從任何線程）

        Args:
            hmi_func: HMI 函數（必須快速響應）
            *args: 位置參數
            timeout: 超時時間（秒）
            **kwargs: 關鍵字參數

        Returns:
            函數返回值
        """
        start_time = time.time()

        try:
            # 檢查當前線程
            if self.threading_model.is_hmi_thread():
                # 已在 HMI 線程，直接調用
                result = hmi_func(*args, **kwargs)
                self._record_operation("hmi_calls", True, time.time() - start_time)
                return result
            else:
                # 從其他線程，使用線程池橋接
                future = self._hmi_executor.submit(hmi_func, *args, **kwargs)
                result = future.result(timeout=timeout)
                self._record_operation("hmi_calls", True, time.time() - start_time)
                return result

        except Exception as e:
            duration = time.time() - start_time
            self._record_operation("hmi_calls", False, duration)
            logger.error(f"HMI call failed after {duration:.3f}s: {e}")
            raise

    def call_async_safe(self, coro, timeout: float = 5.0) -> Any:
        """
        安全調用異步協程（從同步上下文）

        Args:
            coro: 異步協程
            timeout: 超時時間（秒）

        Returns:
            協程結果
        """
        start_time = time.time()

        try:
            if not self.threading_model.async_loop:
                raise RuntimeError("Async worker loop not available")

            future = asyncio.run_coroutine_threadsafe(
                coro, self.threading_model.async_loop
            )
            result = future.result(timeout=timeout)
            self._record_operation("async_calls", True, time.time() - start_time)
            return result

        except Exception as e:
            duration = time.time() - start_time
            self._record_operation("async_calls", False, duration)
            logger.error(f"Async call failed after {duration:.3f}s: {e}")
            raise

    def call_sync_safe(
        self, sync_func: Callable, *args, timeout: float = 2.0, **kwargs
    ) -> Any:
        """
        安全調用同步函數（在線程池中）

        Args:
            sync_func: 同步函數
            *args: 位置參數
            timeout: 超時時間（秒）
            **kwargs: 關鍵字參數

        Returns:
            函數返回值
        """
        start_time = time.time()

        try:
            future = self._io_executor.submit(sync_func, *args, **kwargs)
            result = future.result(timeout=timeout)
            self._record_operation("sync_calls", True, time.time() - start_time)
            return result

        except Exception as e:
            duration = time.time() - start_time
            self._record_operation("sync_calls", False, duration)
            logger.error(f"Sync call failed after {duration:.3f}s: {e}")
            raise

    def delegate_to_async_task(
        self,
        coro,
        task_name: str = "async_task",
        on_completion: Optional[Callable] = None,
    ) -> bool:
        """
        將協程委派給異步任務執行（非阻塞）

        Args:
            coro: 異步協程
            task_name: 任務名稱
            on_completion: 完成回調函數

        Returns:
            是否成功委派
        """
        try:
            if not self.threading_model.async_loop:
                logger.error("Async loop not available for task delegation")
                return False

            async def _run_with_callback():
                try:
                    result = await coro
                    if on_completion:
                        # 在適當的線程中調用回調
                        if self.threading_model.is_main_thread():
                            on_completion(result)
                        else:
                            self.call_hmi_safe(on_completion, result)
                except Exception as e:
                    logger.error(f"Async task '{task_name}' failed: {e}")

            task = self.threading_model.async_loop.create_task(
                _run_with_callback(), name=task_name
            )

            # 添加到活躍任務集合（如果有的話）
            if hasattr(self.tts_integration, "_tts_active_tasks"):
                self.tts_integration._tts_active_tasks.add(task)

            logger.debug(f"Delegated async task: {task_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delegate async task '{task_name}': {e}")
            return False

    def get_bridge_stats(self) -> Dict[str, Any]:
        """獲取橋接統計信息"""
        with self._stats_lock:
            stats = self._operation_stats.copy()

        # 計算成功率
        for op_type in stats:
            total = stats[op_type]["total"]
            success = stats[op_type]["success"]
            stats[op_type]["success_rate"] = (success / total * 100) if total > 0 else 0

        # 線程池狀態
        hmi_pool_stats = {
            "active_threads": len(self._hmi_executor._threads),
            "pending_tasks": self._hmi_executor._work_queue.qsize(),
        }

        io_pool_stats = {
            "active_threads": len(self._io_executor._threads),
            "pending_tasks": self._io_executor._work_queue.qsize(),
        }

        return {
            "operation_stats": stats,
            "thread_pools": {"hmi_pool": hmi_pool_stats, "io_pool": io_pool_stats},
            "health": self._get_health_status(),
            "circuit_breaker": {
                "active": self._circuit_breaker_active,
                "consecutive_failures": self._consecutive_failures,
            },
        }

    def perform_health_check(self) -> Dict[str, Any]:
        """執行橋接器健康檢查"""
        self._last_health_check = time.time()

        health_status = {
            "timestamp": self._last_health_check,
            "hmi_executor_alive": self._hmi_executor is not None,
            "io_executor_alive": self._io_executor is not None,
            "async_loop_available": self.threading_model.async_loop is not None,
            "circuit_breaker_active": self._circuit_breaker_active,
        }

        # 測試基本功能
        try:
            # 測試簡單的 HMI 調用
            result = self.call_hmi_safe(lambda: "health_check", timeout=0.1)
            health_status["hmi_call_test"] = result == "health_check"
        except Exception as e:
            health_status["hmi_call_test"] = False
            health_status["hmi_call_error"] = str(e)

        try:
            # 測試簡單的異步調用
            async def test_coro():
                await asyncio.sleep(0.01)
                return "async_ok"

            result = self.call_async_safe(test_coro(), timeout=0.1)
            health_status["async_call_test"] = result == "async_ok"
        except Exception as e:
            health_status["async_call_test"] = False
            health_status["async_call_error"] = str(e)

        # 更新健康狀態
        all_tests_pass = all(
            [
                health_status.get("hmi_call_test", False),
                health_status.get("async_call_test", False),
                health_status.get("hmi_executor_alive", False),
                health_status.get("io_executor_alive", False),
                health_status.get("async_loop_available", False),
            ]
        )

        health_status["overall_healthy"] = all_tests_pass

        if not all_tests_pass:
            self._consecutive_failures += 1
            if self._consecutive_failures >= self._max_consecutive_failures:
                self._circuit_breaker_active = True
                logger.warning("Circuit breaker activated due to repeated failures")
        else:
            self._consecutive_failures = 0
            if self._circuit_breaker_active:
                self._circuit_breaker_active = False
                logger.info("Circuit breaker deactivated - service recovered")

        return health_status

    def _get_health_status(self) -> Dict[str, Any]:
        """獲取當前健康狀態"""
        time_since_check = time.time() - self._last_health_check

        if time_since_check > self._health_check_interval:
            # 自動執行健康檢查
            health = self.perform_health_check()
        else:
            # 返回最後的檢查結果
            health = {
                "timestamp": self._last_health_check,
                "overall_healthy": not self._circuit_breaker_active,
                "stale": False,
            }

        return health

    def _record_operation(self, op_type: str, success: bool, duration: float) -> None:
        """記錄操作統計"""
        with self._stats_lock:
            stats = self._operation_stats[op_type]
            stats["total"] += 1

            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1

            # 更新平均時間（簡單移動平均）
            if stats["total"] == 1:
                stats["avg_time"] = duration
            else:
                stats["avg_time"] = (
                    stats["avg_time"] * (stats["total"] - 1) + duration
                ) / stats["total"]

    def shutdown(self) -> None:
        """關閉橋接器"""
        logger.info("Shutting down Optimized Async Bridge")

        # 關閉線程池
        self._hmi_executor.shutdown(wait=True)
        self._io_executor.shutdown(wait=True)

        logger.info("Optimized Async Bridge shutdown complete")

    def __del__(self):
        """析構函數確保資源清理"""
        try:
            self.shutdown()
        except Exception:
            pass  # 忽略關閉錯誤
