"""
AlloyDB (PostgreSQL) session store implementation using SQLAlchemy.
"""
from typing import Any, Optional
import json
from datetime import datetime

from sqlalchemy import create_engine, text, Table, Column, String, MetaData
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import SQLAlchemyError

from agent_memory_hub.config.alloydb_config import AlloyDBConfig
from agent_memory_hub.data_plane.adk_session_store import SessionStore
from agent_memory_hub.utils.telemetry import get_tracer
from agent_memory_hub.utils.ttl_manager import get_current_timestamp, is_expired


class AlloyDBSessionStore(SessionStore):
    """
    AlloyDB (PostgreSQL) session store using generic SQLAlchemy.
    Stores sessions in a 'sessions' table: (session_id TEXT PK, data JSONB).
    """

    def __init__(
        self,
        config: AlloyDBConfig,
        ttl_seconds: Optional[int] = None,
    ):
        """
        Initialize AlloyDB session store.

        Args:
            config: AlloyDB connection configuration
            ttl_seconds: Default TTL for entries (None = no expiry)
        """
        self.config = config
        self.ttl_seconds = ttl_seconds
        self._tracer = get_tracer()

        # Construct Connection URI or Engine
        if config.db_url:
            self.engine = create_engine(
                config.db_url,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                pool_pre_ping=True
            )
        else:
            # Use Google Cloud AlloyDB Connector
            # This handles auth and connection establishment automatically (no manual proxy needed)
            try:
                from google.cloud.alloydb.connector import Connector
            except ImportError:
                raise ImportError(
                    "google-cloud-alloydb-connector is required when db_url is not provided. "
                    "Install with: pip install 'agent-memory-hub[alloydb]'"
                )

            # Keep reference to connector to prevent GC closing the loop (if applicable)
            self._connector = Connector()

            def getconn():
                conn = self._connector.connect(
                    config.instance_connection_name,
                    "psycopg2",
                    user=config.user,
                    password=config.password,
                    db=config.database,
                )
                return conn

            self.engine = create_engine(
                "postgresql+psycopg2://",
                creator=getconn,
                pool_size=config.pool_size,
                max_overflow=config.max_overflow,
                pool_pre_ping=True
            )
        
        # Ensure schema exists using raw SQL
        self._init_schema()

    def _init_schema(self):
        """Create sessions table if not exists."""
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            data JSONB NOT NULL DEFAULT '{}'::jsonb
        );
        """
        try:
            with self.engine.begin() as conn:
                conn.execute(text(create_table_sql))
        except SQLAlchemyError as e:
            # Fallback or log if this fails (e.g. read-only user)
            pass

    def write(self, session_id: str, key: str, value: Any) -> None:
        """
        Write a value to the session state in DB.
        UPSERT implementation:
        1. Read existing json.
        2. Merge new key/value.
        3. Write back.
        (Note: PostgreSQL allow updates to jsonb paths directly, which is more efficient)
        """
        with self._tracer.start_as_current_span("AlloyDBSessionStore.write") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            span.set_attribute("database", self.config.database)

            metadata = {
                "value": value,
                "created_at": get_current_timestamp().isoformat(),
                "ttl_seconds": self.ttl_seconds,
            }
            
            # Using PostgreSQL JSONB_SET for atomic valid path update if row exists,
            # Or INSERT behavior. 
            # Simplified: INSERT ON CONFLICT DO UPDATE
            
            # Prepare metadata JSON string
            meta_json = json.dumps(metadata)
            
            sql = text("""
                INSERT INTO sessions (session_id, data)
                VALUES (:sid, jsonb_build_object(:key, :meta::jsonb))
                ON CONFLICT (session_id) 
                DO UPDATE SET data = sessions.data || jsonb_build_object(:key, :meta::jsonb);
            """)
            
            try:
                with self.engine.begin() as conn:
                    conn.execute(sql, {"sid": session_id, "key": key, "meta": meta_json})
            except SQLAlchemyError:
                raise

    def read(self, session_id: str, key: str) -> Optional[Any]:
        """
        Read a value from DB.
        """
        with self._tracer.start_as_current_span("AlloyDBSessionStore.read") as span:
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            
            # Query specific key path
            sql = text("""
                SELECT data->:key FROM sessions WHERE session_id = :sid
            """)
            
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(sql, {"sid": session_id, "key": key}).scalar()
                    
                if result is None:
                    return None
                
                # SQLAlchemy/Psycopg2 might return dict for JSONB or str
                metadata = result if isinstance(result, dict) else json.loads(result)
                
                # Check TTL
                if isinstance(metadata, dict) and "created_at" in metadata:
                    created_at = datetime.fromisoformat(metadata["created_at"])
                    ttl = metadata.get("ttl_seconds")
                    if ttl is not None and is_expired(created_at, ttl):
                        # Lazy delete? Or just return None.
                        # For read performance, we just return None. 
                        # Cleanup job handles real deletion.
                        return None
                    return metadata.get("value")
                
                return metadata
                
            except SQLAlchemyError:
                return None

    def cleanup_expired(self, session_id: Optional[str] = None) -> int:
        """
        Cleanup expired entries via Logic.
        Since we store data in JSONB, we have to iterate or use complex SQL.
        Hard deletion inside JSONB used here.
        """
        count = 0
        
        # NOTE: Cleaning up inside JSONB efficiently requires logic.
        # This simple implementation fetches the session, cleans it, and updates it.
        # Ideally, use a relational schema for high-throughput expiration.
        
        if session_id:
            # Clean single session
            select_sql = text("SELECT data FROM sessions WHERE session_id = :sid FOR UPDATE")
            update_sql = text("UPDATE sessions SET data = :data WHERE session_id = :sid")
            
            try:
                with self.engine.begin() as conn:
                    data = conn.execute(select_sql, {"sid": session_id}).scalar()
                    if not data:
                        return 0
                    
                    if isinstance(data, str):
                        data = json.loads(data)
                        
                    keys_to_del = []
                    for k, v in data.items():
                        if isinstance(v, dict) and "created_at" in v:
                            # Check expiry
                            created_at = datetime.fromisoformat(v["created_at"])
                            ttl = v.get("ttl_seconds")
                            if ttl and is_expired(created_at, ttl):
                                keys_to_del.append(k)
                    
                    if keys_to_del:
                        for k in keys_to_del:
                            del data[k]
                        conn.execute(update_sql, {"sid": session_id, "data": json.dumps(data)})
                        count = len(keys_to_del)
            except SQLAlchemyError:
                pass
                
        return count

