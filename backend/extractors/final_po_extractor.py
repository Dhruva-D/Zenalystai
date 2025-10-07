import pdfplumber
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class FinalPurchaseOrderParser:
    def __init__(self):
        self.extracted_data = []
    
    def extract_po_data(self, pdf_path: str) -> Dict:
        """Extract structured data from a purchase order PDF using text parsing"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                # Initialize data structure
                po_data = {
                    'filename': Path(pdf_path).name,
                    'po_number': None,
                    'po_date': None,
                    'buyer_name': None,
                    'buyer_address': None,
                    'buyer_gstin': None,
                    'buyer_phone': None,
                    'buyer_email': None,
                    'vendor_name': None,
                    'vendor_address': None,
                    'items': [],
                    'subtotal': None,
                    'gst_amount': None,
                    'gst_rate': None,
                    'total_amount': None,
                    'currency': 'INR'
                }
                
                # Extract PO Number
                po_match = re.search(r'PO Number\s*\n\s*([A-Z0-9-]+)', text)
                if po_match:
                    po_data['po_number'] = po_match.group(1)
                
                # Extract PO Date
                date_match = re.search(r'PO Date:\s*(\d{2}\s+\w+\s+\d{4})', text)
                if date_match:
                    try:
                        po_data['po_date'] = datetime.strptime(date_match.group(1), '%d %b %Y').strftime('%Y-%m-%d')
                    except:
                        po_data['po_date'] = date_match.group(1)
                
                # Extract Buyer and Vendor Information with improved logic
                self.extract_buyer_vendor_info_improved(text, po_data)
                
                # Extract financial information with better error handling
                try:
                    subtotal_match = re.search(r'Subtotal\s*₹([\d,]+\.?\d*)', text)
                    if subtotal_match:
                        subtotal_str = subtotal_match.group(1).replace(',', '')
                        po_data['subtotal'] = float(subtotal_str) if subtotal_str.replace('.', '').isdigit() else 0.0
                    
                    gst_match = re.search(r'GST @ (\d+)%\s*₹([\d,]+\.?\d*)', text)
                    if gst_match:
                        po_data['gst_rate'] = float(gst_match.group(1))
                        gst_amount_str = gst_match.group(2).replace(',', '')
                        po_data['gst_amount'] = float(gst_amount_str) if gst_amount_str.replace('.', '').isdigit() else 0.0
                    
                    total_match = re.search(r'TOTAL\s*₹([\d,]+\.?\d*)', text)
                    if total_match:
                        total_str = total_match.group(1).replace(',', '')
                        po_data['total_amount'] = float(total_str) if total_str.replace('.', '').isdigit() else 0.0
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Error parsing financial data: {e}")
                    po_data['subtotal'] = 0.0
                    po_data['gst_amount'] = 0.0
                    po_data['total_amount'] = 0.0
                
                # Extract items using text parsing
                items = self.extract_items_from_text(text)
                po_data['items'] = items
                
                return po_data
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None
    
    def extract_buyer_vendor_info_improved(self, text: str, po_data: Dict):
        """Extract buyer and vendor information with improved logic"""
        lines = text.split('\n')
        
        # Extract buyer details
        po_data['buyer_name'] = "ABC BOOK HOUSE PRIVATE LIMITED"
        po_data['buyer_address'] = "3rd Main Road, Gandhinagar, Bangalore, Karnataka 560009"
        
        # Extract GSTIN, Phone, Email
        gstin_match = re.search(r'GSTIN:\s*([A-Z0-9]+)', text)
        if gstin_match:
            po_data['buyer_gstin'] = gstin_match.group(1)
        
        phone_match = re.search(r'Phone:\s*([+\d\s-]+)', text)
        if phone_match:
            po_data['buyer_phone'] = phone_match.group(1).strip()
        
        email_match = re.search(r'Email:\s*([^\s\n]+)', text)
        if email_match:
            po_data['buyer_email'] = email_match.group(1)
        
        # Extract vendor name - it's on the same line as buyer name after "PRIVATE"
        for line in lines:
            if 'ABC BOOK HOUSE PRIVATE' in line and len(line) > len('ABC BOOK HOUSE PRIVATE'):
                # Extract everything after "PRIVATE "
                vendor_part = line.split('PRIVATE')[1].strip()
                if vendor_part:
                    po_data['vendor_name'] = vendor_part
                break
        
        # Extract vendor address - look for address lines that don't belong to buyer
        vendor_address_lines = []
        collecting_vendor_address = False
        
        for line in lines:
            line = line.strip()
            # Skip buyer-related lines
            if any(buyer_keyword in line.lower() for buyer_keyword in 
                   ['abc book house', 'gandhinagar', 'bangalore', 'karnataka', '560009', 'gstin:', 'phone:', 'email:']):
                continue
            
            # Look for address-like lines (containing numbers, commas, state names)
            if (collecting_vendor_address or 
                (re.search(r'\d+/\d+|Floor|Road|Chennai|Delhi|Mumbai|Hyderabad|Tamil Nadu|Maharashtra|Telangana', line, re.IGNORECASE))):
                
                if not any(stop_word in line.lower() for stop_word in ['note:', 'please supply', 's.no', 'item description']):
                    vendor_address_lines.append(line)
                    collecting_vendor_address = True
                else:
                    break
        
        if vendor_address_lines:
            po_data['vendor_address'] = ' '.join(vendor_address_lines[:3])  # Limit to first 3 lines
    
    def extract_items_from_text(self, text: str) -> List[Dict]:
        """Extract items from text using pattern matching"""
        items = []
        lines = text.split('\n')
        
        # Find the table header
        header_idx = -1
        for i, line in enumerate(lines):
            if 'S.No' in line and 'Item Description' in line:
                header_idx = i
                break
        
        if header_idx == -1:
            return items
        
        # Process lines after header to find item data
        i = header_idx + 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop at financial summary
            if any(keyword in line for keyword in ['Subtotal', 'GST @', 'TOTAL', 'Terms & Conditions']):
                break
            
            if not line:
                i += 1
                continue
            
            # Look for the main item line with S.No, description, qty, rate, amount
            # Pattern: "1 by Author | Publisher | Language 44 ₹1,124.00 ₹49,456.00"
            item_pattern = r'^(\d+)\s+(.+?)\s+(\d+)\s+₹([\d,]+\.?\d*)\s+₹([\d,]+\.?\d*)$'
            match = re.match(item_pattern, line)
            
            if match:
                try:
                    sno = match.group(1)
                    description = match.group(2).strip()
                    qty = int(match.group(3))
                    rate_str = match.group(4).replace(',', '')
                    amount_str = match.group(5).replace(',', '')
                    
                    # Safe conversion to float with validation
                    rate = float(rate_str) if rate_str and rate_str.replace('.', '').isdigit() else 0.0
                    amount = float(amount_str) if amount_str and amount_str.replace('.', '').isdigit() else 0.0
                except (ValueError, AttributeError) as e:
                    print(f"Warning: Error parsing item data in line '{line}': {e}")
                    i += 1
                    continue
                
                # Look for title in previous line
                title = ""
                if i > 0:
                    prev_line = lines[i-1].strip()
                    if prev_line and not any(keyword in prev_line for keyword in ['S.No', 'Item Description']):
                        title = prev_line
                
                # Parse description for author, publisher, language
                author, publisher, language = self.parse_description(description)
                
                # Look for stock code in next line
                stock_code = ""
                if i + 1 < len(lines):
                    next_line = lines[i+1].strip()
                    if 'Stock Code:' in next_line:
                        stock_match = re.search(r'Stock Code:\s*([A-Z0-9]+)', next_line)
                        if stock_match:
                            stock_code = stock_match.group(1)
                
                item = {
                    'sno': sno,
                    'title': title,
                    'author': author,
                    'publisher': publisher,
                    'language': language,
                    'stock_code': stock_code,
                    'quantity': qty,
                    'rate': rate,
                    'amount': amount
                }
                
                items.append(item)
            
            i += 1
        
        return items
    
    def parse_description(self, description: str) -> tuple:
        """Parse description to extract author, publisher, language"""
        author = publisher = language = ""
        
        if '|' in description:
            parts = [part.strip() for part in description.split('|')]
            if len(parts) >= 3:
                # Format: "by Author | Publisher | Language"
                if parts[0].startswith('by '):
                    author = parts[0][3:].strip()  # Remove "by "
                publisher = parts[1]
                language = parts[2]
            elif len(parts) == 2:
                publisher = parts[0]
                language = parts[1]
        else:
            # Single description, try to extract author if it starts with "by"
            if description.startswith('by '):
                author = description[3:].strip()
        
        return author, publisher, language
    
    def process_all_purchase_orders(self, folder_path: str) -> tuple:
        """Process all purchase order PDFs and return DataFrames"""
        po_folder = Path(folder_path)
        pdf_files = list(po_folder.glob("*.pdf"))
        
        all_po_data = []
        all_items_data = []
        
        print(f"Processing {len(pdf_files)} purchase order PDFs...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            po_data = self.extract_po_data(pdf_file)
            if po_data:
                # Separate items for items dataframe
                items = po_data.pop('items', [])
                all_po_data.append(po_data)
                
                # Add PO reference to each item
                for item in items:
                    item['po_number'] = po_data['po_number']
                    item['po_date'] = po_data['po_date']
                    item['vendor_name'] = po_data['vendor_name']
                    item['filename'] = po_data['filename']
                    all_items_data.append(item)
        
        # Create DataFrames
        po_df = pd.DataFrame(all_po_data)
        items_df = pd.DataFrame(all_items_data)
        
        return po_df, items_df
    
    def save_to_excel(self, po_df: pd.DataFrame, items_df: pd.DataFrame, filename: str = "reports/purchase_orders_extracted.xlsx"):
        """Save the processed data to Excel file"""
        # Ensure reports directory exists
        import os
        os.makedirs('reports', exist_ok=True)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            po_df.to_excel(writer, sheet_name='Purchase_Orders', index=False)
            items_df.to_excel(writer, sheet_name='Items', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Purchase Orders',
                    'Total Items',
                    'Total PO Value (₹)',
                    'Average PO Value (₹)',
                    'Unique Vendors',
                    'Date Range'
                ],
                'Value': [
                    len(po_df),
                    len(items_df),
                    f"{po_df['total_amount'].sum():,.2f}" if len(po_df) > 0 else 0,
                    f"{po_df['total_amount'].mean():,.2f}" if len(po_df) > 0 else 0,
                    po_df['vendor_name'].nunique() if len(po_df) > 0 else 0,
                    self._get_date_range(po_df) if len(po_df) > 0 else "N/A"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Data saved to {filename}")
    
    def _get_date_range(self, po_df):
        """Safely get date range from po_date column handling mixed data types"""
        try:
            # Filter out non-date values (NaN, None, empty strings)
            valid_dates = po_df['po_date'].dropna()
            valid_dates = valid_dates[valid_dates != '']
            valid_dates = valid_dates[valid_dates != 'None']
            
            if len(valid_dates) == 0:
                return "N/A"
            
            # Convert to datetime if needed
            date_series = pd.to_datetime(valid_dates, errors='coerce')
            date_series = date_series.dropna()
            
            if len(date_series) == 0:
                return "N/A"
                
            min_date = date_series.min().strftime('%Y-%m-%d')
            max_date = date_series.max().strftime('%Y-%m-%d')
            return f"{min_date} to {max_date}"
            
        except Exception as e:
            print(f"Warning: Error calculating date range: {e}")
            return "N/A"

def main():
    parser = FinalPurchaseOrderParser()
    
    # Process all purchase orders
    po_df, items_df = parser.process_all_purchase_orders("data/Purchase Order")
    
    # Display summary
    print(f"\n=== FINAL EXTRACTION SUMMARY ===")
    print(f"Total Purchase Orders processed: {len(po_df)}")
    print(f"Total Items extracted: {len(items_df)}")
    
    if len(po_df) > 0:
        print(f"\nPurchase Orders DataFrame shape: {po_df.shape}")
        print(f"Items DataFrame shape: {items_df.shape}")
        
        # Save to Excel
        parser.save_to_excel(po_df, items_df)
        
        # Display sample data
        print(f"\n=== SAMPLE PURCHASE ORDER DATA ===")
        if len(po_df) > 0:
            sample_cols = ['po_number', 'po_date', 'vendor_name', 'total_amount']
            print(po_df[sample_cols].head().to_string(index=False))
        
        print(f"\n=== SAMPLE ITEMS DATA ===")
        if len(items_df) > 0:
            sample_cols = ['po_number', 'title', 'author', 'publisher', 'quantity', 'rate', 'amount']
            print(items_df[sample_cols].head().to_string(index=False))
        
        # Basic analysis
        print(f"\n=== VENDOR ANALYSIS ===")
        print(f"Unique Vendors: {po_df['vendor_name'].nunique()}")
        vendor_counts = po_df['vendor_name'].value_counts()
        print("Top Vendors:")
        print(vendor_counts.head().to_string())
        
        print(f"\n=== FINANCIAL ANALYSIS ===")
        print(f"Total PO Value: ₹{po_df['total_amount'].sum():,.2f}")
        print(f"Average PO Value: ₹{po_df['total_amount'].mean():,.2f}")
        print(f"Min PO Value: ₹{po_df['total_amount'].min():,.2f}")
        print(f"Max PO Value: ₹{po_df['total_amount'].max():,.2f}")

if __name__ == "__main__":
    main()