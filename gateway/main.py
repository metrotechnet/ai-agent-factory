"""
API Gateway - Main entry point for all agents
Provides unified interface and intelligent routing
"""
import os
from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
from typing import Optional
from pathlib import Path

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.core.agent_router import agent_router, AgentType

# Create FastAPI app
app = FastAPI(title="AI Agent Platform", description="Multi-agent AI platform with specialized assistants")

# Setup templates - use a shared template directory
TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_DIR.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# Setup static files
STATIC_DIR = Path(__file__).parent / "static"
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Main landing page with agent selection"""
    return templates.TemplateResponse("gateway.html", {
        "request": request,
        "agents": agent_router.get_available_agents()
    })

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "platform": "AI Agent Platform",
        "available_agents": agent_router.get_available_agents()
    }

@app.post("/query")
async def query_agent(
    question: str = Form(...),
    language: str = Form(default="en"),
    agent_type: Optional[str] = Form(default=None)
):
    """Process query through appropriate agent"""
    
    # Convert string to AgentType enum if specified
    selected_agent = None
    if agent_type and agent_type != "auto":
        try:
            selected_agent = AgentType(agent_type)
        except ValueError:
            pass  # Fall back to auto-routing
    
    async def generate_response():
        try:
            async for chunk in agent_router.route_query(question, language, selected_agent):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate_response(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )

@app.get("/agents/{agent_type}")
async def agent_info(agent_type: str):
    """Get information about a specific agent"""
    
    agent_descriptions = {
        "nutrition": {
            "name": "Ben Boulanger - Nutrition Expert",
            "description": "Expert nutritionist with 842+ indexed documents providing personalized nutrition advice",
            "specialties": ["Nutrition planning", "Meal recommendations", "Supplement advice", "Dietary restrictions"]
        },
        "fitness": {
            "name": "Fitness Coach",
            "description": "Professional fitness trainer specializing in workout plans and exercise guidance",
            "specialties": ["Workout planning", "Exercise techniques", "Injury prevention", "Fitness goals"]
        },
        "wellness": {
            "name": "Wellness Therapist", 
            "description": "Mental health and wellness specialist focused on stress management and mindfulness",
            "specialties": ["Stress management", "Meditation guidance", "Mental health support", "Work-life balance"]
        }
    }
    
    return agent_descriptions.get(agent_type, {"error": "Agent not found"})

@app.post("/update/{agent_type}")
async def update_agent_knowledge(agent_type: str, limit: int = 10, enhance_with_ai: bool = False):
    """Update specific agent's knowledge base"""
    
    # For now, only nutrition agent supports updates
    if agent_type == "nutrition":
        try:
            # Import and run the nutrition update pipeline directly
            import sys
            from pathlib import Path
            project_root = Path(__file__).parent.parent
            sys.path.append(str(project_root))
            
            from agents.ben_nutritionist.core.update_pipeline import run_update_pipeline
            result = await run_update_pipeline(limit=limit, enhance_with_ai=enhance_with_ai)
            
            return {
                "status": "success",
                "agent": agent_type,
                "message": "Knowledge base updated successfully",
                **result
            }
        except Exception as e:
            return {
                "status": "error", 
                "agent": agent_type,
                "message": f"Update failed: {str(e)}"
            }
    else:
        return {
            "status": "error",
            "agent": agent_type, 
            "message": f"Update not supported for {agent_type} agent"
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)