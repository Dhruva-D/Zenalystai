from matching_engine import ThreeWayMatchingEngine
from datetime import datetime

def test_matching_engine():
    """Test the 3-way matching engine"""
    print("🔄 Testing 3-Way Matching Engine...")
    print("=" * 60)
    
    # Initialize engine
    engine = ThreeWayMatchingEngine()
    
    # Run analysis
    start_time = datetime.now()
    result = engine.analyze_three_way_matching()
    end_time = datetime.now()
    
    processing_time = (end_time - start_time).total_seconds()
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    # Display results
    dashboard = result['dashboard']
    matching_results = result['matching_results']
    exceptions = result['exceptions']
    vendor_performance = result['vendor_performance']
    
    print(f"✅ Analysis completed in {processing_time:.2f} seconds")
    print(f"\n📊 DASHBOARD SUMMARY:")
    print(f"   Total POs: {dashboard.total_pos}")
    print(f"   Fully Matched: {dashboard.fully_matched}")
    print(f"   Pending GRNs: {dashboard.pending_grns}")
    print(f"   Pending Invoices: {dashboard.pending_invoices}")
    print(f"   Total Exceptions: {dashboard.exceptions}")
    print(f"   Match Rate: {dashboard.match_rate:.1f}%")
    
    print(f"\n💰 FINANCIAL SUMMARY:")
    print(f"   Total PO Value: ₹{dashboard.total_po_value:,.2f}")
    print(f"   Total GRN Value: ₹{dashboard.total_grn_value:,.2f}")
    print(f"   Total Invoice Value: ₹{dashboard.total_invoice_value:,.2f}")
    print(f"   Total Variance: ₹{dashboard.total_variance:,.2f}")
    
    print(f"\n⚠️  EXCEPTION BREAKDOWN:")
    print(f"   Critical: {dashboard.critical_exceptions}")
    print(f"   High: {dashboard.high_exceptions}")
    print(f"   Medium: {dashboard.medium_exceptions}")
    print(f"   Low: {dashboard.low_exceptions}")
    
    print(f"\n🏢 VENDOR PERFORMANCE:")
    print(f"   Total Vendors: {len(vendor_performance)}")
    if vendor_performance:
        top_vendor = vendor_performance[0]
        print(f"   Top Performer: {top_vendor.vendor_name}")
        print(f"   Compliance Score: {top_vendor.compliance_score}")
        print(f"   Match Rate: {top_vendor.match_rate:.1f}%")
    
    # Sample matching results
    print(f"\n📋 SAMPLE MATCHING RESULTS (First 5):")
    for i, result in enumerate(matching_results[:5]):
        print(f"   {i+1}. PO-{result.po_number}: {result.status.value} (Score: {result.match_score:.1f})")
    
    # Sample exceptions
    print(f"\n🚨 SAMPLE EXCEPTIONS (First 3):")
    for i, exc in enumerate(exceptions[:3]):
        print(f"   {i+1}. {exc.exception_type} - {exc.severity.value.upper()}: {exc.description}")
    
    print(f"\n✅ 3-Way Matching Engine test completed successfully!")
    return True

if __name__ == "__main__":
    test_matching_engine()