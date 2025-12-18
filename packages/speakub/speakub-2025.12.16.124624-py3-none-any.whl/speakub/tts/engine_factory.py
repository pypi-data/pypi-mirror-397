"""
Engine Factory Module

Factory pattern for TTS engine creation and initialization.
Manages engine selection, instantiation, and configuration.
"""

import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class TTSEngineFactory:
    """Factory for creating and initializing TTS engines."""

    def __init__(self, config_manager):
        """
        Initialize the engine factory.

        Args:
            config_manager: Configuration manager instance
        """
        # [🔥 修改] 移除預設值 None，強制要求傳入
        self.config_manager = config_manager
        # Import providers lazily to avoid issues if they're not available
        self._providers = None

    def _load_providers(self):
        """Lazy load TTS providers and their availability status."""
        if self._providers is not None:
            return

        self._providers = {}

        # Try to import each provider
        try:
            from speakub.tts.engines.nanmai_tts_provider import NanmaiTTSProvider
            self._providers["nanmai"] = (True, NanmaiTTSProvider)
        except (ImportError, Exception) as e:
            logger.debug(f"NanmaiTTS not available: {e}")
            self._providers["nanmai"] = (False, None)

        try:
            from speakub.tts.engines.gtts_provider import GTTSProvider
            self._providers["gtts"] = (True, GTTSProvider)
        except (ImportError, Exception) as e:
            logger.debug(f"GTTS not available: {e}")
            self._providers["gtts"] = (False, None)

        try:
            from speakub.tts.engines.edge_tts_provider import EdgeTTSProvider
            self._providers["edge-tts"] = (True, EdgeTTSProvider)
        except (ImportError, Exception) as e:
            logger.debug(f"EdgeTTS not available: {e}")
            self._providers["edge-tts"] = (False, None)

    def select_engine(self):
        """
        Select and instantiate the appropriate TTS engine.

        First attempts to use the preferred engine from configuration,
        then falls back to any available engine.

        Returns:
            TTS engine instance, or None if no engine is available
        """
        self._load_providers()

        preferred_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts"
        )

        # Check preferred engine first
        if preferred_engine in self._providers:
            available, provider_class = self._providers[preferred_engine]
            if available and provider_class:
                try:
                    engine = provider_class(config_manager=self.config_manager)
                    logger.info(
                        f"Selected preferred engine: {preferred_engine}")
                    return engine
                except Exception as e:
                    logger.warning(
                        f"Failed to instantiate preferred engine {preferred_engine}: {e}"
                    )

        # Fallback to any available engine
        engine_order = ["edge-tts", "gtts", "nanmai"]
        for engine_name in engine_order:
            if engine_name in self._providers:
                available, provider_class = self._providers[engine_name]
                if available and provider_class:
                    try:
                        engine = provider_class(
                            config_manager=self.config_manager)
                        logger.info(
                            f"Preferred engine not available, using fallback: {engine_name}"
                        )
                        return engine
                    except Exception as e:
                        logger.warning(
                            f"Failed to instantiate fallback engine {engine_name}: {e}"
                        )

        logger.error("No TTS engine available")
        return None

    def initialize_engine(self, engine) -> bool:
        """
        Initialize TTS engine with required setup.

        Args:
            engine: The TTS engine instance to initialize

        Returns:
            bool: True if initialization succeeded, False otherwise
        """
        if not engine:
            return False

        try:
            # Start async loop if the engine supports it
            if hasattr(engine, "start_async_loop"):
                engine.start_async_loop()
                logger.debug("Started TTS engine async loop")

            # Set idle mode if supported
            if hasattr(engine, "set_idle_mode"):
                idle_mode = self.config_manager.get("tts.idle_mode", False)
                engine.set_idle_mode(idle_mode)
                logger.debug(f"Set TTS engine idle mode: {idle_mode}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            return False

    def notify_engine_switched(self, app, playlist_manager) -> None:
        """
        Notify managers about engine switch for strategy updates.

        Args:
            app: Application instance
            playlist_manager: PlaylistManager instance
        """
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts"
        )

        # Notify playlist manager about engine change
        if hasattr(playlist_manager, "notify_engine_switched"):
            playlist_manager.notify_engine_switched(current_engine)
            logger.debug(
                f"Notified playlist manager about engine switch: {current_engine}")
