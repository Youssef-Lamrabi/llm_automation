"""
LLM configuration for the Validation Agent.
Sets up the language model instance used for validation checks.
"""

from langchain_groq import ChatGroq
from .config import config

provider = config.VALIDATION_MODEL_PROVIDER
if provider != "groq":
	raise ValueError("Unsupported LLM provider configured; only 'groq' is implemented in this module.")

llm = ChatGroq(
	model=config.VALIDATION_MODEL_NAME,
	temperature=config.VALIDATION_TEMPERATURE,
	max_tokens=config.VALIDATION_MAX_TOKENS,
	api_key=config.GROQ_API_KEY,
)