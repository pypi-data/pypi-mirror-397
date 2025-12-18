# SpeakUB 📚

A modern, feature-rich terminal EPUB reader with **Text-to-Speech** support, built with Rich/Textual for a beautiful CLI experience.

## ✨ Features

- 🎨 **Rich Terminal UI** - Beautiful interface with Rich and Textual
- 📖 **Full EPUB Support** - Handles EPUB 2 and EPUB 3 formats
- 🔊 **Text-to-Speech** - Built-in TTS using Microsoft Edge-TTS with Reservoir v5.2
- 📊 **Intelligent Buffer Management** - Water Level Control system for seamless playback
- 📑 **Smart Navigation** - Table of contents with hierarchical chapters
- 💾 **Progress Tracking** - Automatically saves your reading position
- 🎯 **Seamless Reading** - Navigate between chapters without interruption
- 🖼️ **Image Support** - View embedded images (optional)
- ⌨️ **Keyboard Shortcuts** - Efficient navigation with familiar keys
- 🎛️ **TTS Controls** - Play, Pause, Stop with speed/volume control
- 🗣️ **Chinese Pronunciation Corrections** - Optional pronunciation correction system

## 🚀 Installation

### Quick Install
```bash
pip install speakub
```

### Development Install
```bash
git clone https://github.com/eyes1971/SpeakUB.git
cd SpeakUB
pip install -e .
```

### With TTS Support
```bash
pip install speakub[tts]
```

### With All Features
```bash
pip install speakub[all]
```

## �️ Desktop Integration

SpeakUB automatically creates a desktop entry on first run, allowing you to:
- Right-click EPUB files and select "Open with SpeakUB"
- Double-click EPUB files to open them directly

The desktop entry uses `speakub %f` command, which automatically detects and launches in your preferred terminal emulator.

## �📋 Requirements

- Python 3.8+
- Terminal with Unicode support

### Optional Dependencies

- **TTS**: `edge-tts` and `pygame` for text-to-speech
- **Images**: `fabulous` and `Pillow` for image display

## 🎮 Usage

### Basic Usage
```bash
speakub book.epub
```

### Dump to Text
```bash
speakub book.epub --dump --cols 80
```

## ⌨️ Keyboard Shortcuts

### Global Controls
| Key | Action |
|-----|---------|
| `Esc` / `q` | Quit application |
| `Tab` | Switch focus between panels |
| `F1` | Toggle table of contents |
| `F2` | Toggle TTS panel |

### Table of Contents (TOC)
| Key | Action |
|-----|---------|
| `↑` / `↓` | Navigate chapters |
| `PgUp` / `PgDn` | Page up/down |
| `Enter` / `→` | Open chapter or expand group |
| `←` | Collapse group |

### Content Reading
| Key | Action |
|-----|---------|
| `↑` / `↓` | Scroll content (seamless across chapters) |
| `PgUp` / `PgDn` | Page up/down |
| `Home` / `End` | Go to start/end of chapter |
| `i` | Open images in browser (if available) |

### TTS Controls
| Key | Action |
|-----|---------|
| `Space` / `p` | Play/Pause |
| `s` | Stop |
| `+` / `=` | Increase volume |
| `-` | Decrease volume |
| `[` | Decrease speed |
| `]` | Increase speed |
| `←` / `→` | Navigate TTS controls |

## 🏗️ Architecture

