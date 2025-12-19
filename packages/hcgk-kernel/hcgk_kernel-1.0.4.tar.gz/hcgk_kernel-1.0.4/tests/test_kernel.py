"""
Comprehensive unit tests for HCGK Kernel
"""

import pytest
import os
from hcgk_kernel import (
    HCGKKernel,
    HCGKConfig,
    SystemScanner,
    HardwareInfo,
    HCGKError,
    DependencyError,
    __version__
)


class TestHCGKConfig:
    """Test suite for HCGKConfig"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = HCGKConfig()
        assert config.MIN_RAM_GB > 0
        assert config.MIN_VRAM_GB > 0
        assert config.MIN_RAM_NO_GPU_GB > 0
        assert 0 <= config.RAM_SAFETY_MARGIN < 1
        assert config.MAX_SCAN_RETRIES >= 1
    
    def test_config_validation_positive_values(self):
        """Test configuration validates positive values"""
        with pytest.raises(ValueError):
            HCGKConfig(MIN_RAM_GB=-1)
        
        with pytest.raises(ValueError):
            HCGKConfig(MIN_VRAM_GB=0)
    
    def test_config_validation_safety_margin(self):
        """Test configuration validates safety margin range"""
        with pytest.raises(ValueError):
            HCGKConfig(RAM_SAFETY_MARGIN=-0.1)
        
        with pytest.raises(ValueError):
            HCGKConfig(RAM_SAFETY_MARGIN=1.5)
    
    def test_config_validation_retries(self):
        """Test configuration validates retry count"""
        with pytest.raises(ValueError):
            HCGKConfig(MAX_SCAN_RETRIES=0)
    
    def test_config_from_environment(self):
        """Test configuration reads from environment variables"""
        os.environ["HCGK_MIN_RAM_GB"] = "16.0"
        os.environ["HCGK_MIN_VRAM_GB"] = "8.0"
        
        config = HCGKConfig()
        assert config.MIN_RAM_GB == 16.0
        assert config.MIN_VRAM_GB == 8.0
        
        # Cleanup
        del os.environ["HCGK_MIN_RAM_GB"]
        del os.environ["HCGK_MIN_VRAM_GB"]


class TestHardwareInfo:
    """Test suite for HardwareInfo"""
    
    def test_hardware_info_creation(self):
        """Test HardwareInfo can be created"""
        info = HardwareInfo(
            success=True,
            timestamp="2025-12-17T10:00:00",
            ram_total_gb=16.0,
            ram_available_gb=8.0
        )
        assert info.success is True
        assert info.ram_total_gb == 16.0
    
    def test_hardware_info_to_dict(self):
        """Test HardwareInfo converts to dictionary"""
        info = HardwareInfo(
            success=True,
            timestamp="2025-12-17T10:00:00",
            ram_total_gb=16.0
        )
        data = info.to_dict()
        
        assert isinstance(data, dict)
        assert data["success"] is True
        assert "ram" in data
        assert "cpu" in data
        assert "gpu" in data
        assert "system" in data
    
    def test_hardware_info_with_error(self):
        """Test HardwareInfo with error information"""
        info = HardwareInfo(
            success=False,
            timestamp="2025-12-17T10:00:00",
            error="Test error"
        )
        assert info.success is False
        assert info.error == "Test error"


class TestHCGKKernel:
    """Test suite for HCGKKernel"""
    
    def test_version(self):
        """Test version is set correctly"""
        assert __version__ is not None
        assert isinstance(__version__, str)
        parts = __version__.split('.')
        assert len(parts) == 3
        assert all(part.isdigit() for part in parts)
    
    def test_kernel_initialization_default(self):
        """Test kernel initializes with defaults"""
        kernel = HCGKKernel(silent=True)
        assert kernel is not None
        assert kernel.scanner is not None
        assert kernel.validator is not None
        assert kernel.config is not None
    
    def test_kernel_initialization_custom_config(self):
        """Test kernel initializes with custom config"""
        config = HCGKConfig(MIN_RAM_GB=16.0, MIN_VRAM_GB=8.0)
        kernel = HCGKKernel(silent=True, config=config)
        
        assert kernel.config.MIN_RAM_GB == 16.0
        assert kernel.config.MIN_VRAM_GB == 8.0
    
    def test_authorization_returns_tuple(self):
        """Test authorize method returns proper tuple"""
        kernel = HCGKKernel(silent=True)
        result = kernel.authorize()
        
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], str)
        assert len(result[1]) > 0
    
    def test_authorization_handles_errors_gracefully(self):
        """Test authorization handles errors without crashing"""
        kernel = HCGKKernel(silent=True)
        
        # Should not raise exception even if something goes wrong
        try:
            authorized, message = kernel.authorize()
            assert isinstance(authorized, bool)
            assert isinstance(message, str)
        except Exception as e:
            pytest.fail(f"Authorization raised unexpected exception: {e}")
    
    def test_get_system_info_returns_dict(self):
        """Test get_system_info returns dictionary"""
        kernel = HCGKKernel(silent=True)
        info = kernel.get_system_info()
        
        assert isinstance(info, dict)
        assert "success" in info
    
    def test_get_system_info_structure(self):
        """Test get_system_info returns complete structure"""
        kernel = HCGKKernel(silent=True)
        info = kernel.get_system_info()
        
        if info.get("success"):
            assert "ram" in info
            assert "cpu" in info
            assert "gpu" in info
            assert "system" in info
            assert "timestamp" in info
            
            # Check nested structures
            assert "total_gb" in info["ram"]
            assert "available_gb" in info["ram"]
            assert "physical_cores" in info["cpu"]
            assert "available" in info["gpu"]


class TestSystemScanner:
    """Test suite for SystemScanner"""
    
    def test_scanner_validates_dependencies(self):
        """Test scanner checks for required dependencies"""
        # This should not raise if dependencies are installed
        from hcgk_kernel import SecureLogger
        config = HCGKConfig()
        logger = SecureLogger(config.LOG_FILE)
        
        try:
            scanner = SystemScanner(logger, config)
            assert scanner is not None
        except DependencyError:
            # Expected if dependencies are missing
            pass
    
    def test_scanner_scan_returns_hardware_info(self):
        """Test scanner returns HardwareInfo object"""
        from hcgk_kernel import SecureLogger
        config = HCGKConfig()
        logger = SecureLogger(config.LOG_FILE)
        
        try:
            scanner = SystemScanner(logger, config)
            result = scanner.scan()
            
            assert isinstance(result, HardwareInfo)
            assert hasattr(result, 'success')
            assert hasattr(result, 'timestamp')
        except DependencyError:
            pytest.skip("Dependencies not available")
    
    def test_scanner_scan_has_valid_data(self):
        """Test scanner returns sensible data"""
        from hcgk_kernel import SecureLogger
        config = HCGKConfig()
        logger = SecureLogger(config.LOG_FILE)
        
        try:
            scanner = SystemScanner(logger, config)
            result = scanner.scan()
            
            if result.success:
                # RAM should be positive
                assert result.ram_total_gb > 0
                assert result.ram_available_gb >= 0
                assert result.ram_available_gb <= result.ram_total_gb
                
                # CPU should have cores
                assert result.cpu_count_physical > 0
                assert result.cpu_count_logical >= result.cpu_count_physical
                
                # GPU info should be consistent
                if result.has_gpu:
                    assert result.gpu_count > 0
                    assert result.vram_total_gb >= 0
                else:
                    assert result.gpu_count == 0
        except DependencyError:
            pytest.skip("Dependencies not available")


# Pytest fixtures
@pytest.fixture
def kernel():
    """Fixture to create a kernel instance"""
    return HCGKKernel(silent=True)


@pytest.fixture
def custom_config():
    """Fixture to create a custom config"""
    return HCGKConfig(
        MIN_RAM_GB=8.0,
        MIN_VRAM_GB=4.0,
        MIN_RAM_NO_GPU_GB=16.0
    )


@pytest.fixture
def system_info(kernel):
    """Fixture to get system info"""
    return kernel.get_system_info()


# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    def test_full_authorization_flow(self, kernel):
        """Test complete authorization workflow"""
        authorized, message = kernel.authorize()
        
        # Should always return valid response
        assert isinstance(authorized, bool)
        assert isinstance(message, str)
        assert len(message) > 0
        
        # Message should contain relevant info
        if authorized:
            assert "✅" in message or "passed" in message.lower()
        else:
            assert "❌" in message or "failed" in message.lower()
    
    def test_system_info_completeness(self, system_info):
        """Test system info contains all expected fields"""
        assert "success" in system_info
        
        if system_info.get("success"):
            # Core fields
            assert "timestamp" in system_info
            assert "ram" in system_info
            assert "cpu" in system_info
            assert "gpu" in system_info
            assert "system" in system_info
            
            # RAM fields
            ram = system_info["ram"]
            assert "total_gb" in ram
            assert "available_gb" in ram
            assert "percent_used" in ram
            
            # CPU fields
            cpu = system_info["cpu"]
            assert "physical_cores" in cpu
            assert "logical_cores" in cpu
            
            # GPU fields
            gpu = system_info["gpu"]
            assert "available" in gpu
            assert "count" in gpu
    
    def test_custom_config_affects_authorization(self, custom_config):
        """Test custom configuration affects authorization"""
        kernel = HCGKKernel(silent=True, config=custom_config)
        
        assert kernel.config.MIN_RAM_GB == custom_config.MIN_RAM_GB
        assert kernel.config.MIN_VRAM_GB == custom_config.MIN_VRAM_GB
        
        # Should still be able to authorize
        authorized, message = kernel.authorize()
        assert isinstance(authorized, bool)
        assert isinstance(message, str)
    
    def test_multiple_authorization_calls(self, kernel):
        """Test kernel can handle multiple authorization calls"""
        results = []
        
        for _ in range(3):
            authorized, message = kernel.authorize()
            results.append((authorized, message))
        
        # All calls should return valid results
        assert len(results) == 3
        assert all(isinstance(r[0], bool) for r in results)
        assert all(isinstance(r[1], str) for r in results)
        
        # Results should be consistent
        authorizations = [r[0] for r in results]
        assert len(set(authorizations)) == 1, "Authorization should be deterministic"


# Error handling tests
class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_config_raises_error(self):
        """Test invalid configuration raises appropriate errors"""
        with pytest.raises(ValueError):
            HCGKConfig(MIN_RAM_GB=-1)
        
        with pytest.raises(ValueError):
            HCGKConfig(RAM_SAFETY_MARGIN=2.0)
    
    def test_kernel_handles_scan_failures_gracefully(self, kernel):
        """Test kernel doesn't crash on scan failures"""
        # Even if scan fails, should return valid tuple
        result = kernel.authorize()
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_get_system_info_on_failure(self, kernel):
        """Test get_system_info returns error dict on failure"""
        info = kernel.get_system_info()
        assert isinstance(info, dict)
        
        if not info.get("success"):
            assert "error" in info