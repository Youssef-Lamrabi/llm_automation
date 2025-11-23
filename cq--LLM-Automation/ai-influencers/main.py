#!/usr/bin/env python3
"""
AI Influencers Workflow Runner

This script runs the complete content creation workflow using the orchestrator agent.
Creates content from topic to final output ready for publishing.
"""

import sys
import os
import json
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the agent registry
from agents import REGISTRY, get

def print_banner(title: str):
    """Print a styled banner for section headers."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step: str, status: str = ""):
    """Print a workflow step with status."""
    status_icon = {"✅": "✅", "❌": "❌", "🔄": "🔄", "📝": "📝", "🎯": "🎯"}.get(status, "🔹")
    print(f"{status_icon} {step}")

def load_personas():
    """Load persona data from the data/personas directory."""
    personas = {}
    
    # Path to personas directory
    personas_dir = Path(__file__).parent.parent / "data" / "personas"
    
    if not personas_dir.exists():
        print(f"⚠️  Personas directory not found: {personas_dir}")
        return {}
    
    # Load all JSON persona files
    for persona_file in personas_dir.glob("*.json"):
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                persona_data = json.load(f)
                
                # Use the complete JSON data as-is
                persona_id = persona_data.get("Persona_ID", persona_file.stem)
                personas[persona_id] = persona_data
                
        except Exception as e:
            print(f"⚠️  Error loading persona {persona_file}: {e}")
    
    return personas

def get_user_input():
    """Get workflow parameters from user input."""
    print_banner("AI INFLUENCERS CONTENT WORKFLOW")
    print("Let's create some content! Please provide the following details:\n")
    
    # Platform selection - only supported platforms
    platforms = ["X", "LinkedIn"]  # Currently supported platforms
    print("📱 Available platforms:")
    for i, platform in enumerate(platforms, 1):
        print(f"  {i}. {platform}")
    
    while True:
        try:
            choice = int(input("\nSelect platform (1-2): ")) - 1
            if 0 <= choice < len(platforms):
                platform = platforms[choice]
                break
            else:
                print("❌ Please select a valid option (1-2)")
        except ValueError:
            print("❌ Please enter a number")
    
    # Content type based on platform - only supported types
    content_types = {
        "LinkedIn": ["text-only"],  # LinkedIn text-only posts
        "X": ["tweet"],             # X tweets
    }
    
    available_types = content_types.get(platform, ["text-only"])
    if len(available_types) > 1:
        print(f"\n📝 Available content types for {platform}:")
        for i, ctype in enumerate(available_types, 1):
            print(f"  {i}. {ctype}")
        
        while True:
            try:
                choice = int(input(f"\nSelect content type (1-{len(available_types)}): ")) - 1
                if 0 <= choice < len(available_types):
                    content_type = available_types[choice]
                    break
                else:
                    print(f"❌ Please select a valid option (1-{len(available_types)})")
            except ValueError:
                print("❌ Please enter a number")
    else:
        content_type = available_types[0]
        print(f"\n📝 Content type: {content_type}")
    
    # Topic
    topic = input("\n💡 Enter your topic: ").strip()
    while not topic:
        topic = input("❌ Topic cannot be empty. Please enter a topic: ").strip()
    
    # Load personas from data files
    personas = load_personas()
    
    if not personas:
        print("⚠️  No personas found. Using default persona.")
        selected_persona = {
            "name": "Default Creator",
            "style": "professional and engaging",
            "expertise": ["content creation", "social media"],
            "tone": "helpful and informative"
        }
    else:
        print("\n👤 Available personas:")
        persona_list = list(personas.keys())
        for i, persona_id in enumerate(persona_list, 1):
            persona = personas[persona_id]
            # Show basic info for selection
            style = persona.get('Communication_Style', '')
            role = persona.get('Current_Role', '')
            description = f"{role} - {style}" if role and style else persona_id
            print(f"  {i}. {persona_id}: {description}")
        
        while True:
            try:
                choice = int(input(f"\nSelect persona (1-{len(persona_list)}): ")) - 1
                if 0 <= choice < len(persona_list):
                    # Pass the complete JSON data as-is
                    selected_persona = personas[persona_list[choice]]
                    break
                else:
                    print(f"❌ Please select a valid option (1-{len(persona_list)})")
            except ValueError:
                print("❌ Please enter a number")
    
    return {
        "platform": platform,
        "content_type": content_type,
        "topic": topic,
        "persona": selected_persona,
        "time": datetime.now().isoformat()
    }

def run_workflow(workflow_input):
    """Run the complete content creation workflow."""
    print_banner("RUNNING CONTENT CREATION WORKFLOW")
    
    # Get orchestrator from registry
    entry = get("orchestrator")
    orchestrator = entry["agent"]
    
    if not orchestrator:
        print_step("❌ Orchestrator agent not available", "❌")
        return False
    
    print_step("🎯 Starting orchestrated content creation workflow...", "🔄")
    print(f"📱 Platform: {workflow_input['platform']}")
    print(f"📝 Content Type: {workflow_input['content_type']}")
    print(f"💡 Topic: {workflow_input['topic']}")
    print(f"👤 Persona: {workflow_input['persona'].get('Persona_ID', workflow_input['persona'].get('name', 'Unknown'))}")
    
    try:
        # Run the orchestrator workflow
        result = orchestrator.invoke(workflow_input)
        
        print_step("🎉 Workflow completed successfully!", "✅")
        
        # Display results
        print_banner("WORKFLOW RESULTS")
        
        print_step(f"📋 Workflow ID: {result.get('workflow_id', 'N/A')}", "📝")
        print_step(f"🎯 Final Stage: {result.get('current_stage', 'unknown')}", "📝")
        
        # Content results
        if result.get('content'):
            print_step("📝 Generated Content:", "📝")
            print(f"\n{result['content']}\n")
            
            if result.get('hashtags'):
                print_step("🏷️  Hashtags:", "📝")
                print(f"{result['hashtags']}\n")
        
        # Validation results
        validation_status = result.get('validation_status', 'unknown')
        if validation_status == 'pass':
            print_step("✅ Content passed validation", "✅")
        elif validation_status == 'fail':
            print_step("❌ Content failed validation", "❌")
        else:
            print_step(f"🔍 Validation status: {validation_status}", "📝")
        
        # Individual validation checks
        if result.get('safety_passed') is not None:
            safety_icon = "✅" if result['safety_passed'] else "❌"
            print_step(f"{safety_icon} Safety check: {'Passed' if result['safety_passed'] else 'Failed'}", "📝")
        
        if result.get('factuality_passed') is not None:
            fact_icon = "✅" if result['factuality_passed'] else "❌"
            print_step(f"{fact_icon} Factuality check: {'Passed' if result['factuality_passed'] else 'Failed'}", "📝")
        
        if result.get('persona_passed') is not None:
            persona_icon = "✅" if result['persona_passed'] else "❌"
            print_step(f"{persona_icon} Persona check: {'Passed' if result['persona_passed'] else 'Failed'}", "📝")
        
        # Confidence score
        if result.get('overall_confidence') is not None:
            confidence = result['overall_confidence']
            print_step(f"🎯 Overall Confidence: {confidence:.2f}", "📝")
        
        # Media results
        media_status = result.get('media_generation_status', 'unknown')
        if media_status == 'completed':
            print_step("🎨 Media generation completed", "✅")
            if result.get('media_assets'):
                print_step(f"📁 Media files: {len(result['media_assets'])} created", "📝")
        elif media_status == 'not_required':
            print_step("🎨 No media required for this content", "📝")
        else:
            print_step(f"🎨 Media status: {media_status}", "📝")
        
        # Publishing results
        pub_status = result.get('publication_status', 'unknown')
        pub_metadata = result.get('publication_metadata', {})
        
        if pub_status == 'draft':
            print_step("📤 Content saved as draft (ready for publishing)", "📝")
        elif pub_status == 'published':
            print_step("📤 Content published successfully!", "✅")
            
            # Show detailed publishing information
            if pub_metadata:
                print("\n" + "─" * 60)
                print("📤 PUBLICATION DETAILS:")
                print("─" * 60)
                print(f"  🌐 Platform: {pub_metadata.get('platform', 'Unknown')}")
                print(f"  🆔 Post ID: {pub_metadata.get('post_id', 'N/A')}")
                print(f"  � URL: {pub_metadata.get('post_url', 'N/A')}")
                print(f"  ⏰ Published: {pub_metadata.get('published_at', 'N/A')}")
                print(f"  👤 Persona: {pub_metadata.get('persona_id', 'N/A')}")
                
                if pub_metadata.get('message'):
                    print(f"  💬 Message: {pub_metadata.get('message')}")
                
                if pub_metadata.get('content_preview'):
                    print(f"\n  📝 Preview: {pub_metadata.get('content_preview')}")
                
                print("─" * 60)
        else:
            print_step(f"�📤 Publishing status: {pub_status}", "📝")
            if pub_metadata.get('error'):
                print(f"     ⚠️  Error: {pub_metadata.get('error')}")
        
        return True
        
    except Exception as e:
        print_step(f"❌ Workflow failed: {str(e)}", "❌")
        print(f"\n🔍 Error details: {e}")
        return False

def main():
    """Main workflow runner."""
    try:
        # Get user input for the workflow
        workflow_input = get_user_input()
        
        # Run the workflow
        success = run_workflow(workflow_input)
        
        if success:
            print_banner("SUCCESS!")
            print("🎉 Your content has been created successfully!")
            print("📝 Review the results above and publish when ready.")
        else:
            print_banner("WORKFLOW FAILED")
            print("❌ The content creation workflow encountered an error.")
            print("🔍 Please check the error details above.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Workflow cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()