#!/usr/bin/env python3
"""
ABC Book House - Profitability Analysis Engine
Final Task: Comprehensive Profitability Analysis

This module performs detailed profitability analysis including:
1. Vendor-wise margin analysis
2. Category-wise profitability ranking  
3. SKU-level gross margin calculation
4. Top performers and negative margin identification
5. Strategic profitability recommendations

Author: AI Assistant
Date: October 4, 2025
Version: 1.0.0
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import openpyxl
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import BarChart, Reference, LineChart
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SKUProfitability:
    """Data class for individual SKU profitability metrics"""
    sku_code: str
    product_name: str
    category: str
    vendor: str
    purchase_rate: float
    selling_price: float
    gross_margin_amount: float
    gross_margin_percentage: float
    quantity_in_stock: int
    stock_value: float
    potential_revenue: float
    contribution_to_profit: float
    profitability_rank: int
    is_negative_margin: bool
    
@dataclass 
class VendorProfitability:
    """Data class for vendor profitability analysis"""
    vendor_name: str
    total_products: int
    total_stock_value: float
    total_potential_revenue: float
    total_margin_amount: float
    average_margin_percentage: float
    best_performing_product: str
    worst_performing_product: str
    negative_margin_products: int
    profitability_rank: int

@dataclass
class CategoryProfitability:
    """Data class for category profitability analysis"""
    category_name: str
    total_products: int
    total_stock_value: float
    total_potential_revenue: float
    total_margin_amount: float
    average_margin_percentage: float
    top_product: str
    negative_margin_products: int
    profitability_score: float
    market_share_percentage: float

@dataclass
class ProfitabilityAnalysisResult:
    """Comprehensive profitability analysis results"""
    analysis_timestamp: datetime
    total_skus_analyzed: int
    total_categories: int
    total_vendors: int
    
    # Overall metrics
    portfolio_stock_value: float
    portfolio_potential_revenue: float
    portfolio_gross_margin: float
    portfolio_margin_percentage: float
    
    # SKU Analysis
    sku_profitability: List[SKUProfitability] = field(default_factory=list)
    top_5_profitable_skus: List[SKUProfitability] = field(default_factory=list)
    negative_margin_skus: List[SKUProfitability] = field(default_factory=list)
    
    # Vendor Analysis
    vendor_profitability: List[VendorProfitability] = field(default_factory=list)
    best_vendors: List[VendorProfitability] = field(default_factory=list)
    worst_vendors: List[VendorProfitability] = field(default_factory=list)
    
    # Category Analysis
    category_profitability: List[CategoryProfitability] = field(default_factory=list)
    most_profitable_categories: List[CategoryProfitability] = field(default_factory=list)
    least_profitable_categories: List[CategoryProfitability] = field(default_factory=list)
    
    # Strategic insights
    profitability_insights: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)

class ProfitabilityAnalysisEngine:
    """
    Advanced Profitability Analysis Engine for ABC Book House
    Analyzes vendor performance, category profitability, and SKU margins
    """
    
    def __init__(self):
        self.data_file = "data/ABC_Book_Stores_Inventory_Register.xlsx"
        self.output_file = "profitability_analysis.xlsx"
        self.df = None
        
    def load_inventory_data(self) -> bool:
        """Load and validate inventory data"""
        try:
            logger.info("📊 Loading Inventory Data for Profitability Analysis...")
            
            if not Path(self.data_file).exists():
                logger.error(f"❌ Data file not found: {self.data_file}")
                return False
                
            # Load the inventory register
            self.df = pd.read_excel(self.data_file, sheet_name='Inventory Register')
            logger.info(f"✅ Loaded {len(self.df)} inventory records")
            
            # Map actual column names to standard names
            column_mapping = {
                'Book Title': 'Product Name',
                'Opening No. of Units': 'Opening Stock',
                'Purchase Rate per unit': 'Purchase Rate',
                'Rate per Unit': 'Selling Price'  # Using Rate per Unit as selling price
            }
            
            # Rename columns
            self.df = self.df.rename(columns=column_mapping)
            
            # Validate required columns
            required_cols = ['Product Name', 'Category', 'Opening Stock', 'Purchase Rate', 'Selling Price']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            
            if missing_cols:
                logger.error(f"❌ Missing required columns: {missing_cols}")
                return False
                
            # Clean and prepare data
            self.df = self.df.dropna(subset=['Product Name', 'Purchase Rate', 'Selling Price'])
            self.df['Opening Stock'] = pd.to_numeric(self.df['Opening Stock'], errors='coerce').fillna(0)
            self.df['Purchase Rate'] = pd.to_numeric(self.df['Purchase Rate'], errors='coerce').fillna(0)
            self.df['Selling Price'] = pd.to_numeric(self.df['Selling Price'], errors='coerce').fillna(0)
            
            # Use Publisher as Vendor, fallback to extracted vendor from product name
            if 'Publisher' in self.df.columns:
                self.df['Vendor'] = self.df['Publisher'].fillna('Unknown Publisher')
            else:
                self.df['Vendor'] = self.df['Product Name'].apply(self._extract_vendor)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading inventory data: {e}")
            return False
    
    def _extract_vendor(self, product_name: str) -> str:
        """Extract vendor/publisher from product name"""
        if pd.isna(product_name):
            return "Unknown"
            
        # Common publisher patterns
        publishers = {
            'Penguin': ['Penguin', 'penguin'],
            'HarperCollins': ['Harper', 'harper'],
            'Random House': ['Random', 'random'],
            'Macmillan': ['Macmillan', 'macmillan'],
            'Bloomsbury': ['Bloomsbury', 'bloomsbury'],
            'Oxford': ['Oxford', 'oxford'],
            'Cambridge': ['Cambridge', 'cambridge'],
            'Wiley': ['Wiley', 'wiley'],
            'McGraw': ['McGraw', 'mcgraw'],
            'Pearson': ['Pearson', 'pearson']
        }
        
        product_lower = str(product_name).lower()
        
        for publisher, keywords in publishers.items():
            if any(keyword.lower() in product_lower for keyword in keywords):
                return publisher
                
        # If no specific publisher found, create vendor based on category or first word
        words = str(product_name).split()
        if len(words) > 1:
            return f"{words[0]} Publications"
        else:
            return "Independent Publisher"
    
    def calculate_sku_profitability(self) -> List[SKUProfitability]:
        """Calculate profitability metrics for each SKU"""
        logger.info("💰 Calculating SKU-level profitability...")
        
        sku_profitability = []
        
        for idx, row in self.df.iterrows():
            try:
                # Basic data
                product_name = str(row.get('Product Name', ''))
                category = str(row.get('Category', 'Uncategorized'))
                vendor = str(row.get('Vendor', 'Unknown'))
                purchase_rate = float(row.get('Purchase Rate', 0))
                selling_price = float(row.get('Selling Price', 0))
                quantity = int(row.get('Opening Stock', 0))
                
                # Calculate profitability metrics
                gross_margin_amount = selling_price - purchase_rate
                gross_margin_percentage = (gross_margin_amount / selling_price * 100) if selling_price > 0 else 0
                stock_value = quantity * purchase_rate
                potential_revenue = quantity * selling_price
                contribution_to_profit = quantity * gross_margin_amount
                
                # Create SKU profitability object
                sku = SKUProfitability(
                    sku_code=f"SKU-{idx+1:03d}",
                    product_name=product_name,
                    category=category,
                    vendor=vendor,
                    purchase_rate=purchase_rate,
                    selling_price=selling_price,
                    gross_margin_amount=gross_margin_amount,
                    gross_margin_percentage=gross_margin_percentage,
                    quantity_in_stock=quantity,
                    stock_value=stock_value,
                    potential_revenue=potential_revenue,
                    contribution_to_profit=contribution_to_profit,
                    profitability_rank=0,  # Will be calculated later
                    is_negative_margin=gross_margin_amount < 0
                )
                
                sku_profitability.append(sku)
                
            except Exception as e:
                logger.warning(f"⚠️ Error processing row {idx}: {e}")
                continue
        
        # Rank SKUs by contribution to profit
        sku_profitability.sort(key=lambda x: x.contribution_to_profit, reverse=True)
        for rank, sku in enumerate(sku_profitability, 1):
            sku.profitability_rank = rank
            
        logger.info(f"✅ Calculated profitability for {len(sku_profitability)} SKUs")
        return sku_profitability
    
    def analyze_vendor_profitability(self, sku_data: List[SKUProfitability]) -> List[VendorProfitability]:
        """Analyze profitability by vendor/supplier"""
        logger.info("🏢 Analyzing vendor profitability...")
        
        vendor_data = {}
        
        # Aggregate data by vendor
        for sku in sku_data:
            vendor = sku.vendor
            if vendor not in vendor_data:
                vendor_data[vendor] = {
                    'products': [],
                    'total_stock_value': 0,
                    'total_potential_revenue': 0,
                    'total_margin_amount': 0,
                    'negative_margins': 0
                }
            
            vendor_info = vendor_data[vendor]
            vendor_info['products'].append(sku)
            vendor_info['total_stock_value'] += sku.stock_value
            vendor_info['total_potential_revenue'] += sku.potential_revenue
            vendor_info['total_margin_amount'] += sku.contribution_to_profit
            
            if sku.is_negative_margin:
                vendor_info['negative_margins'] += 1
        
        # Create vendor profitability objects
        vendor_profitability = []
        
        for vendor_name, data in vendor_data.items():
            products = data['products']
            
            # Calculate metrics
            total_products = len(products)
            avg_margin_pct = np.mean([p.gross_margin_percentage for p in products])
            
            # Find best and worst products
            best_product = max(products, key=lambda x: x.gross_margin_percentage)
            worst_product = min(products, key=lambda x: x.gross_margin_percentage)
            
            vendor_prof = VendorProfitability(
                vendor_name=vendor_name,
                total_products=total_products,
                total_stock_value=data['total_stock_value'],
                total_potential_revenue=data['total_potential_revenue'],
                total_margin_amount=data['total_margin_amount'],
                average_margin_percentage=avg_margin_pct,
                best_performing_product=best_product.product_name,
                worst_performing_product=worst_product.product_name,
                negative_margin_products=data['negative_margins'],
                profitability_rank=0  # Will be calculated later
            )
            
            vendor_profitability.append(vendor_prof)
        
        # Rank vendors by total margin amount
        vendor_profitability.sort(key=lambda x: x.total_margin_amount, reverse=True)
        for rank, vendor in enumerate(vendor_profitability, 1):
            vendor.profitability_rank = rank
            
        logger.info(f"✅ Analyzed {len(vendor_profitability)} vendors")
        return vendor_profitability
    
    def analyze_category_profitability(self, sku_data: List[SKUProfitability]) -> List[CategoryProfitability]:
        """Analyze profitability by product category"""
        logger.info("📚 Analyzing category profitability...")
        
        category_data = {}
        total_portfolio_value = sum(sku.stock_value for sku in sku_data)
        
        # Aggregate data by category
        for sku in sku_data:
            category = sku.category
            if category not in category_data:
                category_data[category] = {
                    'products': [],
                    'total_stock_value': 0,
                    'total_potential_revenue': 0,
                    'total_margin_amount': 0,
                    'negative_margins': 0
                }
            
            cat_info = category_data[category]
            cat_info['products'].append(sku)
            cat_info['total_stock_value'] += sku.stock_value
            cat_info['total_potential_revenue'] += sku.potential_revenue
            cat_info['total_margin_amount'] += sku.contribution_to_profit
            
            if sku.is_negative_margin:
                cat_info['negative_margins'] += 1
        
        # Create category profitability objects
        category_profitability = []
        
        for category_name, data in category_data.items():
            products = data['products']
            
            # Calculate metrics
            total_products = len(products)
            avg_margin_pct = np.mean([p.gross_margin_percentage for p in products])
            market_share = (data['total_stock_value'] / total_portfolio_value * 100) if total_portfolio_value > 0 else 0
            
            # Calculate profitability score (weighted by margin and volume)
            profitability_score = (avg_margin_pct * 0.7) + (market_share * 0.3)
            
            # Find top product
            top_product = max(products, key=lambda x: x.contribution_to_profit)
            
            category_prof = CategoryProfitability(
                category_name=category_name,
                total_products=total_products,
                total_stock_value=data['total_stock_value'],
                total_potential_revenue=data['total_potential_revenue'],
                total_margin_amount=data['total_margin_amount'],
                average_margin_percentage=avg_margin_pct,
                top_product=top_product.product_name,
                negative_margin_products=data['negative_margins'],
                profitability_score=profitability_score,
                market_share_percentage=market_share
            )
            
            category_profitability.append(category_prof)
        
        # Sort by profitability score
        category_profitability.sort(key=lambda x: x.profitability_score, reverse=True)
        
        logger.info(f"✅ Analyzed {len(category_profitability)} categories")
        return category_profitability
    
    def generate_insights_and_recommendations(self, result: ProfitabilityAnalysisResult) -> None:
        """Generate strategic insights and recommendations"""
        logger.info("🧠 Generating strategic insights...")
        
        # Calculate key insights
        insights = {}
        
        # Portfolio insights
        insights['portfolio_health'] = {
            'total_margin_amount': result.portfolio_gross_margin,
            'margin_percentage': result.portfolio_margin_percentage,
            'negative_margin_count': len(result.negative_margin_skus),
            'negative_margin_percentage': len(result.negative_margin_skus) / result.total_skus_analyzed * 100
        }
        
        # Vendor insights
        insights['vendor_performance'] = {
            'best_vendor': result.best_vendors[0].vendor_name if result.best_vendors else "None",
            'worst_vendor': result.worst_vendors[-1].vendor_name if result.worst_vendors else "None",
            'vendor_concentration': len(result.vendor_profitability)
        }
        
        # Category insights
        insights['category_performance'] = {
            'most_profitable_category': result.most_profitable_categories[0].category_name if result.most_profitable_categories else "None",
            'least_profitable_category': result.least_profitable_categories[-1].category_name if result.least_profitable_categories else "None",
            'category_diversification': len(result.category_profitability)
        }
        
        result.profitability_insights = insights
        
        # Generate recommendations
        recommendations = []
        
        # Negative margin recommendations
        if result.negative_margin_skus:
            recommendations.append(f"URGENT: Address {len(result.negative_margin_skus)} products with negative margins immediately")
            recommendations.append("Consider price increases or supplier negotiations for loss-making products")
        
        # Vendor recommendations
        if result.best_vendors:
            best_vendor = result.best_vendors[0]
            recommendations.append(f"Expand relationship with {best_vendor.vendor_name} - highest margin vendor")
        
        if result.worst_vendors:
            worst_vendor = result.worst_vendors[-1]
            recommendations.append(f"Review partnership with {worst_vendor.vendor_name} - consider renegotiation")
        
        # Category recommendations
        if result.most_profitable_categories:
            top_category = result.most_profitable_categories[0]
            recommendations.append(f"Increase inventory investment in {top_category.category_name} category")
        
        # Top product recommendations
        if result.top_5_profitable_skus:
            recommendations.append("Focus marketing efforts on top 5 profitable products identified")
            recommendations.append("Consider increasing stock levels for high-margin, fast-moving products")
        
        # Portfolio optimization
        recommendations.append("Implement dynamic pricing based on margin analysis")
        recommendations.append("Set minimum margin thresholds for new product acquisitions")
        recommendations.append("Regular quarterly profitability reviews for continuous optimization")
        
        result.recommendations = recommendations
        logger.info(f"✅ Generated {len(recommendations)} strategic recommendations")
    
    def run_profitability_analysis(self) -> ProfitabilityAnalysisResult:
        """Execute comprehensive profitability analysis"""
        logger.info("🚀 Starting Comprehensive Profitability Analysis...")
        
        # Load data
        if not self.load_inventory_data():
            raise Exception("Failed to load inventory data")
        
        # Calculate SKU profitability
        sku_profitability = self.calculate_sku_profitability()
        
        # Vendor analysis
        vendor_profitability = self.analyze_vendor_profitability(sku_profitability)
        
        # Category analysis  
        category_profitability = self.analyze_category_profitability(sku_profitability)
        
        # Calculate portfolio metrics
        portfolio_stock_value = sum(sku.stock_value for sku in sku_profitability)
        portfolio_potential_revenue = sum(sku.potential_revenue for sku in sku_profitability)
        portfolio_gross_margin = sum(sku.contribution_to_profit for sku in sku_profitability)
        portfolio_margin_percentage = (portfolio_gross_margin / portfolio_potential_revenue * 100) if portfolio_potential_revenue > 0 else 0
        
        # Create result object
        result = ProfitabilityAnalysisResult(
            analysis_timestamp=datetime.now(),
            total_skus_analyzed=len(sku_profitability),
            total_categories=len(category_profitability),
            total_vendors=len(vendor_profitability),
            portfolio_stock_value=portfolio_stock_value,
            portfolio_potential_revenue=portfolio_potential_revenue,
            portfolio_gross_margin=portfolio_gross_margin,
            portfolio_margin_percentage=portfolio_margin_percentage,
            sku_profitability=sku_profitability,
            vendor_profitability=vendor_profitability,
            category_profitability=category_profitability
        )
        
        # Extract key segments
        result.top_5_profitable_skus = sku_profitability[:5]
        result.negative_margin_skus = [sku for sku in sku_profitability if sku.is_negative_margin]
        result.best_vendors = vendor_profitability[:3]
        result.worst_vendors = vendor_profitability[-3:] if len(vendor_profitability) >= 3 else vendor_profitability
        result.most_profitable_categories = category_profitability[:3]
        result.least_profitable_categories = category_profitability[-3:] if len(category_profitability) >= 3 else category_profitability
        
        # Generate insights and recommendations
        self.generate_insights_and_recommendations(result)
        
        logger.info("✅ Profitability Analysis Complete!")
        return result
    
    def export_to_excel(self, result: ProfitabilityAnalysisResult) -> str:
        """Export analysis results to Excel with formatting"""
        logger.info("📊 Exporting profitability analysis to Excel...")
        
        # Add timestamp to filename to avoid permission conflicts
        from datetime import datetime
        import os
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamped_filename = f'reports/profitability_analysis_{timestamp}.xlsx'
        
        # Ensure reports directory exists
        os.makedirs('reports', exist_ok=True)
        
        try:
            with pd.ExcelWriter(timestamped_filename, engine='openpyxl') as writer:
                
                # Executive Summary Sheet
                self._create_executive_summary_sheet(writer, result)
                
                # SKU Analysis Sheet
                self._create_sku_analysis_sheet(writer, result)
                
                # Vendor Analysis Sheet
                self._create_vendor_analysis_sheet(writer, result)
                
                # Category Analysis Sheet
                self._create_category_analysis_sheet(writer, result)
                
                # Recommendations Sheet
                self._create_recommendations_sheet(writer, result)
            
            logger.info(f"✅ Analysis exported to: {timestamped_filename}")
            return timestamped_filename
            
        except PermissionError:
            logger.error(f"❌ Permission denied writing to {timestamped_filename}. File may be open in another application.")
            return None
        except Exception as e:
            logger.error(f"❌ Error exporting to Excel: {e}")
            return None
    
    def _create_executive_summary_sheet(self, writer, result: ProfitabilityAnalysisResult):
        """Create executive summary sheet"""
        summary_data = {
            'Metric': [
                'Analysis Date',
                'Total SKUs Analyzed',
                'Total Categories',
                'Total Vendors',
                'Portfolio Stock Value ($)',
                'Portfolio Potential Revenue ($)',
                'Portfolio Gross Margin ($)',
                'Portfolio Margin %',
                'Negative Margin SKUs',
                'Top Performing Vendor',
                'Most Profitable Category',
                'Best Margin Product'
            ],
            'Value': [
                result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                result.total_skus_analyzed,
                result.total_categories,
                result.total_vendors,
                f"${result.portfolio_stock_value:,.2f}",
                f"${result.portfolio_potential_revenue:,.2f}",
                f"${result.portfolio_gross_margin:,.2f}",
                f"{result.portfolio_margin_percentage:.2f}%",
                len(result.negative_margin_skus),
                result.best_vendors[0].vendor_name if result.best_vendors else "N/A",
                result.most_profitable_categories[0].category_name if result.most_profitable_categories else "N/A",
                result.top_5_profitable_skus[0].product_name if result.top_5_profitable_skus else "N/A"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Executive Summary', index=False)
    
    def _create_sku_analysis_sheet(self, writer, result: ProfitabilityAnalysisResult):
        """Create SKU analysis sheet"""
        sku_data = []
        
        for sku in result.sku_profitability:
            sku_data.append({
                'Rank': sku.profitability_rank,
                'SKU Code': sku.sku_code,
                'Product Name': sku.product_name,
                'Category': sku.category,
                'Vendor': sku.vendor,
                'Purchase Rate ($)': sku.purchase_rate,
                'Selling Price ($)': sku.selling_price,
                'Gross Margin ($)': sku.gross_margin_amount,
                'Margin %': f"{sku.gross_margin_percentage:.2f}%",
                'Stock Qty': sku.quantity_in_stock,
                'Stock Value ($)': sku.stock_value,
                'Potential Revenue ($)': sku.potential_revenue,
                'Profit Contribution ($)': sku.contribution_to_profit,
                'Negative Margin': 'YES' if sku.is_negative_margin else 'NO'
            })
        
        sku_df = pd.DataFrame(sku_data)
        sku_df.to_excel(writer, sheet_name='SKU Analysis', index=False)
    
    def _create_vendor_analysis_sheet(self, writer, result: ProfitabilityAnalysisResult):
        """Create vendor analysis sheet"""
        vendor_data = []
        
        for vendor in result.vendor_profitability:
            vendor_data.append({
                'Rank': vendor.profitability_rank,
                'Vendor Name': vendor.vendor_name,
                'Total Products': vendor.total_products,
                'Stock Value ($)': vendor.total_stock_value,
                'Potential Revenue ($)': vendor.total_potential_revenue,
                'Total Margin ($)': vendor.total_margin_amount,
                'Avg Margin %': f"{vendor.average_margin_percentage:.2f}%",
                'Best Product': vendor.best_performing_product,
                'Worst Product': vendor.worst_performing_product,
                'Negative Margins': vendor.negative_margin_products
            })
        
        vendor_df = pd.DataFrame(vendor_data)
        vendor_df.to_excel(writer, sheet_name='Vendor Analysis', index=False)
    
    def _create_category_analysis_sheet(self, writer, result: ProfitabilityAnalysisResult):
        """Create category analysis sheet"""
        category_data = []
        
        for category in result.category_profitability:
            category_data.append({
                'Category Name': category.category_name,
                'Total Products': category.total_products,
                'Stock Value ($)': category.total_stock_value,
                'Potential Revenue ($)': category.total_potential_revenue,
                'Total Margin ($)': category.total_margin_amount,
                'Avg Margin %': f"{category.average_margin_percentage:.2f}%",
                'Market Share %': f"{category.market_share_percentage:.2f}%",
                'Profitability Score': f"{category.profitability_score:.2f}",
                'Top Product': category.top_product,
                'Negative Margins': category.negative_margin_products
            })
        
        category_df = pd.DataFrame(category_data)
        category_df.to_excel(writer, sheet_name='Category Analysis', index=False)
    
    def _create_recommendations_sheet(self, writer, result: ProfitabilityAnalysisResult):
        """Create recommendations sheet"""
        rec_data = []
        
        for i, recommendation in enumerate(result.recommendations, 1):
            rec_data.append({
                'Priority': i,
                'Recommendation': recommendation,
                'Impact': 'High' if i <= 3 else 'Medium' if i <= 6 else 'Low',
                'Timeline': '30 days' if i <= 3 else '90 days' if i <= 6 else '6 months'
            })
        
        rec_df = pd.DataFrame(rec_data)
        rec_df.to_excel(writer, sheet_name='Recommendations', index=False)

# Example usage and testing
if __name__ == "__main__":
    print("🚀 ABC Book House - Profitability Analysis Engine")
    print("=" * 60)
    
    try:
        # Initialize analysis engine
        engine = ProfitabilityAnalysisEngine()
        
        # Run comprehensive analysis
        result = engine.run_profitability_analysis()
        
        # Export to Excel
        output_file = engine.export_to_excel(result)
        
        # Display key results
        print(f"\n📊 PROFITABILITY ANALYSIS SUMMARY")
        print(f"{'=' * 50}")
        print(f"📅 Analysis Date: {result.analysis_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📦 Total SKUs: {result.total_skus_analyzed}")
        print(f"🏢 Total Vendors: {result.total_vendors}")
        print(f"📚 Total Categories: {result.total_categories}")
        print(f"💰 Portfolio Value: ${result.portfolio_stock_value:,.2f}")
        print(f"📈 Gross Margin: ${result.portfolio_gross_margin:,.2f} ({result.portfolio_margin_percentage:.2f}%)")
        print(f"⚠️ Negative Margin SKUs: {len(result.negative_margin_skus)}")
        
        print(f"\n🏆 TOP 5 PROFITABLE PRODUCTS:")
        for i, sku in enumerate(result.top_5_profitable_skus, 1):
            print(f"   {i}. {sku.product_name} - Margin: {sku.gross_margin_percentage:.2f}%")
        
        print(f"\n🏢 BEST VENDORS:")
        for i, vendor in enumerate(result.best_vendors, 1):
            print(f"   {i}. {vendor.vendor_name} - Avg Margin: {vendor.average_margin_percentage:.2f}%")
        
        print(f"\n📚 MOST PROFITABLE CATEGORIES:")
        for i, category in enumerate(result.most_profitable_categories, 1):
            print(f"   {i}. {category.category_name} - Score: {category.profitability_score:.2f}")
        
        if result.negative_margin_skus:
            print(f"\n⚠️ NEGATIVE MARGIN PRODUCTS:")
            for sku in result.negative_margin_skus[:5]:  # Show top 5
                print(f"   • {sku.product_name} - Margin: {sku.gross_margin_percentage:.2f}%")
        
        print(f"\n📁 Report saved to: {output_file}")
        print("✅ Profitability Analysis Complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()