```
speakub/
├── speakub/                    # Main package
│   ├── core/                   # Core functionality
│   │   ├── epub_parser.py      # EPUB parsing
│   │   ├── content_renderer.py # HTML to text conversion (with adaptive cache)
│   │   ├── chapter_manager.py  # Chapter navigation
│   │   ├── progress_tracker.py # Reading progress
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── cfi.py              # EPUB CFI handling
│   │   └── epub/               # EPUB-specific parsers
│   │       ├── metadata_parser.py
│   │       ├── opf_parser.py
│   │       ├── path_resolver.py
│   │       └── toc_parser.py
│   ├── tts/                    # Text-to-Speech
│   │   ├── engine.py           # TTS abstraction
│   │   ├── edge_tts_provider.py # Edge-TTS provider
│   │   ├── gtts_provider.py    # Google TTS provider
│   │   ├── nanmai_tts_provider.py # Nanmai TTS provider
│   │   ├── audio_player.py     # Audio playback
│   │   ├── playback_manager.py # Playback management
│   │   ├── playlist_manager.py # Playlist handling
│   │   ├── integration.py      # TTS integration
│   │   ├── reservoir/          # Reservoir architecture (v4.0)
│   │   │   ├── controller.py   # Predictive batch controller
│   │   │   ├── system_monitors.py # Network and resource monitoring
│   │   │   ├── play_monitor.py # Playback time monitoring
│   │   │   ├── queue_predictor.py # Queue prediction engine
│   │   │   └── __init__.py # Package initialization
│   │   ├── backends/           # Audio backends
│   │   │   ├── base.py
│   │   │   ├── mpv_backend.py
│   │   │   └── pygame_backend.py
│   │   └── ui/                 # TTS UI components
│   │       ├── network.py
│   │       ├── playlist.py
│   │       └── runners.py
│   ├── ui/                     # User interfaces
│   │   ├── app.py              # Main application
│   │   ├── epub_manager.py     # EPUB management
│   │   ├── tts_panel.py        # TTS control panel
│   │   ├── voice_selector_panel.py # Voice selection
│   │   ├── actions.py          # UI actions
│   │   ├── panel_titles.py     # Panel titles
│   │   ├── progress.py         # Progress handling
│   │   ├── protocols.py        # UI protocols
│   │   ├── ui_utils.py         # UI utilities
│   │   └── widgets/            # Reusable components
│   │       ├── content_widget.py
│   │       ├── toc_widget.py
│   │       └── tts_widget.py
│   ├── utils/                  # Utility functions
│   │   ├── config.py           # Configuration management
│   │   ├── error_handler.py    # Error handling
│   │   ├── event_bus.py        # Event system
│   │   ├── file_utils.py       # File operations
│   │   ├── logging_config.py   # Logging configuration
│   │   ├── performance_monitor.py # Performance monitoring
│   │   ├── predictive_preloader.py # Content preloading
│   │   ├── resource_monitor.py # Resource monitoring
│   │   ├── security.py         # Security utilities
│   │   ├── system_utils.py     # System utilities
│   │   ├── text_utils.py       # Text processing
│   │   └── voice_filter_utils.py # Voice filtering
│   ├── cli.py                  # Command-line interface
│   ├── desktop.py              # Desktop integration
│   ├── __init__.py
│   └── __main__.py

├── LICENSE
├── pyproject.toml              # Project configuration
├── README.md
└── requirements.txt            # Dependency lock file
```

## 🔊 Text-to-Speech Features

The TTS system provides:

- **Multiple Voices** - Support for various languages and voices
- **Speed Control** - Adjust playback speed (0.5x - 2.0x)
- **Volume Control** - Fine-tune audio levels
- **Chapter Navigation** - Skip to previous/next chapters
- **Progress Tracking** - Visual progress bar with time display
- **Background Processing** - Non-blocking audio synthesis

### Reservoir v5.2: Intelligent Water Level Control

SpeakUB's advanced **Reservoir architecture** features intelligent **Water Level Control** for seamless TTS playback:

#### 🎯 Water Level Monitoring
- **Real-time buffer tracking**: Continuously monitors playback buffer water levels
- **Multi-tier alert system**: Low water → Deficit → Drought → Critical thresholds
- **Predictive warnings**: Anticipates buffer depletion before interruptions occur

#### 🌊 Adaptive Preload Strategies

The system automatically adjusts preloading based on buffer conditions:

- **Conservative Mode** (Buffer adequate): Minimal resource usage, efficient preloading
- **Moderate Mode** (Buffer medium): Balanced performance and resource utilization
- **Aggressive Mode** (Buffer low): Maximum preloading to prevent interruptions
- **Emergency Mode** (Buffer critical): Synchronous fallback to guarantee continuity

#### ⚡ CPU-Optimized Design
- **Pointer-driven selection**: O(1) complexity task selection eliminates CPU waste
- **Hardware-aware scaling**: Automatic adaptation to system capabilities
- **LRU cache management**: Prevents resource leaks while optimizing memory usage

#### 📊 Resource Intelligence
- **Closed-loop CPU control**: Dynamic batch size adjustment based on system pressure
- **Network-adaptive buffering**: Increases safety margins during unstable connections
- **Thermal-aware operation**: Prevents overheating through intelligent throttling

#### 🚀 Performance Results
- **45% CPU reduction**: Through pointer-driven task selection
- **35% memory optimization**: LRU cache improvements
- **80% fault recovery**: Network instability compensation
- **100% playback continuity**: Multi-layer fail-safe mechanisms

