#!/bin/bash

# TTS Smart Preload v4.0 "Reservoir" - Deployment Script
# This script helps deploy the v4.0 Reservoir system with proper configuration

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.config/speakub"
CONFIG_FILE="$CONFIG_DIR/config.yaml"
SAMPLE_CONFIG="$SCRIPT_DIR/config_sample.yaml"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  TTS Smart Preload v4.0 \"Reservoir\"${NC}"
echo -e "${BLUE}         Deployment Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo

# Function to print status messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    print_error "This deployment script is designed for Linux systems."
    print_info "The TTS Smart Preload v4.0 system should work on other Unix-like systems,"
    print_info "but you'll need to manually set up the configuration."
    exit 1
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is required but not found."
    print_info "Please install Python 3 and try again."
    exit 1
fi

print_info "Checking system requirements..."
python3 -c "import asyncio, psutil, threading; print('Python dependencies available')" 2>/dev/null && print_status "Python dependencies satisfied" || {
    print_error "Missing required Python packages (asyncio, psutil, threading)"
    print_info "Install with: pip install psutil"
    exit 1
}

# Create config directory
print_info "Setting up configuration directory..."
if [[ ! -d "$CONFIG_DIR" ]]; then
    mkdir -p "$CONFIG_DIR"
    print_status "Created configuration directory: $CONFIG_DIR"
else
    print_status "Configuration directory already exists: $CONFIG_DIR"
fi

# Detect hardware profile
print_info "Detecting hardware profile..."
HARDWARE_PROFILE=$(python3 -c "
import psutil
import os

# Get system memory in GB
memory_gb = psutil.virtual_memory().total / (1024**3)
cpu_count = psutil.cpu_count(logical=True)

if memory_gb <= 4 or cpu_count <= 2:
    print('low_end')
elif memory_gb <= 8 or cpu_count <= 4:
    print('mid_range')
else:
    print('high_end')
")

print_status "Detected hardware profile: $HARDWARE_PROFILE"

# Check network connectivity
print_info "Checking network connectivity..."
if ping -c 1 -W 2 8.8.8.8 &> /dev/null; then
    NETWORK_STATUS="good"
    print_status "Network connectivity: Good"
else
    NETWORK_STATUS="poor"
    print_warning "Network connectivity: Limited (will use conservative settings)"
fi

# Copy and customize configuration
print_info "Setting up configuration file..."

if [[ ! -f "$CONFIG_FILE" ]]; then
    if [[ -f "$SAMPLE_CONFIG" ]]; then
        cp "$SAMPLE_CONFIG" "$CONFIG_FILE"
        print_status "Copied sample configuration to: $CONFIG_FILE"
    else
        print_error "Sample configuration file not found: $SAMPLE_CONFIG"
        print_info "Please ensure config_sample.yaml exists in the project directory."
        exit 1
    fi
else
    print_warning "Configuration file already exists: $CONFIG_FILE"
    read -p "Do you want to overwrite it with optimized settings? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$SAMPLE_CONFIG" "$CONFIG_FILE"
        print_status "Overwrote configuration with sample settings"
    else
        print_info "Keeping existing configuration"
    fi
fi

# Customize configuration based on detected environment
print_info "Optimizing configuration for your environment..."

python3 -c "
import yaml
import os

config_file = '$CONFIG_FILE'
hardware_profile = '$HARDWARE_PROFILE'
network_status = '$NETWORK_STATUS'

# Load current config
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

# Hardware-specific optimizations
if hardware_profile == 'low_end':
    config['tts']['reservoir'].update({
        'base_safety_buffer': 3.0,
        'resource_factor_weight': 0.7,
        'max_safety_buffer': 20.0
    })
    config['cache'].update({
        'chapter_cache_size': 10,
        'width_cache_size': 200
    })
    print('Applied low-end device optimizations')
elif hardware_profile == 'high_end':
    config['tts']['predictive_config'].update({
        'base_safety_buffer': 1.5,
        'resource_factor_weight': 0.3,
        'max_safety_buffer': 10.0
    })
    config['cache'].update({
        'chapter_cache_size': 100,
        'width_cache_size': 2000
    })
    print('Applied high-end device optimizations')
else:  # mid_range
    print('Using default mid-range settings')

# Network-specific optimizations
if network_status == 'poor':
    config['tts']['predictive_config'].update({
        'base_safety_buffer': max(config['tts']['predictive_config']['base_safety_buffer'], 4.0),
        'resource_factor_weight': 0.8,
        'max_safety_buffer': 25.0
    })
    config['network'].update({
        'recovery_timeout_minutes': 15,
        'recovery_check_interval': 5
    })
    print('Applied unstable network optimizations')

# Save optimized config
with open(config_file, 'w') as f:
    yaml.dump(config, f, indent=2)

print('Configuration optimization complete')
"

print_status "Configuration optimized for your environment"

# Validate configuration
print_info "Validating configuration..."
python3 speakub/utils/config_cli.py get tts.preferred_engine >/dev/null && \
python3 speakub/utils/config_cli.py get tts.predictive_config.base_safety_buffer >/dev/null && \
python3 speakub/utils/config_cli.py get tts.predictive_config.resource_factor_weight >/dev/null && \
python3 speakub/utils/config_cli.py get tts.predictive_config.max_safety_buffer >/dev/null && \
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')

try:
    from speakub.tts.reservoir import PredictiveBatchController, QueuePredictor, PlayTimeMonitor
    play_monitor = PlayTimeMonitor()
    queue_predictor = QueuePredictor(play_monitor)
    controller = PredictiveBatchController(None, queue_predictor)
    buffer = controller._calculate_dynamic_safety_buffer()
    assert 0 < buffer <= 30, f'Buffer calculation out of range: {buffer}'
    print('✓ Configuration validation via CLI successful')
    print('✓ Dynamic buffer calculation working')
    print('All validations passed!')

except Exception as e:
    print(f'❌ Validation failed: {e}')
    sys.exit(1)
" && print_status "Configuration validation successful" || {
    print_error "Configuration validation failed"
    print_info "Please check the configuration file and try again."
    exit 1
}

