# Zenalystai - Business Intelligence & Analytics Platform

A comprehensive business intelligence platform for inventory management, financial analysis, and document processing with AI-powered insights.

## 🏗️ Project Structure

```
Zenalystai/
├── backend/                    # Backend Python modules
│   ├── core/                  # Core business logic
│   │   ├── data_models.py     # Data structures and models
│   │   └── gemini_ai_insights.py # AI-powered insights engine
│   ├── analysis/              # Analysis engines
│   │   ├── inventory_cost_analysis.py      # Cost analysis
│   │   ├── inventory_ageing_analysis.py    # Ageing analysis
│   │   ├── inventory_valuation_analysis.py # Valuation analysis
│   │   └── profitability_analysis.py       # Profitability analysis
│   ├── extractors/            # Document extractors
│   │   ├── final_po_extractor.py          # Purchase order extractor
│   │   ├── grn_extractor.py               # GRN extractor
│   │   ├── purchase_invoice_extractor.py  # Purchase invoice extractor
│   │   └── sales_invoice_extractor.py     # Sales invoice extractor
│   └── api/                   # API utilities
│       ├── matching_engine.py             # 3-way matching engine
│       ├── po_invoice_verification.py     # PO-Invoice verification
│       └── three_way_matching_api.py      # Matching API
├── client/                    # React frontend application
│   ├── src/                   # Source code
│   ├── public/                # Static assets
│   └── package.json           # Frontend dependencies
├── data/                      # Sample data files
├── reports/                   # Generated analysis reports (Excel)
├── main.py                    # FastAPI backend server
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🚀 Features

### Core Analytics
- **Inventory Cost Analysis** - Carrying costs, shelf life, financial risk assessment
- **Inventory Ageing Analysis** - Age-based categorization and risk analysis
- **Inventory Valuation Analysis** - FIFO vs market value analysis
- **Profitability Analysis** - Product, vendor, and category profitability

### Document Processing
- **Purchase Order Extraction** - Automated PO data extraction
- **GRN Processing** - Goods receipt note analysis
- **Invoice Processing** - Purchase and sales invoice extraction
- **3-Way Matching** - PO-GRN-Invoice reconciliation

### AI-Powered Insights
- **Gemini AI Integration** - Intelligent business recommendations
- **Risk Assessment** - Automated risk identification
- **Opportunity Analysis** - Growth opportunity identification
- **Strategic Recommendations** - Actionable business insights

### Modern UI
- **React Dashboard** - Interactive analytics dashboard
- **Real-time Charts** - Dynamic data visualization
- **Export Capabilities** - Excel report generation
- **Responsive Design** - Mobile-friendly interface

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API Key

### Backend Setup
1. Clone the repository
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
6. Start backend server: `python main.py`

### Frontend Setup
1. Navigate to client directory: `cd client`
2. Install dependencies: `npm install`
3. Start development server: `npm run dev`

## 📊 API Endpoints

### Analysis Endpoints
- `POST /analyze/profitability` - Profitability analysis
- `POST /analyze/inventory-cost` - Cost analysis
- `POST /analyze/inventory-ageing` - Ageing analysis
- `POST /analyze/inventory-valuation` - Valuation analysis

### AI Insights
- `GET /analyze/{analysis_type}/ai-insights` - Get AI insights for analysis

### Document Processing
- `POST /extract/purchase-orders` - Extract PO data
- `POST /extract/grn` - Extract GRN data
- `POST /extract/purchase-invoices` - Extract purchase invoice data
- `POST /extract/sales-invoices` - Extract sales invoice data

### Verification
- `POST /verify/po-invoice` - PO-Invoice verification
- `POST /analytics/matching` - 3-way matching analysis

## 💡 Usage

1. Upload your data files through the web interface
2. Run various analyses (profitability, cost, ageing, valuation)
3. View interactive charts and reports
4. Get AI-powered insights and recommendations
5. Export detailed reports in Excel format

## 🔧 Technologies Used

### Backend
- **FastAPI** - Modern Python web framework
- **Pandas** - Data manipulation and analysis
- **Google Gemini AI** - AI-powered insights
- **Uvicorn** - ASGI server

### Frontend
- **React** - UI framework
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS
- **Recharts** - Chart library
- **Vite** - Build tool

## 🎯 Key Features

- ✅ **Real-time Analytics** - Live data processing and visualization
- ✅ **AI-Powered Insights** - Intelligent recommendations using Gemini AI
- ✅ **Multi-format Support** - PDF, Excel, CSV file processing
- ✅ **3-Way Matching** - Automated PO-GRN-Invoice reconciliation
- ✅ **Financial Analysis** - Comprehensive profitability and cost analysis
- ✅ **Risk Assessment** - Automated inventory risk identification
- ✅ **Export Capabilities** - Excel and JSON report generation
- ✅ **Responsive Design** - Works on desktop and mobile devices

## 📈 Business Value

- **Cost Optimization** - Identify carrying cost reduction opportunities
- **Revenue Enhancement** - Discover profitable products and vendors
- **Risk Mitigation** - Early identification of dead stock and ageing inventory
- **Process Automation** - Automated document processing and matching
- **Data-Driven Decisions** - AI-powered business recommendations

## 🔒 Security & Compliance

- Environment variable management for API keys
- CORS configuration for secure frontend-backend communication
- Input validation and error handling
- Secure file upload and processing

## 📞 Support

For questions or support, please contact the development team.

---

**Built with ❤️ for modern businesses seeking data-driven insights**