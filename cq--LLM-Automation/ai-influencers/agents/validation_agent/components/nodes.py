"""
LangGraph nodes for the Validation Agent workflow.
Four validation nodes: safety, factuality, persona alignment, and finalization.
"""

import json
from pathlib import Path
from typing import Dict, Any
from .state import ValidationState
from .llm import llm
from .config import config
from .schemas import SafetyCheckOutput, FactCheckOutput, PersonaCheckOutput


def safety_check_node(state: ValidationState) -> ValidationState:
    """
    Node that performs safety validation on the content using LLM.
    
    Args:
        state: ValidationState with content to validate
        
    Returns:
        Updated state with safety check results
    """
    print("🛡️ Running safety check...")
    
    try:
        # Load and format the prompt template
        prompt_template = Path(config.PROMPTS_DIR, "safety_check_prompt.txt").read_text()
        filled_prompt = prompt_template.format(content=state["content"])
        
        # Call LLM with structured output to ensure JSON response
        structured_llm = llm.with_structured_output(SafetyCheckOutput)
        result: SafetyCheckOutput = structured_llm.invoke(filled_prompt)
        
        # Convert to dict for storage
        safety_result = result.model_dump()
        
        # Store the full safety check result
        state["safety_check_result"] = safety_result
        
        # Use the overall_passed from LLM result
        state["safety_passed"] = safety_result["overall_passed"]
        state["safety_confidence"] = safety_result["overall_confidence"]
        
        if state["safety_passed"]:
            print(f"✅ Safety check passed (confidence: {safety_result['overall_confidence']:.2f})")
        else:
            print(f"❌ Safety check failed (confidence: {safety_result['overall_confidence']:.2f})")
        
    except Exception as e:
        print(f"Error during safety check: {e}")
        state["safety_passed"] = False
        state["safety_confidence"] = 0.0
        state["safety_check_result"] = {"error": str(e)}
    
    return state


def factuality_check_node(state: ValidationState) -> ValidationState:
    """
    Node that performs factuality validation on the content using LLM.
    
    Args:
        state: ValidationState with content to validate
        
    Returns:
        Updated state with factuality check results
    """
    print("📊 Running factuality check...")
    
    try:
        # Choose the appropriate prompt template
        reference_info = state.get("reference_information")
        if reference_info:
            prompt_file = "fact_check_with_reference_prompt.txt"
            prompt_template = Path(config.PROMPTS_DIR, prompt_file).read_text()
            filled_prompt = prompt_template.format(
                content=state["content"],
                reference_information=reference_info
            )
        else:
            prompt_file = "fact_check_general_prompt.txt"
            prompt_template = Path(config.PROMPTS_DIR, prompt_file).read_text()
            filled_prompt = prompt_template.format(content=state["content"])
        
        # Call LLM with structured output to ensure JSON response
        structured_llm = llm.with_structured_output(FactCheckOutput)
        result: FactCheckOutput = structured_llm.invoke(filled_prompt)
        
        # Convert to dict for storage
        fact_result = result.model_dump()
        
        # Store the full factuality check result
        state["factuality_check_result"] = fact_result
        state["factuality_passed"] = fact_result["fact_check_passed"]
        state["factuality_confidence"] = fact_result["confidence"]
        
        if state["factuality_passed"]:
            print(f"✅ Factuality check passed (confidence: {fact_result['confidence']:.2f})")
        else:
            print(f"❌ Factuality check failed (confidence: {fact_result['confidence']:.2f})")
        
    except Exception as e:
        print(f"Error during fact check: {e}")
        state["factuality_passed"] = False
        state["factuality_confidence"] = 0.0
        state["factuality_check_result"] = {"error": str(e)}
    
    return state


