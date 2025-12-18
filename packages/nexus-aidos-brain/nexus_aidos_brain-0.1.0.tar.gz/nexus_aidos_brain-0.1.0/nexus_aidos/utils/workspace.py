"""
Workspace utilities for multi-tenant support.

Provides workspace isolation and validation.
"""

import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def validate_workspace_id(workspace_id: str) -> bool:
    """
    Validate workspace ID format.
    
    Args:
        workspace_id: Workspace identifier
    
    Returns:
        True if valid, False otherwise
    """
    if not workspace_id:
        return False
    
    # Allow alphanumeric, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9_-]+$'
    return bool(re.match(pattern, workspace_id))


def get_workspace_key(workspace_id: str, key_type: str, identifier: Optional[str] = None) -> str:
    """
    Generate a workspace-scoped key for Redis/storage.
    
    Args:
        workspace_id: Workspace identifier
        key_type: Type of key (e.g., 'cache', 'memory', 'session')
        identifier: Optional additional identifier
    
    Returns:
        Formatted workspace key
    
    Example:
        >>> get_workspace_key('ws123', 'cache', 'query1')
        'nexus:ws:ws123:cache:query1'
    """
    if not validate_workspace_id(workspace_id):
        raise ValueError(f"Invalid workspace_id: {workspace_id}")
    
    parts = ['nexus', 'ws', workspace_id, key_type]
    if identifier:
        parts.append(identifier)
    
    return ':'.join(parts)


def extract_workspace_from_key(key: str) -> Optional[str]:
    """
    Extract workspace ID from a formatted key.
    
    Args:
        key: Formatted workspace key
    
    Returns:
        Workspace ID or None if not found
    
    Example:
        >>> extract_workspace_from_key('nexus:ws:ws123:cache:query1')
        'ws123'
    """
    parts = key.split(':')
    if len(parts) >= 3 and parts[0] == 'nexus' and parts[1] == 'ws':
        return parts[2]
    return None
