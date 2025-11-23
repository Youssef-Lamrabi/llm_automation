"""
Media Builder Agent Nodes
"""

from typing import Dict, Any
from .state import MediaBuilderState
from .llm import llm
from .tools import generate_image
from langchain_core.messages import SystemMessage, HumanMessage


def create_image_prompt(state: MediaBuilderState) -> MediaBuilderState:
    """Generate a detailed image prompt based on content and persona."""
    
    content = state.get("content", "")
    platform = state.get("platform", "X")
    persona = state.get("persona", {})
    topic = state.get("topic", "")
    
    print("\n🎨 Creating image prompt...")
    
    # Create prompt for LLM to generate image description
    system_prompt = """You are an expert at creating image generation prompts for social media content.
Generate a detailed, vivid prompt for an AI image generator that will create eye-catching visuals for social media posts.

Focus on:
- Visual style that matches the platform and persona
- Modern, futuristic tech aesthetic when relevant
- Bold colors and dynamic composition
- Social media-friendly layout
- Professional yet engaging look

Keep prompts under 500 characters but be descriptive and specific."""

    user_prompt = f"""Create an image generation prompt for this social media post:

Content: {content}
Topic: {topic}
Platform: {platform}
Persona Style: {persona.get('Communication_Style', 'Professional and engaging')}

Generate ONLY the image prompt, no explanations."""

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        image_prompt = response.content.strip()
        print(f"✅ Image prompt created: {image_prompt[:100]}...")
        
        return {
            **state,
            "image_prompt": image_prompt,
            "media_status": "prompt_created"
        }
        
    except Exception as e:
        print(f"❌ Failed to create image prompt: {e}")
        return {
            **state,
            "media_status": "prompt_failed",
            "error": str(e)
        }


def generate_social_image(state: MediaBuilderState) -> MediaBuilderState:
    """Generate image using Cloudflare AI worker."""
    
    image_prompt = state.get("image_prompt", "")
    
    if not image_prompt:
        return {
            **state,
            "media_status": "failed",
            "error": "No image prompt provided"
        }
    
    print("\n🖼️ Generating image...")
    print(f"Prompt: {image_prompt}")
    
    try:
        image_data = generate_image(image_prompt)
        
        if image_data:
            print("✅ Image generated successfully!")
            return {
                **state,
                "image_data": image_data,
                "media_status": "completed"
            }
        else:
            print("❌ Image generation returned no data")
            return {
                **state,
                "media_status": "failed",
                "error": "Image generation returned no data"
            }
            
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return {
            **state,
            "media_status": "failed",
            "error": str(e)
        }
