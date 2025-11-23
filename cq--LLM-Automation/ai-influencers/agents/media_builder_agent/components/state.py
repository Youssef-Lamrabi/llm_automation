"""
Media Builder Agent State
"""

from typing import TypedDict, Optional


class MediaBuilderState(TypedDict, total=False):
    """State for media builder agent."""
    
    # Input
    content: str
    platform: str
    persona: dict
    topic: str
    
    # Output
    image_prompt: str
    image_data: Optional[bytes]
    media_status: str
    error: Optional[str]
