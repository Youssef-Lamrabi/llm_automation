from __future__ import annotations

from typing import TypedDict, Optional, Literal


class ContentGenState(TypedDict, total=False):
	"""Unified state schema for the Content Generator Agent."""
	time: str
	platform: str
	content_type: str
	topic: str
	persona: dict
	platform_prompt: str
	platform_rules: dict
	content: str
	hashtags: str
	media_type: Literal["none", "image", "video"]
	metadata: dict
	error: str
