#!/usr/bin/env python3
"""
優化評估工具 - Optimization Assessment Tool

基於階段一至四建立的監控系統，評估和實施漸進式優化。
分析生產數據，識別優化機會，實施A/B測試。
"""

from speakub.utils.deadlock_detector import get_deadlock_detector
from speakub.utils.health_monitor import check_system_health
import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# 添加專案路徑
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class OptimizationCandidate:
    """優化候選項目"""
    name: str
    category: str  # "performance", "reliability", "monitoring"
    risk_level: str  # "low", "medium", "high"
    impact_estimate: str  # "low", "medium", "high"
    complexity: str  # "low", "medium", "high"
    prerequisites: List[str]
    description: str
    metrics: Dict[str, Any]

    def calculate_priority_score(self) -> float:
        """計算優先權分數 (0-100)"""
        # 風險權重：高風險加分（因為安全）
        risk_scores = {"low": 30, "medium": 20, "high": 10}

        # 影響權重：高影響加分
        impact_scores = {"low": 10, "medium": 20, "high": 30}

        # 複雜度權重：低複雜度加分
        complexity_scores = {"low": 30, "medium": 20, "high": 10}

        base_score = (
            risk_scores.get(self.risk_level, 20) +
            impact_scores.get(self.impact_estimate, 20) +
            complexity_scores.get(self.complexity, 20)
        )

        return min(100.0, base_score)


class ABTestFramework:
    """A/B測試框架"""

    def __init__(self, test_name: str):
        self.test_name = test_name
        self.variants = {}
        self.metrics = {}
        self.start_time = None
        self.end_time = None
        self.status = "planned"

    def add_variant(self, name: str, config: Dict[str, Any], traffic_percentage: float):
        """添加測試變體"""
        self.variants[name] = {
            "config": config,
            "traffic_percentage": traffic_percentage,
            "metrics": {}
        }

    def start_test(self):
        """開始A/B測試"""
        self.start_time = datetime.now()
        self.status = "running"
        print(f"🧪 Started A/B test: {self.test_name}")

    def record_metric(self, variant_name: str, metric_name: str, value: Any):
        """記錄測試指標"""
        if variant_name not in self.variants:
            return

        if metric_name not in self.variants[variant_name]["metrics"]:
            self.variants[variant_name]["metrics"][metric_name] = []

        self.variants[variant_name]["metrics"][metric_name].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })

    def stop_test(self):
        """停止A/B測試"""
        self.end_time = datetime.now()
        self.status = "completed"

        # 分析結果
        self._analyze_results()

    def _analyze_results(self):
        """分析測試結果"""
        print(f"\n📊 A/B Test Results: {self.test_name}")
        print("="*60)

        for variant_name, variant_data in self.variants.items():
            print(f"\n🔬 Variant: {variant_name}")
            print(f"   Traffic: {variant_data['traffic_percentage']}%")

            for metric_name, measurements in variant_data["metrics"].items():
                if measurements:
                    values = [m["value"] for m in measurements]
                    avg_value = sum(values) / len(values)
                    print(
                        f"   {metric_name}: {avg_value:.3f} (n={len(values)})")

    def get_recommendation(self) -> str:
        """獲取測試建議"""
        # 簡單的推薦邏輯 - 可以根據具體指標擴展
        if len(self.variants) < 2:
            return "需要至少兩個變體才能比較"

        # 比較關鍵指標（示例）
        baseline_variant = None
        best_variant = None
        best_score = 0

        for variant_name, variant_data in self.variants.items():
            if "baseline" in variant_name.lower():
                baseline_variant = variant_name

            # 計算簡單分數（可以自定義）
            score = variant_data["traffic_percentage"]
            if score > best_score:
                best_score = score
                best_variant = variant_name

        if best_variant and baseline_variant and best_variant != baseline_variant:
            return f"建議採用變體 '{best_variant}'，優於基準 '{baseline_variant}'"
        else:
            return "保持當前配置或需要更多測試數據"


