"""
Orchestrator Agent Nodes

Contains LangGraph nodes that coordinate the execution of individual AI agents
in the content creation pipeline. Each node handles calling a specific agent
and managing state transitions.
"""

import uuid
from datetime import datetime
from typing import Dict, Any

from .state import OrchestratorState
from validation_agent import agent as validation_agent
from content_generator_agent import agent as content_generator_agent

def initialize_workflow(state: OrchestratorState) -> OrchestratorState:
    """Initialize the orchestrator workflow with metadata and defaults."""
    print("🚀 Initializing AI Influencer Content Pipeline...")
    
    workflow_id = state.get("workflow_id", str(uuid.uuid4())[:8])
    current_time = datetime.now().isoformat()
    
    # Validate required input parameters
    required_fields = ["time", "platform", "content_type", "topic", "persona"]
    missing_fields = [field for field in required_fields if not state.get(field)]
    
    if missing_fields:
        return {
            **state,
            "workflow_id": workflow_id,
            "current_stage": "initialization",
            "created_at": current_time,
            "updated_at": current_time,
            "error": f"Missing required fields: {', '.join(missing_fields)}"
        }
    
    print(f"📋 Workflow ID: {workflow_id}")
    print(f"🎯 Platform: {state.get('platform')}")
    print(f"📝 Content Type: {state.get('content_type')}")
    print(f"💡 Topic: {state.get('topic')}")
    print("✅ Initialization complete!")
    
    return {
        **state,
        "workflow_id": workflow_id,
        "current_stage": "content_generation",
        "created_at": current_time,
        "updated_at": current_time,
        "retry_count": 0
    }


