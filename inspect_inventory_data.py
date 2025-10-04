#!/usr/bin/env python3
"""
Quick data inspection script to check column names in inventory register
"""
import pandas as pd

def inspect_data():
    try:
        # Load the inventory register
        df = pd.read_excel("data/ABC_Book_Stores_Inventory_Register.xlsx", sheet_name='Inventory Register')
        
        print("📊 INVENTORY DATA INSPECTION")
        print("=" * 50)
        print(f"📈 Total Records: {len(df)}")
        print(f"📋 Total Columns: {len(df.columns)}")
        
        print(f"\n📝 COLUMN NAMES:")
        for i, col in enumerate(df.columns, 1):
            print(f"   {i:2d}. {col}")
        
        print(f"\n🔍 SAMPLE DATA (First 3 rows):")
        print(df.head(3).to_string())
        
        # Check for key columns we need
        key_columns = ['Product Name', 'Category', 'Opening Stock', 'Purchase Rate', 'Selling Price']
        print(f"\n🎯 KEY COLUMN AVAILABILITY:")
        for col in key_columns:
            if col in df.columns:
                print(f"   ✅ {col} - Found")
            else:
                # Try to find similar column names
                similar = [c for c in df.columns if col.lower().replace(' ', '') in c.lower().replace(' ', '')]
                if similar:
                    print(f"   ⚠️  {col} - Not found, but similar: {similar}")
                else:
                    print(f"   ❌ {col} - Missing")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_data()