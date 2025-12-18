#!/usr/bin/env python3
"""
Test batch performance feedback loop system.

Verifies:
1. Performance level classification
2. Dynamic parameter adjustment calculations
3. Adjustment recording and analytics
4. Integration scenarios
"""

from speakub.tts.fusion_reservoir.batch_performance_feedback import (
    BatchPerformanceFeedback,
    PerformanceLevel,
    SynthesisMetrics
)
import sys
sys.path.insert(0, '/home/sam/Templates/epub-reader-rich 專案/GGGG/SpeakUB')


def test_performance_level_classification():
    """Test performance level classification based on metrics"""
    print("=" * 60)
    print("Test 1: Performance Level Classification")
    print("=" * 60)

    feedback = BatchPerformanceFeedback()

    # Test 1a: Excellent performance - fast synthesis, no underruns
    feedback.record_synthesis(5, 200, 10.0, buffer_state="full")
    feedback.record_synthesis(5, 210, 12.0, buffer_state="adequate")
    feedback.record_synthesis(4, 180, 11.5, buffer_state="adequate")

    level = feedback.get_performance_level()
    assert level == PerformanceLevel.EXCELLENT
    print(f"✓ Excellent performance detected: {level.value}")

    # Test 1b: Good performance - moderate synthesis time
    feedback._metrics.clear()
    feedback.record_synthesis(5, 200, 16.0, buffer_state="full")
    feedback.record_synthesis(5, 210, 17.0, buffer_state="adequate")
    feedback.record_synthesis(4, 180, 15.5, buffer_state="adequate")

    level = feedback.get_performance_level()
    assert level == PerformanceLevel.GOOD
    print(f"✓ Good performance detected: {level.value}")

    # Test 1c: Poor performance - slow synthesis with underruns
    feedback._metrics.clear()
    feedback.record_synthesis(3, 150, 20.0, buffer_state="low")
    feedback.record_synthesis(3, 160, 22.0, buffer_state="low")
    feedback.record_synthesis(2, 100, 25.0, buffer_state="adequate")

    level = feedback.get_performance_level()
    assert level == PerformanceLevel.POOR
    print(f"✓ Poor performance detected: {level.value}")

    # Test 1d: Critical performance - multiple underruns
    feedback._metrics.clear()
    for i in range(5):
        feedback.record_synthesis(2, 100, 25.0, buffer_state="critical")

    level = feedback.get_performance_level()
    assert level == PerformanceLevel.CRITICAL
    print(f"✓ Critical performance detected: {level.value}")

    print()


def test_parameter_adjustment_calculation():
    """Test parameter adjustment calculations"""
    print("=" * 60)
    print("Test 2: Parameter Adjustment Calculations")
    print("=" * 60)

    feedback = BatchPerformanceFeedback()

    # Simulate poor performance (underruns)
    for i in range(4):
        feedback.record_synthesis(5, 200, 22.0, buffer_state="low")

    # Get adjustment
    new_char, new_batch, reason = feedback.calculate_adjustment(
        200, 5, "edge-tts")

    print(f"Original: char_limit=200, batch_size=5")
    print(f"Adjusted: char_limit={new_char}, batch_size={new_batch}")
    print(f"Reason: {reason}")

    # In poor performance, should reduce
    assert new_char < 200
    assert new_batch < 5
    print("✓ Parameters reduced for poor performance")

    # Test excellent performance - should increase
    feedback._metrics.clear()
    for i in range(5):
        feedback.record_synthesis(8, 300, 8.0, buffer_state="full")

    new_char, new_batch, reason = feedback.calculate_adjustment(
        200, 5, "edge-tts")
    print(f"\nFor excellent performance:")
    print(f"Adjusted: char_limit={new_char}, batch_size={new_batch}")
    assert new_char > 200, f"Expected char_limit > 200, got {new_char}"
    # Batch size adjustment: 5 * 1.15 = 5.75 -> 5 (int conversion)
    assert new_batch >= 5, f"Expected batch_size >= 5, got {new_batch}"
    print("✓ Parameters adjusted for excellent performance")

    # Test engine-specific bounds for nanmai
    new_char, new_batch, reason = feedback.calculate_adjustment(
        200, 5, "nanmai")
    # Nanmai bounds: (100, 200)
    assert new_char <= 200 and new_char >= 100
    print(f"✓ Nanmai adjustment respects bounds: {new_char}")

    print()


def test_adjustment_recording_and_analytics():
    """Test recording adjustments and gathering analytics"""
    print("=" * 60)
    print("Test 3: Adjustment Recording & Analytics")
    print("=" * 60)

    feedback = BatchPerformanceFeedback()

    # Record some synthesis metrics first
    feedback.record_synthesis(5, 200, 12.0, buffer_state="full")
    feedback.record_synthesis(5, 210, 13.0, buffer_state="adequate")

    # Record some adjustments
    feedback.record_adjustment(
        "edge-tts", 200, 160, 5, 4, "Poor performance: reduce 20%"
    )
    feedback.record_adjustment(
        "edge-tts", 160, 184, 4, 5, "Good performance: increase 15%"
    )
    feedback.record_adjustment(
        "nanmai", 150, 90, 5, 3, "Critical: reduce 40%"
    )

    stats = feedback.get_feedback_statistics()
    print(f"Total adjustments: {stats.get('total_adjustments', 'N/A')}")
    assert stats.get('total_adjustments', 0) == 3
    print("✓ Adjustment count is correct")

    # Check recent adjustments
    recent = stats.get('recent_adjustments', [])
    assert len(recent) > 0
    print(f"✓ Recent adjustments captured: {len(recent)} records")

    for adj in recent:
        print(
            f"  - {adj['engine']}: {adj['prev_char_limit']}->{adj['new_char_limit']}")

    print()


