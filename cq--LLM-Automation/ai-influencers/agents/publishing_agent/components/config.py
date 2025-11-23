import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[1]  # publishing_agent/
SCHEDULES_DIR = BASE_DIR / "Schedules"
SCHEDULES_DIR.mkdir(parents=True, exist_ok=True)

# Default schedule filenames (you can change them)
SCHEDULE_X = SCHEDULES_DIR / "Content_Schedule_X.json"
SCHEDULE_LINKEDIN = SCHEDULES_DIR / "Content_Schedule_LinkedIn.json"
SCHEDULE_INSTAGRAM = SCHEDULES_DIR / "Content_Schedule_Instagram.json"
SCHEDULE_MEDIUM = SCHEDULES_DIR / "Content_Schedule_Medium.json"
SCHEDULE_REDDIT = SCHEDULES_DIR / "Content_Schedule_Reddit.json"

# platform limits
PLATFORM_LIMITS = {
    "twitter": {"max_length": 280},
    "instagram": {"max_length": 2200},
    "linkedin": {"max_length": 1300},  # short posts
    "medium": {"max_length": 100000},  # article, big
    "reddit": {"title_max": 300}
}

# Logging CSV
LOG_CSV = BASE_DIR / "publish_api_logs.csv"

# Twitter/X Configuration
TWITTER_CONFIG = {
    "api_key": os.getenv("X_API_KEY", ""),
    "api_secret": os.getenv("X_API_SECRET", ""),
    "access_token": os.getenv("X_ACCESS_TOKEN", ""),
    "access_secret": os.getenv("X_ACCESS_TOKEN_SECRET", ""),
    "bearer_token": os.getenv("X_BEARER_TOKEN", "")
}

# Dry run mode (prevents actual posting)
DRY_RUN = os.getenv("DRY_RUN", "True").lower() in ("1", "true", "yes")

# Persona data directory
PERSONAS_DIR = Path(__file__).resolve().parents[3] / "data" / "personas"


def load_persona(persona_name: str):
    """
    Load persona data from JSON files.
    
    Args:
        persona_name: Name of the persona (neuralNinja, frank, etc.)
        
    Returns:
        dict: Persona data or basic fallback
    """
    persona_files = {
        "neuralninja": "neuralNinja.json",
        "frank": "frank_algoWizard.json",
        "algowizard": "frank_algoWizard.json"
    }
    
    normalized_name = persona_name.lower().strip()
    
    if normalized_name not in persona_files:
        # Return basic fallback persona
        return {
            "Persona_ID": persona_name,
            "name": persona_name,
            "role": "AI Influencer"
        }
    
    persona_path = PERSONAS_DIR / persona_files[normalized_name]
    
    try:
        if persona_path.exists():
            with open(persona_path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"[warning] Could not load persona {persona_name}: {e}")
    
    # Fallback
    return {
        "Persona_ID": persona_name,
        "name": persona_name,
        "role": "AI Influencer"
    }
