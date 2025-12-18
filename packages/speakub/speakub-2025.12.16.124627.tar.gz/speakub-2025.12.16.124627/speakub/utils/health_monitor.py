#!/usr/bin/env python3
"""
健康監控模組 - Health Monitor Module

為SpeakUB提供運行時健康檢查和狀態監控。
集成死鎖檢測、性能指標和系統健康評估。
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional

from speakub.utils.deadlock_detector import get_deadlock_detector

logger = logging.getLogger(__name__)


class HealthChecker:
    """
    健康檢查器 - 評估系統整體健康狀態

    提供多層次的健康檢查：
    - 基礎功能檢查
    - 並發安全檢查
    - 性能指標檢查
    - 資源使用檢查
    """

    def __init__(self):
        self._last_check_time = 0
        self._check_interval = 30  # 30秒檢查間隔
        self._cached_health_status = None

    def get_comprehensive_health_status(self) -> Dict[str, Any]:
        """
        獲取全面的健康狀態報告

        包括：
        - 系統狀態
        - 死鎖風險
        - 性能指標
        - 資源使用
        - 建議行動
        """
        current_time = time.time()

        # 使用快取避免過於頻繁的檢查
        if (current_time - self._last_check_time) < self._check_interval and self._cached_health_status:
            return self._cached_health_status

        # 執行完整健康檢查
        health_status = {
            "timestamp": current_time,
            "overall_status": "unknown",
            "checks": {},
            "recommendations": [],
            "severity": "low"
        }

        # 1. 死鎖檢測檢查
        deadlock_status = self._check_deadlock_health()
        health_status["checks"]["deadlock"] = deadlock_status

        # 2. 性能指標檢查
        performance_status = self._check_performance_health()
        health_status["checks"]["performance"] = performance_status

        # 3. 資源使用檢查
        resource_status = self._check_resource_health()
        health_status["checks"]["resources"] = resource_status

        # 4. AsyncBridge操作檢查
        bridge_status = self._check_bridge_health()
        health_status["checks"]["async_bridge"] = bridge_status

        # 5. 系統整體狀態評估
        overall_status, severity, recommendations = self._evaluate_overall_health(
            health_status["checks"]
        )
        health_status["overall_status"] = overall_status
        health_status["severity"] = severity
        health_status["recommendations"] = recommendations

        # 快取結果
        self._cached_health_status = health_status
        self._last_check_time = current_time

        logger.debug(
            f"Health check completed: {overall_status} (severity: {severity})")
        return health_status

    def _check_deadlock_health(self) -> Dict[str, Any]:
        """檢查死鎖相關的健康狀態"""
        detector = get_deadlock_detector()
        stats = detector.get_monitoring_stats()

        warnings = stats.get("warnings", [])
        deadlock_risks = stats.get("deadlock_detection", [])

        status = "healthy"
        issues = []

        # 評估死鎖風險
        if deadlock_risks:
            status = "critical"
            issues.extend([f"🚨 {risk}" for risk in deadlock_risks])
        elif warnings:
            status = "warning"
            issues.extend(
                [f"⚠️  {warning}" for warning in warnings[:3]])  # 只顯示前3個

        return {
            "status": status,
            "issues": issues,
            "lock_count": stats["summary"]["total_locks"],
            "total_acquires": stats["summary"]["total_acquires"],
            "contention_time": stats["summary"]["total_contention_time"],
            "avg_contention_ms": stats["summary"]["avg_contention_per_acquire"] * 1000
        }

    def _check_performance_health(self) -> Dict[str, Any]:
        """檢查性能相關指標"""
        detector = get_deadlock_detector()
        stats = detector.get_monitoring_stats()

        status = "healthy"
        issues = []
        metrics = {}

        # 分析鎖定競爭
        avg_contention = stats["summary"]["avg_contention_per_acquire"] * 1000
        metrics["avg_lock_contention_ms"] = avg_contention

        if avg_contention > 5.0:  # 平均競爭超過5ms
            status = "warning"
            issues.append(f"高鎖定競爭: 平均 {avg_contention:.1f}ms")
        elif avg_contention > 10.0:  # 平均競爭超過10ms
            status = "critical"
            issues.append(f"嚴重鎖定競爭: 平均 {avg_contention:.1f}ms")

        # 分析鎖定持有時間
        bottlenecks = stats.get("summary", {}).get("bottlenecks", [])
        if bottlenecks:
            status = "warning" if status == "healthy" else status
            issues.append(f"發現 {len(bottlenecks)} 個性能瓶頸")

        return {
            "status": status,
            "issues": issues,
            "metrics": metrics
        }

    def _check_resource_health(self) -> Dict[str, Any]:
        """檢查資源使用情況"""
        status = "healthy"
        issues = []

        try:
            import psutil
            process = psutil.Process()

            # CPU使用率
            cpu_percent = process.cpu_percent(interval=0.1)
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024

            # 評估資源使用
            if cpu_percent > 80:
                status = "critical"
                issues.append(f"高CPU使用率: {cpu_percent:.1f}%")
            elif cpu_percent > 50:
                status = "warning"
                issues.append(f"中等CPU使用率: {cpu_percent:.1f}%")

            if memory_mb > 500:  # 500MB
                status = "warning" if status == "healthy" else status
                issues.append(f"高記憶體使用: {memory_mb:.1f}MB")

            return {
                "status": status,
                "issues": issues,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "system_memory_percent": psutil.virtual_memory().percent
            }

        except ImportError:
            return {
                "status": "unknown",
                "issues": ["psutil未安裝，無法檢查資源使用"],
                "cpu_percent": None,
                "memory_mb": None
            }
        except Exception as e:
            return {
                "status": "error",
                "issues": [f"資源檢查失敗: {e}"],
                "cpu_percent": None,
                "memory_mb": None
            }

    def _check_bridge_health(self) -> Dict[str, Any]:
        """檢查AsyncBridge操作健康狀態"""
        # 注意：這個檢查需要在TTSIntegration實例可用時進行
        # 這裡返回結構，實際檢查在應用啟動後進行

        return {
            "status": "unknown",
            "issues": ["需要TTSIntegration實例進行橋接檢查"],
            "operations_total": 0,
            "success_rate": 0.0
        }

    def _evaluate_overall_health(self, checks: Dict[str, Any]) -> tuple[str, str, List[str]]:
        """評估整體健康狀態"""
        status_priority = {"healthy": 0, "warning": 1,
                           "critical": 2, "error": 3, "unknown": 4}

        max_severity = 0
        recommendations = []

        for check_name, check_result in checks.items():
            check_status = check_result.get("status", "unknown")
            severity = status_priority.get(check_status, 4)
            max_severity = max(max_severity, severity)

            # 根據檢查類型添加建議
            if check_status in ["warning", "critical", "error"]:
                issues = check_result.get("issues", [])
                recommendations.extend(issues)

                # 添加特定建議
                if check_name == "deadlock" and check_status == "critical":
                    recommendations.append("🔧 立即檢查鎖定使用，可能存在死鎖風險")
                elif check_name == "performance" and check_status == "warning":
                    recommendations.append("📊 考慮優化鎖定競爭，可能影響響應性能")
                elif check_name == "resources" and check_status == "critical":
                    recommendations.append("💾 檢查資源使用，考慮重啟或擴容")

        # 確定整體狀態
        severity_map = {0: "healthy", 1: "warning",
                        2: "critical", 3: "error", 4: "unknown"}
        overall_status = severity_map.get(max_severity, "unknown")

        severity_level = "low"
        if max_severity >= 2:
            severity_level = "high"
        elif max_severity >= 1:
            severity_level = "medium"

        return overall_status, severity_level, recommendations

    def get_health_summary(self) -> Dict[str, Any]:
        """獲取簡化的健康摘要"""
        full_status = self.get_comprehensive_health_status()

        return {
            "status": full_status["overall_status"],
            "severity": full_status["severity"],
            "timestamp": full_status["timestamp"],
            "critical_issues": len([r for r in full_status["recommendations"] if "🚨" in r]),
            "warnings": len([r for r in full_status["recommendations"] if "⚠️" in r]),
            "top_recommendations": full_status["recommendations"][:3]
        }


class AlertManager:
    """
    告警管理器 - 管理健康檢查的告警規則和通知
    """

    def __init__(self):
        self._alert_history = []
        self._alert_thresholds = {
            "deadlock_warnings": 3,  # 累積3個死鎖警告觸發告警
            "performance_degradation": 5.0,  # 平均競爭超過5ms
            "high_cpu_threshold": 80.0,  # CPU使用率超過80%
            "high_memory_threshold": 800.0,  # 記憶體使用超過800MB
        }

    def check_alerts(self, health_status: Dict[str, Any]) -> List[Dict[str, Any]]:
        """檢查是否需要觸發告警"""
        alerts = []

        # 檢查死鎖風險
        deadlock_check = health_status["checks"]["deadlock"]
        if deadlock_check["status"] == "critical":
            alerts.append({
                "type": "deadlock_risk",
                "severity": "critical",
                "message": f"檢測到死鎖風險: {len(deadlock_check['issues'])} 個問題",
                "details": deadlock_check["issues"],
                "timestamp": health_status["timestamp"]
            })

        # 檢查性能問題
        perf_check = health_status["checks"]["performance"]
        avg_contention = perf_check.get(
            "metrics", {}).get("avg_lock_contention_ms", 0)
        if avg_contention > self._alert_thresholds["performance_degradation"]:
            alerts.append({
                "type": "performance_degradation",
                "severity": "warning",
                "message": f"鎖定競爭嚴重: 平均 {avg_contention:.1f}ms",
                "details": perf_check.get("issues", []),
                "timestamp": health_status["timestamp"]
            })

        # 檢查資源問題
        resource_check = health_status["checks"]["resources"]
        cpu_percent = resource_check.get("cpu_percent")
        memory_mb = resource_check.get("memory_mb")

        if cpu_percent and cpu_percent > self._alert_thresholds["high_cpu_threshold"]:
            alerts.append({
                "type": "high_cpu_usage",
                "severity": "warning",
                "message": f"CPU使用率過高: {cpu_percent:.1f}%",
                "details": resource_check.get("issues", []),
                "timestamp": health_status["timestamp"]
            })

        if memory_mb and memory_mb > self._alert_thresholds["high_memory_threshold"]:
            alerts.append({
                "type": "high_memory_usage",
                "severity": "warning",
                "message": f"記憶體使用過高: {memory_mb:.1f}MB",
                "details": resource_check.get("issues", []),
                "timestamp": health_status["timestamp"]
            })

        # 記錄告警歷史
        for alert in alerts:
            self._alert_history.append(alert)

        # 只保留最近100個告警
        if len(self._alert_history) > 100:
            self._alert_history = self._alert_history[-100:]

        return alerts

    def get_alert_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """獲取告警歷史"""
        return self._alert_history[-limit:]

    def clear_alert_history(self) -> None:
        """清除告警歷史"""
        self._alert_history.clear()


# 全域實例
health_checker = HealthChecker()
alert_manager = AlertManager()


def get_health_checker() -> HealthChecker:
    """獲取全域健康檢查器實例"""
    return health_checker


def get_alert_manager() -> AlertManager:
    """獲取全域告警管理器實例"""
    return alert_manager


def check_system_health() -> Dict[str, Any]:
    """便捷函數：檢查系統健康狀態"""
    return health_checker.get_comprehensive_health_status()


def get_health_summary() -> Dict[str, Any]:
    """便捷函數：獲取健康摘要"""
    return health_checker.get_health_summary()


def check_alerts() -> List[Dict[str, Any]]:
    """便捷函數：檢查當前告警"""
    health_status = health_checker.get_comprehensive_health_status()
    return alert_manager.check_alerts(health_status)
