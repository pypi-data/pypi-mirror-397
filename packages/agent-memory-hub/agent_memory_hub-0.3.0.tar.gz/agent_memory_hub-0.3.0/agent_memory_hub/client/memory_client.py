"""
Public facing Memory Client.
"""

from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from agent_memory_hub.config.alloydb_config import AlloyDBConfig

from agent_memory_hub.config.regions import DEFAULT_REGION
from agent_memory_hub.control_plane.region_guard import RegionGuard
from agent_memory_hub.routing.memory_router import MemoryRouter
from agent_memory_hub.utils.telemetry import get_tracer


class MemoryClient:
    """
    Client for accessing agent memory with region governance.
    """

    def __init__(
        self,
        agent_id: str,
        session_id: str,
        region: str = DEFAULT_REGION,
        region_restricted: bool = True,
        backend: str = "adk",
        ttl_seconds: Optional[int] = None,
        alloydb_config: Optional["AlloyDBConfig"] = None,
        environment: str = "prod",
    ):
        """
        Initialize the MemoryClient.

        Args:
            agent_id: Unique identifier for the agent.
            session_id: Unique identifier for the session.
            region: The cloud region where memory should be stored/retrieved.
            region_restricted: If True, enforces strict region checks.
            backend: Storage backend ("adk" for GCS, "alloydb" for AlloyDB).
            ttl_seconds: Time-to-live in seconds (None = no expiry).
            alloydb_config: AlloyDB configuration (required if backend="alloydb").
            environment: Environment context (e.g., "prod", "dev") for resource naming.
        """
        self.agent_id = agent_id
        self.session_id = session_id
        self.region = region
        self.region_restricted = region_restricted
        self.backend = backend
        self.ttl_seconds = ttl_seconds
        self.environment = environment
        self._tracer = get_tracer()

        if region_restricted:
            self._guard = RegionGuard(region)
            self._router = MemoryRouter(
                region_guard=self._guard,
                backend=backend,
                ttl_seconds=ttl_seconds,
                alloydb_config=alloydb_config,
                environment=environment,
            )
        else:
            # Fallback or less strict mode not fully implemented in spec, 
            # assuming guard is always used but maybe with relaxed checks if requested.
            # For now, we strictly follow the requested design where region is passed.
            self._guard = RegionGuard(region)
            self._router = MemoryRouter(
                region_guard=self._guard,
                backend=backend,
                ttl_seconds=ttl_seconds,
                alloydb_config=alloydb_config,
                environment=environment,
            )

    def write(self, value: Any, key: str = "default") -> None:
        """
        Write a value to the memory store.

        Args:
            value: The data to store.
            key: specific key or context for the memory (e.g., 'episodic', 'semantic').
        """
        with self._tracer.start_as_current_span("MemoryClient.write") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("session.id", self.session_id)
            span.set_attribute("region", self.region)
            span.set_attribute("memory.key", key)
            
            # Composite key could include agent_id to namespace it
            composite_key = f"{self.agent_id}/{key}"
            self._router.write(self.session_id, composite_key, value)

    def recall(self, key: str = "default") -> Optional[Any]:
        """
        Recall a value from the memory store.

        Args:
            key: The key used during write.

        Returns:
            The stored value or None if not found.
        """
        with self._tracer.start_as_current_span("MemoryClient.recall") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("session.id", self.session_id)
            span.set_attribute("region", self.region)
            span.set_attribute("memory.key", key)
            
            composite_key = f"{self.agent_id}/{key}"
            return self._router.read(self.session_id, composite_key)

