from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import uvicorn
from pathlib import Path
import json
from datetime import datetime

# Import all extractors
from final_po_extractor import FinalPurchaseOrderParser
from grn_extractor import GRNExtractor
from purchase_invoice_extractor import PurchaseInvoiceExtractor
from sales_invoice_extractor import SalesInvoiceExtractor

# Import 3-way matching system
from matching_engine import ThreeWayMatchingEngine

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

# Global variables to store processed data
processed_data = {
    "purchase_orders_df": pd.DataFrame(),
    "items_df": pd.DataFrame(),
    "last_processed": None
}

@app.get("/")
async def root():
    return {
        "message": "Welcome to Zenalyst AI ETL Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "purchase_orders": "/api/purchase-orders",
            "items": "/api/items",
            "analytics": "/api/analytics",
            "process": "/api/process-purchase-orders"
        }
    }

@app.post("/api/process-purchase-orders")
async def process_purchase_orders():
    """Process all purchase order PDFs and extract structured data"""
    try:
        parser = FinalPurchaseOrderParser()
        po_df, items_df = parser.process_all_purchase_orders("data/Purchase Order")
        
        # Store in global variables
        processed_data["purchase_orders_df"] = po_df
        processed_data["items_df"] = items_df
        processed_data["last_processed"] = pd.Timestamp.now().isoformat()
        
        # Save to Excel
        parser.save_to_excel(po_df, items_df, "purchase_orders_api_result.xlsx")
        
        return {
            "status": "success",
            "message": "Purchase orders processed successfully",
            "summary": {
                "total_purchase_orders": len(po_df),
                "total_items": len(items_df),
                "total_value": float(po_df['total_amount'].sum()) if len(po_df) > 0 else 0,
                "unique_vendors": int(po_df['vendor_name'].nunique()) if len(po_df) > 0 else 0,
                "processed_at": processed_data["last_processed"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing purchase orders: {str(e)}")

@app.get("/api/purchase-orders")
async def get_purchase_orders(limit: int = 100, offset: int = 0):
    """Get purchase orders data with pagination"""
    if processed_data["purchase_orders_df"].empty:
        raise HTTPException(status_code=404, detail="No purchase orders data found. Please process the data first.")
    
    df = processed_data["purchase_orders_df"]
    total_count = len(df)
    
    # Apply pagination
    paginated_df = df.iloc[offset:offset + limit]
    
    return {
        "status": "success",
        "data": paginated_df.to_dict(orient="records"),
        "pagination": {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        }
    }

@app.get("/api/items")
async def get_items(limit: int = 100, offset: int = 0, po_number: str = None):
    """Get items data with pagination and optional filtering by PO number"""
    if processed_data["items_df"].empty:
        raise HTTPException(status_code=404, detail="No items data found. Please process the data first.")
    
    df = processed_data["items_df"]
    
    # Filter by PO number if provided
    if po_number:
        df = df[df['po_number'] == po_number]
    
    total_count = len(df)
    
    # Apply pagination
    paginated_df = df.iloc[offset:offset + limit]
    
    return {
        "status": "success",
        "data": paginated_df.to_dict(orient="records"),
        "pagination": {
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total_count
        },
        "filter": {"po_number": po_number} if po_number else None
    }

@app.get("/api/analytics/summary")
async def get_analytics_summary():
    """Get comprehensive analytics summary of purchase orders"""
    if processed_data["purchase_orders_df"].empty or processed_data["items_df"].empty:
        raise HTTPException(status_code=404, detail="No data found. Please process the data first.")
    
    po_df = processed_data["purchase_orders_df"]
    items_df = processed_data["items_df"]
    
    # Basic metrics
    total_pos = len(po_df)
    total_items = len(items_df)
    total_value = float(po_df['total_amount'].sum())
    avg_po_value = float(po_df['total_amount'].mean())
    
    # Vendor analysis
    vendor_stats = po_df['vendor_name'].value_counts().head(10).to_dict()
    
    # Item analysis
    top_items = items_df.nlargest(10, 'amount')[['title', 'author', 'amount', 'quantity']].to_dict(orient="records")
    
    # Publisher analysis
    publisher_stats = items_df['publisher'].value_counts().head(10).to_dict()
    
    # Date range analysis
    date_range = {
        "start_date": po_df['po_date'].min(),
        "end_date": po_df['po_date'].max()
    }
    
    # Monthly trends (if we have date data)
    monthly_trends = []
    if po_df['po_date'].notna().any():
        po_df['po_month'] = pd.to_datetime(po_df['po_date']).dt.to_period('M')
        monthly_data = po_df.groupby('po_month').agg({
            'total_amount': 'sum',
            'po_number': 'count'
        }).reset_index()
        monthly_trends = monthly_data.to_dict(orient="records")
    
    return {
        "status": "success",
        "summary": {
            "basic_metrics": {
                "total_purchase_orders": total_pos,
                "total_items": total_items,
                "total_value_inr": total_value,
                "average_po_value_inr": avg_po_value
            },
            "date_range": date_range,
            "top_vendors": vendor_stats,
            "top_items_by_value": top_items,
            "top_publishers": publisher_stats,
            "monthly_trends": monthly_trends
        },
        "last_processed": processed_data["last_processed"]
    }

@app.get("/api/analytics/vendor/{vendor_name}")
async def get_vendor_analytics(vendor_name: str):
    """Get detailed analytics for a specific vendor"""
    if processed_data["purchase_orders_df"].empty:
        raise HTTPException(status_code=404, detail="No data found. Please process the data first.")
    
    po_df = processed_data["purchase_orders_df"]
    items_df = processed_data["items_df"]
    
    # Filter data for the vendor
    vendor_pos = po_df[po_df['vendor_name'] == vendor_name]
    vendor_items = items_df[items_df['vendor_name'] == vendor_name]
    
    if vendor_pos.empty:
        raise HTTPException(status_code=404, detail=f"No data found for vendor: {vendor_name}")
    
    # Vendor metrics
    total_pos = len(vendor_pos)
    total_value = float(vendor_pos['total_amount'].sum())
    avg_po_value = float(vendor_pos['total_amount'].mean())
    total_items = len(vendor_items)
    
    # Top items from this vendor
    top_items = vendor_items.nlargest(5, 'amount')[['title', 'author', 'amount', 'quantity']].to_dict(orient="records")
    
    return {
        "status": "success",
        "vendor_name": vendor_name,
        "analytics": {
            "total_purchase_orders": total_pos,
            "total_items": total_items,
            "total_value_inr": total_value,
            "average_po_value_inr": avg_po_value,
            "top_items": top_items
        }
    }

@app.get("/api/export/excel")
async def export_to_excel():
    """Export processed data to Excel file"""
    if processed_data["purchase_orders_df"].empty:
        raise HTTPException(status_code=404, detail="No data found. Please process the data first.")
    
    filename = "zenalyst_export.xlsx"
    parser = FinalPurchaseOrderParser()
    parser.save_to_excel(
        processed_data["purchase_orders_df"], 
        processed_data["items_df"], 
        filename
    )
    
    return FileResponse(
        path=filename,
        filename=filename,
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": pd.Timestamp.now().isoformat(),
        "data_loaded": not processed_data["purchase_orders_df"].empty
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)