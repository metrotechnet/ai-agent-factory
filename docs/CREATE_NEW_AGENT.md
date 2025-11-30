# 🤖 Creating a New AI Agent - Step-by-Step Guide

This guide shows how to create a new specialized AI agent in the multi-agent platform that can be deployed independently on its own URL.

## 📋 Prerequisites

- Existing multi-agent platform setup
- OpenAI API key configured
- Python environment with required dependencies
- (Optional) Google Cloud Platform account for deployment

## 🚀 Step-by-Step Agent Creation

### **Step 1: Create Agent Directory Structure**

```bash
# Create the agent directory (replace "your-agent" with your agent name)
mkdir agents/your-agent
mkdir agents/your-agent/core
mkdir agents/your-agent/static
mkdir agents/your-agent/templates

# Create Python package files
touch agents/__init__.py
touch agents/your-agent/__init__.py
touch agents/your-agent/core/__init__.py
```

### **Step 2: Implement Core Agent Logic**

Create the main query processing logic:

**File: `agents/your-agent/core/query_agent.py`**
```python
"""
Your Agent Core Logic
"""
import os
from typing import AsyncIterator
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class YourAgentDatabase:
    """Knowledge base for your agent"""
    
    def __init__(self):
        self.knowledge_base = {
            # Add your agent-specific knowledge here
            "example_data": ["item1", "item2", "item3"]
        }
    
    def get_relevant_info(self, query: str):
        # Implement your domain-specific knowledge retrieval
        return self.knowledge_base.get("example_data", [])

# Global database instance
agent_db = YourAgentDatabase()

async def ask_agent_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Process questions and provide streaming responses"""
    
    try:
        # Get relevant information from your knowledge base
        relevant_info = agent_db.get_relevant_info(question)
        
        # Build context for your domain
        context = f"""
        Relevant Information:
        {chr(10).join(f"- {item}" for item in relevant_info)}
        """
        
        # Create your agent-specific prompt
        system_prompt = f"""You are a professional [YOUR DOMAIN] specialist with expertise in:
        - [Expertise Area 1]
        - [Expertise Area 2] 
        - [Expertise Area 3]
        
        STYLE:
        - [Your agent's communication style]
        - [Key characteristics]
        - [Tone and approach]
        
        Available context:
        {context}
        
        User question: {question}
        
        Provide helpful, expert advice in {language}."""
        
        # Get streaming response from GPT
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt}
            ],
            temperature=0.7,
            stream=True
        )
        
        first_chunk = True
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                if first_chunk:
                    content = content.lstrip()
                    first_chunk = False
                if content:
                    yield content
        
    except Exception as e:
        yield f"Error processing question: {str(e)}"
```

### **Step 3: Create Agent Application**

**File: `agents/your-agent/app.py`**
```python
"""
Your Agent Entry Point
"""
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from shared.core.base_agent import create_agent

# Load environment variables
load_dotenv()

# Create the agent
agent = create_agent("your-agent")
app = agent.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
```

### **Step 4: Register Agent in Base Framework**

**File: `shared/core/base_agent.py`**

Add your agent class:
```python
class YourAgent(BaseAgent):
    """Your Agent Implementation"""
    
    def _load_knowledge_base(self):
        """Load your agent's knowledge base"""
        try:
            import sys
            sys.path.append(f"agents/{self.config.agent_name}")
            # Initialize your knowledge base here
            self.logger.info(f"Loaded {self.config.agent_name} knowledge base")
        except Exception as e:
            self.logger.error(f"Failed to load knowledge base: {e}")
    
    async def process_query(self, question: str, language: str, context: Optional[Dict] = None) -> AsyncIterator[str]:
        """Process queries using your agent logic"""
        try:
            import sys
            sys.path.append(f"agents/{self.config.agent_name}")
            from core.query_agent import ask_agent_question_stream
            
            async for chunk in ask_agent_question_stream(question, language):
                yield chunk
        except Exception as e:
            yield f"Error processing query: {str(e)}"
    
    async def render_interface(self, request: Request):
        """Render your agent's interface"""
        return {"message": "Your Agent is running!"}
    
    def get_features(self) -> List[str]:
        return ["your_feature_1", "your_feature_2", "domain_expertise"]
```

Add to agent factory:
```python
def create_agent(agent_name: str) -> BaseAgent:
    """Factory function to create appropriate agent instance"""
    config = AgentConfig(agent_name)
    
    agents = {
        "ben-nutritionist": NutritionAgent,
        "fitness-coach": FitnessAgent,
        "your-agent": YourAgent,  # Add your agent here
        # Add more agents here
    }
    
    if agent_name not in agents:
        raise ValueError(f"Unknown agent: {agent_name}")
    
    return agents[agent_name](config)
```

### **Step 5: Add Agent to Router (Optional - for Gateway)**

**File: `shared/core/agent_router.py`**

Add your agent to the enum:
```python
class AgentType(Enum):
    NUTRITION = "nutrition"
    FITNESS = "fitness" 
    WELLNESS = "wellness"
    YOUR_AGENT = "your_agent"  # Add your agent
```

