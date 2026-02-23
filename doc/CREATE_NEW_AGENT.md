# Creating a New Agent from Template 🚀

This guide walks you through creating your own custom AI agent using the IMX Agent Factory template.

## 🎯 Quick Overview

The agent creation process is **mostly automated** using the `scripts/create_agent.py` script:

1. ✅ **You provide**: Configuration JSON with agent settings, documents, and UI preferences
2. ✅ **Script handles**: Copying template, processing documents, transcribing audio, indexing to ChromaDB, creating configs
3. ✅ **You configure**: Environment variables (.env) and deploy

**Time to create agent:** ~10-15 minutes (mostly document processing time)

## What `create_agent.py` Does Automatically:

- 📁 Copies template-agent structure to new agent folder
- 📄 Processes your documents (PDF, DOCX, TXT, JSON)
- 📝 Creates transcript files from all documents
- 🎤 Transcribes audio files using Whisper
- 🔍 Indexes everything to ChromaDB vector database
- 🖼️ Copies logo to static/logos/
- ⚙️ Generates config.json and prompts.json
- ✨ Sets up proper folder structure

**Result:** A production-ready agent with RAG capabilities in minutes!

---

## Prerequisites

- Python 3.11 or higher
- Git (for version control)
- OpenAI API key
- Google Cloud Project (optional, for deployment)
- Firebase Project (optional, for frontend hosting)

## Step 1: Create Agent Configuration

Create a configuration file for your new agent in the `new-agents/` folder:

```bash
# Navigate to agent-factory root
cd c:\dev\agent-factory

# Create your agent folder under new-agents
mkdir new-agents\my-nutrition-agent

# Copy the example configuration
cp new-agents\agent-config.example.json new-agents\my-nutrition-agent\nutrition-agent.json
```

**Windows PowerShell:**
```powershell
cd c:\dev\agent-factory
New-Item -ItemType Directory -Path "new-agents\my-nutrition-agent" -Force
Copy-Item "new-agents\agent-config.example.json" "new-agents\my-nutrition-agent\nutrition-agent.json"
```

Edit `new-agents/my-nutrition-agent/nutrition-agent.json` with your agent details:

```json
{
  "agent": {
    "id": "nutrition",
    "name": {
      "fr": "NutriAgent | Expert Nutrition",
      "en": "NutriAgent | Nutrition Expert"
    },
    "description": {
      "fr": "Agent IA spécialisé en nutrition et santé",
      "en": "AI agent specialized in nutrition and health"
    },
    "logo": "/static/logos/logo-nutrition.png",
    "accessKey": "your-secure-key",
    "icon": "🥗",
    "color": "#4caf50"
  },
  "model": {
    "supplier": "openai",
    "name": "gpt-4o-mini"
  },
  "documents": {
    "files": [
      "C:\\path\\to\\nutrition-basics.pdf",
      "C:\\path\\to\\supplements-guide.docx",
      "C:\\path\\to\\training-protocols.txt"
    ],
    "audio_files": [
      {
        "path": "C:\\path\\to\\nutrition-podcast.mp3",
        "language": "fr",
        "output_name": "Nutrition Podcast.txt"
      }
    ]
  },
  "prompts": {
    "fr": {
      "system_role": "Tu es un assistant virtuel spécialisé en nutrition et santé.",
      "important_notice": "Tu fournis uniquement des informations générales basées sur la science. Tu recommandes toujours de consulter un professionnel de santé qualifié pour des conseils personnalisés.",
      "communication_style": {
        "title": "TON STYLE DE COMMUNICATION EN FRANÇAIS",
        "tone_and_voice": {
          "characteristics": [
            "Ton conversationnel et accessible",
            "Langage clair et basé sur la science",
            "Empathique et encourageant"
          ]
        }
      }
    },
    "en": {
      "system_role": "You are a virtual assistant specialized in nutrition and health.",
      "important_notice": "You provide general science-based information only. Always recommend consulting a qualified health professional for personalized advice."
    }
  },
  "config": {
    "fr": {
      "app": {
        "title": "NutriAgent | Expert Nutrition",
        "description": "Assistant IA nutrition"
      },
      "intro": {
        "title": "Des questions sur la nutrition ?",
        "description": "Posez vos questions et obtenez des réponses basées sur la science.",
        "profileImage": "/static/logos/logo-nutrition.png",
        "profileAlt": "NutriAgent"
      },
      "suggestions": [
        {
          "id": "supplements",
          "title": "💊 Suppléments",
          "description": "Questions sur les suppléments",
          "color": "#b2dfdb"
        },
        {
          "id": "nutrition",
          "title": "🥗 Nutrition",
          "description": "Alimentation saine",
          "color": "#fff9c4"
        }
      ]
    },
    "en": {
      "app": {
        "title": "NutriAgent | Nutrition Expert",
        "description": "AI nutrition assistant"
      },
      "intro": {
        "title": "Questions about nutrition?",
        "description": "Ask your questions and get science-based answers.",
        "profileImage": "/static/logos/logo-nutrition.png"
      }
    }
  }
}
```

