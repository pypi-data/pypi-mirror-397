#!/usr/bin/env python3
"""
Unified TTS Error Handler for SpeakUB.
Provides centralized error handling for TTS runners and operations.
"""

import asyncio
import logging
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from speakub.tts.integration import TTSIntegration

logger = logging.getLogger(__name__)


class TTSErrorType(Enum):
    """TTS error type classifications."""

    NETWORK = "network"
    TTS_SYNTHESIS = "tts_synthesis"
    TTS_PLAYBACK = "tts_playback"
    TTS_VOICE = "tts_voice"
    MEMORY = "memory"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    UNEXPECTED = "unexpected"


class TTSErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"  # Minor issues, can continue
    MEDIUM = "medium"  # Significant issues, may need user attention
    HIGH = "high"  # Critical issues, stop operation
    CRITICAL = "critical"  # System-level issues


class TTSErrorAction(Enum):
    """Actions to take when an error occurs."""

    CONTINUE = "continue"  # Continue operation
    RETRY = "retry"  # Retry the operation
    PAUSE = "pause"  # Pause and wait for user
    STOP = "stop"  # Stop the operation
    RESTART = "restart"  # Restart the system/component
    NOTIFY_ONLY = "notify_only"  # Just notify, don't change state


class TTSRunnerError:
    """Represents a TTS runner error with metadata."""

    def __init__(
        self,
        error: Exception,
        error_type: TTSErrorType,
        severity: TTSErrorSeverity,
        context: str,
        playlist_index: Optional[int] = None,
        content_snippet: Optional[str] = None,
        recoverable: bool = False,
    ):
        self.error = error
        self.error_type = error_type
        self.severity = severity
        self.context = context
        self.playlist_index = playlist_index
        self.content_snippet = content_snippet or ""
        self.recoverable = recoverable
        self.timestamp = (
            asyncio.get_event_loop().time() if asyncio.get_running_loop() else None
        )

    def __str__(self) -> str:
        return (
            f"[{self.error_type.value}] {type(self.error).__name__}: {str(self.error)}"
        )


