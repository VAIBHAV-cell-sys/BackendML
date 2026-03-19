"""
API Testing Script
Tests all endpoints to verify system functionality
"""
import requests
import json
from typing import Dict

# Base URL
BASE_URL = "http://localhost:8000"

def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_response(response: requests.Response):
    """Print formatted response"""
    print(f"\nStatus Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def test_health():
    """Test health check endpoint"""
    print_section("TEST 1: Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response)
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print_section("TEST 2: Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response(response)
    return response.status_code == 200

def test_weather():
    """Test weather endpoint"""
    print_section("TEST 3: Weather Data")
    response = requests.get(f"{BASE_URL}/weather/Pune")
    print_response(response)
    return response.status_code == 200

def test_soil():
    """Test soil endpoint"""
    print_section("TEST 4: Soil Data")
    response = requests.get(f"{BASE_URL}/soil/Delhi")
    print_response(response)
    return response.status_code == 200

def test_price():
    """Test price endpoint"""
    print_section("TEST 5: Crop Price")
    response = requests.get(f"{BASE_URL}/price/wheat")
    print_response(response)
    return response.status_code == 200

def test_crops():
    """Test crops listing"""
    print_section("TEST 6: List All Crops")
    response = requests.get(f"{BASE_URL}/crops")
    print_response(response)
    return response.status_code == 200

def test_analyze():
    """Test farm analysis"""
    print_section("TEST 7: Farm Analysis")
    response = requests.get(f"{BASE_URL}/analyze/Mumbai")
    print_response(response)
    return response.status_code == 200

def test_advice_get():
    """Test advice endpoint (GET)"""
    print_section("TEST 8: Get Advice (GET)")
    params = {
        "message": "What crop should I plant this season?",
        "location": "Pune"
    }
    response = requests.get(f"{BASE_URL}/advice", params=params)
    print_response(response)
    return response.status_code == 200

def test_advice_post():
    """Test advice endpoint (POST)"""
    print_section("TEST 9: Get Advice (POST)")
    data = {
        "message": "Is rice profitable right now?",
        "location": "Kolkata"
    }
    response = requests.post(f"{BASE_URL}/advice", json=data)
    print_response(response)
    return response.status_code == 200

def test_quick_advice():
    """Test quick advice endpoint"""
    print_section("TEST 10: Quick Advice")
    response = requests.get(f"{BASE_URL}/quick-advice/Bangalore")
    print_response(response)
    return response.status_code == 200

def test_compare_crops():
    """Test crop comparison"""
    print_section("TEST 11: Compare Crops")
    params = {
        "crops": "wheat,rice,cotton",
        "area_acres": 2
    }
    response = requests.get(f"{BASE_URL}/compare-crops/Pune", params=params)
    print_response(response)
    return response.status_code == 200

def run_all_tests():
    """Run all tests"""
    print("\n" + "█" * 70)
    print("  CLIMATE-RESILIENT CROP ADVISORY API - TEST SUITE")
    print("█" * 70)
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Weather Data", test_weather),
        ("Soil Data", test_soil),
        ("Crop Price", test_price),
        ("List Crops", test_crops),
        ("Farm Analysis", test_analyze),
        ("Advice (GET)", test_advice_get),
        ("Advice (POST)", test_advice_post),
        ("Quick Advice", test_quick_advice),
        ("Compare Crops", test_compare_crops)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except requests.exceptions.ConnectionError:
            print(f"\n❌ ERROR: Cannot connect to {BASE_URL}")
            print("Make sure the server is running: python main.py")
            return
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

if __name__ == "__main__":
    print("\nStarting API tests...")
    print(f"Target: {BASE_URL}")
    print("\nNote: Make sure the server is running before running tests!")
    print("Start server with: python main.py\n")
    
    input("Press Enter to start tests...")
    
    run_all_tests()
