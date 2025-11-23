from typing import Dict, Any
from pathlib import Path
from langchain.tools import tool
from .config import Config

# Content types available for each platform
# This mapping is the core of the scalable architecture - add new platforms/types here
PLATFORM_CONTENT_TYPES = {
	"LinkedIn": ["text-only"],
	"X": ["tweet"],
	"Medium": ["article"],
	"Instagram": ["post"],
	"Reddit": ["post"],
}

# Legacy mapping for backward compatibility
PLATFORM_FILE_MAP = {
	"X": "X_tweet.prompt.txt",
	"LinkedIn": "LinkedIn_text-only.prompt.txt",
	"Medium": "Medium_article.prompt.txt",
	"Instagram": "Instagram_post.prompt.txt",
	"Reddit": "Reddit_post.prompt.txt",
}

PROMPTS_DIR_PATH = Path(Config.PROMPTS_DIR)


@tool("load_platform_prompt")
def load_platform_prompt(platform: str, content_type: str = None) -> Dict[str, Any]:
	"""Load prompt template for the specified platform and content type."""
	
	# If content_type is provided, use the new format
	if content_type and platform in PLATFORM_CONTENT_TYPES:
		if content_type in PLATFORM_CONTENT_TYPES[platform]:
			filename = f"{platform}_{content_type}.prompt.txt"
			template_path = (PROMPTS_DIR_PATH / filename).resolve()
			
			if template_path.exists():
				return {
					"template_text": template_path.read_text(encoding="utf-8"),
					"filename": filename,
					"platform": platform,
					"content_type": content_type
				}
	
	# Fallback to legacy format
	filename = PLATFORM_FILE_MAP.get(platform, PLATFORM_FILE_MAP["X"])
	template_path = (PROMPTS_DIR_PATH / filename).resolve()
	
	if template_path.exists():
		return {
			"template_text": template_path.read_text(encoding="utf-8"),
			"filename": filename,
			"platform": platform,
			"content_type": content_type or "default"
		}
	
	# If nothing found, return empty template
	return {
		"template_text": "Generate content for the given topic and platform.",
		"filename": "fallback.txt",
		"platform": platform,
		"content_type": content_type or "default"
	}


@tool("get_platform_rules")
def get_platform_rules(platform: str, content_type: str = None) -> Dict[str, Any]:
	"""Get platform-specific rules and constraints based on platform and content type."""
	
	# Platform-specific rules
	# media_default: True = platform requires/strongly prefers media (Instagram)
	# media_default: False = platform supports text-only posts (X, LinkedIn, Reddit, Medium)
	if platform in ("X", "Twitter"):
		base_rules = {"max_length": 280, "hashtag_count": 2, "media_default": False}
	elif platform == "LinkedIn":
		base_rules = {"max_length": 1200, "hashtag_count": 5, "media_default": False}
	elif platform == "Medium":
		base_rules = {"max_length": 10000, "hashtag_count": 5, "media_default": False}
	elif platform == "Instagram":
		# Instagram REQUIRES media - cannot post without image/video
		base_rules = {"max_length": 2200, "hashtag_count": 10, "media_default": True}
	elif platform == "Reddit":
		base_rules = {"max_length": 4000, "hashtag_count": 0, "media_default": False}
	else:
		# Fallback for future platforms
		base_rules = {"max_length": 3000, "hashtag_count": 5, "media_default": False}
	
	base_rules["platform"] = platform
	base_rules["content_type"] = content_type or "default"
	
	return base_rules


@tool("get_available_content_types")
def get_available_content_types(platform: str) -> Dict[str, Any]:
	"""Get available content types for a specific platform."""
	return {
		"platform": platform,
		"content_types": PLATFORM_CONTENT_TYPES.get(platform, []),
		"total_count": len(PLATFORM_CONTENT_TYPES.get(platform, []))
	}


@tool("check_content_length")
def check_content_length(content: str, max_length: int) -> Dict[str, Any]:
	"""Check if content exceeds platform length limits."""
	current_length = len(content)
	exceeds_limit = current_length > max_length
	
	return {
		"current_length": current_length,
		"max_length": max_length,
		"exceeds_limit": exceeds_limit,
		"over_by": max(0, current_length - max_length)
	}


@tool("trim_content")
def trim_content(content: str, max_length: int) -> Dict[str, Any]:
	"""Trim content to fit platform length constraints."""
	if len(content) <= max_length:
		return {"trimmed_content": content, "was_trimmed": False}
	
	sentences = content.split('. ')
	trimmed = ""
	
	for i, sentence in enumerate(sentences):
		test_content = trimmed + (". " if trimmed else "") + sentence
		if i < len(sentences) - 1:
			test_content += "."
		
		if len(test_content) <= max_length:
			trimmed = test_content
		else:
			break
	
	if not trimmed:
		words = content.split()
		for word in words:
			test_content = trimmed + (" " if trimmed else "") + word
			if len(test_content) <= max_length:
				trimmed = test_content
			else:
				break
	
	if not trimmed and max_length > 0:
		trimmed = content[:max_length]
	
	return {
		"trimmed_content": trimmed,
		"was_trimmed": True,
		"original_length": len(content),
		"final_length": len(trimmed)
	}


