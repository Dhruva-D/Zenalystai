#!/usr/bin/env python3
"""
Test script for ABC Book House Inventory Analysis API
Tests all the new inventory analysis endpoints
"""

import requests
import json
import time
from datetime import datetime

# API Base URL
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, method: str = "GET", data: dict = None):
    """Test an API endpoint and return the response"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        print(f"\n{'='*60}")
        print(f"🔍 Testing: {method} {endpoint}")
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            try:
                json_response = response.json()
                # Print first few keys to avoid overwhelming output
                if isinstance(json_response, dict):
                    keys = list(json_response.keys())[:5]
                    print(f"📋 Response Keys: {keys}")
                    if "message" in json_response:
                        print(f"💬 Message: {json_response['message']}")
                else:
                    print(f"📄 Response Type: {type(json_response)}")
            except:
                print(f"📄 Response Length: {len(response.text)} characters")
        else:
            print("❌ FAILED!")
            print(f"📄 Error: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Test all inventory analysis endpoints"""
    print("🚀 ABC Book House - Inventory Analysis API Test Suite")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Base URL: {BASE_URL}")
    
    # Test basic server health
    print("\n" + "="*60)
    print("🏥 HEALTH CHECK")
    test_endpoint("/")
    
    # Test inventory analysis endpoints
    print("\n" + "="*60) 
    print("📦 INVENTORY ANALYSIS ENDPOINTS")
    
    # Test dashboard
    test_endpoint("/analyze/inventory/dashboard")
    
    # Test individual analysis endpoints
    test_endpoint("/analyze/inventory-cost", "POST")
    test_endpoint("/analyze/inventory-ageing", "POST") 
    test_endpoint("/analyze/inventory-valuation", "POST")
    
    # Test comprehensive analysis
    test_endpoint("/analyze/inventory/comprehensive", "POST")
    
    # Test other existing endpoints
    print("\n" + "="*60)
    print("🔍 OTHER KEY ENDPOINTS")
    
    test_endpoint("/api/matching/dashboard")
    test_endpoint("/verify/po-invoice/dashboard")
    
    print("\n" + "="*60)
    print("🎉 API Testing Complete!")
    print(f"⏰ Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()