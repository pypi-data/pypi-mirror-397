"""Integration tests for end-to-end flows."""
from unittest.mock import MagicMock, patch

from agent_memory_hub import MemoryClient
from agent_memory_hub.config.regions import REGION_US_CENTRAL1


class TestIntegration:
    @patch("google.cloud.storage.Client")
    def test_end_to_end_write_read_flow(self, mock_storage_client):
        """Test complete flow from client to storage and back."""
        # Setup mocks
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        
        # Simulate successful write
        mock_blob.upload_from_string = MagicMock()
        
        # Simulate successful read
        mock_blob.exists.return_value = True
        mock_blob.download_as_text.return_value = '{"value": "test_data"}'
        
        # Create client and perform operations
        client = MemoryClient(
            agent_id="integration_agent",
            session_id="session_123",
            region=REGION_US_CENTRAL1
        )
        
        # Write
        client.write("test_data", "episodic")
        
        # Read
        result = client.recall("episodic")
        
        assert result == "test_data"
        mock_blob.upload_from_string.assert_called_once()
        mock_blob.download_as_text.assert_called_once()
    
    @patch("google.cloud.storage.Client")
    def test_multi_session_isolation(self, mock_storage_client):
        """Test that different sessions are isolated."""
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # Track blob paths
        blob_paths = []
        def track_blob(path):
            blob_paths.append(path)
            mock_blob = MagicMock()
            mock_blob.upload_from_string = MagicMock()
            return mock_blob
        
        mock_bucket.blob.side_effect = track_blob
        
        # Create two clients with different sessions
        client1 = MemoryClient("agent1", "session_A", REGION_US_CENTRAL1)
        client2 = MemoryClient("agent1", "session_B", REGION_US_CENTRAL1)
        
        client1.write("data_A", "key1")
        client2.write("data_B", "key1")
        
        # Verify different blob paths were used
        assert len(blob_paths) == 2
        assert "session_A" in blob_paths[0]
        assert "session_B" in blob_paths[1]
    
    @patch("google.cloud.storage.Client")
    def test_telemetry_span_propagation(self, mock_storage_client):
        """Test that telemetry spans are created throughout the stack."""
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import SimpleSpanProcessor
        from opentelemetry.sdk.trace.export.in_memory_span_exporter import (
            InMemorySpanExporter,
        )
        
        # Setup telemetry
        exporter = InMemorySpanExporter()
        provider = TracerProvider()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        
        # Setup storage mocks
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob
        mock_blob.upload_from_string = MagicMock()
        
        # Perform operation
        client = MemoryClient("agent1", "session1", REGION_US_CENTRAL1)
        client.write("data", "key")
        
        # Verify spans were created
        spans = exporter.get_finished_spans()
        span_names = [s.name for s in spans]
        
        assert "MemoryClient.write" in span_names
        assert "AdkSessionStore.write" in span_names
    
    @patch("google.cloud.storage.Client")
    def test_region_restricted_mode(self, mock_storage_client):
        """Test that region_restricted=True enforces validation."""
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        
        # This should work fine
        client = MemoryClient(
            "agent1", 
            "session1", 
            REGION_US_CENTRAL1,
            region_restricted=True
        )
        
        # Verify region guard is active
        assert client.region_restricted is True
        assert client._guard is not None
