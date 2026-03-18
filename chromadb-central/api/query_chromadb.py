"""
Minimal ChromaDB access layer for central API.
"""
import os
from chromadb.config import Settings
import chromadb

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Global cache for preloaded collections
_PRELOADED_COLLECTIONS = {}

# Helper to get collection for a project
def get_collection(project_name):
    # Return preloaded collection if available
    if project_name in _PRELOADED_COLLECTIONS:
        return _PRELOADED_COLLECTIONS[project_name]
    kb_path = os.path.join(PROJECT_ROOT, "knowledge-base", project_name, "chroma_db")
    client = chromadb.PersistentClient(path=kb_path, settings=Settings(anonymized_telemetry=False, allow_reset=False))
    try:
        collection = client.get_collection(name="gdrive_documents")
    except Exception:
        collection = client.create_collection(name="gdrive_documents")
    return collection

# Preload all collections (to be called at startup)
def preload_all_collections():
    for project_name in ["bibliosense", "nutria", "translator"]:
        try:
            kb_path = os.path.join(PROJECT_ROOT, "knowledge-base", project_name, "chroma_db")
            client = chromadb.PersistentClient(path=kb_path, settings=Settings(anonymized_telemetry=False, allow_reset=False))
            try:
                collection = client.get_collection(name="gdrive_documents")
            except Exception:
                collection = client.create_collection(name="gdrive_documents")
            _PRELOADED_COLLECTIONS[project_name] = collection
        except Exception as e:
            print(f"[Preload] Failed to preload collection for {project_name}: {e}")


# Example query function (to be adapted for your schema)
def query_vector_db(project_name, query):
    collection = get_collection(project_name)
    if collection is None:
        return {"error": "ChromaDB collection is not available. Please run 'python index_chromadb.py' first to index your documents."}
    
    # If query is a dict, treat as advanced vector search
    if isinstance(query, dict):
        # Expecting keys: query_embedding, n_results, include, (optional) where
        try:
            query_embedding = query["query_embedding"]
            n_results = query.get("n_results", 10)
            include = query.get("include", ["documents"])
            where = query.get("where")
            query_args = {
                "query_embeddings": [query_embedding],
                "n_results": n_results,
                "include": include
            }
            if where:
                query_args["where"] = where
            results = collection.query(**query_args)
            return results
        except Exception as e:
            return {"error": f"Invalid vector search payload or ChromaDB error: {str(e)}"}
    # Else, treat as simple question string
    return {"project": project_name, "question": query, "result": "(vector search result here)"}


