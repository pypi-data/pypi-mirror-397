"""
Base models for the semantic memory system.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class MemoryScope(str, Enum):
    """
    Defines the scope/visibility of a memory.
    """
    USER = "user"       # Private to a specific user
    AGENT = "agent"     # Private to the agent identity
    SESSION = "session" # Ephemeral, bound to a session
    TEAM = "team"       # Shared across a team/tenant
    GLOBAL = "global"   # System-wide knowledge


class BaseMemory(BaseModel):
    """
    Base class for all memory types.
    """
    model_config = ConfigDict(extra="allow")

    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    agent_id: str
    scope: MemoryScope = MemoryScope.SESSION
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Optional reliability/importance scores
    confidence: float = 1.0
    importance: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        # Using model_dump (pydantic v2)
        data = self.model_dump(mode="json")
        # Inject validation type for polymorphic loading later
        data["memory_type"] = self.__class__.__name__
        return data
