"""Tests for error handling and edge cases."""
from unittest.mock import MagicMock, patch

import pytest

from agent_memory_hub import MemoryClient
from agent_memory_hub.config.regions import REGION_US_CENTRAL1
from agent_memory_hub.data_plane.adk_session_store import AdkSessionStore


class TestErrorHandling:
    @patch("google.cloud.storage.Client")
    def test_gcs_connection_failure(self, mock_storage_client):
        """Test handling of GCS connection failures."""
        from google.cloud.exceptions import GoogleCloudError
        
        mock_storage_client.side_effect = GoogleCloudError("Connection failed")
        
        store = AdkSessionStore("test-bucket", REGION_US_CENTRAL1)
        
        with pytest.raises(GoogleCloudError):
            store.write("session1", "key1", "value")
    
    @patch("google.cloud.storage.Client")
    def test_blob_upload_failure(self, mock_storage_client):
        """Test handling of blob upload failures."""
        from google.cloud.exceptions import GoogleCloudError
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_blob.upload_from_string.side_effect = GoogleCloudError("Upload failed")
        
        store = AdkSessionStore("test-bucket", REGION_US_CENTRAL1)
        
        with pytest.raises(GoogleCloudError):
            store.write("session1", "key1", "value")
    
    @patch("google.cloud.storage.Client")
    def test_invalid_json_in_storage(self, mock_storage_client):
        """Test handling of corrupted data in storage."""
        import json
        
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = "invalid json {{"
        
        store = AdkSessionStore("test-bucket", REGION_US_CENTRAL1)
        
        with pytest.raises(json.JSONDecodeError):
            store.read("session1", "key1")
    
    @patch("google.cloud.storage.Client")
    def test_large_payload_handling(self, mock_storage_client):
        """Test that large payloads are handled correctly."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Create a large payload (1MB of data)
        large_data = "x" * (1024 * 1024)
        
        client = MemoryClient("agent1", "session1", REGION_US_CENTRAL1)
        
        # Should not raise an error
        client.write(large_data, "large_key")
        
        mock_blob.upload_from_string.assert_called_once()
    
    def test_empty_session_id(self):
        """Test that empty session IDs are handled."""
        with pytest.raises((ValueError, TypeError)):
            MemoryClient("agent1", "", REGION_US_CENTRAL1)
    
    def test_empty_agent_id(self):
        """Test that empty agent IDs are handled."""
        with pytest.raises((ValueError, TypeError)):
            MemoryClient("", "session1", REGION_US_CENTRAL1)
    
    @patch("google.cloud.storage.Client")
    def test_special_characters_in_keys(self, mock_storage_client):
        """Test handling of special characters in memory keys."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        client = MemoryClient("agent1", "session1", REGION_US_CENTRAL1)
        
        # Keys with special characters
        special_keys = [
            "key/with/slashes",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots"
        ]
        
        for key in special_keys:
            client.write("data", key)
            # Should not raise errors
        
        assert mock_blob.upload_from_string.call_count == len(special_keys)
    
    @patch("google.cloud.storage.Client")
    def test_concurrent_write_same_key(self, mock_storage_client):
        """Test behavior when writing to the same key concurrently."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        client = MemoryClient("agent1", "session1", REGION_US_CENTRAL1)
        
        # Simulate concurrent writes (last write wins in GCS)
        client.write("value1", "key1")
        client.write("value2", "key1")
        
        # Both writes should succeed
        assert mock_blob.upload_from_string.call_count == 2
    
    @patch("google.cloud.storage.Client")
    def test_read_nonexistent_key_returns_none(self, mock_storage_client):
        """Test that reading a non-existent key returns None."""
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        mock_blob.exists.return_value = False
        
        client = MemoryClient("agent1", "session1", REGION_US_CENTRAL1)
        result = client.recall("nonexistent_key")
        
        assert result is None
