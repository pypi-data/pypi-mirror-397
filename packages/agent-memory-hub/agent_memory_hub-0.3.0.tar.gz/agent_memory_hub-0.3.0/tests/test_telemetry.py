import unittest
from unittest.mock import MagicMock

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from agent_memory_hub.client.memory_client import MemoryClient
from agent_memory_hub.data_plane.adk_session_store import AdkSessionStore


class TestTelemetry(unittest.TestCase):
    def setUp(self):
        # Set up in-memory exporter
        self.exporter = InMemorySpanExporter()
        provider = TracerProvider()
        processor = SimpleSpanProcessor(self.exporter)
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
        
    def test_client_write_span(self):
        client = MemoryClient(
            "test-agent", "test-session", region="us-central1", region_restricted=False
        )
        # Mock internal router to avoid side effects
        client._router = MagicMock()
        
        client.write("data", "episodic")
        
        spans = self.exporter.get_finished_spans()
        # We might get other spans if other tests ran? No, new instance per test.
        # but global tracer provider might persist?
        # TracerProvider is global if set via trace.set_tracer_provider
        
        client_spans = [s for s in spans if s.name == "MemoryClient.write"]
        self.assertTrue(len(client_spans) >= 1)
        span = client_spans[-1] # Get latest
        self.assertEqual(span.attributes["agent.id"], "test-agent")
        self.assertEqual(span.attributes["memory.key"], "episodic")

    def test_store_write_span(self):
        store = AdkSessionStore("test-bucket", "us-central1")
        # Mock interactions
        store._get_bucket = MagicMock()
        store._get_bucket = MagicMock()
        store._get_bucket.return_value.blob.return_value \
            .upload_from_string = MagicMock()
        
        store.write("sess", "key", "val")
        
        spans = self.exporter.get_finished_spans()
        store_spans = [s for s in spans if s.name == "AdkSessionStore.write"]
        self.assertTrue(len(store_spans) >= 1)
        span = store_spans[-1]
        self.assertEqual(span.attributes["bucket.name"], "test-bucket")
