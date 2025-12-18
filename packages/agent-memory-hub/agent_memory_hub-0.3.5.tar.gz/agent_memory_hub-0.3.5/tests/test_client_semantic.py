"""
Tests for MemoryClient semantic model support.
"""
from unittest.mock import MagicMock

from agent_memory_hub import MemoryClient
from agent_memory_hub.models import MemoryScope, SemanticMemory


def test_client_write_model():
    # specialized client mock not needed if we mock the router
    client = MemoryClient(agent_id="test", session_id="s1", region_restricted=False)
    client._router = MagicMock()
    
    mem = SemanticMemory(
        agent_id="test",
        subject="User",
        predicate="likes",
        object="Pizza",
        scope=MemoryScope.USER
    )
    
    client.write_model(mem)
    
    # Verify router called with serialized dict
    args = client._router.write.call_args[0]
    session_id, key, value = args
    
    assert session_id == "s1"
    assert "semanticmemory" in key # key format: type/id
    assert value["subject"] == "User"
    assert value["memory_type"] == "SemanticMemory"
