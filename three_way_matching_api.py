from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import pandas as pd
import json
from datetime import datetime
from typing import Dict, Any, Optional
import io
import base64

from matching_engine import ThreeWayMatchingEngine
from data_models import (
    MatchingAnalysisResponse, RefreshRequest, ExportRequest,
    DashboardSummary, MatchingResult, ExceptionItem, VendorPerformance
)

app = FastAPI(
    title="ABC Book House - 3-Way Matching API",
    description="Comprehensive 3-Way Matching System for Purchase Orders, GRNs, and Invoices",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache for analysis results
analysis_cache = {
    'last_updated': None,
    'data': None
}

matching_engine = ThreeWayMatchingEngine()

@app.get("/")
async def root():
    """API Health Check"""
    return {
        "message": "ABC Book House 3-Way Matching API",
        "version": "1.0.0",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "dashboard": "/api/matching/dashboard",
            "summary": "/api/matching/summary",
            "details": "/api/matching/details",
            "exceptions": "/api/matching/exceptions",
            "vendors": "/api/matching/vendors",
            "refresh": "/api/matching/refresh",
            "export": "/api/matching/export"
        }
    }

@app.get("/api/matching/dashboard")
async def get_dashboard() -> Dict[str, Any]:
    """Get dashboard summary data for frontend widgets"""
    try:
        # Check if we have cached data
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        
        if 'error' in data:
            raise HTTPException(status_code=500, detail=data['error'])
        
        # Return dashboard-specific data
        return {
            "dashboard": data['dashboard'],
            "charts": data['charts'],
            "last_updated": analysis_cache['last_updated'].isoformat(),
            "processing_time": data.get('processing_time', 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard analysis failed: {str(e)}")

@app.get("/api/matching/summary")
async def get_matching_summary() -> Dict[str, Any]:
    """Get comprehensive matching analysis summary"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        
        if 'error' in data:
            raise HTTPException(status_code=500, detail=data['error'])
        
        # Return summary with key metrics
        return {
            "summary": data['dashboard'],
            "total_documents": len(data['matching_results']),
            "total_exceptions": len(data['exceptions']),
            "total_vendors": len(data['vendor_performance']),
            "analysis_date": analysis_cache['last_updated'].isoformat(),
            "key_insights": {
                "match_rate": data['dashboard'].get('match_rate', 0),
                "critical_exceptions": data['dashboard'].get('critical_exceptions', 0),
                "total_variance": data['dashboard'].get('total_variance', 0),
                "top_vendor": data['vendor_performance'][0]['vendor_name'] if data['vendor_performance'] else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@app.get("/api/matching/details")
async def get_matching_details(
    page: int = 1,
    page_size: int = 50,
    status_filter: Optional[str] = None,
    vendor_filter: Optional[str] = None
) -> Dict[str, Any]:
    """Get detailed matching results with pagination and filtering"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        results = data['matching_results']
        
        # Apply filters
        if status_filter:
            results = [r for r in results if r['status'] == status_filter]
        
        if vendor_filter:
            results = [r for r in results if vendor_filter.lower() in r.get('po_vendor', '').lower()]
        
        # Apply pagination
        total_records = len(results)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_results = results[start_idx:end_idx]
        
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
                "vendor": vendor_filter
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Details retrieval failed: {str(e)}")

@app.get("/api/matching/exceptions")
async def get_exceptions(
    severity: Optional[str] = None,
    exception_type: Optional[str] = None
) -> Dict[str, Any]:
    """Get exception reports with filtering"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        exceptions = data['exceptions']
        
        # Apply filters
        if severity:
            exceptions = [e for e in exceptions if e['severity'] == severity]
        
        if exception_type:
            exceptions = [e for e in exceptions if e['exception_type'] == exception_type]
        
        # Group exceptions by severity for summary
        severity_summary = {}
        for exc in exceptions:
            sev = exc['severity']
            severity_summary[sev] = severity_summary.get(sev, 0) + 1
        
        return {
            "exceptions": exceptions,
            "total_exceptions": len(exceptions),
            "severity_summary": severity_summary,
            "exception_types": list(set([e['exception_type'] for e in exceptions])),
            "filters_applied": {
                "severity": severity,
                "exception_type": exception_type
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Exception retrieval failed: {str(e)}")

@app.get("/api/matching/vendors")
async def get_vendor_performance() -> Dict[str, Any]:
    """Get vendor performance analysis"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        vendors = data['vendor_performance']
        
        # Calculate aggregate metrics
        total_vendors = len(vendors)
        avg_compliance = sum([v['compliance_score'] for v in vendors]) / max(total_vendors, 1)
        top_performer = vendors[0] if vendors else None
        
        return {
            "vendors": vendors,
            "total_vendors": total_vendors,
            "average_compliance_score": round(avg_compliance, 2),
            "top_performer": top_performer,
            "performance_categories": {
                "excellent": len([v for v in vendors if v['compliance_score'] >= 80]),
                "good": len([v for v in vendors if 60 <= v['compliance_score'] < 80]),
                "needs_improvement": len([v for v in vendors if v['compliance_score'] < 60])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vendor analysis failed: {str(e)}")

@app.post("/api/matching/refresh")
async def refresh_analysis(request: RefreshRequest = RefreshRequest()) -> Dict[str, Any]:
    """Refresh the matching analysis"""
    try:
        # Force refresh of analysis
        start_time = datetime.now()
        analysis_cache['data'] = matching_engine.analyze_three_way_matching()
        analysis_cache['last_updated'] = datetime.now()
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        data = analysis_cache['data']
        
        return {
            "status": "success",
            "message": "Analysis refreshed successfully",
            "refresh_time": analysis_cache['last_updated'].isoformat(),
            "processing_time_seconds": processing_time,
            "data_summary": {
                "total_pos": len(data.get('matching_results', [])),
                "total_exceptions": len(data.get('exceptions', [])),
                "total_vendors": len(data.get('vendor_performance', []))
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")

@app.post("/api/matching/export")
async def export_data(request: ExportRequest) -> FileResponse:
    """Export matching analysis data"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        
        if request.format == "excel":
            # Create Excel file with multiple sheets
            filename = f"three_way_matching_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                # Dashboard summary
                dashboard_df = pd.DataFrame([data['dashboard']])
                dashboard_df.to_excel(writer, sheet_name='Dashboard', index=False)
                
                # Matching results
                if data['matching_results']:
                    results_df = pd.DataFrame(data['matching_results'])
                    results_df.to_excel(writer, sheet_name='Matching_Results', index=False)
                
                # Exceptions
                if data['exceptions']:
                    exceptions_df = pd.DataFrame(data['exceptions'])
                    exceptions_df.to_excel(writer, sheet_name='Exceptions', index=False)
                
                # Vendor performance
                if data['vendor_performance']:
                    vendors_df = pd.DataFrame(data['vendor_performance'])
                    vendors_df.to_excel(writer, sheet_name='Vendor_Performance', index=False)
            
            return FileResponse(
                filename,
                media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename=filename
            )
        
        elif request.format == "csv":
            # Create CSV with matching results
            if data['matching_results']:
                results_df = pd.DataFrame(data['matching_results'])
                filename = f"matching_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                results_df.to_csv(filename, index=False)
                
                return FileResponse(
                    filename,
                    media_type='text/csv',
                    filename=filename
                )
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.get("/api/matching/charts/{chart_type}")
async def get_chart_data(chart_type: str) -> Dict[str, Any]:
    """Get specific chart data for frontend visualization"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        charts = data.get('charts', {})
        
        if chart_type not in charts:
            raise HTTPException(status_code=404, detail=f"Chart type '{chart_type}' not found")
        
        return {
            "chart_data": charts[chart_type],
            "chart_type": chart_type,
            "last_updated": analysis_cache['last_updated'].isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chart data retrieval failed: {str(e)}")

@app.get("/api/matching/stats")
async def get_statistics() -> Dict[str, Any]:
    """Get various statistics for the dashboard"""
    try:
        if analysis_cache['data'] is None:
            analysis_cache['data'] = matching_engine.analyze_three_way_matching()
            analysis_cache['last_updated'] = datetime.now()
        
        data = analysis_cache['data']
        
        # Calculate additional statistics
        results = data['matching_results']
        exceptions = data['exceptions']
        
        # Processing time statistics
        cycle_times = [r.get('total_cycle_days') for r in results if r.get('total_cycle_days')]
        cycle_times = [t for t in cycle_times if t is not None]
        
        # Amount statistics
        amounts = [r.get('po_amount', 0) for r in results]
        variances = [r.get('amount_variance', 0) for r in results if r.get('amount_variance')]
        
        return {
            "processing_statistics": {
                "avg_cycle_time": sum(cycle_times) / len(cycle_times) if cycle_times else None,
                "min_cycle_time": min(cycle_times) if cycle_times else None,
                "max_cycle_time": max(cycle_times) if cycle_times else None
            },
            "financial_statistics": {
                "total_po_value": sum(amounts),
                "avg_po_value": sum(amounts) / len(amounts) if amounts else 0,
                "total_variance": sum(variances),
                "avg_variance": sum(variances) / len(variances) if variances else 0
            },
            "exception_statistics": {
                "exception_rate": len(exceptions) / len(results) * 100 if results else 0,
                "critical_rate": len([e for e in exceptions if e.get('severity') == 'critical']) / len(results) * 100 if results else 0
            },
            "last_updated": analysis_cache['last_updated'].isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Statistics calculation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ABC Book House 3-Way Matching API...")
    print("📊 Dashboard available at: http://localhost:8001/api/matching/dashboard")
    print("📋 API Documentation at: http://localhost:8001/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)