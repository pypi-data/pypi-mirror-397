"""
Factory for creating session stores.
"""
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agent_memory_hub.config.alloydb_config import AlloyDBConfig

from agent_memory_hub.data_plane.adk_session_store import AdkSessionStore, SessionStore


class StoreFactory:
    """Factory to create the appropriate session store backend."""
    
    @staticmethod
    def get_store(
        backend: str = "adk", 
        region: str = "us-central1",
        bucket_prefix: str = "memory-hub",
        environment: str = "prod",
        ttl_seconds: Optional[int] = None,
        alloydb_config: Optional["AlloyDBConfig"] = None,
    ) -> SessionStore:
        """
        Returns a session store instance.
        
        Args:
            backend: Backend type ("adk" or "alloydb")
            region: GCP region
            bucket_prefix: Prefix for GCS bucket names (adk backend only)
            environment: Environment for GCS bucket names (e.g., "prod", "dev")
            ttl_seconds: Time-to-live in seconds (None = no expiry)
            alloydb_config: AlloyDB configuration (required for alloydb backend)
        """
        if backend == "adk":
            # Convention: memory-hub-{region}-prod or similar. 
            # Simplified for this example.
            bucket_name = f"{bucket_prefix}-{region}-{environment}"
            return AdkSessionStore(
                bucket_name=bucket_name, region=region, ttl_seconds=ttl_seconds
            )
        
        if backend == "alloydb":
            if alloydb_config is None:
                raise ValueError("alloydb_config is required for alloydb backend")
            
            from agent_memory_hub.data_plane.alloydb_session_store import (
                AlloyDBSessionStore,
            )
            
            return AlloyDBSessionStore(config=alloydb_config, ttl_seconds=ttl_seconds)
        
        raise ValueError(f"Unknown backend: {backend}")

