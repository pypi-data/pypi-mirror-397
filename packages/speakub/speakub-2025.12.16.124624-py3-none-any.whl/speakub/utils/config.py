#!/usr/bin/env python3
"""
This module handles configuration management for the EPUB reader.
"""

import yaml
import psutil
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

# Type alias for environment value parsing results
EnvValue = Union[str, int, float, bool]

try:
    from platformdirs import user_config_dir

    PLATFORMDIRS_AVAILABLE = True
except ImportError:
    PLATFORMDIRS_AVAILABLE = False


try:
    from pydantic import BaseModel, Field, ValidationError

    PYDANTIC_AVAILABLE = True

    # Import v2 compatible features
    try:
        from pydantic import model_validator  # v2
        from pydantic.deprecated import validator  # v1 compatibility
    except ImportError:
        model_validator = None
        validator = lambda **kwargs: None

except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # Fallback
    Field = lambda **kwargs: None
    ValidationError = Exception
    model_validator = None
    validator = lambda **kwargs: None

# Set up logging
logger = logging.getLogger(__name__)


# Pydantic models for configuration validation
if PYDANTIC_AVAILABLE:
    from pydantic import confloat, conint, constr

    class TTSConfig(BaseModel):
        """TTS configuration model with proper field constraints."""

        rate: conint(ge=-100, le=100) = Field(
            default=0, description="TTS rate adjustment"
        )
        volume: conint(ge=0, le=100) = Field(
            default=100, description="TTS volume")
        pitch: constr(min_length=1) = Field(
            default="+0Hz", description="TTS pitch adjustment"
        )
        smooth_mode: bool = Field(
            default=False, description="Smooth TTS mode enabled")
        preferred_engine: constr(min_length=1) = Field(
            default="edge-tts", description="Preferred TTS engine"
        )
        smooth_synthesis_delay: confloat(gt=0) = Field(
            default=1.2, description="Synthesis delay in smooth mode"
        )
        preloading_mode: constr(min_length=1) = Field(
            default="batch", description="Preloading mode"
        )
        batch_size: conint(gt=0) = Field(
            default=5, description="Batch size for preloading"
        )
        max_queue_size: conint(gt=0) = Field(
            default=20, description="Maximum queue size for TTS operations"
        )
        dynamic_batch_adjustment: bool = Field(
            default=True, description="Enable dynamic batch size adjustment"
        )
        batch_adjustment_window: conint(gt=0) = Field(
            default=10, description="Window size for batch adjustment calculation"
        )

        model_config = {
            "validate_assignment": True,
        }

    class CacheConfig(BaseModel):
        """Cache configuration model with memory-aware defaults."""

        auto_detect_hardware: bool = Field(
            default=True, description="Auto-detect hardware for cache sizing"
        )
        chapter_cache_size: conint(gt=0) = Field(
            default=50, description="Cache size for chapter rendering"
        )
        width_cache_size: conint(gt=0) = Field(
            default=1000, description="Cache size for width calculations"
        )
        hardware_profile: constr(min_length=1) = Field(
            default="auto", description="Hardware profile override"
        )

        model_config = {
            "validate_assignment": True,
        }

    class NetworkConfig(BaseModel):
        """Network configuration model with connection validation."""

        recovery_timeout_minutes: conint(gt=0) = Field(
            default=30, description="Network recovery timeout in minutes"
        )
        recovery_check_interval: conint(gt=0) = Field(
            default=10, description="Interval between network connectivity checks"
        )
        connectivity_test_host: constr(min_length=1) = Field(
            default="8.8.8.8", description="Host to test network connectivity"
        )
        connectivity_test_port: conint(ge=1, le=65535) = Field(
            default=53, description="Port for network connectivity test"
        )
        connectivity_test_timeout: conint(gt=0) = Field(
            default=5, description="Timeout for connectivity test"
        )

        model_config = {
            "validate_assignment": True,
        }

    class SpeakUBConfig(BaseModel):
        """Main configuration model for SpeakUB."""

        language: constr(min_length=1) = Field(
            default="en", description="Interface language"
        )
        font_size: conint(ge=6, le=72) = Field(
            default=12, description="UI font size")
        reading_speed: conint(gt=0) = Field(
            default=200, description="Reading speed in words per minute"
        )
        theme: constr(min_length=1) = Field(
            default="default", description="UI theme name"
        )

        # Nested configuration sections
        tts: TTSConfig = Field(default_factory=TTSConfig)
        cache: CacheConfig = Field(default_factory=CacheConfig)
        network: NetworkConfig = Field(default_factory=NetworkConfig)

        model_config = {
            "validate_assignment": True,
        }

    def validate_config_with_pydantic(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize configuration using Pydantic models.

        Args:
            config_data: Raw configuration dictionary

        Returns:
            Validated and sanitized configuration dictionary

        Raises:
            ValidationError: If configuration contains invalid values
        """
        try:
            # Attempt to validate the entire configuration
            validated_config = SpeakUBConfig(**config_data)
            logger.debug("Configuration validation successful with Pydantic")
            return validated_config.dict()
        except ValidationError as ve:
            logger.warning(f"Pydantic validation failed: {ve}")
            # Try partial validation for known sections
            try:
                result = {}
                # Validate nested sections individually
                if "tts" in config_data:
                    tts_config = TTSConfig(**config_data["tts"])
                    result["tts"] = tts_config.dict()
                if "cache" in config_data:
                    cache_config = CacheConfig(**config_data["cache"])
                    result["cache"] = cache_config.dict()
                if "network" in config_data:
                    network_config = NetworkConfig(**config_data["network"])
                    result["network"] = network_config.dict()

                # Merge with original data for non-validated sections
                result.update(
                    {
                        k: v
                        for k, v in config_data.items()
                        if k not in ["tts", "cache", "network"]
                    }
                )
                logger.debug("Partial Pydantic validation completed")
                return result
            except Exception:
                logger.error(
                    "All Pydantic validation failed, returning original config"
                )
                return config_data
        except Exception as e:
            logger.error(f"Unexpected error in Pydantic validation: {e}")
            return config_data

else:
    # Fallback when Pydantic is not available
    def validate_config_with_pydantic(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """No-op validation when Pydantic is not available."""
        logger.warning(
            "Pydantic not available, skipping configuration validation")
        return config_data


# Define the path for the configuration file using platformdirs for cross-platform compatibility
if PLATFORMDIRS_AVAILABLE:
    CONFIG_DIR = user_config_dir("speakub", "SpeakUB")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")
else:
    # Fallback to Linux-style path if platformdirs is not available
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".config", "speakub")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.yaml")

# Define default configuration settings
DEFAULT_CONFIG: Dict[str, Any] = {
    "language": "en",
    "voice_rate": "+20%",
    "pitch": "default",
    "volume": "default",
    "tts_enabled": True,
    "reading_speed": 200,  # Words per minute
    "theme": "default",
    "font_size": 12,
    # TTS settings for centralized configuration
    "tts": {
        "rate": 0,  # TTS rate adjustment (-100 to +100)
        "volume": 100,  # TTS volume (0-100)
        "pitch": "+0Hz",  # TTS pitch adjustment
        "smooth_mode": False,  # Smooth TTS mode enabled/disabled
        "preferred_engine": "edge-tts",  # Preferred TTS engine
        # Global delay before synthesis in smooth mode (seconds) - fallback for engines without specific setting
        "smooth_synthesis_delay": 1.2,
        # Batch preloading configuration
        "preloading_mode": "batch",  # "incremental", "batch", or "predictive"
        "batch_size": 5,  # Number of items to preload in batch
        "max_queue_size": 20,  # Maximum queue size for backpressure
        "dynamic_batch_adjustment": True,  # Enable dynamic batch size adjustment
        # Number of synthesis operations to consider for adjustment
        "batch_adjustment_window": 10,
        # Optimal Cut-point Batching configuration
        "optimal_batching": {
            "enabled": True,
            "target_batch_chars": {
                "edge-tts": 60,  # Further reduced for very short segments
                "nanmai": 40,  # Further reduced for very short segments
            },
            "max_segments_per_batch": 15,  # Increased to handle more short segments
            # Allow 100% deviation from target (2x) for maximum flexibility
            "target_tolerance": 1.0,
            # Prefer fewer segments when scores are close
            "prioritize_smaller_batches": True,
            "min_batch_chars": 20,  # Reduced minimum for very short content
        },
        # Fusion v3.5 configuration
        "fusion": {
            "enabled": True,
            "char_limit": 200,  # Paragraph length threshold, used to determine batch strategy
            "max_short_items": 15,  # Maximum batch size for short sentence dense mode
            "paragraph_mode_limit": 5,  # Maximum batch size for standard paragraph mode
        },
        # Reservoir v6.0 Configuration
        "reservoir": {
            "low_watermark": 15.0,  # Seconds
            # Seconds (reduced from 60.0 to optimize memory usage)
            "high_watermark": 45.0,
        },
        # GTTS specific limits
        "volume_min": 0.0,
        "volume_max": 1.5,
        "speed_min": 0.5,
        "speed_max": 3.0,
    },
    # Edge-TTS specific settings
    "edge-tts": {
        "smooth_synthesis_delay": 1.2,  # Edge-TTS specific smooth synthesis delay
        "volume": 1.0,  # Edge-TTS volume (0.0-1.5)
        "playback_speed": 1.0,  # Edge-TTS playback speed (direct MPV value)
        # Edge-TTS specific limits
        "volume_min": 0.0,
        "volume_max": 1.5,
        "speed_min": 0.5,
        "speed_max": 3.0,
    },
    # Nanmai TTS specific settings
    "nanmai": {
        "enable_ffmpeg_transcoding": True,  # Enable/disable ffmpeg bitrate transcoding
        "default_bitrate": "64k",  # Default bitrate when transcoding is enabled
        # NanmaiTTS playback speed (UI speed, not MPV speed)
        "playback_speed": 1.0,
        "volume": 1.0,  # NanmaiTTS volume (0.0-1.5)
        # Increased from 1.0s to 1.2s for improved initial playback fluidity with network synthesis
        "smooth_synthesis_delay": 1.2,
        # Memory threshold for heavy TTS engine (MB)
        "memory_warning_threshold_mb": 400,
        # NanmaiTTS specific limits
        "volume_min": 0.0,
        "volume_max": 1.5,
        "speed_min": 0.5,
        "speed_max": 3.0,
    },
    # GTTS specific settings
    "gtts": {
        "volume": 1.0,  # GTTS volume (0.0-1.5)
        "playback_speed": 1.5,  # GTTS playback speed (MPV speed)
        "smooth_synthesis_delay": 1.5,  # GTTS specific smooth synthesis delay
        # GTTS specific limits
        "volume_min": 0.0,
        "volume_max": 1.5,
        "speed_min": 0.5,
        "speed_max": 3.0,
    },
    # Hardware-aware cache configuration
    "cache": {
        "auto_detect_hardware": True,
        "chapter_cache_size": 50,  # Default fallback
        "width_cache_size": 1000,  # Default fallback
        "hardware_profile": "auto",  # auto, low_end, mid_range, high_end
    },
    # Network configuration
    "network": {
        "recovery_timeout_minutes": 30,  # Network recovery monitoring timeout
        "recovery_check_interval": 10,  # Seconds between connectivity checks
        "connectivity_test_host": "8.8.8.8",  # Host for connectivity testing
        "connectivity_test_port": 53,  # Port for connectivity testing
        "connectivity_test_timeout": 5,  # Timeout for connectivity test
    },
    # Retry policies for different retry scenarios
    "retry_policies": {
        "network": {  # For Edge-TTS network-level retries
            "max_attempts": 3,
            "base_delay": 2.0,
            "dns_delay": 5.0,
            "use_jitter": True,
            "jitter_range": [0.5, 1.5],
            "exponential_factor": 2.0,
        },
        "content": {  # For Integration content-level retries
            "normal_attempts": 2,
            "short_text_attempts": 4,
            "delay": 3.0,
            "use_jitter": False,
        },
    },
    # Performance monitoring configuration
    "performance": {
        "enable_monitoring": False,  # Enable performance monitoring
        "log_slow_operations": True,  # Log operations exceeding thresholds
        # Threshold for slow operations (ms)
        "slow_operation_threshold_ms": 100,
        "memory_usage_tracking": True,  # Track memory usage
        "cpu_usage_tracking": True,  # Track CPU usage
        "benchmark_enabled": False,  # Enable benchmarking mode
        "benchmark_output_file": "performance_benchmark.json",  # Benchmark output file
    },
    # EPUB security configuration
    "epub_security": {
        "max_file_size_mb": 50,  # Maximum EPUB file size in MB
        "max_uncompressed_ratio": 50,  # Maximum compression ratio
        # Minimum compression ratio (highly compressed files)
        "min_compression_ratio": 0.01,
        "max_files_in_zip": 10000,  # Maximum number of files in EPUB
        "max_path_length": 1000,  # Maximum path length
    },
    # Content renderer configuration
    "content_renderer": {
        "default_content_width": 80,  # Default content width
        "min_content_width": 20,  # Minimum content width
        "adaptive_cache_ttl": 300,  # Adaptive cache TTL in seconds
    },
}


_hardware_profile: Optional[str] = None


def detect_hardware_profile() -> str:
    """
    Detect hardware profile based on system resources.
    Uses lazy initialization to avoid running on every import.

    Returns:
        str: Hardware profile ('low_end', 'mid_range', 'high_end')
    """
    global _hardware_profile
    if _hardware_profile is None:
        _hardware_profile = _do_detect_hardware()
    return _hardware_profile


def _do_detect_hardware() -> str:
    """
    Internal function to perform actual hardware detection.
    """
    try:
        from speakub.utils.resource_monitor import get_unified_resource_monitor

        # Use unified resource monitor
        unified_monitor = get_unified_resource_monitor()
        system_info = unified_monitor.get_system_info()

        # Get system memory in GB from unified monitor
        memory_gb = system_info.get("system_memory_total_gb", 8.0)

        # Get CPU core count (this might need to be added to unified monitor)
        # For now, fall back to psutil if available
        try:
            cpu_count = psutil.cpu_count(logical=True)
        except ImportError:
            cpu_count = 4  # Fallback

        logger.debug(
            f"Hardware detection: {cpu_count} cores, {memory_gb:.1f}GB RAM")

        # Classification logic
        if (memory_gb is not None and memory_gb <= 4) or (
            cpu_count is not None and cpu_count <= 2
        ):
            return "low_end"
        elif (memory_gb is not None and memory_gb <= 8) or (
            cpu_count is not None and cpu_count <= 4
        ):
            return "mid_range"
        else:
            return "high_end"

    except Exception as e:
        logger.warning(
            f"Hardware detection failed: {e}, using mid_range as fallback")
        return "mid_range"


def get_cache_sizes_for_profile(profile: str) -> Dict[str, int]:
    """
    Get recommended cache sizes for a hardware profile.

    Args:
        profile: Hardware profile ('low_end', 'mid_range', 'high_end')

    Returns:
        Dict with chapter_cache_size and width_cache_size
    """
    profiles = {
        "low_end": {
            "chapter_cache_size": 10,  # Minimal cache for low memory
            "width_cache_size": 200,
        },
        "mid_range": {
            "chapter_cache_size": 25,  # Balanced cache
            "width_cache_size": 500,
        },
        "high_end": {
            "chapter_cache_size": 50,  # Maximum cache for performance
            "width_cache_size": 1000,
        },
    }

    return profiles.get(profile, profiles["mid_range"])


def get_adaptive_cache_config() -> Dict[str, int]:
    """
    Get adaptive cache configuration based on detected hardware.

    Returns:
        Dict with chapter_cache_size and width_cache_size
    """
    try:
        profile = detect_hardware_profile()
        cache_sizes = get_cache_sizes_for_profile(profile)
        logger.debug(
            f"Adaptive cache config for {profile} hardware: {cache_sizes}")
        return cache_sizes
    except Exception as e:
        logger.warning(
            f"Failed to get adaptive cache config: {e}, using defaults")
        return {"chapter_cache_size": 50, "width_cache_size": 1000}


def get_cache_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
    """
    Get cache configuration, either from config file or auto-detected.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        Dict with chapter_cache_size and width_cache_size
    """
    if config is None:
        config = ConfigManager().get()

    cache_config = config.get("cache", {})

    # Check if auto-detection is enabled
    if cache_config.get("auto_detect_hardware", True):
        # Use hardware detection
        adaptive_config = get_adaptive_cache_config()

        # Allow manual override
        chapter_size = cache_config.get(
            "chapter_cache_size", adaptive_config["chapter_cache_size"]
        )
        width_size = cache_config.get(
            "width_cache_size", adaptive_config["width_cache_size"]
        )

        return {"chapter_cache_size": chapter_size, "width_cache_size": width_size}
    else:
        # Use manual configuration
        return {
            "chapter_cache_size": cache_config.get("chapter_cache_size", 50),
            "width_cache_size": cache_config.get("width_cache_size", 1000),
        }


_tts_config_cache: Optional[Dict[str, Any]] = None
_config_mtime: Optional[float] = None


def get_tts_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get TTS configuration from config file.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        Dict with TTS settings (rate, volume, pitch, smooth_mode)
    """
    global _tts_config_cache, _config_mtime

    if config is None:
        config_path = Path(CONFIG_FILE)
        if config_path.exists():
            current_mtime = config_path.stat().st_mtime
            if _tts_config_cache is None or current_mtime != _config_mtime:
                config = ConfigManager().get()
                _config_mtime = current_mtime
                _tts_config_cache = config.get("tts", {})
            else:
                config = {"tts": _tts_config_cache}
        else:
            config = ConfigManager().get()

    tts_config = config.get("tts", {})
    default_tts = DEFAULT_CONFIG["tts"]

    # Merge with defaults to ensure all keys are present
    merged_tts = default_tts.copy()
    merged_tts.update(tts_config)

    return merged_tts


def save_tts_config(tts_config: Dict[str, Any]) -> None:
    """
    Save TTS configuration to config file.

    Args:
        tts_config: TTS configuration dictionary to save
    """
    try:
        config = ConfigManager().get()
        config["tts"] = tts_config
        save_config(config)
        logger.debug("TTS configuration saved")
    except Exception as e:
        logger.error(f"Error saving TTS configuration: {e}")


def get_current_tts_config_summary() -> str:
    """
    Get a summary string of current TTS configuration for debugging.

    Returns:
        str: Formatted string with preferred_engine and current_voice
    """
    config_mgr = ConfigManager()
    preferred_engine = config_mgr.get("tts.preferred_engine", "edge-tts")
    current_voice = config_mgr.get(
        f"{preferred_engine}.default_voice", "unknown")
    return f"preferred_engine={preferred_engine}, current_voice={current_voice}"


def validate_tts_config(tts_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and sanitize TTS configuration values.

    Args:
        tts_config: TTS configuration to validate

    Returns:
        Validated TTS configuration with sanitized values
    """
    validated = {}

    # Validate rate (-100 to +100)
    rate = tts_config.get("rate", 0)
    validated["rate"] = max(-100, min(100, rate))

    # Validate volume (0 to 100)
    volume = tts_config.get("volume", 100)
    validated["volume"] = max(0, min(100, volume))

    # Validate pitch (string format like "+0Hz", "-10Hz", etc.)
    pitch = tts_config.get("pitch", "+0Hz")
    if isinstance(pitch, str) and pitch.endswith("Hz"):
        try:
            # Extract numeric part
            pitch_value = int(pitch[:-2])
            # Clamp to reasonable range (-50 to +50)
            pitch_value = max(-50, min(50, pitch_value))
            validated["pitch"] = f"{pitch_value:+}Hz"
        except ValueError:
            validated["pitch"] = "+0Hz"
    else:
        validated["pitch"] = "+0Hz"

    # Validate smooth_mode (boolean)
    validated["smooth_mode"] = bool(tts_config.get("smooth_mode", False))

    return validated


def get_smooth_synthesis_delay(
    engine_name: str, config: Optional[Dict[str, Any]] = None
) -> float:
    """
    Get smooth synthesis delay for a specific TTS engine.

    Priority order:
    1. Engine-specific setting (e.g., "nanmai.smooth_synthesis_delay")
    2. Global TTS setting ("tts.smooth_synthesis_delay")
    3. Default value (1.2)

    Args:
        engine_name: Name of the TTS engine ('edge-tts', 'nanmai', 'gtts')
        config: Configuration dictionary (if None, loads from file)

    Returns:
        Smooth synthesis delay in seconds
    """
    if config is None:
        config = ConfigManager().get()

    # Try engine-specific setting first
    engine_config = config.get(engine_name, {})
    if "smooth_synthesis_delay" in engine_config:
        return float(engine_config["smooth_synthesis_delay"])

    # Fall back to global TTS setting
    tts_config = config.get("tts", {})
    if "smooth_synthesis_delay" in tts_config:
        return float(tts_config["smooth_synthesis_delay"])

    # Fall back to default
    return 1.2


def get_network_config(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Get network configuration from config file.

    Args:
        config: Configuration dictionary (if None, loads from file)

    Returns:
        Dict with network settings
    """
    if config is None:
        config = ConfigManager().get()

    network_config = config.get("network", {})
    default_network = DEFAULT_CONFIG["network"]

    # Merge with defaults to ensure all keys are present
    merged_network = default_network.copy()
    merged_network.update(network_config)

    return merged_network


# Define the path for the pronunciation corrections file
CORRECTIONS_FILE = os.path.join(CONFIG_DIR, "corrections.json")


def save_pronunciation_corrections(corrections: Dict[str, str]) -> None:
    """
    Save pronunciation corrections to JSON file.

    Args:
        corrections: Corrections dictionary to save
    """
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)

        # If corrections is empty, create file with instructions and examples
        if not corrections:
            instructions_content = {
                "_comment": "Chinese Pronunciation Corrections Configuration",
                "_instructions": (
                    "Add your correction rules below in format: "
                    "'original': 'corrected'"
                ),
                "_examples": {"生長": "生掌", "長": "常"},
            }
            with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(instructions_content, f,
                          indent=4, ensure_ascii=False)
        else:
            with open(CORRECTIONS_FILE, "w", encoding="utf-8") as f:
                json.dump(corrections, f, indent=4, ensure_ascii=False)

        logger.debug(f"Pronunciation corrections saved to {CORRECTIONS_FILE}")
    except IOError as e:
        logger.error(f"Error saving pronunciation corrections file: {e}")


def load_pronunciation_corrections() -> Dict[str, str]:
    """
    Load pronunciation corrections from external JSON file.
    The file should be a JSON object (dictionary) with "original": "correction" format.
    If the file doesn't exist, creates an empty one for user customization.

    Returns:
        Dict[str, str]: Corrections dictionary.
    """
    if not os.path.exists(CORRECTIONS_FILE):
        logger.debug(
            "Corrections file not found. Skipping pronunciation corrections.")
        return {}

    try:
        with open(CORRECTIONS_FILE, "r", encoding="utf-8") as f:
            corrections = json.load(f)
            if not isinstance(corrections, dict):
                logger.warning(
                    f"'{CORRECTIONS_FILE}' root element is not a JSON object (dict), "
                    "ignored."
                )
                return {}

            # Validate content is string: string, exclude instruction keys
            validated_corrections = {
                k: v
                for k, v in corrections.items()
                if isinstance(k, str) and isinstance(v, str) and not k.startswith("_")
            }

            logger.debug(
                "Successfully loaded "
                f"{len(validated_corrections)} pronunciation correction "
                f"rules from '{CORRECTIONS_FILE}'."
            )
            return validated_corrections

    except (IOError, json.JSONDecodeError) as e:
        logger.error(f"Error reading or parsing '{CORRECTIONS_FILE}': {e}")
        return {}


class ConfigManager:
    """
    Centralized configuration manager with hierarchical override system.
    Implemented as a Singleton to prevent redundant disk I/O.

    Override priority (highest to lowest):
    1. Runtime overrides (set via set_override())
    2. Environment variables (SPEAKUB_*)
    3. Configuration file (~/.config/speakub/config.json)
    4. Default values
    """

    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._overrides: Dict[str, Any] = {}
        self._config_cache: Optional[Dict[str, Any]] = None
        self._config_mtime: Optional[float] = None
        self._initialized = True
        logger.debug("ConfigManager singleton initialized")

    def _load_config_with_hierarchy(self) -> Dict[str, Any]:
        """
        Load configuration with hierarchical override system.
        Supports automatic migration from JSON to YAML format.

        Returns:
            Dict[str, Any]: Merged configuration dictionary
        """
        # Start with defaults
        config = DEFAULT_CONFIG.copy()

        # Handle automatic migration from JSON to YAML
        config_path = Path(CONFIG_FILE)
        old_config_path = Path(CONFIG_FILE.replace(".yaml", ".json"))

        # Check if migration is needed
        if not config_path.exists() and old_config_path.exists():
            logger.info(
                "Detected existing JSON config file. Migrating to YAML format..."
            )
            try:
                with open(old_config_path, "r", encoding="utf-8") as f:
                    old_config = json.load(f)

                # Create ordered config preserving all content
                ordered_keys = _get_ordered_config_keys()
                ordered_config = {}
                for key in ordered_keys:
                    if key in old_config:
                        ordered_config[key] = old_config[key]

                for key, value in old_config.items():
                    if key not in ordered_config:
                        ordered_config[key] = value

                # Save as YAML
                config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(config_path, "w", encoding="utf-8") as f:
                    yaml.dump(
                        ordered_config, f, indent=4, allow_unicode=True, sort_keys=False
                    )

                # Backup original JSON file
                backup_path = old_config_path.with_suffix(".json.bak")
                old_config_path.rename(backup_path)
                logger.info(
                    f"Configuration migrated from JSON to YAML. Original file backed up as {backup_path}"
                )

            except (IOError, json.JSONDecodeError) as e:
                logger.error(f"Failed to migrate config file: {e}")

        # Load from YAML file if exists
        if config_path.exists():
            try:
                current_mtime = config_path.stat().st_mtime
                if self._config_cache is None or self._config_mtime != current_mtime:
                    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                        file_config = yaml.safe_load(f)
                    self._config_cache = file_config
                    self._config_mtime = current_mtime
                else:
                    file_config = self._config_cache

                # Deep merge file config into defaults
                self._deep_update(config, file_config)
            except (IOError, yaml.YAMLError) as e:
                logger.warning(f"Failed to load YAML config file: {e}")

        # Apply environment variable overrides
        self._apply_env_overrides(config)

        # Apply runtime overrides (highest priority)
        self._deep_update(config, self._overrides)

        return config

    def _apply_env_overrides(self, config: Dict[str, Any]) -> None:
        """
        Apply environment variable overrides to configuration.

        Environment variables should be prefixed with SPEAKUB_ and use
        dot notation for nested keys, e.g.:
        SPEAKUB_TTS_RATE=10
        SPEAKUB_TTS_VOLUME=80
        SPEAKUB_FONT_SIZE=14

        Args:
            config: Configuration dictionary to update
        """
        prefix = "SPEAKUB_"

        for env_key, env_value in os.environ.items():
            if not env_key.startswith(prefix):
                continue

            # Remove prefix and convert to lowercase with underscores
            config_key = env_key[len(prefix):].lower()

            # Convert underscores to dots for nested access
            config_key = config_key.replace("_", ".")

            # Parse value (try int, float, bool, otherwise string)
            parsed_value = self._parse_env_value(env_value)

            # Set nested value
            self._set_nested_value(config, config_key, parsed_value)

    def _parse_env_value(self, value: str) -> EnvValue:
        """
        Parse environment variable value to appropriate type.

        Args:
            value: String value from environment

        Returns:
            Parsed value
        """
        # Try boolean
        if value.lower() in ("true", "false"):
            return value.lower() == "true"

        # Try int
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value

    def _set_nested_value(
        self, config: Dict[str, Any], key_path: str, value: Any
    ) -> None:
        """
        Set a value in nested dictionary using dot notation.

        Args:
            config: Configuration dictionary
            key_path: Dot-separated path (e.g., "tts.rate")
            value: Value to set
        """
        keys = key_path.split(".")
        current = config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current or not isinstance(current[key], dict):
                current[key] = {}
            current = current[key]

        # Set the final value
        current[keys[-1]] = value

    def _deep_update(self, base: Dict[str, Any], update: Any) -> None:
        """
        Recursively update a dictionary with another dictionary.

        Args:
            base: Base dictionary to update
            update: Dictionary with updates (or None to skip)
        """
        if update is None or not isinstance(update, dict):
            return

        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value

    def get(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Get configuration value.

        Args:
            key: Dot-separated key path (e.g., "tts.rate"). If None, return full config.
            default: Default value if key not found

        Returns:
            Configuration value
        """
        config = self._load_config_with_hierarchy()

        if key is None:
            return config

        # Navigate nested dictionary
        keys = key.split(".")
        current = config

        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set_override(self, key: str, value: Any) -> None:
        """
        Set a runtime override (highest priority).

        Args:
            key: Dot-separated key path
            value: Value to set
        """
        self._set_nested_value(self._overrides, key, value)
        logger.debug(f"Runtime override set: {key} = {value}")

    def clear_override(self, key: str) -> None:
        """
        Clear a runtime override.

        Args:
            key: Dot-separated key path
        """
        keys = key.split(".")
        current = self._overrides

        try:
            for k in keys[:-1]:
                current = current[k]
            del current[keys[-1]]
            logger.debug(f"Runtime override cleared: {key}")
        except KeyError:
            pass

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value and persist it to file.

        Args:
            key: Dot-separated key path (e.g., "tts.rate")
            value: Value to set
        """
        # First update the runtime override
        self.set_override(key, value)

        # Then save to file (including this change)
        self.save_to_file()

    def save_to_file(self) -> None:
        """
        Save current configuration (without runtime overrides) to file.
        """
        config = self._load_config_with_hierarchy()

        # Remove runtime overrides for saving, but include them in the config
        # We need to save the effective configuration as it stands
        config_file = config.copy()

        # Ensure config directory exists
        config_path = Path(CONFIG_FILE)
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Save current effective configuration
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                yaml.dump(config_file, f, indent=4,
                          allow_unicode=True, sort_keys=False)
            logger.debug(f"Configuration saved to {CONFIG_FILE}")
            # Clear cache to force reload on next access
            self._config_cache = None
            self._config_mtime = None
        except IOError as e:
            logger.error(f"Error saving configuration file: {e}")

    def reload(self) -> None:
        """
        Force reload configuration from disk.
        """
        self._config_cache = None
        self._config_mtime = None
        logger.debug("Configuration reloaded from disk")


# ALL get_config() functions have been removed.
# Use ConfigManager class directly for all configuration access.


# Removed deprecated load_config() function as recommended in feasibility analysis
# Use ConfigManager class directly instead


def _get_ordered_config_keys() -> list:
    """Get the preferred order of configuration keys."""
    return [
        "language",
        "voice_rate",
        "pitch",
        "volume",
        "tts_enabled",
        "reading_speed",
        "theme",
        "font_size",
        "tts",
        "edge-tts",
        "nanmai",
        "gtts",
        "cache",
        "network",
        "performance",
        "epub_security",
        "content_renderer",
    ]


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the config manager.
    This is a backward compatibility wrapper around ConfigManager().get().

    Returns:
        Dict[str, Any]: The loaded configuration dictionary
    """
    return ConfigManager().get()


def save_config(config: Dict[str, Any]) -> None:
    """Save configuration to YAML file."""
    try:
        # Ensure TTS section is always present
        if "tts" not in config:
            config["tts"] = DEFAULT_CONFIG["tts"].copy()

        # Create ordered config by reordering keys to match DEFAULT_CONFIG order
        ordered_config = {}
        ordered_keys = _get_ordered_config_keys()

        # First add keys in preferred order
        for key in ordered_keys:
            if key in config:
                ordered_config[key] = config[key]

        # Then add any remaining keys that weren't in the preferred order
        for key, value in config.items():
            if key not in ordered_config:
                ordered_config[key] = value

        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            yaml.dump(ordered_config, f, indent=4,
                      allow_unicode=True, sort_keys=False)
        logger.debug(f"Configuration saved to {CONFIG_FILE}")
        # Note: Cache invalidation is handled by the ConfigManager instances themselves
    except IOError as e:
        logger.error(f"Error saving configuration file: {e}")


# Example usage removed due to deprecated load_config function
# Use ConfigManager class directly instead
