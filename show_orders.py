import pandas as pd

def show_ordered_items():
    """Display all items ordered in the purchase orders"""
    
    try:
        # Read the Excel file with extracted data
        df_items = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Items')
        df_pos = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Purchase_Orders')
        
        print('ITEMS ORDERED IN PURCHASE ORDERS')
        print('=' * 60)
        print(f'Total Items Ordered: {len(df_items)}')
        print(f'Total Purchase Orders: {len(df_pos)}')
        print()
        
        print('DETAILED LIST OF ALL ITEMS ORDERED:')
        print('-' * 60)
        
        for i, row in df_items.iterrows():
            print(f'{i+1:2d}. {row["title"]}')
            print(f'    Author: {row["author"]}')
            print(f'    Publisher: {row["publisher"]}')
            print(f'    Language: {row["language"]}')
            print(f'    Stock Code: {row["stock_code"]}')
            print(f'    Quantity Ordered: {row["quantity"]}')
            print(f'    Rate per Unit: Rs.{row["rate"]:,.2f}')
            print(f'    Total Amount: Rs.{row["amount"]:,.2f}')
            print(f'    PO Number: {row["po_number"]}')
            print(f'    Vendor: {row["vendor_name"]}')
            print(f'    Order Date: {row["po_date"]}')
            print()
        
        # Summary by categories
        print('\nSUMMARY BY CATEGORIES:')
        print('=' * 40)
        
        # Group by publisher
        publisher_summary = df_items.groupby('publisher').agg({
            'quantity': 'sum',
            'amount': 'sum',
            'title': 'count'
        }).round(2)
        publisher_summary.columns = ['Total_Qty', 'Total_Amount', 'Unique_Titles']
        publisher_summary = publisher_summary.sort_values('Total_Amount', ascending=False)
        
        print('\nBY PUBLISHER:')
        print(publisher_summary.to_string())
        
        # Group by vendor
        vendor_summary = df_items.groupby('vendor_name').agg({
            'quantity': 'sum',
            'amount': 'sum',
            'title': 'count'
        }).round(2)
        vendor_summary.columns = ['Total_Qty', 'Total_Amount', 'Unique_Titles']
        vendor_summary = vendor_summary.sort_values('Total_Amount', ascending=False)
        
        print('\nBY VENDOR:')
        print(vendor_summary.to_string())
        
        # Top items by value
        print('\nTOP 10 HIGHEST VALUE ITEMS:')
        print('-' * 30)
        top_items = df_items.nlargest(10, 'amount')
        for i, row in top_items.iterrows():
            print(f'{row["title"]} - Rs.{row["amount"]:,.2f} (Qty: {row["quantity"]})')
        
        # Total quantities and values
        print(f'\nOVERALL SUMMARY:')
        print('=' * 20)
        print(f'Total Books Ordered: {df_items["quantity"].sum():,}')
        print(f'Total Order Value: Rs.{df_items["amount"].sum():,.2f}')
        print(f'Average Item Value: Rs.{df_items["amount"].mean():,.2f}')
        print(f'Unique Titles: {df_items["title"].nunique()}')
        print(f'Unique Publishers: {df_items["publisher"].nunique()}')
        print(f'Unique Vendors: {df_items["vendor_name"].nunique()}')
        
    except FileNotFoundError:
        print("Excel file not found. Please run the demo first: python demo.py")
    except Exception as e:
        print(f"Error reading data: {e}")

if __name__ == "__main__":
    show_ordered_items()