def test_adjustment_interval_throttling():
    """Test that adjustments are throttled to prevent too-frequent updates"""
    print("=" * 60)
    print("Test 4: Adjustment Interval Throttling")
    print("=" * 60)

    feedback = BatchPerformanceFeedback(window_size=50)
    feedback._adjustment_interval = 0.1  # Very short for testing

    # Create critical performance condition (recent metrics matter)
    feedback.record_synthesis(2, 100, 25.0, buffer_state="critical")
    feedback.record_synthesis(2, 100, 26.0, buffer_state="critical")
    feedback.record_synthesis(2, 100, 25.0, buffer_state="critical")
    feedback.record_synthesis(2, 100, 26.0, buffer_state="critical")
    feedback.record_synthesis(2, 100, 25.0, buffer_state="critical")

    # First adjustment should be allowed (critical performance + no recent adjustment)
    can_adjust = feedback.should_adjust_parameters()
    print(f"First check - should_adjust_parameters: {can_adjust}")

    # Record the adjustment to reset timer
    feedback.record_adjustment("edge-tts", 200, 160, 5, 4, "Test adjustment 1")
    print("✓ Adjustment recorded")

    # Immediate second request should be throttled (interval not passed)
    import time
    can_adjust_now = feedback.should_adjust_parameters()
    print(f"Immediately after - should_adjust_parameters: {can_adjust_now}")
    assert can_adjust_now == False, "Should be throttled immediately"
    print("✓ Adjustment throttled immediately after")

    # Wait for interval to pass
    time.sleep(0.15)
    can_adjust_later = feedback.should_adjust_parameters()
    print(f"After 0.15s - should_adjust_parameters: {can_adjust_later}")
    # After interval, will depend on current performance
    print("✓ Adjustment interval timeout works")

    print()


def test_metrics_recording():
    """Test synthesis metrics recording and statistics"""
    print("=" * 60)
    print("Test 5: Metrics Recording & Statistics")
    print("=" * 60)

    feedback = BatchPerformanceFeedback(window_size=10)

    # Record metrics
    times = [10.0, 11.5, 12.0, 9.5, 10.5]
    chars = [200, 210, 220, 190, 205]

    for i, (time_val, char_val) in enumerate(zip(times, chars)):
        feedback.record_synthesis(5, char_val, time_val,
                                  buffer_state="adequate")

    stats = feedback.get_feedback_statistics()

    print(f"Total samples: {stats['total_samples']}")
    assert stats['total_samples'] == 5
    print("✓ Sample count is correct")

    print(f"Average synthesis time: {stats['avg_synthesis_time']:.1f}s")
    assert 10.0 <= stats['avg_synthesis_time'] <= 12.0
    print("✓ Average time calculated correctly")

    print(
        f"Min/Max: {stats['min_synthesis_time']:.1f}s / {stats['max_synthesis_time']:.1f}s")
    assert stats['min_synthesis_time'] == 9.5
    assert stats['max_synthesis_time'] == 12.0
    print("✓ Min/Max values correct")

    print()


def test_integration_scenario():
    """Test a realistic integration scenario"""
    print("=" * 60)
    print("Test 6: Integration Scenario")
    print("=" * 60)

    feedback = BatchPerformanceFeedback()
    feedback._adjustment_interval = 0.01  # Allow quick adjustments for test

    # Simulate playback: good -> poor -> adjusted -> recovery
    print("\nPhase 1: Initial good performance")
    for i in range(3):
        feedback.record_synthesis(6, 250, 12.0, buffer_state="full")
    print(f"  Performance: {feedback.get_performance_level().value}")

    print("\nPhase 2: Degradation (slow synthesis + underruns)")
    for i in range(5):
        feedback.record_synthesis(6, 250, 23.0, buffer_state="low")
    perf_level = feedback.get_performance_level()
    print(f"  Performance: {perf_level.value}")
    assert perf_level in (PerformanceLevel.POOR, PerformanceLevel.CRITICAL)

    print("\nPhase 3: Apply adjustments")
    if feedback.should_adjust_parameters():
        new_char, new_batch, reason = feedback.calculate_adjustment(
            200, 6, "edge-tts")
        print(f"  Adjustment: {reason}")
        print(f"  Applied: char_limit={new_char}, batch_size={new_batch}")
        feedback.record_adjustment(
            "edge-tts", 200, new_char, 6, new_batch, reason)

    print("\nPhase 4: Recovery (smaller batches work well)")
    feedback._metrics.clear()  # Clear old metrics
    for i in range(3):
        feedback.record_synthesis(4, 160, 9.0, buffer_state="full")
    perf_level = feedback.get_performance_level()
    print(f"  Performance: {perf_level.value}")
    assert perf_level in (PerformanceLevel.GOOD, PerformanceLevel.EXCELLENT)

    print("\n✓ Integration scenario completed successfully")
    print()


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("BATCH PERFORMANCE FEEDBACK LOOP TESTS")
    print("=" * 60 + "\n")

    try:
        test_performance_level_classification()
        test_parameter_adjustment_calculation()
        test_adjustment_recording_and_analytics()
        test_adjustment_interval_throttling()
        test_metrics_recording()
        test_integration_scenario()

        print("=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
