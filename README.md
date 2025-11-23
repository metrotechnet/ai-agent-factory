# Personal AI Agent

A personal AI agent that transcribes videos, indexes transcripts, and allows querying using RAG (Retrieval Augmented Generation).

## Features

- Video transcription using OpenAI Whisper
- Transcript indexing with ChromaDB vector database (local storage)
- Question answering using OpenAI GPT models
- FastAPI REST API for easy integration

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your-key-here
```

4. Add your Word documents (.docx) to the `transcripts/AI - Ben Nutritionniste/` folder

## Usage

### Extract Text from Documents
```bash
python extract_docx.py
```

### Index Documents
```bash
python index_chromadb.py
```

### Query the Agent (Command Line)
```bash
python query_chromadb.py
```

### Run Web Interface
```powershell
.\start_server.ps1
```
Or on Windows CMD:
```cmd
start_server.bat
```

Then access the web interface at http://localhost:8000

## Features

- 💬 ChatGPT-like interface for asking questions
- 🗂️ Automatic document extraction from Word files
- 🔍 Semantic search using ChromaDB (local vector database)
- 🤖 GPT-4 powered answers based on your documents
- 📊 842 chunks indexed from 15 documents

## Requirements

- Python 3.12+
- OpenAI API key
