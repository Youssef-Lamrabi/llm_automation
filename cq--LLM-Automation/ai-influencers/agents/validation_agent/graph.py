"""
Validation Agent Graph Implementation

This module defines the LangGraph workflow for content validation.
"""

from langgraph.graph import StateGraph, START, END
from .components.state import ValidationState
from .components.nodes import (
    safety_check_node,
    factuality_check_node,
    persona_check_node,
    finalize_validation_node
)


builder = StateGraph(ValidationState)

builder.add_node("safety_check", safety_check_node)
builder.add_node("factuality_check", factuality_check_node)
builder.add_node("persona_check", persona_check_node)
builder.add_node("finalize_validation", finalize_validation_node)

builder.add_edge(START, "safety_check")
builder.add_edge("safety_check", "factuality_check")
builder.add_edge("factuality_check", "persona_check")
builder.add_edge("persona_check", "finalize_validation")
builder.add_edge("finalize_validation", END)

validation_agent = builder.compile()
validation_agent.__doc__ = ValidationState.__doc__
