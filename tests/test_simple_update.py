"""
Simple test of the update pipeline functionality
"""
import asyncio
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

async def test_direct_update():
    """Test the update pipeline directly"""
    print("🧪 Testing Update Pipeline Directly...")
    
    try:
        # Import and test the pipeline directly
        sys.path.append("agents/ben-nutritionist")
        from core.update_pipeline import NutritionUpdatePipeline
        
        print("✅ Successfully imported NutritionUpdatePipeline")
        
        # Create pipeline instance
        pipeline = NutritionUpdatePipeline()
        print("✅ Pipeline instance created")
        
        # Test collection stats first (safer)
        stats = pipeline.get_collection_stats()
        print(f"📊 Collection stats: {stats}")
        
        # Test document processing
        result = pipeline.process_new_documents(limit=2)
        print(f"📄 Processing result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_simple_test_doc():
    """Create a simple test document"""
    docs_dir = Path("agents/ben-nutritionist/documents")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = docs_dir / "simple_test.txt"
    if not test_file.exists():
        test_file.write_text("""
        Test Nutrition Information
        
        This is a simple test document for the update pipeline.
        It contains basic nutrition information about healthy eating.
        
        Key nutrients include:
        - Protein for muscle health
        - Vitamin C for immune support
        - Fiber for digestive health
        """, encoding='utf-8')
        print(f"📄 Created test document: {test_file}")
    else:
        print("ℹ️ Test document already exists")

async def main():
    """Main test function"""
    print("🚀 Simple Update Pipeline Test")
    print("=" * 40)
    
    # Create test document
    create_simple_test_doc()
    
    # Test the pipeline
    success = await test_direct_update()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Update pipeline test completed successfully!")
    else:
        print("❌ Update pipeline test failed")

if __name__ == "__main__":
    asyncio.run(main())