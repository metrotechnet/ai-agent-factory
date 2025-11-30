"""
Agent Registry and Router
Central hub for managing and routing between different AI agents
"""
from typing import Dict, Type, List, Optional
from enum import Enum
from pathlib import Path
import re

# Import all agent types
from typing import AsyncIterator
import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Dynamic imports to avoid circular dependencies
async def ask_nutrition_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Import and call nutrition agent dynamically"""
    try:
        # Import the module at runtime
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "query_nutrition", 
            project_root / "agents" / "ben-nutritionist" / "core" / "query_chromadb.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        async for chunk in module.ask_question_stream(question, language):
            yield chunk
    except Exception as e:
        yield f"Error in nutrition agent: {str(e)}"

async def ask_fitness_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Import and call fitness agent dynamically"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "query_fitness", 
            project_root / "agents" / "fitness-coach" / "core" / "query_fitness.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        async for chunk in module.ask_fitness_question_stream(question, language):
            yield chunk
    except Exception as e:
        yield f"Error in fitness agent: {str(e)}"

async def ask_wellness_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Import and call wellness agent dynamically"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "query_wellness", 
            project_root / "agents" / "wellness-therapist" / "core" / "query_wellness.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        async for chunk in module.ask_wellness_question_stream(question, language):
            yield chunk
    except Exception as e:
        yield f"Error in wellness agent: {str(e)}"

class AgentType(Enum):
    NUTRITION = "nutrition"
    FITNESS = "fitness"
    WELLNESS = "wellness"

class AgentRouter:
    """Routes user queries to appropriate specialized agents"""
    
    def __init__(self):
        self.agent_handlers = {
            AgentType.NUTRITION: ask_nutrition_question_stream,
            AgentType.FITNESS: ask_fitness_question_stream,
            AgentType.WELLNESS: ask_wellness_question_stream
        }
        
        # Keywords for automatic routing
        self.routing_keywords = {
            AgentType.NUTRITION: [
                "nutrition", "diet", "food", "meal", "eating", "vitamin", 
                "protein", "carb", "fat", "calorie", "recipe", "ingredient",
                "supplement", "mineral", "nutrient", "healthy eating"
            ],
            AgentType.FITNESS: [
                "workout", "exercise", "fitness", "training", "gym", "muscle",
                "strength", "cardio", "running", "weight", "reps", "sets",
                "sports", "athletic", "performance", "endurance"
            ],
            AgentType.WELLNESS: [
                "stress", "anxiety", "depression", "mental health", "meditation",
                "mindfulness", "therapy", "wellness", "self-care", "burnout",
                "sleep", "relaxation", "breathing", "emotional", "mood"
            ]
        }
    
    def classify_query(self, query: str) -> AgentType:
        """Classify user query to determine which agent should handle it"""
        query_lower = query.lower()
        
        # Count keyword matches for each agent type
        scores = {agent_type: 0 for agent_type in AgentType}
        
        for agent_type, keywords in self.routing_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    scores[agent_type] += 1
        
        # Return agent type with highest score
        best_agent = max(scores.items(), key=lambda x: x[1])
        
        # If no clear match, default to nutrition (most general)
        if best_agent[1] == 0:
            return AgentType.NUTRITION
            
        return best_agent[0]
    
    async def route_query(self, query: str, language: str = "en", agent_type: Optional[AgentType] = None):
        """Route query to appropriate agent handler"""
        
        # Auto-classify if no specific agent requested
        if agent_type is None:
            agent_type = self.classify_query(query)
        
        # Get the handler function
        handler = self.agent_handlers.get(agent_type)
        if not handler:
            raise ValueError(f"No handler found for agent type: {agent_type}")
        
        # Stream response from appropriate agent
        async for chunk in handler(query, language):
            yield chunk
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent types"""
        return [agent.value for agent in AgentType]

# Global router instance
agent_router = AgentRouter()