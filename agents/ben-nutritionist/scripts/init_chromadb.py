"""
Initialize ChromaDB database if it doesn't exist.
This script checks if the transcripts collection exists, and if not, creates it.
"""
import os
from pathlib import Path
import chromadb
from chromadb.config import Settings

def init_chromadb():
    """Initialize ChromaDB database if it doesn't exist"""
    chroma_path = "./chroma_db"
    collection_name = "transcripts"
    
    print(f"Checking ChromaDB initialization at {chroma_path}")
    
    # Create directory if it doesn't exist
    Path(chroma_path).mkdir(parents=True, exist_ok=True)
    
    # Create ChromaDB client
    client = chromadb.PersistentClient(
        path=chroma_path,
        settings=Settings(anonymized_telemetry=False)
    )
    
    # Check if collection exists
    existing_collections = [col.name for col in client.list_collections()]
    print(f"Existing collections: {existing_collections}")
    
    if collection_name not in existing_collections:
        print(f"Collection '{collection_name}' not found. Creating empty collection...")
        client.create_collection(
            name=collection_name,
            metadata={"description": "Nutrition transcripts collection"}
        )
        print(f"Collection '{collection_name}' created successfully (empty)")
    else:
        collection = client.get_collection(collection_name)
        doc_count = collection.count()
        print(f"Collection '{collection_name}' already exists with {doc_count} documents")
    
    print("ChromaDB initialization complete")

if __name__ == "__main__":
    init_chromadb()
