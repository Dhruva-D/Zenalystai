#!/usr/bin/env python3
"""
Test the complete upload and analysis workflow to ensure everything works end-to-end
"""

import sys
sys.path.append('.')

from backend.extractors.final_po_extractor import FinalPurchaseOrderParser
from backend.extractors.grn_extractor import GRNExtractor  
from backend.extractors.purchase_invoice_extractor import PurchaseInvoiceExtractor
from backend.api.matching_engine import ThreeWayMatchingEngine
from pathlib import Path
import pandas as pd
import shutil
import tempfile

def test_complete_workflow():
    print("🧪 TESTING COMPLETE UPLOAD & ANALYSIS WORKFLOW")
    print("=" * 60)
    
    # Use the actual session with files
    session_dir = Path("uploads/session_20251007_170234_0")
    
    if not session_dir.exists():
        print("❌ Session directory not found")
        return
    
    # Get all PDF files and categorize them
    pdf_files = list(session_dir.glob("*.pdf"))
    po_files = [f for f in pdf_files if f.name.upper().startswith(('PO-', 'PO_'))]
    grn_files = [f for f in pdf_files if f.name.upper().startswith(('GRN-', 'GRN_'))]
    pi_files = [f for f in pdf_files if f.name.upper().startswith(('PI-', 'PI_', 'INV-', 'INVOICE-'))]
    
    print(f"📁 File categorization from {len(pdf_files)} total PDFs:")
    print(f"  - Purchase Orders: {len(po_files)} files")
    print(f"  - GRN Records: {len(grn_files)} files")
    print(f"  - Purchase Invoices: {len(pi_files)} files")
    
    # Test 1: Process PO files only
    print(f"\n🔄 STEP 1: Processing Purchase Orders")
    try:
        if po_files:
            # Create temp directory with only PO files
            with tempfile.TemporaryDirectory() as temp_po_dir:
                print(f"📁 Created temp directory: {temp_po_dir}")
                
                # Copy only PO files
                for po_file in po_files:
                    dst_path = Path(temp_po_dir) / po_file.name
                    shutil.copy2(po_file, dst_path)
                    print(f"  📄 Copied: {po_file.name}")
                
                # Extract PO data
                parser = FinalPurchaseOrderParser()
                po_df, po_items_df = parser.process_all_purchase_orders(temp_po_dir)
                
                print(f"✅ PO Extraction: {len(po_df)} orders, {len(po_items_df)} items")
                
                # Save to expected location
                parser.save_to_excel(po_df, po_items_df, "zenalyst_demo_results.xlsx")
                print(f"💾 Saved to zenalyst_demo_results.xlsx")
        else:
            print("⚠️ No PO files found")
    except Exception as e:
        print(f"❌ PO processing failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Process GRN files only  
    print(f"\n🔄 STEP 2: Processing GRN Records")
    try:
        if grn_files:
            with tempfile.TemporaryDirectory() as temp_grn_dir:
                print(f"📁 Created temp directory: {temp_grn_dir}")
                
                # Copy only GRN files
                for grn_file in grn_files:
                    dst_path = Path(temp_grn_dir) / grn_file.name
                    shutil.copy2(grn_file, dst_path)
                    print(f"  📄 Copied: {grn_file.name}")
                
                # Extract GRN data
                grn_extractor = GRNExtractor()
                grn_df, grn_items_df = grn_extractor.process_all_grns(temp_grn_dir)
                
                print(f"✅ GRN Extraction: {len(grn_df)} records, {len(grn_items_df)} items")
                
                # Save to expected location
                grn_extractor.save_to_excel(grn_df, grn_items_df)
                print(f"💾 Saved to reports/grn_extracted_data.xlsx")
        else:
            print("⚠️ No GRN files found")
    except Exception as e:
        print(f"❌ GRN processing failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 3: Process PI files only
    print(f"\n🔄 STEP 3: Processing Purchase Invoices")
    try:
        if pi_files:
            with tempfile.TemporaryDirectory() as temp_pi_dir:
                print(f"📁 Created temp directory: {temp_pi_dir}")
                
                # Copy only PI files
                for pi_file in pi_files:
                    dst_path = Path(temp_pi_dir) / pi_file.name
                    shutil.copy2(pi_file, dst_path)
                    print(f"  📄 Copied: {pi_file.name}")
                
                # Extract PI data
                pi_extractor = PurchaseInvoiceExtractor()
                pi_df, pi_items_df = pi_extractor.process_all_invoices(temp_pi_dir)
                
                print(f"✅ PI Extraction: {len(pi_df)} invoices, {len(pi_items_df)} items")
                
                # Save to expected location
                pi_extractor.save_to_excel(pi_df, pi_items_df)
                print(f"💾 Saved to reports/purchase_invoices_extracted.xlsx")
        else:
            print("⚠️ No PI files found")
    except Exception as e:
        print(f"❌ PI processing failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 4: Verify file creation
    print(f"\n🔄 STEP 4: Verifying File Creation")
    expected_files = [
        'zenalyst_demo_results.xlsx',
        'reports/grn_extracted_data.xlsx', 
        'reports/purchase_invoices_extracted.xlsx'
    ]
    
    all_files_exist = True
    for file_path in expected_files:
        exists = Path(file_path).exists()
        print(f"  {'✅' if exists else '❌'} {file_path}")
        if not exists:
            all_files_exist = False
    
    # Test 5: Test 3-way matching
    print(f"\n🔄 STEP 5: Testing 3-Way Matching Engine")
    if all_files_exist:
        try:
            engine = ThreeWayMatchingEngine()
            success = engine.load_data()
            
            print(f"Data loading: {'✅ Success' if success else '❌ Failed'}")
            
            if success:
                print(f"  📊 Data loaded:")
                print(f"    - PO Records: {len(engine.po_df)}")
                print(f"    - PO Items: {len(engine.po_items_df)}")
                print(f"    - GRN Records: {len(engine.grn_df)}")
                print(f"    - GRN Items: {len(engine.grn_items_df)}")
                print(f"    - PI Records: {len(engine.pi_df)}")
                print(f"    - PI Items: {len(engine.pi_items_df)}")
                
                print(f"\n  🔄 Running 3-way matching analysis...")
                result = engine.analyze_three_way_matching()
                
                if 'error' in result:
                    print(f"  ❌ Analysis error: {result['error']}")
                else:
                    print(f"  ✅ Analysis successful!")
                    dashboard = result['dashboard']
                    print(f"    📈 Results:")
                    print(f"      - Total POs: {dashboard.total_pos}")
                    print(f"      - Fully Matched: {dashboard.fully_matched}")
                    print(f"      - Partial Matches: {dashboard.partial_matches}")
                    print(f"      - Total PO Value: ₹{dashboard.total_po_value:,.2f}")
                    print(f"      - Total GRN Value: ₹{dashboard.total_grn_value:,.2f}")
                    print(f"      - Total Invoice Value: ₹{dashboard.total_invoice_value:,.2f}")
                    print(f"      - Match Rate: {dashboard.match_rate:.1f}%")
        except Exception as e:
            print(f"  ❌ Matching engine error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("  ⚠️ Skipping matching test - required files missing")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 WORKFLOW TEST COMPLETE")

if __name__ == "__main__":
    test_complete_workflow()