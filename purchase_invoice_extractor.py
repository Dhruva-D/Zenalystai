import pdfplumber
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class PurchaseInvoiceExtractor:
    def __init__(self):
        self.extracted_data = []
    
    def extract_invoice_data(self, pdf_path: str) -> Dict:
        """Extract structured data from a Purchase Invoice PDF using text parsing"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                # Initialize data structure
                invoice_data = {
                    'filename': Path(pdf_path).name,
                    'invoice_number': None,
                    'invoice_date': None,
                    'related_po': None,
                    'po_date': None,
                    'buyer_name': None,
                    'buyer_address': None,
                    'buyer_gstin': None,
                    'buyer_phone': None,
                    'buyer_email': None,
                    'supplier_name': None,
                    'supplier_address': None,
                    'items': [],
                    'subtotal': None,
                    'gst_amount': None,
                    'gst_rate': None,
                    'total_amount': None,
                    'currency': 'INR'
                }
                
                # Extract Invoice Number
                invoice_match = re.search(r'Invoice No\.\s*\n\s*([A-Z0-9-]+)', text)
                if invoice_match:
                    invoice_data['invoice_number'] = invoice_match.group(1)
                
                # Extract Invoice Date
                date_match = re.search(r'Invoice Date:\s*(\d{2}\s+\w+\s+\d{4})', text)
                if date_match:
                    try:
                        invoice_data['invoice_date'] = datetime.strptime(date_match.group(1), '%d %b %Y').strftime('%Y-%m-%d')
                    except:
                        invoice_data['invoice_date'] = date_match.group(1)
                
                # Extract Related PO
                po_match = re.search(r'PO Number:\s*([A-Z0-9-]+)', text)
                if po_match:
                    invoice_data['related_po'] = po_match.group(1)
                
                # Extract PO Date
                po_date_match = re.search(r'PO Date:\s*(\d{2}\s+\w+\s+\d{4})', text)
                if po_date_match:
                    try:
                        invoice_data['po_date'] = datetime.strptime(po_date_match.group(1), '%d %b %Y').strftime('%Y-%m-%d')
                    except:
                        invoice_data['po_date'] = po_date_match.group(1)
                
                # Extract Buyer and Supplier Information
                self.extract_buyer_supplier_info(text, invoice_data)
                
                # Extract financial information
                subtotal_match = re.search(r'Subtotal\s*₹([\d,]+\.?\d*)', text)
                if subtotal_match:
                    invoice_data['subtotal'] = float(subtotal_match.group(1).replace(',', ''))
                
                gst_match = re.search(r'GST @ (\d+)%\s*₹([\d,]+\.?\d*)', text)
                if gst_match:
                    invoice_data['gst_rate'] = float(gst_match.group(1))
                    invoice_data['gst_amount'] = float(gst_match.group(2).replace(',', ''))
                
                total_match = re.search(r'TOTAL\s*₹([\d,]+\.?\d*)', text)
                if total_match:
                    invoice_data['total_amount'] = float(total_match.group(1).replace(',', ''))
                
                # Extract items using text parsing
                items = self.extract_items_from_text(text)
                invoice_data['items'] = items
                
                return invoice_data
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None
    
    def extract_buyer_supplier_info(self, text: str, invoice_data: Dict):
        """Extract buyer and supplier information from text"""
        lines = text.split('\n')
        
        # Extract buyer details (ABC Book House)
        invoice_data['buyer_name'] = "ABC BOOK HOUSE PRIVATE LIMITED"
        invoice_data['buyer_address'] = "3rd Main Road, Gandhinagar, Bangalore, Karnataka 560009"
        
        # Extract GSTIN, Phone, Email
        gstin_match = re.search(r'GSTIN:\s*([A-Z0-9]+)', text)
        if gstin_match:
            invoice_data['buyer_gstin'] = gstin_match.group(1)
        
        phone_match = re.search(r'Phone:\s*([+\d\s-]+)', text)
        if phone_match:
            invoice_data['buyer_phone'] = phone_match.group(1).strip()
        
        email_match = re.search(r'Email:\s*([^\s\n]+)', text)
        if email_match:
            invoice_data['buyer_email'] = email_match.group(1)
        
        # Extract supplier name - look for pattern in SUPPLIER DETAILS section
        for line in lines:
            if 'ABC BOOK HOUSE PRIVATE' in line and len(line) > len('ABC BOOK HOUSE PRIVATE'):
                # Extract everything after "PRIVATE "
                supplier_part = line.split('PRIVATE')[1].strip()
                if supplier_part:
                    invoice_data['supplier_name'] = supplier_part
                break
        
        # Extract supplier address
        supplier_address_lines = []
        collecting_supplier_address = False
        
        for line in lines:
            line = line.strip()
            # Skip buyer-related lines
            if any(buyer_keyword in line.lower() for buyer_keyword in 
                   ['abc book house', 'gandhinagar', 'bangalore', 'karnataka', '560009', 'gstin:', 'phone:', 'email:']):
                continue
            
            # Look for address-like lines
            if (collecting_supplier_address or 
                (re.search(r'\d+/\d+|Floor|Road|Building|Chennai|Delhi|Mumbai|Hyderabad|Tamil Nadu|Maharashtra|Telangana', line, re.IGNORECASE))):
                
                if not any(stop_word in line.lower() for stop_word in ['purchase order', 's.no', 'item description']):
                    supplier_address_lines.append(line)
                    collecting_supplier_address = True
                else:
                    break
        
        if supplier_address_lines:
            invoice_data['supplier_address'] = ' '.join(supplier_address_lines[:3])
    
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
            if any(keyword in line for keyword in ['Subtotal', 'GST @', 'TOTAL', 'This is a computer-generated']):
                break
            
            if not line:
                i += 1
                continue
            
            # Look for the main item line with S.No, description, qty, rate, amount
            # Pattern: "1 by Author | Publisher | Language 35 ₹1,077.00 ₹37,695.00"
            item_pattern = r'^(\d+)\s+(.+?)\s+(\d+)\s+₹([\d,]+\.?\d*)\s+₹([\d,]+\.?\d*)$'
            match = re.match(item_pattern, line)
            
            if match:
                sno = match.group(1)
                description = match.group(2).strip()
                qty_billed = int(match.group(3))
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
                    'qty_billed': qty_billed,
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
    
    def process_all_invoices(self, folder_path: str) -> tuple:
        """Process all Purchase Invoice PDFs and return DataFrames"""
        invoice_folder = Path(folder_path)
        pdf_files = list(invoice_folder.glob("*.pdf"))
        
        all_invoice_data = []
        all_items_data = []
        
        print(f"Processing {len(pdf_files)} Purchase Invoice PDFs...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            invoice_data = self.extract_invoice_data(pdf_file)
            if invoice_data:
                # Separate items for items dataframe
                items = invoice_data.pop('items', [])
                all_invoice_data.append(invoice_data)
                
                # Add Invoice reference to each item
                for item in items:
                    item['invoice_number'] = invoice_data['invoice_number']
                    item['invoice_date'] = invoice_data['invoice_date']
                    item['related_po'] = invoice_data['related_po']
                    item['supplier_name'] = invoice_data['supplier_name']
                    item['filename'] = invoice_data['filename']
                    all_items_data.append(item)
        
        # Create DataFrames
        invoice_df = pd.DataFrame(all_invoice_data)
        items_df = pd.DataFrame(all_items_data)
        
        return invoice_df, items_df
    
    def save_to_excel(self, invoice_df: pd.DataFrame, items_df: pd.DataFrame, filename: str = "purchase_invoices_extracted.xlsx"):
        """Save the processed data to Excel file"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            invoice_df.to_excel(writer, sheet_name='Purchase_Invoices', index=False)
            items_df.to_excel(writer, sheet_name='Billed_Items', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Purchase Invoices',
                    'Total Items Billed',
                    'Total Invoice Value (₹)',
                    'Average Invoice Value (₹)',
                    'Unique Suppliers',
                    'Date Range'
                ],
                'Value': [
                    len(invoice_df),
                    len(items_df),
                    f"{invoice_df['total_amount'].sum():,.2f}" if len(invoice_df) > 0 else 0,
                    f"{invoice_df['total_amount'].mean():,.2f}" if len(invoice_df) > 0 else 0,
                    invoice_df['supplier_name'].nunique() if len(invoice_df) > 0 else 0,
                    f"{invoice_df['invoice_date'].min()} to {invoice_df['invoice_date'].max()}" if len(invoice_df) > 0 else "N/A"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Purchase Invoice data saved to {filename}")

def main():
    extractor = PurchaseInvoiceExtractor()
    
    # Process all Purchase Invoices
    invoice_df, items_df = extractor.process_all_invoices("data/Purchase Invoice")
    
    # Display summary
    print(f"\n=== PURCHASE INVOICE EXTRACTION SUMMARY ===")
    print(f"Total Purchase Invoices processed: {len(invoice_df)}")
    print(f"Total Items billed: {len(items_df)}")
    
    if len(invoice_df) > 0:
        print(f"\nPurchase Invoices DataFrame shape: {invoice_df.shape}")
        print(f"Billed Items DataFrame shape: {items_df.shape}")
        
        # Save to Excel
        extractor.save_to_excel(invoice_df, items_df)
        
        # Display sample data
        print(f"\n=== SAMPLE PURCHASE INVOICE DATA ===")
        if len(invoice_df) > 0:
            sample_cols = ['invoice_number', 'invoice_date', 'related_po', 'supplier_name', 'total_amount']
            print(invoice_df[sample_cols].head().to_string(index=False))
        
        print(f"\n=== SAMPLE BILLED ITEMS DATA ===")
        if len(items_df) > 0:
            sample_cols = ['invoice_number', 'title', 'author', 'publisher', 'qty_billed', 'rate', 'amount']
            print(items_df[sample_cols].head().to_string(index=False))
        
        # Basic analysis
        print(f"\n=== PURCHASE INVOICE ANALYSIS ===")
        print(f"Total Invoice Value: ₹{invoice_df['total_amount'].sum():,.2f}")
        print(f"Average Invoice Value: ₹{invoice_df['total_amount'].mean():,.2f}")
        print(f"Unique Suppliers: {invoice_df['supplier_name'].nunique()}")
        
        if invoice_df['supplier_name'].nunique() > 0:
            supplier_counts = invoice_df['supplier_name'].value_counts()
            print("Top Suppliers:")
            print(supplier_counts.head().to_string())

if __name__ == "__main__":
    main()