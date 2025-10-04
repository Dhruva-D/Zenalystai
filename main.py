from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

# Import all extractors
from final_po_extractor import FinalPurchaseOrderParser
from grn_extractor import GRNExtractor
from purchase_invoice_extractor import PurchaseInvoiceExtractor
from sales_invoice_extractor import SalesInvoiceExtractor

# Import 3-way matching system
from matching_engine import ThreeWayMatchingEngine

# Import PO-Invoice verification system
from po_invoice_verification import POInvoiceVerificationEngine

# Import inventory analysis engines
from inventory_cost_analysis import InventoryCostAnalysisEngine
from inventory_ageing_analysis import InventoryAgeingAnalysisEngine  
from inventory_valuation_analysis import InventoryValuationAnalysisEngine
from profitability_analysis import ProfitabilityAnalysisEngine

app = FastAPI(
    title="ABC Book House - Comprehensive ETL & Analytics API", 
    version="2.0.0",
    description="Complete document processing and 3-way matching system"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize matching engine
matching_engine = ThreeWayMatchingEngine()

@app.get("/")
async def root():
    return {
        "message": "ABC Book House - Comprehensive ETL & Analytics API",
        "version": "2.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "modules": {
            "document_extraction": {
                "purchase_orders": "/extract/purchase-orders",
                "grn_records": "/extract/grn",
                "purchase_invoices": "/extract/purchase-invoices", 
                "sales_invoices": "/extract/sales-invoices",
                "all_documents": "/extract/all-documents"
            },
            "analytics": {
                "comprehensive": "/analytics/comprehensive",
                "three_way_matching": "/analytics/matching"
            },
            "matching_api": {
                "dashboard": "/api/matching/dashboard",
                "details": "/api/matching/details",
                "exceptions": "/api/matching/exceptions",
                "vendors": "/api/matching/vendors"
            }
        }
    }

# ========================= DOCUMENT EXTRACTION ENDPOINTS =========================

