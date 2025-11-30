"""
Ben Nutritionist API - Production Cloud Run Version
"""
import os
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Ben Boulanger - Nutrition Expert", 
    version="2.0.0",
    description="AI-powered nutrition assistant by Ben Boulanger"
)

@app.get("/")
async def root():
    """Welcome endpoint"""
    return {
        "message": "Welcome to Ben Boulanger's Nutrition Expert API",
        "version": "2.0.0",
        "status": "healthy",
        "endpoints": {
            "health": "/health",
            "query": "/query (POST)",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "Ben Boulanger Nutrition Expert",
        "version": "2.0.0"
    }

@app.post("/query")
async def query_nutrition(
    question: str = Form(...),
    language: str = Form(default="en")
):
    """
    Query the nutrition expert
    Note: Full ChromaDB functionality will be added once database is properly configured
    """
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # For now, return a mock response until ChromaDB is properly configured
    return {
        "question": question,
        "language": language,
        "response": f"Thank you for your nutrition question: '{question}'. Ben Boulanger's AI nutrition expert is now online! Full functionality with 842+ nutrition documents will be available soon.",
        "status": "success",
        "note": "This is a basic response. Full ChromaDB integration coming soon."
    }

@app.get("/status")
async def status():
    """Service status information"""
    return {
        "service": "Ben Boulanger Nutrition Expert",
        "version": "2.0.0",
        "status": "online",
        "features": {
            "basic_api": "active",
            "chromadb": "pending_configuration",
            "document_count": "842+ (to be integrated)"
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    logger.info(f"Starting Ben Nutritionist API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)