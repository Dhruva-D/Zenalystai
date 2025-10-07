#!/usr/bin/env python3
"""
Debug script to test file extraction and see why zenalyst_demo_results.xlsx is not being created
"""

import sys
sys.path.append('.')

from backend.extractors.final_po_extractor import FinalPurchaseOrderParser
from backend.extractors.grn_extractor import GRNExtractor  
from backend.extractors.purchase_invoice_extractor import PurchaseInvoiceExtractor
from pathlib import Path
import pandas as pd

def debug_file_extraction():
    print("🔍 DEBUGGING FILE EXTRACTION PROCESS")
    print("=" * 50)
    
    # Check what files exist in uploads
    uploads_dir = Path("uploads")
    if uploads_dir.exists():
        sessions = list(uploads_dir.iterdir())
        print(f"📁 Found {len(sessions)} upload sessions:")
        
        for session_dir in sessions:
            if session_dir.is_dir():
                files = list(session_dir.glob("*.pdf"))
                print(f"  Session {session_dir.name}: {len(files)} PDF files")
                
                # Categorize files
                po_files = [f for f in files if f.name.upper().startswith(('PO-', 'PO_'))]
                grn_files = [f for f in files if f.name.upper().startswith(('GRN-', 'GRN_'))]
                pi_files = [f for f in files if f.name.upper().startswith(('PI-', 'PI_', 'INV-'))]
                
                print(f"    - PO files: {len(po_files)}")
                print(f"    - GRN files: {len(grn_files)}")  
                print(f"    - PI files: {len(pi_files)}")
                
                if po_files:
                    print(f"  📄 PO Files found:")
                    for po_file in po_files:
                        print(f"    - {po_file.name}")
                
                # Test extraction on most recent session
                if session_dir.name.startswith('session_') and po_files:
                    print(f"\n🧪 Testing PO extraction on session: {session_dir.name}")
                    
                    try:
                        parser = FinalPurchaseOrderParser()
                        po_df, po_items_df = parser.process_all_purchase_orders(str(session_dir))
                        
                        print(f"✅ Extraction successful!")
                        print(f"  - PO DataFrame shape: {po_df.shape}")
                        print(f"  - Items DataFrame shape: {po_items_df.shape}")
                        
                        if len(po_df) > 0:
                            print(f"  - Sample PO data:")
                            print(f"    Columns: {list(po_df.columns)}")
                            print(f"    Total amount sum: {po_df['total_amount'].sum() if 'total_amount' in po_df.columns else 'No total_amount column'}")
                            
                            # Test saving
                            print(f"\n💾 Testing save to zenalyst_demo_results.xlsx...")
                            parser.save_to_excel(po_df, po_items_df)
                            
                            # Check if file was created
                            if Path('zenalyst_demo_results.xlsx').exists():
                                print("✅ zenalyst_demo_results.xlsx created successfully!")
                                
                                # Test loading it back
                                test_po_df = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Purchase_Orders')
                                test_items_df = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Items')
                                print(f"✅ File readable - PO: {test_po_df.shape}, Items: {test_items_df.shape}")
                            else:
                                print("❌ zenalyst_demo_results.xlsx was NOT created!")
                        else:
                            print("⚠️ No PO data extracted - empty DataFrame")
                            
                    except Exception as e:
                        print(f"❌ PO extraction failed: {e}")
                        import traceback
                        traceback.print_exc()
                
                break  # Only test first session
    else:
        print("❌ No uploads directory found")
    
    print("\n" + "=" * 50)
    print("🔍 CHECKING EXPECTED FILES")
    
    # Check expected files
    expected_files = [
        'zenalyst_demo_results.xlsx',
        'reports/grn_extracted_data.xlsx',
        'reports/purchase_invoices_extracted.xlsx'
    ]
    
    for file_path in expected_files:
        path = Path(file_path)
        if path.exists():
            print(f"✅ {file_path} exists")
            try:
                if file_path == 'zenalyst_demo_results.xlsx':
                    po_df = pd.read_excel(file_path, sheet_name='Purchase_Orders')
                    items_df = pd.read_excel(file_path, sheet_name='Items')
                    print(f"    - PO records: {len(po_df)}")
                    print(f"    - Item records: {len(items_df)}")
                elif 'grn' in file_path:
                    grn_df = pd.read_excel(file_path, sheet_name='GRN_Records')
                    grn_items_df = pd.read_excel(file_path, sheet_name='Received_Items')
                    print(f"    - GRN records: {len(grn_df)}")
                    print(f"    - GRN items: {len(grn_items_df)}")
                elif 'purchase_invoices' in file_path:
                    pi_df = pd.read_excel(file_path, sheet_name='Purchase_Invoices')
                    pi_items_df = pd.read_excel(file_path, sheet_name='Billed_Items')
                    print(f"    - PI records: {len(pi_df)}")
                    print(f"    - PI items: {len(pi_items_df)}")
            except Exception as e:
                print(f"    ❌ Error reading file: {e}")
        else:
            print(f"❌ {file_path} does NOT exist")

if __name__ == "__main__":
    debug_file_extraction()