**Important Configuration Fields:**
- `agent.id`: Short identifier (alphanumeric, hyphens, underscores) - will be used as folder name
- `documents.files`: Absolute paths to your PDF, DOCX, TXT, or JSON files
- `documents.audio_files`: Audio files to transcribe with Whisper (MP3, M4A, WAV, WEBM)
- `prompts`: System prompts in French and English
- `config`: UI configuration (titles, suggestions, colors)

**📖 See [new-agents/agent-config.example.json](new-agents/agent-config.example.json) for complete configuration reference with all available options.**

### Add Your Logo

Place your logo in the same folder as your config:

```bash
# Copy logo to agent folder
cp my-logo.png new-agents/my-nutrition-agent/logo-nutrition.png
```

The script will automatically copy it to `static/logos/` during agent creation.

### Run Agent Creation Script

```bash
# From agent-factory root
python scripts/create_agent.py new-agents/my-nutrition-agent/nutrition-agent.json
```

This automated script will:
- ✅ Copy template-agent structure to create `nutrition-agent/` folder
- ✅ Create knowledge base directories
- ✅ Copy and process your documents
  - Extract text from PDFs (PyPDF2)
  - Extract text from DOCX files
  - Process JSON data files
  - Create transcript files automatically
- ✅ Transcribe audio files using OpenAI Whisper
- ✅ Index all content to ChromaDB vector database
- ✅ Copy logo to `static/logos/`
- ✅ Generate `config.json` and `prompts.json`
- ✅ Set up proper folder structure

**Output:**
```
📁 Creating agent structure: nutrition-agent
✅ Agent structure created
✅ Created: prompts.json
✅ Created: config.json
✅ Copied logo: logo-nutrition.png -> static/logos/
📄 Processing documents...
✅ Processed: nutrition-basics.pdf -> transcripts/
🎤 Transcribing audio files...
✅ Transcribed: nutrition-podcast.mp3
📊 Indexing to ChromaDB...
✅ Indexed 45 chunks
✅ Agent creation complete!
```

Now navigate to your new agent:

```bash
cd nutrition-agent
```

## Step 2: Verify Agent Structure

The `create_agent.py` script has already created your agent structure. Verify it was created correctly:

```bash
cd nutrition-agent

# Check folder structure
ls -la
```

You should see:
```
nutrition-agent/
├── knowledge-base/
│   └── agent/
│       ├── config.json         # ✅ Created from your config
│       ├── prompts.json        # ✅ Created from your config  
│       ├── transcripts/        # ✅ Auto-generated from documents
│       ├── documents/          # ✅ Your source documents copied here
│       ├── extracted_texts/    # ✅ Processed text files
│       └── chroma_db/          # ✅ Vector database indexed
├── static/
│   └── logos/
│       └── logo-nutrition.png  # ✅ Your logo copied here
├── templates/
├── api/
├── core/
├── .env                        # ⚠️ Needs configuration (next step)
└── app.py
```

**Note:** The agent creation script already handled:
- ✅ Document processing and transcript creation
- ✅ Audio transcription with Whisper
- ✅ ChromaDB indexing
- ✅ Logo copying
- ✅ Config files generation

## Step 3: Configure Environment Variables

Create your `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# ====================================
# API Keys (REQUIRED)
# ====================================
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here

# ====================================
# Knowledge Base Configuration
# ====================================
# Which knowledge base folder to use (defaults to 'agent')
KNOWLEDGE_BASE=agent

# ====================================
# Google Cloud Platform (for deployment)
# ====================================
GCP_PROJECT_ID=my-nutrition-agent-123456
GCP_REGION=us-east4
GCP_SERVICE_NAME=my-nutrition-agent
GCP_IMAGE_NAME=gcr.io/my-nutrition-agent-123456/my-nutrition-agent

# Cloud Run Configuration
CLOUD_RUN_MEMORY=1Gi
CLOUD_RUN_TIMEOUT=300

# ====================================
# Frontend Configuration (for deployment)
# ====================================
FIREBASE_PROJECT_ID=my-nutrition-agent
BACKEND_URL=http://localhost:8080

# ====================================
# Optional: Google Drive Integration
# ====================================
GDRIVE_FOLDER_ID=your-google-drive-folder-id

# ====================================
# Optional: Additional CORS Origins
# ====================================
ADDITIONAL_CORS_ORIGINS=https://custom-domain.com
```