class OptimizationAssessmentFramework:
    """優化評估框架"""

    def __init__(self):
        self.optimization_candidates = []
        self.assessment_period_days = 30

    def identify_candidates(self) -> List[OptimizationCandidate]:
        """基於監控數據識別優化候選項目"""
        candidates = []

        # 分析死鎖檢測數據
        deadlock_detector = get_deadlock_detector()
        stats = deadlock_detector.get_monitoring_stats()

        # 候選1: 鎖定持有時間優化
        avg_contention = stats["summary"]["avg_contention_per_acquire"] * 1000
        if avg_contention > 1.0:  # 超過1ms平均競爭
            candidates.append(OptimizationCandidate(
                name="lock_holding_optimization",
                category="performance",
                risk_level="medium",
                impact_estimate="medium",
                complexity="medium",
                prerequisites=["階段一至四監控系統", "生產環境測試"],
                description="優化鎖定持有時間，減少競爭",
                metrics={"current_avg_contention_ms": avg_contention}
            ))

        # 候選2: 死鎖檢測優化
        if stats["summary"]["total_waits"] > stats["summary"]["total_acquires"] * 0.05:  # 5%等待率
            candidates.append(OptimizationCandidate(
                name="deadlock_detection_enhancement",
                category="reliability",
                risk_level="low",
                impact_estimate="low",
                complexity="low",
                prerequisites=["死鎖檢測器運行穩定"],
                description="增強死鎖檢測算法，減少誤報",
                metrics={"wait_ratio": stats["summary"]["total_waits"] /
                         max(1, stats["summary"]["total_acquires"])}
            ))

        # 候選3: AsyncBridge性能優化
        # 這個需要從健康檢查中獲取AsyncBridge統計
        health_status = check_system_health()
        bridge_check = health_status["checks"].get("async_bridge", {})
        if bridge_check.get("status") == "unknown":  # 表示需要實現
            candidates.append(OptimizationCandidate(
                name="async_bridge_performance",
                category="performance",
                risk_level="medium",
                impact_estimate="medium",
                complexity="high",
                prerequisites=["AsyncBridge統計收集", "性能基準測試"],
                description="優化AsyncBridge操作性能，減少同步等待時間",
                metrics={"bridge_status": "not_implemented"}
            ))

        # 候選4: 資源使用優化
        resource_check = health_status["checks"].get("resources", {})
        if resource_check.get("status") in ["warning", "critical"]:
            candidates.append(OptimizationCandidate(
                name="resource_usage_optimization",
                category="performance",
                risk_level="high",
                impact_estimate="high",
                complexity="high",
                prerequisites=["資源監控數據", "性能分析工具"],
                description="優化CPU和記憶體使用，改善系統整體性能",
                metrics={"cpu_percent": resource_check.get("cpu_percent")}
            ))

        # 候選5: 監控系統優化
        if len(stats["warnings"]) > 5:  # 太多警告
            candidates.append(OptimizationCandidate(
                name="monitoring_system_optimization",
                category="monitoring",
                risk_level="low",
                impact_estimate="low",
                complexity="medium",
                prerequisites=["監控系統運行數據"],
                description="優化監控系統，減少誤報並提高準確性",
                metrics={"warning_count": len(stats["warnings"])}
            ))

        self.optimization_candidates = candidates
        return candidates

    def rank_candidates(self) -> List[Tuple[OptimizationCandidate, float]]:
        """對優化候選項目進行排名"""
        ranked = []
        for candidate in self.optimization_candidates:
            score = candidate.calculate_priority_score()
            ranked.append((candidate, score))

        # 按分數降序排序
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    def create_ab_test_plan(self, candidate: OptimizationCandidate) -> ABTestFramework:
        """為優化候選創建A/B測試計劃"""
        test_name = f"optimization_test_{candidate.name}"

        ab_test = ABTestFramework(test_name)

        # 基準變體
        ab_test.add_variant("baseline", {"optimization_enabled": False}, 70)

        # 優化變體
        ab_test.add_variant("optimized", {"optimization_enabled": True}, 30)

        return ab_test

    def generate_implementation_plan(self, candidate: OptimizationCandidate) -> Dict[str, Any]:
        """生成實施計劃"""
        plan = {
            "candidate": candidate.name,
            "description": candidate.description,
            "risk_assessment": {
                "level": candidate.risk_level,
                "mitigations": self._get_risk_mitigations(candidate)
            },
            "implementation_steps": self._get_implementation_steps(candidate),
            "rollback_plan": self._get_rollback_plan(candidate),
            "success_metrics": self._get_success_metrics(candidate),
            "timeline_weeks": self._estimate_timeline(candidate)
        }

        return plan

    def _get_risk_mitigations(self, candidate: OptimizationCandidate) -> List[str]:
        """獲取風險緩解措施"""
        mitigations = []

        if candidate.risk_level == "high":
            mitigations.extend([
                "在測試環境完整驗證",
                "準備立即回滾機制",
                "分階段灰度釋放",
                "實時監控關鍵指標"
            ])
        elif candidate.risk_level == "medium":
            mitigations.extend([
                "A/B測試驗證效果",
                "監控系統持續運行",
                "準備降級方案"
            ])
        else:  # low
            mitigations.extend([
                "代碼審查確保正確性",
                "單元測試覆蓋"
            ])

        return mitigations

    def _get_implementation_steps(self, candidate: OptimizationCandidate) -> List[str]:
        """獲取實施步驟"""
        steps = []

        if candidate.name == "lock_holding_optimization":
            steps = [
                "分析當前鎖定持有模式",
                "識別不必要的長時間持有",
                "實現鎖定範圍優化",
                "添加性能基準測試",
                "A/B測試驗證改善"
            ]
        elif candidate.name == "async_bridge_performance":
            steps = [
                "實現AsyncBridge統計收集",
                "分析操作模式和瓶頸",
                "優化關鍵路徑操作",
                "性能測試驗證改善",
                "生產環境灰度釋放"
            ]
        else:
            steps = [
                "詳細設計優化方案",
                "實現和測試",
                "性能評估",
                "生產環境部署"
            ]

        return steps

    def _get_rollback_plan(self, candidate: OptimizationCandidate) -> Dict[str, Any]:
        """獲取回滾計劃"""
        return {
            "immediate_rollback": "關閉優化標記，恢復原始行為",
            "monitoring_rollback": "繼續監控，回滾後評估影響",
            "data_preservation": "保留優化期間的所有監控數據",
            "communication_plan": "通知相關團隊優化回滾原因"
        }

    def _get_success_metrics(self, candidate: OptimizationCandidate) -> List[str]:
        """獲取成功指標"""
        if candidate.name == "lock_holding_optimization":
            return [
                "平均鎖定競爭時間減少20%",
                "系統響應時間改善10%",
                "死鎖風險評估分數降低"
            ]
        elif candidate.name == "async_bridge_performance":
            return [
                "AsyncBridge操作平均響應時間減少15%",
                "關鍵操作成功率維持99.9%以上",
                "背景操作Fire-and-forget成功率>95%"
            ]
        else:
            return [
                "相關性能指標改善",
                "系統穩定性維持",
                "資源使用效率提升"
            ]

    def _estimate_timeline(self, candidate: OptimizationCandidate) -> int:
        """估計時間表（週）"""
        complexity_multiplier = {"low": 1, "medium": 2, "high": 4}
        risk_multiplier = {"low": 1, "medium": 1.5, "high": 2}

        base_weeks = 2  # 基礎時間
        timeline = base_weeks * \
            complexity_multiplier.get(candidate.complexity, 2)
        timeline *= risk_multiplier.get(candidate.risk_level, 1.5)

        return int(timeline)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description="SpeakUB Optimization Assessment Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