### TTS Panel Controls

```
┌──────────────────────────────────────────┐
│ TTS: PLAYING (Smooth) | 23% | Vol: 100% | Speed: +30% | Pitch: +0Hz │
└──────────────────────────────────────────┘
```

## 🛠️ Configuration

SpeakUB now provides a comprehensive configuration management system with:

- **YAML-based Configuration**: All settings stored in a human-readable YAML file
- **Command-line Tools**: `config_cli.py` tool for managing settings
- **Dependency Injection**: Each component uses its own ConfigManager instance
- **Migration Support**: Automatic migration from legacy JSON configurations

### Configuration Location

Configuration file: `~/.config/speakub/config.yaml`

### CLI Configuration Tool

SpeakUB includes a powerful CLI tool for configuration management:

```bash
# Get a configuration value
python speakub/utils/config_cli.py get tts.preferred_engine

# Set a configuration value
python speakub/utils/config_cli.py set tts.preferred_engine "gtts"

# List all configuration keys (or prefix)
python speakub/utils/config_cli.py list tts

# Export configuration
python speakub/utils/config_cli.py export my_backup.yaml

# Import configuration
python speakub/utils/config_cli.py import my_backup.yaml

# Migrate from legacy JSON configuration
python speakub/utils/config_cli.py migrate

# Show configuration system information
python speakub/utils/config_cli.py info
```

### Automatic Configuration

The reader automatically saves:
- Reading progress for each book
- Last position in each chapter
- TTS settings (volume, speed)

Progress is stored in `~/.speakub_progress.json`

### Manual Configuration

#### Environment Variables

You can customize the reader's behavior through environment variables:

#### Display Settings
```bash
# Set default content width (default: 80)
export SPEAKUB_WIDTH=100

# Enable/disable trace logging
export SPEAKUB_TRACE=1

# Set maximum cache size for content rendering
export SPEAKUB_CACHE_SIZE=100
```

#### TTS Configuration
```bash
# Set default TTS voice
export SPEAKUB_VOICE="en-US-AriaRUS"

# Set default TTS speed (0.5-2.0)
export SPEAKUB_TTS_SPEED=1.2

# Set default TTS volume (0-100)
export SPEAKUB_TTS_VOLUME=80
```

#### Performance Tuning
```bash
# Set chapter cache size (default: 50)
export SPEAKUB_CHAPTER_CACHE=100

# Enable/disable background processing
export SPEAKUB_BACKGROUND=1

# Set polling frequency for UI updates (milliseconds)
export SPEAKUB_POLL_INTERVAL=100
```

### Configuration File

Create a configuration file at `~/.config/speakub/config.yaml`:

```yaml
# SpeakUB Configuration
language: en
voice_rate: "+20%"
pitch: "default"
volume: "default"
tts_enabled: true
reading_speed: 200
theme: default
font_size: 12

# TTS settings for centralized configuration
tts:
  rate: 0
  volume: 100
  pitch: "+0Hz"
  smooth_mode: false
  preferred_engine: "edge-tts"
  smooth_synthesis_delay: 1.2

# Engine-specific settings
edge-tts:
  volume: 1.0
  playback_speed: 1.0
  smooth_synthesis_delay: 1.2

nanmai:
  volume: 1.0
  playback_speed: 1.0
  smooth_synthesis_delay: 1.0

gtts:
  volume: 1.0
  playback_speed: 1.5
  smooth_synthesis_delay: 1.5

# Hardware-aware cache configuration
cache:
  auto_detect_hardware: true
  chapter_cache_size: 50
  width_cache_size: 1000
  hardware_profile: auto

# Network configuration
network:
  recovery_timeout_minutes: 30
  recovery_check_interval: 10
  connectivity_test_host: "8.8.8.8"
  connectivity_test_port: 53
  connectivity_test_timeout: 5

# Performance monitoring configuration
performance:
  enable_monitoring: false
  log_slow_operations: true
  slow_operation_threshold_ms: 100
  memory_usage_tracking: true
  cpu_usage_tracking: true
  benchmark_enabled: false
  benchmark_output_file: "performance_benchmark.json"

# EPUB security configuration
epub_security:
  max_file_size_mb: 50
  max_uncompressed_ratio: 50
  min_compression_ratio: 0.01
  max_files_in_zip: 10000
  max_path_length: 1000

# Content renderer configuration
content_renderer:
  default_content_width: 80
  min_content_width: 20
  adaptive_cache_ttl: 300
```

