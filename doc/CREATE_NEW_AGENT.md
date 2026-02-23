# Creating a New Agent from Template 🚀

This guide walks you through creating your own custom AI agent using the IMX Agent Factory template.

## 🎯 Quick Overview - 5 Steps

1. **Generate Template** - Create agent structure from config JSON
2. **Build Databases** - Index documents to ChromaDB
3. **Configure Environment** - Set up Firebase and GCP credentials
4. **Test Locally** - Verify everything works
5. **Build and Deploy** - Deploy to production

**Time to create agent:** ~15-20 minutes

---

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Google Cloud Project (for deployment)
- Firebase Project (for frontend hosting)
- Google Cloud SDK installed (`gcloud`)
- Firebase CLI installed (`firebase-tools`)

---

## Step 1: Generate Template 📁

Create your agent configuration and generate the template structure.

### 1.1 Create Configuration File

Create a folder and config file for your agent in `new-agents/`:

```powershell
cd c:\dev\agent-factory
New-Item -ItemType Directory -Path "new-agents\nutria" -Force
Copy-Item "new-agents\agent-config.example.json" "new-agents\nutria\nutria-agent.json"
```

### 1.2 Edit Configuration

Edit `new-agents\nutria\nutria-agent.json` with your agent details. See the example configuration at the end of this guide or reference existing agents like `new-agents/nutria/nutria-agent.json`.

**⚠️ CRITICAL:** The `template` field in the `prompts` section is **REQUIRED**. This defines how the prompt is assembled. Without it, queries will fail with "prompt is null" error.

Example template field:
```json
{
  "prompts": {
    "fr": {
      "template": "{system_role}\n\n{important_notice}\n\n{communication_style_title}\n{communication_style_content}\n{absolute_rules_title}\n{absolute_rules_content}\n{behavioral_constraints_title}\n{behavioral_constraints_content}\n\nCONTEXTE:\n{context}\n\n{history}\n\nQUESTION: {question}"
    }
  }
}
```

**Key Configuration Sections:**
- `agent`: Basic info (id, name, logo)
- `model`: LLM configuration (openai/google, model name)
- `documents`: List of files to process
- `prompts`: System prompts with **template field** (REQUIRED)
- `config`: UI configuration (titles, colors, suggestions)

### 1.3 Add Documents and Logo

Place your documents and logo in the agent folder:

```powershell
# Add your documents
Copy-Item "C:\path\to\doc1.pdf" "new-agents\nutria\"

# Add your logo
Copy-Item "C:\path\to\logo.png" "new-agents\nutria\logo-nutria.png"
```

### 1.4 Generate Template

Run the creation script:

```powershell
python.exe .\scripts\create_agent.py .\new-agents\nutria\nutria-agent.json
```

This creates a new folder `nutria-agent/` with:
- Complete template-agent structure
- Processed documents copied to `knowledge-base/agent/documents/`
- Generated `config.json` and `prompts.json`
- Logo copied to `static/logos/`

**Output:**
```
📁 Creating agent structure: nutria-agent
✅ Agent structure created
✅ Created: prompts.json
✅ Created: config.json
✅ Copied logo to static/logos/
✅ Processed 15 documents
✅ Agent creation complete!
```

---

## Step 2: Build Databases 🔍

Index your documents to ChromaDB vector database.

```powershell
cd nutria-agent
python.exe .\core\index_chromadb_json.py .\knowledge-base\agent\
```

This will:
- Process all documents in `knowledge-base/agent/documents/`
- Create embeddings using OpenAI
- Index to ChromaDB at `knowledge-base/agent/chroma_db/`
- Create metadata in `transcripts_chromadb.json`

**Output:**
```
📊 Indexing documents to ChromaDB...
Processing: Capsule 061025.txt
Processing: Capsule 261025.txt
...
✅ Indexed 427 chunks from 15 documents
✅ ChromaDB collection: gdrive_documents
```

---

## Step 3: Configure Environment ⚙️

Set up Firebase, Google Cloud, and environment variables using `.env.example` as reference.

### 3.1 Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create new project: `nutria-agent-prod`
3. Enable **Firebase Hosting**
4. Note your Project ID

### 3.2 Create Google Cloud Project

```powershell
# Set project ID (use same as Firebase)
gcloud config set project nutria-agent-prod

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com
```

### 3.3 Configure .env File

Copy the example and configure using `.env.example` as a guide:

```powershell
cd nutria-agent
Copy-Item ".env.example" ".env"
```

Edit `.env` and fill in all required values from `.env.example`:

```env
# OpenAI API Key (required)
OPENAI_API_KEY=sk-...

# Google Cloud Configuration
GCP_PROJECT_ID=nutria-agent-prod
GCP_REGION=us-central1

# Firebase Configuration
FIREBASE_PROJECT_ID=nutria-agent-prod

# Application Settings
KNOWLEDGE_BASE=agent
CORS_ORIGINS=*

# Optional: DeepL for translation
DEEPL_API_KEY=...
```

**⚠️ Important:** 
- Use `.env.example` as your reference for all available configuration options
- Never commit `.env` to git!

---

## Step 4: Test Locally 🧪

Test your agent before deployment.

### 4.1 Start Backend

```powershell
.\start-backend.bat
```

Backend runs at: http://localhost:5000

**Test endpoints:**
- http://localhost:5000/api/get_config - Should return your config
- http://localhost:5000/api/query - POST endpoint for questions

### 4.2 Start Frontend

Open a **new terminal**:

```powershell
.\start-frontend.bat
```

Frontend runs at: http://localhost:8080

**Test your agent:**
1. Open http://localhost:8080
2. Verify logo and branding appear correctly
3. Ask questions related to your documents
4. Verify responses are accurate and relevant
5. Check that RAG retrieves correct context

**Common Issues:**
- **"prompt is null" error**: Check that `prompts.json` has the `template` field for both `fr` and `en`
- **No responses**: Verify ChromaDB was indexed (check `knowledge-base/agent/chroma_db/` exists)
- **Config errors**: Verify `config.json` exists in `knowledge-base/agent/`
- **CORS errors**: Check CORS_ORIGINS in `.env`

---

## Step 5: Build and Deploy 🚀

Deploy your agent to production.

### 5.1 Build Backend

Build Docker image and push to Artifact Registry:

```powershell
.\build-backend.bat
```

This will:
- Build Docker image with Cloud Build
- Include your knowledge base (via `.gcloudignore`)
- Push to Google Artifact Registry

**Expected output:**
```
Submitting build to Cloud Build...
Building Docker image...
Pushing image to Artifact Registry...
✅ Build complete!
```

### 5.2 Deploy Backend

Deploy to Cloud Run:

```powershell
.\deploy-backend.bat
```

This will:
- Deploy container to Cloud Run
- Set environment variables from `.env
`
- Configure CORS
- Output backend URL

**Expected output:**
```
Deploying to Cloud Run...
Service URL: https://nutria-agent-4ykvm5teta-uc.a.run.app
✅ Backend deployed!
```

### 5.3 Deploy Frontend

Deploy to Firebase Hosting:

```powershell
.\deploy-frontend.bat
```

This will:
- Configure Firebase project
- Build frontend with backend URL
- Deploy to Firebase Hosting

**Expected output:**
```
Deploying to Firebase Hosting...
✅ Deploy complete!
✅ Hosting URL: https://nutria-agent-prod.web.app
```

---

## ✅ Your Agent is Live!

Visit your production URL: `https://nutria-agent-prod.web.app`

---

## Troubleshooting

### "prompt is null" Error

**Cause:** Missing `template` field in `prompts.json`

**Fix:** Ensure your config JSON has the template field in both language sections:

```json
{
  "prompts": {
    "fr": {
      "system_role": "...",
      "important_notice": "...",
      "communication_style": {...},
      "absolute_rules": {...},
      "behavioral_constraints": {...},
      "template": "{system_role}\n\n{important_notice}\n\n{communication_style_title}\n{communication_style_content}\n{absolute_rules_title}\n{absolute_rules_content}\n{behavioral_constraints_title}\n{behavioral_constraints_content}\n\nCONTEXTE:\n{context}\n\n{history}\n\nQUESTION: {question}"
    },
    "en": {
      "template": "..."
    }
  }
}
```

Then regenerate the agent by running Step 1.4 again.

### ChromaDB Not Found

**Cause:** Forgot to run `index_chromadb_json.py`

**Fix:** Run Step 2 again:
```powershell
python.exe .\core\index_chromadb_json.py .\knowledge-base\agent\
```

### Config Not Found (Deployment)

**Cause:** `.gcloudignore` excluding JSON files

**Fix:** Verify `.gcloudignore` includes:
```
# Include knowledge base files
!knowledge-base/**/*.json
```

### CORS Errors

**Cause:** Frontend domain not in CORS origins

**Fix:** Update `.env`:
```env
CORS_ORIGINS=https://nutria-agent-prod.web.app,https://nutria-agent-prod.firebaseapp.com
```

Redeploy backend:
```powershell
.\deploy-backend.bat
```

### Port Already in Use

**Cause:** Backend or frontend already running

**Fix:**
```powershell
# Find and kill process on port 5000
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess | Stop-Process

# Or on port 8080
Get-Process -Id (Get-NetTCPConnection -LocalPort 8080).OwningProcess | Stop-Process
```

