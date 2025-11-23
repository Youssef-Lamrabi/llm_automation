"""
Comprehensive Test Script for Validation Agent

This script tests the validation agent with various content types and personas
to ensure proper validation across safety, factuality, and persona alignment checks.
"""

import sys
import os
from typing import Dict, Any

# Add the current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from graph import validation_agent
from components.state import ValidationState


def print_test_header(test_name: str, test_number: int):
    """Print formatted test header"""
    print("\n" + "="*80)
    print(f"TEST {test_number}: {test_name}")
    print("="*80)


def print_example_content(content: str, persona: Dict = None, expected: Dict = None):
    """Print the test input and expected output"""
    print("\n📝 EXAMPLE CONTENT:")
    print("-" * 40)
    print(content)
    
    if persona:
        print("\n👤 PERSONA:")
        print("-" * 40)
        for key, value in persona.items():
            print(f"{key}: {value}")
    
    if expected:
        print("\n🎯 EXPECTED OUTPUT:")
        print("-" * 40)
        for key, value in expected.items():
            print(f"{key}: {value}")


def run_validation_test(content: str, persona: Dict = None, reference_info: str = None) -> Dict[str, Any]:
    """Run validation agent and return results"""
    print("\n🚀 RUNNING VALIDATION AGENT...")
    print("-" * 40)
    
    initial_state = {
        "content": content,
        "persona": persona,
        "reference_information": reference_info
    }
    
    try:
        result = validation_agent.invoke(initial_state)
        return result
    except Exception as e:
        print(f"❌ Error running validation: {e}")
        return {"error": str(e)}


def print_results(result: Dict[str, Any]):
    """Print formatted test results"""
    print("\n📊 AGENT RESULTS:")
    print("-" * 40)
    
    if "error" in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    # Overall status
    status = result.get("validation_status", "unknown")
    overall_confidence = result.get("overall_confidence", 0.0)
    status_emoji = "✅" if status == "pass" else "❌" if status == "fail" else "❓"
    print(f"Overall Status: {status_emoji} {status.upper()} (confidence: {overall_confidence:.2f})")
    
    # Individual check results with confidence
    safety = result.get("safety_passed", False)
    factuality = result.get("factuality_passed", False)
    persona = result.get("persona_passed", False)
    
    safety_conf = result.get("safety_confidence", 0.0)
    factuality_conf = result.get("factuality_confidence", 0.0)
    persona_conf = result.get("persona_confidence", 0.0)
    
    print(f"Safety Check: {'✅ PASS' if safety else '❌ FAIL'} (confidence: {safety_conf:.2f})")
    print(f"Factuality Check: {'✅ PASS' if factuality else '❌ FAIL'} (confidence: {factuality_conf:.2f})")
    print(f"Persona Check: {'✅ PASS' if persona else '❌ FAIL'} (confidence: {persona_conf:.2f})")
    
    # Confidence warnings
    if "confidence_warnings" in result:
        print("\n⚠️ Confidence Warnings:")
        for warning in result["confidence_warnings"]:
            print(f"  - {warning}")
    
    # Detailed results if available
    if "safety_check_result" in result:
        safety_details = result["safety_check_result"]
        if "explanation" in safety_details:
            print(f"\nSafety Details: {safety_details['explanation']}")
    
    if "factuality_check_result" in result:
        fact_details = result["factuality_check_result"]
        if "explanation" in fact_details:
            print(f"Factuality Details: {fact_details['explanation']}")
        if "accuracy_score" in fact_details:
            print(f"Accuracy Score: {fact_details['accuracy_score']:.2f}")
    
    if "persona_check_result" in result:
        persona_details = result["persona_check_result"]
        if "explanation" in persona_details:
            print(f"Persona Details: {persona_details['explanation']}")
        if "style_alignment_score" in persona_details:
            print(f"Style Alignment: {persona_details['style_alignment_score']:.2f}")
        if "tone_alignment_score" in persona_details:
            print(f"Tone Alignment: {persona_details['tone_alignment_score']:.2f}")
        if "audience_alignment_score" in persona_details:
            print(f"Audience Alignment: {persona_details['audience_alignment_score']:.2f}")


def test_case_1_clean_professional_content():
    """Test 1: Clean, professional content that should pass all checks"""
    print_test_header("Clean Professional Content", 1)
    
    content = """
    Welcome to our comprehensive guide on cloud computing best practices. 
    In this article, we'll explore proven strategies for implementing scalable 
    cloud infrastructure that can help your organization reduce costs while 
    improving performance. Our research shows that companies adopting these 
    practices see an average 30% improvement in operational efficiency.
    """
    
    persona = {
        "role": "Technology Consultant",
        "style": "Professional and informative",
        "audience": "IT professionals and decision makers",
        "tone": "Expert but accessible"
    }
    
    expected = {
        "safety_passed": True,
        "factuality_passed": True,
        "persona_passed": True,
        "validation_status": "pass"
    }
    
    print_example_content(content.strip(), persona, expected)
    result = run_validation_test(content.strip(), persona)
    print_results(result)


def test_case_2_unsafe_content():
    """Test 2: Content with safety issues that should fail safety check"""
    print_test_header("Unsafe Content", 2)
    
    content = """
    I hate dealing with incompetent developers who write terrible code. 
    These idiots don't deserve their jobs and should be fired immediately. 
    Anyone who can't write basic functions is a complete waste of space.
    """
    
    persona = {
        "role": "Technology Consultant",
        "style": "Professional and informative",
        "audience": "IT professionals",
        "tone": "Respectful and constructive"
    }
    
    expected = {
        "safety_passed": False,
        "factuality_passed": True,  # May pass as it's opinion-based
        "persona_passed": False,    # Doesn't match professional persona
        "validation_status": "fail"
    }
    
    print_example_content(content.strip(), persona, expected)
    result = run_validation_test(content.strip(), persona)
    print_results(result)