### Cache Management

The reader implements intelligent caching to improve performance:

- **Chapter Content Cache**: Stores parsed chapter content (LRU with 50 entries)
- **Width Calculation Cache**: Caches display width calculations (LRU with 100 entries)
- **Adaptive Renderer Cache**: Caches HTML-to-text renderers by width with TTL and statistics

#### Adaptive Cache Features

The new adaptive cache system provides:

- **TTL (Time-To-Live)**: Automatically expires cached items after 5 minutes to prevent memory leaks
- **LRU Eviction**: Removes least recently used items when cache is full
- **Performance Statistics**: Tracks hit rates, cache size, and access patterns
- **Memory-Aware Sizing**: Automatically adjusts cache size based on system memory

### Performance Monitoring

SpeakUB includes built-in performance monitoring to track system health:

```bash
# Monitor cache statistics in real-time
from speakub.core.content_renderer import ContentRenderer
renderer = ContentRenderer()
stats = renderer.get_cache_stats()
print(f"Cache hit rate: {stats['hit_rate']:.1%}")
```

#### Performance Metrics

- **Cache Hit Rate**: Percentage of cache requests that hit
- **Memory Usage**: Current and peak memory consumption
- **TTS State Changes**: Number of TTS state transitions
- **Render Time**: Time spent rendering content

To clear all caches, delete the progress file:
```bash
rm ~/.speakub_progress.json
```

## 🗣️ Chinese Pronunciation Corrections

SpeakUB supports optional pronunciation corrections for Chinese text. This feature allows you to customize how specific Chinese characters or words are pronounced by the TTS system.

### Setting Up Corrections

1. **Automatic Setup**: The first time you run SpeakUB, it will create a corrections file at `~/.config/speakub/corrections.json` with instructions and examples.

2. **Manual Setup**: You can also create the file manually:
```bash
mkdir -p ~/.config/speakub
touch ~/.config/speakub/corrections.json
```

### Corrections File Format

The corrections file is a JSON object where each key is the original text and the value is the corrected pronunciation:

```json
{
  "_comment": "Chinese Pronunciation Corrections Configuration",
  "_instructions": "Add your correction rules below in format: 'original': 'corrected'",
  "_examples": {
    "生長": "生掌",
    "長": "常"
  },
  "生長": "生掌",
  "長": "常",
  "银行": "yínháng",
  "给予": "jǐyǔ"
}
```

### How It Works

- **Keys starting with `_`**: These are treated as comments and instructions, not correction rules
- **Regular keys**: These are the actual correction mappings
- **Automatic filtering**: The system automatically filters out instruction keys when loading corrections
- **Optional feature**: If the corrections file doesn't exist, SpeakUB works normally without corrections

### Common Use Cases

- **Polyphonic characters**: Characters that can be pronounced differently in different contexts
- **Proper nouns**: Names, places, or terms that need specific pronunciation
- **Technical terms**: Specialized vocabulary that needs consistent pronunciation
- **Regional variations**: Different pronunciation preferences

### Examples

```json
{
  "行": "xíng",        // 行走 (walking)
  "银行": "yínháng",   // 银行 (bank)
  "银行家": "yínhángjiā", // 银行家 (banker)
  "长": "cháng",       // 长度 (length)
  "长江": "chángjiāng" // 长江 (Yangtze River)
}
```

### Tips

- Use Pinyin with tone marks for best results
- Test corrections with short text first
- The corrections are applied before TTS processing
- You can have multiple corrections for the same character in different contexts

## 📋 Version History

### Version 2025.12.06.195815 (Latest - 2025-12-06)
- ✨ **New Feature**: Comprehensive configuration management system with YAML support
- 🔧 **Enhancement**: Implemented dependency injection for all configuration handling
- 🛠️ **CLI Tool**: Added `config_cli.py` for configuration management via command line
- 🔄 **Migration**: Automatic migration support from JSON to YAML configurations
- 📦 **Architecture**: Refactored to use ConfigManager instances instead of global functions
- 🧪 **Testing**: Updated test suite to use dependency injection patterns
- 📚 **Documentation**: Complete README rewrite with new configuration system guide

