# Agent Factory

A production-ready template for creating and deploying AI agents with RAG (Retrieval-Augmented Generation) capabilities. Built with FastAPI backend, vanilla JavaScript frontend, and ChromaDB for vector search.

## 🚀 Quick Start

Create a new agent in minutes using the automated setup:

```bash
# 1. Create agent configuration in new-agents/ folder
# 2. Run the creation script
python scripts/create_agent.py new-agents/my-agent/config.json

# 3. Deploy to Google Cloud
cd template-agent
.\deploy-backend.bat
.\deploy-frontend.bat
```

## 📚 Documentation

- **[CREATE_NEW_AGENT.md](doc/CREATE_NEW_AGENT.md)** - Step-by-step guide for creating new agents
- **[AGENT_CREATION.md](doc/AGENT_CREATION.md)** - Complete reference for agent configuration
- **[SHARED_GDRIVE_SETUP.md](doc/SHARED_GDRIVE_SETUP.md)** - Google Drive integration for dynamic knowledge base updates
- **[template-agent/README.md](template-agent/README.md)** - Template deployment and configuration guide

## 🎯 Features

- **Automated Agent Creation** - Script handles document processing, transcription, and vector indexing
- **RAG-Powered Chat** - Context-aware responses using ChromaDB vector search
- **Multi-Format Support** - PDF, DOCX, TXT documents + audio transcription
- **Refusal Engine** - Configurable boundaries for agent responses
- **Translation** - Multi-language support with DeepL integration
- **Text-to-Speech** - Natural voice output via OpenAI
- **Session Management** - Conversation history and context persistence
- **Google Drive Sync** - Automatic knowledge base updates from shared drives
- **Production Ready** - Docker containerization, Cloud Run deployment

## 🏗️ Project Structure

```
agent-factory/
├── scripts/              # Automation tools
│   └── create_agent.py   # Agent creation script
├── new-agents/           # Agent configurations
│   └── example.json      # Configuration template
├── template-agent/       # Deployable template
│   ├── api/              # FastAPI backend
│   ├── core/             # Core logic (RAG, translation, refusal)
│   ├── static/           # Frontend JavaScript
│   ├── knowledge-base/   # Agent-specific data
│   └── README.md         # Deployment guide
└── doc/                  # Documentation
    ├── CREATE_NEW_AGENT.md
    ├── AGENT_CREATION.md
    └── SHARED_GDRIVE_SETUP.md
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- ChromaDB (vector database)
- OpenAI API (embeddings, completions, TTS)
- DeepL API (translation)

**Frontend:**
- Vanilla JavaScript (modular architecture)
- No build tools required
- Responsive design

**Infrastructure:**
- Docker containerization
- Google Cloud Run (backend)
- Firebase Hosting (frontend)
- Google Drive (knowledge base sync)

## 📋 Prerequisites

- Python 3.11+
- OpenAI API key
- DeepL API key (optional, for translation)
- Google Cloud account (for deployment)
- Firebase account (for frontend hosting)

## 🎓 Getting Started

### 1. Create Your First Agent

Follow the [CREATE_NEW_AGENT.md](doc/CREATE_NEW_AGENT.md) guide:

1. Prepare your knowledge base (documents, transcripts)
2. Create agent configuration JSON
3. Run `scripts/create_agent.py` to process and index content
4. Deploy to Google Cloud

### 2. Local Development

```bash
cd template-agent

# Set environment variables
cp .env.example .env
# Edit .env with your API keys

# Install dependencies
pip install -r requirements.txt

# Start backend
python app.py

# Start frontend (separate terminal)
python serve_frontend.py
```

### 3. Production Deployment

```bash
cd template-agent

# Deploy backend to Cloud Run
.\deploy-backend.bat

# Deploy frontend to Firebase
.\deploy-frontend.bat
```

## 🔑 Environment Configuration

Key environment variables (see [template-agent/README.md](template-agent/README.md) for complete list):

```bash
OPENAI_API_KEY=sk-...           # Required for embeddings and completions
DEEPL_API_KEY=...               # Required for translation
KNOWLEDGE_BASE=agent            # Which knowledge base to use
CORS_ORIGINS=*                  # Frontend URLs for CORS
```

## 🧪 Example Agents

Sample configurations in `new-agents/`:

- **Bibliosense** - Book recommendation agent
- **Nutria** - Nutrition advisor

Create your own by copying `agent-config.example.json` and customizing.

## 📖 Key Concepts

### Knowledge Base Structure

Each agent has:
- **config.json** - Agent name, description, personality
- **prompts.json** - System prompts and instructions
- **transcripts_chromadb.json** - Vector database metadata
- **chroma_db/** - ChromaDB vector store
- **documents/** - Source documents (PDF, DOCX, TXT)
- **transcripts/** - Processed text files

### Automated Workflow

`scripts/create_agent.py` handles:
1. Document text extraction
2. Audio transcription (if audio files present)
3. Text chunking and embedding
4. ChromaDB indexing
5. Configuration file generation

### Refusal Engine

Configurable boundaries in `knowledge-base/common/refusal_patterns.json`:
- Pattern matching for off-topic queries
- Graceful response when outside expertise
- Customizable refusal messages

## 🤝 Contributing

This is a template project. Fork it and customize for your needs!

## 📄 License

[Add your license here]

## 🆘 Support

- Review [documentation](doc/) for detailed guides
- Check [template-agent/README.md](template-agent/README.md) for deployment troubleshooting
- Examine existing agent configurations in `new-agents/`

---

**Ready to build your AI agent?** Start with [CREATE_NEW_AGENT.md](doc/CREATE_NEW_AGENT.md)
