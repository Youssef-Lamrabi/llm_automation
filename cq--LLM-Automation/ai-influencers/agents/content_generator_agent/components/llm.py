from langchain_groq import ChatGroq
from .config import config

# Validate provider
if config.MODEL_PROVIDER != "groq":
	raise ValueError("Unsupported LLM provider configured; only 'groq' is implemented in this module.")

llm = ChatGroq(
	model=config.MODEL_NAME,
	temperature=config.TEMPERATURE,
	max_tokens=config.MAX_TOKENS,
	api_key=config.API_KEY,
)