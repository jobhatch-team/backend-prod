#!/usr/bin/env python3
"""
Test script to verify JobHatch backend deployment on Vercel
"""

import requests
import json
import time
from typing import Dict, Any

def test_endpoint(url: str, method: str = 'GET', expected_status: int = 200) -> Dict[str, Any]:
    """Test a single endpoint"""
    try:
        print(f"Testing {method} {url}")
        
        if method == 'GET':
            response = requests.get(url, timeout=10)
        elif method == 'POST':
            response = requests.post(url, json={}, timeout=10)
        elif method == 'OPTIONS':
            response = requests.options(url, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"  Status: {response.status_code}")
        print(f"  Headers: {dict(response.headers)}")
        
        if response.status_code == expected_status:
            try:
                data = response.json()
                print(f"  Response: {json.dumps(data, indent=2)}")
                return {"success": True, "data": data, "status": response.status_code}
            except:
                print(f"  Response (text): {response.text}")
                return {"success": True, "data": response.text, "status": response.status_code}
        else:
            print(f"  ERROR: Expected {expected_status}, got {response.status_code}")
            print(f"  Response: {response.text}")
            return {"success": False, "error": f"Status {response.status_code}", "data": response.text}
            
    except requests.exceptions.RequestException as e:
        print(f"  ERROR: Request failed - {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        print(f"  ERROR: Unexpected error - {e}")
        return {"success": False, "error": str(e)}

def main():
    """Main test function"""
    base_url = "https://backend-prod-dun.vercel.app"
    
    print("=" * 60)
    print("JobHatch Backend Deployment Test")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test endpoints
    endpoints = [
        # Basic health checks
        ("Root endpoint", f"{base_url}/", "GET"),
        ("Health endpoint", f"{base_url}/api/health", "GET"),
        ("Test endpoint", f"{base_url}/api/test", "GET"),
        
        # Waitlist endpoint (the problematic one)
        ("Waitlist GET", f"{base_url}/api/waitlist", "GET"),
        ("Waitlist OPTIONS", f"{base_url}/api/waitlist", "OPTIONS"),
        
        # Other critical endpoints
        ("Jobs endpoint", f"{base_url}/api/jobs", "GET"),
        ("Auth endpoint", f"{base_url}/api/auth", "GET"),
        ("Resumes endpoint", f"{base_url}/api/resumes", "GET"),
        ("Onboarding endpoint", f"{base_url}/api/onboarding", "GET"),
        ("Profiles endpoint", f"{base_url}/api/profiles", "GET"),
        
        # AI endpoints
        ("AI endpoint", f"{base_url}/api/ai", "GET"),
        
        # Documentation
        ("API docs", f"{base_url}/api/docs", "GET"),
    ]
    
    results = []
    
    for name, url, method in endpoints:
        print(f"\n{'-' * 40}")
        print(f"TEST: {name}")
        print(f"{'-' * 40}")
        
        result = test_endpoint(url, method)
        results.append((name, result))
        
        time.sleep(0.5)  # Small delay between requests
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    success_count = 0
    for name, result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {name}")
        if result["success"]:
            success_count += 1
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {success_count}")
    print(f"Failed: {len(results) - success_count}")
    
    if success_count == len(results):
        print("\n🎉 ALL TESTS PASSED! Backend deployment is working correctly.")
    else:
        print(f"\n⚠️  {len(results) - success_count} tests failed. Check the errors above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 