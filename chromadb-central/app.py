# Endpoint générique pour requêter n'importe quelle collection d'un projet
from fastapi import Body
from api.query_chromadb import get_collection

"""
ChromaDB Central API
Provides access to multiple project vector databases (Bibliosense, Nutria, Translator).
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import asynccontextmanager
from api.query_chromadb import list_collections, query_vector_db, preload_all_collections

# Use FastAPI lifespan context for startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60, flush=True)
    print("🚀 Starting IMX Agent Factory...", flush=True)
    print("=" * 60, flush=True)
    try:
        preload_all_collections(["bibliosense", "nutria", "innovia"])
        from api.query_chromadb import list_collections
        for db in ["bibliosense", "nutria", "innovia"]:
            collections = list_collections(db)
            if collections:
                print(f"✅ ChromaDB loaded successfully!", flush=True)
                print(f"   - Project: {db}", flush=True)
                print(f"   - Collections found:", flush=True)
                for col in collections:
                    print(f"     • {col.name} (count: {col.count()})", flush=True)
            else:
                print(f"⚠️  Warning: No ChromaDB collection found for '{db}'", flush=True)
                print(f"   Database will be loaded on first query", flush=True)
    except Exception as e:
        print(f"⚠️  Warning: Failed to preload ChromaDB: {str(e)}", flush=True)
        print(f"   Database will be loaded on first query", flush=True)
    print("=" * 60, flush=True)
    print("✅ Application startup complete", flush=True)
    print("=" * 60, flush=True)
    yield
    print("🛑 Shutting down IMX Agent Factory...", flush=True)

app = FastAPI(title="IMX Agent Factory - ChromaDB Central API", lifespan=lifespan)


# Root endpoint
@app.get("/")
def root():
    return {"message": "ChromaDB Central API is running."}


@app.post("/query")
async def generic_query_post(
    payload: dict = Body(...)
):
    """
    Expects JSON body with:
      - project_name: str
      - collection_name: str (optional)
      - query: dict (requête ChromaDB)
    """
    print (f"Received query for project '{payload.get('project_name')}' collection '{payload.get('collection_name')}' ", flush=True)
    project_name = payload.get("project_name")
    collection_name = payload.get("collection_name")
    data = payload.get("query")
    result = query_vector_db(project_name, collection_name, data)
    # print(f"Query result: {result}", flush=True)
    return JSONResponse(content=result)



# =====================================================
# Run Application
# =====================================================
if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 2000))
    uvicorn.run(app, host="0.0.0.0", port=port)