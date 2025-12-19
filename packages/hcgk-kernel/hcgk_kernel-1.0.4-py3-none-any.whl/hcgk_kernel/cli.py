#!/usr/bin/env python3
"""
HCGK Kernel CLI
Command-line interface for Hardware Control Gatekeeper Kernel
"""

import sys
import json
import argparse
from typing import Optional
from hcgk_kernel import HCGKKernel, HCGKConfig, __version__


def format_size(gb: float) -> str:
    """Format size in GB with proper units"""
    if gb < 1:
        return f"{gb * 1024:.0f} MB"
    return f"{gb:.2f} GB"


def cmd_check(args) -> int:
    """Check hardware authorization"""
    try:
        kernel = HCGKKernel(silent=args.silent)
        authorized, message = kernel.authorize()
        
        if not args.silent:
            if authorized:
                print(f"\n✅ Status: AUTHORIZED")
            else:
                print(f"\n❌ Status: DENIED")
            
            if args.verbose:
                print(f"\nDetails:\n{message}")
        
        return 0 if authorized else 1
        
    except Exception as e:
        if not args.silent:
            print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_info(args) -> int:
    """Display detailed system information"""
    try:
        kernel = HCGKKernel(silent=True)
        info = kernel.get_system_info()
        
        if not info.get("success"):
            print(f"❌ Failed to scan system: {info.get('error')}")
            return 1
        
        # Output format
        if args.json:
            print(json.dumps(info, indent=2))
            return 0
        
        # Human-readable format
        print("\n" + "="*60)
        print("🖥️  SYSTEM INFORMATION")
        print("="*60)
        
        # System
        system = info.get("system", {})
        print(f"\nSystem:")
        print(f"  Platform:       {system.get('platform', 'Unknown')}")
        print(f"  Python:         {system.get('python_version', 'Unknown')}")
        
        # RAM
        ram = info.get("ram", {})
        print(f"\nRAM:")
        print(f"  Total:          {format_size(ram.get('total_gb', 0))}")
        print(f"  Available:      {format_size(ram.get('available_gb', 0))}")
        print(f"  Used:           {ram.get('percent_used', 0):.1f}%")
        
        # CPU
        cpu = info.get("cpu", {})
        print(f"\nCPU:")
        print(f"  Physical Cores: {cpu.get('physical_cores', 0)}")
        print(f"  Logical Cores:  {cpu.get('logical_cores', 0)}")
        print(f"  Usage:          {cpu.get('percent_used', 0):.1f}%")
        
        # GPU
        gpu = info.get("gpu", {})
        print(f"\nGPU:")
        print(f"  Available:      {'Yes' if gpu.get('available') else 'No'}")
        
        if gpu.get('available'):
            print(f"  Count:          {gpu.get('count', 0)}")
            print(f"  Name:           {gpu.get('name', 'Unknown')}")
            print(f"  VRAM Total:     {format_size(gpu.get('vram_total_gb', 0))}")
            print(f"  VRAM Allocated: {format_size(gpu.get('vram_allocated_gb', 0))}")
            print(f"  VRAM Reserved:  {format_size(gpu.get('vram_reserved_gb', 0))}")
            
            vram_free = gpu.get('vram_total_gb', 0) - gpu.get('vram_allocated_gb', 0)
            print(f"  VRAM Free:      {format_size(vram_free)}")
        
        # Requirements check
        if args.requirements:
            config = HCGKConfig()
            print("\n" + "-"*60)
            print("REQUIREMENTS CHECK")
            print("-"*60)
            
            if gpu.get('available'):
                print(f"\nGPU Mode Requirements:")
                print(f"  Min RAM:        {format_size(config.MIN_RAM_GB)}")
                print(f"  Min VRAM:       {format_size(config.MIN_VRAM_GB)}")
                
                ram_ok = ram.get('total_gb', 0) >= config.MIN_RAM_GB
                vram_ok = gpu.get('vram_total_gb', 0) >= config.MIN_VRAM_GB
                
                print(f"\nStatus:")
                print(f"  RAM Check:      {'✅ PASS' if ram_ok else '❌ FAIL'}")
                print(f"  VRAM Check:     {'✅ PASS' if vram_ok else '❌ FAIL'}")
                print(f"  Overall:        {'✅ PASS' if (ram_ok and vram_ok) else '❌ FAIL'}")
            else:
                print(f"\nCPU Mode Requirements:")
                print(f"  Min RAM:        {format_size(config.MIN_RAM_NO_GPU_GB)}")
                
                ram_ok = ram.get('total_gb', 0) >= config.MIN_RAM_NO_GPU_GB
                
                print(f"\nStatus:")
                print(f"  RAM Check:      {'✅ PASS' if ram_ok else '❌ FAIL'}")
                print(f"  Overall:        {'✅ PASS' if ram_ok else '❌ FAIL'}")
        
        print("="*60 + "\n")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_config(args) -> int:
    """Display current configuration"""
    try:
        config = HCGKConfig()
        
        if args.json:
            config_dict = {
                "version": __version__,
                "min_ram_gb": config.MIN_RAM_GB,
                "min_vram_gb": config.MIN_VRAM_GB,
                "min_ram_no_gpu_gb": config.MIN_RAM_NO_GPU_GB,
                "ram_safety_margin": config.RAM_SAFETY_MARGIN,
                "max_scan_retries": config.MAX_SCAN_RETRIES,
                "strict_mode": config.STRICT_MODE,
                "log_directory": str(config.KERNEL_LOG_DIR)
            }
            print(json.dumps(config_dict, indent=2))
            return 0
        
        print("\n" + "="*60)
        print("⚙️  HCGK CONFIGURATION")
        print("="*60)
        print(f"\nVersion:                {__version__}")
        print(f"\nHardware Requirements:")
        print(f"  Min RAM (GPU mode):   {format_size(config.MIN_RAM_GB)}")
        print(f"  Min VRAM:             {format_size(config.MIN_VRAM_GB)}")
        print(f"  Min RAM (CPU mode):   {format_size(config.MIN_RAM_NO_GPU_GB)}")
        print(f"\nSafety Settings:")
        print(f"  RAM Safety Margin:    {config.RAM_SAFETY_MARGIN * 100:.0f}%")
        print(f"  Max Scan Retries:     {config.MAX_SCAN_RETRIES}")
        print(f"  Strict Mode:          {'Enabled' if config.STRICT_MODE else 'Disabled'}")
        print(f"\nLogging:")
        print(f"  Log Directory:        {config.KERNEL_LOG_DIR}")
        print(f"  Log File:             {config.LOG_FILE}")
        
        print("\nEnvironment Variables:")
        print("  HCGK_MIN_RAM_GB            - Minimum RAM for GPU mode")
        print("  HCGK_MIN_VRAM_GB           - Minimum VRAM required")
        print("  HCGK_MIN_RAM_NO_GPU_GB     - Minimum RAM for CPU mode")
        print("  HCGK_RAM_SAFETY_MARGIN     - RAM safety margin (0.0-1.0)")
        print("  HCGK_MAX_SCAN_RETRIES      - Maximum scan retry attempts")
        print("  HCGK_STRICT_MODE           - Enable strict validation (true/false)")
        print("="*60 + "\n")
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


