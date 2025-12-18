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
        return MemoryRouter(region_guard=mock_region_guard)
    
    def test_router_initialization(self, mock_region_guard):
        """Test that router initializes with region guard."""
        router = MemoryRouter(region_guard=mock_region_guard)
        assert router.region_guard == mock_region_guard
    
    @patch("agent_memory_hub.routing.memory_router.StoreFactory")
    def test_write_delegates_to_store(self, mock_factory, router):
        """Test that write operations are delegated to the session store."""
        mock_store = MagicMock()
        mock_factory.create_store.return_value = mock_store
        router._store = mock_store
        
        router.write("session1", "key1", "value1")
        
        mock_store.write.assert_called_once_with("session1", "key1", "value1")
    
    @patch("agent_memory_hub.routing.memory_router.StoreFactory")
    def test_read_delegates_to_store(self, mock_factory, router):
        """Test that read operations are delegated to the session store."""
        mock_store = MagicMock()
        mock_store.read.return_value = "stored_value"
        mock_factory.create_store.return_value = mock_store
        router._store = mock_store
        
        result = router.read("session1", "key1")
        
        mock_store.read.assert_called_once_with("session1", "key1")
        assert result == "stored_value"
    
    @patch("agent_memory_hub.routing.memory_router.StoreFactory")
    def test_store_lazy_initialization(self, mock_factory, router):
        """Test that store is lazily initialized on first use."""
        mock_store = MagicMock()
        mock_factory.create_store.return_value = mock_store
        
        # Store should not be created yet
        assert not hasattr(router, '_store') or router._store is None
        
        # First operation triggers initialization
        router.write("session1", "key1", "value1")
        
        mock_factory.create_store.assert_called_once()
