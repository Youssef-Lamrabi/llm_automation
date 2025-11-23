"""
Pydantic schemas for the Validation Agent structured outputs.
"""

from pydantic import BaseModel
from typing import Dict, Any


class SafetyCheckItem(BaseModel):
    flagged: bool
    score: float
    confidence: float


class SafetyCheckOutput(BaseModel):
    toxicity: SafetyCheckItem
    offensiveness: SafetyCheckItem
    hate_speech: SafetyCheckItem
    overall_passed: bool
    overall_confidence: float
    explanation: str


class FactCheckOutput(BaseModel):
    fact_check_passed: bool
    confidence: float
    explanation: str
    accuracy_score: float


class PersonaCheckOutput(BaseModel):
    persona_check_passed: bool
    confidence: float
    explanation: str
    style_alignment_score: float
    tone_alignment_score: float
    audience_alignment_score: float