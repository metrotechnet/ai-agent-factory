import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key-here")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "your-pinecone-api-key-here")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-west1-gcp")
INDEX_NAME = "my-agent-index"
VIDEO_FOLDER = "./videos"
TRANSCRIPT_FOLDER = "./transcripts"
