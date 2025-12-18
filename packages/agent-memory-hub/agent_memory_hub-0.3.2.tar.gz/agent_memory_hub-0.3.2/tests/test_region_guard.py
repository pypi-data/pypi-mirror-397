"""Tests for RegionGuard control plane component."""
import pytest

from agent_memory_hub.config.regions import REGION_EUROPE_WEST1, REGION_US_CENTRAL1
from agent_memory_hub.control_plane.region_guard import RegionGuard


class TestRegionGuard:
    def test_valid_region_initialization(self):
        """Test that RegionGuard accepts valid regions."""
        guard = RegionGuard(REGION_US_CENTRAL1)
        # Implementation uses 'current_region' property
        assert guard.current_region == REGION_US_CENTRAL1
        
    def test_invalid_region_raises_error(self):
        """Test that invalid regions raise ValueError."""
        with pytest.raises(
            ValueError, match="Region 'invalid-region' is not supported"
        ):
            RegionGuard("invalid-region")
    
    def test_all_supported_regions(self):
        """Test that all defined regions are accepted."""
        valid_regions = [REGION_US_CENTRAL1, REGION_EUROPE_WEST1, "asia-south1"]
        for region in valid_regions:
            guard = RegionGuard(region)
            assert guard.current_region == region
    
    def test_region_validation_method(self):
        """Test the validate_region method."""
        guard = RegionGuard(REGION_US_CENTRAL1)
        # Should return True for valid region
        assert guard.validate_region(REGION_US_CENTRAL1) is True
        
        # Should return False for invalid region (does not raise)
        assert guard.validate_region("mars-north1") is False

        # check_residency should raise
        with pytest.raises(RuntimeError):
            guard.check_residency("mars-north1")
    
    def test_region_guard_immutability(self):
        """Test that region cannot be changed after initialization."""
        guard = RegionGuard(REGION_US_CENTRAL1)
        
        # current_region is a property without a setter, so setting it should fail
        with pytest.raises(AttributeError):
            guard.current_region = "new-region"
