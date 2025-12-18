"""
Core functionality for SpeakUB.

Exception Classes:
------------------
All exception classes have been moved to exceptions.py for better organization
and maintainability. They are imported here for backward compatibility.

The unified exception hierarchy provides:
- SpeakUBException: Base exception with logging support
- Specific exceptions for different error types (Parsing, Configuration, Security, etc.)
- Backward compatibility aliases for existing code

Resource Management:
-------------------
Resource monitoring and management is handled through the unified interface
in utils/resource_monitor.py, which combines memory monitoring, file cleanup,
and performance tracking from multiple components.
"""

# Exception classes have been moved to exceptions.py for better organization
from speakub.core.exceptions import (  # noqa: F401
    TTSError,
)
