#!/usr/bin/env python3
"""
Intelligent Notification System for SpeakUB
Provides smart, contextual notifications based on system state and user behavior.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class NotificationManager:
    """Intelligent notification system with contextual awareness."""

    def __init__(self, app):
        self.app = app
        self._last_notifications: Dict[str, float] = {}
        self._notification_cooldowns = {
            "tts_performance": 300,  # 5 minutes
            "resource_warning": 180,  # 3 minutes
            "system_health": 600,  # 10 minutes
            "user_activity": 120,  # 2 minutes
        }
        self._performance_history: List[Dict[str, Any]] = []
        self._user_activity_patterns: Dict[str, Any] = {}

    def start_monitoring(self) -> None:
        """Start the intelligent notification monitoring."""
        # Schedule periodic checks
        self.app.set_interval(60.0, self._check_system_health)
        self.app.set_interval(120.0, self._check_tts_performance)
        self.app.set_interval(180.0, self._check_resource_usage)
        self.app.set_interval(300.0, self._check_user_patterns)

        logger.debug("Intelligent notification system started")

    def _can_send_notification(self, notification_type: str) -> bool:
        """Check if a notification can be sent based on cooldown."""
        last_sent = self._last_notifications.get(notification_type, 0)
        cooldown = self._notification_cooldowns.get(notification_type, 60)
        return (time.time() - last_sent) >= cooldown

    def _send_notification(
        self, message: str, severity: str = "info", notification_type: str = "general"
    ) -> None:
        """Send a notification if cooldown allows."""
        if self._can_send_notification(notification_type):
            self.app.notify(message, severity=severity, timeout=5)
            self._last_notifications[notification_type] = time.time()
            logger.debug(f"Sent {severity} notification: {message}")

    def _check_system_health(self) -> None:
        """Check overall system health and provide recommendations."""
        try:
            # Check memory usage
            from speakub.utils.file_utils import get_resource_manager

            rm = get_resource_manager()
            stats = rm.get_resource_stats()

            memory_mb = stats.get("memory_rss_mb", 0)
            temp_files = stats.get("temp_files_count", 0)

            # Memory warnings
            if memory_mb > 400:
                self._send_notification(
                    f"High memory usage ({memory_mb:.0f}MB). Consider restarting the application.",
                    "warning",
                    "system_health",
                )
            elif memory_mb > 300:
                self._send_notification(
                    f"Elevated memory usage ({memory_mb:.0f}MB). Monitor performance.",
                    "info",
                    "system_health",
                )

            # Temp file cleanup suggestions
            if temp_files > 20:
                self._send_notification(
                    f"Many temporary files ({temp_files}) detected. Consider cleanup.",
                    "info",
                    "system_health",
                )

        except Exception as e:
            logger.debug(f"System health check error: {e}")

    def _check_tts_performance(self) -> None:
        """Analyze TTS performance and suggest optimizations."""
        try:
            if not hasattr(self.app, "tts_integration") or not self.app.tts_integration:
                return

            pm = self.app.tts_integration.playlist_manager
            if not pm:
                return

            # Get performance stats
            stats = pm.get_preloading_stats()

            # Analyze batch efficiency
            queue_size = stats.get("queue_size", 0)
            batch_size = stats.get("batch_size", 0)  # noqa: F841

            if queue_size > 10:
                self._send_notification(
                    f"Large TTS queue ({queue_size} items). Consider increasing batch size.",
                    "info",
                    "tts_performance",
                )

            # Check predictive mode effectiveness
            if stats.get("predictive_mode"):
                trigger_count = stats.get("trigger_count", 0)
                # Handle None values safely
                if trigger_count is not None and trigger_count > 50:  # High activity
                    self._send_notification(
                        "High TTS activity detected. Predictive mode is working well!",
                        "success",
                        "tts_performance",
                    )

            # Circuit breaker status
            cb = self.app.tts_integration.circuit_breaker
            if cb:
                cb_state = cb.get_state()
                if cb_state.get("state") == "open":
                    self._send_notification(
                        "TTS circuit breaker is open. Service temporarily unavailable.",
                        "warning",
                        "tts_performance",
                    )
                elif cb_state.get("state") == "half_open":
                    self._send_notification(
                        "TTS service recovering. Testing connection...",
                        "info",
                        "tts_performance",
                    )

        except Exception as e:
            logger.debug(f"TTS performance check error: {e}")

    def _check_resource_usage(self) -> None:
        """Monitor resource usage patterns."""
        try:
            from speakub.utils.file_utils import get_resource_manager

            rm = get_resource_manager()
            stats = rm.get_resource_stats()

            temp_size_mb = stats.get("total_temp_files_size_mb", 0)
            system_memory = stats.get("system_memory_available_gb", 0)

            # Temp file size warnings
            if temp_size_mb > 200:
                self._send_notification(
                    f"Large temp file storage ({temp_size_mb:.0f}MB). Automatic cleanup recommended.",
                    "warning",
                    "resource_warning",
                )

            # System memory warnings
            if system_memory < 0.5:
                self._send_notification(
                    f"Low system memory ({system_memory:.1f}GB available). Close other applications.",
                    "error",
                    "resource_warning",
                )
            elif system_memory < 1.0:
                self._send_notification(
                    f"Limited system memory ({system_memory:.1f}GB available). Monitor usage.",
                    "warning",
                    "resource_warning",
                )

        except Exception as e:
            logger.debug(f"Resource usage check error: {e}")

    def _check_user_patterns(self) -> None:
        """Analyze user activity patterns and provide suggestions."""
        try:
            # Check TTS status and provide usage tips
            if hasattr(self.app, "tts_status"):
                status = self.app.tts_status

                if status == "STOPPED":
                    # Suggest starting TTS if user has been inactive
                    if self._get_user_inactive_time() > 300:  # 5 minutes
                        self._send_notification(
                            "Ready to continue reading? Press SPACE to resume TTS.",
                            "info",
                            "user_activity",
                        )

                elif status == "PLAYING":
                    # Check if user might benefit from speed adjustment
                    if self._detect_reading_speed_pattern():
                        self._send_notification(
                            "Consider adjusting reading speed with [ ] keys for better comprehension.",
                            "info",
                            "user_activity",
                        )

        except Exception as e:
            logger.debug(f"User pattern check error: {e}")

    def _get_user_inactive_time(self) -> float:
        """Get time since last user activity."""
        # This would need to be implemented based on actual user activity tracking
        # For now, return a reasonable default
        return 0.0

    def _detect_reading_speed_pattern(self) -> bool:
        """Detect if user might benefit from speed adjustments."""
        # This would analyze reading patterns, pauses, etc.
        # For now, return False as we don't have the data
        return False

    def record_tts_performance(self, performance_data: Dict[str, Any]) -> None:
        """Record TTS performance data for analysis."""
        self._performance_history.append(
            {**performance_data, "timestamp": time.time()})

        # Keep only last 100 entries
        if len(self._performance_history) > 100:
            self._performance_history.pop(0)

    def get_performance_insights(self) -> Dict[str, Any]:
        """Get insights from performance history."""
        if not self._performance_history:
            return {}

        # Analyze performance trends
        recent_entries = [
            entry
            for entry in self._performance_history
            # Last hour
            if time.time() - entry["timestamp"] < 3600
        ]

        if not recent_entries:
            return {}

        avg_synthesis_time = sum(
            entry.get("synthesis_time", 0) for entry in recent_entries
        ) / len(recent_entries)

        return {
            "avg_synthesis_time": avg_synthesis_time,
            "total_requests": len(recent_entries),
            # Could be 'improving', 'degrading', etc.
            "performance_trend": "stable",
        }