def cmd_validate(args) -> int:
    """Validate configuration without running authorization"""
    try:
        config = HCGKConfig()
        print("✅ Configuration is valid")
        return 0
    except Exception as e:
        print(f"❌ Configuration error: {e}", file=sys.stderr)
        return 1


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="hcgk",
        description="HCGK Kernel - Hardware Control Gatekeeper for AI Models",
        epilog=f"Version {__version__} | Created by Matias Nisperuza."
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"HCGK Kernel v{__version__}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check hardware authorization"
    )
    check_parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Suppress output (exit code only)"
    )
    check_parser.add_argument(
        "-V", "--verbose",
        action="store_true",
        help="Show detailed validation messages"
    )
    check_parser.set_defaults(func=cmd_check)
    
    # Info command
    info_parser = subparsers.add_parser(
        "info",
        help="Display detailed system information"
    )
    info_parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output in JSON format"
    )
    info_parser.add_argument(
        "-r", "--requirements",
        action="store_true",
        help="Include requirements check"
    )
    info_parser.set_defaults(func=cmd_info)
    
    # Config command
    config_parser = subparsers.add_parser(
        "config",
        help="Display configuration"
    )
    config_parser.add_argument(
        "-j", "--json",
        action="store_true",
        help="Output in JSON format"
    )
    config_parser.set_defaults(func=cmd_config)
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration"
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())