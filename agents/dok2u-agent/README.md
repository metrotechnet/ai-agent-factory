# Dok2u Agent 🧠

A multi-agent AI assistant platform by [Dok2U](https://dok2u.com). Features a **Document Assistant** powered by RAG (Retrieval-Augmented Generation) over your documents, and a **Translation Agent** with speech-to-text via OpenAI Whisper. Built with FastAPI, ChromaDB, and OpenAI GPT-4o-mini.

## ✨ Features

- **🤖 Multi-Agent Architecture**: Switch between agents from a unified interface
  - **Assistant Nutrition**: RAG-based Q&A over indexed documents and transcripts
  - **Traducteur**: Real-time text & audio translation across 27 languages
- **🎬 Automated Content Pipeline**: Process files from Google Drive — download, transcribe (Whisper), extract, chunk, and index
- **🔍 Vector Search**: ChromaDB for semantic retrieval over chunked documents
- **🎙️ Speech-to-Text**: OpenAI Whisper integration for audio transcription and translation
- **🌍 Bilingual UI**: Full French/English interface with i18n via `config.json`
- **⚡ Streaming Responses**: Real-time answers using Server-Sent Events (SSE)
- **📱 Responsive Design**: Mobile-first UI with breakpoints at 768px and 380px
- **🔐 Secure**: Environment-based secrets, no API keys in code
- **🛡️ Refusal Engine**: Configurable pattern-based refusal for out-of-scope questions

## 📁 Project Structure

```
dok2u-agent/
├── app.py                    # FastAPI application (chat + translation endpoints)
├── core/
│   ├── query_chromadb.py     # ChromaDB vector search + LLM streaming
│   ├── translate.py          # Translation module (text + audio via Whisper/GPT)
│   ├── pipeline_gdrive.py    # Pipeline: Google Drive → transcribe → index
│   └── refusal_engine.py     # Pattern-based refusal for off-topic questions
├── scripts/
│   └── index_chromadb.py     # Index transcripts/documents to ChromaDB
├── config/
│   ├── config.json           # UI translations (FR/EN), agent config, prompts
│   ├── prompts.json          # System prompts for the assistant
│   ├── refusal_patterns.json # Patterns to detect off-topic questions
│   └── refusal_responses.json# Canned refusal responses
├── templates/
│   └── index.html            # Main UI template (agent cards, selectors)
├── static/
│   ├── script.js             # Frontend JS (agent switching, translation, SSE)
│   ├── style.css             # Styles (pill selectors, responsive, dark theme)
│   ├── logo-dok2u.png        # Dok2U logo
│   └── favicon.ico           # Favicon
├── transcripts/              # Transcript .txt files
├── videos/                   # Downloaded videos
├── documents/                # Documents to index (JSON)
├── extracted_texts/          # Texts extracted from documents
├── chroma_db/                # Local ChromaDB storage
├── requirements.txt          # Python dependencies
├── Dockerfile                # Container config
├── build.bat                 # Cloud Build script
├── deploy.bat                # Cloud Run deployment
├── start_server.ps1          # Local server startup (PowerShell)
├── startup.sh                # Container startup
└── .env                      # Environment variables (not in git)
```

## ⚙️ Setup

### 1. Clone and Navigate

```bash
cd c:\dev\agent-factory\agents\dok2u-agent
```

### 2. Create Virtual Environment

```powershell
# From the agent-factory root
cd c:\dev\agent-factory
python -m venv .venv
.\.venv\Scripts\Activate.ps1
cd agents\dok2u-agent
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file with:

```env
OPENAI_API_KEY=your-openai-api-key
GCP_PROJECT_ID=your-gcp-project-id        # For Google Drive pipeline
GCS_BUCKET_NAME=your-bucket-name
GCS_REGION=us-east4
CLOUD_RUN_MEMORY=1Gi
CLOUD_RUN_TIMEOUT=300
```

### 4. Add Documents

Place your transcript files (`.txt`) in `transcripts/` and/or document files (`.json`) in `documents/`.

## 🛠️ Usage

### Index Documents to ChromaDB

```powershell
# Activate virtual environment first
& c:\dev\agent-factory\.venv\Scripts\Activate.ps1

# Navigate to the agent directory
cd c:\dev\agent-factory\agents\dok2u-agent

# Index transcripts to local ChromaDB
python scripts/index_chromadb.py
```

This will process transcripts from `transcripts/` and documents from `documents/`, creating a local vector database in `chroma_db/`.

### Google Drive Pipeline

```powershell
# Download, transcribe, and index content from Google Drive
python -c "from core.pipeline_gdrive import run_pipeline; run_pipeline()"
```

Or via API:

```bash
curl -X POST http://localhost:8080/update?limit=10
```

See [GDRIVE_SETUP.md](GDRIVE_SETUP.md) for Google Drive service account configuration.

### Run the Application

```powershell
# Use PowerShell script (automatically activates venv)
.\start_server.ps1

# Or manually with venv activated
python app.py
```

Access the application at **http://localhost:8080**

## 🤖 Agents

### Assistant Nutrition (dok2u)

RAG-based assistant that answers questions using indexed documents and transcripts. Uses ChromaDB for semantic search and GPT-4o-mini for response generation with source citations.

**Endpoints:**
- `POST /ask` — Streaming chat with SSE (supports conversation history)

### Traducteur (translator)

Real-time translation agent supporting 27 languages. Accepts both text and audio input.

**Endpoints:**
- `GET /api/languages` — List supported languages
- `POST /api/translate` — Translate text (streaming SSE)
- `POST /api/translate_audio` — Transcribe & translate audio file (Whisper + GPT-4o-mini)

**Supported Languages:** French, English, Spanish, German, Italian, Portuguese, Chinese, Japanese, Korean, Arabic, Russian, Hindi, Dutch, Polish, Swedish, Turkish, Vietnamese, Thai, Indonesian, Czech, Romanian, Hungarian, Greek, Hebrew, Danish, Finnish, Norwegian.

## 🎯 Key Features

### Multi-Agent UI

- **Agent Selector**: Pill-styled dropdown in the header to switch between agents
- **Agent Cards**: Intro page with clickable cards for each agent
- **Chat Clearing**: Conversation resets when switching agents
- **Welcome Messages**: Each agent displays a localized welcome message on selection
- **Dynamic Placeholders**: Input placeholder and disclaimer update per agent

### Internationalization (i18n)

All UI text is stored in `config/config.json` under `fr` and `en` sections. The language toggle in the header switches between French and English. Agent names, welcome messages, suggestions, and disclaimers are all translatable.

### Vector Search (ChromaDB)

- Semantic search over chunked documents
- OpenAI text-embedding-3-large (3072 dimensions)
- Fast local queries, no cloud costs
- Source citation with document references

### Refusal Engine

Configurable pattern matching to detect and refuse off-topic questions gracefully. Patterns and responses are defined in `config/refusal_patterns.json` and `config/refusal_responses.json`.

## 🔧 Technical Stack

- **Backend**: FastAPI, Python 3.11+
- **AI/ML**: OpenAI GPT-4o-mini (chat + translation), OpenAI Whisper (transcription)
- **Vector DB**: ChromaDB (local)
- **Embeddings**: OpenAI text-embedding-3-large (3072 dimensions)
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **i18n**: JSON-based config with `data-i18n` attributes
- **Cloud**: Google Cloud Run, Google Drive API
- **Configuration**: Environment variables (`.env`) + `config/config.json`

## 🚀 Deployment to Google Cloud Run

### Step 1: Build Docker Image

```bash
.\build.bat
```

This will use Cloud Build to create and push the Docker image.

### Step 2: Deploy to Cloud Run

```bash
.\deploy.bat
```

This will:
- Load configuration from `.env`
- Deploy with all environment variables
- Configure memory, timeout, and scaling
- Output the service URL

**Configuration**:
- Memory: 1Gi (configurable in `.env`)
- Timeout: 300s (5 minutes)
- Min instances: 1
- Max instances: 10
- CPU: 1

## 🔐 Security

- Environment-based secrets management
- No API keys in code or config files
- `.env` file excluded from version control
- Secure Cloud Run deployment with IAM
- Refusal engine for out-of-scope question handling

## 📝 Requirements

- **Python**: 3.11 or higher
- **Memory**: 2GB+ recommended
- **Storage**: 1GB for transcripts and database
- **APIs**: OpenAI API key required
- **GCP**: Google Cloud Project (optional, for Cloud Run deployment and Google Drive pipeline)

## 🐛 Troubleshooting

### ChromaDB Issues

```bash
# Re-index transcripts
python scripts/index_chromadb.py
```

### Server Won't Start

- Ensure `.env` file exists with `OPENAI_API_KEY`
- Verify Python 3.11+ is installed: `python --version`
- Check venv is activated: `.\.venv\Scripts\Activate.ps1`
- Install dependencies: `pip install -r requirements.txt`

### Translation Not Working

- Verify `OPENAI_API_KEY` is set (used for both Whisper and GPT-4o-mini)
- Check audio file format (supports mp3, wav, m4a, webm)

### Deployment Fails

- Check `.env` file exists and has all required variables
- Verify Cloud Build API is enabled
- Ensure billing is enabled on GCP project
- Check IAM permissions for Cloud Build service account

## 💰 Cost Estimation

**Cloud Run** (~$20-50/month):
- CPU: $0.00002400/vCPU-second
- Memory: $0.00000250/GiB-second
- Free tier: 2M requests/month

**OpenAI API** (~$10-30/month):
- text-embedding-3-large: $0.13/1M tokens
- gpt-4o-mini: $0.15/1M input, $0.60/1M output
- Whisper: $0.006/minute of audio
