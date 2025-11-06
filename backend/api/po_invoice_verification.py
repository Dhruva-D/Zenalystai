import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import re
from fuzzywuzzy import fuzz, process
import warnings
warnings.filterwarnings('ignore')

@dataclass
class VerificationResult:
    """Data structure for PO-Invoice verification results"""
    po_number: str
    invoice_number: str
    verification_status: str  # 'MATCHED', 'EXCESS', 'SHORT', 'MISMATCH', 'PRICE_VARIANCE'
    item_title: str
    po_quantity: float
    invoice_quantity: float
    quantity_variance: float
    quantity_variance_pct: float
    po_rate: float
    invoice_rate: float
    price_variance: float
    price_variance_pct: float
    po_amount: float
    invoice_amount: float
    amount_variance: float
    severity: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    business_impact: str
    recommendation: str

@dataclass
class VendorPerformance:
    """Vendor performance metrics based on PO-Invoice verification"""
    vendor_name: str
    total_pos: int
    total_invoices: int
    matched_items: int
    excess_items: int
    short_items: int
    price_variance_items: int
    compliance_score: float
    reliability_rating: str
    total_po_value: float
    total_invoice_value: float
    financial_variance: float

class POInvoiceVerificationEngine:
    """
    Smart PO-Invoice Verification Engine for detecting procurement variances
    
    Features:
    1. Excess/Short Procurement Detection
    2. Price Variance Analysis
    3. Item Matching with Fuzzy Logic
    4. Vendor Performance Scoring
    5. Business Impact Assessment
    6. Automated Recommendations
    """
    
    def __init__(self):
        self.verification_results = []
        self.vendor_performance = {}
        self.tolerance_threshold = 0.05  # 5% tolerance for minor variances
        
    def normalize_item_title(self, title: str) -> str:
        """Normalize item titles for better matching"""
        if pd.isna(title):
            return ""
        
        # Convert to lowercase and remove extra spaces
        normalized = str(title).lower().strip()
        
        # Remove common prefixes/suffixes
        normalized = re.sub(r'\b(by|author|publisher|edition|book|paperback|hardcover)\b', '', normalized)
        
        # Remove special characters but keep alphanumeric and spaces
        normalized = re.sub(r'[^\w\s]', ' ', normalized)
        
        # Remove extra spaces
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def match_items_fuzzy(self, po_items: List[str], invoice_items: List[str], threshold: int = 80) -> Dict[str, str]:
        """
        Match PO items with Invoice items using fuzzy string matching
        Returns dict mapping invoice_item -> best_po_match
        """
        matches = {}
        
        # Normalize all items
        po_normalized = {item: self.normalize_item_title(item) for item in po_items}
        invoice_normalized = {item: self.normalize_item_title(item) for item in invoice_items}
        
        for inv_item, inv_normalized in invoice_normalized.items():
            if not inv_normalized:
                continue
                
            # Find best match in PO items
            best_match = process.extractOne(
                inv_normalized, 
                list(po_normalized.values()), 
                scorer=fuzz.token_sort_ratio
            )
            
            if best_match and best_match[1] >= threshold:
                # Find original PO item for this normalized match
                for po_item, po_norm in po_normalized.items():
                    if po_norm == best_match[0]:
                        matches[inv_item] = po_item
                        break
        
        return matches
    
    def calculate_severity(self, quantity_variance_pct: float, amount_variance: float) -> str:
        """Calculate severity level based on variance percentages and amounts"""
        abs_qty_var = abs(quantity_variance_pct)
        abs_amt_var = abs(amount_variance)
        
        if abs_qty_var >= 50 or abs_amt_var >= 50000:
            return 'CRITICAL'
        elif abs_qty_var >= 25 or abs_amt_var >= 25000:
            return 'HIGH'
        elif abs_qty_var >= 10 or abs_amt_var >= 10000:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_business_impact(self, result: VerificationResult) -> str:
        """Generate business impact description"""
        if result.verification_status == 'EXCESS':
            if result.severity in ['CRITICAL', 'HIGH']:
                return f"Over-procurement of ${abs(result.amount_variance):,.2f} - Excess inventory carrying cost"
            else:
                return f"Minor over-procurement - Monitor vendor compliance"
        
        elif result.verification_status == 'SHORT':
            if result.severity in ['CRITICAL', 'HIGH']:
                return f"Under-delivery of ${abs(result.amount_variance):,.2f} - Potential stockout risk"
            else:
                return f"Minor shortage - Acceptable delivery variance"
        
        elif result.verification_status == 'PRICE_VARIANCE':
            if result.price_variance > 0:
                return f"Price increase of ${result.price_variance:,.2f} - Inflation impact"
            else:
                return f"Price reduction of ${abs(result.price_variance):,.2f} - Cost savings"
        
        elif result.verification_status == 'MATCHED':
            return "Perfect compliance - No variances detected"
        
        else:
            return "Item mismatch - Review procurement process"
    
    def generate_recommendation(self, result: VerificationResult) -> str:
        """Generate actionable recommendations"""
        if result.verification_status == 'EXCESS' and result.severity in ['CRITICAL', 'HIGH']:
            return "Review vendor delivery process, implement stricter quantity controls"
        
        elif result.verification_status == 'SHORT' and result.severity in ['CRITICAL', 'HIGH']:
            return "Escalate with vendor, ensure full delivery, consider penalty clause"
        
        elif result.verification_status == 'PRICE_VARIANCE' and abs(result.price_variance_pct) > 10:
            return "Negotiate price revisions, review contract terms"
        
        elif result.verification_status == 'MISMATCH':
            return "Verify item specifications, resolve with vendor immediately"
        
        else:
            return "Continue monitoring, maintain current vendor relationship"
    
    def verify_po_invoice_pair(self, po_df: pd.DataFrame, invoice_df: pd.DataFrame, 
                              po_items_df: pd.DataFrame, invoice_items_df: pd.DataFrame) -> List[VerificationResult]:
        """
        Verify a specific PO against its corresponding invoice
        """
        results = []
        
        # Handle case where no invoice items were extracted
        if len(invoice_items_df) == 0 or 'title' not in invoice_items_df.columns:
            # Process all PO items as "SHORT" since they weren't invoiced
            for _, po_item in po_items_df.iterrows():
                po_number = po_df.iloc[0]['po_number'] if len(po_df) > 0 else 'UNKNOWN'
                invoice_number = invoice_df.iloc[0]['invoice_number'] if len(invoice_df) > 0 else 'NO_ITEMS'
                
                result = VerificationResult(
                    po_number=po_number,
                    invoice_number=invoice_number,
                    verification_status='SHORT',
                    item_title=po_item.get('title', 'Unknown Item'),
                    po_quantity=float(po_item.get('quantity', 0)),
                    invoice_quantity=0.0,
                    quantity_variance=-float(po_item.get('quantity', 0)),
                    quantity_variance_pct=-100.0,
                    po_rate=float(po_item.get('rate', 0)),
                    invoice_rate=0.0,
                    price_variance=0.0,
                    price_variance_pct=0.0,
                    po_amount=float(po_item.get('quantity', 0)) * float(po_item.get('rate', 0)),
                    invoice_amount=0.0,
                    amount_variance=-float(po_item.get('quantity', 0)) * float(po_item.get('rate', 0)),
                    severity='HIGH',
                    business_impact="Invoice received but no itemized details extracted",
                    recommendation="Review invoice extraction process or manual verification needed"
                )
                results.append(result)
            return results
        
        # Match items between PO and Invoice using fuzzy matching
        po_items_list = po_items_df['title'].dropna().tolist()
        invoice_items_list = invoice_items_df['title'].dropna().tolist()
        
        item_matches = self.match_items_fuzzy(po_items_list, invoice_items_list)
        
        # Create lookup dictionaries
        po_items_lookup = po_items_df.set_index('title').to_dict('index')
        invoice_items_lookup = invoice_items_df.set_index('title').to_dict('index')
        
        # Process matched items
        for invoice_item, po_item in item_matches.items():
            if po_item in po_items_lookup and invoice_item in invoice_items_lookup:
                po_data = po_items_lookup[po_item]
                invoice_data = invoice_items_lookup[invoice_item]
                
                # Extract quantities and rates
                po_qty = float(po_data.get('quantity', 0))
                invoice_qty = float(invoice_data.get('qty_billed', 0))
                po_rate = float(po_data.get('rate', 0))
                invoice_rate = float(invoice_data.get('rate', 0))
                
                # Calculate variances
                qty_variance = invoice_qty - po_qty
                qty_variance_pct = (qty_variance / po_qty * 100) if po_qty > 0 else 0
                
                price_variance = invoice_rate - po_rate
                price_variance_pct = (price_variance / po_rate * 100) if po_rate > 0 else 0
                
                po_amount = po_qty * po_rate
                invoice_amount = invoice_qty * invoice_rate
                amount_variance = invoice_amount - po_amount
                
                # Determine verification status
                status = 'MATCHED'
                if abs(qty_variance_pct) > self.tolerance_threshold * 100:
                    if qty_variance > 0:
                        status = 'EXCESS'
                    else:
                        status = 'SHORT'
                elif abs(price_variance_pct) > self.tolerance_threshold * 100:
                    status = 'PRICE_VARIANCE'
                
                # Create verification result
                result = VerificationResult(
                    po_number=po_df.iloc[0]['po_number'] if len(po_df) > 0 else 'N/A',
                    invoice_number=invoice_df.iloc[0]['invoice_number'] if len(invoice_df) > 0 else 'N/A',
                    verification_status=status,
                    item_title=po_item,
                    po_quantity=po_qty,
                    invoice_quantity=invoice_qty,
                    quantity_variance=qty_variance,
                    quantity_variance_pct=qty_variance_pct,
                    po_rate=po_rate,
                    invoice_rate=invoice_rate,
                    price_variance=price_variance,
                    price_variance_pct=price_variance_pct,
                    po_amount=po_amount,
                    invoice_amount=invoice_amount,
                    amount_variance=amount_variance,
                    severity=self.calculate_severity(qty_variance_pct, amount_variance),
                    business_impact='',
                    recommendation=''
                )
                
                # Generate business insights
                result.business_impact = self.generate_business_impact(result)
                result.recommendation = self.generate_recommendation(result)
                
                results.append(result)
        
        # Process unmatched items (items in PO but not in Invoice)
        unmatched_po_items = set(po_items_list) - set(item_matches.values())
        for po_item in unmatched_po_items:
            if po_item in po_items_lookup:
                po_data = po_items_lookup[po_item]
                
                result = VerificationResult(
                    po_number=po_df.iloc[0]['po_number'] if len(po_df) > 0 else 'N/A',
                    invoice_number=invoice_df.iloc[0]['invoice_number'] if len(invoice_df) > 0 else 'N/A',
                    verification_status='SHORT',
                    item_title=po_item,
                    po_quantity=float(po_data.get('quantity', 0)),
                    invoice_quantity=0.0,
                    quantity_variance=-float(po_data.get('quantity', 0)),
                    quantity_variance_pct=-100.0,
                    po_rate=float(po_data.get('rate', 0)),
                    invoice_rate=0.0,
                    price_variance=0.0,
                    price_variance_pct=0.0,
                    po_amount=float(po_data.get('quantity', 0)) * float(po_data.get('rate', 0)),
                    invoice_amount=0.0,
                    amount_variance=-float(po_data.get('quantity', 0)) * float(po_data.get('rate', 0)),
                    severity='CRITICAL',
                    business_impact=f"Item not delivered - Complete stockout risk",
                    recommendation="Immediate vendor escalation required - Ensure delivery or cancel PO"
                )
                
                results.append(result)
        
        # Process extra items (items in Invoice but not in PO)
        unmatched_invoice_items = set(invoice_items_list) - set(item_matches.keys())
        for invoice_item in unmatched_invoice_items:
            if invoice_item in invoice_items_lookup:
                invoice_data = invoice_items_lookup[invoice_item]
                
                result = VerificationResult(
                    po_number=po_df.iloc[0]['po_number'] if len(po_df) > 0 else 'N/A',
                    invoice_number=invoice_df.iloc[0]['invoice_number'] if len(invoice_df) > 0 else 'N/A',
                    verification_status='MISMATCH',
                    item_title=invoice_item,
                    po_quantity=0.0,
                    invoice_quantity=float(invoice_data.get('quantity', 0)),
                    quantity_variance=float(invoice_data.get('quantity', 0)),
                    quantity_variance_pct=100.0,
                    po_rate=0.0,
                    invoice_rate=float(invoice_data.get('rate', 0)),
                    price_variance=0.0,
                    price_variance_pct=0.0,
                    po_amount=0.0,
                    invoice_amount=float(invoice_data.get('quantity', 0)) * float(invoice_data.get('rate', 0)),
                    amount_variance=float(invoice_data.get('quantity', 0)) * float(invoice_data.get('rate', 0)),
                    severity='HIGH',
                    business_impact=f"Unordered item billed - Potential overbilling",
                    recommendation="Verify authorization for item, request credit note if unauthorized"
                )
                
                results.append(result)
        
        return results
    
    def process_all_verifications(self) -> Tuple[pd.DataFrame, Dict[str, VendorPerformance]]:
        """
        Process all PO-Invoice verifications and generate comprehensive results
        """
        print("🔍 Starting PO-Invoice Verification Analysis...")
        
        # Load all data
        try:
            po_df = pd.read_excel('reports/purchase_orders_extracted.xlsx', sheet_name='Purchase_Orders')
            po_items_df = pd.read_excel('reports/purchase_orders_extracted.xlsx', sheet_name='Items')
            
            pi_df = pd.read_excel('reports/purchase_invoices_extracted.xlsx', sheet_name='Purchase_Invoices')
            pi_items_df = pd.read_excel('reports/purchase_invoices_extracted.xlsx', sheet_name='Billed_Items')
            
            # Check if invoice items were extracted properly
            if len(pi_items_df) == 0 or 'invoice_number' not in pi_items_df.columns:
                print("⚠️ Warning: No invoice items found in extracted data.")
                print("This usually indicates an issue with the invoice extraction process.")
                print("The verification will proceed using invoice header data only.")
                # Create an empty DataFrame with expected columns for consistency
                pi_items_df = pd.DataFrame(columns=['invoice_number', 'title', 'qty_billed', 'rate', 'amount'])
            
        except FileNotFoundError as e:
            print(f"❌ Error: Required Excel files not found - {e}")
            print("Please run PO and Invoice extraction first!")
            return pd.DataFrame(), {}
        
        all_results = []
        vendor_stats = {}
        
        # Process each PO-Invoice pair
        for _, po_row in po_df.iterrows():
            try:
                po_number = po_row['po_number']
                related_po = po_row.get('related_po', po_number)
                
                # Find corresponding invoice(s)
                try:
                    matching_invoices = pi_df[pi_df['related_po'].str.contains(po_number, na=False)]
                except Exception as e:
                    print(f"⚠️ Warning: Error matching invoices for PO {po_number}: {e}")
                    matching_invoices = pd.DataFrame()
                
                if len(matching_invoices) == 0:
                    # No matching invoice found
                    po_items = po_items_df[po_items_df['po_number'] == po_number]
                    
                    for _, item_row in po_items.iterrows():
                        result = VerificationResult(
                            po_number=po_number,
                            invoice_number='NOT_INVOICED',
                            verification_status='SHORT',
                            item_title=item_row['title'],
                            po_quantity=float(item_row['quantity']),
                            invoice_quantity=0.0,
                            quantity_variance=-float(item_row['quantity']),
                            quantity_variance_pct=-100.0,
                            po_rate=float(item_row['rate']),
                            invoice_rate=0.0,
                            price_variance=0.0,
                            price_variance_pct=0.0,
                            po_amount=float(item_row['quantity']) * float(item_row['rate']),
                            invoice_amount=0.0,
                            amount_variance=-float(item_row['quantity']) * float(item_row['rate']),
                            severity='CRITICAL',
                            business_impact="PO not invoiced - Payment pending or delivery issue",
                            recommendation="Follow up with vendor for invoice or delivery status"
                        )
                        all_results.append(result)
                
                else:
                    # Process each matching invoice
                    for _, invoice_row in matching_invoices.iterrows():
                        invoice_number = invoice_row['invoice_number']
                        
                        # Get items for this PO and Invoice
                        po_items = po_items_df[po_items_df['po_number'] == po_number]
                        invoice_items = pi_items_df[pi_items_df['invoice_number'] == invoice_number]
                        
                        # Verify this PO-Invoice pair
                        pair_results = self.verify_po_invoice_pair(
                            po_df[po_df['po_number'] == po_number],
                            pi_df[pi_df['invoice_number'] == invoice_number],
                            po_items,
                            invoice_items
                        )
                        
                        all_results.extend(pair_results)
                        
                        # Update vendor statistics
                        vendor_name = po_row.get('supplier_name', 'Unknown')
                        if vendor_name not in vendor_stats:
                            vendor_stats[vendor_name] = {
                                'total_pos': 0,
                                'total_invoices': 0,
                                'matched_items': 0,
                                'excess_items': 0,
                                'short_items': 0,
                                'price_variance_items': 0,
                                'total_po_value': 0.0,
                                'total_invoice_value': 0.0
                            }
                        
                        vendor_stats[vendor_name]['total_pos'] += 1
                        vendor_stats[vendor_name]['total_invoices'] += 1
                        vendor_stats[vendor_name]['total_po_value'] += float(po_row.get('total_amount', 0))
                        vendor_stats[vendor_name]['total_invoice_value'] += float(invoice_row.get('total_amount', 0))
                        
                        for result in pair_results:
                            if result.verification_status == 'MATCHED':
                                vendor_stats[vendor_name]['matched_items'] += 1
                            elif result.verification_status == 'EXCESS':
                                vendor_stats[vendor_name]['excess_items'] += 1
                            elif result.verification_status == 'SHORT':
                                vendor_stats[vendor_name]['short_items'] += 1
                            elif result.verification_status == 'PRICE_VARIANCE':
                                vendor_stats[vendor_name]['price_variance_items'] += 1
                                
            except Exception as e:
                print(f"⚠️ Error processing PO {po_number}: {e}")
                # Continue processing other POs even if one fails
                continue
        
        # Convert results to DataFrame
        results_df = pd.DataFrame([
            {
                'PO_Number': r.po_number,
                'Invoice_Number': r.invoice_number,
                'Verification_Status': r.verification_status,
                'Item_Title': r.item_title,
                'PO_Quantity': r.po_quantity,
                'Invoice_Quantity': r.invoice_quantity,
                'Quantity_Variance': r.quantity_variance,
                'Quantity_Variance_Pct': r.quantity_variance_pct,
                'PO_Rate': r.po_rate,
                'Invoice_Rate': r.invoice_rate,
                'Price_Variance': r.price_variance,
                'Price_Variance_Pct': r.price_variance_pct,
                'PO_Amount': r.po_amount,
                'Invoice_Amount': r.invoice_amount,
                'Amount_Variance': r.amount_variance,
                'Severity': r.severity,
                'Business_Impact': r.business_impact,
                'Recommendation': r.recommendation
            }
            for r in all_results
        ])
        
        # Calculate vendor performance scores
        vendor_performance = {}
        for vendor, stats in vendor_stats.items():
            total_items = (stats['matched_items'] + stats['excess_items'] + 
                          stats['short_items'] + stats['price_variance_items'])
            
            if total_items > 0:
                compliance_score = (stats['matched_items'] / total_items) * 100
            else:
                compliance_score = 0
            
            # Determine reliability rating
            if compliance_score >= 95:
                rating = 'EXCELLENT'
            elif compliance_score >= 85:
                rating = 'GOOD'
            elif compliance_score >= 70:
                rating = 'AVERAGE'
            else:
                rating = 'POOR'
            
            vendor_performance[vendor] = VendorPerformance(
                vendor_name=vendor,
                total_pos=stats['total_pos'],
                total_invoices=stats['total_invoices'],
                matched_items=stats['matched_items'],
                excess_items=stats['excess_items'],
                short_items=stats['short_items'],
                price_variance_items=stats['price_variance_items'],
                compliance_score=compliance_score,
                reliability_rating=rating,
                total_po_value=stats['total_po_value'],
                total_invoice_value=stats['total_invoice_value'],
                financial_variance=stats['total_invoice_value'] - stats['total_po_value']
            )
        
        # Save results to Excel with error handling
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'reports/po_invoice_verification_results_{timestamp}.xlsx'
        
        # Ensure reports directory exists
        import os
        os.makedirs('reports', exist_ok=True)
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                results_df.to_excel(writer, sheet_name='Verification_Results', index=False)
                
                # Vendor performance summary
                vendor_df = pd.DataFrame([
                    {
                        'Vendor_Name': vp.vendor_name,
                        'Total_POs': vp.total_pos,
                        'Total_Invoices': vp.total_invoices,
                        'Matched_Items': vp.matched_items,
                        'Excess_Items': vp.excess_items,
                        'Short_Items': vp.short_items,
                        'Price_Variance_Items': vp.price_variance_items,
                        'Compliance_Score_Pct': vp.compliance_score,
                        'Reliability_Rating': vp.reliability_rating,
                        'Total_PO_Value': vp.total_po_value,
                        'Total_Invoice_Value': vp.total_invoice_value,
                        'Financial_Variance': vp.financial_variance
                    }
                    for vp in vendor_performance.values()
                ])
                vendor_df.to_excel(writer, sheet_name='Vendor_Performance', index=False)
            
            print(f"✅ PO-Invoice Verification Complete!")
            print(f"   📊 {len(results_df)} item verifications processed")
            print(f"   🏪 {len(vendor_performance)} vendors analyzed")
            print(f"   📁 Results saved to: {filename}")
            
        except PermissionError as e:
            print(f"⚠️  Warning: Could not save Excel file - {str(e)}")
            print(f"   📊 {len(results_df)} item verifications processed (results still available)")
            print(f"   🏪 {len(vendor_performance)} vendors analyzed")
        except Exception as e:
            print(f"⚠️  Warning: Excel save error - {str(e)}")
            print(f"   📊 Analysis completed: {len(results_df)} verifications, {len(vendor_performance)} vendors")
        
        return results_df, vendor_performance

