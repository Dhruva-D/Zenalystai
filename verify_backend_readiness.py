#!/usr/bin/env python3
"""
Comprehensive Backend Readiness Verification Script
Verifies all 5 tasks' APIs are ready for frontend connection

Tasks to verify:
- Task 1-2: Document Processing & 3-Way Matching
- Task 3: Inventory Cost Analysis  
- Task 4: Inventory Ageing Analysis
- Task 5: FIFO Inventory Valuation Analysis
- Final Task: Comprehensive Profitability Analysis
"""

import requests
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, method="GET", data=None, description=""):
    """Test a single endpoint and return detailed results"""
    try:
        url = f"{BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=30)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        status = "✅ READY" if response.status_code == 200 else f"❌ FAILED ({response.status_code})"
        
        # Parse response for key info
        response_info = ""
        if response.status_code == 200:
            try:
                json_resp = response.json()
                if "status" in json_resp and json_resp["status"] == "success":
                    response_info = " - Analysis Complete"
                elif "dashboard" in json_resp:
                    response_info = " - Dashboard Ready"
                elif "message" in json_resp:
                    response_info = f" - {json_resp['message'][:50]}..."
            except:
                response_info = " - Non-JSON Response"
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "status_code": response.status_code,
            "description": description,
            "response_info": response_info
        }
        
    except requests.exceptions.ConnectionError:
        return {
            "endpoint": endpoint,
            "method": method, 
            "status": "🔌 CONNECTION ERROR",
            "status_code": 0,
            "description": description,
            "response_info": "Server not running"
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status": f"❌ ERROR: {str(e)[:30]}",
            "status_code": 0,
            "description": description,
            "response_info": ""
        }

