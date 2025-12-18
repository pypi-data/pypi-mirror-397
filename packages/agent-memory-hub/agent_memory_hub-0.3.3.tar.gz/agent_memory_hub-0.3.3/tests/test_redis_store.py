
import json
import unittest
from unittest.mock import MagicMock, patch

# Import assuming agent_memory_hub is in path
try:
    from agent_memory_hub.data_plane.redis_session_store import (
        REDIS_AVAILABLE,
        RedisConfig,
        RedisSessionStore,
    )
    from agent_memory_hub.utils.ttl_manager import get_current_timestamp
except ImportError:
    # Handle optional import failure in tests if deps not present
    REDIS_AVAILABLE = False
    RedisSessionStore = None

class TestRedisSessionStore(unittest.TestCase):
    
    def setUp(self):
        if not REDIS_AVAILABLE:
            self.skipTest("redis not installed")
            
        self.mock_redis_client = MagicMock()
        self.config = RedisConfig(host="localhost")
        
        with patch("redis.Redis", return_value=self.mock_redis_client):
            self.store = RedisSessionStore(config=self.config, ttl_seconds=3600)

    def test_write_with_ttl(self):
        value = "test-value"
        self.store.write("sess-1", "key-1", value)
        
        self.mock_redis_client.setex.assert_called_once()
        args = self.mock_redis_client.setex.call_args
        key = args[0][0]
        ttl = args[0][1]
        data = json.loads(args[0][2])
        
        self.assertEqual(key, "session:sess-1:key-1")
        self.assertEqual(ttl, 3600)
        self.assertEqual(data["value"], value)
        self.assertEqual(data["ttl_seconds"], 3600)

    def test_read_hit(self):
        mock_data = {
            "value": "found-value",
            "created_at": get_current_timestamp().isoformat(),
            "ttl_seconds": 3600
        }
        self.mock_redis_client.get.return_value = json.dumps(mock_data)
        
        result = self.store.read("sess-1", "key-1")
        self.assertEqual(result, "found-value")

    def test_read_miss(self):
        self.mock_redis_client.get.return_value = None
        result = self.store.read("sess-1", "missing")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
