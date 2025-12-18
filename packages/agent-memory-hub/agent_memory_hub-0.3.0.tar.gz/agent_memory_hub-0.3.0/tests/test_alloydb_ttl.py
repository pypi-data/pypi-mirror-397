from typing import Any, Dict
from unittest.mock import patch

import pytest

from agent_memory_hub.config.alloydb_config import AlloyDBConfig
from agent_memory_hub.data_plane.alloydb_session_store import AlloyDBSessionStore


# Mocks to simulate ADK classes
class MockSession:
    def __init__(self, id, app_name, user_id):
        self.id = id
        self.state: Dict[str, Any] = {}

class MockDatabaseSessionService:
    def __init__(self, database_uri, pool_size, max_overflow):
        self.sessions: Dict[str, MockSession] = {}

    def get_session(self, session_id: str) -> MockSession:
        return self.sessions[session_id]

    def create_session(self, session: MockSession) -> None:
        self.sessions[session.id] = session

    def update_session(self, session: MockSession) -> None:
        self.sessions[session.id] = session

@pytest.fixture
def store():
    cfg = AlloyDBConfig(
        user="test",
        password="test", # noqa: S106
        database="testdb",
        instance_connection_name="proj:region:inst",
        pool_size=1,
        max_overflow=0,
    )
    
    # We must patch multiple things because the module might not have ADK installed
    with patch(
        "agent_memory_hub.data_plane.alloydb_session_store.ADK_AVAILABLE", True
    ), \
         patch("agent_memory_hub.data_plane.alloydb_session_store.DatabaseSessionService", 
               MockDatabaseSessionService), \
         patch(
             "agent_memory_hub.data_plane.alloydb_session_store.Session", MockSession
         ):
         
        s = AlloyDBSessionStore(config=cfg, ttl_seconds=1)
        # We don't need to manually replace session_service now because 
        # __init__ will use our MockDatabaseSessionService from the patch
        return s

def test_write_and_read_within_ttl(store):
    store.write("sess1", "key1", "value1")
    assert store.read("sess1", "key1") == "value1"

def test_expiry_after_ttl(store):
    store.write("sess2", "key2", "value2")
    # Wait longer than the 1‑second TTL
    import time
    time.sleep(1.5)
    assert store.read("sess2", "key2") is None
