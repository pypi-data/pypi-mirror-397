"""
TTL (Time-To-Live) management utilities.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional


def get_expiry_timestamp(ttl_seconds: Optional[int]) -> Optional[datetime]:
    """
    Calculate expiry timestamp from TTL seconds.
    
    Args:
        ttl_seconds: Time-to-live in seconds, None for no expiry
        
    Returns:
        Expiry timestamp in UTC, or None if no TTL
    """
    if ttl_seconds is None:
        return None
    return datetime.now(timezone.utc) + timedelta(seconds=ttl_seconds)


def is_expired(created_at: datetime, ttl_seconds: Optional[int]) -> bool:
    """
    Check if an entry has expired based on creation time and TTL.
    
    Args:
        created_at: When the entry was created (UTC)
        ttl_seconds: Time-to-live in seconds, None for no expiry
        
    Returns:
        True if expired, False otherwise
    """
    if ttl_seconds is None:
        return False
    
    expiry_time = created_at + timedelta(seconds=ttl_seconds)
    return datetime.now(timezone.utc) > expiry_time


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp."""
    return datetime.now(timezone.utc)
