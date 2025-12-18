"""Tests for RegionGuard control plane component."""
import pytest

from agent_memory_hub.config.regions import REGION_EUROPE_WEST1, REGION_US_CENTRAL1
from agent_memory_hub.control_plane.region_guard import RegionGuard


class TestRegionGuard:
    def test_valid_region_initialization(self):
        """Test that RegionGuard accepts valid regions."""
        guard = RegionGuard(REGION_US_CENTRAL1)
        assert guard.region == REGION_US_CENTRAL1
        
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
            assert guard.region == region
    
    def test_region_validation_method(self):
        """Test the validate_region method."""
        guard = RegionGuard(REGION_US_CENTRAL1)
        # Should not raise for valid region
        guard.validate_region(REGION_US_CENTRAL1)
        
        # Should raise for invalid region
        with pytest.raises(ValueError):
            guard.validate_region("mars-north1")
    
    def test_region_guard_immutability(self):
        """Test that region cannot be changed after initialization."""
        guard = RegionGuard(REGION_US_CENTRAL1)
        # original_region = guard.region
        
        # Attempt to modify (should not affect internal state if properly designed)
        with pytest.raises(AttributeError):
            guard.region = "new-region"
