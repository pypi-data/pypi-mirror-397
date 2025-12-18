#!/usr/bin/env python3
"""
Command-line tool for configuration management.
Enhanced with batch operations, validation, and better error handling.
Replaces direct Python calls in deployment scripts.
"""

from speakub.utils.config import ConfigManager
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Add the parent directory to Python path
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> None:
    """Main command-line interface for configuration operations."""
    parser = argparse.ArgumentParser(
        description="SpeakUB Configuration Management CLI"
    )

    subparsers = parser.add_subparsers(
        dest='command', help='Available commands')

    # Get command
    get_parser = subparsers.add_parser('get', help='Get configuration value')
    get_parser.add_argument('key', help='Configuration key (dot notation)')
    get_parser.add_argument(
        '--default',
        help='Default value if key not found',
        default=None
    )

    # Set command
    set_parser = subparsers.add_parser('set', help='Set configuration value')
    set_parser.add_argument('key', help='Configuration key (dot notation)')
    set_parser.add_argument('value', help='Value to set')
    set_parser.add_argument(
        '--type',
        choices=['str', 'int', 'float', 'bool'],
        help='Force value type'
    )

    # List command
    list_parser = subparsers.add_parser('list', help='List configuration keys')
    list_parser.add_argument(
        'prefix',
        nargs='?',
        help='Filter keys by prefix',
        default=''
    )

    # Batch set command
    batch_parser = subparsers.add_parser(
        'batch-set', help='Set multiple values from JSON file')
    batch_parser.add_argument('file', help='JSON file with key-value pairs')
    batch_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show changes without applying them'
    )

    # Export command
    export_parser = subparsers.add_parser(
        'export', help='Export configuration to JSON file')
    export_parser.add_argument(
        'file', help='Output JSON file')
    export_parser.add_argument(
        '--prefix',
        help='Export only keys with this prefix',
        default=''
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate', help='Validate configuration')
    validate_parser.add_argument(
        '--strict',
        action='store_true',
        help='Perform strict validation'
    )

    # Profile command
    profile_parser = subparsers.add_parser(
        'profile', help='Apply hardware/network profile optimizations')
    profile_parser.add_argument(
        'profile',
        choices=['auto', 'desktop', 'laptop', 'embedded'],
        help='Hardware profile to apply'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == 'get':
            handle_get(args.key, args.default)
        elif args.command == 'set':
            handle_set(args.key, args.value, args.type)
        elif args.command == 'list':
            handle_list(args.prefix)
        elif args.command == 'batch-set':
            handle_batch_set(args.file, args.dry_run)
        elif args.command == 'export':
            handle_export(args.file, args.prefix)
        elif args.command == 'validate':
            handle_validate(args.strict)
        elif args.command == 'profile':
            handle_profile(args.profile)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def handle_get(key: str, default: Optional[str] = None) -> None:
    """Handle get configuration command."""
    manager = ConfigManager()

    value = manager.get(key, default)

    if value is None:
        print("", end="")
    else:
        # Convert to appropriate type if needed
        if isinstance(value, bool):
            print("true" if value else "false", end="")
        elif isinstance(value, (int, float)):
            print(value, end="")
        else:
            print(str(value), end="")


def handle_set(key: str, value_str: str, type_hint: Optional[str] = None) -> None:
    """Handle set configuration command."""
    manager = ConfigManager()

    # Parse value based on type hint or auto-detect
    try:
        if type_hint == 'int':
            value = int(value_str)
        elif type_hint == 'float':
            value = float(value_str)
        elif type_hint == 'bool':
            value = value_str.lower() == 'true'
        elif type_hint == 'str':
            value = value_str
        else:
            # Auto-detect
            if value_str.lower() == 'true':
                value = True
            elif value_str.lower() == 'false':
                value = False
            elif value_str.isdigit():
                value = int(value_str)
            elif _is_float(value_str):
                value = float(value_str)
            else:
                value = value_str
    except ValueError as e:
        raise ValueError(f"Invalid value format: {e}")

    manager.set_override(key, value)
    manager.save_to_file()


def _is_float(value: str) -> bool:
    """Check if string represents a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False


def handle_list(prefix: str = '') -> None:
    """Handle list configuration command."""
    manager = ConfigManager()
    keys = manager.list_keys(prefix)

    if not keys:
        print("No configuration keys found.", file=sys.stderr)
        sys.exit(1)

    for key in sorted(keys):
        value = manager.get(key)
        if isinstance(value, dict):
            print(f"{key}/")
        else:
            print(f"{key} = {_format_value(value)}")


def handle_batch_set(file_path: str, dry_run: bool = False) -> None:
    """Handle batch-set configuration command."""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to load JSON file: {e}")

    if not isinstance(data, dict):
        raise ValueError("JSON file must contain a dictionary")

    manager = ConfigManager()
    changed_keys = []

    for key, value in data.items():
        current_value = manager.get(key)
        if current_value != value:
            changed_keys.append((key, current_value, value))

    if dry_run:
        if changed_keys:
            print("The following changes would be made:")
            for key, old_val, new_val in changed_keys:
                print(
                    f"  {key}: {_format_value(old_val)} -> {_format_value(new_val)}")
        else:
            print("No changes needed.")
        return

    for key, value in data.items():
        manager.set_override(key, value)

    manager.save_to_file()
    print(f"Successfully set {len(data)} configuration values")


def handle_export(file_path: str, prefix: str = '') -> None:
    """Handle export configuration command."""
    manager = ConfigManager()
    keys = manager.list_keys(prefix)

    data = {}
    for key in keys:
        value = manager.get(key)
        if not isinstance(value, dict):
            data[key] = value

    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(
            f"Successfully exported {len(data)} configuration values to {file_path}")
    except Exception as e:
        raise ValueError(f"Failed to export to file: {e}")


def handle_validate(strict: bool = False) -> None:
    """Handle validate configuration command."""
    manager = ConfigManager()
    errors = []
    warnings = []

    # Basic validation rules
    required_configs = [
        'tts.preferred_engine',
        'cache.chapter_cache_size',
        'cache.width_cache_size'
    ]

    for key in required_configs:
        if manager.get(key) is None:
            errors.append(f"Missing required configuration: {key}")

    # Type validations
    int_configs = ['cache.chapter_cache_size', 'cache.width_cache_size']
    for key in int_configs:
        value = manager.get(key)
        if value is not None and not isinstance(value, int):
            errors.append(f"Configuration {key} must be an integer")

    float_configs = [
        'tts.volume', 'tts.speed', 'gtts.volume', 'gtts.playback_speed',
        'nanmai.volume', 'nanmai.playback_speed'
    ]
    for key in float_configs:
        value = manager.get(key)
        if value is not None and not isinstance(value, (int, float)):
            errors.append(f"Configuration {key} must be a number")

    # Engine-specific validations
    preferred_engine = manager.get('tts.preferred_engine')
    if preferred_engine:
        valid_engines = ['edge-tts', 'gtts', 'nanmai']
        if preferred_engine not in valid_engines:
            warnings.append(f"Unknown TTS engine: {preferred_engine}")

    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"  ERROR: {error}")
        sys.exit(1)
    elif warnings:
        print("Validation completed with warnings:")
        for warning in warnings:
            print(f"  WARNING: {warning}")
    else:
        print("Configuration validation passed")


def handle_profile(profile: str) -> None:
    """Handle profile configuration command."""
    manager = ConfigManager()

    # Auto-detect if requested
    if profile == 'auto':
        try:
            import psutil
            memory_gb = psutil.virtual_memory().total / (1024**3)
            cpu_count = psutil.cpu_count(logical=True)

            if memory_gb <= 4 or cpu_count <= 2:
                profile = 'embedded'
            elif memory_gb <= 8 or cpu_count <= 4:
                profile = 'laptop'
            else:
                profile = 'desktop'
        except ImportError:
            profile = 'laptop'  # Default fallback

    # Apply profile settings
    if profile == 'desktop':
        optimizations = {
            'tts.predictive_config.base_safety_buffer': 1.5,
            'tts.predictive_config.resource_factor_weight': 0.3,
            'cache.chapter_cache_size': 100,
            'cache.width_cache_size': 2000,
        }
    elif profile == 'laptop':
        optimizations = {
            'tts.predictive_config.base_safety_buffer': 2.5,
            'tts.predictive_config.resource_factor_weight': 0.5,
            'cache.chapter_cache_size': 50,
            'cache.width_cache_size': 1000,
        }
    elif profile == 'embedded':
        optimizations = {
            'tts.predictive_config.base_safety_buffer': 3.0,
            'tts.predictive_config.resource_factor_weight': 0.7,
            'cache.chapter_cache_size': 10,
            'cache.width_cache_size': 200,
        }

    for key, value in optimizations.items():
        manager.set_override(key, value)

    manager.save_to_file()
    print(f"Applied {profile} profile optimizations")


def _format_value(value: Any) -> str:
    """Format configuration value for display."""
    if isinstance(value, bool):
        return "true" if value else "false"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, str):
        return f'"{value}"'
    elif value is None:
        return "null"
    else:
        return str(value)


if __name__ == '__main__':
    main()
