# AI Influencers Studio

**Automated social media content creation with AI-powered validation, image generation, and multi-platform publishing.**

Create engaging, persona-driven content for X, LinkedIn, Instagram, Reddit, and Medium with built-in safety checks and AI-generated visuals.

---

## ✨ Features

- 🤖 **AI Content Generation**: Platform-optimized posts using persona-based writing styles
- ✅ **Automated Validation**: Safety, factuality, and persona consistency checks
- 🎨 **AI Image Generation**: Cloudflare-powered visuals for platforms like Instagram
- 📤 **Multi-Platform Publishing**: Direct posting to X, LinkedIn, Instagram, Reddit, Medium
- 🎭 **Persona Management**: Multiple AI influencer personalities with unique voices
- 🔄 **LangGraph Orchestration**: Coordinated multi-agent workflow pipeline

---

## � Quick Start

### Prerequisites

- Python 3.10+
- Groq API key (for LLM)
- Social media API credentials (for publishing)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/LotusCapital2025/cq--LLM-Automation.git
cd cq--LLM-Automation/ai-influencers
```

2. **Create virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Required environment variables in `.env`:

```bash
# LLM Configuration
GROQ_API_KEY=your_groq_api_key

# Image Generation
CLOUDFLARE_IMAGE_API_URL=
IMAGE_MODEL=@cf/leonardo/phoenix-1.0

# Publishing (optional - configure platforms you want to use)
X_ACCESS_TOKEN=your_twitter_token
LINKEDIN_ACCESS_TOKEN=your_linkedin_token
INSTAGRAM_ACCESS_TOKEN=your_instagram_token
# ... see .env.example for complete list
```

### Run the Application

```bash
cd ai-influencers
streamlit run app.py
```

Open your browser to `http://localhost:8501`

---

## 📖 How to Use

### 1. Select Platform
Choose your target social media platform (X, LinkedIn, Instagram, Reddit, Medium)

### 2. Enter Topic
Describe what you want to post about (e.g., "AI in healthcare", "Startup funding tips")

### 3. Choose Persona
Select an AI influencer persona with a unique writing style and voice

### 4. Configure Publishing
- **Save Only**: Generate content without publishing
- **Publish Now**: Post immediately after generation
- **Schedule for Later**: Set a future publish time

### 5. Generate Content
Click "Generate Content" to create:
- Platform-optimized text
- Relevant hashtags
- AI-generated image (for visual platforms like Instagram)

### 6. Review & Publish
View validation results and generated content, then publish or save

---
Core Components
The workflow consists of four core agents working in sequence and a professional dashboard for visualization and monitoring:
1.	Content Generator Agent → Creates draft content.

2.	Validation Agent → Ensures factuality, safety, and persona alignment.

3.	Media Builder Agent → Builds supporting media assets (video, audio, captions).

4.	Publishing Agent → Formats, schedules, and publishes content.

5.	Frontend Dashboard → Visualizes agent execution, validation results, publishing logs, and metrics..


## 🏗️ Architecture

### Workflow Pipeline

```
Content Generation → Validation → Media Building → Publishing
         ↓              ↓              ↓              ↓
    LLM creates    Safety checks   Image generation  Multi-platform
    text content   Fact checking   (Cloudflare AI)    API posting
```

### Agents

- **Content Generator**: Platform-specific content with persona styling
- **Validation Agent**: Safety, factuality, and persona consistency checks
- **Media Builder**: AI image generation using Cloudflare Workers
- **Publishing Agent**: Multi-platform API integration
- **Orchestrator**: LangGraph-based workflow coordination

---

## 🎭 Personas

Located in `data/personas/`:
- **Frank (AlgoWizard)**: Tech-savvy with gaming references
- **NeuralNinja**: Technical depth with cybersecurity focus

---

## 📁 Project Structure

```
cq--LLM-Automation/
├── README.md                       # This file
├── data/
│   └── personas/                   # AI influencer persona definitions
│       ├── frank_algoWizard.json
│       └── neuralNinja.json
└── ai-influencers/                 # Main application folder
    ├── app.py                      # Streamlit UI
    ├── requirements.txt            # Python dependencies
    ├── .env.example                # Environment template
    ├── agents/
    │   ├── content_generator_agent/    # Content creation
    │   ├── validation_agent/           # Content validation
    │   ├── media_builder_agent/        # Image generation
    │   ├── publishing_agent/           # Social media posting
    │   └── orchestrator_agent/         # Workflow coordination
    └── generated_images/               # AI-generated visuals
```

---

## 🔧 Platform Configuration

### API Setup

See `.env.example` for required credentials for each platform.

---

## �️ Tech Stack

- **LangGraph**: Workflow orchestration
- **LangChain**: LLM integration
- **Groq**: LLM provider
- **Cloudflare AI Workers**: Image generation
- **Streamlit**: Web interface
- **Python 3.10+**: Core language
