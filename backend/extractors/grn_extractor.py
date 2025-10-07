import pdfplumber
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class GRNExtractor:
    def __init__(self):
        self.extracted_data = []
    
    def extract_grn_data(self, pdf_path: str) -> Dict:
        """Extract structured data from a GRN PDF using text parsing"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                # Initialize data structure
                grn_data = {
                    'filename': Path(pdf_path).name,
                    'grn_code': None,
                    'grn_date': None,
                    'related_po': None,
                    'related_invoice': None,
                    'supplier_name': None,
                    'supplier_address': None,
                    'receiver_name': None,
                    'receiver_address': None,
                    'receiver_gstin': None,
                    'items': [],
                    'subtotal': None,
                    'gst_amount': None,
                    'gst_rate': None,
                    'total_value': None,
                    'total_items_received': None,
                    'currency': 'INR'
                }
                
                # Extract GRN Code
                grn_match = re.search(r'GRN Code\s*\n\s*([A-Z0-9-]+)', text)
                if grn_match:
                    grn_data['grn_code'] = grn_match.group(1)
                
                # Extract GRN Date
                date_match = re.search(r'GRN Date:\s*(\d{2}\s+\w+\s+\d{4})', text)
                if date_match:
                    try:
                        grn_data['grn_date'] = datetime.strptime(date_match.group(1), '%d %b %Y').strftime('%Y-%m-%d')
                    except:
                        grn_data['grn_date'] = date_match.group(1)
                
                # Extract Related PO
                po_match = re.search(r'PO:\s*([A-Z0-9-]+)', text)
                if po_match:
                    grn_data['related_po'] = po_match.group(1)
                
                # Extract Related Invoice
                invoice_match = re.search(r'Invoice No\.\s*([A-Z0-9-]+)', text)
                if invoice_match:
                    grn_data['related_invoice'] = invoice_match.group(1)
                
                # Extract Receiver and Supplier Information
                self.extract_receiver_supplier_info(text, grn_data)
                
                # Extract financial information
                subtotal_match = re.search(r'Subtotal\s*₹([\d,]+\.?\d*)', text)
                if subtotal_match:
                    grn_data['subtotal'] = float(subtotal_match.group(1).replace(',', ''))
                
                gst_match = re.search(r'GST @ (\d+)%\s*₹([\d,]+\.?\d*)', text)
                if gst_match:
                    grn_data['gst_rate'] = float(gst_match.group(1))
                    grn_data['gst_amount'] = float(gst_match.group(2).replace(',', ''))
                
                total_match = re.search(r'TOTAL VALUE\s*₹([\d,]+\.?\d*)', text)
                if total_match:
                    grn_data['total_value'] = float(total_match.group(1).replace(',', ''))
                
                # Extract total items received
                total_items_match = re.search(r'Total Items Received\s*(\d+)', text)
                if total_items_match:
                    grn_data['total_items_received'] = int(total_items_match.group(1))
                
                # Extract items using text parsing
                items = self.extract_items_from_text(text)
                grn_data['items'] = items
                
                return grn_data
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None
    
    def extract_receiver_supplier_info(self, text: str, grn_data: Dict):
        """Extract receiver and supplier information from text"""
        lines = text.split('\n')
        
        # Extract receiver details (ABC Book House)
        grn_data['receiver_name'] = "ABC BOOK HOUSE PRIVATE LIMITED"
        grn_data['receiver_address'] = "3rd Main Road, Gandhinagar, Bangalore, Karnataka 560009"
        
        # Extract GSTIN
        gstin_match = re.search(r'GSTIN:\s*([A-Z0-9]+)', text)
        if gstin_match:
            grn_data['receiver_gstin'] = gstin_match.group(1)
        
        # Extract supplier name - look for pattern after "RECEIVED FROM (SUPPLIER)"
        for line in lines:
            if 'ABC BOOK HOUSE PRIVATE' in line and len(line) > len('ABC BOOK HOUSE PRIVATE'):
                # Extract everything after "PRIVATE "
                supplier_part = line.split('PRIVATE')[1].strip()
                if supplier_part:
                    grn_data['supplier_name'] = supplier_part
                break
        
        # Extract supplier address - look for address lines that don't belong to receiver
        supplier_address_lines = []
        collecting_supplier_address = False
        
        for line in lines:
            line = line.strip()
            # Skip receiver-related lines
            if any(receiver_keyword in line.lower() for receiver_keyword in 
                   ['abc book house', 'gandhinagar', 'bangalore', 'karnataka', '560009', 'gstin:']):
                continue
            
            # Look for address-like lines
            if (collecting_supplier_address or 
                (re.search(r'\d+/\d+|Building|Road|Chennai|Delhi|Mumbai|Hyderabad|Tamil Nadu|Maharashtra|Telangana|Daryaganj', line, re.IGNORECASE))):
                
                if not any(stop_word in line.lower() for stop_word in ['note:', 'following goods', 's.no', 'item description']):
                    supplier_address_lines.append(line)
                    collecting_supplier_address = True
                else:
                    break
        
        if supplier_address_lines:
            grn_data['supplier_address'] = ' '.join(supplier_address_lines[:3])
    
    def extract_items_from_text(self, text: str) -> List[Dict]:
        """Extract items from text using pattern matching"""
        items = []
        lines = text.split('\n')
        
        # Find the table header
        header_idx = -1
        for i, line in enumerate(lines):
            if 'S.No' in line and 'Item Description' in line and 'Qty Received' in line:
                header_idx = i
                break
        
        if header_idx == -1:
            return items
        
        # Process lines after header to find item data
        i = header_idx + 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop at financial summary
            if any(keyword in line for keyword in ['Subtotal', 'Total Items Received', 'GST @', 'TOTAL VALUE', 'Received By']):
                break
            
            if not line:
                i += 1
                continue
            
            # Look for the main item line with S.No, description, qty, rate, amount
            # Pattern: "1 by Author | Publisher | Language 40 ₹1,388.00 ₹55,520.00"
            item_pattern = r'^(\d+)\s+(.+?)\s+(\d+)\s+₹([\d,]+\.?\d*)\s+₹([\d,]+\.?\d*)$'
            match = re.match(item_pattern, line)
            
            if match:
                sno = match.group(1)
                description = match.group(2).strip()
                qty_received = int(match.group(3))
                rate = float(match.group(4).replace(',', ''))
                amount = float(match.group(5).replace(',', ''))
                
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
                    'qty_received': qty_received,
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
    
    def process_all_grns(self, folder_path: str) -> tuple:
        """Process all GRN PDFs and return DataFrames"""
        grn_folder = Path(folder_path)
        pdf_files = list(grn_folder.glob("*.pdf"))
        
        all_grn_data = []
        all_items_data = []
        
        print(f"Processing {len(pdf_files)} GRN PDFs...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            grn_data = self.extract_grn_data(pdf_file)
            if grn_data:
                # Separate items for items dataframe
                items = grn_data.pop('items', [])
                all_grn_data.append(grn_data)
                
                # Add GRN reference to each item
                for item in items:
                    item['grn_code'] = grn_data['grn_code']
                    item['grn_date'] = grn_data['grn_date']
                    item['related_po'] = grn_data['related_po']
                    item['related_invoice'] = grn_data['related_invoice']
                    item['supplier_name'] = grn_data['supplier_name']
                    item['filename'] = grn_data['filename']
                    all_items_data.append(item)
        
        # Create DataFrames
        grn_df = pd.DataFrame(all_grn_data)
        items_df = pd.DataFrame(all_items_data)
        
        return grn_df, items_df
    
    def save_to_excel(self, grn_df: pd.DataFrame, items_df: pd.DataFrame, filename: str = "reports/grn_extracted_data.xlsx"):
        """Save the processed data to Excel file"""
        # Ensure reports directory exists
        import os
        os.makedirs('reports', exist_ok=True)
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            grn_df.to_excel(writer, sheet_name='GRN_Records', index=False)
            items_df.to_excel(writer, sheet_name='Received_Items', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total GRN Records',
                    'Total Items Received',
                    'Total GRN Value (₹)',
                    'Average GRN Value (₹)',
                    'Unique Suppliers',
                    'Date Range'
                ],
                'Value': [
                    len(grn_df),
                    len(items_df),
                    f"{grn_df['total_value'].sum():,.2f}" if len(grn_df) > 0 else 0,
                    f"{grn_df['total_value'].mean():,.2f}" if len(grn_df) > 0 else 0,
                    grn_df['supplier_name'].nunique() if len(grn_df) > 0 else 0,
                    f"{grn_df['grn_date'].min()} to {grn_df['grn_date'].max()}" if len(grn_df) > 0 else "N/A"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"GRN data saved to {filename}")

def main():
    extractor = GRNExtractor()
    
    # Process all GRNs
    grn_df, items_df = extractor.process_all_grns("data/GRN Copies")
    
    # Display summary
    print(f"\n=== GRN EXTRACTION SUMMARY ===")
    print(f"Total GRN Records processed: {len(grn_df)}")
    print(f"Total Items received: {len(items_df)}")
    
    if len(grn_df) > 0:
        print(f"\nGRN Records DataFrame shape: {grn_df.shape}")
        print(f"Received Items DataFrame shape: {items_df.shape}")
        
        # Save to Excel
        extractor.save_to_excel(grn_df, items_df)
        
        # Display sample data
        print(f"\n=== SAMPLE GRN DATA ===")
        if len(grn_df) > 0:
            sample_cols = ['grn_code', 'grn_date', 'related_po', 'supplier_name', 'total_value']
            print(grn_df[sample_cols].head().to_string(index=False))
        
        print(f"\n=== SAMPLE RECEIVED ITEMS DATA ===")
        if len(items_df) > 0:
            sample_cols = ['grn_code', 'title', 'author', 'publisher', 'qty_received', 'rate', 'amount']
            print(items_df[sample_cols].head().to_string(index=False))
        
        # Basic analysis
        print(f"\n=== GRN ANALYSIS ===")
        print(f"Total GRN Value: ₹{grn_df['total_value'].sum():,.2f}")
        print(f"Average GRN Value: ₹{grn_df['total_value'].mean():,.2f}")
        print(f"Unique Suppliers: {grn_df['supplier_name'].nunique()}")
        
        if grn_df['supplier_name'].nunique() > 0:
            supplier_counts = grn_df['supplier_name'].value_counts()
            print("Top Suppliers:")
            print(supplier_counts.head().to_string())

if __name__ == "__main__":
    main()