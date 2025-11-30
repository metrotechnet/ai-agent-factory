"""
Base Agent Framework - Shared functionality for all AI agents
"""
import os
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any, AsyncIterator
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging

class AgentConfig:
    """Configuration management for agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.specialization = os.getenv("AGENT_SPECIALIZATION")
        self.db_type = os.getenv("DB_TYPE", "chromadb")
        self.languages = os.getenv("LANGUAGE_SUPPORT", "en").split(",")
        
    @property
    def config_path(self) -> Path:
        return Path(f"agents/{self.agent_name}/config")
    
    @property
    def documents_path(self) -> Path:
        return Path(f"agents/{self.agent_name}/documents")

class QueryRequest(BaseModel):
    question: str
    language: str = "en"
    context: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.app = FastAPI(title=f"{config.agent_name.title()} AI Agent")
        self.logger = self._setup_logging()
        self._setup_routes()
        self._load_knowledge_base()
    
    def _setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(f"agent.{self.config.agent_name}")
    
    def _setup_routes(self):
        """Setup common FastAPI routes"""
        
        @self.app.get("/")
        async def home(request: Request):
            return await self.render_interface(request)
        
        @self.app.get("/health")
        async def health():
            return {
                "service": f"{self.config.agent_name}-agent",
                "status": "healthy",
                "version": "2.0.0",
                "specialization": self.config.specialization,
                "features": self.get_features()
            }
        
        @self.app.post("/query")
        async def query_agent(request: QueryRequest):
            async def generate():
                async for chunk in self.process_query(
                    request.question, 
                    request.language,
                    request.context
                ):
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/event-stream",
                headers={"Cache-Control": "no-cache"}
            )
        
        @self.app.post("/update")
        async def update_knowledge_base(limit: int = 10, enhance_with_ai: bool = False):
            """Update agent's knowledge base with new content"""
            try:
                result = await self.update_knowledge_base(limit, enhance_with_ai)
                return {
                    "status": "success",
                    "message": "Knowledge base updated successfully",
                    **result
                }
            except Exception as e:
                self.logger.error(f"Update failed: {e}")
                return {
                    "status": "error",
                    "message": f"Failed to update knowledge base: {str(e)}"
                }
    
    @abstractmethod
    async def process_query(self, question: str, language: str, context: Optional[Dict] = None) -> AsyncIterator[str]:
        """Process a user query and return streaming response"""
        pass
    
    @abstractmethod
    def _load_knowledge_base(self):
        """Load agent-specific knowledge base"""
        pass
    
    @abstractmethod
    async def render_interface(self, request: Request):
        """Render the agent's web interface"""
        pass
    
    @abstractmethod
    def get_features(self) -> List[str]:
        """Return list of agent features"""
        pass
    
    async def update_knowledge_base(self, limit: int = 10, enhance_with_ai: bool = False) -> Dict:
        """Update agent's knowledge base - default implementation"""
        return {
            "processed_files": 0,
            "new_documents": 0,
            "message": "Update not implemented for this agent type"
        }

class NutritionAgent(BaseAgent):
    """Ben Nutritionist AI Agent"""
    
    def __init__(self, config: AgentConfig):
        super().__init__(config)
        # Mount static files and templates
        self.app.mount("/static", StaticFiles(directory=f"agents/{config.agent_name}/static"), name="static")
        self.templates = Jinja2Templates(directory=f"agents/{config.agent_name}/templates")
    
    def _load_knowledge_base(self):
        """Load ChromaDB with nutrition documents"""
        try:
            import sys
            sys.path.append(f"agents/{self.config.agent_name}")
            from core.query_chromadb import get_collection
            self.collection = get_collection()
            self.logger.info(f"Loaded nutrition knowledge base with {self.collection.count() if self.collection else 0} documents")
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
            self.collection = None
    
    async def process_query(self, question: str, language: str, context: Optional[Dict] = None) -> AsyncIterator[str]:
        """Process nutrition query using ChromaDB and GPT-4"""
        try:
            import sys
            sys.path.append(f"agents/{self.config.agent_name}")
            from core.query_chromadb import ask_question_stream
            
            async for chunk in ask_question_stream(question, language):
                yield chunk
        except Exception as e:
            yield f"Error processing query: {str(e)}"
    
    async def render_interface(self, request: Request):
        """Render nutrition interface"""
        return self.templates.TemplateResponse("index.html", {"request": request})
    
    def get_features(self) -> List[str]:
        return ["nutrition_ai", "chromadb", "multilingual", "meal_planning", "document_updates"]
    
    async def update_knowledge_base(self, limit: int = 10, enhance_with_ai: bool = False) -> Dict:
        """Update nutrition knowledge base with new documents"""
        try:
            import sys
            sys.path.append(f"agents/{self.config.agent_name}")
            from core.update_pipeline import run_update_pipeline
            
            result = await run_update_pipeline(limit=limit, enhance_with_ai=enhance_with_ai)
            
            # Reload the knowledge base after update
            self._load_knowledge_base()
            
            return result
        except Exception as e:
            self.logger.error(f"Failed to update nutrition knowledge base: {e}")
            return {
                "processed_files": 0,
                "new_documents": 0,
                "errors": [str(e)],
                "status": "failed"
            }

class FitnessAgent(BaseAgent):
    """Fitness Coach AI Agent"""
    
    def _load_knowledge_base(self):
        """Load Pinecone with fitness data"""
        # Implementation for Pinecone fitness database
        pass
    
    async def process_query(self, question: str, language: str, context: Optional[Dict] = None) -> AsyncIterator[str]:
        """Process fitness queries with workout recommendations"""
        # Implementation for fitness-specific processing
        pass
    
    async def render_interface(self, request: Request):
        """Render fitness interface with workout tracking"""
        pass
    
    def get_features(self) -> List[str]:
        return ["workout_plans", "fitness_tracking", "progress_monitoring"]

# Agent Factory
def create_agent(agent_name: str) -> BaseAgent:
    """Factory function to create appropriate agent instance"""
    config = AgentConfig(agent_name)
    
    agents = {
        "ben-nutritionist": NutritionAgent,
        "fitness-coach": FitnessAgent,
        # Add more agents here
    }
    
    if agent_name not in agents:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    return agents[agent_name](config)