import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import re
from fuzzywuzzy import fuzz
from backend.core.data_models import (
    MatchingResult, ExceptionItem, VendorPerformance, DashboardSummary,
    ChartData, MatchStatus, ExceptionSeverity, PurchaseOrderData, GRNData, InvoiceData
)

class ThreeWayMatchingEngine:
    def __init__(self):
        self.po_df = pd.DataFrame()
        self.po_items_df = pd.DataFrame()
        self.grn_df = pd.DataFrame()
        self.grn_items_df = pd.DataFrame()
        self.pi_df = pd.DataFrame()
        self.pi_items_df = pd.DataFrame()
        
        self.matching_results = []
        self.exceptions = []
        self.vendor_performance = []
        
    def load_data(self) -> bool:
        """Load all extracted data from Excel files"""
        try:
            # Purchase Orders
            if Path('zenalyst_demo_results.xlsx').exists():
                self.po_df = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Purchase_Orders')
                self.po_items_df = pd.read_excel('zenalyst_demo_results.xlsx', sheet_name='Items')
            
            # GRN Data
            if Path('grn_extracted_data.xlsx').exists():
                self.grn_df = pd.read_excel('grn_extracted_data.xlsx', sheet_name='GRN_Records')
                self.grn_items_df = pd.read_excel('grn_extracted_data.xlsx', sheet_name='Received_Items')
            
            # Purchase Invoices
            if Path('purchase_invoices_extracted.xlsx').exists():
                self.pi_df = pd.read_excel('purchase_invoices_extracted.xlsx', sheet_name='Purchase_Invoices')
                self.pi_items_df = pd.read_excel('purchase_invoices_extracted.xlsx', sheet_name='Billed_Items')
            
            # Clean and standardize data
            self._clean_data()
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def _clean_data(self):
        """Clean and standardize data for matching"""
        # Standardize PO numbers
        for df in [self.po_df, self.grn_df, self.pi_df]:
            if 'po_number' in df.columns:
                df['po_number'] = df['po_number'].astype(str).str.strip()
            if 'related_po' in df.columns:
                df['related_po'] = df['related_po'].astype(str).str.strip()
        
        # Standardize vendor names
        for df in [self.po_df, self.grn_df, self.pi_df]:
            vendor_cols = ['vendor_name', 'supplier_name']
            for col in vendor_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.strip().str.title()
        
        # Handle missing values
        numeric_cols = ['total_amount', 'total_value']
        for df in [self.po_df, self.grn_df, self.pi_df]:
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    def normalize_vendor_name(self, vendor: str) -> str:
        """Normalize vendor names for better matching"""
        if pd.isna(vendor) or vendor == 'nan':
            return ""
        
        vendor = str(vendor).strip().title()
        # Remove common suffixes for better matching
        suffixes = ['Private Limited', 'Pvt Ltd', 'Ltd', 'Inc', 'Corporation', 'Corp']
        for suffix in suffixes:
            vendor = re.sub(rf'\s+{suffix}$', '', vendor, flags=re.IGNORECASE)
        
        return vendor.strip()
    
    def fuzzy_match_vendor(self, vendor1: str, vendor2: str, threshold: int = 80) -> bool:
        """Fuzzy match vendor names"""
        vendor1_norm = self.normalize_vendor_name(vendor1)
        vendor2_norm = self.normalize_vendor_name(vendor2)
        
        if not vendor1_norm or not vendor2_norm:
            return False
        
        ratio = fuzz.ratio(vendor1_norm, vendor2_norm)
        return ratio >= threshold
    
    def calculate_date_difference(self, date1: str, date2: str) -> Optional[int]:
        """Calculate difference in days between two dates"""
        try:
            if pd.isna(date1) or pd.isna(date2):
                return None
            
            d1 = pd.to_datetime(date1, errors='coerce')
            d2 = pd.to_datetime(date2, errors='coerce')
            
            if pd.isna(d1) or pd.isna(d2):
                return None
            
            return abs((d2 - d1).days)
        except:
            return None
    
    def analyze_three_way_matching(self) -> Dict:
        """Main method to perform 3-way matching analysis"""
        if not self.load_data():
            return {"error": "Failed to load data"}
        
        start_time = datetime.now()
        
        # Perform matching analysis
        self._perform_matching()
        self._generate_exceptions()
        self._calculate_vendor_performance()
        
        # Generate dashboard summary
        dashboard = self._generate_dashboard_summary()
        
        # Generate chart data
        charts = self._generate_chart_data()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'dashboard': dashboard,
            'matching_results': self.matching_results,
            'exceptions': self.exceptions,
            'vendor_performance': self.vendor_performance,
            'charts': charts,
            'processing_time': processing_time
        }
    
    def _perform_matching(self):
        """Perform the main 3-way matching logic"""
        self.matching_results = []
        
        if len(self.po_df) == 0:
            return
        
        for _, po_row in self.po_df.iterrows():
            po_number = po_row['po_number']
            
            # Find matching GRN
            matching_grn = self.grn_df[self.grn_df['related_po'] == po_number]
            
            # Find matching Purchase Invoice
            matching_invoice = self.pi_df[self.pi_df['related_po'] == po_number]
            
            # Calculate quantities
            po_items = self.po_items_df[self.po_items_df['po_number'] == po_number]
            grn_items = self.grn_items_df[self.grn_items_df['related_po'] == po_number]
            invoice_items = self.pi_items_df[self.pi_items_df['related_po'] == po_number]
            
            ordered_qty = po_items['quantity'].sum() if len(po_items) > 0 else 0
            received_qty = grn_items['qty_received'].sum() if len(grn_items) > 0 else 0
            billed_qty = invoice_items['qty_billed'].sum() if len(invoice_items) > 0 else 0
            
            # Create matching result (initialize with default values first)
            result = MatchingResult(
                po_number=po_number,
                status=MatchStatus.ORPHANED,  # Will be updated later
                match_score=0.0,  # Will be calculated later
                has_po=True,
                has_grn=len(matching_grn) > 0,
                has_invoice=len(matching_invoice) > 0,
                po_amount=float(po_row.get('total_amount', 0)),
                grn_amount=float(matching_grn['total_value'].sum()) if len(matching_grn) > 0 else 0,
                invoice_amount=float(matching_invoice['total_amount'].sum()) if len(matching_invoice) > 0 else 0,
                ordered_quantity=int(ordered_qty),
                received_quantity=int(received_qty),
                billed_quantity=int(billed_qty),
                po_vendor=str(po_row.get('vendor_name', '')),
                grn_vendor=str(matching_grn['supplier_name'].iloc[0]) if len(matching_grn) > 0 else None,
                invoice_vendor=str(matching_invoice['supplier_name'].iloc[0]) if len(matching_invoice) > 0 else None,
                po_date=str(po_row.get('po_date', '')),
                grn_date=str(matching_grn['grn_date'].iloc[0]) if len(matching_grn) > 0 else None,
                invoice_date=str(matching_invoice['invoice_date'].iloc[0]) if len(matching_invoice) > 0 else None
            )
            
            # Calculate variances
            result.amount_variance = result.po_amount - result.invoice_amount
            if result.po_amount > 0:
                result.amount_variance_percentage = (result.amount_variance / result.po_amount) * 100
            
            result.quantity_variance = result.ordered_quantity - result.received_quantity
            
            # Check vendor consistency
            if result.grn_vendor and result.invoice_vendor:
                result.vendor_consistent = self.fuzzy_match_vendor(
                    result.po_vendor, result.grn_vendor
                ) and self.fuzzy_match_vendor(
                    result.po_vendor, result.invoice_vendor
                )
            
            # Calculate timeline
            if result.po_date and result.grn_date:
                result.po_to_grn_days = self.calculate_date_difference(result.po_date, result.grn_date)
            
            if result.grn_date and result.invoice_date:
                result.grn_to_invoice_days = self.calculate_date_difference(result.grn_date, result.invoice_date)
            
            if result.po_date and result.invoice_date:
                result.total_cycle_days = self.calculate_date_difference(result.po_date, result.invoice_date)
            
            # Determine status and match score
            result.status, result.match_score = self._determine_match_status(result)
            
            self.matching_results.append(result)
    
    def _determine_match_status(self, result: MatchingResult) -> Tuple[MatchStatus, float]:
        """Determine the matching status and score"""
        score = 0
        
        # Document presence scoring (40 points)
        if result.has_po:
            score += 13.33
        if result.has_grn:
            score += 13.33
        if result.has_invoice:
            score += 13.33
        
        # Amount matching scoring (30 points)
        if result.po_amount > 0 and result.invoice_amount > 0:
            variance_pct = abs(result.amount_variance_percentage)
            if variance_pct <= 1:
                score += 30
            elif variance_pct <= 5:
                score += 20
            elif variance_pct <= 10:
                score += 10
        
        # Quantity matching scoring (20 points)
        if result.ordered_quantity > 0 and result.received_quantity > 0:
            qty_variance_pct = abs(result.quantity_variance / result.ordered_quantity * 100)
            if qty_variance_pct <= 1:
                score += 20
            elif qty_variance_pct <= 5:
                score += 15
            elif qty_variance_pct <= 10:
                score += 10
        
        # Vendor consistency scoring (10 points)
        if result.vendor_consistent:
            score += 10
        
        # Determine status based on conditions
        if not result.has_grn and not result.has_invoice:
            return MatchStatus.ORPHANED, score
        elif not result.has_grn:
            return MatchStatus.PENDING_GRN, score
        elif not result.has_invoice:
            return MatchStatus.PENDING_INVOICE, score
        elif not result.vendor_consistent:
            return MatchStatus.VENDOR_MISMATCH, score
        elif abs(result.amount_variance_percentage) > 10:
            return MatchStatus.AMOUNT_MISMATCH, score
        elif abs(result.quantity_variance / max(result.ordered_quantity, 1) * 100) > 10:
            return MatchStatus.QUANTITY_MISMATCH, score
        elif score > 90:
            return MatchStatus.FULLY_MATCHED, score
        else:
            return MatchStatus.PARTIAL_MATCH, score
    
    def _generate_exceptions(self):
        """Generate detailed exception reports"""
        self.exceptions = []
        
        for result in self.matching_results:
            # Missing GRN exception
            if not result.has_grn:
                self.exceptions.append(ExceptionItem(
                    po_number=result.po_number,
                    exception_type="Missing GRN",
                    severity=ExceptionSeverity.HIGH,
                    description=f"No GRN found for PO {result.po_number}",
                    recommendation="Create GRN or verify receipt of goods",
                    impact=f"Cannot verify receipt of ${result.po_amount:,.2f} worth of goods",
                    expected_value="GRN record",
                    actual_value="Missing"
                ))
            
            # Missing Invoice exception
            if not result.has_invoice:
                self.exceptions.append(ExceptionItem(
                    po_number=result.po_number,
                    exception_type="Missing Invoice",
                    severity=ExceptionSeverity.MEDIUM,
                    description=f"No invoice found for PO {result.po_number}",
                    recommendation="Follow up with supplier for invoice or verify payment terms",
                    impact=f"Cannot process payment for ${result.po_amount:,.2f}",
                    expected_value="Purchase invoice",
                    actual_value="Missing"
                ))
            
            # Amount variance exception
            if abs(result.amount_variance_percentage) > 5:
                severity = ExceptionSeverity.CRITICAL if abs(result.amount_variance_percentage) > 20 else ExceptionSeverity.HIGH
                self.exceptions.append(ExceptionItem(
                    po_number=result.po_number,
                    exception_type="Amount Variance",
                    severity=severity,
                    description=f"Amount variance of {result.amount_variance_percentage:.1f}% between PO and Invoice",
                    recommendation="Review pricing discrepancies with supplier",
                    impact=f"Potential overcharge/undercharge of ${abs(result.amount_variance):,.2f}",
                    expected_value=f"${result.po_amount:,.2f}",
                    actual_value=f"${result.invoice_amount:,.2f}",
                    variance=result.amount_variance
                ))
            
            # Quantity variance exception
            if result.ordered_quantity > 0 and abs(result.quantity_variance) > 0:
                qty_variance_pct = abs(result.quantity_variance / result.ordered_quantity * 100)
                if qty_variance_pct > 5:
                    severity = ExceptionSeverity.HIGH if qty_variance_pct > 20 else ExceptionSeverity.MEDIUM
                    self.exceptions.append(ExceptionItem(
                        po_number=result.po_number,
                        exception_type="Quantity Variance",
                        severity=severity,
                        description=f"Quantity variance of {result.quantity_variance} units ({qty_variance_pct:.1f}%)",
                        recommendation="Verify delivery quantities and update inventory records",
                        impact="Inventory discrepancy affecting stock levels",
                        expected_value=f"{result.ordered_quantity} units",
                        actual_value=f"{result.received_quantity} units",
                        variance=float(result.quantity_variance)
                    ))
            
            # Vendor mismatch exception
            if not result.vendor_consistent and result.has_grn and result.has_invoice:
                self.exceptions.append(ExceptionItem(
                    po_number=result.po_number,
                    exception_type="Vendor Mismatch",
                    severity=ExceptionSeverity.HIGH,
                    description="Vendor names inconsistent across documents",
                    recommendation="Verify supplier details and update master data",
                    impact="Potential payment to wrong supplier or data quality issues",
                    expected_value=result.po_vendor,
                    actual_value=f"GRN: {result.grn_vendor}, Invoice: {result.invoice_vendor}"
                ))
    
    def _calculate_vendor_performance(self):
        """Calculate vendor performance metrics"""
        self.vendor_performance = []
        
        if len(self.po_df) == 0:
            return
        
        vendors = self.po_df['vendor_name'].unique()
        
        for vendor in vendors:
            if pd.isna(vendor):
                continue
            
            vendor_pos = [r for r in self.matching_results if r.po_vendor == vendor]
            
            if not vendor_pos:
                continue
            
            perf = VendorPerformance(
                vendor_name=vendor,
                total_pos=len(vendor_pos),
                matched_pos=len([r for r in vendor_pos if r.status == MatchStatus.FULLY_MATCHED]),
                pending_grns=len([r for r in vendor_pos if r.status == MatchStatus.PENDING_GRN]),
                pending_invoices=len([r for r in vendor_pos if r.status == MatchStatus.PENDING_INVOICE]),
                total_po_value=sum([r.po_amount for r in vendor_pos]),
                total_grn_value=sum([r.grn_amount for r in vendor_pos]),
                total_invoice_value=sum([r.invoice_amount for r in vendor_pos])
            )
            
            # Calculate rates
            if perf.total_pos > 0:
                perf.match_rate = (perf.matched_pos / perf.total_pos) * 100
            
            # Calculate average processing times
            po_to_grn_days = [r.po_to_grn_days for r in vendor_pos if r.po_to_grn_days is not None]
            if po_to_grn_days:
                perf.avg_po_to_grn_days = sum(po_to_grn_days) / len(po_to_grn_days)
            
            grn_to_invoice_days = [r.grn_to_invoice_days for r in vendor_pos if r.grn_to_invoice_days is not None]
            if grn_to_invoice_days:
                perf.avg_grn_to_invoice_days = sum(grn_to_invoice_days) / len(grn_to_invoice_days)
            
            # Calculate amount variance
            perf.amount_variance = perf.total_po_value - perf.total_invoice_value
            
            # Calculate compliance score (simplified)
            compliance_factors = []
            if perf.match_rate >= 80:
                compliance_factors.append(25)
            elif perf.match_rate >= 60:
                compliance_factors.append(15)
            elif perf.match_rate >= 40:
                compliance_factors.append(10)
            
            if abs(perf.amount_variance / max(perf.total_po_value, 1)) <= 0.05:
                compliance_factors.append(25)
            elif abs(perf.amount_variance / max(perf.total_po_value, 1)) <= 0.1:
                compliance_factors.append(15)
            
            if perf.avg_po_to_grn_days and perf.avg_po_to_grn_days <= 7:
                compliance_factors.append(25)
            elif perf.avg_po_to_grn_days and perf.avg_po_to_grn_days <= 14:
                compliance_factors.append(15)
            
            if perf.avg_grn_to_invoice_days and perf.avg_grn_to_invoice_days <= 7:
                compliance_factors.append(25)
            elif perf.avg_grn_to_invoice_days and perf.avg_grn_to_invoice_days <= 14:
                compliance_factors.append(15)
            
            perf.compliance_score = sum(compliance_factors)
            
            self.vendor_performance.append(perf)
        
        # Sort by compliance score
        self.vendor_performance.sort(key=lambda x: x.compliance_score, reverse=True)
    
    def _generate_dashboard_summary(self) -> DashboardSummary:
        """Generate dashboard summary statistics"""
        dashboard = DashboardSummary()
        
        if not self.matching_results:
            return dashboard
        
        # Overall statistics
        dashboard.total_pos = len(self.matching_results)
        dashboard.fully_matched = len([r for r in self.matching_results if r.status == MatchStatus.FULLY_MATCHED])
        dashboard.partial_matches = len([r for r in self.matching_results if r.status == MatchStatus.PARTIAL_MATCH])
        dashboard.pending_grns = len([r for r in self.matching_results if r.status == MatchStatus.PENDING_GRN])
        dashboard.pending_invoices = len([r for r in self.matching_results if r.status == MatchStatus.PENDING_INVOICE])
        dashboard.exceptions = len(self.exceptions)
        
        if dashboard.total_pos > 0:
            dashboard.match_rate = (dashboard.fully_matched / dashboard.total_pos) * 100
        
        # Financial summary
        dashboard.total_po_value = sum([r.po_amount for r in self.matching_results])
        dashboard.total_grn_value = sum([r.grn_amount for r in self.matching_results])
        dashboard.total_invoice_value = sum([r.invoice_amount for r in self.matching_results])
        dashboard.total_variance = dashboard.total_po_value - dashboard.total_invoice_value
        
        # Exception severity counts
        dashboard.critical_exceptions = len([e for e in self.exceptions if e.severity == ExceptionSeverity.CRITICAL])
        dashboard.high_exceptions = len([e for e in self.exceptions if e.severity == ExceptionSeverity.HIGH])
        dashboard.medium_exceptions = len([e for e in self.exceptions if e.severity == ExceptionSeverity.MEDIUM])
        dashboard.low_exceptions = len([e for e in self.exceptions if e.severity == ExceptionSeverity.LOW])
        
        # Processing time analysis
        cycle_times = [r.total_cycle_days for r in self.matching_results if r.total_cycle_days is not None]
        if cycle_times:
            dashboard.avg_processing_time = sum(cycle_times) / len(cycle_times)
            dashboard.fastest_processing = min(cycle_times)
            dashboard.slowest_processing = max(cycle_times)
        
        return dashboard
    
    def _generate_chart_data(self) -> Dict[str, ChartData]:
        """Generate chart data for frontend visualization"""
        charts = {}
        
        # Match Status Distribution Chart
        status_counts = {}
        for result in self.matching_results:
            status = result.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        charts['match_status'] = ChartData(
            labels=list(status_counts.keys()),
            datasets=[{
                'label': 'PO Count',
                'data': list(status_counts.values()),
                'backgroundColor': [
                    '#4CAF50', '#FF9800', '#F44336', '#2196F3', 
                    '#9C27B0', '#607D8B', '#795548', '#E91E63'
                ][:len(status_counts)]
            }]
        )
        
        # Vendor Performance Chart
        if self.vendor_performance:
            top_vendors = self.vendor_performance[:10]  # Top 10 vendors
            charts['vendor_performance'] = ChartData(
                labels=[v.vendor_name for v in top_vendors],
                datasets=[{
                    'label': 'Compliance Score',
                    'data': [v.compliance_score for v in top_vendors],
                    'backgroundColor': '#2196F3'
                }, {
                    'label': 'Match Rate (%)',
                    'data': [v.match_rate for v in top_vendors],
                    'backgroundColor': '#4CAF50'
                }]
            )
        
        # Amount Variance Chart
        variance_data = [(r.po_number, r.amount_variance) for r in self.matching_results 
                        if abs(r.amount_variance) > 0]
        variance_data.sort(key=lambda x: abs(x[1]), reverse=True)
        top_variances = variance_data[:10]
        
        if top_variances:
            charts['amount_variance'] = ChartData(
                labels=[f"PO-{v[0]}" for v in top_variances],
                datasets=[{
                    'label': 'Amount Variance ($)',
                    'data': [v[1] for v in top_variances],
                    'backgroundColor': ['#F44336' if v[1] > 0 else '#4CAF50' for v in top_variances]
                }]
            )
        
        return charts