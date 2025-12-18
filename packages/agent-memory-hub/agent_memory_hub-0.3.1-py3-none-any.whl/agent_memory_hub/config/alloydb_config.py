"""
Configuration for AlloyDB connections.
"""
from dataclasses import dataclass


@dataclass
class AlloyDBConfig:
    """
    Configuration for connecting to GCP AlloyDB (PostgreSQL).
    
    Attributes:
        instance_connection_name: Format: project:region:instance
        database: Database name
        user: Database user
        password: Database password (prefer Secret Manager in production)
        region: GCP region for the AlloyDB instance
        pool_size: Connection pool size (default: 5)
        max_overflow: Max overflow connections (default: 10)
    """
    instance_connection_name: str
    database: str
    user: str
    password: str
    region: str
    pool_size: int = 5
    max_overflow: int = 10
    
    def get_connection_string(self) -> str:
        """
        Get SQLAlchemy connection string for AlloyDB.
        
        Returns:
            Connection string in format: postgresql+psycopg2://user:pass@/db
        """
        return (
            f"postgresql+psycopg2://{self.user}:{self.password}@/"
            f"{self.database}"
        )
    
    @classmethod
    def from_env(cls) -> "AlloyDBConfig":
        """
        Create config from environment variables.
        
        Expected env vars:
        - ALLOYDB_INSTANCE: Instance connection name
        - ALLOYDB_DATABASE: Database name
        - ALLOYDB_USER: Database user
        - ALLOYDB_PASSWORD: Database password
        - ALLOYDB_REGION: GCP region
        """
        import os
        
        return cls(
            instance_connection_name=os.environ["ALLOYDB_INSTANCE"],
            database=os.environ["ALLOYDB_DATABASE"],
            user=os.environ["ALLOYDB_USER"],
            password=os.environ["ALLOYDB_PASSWORD"],
            region=os.environ.get("ALLOYDB_REGION", "us-central1"),
        )
