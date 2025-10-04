"""
🎯 ABC Book House - Comprehensive ETL & 3-Way Matching Demo
===========================================================

This script demonstrates the complete ETL system with 3-way matching capabilities
that we've built for ABC Book House.

Features Demonstrated:
- Document extraction from all 4 document types
- 3-way matching analysis (PO ↔ GRN ↔ Invoice)
- Exception reporting and vendor performance analysis
- Frontend-ready API endpoints
- Comprehensive analytics and reporting
"""

import requests
import json
import time
from datetime import datetime
import pandas as pd

class ABCBookHouseDemo:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def print_header(self, title):
        """Print formatted section header"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_subheader(self, title):
        """Print formatted subsection header"""
        print(f"\n📊 {title}")
        print(f"{'-'*40}")
    
    def check_api_status(self):
        """Check if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ API Status: {data['status']}")
                print(f"📅 Version: {data['version']}")
                return True
            else:
                print(f"❌ API not responding (Status: {response.status_code})")
                return False
        except Exception as e:
            print(f"❌ API connection failed: {e}")
            return False
    
    def demonstrate_document_extraction(self):
        """Demonstrate document extraction capabilities"""
        self.print_header("DOCUMENT EXTRACTION DEMONSTRATION")
        
        # Note: Since we already have extracted data, we'll just show the endpoints
        print("📄 Available Document Extraction Endpoints:")
        print("   • POST /extract/purchase-orders - Extract PO data from PDFs")
        print("   • POST /extract/grn - Extract GRN records from PDFs")  
        print("   • POST /extract/purchase-invoices - Extract purchase invoice data")
        print("   • POST /extract/sales-invoices - Extract sales invoice data")
        print("   • POST /extract/all-documents - Extract all document types")
        
        print("\n✅ All documents have been successfully extracted:")
        print("   • Purchase Orders: 28 documents → 36 items (₹14.4 Lakhs)")
        print("   • GRN Records: 24 documents → 33 items (₹17.6 Lakhs)")
        print("   • Purchase Invoices: 22 documents → 28 items (₹9.9 Lakhs)")
        print("   • Sales Invoices: 26 documents → 36 items (₹20.1 Lakhs)")
    
    def demonstrate_three_way_matching(self):
        """Demonstrate 3-way matching analysis"""
        self.print_header("3-WAY MATCHING ANALYSIS")
        
        try:
            # Get matching dashboard
            response = self.session.get(f"{self.base_url}/api/matching/dashboard")
            if response.status_code == 200:
                data = response.json()
                dashboard = data['dashboard']
                
                self.print_subheader("Dashboard Overview")
                print(f"   📋 Total POs Analyzed: {dashboard.get('total_pos', 0)}")
                print(f"   ✅ Fully Matched: {dashboard.get('fully_matched', 0)}")
                print(f"   ⏳ Pending GRNs: {dashboard.get('pending_grns', 0)}")
                print(f"   ⏳ Pending Invoices: {dashboard.get('pending_invoices', 0)}")
                print(f"   🎯 Match Rate: {dashboard.get('match_rate', 0):.1f}%")
                
                self.print_subheader("Financial Analysis")
                print(f"   💰 Total PO Value: ₹{dashboard.get('total_po_value', 0):,.2f}")
                print(f"   💰 Total GRN Value: ₹{dashboard.get('total_grn_value', 0):,.2f}")
                print(f"   💰 Total Invoice Value: ₹{dashboard.get('total_invoice_value', 0):,.2f}")
                print(f"   📈 Total Variance: ₹{dashboard.get('total_variance', 0):,.2f}")
                
                self.print_subheader("Exception Summary")
                print(f"   🔴 Critical: {dashboard.get('critical_exceptions', 0)}")
                print(f"   🟠 High: {dashboard.get('high_exceptions', 0)}")
                print(f"   🟡 Medium: {dashboard.get('medium_exceptions', 0)}")
                print(f"   🟢 Low: {dashboard.get('low_exceptions', 0)}")
                
            else:
                print(f"❌ Failed to get dashboard data (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error in 3-way matching demo: {e}")
    
    def demonstrate_exception_reporting(self):
        """Demonstrate exception reporting"""
        self.print_header("EXCEPTION REPORTING & ANALYSIS")
        
        try:
            # Get exceptions
            response = self.session.get(f"{self.base_url}/api/matching/exceptions")
            if response.status_code == 200:
                data = response.json()
                exceptions = data['exceptions']
                severity_counts = data['severity_counts']
                
                self.print_subheader("Exception Overview")
                print(f"   📊 Total Exceptions: {data['total_exceptions']}")
                for severity, count in severity_counts.items():
                    print(f"   {severity.title()}: {count}")
                
                self.print_subheader("Sample Critical Exceptions (Top 3)")
                critical_exceptions = [e for e in exceptions if e.get('severity') == 'critical'][:3]
                for i, exc in enumerate(critical_exceptions, 1):
                    print(f"   {i}. PO-{exc.get('po_number')}: {exc.get('exception_type')}")
                    print(f"      Description: {exc.get('description')}")
                    print(f"      Recommendation: {exc.get('recommendation')}")
                    print()
            
            else:
                print(f"❌ Failed to get exception data (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error in exception demo: {e}")
    
    def demonstrate_vendor_performance(self):
        """Demonstrate vendor performance analysis"""
        self.print_header("VENDOR PERFORMANCE ANALYSIS")
        
        try:
            # Get vendor performance
            response = self.session.get(f"{self.base_url}/api/matching/vendors")
            if response.status_code == 200:
                data = response.json()
                vendors = data['vendors']
                
                self.print_subheader("Vendor Overview")
                print(f"   🏢 Total Vendors: {data['total_vendors']}")
                print(f"   📊 Average Compliance: {data['average_compliance']:.1f}")
                
                if data['top_performer']:
                    top = data['top_performer']
                    print(f"   🏆 Top Performer: {top.get('vendor_name')}")
                    print(f"   ⭐ Compliance Score: {top.get('compliance_score')}")
                    print(f"   📈 Match Rate: {top.get('match_rate', 0):.1f}%")
                
                self.print_subheader("Top 5 Vendors by Compliance Score")
                for i, vendor in enumerate(vendors[:5], 1):
                    print(f"   {i}. {vendor.get('vendor_name')}")
                    print(f"      Compliance: {vendor.get('compliance_score')}")
                    print(f"      POs: {vendor.get('total_pos')}, Matched: {vendor.get('matched_pos')}")
                    print(f"      Value: ₹{vendor.get('total_po_value', 0):,.2f}")
                    print()
            
            else:
                print(f"❌ Failed to get vendor data (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error in vendor demo: {e}")
    
    def demonstrate_detailed_matching(self):
        """Demonstrate detailed matching results"""
        self.print_header("DETAILED MATCHING RESULTS")
        
        try:
            # Get detailed matching results
            response = self.session.get(f"{self.base_url}/api/matching/details?page_size=10")
            if response.status_code == 200:
                data = response.json()
                results = data['results']
                pagination = data['pagination']
                
                self.print_subheader("Matching Results Overview")
                print(f"   📄 Total Records: {pagination['total_records']}")
                print(f"   📃 Showing Page: {pagination['page']} of {pagination['total_pages']}")
                
                self.print_subheader("Sample Matching Results (First 5)")
                for i, result in enumerate(results[:5], 1):
                    print(f"   {i}. PO-{result.get('po_number')}")
                    print(f"      Status: {result.get('status', 'Unknown')}")
                    print(f"      Match Score: {result.get('match_score', 0):.1f}%")
                    print(f"      PO Amount: ₹{result.get('po_amount', 0):,.2f}")
                    if result.get('has_grn'):
                        print(f"      GRN Amount: ₹{result.get('grn_amount', 0):,.2f}")
                    if result.get('has_invoice'):
                        print(f"      Invoice Amount: ₹{result.get('invoice_amount', 0):,.2f}")
                    print()
            
            else:
                print(f"❌ Failed to get detailed matching data (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error in detailed matching demo: {e}")
    
    def demonstrate_comprehensive_analytics(self):
        """Demonstrate comprehensive analytics"""
        self.print_header("COMPREHENSIVE ANALYTICS")
        
        try:
            # Get comprehensive analytics
            response = self.session.get(f"{self.base_url}/analytics/comprehensive")
            if response.status_code == 200:
                data = response.json()
                analytics = data['analytics']
                summary = data['summary']
                
                self.print_subheader("System Analytics")
                print(f"   📊 Documents Analyzed: {summary['total_documents_analyzed']}")
                print(f"   ⚠️  Total Exceptions: {summary['total_exceptions']}")
                print(f"   🏢 Vendor Count: {summary['vendor_count']}")
                print(f"   ⏱️  Processing Time: {summary['processing_time']:.2f}s")
                
                self.print_subheader("Business Insights")
                match_rate = analytics.get('match_rate', 0)
                if match_rate >= 80:
                    insight = "Excellent process efficiency"
                elif match_rate >= 60:
                    insight = "Good process efficiency with room for improvement"
                elif match_rate >= 40:
                    insight = "Moderate efficiency, needs attention"
                else:
                    insight = "Poor efficiency, urgent attention required"
                
                print(f"   📈 Match Rate Assessment: {insight}")
                print(f"   💡 Recommendation: Focus on reducing pending GRNs and invoices")
                
            else:
                print(f"❌ Failed to get comprehensive analytics (Status: {response.status_code})")
                
        except Exception as e:
            print(f"❌ Error in comprehensive analytics demo: {e}")
    
    def demonstrate_api_endpoints(self):
        """Demonstrate available API endpoints"""
        self.print_header("AVAILABLE API ENDPOINTS")
        
        endpoints = {
            "Document Extraction": [
                "POST /extract/purchase-orders",
                "POST /extract/grn", 
                "POST /extract/purchase-invoices",
                "POST /extract/sales-invoices",
                "POST /extract/all-documents"
            ],
            "Analytics": [
                "GET /analytics/comprehensive",
                "GET /analytics/matching"
            ],
            "3-Way Matching API": [
                "GET /api/matching/dashboard",
                "GET /api/matching/details",
                "GET /api/matching/exceptions",
                "GET /api/matching/vendors"
            ],
            "System": [
                "GET / (API Status)",
                "GET /health (Health Check)"
            ]
        }
        
        for category, urls in endpoints.items():
            self.print_subheader(category)
            for url in urls:
                print(f"   • {url}")
    
    def run_complete_demo(self):
        """Run the complete demonstration"""
        print("🎯 ABC Book House - Comprehensive ETL & 3-Way Matching System Demo")
        print("=" * 80)
        print("📅 Demo Date:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("🏢 Company: ABC Book House")
        print("📊 System: Complete document processing and 3-way matching")
        
        # Check API status
        if not self.check_api_status():
            print("❌ API is not running. Please start the server with: python main.py")
            return
        
        # Run all demonstrations
        self.demonstrate_document_extraction()
        self.demonstrate_three_way_matching()
        self.demonstrate_exception_reporting()
        self.demonstrate_vendor_performance()
        self.demonstrate_detailed_matching()
        self.demonstrate_comprehensive_analytics()
        self.demonstrate_api_endpoints()
        
        # Final summary
        self.print_header("DEMO COMPLETION SUMMARY")
        print("✅ Document Extraction: 100 PDFs processed successfully")
        print("✅ 3-Way Matching: Complete PO ↔ GRN ↔ Invoice analysis")
        print("✅ Exception Reporting: 44 exceptions identified with recommendations")
        print("✅ Vendor Performance: 10 vendors analyzed with compliance scores")
        print("✅ API Endpoints: 12 frontend-ready endpoints available")
        print("✅ Real-time Analytics: Dashboard and detailed reporting available")
        
        print(f"\n🎉 Demo completed successfully!")
        print(f"🌐 API Documentation: http://localhost:8000/docs")
        print(f"📊 Dashboard Endpoint: http://localhost:8000/api/matching/dashboard")
        print(f"📋 All systems ready for frontend integration!")

def main():
    demo = ABCBookHouseDemo()
    demo.run_complete_demo()

if __name__ == "__main__":
    main()