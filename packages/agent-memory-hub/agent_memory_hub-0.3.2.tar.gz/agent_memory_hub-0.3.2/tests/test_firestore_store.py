
import unittest
from unittest.mock import MagicMock, patch

try:
    from agent_memory_hub.data_plane.firestore_session_store import (
        FIRESTORE_AVAILABLE,
        FirestoreSessionStore,
    )
    from agent_memory_hub.utils.ttl_manager import get_current_timestamp
except ImportError:
    FIRESTORE_AVAILABLE = False
    FirestoreSessionStore = None

class TestFirestoreSessionStore(unittest.TestCase):
    
    def setUp(self):
        if not FIRESTORE_AVAILABLE:
            self.skipTest("firestore not installed")
            
        self.mock_firestore_client = MagicMock()
        self.mock_doc = MagicMock()
        self.mock_collection = MagicMock()
        
        # Setup chain: client -> collection -> doc
        self.mock_firestore_client.collection.return_value = self.mock_collection
        self.mock_collection.document.return_value = self.mock_doc
        
        with patch(
            "google.cloud.firestore.Client", 
            return_value=self.mock_firestore_client
        ):
            self.store = FirestoreSessionStore(collection="test-mem", ttl_seconds=3600)

    def test_write(self):
        self.store.write("sess-1", "key-1", "value-1")
        
        self.mock_doc.set.assert_called_once()
        args, kwargs = self.mock_doc.set.call_args
        
        self.assertTrue(kwargs.get("merge"))
        self.assertIn("key-1", args[0])
        self.assertEqual(args[0]["key-1"]["value"], "value-1")

    def test_read_hit(self):
        mock_data = {
            "key-1": {
                "value": "found-value",
                "created_at": get_current_timestamp().isoformat(),
                "ttl_seconds": 3600
            }
        }
        mock_snapshot = MagicMock()
        mock_snapshot.exists = True
        mock_snapshot.to_dict.return_value = mock_data
        self.mock_doc.get.return_value = mock_snapshot
        
        result = self.store.read("sess-1", "key-1")
        self.assertEqual(result, "found-value")

    def test_read_miss(self):
        mock_snapshot = MagicMock()
        mock_snapshot.exists = False
        self.mock_doc.get.return_value = mock_snapshot
        
        result = self.store.read("sess-1", "missing")
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
