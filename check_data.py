"""
Quick test to show what happens when you run the extraction
"""
from pathlib import Path
import pandas as pd

def check_current_data():
    """Check what data we currently have"""
    
    print("🔍 CURRENT DATA STATUS")
    print("=" * 30)
    
    # Check data folder
    data_folder = Path("data/Purchase Order")
    if data_folder.exists():
        pdf_files = list(data_folder.glob("*.pdf"))
        print(f"📁 Purchase Order PDFs: {len(pdf_files)} files")
        
        # Show first few filenames
        for i, pdf_file in enumerate(pdf_files[:5], 1):
            print(f"   {i}. {pdf_file.name}")
        if len(pdf_files) > 5:
            print(f"   ... and {len(pdf_files) - 5} more files")
    else:
        print("❌ No data folder found!")
        return
    
    print()
    
    # Check if we have extracted data
    excel_file = Path("zenalyst_demo_results.xlsx")
    if excel_file.exists():
        print("📊 CURRENT EXTRACTED DATA:")
        print("-" * 25)
        
        # Read current data
        df_pos = pd.read_excel(excel_file, sheet_name='Purchase_Orders')
        df_items = pd.read_excel(excel_file, sheet_name='Items')
        
        print(f"✅ Purchase Orders: {len(df_pos)} records")
        print(f"✅ Items: {len(df_items)} records")
        print(f"✅ Total Value: ₹{df_pos['total_amount'].sum():,.2f}")
        
        print(f"\n📋 Sample extracted items:")
        for i in range(min(3, len(df_items))):
            item = df_items.iloc[i]
            print(f"   • {item['title']} (Qty: {item['quantity']}, ₹{item['amount']:,.0f})")
    else:
        print("❌ No extracted data found. Run 'python demo.py' first!")
    
    print()
    print("🔄 TO PROCESS NEW DATA:")
    print("1. Replace PDFs in 'data/Purchase Order/' folder")
    print("2. Run: python demo.py")
    print("3. New zenalyst_demo_results.xlsx will be created")

if __name__ == "__main__":
    check_current_data()