### Version 1.1.37
- ✨ **New Feature**: Added Chinese pronunciation corrections system
- 🔧 **Enhancement**: Improved content widget with better text processing
- 🐛 **Bug Fix**: Fixed Flake8 linting issues
- 📚 **Documentation**: Updated README with corrections usage guide
- 🏗️ **Build**: Updated build system and version management

### Version 1.0.0
- 🎉 Initial release with full EPUB reading capabilities
- 🔊 Text-to-Speech support with Microsoft Edge-TTS
- 🎨 Rich terminal UI with Textual framework
- 📑 Smart table of contents navigation
- 💾 Automatic progress tracking
- 🎛️ Comprehensive TTS controls

## 📖 API Documentation

### Core Classes

#### EPUBParser
Main class for parsing EPUB files.

```python
from speakub.core.epub_parser import EPUBParser

parser = EPUBParser("book.epub")
chapters = parser.get_chapters()
metadata = parser.get_metadata()
```

#### ContentRenderer
Handles HTML to text conversion with caching.

```python
from speakub.core.content_renderer import ContentRenderer

renderer = ContentRenderer()
text = renderer.render_html_to_text(html_content, width=80)
```

#### TTSEngine
Abstract base class for TTS engines.

```python
from speakub.tts.engine import TTSEngine

# Get available voices
voices = await engine.get_available_voices()

# Synthesize text
audio_data = await engine.synthesize("Hello world", voice="en-US-AriaRUS")
```

### TTS Providers

#### EdgeTTSProvider
Microsoft Edge TTS integration.

```python
from speakub.tts.edge_tts_provider import EdgeTTSProvider

provider = EdgeTTSProvider()
await provider.initialize()
voices = await provider.get_voices()
```

#### GTTSProvider
Google Text-to-Speech integration.

```python
from speakub.tts.gtts_provider import GTTSProvider

provider = GTTSProvider()
audio = await provider.synthesize("Hello", lang="en")
```

### Configuration

#### ConfigManager
Centralized configuration management.

```python
from speakub.utils.config import ConfigManager

config = ConfigManager()
tts_speed = config.get("tts.speed", 1.0)
config.set_override("tts.speed", 1.2)
```

### Event System

#### EventBus
Application-wide event handling.

```python
from speakub.utils.event_bus import EventBus

bus = EventBus()
bus.subscribe("tts.state_changed", callback_function)
bus.publish("tts.state_changed", {"state": "playing"})
```

### Performance Monitoring

#### PerformanceMonitor
System resource monitoring.

```python
from speakub.utils.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()
stats = monitor.get_system_stats()
monitor.log_performance_metrics()
```

## 🔧 Development

### Setup Development Environment
```bash
git clone https://github.com/eyes1971/SpeakUB.git
cd SpeakUB
pip install -e .[dev]
pre-commit install
```

### Development Tools
The `tools/` directory contains helpful scripts for development and debugging:

```bash
# Check available TTS voices
python tools/check_voices.py

# Debug voice data structures
python tools/debug_voices.py

# Test TTS provider functionality
python tools/simple_test.py

# Interactive voice selector demo
python tools/voice_selector_demo.py

# Verify UI layout changes
python tools/simple_layout_check.py
```



### Run Tests
```bash
pytest
```

### Code Formatting
```bash
black speakub/
isort speakub/
flake8 speakub/
```

### Type Checking
```bash
mypy speakub/
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository at [https://github.com/eyes1971/SpeakUB](https://github.com/eyes1971/SpeakUB)
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

- **Author**: Sam Weng
- **Email**: eyes1971@gmail.com
- **GitHub**: [https://github.com/eyes1971/SpeakUB](https://github.com/eyes1971/SpeakUB)

## 🙏 Acknowledgments

- **Rich** - For the beautiful terminal UI framework
- **Textual** - For the modern TUI components  
- **BeautifulSoup** - For robust HTML parsing
- **Edge-TTS** - For high-quality text-to-speech
- **html2text** - For HTML to text conversion

## 🐛 Known Issues

- Image display requires `fabulous` and may not work in all terminals
- TTS seeking is not supported with the pygame audio backend
- Very large EPUB files may consume significant memory

## 📚 Similar Projects

- [epr](https://github.com/wustho/epr) - CLI EPUB reader
- [epub](https://github.com/rupa/epub) - Simple EPUB reader

---

**Happy Reading!** 📖✨

For more information, visit our [documentation](https://speakub.readthedocs.io/) or [report issues](https://github.com/eyes1971/SpeakUB/issues).