**Important**: Never commit `.env` to version control!

## Step 4: Set Up Python Environment

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Test Locally

The agent creation script has already indexed your documents and configured everything. You can now test immediately!

### Option 1: Start Both Servers
      {
        "id": "supplements",
        "title": "💊 Supplements",
        "description": "Questions about supplements",
        "event": "display: Questions about supplements",
        "color": "#b2dfdb"
      },
      {
        "id": "nutrition",
        "title": "🥗 Nutrition",
        "description": "Healthy eating and diet",
        "event": "display: Healthy eating and diet",
        "color": "#fff9c4"
      },
      {
        "id": "training",
        "title": "🏋️ Training",
        "description": "Athletic performance",
        "event": "display: Athletic performance",
        "color": "#ffe0b2"
      }
    ],
    "components": {
      "inputArea": {
        "showInputOnLoad": true,
        "placeholder": "Ask me a question about nutrition...",
        "sendButton": "Send",
        "voiceButton": "Record voice message",
        "disclaimer": "⚠️ May contain errors. Does not replace professional advice."
      }
    }
  },
  "en": {
    // English translations...
  }
}
```

### Test Your Agent

1. Open http://localhost:3000
2. Verify your branding and logo appear
3. Try the suggestion cards
4. Ask questions to test RAG responses
5. Check that sources are cited correctly
6. Test voice input (if configured)

## Step 6: Optional Customizations

If you need to make changes after agent creation:

### Add More Documents

```bash
# Add new files to knowledge-base/agent/extracted_texts/
# Then reindex
python scripts/index_chromadb.py agent extracted_texts
```

### Update UI Configuration

Edit `knowledge-base/agent/config.json` to change:
- App title and descriptions
- Suggestion cards
- Colors and icons
- Input placeholders

Restart frontend: `.\start_frontend.ps1`

### Change AI Model

Edit `knowledge-base/agent/prompts.json`:
```json
{
  "model_supplier": "google",
  "model_name": "gemini-2.0-flash-exp"
}
```

Restart backend: `.\start_backend.ps1`

### Update Logo

Replace `static/logos/logo-nutrition.png` with your new logo and restart frontend.

## Step 7: Configure Google Cloud (For Deployment)

### Set Up GCP Project

```bash
# Install Google Cloud SDK if not already installed
# https://cloud.google.com/sdk/docs/install

# Login to Google Cloud
gcloud auth login

# Create new project (or use existing)
gcloud projects create my-nutrition-agent-123456

# Set active project
gcloud config set project my-nutrition-agent-123456

# Enable required APIs
gcloud services enable \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com

# Enable billing (required for Cloud Run)
# Visit: https://console.cloud.google.com/billing
```

### Create Secrets (Optional - for Google Drive)

```bash
# Create secret for Google Drive credentials
gcloud secrets create gdrive-credentials \
  --data-file=path/to/credentials.json \
  --replication-policy=automatic
```

## Step 8: Configure Firebase (For Frontend)

```bash
# Install Firebase CLI if not already installed
npm install -g firebase-tools

# Login to Firebase
firebase login

# Create new Firebase project
# Visit: https://console.firebase.google.com/

# Initialize Firebase (if not already done)
firebase init hosting

# Select your project
firebase use my-nutrition-agent

# Update .firebaserc with your project ID
```

Edit `.firebaserc`:
```json
{
  "projects": {
    "default": "my-nutrition-agent"
  }
}
```

## Step 9: Deploy to Production

### Build Backend Image

```bash
# Build Docker image with Cloud Build
.\build-backend.bat
```

This will:
- Upload code to Cloud Build (respecting `.gcloudignore`)
- Build Docker image with your knowledge base
- Push to Google Container Registry

### Deploy Backend

```bash
# Deploy to Cloud Run
.\deploy-backend.bat
```

This will:
- Deploy container to Cloud Run
- Set environment variables from `.env`
- Configure CORS for your Firebase domain
- Output the backend URL
- Save URL to `.env` and `.backend-url.tmp`

### Deploy Frontend

```bash
# Deploy to Firebase Hosting
.\deploy-frontend.bat
```

This will:
- Set Firebase project
- Copy files to `public/` folder
- Update paths for Firebase hosting
- Create `backend-url.js` with your Cloud Run URL
- Deploy to Firebase Hosting

### Verify Deployment

1. Visit your Firebase URL: `https://my-nutrition-agent.web.app`
2. Test the agent with real questions
3. Verify CORS is working (no console errors)
4. Check Cloud Run logs: `gcloud run logs read imx-multi-agent --region us-east4`
5. Monitor costs in GCP Console

