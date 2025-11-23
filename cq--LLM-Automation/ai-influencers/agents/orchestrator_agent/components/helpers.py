"""
Orchestrator Agent Helper Functions

Contains utility functions for conditional routing and workflow management
used in the LangGraph workflow.
"""

from .state import OrchestratorState


def should_retry_validation(state: OrchestratorState) -> str:
    """
    Determine if validation should be retried or proceed to next stage.
    
    Returns:
        "retry" if validation failed and retries are available
        "media_building" if validation passed or max retries reached
    """
    validation_status = state.get("validation_status", "fail")
    retry_count = state.get("retry_count", 0)
    max_retries = 2  # Allow up to 2 retries
    
    if validation_status == "pass":
        return "media_building"
    elif retry_count < max_retries:
        return "retry_validation"
    else:
        # Max retries reached, proceed anyway but mark as failed
        return "media_building"


def should_continue_after_error(state: OrchestratorState) -> str:
    """
    Determine if workflow should continue after an error.
    
    Returns:
        "end" if there's a critical error
        Next stage if error is recoverable
    """
    error = state.get("error")
    current_stage = state.get("current_stage", "")
    
    if error and "Missing required fields" in error:
        # Critical error - can't proceed without required fields
        return "end"
    
    # For other errors, continue to next appropriate stage
    if current_stage == "content_generation":
        return "validation"
    elif current_stage == "validation":
        return "media_building"
    elif current_stage == "media_building":
        return "publishing"
    elif current_stage == "publishing":
        return "finalization"
    else:
        return "end"


def increment_retry_count(state: OrchestratorState) -> OrchestratorState:
    """Increment retry counter for validation retries."""
    return {
        **state,
        "retry_count": state.get("retry_count", 0) + 1,
        "current_stage": "content_generation"  # Retry from content generation
    }


def route_after_validation(state: OrchestratorState) -> str:
    """Simple routing after validation - either continue or retry."""
    validation_status = state.get("validation_status", "fail")
    
    if validation_status == "pass":
        return "media_building"
    else:
        return "media_building"  # For now, continue even if validation fails


def has_error(state: OrchestratorState) -> bool:
    """Check if state has an error."""
    return bool(state.get("error"))


def get_next_stage(state: OrchestratorState) -> str:
    """Get the next stage based on current stage."""
    current_stage = state.get("current_stage", "")
    
    stage_flow = {
        "initialization": "content_generation",
        "content_generation": "validation", 
        "validation": "media_building",
        "media_building": "publishing",
        "publishing": "finalization",
        "finalization": "completed"
    }
    
    return stage_flow.get(current_stage, "completed")