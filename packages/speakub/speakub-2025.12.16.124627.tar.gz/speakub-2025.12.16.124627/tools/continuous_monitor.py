#!/usr/bin/env python3
"""
持續監控腳本 - Continuous Monitoring Script

定期檢查SpeakUB系統健康狀態，記錄指標和告警。
可用於生產環境的持續監控和日誌記錄。
"""

from speakub.utils.health_monitor import (
    get_health_checker,
    get_alert_manager,
    check_system_health,
    check_alerts
)
import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# 添加專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('speakub_monitor.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)


class ContinuousMonitor:
    """持續監控器"""

    def __init__(self,
                 interval: float = 60.0,
                 log_file: Optional[str] = None,
                 alert_file: Optional[str] = None,
                 duration: Optional[float] = None):
        self.interval = interval
        self.duration = duration
        self.start_time = time.time()

        # 日誌文件
        self.log_file = log_file or "speakub_health_monitor.log"
        self.alert_file = alert_file or "speakub_alerts.log"

        # 統計
        self.check_count = 0
        self.error_count = 0
        self.alert_count = 0

        logger.info(
            f"Continuous monitor initialized - interval: {interval}s, duration: {duration or 'unlimited'}")

    def run(self) -> None:
        """運行持續監控"""
        logger.info("🚀 Starting SpeakUB continuous health monitoring")
        logger.info(f"📊 Check interval: {self.interval} seconds")
        logger.info(f"📝 Health log: {self.log_file}")
        logger.info(f"🚨 Alert log: {self.alert_file}")
        logger.info("🛑 Press Ctrl+C to stop monitoring")

        try:
            while self._should_continue():
                self._perform_check()
                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            sys.exit(1)

        self._print_summary()

    def _should_continue(self) -> bool:
        """檢查是否應該繼續監控"""
        if self.duration is None:
            return True

        elapsed = time.time() - self.start_time
        return elapsed < self.duration

    def _perform_check(self) -> None:
        """執行一次健康檢查"""
        try:
            self.check_count += 1

            # 獲取健康狀態
            health_status = check_system_health()

            # 檢查告警
            alerts = check_alerts()

            # 記錄健康狀態
            self._log_health_status(health_status)

            # 記錄告警
            if alerts:
                self.alert_count += len(alerts)
                self._log_alerts(alerts)

            # 輸出簡要狀態
            status = health_status["overall_status"]
            severity = health_status["severity"]
            recommendations = len(health_status.get("recommendations", []))

            logger.info(
                f"✅ Health check #{self.check_count}: {status} "
                f"(severity: {severity}, recommendations: {recommendations}, alerts: {len(alerts)})"
            )

        except Exception as e:
            self.error_count += 1
            logger.error(f"❌ Health check #{self.check_count} failed: {e}")

    def _log_health_status(self, health_status: Dict[str, Any]) -> None:
        """記錄健康狀態到文件"""
        try:
            log_entry = {
                "timestamp": health_status["timestamp"],
                "check_number": self.check_count,
                "overall_status": health_status["overall_status"],
                "severity": health_status["severity"],
                "recommendations": health_status.get("recommendations", []),
                "checks": health_status.get("checks", {})
            }

            with open(self.log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')

        except Exception as e:
            logger.warning(f"Failed to write health log: {e}")

    def _log_alerts(self, alerts: list) -> None:
        """記錄告警到文件"""
        try:
            alert_entry = {
                "timestamp": time.time(),
                "check_number": self.check_count,
                "alerts": alerts
            }

            with open(self.alert_file, 'a', encoding='utf-8') as f:
                json.dump(alert_entry, f, ensure_ascii=False)
                f.write('\n')

            # 同時記錄到主日誌
            for alert in alerts:
                logger.warning(
                    f"🚨 ALERT: {alert.get('type', 'unknown')} - {alert.get('message', 'no message')}")

        except Exception as e:
            logger.warning(f"Failed to write alert log: {e}")

    def _print_summary(self) -> None:
        """輸出監控總結"""
        total_time = time.time() - self.start_time
        checks_per_minute = (self.check_count / total_time) * \
            60 if total_time > 0 else 0

        print("\n" + "="*60)
        print("📊 SpeakUB Health Monitoring Summary")
        print("="*60)
        print(f"⏱️  Total monitoring time: {total_time:.1f} seconds")
        print(f"🔢 Health checks performed: {self.check_count}")
        print(f"⚡ Checks per minute: {checks_per_minute:.1f}")
        print(f"❌ Failed checks: {self.error_count}")
        print(f"🚨 Total alerts: {self.alert_count}")
        print(f"📝 Health log: {self.log_file}")
        print(f"🚨 Alert log: {self.alert_file}")
        print("="*60)

        if self.error_count > 0:
            error_rate = (self.error_count / self.check_count) * 100
            print(f"⚠️  Error rate: {error_rate:.1f}%")

        if self.alert_count > 0:
            print(f"⚠️  Total alerts recorded: {self.alert_count}")
            print("   Check alert log for details")


def analyze_logs(log_file: str, hours: int = 24) -> None:
    """分析監控日誌"""
    try:
        import datetime

        # 計算時間窗口
        cutoff_time = time.time() - (hours * 3600)

        # 讀取和分析日誌
        health_trends = []
        alert_counts = {}

        if Path(log_file).exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get("timestamp", 0) >= cutoff_time:
                            health_trends.append(entry)
                    except json.JSONDecodeError:
                        continue

        # 分析趨勢
        status_counts = {}
        severity_counts = {}

        for entry in health_trends:
            status = entry.get("overall_status", "unknown")
            severity = entry.get("severity", "unknown")

            status_counts[status] = status_counts.get(status, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        print(f"\n📊 Health Log Analysis (last {hours} hours)")
        print("="*50)
        print(f"Total health checks: {len(health_trends)}")

        if status_counts:
            print("\nStatus distribution:")
            for status, count in status_counts.items():
                percentage = (count / len(health_trends)) * 100
                print(f"  {status}: {count} ({percentage:.1f}%)")

        if severity_counts:
            print("\nSeverity distribution:")
            for severity, count in severity_counts.items():
                percentage = (count / len(health_trends)) * 100
                print(f"  {severity}: {count} ({percentage:.1f}%)")

    except Exception as e:
        print(f"❌ Failed to analyze logs: {e}")


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="SpeakUB Continuous Health Monitor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
定期監控SpeakUB系統健康狀態並記錄到日誌文件。

使用示例:
  python continuous_monitor.py                      # 每60秒檢查一次
  python continuous_monitor.py --interval 30       # 每30秒檢查一次
  python continuous_monitor.py --duration 3600     # 監控1小時
  python continuous_monitor.py --analyze 24        # 分析最近24小時的日誌

輸出文件:
  speakub_health_monitor.log - 健康檢查記錄
  speakub_alerts.log         - 告警記錄
  speakub_monitor.log        - 控制台日誌
        """
    )

    parser.add_argument(
        "--interval", "-i",
        type=float,
        default=60.0,
        help="檢查間隔秒數 (預設: 60.0)"
    )

    parser.add_argument(
        "--duration", "-d",
        type=float,
        help="監控持續時間秒數 (預設: 無限)"
    )

    parser.add_argument(
        "--log-file", "-l",
        default="speakub_health_monitor.log",
        help="健康日誌文件路徑"
    )

    parser.add_argument(
        "--alert-file", "-a",
        default="speakub_alerts.log",
        help="告警日誌文件路徑"
    )

    parser.add_argument(
        "--analyze", "-A",
        type=int,
        help="分析最近N小時的日誌（不啟動監控）"
    )

    args = parser.parse_args()

    if args.analyze:
        # 分析模式
        analyze_logs(args.log_file, args.analyze)
    else:
        # 監控模式
        monitor = ContinuousMonitor(
            interval=args.interval,
            log_file=args.log_file,
            alert_file=args.alert_file,
            duration=args.duration
        )
        monitor.run()


if __name__ == "__main__":
    main()
