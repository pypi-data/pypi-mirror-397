#!/usr/bin/env python3
"""
健康檢查服務 - Health Check Service

提供HTTP API端點用於運行時健康檢查和監控。
可以集成到現有的Web應用或作為獨立服務運行。
"""

from speakub.utils.deadlock_detector import get_deadlock_detector
from speakub.utils.health_monitor import (
    get_health_checker,
    get_alert_manager,
    check_system_health,
    get_health_summary,
    check_alerts
)
import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# 添加專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from flask import Flask, jsonify, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


logger = logging.getLogger(__name__)


class HealthService:
    """健康檢查服務類"""

    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = None
        self._setup_app()

    def _setup_app(self):
        """設置Flask應用"""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask未安裝，請運行: pip install flask")

        self.app = Flask(__name__)

        # 註冊路由
        self._register_routes()

        # 添加錯誤處理
        self._setup_error_handlers()

    def _register_routes(self):
        """註冊API路由"""

        @self.app.route("/health", methods=["GET"])
        def health_endpoint():
            """基礎健康檢查端點"""
            try:
                summary = get_health_summary()
                status_code = self._get_status_code(summary["status"])
                return jsonify(summary), status_code
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                return jsonify({
                    "status": "error",
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

        @self.app.route("/health/detailed", methods=["GET"])
        def detailed_health_endpoint():
            """詳細健康檢查端點"""
            try:
                detailed = check_system_health()
                status_code = self._get_status_code(detailed["overall_status"])
                return jsonify(detailed), status_code
            except Exception as e:
                logger.error(f"Detailed health check failed: {e}")
                return jsonify({
                    "overall_status": "error",
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

        @self.app.route("/health/alerts", methods=["GET"])
        def alerts_endpoint():
            """告警檢查端點"""
            try:
                alerts = check_alerts()
                return jsonify({
                    "alert_count": len(alerts),
                    "alerts": alerts,
                    "timestamp": __import__('time').time()
                }), 200
            except Exception as e:
                logger.error(f"Alerts check failed: {e}")
                return jsonify({
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

        @self.app.route("/health/concurrency", methods=["GET"])
        def concurrency_health_endpoint():
            """並發健康檢查端點（專門針對死鎖檢測）"""
            try:
                detector = get_deadlock_detector()
                stats = detector.get_monitoring_stats()

                # 轉換為HTTP友好的格式
                response = {
                    "monitoring_enabled": stats["monitoring_enabled"],
                    "locks": stats["locks"],
                    "summary": stats["summary"],
                    "warnings": stats["warnings"],
                    "deadlock_detection": stats["deadlock_detection"],
                    "timestamp": stats["timestamp"]
                }

                # 根據是否有嚴重問題決定狀態碼
                has_critical = any("Potential deadlock" in str(w)
                                   for w in stats["deadlock_detection"])
                status_code = 503 if has_critical else 200

                return jsonify(response), status_code
            except Exception as e:
                logger.error(f"Concurrency health check failed: {e}")
                return jsonify({
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

        @self.app.route("/health/history", methods=["GET"])
        def health_history_endpoint():
            """健康檢查歷史端點"""
            try:
                alert_manager = get_alert_manager()
                limit = int(request.args.get('limit', 10))

                history = alert_manager.get_alert_history(limit)
                return jsonify({
                    "history_count": len(history),
                    "history": history,
                    "timestamp": __import__('time').time()
                }), 200
            except Exception as e:
                logger.error(f"Health history check failed: {e}")
                return jsonify({
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

        @self.app.route("/health/reset", methods=["POST"])
        def reset_health_endpoint():
            """重置健康檢查狀態（管理用途）"""
            try:
                # 重置快取
                health_checker = get_health_checker()
                health_checker._cached_health_status = None
                health_checker._last_check_time = 0

                # 重置告警歷史
                alert_manager = get_alert_manager()
                alert_manager.clear_alert_history()

                logger.info("Health check state reset")
                return jsonify({
                    "status": "reset",
                    "message": "Health check state has been reset",
                    "timestamp": __import__('time').time()
                }), 200
            except Exception as e:
                logger.error(f"Health reset failed: {e}")
                return jsonify({
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

        @self.app.route("/health/config", methods=["GET"])
        def config_endpoint():
            """健康檢查配置信息"""
            try:
                alert_manager = get_alert_manager()
                health_checker = get_health_checker()

                config_info = {
                    "alert_thresholds": alert_manager._alert_thresholds,
                    "health_check_interval": health_checker._check_interval,
                    "monitoring_enabled": True,  # 假設總是啟用
                    "endpoints": [
                        "/health - 基礎健康摘要",
                        "/health/detailed - 詳細健康報告",
                        "/health/alerts - 當前告警",
                        "/health/concurrency - 並發健康檢查",
                        "/health/history - 告警歷史",
                        "/health/reset - 重置狀態 (POST)",
                        "/health/config - 配置信息"
                    ]
                }

                return jsonify(config_info), 200
            except Exception as e:
                logger.error(f"Config endpoint failed: {e}")
                return jsonify({
                    "error": str(e),
                    "timestamp": __import__('time').time()
                }), 500

    def _setup_error_handlers(self):
        """設置錯誤處理器"""

        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "error": "Endpoint not found",
                "available_endpoints": [
                    "/health",
                    "/health/detailed",
                    "/health/alerts",
                    "/health/concurrency",
                    "/health/history",
                    "/health/reset",
                    "/health/config"
                ]
            }), 404

        @self.app.errorhandler(500)
        def internal_error(error):
            return jsonify({
                "error": "Internal server error",
                "timestamp": __import__('time').time()
            }), 500

    def _get_status_code(self, status: str) -> int:
        """根據健康狀態返回HTTP狀態碼"""
        status_codes = {
            "healthy": 200,
            "warning": 200,  # 警告仍返回200，但內容標明問題
            "critical": 503,  # 服務不可用
            "error": 503,
            "unknown": 503
        }
        return status_codes.get(status, 503)

    def run(self, debug: bool = False):
        """運行健康檢查服務"""
        if not self.app:
            raise RuntimeError("Flask app not initialized")

        print("🚀 SpeakUB Health Check Service")
        print(f"📍 Server: http://{self.host}:{self.port}")
        print("📋 Available endpoints:")
        print("  GET  /health         - Basic health summary")
        print("  GET  /health/detailed - Detailed health report")
        print("  GET  /health/alerts   - Current alerts")
        print("  GET  /health/concurrency - Concurrency health check")
        print("  GET  /health/history  - Alert history")
        print("  POST /health/reset    - Reset health state")
        print("  GET  /health/config   - Configuration info")
        print("\n🛑 Press Ctrl+C to stop")

        try:
            self.app.run(
                host=self.host,
                port=self.port,
                debug=debug,
                use_reloader=False  # 避免重載導致狀態丟失
            )
        except KeyboardInterrupt:
            print("\n🛑 Health check service stopped")
        except Exception as e:
            print(f"❌ Failed to start health service: {e}")
            sys.exit(1)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="SpeakUB Health Check Service",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
啟動SpeakUB健康檢查HTTP服務，提供運行時監控API。

使用示例:
  python health_service.py                    # 預設localhost:8080
  python health_service.py --host 0.0.0.0    # 綁定所有接口
  python health_service.py --port 9000       # 自訂端口
  python health_service.py --debug            # 調試模式

API端點:
  GET /health          - 基礎健康摘要
  GET /health/detailed  - 詳細健康報告
  GET /health/alerts    - 當前告警
  GET /health/concurrency - 並發健康檢查
  GET /health/history   - 告警歷史
  POST /health/reset    - 重置狀態
  GET /health/config    - 配置信息

健康狀態碼:
  200 - 健康/警告
  503 - 嚴重問題/服務不可用
        """
    )

    parser.add_argument(
        "--host", "-H",
        default="localhost",
        help="服務綁定地址 (預設: localhost)"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="服務端口 (預設: 8080)"
    )

    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="啟用調試模式"
    )

    args = parser.parse_args()

    # 檢查依賴
    if not FLASK_AVAILABLE:
        print("❌ Flask未安裝。請運行: pip install flask")
        sys.exit(1)

    # 啟動服務
    service = HealthService(host=args.host, port=args.port)
    service.run(debug=args.debug)


if __name__ == "__main__":
    main()
