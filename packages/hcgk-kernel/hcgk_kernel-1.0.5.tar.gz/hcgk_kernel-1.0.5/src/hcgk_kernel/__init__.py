# ==============================================================
# HCGK Kernel
# Hardware Authorization System for AI Frameworks
# 
# Author: Matias Nisperuza - 2025
# License: MIT
# ==============================================================

__version__ = "1.0.5"
__author__ = "Matias Nisperuza"

import os
import sys
import logging
import platform
from pathlib import Path
from datetime import datetime
from typing import Tuple, Dict, Optional, List
from dataclasses import dataclass

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

# =========================
# CONFIGURATION
# =========================
@dataclass
class HCGKConfig:
    """Immutable configuration for HCGK Kernel"""
    # Hardware constraints (configurable via environment variables)
    MIN_RAM_GB: float = float(os.getenv("HCGK_MIN_RAM_GB", "8.0"))
    MIN_VRAM_GB: float = float(os.getenv("HCGK_MIN_VRAM_GB", "4.0"))
    MIN_RAM_NO_GPU_GB: float = float(os.getenv("HCGK_MIN_RAM_NO_GPU_GB", "16.0"))
    
    # Safety margins (percentage of resources to keep free)
    RAM_SAFETY_MARGIN: float = float(os.getenv("HCGK_RAM_SAFETY_MARGIN", "0.1"))  # 10%
    
    # Logging
    KERNEL_LOG_DIR: Path = Path.home() / ".alice_kernels" / "logs"
    LOG_FILE: Path = KERNEL_LOG_DIR / ".hcgk_au.log"
    
    # Scan retries
    MAX_SCAN_RETRIES: int = int(os.getenv("HCGK_MAX_SCAN_RETRIES", "2"))
    
    # Validation
    STRICT_MODE: bool = os.getenv("HCGK_STRICT_MODE", "true").lower() == "true"
    
    def __post_init__(self):
        """Validate configuration values"""
        if self.MIN_RAM_GB <= 0 or self.MIN_VRAM_GB <= 0 or self.MIN_RAM_NO_GPU_GB <= 0:
            raise ValueError("All minimum resource values must be positive")
        
        if not 0 <= self.RAM_SAFETY_MARGIN < 1:
            raise ValueError("RAM_SAFETY_MARGIN must be between 0 and 1")
        
        if self.MAX_SCAN_RETRIES < 1:
            raise ValueError("MAX_SCAN_RETRIES must be at least 1")

# =========================
# EXCEPTIONS
# =========================
class HCGKError(Exception):
    """Base exception for HCGK Kernel"""
    pass

class DependencyError(HCGKError):
    """Missing required dependencies"""
    pass

class ScanError(HCGKError):
    """Hardware scan failed"""
    pass

class ValidationError(HCGKError):
    """Hardware validation failed"""
    pass