## Step 10: Managing Your Agent

### Adding More Documents

If you need to add new documents after initial creation:

**Option 1: Re-run create_agent.py (Recommended)**

Update your config JSON in `new-agents/` with new document paths and re-run:

```bash
# Update new-agents/my-nutrition-agent/nutrition-agent.json
# Add new files to "documents.files" array

# Re-run creation script (this will ask to overwrite)
cd c:\dev\agent-factory
python scripts/create_agent.py new-agents/my-nutrition-agent/nutrition-agent.json
```

**Option 2: Manual Addition**

```bash
# 1. Add new documents to knowledge-base/agent/extracted_texts/
cp new-document.txt knowledge-base/agent/extracted_texts/

# 2. Reindex locally
python scripts/index_chromadb.py agent extracted_texts

# 3. Rebuild Docker image
.\build-backend.bat

# 4. Redeploy to Cloud Run
.\deploy-backend.bat
```

**Note**: The `chroma_db/` folder is included in the Docker image. Changes to the knowledge base require rebuilding and redeploying.

## Common Customizations

### Change Knowledge Base

Update `.env`:
```env
KNOWLEDGE_BASE=nutrition
```

Then rebuild and redeploy:
```bash
.\build-backend.bat
.\deploy-backend.bat
```

### Switch AI Model

Edit `knowledge-base/agent/prompts.json`:
```json
{
  "model_supplier": "google",
  "model_name": "gemini-2.0-flash-exp"
}
```

Restart the backend (no rebuild needed).

### Update UI Text

Edit `knowledge-base/agent/config.json` and `knowledge-base/common/config.json`.

Restart frontend:
```powershell
.\start_frontend.ps1
```

For deployment, run:
```bash
.\deploy-frontend.bat
```

### Add Refusal Patterns

Edit `knowledge-base/common/refusal_patterns.json`:
```json
{
  "patterns": [
    "medical diagnosis",
    "prescribe medication",
    "legal advice"
  ]
}
```

Edit `knowledge-base/common/refusal_responses.json` for custom refusal messages.

See `knowledge-base/common/README_REFUSAL.md` for details.

## Troubleshooting

### Build Fails

```bash
# Check .gcloudignore includes JSON files
# knowledge-base/**/*.json should NOT be excluded

# Verify .env has all required variables
cat .env | grep -E "OPENAI_API_KEY|GCP_PROJECT_ID|FIREBASE_PROJECT_ID"

# Check Cloud Build logs
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

### Deployment Fails

```bash
# Verify APIs are enabled
gcloud services list --enabled

# Check IAM permissions
gcloud projects get-iam-policy my-nutrition-agent-123456

# View Cloud Run logs
gcloud run logs read imx-multi-agent --region us-east4 --limit=50
```

### Config Not Found Error

```bash
# Check KNOWLEDGE_BASE in .env matches your folder
# Verify knowledge-base/agent/config.json exists
ls -la knowledge-base/agent/

# Check Docker image includes files
docker run --rm <IMAGE> ls -la /app/knowledge-base/agent/
```

### CORS Errors

Update `app.py` to include your domain:
```python
# CORS middleware already configured to use FIREBASE_PROJECT_ID
# from environment variable
```

Redeploy:
```bash
.\deploy-backend.bat
```

## Next Steps

- 📚 Read [AGENT_CREATION.md](AGENT_CREATION.md) for advanced configuration
- 🗄️ See [knowledge-base/README.md](../template-agent/knowledge-base/README.md) for KB management
- 🔧 Review [api/README.md](../template-agent/api/README.md) for API architecture
- 🚀 Set up [Google Drive sync](SHARED_GDRIVE_SETUP.md) for automated updates
- 📊 Configure monitoring and alerting in GCP Console

## Support

For issues or questions:
- Check [README.md](README.md) for general documentation
- Review troubleshooting section above
- Check Cloud Run logs for backend issues
- Inspect browser console for frontend errors

## License

Check the root LICENSE file for licensing information.
