#!/usr/bin/env python3
"""
Event-driven architecture for SpeakUB

Provides a centralized event bus for decoupling application components.
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class EventBus:
    """
    Centralized event bus for decoupling application modules.

    Example usage:
        # Publish an event
        event_bus.publish("chapter_loaded",
                         {"chapter_id": "chap1", "title": "Introduction"})

        # Subscribe to an event
        event_bus.subscribe("chapter_loaded", handle_chapter_loaded)

        async def handle_chapter_loaded(event_data: Dict[str, Any]):
            chapter_id = event_data.get("chapter_id")
            print(f"Chapter {chapter_id} loaded")
    """

    def __init__(self):
        """Initialize the event bus."""
        self._handlers: Dict[str, List[Callable]] = {}  # event -> [handlers]

    def subscribe(self, event: str, handler: Callable) -> None:
        """
        Subscribe to an event.

        Args:
            event: Event name to subscribe to
            handler: Async or sync callable that handles the event
        """
        if event not in self._handlers:
            self._handlers[event] = []

        # Prevent duplicate subscriptions
        if handler not in self._handlers[event]:
            self._handlers[event].append(handler)
            logger.debug(f"Subscribed handler {handler.__name__} to event '{event}'")

    def unsubscribe(self, event: str, handler: Callable) -> None:
        """
        Unsubscribe from an event.

        Args:
            event: Event name to unsubscribe from
            handler: Handler to remove
        """
        if event in self._handlers:
            if handler in self._handlers[event]:
                self._handlers[event].remove(handler)
                logger.debug(
                    f"Unsubscribed handler {handler.__name__} from event '{event}'"
                )

    async def publish(self, event: str, data: Any = None) -> None:
        """
        Publish an event to all subscribers.

        Args:
            event: Event name to publish
            data: Optional data to pass to handlers
        """
        if event in self._handlers and self._handlers[event]:
            tasks = []
            for handler in self._handlers[event]:
                try:
                    # Support both sync and async handlers
                    if asyncio.iscoroutinefunction(handler):
                        tasks.append(handler(data))
                    else:
                        # Run sync handlers in a thread pool
                        loop = asyncio.get_event_loop()
                        tasks.append(loop.run_in_executor(None, handler, data))
                except Exception as e:
                    logger.error(
                        f"Error executing handler {handler.__name__} for event '{event}': {e}"
                    )

            # Await all handlers
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
                logger.debug(f"Published event '{event}' to {len(tasks)} handlers")
        else:
            logger.debug(f"No handlers registered for event '{event}'")

    def publish_sync(self, event: str, data: Any = None) -> None:
        """
        Synchronous version of publish (useful for non-async contexts).

        Args:
            event: Event name to publish
            data: Optional data to pass to handlers
        """
        if event in self._handlers and self._handlers[event]:
            for handler in self._handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        logger.warning(
                            f"Async handler {handler.__name__} called synchronously for event '{event}'"
                        )
                        continue  # Skip async handlers in sync mode
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(
                        f"Error executing handler {handler.__name__} for event '{event}': {e}"
                    )

            logger.debug(f"Published event '{event}' synchronously to handlers")


# Global instance
event_bus = EventBus()


# Common event names used in SpeakUB
class SpeakUBEvents:
    """Common event names for SpeakUB application."""

    # EPUB related
    CHAPTER_LOADED = "chapter_loaded"
    TOC_UPDATED = "toc_updated"
    EPUB_LOADED = "epub_loaded"

    # TTS related
    TTS_STATE_CHANGED = "tts_state_changed"
    TTS_VOICE_CHANGED = "tts_voice_changed"
    TTS_ENGINE_CHANGED = "tts_engine_changed"
    TTS_PROGRESS_UPDATED = "tts_progress_updated"

    # UI related
    PANEL_FOCUS_CHANGED = "panel_focus_changed"
    VOICE_PANEL_TOGGLED = "voice_panel_toggled"

    # System related
    APPLICATION_STARTED = "application_started"
    APPLICATION_STOPPED = "application_stopped"
    ERROR_OCCURRED = "error_occurred"
