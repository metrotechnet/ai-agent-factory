"""
Multi-Agent API Gateway
Routes requests to appropriate specialized agents
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import httpx
import os
import json
from typing import Dict, List

app = FastAPI(title="AI Agents Gateway", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Agent service URLs (from environment or config)
AGENT_SERVICES = {
    "nutrition": os.getenv("NUTRITION_SERVICE_URL", "https://ben-nutritionist-prod-159044106998.us-east4.run.app"),
    "fitness": os.getenv("FITNESS_SERVICE_URL", "https://fitness-coach.run.app"),
}

# Agent routing logic
AGENT_KEYWORDS = {
    "nutrition": ["nutrition", "food", "diet", "meal", "vitamin", "calorie", "recipe", "eating"],
    "fitness": ["workout", "exercise", "fitness", "training", "muscle", "cardio", "strength"],
}

def classify_query(question: str) -> str:
    """Classify query to determine appropriate agent"""
    question_lower = question.lower()
    
    scores = {}
    for agent, keywords in AGENT_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in question_lower)
        if score > 0:
            scores[agent] = score
    
    if scores:
        return max(scores, key=scores.get)
    
    # Default to nutrition agent if no clear match
    return "nutrition"

@app.get("/")
async def root():
    return {
        "service": "AI Agents Gateway",
        "version": "2.0.0",
        "available_agents": list(AGENT_SERVICES.keys()),
        "status": "healthy"
    }

@app.get("/agents")
async def list_agents():
    """List all available agents with their capabilities"""
    agent_info = {}
    
    async with httpx.AsyncClient() as client:
        for agent_name, service_url in AGENT_SERVICES.items():
            try:
                response = await client.get(f"{service_url}/health", timeout=5.0)
                agent_info[agent_name] = response.json()
            except:
                agent_info[agent_name] = {"status": "unavailable"}
    
    return agent_info

@app.post("/query")
async def query_gateway(request: dict):
    """Route query to appropriate agent"""
    question = request.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")
    
    # Classify the query
    agent_type = classify_query(question)
    service_url = AGENT_SERVICES.get(agent_type)
    
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not available")
    
    # Forward request to appropriate agent
    async def stream_response():
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{service_url}/query",
                    json=request,
                    timeout=60.0
                ) as response:
                    async for chunk in response.aiter_text():
                        yield chunk
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream",
        headers={
            "X-Agent-Type": agent_type,
            "X-Agent-URL": service_url,
        }
    )

@app.post("/query/{agent_type}")
async def query_specific_agent(agent_type: str, request: dict):
    """Query a specific agent directly"""
    service_url = AGENT_SERVICES.get(agent_type)
    
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_type}' not found")
    
    async def stream_response():
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{service_url}/query",
                json=request,
                timeout=60.0
            ) as response:
                async for chunk in response.aiter_text():
                    yield chunk
    
    return StreamingResponse(
        stream_response(),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)