基於監控數據評估優化機會並實施A/B測試。

使用示例:
  python optimization_assessment.py candidates    # 識別優化候選
  python optimization_assessment.py plan lock_holding_optimization  # 生成實施計劃
  python optimization_assessment.py ab-test async_bridge_performance  # 創建A/B測試
  python optimization_assessment.py report       # 生成評估報告
        """
    )

    parser.add_argument(
        'command',
        choices=['candidates', 'plan', 'ab-test', 'report'],
        help='要執行的命令'
    )

    parser.add_argument(
        'target',
        nargs='?',
        help='目標優化候選項目名稱'
    )

    args = parser.parse_args()

    framework = OptimizationAssessmentFramework()

    if args.command == 'candidates':
        # 識別和排名優化候選
        candidates = framework.identify_candidates()
        ranked = framework.rank_candidates()

        print("🎯 SpeakUB 優化候選評估")
        print("="*60)

        for i, (candidate, score) in enumerate(ranked, 1):
            print(f"\n{i}. {candidate.name}")
            print(f"   類別: {candidate.category}")
            print(
                f"   風險: {candidate.risk_level} | 影響: {candidate.impact_estimate} | 複雜度: {candidate.complexity}")
            print(f"   優先權分數: {score:.1f}/100")
            print(f"   描述: {candidate.description}")

            if candidate.prerequisites:
                print(f"   先決條件: {', '.join(candidate.prerequisites)}")

    elif args.command == 'plan':
        if not args.target:
            print("❌ 需要指定優化候選項目名稱")
            sys.exit(1)

        # 生成實施計劃
        candidates = framework.identify_candidates()
        candidate = next(
            (c for c in candidates if c.name == args.target), None)

        if not candidate:
            print(f"❌ 未找到優化候選項目: {args.target}")
            sys.exit(1)

        plan = framework.generate_implementation_plan(candidate)

        print(f"📋 優化實施計劃: {candidate.name}")
        print("="*60)
        print(json.dumps(plan, indent=2, ensure_ascii=False))

    elif args.command == 'ab-test':
        if not args.target:
            print("❌ 需要指定優化候選項目名稱")
            sys.exit(1)

        # 創建A/B測試
        candidates = framework.identify_candidates()
        candidate = next(
            (c for c in candidates if c.name == args.target), None)

        if not candidate:
            print(f"❌ 未找到優化候選項目: {args.target}")
            sys.exit(1)

        ab_test = framework.create_ab_test_plan(candidate)

        print(f"🧪 A/B測試計劃: {candidate.name}")
        print("="*60)

        for variant_name, variant_data in ab_test.variants.items():
            print(f"\n變體: {variant_name}")
            print(f"  流量分配: {variant_data['traffic_percentage']}%")
            print(f"  配置: {variant_data['config']}")

        print(f"\n建議: {ab_test.get_recommendation()}")

    elif args.command == 'report':
        # 生成完整評估報告
        candidates = framework.identify_candidates()
        ranked = framework.rank_candidates()

        health_status = check_system_health()

        report = {
            "assessment_date": datetime.now().isoformat(),
            "assessment_period_days": framework.assessment_period_days,
            "current_health_status": health_status["overall_status"],
            "optimization_candidates_count": len(candidates),
            "top_candidates": [
                {
                    "name": candidate.name,
                    "priority_score": score,
                    "risk_level": candidate.risk_level,
                    "impact_estimate": candidate.impact_estimate
                } for candidate, score in ranked[:5]
            ],
            "recommendations": [
                "基於監控數據評估優化機會",
                "優先實施高優先權、低風險的優化",
                "使用A/B測試驗證優化效果",
                "建立回滾機制確保系統穩定"
            ]
        }

        print("📊 SpeakUB 優化評估報告")
        print("="*60)
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
