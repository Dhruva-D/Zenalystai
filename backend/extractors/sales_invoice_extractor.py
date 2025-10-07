import pdfplumber
import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import warnings
warnings.filterwarnings('ignore')

class SalesInvoiceExtractor:
    def __init__(self):
        self.extracted_data = []
    
    def extract_sales_invoice_data(self, pdf_path: str) -> Dict:
        """Extract structured data from a Sales Invoice PDF using text parsing"""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                first_page = pdf.pages[0]
                text = first_page.extract_text()
                
                # Initialize data structure
                invoice_data = {
                    'filename': Path(pdf_path).name,
                    'invoice_number': None,
                    'invoice_date': None,
                    'seller_name': None,
                    'seller_address': None,
                    'seller_gstin': None,
                    'seller_phone': None,
                    'seller_email': None,
                    'buyer_name': None,
                    'buyer_address': None,
                    'buyer_phone': None,
                    'buyer_email': None,
                    'items': [],
                    'subtotal': None,
                    'discount_amount': None,
                    'gst_amount': None,
                    'gst_rate': None,
                    'total_amount': None,
                    'currency': 'INR'
                }
                
                # Extract Invoice Number from filename (INV-202510-XXX format)
                filename = Path(pdf_path).name
                invoice_match = re.search(r'INV-(\d{6}-\d{3})', filename)
                if invoice_match:
                    invoice_data['invoice_number'] = f"INV-{invoice_match.group(1)}"
                
                # Extract Invoice Date
                date_match = re.search(r'Invoice Date\s+(\d{2}-\w{3}-\d{4})', text)
                if date_match:
                    try:
                        invoice_data['invoice_date'] = datetime.strptime(date_match.group(1), '%d-%b-%Y').strftime('%Y-%m-%d')
                    except:
                        invoice_data['invoice_date'] = date_match.group(1)
                
                # Extract seller information (ABC Book PVT LTD)
                invoice_data['seller_name'] = "ABC BOOK PVT LTD"
                
                # Extract seller address
                address_match = re.search(r'ABC BOOK PVT LTD\n(.+?)\n', text)
                if address_match:
                    invoice_data['seller_address'] = address_match.group(1).strip()
                
                # Extract Phone and Email
                phone_match = re.search(r'Phone:\s*([+\d\s-]+)', text)
                if phone_match:
                    invoice_data['seller_phone'] = phone_match.group(1).strip()
                
                email_match = re.search(r'Email:\s*([^\s\n|]+)', text)
                if email_match:
                    invoice_data['seller_email'] = email_match.group(1)
                
                # Extract PAN
                pan_match = re.search(r"Company's PAN\s+([A-Z0-9]+)", text)
                if pan_match:
                    invoice_data['seller_gstin'] = pan_match.group(1)
                
                # Extract buyer information
                self.extract_buyer_info(text, invoice_data)
                
                # Extract financial information (note: amounts use 'n' instead of '$')
                subtotal_match = re.search(r'Subtotal\s+n([\d,]+\.?\d*)', text)
                if subtotal_match:
                    invoice_data['subtotal'] = float(subtotal_match.group(1).replace(',', ''))
                
                gst_match = re.search(r'GST @(\d+)%\s+n([\d,]+\.?\d*)', text)
                if gst_match:
                    invoice_data['gst_rate'] = float(gst_match.group(1))
                    invoice_data['gst_amount'] = float(gst_match.group(2).replace(',', ''))
                
                total_match = re.search(r'Total\s+n([\d,]+\.?\d*)', text)
                if total_match:
                    invoice_data['total_amount'] = float(total_match.group(1).replace(',', ''))
                
                # Extract items using text parsing
                items = self.extract_items_from_text(text)
                invoice_data['items'] = items
                
                return invoice_data
                
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return None
    
    def extract_buyer_info(self, text: str, invoice_data: Dict):
        """Extract buyer information from text"""
        # Look for "Buyer (Bill To)" pattern
        buyer_match = re.search(r'Buyer \(Bill To\)\s+(.+?)\n', text)
        if buyer_match:
            invoice_data['buyer_name'] = buyer_match.group(1).strip()
    
    def extract_items_from_text(self, text: str) -> List[Dict]:
        """Extract items from text using pattern matching"""
        items = []
        lines = text.split('\n')
        
        # Find the table header
        header_idx = -1
        for i, line in enumerate(lines):
            if 'Sl No.' in line and 'Particulars' in line:
                header_idx = i
                break
        
        if header_idx == -1:
            return items
        
        # Process lines after header to find item data
        i = header_idx + 1
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Stop at financial summary
            if any(keyword in line for keyword in ['Subtotal', 'GST @', 'Total', 'Amount Chargeable']):
                break
            
            if not line:
                i += 1
                continue
            
            # Look for item line pattern: "1 The Alchemist by Paulo Coelho 25 n2,271.00 n56,775.00"
            item_pattern = r'^(\d+)\s+(.+?)\s+(\d+)\s+n([\d,]+\.?\d*)\s+n([\d,]+\.?\d*)$'
            match = re.match(item_pattern, line)
            
            if match:
                sno = match.group(1)
                title = match.group(2).strip()
                qty_sold = int(match.group(3))
                rate = float(match.group(4).replace(',', ''))
                amount = float(match.group(5).replace(',', ''))
                
                # Look for author in next line
                author = ""
                category = ""
                if i + 1 < len(lines):
                    author_line = lines[i+1].strip()
                    if author_line.startswith('Author:'):
                        author = author_line.replace('Author:', '').strip()
                
                # Look for category in the line after author
                if i + 2 < len(lines):
                    category_line = lines[i+2].strip()
                    if category_line.startswith('Category:'):
                        category = category_line.replace('Category:', '').strip()
                
                item = {
                    'sno': sno,
                    'title': title,
                    'author': author,
                    'category': category,
                    'qty_sold': qty_sold,
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
    
    def process_all_sales_invoices(self, folder_path: str) -> tuple:
        """Process all Sales Invoice PDFs and return DataFrames"""
        invoice_folder = Path(folder_path)
        pdf_files = list(invoice_folder.glob("*.pdf"))
        
        all_invoice_data = []
        all_items_data = []
        
        print(f"Processing {len(pdf_files)} Sales Invoice PDFs...")
        
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")
            
            invoice_data = self.extract_sales_invoice_data(pdf_file)
            if invoice_data:
                # Separate items for items dataframe
                items = invoice_data.pop('items', [])
                all_invoice_data.append(invoice_data)
                
                # Add Invoice reference to each item
                for item in items:
                    item['invoice_number'] = invoice_data['invoice_number']
                    item['invoice_date'] = invoice_data['invoice_date']
                    item['buyer_name'] = invoice_data['buyer_name']
                    item['filename'] = invoice_data['filename']
                    all_items_data.append(item)
        
        # Create DataFrames
        invoice_df = pd.DataFrame(all_invoice_data)
        items_df = pd.DataFrame(all_items_data)
        
        return invoice_df, items_df
    
    def save_to_excel(self, invoice_df: pd.DataFrame, items_df: pd.DataFrame, filename: str = "sales_invoices_extracted.xlsx"):
        """Save the processed data to Excel file"""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            invoice_df.to_excel(writer, sheet_name='Sales_Invoices', index=False)
            items_df.to_excel(writer, sheet_name='Sold_Items', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Sales Invoices',
                    'Total Items Sold',
                    'Total Sales Revenue ($)',
                    'Average Invoice Value ($)',
                    'Unique Customers',
                    'Date Range'
                ],
                'Value': [
                    len(invoice_df),
                    len(items_df),
                    f"{invoice_df['total_amount'].sum():,.2f}" if len(invoice_df) > 0 else 0,
                    f"{invoice_df['total_amount'].mean():,.2f}" if len(invoice_df) > 0 else 0,
                    invoice_df['buyer_name'].nunique() if len(invoice_df) > 0 else 0,
                    f"{invoice_df['invoice_date'].min()} to {invoice_df['invoice_date'].max()}" if len(invoice_df) > 0 else "N/A"
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Sales Invoice data saved to {filename}")

def main():
    extractor = SalesInvoiceExtractor()
    
    # Process all Sales Invoices
    invoice_df, items_df = extractor.process_all_sales_invoices("data/Sales Invoices")
    
    # Display summary
    print(f"\n=== SALES INVOICE EXTRACTION SUMMARY ===")
    print(f"Total Sales Invoices processed: {len(invoice_df)}")
    print(f"Total Items sold: {len(items_df)}")
    
    if len(invoice_df) > 0:
        print(f"\nSales Invoices DataFrame shape: {invoice_df.shape}")
        print(f"Sold Items DataFrame shape: {items_df.shape}")
        
        # Save to Excel
        extractor.save_to_excel(invoice_df, items_df)
        
        # Display sample data
        print(f"\n=== SAMPLE SALES INVOICE DATA ===")
        if len(invoice_df) > 0:
            sample_cols = ['invoice_number', 'invoice_date', 'buyer_name', 'total_amount']
            print(invoice_df[sample_cols].head().to_string(index=False))
        
        print(f"\n=== SAMPLE SOLD ITEMS DATA ===")
        if len(items_df) > 0:
            sample_cols = ['invoice_number', 'title', 'author', 'category', 'qty_sold', 'rate', 'amount']
            print(items_df[sample_cols].head().to_string(index=False))
        
        # Basic analysis
        print(f"\n=== SALES ANALYSIS ===")
        print(f"Total Sales Revenue: ${invoice_df['total_amount'].sum():,.2f}")
        print(f"Average Invoice Value: ${invoice_df['total_amount'].mean():,.2f}")
        print(f"Unique Customers: {invoice_df['buyer_name'].nunique()}")
        
        if invoice_df['buyer_name'].nunique() > 0:
            customer_counts = invoice_df['buyer_name'].value_counts()
            print("Top Customers:")
            print(customer_counts.head().to_string())

if __name__ == "__main__":
    main()