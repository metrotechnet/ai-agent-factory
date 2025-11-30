"""
Test the update functionality integration
"""
import asyncio
import httpx
import json
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

async def test_update_functionality():
    """Test the integrated update functionality"""
    print("🧪 Testing Update Functionality Integration...")
    
    # Test 1: Direct pipeline test
    print("\n1. Testing Direct Update Pipeline...")
    try:
        from agents.ben_nutritionist.core.update_pipeline import run_update_pipeline
        result = await run_update_pipeline(limit=3)
        
        print(f"✅ Direct pipeline test:")
        print(f"   Processed files: {result.get('processed_files', 0)}")
        print(f"   New documents: {result.get('new_documents', 0)}")
        print(f"   Errors: {len(result.get('errors', []))}")
        
    except Exception as e:
        print(f"❌ Direct pipeline test failed: {e}")
    
    # Test 2: Gateway API test
    print("\n2. Testing Gateway Update API...")
    base_url = "http://localhost:8080"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Test update endpoint
            response = await client.post(f"{base_url}/update/nutrition?limit=3&enhance_with_ai=false")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Gateway update API:")
                print(f"   Status: {result.get('status')}")
                print(f"   Processed files: {result.get('processed_files', 0)}")
                print(f"   New documents: {result.get('new_documents', 0)}")
                if result.get('collection_stats'):
                    print(f"   Total documents in DB: {result['collection_stats'].get('total_documents', 'unknown')}")
            else:
                print(f"❌ Gateway update API failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Gateway API test failed: {e}")
    
    # Test 3: Agent-specific update test
    print("\n3. Testing Agent-Specific Update...")
    try:
        from shared.core.base_agent import create_agent
        
        # Create nutrition agent
        agent = create_agent("ben-nutritionist")
        
        # Test update method
        result = await agent.update_knowledge_base(limit=2)
        
        print(f"✅ Agent update method:")
        print(f"   Processed files: {result.get('processed_files', 0)}")
        print(f"   New documents: {result.get('new_documents', 0)}")
        print(f"   Status: {result.get('status', 'success')}")
        
    except Exception as e:
        print(f"❌ Agent update test failed: {e}")

def create_test_documents():
    """Create some test documents for the update pipeline"""
    documents_dir = Path("agents/ben-nutritionist/documents")
    documents_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test nutrition documents
    test_docs = [
        {
            "filename": "test_vitamins.txt",
            "content": """
Vitamin D and Immune Health

Vitamin D plays a crucial role in immune system function. It helps regulate immune responses and supports the body's ability to fight infections.

Key benefits of Vitamin D:
- Supports bone health and calcium absorption
- Enhances immune system function
- May reduce risk of respiratory infections
- Helps with muscle function and strength

Food sources of Vitamin D:
- Fatty fish (salmon, mackerel, sardines)
- Egg yolks
- Fortified dairy products
- Mushrooms (UV-exposed varieties)

Recommended daily intake varies by age and location, typically 600-800 IU for adults.
            """
        },
        {
            "filename": "test_protein.txt", 
            "content": """
Complete vs Incomplete Proteins

Understanding protein quality is essential for optimal nutrition, especially for vegetarians and vegans.

Complete Proteins (contain all essential amino acids):
- Animal sources: meat, fish, poultry, eggs, dairy
- Plant sources: quinoa, buckwheat, hemp seeds, chia seeds, spirulina

Incomplete Proteins (missing one or more essential amino acids):
- Legumes (beans, lentils, peas)
- Grains (rice, wheat, oats)
- Nuts and seeds (most varieties)
- Most vegetables

Protein combining strategies:
- Rice and beans
- Hummus with whole grain pita
- Peanut butter on whole grain bread
- Lentil and grain soups

Daily protein needs: 0.8-1.2g per kg body weight for sedentary adults, more for active individuals.
            """
        }
    ]
    
    created_count = 0
    for doc in test_docs:
        file_path = documents_dir / doc["filename"]
        if not file_path.exists():
            file_path.write_text(doc["content"], encoding='utf-8')
            created_count += 1
            print(f"📄 Created test document: {doc['filename']}")
    
    if created_count > 0:
        print(f"✅ Created {created_count} test documents in {documents_dir}")
    else:
        print("ℹ️ Test documents already exist")

async def main():
    """Run all update functionality tests"""
    print("🚀 Update Functionality Integration Test Suite")
    print("=" * 60)
    
    # Create test documents first
    create_test_documents()
    
    # Run tests
    await test_update_functionality()
    
    print("\n" + "=" * 60)
    print("🎉 Update functionality test suite completed!")
    print("\n📱 Try the update button at: http://localhost:8080")

if __name__ == "__main__":
    asyncio.run(main())