def test_case_3_factually_incorrect():
    """Test 3: Content with factual errors that should fail fact check"""
    print_test_header("Factually Incorrect Content", 3)
    
    content = """
    Python was created in 1995 by Linus Torvalds as a replacement for C++. 
    It's primarily used for hardware programming and doesn't support object-oriented 
    programming. Python code is compiled to machine code before execution, 
    making it faster than languages like JavaScript and Java.
    """
    
    persona = {
        "role": "Programming Instructor",
        "style": "Educational and accurate",
        "audience": "Programming students",
        "tone": "Clear and informative"
    }
    
    expected = {
        "safety_passed": True,
        "factuality_passed": False,  # Multiple factual errors
        "persona_passed": True,      # Style matches educational persona
        "validation_status": "fail"
    }
    
    print_example_content(content.strip(), persona, expected)
    result = run_validation_test(content.strip(), persona)
    print_results(result)


def test_case_4_persona_mismatch():
    """Test 4: Content that doesn't match the specified persona"""
    print_test_header("Persona Mismatch", 4)
    
    content = """
    OMG! This new JavaScript framework is absolutely INSANE! 🔥🔥🔥 
    You guys NEED to check this out RIGHT NOW! It's going to blow your minds! 
    Like and subscribe for more epic coding content! #JavaScript #Coding #Epic
    """
    
    persona = {
        "role": "Senior Software Architect",
        "style": "Professional and technical",
        "audience": "Enterprise development teams",
        "tone": "Formal and analytical"
    }
    
    expected = {
        "safety_passed": True,
        "factuality_passed": True,   # General statement, not specific claims
        "persona_passed": False,     # Social media style vs professional persona
        "validation_status": "fail"
    }
    
    print_example_content(content.strip(), persona, expected)
    result = run_validation_test(content.strip(), persona)
    print_results(result)


def test_case_5_perfect_match():
    """Test 5: Content perfectly aligned with persona and factually accurate"""
    print_test_header("Perfect Match", 5)
    
    content = """
    As a senior data scientist, I've observed that implementing proper data 
    validation pipelines is crucial for maintaining model accuracy. Based on 
    our team's experience with production ML systems, I recommend establishing 
    clear data quality metrics and automated monitoring. This approach has 
    helped us maintain 99.5% model reliability across our deployment pipeline.
    """
    
    persona = {
        "role": "Senior Data Scientist",
        "style": "Technical and experience-based",
        "audience": "Data science professionals",
        "tone": "Authoritative but collaborative"
    }
    
    expected = {
        "safety_passed": True,
        "factuality_passed": True,
        "persona_passed": True,
        "validation_status": "pass"
    }
    
    print_example_content(content.strip(), persona, expected)
    result = run_validation_test(content.strip(), persona)
    print_results(result)


def test_case_6_no_persona():
    """Test 6: Content without persona - should skip persona check"""
    print_test_header("No Persona Provided", 6)
    
    content = """
    Machine learning has revolutionized how we approach data analysis. 
    Modern algorithms can process vast amounts of information and identify 
    patterns that would be impossible for humans to detect manually. 
    This technology continues to evolve and improve across various industries.
    """
    
    expected = {
        "safety_passed": True,
        "factuality_passed": True,
        "persona_passed": True,      # Should auto-pass when no persona
        "validation_status": "pass"
    }
    
    print_example_content(content.strip(), None, expected)
    result = run_validation_test(content.strip())
    print_results(result)


def test_case_7_with_reference_info():
    """Test 7: Content with reference information for fact checking"""
    print_test_header("Content with Reference Information", 7)
    
    content = """
    According to our recent study, 85% of companies reported improved 
    productivity after implementing remote work policies. The study also 
    found that employee satisfaction increased by 40% on average.
    """
    
    reference_info = """
    Recent Study Results:
    - 1000 companies surveyed
    - 78% reported improved productivity (not 85%)
    - Employee satisfaction increased by 35% (not 40%)
    - Study conducted over 6 months in 2024
    """
    
    persona = {
        "role": "Business Analyst",
        "style": "Data-driven and precise",
        "audience": "Business executives",
        "tone": "Professional and analytical"
    }
    
    expected = {
        "safety_passed": True,
        "factuality_passed": False,  # Numbers don't match reference
        "persona_passed": True,
        "validation_status": "fail"
    }
    
    print_example_content(content.strip(), persona, expected)
    print(f"\n📚 REFERENCE INFORMATION:\n{reference_info.strip()}")
    result = run_validation_test(content.strip(), persona, reference_info.strip())
    print_results(result)


def run_all_tests():
    """Run all test cases"""
    print("🧪 VALIDATION AGENT COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Testing validation agent with various content types and scenarios...")
    
    test_functions = [
        test_case_1_clean_professional_content,
        test_case_2_unsafe_content,
        test_case_3_factually_incorrect,
        test_case_4_persona_mismatch,
        test_case_5_perfect_match,
        test_case_6_no_persona,
        test_case_7_with_reference_info
    ]
    
    for i, test_func in enumerate(test_functions, 1):
        try:
            test_func()
        except Exception as e:
            print(f"\n❌ Test {i} failed with error: {e}")
        
        if i < len(test_functions):
            input("\n⏸️  Press Enter to continue to next test...")
    
    print("\n" + "="*80)
    print("🏁 ALL TESTS COMPLETED!")
    print("="*80)


if __name__ == "__main__":
    run_all_tests()