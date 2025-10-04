import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@dataclass
class InventoryItem:
    """Data structure for inventory item analysis"""
    isbn: str
    book_title: str
    author: str
    publisher: str
    category: str
    store_location: str
    opening_units: int
    opening_stock_rate: float
    opening_stock_amount: float
    purchased_units: int
    purchase_rate: float
    purchase_amount: float
    issued_opening: int
    issued_current: int
    closing_units: int
    closing_stock_rate: float
    closing_stock_amount: float
    carrying_cost_per_unit: float
    shelf_life_days: int
    expected_removal_date: str
    po_date: str
    sales_date: str
    
@dataclass
class CostAnalysisResult:
    """Result structure for cost analysis"""
    isbn: str
    book_title: str
    category: str
    publisher: str
    closing_units: int
    closing_stock_amount: float
    carrying_cost_per_unit: float
    total_carrying_cost: float
    purchase_rate: float
    selling_rate: float
    gross_margin: float
    gross_margin_pct: float
    is_obsolete: bool
    days_in_stock: int
    shelf_life_remaining: int
    obsolescence_risk: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    margin_vs_carrying_cost: str  # 'PROFITABLE', 'BREAK_EVEN', 'LOSS_MAKING'
    recommendation: str
    financial_impact: float

@dataclass
class CategoryAnalysis:
    """Category-wise analysis results"""
    category: str
    total_items: int
    total_closing_value: float
    total_carrying_cost: float
    avg_gross_margin_pct: float
    obsolete_items: int
    high_risk_items: int
    profitable_items: int
    loss_making_items: int

