"""
Abstract base class definition for session stores and a concrete 
Google ADK-compatible implementation.
"""

import abc
import json
from typing import Any, Optional

from agent_memory_hub.utils.telemetry import get_tracer


class SessionStore(abc.ABC):
    """Abstract interface for memory storage backends."""
    
    @abc.abstractmethod
    def write(self, session_id: str, key: str, value: Any) -> None:
        """Persist a value associated with a session and key."""
        pass

    @abc.abstractmethod
    def read(self, session_id: str, key: str) -> Optional[Any]:
        """Retrieve a value by session and key."""
        pass


class AdkSessionStore(SessionStore):
    """
    Google ADK-compatible session store implementation. 
    Uses Google Cloud Storage as the underlying persistence layer.
    """
    
    def __init__(self, bucket_name: str, region: str):
        self.bucket_name = bucket_name
        self.region = region
        self._tracer = get_tracer()
        # Lazy initialization to avoid runtime side effects on import
        self._client = None
        self._bucket = None

    def _get_bucket(self):
        if self._bucket:
            return self._bucket
            
        # Import here to avoid import-time network calls/side effects
        from google.cloud import storage  # type: ignore
        
        if not self._client:
            self._client = storage.Client()
            
        self._bucket = self._client.bucket(self.bucket_name)
        # In a real ADK scenario, we might verify bucket location matches self.region
        return self._bucket

    def _get_blob_path(self, session_id: str, key: str) -> str:
        return f"sessions/{session_id}/{key}.json"

    def write(self, session_id: str, key: str, value: Any) -> None:
        with self._tracer.start_as_current_span("AdkSessionStore.write") as span:
            blob_path = self._get_blob_path(session_id, key)
            span.set_attribute("bucket.name", self.bucket_name)
            span.set_attribute("object.key", blob_path)
            
            bucket = self._get_bucket()
            blob = bucket.blob(blob_path)
            blob.upload_from_string(
                json.dumps({"value": value}), 
                content_type="application/json"
            )

    def read(self, session_id: str, key: str) -> Optional[Any]:
        with self._tracer.start_as_current_span("AdkSessionStore.read") as span:
            blob_path = self._get_blob_path(session_id, key)
            span.set_attribute("bucket.name", self.bucket_name)
            span.set_attribute("object.key", blob_path)
            
            bucket = self._get_bucket()
            blob = bucket.blob(blob_path)
            
            if not blob.exists():
                return None
                
            content = blob.download_as_text()
            data = json.loads(content)
            return data.get("value")
