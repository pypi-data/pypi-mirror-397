"""
Specific memory type definitions.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import Field

from agent_memory_hub.models.base import BaseMemory, MemoryScope


class EpisodicMemory(BaseMemory):
    """
    Represents an event or interaction.
    Example: "User engaged in conversation about football on Sunday."
    """
    content: str
    source: str = "conversation" # e.g. conversation, tool_output, external_event
    participants: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    

class SemanticMemory(BaseMemory):
    """
    Represents a fact or piece of knowledge.
    Example: (User, likes, Football)
    """
    subject: str
    predicate: str
    object: str
    truth_score: float = 1.0
    evidence: Optional[str] = None # Reference to source (e.g., source episode ID)


class EntityMemory(BaseMemory):
    """
    Represents a profile for an entity (User, Agent, Organization).
    """
    entity_id: str
    entity_type: str # e.g. "user", "agent", "organization"
    attributes: Dict[str, Any] = Field(default_factory=dict)
    
    # Override default scope for entities to be higher
    scope: MemoryScope = MemoryScope.GLOBAL


class ProceduralMemory(BaseMemory):
    """
    Represents a skill or tool usage pattern.
    """
    skill_name: str
    steps: List[str]
    success_rate: float = 0.0
    execution_count: int = 0
