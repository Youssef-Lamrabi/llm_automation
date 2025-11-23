# Media Builder Agent

## Overview

The Media Builder Agent generates AI-powered images for social media content using LLM-generated prompts and Cloudflare AI Workers.

## Mission

Transform social media text content into visually engaging images by:
1. Creating detailed, platform-optimized image generation prompts using LLM
2. Generating high-quality images via Cloudflare AI Workers
3. Saving images for use in social media posts

## How It Works

```
Input: Content + Platform + Persona + Topic
    ↓
[Create Image Prompt Node]
    ↓ (LLM generates detailed visual description)
[Generate Image Node]
    ↓ (Cloudflare Worker creates image)
Output: Image Data + Saved File
```

## Key Features

- **Smart Prompt Generation**: Uses LLM to create detailed, context-aware image prompts
- **Cloudflare AI Integration**: Leverages `@cf/leonardo/phoenix-1.0` model for high-quality images
- **Platform-Aware**: Adapts visual style based on platform and persona
- **Automatic Saving**: Stores generated images in `generated_images/` folder

## Configuration

Environment variables in `.env`:

```bash
# Cloudflare AI Worker endpoint
CLOUDFLARE_IMAGE_API_URL=

# Image generation model
IMAGE_MODEL=@cf/leonardo/phoenix-1.0

# LLM for prompt generation
GROQ_API_KEY=your_groq_api_key
```

## Usage

### As Part of Workflow

The media builder is automatically called by the orchestrator when `media_type = "image"`:

```python
# Instagram always requires media
platform = "Instagram"  # → media_type = "image"

# Other platforms: LLM decides based on content
platform = "X"  # → media_type = "none" or "image"
```

### Standalone Testing

```bash
python test_media_builder.py
```

## Output

- **Image Data**: Raw PNG bytes for immediate use
- **Saved File**: `generated_images/{platform}_{workflow_id}_{timestamp}.png`
- **Metadata**: Image prompt, generation status, file path

## Platform Requirements

| Platform | Media Required |
|----------|----------------|
| Instagram | ✅ Always |
| X/Twitter | ❌ Optional |
| LinkedIn | ❌ Optional |
| Reddit | ❌ Optional |
| Medium | ❌ Optional |

## Example

**Input:**
```python
{
    "content": "AI is transforming cybersecurity with lightning-fast threat detection!",
    "platform": "Instagram",
    "persona": {"style": "Tech-savvy with gaming references"},
    "topic": "AI in cybersecurity"
}
```

**Generated Prompt:**
> "Create a futuristic cybersecurity scene with AI neural networks defending against digital threats. Dynamic composition with glowing blue accents, circuit patterns, and tech aesthetic. Bold, eye-catching style for social media."

**Output:** High-quality PNG image saved and ready for posting
