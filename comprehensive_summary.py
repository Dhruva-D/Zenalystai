import pandas as pd
from pathlib import Path
import json
from datetime import datetime

class ComprehensiveETLSummary:
    def __init__(self):
        self.summary_data = {
            'extraction_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'documents_processed': {},
            'financial_summary': {},
            'inventory_analysis': {},
            'three_way_matching': {}
        }
    
    def load_extracted_data(self):
        """Load all extracted data from Excel files"""
        # Purchase Orders
        try:
            po_df = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Purchase_Orders')
            po_items_df = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Items')
            self.po_df = po_df
            self.po_items_df = po_items_df
        except Exception as e:
            print(f"Purchase Order data error: {e}")
            self.po_df = pd.DataFrame()
            self.po_items_df = pd.DataFrame()
        
        # GRN Data
        try:
            grn_df = pd.read_excel('grn_extracted_data.xlsx', sheet_name='GRN_Records')
            grn_items_df = pd.read_excel('grn_extracted_data.xlsx', sheet_name='Received_Items')
            self.grn_df = grn_df
            self.grn_items_df = grn_items_df
        except:
            print("GRN data not found")
            self.grn_df = pd.DataFrame()
            self.grn_items_df = pd.DataFrame()
        
        # Purchase Invoices
        try:
            pi_df = pd.read_excel('purchase_invoices_extracted.xlsx', sheet_name='Purchase_Invoices')
            pi_items_df = pd.read_excel('purchase_invoices_extracted.xlsx', sheet_name='Billed_Items')
            self.pi_df = pi_df
            self.pi_items_df = pi_items_df
        except:
            print("Purchase Invoice data not found")
            self.pi_df = pd.DataFrame()
            self.pi_items_df = pd.DataFrame()
        
        # Sales Invoices
        try:
            si_df = pd.read_excel('sales_invoices_extracted.xlsx', sheet_name='Sales_Invoices')
            si_items_df = pd.read_excel('sales_invoices_extracted.xlsx', sheet_name='Sold_Items')
            self.si_df = si_df
            self.si_items_df = si_items_df
        except:
            print("Sales Invoice data not found")
            self.si_df = pd.DataFrame()
            self.si_items_df = pd.DataFrame()
    
    def generate_comprehensive_summary(self):
        """Generate comprehensive summary of all extracted data"""
        self.load_extracted_data()
        
        # Document Processing Summary
        self.summary_data['documents_processed'] = {
            'purchase_orders': {
                'count': len(self.po_df),
                'items': len(self.po_items_df),
                'total_value': float(self.po_df['total_amount'].sum()) if len(self.po_df) > 0 else 0
            },
            'goods_receipt_notes': {
                'count': len(self.grn_df),
                'items': len(self.grn_items_df),
                'total_value': float(self.grn_df['total_value'].sum()) if len(self.grn_df) > 0 else 0
            },
            'purchase_invoices': {
                'count': len(self.pi_df),
                'items': len(self.pi_items_df),
                'total_value': float(self.pi_df['total_amount'].sum()) if len(self.pi_df) > 0 else 0
            },
            'sales_invoices': {
                'count': len(self.si_df),
                'items': len(self.si_items_df),
                'total_value': float(self.si_df['total_amount'].sum()) if len(self.si_df) > 0 else 0
            }
        }
        
        # Financial Summary
        purchase_total = self.summary_data['documents_processed']['purchase_invoices']['total_value']
        sales_total = self.summary_data['documents_processed']['sales_invoices']['total_value']
        
        self.summary_data['financial_summary'] = {
            'total_purchases': purchase_total,
            'total_sales': sales_total,
            'gross_profit': sales_total - purchase_total,
            'gross_profit_margin': ((sales_total - purchase_total) / sales_total * 100) if sales_total > 0 else 0
        }
        
        # Vendor Analysis
        if len(self.pi_df) > 0:
            vendor_analysis = self.pi_df['supplier_name'].value_counts().to_dict()
            self.summary_data['vendor_analysis'] = vendor_analysis
        
        # Customer Analysis
        if len(self.si_df) > 0:
            customer_analysis = self.si_df['buyer_name'].value_counts().to_dict()
            self.summary_data['customer_analysis'] = customer_analysis
        
        return self.summary_data
    
    def perform_three_way_matching(self):
        """Perform 3-way matching analysis between PO, GRN, and Invoice"""
        matching_results = []
        
        if len(self.po_df) == 0 or len(self.grn_df) == 0 or len(self.pi_df) == 0:
            print("Insufficient data for 3-way matching")
            return pd.DataFrame()
        
        # Match based on PO numbers
        for _, po_row in self.po_df.iterrows():
            po_number = po_row['po_number']
            
            # Find matching GRN
            matching_grn = self.grn_df[self.grn_df['related_po'] == po_number]
            
            # Find matching Purchase Invoice
            matching_invoice = self.pi_df[self.pi_df['related_po'] == po_number]
            
            match_result = {
                'po_number': po_number,
                'po_amount': po_row['total_amount'],
                'po_vendor': po_row['vendor_name'],
                'grn_found': len(matching_grn) > 0,
                'grn_amount': matching_grn['total_value'].sum() if len(matching_grn) > 0 else 0,
                'invoice_found': len(matching_invoice) > 0,
                'invoice_amount': matching_invoice['total_amount'].sum() if len(matching_invoice) > 0 else 0,
                'amounts_match': False,
                'status': 'Pending'
            }
            
            # Check if amounts match (within 1% tolerance)
            if match_result['grn_found'] and match_result['invoice_found']:
                po_amt = match_result['po_amount']
                grn_amt = match_result['grn_amount']
                inv_amt = match_result['invoice_amount']
                
                if abs(po_amt - grn_amt) / po_amt < 0.01 and abs(po_amt - inv_amt) / po_amt < 0.01:
                    match_result['amounts_match'] = True
                    match_result['status'] = 'Matched'
                else:
                    match_result['status'] = 'Amount Mismatch'
            elif match_result['grn_found'] and not match_result['invoice_found']:
                match_result['status'] = 'Invoice Pending'
            elif not match_result['grn_found'] and match_result['invoice_found']:
                match_result['status'] = 'GRN Pending'
            
            matching_results.append(match_result)
        
        return pd.DataFrame(matching_results)
    
    def save_comprehensive_report(self):
        """Save comprehensive ETL report to Excel"""
        summary = self.generate_comprehensive_summary()
        matching_df = self.perform_three_way_matching()
        
        with pd.ExcelWriter('comprehensive_etl_report.xlsx', engine='openpyxl') as writer:
            # Executive Summary
            exec_summary = pd.DataFrame([
                ['Document Processing Summary', ''],
                ['Purchase Orders Processed', summary['documents_processed']['purchase_orders']['count']],
                ['GRN Records Processed', summary['documents_processed']['goods_receipt_notes']['count']],
                ['Purchase Invoices Processed', summary['documents_processed']['purchase_invoices']['count']],
                ['Sales Invoices Processed', summary['documents_processed']['sales_invoices']['count']],
                ['', ''],
                ['Financial Summary', ''],
                ['Total Purchases (₹)', f"{summary['financial_summary']['total_purchases']:,.2f}"],
                ['Total Sales (₹)', f"{summary['financial_summary']['total_sales']:,.2f}"],
                ['Gross Profit (₹)', f"{summary['financial_summary']['gross_profit']:,.2f}"],
                ['Gross Profit Margin (%)', f"{summary['financial_summary']['gross_profit_margin']:.2f}%"],
                ['', ''],
                ['Extraction Date', summary['extraction_date']]
            ], columns=['Metric', 'Value'])
            exec_summary.to_excel(writer, sheet_name='Executive_Summary', index=False)
            
            # 3-Way Matching Results
            if len(matching_df) > 0:
                matching_df.to_excel(writer, sheet_name='Three_Way_Matching', index=False)
            
            # Document Count Summary
            doc_summary = pd.DataFrame([
                ['Purchase Orders', summary['documents_processed']['purchase_orders']['count'], 
                 summary['documents_processed']['purchase_orders']['items'],
                 summary['documents_processed']['purchase_orders']['total_value']],
                ['GRN Records', summary['documents_processed']['goods_receipt_notes']['count'],
                 summary['documents_processed']['goods_receipt_notes']['items'],
                 summary['documents_processed']['goods_receipt_notes']['total_value']],
                ['Purchase Invoices', summary['documents_processed']['purchase_invoices']['count'],
                 summary['documents_processed']['purchase_invoices']['items'],
                 summary['documents_processed']['purchase_invoices']['total_value']],
                ['Sales Invoices', summary['documents_processed']['sales_invoices']['count'],
                 summary['documents_processed']['sales_invoices']['items'],
                 summary['documents_processed']['sales_invoices']['total_value']]
            ], columns=['Document Type', 'Document Count', 'Item Count', 'Total Value (₹)'])
            doc_summary.to_excel(writer, sheet_name='Document_Summary', index=False)
        
        print("Comprehensive ETL report saved to comprehensive_etl_report.xlsx")
        return summary, matching_df
    
    def print_summary(self):
        """Print comprehensive summary to console"""
        summary, matching_df = self.save_comprehensive_report()
        
        print("\n" + "="*80)
        print("         COMPREHENSIVE ABC BOOK HOUSE ETL ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"\n📊 DOCUMENT PROCESSING OVERVIEW")
        print(f"   └─ Purchase Orders: {summary['documents_processed']['purchase_orders']['count']} documents, {summary['documents_processed']['purchase_orders']['items']} items")
        print(f"   └─ GRN Records: {summary['documents_processed']['goods_receipt_notes']['count']} documents, {summary['documents_processed']['goods_receipt_notes']['items']} items")
        print(f"   └─ Purchase Invoices: {summary['documents_processed']['purchase_invoices']['count']} documents, {summary['documents_processed']['purchase_invoices']['items']} items")
        print(f"   └─ Sales Invoices: {summary['documents_processed']['sales_invoices']['count']} documents, {summary['documents_processed']['sales_invoices']['items']} items")
        
        print(f"\n💰 FINANCIAL ANALYSIS")
        print(f"   └─ Total Purchases: ₹{summary['financial_summary']['total_purchases']:,.2f}")
        print(f"   └─ Total Sales: ₹{summary['financial_summary']['total_sales']:,.2f}")
        print(f"   └─ Gross Profit: ₹{summary['financial_summary']['gross_profit']:,.2f}")
        print(f"   └─ Gross Profit Margin: {summary['financial_summary']['gross_profit_margin']:.2f}%")
        
        if len(matching_df) > 0:
            print(f"\n🔄 THREE-WAY MATCHING ANALYSIS")
            matched_count = len(matching_df[matching_df['status'] == 'Matched'])
            pending_count = len(matching_df[matching_df['status'].str.contains('Pending')])
            mismatch_count = len(matching_df[matching_df['status'] == 'Amount Mismatch'])
            
            print(f"   └─ Total POs Analyzed: {len(matching_df)}")
            print(f"   └─ Fully Matched: {matched_count}")
            print(f"   └─ Pending Items: {pending_count}")
            print(f"   └─ Amount Mismatches: {mismatch_count}")
        
        print(f"\n📁 GENERATED FILES")
        print(f"   └─ zenalyst_demo_results.xlsx (Purchase Orders)")
        print(f"   └─ grn_extracted_data.xlsx (GRN Records)")
        print(f"   └─ purchase_invoices_extracted.xlsx (Purchase Invoices)")
        print(f"   └─ sales_invoices_extracted.xlsx (Sales Invoices)")
        print(f"   └─ comprehensive_etl_report.xlsx (Complete Analysis)")
        
        print(f"\n⏰ Analysis completed on: {summary['extraction_date']}")
        print("="*80)

def main():
    analyzer = ComprehensiveETLSummary()
    analyzer.print_summary()

if __name__ == "__main__":
    main()