class InventoryCostAnalysisEngine:
    """
    Advanced Inventory Cost Analysis Engine for Task 3
    
    Features:
    1. Carrying Cost Analysis for each product
    2. Gross Margin vs Carrying Cost comparison
    3. Obsolete/Dead Stock identification
    4. Shelf life analysis and risk assessment
    5. Category-wise profitability analysis
    6. Financial impact quantification
    7. Strategic recommendations
    """
    
    def __init__(self):
        self.inventory_data = []
        self.analysis_results = []
        self.category_analysis = {}
        
    def load_inventory_register(self, file_path: str = "data/ABC_Book_Stores_Inventory_Register.xlsx") -> pd.DataFrame:
        """Load and process inventory register data"""
        print("📊 Loading Inventory Register...")
        
        try:
            # Load the inventory register
            df = pd.read_excel(file_path, sheet_name='Inventory Register')
            
            print(f"✅ Loaded {len(df)} inventory records")
            return df
            
        except Exception as e:
            print(f"❌ Error loading inventory register: {e}")
            return pd.DataFrame()
    
    def calculate_days_in_stock(self, po_date: str, current_date: str = None) -> int:
        """Calculate days the item has been in stock"""
        if pd.isna(po_date):
            return 0
            
        try:
            if current_date is None:
                current_date = datetime.now().strftime('%Y-%m-%d')
            
            po_dt = pd.to_datetime(po_date)
            current_dt = pd.to_datetime(current_date)
            
            return (current_dt - po_dt).days
        except:
            return 0
    
    def calculate_shelf_life_remaining(self, po_date: str, shelf_life_days: int) -> int:
        """Calculate remaining shelf life"""
        days_in_stock = self.calculate_days_in_stock(po_date)
        return max(0, shelf_life_days - days_in_stock)
    
    def assess_obsolescence_risk(self, shelf_life_remaining: int, shelf_life_total: int) -> str:
        """Assess obsolescence risk based on remaining shelf life"""
        if shelf_life_total <= 0:
            return 'UNKNOWN'
        
        remaining_pct = (shelf_life_remaining / shelf_life_total) * 100
        
        if remaining_pct <= 10:
            return 'CRITICAL'
        elif remaining_pct <= 25:
            return 'HIGH'
        elif remaining_pct <= 50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def calculate_gross_margin(self, purchase_rate: float, selling_rate: float) -> Tuple[float, float]:
        """Calculate gross margin amount and percentage"""
        if purchase_rate <= 0 or selling_rate <= 0:
            return 0.0, 0.0
        
        margin = selling_rate - purchase_rate
        margin_pct = (margin / selling_rate) * 100
        
        return margin, margin_pct
    
    def determine_profitability_status(self, gross_margin: float, carrying_cost: float) -> str:
        """Determine if item is profitable compared to carrying cost"""
        if gross_margin > carrying_cost * 1.1:  # 10% buffer
            return 'PROFITABLE'
        elif gross_margin >= carrying_cost * 0.9:  # Within 10% of carrying cost
            return 'BREAK_EVEN'
        else:
            return 'LOSS_MAKING'
    
    def generate_recommendation(self, result: CostAnalysisResult) -> str:
        """Generate strategic recommendation for inventory item"""
        if result.obsolescence_risk == 'CRITICAL':
            return f"URGENT: Liquidate immediately - only {result.shelf_life_remaining} days remaining"
        
        elif result.obsolescence_risk == 'HIGH':
            return f"HIGH PRIORITY: Promote heavily or consider discount - {result.shelf_life_remaining} days remaining"
        
        elif result.margin_vs_carrying_cost == 'LOSS_MAKING':
            return f"REVIEW: Gross margin (₹{result.gross_margin:.2f}) < Carrying cost (₹{result.carrying_cost_per_unit:.2f}) - Consider price increase"
        
        elif result.margin_vs_carrying_cost == 'BREAK_EVEN':
            return f"MONITOR: Margin barely covers carrying cost - Optimize pricing or reduce costs"
        
        elif result.closing_units > 50 and result.obsolescence_risk == 'MEDIUM':
            return f"OPTIMIZE: High stock with medium obsolescence risk - Balance inventory levels"
        
        else:
            return f"MAINTAIN: Profitable item with good margin (₹{result.gross_margin:.2f}) and low risk"
    
    def calculate_financial_impact(self, result: CostAnalysisResult) -> float:
        """Calculate financial impact of inventory decisions"""
        # Calculate potential loss from obsolete stock
        if result.obsolescence_risk in ['CRITICAL', 'HIGH']:
            potential_loss = result.closing_stock_amount * 0.7  # Assume 70% loss on liquidation
        else:
            potential_loss = 0
        
        # Calculate carrying cost impact
        annual_carrying_cost = result.total_carrying_cost * 12  # Assuming monthly data
        
        # Calculate margin opportunity cost
        if result.margin_vs_carrying_cost == 'LOSS_MAKING':
            margin_loss = abs(result.gross_margin - result.carrying_cost_per_unit) * result.closing_units
        else:
            margin_loss = 0
        
        return potential_loss + annual_carrying_cost + margin_loss
    
    def process_inventory_analysis(self) -> Tuple[List[CostAnalysisResult], Dict[str, CategoryAnalysis]]:
        """Process complete inventory cost analysis"""
        print("🔍 Starting Inventory Cost Analysis...")
        
        # Load inventory data
        df = self.load_inventory_register()
        
        if df.empty:
            print("❌ No inventory data to analyze")
            return [], {}
        
        analysis_results = []
        category_stats = {}
        
        # Process each inventory item
        for _, row in df.iterrows():
            try:
                # Extract and clean data
                closing_units = int(row.get('Closing Stock No. of Units', 0))
                closing_stock_amount = float(row.get('Closing Stock Total amount', 0))
                carrying_cost_per_unit = float(row.get('Carrying Cost per Unit', 0))
                purchase_rate = float(row.get('Purchase Rate per unit', 0))
                shelf_life_days = int(row.get('Average Shelf life of the Books(in days)', 365))
                
                # Skip items with no closing stock
                if closing_units <= 0:
                    continue
                
                # Calculate selling rate (assuming Rate per Unit is selling price)
                selling_rate = float(row.get('Rate per Unit', 0))
                
                # Calculate metrics
                total_carrying_cost = carrying_cost_per_unit * closing_units
                gross_margin, gross_margin_pct = self.calculate_gross_margin(purchase_rate, selling_rate)
                
                po_date = row.get('PO Date', '')
                days_in_stock = self.calculate_days_in_stock(po_date)
                shelf_life_remaining = self.calculate_shelf_life_remaining(po_date, shelf_life_days)
                
                obsolescence_risk = self.assess_obsolescence_risk(shelf_life_remaining, shelf_life_days)
                profitability_status = self.determine_profitability_status(gross_margin, carrying_cost_per_unit)
                
                # Create analysis result
                result = CostAnalysisResult(
                    isbn=str(row.get('ISBN', '')),
                    book_title=str(row.get('Book Title', '')),
                    category=str(row.get('Category', 'Unknown')),
                    publisher=str(row.get('Publisher', '')),
                    closing_units=closing_units,
                    closing_stock_amount=closing_stock_amount,
                    carrying_cost_per_unit=carrying_cost_per_unit,
                    total_carrying_cost=total_carrying_cost,
                    purchase_rate=purchase_rate,
                    selling_rate=selling_rate,
                    gross_margin=gross_margin,
                    gross_margin_pct=gross_margin_pct,
                    is_obsolete=(obsolescence_risk in ['CRITICAL', 'HIGH']),
                    days_in_stock=days_in_stock,
                    shelf_life_remaining=shelf_life_remaining,
                    obsolescence_risk=obsolescence_risk,
                    margin_vs_carrying_cost=profitability_status,
                    recommendation='',
                    financial_impact=0.0
                )
                
                # Generate recommendation and calculate financial impact
                result.recommendation = self.generate_recommendation(result)
                result.financial_impact = self.calculate_financial_impact(result)
                
                analysis_results.append(result)
                
                # Update category statistics
                category = result.category
                if category not in category_stats:
                    category_stats[category] = {
                        'total_items': 0,
                        'total_closing_value': 0.0,
                        'total_carrying_cost': 0.0,
                        'gross_margins': [],
                        'obsolete_items': 0,
                        'high_risk_items': 0,
                        'profitable_items': 0,
                        'loss_making_items': 0
                    }
                
                stats = category_stats[category]
                stats['total_items'] += 1
                stats['total_closing_value'] += closing_stock_amount
                stats['total_carrying_cost'] += total_carrying_cost
                stats['gross_margins'].append(gross_margin_pct)
                
                if result.is_obsolete:
                    stats['obsolete_items'] += 1
                if result.obsolescence_risk in ['HIGH', 'CRITICAL']:
                    stats['high_risk_items'] += 1
                if result.margin_vs_carrying_cost == 'PROFITABLE':
                    stats['profitable_items'] += 1
                elif result.margin_vs_carrying_cost == 'LOSS_MAKING':
                    stats['loss_making_items'] += 1
                
            except Exception as e:
                print(f"⚠️ Error processing row: {e}")
                continue
        
        # Create category analysis objects
        category_analysis = {}
        for category, stats in category_stats.items():
            avg_margin = np.mean(stats['gross_margins']) if stats['gross_margins'] else 0
            
            category_analysis[category] = CategoryAnalysis(
                category=category,
                total_items=stats['total_items'],
                total_closing_value=stats['total_closing_value'],
                total_carrying_cost=stats['total_carrying_cost'],
                avg_gross_margin_pct=avg_margin,
                obsolete_items=stats['obsolete_items'],
                high_risk_items=stats['high_risk_items'],
                profitable_items=stats['profitable_items'],
                loss_making_items=stats['loss_making_items']
            )
        
        # Save results to Excel
        self.save_analysis_results(analysis_results, category_analysis)
        
        print(f"✅ Analysis Complete!")
        print(f"   📊 {len(analysis_results)} items analyzed")
        print(f"   📂 {len(category_analysis)} categories processed")
        print(f"   📁 Results saved to: inventory_cost_analysis.xlsx")
        
        return analysis_results, category_analysis
    
    def save_analysis_results(self, results: List[CostAnalysisResult], category_analysis: Dict[str, CategoryAnalysis]):
        """Save analysis results to Excel file"""
        
        # Create item analysis DataFrame
        items_data = []
        for result in results:
            items_data.append({
                'ISBN': result.isbn,
                'Book_Title': result.book_title,
                'Category': result.category,
                'Publisher': result.publisher,
                'Closing_Units': result.closing_units,
                'Closing_Stock_Value': result.closing_stock_amount,
                'Carrying_Cost_Per_Unit': result.carrying_cost_per_unit,
                'Total_Carrying_Cost': result.total_carrying_cost,
                'Purchase_Rate': result.purchase_rate,
                'Selling_Rate': result.selling_rate,
                'Gross_Margin': result.gross_margin,
                'Gross_Margin_Pct': result.gross_margin_pct,
                'Days_In_Stock': result.days_in_stock,
                'Shelf_Life_Remaining': result.shelf_life_remaining,
                'Obsolescence_Risk': result.obsolescence_risk,
                'Margin_vs_Carrying_Cost': result.margin_vs_carrying_cost,
                'Is_Obsolete': result.is_obsolete,
                'Financial_Impact': result.financial_impact,
                'Recommendation': result.recommendation
            })
        
        items_df = pd.DataFrame(items_data)
        
        # Create category analysis DataFrame
        category_data = []
        for category, analysis in category_analysis.items():
            category_data.append({
                'Category': analysis.category,
                'Total_Items': analysis.total_items,
                'Total_Closing_Value': analysis.total_closing_value,
                'Total_Carrying_Cost': analysis.total_carrying_cost,
                'Avg_Gross_Margin_Pct': analysis.avg_gross_margin_pct,
                'Obsolete_Items': analysis.obsolete_items,
                'High_Risk_Items': analysis.high_risk_items,
                'Profitable_Items': analysis.profitable_items,
                'Loss_Making_Items': analysis.loss_making_items,
                'Obsolescence_Rate_Pct': (analysis.obsolete_items / analysis.total_items * 100) if analysis.total_items > 0 else 0,
                'Profitability_Rate_Pct': (analysis.profitable_items / analysis.total_items * 100) if analysis.total_items > 0 else 0
            })
        
        category_df = pd.DataFrame(category_data)
        
        # Save to Excel
        with pd.ExcelWriter('inventory_cost_analysis.xlsx', engine='openpyxl') as writer:
            items_df.to_excel(writer, sheet_name='Item_Analysis', index=False)
            category_df.to_excel(writer, sheet_name='Category_Analysis', index=False)
            
            # Create summary sheet
            summary_data = {
                'Metric': [
                    'Total Items Analyzed',
                    'Total Closing Stock Value',
                    'Total Carrying Cost',
                    'Items with Obsolescence Risk',
                    'Items with Margin < Carrying Cost',
                    'Profitable Items',
                    'Total Financial Impact',
                    'Average Gross Margin %'
                ],
                'Value': [
                    len(results),
                    sum([r.closing_stock_amount for r in results]),
                    sum([r.total_carrying_cost for r in results]),
                    len([r for r in results if r.is_obsolete]),
                    len([r for r in results if r.margin_vs_carrying_cost == 'LOSS_MAKING']),
                    len([r for r in results if r.margin_vs_carrying_cost == 'PROFITABLE']),
                    sum([r.financial_impact for r in results]),
                    np.mean([r.gross_margin_pct for r in results if r.gross_margin_pct > 0])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)

def main():
    """Demo execution of Inventory Cost Analysis"""
    engine = InventoryCostAnalysisEngine()
    results, category_analysis = engine.process_inventory_analysis()
    
    if not results:
        print("❌ No analysis results to display")
        return
    
    print("\n" + "="*80)
    print("📊 INVENTORY COST ANALYSIS - EXECUTIVE SUMMARY")
    print("="*80)
    
    # Overall statistics
    total_items = len(results)
    total_closing_value = sum([r.closing_stock_amount for r in results])
    total_carrying_cost = sum([r.total_carrying_cost for r in results])
    obsolete_items = len([r for r in results if r.is_obsolete])
    loss_making_items = len([r for r in results if r.margin_vs_carrying_cost == 'LOSS_MAKING'])
    profitable_items = len([r for r in results if r.margin_vs_carrying_cost == 'PROFITABLE'])
    
    print(f"📈 Portfolio Overview:")
    print(f"   • Total Items in Inventory: {total_items}")
    print(f"   • Total Closing Stock Value: ₹{total_closing_value:,.2f}")
    print(f"   • Total Monthly Carrying Cost: ₹{total_carrying_cost:,.2f}")
    print(f"   • Annual Carrying Cost: ₹{total_carrying_cost * 12:,.2f}")
    
    print(f"\n🚨 Risk Assessment:")
    print(f"   • Obsolete/High-Risk Items: {obsolete_items} ({obsolete_items/total_items*100:.1f}%)")
    print(f"   • Loss-Making Items: {loss_making_items} ({loss_making_items/total_items*100:.1f}%)")
    print(f"   • Profitable Items: {profitable_items} ({profitable_items/total_items*100:.1f}%)")
    
    # Critical issues
    critical_items = [r for r in results if r.obsolescence_risk == 'CRITICAL']
    if critical_items:
        print(f"\n🔴 CRITICAL ALERTS - Items Requiring Immediate Action:")
        for item in critical_items[:5]:
            print(f"   • {item.book_title[:50]}... | {item.shelf_life_remaining} days left | ₹{item.closing_stock_amount:,.2f} at risk")
    
    # Category performance
    print(f"\n📚 Category Performance:")
    sorted_categories = sorted(category_analysis.values(), key=lambda x: x.avg_gross_margin_pct, reverse=True)
    for cat in sorted_categories[:5]:
        print(f"   • {cat.category}: {cat.avg_gross_margin_pct:.1f}% avg margin | {cat.obsolete_items}/{cat.total_items} obsolete")
    
    # Financial impact
    total_financial_impact = sum([r.financial_impact for r in results])
    print(f"\n💰 Financial Impact Analysis:")
    print(f"   • Total Financial Risk: ₹{total_financial_impact:,.2f}")
    print(f"   • Potential Annual Savings: ₹{total_carrying_cost * 6:,.2f} (through optimization)")

if __name__ == "__main__":
    main()