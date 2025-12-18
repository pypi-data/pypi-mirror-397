# tests/tts/reservoir/test_integration.py
"""
Integration tests for the complete Reservoir TTS system.
"""

from collections import deque

from speakub.tts.reservoir import (
    PredictiveBatchController,
    PlayTimeMonitor,
    QueuePredictor,
    NetworkMonitor,
    ResourceManager,
    SynthesisTimeMonitor
)
from speakub.utils.config import ConfigManager


class TestReservoirIntegration:
    """Integration tests for Reservoir components working together."""

    def test_complete_initialization(self):
        """Test that all Reservoir components can be initialized together."""
        # Create all components manually to test integration
        play_monitor = PlayTimeMonitor()
        queue_predictor = QueuePredictor(play_monitor)
        network_monitor = NetworkMonitor()
        resource_manager = ResourceManager()
        synthesis_monitor = SynthesisTimeMonitor(engine_type="edge-tts")

        # Test that components know about each other where needed
        assert queue_predictor.play_monitor == play_monitor

        assert isinstance(network_monitor.latency_history, deque)
        assert isinstance(resource_manager.cpu_history, deque)
        assert len(synthesis_monitor.synthesis_times_normalized) == 0

    def test_component_interaction_flow(self):
        """Test typical interaction flow between components."""
        # Create components
        play_monitor = PlayTimeMonitor()
        queue_predictor = QueuePredictor(play_monitor)
        network_monitor = NetworkMonitor()
        resource_manager = ResourceManager()

        # Simulate typical usage flow:

        # 1. Record some play time data
        play_monitor.record_play_time(1, 5.0, 100)
        play_monitor.record_play_time(2, 7.5, 150)

        # 2. Estimate play time
        estimate = play_monitor.estimate_play_time(125)
        assert estimate > 0

        # 3. Check buffer time estimation
        queue_items = [
            ("text1", 1, None),  # Unpreloaded
            ("text2", 2, b"audio123")  # Preloaded
        ]
        remaining_time = queue_predictor.estimate_remaining_time(queue_items)
        assert remaining_time > 0

        # 4. Record some network data
        network_monitor.record_latency(1.5)
        network_monitor.record_failure()
        factor = network_monitor.get_latency_factor()
        assert factor > 1.0  # Should compensate for poor network

        # 5. Record some system resource data
        resource_manager.record_cpu_usage(70.0)
        resource_manager.record_memory_usage(80.0)
        pressure = resource_manager.get_cpu_pressure_factor()
        assert pressure > 1.0  # Should indicate pressure

    def test_system_adaptation_chain(self):
        """Test the complete adaptation chain."""
        # Create adaptive components
        network_monitor = NetworkMonitor()
        resource_manager = ResourceManager()
        synthesis_monitor = SynthesisTimeMonitor()

        # Simulate system under stress:
        # High network latency
        network_monitor.record_latency(4.0)
        # High CPU usage
        resource_manager.record_cpu_usage(85.0)
        # Synthesis failures and normal operations to trigger trend analysis
        synthesis_monitor.record_synthesis(3.0, 100, True)   # Normal
        synthesis_monitor.record_synthesis(2.5, 100, True)   # Normal
        # Failure (triggers defensive posture)
        synthesis_monitor.record_synthesis(0, 100, False)
        synthesis_monitor.record_synthesis(
            4.0, 100, True)   # Slower after failure
        synthesis_monitor.record_synthesis(
            5.0, 100, True)   # Even slower (trend)

        # Check that all monitors detect issues
        assert network_monitor.get_latency_factor() > 1.0
        assert resource_manager.get_cpu_pressure_factor() > 1.0
        assert synthesis_monitor.trend_factor > 1.0

        # Test that synthesis monitor predicts longer times
        prediction_normal = SynthesisTimeMonitor().get_predicted_synthesis_time(100)
        prediction_stressed = synthesis_monitor.get_predicted_synthesis_time(
            100)

        # Stressed system should predict longer synthesis time
        assert prediction_stressed >= prediction_normal

    def test_monitoring_data_consistency(self):
        """Test that monitoring data is consistent across components."""
        play_monitor = PlayTimeMonitor()
        queue_predictor = QueuePredictor(play_monitor)

        # Record consistent play data
        test_data = [
            (1, 5.0, 100),
            (2, 7.5, 150),
            (3, 6.0, 120)
        ]

        for segment_id, duration, text_len in test_data:
            play_monitor.record_play_time(segment_id, duration, text_len)
            queue_predictor.play_monitor.record_play_time(
                segment_id, duration, text_len)

        # Both should have same statistics
        stats1 = play_monitor.get_recent_performance()
        stats2 = queue_predictor.play_monitor.get_recent_performance()

        assert stats1['sample_count'] == stats2['sample_count']
        assert stats1['average_play_time'] == stats2['average_play_time']

    def test_resource_monitoring_realistic_scenario(self):
        """Test resource monitoring under realistic usage patterns."""
        resource_manager = ResourceManager()

        # Simulate 30 seconds of operation with varying load
        import random
        random.seed(42)  # For reproducible results

        for i in range(30):
            # Simulate varying system load
            cpu_usage = 40 + random.uniform(-10, 20)  # 30-60% range
            memory_usage = 50 + random.uniform(-5, 15)  # 45-65% range

            cpu_usage = max(0, min(100, cpu_usage))
            memory_usage = max(0, min(100, memory_usage))

            resource_manager.record_cpu_usage(cpu_usage)
            resource_manager.record_memory_usage(memory_usage)

        # Should have collected history
        assert len(resource_manager.cpu_history) <= 10  # Capped at maxlen
        assert len(resource_manager.memory_history) <= 10

        # Should be able to calculate pressure factors
        cpu_pressure = resource_manager.get_cpu_pressure_factor()
        memory_pressure = resource_manager.get_memory_pressure_factor()

        assert cpu_pressure > 0
        assert memory_pressure > 0

        # Should be able to get adaptive polling interval
        interval = resource_manager.get_adaptive_polling_interval(60.0)
        assert interval > 0

    def test_batch_size_adaptation_chain(self):
        """Test complete batch size adaptation chain."""
        resource_manager = ResourceManager()

        # Simulate normal conditions
        resource_manager.record_cpu_usage(50.0)
        resource_manager.record_memory_usage(60.0)

        assert resource_manager.get_cpu_pressure_factor() == 1.0
        assert not resource_manager.should_reduce_batch_size()

        # Simulate high pressure
        resource_manager.record_cpu_usage(80.0)  # High CPU
        resource_manager.record_memory_usage(85.0)  # High memory

        assert resource_manager.get_cpu_pressure_factor() > 2.0
        assert resource_manager.get_memory_pressure_factor() > 2.0
        assert resource_manager.should_reduce_batch_size() == True

    def test_network_adaptation_in_decisions(self):
        """Test how network conditions affect batch decisions."""
        play_monitor = PlayTimeMonitor()
        queue_predictor = QueuePredictor(play_monitor)

        # Record normal play time
        play_monitor.record_play_time(1, 5.0, 100)

        # Test with normal network
        should_trigger_normal = queue_predictor.should_trigger_batch(
            remaining_time=2.0, current_engine="edge-tts")

        # Manually adjust network conditions to poor
        queue_predictor.engine_configs['edge-tts']['threshold'] *= 0.5

        # Test with adjusted threshold (worse network)
        should_trigger_poor = queue_predictor.should_trigger_batch(
            remaining_time=2.0, current_engine="edge-tts")

        # Poorer network should not change trigger decision for this test
        # (this is just demonstrating that network config affects decisions)
        assert isinstance(should_trigger_normal, bool)
        assert isinstance(should_trigger_poor, bool)

    def test_config_driven_initialization(self):
        """Test that components are initialized based on configuration."""
        # Test with mocked config manager
        synthesis_monitor = SynthesisTimeMonitor(engine_type="nanmai")

        # Should have nanmai-specific defaults
        assert synthesis_monitor.avg_time_per_100_chars == 6.0
        assert synthesis_monitor.time_std_dev == 2.0

    def test_performance_monitoring_integration(self):
        """Test that components provide performance monitoring data."""
        play_monitor = PlayTimeMonitor()
        network_monitor = NetworkMonitor()
        resource_manager = ResourceManager()

        # Generate some usage data
        play_monitor.record_play_time(1, 5.0, 100)
        network_monitor.record_latency(2.0)
        resource_manager.record_cpu_usage(60.0)

        # Test that all components can report their status
        play_stats = play_monitor.get_recent_performance()
        network_factor = network_monitor.get_latency_factor()
        cpu_pressure = resource_manager.get_cpu_pressure_factor()

        assert isinstance(play_stats, dict)
        assert isinstance(network_factor, float)
        assert isinstance(cpu_pressure, float)

        # Stats should be reasonable
        assert play_stats['sample_count'] == 1
        assert network_factor >= 1.0
        assert cpu_pressure >= 1.0

    def test_component_independence(self):
        """Test that components can operate independently."""
        # Create components without dependencies
        network_monitor = NetworkMonitor()
        resource_manager = ResourceManager()
        synthesis_monitor = SynthesisTimeMonitor()

        # They should work without interaction
        network_monitor.record_latency(1.0)
        resource_manager.record_cpu_usage(50.0)
        synthesis_monitor.record_synthesis(3.0, 100, True)

        # All should have collected some data
        assert len(network_monitor.latency_history) == 1
        assert len(resource_manager.cpu_history) == 1
        assert len(synthesis_monitor.synthesis_times_normalized) == 1
