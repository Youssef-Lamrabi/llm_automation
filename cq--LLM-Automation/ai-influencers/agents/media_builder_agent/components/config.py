"""
Media Builder Agent Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

# Cloudflare Worker API URL
CLOUDFLARE_IMAGE_API_URL = os.getenv("CLOUDFLARE_IMAGE_API_URL")

# Best model for social media images
IMAGE_MODEL = os.getenv(
    "IMAGE_MODEL",
    "@cf/leonardo/phoenix-1.0"
)

# LLM API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
