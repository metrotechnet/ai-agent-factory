"""
Ben Nutritionist AI Agent Entry Point
"""
import sys
import os

# Add parent directories to path so we can import shared modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from dotenv import load_dotenv
from shared.core.base_agent import create_agent

# Load environment variables
load_dotenv()

# Create the nutrition agent
agent = create_agent("ben-nutritionist")
app = agent.app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))