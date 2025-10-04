"""
Zenalyst AI - ETL Analysis Demo
===============================

This script demonstrates the current capabilities of the ETL analysis platform
for Purchase Order processing without requiring the API server.
"""

import pandas as pd
from final_po_extractor import FinalPurchaseOrderParser
import json
from pathlib import Path

def demo_etl_analysis():
    """Demonstrate the complete ETL analysis workflow"""
    
    print("🚀 ZENALYST AI - ETL ANALYSIS DEMO")
    print("=" * 50)
    
    # Initialize the parser
    parser = FinalPurchaseOrderParser()
    
    # Check if data folder exists
    data_folder = Path("data/Purchase Order")
    if not data_folder.exists():
        print("❌ Data folder not found. Please ensure 'data/Purchase Order' folder exists.")
        return
    
    print(f"📁 Found data folder: {data_folder}")
    pdf_files = list(data_folder.glob("*.pdf"))
    print(f"📄 Found {len(pdf_files)} PDF files to process")
    
    print("\n🔄 PROCESSING PURCHASE ORDERS...")
    print("-" * 30)
    
    # Process all purchase orders
    po_df, items_df = parser.process_all_purchase_orders("data/Purchase Order")
    
    print(f"\n✅ EXTRACTION COMPLETE!")
    print(f"📊 Results:")
    print(f"   • Purchase Orders: {len(po_df)}")
    print(f"   • Items Extracted: {len(items_df)}")
    
    if len(po_df) == 0:
        print("❌ No data extracted. Please check the PDF files.")
        return
    
    # Save to Excel
    excel_filename = "zenalyst_demo_results.xlsx"
    parser.save_to_excel(po_df, items_df, excel_filename)
    print(f"💾 Data saved to: {excel_filename}")
    
    # Display analytics
    print(f"\n📈 ANALYTICS SUMMARY")
    print("=" * 30)
    
    # Basic metrics
    total_value = po_df['total_amount'].sum()
    avg_value = po_df['total_amount'].mean()
    unique_vendors = po_df['vendor_name'].nunique()
    
    print(f"💰 Financial Metrics:")
    print(f"   • Total PO Value: ₹{total_value:,.2f}")
    print(f"   • Average PO Value: ₹{avg_value:,.2f}")
    print(f"   • Min PO Value: ₹{po_df['total_amount'].min():,.2f}")
    print(f"   • Max PO Value: ₹{po_df['total_amount'].max():,.2f}")
    
    print(f"\n🏢 Vendor Analysis:")
    print(f"   • Unique Vendors: {unique_vendors}")
    vendor_counts = po_df['vendor_name'].value_counts()
    print(f"   • Top 5 Vendors by PO Count:")
    for i, (vendor, count) in enumerate(vendor_counts.head().items(), 1):
        print(f"     {i}. {vendor}: {count} POs")
    
    # Date analysis
    if po_df['po_date'].notna().any():
        print(f"\n📅 Date Range:")
        print(f"   • From: {po_df['po_date'].min()}")
        print(f"   • To: {po_df['po_date'].max()}")
    
    # Item analysis
    if len(items_df) > 0:
        print(f"\n📚 Item Analysis:")
        print(f"   • Total Items: {len(items_df)}")
        print(f"   • Total Quantity: {items_df['quantity'].sum():,}")
        print(f"   • Average Item Value: ₹{items_df['amount'].mean():,.2f}")
        
        # Top items by value
        top_items = items_df.nlargest(5, 'amount')
        print(f"   • Top 5 Items by Value:")
        for i, (_, item) in enumerate(top_items.iterrows(), 1):
            print(f"     {i}. {item['title']} - ₹{item['amount']:,.2f}")
        
        # Publisher analysis
        publisher_counts = items_df['publisher'].value_counts()
        print(f"   • Top 5 Publishers:")
        for i, (publisher, count) in enumerate(publisher_counts.head().items(), 1):
            print(f"     {i}. {publisher}: {count} items")
    
    # Sample data preview
    print(f"\n📋 SAMPLE DATA PREVIEW")
    print("-" * 30)
    
    print(f"\n🧾 Sample Purchase Order:")
    sample_po = po_df.iloc[0]
    print(f"   • PO Number: {sample_po['po_number']}")
    print(f"   • Date: {sample_po['po_date']}")
    print(f"   • Vendor: {sample_po['vendor_name']}")
    print(f"   • Amount: ₹{sample_po['total_amount']:,.2f}")
    
    if len(items_df) > 0:
        print(f"\n📖 Sample Item:")
        sample_item = items_df.iloc[0]
        print(f"   • Title: {sample_item['title']}")
        print(f"   • Author: {sample_item['author']}")
        print(f"   • Publisher: {sample_item['publisher']}")
        print(f"   • Quantity: {sample_item['quantity']}")
        print(f"   • Rate: ₹{sample_item['rate']:,.2f}")
        print(f"   • Amount: ₹{sample_item['amount']:,.2f}")
    
    # Next steps
    print(f"\n🎯 NEXT STEPS FOR COMPLETE ETL ANALYSIS")
    print("=" * 45)
    print("Phase 2 - Expand Document Processing:")
    print("  ☐ Purchase Invoice PDF extraction")
    print("  ☐ GRN (Goods Receipt Note) processing")
    print("  ☐ Sales Invoice analysis")
    print("  ☐ Excel inventory register integration")
    
    print("\nPhase 3 - Advanced Analytics:")
    print("  ☐ 3-Way Match (PO vs Invoice vs GRN)")
    print("  ☐ Excess/Short Procurement analysis")
    print("  ☐ Inventory aging and dead stock identification")
    print("  ☐ Profitability analysis by vendor/category")
    print("  ☐ Gross margin analysis and negative margin detection")
    
    print(f"\n✨ DEMO COMPLETE!")
    print(f"📁 Check '{excel_filename}' for detailed results")
    print("🌐 For API access, run: uvicorn main:app --reload")
    print("📖 API docs will be available at: http://localhost:8000/docs")

if __name__ == "__main__":
    demo_etl_analysis()