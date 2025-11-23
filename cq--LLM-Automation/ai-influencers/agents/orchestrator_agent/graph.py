"""
Orchestrator Agent Graph Implementation

This module defines the LangGraph workflow that coordinates all AI agents
in the content creation pipeline.
"""

from langgraph.graph import StateGraph, START, END
from .components.state import OrchestratorState
from .components.nodes import (
    initialize_workflow,
    content_generation,
    validation,
    media_building,
    publishing,
    finalization
)
from .components.helpers import route_after_validation


# Create the workflow graph
workflow = StateGraph(OrchestratorState)

# Add nodes
workflow.add_node("initialize", initialize_workflow)
workflow.add_node("content_generation", content_generation)
workflow.add_node("validation", validation)
workflow.add_node("media_building", media_building)
workflow.add_node("publishing", publishing)
workflow.add_node("finalization", finalization)

# Add edges
workflow.add_edge(START, "initialize")
workflow.add_edge("initialize", "content_generation")
workflow.add_edge("content_generation", "validation")

# Conditional edge after validation
workflow.add_conditional_edges(
    "validation",
    route_after_validation,
    {
        "media_building": "media_building"
    }
)

workflow.add_edge("media_building", "publishing")
workflow.add_edge("publishing", "finalization")
workflow.add_edge("finalization", END)

# Compile the graph
orchestrator_agent = workflow.compile()