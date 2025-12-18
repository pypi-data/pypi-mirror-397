# speakub/tts/fusion_reservoir/__init__.py
"""
Fusion Reservoir System v7.0 - Unified Intelligent Batching &
Time-based Controller

A comprehensive TTS optimization system that integrates:
1. Fusion Batching Strategy v3.5 - Intelligent content-aware batching
2. Reservoir Controller v7.0 - Lightweight time-based buffer management

Key improvements:
- Intelligent batching with chapter boundary protection
- Time-based buffer management instead of item count
- Engine-aware parameter optimization
- Unified architecture for better maintainability

Components:
- FusionBatchingStrategy: Content-aware batch selection with chapter integrity
- SimpleReservoirController: Lightweight time-based watermark controller
"""

from .controller import SimpleReservoirController
from .batching_strategy import FusionBatchingStrategy, BatchDecisionMonitor

# Backward compatibility aliases
ReservoirController = SimpleReservoirController

__version__ = "7.0"
__all__ = [
    "FusionBatchingStrategy",
    "BatchDecisionMonitor",
    "SimpleReservoirController",
    "ReservoirController",  # Backward compatibility
]

# Version info for the Fusion Reservoir system
FUSION_RESERVOIR_VERSION = "7.0"
FUSION_RESERVOIR_COMPONENTS = [
    "fusion_batching_strategy",
    "batch_decision_monitor",
    "simple_reservoir_controller",
]
