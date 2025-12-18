"""
Configuration for Redis connections.
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class RedisConfig:
    """
    Configuration for connecting to Redis (e.g., Google Cloud Memorystore).
    
    Attributes:
        host: Redis host address
        port: Redis port (default: 6379)
        db: Redis database index (default: 0)
        password: Redis password (optional)
        ssl: Whether to use SSL (default: False, true for some Memorystore configs)
    """
    host: str
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False

    @classmethod
    def from_env(cls) -> "RedisConfig":
        """
        Create config from environment variables.
        
        Expected env vars:
        - REDIS_HOST
        - REDIS_PORT
        - REDIS_DB
        - REDIS_PASSWORD
        - REDIS_SSL
        """
        return cls(
            host=os.environ["REDIS_HOST"],
            port=int(os.environ.get("REDIS_PORT", "6379")),
            db=int(os.environ.get("REDIS_DB", "0")),
            password=os.environ.get("REDIS_PASSWORD"),
            ssl=os.environ.get("REDIS_SSL", "False").lower() == "true",
        )
