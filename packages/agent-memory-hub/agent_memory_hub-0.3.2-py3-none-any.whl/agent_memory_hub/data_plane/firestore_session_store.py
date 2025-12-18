"""
Firestore session store implementation.
"""
from datetime import datetime
from typing import Any, Optional

try:
    from google.cloud import firestore
    FIRESTORE_AVAILABLE = True
except ImportError:
    FIRESTORE_AVAILABLE = False

from agent_memory_hub.data_plane.adk_session_store import SessionStore
from agent_memory_hub.utils.telemetry import get_tracer
from agent_memory_hub.utils.ttl_manager import get_current_timestamp, is_expired


class FirestoreSessionStore(SessionStore):
    """
    Firestore-based session store for serverless, flexible memory.
    """

    def __init__(
        self,
        collection: str = "agent_memory",
        project: Optional[str] = None,
        ttl_seconds: Optional[int] = None,
    ):
        """
        Initialize Firestore session store.

        Args:
            collection: Root collection name for memory
            project: GCP project ID (optional, inferred from env)
            ttl_seconds: Default TTL for entries (None = no expiry)
        """
        if not FIRESTORE_AVAILABLE:
            raise ImportError(
                "google-cloud-firestore is required for Firestore backend. "
                "Install with: pip install google-cloud-firestore"
            )
        
        self.collection_name = collection
        self.ttl_seconds = ttl_seconds
        self._tracer = get_tracer()
        
        # Initialize client
        self._db = firestore.Client(project=project)

    def _get_doc_ref(self, session_id: str):
        return self._db.collection(self.collection_name).document(session_id)

    def write(self, session_id: str, key: str, value: Any) -> None:
        """
        Write a value to Firestore.
        
        Structure: Collection(collection_name) -> Doc(session_id) -> Field(key)
        Stores complex object: { "value": ..., "created_at": ..., "ttl_seconds": ... }
        """
        with self._tracer.start_as_current_span("FirestoreSessionStore.write") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            
            doc_ref = self._get_doc_ref(session_id)
            
            # Metadata wrapper
            metadata = {
                "value": value,
                "created_at": get_current_timestamp().isoformat(),
                "ttl_seconds": self.ttl_seconds,
            }
            
            # Merge into document (create if not exists)
            doc_ref.set({key: metadata}, merge=True)

    def read(self, session_id: str, key: str) -> Optional[Any]:
        """
        Read a value from Firestore.
        """
        with self._tracer.start_as_current_span("FirestoreSessionStore.read") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            
            doc_ref = self._get_doc_ref(session_id)
            snapshot = doc_ref.get()
            
            if not snapshot.exists:
                return None
            
            data = snapshot.to_dict()
            if key not in data:
                return None
                
            entry = data[key]
            
            # Check TTL
            if (
                isinstance(entry, dict) 
                and "created_at" in entry 
                and "ttl_seconds" in entry
            ):
                created_at = datetime.fromisoformat(entry["created_at"])
                ttl = entry["ttl_seconds"]
                
                if ttl is not None and is_expired(created_at, ttl):
                    # Delete specific field
                    doc_ref.update({key: firestore.DELETE_FIELD})
                    return None
                
                return entry.get("value")
            
            # Fallback
            return entry

    def cleanup_expired(self, session_id: Optional[str] = None) -> int:
        """
        Cleanup expired entries.
        
        Args:
            session_id: If provided, only cleans that session.
            
        Returns:
            Number of deleted fields.
        """
        # Note: Scannning all docs is expensive in Firestore. 
        # This implementation assumes scoped usage.
        
        count = 0
        
        if session_id:
            docs = [self._get_doc_ref(session_id).get()]
        else:
            # WARNING: Full scan
            docs = self._db.collection(self.collection_name).stream()
            
        for snapshot in docs:
            if not snapshot.exists:
                continue
                
            data = snapshot.to_dict()
            updates = {}
            for key, entry in data.items():
                if (
                    isinstance(entry, dict) 
                    and "created_at" in entry 
                    and "ttl_seconds" in entry
                ):
                    created_at = datetime.fromisoformat(entry["created_at"])
                    ttl = entry["ttl_seconds"]
                    if ttl and is_expired(created_at, ttl):
                        updates[key] = firestore.DELETE_FIELD
                        count += 1
            
            if updates:
                snapshot.reference.update(updates)
                
        return count
