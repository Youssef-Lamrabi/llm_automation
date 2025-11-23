"""
Nodes for Publishing Agent (No OpenAI/LLM).
- prepare_post(entry): Formats schedule entry into post-ready state (rule-based Twitter formatting).
- publish_post(state): Posts to Twitter/X via tweepy; returns result dict.
Handles dry-run. Text-only (no media).
"""
import os
import tweepy
from datetime import datetime
from typing import Dict, Any

# Imports from config (fixed: no CONFIG or load_schedule; matches your .env)
from .config import TWITTER_CONFIG, DRY_RUN, load_persona

def prepare_post(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare schedule entry for posting (rule-based, no LLM).
    - Combines Content + Hashtags.
    - Ensures <280 chars for Twitter; adds basic CTA.
    - Defaults: Platform="Twitter", Persona="neuralNinja".
    Returns state dict for publish_post.
    """
    content = str(entry.get("Content", "")).strip()
    hashtags = str(entry.get("Hashtags", "")).strip()
    platform = entry.get("Platform", "Twitter")
    persona_name = entry.get("Persona", "neuralNinja")
    
    if not content:
        raise ValueError("Entry missing 'Content'")
    
    # Basic combine + formatting (rule-based)
    raw_text = f"{content} {hashtags}".strip()
    # Add simple CTA for engagement (GenZ vibe)
    cta = " What's your take? 💭"  # Or "Drop a reply!"
    formatted_text = (raw_text + cta).strip()
    
    # Twitter limit: Truncate if >280 chars
    if platform.lower() == "twitter" and len(formatted_text) > 280:
        formatted_text = formatted_text[:277] + "... 💭"
    
    # Load persona for logging (optional)
    persona = load_persona(persona_name)
    
    state = {
        "formatted_text": formatted_text,
        "platform": platform,
        "persona": persona_name,
        "original_entry": entry,  # For logging
        "scheduled_time": entry.get("Date") + "T" + entry.get("Time"),
        "persona_info": persona  # For potential logging
    }
    print(f"[prepare] Formatted ({persona_name}): {formatted_text[:100]}... (len={len(formatted_text)})")
    return state

def publish_post(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Publish formatted state to platform (Twitter/X only).
    Returns: {"status": "success/failure", "tweet_id": ..., "post_url": ..., "message": "..."}
    """
    if DRY_RUN:
        print("[dry-run] Would post:", state["formatted_text"][:100] + "...")
        return {"status": "success", "tweet_id": "MOCK_123", "post_url": "https://twitter.com/mock", "message": "Dry-run success"}
    
    platform = state["platform"].lower()
    if platform != "twitter":
        return {"status": "failed", "message": f"Unsupported platform: {platform}"}
    
    try:
        # Initialize tweepy Client (v2 API)
        client = tweepy.Client(
            consumer_key=TWITTER_CONFIG["api_key"],
            consumer_secret=TWITTER_CONFIG["api_secret"],
            access_token=TWITTER_CONFIG["access_token"],
            access_token_secret=TWITTER_CONFIG["access_secret"],  # Will fail if missing
            bearer_token=TWITTER_CONFIG["bearer_token"],
            wait_on_rate_limit=True,
        )
        
        # Verify auth
        me = client.get_me(user_auth=True)
        if not me.data:
            raise Exception("Twitter auth failed: Invalid keys (check ACCESS_TOKEN_SECRET)")
        
        # Post tweet
        response = client.create_tweet(text=state["formatted_text"])
        if response.data:
            tweet_id = response.data["id"]
            post_url = f"https://twitter.com/{me.data.username}/status/{tweet_id}"
            print(f"[publish] Posted! ID={tweet_id}, URL={post_url}")
            return {
                "status": "success",
                "tweet_id": tweet_id,
                "platform_id": tweet_id,
                "post_url": post_url,
                "message": f"Posted by @{me.data.username}"
            }
        else:
            raise Exception("No tweet data in response")
    
    except tweepy.TweepyException as e:
        error_msg = str(e).split("\n")[0]  # First line for brevity
        print(f"[publish-error] Twitter API: {error_msg}")
        return {"status": "failed", "message": error_msg, "tweet_id": None}
    
    except Exception as e:
        print(f"[publish-error] Unexpected: {e}")
        return {"status": "failed", "message": str(e), "tweet_id": None}