def main():
    """Demo execution of PO-Invoice Verification"""
    engine = POInvoiceVerificationEngine()
    results_df, vendor_performance = engine.process_all_verifications()
    
    if len(results_df) > 0:
        print("\n" + "="*60)
        print("📈 PO-INVOICE VERIFICATION SUMMARY")
        print("="*60)
        
        # Overall statistics
        total_verifications = len(results_df)
        matched = len(results_df[results_df['Verification_Status'] == 'MATCHED'])
        excess = len(results_df[results_df['Verification_Status'] == 'EXCESS'])
        short = len(results_df[results_df['Verification_Status'] == 'SHORT'])
        price_var = len(results_df[results_df['Verification_Status'] == 'PRICE_VARIANCE'])
        mismatch = len(results_df[results_df['Verification_Status'] == 'MISMATCH'])
        
        print(f"Total Item Verifications: {total_verifications}")
        print(f"✅ Perfect Matches: {matched} ({matched/total_verifications*100:.1f}%)")
        print(f"📈 Excess Procurement: {excess} ({excess/total_verifications*100:.1f}%)")
        print(f"📉 Short Procurement: {short} ({short/total_verifications*100:.1f}%)")
        print(f"💰 Price Variances: {price_var} ({price_var/total_verifications*100:.1f}%)")
        print(f"❌ Mismatches: {mismatch} ({mismatch/total_verifications*100:.1f}%)")
        
        # Financial impact
        total_po_value = results_df['PO_Amount'].sum()
        total_invoice_value = results_df['Invoice_Amount'].sum()
        total_variance = results_df['Amount_Variance'].sum()
        
        print(f"\n💵 Financial Impact:")
        print(f"   Total PO Value: ${total_po_value:,.2f}")
        print(f"   Total Invoice Value: ${total_invoice_value:,.2f}")
        print(f"   Net Variance: ${total_variance:,.2f}")
        
        # Critical issues
        critical_issues = results_df[results_df['Severity'] == 'CRITICAL']
        if len(critical_issues) > 0:
            print(f"\n🚨 Critical Issues Requiring Immediate Attention: {len(critical_issues)}")
            for _, issue in critical_issues.head(3).iterrows():
                print(f"   • {issue['PO_Number']} - {issue['Item_Title'][:50]}...")
                print(f"     Impact: {issue['Business_Impact']}")
        
        # Top performing vendors
        if vendor_performance:
            print(f"\n🏆 Top Performing Vendors:")
            sorted_vendors = sorted(vendor_performance.values(), 
                                  key=lambda x: x.compliance_score, reverse=True)
            for vendor in sorted_vendors[:3]:
                print(f"   • {vendor.vendor_name}: {vendor.compliance_score:.1f}% compliance ({vendor.reliability_rating})")

if __name__ == "__main__":
    main()