@app.post("/extract/purchase-orders")
async def extract_purchase_orders():
    """Extract all purchase orders from PDFs"""
    try:
        parser = FinalPurchaseOrderParser()
        po_df, items_df = parser.process_all_purchase_orders("data/Purchase Order")
        
        # Save to Excel
        parser.save_to_excel(po_df, items_df)
        
        return {
            "status": "success",
            "message": "Purchase orders extracted successfully",
            "purchase_orders": len(po_df),
            "items": len(items_df),
            "total_value": float(po_df['total_amount'].sum()) if len(po_df) > 0 else 0,
            "file_generated": "zenalyst_demo_results.xlsx"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/grn")
async def extract_grn_records():
    """Extract all GRN records from PDFs"""
    try:
        extractor = GRNExtractor()
        grn_df, items_df = extractor.process_all_grns("data/GRN Copies")
        
        # Save to Excel
        extractor.save_to_excel(grn_df, items_df)
        
        return {
            "status": "success",
            "message": "GRN records extracted successfully",
            "grn_records": len(grn_df),
            "received_items": len(items_df),
            "total_value": float(grn_df['total_value'].sum()) if len(grn_df) > 0 else 0,
            "file_generated": "grn_extracted_data.xlsx"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/purchase-invoices")
async def extract_purchase_invoices():
    """Extract all purchase invoices from PDFs"""
    try:
        extractor = PurchaseInvoiceExtractor()
        invoice_df, items_df = extractor.process_all_invoices("data/Purchase Invoice")
        
        # Save to Excel
        extractor.save_to_excel(invoice_df, items_df)
        
        return {
            "status": "success",
            "message": "Purchase invoices extracted successfully",
            "invoices": len(invoice_df),
            "billed_items": len(items_df),
            "total_value": float(invoice_df['total_amount'].sum()) if len(invoice_df) > 0 else 0,
            "file_generated": "purchase_invoices_extracted.xlsx"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/sales-invoices")
async def extract_sales_invoices():
    """Extract all sales invoices from PDFs"""
    try:
        extractor = SalesInvoiceExtractor()
        invoice_df, items_df = extractor.process_all_sales_invoices("data/Sales Invoices")
        
        # Save to Excel
        extractor.save_to_excel(invoice_df, items_df)
        
        return {
            "status": "success",
            "message": "Sales invoices extracted successfully",
            "invoices": len(invoice_df),
            "sold_items": len(items_df),
            "total_revenue": float(invoice_df['total_amount'].sum()) if len(invoice_df) > 0 else 0,
            "file_generated": "sales_invoices_extracted.xlsx"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract/all-documents")
async def extract_all_documents(background_tasks: BackgroundTasks):
    """Extract all document types in sequence"""
    try:
        results = {}
        
        # Extract Purchase Orders
        po_parser = FinalPurchaseOrderParser()
        po_df, po_items_df = po_parser.process_all_purchase_orders("data/Purchase Order")
        po_parser.save_to_excel(po_df, po_items_df)
        results['purchase_orders'] = {
            "count": len(po_df),
            "items": len(po_items_df),
            "value": float(po_df['total_amount'].sum()) if len(po_df) > 0 else 0
        }
        
        # Extract GRNs
        grn_extractor = GRNExtractor()
        grn_df, grn_items_df = grn_extractor.process_all_grns("data/GRN Copies")
        grn_extractor.save_to_excel(grn_df, grn_items_df)
        results['grn_records'] = {
            "count": len(grn_df),
            "items": len(grn_items_df),
            "value": float(grn_df['total_value'].sum()) if len(grn_df) > 0 else 0
        }
        
        # Extract Purchase Invoices
        pi_extractor = PurchaseInvoiceExtractor()
        pi_df, pi_items_df = pi_extractor.process_all_invoices("data/Purchase Invoice")
        pi_extractor.save_to_excel(pi_df, pi_items_df)
        results['purchase_invoices'] = {
            "count": len(pi_df),
            "items": len(pi_items_df),
            "value": float(pi_df['total_amount'].sum()) if len(pi_df) > 0 else 0
        }
        
        # Extract Sales Invoices
        si_extractor = SalesInvoiceExtractor()
        si_df, si_items_df = si_extractor.process_all_sales_invoices("data/Sales Invoices")
        si_extractor.save_to_excel(si_df, si_items_df)
        results['sales_invoices'] = {
            "count": len(si_df),
            "items": len(si_items_df),
            "value": float(si_df['total_amount'].sum()) if len(si_df) > 0 else 0
        }
        
        return {
            "status": "success",
            "message": "All documents extracted successfully",
            "extraction_results": results,
            "total_documents": sum([r['count'] for r in results.values()]),
            "files_generated": [
                "zenalyst_demo_results.xlsx",
                "grn_extracted_data.xlsx", 
                "purchase_invoices_extracted.xlsx",
                "sales_invoices_extracted.xlsx"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================= ANALYTICS ENDPOINTS =========================

@app.get("/analytics/comprehensive")
async def get_comprehensive_analytics():
    """Get comprehensive analytics across all document types"""
    try:
        # Trigger 3-way matching analysis
        analysis_result = matching_engine.analyze_three_way_matching()
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        return {
            "status": "success",
            "analytics": analysis_result['dashboard'].__dict__ if hasattr(analysis_result['dashboard'], '__dict__') else analysis_result['dashboard'],
            "summary": {
                "total_documents_analyzed": len(analysis_result['matching_results']),
                "total_exceptions": len(analysis_result['exceptions']),
                "vendor_count": len(analysis_result['vendor_performance']),
                "processing_time": analysis_result.get('processing_time', 0)
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analytics/matching")
async def get_matching_analysis():
    """Get 3-way matching analysis"""
    try:
        analysis_result = matching_engine.analyze_three_way_matching()
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        # Convert objects to dictionaries for JSON serialization
        serialized_result = {
            'dashboard': analysis_result['dashboard'].__dict__ if hasattr(analysis_result['dashboard'], '__dict__') else analysis_result['dashboard'],
            'matching_results': [r.__dict__ if hasattr(r, '__dict__') else r for r in analysis_result['matching_results']],
            'exceptions': [e.__dict__ if hasattr(e, '__dict__') else e for e in analysis_result['exceptions']],
            'vendor_performance': [v.__dict__ if hasattr(v, '__dict__') else v for v in analysis_result['vendor_performance']],
            'charts': analysis_result.get('charts', {}),
            'processing_time': analysis_result.get('processing_time', 0)
        }
        
        return serialized_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================= 3-WAY MATCHING API ENDPOINTS =========================

@app.get("/api/matching/dashboard")
async def get_matching_dashboard():
    """Get dashboard data for 3-way matching"""
    try:
        analysis_result = matching_engine.analyze_three_way_matching()
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        return {
            "dashboard": analysis_result['dashboard'].__dict__ if hasattr(analysis_result['dashboard'], '__dict__') else analysis_result['dashboard'],
            "charts": analysis_result.get('charts', {}),
            "last_updated": datetime.now().isoformat(),
            "processing_time": analysis_result.get('processing_time', 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/matching/details")
async def get_matching_details(
    page: int = 1,
    page_size: int = 50,
    status_filter: str = None
):
    """Get detailed matching results with pagination"""
    try:
        analysis_result = matching_engine.analyze_three_way_matching()
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        results = analysis_result['matching_results']
        
        # Apply status filter
        if status_filter:
            results = [r for r in results if (hasattr(r, 'status') and r.status.value == status_filter)]
        
        # Apply pagination
        total_records = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
        return {
            "results": [r.__dict__ if hasattr(r, '__dict__') else r for r in paginated_results],
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": (total_records + page_size - 1) // page_size
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/matching/exceptions")
async def get_matching_exceptions(severity: str = None):
    """Get exception reports"""
    try:
        analysis_result = matching_engine.analyze_three_way_matching()
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        exceptions = analysis_result['exceptions']
        
        # Apply severity filter
        if severity:
            exceptions = [e for e in exceptions if (hasattr(e, 'severity') and e.severity.value == severity)]
        
        return {
            "exceptions": [e.__dict__ if hasattr(e, '__dict__') else e for e in exceptions],
            "total_exceptions": len(exceptions),
            "severity_counts": {
                "critical": len([e for e in analysis_result['exceptions'] if hasattr(e, 'severity') and e.severity.value == 'critical']),
                "high": len([e for e in analysis_result['exceptions'] if hasattr(e, 'severity') and e.severity.value == 'high']),
                "medium": len([e for e in analysis_result['exceptions'] if hasattr(e, 'severity') and e.severity.value == 'medium']),
                "low": len([e for e in analysis_result['exceptions'] if hasattr(e, 'severity') and e.severity.value == 'low'])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/matching/vendors")
async def get_vendor_performance():
    """Get vendor performance analysis"""
    try:
        analysis_result = matching_engine.analyze_three_way_matching()
        
        if 'error' in analysis_result:
            raise HTTPException(status_code=500, detail=analysis_result['error'])
        
        vendors = analysis_result['vendor_performance']
        
        return {
            "vendors": [v.__dict__ if hasattr(v, '__dict__') else v for v in vendors],
            "total_vendors": len(vendors),
            "top_performer": vendors[0].__dict__ if vendors and hasattr(vendors[0], '__dict__') else (vendors[0] if vendors else None),
            "average_compliance": sum([v.compliance_score if hasattr(v, 'compliance_score') else 0 for v in vendors]) / len(vendors) if vendors else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================= PO-INVOICE VERIFICATION ENDPOINTS =========================

@app.post("/verify/po-invoice")
async def verify_po_invoice():
    """Run comprehensive PO-Invoice verification analysis"""
    try:
        verification_engine = POInvoiceVerificationEngine()
        results_df, vendor_performance = verification_engine.process_all_verifications()
        
        if len(results_df) == 0:
            raise HTTPException(status_code=404, detail="No PO-Invoice data found for verification")
        
        # Calculate summary statistics
        total_verifications = len(results_df)
        matched = len(results_df[results_df['Verification_Status'] == 'MATCHED'])
        excess = len(results_df[results_df['Verification_Status'] == 'EXCESS'])
        short = len(results_df[results_df['Verification_Status'] == 'SHORT'])
        price_var = len(results_df[results_df['Verification_Status'] == 'PRICE_VARIANCE'])
        mismatch = len(results_df[results_df['Verification_Status'] == 'MISMATCH'])
        
        critical_issues = len(results_df[results_df['Severity'] == 'CRITICAL'])
        high_issues = len(results_df[results_df['Severity'] == 'HIGH'])
        
        return {
            "status": "success",
            "message": "PO-Invoice verification completed successfully",
            "summary": {
                "total_verifications": total_verifications,
                "perfect_matches": matched,
                "excess_procurement": excess,
                "short_procurement": short,
                "price_variances": price_var,
                "item_mismatches": mismatch,
                "critical_issues": critical_issues,
                "high_priority_issues": high_issues,
                "match_rate_pct": round((matched / total_verifications) * 100, 1),
                "compliance_issues_pct": round(((excess + short + mismatch) / total_verifications) * 100, 1)
            },
            "financial_impact": {
                "total_po_value": float(results_df['PO_Amount'].sum()),
                "total_invoice_value": float(results_df['Invoice_Amount'].sum()),
                "net_variance": float(results_df['Amount_Variance'].sum()),
                "variance_pct": round((results_df['Amount_Variance'].sum() / results_df['PO_Amount'].sum()) * 100, 2) if results_df['PO_Amount'].sum() > 0 else 0
            },
            "vendor_count": len(vendor_performance),
            "file_generated": "po_invoice_verification_results.xlsx",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verify/po-invoice/dashboard")
async def get_verification_dashboard():
    """Get PO-Invoice verification dashboard data"""
    try:
        # Check if verification results exist
        results_file = Path("po_invoice_verification_results.xlsx")
        if not results_file.exists():
            # Run verification if results don't exist
            verification_engine = POInvoiceVerificationEngine()
            results_df, vendor_performance = verification_engine.process_all_verifications()
        else:
            # Load existing results
            results_df = pd.read_excel("po_invoice_verification_results.xlsx", sheet_name="Verification_Results")
            vendor_df = pd.read_excel("po_invoice_verification_results.xlsx", sheet_name="Vendor_Performance")
        
        # Calculate dashboard metrics
        total_verifications = len(results_df)
        status_counts = results_df['Verification_Status'].value_counts().to_dict()
        severity_counts = results_df['Severity'].value_counts().to_dict()
        
        # Top issues requiring attention
        critical_issues = results_df[results_df['Severity'] == 'CRITICAL'].head(5).to_dict('records')
        
        return {
            "dashboard_summary": {
                "total_verifications": total_verifications,
                "status_breakdown": status_counts,
                "severity_breakdown": severity_counts,
                "financial_summary": {
                    "total_po_value": float(results_df['PO_Amount'].sum()),
                    "total_invoice_value": float(results_df['Invoice_Amount'].sum()),
                    "net_variance": float(results_df['Amount_Variance'].sum())
                }
            },
            "critical_alerts": critical_issues,
            "charts_data": {
                "status_distribution": [{"name": k, "value": v} for k, v in status_counts.items()],
                "severity_distribution": [{"name": k, "value": v} for k, v in severity_counts.items()]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verify/po-invoice/results")
async def get_verification_results(
    status_filter: str = None,
    severity_filter: str = None,
    page: int = 1,
    page_size: int = 50
):
    """Get paginated verification results with filters"""
    try:
        results_file = Path("po_invoice_verification_results.xlsx")
        if not results_file.exists():
            raise HTTPException(status_code=404, detail="Verification results not found. Run verification first.")
        
        results_df = pd.read_excel("po_invoice_verification_results.xlsx", sheet_name="Verification_Results")
        
        # Apply filters
        if status_filter:
            results_df = results_df[results_df['Verification_Status'] == status_filter.upper()]
        
        if severity_filter:
            results_df = results_df[results_df['Severity'] == severity_filter.upper()]
        
        # Apply pagination
        total_records = len(results_df)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results_df.iloc[start_idx:end_idx].to_dict('records')
        
        return {
            "results": paginated_results,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": (total_records + page_size - 1) // page_size
            },
            "filters_applied": {
                "status": status_filter,
                "severity": severity_filter
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/verify/po-invoice/vendors")
async def get_vendor_performance():
    """Get vendor performance analysis from verification results"""
    try:
        results_file = Path("po_invoice_verification_results.xlsx")
        if not results_file.exists():
            raise HTTPException(status_code=404, detail="Verification results not found. Run verification first.")
        
        vendor_df = pd.read_excel("po_invoice_verification_results.xlsx", sheet_name="Vendor_Performance")
        
        # Convert to list of dicts for JSON response
        vendor_performance = vendor_df.to_dict('records')
        
        # Calculate overall statistics
        avg_compliance = vendor_df['Compliance_Score_Pct'].mean()
        total_vendors = len(vendor_df)
        excellent_vendors = len(vendor_df[vendor_df['Reliability_Rating'] == 'EXCELLENT'])
        poor_vendors = len(vendor_df[vendor_df['Reliability_Rating'] == 'POOR'])
        
        return {
            "vendor_performance": vendor_performance,
            "summary": {
                "total_vendors": total_vendors,
                "average_compliance_score": round(avg_compliance, 1),
                "excellent_performers": excellent_vendors,
                "poor_performers": poor_vendors,
                "total_po_value": float(vendor_df['Total_PO_Value'].sum()),
                "total_invoice_value": float(vendor_df['Total_Invoice_Value'].sum()),
                "net_financial_variance": float(vendor_df['Financial_Variance'].sum())
            },
            "charts_data": {
                "compliance_distribution": [
                    {"vendor": row['Vendor_Name'], "compliance": row['Compliance_Score_Pct']} 
                    for _, row in vendor_df.iterrows()
                ],
                "rating_distribution": vendor_df['Reliability_Rating'].value_counts().to_dict()
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========================= INVENTORY ANALYSIS ENDPOINTS =========================

@app.post("/analyze/inventory-cost")
async def analyze_inventory_cost():
    """Run comprehensive inventory cost analysis (Task 3)"""
    try:
        cost_engine = InventoryCostAnalysisEngine()
        results, category_analysis = cost_engine.process_inventory_analysis()
        
        if not results:
            raise HTTPException(status_code=404, detail="No inventory data found for cost analysis")
        
        # Calculate summary statistics
        total_items = len(results)
        total_closing_value = sum([r.closing_stock_amount for r in results])
        total_carrying_cost = sum([r.total_carrying_cost for r in results])
        obsolete_items = len([r for r in results if r.is_obsolete])
        loss_making_items = len([r for r in results if r.margin_vs_carrying_cost == 'LOSS_MAKING'])
        profitable_items = len([r for r in results if r.margin_vs_carrying_cost == 'PROFITABLE'])
        
        return {
            "status": "success",
            "message": "Inventory cost analysis completed successfully",
            "summary": {
                "total_items": total_items,
                "total_closing_value": total_closing_value,
                "total_carrying_cost": total_carrying_cost,
                "annual_carrying_cost": total_carrying_cost * 12,
                "obsolete_items": obsolete_items,
                "loss_making_items": loss_making_items,
                "profitable_items": profitable_items,
                "obsolescence_rate_pct": round((obsolete_items / total_items) * 100, 1),
                "profitability_rate_pct": round((profitable_items / total_items) * 100, 1)
            },
            "category_count": len(category_analysis),
            "file_generated": "inventory_cost_analysis.xlsx",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/inventory-ageing")
async def analyze_inventory_ageing():
    """Run comprehensive inventory ageing analysis (Task 4)"""
    try:
        ageing_engine = InventoryAgeingAnalysisEngine()
        results, ageing_buckets = ageing_engine.process_ageing_analysis()
        
        if not results:
            raise HTTPException(status_code=404, detail="No inventory data found for ageing analysis")
        
        # Calculate summary statistics
        total_items = len(results)
        total_value = sum([r.closing_stock_value for r in results])
        dead_items = len([r for r in results if r.ageing_category == 'DEAD'])
        stale_items = len([r for r in results if r.ageing_category == 'STALE'])
        critical_risk_items = len([r for r in results if r.dead_stock_risk == 'CRITICAL'])
        urgent_items = len([r for r in results if r.liquidation_priority <= 2])
        total_potential_loss = sum([r.potential_loss for r in results])
        
        return {
            "status": "success",
            "message": "Inventory ageing analysis completed successfully",
            "summary": {
                "total_items": total_items,
                "total_portfolio_value": total_value,
                "dead_stock_items": dead_items,
                "stale_stock_items": stale_items,
                "critical_risk_items": critical_risk_items,
                "urgent_action_items": urgent_items,
                "dead_stock_rate_pct": round((dead_items / total_items) * 100, 1),
                "critical_risk_rate_pct": round((critical_risk_items / total_items) * 100, 1),
                "total_potential_loss": total_potential_loss
            },
            "ageing_buckets": len(ageing_buckets),
            "file_generated": "inventory_ageing_analysis.xlsx",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/inventory-valuation")
async def analyze_inventory_valuation():
    """Run comprehensive FIFO inventory valuation analysis (Task 5)"""
    try:
        valuation_engine = InventoryValuationAnalysisEngine()
        results, category_analysis = valuation_engine.process_valuation_analysis()
        
        if not results:
            raise HTTPException(status_code=404, detail="No inventory data found for valuation analysis")
        
        # Calculate summary statistics
        total_items = len(results)
        total_current_value = sum([r.current_stock_value for r in results])
        total_fifo_value = sum([r.fifo_stock_value for r in results])
        total_market_value = sum([r.market_value for r in results])
        
        valuation_difference = total_current_value - total_fifo_value
        market_premium = total_market_value - total_fifo_value
        
        undervalued = len([r for r in results if r.valuation_status == 'UNDERVALUED'])
        overvalued = len([r for r in results if r.valuation_status == 'OVERVALUED'])
        profitable_liquidation = len([r for r in results if r.liquidation_feasibility == 'PROFITABLE'])
        
        return {
            "status": "success",
            "message": "FIFO inventory valuation analysis completed successfully",
            "summary": {
                "total_items": total_items,
                "current_book_value": total_current_value,
                "fifo_book_value": total_fifo_value,
                "market_value": total_market_value,
                "valuation_difference": valuation_difference,
                "market_premium": market_premium,
                "market_premium_pct": round((market_premium / total_fifo_value * 100), 1) if total_fifo_value > 0 else 0,
                "undervalued_items": undervalued,
                "overvalued_items": overvalued,
                "profitable_liquidation_items": profitable_liquidation,
                "profitable_liquidation_rate_pct": round((profitable_liquidation / total_items) * 100, 1)
            },
            "category_count": len(category_analysis),
            "file_generated": "inventory_valuation_analysis.xlsx",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analyze/inventory/dashboard")
async def get_inventory_dashboard():
    """Get comprehensive inventory analysis dashboard"""
    try:
        dashboard_data = {
            "cost_analysis": None,
            "ageing_analysis": None,
            "valuation_analysis": None
        }
        
        # Check if analysis files exist and load summary data
        cost_file = Path("inventory_cost_analysis.xlsx")
        ageing_file = Path("inventory_ageing_analysis.xlsx")
        valuation_file = Path("inventory_valuation_analysis.xlsx")
        
        if cost_file.exists():
            cost_df = pd.read_excel("inventory_cost_analysis.xlsx", sheet_name="Executive_Summary")
            dashboard_data["cost_analysis"] = {
                "available": True,
                "summary": cost_df.set_index('Metric')['Value'].to_dict()
            }
        
        if ageing_file.exists():
            ageing_df = pd.read_excel("inventory_ageing_analysis.xlsx", sheet_name="Executive_Summary")
            dashboard_data["ageing_analysis"] = {
                "available": True,
                "summary": ageing_df.set_index('Metric')['Value'].to_dict()
            }
        
        if valuation_file.exists():
            valuation_df = pd.read_excel("inventory_valuation_analysis.xlsx", sheet_name="Executive_Summary")
            dashboard_data["valuation_analysis"] = {
                "available": True,
                "summary": valuation_df.set_index('Metric')['Value'].to_dict()
            }
        
        return {
            "dashboard": dashboard_data,
            "analysis_status": {
                "cost_analysis_available": cost_file.exists(),
                "ageing_analysis_available": ageing_file.exists(),
                "valuation_analysis_available": valuation_file.exists()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze/inventory/comprehensive")
async def run_comprehensive_inventory_analysis():
    """Run all inventory analyses (Tasks 3, 4, and 5) in sequence"""
    try:
        results = {}
        
        print("🔄 Running comprehensive inventory analysis...")
        
        # Task 3: Cost Analysis
        print("📊 Running cost analysis...")
        cost_engine = InventoryCostAnalysisEngine()
        cost_results, cost_categories = cost_engine.process_inventory_analysis()
        results["cost_analysis"] = {
            "items_analyzed": len(cost_results),
            "categories": len(cost_categories),
            "obsolete_items": len([r for r in cost_results if r.is_obsolete]),
            "total_carrying_cost": sum([r.total_carrying_cost for r in cost_results])
        }
        
        # Task 4: Ageing Analysis
        print("📅 Running ageing analysis...")
        ageing_engine = InventoryAgeingAnalysisEngine()
        ageing_results, ageing_buckets = ageing_engine.process_ageing_analysis()
        results["ageing_analysis"] = {
            "items_analyzed": len(ageing_results),
            "ageing_buckets": len(ageing_buckets),
            "dead_stock_items": len([r for r in ageing_results if r.ageing_category == 'DEAD']),
            "total_potential_loss": sum([r.potential_loss for r in ageing_results])
        }
        
        # Task 5: Valuation Analysis
        print("💰 Running valuation analysis...")
        valuation_engine = InventoryValuationAnalysisEngine()
        valuation_results, valuation_categories = valuation_engine.process_valuation_analysis()
        results["valuation_analysis"] = {
            "items_analyzed": len(valuation_results),
            "categories": len(valuation_categories),
            "market_premium": sum([r.market_value - r.fifo_stock_value for r in valuation_results]),
            "profitable_liquidation_items": len([r for r in valuation_results if r.liquidation_feasibility == 'PROFITABLE'])
        }
        
        return {
            "status": "success",
            "message": "Comprehensive inventory analysis completed successfully",
            "analysis_results": results,
            "files_generated": [
                "inventory_cost_analysis.xlsx",
                "inventory_ageing_analysis.xlsx", 
                "inventory_valuation_analysis.xlsx"
            ],
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# =============================================================================
# PROFITABILITY ANALYSIS ENDPOINTS
# =============================================================================

@app.post("/analyze/profitability")
async def run_profitability_analysis():
    """
    Run comprehensive profitability analysis
    
    Analyzes:
    - Vendor-wise margin performance
    - Category-wise profitability ranking
    - SKU-level gross margin calculation
    - Top 5 most profitable products
    - Negative margin identification
    """
    try:
        print("🚀 Running profitability analysis...")
        
        # Initialize analysis engine
        engine = ProfitabilityAnalysisEngine()
        
        # Run analysis
        result = engine.run_profitability_analysis()
        
        # Export to Excel
        output_file = engine.export_to_excel(result)
        
        # Prepare response summary
        summary = {
            "total_skus": result.total_skus_analyzed,
            "total_vendors": result.total_vendors,
            "total_categories": result.total_categories,
            "portfolio_value": result.portfolio_stock_value,
            "portfolio_margin": result.portfolio_gross_margin,
            "portfolio_margin_percentage": result.portfolio_margin_percentage,
            "negative_margin_count": len(result.negative_margin_skus)
        }
        
        # Top performers
        top_products = [
            {
                "rank": i + 1,
                "product_name": sku.product_name,
                "margin_percentage": sku.gross_margin_percentage,
                "contribution": sku.contribution_to_profit
            }
            for i, sku in enumerate(result.top_5_profitable_skus)
        ]
        
        best_vendors = [
            {
                "rank": vendor.profitability_rank,
                "vendor_name": vendor.vendor_name,
                "average_margin": vendor.average_margin_percentage,
                "total_margin": vendor.total_margin_amount
            }
            for vendor in result.best_vendors
        ]
        
        profitable_categories = [
            {
                "category_name": cat.category_name,
                "profitability_score": cat.profitability_score,
                "average_margin": cat.average_margin_percentage,
                "market_share": cat.market_share_percentage
            }
            for cat in result.most_profitable_categories
        ]
        
        return {
            "status": "success",
            "message": "Profitability analysis completed successfully",
            "summary": summary,
            "top_5_products": top_products,
            "best_vendors": best_vendors,
            "profitable_categories": profitable_categories,
            "negative_margin_products": [
                {
                    "product_name": sku.product_name,
                    "vendor": sku.vendor,
                    "margin_percentage": sku.gross_margin_percentage,
                    "loss_amount": sku.contribution_to_profit
                }
                for sku in result.negative_margin_skus
            ],
            "recommendations": result.recommendations,
            "file_generated": output_file,
            "timestamp": result.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in profitability analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analyze/profitability/dashboard")
async def profitability_dashboard():
    """
    Get profitability analysis dashboard with key metrics
    """
    try:
        print("📊 Generating profitability dashboard...")
        
        # Run quick analysis for dashboard
        engine = ProfitabilityAnalysisEngine()
        result = engine.run_profitability_analysis()
        
        # Create dashboard data
        dashboard = {
            "overview": {
                "total_skus": result.total_skus_analyzed,
                "total_vendors": result.total_vendors,
                "total_categories": result.total_categories,
                "portfolio_value": f"₹{result.portfolio_stock_value:,.2f}",
                "portfolio_margin": f"₹{result.portfolio_gross_margin:,.2f}",
                "margin_percentage": f"{result.portfolio_margin_percentage:.2f}%",
                "negative_margin_skus": len(result.negative_margin_skus)
            },
            "top_performers": {
                "products": [
                    {
                        "name": sku.product_name,
                        "margin": f"{sku.gross_margin_percentage:.2f}%",
                        "contribution": f"₹{sku.contribution_to_profit:,.2f}"
                    }
                    for sku in result.top_5_profitable_skus
                ],
                "vendors": [
                    {
                        "name": vendor.vendor_name,
                        "avg_margin": f"{vendor.average_margin_percentage:.2f}%",
                        "products": vendor.total_products
                    }
                    for vendor in result.best_vendors
                ],
                "categories": [
                    {
                        "name": cat.category_name,
                        "score": f"{cat.profitability_score:.2f}",
                        "margin": f"{cat.average_margin_percentage:.2f}%"
                    }
                    for cat in result.most_profitable_categories
                ]
            },
            "alerts": []
        }
        
        # Add alerts for negative margins
        if result.negative_margin_skus:
            dashboard["alerts"].append({
                "type": "warning",
                "message": f"{len(result.negative_margin_skus)} products have negative margins",
                "action": "Review pricing or supplier negotiations"
            })
        
        # Add alerts for poor performing vendors
        if result.worst_vendors:
            worst_vendor = result.worst_vendors[-1]
            if worst_vendor.average_margin_percentage < 20:
                dashboard["alerts"].append({
                    "type": "info",
                    "message": f"{worst_vendor.vendor_name} has low margins ({worst_vendor.average_margin_percentage:.1f}%)",
                    "action": "Consider renegotiating terms"
                })
        
        return {
            "dashboard": dashboard,
            "analysis_status": "completed",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error generating profitability dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")

@app.get("/analyze/profitability/vendors")
async def get_vendor_profitability():
    """Get detailed vendor profitability analysis"""
    try:
        engine = ProfitabilityAnalysisEngine()
        result = engine.run_profitability_analysis()
        
        vendor_analysis = [
            {
                "rank": vendor.profitability_rank,
                "vendor_name": vendor.vendor_name,
                "total_products": vendor.total_products,
                "total_margin": f"₹{vendor.total_margin_amount:,.2f}",
                "average_margin_percentage": f"{vendor.average_margin_percentage:.2f}%",
                "best_product": vendor.best_performing_product,
                "worst_product": vendor.worst_performing_product,
                "negative_margins": vendor.negative_margin_products,
                "stock_value": f"₹{vendor.total_stock_value:,.2f}",
                "potential_revenue": f"₹{vendor.total_potential_revenue:,.2f}"
            }
            for vendor in result.vendor_profitability
        ]
        
        return {
            "status": "success",
            "vendor_analysis": vendor_analysis,
            "summary": {
                "total_vendors": len(vendor_analysis),
                "best_vendor": vendor_analysis[0]["vendor_name"] if vendor_analysis else None,
                "average_portfolio_margin": result.portfolio_margin_percentage
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in vendor profitability analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/analyze/profitability/categories")
async def get_category_profitability():
    """Get detailed category profitability analysis"""
    try:
        engine = ProfitabilityAnalysisEngine()
        result = engine.run_profitability_analysis()
        
        category_analysis = [
            {
                "category_name": cat.category_name,
                "total_products": cat.total_products,
                "market_share": f"{cat.market_share_percentage:.2f}%",
                "total_margin": f"₹{cat.total_margin_amount:,.2f}",
                "average_margin_percentage": f"{cat.average_margin_percentage:.2f}%",
                "profitability_score": f"{cat.profitability_score:.2f}",
                "top_product": cat.top_product,
                "negative_margins": cat.negative_margin_products,
                "stock_value": f"₹{cat.total_stock_value:,.2f}",
                "potential_revenue": f"₹{cat.total_potential_revenue:,.2f}"
            }
            for cat in result.category_profitability
        ]
        
        return {
            "status": "success",
            "category_analysis": category_analysis,
            "summary": {
                "total_categories": len(category_analysis),
                "most_profitable": category_analysis[0]["category_name"] if category_analysis else None,
                "average_portfolio_margin": result.portfolio_margin_percentage
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ Error in category profitability analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "4.0.0",
        "api_endpoints": 26,
        "features": [
            "Document Extraction (PO, Invoices, GRN, Sales)",
            "3-Way Matching Analysis", 
            "PO-Invoice Verification",
            "Inventory Cost Analysis",
            "Inventory Ageing Analysis", 
            "FIFO Inventory Valuation",
            "Comprehensive Profitability Analysis"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting ABC Book House Comprehensive ETL & Analytics API...")
    print("📊 Main API available at: http://localhost:8000")
    print("📋 API Documentation at: http://localhost:8000/docs")
    print("🔄 3-Way Matching Dashboard at: http://localhost:8000/api/matching/dashboard")
    print("📈 PO-Invoice Verification at: http://localhost:8000/verify/po-invoice/dashboard")
    print("📦 Inventory Analysis Dashboard at: http://localhost:8000/analyze/inventory/dashboard")
    print("💰 Profitability Analysis Dashboard at: http://localhost:8000/analyze/profitability/dashboard")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)