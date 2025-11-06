import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import os
import warnings
warnings.filterwarnings('ignore')

@dataclass
class AgeingAnalysisResult:
    """Result structure for inventory ageing analysis"""
    isbn: str
    book_title: str
    category: str
    publisher: str
    closing_units: int
    closing_stock_value: float
    days_in_stock: int
    shelf_life_total: int
    shelf_life_remaining: int
    shelf_life_used_pct: float
    ageing_category: str  # 'FRESH', 'MODERATE', 'OLD', 'STALE', 'DEAD'
    dead_stock_risk: str  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    recommended_action: str
    liquidation_priority: int  # 1 = Highest priority, 5 = Lowest
    potential_loss: float

@dataclass
class AgeingBucket:
    """Age bucket analysis"""
    age_range: str
    item_count: int
    total_value: float
    percentage_of_portfolio: float
    avg_days_remaining: float

class InventoryAgeingAnalysisEngine:
    """
    Advanced Inventory Ageing Analysis Engine for Task 4
    
    Features:
    1. Age-based categorization of inventory
    2. Dead stock identification within shelf life
    3. Risk-based prioritization
    4. Liquidation recommendations
    5. Financial impact assessment
    6. Shelf life optimization insights
    """
    
    def __init__(self, data_file: str = None):
        self.ageing_results = []
        self.ageing_buckets = {}
        self.data_file = data_file or "data/ABC_Book_Stores_Inventory_Register.xlsx"
        
    def load_inventory_data(self, file_path: str = None) -> pd.DataFrame:
        """Load inventory register data"""
        print("📊 Loading Inventory Data for Ageing Analysis...")
        
        # Use provided file_path, or instance data_file, or default
        if file_path is None:
            file_path = self.data_file
        
        print(f"📂 Loading from: {file_path}")
        
        try:
            # Try different sheet names
            try:
                df = pd.read_excel(file_path, sheet_name='Inventory Register')
            except:
                print("ℹ️ 'Inventory Register' sheet not found, trying first sheet...")
                df = pd.read_excel(file_path, sheet_name=0)
            
            print(f"✅ Loaded {len(df)} inventory records")
            return df
        except Exception as e:
            print(f"❌ Error loading inventory data: {e}")
            return pd.DataFrame()
    
    def calculate_days_in_stock(self, po_date: str) -> int:
        """Calculate days since purchase order"""
        if pd.isna(po_date):
            return 0
            
        try:
            po_dt = pd.to_datetime(po_date)
            current_dt = datetime.now()
            return (current_dt - po_dt).days
        except:
            return 0
    
    def categorize_by_age(self, days_in_stock: int, shelf_life_total: int) -> str:
        """Categorize inventory by age"""
        if shelf_life_total <= 0:
            return 'UNKNOWN'
        
        age_pct = (days_in_stock / shelf_life_total) * 100
        
        if age_pct <= 20:
            return 'FRESH'       # 0-20% of shelf life used
        elif age_pct <= 40:
            return 'MODERATE'    # 21-40% of shelf life used
        elif age_pct <= 60:
            return 'OLD'         # 41-60% of shelf life used
        elif age_pct <= 80:
            return 'STALE'       # 61-80% of shelf life used
        else:
            return 'DEAD'        # 81-100% of shelf life used
    
    def assess_dead_stock_risk(self, shelf_life_remaining: int, closing_units: int) -> str:
        """Assess dead stock risk based on remaining shelf life and quantity"""
        if shelf_life_remaining <= 0:
            return 'CRITICAL'
        elif shelf_life_remaining <= 30:  # Less than 30 days
            if closing_units > 20:
                return 'CRITICAL'
            else:
                return 'HIGH'
        elif shelf_life_remaining <= 90:  # Less than 3 months
            if closing_units > 50:
                return 'HIGH'
            else:
                return 'MEDIUM'
        else:
            return 'LOW'
    
    def determine_liquidation_priority(self, ageing_category: str, dead_stock_risk: str, closing_value: float) -> int:
        """Determine liquidation priority (1 = highest, 5 = lowest)"""
        if ageing_category == 'DEAD' or dead_stock_risk == 'CRITICAL':
            return 1
        elif ageing_category == 'STALE' or dead_stock_risk == 'HIGH':
            return 2
        elif ageing_category == 'OLD' or dead_stock_risk == 'MEDIUM':
            return 3
        elif ageing_category == 'MODERATE':
            return 4
        else:
            return 5
    
    def generate_action_recommendation(self, result: AgeingAnalysisResult) -> str:
        """Generate specific action recommendations"""
        if result.ageing_category == 'DEAD':
            return f"LIQUIDATE IMMEDIATELY: Dead stock - {result.days_in_stock} days old, dispose or sell at heavy discount"
        
        elif result.ageing_category == 'STALE':
            return f"URGENT CLEARANCE: Organize clearance sale, offer 30-50% discount to move {result.closing_units} units"
        
        elif result.ageing_category == 'OLD':
            return f"PROMOTIONAL PUSH: Launch targeted marketing, bundle offers, or 20-30% discount"
        
        elif result.ageing_category == 'MODERATE':
            if result.closing_units > 30:
                return f"MONITOR CLOSELY: High quantity ({result.closing_units} units) with moderate age - optimize reorder levels"
            else:
                return f"NORMAL OPERATIONS: Continue regular sales activities"
        
        else:  # FRESH
            return f"OPTIMAL INVENTORY: Fresh stock, maintain current strategy"
    
    def calculate_potential_loss(self, closing_value: float, ageing_category: str, dead_stock_risk: str) -> float:
        """Calculate potential financial loss from ageing inventory"""
        loss_factors = {
            'DEAD': 0.8,      # 80% loss expected
            'STALE': 0.6,     # 60% loss expected
            'OLD': 0.4,       # 40% loss expected
            'MODERATE': 0.2,  # 20% loss expected
            'FRESH': 0.1      # 10% loss expected
        }
        
        base_loss = loss_factors.get(ageing_category, 0.5)
        
        # Adjust based on dead stock risk
        if dead_stock_risk == 'CRITICAL':
            base_loss = min(base_loss + 0.2, 0.9)
        elif dead_stock_risk == 'HIGH':
            base_loss = min(base_loss + 0.1, 0.8)
        
        return closing_value * base_loss
    
    def create_ageing_buckets(self, results: List[AgeingAnalysisResult]) -> Dict[str, AgeingBucket]:
        """Create age-based buckets for analysis"""
        buckets = {
            'FRESH (0-20% shelf life)': [],
            'MODERATE (21-40% shelf life)': [],
            'OLD (41-60% shelf life)': [],
            'STALE (61-80% shelf life)': [],
            'DEAD (81-100% shelf life)': []
        }
        
        # Categorize items into buckets
        for result in results:
            if result.ageing_category == 'FRESH':
                buckets['FRESH (0-20% shelf life)'].append(result)
            elif result.ageing_category == 'MODERATE':
                buckets['MODERATE (21-40% shelf life)'].append(result)
            elif result.ageing_category == 'OLD':
                buckets['OLD (41-60% shelf life)'].append(result)
            elif result.ageing_category == 'STALE':
                buckets['STALE (61-80% shelf life)'].append(result)
            else:  # DEAD
                buckets['DEAD (81-100% shelf life)'].append(result)
        
        # Create bucket analysis
        total_portfolio_value = sum([r.closing_stock_value for r in results])
        ageing_bucket_analysis = {}
        
        for bucket_name, items in buckets.items():
            if items:
                total_value = sum([item.closing_stock_value for item in items])
                avg_days_remaining = np.mean([item.shelf_life_remaining for item in items])
                
                ageing_bucket_analysis[bucket_name] = AgeingBucket(
                    age_range=bucket_name,
                    item_count=len(items),
                    total_value=total_value,
                    percentage_of_portfolio=(total_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0,
                    avg_days_remaining=avg_days_remaining
                )
        
        return ageing_bucket_analysis
    
    def process_ageing_analysis(self) -> Tuple[List[AgeingAnalysisResult], Dict[str, AgeingBucket]]:
        """Process complete inventory ageing analysis"""
        print("📈 Starting Inventory Ageing Analysis...")
        
        # Load data
        df = self.load_inventory_data()
        if df.empty:
            return [], {}
        
        results = []
        
        # Process each inventory item
        for _, row in df.iterrows():
            try:
                closing_units = int(row.get('Closing Stock No. of Units', 0))
                closing_stock_value = float(row.get('Closing Stock Total amount', 0))
                shelf_life_days = int(row.get('Average Shelf life of the Books(in days)', 365))
                po_date = row.get('PO Date', '')
                
                # Skip items with no closing stock
                if closing_units <= 0:
                    continue
                
                # Calculate ageing metrics
                days_in_stock = self.calculate_days_in_stock(po_date)
                shelf_life_remaining = max(0, shelf_life_days - days_in_stock)
                shelf_life_used_pct = (days_in_stock / shelf_life_days * 100) if shelf_life_days > 0 else 0
                
                ageing_category = self.categorize_by_age(days_in_stock, shelf_life_days)
                dead_stock_risk = self.assess_dead_stock_risk(shelf_life_remaining, closing_units)
                liquidation_priority = self.determine_liquidation_priority(ageing_category, dead_stock_risk, closing_stock_value)
                
                # Create result
                result = AgeingAnalysisResult(
                    isbn=str(row.get('ISBN', '')),
                    book_title=str(row.get('Book Title', '')),
                    category=str(row.get('Category', 'Unknown')),
                    publisher=str(row.get('Publisher', '')),
                    closing_units=closing_units,
                    closing_stock_value=closing_stock_value,
                    days_in_stock=days_in_stock,
                    shelf_life_total=shelf_life_days,
                    shelf_life_remaining=shelf_life_remaining,
                    shelf_life_used_pct=shelf_life_used_pct,
                    ageing_category=ageing_category,
                    dead_stock_risk=dead_stock_risk,
                    recommended_action='',
                    liquidation_priority=liquidation_priority,
                    potential_loss=0.0
                )
                
                # Generate recommendations and calculate potential loss
                result.recommended_action = self.generate_action_recommendation(result)
                result.potential_loss = self.calculate_potential_loss(closing_stock_value, ageing_category, dead_stock_risk)
                
                results.append(result)
                
            except Exception as e:
                print(f"⚠️ Error processing row: {e}")
                continue
        
        # Create ageing buckets
        ageing_buckets = self.create_ageing_buckets(results)
        
        # Save results
        self.save_ageing_results(results, ageing_buckets)
        
        print(f"✅ Ageing Analysis Complete!")
        print(f"   📊 {len(results)} items analyzed")
        print(f"   📂 {len(ageing_buckets)} age buckets created")
        print(f"   📁 Results saved to: inventory_ageing_analysis.xlsx")
        
        return results, ageing_buckets
    
    def save_ageing_results(self, results: List[AgeingAnalysisResult], ageing_buckets: Dict[str, AgeingBucket]):
        """Save ageing analysis results to Excel"""
        
        # Item analysis data
        items_data = []
        for result in results:
            items_data.append({
                'ISBN': result.isbn,
                'Book_Title': result.book_title,
                'Category': result.category,
                'Publisher': result.publisher,
                'Closing_Units': result.closing_units,
                'Closing_Stock_Value': result.closing_stock_value,
                'Days_In_Stock': result.days_in_stock,
                'Shelf_Life_Total': result.shelf_life_total,
                'Shelf_Life_Remaining': result.shelf_life_remaining,
                'Shelf_Life_Used_Pct': result.shelf_life_used_pct,
                'Ageing_Category': result.ageing_category,
                'Dead_Stock_Risk': result.dead_stock_risk,
                'Liquidation_Priority': result.liquidation_priority,
                'Potential_Loss': result.potential_loss,
                'Recommended_Action': result.recommended_action
            })
        
        items_df = pd.DataFrame(items_data)
        
        # Ageing buckets data
        buckets_data = []
        for bucket_name, bucket in ageing_buckets.items():
            buckets_data.append({
                'Age_Range': bucket.age_range,
                'Item_Count': bucket.item_count,
                'Total_Value': bucket.total_value,
                'Portfolio_Percentage': bucket.percentage_of_portfolio,
                'Avg_Days_Remaining': bucket.avg_days_remaining
            })
        
        buckets_df = pd.DataFrame(buckets_data)
        
        # Save to Excel with error handling
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'reports/inventory_ageing_analysis_{timestamp}.xlsx'
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                items_df.to_excel(writer, sheet_name='Item_Ageing_Analysis', index=False)
                buckets_df.to_excel(writer, sheet_name='Ageing_Buckets', index=False)
            
            # Executive summary
            summary_data = {
                'Metric': [
                    'Total Items Analyzed',
                    'Total Portfolio Value',
                    'Items in DEAD Category',
                    'Items in STALE Category',
                    'Items with Critical Risk',
                    'Items with High Risk',
                    'Total Potential Loss',
                    'Average Days in Stock',
                    'Items Requiring Immediate Action (Priority 1-2)'
                ],
                'Value': [
                    len(results),
                    sum([r.closing_stock_value for r in results]),
                    len([r for r in results if r.ageing_category == 'DEAD']),
                    len([r for r in results if r.ageing_category == 'STALE']),
                    len([r for r in results if r.dead_stock_risk == 'CRITICAL']),
                    len([r for r in results if r.dead_stock_risk == 'HIGH']),
                    sum([r.potential_loss for r in results]),
                    np.mean([r.days_in_stock for r in results]),
                    len([r for r in results if r.liquidation_priority <= 2])
                ]
            }
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
                
        except PermissionError:
            print(f"Warning: Could not write to {filename}. File may be open in another application.")
            return None
        except Exception as e:
            print(f"Error writing Excel file: {str(e)}")
            return None

def main():
    """Demo execution of Inventory Ageing Analysis"""
    engine = InventoryAgeingAnalysisEngine()
    results, ageing_buckets = engine.process_ageing_analysis()
    
    if not results:
        print("❌ No ageing analysis results to display")
        return
    
    print("\n" + "="*80)
    print("📅 INVENTORY AGEING ANALYSIS - EXECUTIVE SUMMARY")
    print("="*80)
    
    # Overall statistics
    total_items = len(results)
    total_value = sum([r.closing_stock_value for r in results])
    avg_days_in_stock = np.mean([r.days_in_stock for r in results])
    
    dead_items = len([r for r in results if r.ageing_category == 'DEAD'])
    stale_items = len([r for r in results if r.ageing_category == 'STALE'])
    critical_risk_items = len([r for r in results if r.dead_stock_risk == 'CRITICAL'])
    
    print(f"📈 Portfolio Overview:")
    print(f"   • Total Items: {total_items}")
    print(f"   • Total Portfolio Value: ₹{total_value:,.2f}")
    print(f"   • Average Days in Stock: {avg_days_in_stock:.0f} days")
    
    print(f"\n💀 Dead Stock Analysis:")
    print(f"   • DEAD Stock Items: {dead_items} ({dead_items/total_items*100:.1f}%)")
    print(f"   • STALE Stock Items: {stale_items} ({stale_items/total_items*100:.1f}%)")
    print(f"   • Critical Risk Items: {critical_risk_items} ({critical_risk_items/total_items*100:.1f}%)")
    
    # Ageing bucket analysis
    print(f"\n📊 Age Distribution:")
    for bucket_name, bucket in ageing_buckets.items():
        print(f"   • {bucket_name}: {bucket.item_count} items (₹{bucket.total_value:,.2f}, {bucket.percentage_of_portfolio:.1f}%)")
    
    # Critical items requiring immediate action
    urgent_items = [r for r in results if r.liquidation_priority <= 2]
    urgent_items.sort(key=lambda x: x.liquidation_priority)
    
    if urgent_items:
        print(f"\n🚨 URGENT ACTION REQUIRED ({len(urgent_items)} items):")
        for item in urgent_items[:8]:
            print(f"   • Priority {item.liquidation_priority}: {item.book_title[:45]}...")
            print(f"     {item.ageing_category} stock | {item.shelf_life_remaining} days left | ₹{item.closing_stock_value:,.2f} at risk")
    
    # Financial impact
    total_potential_loss = sum([r.potential_loss for r in results])
    print(f"\n💰 Financial Impact:")
    print(f"   • Total Potential Loss: ₹{total_potential_loss:,.2f}")
    print(f"   • Immediate Action Value: ₹{sum([r.closing_stock_value for r in urgent_items]):,.2f}")

if __name__ == "__main__":
    main()