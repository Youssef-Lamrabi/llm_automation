"""
Content Generator Agent Graph Implementation

This module defines the LangGraph workflow for content generation.
"""

from langgraph.graph import StateGraph, START, END
from .components.state import ContentGenState
from .components.nodes import (
    platform_adapter,
    content_draft_generator, 
    post_processing
)

# Build the workflow graph
builder = StateGraph(ContentGenState)

# Add processing nodes
builder.add_node("platform_adapter", platform_adapter)
builder.add_node("content_draft_generator", content_draft_generator)
builder.add_node("post_processing", post_processing)

# Define workflow edges (sequential processing)
builder.add_edge(START, "platform_adapter")
builder.add_edge("platform_adapter", "content_draft_generator")
builder.add_edge("content_draft_generator", "post_processing")
builder.add_edge("post_processing", END)

# Compile the agent
content_generator_agent = builder.compile()
content_generator_agent.__doc__ = ContentGenState.__doc__