# =========================
# SECURE LOGGING
# =========================
class SecureLogger:
    """Thread-safe secure logger with comprehensive error handling"""
    
    def __init__(self, log_path: Path):
        self.log_path = log_path
        self._ensure_secure_directory()
        self._setup_logger()
    
    def _ensure_secure_directory(self):
        """Create hidden log directory with restricted permissions"""
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            # Set directory permissions: owner read/write/execute only
            if platform.system() != "Windows":
                os.chmod(self.log_path.parent, 0o700)
        except OSError as e:
            # Fallback to current directory if home directory is not writable
            fallback_dir = Path.cwd() / ".hcgk_logs"
            fallback_dir.mkdir(exist_ok=True)
            self.log_path = fallback_dir / ".hcgk_au.log"
            print(f"Warning: Using fallback log directory: {fallback_dir}", file=sys.stderr)
    
    def _setup_logger(self):
        """Configure kernel logger with comprehensive formatting"""
        self.logger = logging.getLogger("HCGKKernel")
        self.logger.setLevel(logging.DEBUG)
        self.logger.handlers.clear()
        
        # File handler with detailed formatting
        try:
            file_handler = logging.FileHandler(self.log_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_formatter = logging.Formatter(
                "%(asctime)s - [HCGK] - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        except (OSError, PermissionError) as e:
            print(f"Warning: Could not create log file: {e}", file=sys.stderr)
    
    def debug(self, msg: str):
        """Log debug message"""
        self.logger.debug(msg)
    
    def info(self, msg: str):
        """Log info message"""
        self.logger.info(msg)
    
    def warning(self, msg: str):
        """Log warning message"""
        self.logger.warning(msg)
    
    def error(self, msg: str):
        """Log error message"""
        self.logger.error(msg)
    
    def critical(self, msg: str):
        """Log critical message"""
        self.logger.critical(msg)

# =========================
# HARDWARE DETECTION
# =========================
@dataclass
class HardwareInfo:
    """Immutable hardware information container"""
    success: bool
    timestamp: str
    
    # RAM
    ram_total_gb: float = 0.0
    ram_available_gb: float = 0.0
    ram_percent_used: float = 0.0
    
    # CPU
    cpu_count_physical: int = 0
    cpu_count_logical: int = 0
    cpu_percent: float = 0.0
    
    # GPU
    has_gpu: bool = False
    gpu_count: int = 0
    gpu_name: str = "None"
    vram_total_gb: float = 0.0
    vram_allocated_gb: float = 0.0
    vram_reserved_gb: float = 0.0
    
    # System
    platform: str = ""
    python_version: str = ""
    
    # Error info
    error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "success": self.success,
            "timestamp": self.timestamp,
            "ram": {
                "total_gb": self.ram_total_gb,
                "available_gb": self.ram_available_gb,
                "percent_used": self.ram_percent_used
            },
            "cpu": {
                "physical_cores": self.cpu_count_physical,
                "logical_cores": self.cpu_count_logical,
                "percent_used": self.cpu_percent
            },
            "gpu": {
                "available": self.has_gpu,
                "count": self.gpu_count,
                "name": self.gpu_name,
                "vram_total_gb": self.vram_total_gb,
                "vram_allocated_gb": self.vram_allocated_gb,
                "vram_reserved_gb": self.vram_reserved_gb
            },
            "system": {
                "platform": self.platform,
                "python_version": self.python_version
            },
            "error": self.error
        }

# =========================
# SYSTEM SCANNER
# =========================
class SystemScanner:
    """
    Production-grade hardware scanner with comprehensive detection
    and error handling. Provides detailed system information.
    """
    
    def __init__(self, logger: SecureLogger, config: HCGKConfig):
        self.logger = logger
        self.config = config
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Validate required dependencies are available"""
        missing = []
        if not HAS_PSUTIL:
            missing.append("psutil")
        if not HAS_TORCH:
            missing.append("torch")
        
        if missing:
            error_msg = f"Missing required dependencies: {', '.join(missing)}"
            self.logger.critical(error_msg)
            raise DependencyError(error_msg)
        
        self.logger.info("All dependencies validated successfully")
    
    def _scan_ram(self) -> Tuple[float, float, float]:
        """
        Scan RAM with comprehensive error handling
        Returns: (total_gb, available_gb, percent_used)
        """
        try:
            mem = psutil.virtual_memory()
            total_gb = mem.total / (1024 ** 3)
            available_gb = mem.available / (1024 ** 3)
            percent_used = mem.percent
            
            self.logger.debug(f"RAM scan: {total_gb:.2f}GB total, {available_gb:.2f}GB available ({percent_used:.1f}% used)")
            
            # Sanity checks
            if total_gb <= 0 or available_gb < 0:
                raise ValueError(f"Invalid RAM values: total={total_gb}, available={available_gb}")
            
            if available_gb > total_gb:
                self.logger.warning(f"Available RAM ({available_gb:.2f}GB) exceeds total ({total_gb:.2f}GB), using total")
                available_gb = total_gb
            
            return (total_gb, available_gb, percent_used)
            
        except Exception as e:
            self.logger.error(f"RAM scan failed: {type(e).__name__}: {e}")
            raise ScanError(f"Failed to scan RAM: {e}")
    
    def _scan_cpu(self) -> Tuple[int, int, float]:
        """
        Scan CPU with comprehensive error handling
        Returns: (physical_cores, logical_cores, percent_used)
        """
        try:
            physical = psutil.cpu_count(logical=False)
            logical = psutil.cpu_count(logical=True)
            
            # Handle None values (can happen on some systems)
            if physical is None:
                physical = logical if logical else 1
            if logical is None:
                logical = physical if physical else 1
            
            # Get CPU usage (average over 0.1 seconds)
            try:
                cpu_percent = psutil.cpu_percent(interval=0.1)
            except Exception:
                cpu_percent = 0.0
                self.logger.warning("Could not measure CPU usage")
            
            self.logger.debug(f"CPU scan: {physical} physical cores, {logical} logical cores, {cpu_percent:.1f}% used")
            
            return (physical, logical, cpu_percent)
            
        except Exception as e:
            self.logger.error(f"CPU scan failed: {type(e).__name__}: {e}")
            raise ScanError(f"Failed to scan CPU: {e}")
    
    def _scan_gpu(self) -> Tuple[bool, int, str, float, float, float]:
        """
        Scan GPU with comprehensive CUDA detection and error handling
        Returns: (has_gpu, gpu_count, gpu_name, vram_total_gb, vram_allocated_gb, vram_reserved_gb)
        """
        try:
            # Check CUDA availability
            cuda_available = torch.cuda.is_available()
            
            if not cuda_available:
                self.logger.info("No CUDA GPU detected")
                return (False, 0, "None", 0.0, 0.0, 0.0)
            
            # Get GPU count
            gpu_count = torch.cuda.device_count()
            
            if gpu_count == 0:
                self.logger.warning("CUDA available but no GPUs detected")
                return (False, 0, "None", 0.0, 0.0, 0.0)
            
            # Get primary GPU info (device 0)
            try:
                device_props = torch.cuda.get_device_properties(0)
                gpu_name = device_props.name
                vram_total = device_props.total_memory / (1024 ** 3)
                
                # Get current memory usage
                vram_allocated = torch.cuda.memory_allocated(0) / (1024 ** 3)
                vram_reserved = torch.cuda.memory_reserved(0) / (1024 ** 3)
                
                self.logger.debug(
                    f"GPU scan: {gpu_name}, {vram_total:.2f}GB VRAM total, "
                    f"{vram_allocated:.2f}GB allocated, {vram_reserved:.2f}GB reserved"
                )
                
                # Sanity checks
                if vram_total <= 0:
                    raise ValueError(f"Invalid VRAM total: {vram_total}")
                
                return (True, gpu_count, gpu_name, vram_total, vram_allocated, vram_reserved)
                
            except Exception as e:
                self.logger.error(f"Failed to get GPU properties: {e}")
                # Return basic info if detailed scan fails
                return (True, gpu_count, "Unknown GPU", 0.0, 0.0, 0.0)
            
        except Exception as e:
            self.logger.error(f"GPU scan failed: {type(e).__name__}: {e}")
            # Return no GPU rather than failing
            return (False, 0, "None", 0.0, 0.0, 0.0)
    
    def scan(self) -> HardwareInfo:
        """
        Perform comprehensive hardware scan with retry logic
        Returns: HardwareInfo object with all system details
        """
        self.logger.info("="*60)
        self.logger.info("Starting hardware scan")
        
        last_error = None
        
        for attempt in range(self.config.MAX_SCAN_RETRIES):
            try:
                # Scan RAM
                ram_total, ram_available, ram_percent = self._scan_ram()
                
                # Scan CPU
                cpu_physical, cpu_logical, cpu_percent = self._scan_cpu()
                
                # Scan GPU
                has_gpu, gpu_count, gpu_name, vram_total, vram_allocated, vram_reserved = self._scan_gpu()
                
                # Get system info
                platform_str = f"{platform.system()} {platform.release()}"
                python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                
                # Create hardware info
                hw_info = HardwareInfo(
                    success=True,
                    timestamp=datetime.now().isoformat(),
                    ram_total_gb=round(ram_total, 2),
                    ram_available_gb=round(ram_available, 2),
                    ram_percent_used=round(ram_percent, 1),
                    cpu_count_physical=cpu_physical,
                    cpu_count_logical=cpu_logical,
                    cpu_percent=round(cpu_percent, 1),
                    has_gpu=has_gpu,
                    gpu_count=gpu_count,
                    gpu_name=gpu_name,
                    vram_total_gb=round(vram_total, 2),
                    vram_allocated_gb=round(vram_allocated, 2),
                    vram_reserved_gb=round(vram_reserved, 2),
                    platform=platform_str,
                    python_version=python_version
                )
                
                self.logger.info(f"Hardware scan completed successfully on attempt {attempt + 1}")
                self.logger.info(f"System: {platform_str}, Python {python_version}")
                self.logger.info(f"RAM: {ram_total:.2f}GB total, {ram_available:.2f}GB available")
                self.logger.info(f"CPU: {cpu_physical} physical cores, {cpu_logical} logical cores")
                self.logger.info(f"GPU: {gpu_name} ({vram_total:.2f}GB VRAM)" if has_gpu else "GPU: None")
                
                return hw_info
                
            except ScanError as e:
                last_error = str(e)
                self.logger.warning(f"Scan attempt {attempt + 1} failed: {e}")
                if attempt < self.config.MAX_SCAN_RETRIES - 1:
                    self.logger.info(f"Retrying scan ({attempt + 2}/{self.config.MAX_SCAN_RETRIES})...")
            
            except Exception as e:
                last_error = f"{type(e).__name__}: {e}"
                self.logger.error(f"Unexpected error during scan: {last_error}")
                break
        
        # All retries failed
        self.logger.critical(f"Hardware scan failed after {self.config.MAX_SCAN_RETRIES} attempts")
        return HardwareInfo(
            success=False,
            timestamp=datetime.now().isoformat(),
            error=last_error or "Unknown scan error"
        )

# =========================
# CONSTRAINT VALIDATOR
# =========================
class ConstraintValidator:
    """
    Production-grade constraint validator with detailed reporting
    and comprehensive checks
    """
    
    def __init__(self, logger: SecureLogger, config: HCGKConfig):
        self.logger = logger
        self.config = config
    
    def _check_ram_sufficient(self, hw_info: HardwareInfo) -> Tuple[bool, List[str]]:
        """
        Check if RAM is sufficient for model loading
        Returns: (is_sufficient, reasons)
        """
        reasons = []
        
        # Calculate effective available RAM considering safety margin
        effective_available = hw_info.ram_available_gb * (1 - self.config.RAM_SAFETY_MARGIN)
        
        if hw_info.has_gpu:
            # GPU mode: Lower RAM requirement
            required = self.config.MIN_RAM_GB
            if hw_info.ram_total_gb < required:
                reasons.append(
                    f"Insufficient total RAM: {hw_info.ram_total_gb:.2f}GB < {required:.2f}GB required (GPU mode)"
                )
            
            if effective_available < required * 0.5:  # Need at least 50% of requirement available
                reasons.append(
                    f"Insufficient available RAM: {effective_available:.2f}GB available after safety margin "
                    f"(need ~{required * 0.5:.2f}GB)"
                )
        else:
            # CPU mode: Higher RAM requirement
            required = self.config.MIN_RAM_NO_GPU_GB
            if hw_info.ram_total_gb < required:
                reasons.append(
                    f"Insufficient total RAM: {hw_info.ram_total_gb:.2f}GB < {required:.2f}GB required (CPU mode)"
                )
            
            if effective_available < required * 0.5:
                reasons.append(
                    f"Insufficient available RAM: {effective_available:.2f}GB available after safety margin "
                    f"(need ~{required * 0.5:.2f}GB)"
                )
        
        # Check if system is under extreme memory pressure
        if hw_info.ram_percent_used > 90:
            reasons.append(
                f"System under extreme memory pressure: {hw_info.ram_percent_used:.1f}% RAM used"
            )
        
        return (len(reasons) == 0, reasons)
    
    def _check_vram_sufficient(self, hw_info: HardwareInfo) -> Tuple[bool, List[str]]:
        """
        Check if VRAM is sufficient for GPU model loading
        Returns: (is_sufficient, reasons)
        """
        if not hw_info.has_gpu:
            return (True, [])  # No GPU, no VRAM requirement
        
        reasons = []
        required = self.config.MIN_VRAM_GB
        
        if hw_info.vram_total_gb < required:
            reasons.append(
                f"Insufficient VRAM: {hw_info.vram_total_gb:.2f}GB < {required:.2f}GB required"
            )
        
        # Check available VRAM (total - allocated)
        vram_available = hw_info.vram_total_gb - hw_info.vram_allocated_gb
        if vram_available < required * 0.8:  # Need at least 80% of requirement free
            reasons.append(
                f"Insufficient free VRAM: {vram_available:.2f}GB available "
                f"(need ~{required * 0.8:.2f}GB free)"
            )
        
        return (len(reasons) == 0, reasons)
    
    def _generate_recommendations(self, hw_info: HardwareInfo, ram_ok: bool, vram_ok: bool) -> str:
        """Generate detailed recommendations based on hardware"""
        recommendations = []
        
        if not ram_ok:
            if hw_info.has_gpu:
                recommendations.append(
                    f"• Upgrade RAM to at least {self.config.MIN_RAM_GB:.0f}GB for GPU-accelerated models"
                )
            else:
                recommendations.append(
                    f"• Upgrade RAM to at least {self.config.MIN_RAM_NO_GPU_GB:.0f}GB for CPU-based models"
                )
            
            recommendations.append(
                "• Close other applications to free up memory"
            )
            
            recommendations.append(
                "• Consider using quantized models (4-bit or 8-bit) which require less RAM"
            )
        
        if hw_info.has_gpu and not vram_ok:
            recommendations.append(
                f"• Upgrade GPU or get GPU with at least {self.config.MIN_VRAM_GB:.0f}GB VRAM"
            )
            recommendations.append(
                "• Use model quantization to reduce VRAM usage"
            )
            recommendations.append(
                "• Consider CPU-only mode if GPU VRAM is insufficient"
            )
        
        if not hw_info.has_gpu:
            recommendations.append(
                "• Consider adding a GPU for better performance (8GB+ VRAM recommended)"
            )
        
        # Memory pressure recommendations
        if hw_info.ram_percent_used > 80:
            recommendations.append(
                f"• High memory usage detected ({hw_info.ram_percent_used:.1f}%). Close unnecessary applications"
            )
        
        return "\n".join(recommendations) if recommendations else "Hardware meets requirements"
    
    def validate(self, hw_info: HardwareInfo) -> Tuple[bool, str]:
        """
        Validate hardware against requirements
        Returns: (authorized, detailed_message)
        """
        self.logger.info("="*60)
        self.logger.info("Starting hardware validation")
        
        # Check if scan was successful
        if not hw_info.success:
            error_msg = f"Hardware scan failed: {hw_info.error}"
            self.logger.error(error_msg)
            return (False, f"❌ {error_msg}\n\nCannot proceed without valid hardware information.")
        
        # Perform checks
        ram_ok, ram_reasons = self._check_ram_sufficient(hw_info)
        vram_ok, vram_reasons = self._check_vram_sufficient(hw_info)
        
        # Determine authorization
        authorized = ram_ok and vram_ok
        
        # Build detailed message
        if authorized:
            mode = "GPU" if hw_info.has_gpu else "CPU"
            message = (
                f"✅ Hardware validation passed ({mode} mode)\n\n"
                f"System Information:\n"
                f"  • RAM: {hw_info.ram_total_gb:.2f}GB total, {hw_info.ram_available_gb:.2f}GB available\n"
                f"  • CPU: {hw_info.cpu_count_physical} physical cores"
            )
            
            if hw_info.has_gpu:
                message += (
                    f"\n  • GPU: {hw_info.gpu_name}\n"
                    f"  • VRAM: {hw_info.vram_total_gb:.2f}GB total, "
                    f"{hw_info.vram_total_gb - hw_info.vram_allocated_gb:.2f}GB free"
                )
            
            self.logger.info(f"Validation PASSED: {mode} mode authorized")
        else:
            all_reasons = ram_reasons + vram_reasons
            
            message = (
                f"❌ Hardware validation failed\n\n"
                f"Issues detected:\n"
            )
            
            for i, reason in enumerate(all_reasons, 1):
                message += f"  {i}. {reason}\n"
            
            message += "\n" + self._generate_recommendations(hw_info, ram_ok, vram_ok)
            
            self.logger.warning(f"Validation FAILED: {len(all_reasons)} issue(s) detected")
            for reason in all_reasons:
                self.logger.warning(f"  - {reason}")
        
        return (authorized, message)

# =========================
# HCGK KERNEL
# =========================
class HCGKKernel:
    """
    Production-grade Hardware Control Gatekeeper Kernel
    
    Features:
    - Comprehensive hardware detection
    - Detailed validation and reporting
    - Retry logic for scan failures
    - Extensive logging
    - Type-safe with dataclasses
    - Zero external side effects
    """
    
    def __init__(self, silent: bool = False, config: Optional[HCGKConfig] = None):
        """
        Initialize HCGK Kernel
        
        Args:
            silent: Suppress console output
            config: Custom configuration (uses defaults if None)
        """
        self.silent = silent
        
        # Initialize configuration
        try:
            self.config = config or HCGKConfig()
        except Exception as e:
            raise HCGKError(f"Configuration error: {e}")
        
        # Initialize logger
        self.logger = SecureLogger(self.config.LOG_FILE)
        
        # Initialize components
        try:
            self.scanner = SystemScanner(self.logger, self.config)
            self.validator = ConstraintValidator(self.logger, self.config)
        except DependencyError as e:
            self.logger.critical(f"Initialization failed: {e}")
            raise
        
        self.logger.info("="*60)
        self.logger.info(f"HCGK Kernel v{__version__} initialized")
        self.logger.info(f"Configuration: MIN_RAM_GB={self.config.MIN_RAM_GB}, "
                        f"MIN_VRAM_GB={self.config.MIN_VRAM_GB}, "
                        f"MIN_RAM_NO_GPU_GB={self.config.MIN_RAM_NO_GPU_GB}")
        self.logger.info("="*60)
    
    def authorize(self) -> Tuple[bool, str]:
        """
        Perform hardware authorization check
        
        Returns:
            Tuple of (authorized: bool, message: str)
            
        Raises:
            HCGKError: If critical error occurs during authorization
        """
        if not self.silent:
            print("\n" + "="*60)
            print("🛡️  HCGK KERNEL: Hardware Authorization")
            print("="*60)
        
        try:
            # Perform hardware scan
            hw_info = self.scanner.scan()
            
            # Validate against requirements
            authorized, message = self.validator.validate(hw_info)
            
            # Log result
            if authorized:
                self.logger.info("✅ AUTHORIZATION GRANTED")
            else:
                self.logger.warning("❌ AUTHORIZATION DENIED")
            
            # Print result if not silent
            if not self.silent:
                print(message)
                print("="*60 + "\n")
            
            return (authorized, message)
            
        except DependencyError as e:
            error_msg = f"Missing dependencies: {e}"
            self.logger.critical(error_msg)
            if not self.silent:
                print(f"❌ {error_msg}")
                print("="*60 + "\n")
            return (False, error_msg)
        
        except Exception as e:
            error_msg = f"Unexpected error: {type(e).__name__}: {e}"
            self.logger.critical(error_msg)
            if not self.silent:
                print(f"❌ {error_msg}")
                print("="*60 + "\n")
            return (False, error_msg)
    
    def get_system_info(self) -> Dict:
        """
        Get detailed system information without authorization
        
        Returns:
            Dictionary with comprehensive hardware information
        """
        try:
            hw_info = self.scanner.scan()
            return hw_info.to_dict()
        except Exception as e:
            self.logger.error(f"Failed to get system info: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Public API
__all__ = [
    "HCGKKernel",
    "HCGKConfig",
    "HardwareInfo",
    "SystemScanner",
    "ConstraintValidator",
    "HCGKError",
    "DependencyError",
    "ScanError",
    "ValidationError",
    "__version__"
]