def content_generation(state: OrchestratorState) -> OrchestratorState:
    """Execute the Content Generator Agent."""
    print("\n📝 STAGE 1: Content Generation")
    print("=" * 50)
    
    try:
        # Prepare input for content generator
        content_gen_input = {
            "time": state.get("time", ""),
            "platform": state.get("platform", ""),
            "content_type": state.get("content_type", ""),
            "topic": state.get("topic", ""),
            "persona": state.get("persona", {})
        }
        
        print(f"📤 Calling Content Generator Agent...")
        print(f"   Platform: {content_gen_input['platform']}")
        print(f"   Content Type: {content_gen_input['content_type']}")
        print(f"   Topic: {content_gen_input['topic']}")
        
        # Execute content generator agent
        result = content_generator_agent.invoke(content_gen_input)
        
        print("✅ Content generation completed!")
        print(f"📝 Generated content: {result.get('content', '')[:100]}...")
        
        # Map results back to orchestrator state
        return {
            **state,
            "current_stage": "validation",
            "content": result.get("content", ""),
            "hashtags": result.get("hashtags", ""),
            "media_type": result.get("media_type", "none"),
            "content_metadata": result.get("metadata", {}),
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Content generation failed: {str(e)}")
        return {
            **state,
            "current_stage": "content_generation",
            "error": f"Content generation failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        }


def validation(state: OrchestratorState) -> OrchestratorState:
    """Execute the Validation Agent."""
    print("\n🔍 STAGE 2: Content Validation")
    print("=" * 50)
    
    try:
        # Prepare input for validation agent
        validation_input = {
            "content": state.get("content", ""),
            "persona": state.get("persona", {}),
            "metadata": state.get("content_metadata", {}),
            "reference_information": None
        }
        
        print(f"📤 Calling Validation Agent...")
        print(f"   Content length: {len(validation_input['content'])} characters")
        print(f"   Persona: {validation_input['persona'].get('Persona_ID', validation_input['persona'].get('name', 'Unknown'))}")
        
        # Execute validation agent
        result = validation_agent.invoke(validation_input)
        
        validation_status = result.get("validation_status", "fail")
        print(f"✅ Validation completed: {validation_status}")
        print(f"🛡️  Safety: {'✅' if result.get('safety_passed') else '❌'}")
        print(f"📊 Factuality: {'✅' if result.get('factuality_passed') else '❌'}")
        print(f"🎭 Persona: {'✅' if result.get('persona_passed') else '❌'}")
        print(f"🎯 Confidence: {result.get('overall_confidence', 0):.2f}")
        
        # Map results back to orchestrator state
        return {
            **state,
            "current_stage": "media_building" if validation_status == "pass" else "validation",
            "validation_status": validation_status,
            "safety_passed": result.get("safety_passed", False),
            "factuality_passed": result.get("factuality_passed", False),
            "persona_passed": result.get("persona_passed", False),
            "overall_confidence": result.get("overall_confidence", 0.0),
            "validation_details": {
                "safety_confidence": result.get("safety_confidence", 0.0),
                "factuality_confidence": result.get("factuality_confidence", 0.0),
                "persona_confidence": result.get("persona_confidence", 0.0),
                "confidence_warnings": result.get("confidence_warnings", [])
            },
            "updated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Validation failed: {str(e)}")
        return {
            **state,
            "current_stage": "validation",
            "validation_status": "fail",
            "error": f"Validation failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        }


def media_building(state: OrchestratorState) -> OrchestratorState:
    """Execute the Media Builder Agent to generate social media images."""
    print("\n🎨 STAGE 3: Media Building")
    print("=" * 50)
    
    media_type = state.get("media_type", "none")
    
    # Skip media building only if no media is required
    if media_type == "none":
        print("⏭️  No media required - proceeding to human approval")
        return {
            **state,
            "current_stage": "human_approval",
            "media_generation_status": "not_required",
            "media_assets": [],
            "media_metadata": {"media_type": "none"},
            "updated_at": datetime.now().isoformat()
        }
    
    try:
        # Import media builder agent
        from media_builder_agent import agent as media_builder_agent
        
        # Prepare input for media builder
        media_input = {
            "content": state.get("content", ""),
            "platform": state.get("platform", ""),
            "persona": state.get("persona", {}),
            "topic": state.get("topic", "")
        }
        
        print(f"� Calling Media Builder Agent...")
        print(f"   Platform: {media_input['platform']}")
        print(f"   Topic: {media_input['topic']}")
        
        # Execute media builder agent
        result = media_builder_agent.invoke(media_input)
        
        if result.get("media_status") == "completed" and result.get("image_data"):
            print("✅ Media building completed!")
            print(f"   Image prompt: {result.get('image_prompt', '')[:100]}...")
            
            # Save the generated image
            image_path = None
            try:
                from pathlib import Path
                
                # Create output directory
                output_dir = Path(__file__).parent.parent.parent.parent / "generated_images"
                output_dir.mkdir(exist_ok=True)
                
                # Save with workflow_id and timestamp
                workflow_id = state.get("workflow_id", "unknown")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                platform = state.get("platform", "unknown")
                image_filename = f"{platform}_{workflow_id}_{timestamp}.png"
                image_path = output_dir / image_filename
                
                with open(image_path, "wb") as f:
                    f.write(result.get("image_data"))
                
                print(f"   💾 Image saved: {image_path}")
            except Exception as e:
                print(f"   ⚠️ Failed to save image: {e}")
            
            return {
                **state,
                "current_stage": "human_approval",
                "media_generation_status": "completed",
                "image_prompt": result.get("image_prompt", ""),
                "image_data": result.get("image_data"),
                "image_path": str(image_path) if image_path else None,
                "media_metadata": {
                    "media_type": "image",
                    "status": "generated",
                    "prompt": result.get("image_prompt", ""),
                    "saved_path": str(image_path) if image_path else None
                },
                "updated_at": datetime.now().isoformat()
            }
        else:
            print(f"⚠️ Media generation had issues: {result.get('error', 'Unknown error')}")
            return {
                **state,
                "current_stage": "human_approval",
                "media_generation_status": "failed",
                "error": result.get("error", "Media generation failed"),
                "updated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ Media building failed: {str(e)}")
        return {
            **state,
            "current_stage": "human_approval",
            "media_generation_status": "error",
            "error": f"Media building error: {str(e)}",
            "updated_at": datetime.now().isoformat()
        }


def publishing(state: OrchestratorState) -> OrchestratorState:
    """Execute the Publishing Agent using the existing publishing system."""
    print("\n📤 STAGE 4: Publishing")
    print("=" * 50)
    
    try:
        platform = state.get("platform", "").lower()
        content = state.get("content", "")
        hashtags = state.get("hashtags", "")
        scheduled_time = state.get("time", "")
        persona = state.get("persona", {})
        
        # Map platform names to match publishing agent's expectations
        platform_mapping = {
            "x": "Twitter",
            "twitter": "Twitter",
            "linkedin": "LinkedIn",
            "instagram": "Instagram",
            "medium": "Medium",
            "reddit": "Reddit"
        }
        
        mapped_platform = platform_mapping.get(platform, "Twitter")
        
        print(f"📋 Target platform: {mapped_platform}")
        print(f"📝 Content: {content[:100]}...")
        print(f"🏷️  Hashtags: {hashtags}")
        
        # Import publishing agent components
        try:
            from publishing_agent.components.nodes import prepare_post, publish_post
            
            # Prepare entry in the format expected by publishing agent
            entry = {
                "Content": content,
                "Hashtags": hashtags,
                "Platform": mapped_platform,
                "Date": scheduled_time.split("T")[0] if "T" in scheduled_time else datetime.now().strftime("%Y-%m-%d"),
                "Time": scheduled_time.split("T")[1].replace("Z", "") if "T" in scheduled_time else datetime.now().strftime("%H:%M:%S"),
                "Persona": persona.get("Persona_ID", "neuralNinja")
            }
            
            # Prepare the post
            print("� Preparing post for publication...")
            prepared_state = prepare_post(entry)
            
            # Publish the post
            print("🚀 Publishing to platform...")
            result = publish_post(prepared_state)
            
            # Check result
            if result.get("status") == "success":
                print(f"\n✅ Successfully published to {mapped_platform}!")
                print("=" * 50)
                print(f"� PUBLICATION DETAILS:")
                print(f"   Platform: {mapped_platform}")
                print(f"   Post ID: {result.get('tweet_id') or result.get('platform_id', 'N/A')}")
                print(f"   Post URL: {result.get('post_url', 'N/A')}")
                print(f"   Published At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   Status Message: {result.get('message', 'Success')}")
                print(f"\n📝 PUBLISHED CONTENT:")
                print(f"   {prepared_state.get('formatted_text', content)[:200]}...")
                print(f"\n🎯 PERSONA: {persona.get('Persona_ID', 'Unknown')}")
                print(f"📊 SCHEDULED TIME: {scheduled_time}")
                print("=" * 50)
                
                return {
                    **state,
                    "current_stage": "completed",
                    "publication_status": "published",
                    "publication_metadata": {
                        "platform": mapped_platform,
                        "status": "success",
                        "post_id": result.get("tweet_id") or result.get("platform_id"),
                        "post_url": result.get("post_url"),
                        "message": result.get("message"),
                        "published_at": datetime.now().isoformat(),
                        "scheduled_time": scheduled_time,
                        "persona_id": persona.get("Persona_ID", "Unknown"),
                        "content_preview": content[:100] + "..." if len(content) > 100 else content
                    },
                    "updated_at": datetime.now().isoformat()
                }
            else:
                print(f"❌ Publishing failed: {result.get('message', 'Unknown error')}")
                return {
                    **state,
                    "current_stage": "completed",
                    "publication_status": "failed",
                    "publication_metadata": {
                        "platform": mapped_platform,
                        "status": "failed",
                        "error": result.get("message", "Unknown error")
                    },
                    "error": f"Publishing failed: {result.get('message')}",
                    "updated_at": datetime.now().isoformat()
                }
                
        except ImportError as e:
            print(f"⚠️  Publishing Agent not available: {e}")
            print("📋 Marking as draft...")
            return {
                **state,
                "current_stage": "completed",
                "publication_status": "draft",
                "publication_metadata": {
                    "platform": mapped_platform,
                    "status": "draft",
                    "reason": "Publishing agent not available"
                },
                "updated_at": datetime.now().isoformat()
            }
            
    except Exception as e:
        print(f"❌ Publishing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            **state,
            "current_stage": "completed",
            "publication_status": "failed",
            "publication_metadata": {
                "platform": state.get("platform", "Unknown"),
                "status": "failed",
                "error": str(e)
            },
            "error": f"Publishing failed: {str(e)}",
            "updated_at": datetime.now().isoformat()
        }


def finalization(state: OrchestratorState) -> OrchestratorState:
    """Finalize the workflow and provide summary."""
    print("\n🎉 PIPELINE COMPLETE!")
    print("=" * 50)
    
    workflow_id = state.get("workflow_id", "Unknown")
    print(f"📋 Workflow ID: {workflow_id}")
    print(f"🎯 Platform: {state.get('platform', 'Unknown')}")
    print(f"📝 Content Type: {state.get('content_type', 'Unknown')}")
    print(f"💡 Topic: {state.get('topic', 'Unknown')}")
    
    # Summary of results
    print(f"\n📊 RESULTS SUMMARY:")
    print(f"   ✍️  Content Generated: {'✅' if state.get('content') else '❌'}")
    print(f"   🔍 Validation: {state.get('validation_status', 'Unknown')}")
    print(f"   🎨 Media: {state.get('media_generation_status', 'Unknown')}")
    print(f"   📤 Publishing: {state.get('publication_status', 'Unknown')}")
    
    # Show detailed publishing info if published successfully
    pub_metadata = state.get('publication_metadata', {})
    if state.get('publication_status') == 'published' and pub_metadata:
        print(f"\n🚀 PUBLICATION SUCCESS DETAILS:")
        print(f"   Platform: {pub_metadata.get('platform', 'Unknown')}")
        print(f"   Post ID: {pub_metadata.get('post_id', 'N/A')}")
        print(f"   Post URL: {pub_metadata.get('post_url', 'N/A')}")
        print(f"   Published: {pub_metadata.get('published_at', 'N/A')}")
        print(f"   Persona: {pub_metadata.get('persona_id', 'N/A')}")
    
    if state.get("error"):
        print(f"   ⚠️  Error: {state.get('error')}")
    
    return {
        **state,
        "current_stage": "completed",
        "updated_at": datetime.now().isoformat()
    }