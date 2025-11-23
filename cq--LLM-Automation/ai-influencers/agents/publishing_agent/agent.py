"""
Publishing Agent - Integration wrapper for orchestrator.

This module provides a clean interface for the orchestrator to use the 
existing publishing system. It wraps the prepare_post and publish_post
functions from nodes.py.
"""

from typing import Dict, Any
from datetime import datetime
from .components.nodes import prepare_post, publish_post
from .components.state import PublishState


def publish_content(
    content: str,
    hashtags: str = "",
    platform: str = "Twitter",
    scheduled_time: str = None,
    persona: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Main publishing function that orchestrator can call.
    
    Args:
        content: The main content to publish
        hashtags: Hashtags to include
        platform: Target platform (Twitter, LinkedIn, etc.)
        scheduled_time: ISO format timestamp
        persona: Persona information dict
        
    Returns:
        Dict with publication results including status, post_id, post_url, etc.
    """
    
    # Default values
    if scheduled_time is None:
        scheduled_time = datetime.now().isoformat()
    
    if persona is None:
        persona = {"Persona_ID": "neuralNinja"}
    
    # Parse scheduled_time
    if "T" in scheduled_time:
        date_part = scheduled_time.split("T")[0]
        time_part = scheduled_time.split("T")[1].replace("Z", "")
    else:
        date_part = datetime.now().strftime("%Y-%m-%d")
        time_part = datetime.now().strftime("%H:%M:%S")
    
    # Create entry in publishing agent's expected format
    entry = {
        "Content": content,
        "Hashtags": hashtags,
        "Platform": platform,
        "Date": date_part,
        "Time": time_part,
        "Persona": persona.get("Persona_ID", "neuralNinja")
    }
    
    try:
        # Step 1: Prepare the post
        prepared_state = prepare_post(entry)
        
        # Step 2: Publish the post
        result = publish_post(prepared_state)
        
        # Return unified result
        return {
            "status": result.get("status"),
            "platform_id": result.get("tweet_id") or result.get("platform_id"),
            "post_url": result.get("post_url"),
            "message": result.get("message"),
            "error": result.get("message") if result.get("status") == "failed" else None,
            "published_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "platform_id": None,
            "post_url": None,
            "message": str(e),
            "error": str(e),
            "published_at": datetime.now().isoformat()
        }


# For backward compatibility with registry pattern
agent = None  # This agent doesn't use LangGraph, just direct function calls
state = PublishState


__all__ = ["publish_content", "agent", "state"]
