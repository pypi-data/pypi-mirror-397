#!/usr/bin/env python3
"""
Unit tests for PlaylistManager pointer-driven batch selection v5.0 Reservoir.
Tests pointer initialization, advancement, and CPU optimization.
"""

import asyncio
import pytest
from unittest.mock import Mock, MagicMock, AsyncMock

from speakub.tts.playlist_manager import PlaylistManager
from speakub.utils.config import ConfigManager


class MockTTSIntegration:
    """Mock TTS Integration for testing."""

    def __init__(self):
        self.app = Mock()
        self.app.tts_engine = Mock()
        self.app.tts_smooth_mode = True
        self.app.tts_rate = 0
        self.app.tts_volume = 50
        self.app.tts_pitch = 1.0
        self.tts_lock = asyncio.Lock()
        self.tts_stop_requested = asyncio.Event()
        self.tts_audio_ready = asyncio.Event()


@pytest.fixture
def mock_config():
    """Mock ConfigManager for testing."""
    config = ConfigManager()
    config.get = Mock(side_effect=lambda key, default=None: {
        "tts.fusion.enabled": True,
        "tts.batch_size": 5,
        "tts.max_queue_size": 20,
        "tts.dynamic_batch_adjustment": False,
        "tts.batch_adjustment_window": 10,
        "tts.smooth_mode": True,
        "tts.preferred_engine": "edge-tts",
        "tts.fusion.char_limit": 200,
        "tts.fusion.max_short_items": 15,
    }.get(key, default))
    return config


@pytest.fixture
async def playlist_manager(mock_config):
    """Create a PlaylistManager instance for testing."""
    integration = MockTTSIntegration()
    manager = PlaylistManager(integration, mock_config)

    # Mock event bus
    manager._event_bus = Mock()
    manager._event_bus.subscribe = Mock()

    # Mock predictive controller
    manager._predictive_controller = Mock()
    manager._predictive_controller.get_performance_stats = Mock(return_value={
        "monitor_active": True,
        "state": "monitoring"
    })

    yield manager

    # Cleanup
    await manager._cancel_batch_preload_task()