---

## Agent Configuration Reference

### Minimal Config Example

```json
{
  "agent": {
    "id": "my-agent",
    "name": {"fr": "Mon Agent", "en": "My Agent"},
    "description": {"fr": "Description", "en": "Description"},
    "logo": "logo-my-agent.png",
    "accessKey": "secure-random-key",
    "icon": "🤖",
    "color": "#4caf50"
  },
  "model": {
    "supplier": "openai",
    "name": "gpt-4o-mini"
  },
  "documents": {
    "files": [
      "new-agents/my-agent/document1.pdf"
    ]
  },
  "prompts": {
    "fr": {
      "system_role": "Tu es un assistant virtuel...",
      "important_notice": "Important...",
      "communication_style": {
        "title": "TON STYLE",
        "tone_and_voice": {
          "title": "Ton",
          "characteristics": ["Conversationnel"]
        },
        "recurring_messages": {
          "title": "Messages",
          "messages": ["Message 1"]
        }
      },
      "absolute_rules": {
        "title": "RÈGLES",
        "rules": ["Règle 1"]
      },
      "behavioral_constraints": {
        "title": "CONSIGNES",
        "constraints": ["Consigne 1"]
      },
      "template": "{system_role}\n\n{important_notice}\n\n{communication_style_title}\n{communication_style_content}\n{absolute_rules_title}\n{absolute_rules_content}\n{behavioral_constraints_title}\n{behavioral_constraints_content}\n\nCONTEXTE:\n{context}\n\n{history}\n\nQUESTION: {question}"
    },
    "en": {
      "system_role": "You are a virtual assistant...",
      "important_notice": "Important...",
      "communication_style": {
        "title": "YOUR STYLE",
        "tone_and_voice": {
          "title": "Tone",
          "characteristics": ["Conversational"]
        },
        "recurring_messages": {
          "title": "Messages",
          "messages": ["Message 1"]
        }
      },
      "absolute_rules": {
        "title": "RULES",
        "rules": ["Rule 1"]
      },
      "behavioral_constraints": {
        "title": "GUIDELINES",
        "constraints": ["Guideline 1"]
      },
      "template": "{system_role}\n\n{important_notice}\n\n{communication_style_title}\n{communication_style_content}\n{absolute_rules_title}\n{absolute_rules_content}\n{behavioral_constraints_title}\n{behavioral_constraints_content}\n\nCONTEXT:\n{context}\n\n{history}\n\nQUESTION: {question}"
    }
  },
  "config": {
    "fr": {
      "app": {
        "title": "Mon Agent",
        "description": "Description"
      },
      "intro": {
        "title": "Bienvenue",
        "description": "Posez vos questions",
        "profileImage": "/static/logos/logo-my-agent.png",
        "profileAlt": "Mon Agent"
      },
      "suggestions": [
        {
          "id": "topic1",
          "title": "💡 Sujet",
          "description": "Description",
          "event": "display: Description",
          "color": "#fff9c4"
        }
      ],
      "components": {
        "inputArea": {
          "showInputOnLoad": true,
          "placeholder": "Pose-moi une question...",
          "sendButton": "Envoyer",
          "voiceButton": "Enregistrer",
          "disclaimer": "⚠️ Peut contenir des erreurs."
        }
      }
    },
    "en": {
      "app": {"title": "My Agent", "description": "Description"},
      "intro": {"title": "Welcome", "description": "Ask questions"}
    }
  }
}
```

### Template Placeholder Variables

- `{system_role}` - Agent role definition
- `{important_notice}` - Important notice/disclaimer
- `{communication_style_title}` - Communication style section title
- `{communication_style_content}` - Communication style details (tone + recurring messages)
- `{absolute_rules_title}` - Absolute rules section title
- `{absolute_rules_content}` - List of absolute rules
- `{behavioral_constraints_title}` - Behavioral constraints section title
- `{behavioral_constraints_content}` - List of behavioral constraints
- `{context}` - RAG context from ChromaDB
- `{history}` - Conversation history
- `{question}` - User's current question

---

## Next Steps

- 📚 Read [AGENT_CREATION.md](AGENT_CREATION.md) for advanced configuration
- 🚀 Set up [Google Drive sync](SHARED_GDRIVE_SETUP.md) for automated knowledge base updates
- 📊 Configure monitoring and alerting in GCP Console
- 🔧 Review [template-agent/README.md](../template-agent/README.md) for deployment details

---

## Support

For issues:
- Check troubleshooting section above
- Review Cloud Run logs: `gcloud run logs read --service=imx-multi-agent`
- Check browser console for frontend errors
- Verify all required fields in config JSON (especially `template` in prompts)
- Ensure `.env` is properly configured using `.env.example` as reference
