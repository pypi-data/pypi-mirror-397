#!/usr/bin/env python3
"""
Batch Performance Feedback Loop Manager

Implements adaptive parameter adjustment based on actual playback performance:
- Monitors synthesis times and buffer states
- Adjusts char_limit and batch_size dynamically
- Forms a closed-loop optimization system
"""

import logging
import time
from collections import deque
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class PerformanceLevel(Enum):
    """Performance classification for feedback loop"""
    EXCELLENT = "excellent"  # Smooth playback, no underruns
    GOOD = "good"            # Occasional underruns, manageable
    POOR = "poor"            # Frequent underruns, problematic
    CRITICAL = "critical"    # Severe issues, needs intervention


@dataclass
class SynthesisMetrics:
    """Metrics from a single synthesis batch"""
    batch_size: int          # Number of items synthesized
    total_chars: int         # Total characters synthesized
    synthesis_time: float    # Time taken in seconds
    buffer_state: Optional[str] = None  # "full", "adequate", "low", "critical"
    timestamp: float = 0.0


class BatchPerformanceFeedback:
    """
    Monitors playback performance and adjusts batching parameters dynamically.

    Feedback loop:
    1. Record synthesis metrics (time, buffer state)
    2. Calculate performance level
    3. Adjust parameters if needed
    4. Record adjustment for analytics
    """

    def __init__(self, window_size: int = 50):
        """
        Initialize performance feedback system.

        Args:
            window_size: Number of recent metrics to maintain
        """
        self._metrics: deque = deque(maxlen=window_size)
        self._adjustments: deque = deque(maxlen=100)
        self._last_adjustment_time = time.time()
        self._adjustment_interval = 5.0  # Min seconds between adjustments

        # Performance thresholds
        self._time_threshold_good = 15.0      # Good: synthesis < 15s
        self._time_threshold_poor = 25.0      # Poor: synthesis > 25s
        self._underrun_threshold = 3           # Poor if 3+ underruns in window

    def record_synthesis(
        self,
        batch_size: int,
        total_chars: int,
        synthesis_time: float,
        buffer_state: Optional[str] = None
    ) -> None:
        """
        Record metrics from a synthesis batch.

        Args:
            batch_size: Number of items synthesized
            total_chars: Total characters synthesized
            synthesis_time: Time taken in seconds
            buffer_state: Current buffer state ("full", "adequate", "low", "critical")
        """
        metric = SynthesisMetrics(
            batch_size=batch_size,
            total_chars=total_chars,
            synthesis_time=synthesis_time,
            buffer_state=buffer_state,
            timestamp=time.time()
        )
        self._metrics.append(metric)
        logger.debug(
            f"Recorded synthesis metric: items={batch_size}, chars={total_chars}, "
            f"time={synthesis_time:.1f}s, buffer={buffer_state}"
        )

    def get_performance_level(self) -> PerformanceLevel:
        """
        Analyze recent metrics and determine performance level.

        Returns:
            Performance level based on synthesis times and buffer state
        """
        if not self._metrics:
            return PerformanceLevel.GOOD

        recent_metrics = list(self._metrics)[-10:]  # Last 10 metrics

        # Count buffer underruns
        underruns = sum(
            1 for m in recent_metrics
            if m.buffer_state in ("low", "critical")
        )

        if underruns >= self._underrun_threshold:
            return PerformanceLevel.CRITICAL

        # Analyze synthesis times
        avg_time = sum(m.synthesis_time for m in recent_metrics) / \
            len(recent_metrics)

        if avg_time > self._time_threshold_poor or underruns > 0:
            return PerformanceLevel.POOR
        elif avg_time < self._time_threshold_good:
            return PerformanceLevel.EXCELLENT
        else:
            return PerformanceLevel.GOOD

    def should_adjust_parameters(self) -> bool:
        """
        Determine if parameters should be adjusted based on performance.

        Returns:
            True if adjustment is needed and interval has passed
        """
        # Check adjustment interval
        now = time.time()
        if now - self._last_adjustment_time < self._adjustment_interval:
            return False

        performance = self.get_performance_level()
        return performance in (PerformanceLevel.CRITICAL, PerformanceLevel.POOR)

    def calculate_adjustment(
        self,
        current_char_limit: int,
        current_batch_size: int,
        engine_name: str
    ) -> Tuple[int, int, str]:
        """
        Calculate recommended parameter adjustments based on performance.

        Args:
            current_char_limit: Current character limit
            current_batch_size: Current batch size
            engine_name: Name of TTS engine

        Returns:
            Tuple of (new_char_limit, new_batch_size, reason)
        """
        performance = self.get_performance_level()

        # Conservative adjustments for different performance levels
        adjustment_factor = {
            PerformanceLevel.CRITICAL: 0.6,   # Reduce to 60%
            PerformanceLevel.POOR: 0.8,       # Reduce to 80%
            PerformanceLevel.GOOD: 1.0,       # No change
            PerformanceLevel.EXCELLENT: 1.15,  # Increase to 115%
        }

        factor = adjustment_factor[performance]

        # Calculate new values
        new_char_limit = max(50, int(current_char_limit * factor))
        new_batch_size = max(1, int(current_batch_size * factor))

        # Ensure reasonable bounds per engine
        engine_bounds = {
            "edge-tts": (150, 250),
            "nanmai": (100, 200),
        }

        if engine_name in engine_bounds:
            min_limit, max_limit = engine_bounds[engine_name]
            new_char_limit = max(min_limit, min(max_limit, new_char_limit))

        reason = f"Performance {performance.value}: adjust from {current_char_limit}/{current_batch_size} " \
            f"to {new_char_limit}/{new_batch_size}"

        return new_char_limit, new_batch_size, reason

    def record_adjustment(
        self,
        engine: str,
        prev_char_limit: int,
        new_char_limit: int,
        prev_batch_size: int,
        new_batch_size: int,
        reason: str
    ) -> None:
        """Record an adjustment for analytics"""
        adjustment = {
            "timestamp": time.time(),
            "engine": engine,
            "prev_char_limit": prev_char_limit,
            "new_char_limit": new_char_limit,
            "prev_batch_size": prev_batch_size,
            "new_batch_size": new_batch_size,
            "reason": reason,
        }
        self._adjustments.append(adjustment)
        self._last_adjustment_time = time.time()
        logger.info(f"Parameter adjustment: {reason}")

    def get_feedback_statistics(self) -> Dict:
        """Get comprehensive feedback loop statistics"""
        if not self._metrics:
            return {"error": "No metrics recorded"}

        metrics = list(self._metrics)
        times = [m.synthesis_time for m in metrics]

        stats = {
            "total_samples": len(metrics),
            "performance_level": self.get_performance_level().value,
            "avg_synthesis_time": sum(times) / len(times),
            "min_synthesis_time": min(times),
            "max_synthesis_time": max(times),
            "buffer_underruns": sum(
                1 for m in metrics if m.buffer_state in ("low", "critical")
            ),
            "total_adjustments": len(self._adjustments),
            "recent_adjustments": list(self._adjustments)[-5:],
        }

        return stats

    def reset_metrics(self) -> None:
        """Reset metrics for a new playback session"""
        self._metrics.clear()
        logger.debug("Performance metrics reset")


