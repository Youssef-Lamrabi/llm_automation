"""
Media Builder Agent Graph
"""

from langgraph.graph import StateGraph, START, END
from .components.state import MediaBuilderState
from .components.nodes import create_image_prompt, generate_social_image

# Create workflow
workflow = StateGraph(MediaBuilderState)

# Add nodes
workflow.add_node("create_prompt", create_image_prompt)
workflow.add_node("generate_image", generate_social_image)

# Add edges
workflow.add_edge(START, "create_prompt")
workflow.add_edge("create_prompt", "generate_image")
workflow.add_edge("generate_image", END)

# Compile
media_builder_agent = workflow.compile()
