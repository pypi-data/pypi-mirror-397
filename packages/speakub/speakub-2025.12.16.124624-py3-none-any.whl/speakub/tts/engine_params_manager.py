"""
Engine Parameter Manager Module

Centralized management of TTS engine-specific parameters.
Handles parameter preparation for different TTS engines (Edge-TTS, GTTS, Nanmai).
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EngineParamsManager:
    """Manages TTS engine-specific parameter preparation and validation."""

    def __init__(self, config_manager, app):
        """
        Initialize the EngineParamsManager.

        Args:
            config_manager: Configuration manager instance for reading settings
            app: Application instance for accessing TTS volume, rate, and pitch settings
        """
        # [🔥 修改] 確保使用注入的實例
        self.config_manager = config_manager
        self.app = app

    def get_params_for_engine(self) -> dict:
        """
        Prepare TTS engine-specific parameters.

        Returns a dict of parameters suitable for the current TTS engine.
        Automatically selects parameter preparation based on configured engine.

        Returns:
            dict: Engine-specific parameters
        """
        current_engine = self.config_manager.get(
            "tts.preferred_engine", "edge-tts"
        )

        if current_engine in ("gtts", "nanmai"):
            return self._prepare_mpv_engine_params(current_engine)
        elif current_engine == "edge-tts":
            return self._prepare_edge_tts_params()
        else:
            # Fallback for unknown engines
            logger.warning(
                f"Unknown TTS engine '{current_engine}', falling back to edge-tts params"
            )
            return self._prepare_edge_tts_params()

    def _prepare_mpv_engine_params(self, engine: str) -> dict:
        """
        Prepare parameters for MPV-based engines (GTTS, Nanmai).

        MPV-based engines (GTTS and Nanmai) use direct volume and speed settings
        instead of rate/pitch/volume strings.

        Args:
            engine: Engine name ("gtts" or "nanmai")

        Returns:
            dict: Empty dict (parameters applied directly to engine instance)
        """
        # 使用已有的 config_manager 實例，而不是匯入全局函數
        # 根據當前引擎獲取對應的配置值，而不是使用全局設定
        if engine == "gtts":
            # GTTS 使用自己的配置
            volume = self.config_manager.get("gtts.volume", 1.0)
            speed = self.config_manager.get("gtts.playback_speed", 1.5)
            logger.debug(
                f"GTTS: Using engine-specific settings - volume: {volume}, speed: {speed}"
            )
        elif engine == "nanmai":
            # NanmaiTTS 使用自己的配置
            volume = self.config_manager.get("nanmai.volume", 1.0)
            speed = self.config_manager.get("nanmai.playback_speed", 0.8)
            logger.debug(
                f"NanmaiTTS: Using engine-specific settings - volume: {volume}, speed: {speed}"
            )
        else:
            # 回退到全局設定（以防萬一）
            volume = self.app.tts_volume / 100.0
            speed = self._convert_tts_rate_to_mpv_speed(self.app.tts_rate)
            logger.debug(
                f"{engine.title()}: Using global settings - volume: {volume}, speed: {speed}"
            )

        # 應用到 TTS 引擎
        self.app.tts_engine.set_speed(speed)
        self.app.tts_engine.set_volume(volume)
        return {}

    def _prepare_edge_tts_params(self) -> dict:
        """
        Prepare parameters for Edge-TTS engine.

        Edge-TTS uses string-based rate/pitch/volume parameters
        in the format "+10%", "-5%", etc.

        Returns:
            dict: Dictionary with 'rate', 'volume', and 'pitch' keys
        """
        rate = f"{self.app.tts_rate:+}%"
        volume = f"{self.app.tts_volume - 100:+}%"
        return {"rate": rate, "volume": volume, "pitch": self.app.tts_pitch}

    def _convert_tts_rate_to_mpv_speed(self, tts_rate: int) -> float:
        """
        Convert TTS rate (0-100) to MPV speed (0.5-2.0).

        Args:
            tts_rate: TTS rate value (0-100, where 50 is normal)

        Returns:
            float: MPV speed value (0.5-2.0)
        """
        # Convert from 0-100 scale to 0.5-2.0 scale
        # 50 (normal) = 1.0, 100 (fast) = 2.0, 0 (slow) = 0.5
        return 0.5 + (tts_rate / 100.0) * 1.5
