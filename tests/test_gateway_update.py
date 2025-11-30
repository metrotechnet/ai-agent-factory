"""
Integration Test for Update Functionality via Gateway API
"""
import requests
import json
import time

def test_update_via_gateway():
    """Test update functionality through the gateway API"""
    print("🧪 Testing Update via Gateway API...")
    
    gateway_url = "http://localhost:8080"
    
    try:
        # Test health endpoint first
        print("1. Testing gateway health...")
        health_response = requests.get(f"{gateway_url}/health", timeout=10)
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"✅ Gateway is healthy: {health_data.get('status')}")
            print(f"   Available agents: {', '.join(health_data.get('available_agents', []))}")
        else:
            print(f"❌ Gateway health check failed: {health_response.status_code}")
            return False
        
        # Test update endpoint
        print("\n2. Testing update endpoint...")
        update_url = f"{gateway_url}/update/nutrition"
        params = {"limit": 3, "enhance_with_ai": False}
        
        print(f"   Making POST request to: {update_url}")
        print(f"   Parameters: {params}")
        
        update_response = requests.post(update_url, params=params, timeout=60)
        
        print(f"   Response status: {update_response.status_code}")
        
        if update_response.status_code == 200:
            result = update_response.json()
            print(f"✅ Update completed successfully!")
            print(f"   Status: {result.get('status')}")
            print(f"   Processed files: {result.get('processed_files', 0)}")
            print(f"   New documents: {result.get('new_documents', 0)}")
            
            if result.get('collection_stats'):
                stats = result['collection_stats']
                print(f"   Total documents in DB: {stats.get('total_documents', 'unknown')}")
            
            if result.get('errors'):
                print(f"   Errors: {result['errors']}")
            
            return True
        else:
            print(f"❌ Update request failed: {update_response.status_code}")
            print(f"   Response: {update_response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to gateway. Make sure it's running on localhost:8080")
        print("   Start it with: python gateway/main.py")
        return False
    except Exception as e:
        print(f"❌ Update test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Gateway Update Integration Test")
    print("=" * 50)
    print("📌 This test requires the gateway to be running!")
    print("   Start with: python gateway/main.py")
    print("=" * 50)
    
    # Wait a moment for user to see the message
    time.sleep(2)
    
    # Run the test
    success = test_update_via_gateway()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Gateway update test completed successfully!")
        print("🌐 You can now test the update button at: http://localhost:8080")
    else:
        print("❌ Gateway update test failed")
        print("🔧 Make sure the gateway is running and try again")

if __name__ == "__main__":
    main()