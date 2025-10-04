# 🔄 HOW TO PROCESS NEW DATA

## 📁 If You Replace Data Files, Run This:

### **Primary Option: `demo.py` (Recommended)**
```bash
python demo.py
```

**What it does:**
- Processes all Purchase Order PDFs in `data/Purchase Order/` folder
- Creates new `zenalyst_demo_results.xlsx` with fresh data
- Shows complete analytics and summary
- Works standalone (no API server needed)

### **Alternative: `final_po_extractor.py` (Direct)**  
```bash
python final_po_extractor.py
```

**What it does:**
- Same extraction logic as demo.py
- Creates `purchase_orders_final.xlsx` 
- More technical output, less user-friendly

## 🔄 **Complete Workflow for New Data:**

### **Step 1: Replace Your Data**
```
data/
├── Purchase Order/          ← Put your new PO PDFs here
├── Purchase Invoice/        ← Put your new Invoice PDFs here  
├── GRN Copies/             ← Put your new GRN PDFs here
└── Sales Invoices/         ← Put your new Sales PDFs here
```

### **Step 2: Run the Extractor**
```bash
# This will process whatever PDFs are in data/Purchase Order/
python demo.py
```

### **Step 3: View Results**
```bash
# See the extracted orders
python show_orders.py

# Or check the Excel file directly
# File: zenalyst_demo_results.xlsx
```

## 📊 **Output Files Created:**

| File | Contains | Sheets |
|------|----------|---------|
| `zenalyst_demo_results.xlsx` | All extracted data | • Purchase_Orders<br>• Items<br>• Summary |

## 🎯 **Key Points:**

1. **`demo.py` is your main extraction script** ✅
2. **It automatically finds all PDFs** in `data/Purchase Order/` folder
3. **Creates fresh Excel file** with new data each time
4. **No configuration needed** - just run it!

## 🔧 **What Happens Behind the Scenes:**

```python
# In demo.py:
parser = FinalPurchaseOrderParser()
po_df, items_df = parser.process_all_purchase_orders("data/Purchase Order")
parser.save_to_excel(po_df, items_df, "zenalyst_demo_results.xlsx")
```

**So if you have 50 new PO PDFs, just put them in `data/Purchase Order/` and run `python demo.py` - it will extract all 50 automatically!** 🚀