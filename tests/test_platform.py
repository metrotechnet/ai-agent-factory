"""
Test the multi-agent platform
"""
import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from shared.core.agent_router import agent_router, AgentType

async def test_agent_router():
    """Test the agent router functionality"""
    print("🧪 Testing Agent Router...")
    
    # Test query classification
    test_queries = [
        ("What should I eat for breakfast?", AgentType.NUTRITION),
        ("I need a workout plan", AgentType.FITNESS),
        ("I'm feeling stressed", AgentType.WELLNESS),
        ("How many calories in an apple?", AgentType.NUTRITION),
        ("Best exercises for abs", AgentType.FITNESS),
        ("Meditation techniques", AgentType.WELLNESS),
    ]
    
    for query, expected_agent in test_queries:
        predicted_agent = agent_router.classify_query(query)
        status = "✅" if predicted_agent == expected_agent else "❌"
        print(f"{status} Query: '{query}' -> {predicted_agent.value} (expected: {expected_agent.value})")
    
    # Test actual query processing
    print("\n🤖 Testing Agent Query Processing...")
    
    test_question = "What are some healthy breakfast options?"
    print(f"Question: {test_question}")
    print("Response:", end=" ")
    
    try:
        async for chunk in agent_router.route_query(test_question):
            print(chunk, end="", flush=True)
        print("\n✅ Query processing successful")
    except Exception as e:
        print(f"\n❌ Query processing failed: {e}")

async def test_gateway_api():
    """Test the gateway API endpoints"""
    print("\n🌐 Testing Gateway API...")
    
    base_url = "http://localhost:8080"
    
    async with httpx.AsyncClient() as client:
        try:
            # Test health endpoint
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Health check: {health_data['status']}")
                print(f"   Available agents: {', '.join(health_data['available_agents'])}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
            
            # Test agent info endpoints
            for agent_type in ["nutrition", "fitness", "wellness"]:
                response = await client.get(f"{base_url}/agents/{agent_type}")
                if response.status_code == 200:
                    agent_info = response.json()
                    print(f"✅ {agent_info['name']}: {agent_info['description'][:50]}...")
                else:
                    print(f"❌ Agent info failed for {agent_type}: {response.status_code}")
            
        except Exception as e:
            print(f"❌ API test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Multi-Agent Platform Test Suite")
    print("=" * 50)
    
    await test_agent_router()
    await test_gateway_api()
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n📱 Access the platform at: http://localhost:8080")

if __name__ == "__main__":
    asyncio.run(main())