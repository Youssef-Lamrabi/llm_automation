"""
Configuration settings for the Validation Agent.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuration for Validation Agent"""
    
    # Prompts directory - relative to the validation_agent directory
    PROMPTS_DIR: str = os.getenv("VALIDATION_PROMPTS_DIR", str(Path(__file__).parent.parent / "prompts"))
    
    # LLM Configuration
    VALIDATION_MODEL_PROVIDER: str = os.getenv("VALIDATION_MODEL_PROVIDER", "groq")
    VALIDATION_MODEL_NAME: str = os.getenv("VALIDATION_MODEL_NAME", "llama-3.3-70b-versatile")
    VALIDATION_TEMPERATURE: float = float(os.getenv("VALIDATION_TEMPERATURE", "0.1"))
    VALIDATION_MAX_TOKENS: int = int(os.getenv("VALIDATION_MAX_TOKENS", "512"))
    
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Validation thresholds
    SAFETY_THRESHOLD: float = float(os.getenv("SAFETY_THRESHOLD", "0.7"))
    FACTUALITY_CONFIDENCE_THRESHOLD: float = float(os.getenv("FACTUALITY_CONFIDENCE_THRESHOLD", "0.8"))
    
    # Validation settings
    ENABLE_SAFETY_CHECK: bool = os.getenv("ENABLE_SAFETY_CHECK", "true").lower() == "true"
    ENABLE_FACTUALITY_CHECK: bool = os.getenv("ENABLE_FACTUALITY_CHECK", "true").lower() == "true"
    ENABLE_PERSONA_CHECK: bool = os.getenv("ENABLE_PERSONA_CHECK", "true").lower() == "true"

    # pydantic-like model_config placeholder for potential migration
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore",
    }


config = Config()
