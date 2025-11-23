"""
Media Builder Agent Tools
"""

import requests
from .config import CLOUDFLARE_IMAGE_API_URL, IMAGE_MODEL


def generate_image(prompt: str) -> bytes:
    """
    Generate an image using Cloudflare AI worker.
    
    Args:
        prompt: Detailed image generation prompt
        
    Returns:
        Image data as bytes or None if failed
    """
    payload = {
        "prompt": prompt,
        "model": IMAGE_MODEL
    }
    
    try:
        response = requests.post(CLOUDFLARE_IMAGE_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        # API returns raw image data
        return response.content
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error calling image API: {e}")
        return None
