import streamlit as st
import sys
import os
import json
from datetime import datetime, timedelta
from pathlib import Path
import time
import os

# Configuration pour Render (important !)
if 'RENDER' in os.environ:
    # Sur Render, utiliser le port fourni par la variable d'environnement
    pass
# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the agent registry
from agents import REGISTRY, get

# Import publishing agent
try:
    from agents.publishing_agent.agent import publish_content
    PUBLISHING_AVAILABLE = True
except ImportError as e:
    PUBLISHING_AVAILABLE = False
    print(f"Warning: Publishing not available: {e}")

# Page configuration
st.set_page_config(
    page_title="AI Influencers Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #333;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    .persona-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    
    .content-result {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
    }
    
    .validation-success {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .validation-fail {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

def load_personas():
    """Load persona data from the data/personas directory."""
    personas = {}
    
    # Path to personas directory
    personas_dir = Path(__file__).resolve().parent.parent / "data" / "personas"
    
    if not personas_dir.exists():
        st.error(f"⚠️ Personas directory not found: {personas_dir}")
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
            st.error(f"⚠️ Error loading persona {persona_file}: {e}")
    
    return personas

def display_persona_card(persona_data):
    """Display a beautiful persona card."""
    persona_id = persona_data.get("Persona_ID", "Unknown")
    role = persona_data.get("Current_Role", "")
    style = persona_data.get("Communication_Style", "")
    tagline = persona_data.get("Tagline", "")
    
    st.markdown(f"""
    <div class="persona-card">
        <h3>{persona_id}</h3>
        <p><strong>Role:</strong> {role}</p>
        <p><strong>Style:</strong> {style}</p>
        <p><strong>Tagline:</strong> "{tagline}"</p>
    </div>
    """, unsafe_allow_html=True)

def run_workflow(platform, content_type, topic, persona_data, schedule_for_publishing=False):
    """Run the AI content creation workflow."""
    
    # Get orchestrator from registry
    try:
        entry = get("orchestrator")
        orchestrator = entry["agent"]
    except Exception as e:
        st.error(f"❌ Failed to get orchestrator: {e}")
        return None
    
    if not orchestrator:
        st.error("❌ Orchestrator agent not available")
        return None
    
    # Prepare workflow input
    workflow_input = {
        "platform": platform,
        "content_type": content_type,
        "topic": topic,
        "persona": persona_data,
        "time": datetime.now().isoformat(),
        "schedule_for_publishing": schedule_for_publishing
    }
    
    try:
        # Run the orchestrator workflow
        with st.spinner("🤖 AI is creating your content..."):
            result = orchestrator.invoke(workflow_input)
        
        return result
        
    except Exception as e:
        st.error(f"❌ Workflow failed: {str(e)}")
        st.error(f"Error type: {type(e).__name__}")
        st.error(f"Error details: {e}")
        return None

def publish_or_schedule_content(content, hashtags, platform, persona_data, scheduled_time=None):
    """Publish or schedule content using the publishing agent."""
    
    if not PUBLISHING_AVAILABLE:
        st.error("❌ Publishing functionality is not available. Please install required packages.")
        return None
    
    try:
        # Get persona ID
        persona_id = persona_data.get("Persona_ID", "Unknown")
        
        # Call the publishing agent
        with st.spinner("📤 Publishing content..." if not scheduled_time else "📅 Scheduling content..."):
            result = publish_content(
                content=content,
                hashtags=hashtags,
                platform=platform,
                scheduled_time=scheduled_time,
                persona=persona_id
            )
        
        return result
        
    except Exception as e:
        st.error(f"❌ Publishing failed: {str(e)}")
        return None

def display_results(result, show_publishing_options=True):
    """Display the workflow results beautifully."""
    if not result:
        return
    
    # Main content result
    content = result.get('content', 'No content generated')
    hashtags = result.get('hashtags', '')
    
    st.markdown(f"""
    <div class="content-result">
        <h2>📝 Generated Content</h2>
        <p style="font-size: 1.1rem; line-height: 1.6;">{content}</p>
        {f'<p><strong>🏷️ Hashtags:</strong> {hashtags}</p>' if hashtags else ''}
    </div>
    """, unsafe_allow_html=True)
    
    # Display generated image if available
    image_data = result.get('image_data')
    image_path = result.get('image_path')
    media_status = result.get('media_generation_status', 'not_required')
    
    if media_status == "completed" and image_data:
        st.markdown("### 🖼️ Generated Image")
        st.image(image_data, use_column_width=True)
        if image_path:
            st.caption(f"💾 Saved to: {image_path}")
    elif media_status == "not_required":
        st.info("📝 Text-only post (no image generated)")
    elif media_status in ["failed", "error"]:
        st.warning(f"⚠️ Image generation {media_status}: {result.get('error', 'Unknown error')}")
    
    # Validation results
    validation_status = result.get('validation_status', 'unknown')
    
    if validation_status == 'pass':
        st.markdown("""
        <div class="validation-success">
            <h3>✅ Validation Results - PASSED</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="validation-fail">
            <h3>❌ Validation Results - FAILED</h3>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        safety = "✅" if result.get('safety_passed') else "❌"
        st.metric("🛡️ Safety", safety)
    
    with col2:
        factuality = "✅" if result.get('factuality_passed') else "❌"
        st.metric("📊 Factuality", factuality)
    
    with col3:
        persona = "✅" if result.get('persona_passed') else "❌"
        st.metric("🎭 Persona", persona)
    
    with col4:
        confidence = result.get('overall_confidence', 0)
        st.metric("🎯 Confidence", f"{confidence:.2f}")
    
    # Publishing status if available
    publication_metadata = result.get('publication_metadata')
    if publication_metadata:
        st.markdown("---")
        st.markdown("### 📤 Publication Details")
        
        pub_col1, pub_col2, pub_col3 = st.columns(3)
        
        with pub_col1:
            st.info(f"**Platform:** {publication_metadata.get('platform', 'N/A')}")
        
        with pub_col2:
            status = publication_metadata.get('status', 'N/A')
            if status == 'published':
                st.success(f"**Status:** ✅ {status}")
            elif status == 'scheduled':
                st.warning(f"**Status:** 📅 {status}")
            else:
                st.info(f"**Status:** {status}")
        
        with pub_col3:
            st.info(f"**Published:** {publication_metadata.get('published_at', 'N/A')}")
        
        # Show post URL if available
        post_url = publication_metadata.get('post_url')
        if post_url and post_url != 'N/A':
            st.success(f"🔗 **Post URL:** {post_url}")
        
        # Show post ID
        post_id = publication_metadata.get('post_id')
        if post_id:
            st.info(f"📋 **Post ID:** {post_id}")
    
    return content, hashtags

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">AI Influencers Studio</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create engaging content with AI-powered personas</p>', unsafe_allow_html=True)
    
    # Sidebar for inputs
    with st.sidebar:
        st.markdown("## Content Configuration")
        
        mode = "Create Content"
        
        if True:
            # Platform selection
            platform = st.selectbox(
                "Platform",
                ["X", "LinkedIn", "Medium", "Instagram", "Reddit"],
                help="Choose the social media platform for your content"
            )
            
            # Content type (auto-selected based on platform)
            content_types = {
                "LinkedIn": "text-only",
                "X": "tweet",
                "Medium": "article",
                "Instagram": "post",
                "Reddit": "post"
            }
            content_type = content_types[platform]
            st.info(f"Content Type: {content_type}")
            
            # Topic input
            topic = st.text_input(
                "Content Topic",
                placeholder="e.g., The future of AI in healthcare",
                help="Enter the topic you want to create content about"
            )
            
            # Publishing/Scheduling Options
            st.markdown("---")
            st.markdown("## Publishing Settings")
            
            publish_action = st.radio(
                "When to publish:",
                ["Save Only (Don't Publish)", "Publish Now", "Schedule for Later"],
                help="Choose when to publish the content"
            )
            
            scheduled_datetime = None
            if publish_action == "Schedule for Later":
                col1, col2 = st.columns(2)
                with col1:
                    schedule_date = st.date_input(
                        "Date",
                        value=datetime.now().date() + timedelta(days=1),
                        min_value=datetime.now().date(),
                        help="Select the date to publish"
                    )
                with col2:
                    schedule_time = st.time_input(
                        "Time",
                        value=datetime.now().time(),
                        help="Select the time to publish"
                    )
                scheduled_datetime = datetime.combine(schedule_date, schedule_time)
                st.info(f"Will be scheduled for: {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
            elif publish_action == "Publish Now":
                st.info("Content will be published immediately after generation")
            
            # Load and display personas
            st.markdown("## Select Persona")
            personas = load_personas()
            
            if not personas:
                st.error("No personas found!")
                return
            
            persona_options = list(personas.keys())
            selected_persona_key = st.selectbox(
                "Choose your AI persona",
                persona_options,
                format_func=lambda x: f"{x} - {personas[x].get('Current_Role', '')}"
            )
            
            # Display selected persona details
            if selected_persona_key:
                st.markdown("### Persona Preview")
                display_persona_card(personas[selected_persona_key])
    
    # Main content area
    if topic and selected_persona_key:
        col1, col2 = st.columns([3, 1])
        
        with col2:
            generate_button = st.button(
                "Generate Content",
                type="primary",
                use_container_width=True
            )
        
        if generate_button:
            selected_persona = personas[selected_persona_key]
            
            # Show generation progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Simulate progress updates
            status_text.text("Initializing workflow...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            status_text.text("Generating content...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            status_text.text("Validating content...")
            progress_bar.progress(75)
            time.sleep(0.5)
            
            status_text.text("Finalizing results...")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            # Run the workflow
            result = run_workflow(platform, content_type, topic, selected_persona)
            
            if result:
                # Store result in session state for publishing
                st.session_state['last_result'] = result
                st.session_state['last_persona'] = selected_persona
                st.session_state['last_platform'] = platform
                
                # Display results
                content, hashtags = display_results(result)
                
                # Auto-publish or schedule based on settings
                if PUBLISHING_AVAILABLE and result.get('validation_status') == 'pass':
                    if publish_action == "Publish Now":
                        st.markdown("---")
                        st.markdown("### Publishing")
                        
                        pub_result = publish_or_schedule_content(
                            content=content,
                            hashtags=hashtags,
                            platform=platform,
                            persona_data=selected_persona,
                            scheduled_time=None
                        )
                        
                        if pub_result and pub_result.get('status') == 'published':
                            st.success("Content published successfully!")
                            
                            # Show publication details
                            pub_col1, pub_col2 = st.columns(2)
                            with pub_col1:
                                if pub_result.get('post_url'):
                                    st.success(f"**Post URL:** {pub_result['post_url']}")
                            with pub_col2:
                                if pub_result.get('post_id'):
                                    st.info(f"**Post ID:** {pub_result['post_id']}")
                    
                    elif publish_action == "Schedule for Later":
                        st.markdown("---")
                        st.markdown("### Scheduling")
                        
                        pub_result = publish_or_schedule_content(
                            content=content,
                            hashtags=hashtags,
                            platform=platform,
                            persona_data=selected_persona,
                            scheduled_time=scheduled_datetime.isoformat() if scheduled_datetime else None
                        )
                        
                        if pub_result:
                            st.success(f"Content scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M')}")
                            if pub_result.get('post_id'):
                                st.info(f"**Scheduled ID:** {pub_result.get('post_id', 'N/A')}")
                
                elif not PUBLISHING_AVAILABLE and publish_action != "Save Only (Don't Publish)":
                    st.warning("Publishing functionality is not available. Install required packages to enable publishing.")
                elif result.get('validation_status') != 'pass' and publish_action != "Save Only (Don't Publish)":
                    st.warning("Content must pass validation before publishing.")
                
                # Download button for content
                st.markdown("---")
                content_text = f"""
Platform: {platform}
Topic: {topic}
Persona: {selected_persona_key}

Content:
{result.get('content', '')}

Hashtags:
{result.get('hashtags', '')}

Validation Status: {result.get('validation_status', 'unknown')}
Confidence Score: {result.get('overall_confidence', 0):.2f}
"""
                
                st.download_button(
                    "Download Content",
                    content_text,
                    file_name=f"ai_content_{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            
    else:
        # Welcome message
        st.markdown("""
        ## Welcome to AI Influencers Studio
        
        Create engaging social media content using AI-powered personas with automated validation and publishing.
        
        ### How it works:
        1. **Select your platform** - Choose between X (Twitter) or LinkedIn
        2. **Enter your topic** - What you want to create content about
        3. **Choose a persona** - Select an AI influencer with a unique voice and expertise
        4. **Set publishing preferences** - Publish now, schedule for later, or save only
        5. **Generate content** - AI creates, validates, and publishes your content
        
        ### Key Features:
        - **AI-Powered Generation** - Advanced language models create authentic, engaging content
        - **Unique Personas** - Each AI influencer has their own style, tone, and area of expertise
        - **Automatic Validation** - Content is checked for safety, factuality, and persona alignment
        - **Quality Metrics** - View confidence scores and detailed validation results
        - **Multi-Platform Support** - Optimized content for different social media platforms
        - **Flexible Publishing** - Publish immediately, schedule for specific times, or save drafts
        - **Schedule Management** - View and track all scheduled content across platforms
        
        ### Get Started
        Configure your content settings in the sidebar to begin creating AI-powered social media content.
        """)
        
        # Show sample personas
        if personas:
            st.markdown("### Available AI Personas")
            cols = st.columns(len(personas))
            
            for idx, (persona_key, persona_data) in enumerate(personas.items()):
                with cols[idx]:
                    display_persona_card(persona_data)

if __name__ == "__main__":
    # Configuration Streamlit pour production
    import streamlit.web.cli as stcli
    import sys
    
    if 'RENDER' not in os.environ:
        # Local : lance normalement
        main()
    else:
        # Production Render : utilise streamlit CLI
        sys.argv = ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
        sys.exit(stcli.main())