import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

@dataclass
class FIFOValuationResult:
    """Result structure for FIFO inventory valuation"""
    isbn: str
    book_title: str
    category: str
    publisher: str
    closing_units: int
    
    # Current accounting values
    current_stock_value: float
    current_rate_per_unit: float
    
    # FIFO-based values
    fifo_stock_value: float
    fifo_rate_per_unit: float
    
    # Market values
    selling_price: float
    market_value: float
    
    # Analysis results
    valuation_difference: float
    valuation_difference_pct: float
    price_realization_potential: float
    price_realization_pct: float
    
    # Strategic insights
    valuation_status: str  # 'UNDERVALUED', 'FAIR_VALUE', 'OVERVALUED'
    liquidation_feasibility: str  # 'PROFITABLE', 'BREAK_EVEN', 'LOSS_MAKING'
    recommended_pricing: float
    strategic_action: str

@dataclass
class CategoryValuation:
    """Category-wise valuation analysis"""
    category: str
    total_items: int
    current_book_value: float
    fifo_book_value: float
    market_value: float
    total_units: int
    avg_price_realization_pct: float
    undervalued_items: int
    overvalued_items: int

class InventoryValuationAnalysisEngine:
    """
    Advanced Inventory Valuation Analysis Engine for Task 5
    
    Features:
    1. FIFO-based stock valuation vs current book value
    2. Market value comparison with selling prices
    3. Price realization potential analysis
    4. Valuation gap identification
    5. Strategic pricing recommendations
    6. Liquidation feasibility assessment
    """
    
    def __init__(self):
        self.valuation_results = []
        self.category_analysis = {}
        
    def load_inventory_data(self, file_path: str = "data/ABC_Book_Stores_Inventory_Register.xlsx") -> pd.DataFrame:
        """Load inventory register data"""
        print("📊 Loading Inventory Data for Valuation Analysis...")
        
        try:
            df = pd.read_excel(file_path, sheet_name='Inventory Register')
            print(f"✅ Loaded {len(df)} inventory records")
            return df
        except Exception as e:
            print(f"❌ Error loading inventory data: {e}")
            return pd.DataFrame()
    
    def calculate_fifo_valuation(self, opening_units: int, opening_rate: float, 
                                purchased_units: int, purchase_rate: float, 
                                closing_units: int) -> Tuple[float, float]:
        """
        Calculate FIFO-based valuation
        FIFO assumes first purchased items are sold first, so closing stock 
        consists of most recently purchased items
        """
        if closing_units <= 0:
            return 0.0, 0.0
        
        total_available_units = opening_units + purchased_units
        
        if closing_units > total_available_units:
            # Error case - closing units cannot exceed available units
            return closing_units * purchase_rate, purchase_rate
        
        # FIFO Logic: Closing stock comes from most recent purchases first
        if closing_units <= purchased_units:
            # All closing stock is from current year purchases
            fifo_value = closing_units * purchase_rate
            fifo_rate = purchase_rate
        else:
            # Closing stock includes both current purchases and opening stock
            current_purchase_contribution = purchased_units * purchase_rate
            opening_contribution = (closing_units - purchased_units) * opening_rate
            
            fifo_value = current_purchase_contribution + opening_contribution
            fifo_rate = fifo_value / closing_units if closing_units > 0 else 0
        
        return fifo_value, fifo_rate
    
    def determine_valuation_status(self, current_value: float, fifo_value: float, threshold: float = 0.05) -> str:
        """Determine if inventory is undervalued, fairly valued, or overvalued"""
        if fifo_value <= 0:
            return 'UNKNOWN'
        
        difference_pct = abs(current_value - fifo_value) / fifo_value
        
        if difference_pct <= threshold:
            return 'FAIR_VALUE'
        elif current_value < fifo_value:
            return 'UNDERVALUED'
        else:
            return 'OVERVALUED'
    
    def assess_liquidation_feasibility(self, fifo_rate: float, selling_price: float) -> str:
        """Assess whether liquidation would be profitable"""
        if selling_price <= 0 or fifo_rate <= 0:
            return 'UNKNOWN'
        
        margin = selling_price - fifo_rate
        margin_pct = (margin / selling_price) * 100
        
        if margin_pct >= 20:
            return 'PROFITABLE'
        elif margin_pct >= 0:
            return 'BREAK_EVEN'
        else:
            return 'LOSS_MAKING'
    
    def calculate_recommended_pricing(self, fifo_rate: float, target_margin_pct: float = 25) -> float:
        """Calculate recommended selling price based on target margin"""
        if fifo_rate <= 0:
            return 0.0
        
        # Target margin formula: Selling Price = Cost / (1 - Target Margin %)
        target_margin_decimal = target_margin_pct / 100
        recommended_price = fifo_rate / (1 - target_margin_decimal)
        
        return recommended_price
    
    def generate_strategic_action(self, result: FIFOValuationResult) -> str:
        """Generate strategic action recommendations"""
        if result.valuation_status == 'UNDERVALUED':
            if result.liquidation_feasibility == 'PROFITABLE':
                return f"OPPORTUNITY: Undervalued by ₹{abs(result.valuation_difference):,.2f} - Consider price increase or promotional push"
            else:
                return f"REVIEW: Undervalued stock with limited margin - Optimize cost structure"
        
        elif result.valuation_status == 'OVERVALUED':
            if result.liquidation_feasibility == 'LOSS_MAKING':
                return f"RISK: Overvalued by ₹{result.valuation_difference:,.2f} - Consider writedown or deep discount"
            else:
                return f"ADJUST: Overvalued but sellable - Moderate pricing adjustment needed"
        
        elif result.liquidation_feasibility == 'PROFITABLE':
            return f"OPTIMIZE: Good margin potential (₹{result.price_realization_potential:,.2f}) - Maintain current strategy"
        
        elif result.liquidation_feasibility == 'LOSS_MAKING':
            return f"CONCERN: Below-cost selling price - Review pricing strategy or reduce procurement cost"
        
        else:
            return f"MONITOR: Fair valuation - Continue regular operations"
    
    def process_valuation_analysis(self) -> Tuple[List[FIFOValuationResult], Dict[str, CategoryValuation]]:
        """Process complete inventory valuation analysis"""
        print("💰 Starting FIFO Inventory Valuation Analysis...")
        
        # Load data
        df = self.load_inventory_data()
        if df.empty:
            return [], {}
        
        results = []
        category_stats = {}
        
        # Process each inventory item
        for _, row in df.iterrows():
            try:
                # Extract data
                closing_units = int(row.get('Closing Stock No. of Units', 0))
                current_stock_value = float(row.get('Closing Stock Total amount', 0))
                current_rate = float(row.get('Closing Stock Rate per Unit', 0))
                
                # Skip items with no closing stock
                if closing_units <= 0:
                    continue
                
                # Extract FIFO calculation inputs
                opening_units = int(row.get('Opening No. of Units', 0))
                opening_rate = float(row.get('Opening Stock Rate per Unit', 0))
                purchased_units = int(row.get('Purchased No. of Units', 0))
                purchase_rate = float(row.get('Purchase Rate per unit', 0))
                
                # Market pricing
                selling_price = float(row.get('Rate per Unit', 0))  # This appears to be selling rate
                market_value = selling_price * closing_units
                
                # Calculate FIFO valuation
                fifo_stock_value, fifo_rate = self.calculate_fifo_valuation(
                    opening_units, opening_rate, purchased_units, purchase_rate, closing_units
                )
                
                # Calculate differences and analysis
                valuation_difference = current_stock_value - fifo_stock_value
                valuation_difference_pct = (valuation_difference / fifo_stock_value * 100) if fifo_stock_value > 0 else 0
                
                price_realization_potential = market_value - fifo_stock_value
                price_realization_pct = (price_realization_potential / fifo_stock_value * 100) if fifo_stock_value > 0 else 0
                
                # Strategic analysis
                valuation_status = self.determine_valuation_status(current_stock_value, fifo_stock_value)
                liquidation_feasibility = self.assess_liquidation_feasibility(fifo_rate, selling_price)
                recommended_pricing = self.calculate_recommended_pricing(fifo_rate)
                
                # Create result
                result = FIFOValuationResult(
                    isbn=str(row.get('ISBN', '')),
                    book_title=str(row.get('Book Title', '')),
                    category=str(row.get('Category', 'Unknown')),
                    publisher=str(row.get('Publisher', '')),
                    closing_units=closing_units,
                    current_stock_value=current_stock_value,
                    current_rate_per_unit=current_rate,
                    fifo_stock_value=fifo_stock_value,
                    fifo_rate_per_unit=fifo_rate,
                    selling_price=selling_price,
                    market_value=market_value,
                    valuation_difference=valuation_difference,
                    valuation_difference_pct=valuation_difference_pct,
                    price_realization_potential=price_realization_potential,
                    price_realization_pct=price_realization_pct,
                    valuation_status=valuation_status,
                    liquidation_feasibility=liquidation_feasibility,
                    recommended_pricing=recommended_pricing,
                    strategic_action=''
                )
                
                # Generate strategic action
                result.strategic_action = self.generate_strategic_action(result)
                
                results.append(result)
                
                # Update category statistics
                category = result.category
                if category not in category_stats:
                    category_stats[category] = {
                        'total_items': 0,
                        'current_book_value': 0.0,
                        'fifo_book_value': 0.0,
                        'market_value': 0.0,
                        'total_units': 0,
                        'price_realizations': [],
                        'undervalued_items': 0,
                        'overvalued_items': 0
                    }
                
                stats = category_stats[category]
                stats['total_items'] += 1
                stats['current_book_value'] += current_stock_value
                stats['fifo_book_value'] += fifo_stock_value
                stats['market_value'] += market_value
                stats['total_units'] += closing_units
                stats['price_realizations'].append(price_realization_pct)
                
                if valuation_status == 'UNDERVALUED':
                    stats['undervalued_items'] += 1
                elif valuation_status == 'OVERVALUED':
                    stats['overvalued_items'] += 1
                
            except Exception as e:
                print(f"⚠️ Error processing row: {e}")
                continue
        
        # Create category analysis
        category_analysis = {}
        for category, stats in category_stats.items():
            avg_price_realization = np.mean(stats['price_realizations']) if stats['price_realizations'] else 0
            
            category_analysis[category] = CategoryValuation(
                category=category,
                total_items=stats['total_items'],
                current_book_value=stats['current_book_value'],
                fifo_book_value=stats['fifo_book_value'],
                market_value=stats['market_value'],
                total_units=stats['total_units'],
                avg_price_realization_pct=avg_price_realization,
                undervalued_items=stats['undervalued_items'],
                overvalued_items=stats['overvalued_items']
            )
        
        # Save results
        self.save_valuation_results(results, category_analysis)
        
        print(f"✅ Valuation Analysis Complete!")
        print(f"   📊 {len(results)} items analyzed")
        print(f"   📂 {len(category_analysis)} categories processed")
        print(f"   📁 Results saved to: inventory_valuation_analysis.xlsx")
        
        return results, category_analysis
    
    def save_valuation_results(self, results: List[FIFOValuationResult], category_analysis: Dict[str, CategoryValuation]):
        """Save valuation analysis results to Excel"""
        
        # Item analysis data
        items_data = []
        for result in results:
            items_data.append({
                'ISBN': result.isbn,
                'Book_Title': result.book_title,
                'Category': result.category,
                'Publisher': result.publisher,
                'Closing_Units': result.closing_units,
                'Current_Stock_Value': result.current_stock_value,
                'Current_Rate_Per_Unit': result.current_rate_per_unit,
                'FIFO_Stock_Value': result.fifo_stock_value,
                'FIFO_Rate_Per_Unit': result.fifo_rate_per_unit,
                'Selling_Price': result.selling_price,
                'Market_Value': result.market_value,
                'Valuation_Difference': result.valuation_difference,
                'Valuation_Difference_Pct': result.valuation_difference_pct,
                'Price_Realization_Potential': result.price_realization_potential,
                'Price_Realization_Pct': result.price_realization_pct,
                'Valuation_Status': result.valuation_status,
                'Liquidation_Feasibility': result.liquidation_feasibility,
                'Recommended_Pricing': result.recommended_pricing,
                'Strategic_Action': result.strategic_action
            })
        
        items_df = pd.DataFrame(items_data)
        
        # Category analysis data
        category_data = []
        for category, analysis in category_analysis.items():
            category_data.append({
                'Category': analysis.category,
                'Total_Items': analysis.total_items,
                'Current_Book_Value': analysis.current_book_value,
                'FIFO_Book_Value': analysis.fifo_book_value,
                'Market_Value': analysis.market_value,
                'Total_Units': analysis.total_units,
                'Avg_Price_Realization_Pct': analysis.avg_price_realization_pct,
                'Undervalued_Items': analysis.undervalued_items,
                'Overvalued_Items': analysis.overvalued_items,
                'Valuation_Accuracy_Pct': ((analysis.total_items - analysis.undervalued_items - analysis.overvalued_items) / analysis.total_items * 100) if analysis.total_items > 0 else 0
            })
        
        category_df = pd.DataFrame(category_data)
        
        # Save to Excel with timestamp to avoid permission conflicts
        from datetime import datetime
        import os
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'reports/inventory_valuation_analysis_{timestamp}.xlsx'
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                items_df.to_excel(writer, sheet_name='FIFO_Valuation_Analysis', index=False)
                category_df.to_excel(writer, sheet_name='Category_Valuation', index=False)
                
                # Executive summary
                total_current_value = sum([r.current_stock_value for r in results])
                total_fifo_value = sum([r.fifo_stock_value for r in results])
                total_market_value = sum([r.market_value for r in results])
                
                summary_data = {
                    'Metric': [
                        'Total Items Analyzed',
                        'Total Current Book Value',
                        'Total FIFO Book Value',
                        'Total Market Value',
                        'Valuation Difference (Current vs FIFO)',
                        'Market Premium over FIFO',
                        'Undervalued Items',
                        'Overvalued Items',
                        'Fair Valued Items',
                        'Profitable Liquidation Items',
                        'Loss-Making Liquidation Items'
                    ],
                    'Value': [
                        len(results),
                        total_current_value,
                        total_fifo_value,
                        total_market_value,
                        total_current_value - total_fifo_value,
                        total_market_value - total_fifo_value,
                        len([r for r in results if r.valuation_status == 'UNDERVALUED']),
                        len([r for r in results if r.valuation_status == 'OVERVALUED']),
                        len([r for r in results if r.valuation_status == 'FAIR_VALUE']),
                        len([r for r in results if r.liquidation_feasibility == 'PROFITABLE']),
                        len([r for r in results if r.liquidation_feasibility == 'LOSS_MAKING'])
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
    """Demo execution of Inventory Valuation Analysis"""
    engine = InventoryValuationAnalysisEngine()
    results, category_analysis = engine.process_valuation_analysis()
    
    if not results:
        print("❌ No valuation analysis results to display")
        return
    
    print("\n" + "="*80)
    print("💰 FIFO INVENTORY VALUATION ANALYSIS - EXECUTIVE SUMMARY")
    print("="*80)
    
    # Overall statistics
    total_items = len(results)
    total_current_value = sum([r.current_stock_value for r in results])
    total_fifo_value = sum([r.fifo_stock_value for r in results])
    total_market_value = sum([r.market_value for r in results])
    
    valuation_difference = total_current_value - total_fifo_value
    market_premium = total_market_value - total_fifo_value
    
    print(f"📊 Valuation Overview:")
    print(f"   • Total Items: {total_items}")
    print(f"   • Current Book Value: ₹{total_current_value:,.2f}")
    print(f"   • FIFO Book Value: ₹{total_fifo_value:,.2f}")
    print(f"   • Market Value: ₹{total_market_value:,.2f}")
    
    print(f"\n🔍 Valuation Analysis:")
    print(f"   • Book Value vs FIFO Difference: ₹{valuation_difference:+,.2f}")
    print(f"   • Market Premium over FIFO: ₹{market_premium:+,.2f} ({market_premium/total_fifo_value*100:+.1f}%)")
    
    # Valuation status breakdown
    undervalued = len([r for r in results if r.valuation_status == 'UNDERVALUED'])
    overvalued = len([r for r in results if r.valuation_status == 'OVERVALUED'])
    fair_valued = len([r for r in results if r.valuation_status == 'FAIR_VALUE'])
    
    print(f"\n📈 Valuation Status:")
    print(f"   • Undervalued Items: {undervalued} ({undervalued/total_items*100:.1f}%)")
    print(f"   • Overvalued Items: {overvalued} ({overvalued/total_items*100:.1f}%)")
    print(f"   • Fair Valued Items: {fair_valued} ({fair_valued/total_items*100:.1f}%)")
    
    # Liquidation feasibility
    profitable = len([r for r in results if r.liquidation_feasibility == 'PROFITABLE'])
    break_even = len([r for r in results if r.liquidation_feasibility == 'BREAK_EVEN'])
    loss_making = len([r for r in results if r.liquidation_feasibility == 'LOSS_MAKING'])
    
    print(f"\n💹 Liquidation Feasibility:")
    print(f"   • Profitable to Liquidate: {profitable} ({profitable/total_items*100:.1f}%)")
    print(f"   • Break-even Liquidation: {break_even} ({break_even/total_items*100:.1f}%)")
    print(f"   • Loss-making Liquidation: {loss_making} ({loss_making/total_items*100:.1f}%)")
    
    # Top opportunities and risks
    undervalued_items = [r for r in results if r.valuation_status == 'UNDERVALUED']
    undervalued_items.sort(key=lambda x: abs(x.valuation_difference), reverse=True)
    
    if undervalued_items:
        print(f"\n🚀 Top Undervalued Opportunities:")
        for item in undervalued_items[:5]:
            print(f"   • {item.book_title[:50]}...")
            print(f"     Undervalued by ₹{abs(item.valuation_difference):,.2f} | Market potential: ₹{item.price_realization_potential:,.2f}")
    
    # Category performance
    print(f"\n📚 Category Performance:")
    sorted_categories = sorted(category_analysis.values(), key=lambda x: x.avg_price_realization_pct, reverse=True)
    for cat in sorted_categories[:5]:
        print(f"   • {cat.category}: {cat.avg_price_realization_pct:.1f}% avg realization | {cat.undervalued_items}/{cat.total_items} undervalued")

if __name__ == "__main__":
    main()