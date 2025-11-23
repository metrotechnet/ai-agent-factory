# Personal AI Agent

A personal AI agent that transcribes videos, indexes transcripts, and allows querying using RAG (Retrieval Augmented Generation).

## Features

- Video transcription using OpenAI Whisper
- Transcript indexing with Pinecone vector database
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

3. Create a `config.py` file with your API keys and settings (see config.py for template)

4. Add videos to the `videos/` folder

## Usage

### Transcribe Videos
```bash
python ingest.py
```

### Index Transcripts
```bash
python index.py
```

### Query the Agent
```bash
python query.py
```

### Run API Server
```bash
uvicorn app:app --reload
```

Then access the API at http://localhost:8000

## API Endpoints

- `GET /` - Health check
- `POST /query?question=your_question` - Query the AI agent

## Requirements

- Python 3.12+
- OpenAI API key
- Pinecone API key
