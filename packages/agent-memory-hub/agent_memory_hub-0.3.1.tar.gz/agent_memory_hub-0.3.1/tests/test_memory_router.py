"""Tests for MemoryRouter routing layer."""
from unittest.mock import MagicMock, patch

import pytest

from agent_memory_hub.config.regions import REGION_US_CENTRAL1
from agent_memory_hub.control_plane.region_guard import RegionGuard
from agent_memory_hub.routing.memory_router import MemoryRouter


class TestMemoryRouter:
    @pytest.fixture
    def mock_region_guard(self):
        """Create a mock RegionGuard."""
        guard = MagicMock(spec=RegionGuard)
        guard.current_region = REGION_US_CENTRAL1
        return guard
    
    @pytest.fixture
    def router(self, mock_region_guard):
        """Create a MemoryRouter with mocked dependencies."""
        with patch(
        "agent_memory_hub.routing.memory_router.StoreFactory"
    ) as mock_factory:
            mock_store = MagicMock()
            mock_factory.get_store.return_value = mock_store
            
            router = MemoryRouter(region_guard=mock_region_guard)
            
            # Attach mock for verification
            router._mock_store = mock_store
            router._mock_factory = mock_factory
            return router
    
    def test_router_initialization(self, mock_region_guard, router):
        """Test that router initializes with region guard."""
        assert router.region_guard == mock_region_guard
        # Check that store was initialized (eagerly)
        router._mock_factory.get_store.assert_called_once()
        assert router.store == router._mock_store
    
    def test_write_delegates_to_store(self, router):
        """Test that write operations are delegated to the session store."""
        router.write("session1", "key1", "value1")
        
        router._mock_store.write.assert_called_once_with("session1", "key1", "value1")
    
    def test_read_delegates_to_store(self, router):
        """Test that read operations are delegated to the session store."""
        router._mock_store.read.return_value = "stored_value"
        
        result = router.read("session1", "key1")
        
        router._mock_store.read.assert_called_once_with("session1", "key1")
        assert result == "stored_value"
