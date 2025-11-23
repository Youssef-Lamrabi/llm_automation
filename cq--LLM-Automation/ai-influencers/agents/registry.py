"""
Simple Agent Registry

This module provides a compact, explicit `REGISTRY` mapping for easy
access to agents and their state classes. The shape mirrors your
preferred example where each entry is a dict with `agent` and
`state_class` keys.
"""

import sys
import os
from typing import Dict, Any, Optional

# Ensure agents directory is in the path for importing
current_dir = os.path.dirname(__file__)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import available agents and state classes using clean package imports
try:
    from content_generator_agent import agent as content_generator_agent, state as ContentGenState
except Exception:
    content_generator_agent = None  # type: ignore
    ContentGenState = None  # type: ignore

try:
    from validation_agent import agent as validation_agent, state as ValidationState
except Exception:
    validation_agent = None  # type: ignore
    ValidationState = None  # type: ignore

try:
    from orchestrator_agent import agent as orchestrator_agent, state as OrchestratorState
except Exception:
    orchestrator_agent = None  # type: ignore
    OrchestratorState = None  # type: ignore

try:
    from media_builder_agent import agent as media_builder_agent
    from media_builder_agent.components.state import MediaBuilderState
except Exception:
    media_builder_agent = None
    MediaBuilderState = None

# publishing agent uses direct function calls, not LangGraph
try:
    from publishing_agent import agent as publishing_agent, state as PublishingState
except Exception:
    publishing_agent = None
    PublishingState = None

REGISTRY: Dict[str, Dict[str, Optional[Any]]] = {
    "content_generator": {
        "agent": content_generator_agent,
        "state_class": ContentGenState,
    },
    "validation": {
        "agent": validation_agent,
        "state_class": ValidationState,
    },
    "orchestrator": {
        "agent": orchestrator_agent,
        "state_class": OrchestratorState,
    },
    "media_builder": {
        "agent": media_builder_agent,
        "state_class": MediaBuilderState,
    },
    "publishing": {
        "agent": publishing_agent,
        "state_class": PublishingState,
    },
}


def get(agent_key: str) -> Dict[str, Optional[Any]]:
    """Get the registry entry for an agent key.

    Returns a dict with keys `agent` and `state_class`. If the agent is
    not implemented the values will be None.
    """
    return REGISTRY.get(agent_key, {"agent": None, "state_class": None})


__all__ = ["REGISTRY", "get"]