class TestPlaylistManagerPointer:
    """Test pointer-driven batch selection functionality."""

    @pytest.mark.asyncio
    async def test_pointer_initialization(self, playlist_manager):
        """Test pointer initialization on empty playlist."""
        assert playlist_manager._next_synthesis_idx is None

        # Test with empty playlist
        playlist_manager.playlist = []
        assert not playlist_manager._has_synthesis_work_remaining()
        assert playlist_manager._next_synthesis_idx is None

    @pytest.mark.asyncio
    async def test_pointer_finds_first_unsynthesized_item(self, playlist_manager):
        """Test pointer correctly finds first unsynthesized item."""
        # Setup playlist with synthesized and unsynthesized items
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),  # Synthesized
            ("Text 1", 1234567890, "audio_data_1"),  # Synthesized
            ("Text 2", 1234567890),                   # Unsynthesized
            ("Text 3", 1234567890, "audio_data_3"),  # Synthesized
        ]

        playlist_manager._find_next_synthesis_position()
        assert playlist_manager._next_synthesis_idx == 2

    @pytest.mark.asyncio
    async def test_pointer_skips_filtered_content(self, playlist_manager):
        """Test pointer skips over filtered content."""
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),          # Synthesized
            ("Text 1", 1234567890, b"CONTENT_FILTERED"),     # Filtered
            ("Text 2", 1234567890),                           # Unsynthesized
        ]

        playlist_manager._find_next_synthesis_position()
        assert playlist_manager._next_synthesis_idx == 2

    @pytest.mark.asyncio
    async def test_pointer_update_after_batch_selection(self, playlist_manager, mock_config):
        """Test pointer advancement after batch selection."""
        # Setup playlist with consecutive unsynthesized items
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),  # Synthesized
            ("Text 1", 1234567890),                   # Unsynthesized
            ("Text 2", 1234567890),                   # Unsynthesized
            ("Text 3", 1234567890),                   # Unsynthesized
            ("Text 4", 1234567890, "audio_data_4"),  # Synthesized
        ]

        # Mock batching strategy to select items at indices 1 and 2
        mock_strategy = Mock()
        mock_strategy.select_batch = Mock(return_value=(
            [(1, "Text 1"), (2, "Text 2")], "PARAGRAPH_MODE"
        ))
        playlist_manager.batching_strategy = mock_strategy

        # Position pointer at first unsynthesized item
        playlist_manager._next_synthesis_idx = 1

        # Call optimal batch logic
        batch = await playlist_manager._get_next_batch_optimal()

        # Verify selected items
        assert len(batch) == 2
        assert batch[0] == (1, "Text 1")
        assert batch[1] == (2, "Text 2")

        # Verify pointer advanced to position after selected batch
        assert playlist_manager._next_synthesis_idx == 3  # Next after last selected

    @pytest.mark.asyncio
    async def test_pointer_handles_end_of_playlist(self, playlist_manager):
        """Test pointer handles end of playlist scenario."""
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),  # Synthesized
            ("Text 1", 1234567890, "audio_data_1"),  # Synthesized
        ]

        playlist_manager._find_next_synthesis_position()
        assert playlist_manager._next_synthesis_idx is None

        assert not playlist_manager._has_synthesis_work_remaining()

    @pytest.mark.asyncio
    async def test_pointer_reset_on_playlist_reset(self, playlist_manager):
        """Test pointer reset when playlist is reset."""
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),
            ("Text 1", 1234567890),  # Unsynthesized
        ]
        playlist_manager._next_synthesis_idx = 1

        # Reset playlist
        playlist_manager.reset()
        assert playlist_manager._next_synthesis_idx is None

    @pytest.mark.asyncio
    async def test_pointer_invalidation_on_seek(self, playlist_manager):
        """Test pointer invalidation on seek operations."""
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),
            ("Text 1", 1234567890),
            ("Text 2", 1234567890),
            ("Text 3", 1234567890),
        ]

        # Set current index and initialize pointer
        playlist_manager.current_index = 0
        playlist_manager._next_synthesis_idx = 1

        # Small forward seek (should not invalidate)
        playlist_manager.set_current_index(1)
        assert playlist_manager._next_synthesis_idx == 1

        # Large jump (should invalidate pointer)
        playlist_manager.set_current_index(1)  # Set back to test jump
        playlist_manager.set_current_index(3)  # Jump 2 positions
        assert playlist_manager._next_synthesis_idx is None

    @pytest.mark.asyncio
    async def test_cpu_optimization_no_empty_scans(self, playlist_manager, mock_config):
        """Test that pointer eliminates unnecessary scanning."""
        # Setup scenario where old logic would scan extensively
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),  # Many synthesized items
        ] * 10 + [
            # First unsynthesized at index 10
            ("Text 10", 1234567890),
            ("Text 11", 1234567890),                 # Next unsynthesized
        ]

        # Initialize pointer - should find index 10 immediately
        playlist_manager._find_next_synthesis_position()
        assert playlist_manager._next_synthesis_idx == 10

        # Mock batching strategy to select first item
        mock_strategy = Mock()
        mock_strategy.select_batch = Mock(return_value=(
            [(10, "Text 10")], "SINGLE_ITEM_MODE"
        ))
        playlist_manager.batching_strategy = mock_strategy

        # Get batch - should start from pointer position without scanning previous items
        batch = await playlist_manager._get_next_batch_optimal()

        assert len(batch) == 1
        assert batch[0] == (10, "Text 10")
        assert playlist_manager._next_synthesis_idx == 11

    @pytest.mark.asyncio
    # Legacy test updated - now tests fallback behavior when Fusion is disabled
    async def test_fallback_to_legacy_with_pointer(self, playlist_manager, mock_config):
        """Test fallback behavior when Fusion is disabled (returns empty list)."""
        # Disable Fusion
        mock_config.get = Mock(side_effect=lambda key, default=None: {
            "tts.fusion.enabled": False,
            "tts.batch_size": 2,
            "tts.max_queue_size": 20,
        }.get(key, default))

        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),  # Synthesized
            ("Text 1", 1234567890),                   # Unsynthesized
            ("Text 2", 1234567890),                   # Unsynthesized
            ("Text 3", 1234567890, "audio_data_3"),  # Synthesized
        ]

        # Set pointer to position 1
        playlist_manager._next_synthesis_idx = 1

        # Get batch using legacy with pointer
        batch = await playlist_manager._get_next_batch_optimal()

        # Should still use pointer and collect from there
        assert len(batch) == 2  # Limited by batch_size
        assert batch[0] == (1, "Text 1")
        assert batch[1] == (2, "Text 2")

        # Pointer should advance
        assert playlist_manager._next_synthesis_idx == 3

    @pytest.mark.asyncio
    async def test_queue_backpressure_stops_preload(self, playlist_manager):
        """Test that backpressure prevents preload when queue is full."""
        # Fill the playback queue beyond limit
        for _ in range(25):  # Over max_queue_size of 20
            await playlist_manager._playback_queue.put(None)

        # Setup playlist with unsynthesized items
        playlist_manager.playlist = [
            ("Text 0", 1234567890, "audio_data_0"),
            ("Text 1", 1234567890),  # Unsynthesized at index 1
        ]
        playlist_manager._next_synthesis_idx = 1

        # Should not preload due to full queue
        batch = await playlist_manager._get_next_batch_optimal()
        assert len(batch) == 0
