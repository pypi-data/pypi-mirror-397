"""Tests for AdkSessionStore GCS backend."""
import json
from unittest.mock import MagicMock, patch

import pytest

from agent_memory_hub.data_plane.adk_session_store import AdkSessionStore


class TestAdkSessionStore:
    @pytest.fixture
    def store(self):
        """Create an AdkSessionStore instance."""
        return AdkSessionStore("test-bucket", "us-central1")
    
    def test_store_initialization(self, store):
        """Test that store initializes with bucket and region."""
        assert store.bucket_name == "test-bucket"
        assert store.region == "us-central1"
        assert store._client is None  # Lazy initialization
        assert store._bucket is None
    
    def test_blob_path_generation(self, store):
        """Test that blob paths are generated correctly."""
        path = store._get_blob_path("session123", "memory_key")
        assert path == "sessions/session123/memory_key.json"
    
    @patch("agent_memory_hub.data_plane.adk_session_store.storage")
    def test_write_operation(self, mock_storage, store):
        """Test write operation uploads to GCS."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        store.write("session1", "key1", {"data": "test"})
        
        # Verify blob was created with correct path
        mock_bucket.blob.assert_called_with("sessions/session1/key1.json")
        
        # Verify upload was called
        mock_blob.upload_from_string.assert_called_once()
        call_args = mock_blob.upload_from_string.call_args
        uploaded_data = json.loads(call_args[0][0])
        assert uploaded_data["value"] == {"data": "test"}
    
    @patch("agent_memory_hub.data_plane.adk_session_store.storage")
    def test_read_existing_blob(self, mock_storage, store):
        """Test reading an existing blob from GCS."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = '{"value": "retrieved_data"}'
        
        result = store.read("session1", "key1")
        
        assert result == "retrieved_data"
        mock_blob.exists.assert_called_once()
        mock_blob.download_as_text.assert_called_once()
    
    @patch("agent_memory_hub.data_plane.adk_session_store.storage")
    def test_read_nonexistent_blob(self, mock_storage, store):
        """Test reading a non-existent blob returns None."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_blob.exists.return_value = False
        
        result = store.read("session1", "nonexistent_key")
        
        assert result is None
        mock_blob.exists.assert_called_once()
        mock_blob.download_as_text.assert_not_called()
    
    @patch("agent_memory_hub.data_plane.adk_session_store.storage")
    def test_lazy_client_initialization(self, mock_storage, store):
        """Test that GCS client is lazily initialized."""
        mock_client = MagicMock()
        mock_bucket = MagicMock()
        
        mock_storage.Client.return_value = mock_client
        mock_client.bucket.return_value = mock_bucket
        
        # Client should not be initialized yet
        assert store._client is None
        
        # First call to _get_bucket initializes client
        bucket = store._get_bucket()
        
        assert store._client is not None
        assert store._bucket is not None
        mock_storage.Client.assert_called_once()
        
        # Second call reuses existing bucket
        bucket2 = store._get_bucket()
        assert bucket2 is bucket
        mock_storage.Client.assert_called_once()  # Still only called once
