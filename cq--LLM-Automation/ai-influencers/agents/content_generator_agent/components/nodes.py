from typing import Dict, Any
import re
import json

from .tools import load_platform_prompt, get_platform_rules, check_content_length, trim_content
from .state import ContentGenState
from langchain_core.messages import SystemMessage, HumanMessage
from .llm import llm


def platform_adapter(state: ContentGenState) -> ContentGenState:
	"""Load platform prompt and rules for the specified platform and content type."""
	platform = state.get("platform", "X")
	content_type = state.get("content_type", None)
	
	prompt_info = load_platform_prompt.invoke({
		"platform": platform, 
		"content_type": content_type
	})
	prompt_text = prompt_info.get("template_text", "")
	
	rules = get_platform_rules.invoke({
		"platform": platform,
		"content_type": content_type
	})
	
	return {"platform_prompt": prompt_text, "platform_rules": rules}


def content_draft_generator(state: ContentGenState) -> ContentGenState:
	"""Generate draft content and hashtags separately using LLM with persona and platform context."""
	platform = state.get("platform", "X")
	content_type = state.get("content_type", "default")
	topic = state.get("topic", "")
	persona = state.get("persona", {}) or {}
	platform_prompt = state.get("platform_prompt", "")
	platform_rules = state.get("platform_rules", {})

	system_prompt = (
		"You are an elite social media ghostwriter. Generate content and hashtags separately. "
		"Respond with ONLY a valid JSON object containing content and hashtags."
	)
	
	user_prompt_parts = [
		f"Topic: {topic}",
		f"Persona: {persona}",
		f"Platform: {platform}",
		f"Content Type: {content_type}",
		f"Platform Rules: {platform_rules}",
		"Platform Template:",
		platform_prompt,
		"",
		f"Generate {content_type} content for {platform} and {platform_rules.get('hashtag_count', 3)} hashtags.",
		"",
		"Respond with ONLY this JSON format:",
		'{{',
		'    "content": "your content text without hashtags",',
		'    "hashtags": "#hashtag1 #hashtag2"',
		'}}'
	]
	
	user_prompt = "\n".join(user_prompt_parts)
	resp = llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
	response_content = getattr(resp, "content", "").strip()
	
	# Parse JSON response
	try:
		# Clean response if wrapped in code blocks
		if response_content.startswith('```json'):
			response_content = response_content.replace('```json', '').replace('```', '').strip()
		
		llm_output = json.loads(response_content)
		draft = llm_output.get("content", "")
		hashtags = llm_output.get("hashtags", "")
		
	except json.JSONDecodeError:
		# Fallback if JSON parsing fails
		draft = response_content
		hashtags = "#AI #Tech"
	
	return {"content": draft, "hashtags": hashtags}


def post_processing(state: ContentGenState) -> ContentGenState:
	"""Post-process content, check length limits, and determine media type."""

	content = state["content"]
	hashtags = state["hashtags"]
	platform = state["platform"]
	content_type = state.get("content_type", "default")
	topic = state["topic"]
	platform_rules = state["platform_rules"]
	time_val = state.get("time", "")
	persona = state.get("persona", {}) or {}
	
	llm_with_tools = llm.bind_tools([check_content_length, trim_content])
	prompt = f"""
Process this {platform} {content_type} content and make decisions:

CONTENT: {content}
PLATFORM: {platform}
CONTENT_TYPE: {content_type}
TOPIC: {topic}
RULES: {platform_rules}

Tasks:
1. Check content length against platform limits and trim if needed using tools
2. Determine media type needed for this content

MEDIA TYPE OPTIONS:
- "none": Regular text post, no media needed
- "image": Content would benefit from visual elements (charts, infographics, photos, diagrams)  
- "video": Content is meant for video format (tutorials, demos, explanations, stories)

Consider platform characteristics, content type, and content to decide media type.
For content types like "video-script", "reel-script" -> automatically "video"
For content types like "image-with-text" -> automatically "image"
For text-only content types -> usually "none" unless content specifically suggests visuals

After using tools if needed, respond with your final analysis in this exact format:
MEDIA_TYPE: [none/image/video]
REASONING: [brief explanation]
"""
	
	response = llm_with_tools.invoke(prompt)
	final_content = content
	
	if hasattr(response, 'tool_calls') and response.tool_calls:
		for tool_call in response.tool_calls:
			if tool_call['name'] == 'trim_content':
				result = trim_content.invoke(tool_call['args'])
				if result.get('was_trimmed'):
					final_content = result['trimmed_content']
	
	response_content = getattr(response, "content", "").lower()
	media_type = "none"
	
	# Check if platform requires media by default (e.g., Instagram)
	media_required = platform_rules.get("media_default", False)
	
	# Determine media type based on content type and LLM response
	if content_type in ["video-script", "reel-script", "comment-hook"]:
		media_type = "video"
	elif content_type in ["image-with-text", "story-text"]:
		media_type = "image"
	elif media_required:
		# Platform requires media (e.g., Instagram) - default to image
		media_type = "image"
	elif "media_type: image" in response_content or "media_type:image" in response_content:
		media_type = "image"
	elif "media_type: video" in response_content or "media_type:video" in response_content:
		media_type = "video"
	elif "media_type: none" in response_content or "media_type:none" in response_content:
		media_type = "none"
	
	metadata = {
		"platform": platform,
		"content_type": content_type,
		"persona": persona,
		"topic": topic,
		"scheduled_time": time_val,
		"media_type": media_type
	}
	
	return {
		"content": final_content,
		"hashtags": hashtags,
		"media_type": media_type,
		"metadata": metadata
	}


