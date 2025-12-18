"""
Redis session store implementation.
"""
import json
from typing import Any, Optional

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from agent_memory_hub.config.redis_config import RedisConfig
from agent_memory_hub.data_plane.adk_session_store import SessionStore
from agent_memory_hub.utils.telemetry import get_tracer
from agent_memory_hub.utils.ttl_manager import get_current_timestamp


class RedisSessionStore(SessionStore):
    """
    Redis-based session store for low-latency memory.
    """

    def __init__(
        self,
        config: RedisConfig,
        ttl_seconds: Optional[int] = None,
    ):
        """
        Initialize Redis session store.

        Args:
            config: Redis connection configuration
            ttl_seconds: Default TTL for entries (None = no expiry)
        
        Raises:
            ImportError: If redis is not installed
        """
        if not REDIS_AVAILABLE:
            raise ImportError(
                "redis is required for Redis backend. "
                "Install with: pip install redis"
            )
        
        self.config = config
        self.ttl_seconds = ttl_seconds
        self._tracer = get_tracer()

        self._client = redis.Redis(
            host=config.host,
            port=config.port,
            db=config.db,
            password=config.password,
            ssl=config.ssl,
            decode_responses=True # Ensure we get strings back
        )

    def _get_redis_key(self, session_id: str, key: str) -> str:
        return f"session:{session_id}:{key}"

    def write(self, session_id: str, key: str, value: Any) -> None:
        """
        Write a value to Redis.

        Args:
            session_id: Session identifier
            key: Memory key
            value: Value to store
        """
        with self._tracer.start_as_current_span("RedisSessionStore.write") as span:
            redis_key = self._get_redis_key(session_id, key)
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)
            span.set_attribute("redis.key", redis_key)

            # Wrapper for metadata
            data = {
                "value": value,
                "created_at": get_current_timestamp().isoformat(),
                "ttl_seconds": self.ttl_seconds,
            }
            
            # Serialize
            serialized = json.dumps(data)
            
            # Set in Redis with TTL if configured
            if self.ttl_seconds:
                self._client.setex(redis_key, self.ttl_seconds, serialized)
            else:
                self._client.set(redis_key, serialized)

    def read(self, session_id: str, key: str) -> Optional[Any]:
        """
        Read a value from Redis.

        Args:
            session_id: Session identifier
            key: Memory key

        Returns:
            Stored value or None if not found
        """
        with self._tracer.start_as_current_span("RedisSessionStore.read") as span:
            redis_key = self._get_redis_key(session_id, key)
            span.set_attribute("session.id", session_id)
            span.set_attribute("memory.key", key)

            serialized = self._client.get(redis_key)
            
            if not serialized:
                return None
            
            try:
                data = json.loads(serialized)
                return data.get("value")
            except json.JSONDecodeError:
                return None

    def cleanup_expired(self, session_id: Optional[str] = None) -> int:
        """
        No-op for Redis as it handles TTL natively.
        
        Args:
            session_id: Ignored for Redis
            
        Returns:
            0
        """
        # Redis handles TTL automatically
        return 0
