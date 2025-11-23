import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
	"""configuration for Content Generator Agent"""
	PROMPTS_DIR: str = os.getenv("PROMPTS_DIR", "content_generator_agent/prompts")
	
	# LLM Configuration
	MODEL_PROVIDER: str = os.getenv("CONTENT_GEN_MODEL_PROVIDER", "groq")
	MODEL_NAME: str = os.getenv("CONTENT_GEN_MODEL_NAME", "llama-3.3-70b-versatile")
	TEMPERATURE: float = float(os.getenv("CONTENT_GEN_TEMPERATURE", "0.7"))
	MAX_TOKENS: int = int(os.getenv("CONTENT_GEN_MAX_TOKENS", "512"))
	API_KEY: str = os.getenv("GROQ_API_KEY", "")

	# Configuration metadata for potential future pydantic migration
	model_config = {
		"env_file": ".env",
		"case_sensitive": False,
		"extra": "ignore",
	}


# Global config instance
config = Config()