def persona_check_node(state: ValidationState) -> ValidationState:
    """
    Node that performs persona alignment validation on the content using LLM.
    
    Args:
        state: ValidationState with content and persona to validate
        
    Returns:
        Updated state with persona check results
    """
    print("🎭 Running persona alignment check...")
    
    persona = state.get("persona")
    
    if not persona:
        print("⚠️ No persona data provided, skipping persona check")
        state["persona_passed"] = True
        state["persona_confidence"] = 1.0
    else:
        try:
            # Load and format the prompt template
            prompt_template = Path(config.PROMPTS_DIR, "persona_check_prompt.txt").read_text()
            filled_prompt = prompt_template.format(
                content=state["content"],
                persona=persona
            )
            
            # Call LLM with structured output to ensure JSON response
            structured_llm = llm.with_structured_output(PersonaCheckOutput)
            result: PersonaCheckOutput = structured_llm.invoke(filled_prompt)
            
            # Convert to dict for storage
            persona_result = result.model_dump()
            
            # Store the full persona check result
            state["persona_check_result"] = persona_result
            state["persona_passed"] = persona_result["persona_check_passed"]
            state["persona_confidence"] = persona_result["confidence"]
            
            if state["persona_passed"]:
                print(f"✅ Persona check passed (confidence: {persona_result['confidence']:.2f})")
            else:
                print(f"❌ Persona check failed (confidence: {persona_result['confidence']:.2f})")
            
        except Exception as e:
            print(f"Error during persona check: {e}")
            state["persona_passed"] = False
            state["persona_confidence"] = 0.0
            state["persona_check_result"] = {"error": str(e)}
    
    return state


def finalize_validation_node(state: ValidationState) -> ValidationState:
    """
    Node that finalizes the overall validation status based on all check results.
    
    Args:
        state: ValidationState with all validation check results
        
    Returns:
        Updated state with final validation status and confidence metrics
    """
    print("📋 Finalizing validation results...")
    
    # Get individual results
    safety_passed = state.get("safety_passed", False)
    factuality_passed = state.get("factuality_passed", False)
    persona_passed = state.get("persona_passed", False)
    
    # Get confidence scores
    safety_confidence = state.get("safety_confidence", 0.0)
    factuality_confidence = state.get("factuality_confidence", 0.0)
    persona_confidence = state.get("persona_confidence", 0.0)
    
    # Calculate overall validation
    all_passed = safety_passed and factuality_passed and persona_passed
    
    # Calculate overall confidence (average of individual confidences)
    overall_confidence = (safety_confidence + factuality_confidence + persona_confidence) / 3.0
    
    # Determine validation status
    if all_passed:
        state["validation_status"] = "pass"
        print(f"✅ All validation checks passed! (overall confidence: {overall_confidence:.2f})")
    else:
        state["validation_status"] = "fail"
        print(f"❌ Validation failed (overall confidence: {overall_confidence:.2f})")
        
        # Log which checks failed with confidence
        if not safety_passed:
            print(f"  - Safety check failed (confidence: {safety_confidence:.2f})")
        if not factuality_passed:
            print(f"  - Factuality check failed (confidence: {factuality_confidence:.2f})")
        if not persona_passed:
            print(f"  - Persona check failed (confidence: {persona_confidence:.2f})")
    
    # Store overall confidence
    state["overall_confidence"] = overall_confidence
    
    # Add confidence-based recommendations
    low_confidence_threshold = 0.7
    confidence_warnings = []
    
    if safety_confidence < low_confidence_threshold:
        confidence_warnings.append(f"Low confidence in safety assessment ({safety_confidence:.2f})")
    if factuality_confidence < low_confidence_threshold:
        confidence_warnings.append(f"Low confidence in factuality assessment ({factuality_confidence:.2f})")
    if persona_confidence < low_confidence_threshold:
        confidence_warnings.append(f"Low confidence in persona assessment ({persona_confidence:.2f})")
    
    if confidence_warnings:
        state["confidence_warnings"] = confidence_warnings
        print("⚠️ Confidence warnings:")
        for warning in confidence_warnings:
            print(f"  - {warning}")
    
    return state