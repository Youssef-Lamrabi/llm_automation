from graph import content_generator_agent
from components.state import ContentGenState
from components.tools import PLATFORM_FILE_MAP, PLATFORM_CONTENT_TYPES
import json
import os

def load_persona_data(influencer_name):
    """
    Load persona data from JSON files based on influencer name.
    
    Args:
        influencer_name (str): Name of the influencer (case-insensitive)
        
    Returns:
        dict: Persona data or None if not found
    """
    # Available personas mapping (case-insensitive)
    persona_files = {
        "neuralninja": "neuralNinja.json",
        "frank": "frank_algoWizard.json",
        "algowizard": "frank_algoWizard.json"
    }
    
    # Normalize the input name
    normalized_name = influencer_name.lower().strip()
    
    # Check if the persona exists
    if normalized_name not in persona_files:
        print(f"❌ Persona '{influencer_name}' not found!")
        print(f"Available personas: {', '.join(list(persona_files.keys()))}")
        return None
    
    personas_dir = os.path.join("..", "..", "data", "personas")
    file_path = os.path.join(personas_dir, persona_files[normalized_name])
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            persona_data = json.load(f)
            
        # Return the complete JSON data directly to the agent
        return persona_data
        
    except FileNotFoundError:
        print(f"❌ Persona file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing persona file: {e}")
        return None
    except Exception as e:
        print(f"❌ Error loading persona data: {e}")
        return None

def main():
    print("=== Content Generator Agent (MVP) ===")
    print("Currently supports: X tweets and LinkedIn text-only posts")
    
    # Get input from user
    platform = input("Platform (LinkedIn/X): ") or "X"
    
    # Validate platform
    valid_platforms = list(PLATFORM_CONTENT_TYPES.keys())
    if platform not in valid_platforms:
        print(f"❌ Invalid platform. Choose from: {', '.join(valid_platforms)}")
        platform = "X"  # fallback
    
    # Get content type (simplified for MVP)
    available_types = PLATFORM_CONTENT_TYPES[platform]
    if len(available_types) == 1:
        content_type = available_types[0]
        print(f"Content type: {content_type} (only option for {platform})")
    else:
        print(f"Available content types for {platform}: {', '.join(available_types)}")
        content_type_choice = input("Choose content type: ").strip()
        if content_type_choice in available_types:
            content_type = content_type_choice
        else:
            content_type = available_types[0]
            print(f"❌ Invalid content type. Using default: {content_type}")
    
    topic = input("Topic: ")
    if not topic:
        print("❌ Topic is required!")
        return
        
    time = input("Scheduled time (YYYY-MM-DDTHH:MM:SSZ) [optional]: ") or "2025-09-23T14:30:00Z"
    
    # Get persona details - just ask for influencer name
    print("\n--- Persona Selection ---")
    print("Available influencers: NeuralNinja, Frank (AlgoWizard)")
    influencer_name = input("Influencer name: ")
    
    if not influencer_name:
        print("❌ Influencer name is required!")
        return
    
    # Load persona data from JSON files
    persona = load_persona_data(influencer_name)
    
    if not persona:
        print("❌ Failed to load persona data!")
        return
        
    print(f"✅ Loaded persona: {persona.get('Persona_ID', 'Unknown')} - {persona.get('Current_Role', 'Unknown Role')}")
    print(f"   Communication Style: {persona.get('Communication_Style', 'Unknown')}")
    print(f"   Tagline: {persona.get('Tagline', 'No tagline')}")
    
    # Create state dict
    state = {
        "time": time,
        "platform": platform,
        "content_type": content_type,
        "topic": topic,
        "persona": persona
    }
    
    print(f"\n🚀 Generating {content_type} content for {platform}...")
    
    try:
        # Run the agent
        final_state = content_generator_agent.invoke(state)
        
        # Check if generation was successful
        if not final_state.get('content'):
            print("❌ Content generation failed - no content produced")
            return
            
    except Exception as e:
        print(f"❌ Error during content generation: {e}")
        return
    
    # Print results
    print("\n===== GENERATED CONTENT =====")
    print(f"Content: {final_state.get('content')}")
    print(f"Hashtags: {final_state.get('hashtags')}")
    
    print("\n===== METADATA =====")
    print(json.dumps(final_state.get("metadata", {}), indent=2, ensure_ascii=False, default=str))
    
    print("\n===== PROCESSING DETAILS =====")
    print(f"Platform: {final_state.get('platform')}")
    print(f"Content Type: {final_state.get('content_type')}")
    print(f"Topic: {final_state.get('topic')}")
    print(f"Content Length: {len(final_state.get('content', ''))}")
    print(f"Hashtags Length: {len(final_state.get('hashtags', ''))}")
    print(f"Media Type: {final_state.get('media_type')}")
    
    print("\n===== PLATFORM RULES APPLIED =====")
    print(json.dumps(final_state.get("platform_rules", {}), indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()