"""
Tests for pydantic semantic models.
"""
from agent_memory_hub.models import EpisodicMemory, MemoryScope, SemanticMemory


def test_episodic_memory_creation():
    mem = EpisodicMemory(
        agent_id="agent_1",
        content="User said hello",
        scope=MemoryScope.SESSION
    )
    assert mem.content == "User said hello"
    assert mem.scope == MemoryScope.SESSION
    assert "EpisodicMemory" in mem.to_dict()["memory_type"]

def test_semantic_memory_serialization():
    mem = SemanticMemory(
        agent_id="agent_1",
        subject="Sky",
        predicate="is",
        object="Blue"
    )
    data = mem.to_dict()
    assert data["subject"] == "Sky"
    assert data["memory_type"] == "SemanticMemory"
    assert data["agent_id"] == "agent_1"

def test_scope_enum():
    assert MemoryScope.USER == "user"
    assert MemoryScope.GLOBAL == "global"