# ============================================================================
# Integration with FusionBatchingStrategy
# ============================================================================

def integrate_feedback_loop_with_strategy(strategy, feedback_manager: BatchPerformanceFeedback) -> None:
    """
    Example of integrating feedback loop with batching strategy.

    This would be called periodically during playback to apply performance-based adjustments.
    """
    if not feedback_manager.should_adjust_parameters():
        return

    # Get current parameters
    current_char_limit = strategy.char_limit
    current_batch_size = strategy.base_batch_size
    current_engine = strategy._current_engine

    # Calculate adjustment
    new_char_limit, new_batch_size, reason = feedback_manager.calculate_adjustment(
        current_char_limit,
        current_batch_size,
        current_engine
    )

    # Apply if different
    if new_char_limit != current_char_limit or new_batch_size != current_batch_size:
        strategy.char_limit = new_char_limit
        strategy.base_batch_size = new_batch_size
        feedback_manager.record_adjustment(
            current_engine,
            current_char_limit,
            new_char_limit,
            current_batch_size,
            new_batch_size,
            reason
        )
        logger.info(f"Batching parameters updated: {reason}")


if __name__ == "__main__":
    # Example usage
    feedback = BatchPerformanceFeedback()

    # Simulate some synthesis metrics
    feedback.record_synthesis(5, 200, 12.0, buffer_state="full")
    feedback.record_synthesis(5, 210, 13.5, buffer_state="adequate")
    feedback.record_synthesis(3, 150, 8.0, buffer_state="adequate")
    feedback.record_synthesis(4, 180, 25.0, buffer_state="low")  # Underrun
    feedback.record_synthesis(3, 120, 22.0, buffer_state="low")  # Underrun

    # Check performance
    perf_level = feedback.get_performance_level()
    print(f"Performance level: {perf_level.value}")

    # Check if adjustment needed
    if feedback.should_adjust_parameters():
        new_char, new_batch, reason = feedback.calculate_adjustment(
            200, 5, "edge-tts")
        print(f"Adjustment recommended: {reason}")

    # Get statistics
    stats = feedback.get_feedback_statistics()
    print(f"Statistics: {stats}")