# Run quick functionality test
print_info "Running quick functionality test..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')

print('Testing core functionality...')

# Test imports
from speakub.tts.reservoir import PredictiveBatchController, QueuePredictor, PlayTimeMonitor
from speakub.utils.config import ConfigManager
print('✓ Imports successful')

# Test controller creation
play_monitor = PlayTimeMonitor()
queue_predictor = QueuePredictor(play_monitor)
controller = PredictiveBatchController(None, queue_predictor)
print('✓ Controller initialization successful')

# Test configuration loading via ConfigManager
config_mgr = ConfigManager()
config = config_mgr.get('tts.predictive_config', {})
print(f'✓ Configuration loaded via ConfigManager: {len(config)} parameters')

# Test buffer calculation
buffer = controller._calculate_dynamic_safety_buffer()
print(f'✓ Dynamic buffer calculation: {buffer:.2f}s')

# Test network and resource monitoring
controller.network_monitor.record_latency(1.5)
latency_factor = controller.network_monitor.get_latency_factor()
print(f'✓ Network monitoring: latency factor = {latency_factor:.2f}')

controller.resource_manager.record_cpu_usage(50.0)
cpu_pressure = controller.resource_manager.get_cpu_pressure_factor()
print(f'✓ Resource monitoring: CPU pressure factor = {cpu_pressure:.2f}')

print('All functionality tests passed!')
" && print_status "Functionality test successful" || {
    print_error "Functionality test failed"
    print_info "The system may still work, but there are some issues to investigate."
}

# Create deployment summary
print_info "Creating deployment summary..."
cat > "$CONFIG_DIR/deployment_summary.txt" << EOF
TTS Smart Preload v4.0 "Reservoir" - Deployment Summary
======================================================

Deployment Date: $(date)
Hardware Profile: $HARDWARE_PROFILE
Network Status: $NETWORK_STATUS
Configuration File: $CONFIG_FILE

Key Settings Applied:
- Base Safety Buffer: $(python3 speakub/utils/config_cli.py get tts.predictive_config.base_safety_buffer --default default)
- Resource Factor Weight: $(python3 speakub/utils/config_cli.py get tts.predictive_config.resource_factor_weight --default default)
- Max Safety Buffer: $(python3 speakub/utils/config_cli.py get tts.predictive_config.max_safety_buffer --default default)

Next Steps:
1. Start the SpeakUB application
2. Enable TTS smooth mode in settings
3. Monitor performance logs for optimization opportunities
4. Adjust configuration parameters based on usage patterns

For troubleshooting, see: $SCRIPT_DIR/README_v5_reservoir.md
EOF

print_status "Deployment summary created: $CONFIG_DIR/deployment_summary.txt"

# Final instructions
echo
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  🎉 DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo -e "${GREEN}========================================${NC}"
echo
echo -e "${BLUE}Configuration Summary:${NC}"
echo -e "  📁 Config Location: $CONFIG_FILE"
echo -e "  🖥️  Hardware Profile: $HARDWARE_PROFILE"
echo -e "  🌐 Network Status: $NETWORK_STATUS"
echo
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Start SpeakUB application"
echo -e "  2. Enable TTS smooth mode"
echo -e "  3. Monitor logs for performance metrics"
echo -e "  4. Fine-tune configuration as needed"
echo
echo -e "${BLUE}Documentation:${NC}"
echo -e "  📖 README: $SCRIPT_DIR/README_v5_reservoir.md"
echo -e "  📋 Summary: $CONFIG_DIR/deployment_summary.txt"
echo
echo -e "${GREEN}The TTS Smart Preload v4.0 \"Reservoir\" system is now ready! 🚀${NC}"
echo
