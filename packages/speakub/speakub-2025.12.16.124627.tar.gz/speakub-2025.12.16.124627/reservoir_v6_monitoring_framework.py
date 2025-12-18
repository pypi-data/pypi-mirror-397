#!/usr/bin/env python3
"""
SpeakUB Reservoir v6.0 效能監控框架

提供生產環境的水位變化監控、效能指標收集和參數優化建議。
"""

import json
import logging
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class BufferMetrics:
    """緩衝區效能指標"""
    timestamp: float
    buffer_level: float
    trigger_count: int
    consumption_rate: float
    network_latency: Optional[float] = None
    cpu_usage: Optional[float] = None


@dataclass
class PerformanceReport:
    """效能報告"""
    period_start: float
    period_end: float
    total_triggers: int
    avg_buffer_level: float
    min_buffer_level: float
    max_buffer_level: float
    buffer_stability: float
    consumption_efficiency: float
    recommendations: List[str]


class ReservoirV6Monitor:
    """Reservoir v6.0 效能監控器"""

    def __init__(self, history_size: int = 1000):
        self.metrics_history = deque(maxlen=history_size)
        self.current_session_start = time.time()
        self.last_trigger_count = 0

    def record_buffer_level(self, buffer_level: float, trigger_count: int,
                            network_latency: Optional[float] = None,
                            cpu_usage: Optional[float] = None):
        """記錄緩衝區水位"""
        consumption_rate = self._calculate_consumption_rate()

        metric = BufferMetrics(
            timestamp=time.time(),
            buffer_level=buffer_level,
            trigger_count=trigger_count,
            consumption_rate=consumption_rate,
            network_latency=network_latency,
            cpu_usage=cpu_usage
        )

        self.metrics_history.append(metric)

        # 記錄顯著事件
        if len(self.metrics_history) >= 2:
            prev_metric = self.metrics_history[-2]

            # 檢測水位急劇下降
            if prev_metric.buffer_level - buffer_level > 10:
                logger.warning(".2f")
            # 檢測過度觸發
            if trigger_count > prev_metric.trigger_count + 5:
                logger.warning(
                    f"觸發頻率異常增加: {prev_metric.trigger_count} -> {trigger_count}")

    def _calculate_consumption_rate(self) -> float:
        """計算緩衝消耗率"""
        if len(self.metrics_history) < 2:
            return 0.0

        recent_metrics = list(self.metrics_history)[-10:]  # 最近10個數據點
        if len(recent_metrics) < 2:
            return 0.0

        time_span = recent_metrics[-1].timestamp - recent_metrics[0].timestamp
        buffer_change = recent_metrics[-1].buffer_level -
        recent_metrics[0].buffer_level

        if time_span > 0:
            return -buffer_change / time_span  # 正值表示消耗率
        return 0.0

    def generate_performance_report(self, period_hours: float = 1.0) -> PerformanceReport:
        """生成效能報告"""
        cutoff_time = time.time() - (period_hours * 3600)
        recent_metrics = [
            m for m in self.metrics_history if m.timestamp >= cutoff_time]

        if not recent_metrics:
            return PerformanceReport(
                period_start=cutoff_time,
                period_end=time.time(),
                total_triggers=0,
                avg_buffer_level=0.0,
                min_buffer_level=0.0,
                max_buffer_level=0.0,
                buffer_stability=0.0,
                consumption_efficiency=0.0,
                recommendations=["無足夠數據生成報告"]
            )

        # 計算基本指標
        buffer_levels = [m.buffer_level for m in recent_metrics]
        trigger_counts = [m.trigger_count for m in recent_metrics]

        total_triggers = max(trigger_counts) -
        min(trigger_counts) if trigger_counts else 0
        avg_buffer_level = sum(buffer_levels) / len(buffer_levels)
        min_buffer_level = min(buffer_levels)
        max_buffer_level = max(buffer_levels)

        # 計算穩定性指標 (0-1, 1為最穩定)
        if max_buffer_level > 0:
            buffer_stability = 1 - (max_buffer_level -
                                    min_buffer_level) / (max_buffer_level + 1)
        else:
            buffer_stability = 1.0

        # 計算消耗效率 (理想範圍: 15-60秒)
        consumption_efficiency = 0.0
        if 15 <= avg_buffer_level <= 60:
            consumption_efficiency = 1.0
        elif avg_buffer_level < 15:
            consumption_efficiency = avg_buffer_level / 15.0  # 低於15秒的懲罰
        else:
            consumption_efficiency = 60.0 / avg_buffer_level  # 高於60秒的懲罰

        # 生成建議
        recommendations = self._generate_recommendations(
            avg_buffer_level, min_buffer_level, max_buffer_level,
            buffer_stability, total_triggers, period_hours
        )

        return PerformanceReport(
            period_start=cutoff_time,
            period_end=time.time(),
            total_triggers=total_triggers,
            avg_buffer_level=avg_buffer_level,
            min_buffer_level=min_buffer_level,
            max_buffer_level=max_buffer_level,
            buffer_stability=buffer_stability,
            consumption_efficiency=consumption_efficiency,
            recommendations=recommendations
        )

    def _generate_recommendations(self, avg_buffer: float, min_buffer: float,
                                  max_buffer: float, stability: float,
                                  triggers: int, period_hours: float) -> List[str]:
        """生成優化建議"""
        recommendations = []

        # 緩衝水位分析
        if avg_buffer < 10:
            recommendations.append("⚠️ 平均緩衝水位過低，建議降低 LOW_WATERMARK 或增加網路優先級")
        elif avg_buffer > 70:
            recommendations.append("⚠️ 平均緩衝水位過高，建議提高 HIGH_WATERMARK 或增加消耗率")

        # 穩定性分析
        if stability < 0.5:
            recommendations.append("⚠️ 緩衝水位波動過大，建議檢查網路穩定性或調整水位閾值")
        elif stability > 0.9:
            recommendations.append("✅ 緩衝水位非常穩定，系統運行良好")

        # 觸發頻率分析
        trigger_rate = triggers / period_hours  # 每小時觸發次數
        if trigger_rate > 20:
            recommendations.append("⚠️ 觸發頻率過高，建議增加批次大小或降低 LOW_WATERMARK")
        elif trigger_rate < 2:
            recommendations.append("ℹ️ 觸發頻率偏低，系統運行高效")

        # 極端情況分析
        if min_buffer < 5:
            recommendations.append("🚨 檢測到嚴重低水位情況，建議立即檢查網路連接")
        if max_buffer > 100:
            recommendations.append("ℹ️ 緩衝水位經常過高，考慮增加播放速度或降低 HIGH_WATERMARK")

        # 效能評估
        if stability > 0.7 and 15 <= avg_buffer <= 60:
            recommendations.append("✅ 系統效能優良，水位控制運行正常")
        elif stability < 0.3:
            recommendations.append("❌ 系統效能不穩定，需要緊急調整參數")

        return recommendations

    def export_metrics_to_json(self, filename: str):
        """匯出指標數據到JSON文件"""
        metrics_data = []
        for metric in self.metrics_history:
            metrics_data.append({
                'timestamp': metric.timestamp,
                'buffer_level': metric.buffer_level,
                'trigger_count': metric.trigger_count,
                'consumption_rate': metric.consumption_rate,
                'network_latency': metric.network_latency,
                'cpu_usage': metric.cpu_usage
            })

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(metrics_data, f, indent=2, ensure_ascii=False)

        logger.info(f"指標數據已匯出到 {filename}")

    def get_current_status(self) -> Dict:
        """獲取當前狀態摘要"""
        if not self.metrics_history:
            return {"status": "no_data"}

        latest = self.metrics_history[-1]
        recent_avg = sum(m.buffer_level for m in list(
            self.metrics_history)[-10:]) / min(10, len(self.metrics_history))

        return {
            "current_buffer": latest.buffer_level,
            "recent_avg_buffer": recent_avg,
            "total_metrics": len(self.metrics_history),
            "session_duration": time.time() - self.current_session_start,
            "last_update": latest.timestamp
        }


