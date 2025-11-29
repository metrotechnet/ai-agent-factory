# Ben Boulanger AI Agent 🧠

An intelligent personal AI assistant that processes transcripts and documents, providing expert nutritional and wellness guidance through advanced RAG (Retrieval Augmented Generation) technology.

## 🚀 Features

- 📄 **Document Processing**: Extract and index content from Word documents and transcripts
- 🔍 **Semantic Search**: ChromaDB vector database for intelligent document retrieval
- 🤖 **AI-Powered Responses**: GPT-4 integration with Ben Boulanger's expertise
- 🌐 **Multilingual Support**: French and English interface and responses
- ⚡ **Real-time Streaming**: FastAPI with Server-Sent Events for responsive chat
- 🎨 **Modern UI**: Clean, intuitive web interface
- 🔒 **Secure Configuration**: External JSON configs with protected access

## 📁 Project Structure

```
benboulanger.ai/
├── core/                    # Core business logic
│   └── query_chromadb.py   # Main AI processing engine
├── tests/                  # Unit tests and validation
├── scripts/               # Utility scripts
│   ├── extract_docx.py    # Document extraction
│   ├── index_chromadb.py  # Database indexing
│   └── init_chromadb.py   # Database initialization
├── config/                # Secure configuration files
│   ├── style_guides.json  # AI personality and style rules
│   └── system_prompts.json # Multilingual system prompts
├── static/                # Frontend assets
├── templates/             # HTML templates
├── documents/             # Source documents
├── chroma_db/            # Vector database storage
└── app.py                # FastAPI application entry point
```

## ⚙️ Setup

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate environment
.\venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source venv/bin/activate     # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file with your OpenAI API key:
```env
OPENAI_API_KEY=your-openai-api-key-here
```

### 4. Document Setup
Add your documents (.docx, .txt) to the `documents/` folder structure

## 🛠️ Usage

### Initialize and Index Documents
```bash
# Extract text from Word documents
python scripts/extract_docx.py

# Initialize ChromaDB database
python scripts/init_chromadb.py

# Index documents for search
python scripts/index_chromadb.py
```

### Run the Application
```bash
# Start the web server
python app.py

# Or use PowerShell script
.\start_server.ps1
```

Access the application at **http://localhost:8001**

### Command Line Interface
```bash
# Direct querying (for testing)
python core/query_chromadb.py
```

## 🎯 Key Features

- **🧠 Expert AI Persona**: Configured with Ben Boulanger's nutritional expertise
- **🌍 Multilingual**: Seamless French/English support
- **📊 Smart Indexing**: 842+ document chunks intelligently indexed
- **⚡ Fast Responses**: Optimized retrieval and generation pipeline
- **🔐 Production Ready**: Secure configuration management
- **📱 Responsive Design**: Works on desktop and mobile devices

## 🔧 Technical Stack

- **Backend**: FastAPI, Python 3.12+
- **AI/ML**: OpenAI GPT-4, ChromaDB vector database
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Storage**: Local ChromaDB with SQLite backend
- **Configuration**: JSON-based external configs
- **Security**: Protected configuration files outside web root

## 📊 Performance

- **Document Coverage**: 15+ expert documents indexed
- **Response Time**: < 2 seconds average
- **Accuracy**: High relevance through semantic search
- **Scalability**: Optimized for production deployment

## 🚀 Deployment

The application is containerized and ready for deployment:

```bash
# Build Docker image
docker build -t benboulanger-ai .

# Run container
docker run -p 8001:8001 benboulanger-ai
```

## 🔐 Security

- Configuration files secured in `/config` directory
- No sensitive data exposed through static file serving
- Environment-based API key management
- CORS and security headers configured

## 📝 Requirements

- **Python**: 3.12 or higher
- **Memory**: 2GB+ recommended
- **Storage**: 1GB for documents and database
- **API**: OpenAI API key required
