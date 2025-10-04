#!/usr/bin/env python3
"""
Test script for the new Profitability Analysis API endpoints
"""

import requests
import json
from datetime import datetime

# Test on port 8000 (original server)
BASE_URL = "http://localhost:8000"

def test_profitability_endpoints():
    """Test all profitability analysis endpoints"""
    
    print("🧪 TESTING PROFITABILITY ANALYSIS API ENDPOINTS")
    print("=" * 60)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    endpoints = [
        {
            "name": "Profitability Dashboard",
            "method": "GET", 
            "endpoint": "/analyze/profitability/dashboard",
            "description": "Get profitability analysis dashboard"
        },
        {
            "name": "Run Profitability Analysis",
            "method": "POST",
            "endpoint": "/analyze/profitability", 
            "description": "Run comprehensive profitability analysis"
        },
        {
            "name": "Vendor Profitability",
            "method": "GET",
            "endpoint": "/analyze/profitability/vendors",
            "description": "Get vendor profitability analysis"
        },
        {
            "name": "Category Profitability", 
            "method": "GET",
            "endpoint": "/analyze/profitability/categories",
            "description": "Get category profitability analysis"
        }
    ]
    
    results = []
    
    for endpoint_info in endpoints:
        print(f"\n{'='*60}")
        print(f"🔍 Testing: {endpoint_info['name']}")
        print(f"📍 {endpoint_info['method']} {endpoint_info['endpoint']}")
        print(f"📝 {endpoint_info['description']}")
        
        try:
            url = f"{BASE_URL}{endpoint_info['endpoint']}"
            
            if endpoint_info['method'] == 'GET':
                response = requests.get(url, timeout=60)
            else:
                response = requests.post(url, timeout=60)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                
                try:
                    json_response = response.json()
                    
                    # Display key information
                    if 'status' in json_response:
                        print(f"📈 Status: {json_response['status']}")
                    
                    if 'message' in json_response:
                        print(f"💬 Message: {json_response['message']}")
                    
                    if 'summary' in json_response:
                        summary = json_response['summary']
                        if isinstance(summary, dict):
                            print(f"📊 Summary Keys: {list(summary.keys())}")
                    
                    if 'dashboard' in json_response:
                        dashboard = json_response['dashboard']
                        if 'overview' in dashboard:
                            overview = dashboard['overview']
                            print(f"📈 Portfolio Value: {overview.get('portfolio_value', 'N/A')}")
                            print(f"💰 Portfolio Margin: {overview.get('portfolio_margin', 'N/A')}")
                    
                    if 'top_5_products' in json_response:
                        products = json_response['top_5_products']
                        print(f"🏆 Top Products: {len(products)} found")
                        if products:
                            print(f"   🥇 Best: {products[0].get('product_name', 'N/A')} ({products[0].get('margin_percentage', 0):.1f}%)")
                    
                    if 'best_vendors' in json_response:
                        vendors = json_response['best_vendors']
                        print(f"🏢 Best Vendors: {len(vendors)} found")
                        if vendors:
                            print(f"   🥇 Best: {vendors[0].get('vendor_name', 'N/A')} ({vendors[0].get('average_margin', 0):.1f}%)")
                    
                    if 'file_generated' in json_response:
                        print(f"📁 File Generated: {json_response['file_generated']}")
                    
                    results.append({
                        "endpoint": endpoint_info['name'],
                        "status": "SUCCESS",
                        "response_size": len(str(json_response))
                    })
                    
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Response is not valid JSON")
                    print(f"📄 Response Preview: {response.text[:200]}...")
                    results.append({
                        "endpoint": endpoint_info['name'],
                        "status": "SUCCESS (Non-JSON)",
                        "response_size": len(response.text)
                    })
            else:
                print("❌ FAILED!")
                print(f"📄 Error Response: {response.text[:200]}...")
                results.append({
                    "endpoint": endpoint_info['name'],
                    "status": f"FAILED ({response.status_code})",
                    "response_size": 0
                })
                
        except requests.exceptions.ConnectionError:
            print("❌ CONNECTION ERROR!")
            print("🔌 Server may not be running on port 8000")
            results.append({
                "endpoint": endpoint_info['name'],
                "status": "CONNECTION_ERROR",
                "response_size": 0
            })
        except requests.exceptions.Timeout:
            print("⏰ TIMEOUT ERROR!")
            print("🕐 Request took longer than 60 seconds")
            results.append({
                "endpoint": endpoint_info['name'],
                "status": "TIMEOUT",
                "response_size": 0
            })
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")
            results.append({
                "endpoint": endpoint_info['name'],
                "status": f"ERROR: {str(e)}",
                "response_size": 0
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    successful = sum(1 for r in results if "SUCCESS" in r["status"])
    failed = len(results) - successful
    
    print(f"✅ Successful: {successful}/{len(results)}")
    print(f"❌ Failed: {failed}/{len(results)}")
    
    for result in results:
        status_emoji = "✅" if "SUCCESS" in result["status"] else "❌"
        print(f"   {status_emoji} {result['endpoint']}: {result['status']}")
    
    print(f"\n⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful == len(results):
        print("🎉 ALL PROFITABILITY ENDPOINTS WORKING!")
    else:
        print("⚠️ Some endpoints need attention")

if __name__ == "__main__":
    test_profitability_endpoints()