class ParameterOptimizer:
    """參數優化建議生成器"""

    @staticmethod
    def analyze_and_suggest_parameters(report: PerformanceReport,
                                       current_low_watermark: float = 15.0,
                                       current_high_watermark: float = 60.0) -> Dict:
        """基於效能報告分析並建議參數調整"""

        suggestions = {
            "low_watermark": current_low_watermark,
            "high_watermark": current_high_watermark,
            "recommended_changes": [],
            "expected_improvements": []
        }

        # 低水位調整建議
        if report.min_buffer_level < 8:
            new_low = max(8.0, current_low_watermark * 0.8)
            suggestions["low_watermark"] = new_low
            suggestions["recommended_changes"].append(
                f"降低 LOW_WATERMARK: {current_low_watermark} -> {new_low}")
            suggestions["expected_improvements"].append("減少低水位警報頻率")

        elif report.avg_buffer_level < 12:
            new_low = max(10.0, current_low_watermark * 0.9)
            suggestions["low_watermark"] = new_low
            suggestions["recommended_changes"].append(
                f"適度降低 LOW_WATERMARK: {current_low_watermark} -> {new_low}")
            suggestions["expected_improvements"].append("提升緩衝效率")

        # 高水位調整建議
        if report.max_buffer_level > 80:
            new_high = min(80.0, current_high_watermark * 1.2)
            suggestions["high_watermark"] = new_high
            suggestions["recommended_changes"].append(
                f"提高 HIGH_WATERMARK: {current_high_watermark} -> {new_high}")
            suggestions["expected_improvements"].append("減少不必要的休眠時間")

        elif report.avg_buffer_level > 70:
            new_high = min(75.0, current_high_watermark * 1.1)
            suggestions["high_watermark"] = new_high
            suggestions["recommended_changes"].append(
                f"適度提高 HIGH_WATERMARK: {current_high_watermark} -> {new_high}")
            suggestions["expected_improvements"].append("優化資源利用")

        # 穩定性調整建議
        if report.buffer_stability < 0.5:
            suggestions["recommended_changes"].append("緩衝波動大，建議檢查網路條件")
            suggestions["expected_improvements"].append("改善網路連接穩定性")

        return suggestions


