from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class MatchStatus(str, Enum):
    FULLY_MATCHED = "fully_matched"
    PARTIAL_MATCH = "partial_match"
    PENDING_GRN = "pending_grn"
    PENDING_INVOICE = "pending_invoice"
    AMOUNT_MISMATCH = "amount_mismatch"
    QUANTITY_MISMATCH = "quantity_mismatch"
    VENDOR_MISMATCH = "vendor_mismatch"
    ORPHANED = "orphaned"

class ExceptionSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class DocumentItem(BaseModel):
    sno: Optional[str] = None
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    category: Optional[str] = None
    quantity: int = 0
    rate: float = 0.0
    amount: float = 0.0

class PurchaseOrderData(BaseModel):
    po_number: str
    po_date: Optional[str] = None
    vendor_name: Optional[str] = None
    total_amount: float = 0.0
    items: List[DocumentItem] = []
    filename: Optional[str] = None

class GRNData(BaseModel):
    grn_number: str
    grn_date: Optional[str] = None
    related_po: Optional[str] = None
    supplier_name: Optional[str] = None
    total_value: float = 0.0
    items: List[DocumentItem] = []
    filename: Optional[str] = None

class InvoiceData(BaseModel):
    invoice_number: str
    invoice_date: Optional[str] = None
    related_po: Optional[str] = None
    supplier_name: Optional[str] = None
    total_amount: float = 0.0
    items: List[DocumentItem] = []
    filename: Optional[str] = None

class MatchingResult(BaseModel):
    po_number: str
    status: MatchStatus
    match_score: float = Field(ge=0, le=100, description="Matching score percentage")
    
    # Document presence flags
    has_po: bool = True
    has_grn: bool = False
    has_invoice: bool = False
    
    # Financial data
    po_amount: float = 0.0
    grn_amount: float = 0.0
    invoice_amount: float = 0.0
    amount_variance: float = 0.0
    amount_variance_percentage: float = 0.0
    
    # Quantity data
    ordered_quantity: int = 0
    received_quantity: int = 0
    billed_quantity: int = 0
    quantity_variance: int = 0
    
    # Vendor data
    po_vendor: Optional[str] = None
    grn_vendor: Optional[str] = None
    invoice_vendor: Optional[str] = None
    vendor_consistent: bool = True
    
    # Dates for timeline analysis
    po_date: Optional[str] = None
    grn_date: Optional[str] = None
    invoice_date: Optional[str] = None
    po_to_grn_days: Optional[int] = None
    grn_to_invoice_days: Optional[int] = None
    total_cycle_days: Optional[int] = None

class ExceptionItem(BaseModel):
    po_number: str
    exception_type: str
    severity: ExceptionSeverity
    description: str
    recommendation: str
    impact: str
    expected_value: Optional[str] = None
    actual_value: Optional[str] = None
    variance: Optional[float] = None

class VendorPerformance(BaseModel):
    vendor_name: str
    total_pos: int = 0
    matched_pos: int = 0
    pending_grns: int = 0
    pending_invoices: int = 0
    match_rate: float = 0.0
    avg_po_to_grn_days: Optional[float] = None
    avg_grn_to_invoice_days: Optional[float] = None
    total_po_value: float = 0.0
    total_grn_value: float = 0.0
    total_invoice_value: float = 0.0
    amount_variance: float = 0.0
    on_time_delivery_rate: float = 0.0
    compliance_score: float = 0.0

class DashboardSummary(BaseModel):
    # Overall statistics
    total_pos: int = 0
    fully_matched: int = 0
    partial_matches: int = 0
    pending_grns: int = 0
    pending_invoices: int = 0
    exceptions: int = 0
    match_rate: float = 0.0
    
    # Financial summary
    total_po_value: float = 0.0
    total_grn_value: float = 0.0
    total_invoice_value: float = 0.0
    total_variance: float = 0.0
    
    # Process efficiency
    avg_processing_time: Optional[float] = None
    fastest_processing: Optional[float] = None
    slowest_processing: Optional[float] = None
    
    # Top issues
    critical_exceptions: int = 0
    high_exceptions: int = 0
    medium_exceptions: int = 0
    low_exceptions: int = 0

class ChartData(BaseModel):
    labels: List[str]
    datasets: List[Dict[str, Any]]

class MatchingAnalysisResponse(BaseModel):
    dashboard: DashboardSummary
    matching_results: List[MatchingResult]
    exceptions: List[ExceptionItem]
    vendor_performance: List[VendorPerformance]
    
    # Chart data for frontend
    match_status_chart: ChartData
    vendor_performance_chart: ChartData
    timeline_chart: ChartData
    amount_variance_chart: ChartData
    
    # Metadata
    analysis_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_documents_analyzed: int = 0
    processing_time_seconds: Optional[float] = None

class RefreshRequest(BaseModel):
    force_reload: bool = False
    include_detailed_analysis: bool = True

class ExportRequest(BaseModel):
    format: str = Field(pattern="^(excel|pdf|csv)$")
    include_charts: bool = True
    include_details: bool = True