class TTSRunnerErrorHandler:
    """
    Unified error handler for TTS runners.
    Provides centralized error processing, logging, and user notification.
    """

    def __init__(self):
        self._error_counts: Dict[TTSErrorType, int] = {}
        self._recent_errors: list[TTSRunnerError] = []
        self._max_recent_errors = 10

    async def handle_runner_error(
        self,
        error: Exception,
        context: str,
        tts_integration: "TTSIntegration",
        playlist_manager=None,
        playlist_index: Optional[int] = None,
    ) -> TTSErrorAction:
        """
        Handle a TTS runner error with unified processing.

        Args:
            error: The exception that occurred
            context: Context where the error occurred
            tts_integration: TTS integration instance
            playlist_manager: Playlist manager instance (optional)
            playlist_index: Current playlist index (optional)

        Returns:
            TTSErrorAction: Recommended action to take
        """
        # Classify the error
        runner_error = self._classify_error(error, context, playlist_index)

        # Update error statistics
        self._update_error_stats(runner_error)

        # Log the error with appropriate level
        await self._log_error(runner_error)

        # Determine action based on error type and severity
        action = self._determine_action(runner_error)

        # Execute the action
        await self._execute_action(
            action, runner_error, tts_integration, playlist_manager
        )

        return action

    def _classify_error(
        self, error: Exception, context: str, playlist_index: Optional[int] = None
    ) -> TTSRunnerError:
        """Classify an error into TTS error type and determine severity."""

        error_type = TTSErrorType.UNEXPECTED
        severity = TTSErrorSeverity.MEDIUM
        recoverable = False

        # Timeout errors (check first since TimeoutError inherits from OSError)
        if isinstance(error, asyncio.TimeoutError):
            error_type = TTSErrorType.TIMEOUT
            severity = TTSErrorSeverity.HIGH
            recoverable = True

        # Network errors
        elif isinstance(error, (OSError, ConnectionError)):
            if hasattr(error, "errno") and error.errno in (
                110,
                111,
            ):  # Connection timed out/refused
                error_type = TTSErrorType.NETWORK
                severity = TTSErrorSeverity.HIGH
                recoverable = True
            else:
                error_type = TTSErrorType.NETWORK
                severity = TTSErrorSeverity.MEDIUM
                recoverable = True

        # TTS specific errors
        elif hasattr(error, "__class__") and "TTS" in error.__class__.__name__:
            if "Synthesis" in error.__class__.__name__:
                error_type = TTSErrorType.TTS_SYNTHESIS
                severity = TTSErrorSeverity.HIGH
                recoverable = True
            elif "Playback" in error.__class__.__name__:
                error_type = TTSErrorType.TTS_PLAYBACK
                severity = TTSErrorSeverity.HIGH
                recoverable = False
            elif "Voice" in error.__class__.__name__:
                error_type = TTSErrorType.TTS_VOICE
                severity = TTSErrorSeverity.MEDIUM
                recoverable = True
            else:
                error_type = TTSErrorType.TTS_SYNTHESIS
                severity = TTSErrorSeverity.MEDIUM
                recoverable = True

        # Memory errors
        elif isinstance(error, MemoryError):
            error_type = TTSErrorType.MEMORY
            severity = TTSErrorSeverity.CRITICAL
            recoverable = False

        # Cancellation errors
        elif isinstance(error, asyncio.CancelledError):
            error_type = TTSErrorType.CANCELLED
            severity = TTSErrorSeverity.LOW
            recoverable = True

        # Extract content snippet if possible
        content_snippet = None
        if playlist_index is not None and hasattr(error, "__class__"):
            # Try to extract content from error message or context
            error_str = str(error)
            if len(error_str) > 100:
                content_snippet = error_str[:100] + "..."

        return TTSRunnerError(
            error=error,
            error_type=error_type,
            severity=severity,
            context=context,
            playlist_index=playlist_index,
            content_snippet=content_snippet,
            recoverable=recoverable,
        )

    def _update_error_stats(self, runner_error: TTSRunnerError) -> None:
        """Update error statistics."""
        self._error_counts[runner_error.error_type] = (
            self._error_counts.get(runner_error.error_type, 0) + 1
        )

        # Keep recent errors for analysis
        self._recent_errors.append(runner_error)
        if len(self._recent_errors) > self._max_recent_errors:
            self._recent_errors.pop(0)

    async def _log_error(self, runner_error: TTSRunnerError) -> None:
        """Log error with appropriate level and context."""
        error_msg = f"TTS Runner error in {runner_error.context}: {runner_error}"

        if runner_error.playlist_index is not None:
            error_msg += f" (index: {runner_error.playlist_index})"

        # Choose log level based on severity
        if runner_error.severity == TTSErrorSeverity.CRITICAL:
            logger.critical(error_msg, exc_info=True)
        elif runner_error.severity == TTSErrorSeverity.HIGH:
            logger.error(error_msg, exc_info=True)
        elif runner_error.severity == TTSErrorSeverity.MEDIUM:
            logger.warning(error_msg)
        else:
            logger.info(error_msg)

    def _determine_action(self, runner_error: TTSRunnerError) -> TTSErrorAction:
        """Determine the appropriate action based on error type and severity."""

        # Critical errors always stop
        if runner_error.severity == TTSErrorSeverity.CRITICAL:
            return TTSErrorAction.STOP

        # Network errors may be recoverable
        if runner_error.error_type == TTSErrorType.NETWORK and runner_error.recoverable:
            # Check if we've had too many network errors recently
            recent_network_errors = sum(
                1
                for e in self._recent_errors[-5:]
                if e.error_type == TTSErrorType.NETWORK
            )
            if recent_network_errors >= 3:
                return TTSErrorAction.PAUSE
            return TTSErrorAction.RETRY

        # TTS synthesis errors can often be retried
        if runner_error.error_type == TTSErrorType.TTS_SYNTHESIS:
            return TTSErrorAction.RETRY

        # Playback errors usually require stopping
        if runner_error.error_type == TTSErrorType.TTS_PLAYBACK:
            return TTSErrorAction.STOP

        # Timeout errors can be retried
        if runner_error.error_type == TTSErrorType.TIMEOUT:
            return TTSErrorAction.RETRY

        # Cancelled operations are normal
        if runner_error.error_type == TTSErrorType.CANCELLED:
            return TTSErrorAction.CONTINUE

        # Default to stopping for unexpected errors
        return TTSErrorAction.STOP

    async def _execute_action(
        self,
        action: TTSErrorAction,
        runner_error: TTSRunnerError,
        tts_integration: "TTSIntegration",
        playlist_manager=None,
    ) -> None:
        """Execute the determined action."""

        app = tts_integration.app

        if action == TTSErrorAction.CONTINUE:
            # Just log, no action needed
            pass

        elif action == TTSErrorAction.RETRY:
            # For retry, we might want to mark the item for retry later
            # This would require additional logic in the calling code
            await self._notify_user(runner_error, "將重試操作", "info", app)

        elif action == TTSErrorAction.PAUSE:
            await tts_integration.set_tts_status_safe("PAUSED")
            await self._notify_user(runner_error, "播放已暫停，請檢查連線後重試", "warning", app)

        elif action == TTSErrorAction.STOP:
            await tts_integration.set_tts_status_safe("STOPPED")
            await self._notify_user(runner_error, "播放已停止", "error", app)

        elif action == TTSErrorAction.RESTART:
            # This would require restarting the TTS engine or system
            # For now, just stop
            await tts_integration.set_tts_status_safe("STOPPED")
            await self._notify_user(runner_error, "需要重新啟動系統", "error", app)

        elif action == TTSErrorAction.NOTIFY_ONLY:
            await self._notify_user(runner_error, "已記錄錯誤", "info", app)

    async def _notify_user(
        self, runner_error: TTSRunnerError, message: str, severity: str, app
    ) -> None:
        """Send user notification about the error."""
        try:
            # Create user-friendly error message
            error_title_map = {
                TTSErrorType.NETWORK: "網路錯誤",
                TTSErrorType.TTS_SYNTHESIS: "語音合成錯誤",
                TTSErrorType.TTS_PLAYBACK: "播放錯誤",
                TTSErrorType.TTS_VOICE: "語音設定錯誤",
                TTSErrorType.MEMORY: "記憶體錯誤",
                TTSErrorType.TIMEOUT: "逾時錯誤",
                TTSErrorType.CANCELLED: "操作取消",
                TTSErrorType.UNEXPECTED: "未預期錯誤",
            }

            title = error_title_map.get(runner_error.error_type, "TTS 錯誤")

            # Add context information
            full_message = message
            if runner_error.content_snippet:
                full_message += f"\n內容: {runner_error.content_snippet}"

            app.notify(full_message, title=title, severity=severity)

        except Exception as notify_error:
            logger.warning(f"Failed to notify user about error: {notify_error}")

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            "error_counts": {k.value: v for k, v in self._error_counts.items()},
            "recent_errors_count": len(self._recent_errors),
            "most_common_error": max(
                self._error_counts.items(), key=lambda x: x[1], default=(None, 0)
            )[0],
        }

    def clear_stats(self) -> None:
        """Clear error statistics."""
        self._error_counts.clear()
        self._recent_errors.clear()


# Global error handler instance
error_handler = TTSRunnerErrorHandler()


async def handle_runner_error(
    error: Exception,
    context: str,
    tts_integration: "TTSIntegration",
    playlist_manager=None,
    playlist_index: Optional[int] = None,
) -> TTSErrorAction:
    """
    Convenience function to handle TTS runner errors.

    This is the main entry point for error handling in TTS runners.
    """
    return await error_handler.handle_runner_error(
        error, context, tts_integration, playlist_manager, playlist_index
    )
