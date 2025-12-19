# HCGK Kernel

**Hardware Control Gatekeeper Kernel for AI Model Loading**

[![PyPI version](https://badge.fury.io/py/hcgk-kernel.svg)](https://badge.fury.io/py/hcgk-kernel)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

HCGK Kernel is a hardware authorization system designed to prevent AI model loading failures by validating system resources before execution. It performs comprehensive hardware detection and validation to ensure your system meets the requirements for loading memory-intensive models.

---

## Overview

Modern AI models require substantial computational resources. Loading a model without adequate RAM or VRAM can lead to:
- System crashes and out-of-memory errors
- Prolonged loading times and system freezes
- Data loss from forced shutdowns
- Wasted time troubleshooting preventable failures

HCGK Kernel solves this by validating your hardware **before** attempting to load models, providing clear feedback on what's available and what's required.

---

## Features

- **Comprehensive Hardware Detection**: Detailed scanning of RAM, VRAM, CPU, and GPU resources
- **Validated Configuration**: Type-safe configuration with automatic validation
- **Safety Margins**: Configurable resource reservation to prevent system instability
- **Retry Logic**: Automatic retry on transient hardware detection failures
- **Detailed Reporting**: Clear, actionable feedback on authorization status
- **CLI Tools**: Professional command-line interface with JSON output support
- **Extensive Logging**: Comprehensive logs for debugging and monitoring
- **Zero Side Effects**: Pure functional design with no global state

---

## Installation

```bash
pip install hcgk-kernel
```

**Requirements:**
- Python 3.8 or higher
- psutil 5.9.0 or higher
- torch 2.0.0 or higher

---

## Quick Start

### Command Line Interface

```bash
# Check hardware authorization
hcgk check

# Display system information
hcgk info

# Show system requirements
hcgk info --requirements

# Output as JSON
hcgk info --json

# Display configuration
hcgk config
```

### Python API

```python
from hcgk_kernel import HCGKKernel

# Initialize kernel
kernel = HCGKKernel()

# Check authorization
authorized, message = kernel.authorize()

if authorized:
    # Proceed with model loading
    model = load_your_model()
else:
    print(f"Authorization denied: {message}")
```

---

## Hardware Requirements

HCGK Kernel validates hardware against configurable thresholds:

### GPU Mode (CUDA Available)
- Minimum RAM: 8 GB (default)
- Minimum VRAM: 4 GB (default)

### CPU Mode (No GPU)
- Minimum RAM: 16 GB (default)

These values can be configured via environment variables or programmatic configuration.

---

## Configuration

### Environment Variables

```bash
# Hardware thresholds
export HCGK_MIN_RAM_GB=8.0              # Minimum RAM for GPU mode
export HCGK_MIN_VRAM_GB=4.0             # Minimum VRAM required
export HCGK_MIN_RAM_NO_GPU_GB=16.0      # Minimum RAM for CPU mode

# Safety settings
export HCGK_RAM_SAFETY_MARGIN=0.1       # Reserve 10% RAM (0.0-1.0)
export HCGK_MAX_SCAN_RETRIES=2          # Hardware scan retry attempts
export HCGK_STRICT_MODE=true            # Enable strict validation
```

### Programmatic Configuration

```python
from hcgk_kernel import HCGKKernel, HCGKConfig

config = HCGKConfig(
    MIN_RAM_GB=16.0,
    MIN_VRAM_GB=8.0,
    MIN_RAM_NO_GPU_GB=32.0,
    RAM_SAFETY_MARGIN=0.15,
    MAX_SCAN_RETRIES=3,
    STRICT_MODE=True
)

kernel = HCGKKernel(config=config)
```

---

## Usage Examples

### Basic Authorization

```python
from hcgk_kernel import HCGKKernel

kernel = HCGKKernel()
authorized, message = kernel.authorize()

if not authorized:
    raise RuntimeError(f"Hardware requirements not met: {message}")

# Safe to proceed with model loading
```

### Retrieve System Information

```python
kernel = HCGKKernel()
info = kernel.get_system_info()

# Access hardware details
ram_total = info['ram']['total_gb']
gpu_name = info['gpu']['name']
vram_free = info['gpu']['vram_total_gb'] - info['gpu']['vram_allocated_gb']

print(f"System: {ram_total:.2f}GB RAM, GPU: {gpu_name}")
```

### Silent Mode for Scripts

```python
import sys
from hcgk_kernel import HCGKKernel

kernel = HCGKKernel(silent=True)
authorized, _ = kernel.authorize()

sys.exit(0 if authorized else 1)
```

### Custom Configuration

```python
from hcgk_kernel import HCGKKernel, HCGKConfig

# Define custom requirements
config = HCGKConfig(
    MIN_RAM_GB=32.0,
    MIN_VRAM_GB=16.0,
    RAM_SAFETY_MARGIN=0.2
)

kernel = HCGKKernel(config=config)
authorized, message = kernel.authorize()
```

### Integration with Model Loading

```python
from hcgk_kernel import HCGKKernel
import torch

def load_model_with_validation(model_path):
    """Load model with hardware validation."""
    kernel = HCGKKernel()
    
    # Validate hardware
    authorized, message = kernel.authorize()
    if not authorized:
        raise RuntimeError(f"Hardware validation failed: {message}")
    
    # Get system info for optimization
    info = kernel.get_system_info()
    device = "cuda" if info['gpu']['available'] else "cpu"
    
    # Load model
    model = torch.load(model_path, map_location=device)
    return model

# Usage
try:
    model = load_model_with_validation("model.pt")
except RuntimeError as e:
    print(f"Error: {e}")
```

---

## CLI Reference

### `hcgk check`

Check hardware authorization status.

**Options:**
- `-s, --silent` - Suppress output, return exit code only
- `-V, --verbose` - Show detailed validation messages

**Exit Codes:**
- `0` - Authorization granted
- `1` - Authorization denied or error

**Example:**
```bash
hcgk check --verbose
```

### `hcgk info`

Display detailed system information.

**Options:**
- `-j, --json` - Output in JSON format
- `-r, --requirements` - Include requirements check

**Example:**
```bash
hcgk info --json --requirements
```

### `hcgk config`

Display current configuration.

**Options:**
- `-j, --json` - Output in JSON format

**Example:**
```bash
hcgk config
```

### `hcgk validate`

Validate configuration without running authorization.

**Example:**
```bash
hcgk validate
```

---

## Architecture

HCGK Kernel is built with a modular architecture:

- **HCGKKernel**: Main orchestrator that coordinates scanning and validation
- **SystemScanner**: Performs hardware detection with retry logic
- **ConstraintValidator**: Validates hardware against requirements
- **HCGKConfig**: Type-safe configuration with validation
- **HardwareInfo**: Immutable data container for hardware information
- **SecureLogger**: Thread-safe logging with secure directory handling

---

## Safety Features

### RAM Safety Margin

By default, HCGK reserves 10% of available RAM to prevent the system from running out of memory during model loading. This margin is configurable via `RAM_SAFETY_MARGIN`.

### Retry Logic

Hardware scanning includes automatic retry logic to handle transient failures. The number of retries is configurable via `MAX_SCAN_RETRIES`.

### Validation Checks

Multiple independent validation checks are performed:
- Total RAM sufficiency
- Available RAM after safety margin
- VRAM total and free space
- System memory pressure detection

### Detailed Reporting

When validation fails, HCGK provides:
- Specific reasons for each failure
- Current hardware specifications
- Actionable recommendations for resolution

---

## Error Handling

HCGK Kernel provides a hierarchy of custom exceptions:

- `HCGKError`: Base exception for all kernel errors
- `DependencyError`: Missing required dependencies (psutil, torch)
- `ScanError`: Hardware scan failures
- `ValidationError`: Hardware validation failures

All exceptions include detailed error messages for debugging.

---

## Performance

- **Initialization**: 10-20ms
- **Hardware Scan**: 50-100ms
- **Validation**: 5-10ms
- **Total Authorization**: 100-150ms
- **Memory Overhead**: 2-5MB

Performance measurements on standard development hardware.

---

## Testing

HCGK Kernel includes comprehensive test coverage:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=hcgk_kernel
```

Test suite includes:
- Unit tests for all components
- Integration tests for complete workflows
- Configuration validation tests
- Error handling tests

---

## Logging

Logs are written to `~/.alice_kernels/logs/.hcgk_au.log` by default. Log entries include:
- Timestamp
- Log level
- Function name and line number
- Detailed message

Logging is thread-safe and includes fallback to current directory if home directory is not writable.

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

Please ensure code follows the existing style and includes appropriate documentation.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

## Author

**Matias Nisperuza**  

---

## Support

Email: mnisperuza1102@gmail.com
pyPI page:https://pypi.org/project/hcgk-kernel/

---

## Acknowledgments

Built for the AI/ML community to provide reliable hardware validation for model loading operations.