def print_monitoring_guide():
    """列印監控使用指南"""
    print("\n" + "="*80)
    print("SPEAKUB RESERVOIR v6.0 效能監控指南")
    print("="*80)

    print("\n1. 部署監控")
    print("   - 在應用啟動時建立 ReservoirV6Monitor 實例")
    print("   - 在水位變化時調用 record_buffer_level()")
    print("   - 定期生成效能報告")

    print("\n2. 關鍵指標監控")
    print("   - 平均緩衝水位: 理想範圍 15-60秒")
    print("   - 緩衝穩定性: >0.7 表示運行良好")
    print("   - 觸發頻率: 正常範圍 2-20次/小時")
    print("   - 消耗效率: >0.8 表示高效")

    print("\n3. 告警條件")
    print("   - 平均緩衝 < 10秒: 低水位告警")
    print("   - 穩定性 < 0.3: 波動告警")
    print("   - 觸發頻率 > 30次/小時: 過載告警")

    print("\n4. 參數優化")
    print("   - LOW_WATERMARK: 根據網路速度調整 (8-20秒)")
    print("   - HIGH_WATERMARK: 根據記憶體限制調整 (40-80秒)")
    print("   - 定期評估並調整參數")

    print("\n5. 數據匯出")
    print("   - 使用 export_metrics_to_json() 匯出歷史數據")
    print("   - 用於離線分析和長期趨勢研究")


if __name__ == "__main__":
    print_monitoring_guide()
