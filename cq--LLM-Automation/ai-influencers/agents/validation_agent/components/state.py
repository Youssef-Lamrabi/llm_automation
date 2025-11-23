"""
State management for the Validation Agent.
Defines the data structure that flows through the validation workflow.
"""

from __future__ import annotations

from typing import TypedDict, Optional, Literal


class ValidationState(TypedDict, total=False):
	"""Unified state schema for the Validation Agent."""
	# Input content from Content Generator
	content: str
	metadata: dict
	persona: dict
	
	# Validation results
	validation_status: Literal["pending", "pass", "fail"]
	
	# Individual check results
	safety_passed: bool
	factuality_passed: bool
	persona_passed: bool
	
	# Confidence scores
	safety_confidence: float
	factuality_confidence: float
	persona_confidence: float
	overall_confidence: float
	
	# Detailed results (for debugging/logging)
	safety_check_result: dict
	factuality_check_result: dict
	persona_check_result: dict
	
	# Confidence warnings
	confidence_warnings: list
	
	# Additional context
	reference_information: Optional[str]
	error: str
