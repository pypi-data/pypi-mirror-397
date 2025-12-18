#!/usr/bin/env python3
"""
Unit tests for event_bus.py module.
"""

import asyncio
import pytest
from speakub.utils.event_bus import EventBus, SpeakUBEvents, event_bus


class TestEventBus:
    """Test cases for EventBus class."""

    def test_event_bus_initialization(self):
        """Test EventBus initialization."""
        bus = EventBus()
        assert bus._handlers == {}

    def test_subscribe_to_event(self):
        """Test subscribing to an event."""
        bus = EventBus()

        def handler(data):
            pass

        bus.subscribe("test_event", handler)
        assert "test_event" in bus._handlers
        assert handler in bus._handlers["test_event"]

    def test_subscribe_duplicate_handler(self):
        """Test that duplicate handlers are not added."""
        bus = EventBus()

        def handler(data):
            pass

        bus.subscribe("test_event", handler)
        bus.subscribe("test_event", handler)  # Try to subscribe again

        assert len(bus._handlers["test_event"]) == 1

    def test_unsubscribe_from_event(self):
        """Test unsubscribing from an event."""
        bus = EventBus()

        def handler(data):
            pass

        bus.subscribe("test_event", handler)
        assert handler in bus._handlers["test_event"]

        bus.unsubscribe("test_event", handler)
        assert handler not in bus._handlers["test_event"]

    def test_unsubscribe_nonexistent_handler(self):
        """Test unsubscribing a handler that doesn't exist."""
        bus = EventBus()

        def handler1(data):
            pass

        def handler2(data):
            pass

        bus.subscribe("test_event", handler1)

        # Try to unsubscribe a handler that was never subscribed
        bus.unsubscribe("test_event", handler2)

        # Should not raise an error and handler1 should still be there
        assert handler1 in bus._handlers["test_event"]

    def test_publish_event_no_handlers(self):
        """Test publishing an event with no handlers."""
        bus = EventBus()

        # Should not raise an error
        asyncio.run(bus.publish("nonexistent_event", {"data": "test"}))

    @pytest.mark.asyncio
    async def test_publish_event_with_sync_handler(self):
        """Test publishing an event with a synchronous handler."""
        bus = EventBus()
        received_data = None

        def sync_handler(data):
            nonlocal received_data
            received_data = data

        bus.subscribe("test_event", sync_handler)

        test_data = {"key": "value"}
        await bus.publish("test_event", test_data)

        assert received_data == test_data

    @pytest.mark.asyncio
    async def test_publish_event_with_async_handler(self):
        """Test publishing an event with an asynchronous handler."""
        bus = EventBus()
        received_data = None

        async def async_handler(data):
            nonlocal received_data
            received_data = data

        bus.subscribe("test_event", async_handler)

        test_data = {"key": "value"}
        await bus.publish("test_event", test_data)

        assert received_data == test_data

    @pytest.mark.asyncio
    async def test_publish_event_multiple_handlers(self):
        """Test publishing an event with multiple handlers."""
        bus = EventBus()
        call_count = 0

        def handler1(data):
            nonlocal call_count
            call_count += 1

        def handler2(data):
            nonlocal call_count
            call_count += 1

        bus.subscribe("test_event", handler1)
        bus.subscribe("test_event", handler2)

        await bus.publish("test_event", {"data": "test"})

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_publish_event_with_exception(self):
        """Test publishing an event where a handler raises an exception."""
        bus = EventBus()

        def good_handler(data):
            pass

        def bad_handler(data):
            raise ValueError("Test exception")

        bus.subscribe("test_event", good_handler)
        bus.subscribe("test_event", bad_handler)

        # Should not raise an exception - errors are logged but don't stop other handlers
        await bus.publish("test_event", {"data": "test"})

    def test_publish_sync_event_with_sync_handler(self):
        """Test synchronous publishing with synchronous handler."""
        bus = EventBus()
        received_data = None

        def sync_handler(data):
            nonlocal received_data
            received_data = data

        bus.subscribe("test_event", sync_handler)

        test_data = {"key": "value"}
        bus.publish_sync("test_event", test_data)

        assert received_data == test_data

    def test_publish_sync_event_with_async_handler(self):
        """Test synchronous publishing with async handler (should be skipped)."""
        bus = EventBus()
        call_count = 0

        async def async_handler(data):
            nonlocal call_count
            call_count += 1

        def sync_handler(data):
            nonlocal call_count
            call_count += 1

        bus.subscribe("test_event", async_handler)
        bus.subscribe("test_event", sync_handler)

        bus.publish_sync("test_event", {"data": "test"})

        # Only the sync handler should be called
        assert call_count == 1

    def test_publish_sync_event_no_handlers(self):
        """Test synchronous publishing with no handlers."""
        bus = EventBus()

        # Should not raise an error
        bus.publish_sync("nonexistent_event", {"data": "test"})

    def test_global_event_bus_instance(self):
        """Test that the global event_bus instance exists."""
        assert isinstance(event_bus, EventBus)

    def test_speakub_events_constants(self):
        """Test that SpeakUBEvents constants are defined."""
        assert SpeakUBEvents.CHAPTER_LOADED == "chapter_loaded"
        assert SpeakUBEvents.TTS_STATE_CHANGED == "tts_state_changed"
        assert SpeakUBEvents.APPLICATION_STARTED == "application_started"
        assert SpeakUBEvents.ERROR_OCCURRED == "error_occurred"


if __name__ == "__main__":
    pytest.main([__file__])
