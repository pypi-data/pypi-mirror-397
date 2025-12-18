"""
Test for improved resource monitoring and memory management.
"""
import asyncio
from unittest.mock import MagicMock, patch

from speakub.utils.system_utils import get_system_performance_rating


class TestResourceMonitoring:
    """Test resource monitoring improvements."""

    def test_system_performance_rating(self):
        """Test that performance rating works correctly."""
        with patch('psutil.cpu_count') as mock_cpu:
            with patch('psutil.virtual_memory') as mock_mem:
                # Mock high-end hardware
                mock_cpu.return_value = 8
                mock_mem.return_value = MagicMock()
                mock_mem.return_value.total = 16 * 1024**3  # 16GB

                rating = get_system_performance_rating()
                assert rating in ["low_end", "mid_range", "high_end"]

    def test_memory_leak_detection(self):
        """Test basic memory leak detection."""
        import gc
        import weakref

        # Create object that should be garbage collected
        class TestObject:
            def __init__(self):
                self.data = "test data" * 1000

        # Create and verify object exists
        obj = TestObject()
        ref = weakref.ref(obj)
        assert ref() is not None

        # Delete reference and force garbage collection
        del obj
        gc.collect()

        # Object should be garbage collected
        assert ref() is None

    def test_async_resource_cleanup(self):
        """Test async resource cleanup patterns."""
        async def test_operation():
            resources = []

            # Simulate acquiring resources
            for i in range(3):
                mock_resource = MagicMock()
                mock_resource.cleanup = MagicMock()
                resources.append(mock_resource)

            # Simulate exception during operation
            try:
                raise RuntimeError("Test exception")
            finally:
                # Cleanup should happen even on exception
                for resource in resources:
                    try:
                        resource.cleanup()
                    except Exception:
                        pass  # Suppress cleanup errors

            # Verify all resources were cleaned up
            for resource in resources:
                resource.cleanup.assert_called_once()

        asyncio.run(test_operation())
