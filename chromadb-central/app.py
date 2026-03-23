
"""
ChromaDB Central API
Provides access to multiple project vector databases (Bibliosense, Nutria, Translator).
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.concurrency import asynccontextmanager
from api.query_chromadb import get_collection, query_vector_db, preload_all_collections

# Use FastAPI lifespan context for startup/shutdown logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60, flush=True)
    print("🚀 Starting IMX Agent Factory...", flush=True)
    print("=" * 60, flush=True)
    try:
        preload_all_collections(["bibliosense", "nutria"])
        for db in ["bibliosense", "nutria"]:
            collection = get_collection(db)
            if collection:
                count = collection.count()
                print(f"✅ ChromaDB loaded successfully!", flush=True)
                print(f"   - Collection: gdrive_documents", flush=True)
                print(f"   - Documents: {count:,}", flush=True)
                print(f"   - Knowledge base: {db}", flush=True)
            else:
                print(f"⚠️  Warning: ChromaDB collection not found for '{db}'", flush=True)
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



# POST: advanced vector search for Bibliosense
@app.post("/bibliosense/query")
async def bibliosense_query_post(request: Request):
    data = await request.json()
    result = query_vector_db("bibliosense", data)
    return JSONResponse(content=result)

# POST: advanced vector search for Nutria
@app.post("/nutria/query")
async def nutria_query_post(request: Request):
    data = await request.json()
    result = query_vector_db("nutria", data)
    return JSONResponse(content=result)

