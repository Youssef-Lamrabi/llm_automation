"""
Media Builder Agent LLM Configuration
"""

from langchain_groq import ChatGroq
from .config import GROQ_API_KEY

# Initialize LLM for prompt generation
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.8,
    max_tokens=512,
    api_key=GROQ_API_KEY
)
