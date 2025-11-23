"""
Orchestrator Agent State Management

Defines a clean, unified state schema for coordinating multiple AI agents
in the content creation pipeline. Only includes essential fields needed
for orchestration and inter-agent communication.
"""

from __future__ import annotations
from typing import TypedDict, Optional, Literal, List, Dict, Any


class OrchestratorState(TypedDict, total=False):
    """
    Clean unified state for the Orchestrator Agent.
    Contains only essential fields for coordinating the content pipeline.
    """
    
    # === WORKFLOW METADATA ===
    workflow_id: str
    current_stage: Literal["initialization", "content_generation", "validation", "media_building", "publishing", "completed"]
    created_at: str
    updated_at: str
    
    # === INPUT PARAMETERS ===
    # Core content requirements
    time: str
    platform: str
    content_type: str
    topic: str
    persona: Dict[str, Any]
    
    # === CONTENT GENERATION RESULTS ===
    content: Optional[str]      
    hashtags: Optional[str]     
    media_type: Optional[Literal["none", "image", "video"]]  
    content_metadata: Optional[Dict[str, Any]]  
    
    # === VALIDATION RESULTS ===
    validation_status: Optional[Literal["pending", "pass", "fail"]]
    safety_passed: Optional[bool]
    factuality_passed: Optional[bool] 
    persona_passed: Optional[bool]
    overall_confidence: Optional[float]
    validation_details: Optional[Dict[str, Any]]  
    
    # === MEDIA BUILDING RESULTS ===
    media_generation_status: Optional[Literal["pending", "completed", "not_required", "failed"]]
    media_assets: Optional[List[str]]  
    media_metadata: Optional[Dict[str, Any]]  
    
    # === PUBLISHING RESULTS ===
    publication_status: Optional[Literal["draft", "scheduled", "published", "failed"]]
    publication_metadata: Optional[Dict[str, Any]] 
    
    # === ERROR HANDLING ===
    error: Optional[str]       
    retry_count: Optional[int]  