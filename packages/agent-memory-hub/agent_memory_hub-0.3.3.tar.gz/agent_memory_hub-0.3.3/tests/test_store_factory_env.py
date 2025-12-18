from agent_memory_hub.data_plane.adk_session_store import AdkSessionStore
from agent_memory_hub.data_plane.store_factory import StoreFactory


def test_get_store_with_environment():
    """Test that StoreFactory creates bucket name with environment."""
    store = StoreFactory.get_store(
        backend="adk",
        region="us-central1",
        bucket_prefix="my-prefix",
        environment="staging"
    )
    
    assert isinstance(store, AdkSessionStore)
    assert store.bucket_name == "my-prefix-us-central1-staging"
    assert store.region == "us-central1"

def test_get_store_default_environment():
    """Test that StoreFactory defaults to prod environment."""
    store = StoreFactory.get_store(
        backend="adk",
        region="us-central1",
        bucket_prefix="my-prefix"
    )
    
    # logic in store_factory.py uses default environment="prod" 
    # if not passed (though in get_store signature it defaults to "prod")
    assert store.bucket_name == "my-prefix-us-central1-prod"

def test_memory_client_integration_stub():
    """Verify MemoryClient propagates environment correctly (stub test)."""
    # This just ensures we can instantiate Client with environment
    from agent_memory_hub.client.memory_client import MemoryClient
    
    client = MemoryClient(
        agent_id="agent1",
        session_id="sess1",
        region="us-central1",
        environment="dev"
    )
    
    assert client.environment == "dev"
    # Inspect internal router store to verify bucket name
    # Note: MemoryClient._router is private, testing internals for verification
    store = client._router.store
    # Default prefix in MemoryRouter is "memory-hub" 
    # (via defaults or explicitly if we updated it)
    # StoreFactory default prefix is "memory-hub"
    assert store.bucket_name == "memory-hub-us-central1-dev"