Add routing keywords:
```python
self.routing_keywords = {
    # ... existing agents
    AgentType.YOUR_AGENT: [
        "keyword1", "keyword2", "keyword3",  # Your domain keywords
        "relevant_term", "domain_specific"
    ]
}
```

Add handler function:
```python
async def ask_your_agent_question_stream(question: str, language: str = "en") -> AsyncIterator[str]:
    """Import and call your agent dynamically"""
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "query_agent", 
            project_root / "agents" / "your-agent" / "core" / "query_agent.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        async for chunk in module.ask_agent_question_stream(question, language):
            yield chunk
    except Exception as e:
        yield f"Error in your agent: {str(e)}"

# Add to agent_handlers
self.agent_handlers = {
    # ... existing handlers
    AgentType.YOUR_AGENT: ask_your_agent_question_stream,
}
```

### **Step 6: Update Gateway (Optional)**

**File: `gateway/main.py`**

Add agent description:
```python
agent_descriptions = {
    # ... existing agents
    "your_agent": {
        "name": "Your Agent Name",
        "description": "Description of what your agent does",
        "specialties": ["Specialty 1", "Specialty 2", "Specialty 3"]
    }
}
```

**File: `gateway/templates/gateway.html`**

Add agent card:
```html
<div class="agent-card" data-agent="your_agent">
    <div class="agent-icon">🎯</div>
    <h3>Your Agent Name</h3>
    <p>Description of your agent's capabilities and expertise.</p>
    <div class="specialties">
        <span class="specialty-tag">Specialty 1</span>
        <span class="specialty-tag">Specialty 2</span>
        <span class="specialty-tag">Specialty 3</span>
    </div>
</div>
```

Add to select dropdown:
```html
<select id="agentSelect" name="agent_type">
    <!-- ... existing options -->
    <option value="your_agent">🎯 Your Agent Name</option>
</select>
```

### **Step 7: Create Deployment Configuration**

**File: `infrastructure/terraform/agents/your-agent/main.tf`**
```hcl
module "your_agent_service" {
  source = "../../modules/agent-service"
  
  agent_name = "your-agent"
  project_id = var.project_id
  region     = var.region
  
  # Agent-specific environment variables
  environment_variables = {
    OPENAI_API_KEY = var.openai_api_key
    AGENT_SPECIALIZATION = "your_domain"
  }
  
  # Resource allocation
  memory_limit = "1Gi"
  cpu_limit    = "1000m"
  
  # Scaling configuration  
  min_instances = 0
  max_instances = 10
}
```

### **Step 8: Test Your Agent**

Create a test file:

**File: `tests/test_your_agent.py`**
```python
"""Test your new agent"""
import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

async def test_your_agent():
    """Test your agent functionality"""
    try:
        from shared.core.base_agent import create_agent
        
        # Create and test your agent
        agent = create_agent("your-agent")
        
        # Test query processing
        test_question = "Test question for your domain"
        print(f"Testing: {test_question}")
        
        response = ""
        async for chunk in agent.process_query(test_question, "en"):
            response += chunk
        
        print(f"Response: {response}")
        return True
        
    except Exception as e:
        print(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_your_agent())
```

### **Step 9: Deploy Your Agent**

#### **Local Testing**
```bash
# Test locally
python agents/your-agent/app.py
# Visit: http://localhost:8080
```

#### **Docker Deployment**
```bash
# Build and run in Docker
python scripts/deploy.py your-agent docker
```

#### **Google Cloud Deployment**
```bash
# Deploy to GCP Cloud Run
python scripts/deploy.py your-agent gcp
# Your agent will get its own URL: https://your-agent-xyz.a.run.app
```

#### **Gateway Integration**
```bash
# Run gateway with all agents
python gateway/main.py
# Visit: http://localhost:8080
```

## 🎯 **Deployment Options Summary**

| Deployment Type | Command | Result |
|----------------|---------|--------|
| **Individual Agent** | `python scripts/deploy.py your-agent gcp` | Independent URL for your agent only |
| **Gateway + Agents** | Deploy gateway + individual agents | Main platform + direct agent access |
| **Local Development** | `python agents/your-agent/app.py` | Local testing at localhost:8080 |

## ✅ **Checklist**

- [ ] Created agent directory structure
- [ ] Implemented core agent logic
- [ ] Created agent application entry point
- [ ] Registered agent in base framework
- [ ] (Optional) Added to gateway router
- [ ] (Optional) Updated gateway interface
- [ ] Created deployment configuration
- [ ] Tested agent functionality
- [ ] Deployed to desired environment

## 🚀 **Next Steps**

After creating your agent:

1. **Enhance Knowledge Base**: Add domain-specific data sources
2. **Customize Interface**: Create agent-specific web templates
3. **Add Update Pipeline**: Implement knowledge base updates
4. **Configure Monitoring**: Add health checks and logging
5. **Scale Resources**: Adjust memory/CPU based on usage
6. **Custom Domain**: Point your domain to the agent URL

Your new agent is now ready and can be deployed independently on its own URL! 🎉