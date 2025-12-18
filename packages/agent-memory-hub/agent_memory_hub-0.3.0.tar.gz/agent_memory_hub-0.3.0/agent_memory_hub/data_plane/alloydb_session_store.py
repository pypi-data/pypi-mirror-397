"""
AlloyDB (PostgreSQL) session store implementation using ADK's DatabaseSessionService.
"""
from typing import Any, Optional

try:
    from google.adk.sessions import DatabaseSessionService, Session
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

from agent_memory_hub.config.alloydb_config import AlloyDBConfig
from agent_memory_hub.data_plane.adk_session_store import SessionStore
from agent_memory_hub.utils.telemetry import get_tracer
from agent_memory_hub.utils.ttl_manager import get_current_timestamp, is_expired


class AlloyDBSessionStore(SessionStore):
    """
    AlloyDB (PostgreSQL) session store using ADK's DatabaseSessionService.
    Leverages ADK's built-in session management for better ecosystem integration.
    """

    def __init__(
        self,
        config: AlloyDBConfig,
        ttl_seconds: Optional[int] = None,
    ):
        """
        Initialize AlloyDB session store using ADK's DatabaseSessionService.

        Args:
            config: AlloyDB connection configuration
            ttl_seconds: Default TTL for entries (None = no expiry)
        
        Raises:
            ImportError: If google-adk is not installed
        """
        if not ADK_AVAILABLE:
            raise ImportError(
                "google-adk is required for AlloyDB backend. "
                "Install with: pip install google-adk"
            )
        
        self.config = config
        self.ttl_seconds = ttl_seconds
        self._tracer = get_tracer()

        # Create ADK DatabaseSessionService with PostgreSQL connection
        database_uri = (
            f"postgresql+psycopg2://{config.user}:{config.password}@"
            f"/{config.database}?host=/cloudsql/{config.instance_connection_name}"
        )
        
        self.session_service = DatabaseSessionService(
            database_uri=database_uri,
            pool_size=config.pool_size,
            max_overflow=config.max_overflow,
        )

    def write(self, session_id: str, key: str, value: Any) -> None:
        """
        Write a value using ADK's session service.

        Args:
            session_id: Session identifier
            key: Memory key
            value: Value to store
        """
        with self._tracer.start_as_current_span("AlloyDBSessionStore.write") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            span.set_attribute("database", self.config.database)

            # Get or create ADK session
            try:
                session = self.session_service.get_session(session_id)
            except Exception:
                # Session doesn't exist, create it
                session = Session(
                    id=session_id,
                    app_name="agent-memory-hub",
                    user_id="system",
                )
                self.session_service.create_session(session)

            # Store value in session state with TTL metadata
            metadata = {
                "value": value,
                "created_at": get_current_timestamp().isoformat(),
                "ttl_seconds": self.ttl_seconds,
            }
            
            # Update session state
            if not hasattr(session, 'state') or session.state is None:
                session.state = {}
            session.state[key] = metadata
            
            self.session_service.update_session(session)

    def read(self, session_id: str, key: str) -> Optional[Any]:
        """
        Read a value using ADK's session service.

        Args:
            session_id: Session identifier
            key: Memory key

        Returns:
            Stored value or None if not found/expired
        """
        with self._tracer.start_as_current_span("AlloyDBSessionStore.read") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            span.set_attribute("database", self.config.database)

            try:
                session = self.session_service.get_session(session_id)
            except Exception:
                return None

            if not hasattr(session, 'state') or session.state is None:
                return None

            if key not in session.state:
                return None

            metadata = session.state[key]
            
            # Check for TTL expiry
            if isinstance(metadata, dict) and "created_at" in metadata:
                from datetime import datetime
                created_at = datetime.fromisoformat(metadata["created_at"])
                ttl = metadata.get("ttl_seconds")
                
                if ttl is not None and is_expired(created_at, ttl):
                    # Delete expired entry
                    del session.state[key]
                    self.session_service.update_session(session)
                    return None
                
                return metadata.get("value")
            
            # Backward compatibility for non-metadata values
            return metadata

    def cleanup_expired(self, session_id: Optional[str] = None) -> int:
        """
        Manually cleanup expired entries using ADK's session service.

        Args:
            session_id: Optional session ID to limit cleanup scope

        Returns:
            Number of entries deleted
        """
        from datetime import datetime
        
        deleted_count = 0
        
        if session_id:
            # Cleanup specific session
            try:
                session = self.session_service.get_session(session_id)
                if hasattr(session, 'state') and session.state:
                    keys_to_delete = []
                    for key, metadata in session.state.items():
                        if isinstance(metadata, dict) and "created_at" in metadata:
                            created_at = datetime.fromisoformat(metadata["created_at"])
                            ttl = metadata.get("ttl_seconds")
                            if ttl and is_expired(created_at, ttl):
                                keys_to_delete.append(key)
                    
                    for key in keys_to_delete:
                        del session.state[key]
                        deleted_count += 1
                    
                    if keys_to_delete:
                        self.session_service.update_session(session)
            except Exception: # noqa: S110
                pass
        else:
            # Cleanup all sessions (expensive operation)
            # Note: ADK doesn't provide list_all_sessions, so this is limited
            # In production, consider using a scheduled job with direct DB access
            pass
        
        return deleted_count