def verify_backend_readiness():
    """Comprehensive verification of all backend endpoints"""
    
    print("🔍 BACKEND READINESS VERIFICATION FOR FRONTEND CONNECTION")
    print("=" * 80)
    print(f"🌐 Base URL: {BASE_URL}")
    print(f"⏰ Verification Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Define all endpoints organized by task
    endpoints = {
        "🏥 System Health": [
            {"endpoint": "/", "method": "GET", "description": "Main API health check"},
            {"endpoint": "/health", "method": "GET", "description": "Detailed health status"}
        ],
        
        "📋 Tasks 1-2: Document Processing & 3-Way Matching": [
            {"endpoint": "/extract/purchase-orders", "method": "POST", "description": "Extract Purchase Orders"},
            {"endpoint": "/extract/grn", "method": "POST", "description": "Extract GRN records"},
            {"endpoint": "/extract/purchase-invoices", "method": "POST", "description": "Extract Purchase Invoices"},
            {"endpoint": "/extract/sales-invoices", "method": "POST", "description": "Extract Sales Invoices"},
            {"endpoint": "/analytics/comprehensive", "method": "GET", "description": "Comprehensive analytics dashboard"},
            {"endpoint": "/api/matching/dashboard", "method": "GET", "description": "3-Way matching dashboard"},
            {"endpoint": "/api/matching/details", "method": "GET", "description": "3-Way matching details"}
        ],
        
        "📊 Task 3: Inventory Cost Analysis": [
            {"endpoint": "/analyze/inventory-cost", "method": "POST", "description": "Run inventory cost analysis"},
        ],
        
        "📅 Task 4: Inventory Ageing Analysis": [
            {"endpoint": "/analyze/inventory-ageing", "method": "POST", "description": "Run inventory ageing analysis"},
        ],
        
        "💰 Task 5: FIFO Inventory Valuation": [
            {"endpoint": "/analyze/inventory-valuation", "method": "POST", "description": "Run FIFO valuation analysis"},
        ],
        
        "📦 Unified Inventory Dashboard": [
            {"endpoint": "/analyze/inventory/dashboard", "method": "GET", "description": "Unified inventory dashboard"},
            {"endpoint": "/analyze/inventory/comprehensive", "method": "POST", "description": "Run all inventory analyses"}
        ],
        
        "🎯 Final Task: Profitability Analysis": [
            {"endpoint": "/analyze/profitability", "method": "POST", "description": "Run comprehensive profitability analysis"},
            {"endpoint": "/analyze/profitability/dashboard", "method": "GET", "description": "Profitability dashboard"},
            {"endpoint": "/analyze/profitability/vendors", "method": "GET", "description": "Vendor profitability analysis"},
            {"endpoint": "/analyze/profitability/categories", "method": "GET", "description": "Category profitability analysis"}
        ],
        
        "🔍 PO-Invoice Verification": [
            {"endpoint": "/verify/po-invoice", "method": "POST", "description": "Run PO-Invoice verification"},
            {"endpoint": "/verify/po-invoice/dashboard", "method": "GET", "description": "PO-Invoice verification dashboard"}
        ]
    }
    
    all_results = {}
    total_endpoints = 0
    successful_endpoints = 0
    
    # Test each category
    for category, category_endpoints in endpoints.items():
        print(f"\n{category}")
        print("-" * 60)
        
        category_results = []
        
        for endpoint_info in category_endpoints:
            result = test_endpoint(
                endpoint_info["endpoint"],
                endpoint_info["method"], 
                description=endpoint_info["description"]
            )
            
            category_results.append(result)
            total_endpoints += 1
            
            if "✅ READY" in result["status"]:
                successful_endpoints += 1
            
            # Display result
            status_emoji = "✅" if "✅ READY" in result["status"] else "❌"
            print(f"   {status_emoji} {result['method']} {result['endpoint']}")
            print(f"      📝 {result['description']}")
            print(f"      📊 Status: {result['status']}{result['response_info']}")
        
        all_results[category] = category_results
    
    # Overall Summary
    print(f"\n{'=' * 80}")
    print("📊 BACKEND READINESS SUMMARY")
    print(f"{'=' * 80}")
    
    success_rate = (successful_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
    
    print(f"✅ Successful Endpoints: {successful_endpoints}/{total_endpoints}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print(f"❌ Failed Endpoints: {total_endpoints - successful_endpoints}")
    
    # Detailed breakdown by task
    print(f"\n📋 TASK-WISE READINESS STATUS:")
    
    task_mapping = {
        "🏥 System Health": "System Core",
        "📋 Tasks 1-2: Document Processing & 3-Way Matching": "Tasks 1-2",
        "📊 Task 3: Inventory Cost Analysis": "Task 3", 
        "📅 Task 4: Inventory Ageing Analysis": "Task 4",
        "💰 Task 5: FIFO Inventory Valuation": "Task 5",
        "📦 Unified Inventory Dashboard": "Inventory Hub",
        "🎯 Final Task: Profitability Analysis": "Final Task",
        "🔍 PO-Invoice Verification": "Verification"
    }
    
    for category, results in all_results.items():
        successful = sum(1 for r in results if "✅ READY" in r["status"])
        total = len(results)
        task_rate = (successful / total * 100) if total > 0 else 0
        
        status_icon = "✅" if task_rate == 100 else "⚠️" if task_rate >= 50 else "❌"
        task_name = task_mapping.get(category, category)
        
        print(f"   {status_icon} {task_name}: {successful}/{total} endpoints ({task_rate:.0f}%)")
    
    # Frontend Connection Readiness Assessment
    print(f"\n🌐 FRONTEND CONNECTION READINESS ASSESSMENT:")
    print("-" * 60)
    
    if success_rate == 100:
        print("🎉 EXCELLENT! All endpoints ready for frontend connection")
        print("✅ Backend is 100% ready for frontend integration")
        print("🚀 All 5 tasks APIs are operational and responding correctly")
    elif success_rate >= 90:
        print("✅ GOOD! Backend is ready for frontend connection")
        print("⚠️ Minor issues detected but core functionality available")
        print("🔧 Consider fixing failed endpoints before production")
    elif success_rate >= 70:
        print("⚠️ PARTIAL! Backend has core functionality but needs attention")
        print("🔧 Several endpoints require fixes before frontend connection")
        print("📋 Recommend resolving issues before proceeding")
    else:
        print("❌ NOT READY! Significant issues detected")
        print("🚨 Backend requires major fixes before frontend connection")
        print("🔧 Please resolve all critical endpoints first")
    
    # Critical Endpoints Check
    critical_endpoints = [
        "/",
        "/health", 
        "/analyze/inventory/dashboard",
        "/analyze/profitability/dashboard",
        "/api/matching/dashboard"
    ]
    
    print(f"\n🎯 CRITICAL ENDPOINTS STATUS:")
    critical_ready = 0
    
    for category, results in all_results.items():
        for result in results:
            if result["endpoint"] in critical_endpoints:
                status_icon = "✅" if "✅ READY" in result["status"] else "❌"
                print(f"   {status_icon} {result['endpoint']} - {result['status']}")
                if "✅ READY" in result["status"]:
                    critical_ready += 1
    
    critical_rate = (critical_ready / len(critical_endpoints) * 100)
    print(f"\n📊 Critical Endpoints Ready: {critical_ready}/{len(critical_endpoints)} ({critical_rate:.0f}%)")
    
    # Final Recommendation
    print(f"\n🎯 FINAL RECOMMENDATION:")
    print("-" * 40)
    
    if critical_rate == 100 and success_rate >= 90:
        print("🟢 PROCEED: Backend ready for frontend connection")
        print("✅ All critical endpoints operational")
        print("🚀 Frontend development can begin immediately")
    elif critical_rate >= 80:
        print("🟡 CAUTION: Core endpoints ready, minor fixes needed")
        print("⚠️ Frontend can connect but some features may be limited")
        print("🔧 Recommend fixing remaining issues during development")  
    else:
        print("🔴 STOP: Backend not ready for frontend connection")
        print("❌ Critical endpoints failing")
        print("🚨 Must resolve core issues before proceeding")
    
    print(f"\n⏰ Verification Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    return {
        "total_endpoints": total_endpoints,
        "successful_endpoints": successful_endpoints,
        "success_rate": success_rate,
        "critical_ready": critical_ready,
        "critical_rate": critical_rate,
        "ready_for_frontend": critical_rate == 100 and success_rate >= 90
    }

if __name__ == "__main__":
    result = verify_backend_readiness()
    
    # Exit with appropriate code
    if result["ready_for_frontend"]:
        print("\n🎉 BACKEND VERIFICATION COMPLETE - READY FOR FRONTEND! 🎉")
        exit(0)
    else:
        print("\n⚠️ BACKEND VERIFICATION COMPLETE - NEEDS ATTENTION ⚠️")
        exit(1)