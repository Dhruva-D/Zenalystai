import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { 
  BarChart3, 
  ArrowRight, 
  RefreshCw, 
  Download,
  FileText,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  Clock,
  DollarSign,
  Package,
  Eye,
  ArrowLeft
} from "lucide-react";
import { useToast } from "@/components/ui/use-toast";
import { Navbar } from "@/components/Navbar";
import { FloatingScrollToTop } from "@/components/FloatingScrollToTop";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart,
} from "recharts";

interface AnalysisCard {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  color: string;
  bgColor: string;
  endpoint: string;
  method: 'GET' | 'POST';
}

const analysisCards: AnalysisCard[] = [
  {
    id: 'summary-data',
    title: '3-Way Match: Summary of Data',
    description: 'Verify if PO quantities match GRN quantities and vendor invoices',
    icon: <FileText className="h-8 w-8" />,
    color: 'text-blue-600',
    bgColor: 'bg-blue-50',
    endpoint: '/analytics/matching',
    method: 'GET',
  },
  {
    id: 'verification',
    title: 'Verification',
    description: 'Excess Short Procurement / excess procurement analysis',
    icon: <CheckCircle className="h-8 w-8" />,
    color: 'text-green-600',
    bgColor: 'bg-green-50',
    endpoint: '/verify/po-invoice',
    method: 'POST',
  },
  {
    id: 'inventory-cost',
    title: 'Inventory Cost Analysis',
    description: 'Carrying Cost Incurred for each product on Obsolete products & highlight if Gross Margin is less than Carrying Cost',
    icon: <DollarSign className="h-8 w-8" />,
    color: 'text-purple-600',
    bgColor: 'bg-purple-50',
    endpoint: '/analyze/inventory-cost',
    method: 'POST',
  },
  {
    id: 'inventory-ageing',
    title: 'Inventory Ageing Analysis',
    description: 'Obsolete/Dead Stock: Items not sold within shelf life window',
    icon: <Clock className="h-8 w-8" />,
    color: 'text-orange-600',
    bgColor: 'bg-orange-50',
    endpoint: '/analyze/inventory-ageing',
    method: 'POST',
  },
  {
    id: 'inventory-valuation',
    title: 'Inventory Valuation Analysis',
    description: 'Stock Valuation: Value of inventory based on FIFO (Purchase Invoices) vs. selling price',
    icon: <Package className="h-8 w-8" />,
    color: 'text-indigo-600',
    bgColor: 'bg-indigo-50',
    endpoint: '/analyze/inventory-valuation',
    method: 'POST',
  },
  {
    id: 'profitability',
    title: 'Profitability Analysis',
    description: '1. Which vendor-supplied books generate best margins. 2. Which categories are most profitable. 3. Calculate Gross Margin of each SKUs and highlight negative margin SKUs & Top 5 products with highest gross margin',
    icon: <TrendingUp className="h-8 w-8" />,
    color: 'text-red-600',
    bgColor: 'bg-red-50',
    endpoint: '/analyze/profitability',
    method: 'POST',
  },
];

export const AnalyzeData = () => {
  const [selectedAnalysis, setSelectedAnalysis] = useState<string | null>(null);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const { toast } = useToast();

  const handleCardClick = async (card: AnalysisCard) => {
    setSelectedAnalysis(card.id);
    setLoading(true);
    setAnalysisData(null);

    try {
      const response = await fetch(`http://localhost:8000${card.endpoint}`, {
        method: card.method,
        headers: {
          'Content-Type': 'application/json',
        },
        ...(card.method === 'POST' && { body: JSON.stringify({}) }),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch ${card.title}`);
      }

      const data = await response.json();
      setAnalysisData(data);
      
      toast({
        title: "Analysis Complete",
        description: `${card.title} analysis has been completed successfully.`,
      });
    } catch (error) {
      toast({
        title: "Analysis Error",
        description: `Failed to execute ${card.title}. Please check your backend connection.`,
        variant: "destructive",
      });
      console.error('Analysis error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBackToCards = () => {
    setSelectedAnalysis(null);
    setAnalysisData(null);
  };

  const downloadReport = () => {
    if (!analysisData) return;
    
    const blob = new Blob([JSON.stringify(analysisData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selectedAnalysis}-analysis-report-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast({
      title: "Report Downloaded",
      description: "Analysis report has been downloaded successfully.",
    });
  };

  const renderAnalysisResults = () => {
    if (!analysisData) return null;

    const selectedCard = analysisCards.find(card => card.id === selectedAnalysis);
    if (!selectedCard) return null;

    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="space-y-6"
      >
        {/* Header with back button */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              onClick={handleBackToCards}
              variant="outline"
              size="sm"
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Analysis Cards
            </Button>
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg ${selectedCard.bgColor}`}>
                <div className={selectedCard.color}>
                  {selectedCard.icon}
                </div>
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900">{selectedCard.title}</h2>
                <p className="text-muted-foreground">{selectedCard.description}</p>
              </div>
            </div>
          </div>
          <Button onClick={downloadReport} variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download Report
          </Button>
        </div>

        {/* Analysis Results */}
        <Card>
          <CardHeader>
            <CardTitle>Analysis Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {/* Display results based on analysis type */}
              {selectedAnalysis === 'summary-data' && renderThreeWayMatching()}
              {selectedAnalysis === 'verification' && renderVerificationResults()}
              {selectedAnalysis === 'inventory-cost' && renderInventoryCostResults()}
              {selectedAnalysis === 'inventory-ageing' && renderInventoryAgeingResults()}
              {selectedAnalysis === 'inventory-valuation' && renderInventoryValuationResults()}
              {selectedAnalysis === 'profitability' && renderProfitabilityResults()}
            </div>
          </CardContent>
        </Card>
      </motion.div>
    );
  };

  const renderThreeWayMatching = () => {
    // Sample data - replace with actual analysisData
    const matchingData = [
      { name: 'Perfect Matches', value: analysisData?.summary?.total_matches || 245, color: '#10B981' },
      { name: 'Discrepancies', value: analysisData?.summary?.discrepancies || 35, color: '#F59E0B' },
      { name: 'Pending', value: analysisData?.summary?.pending || 20, color: '#6B7280' },
    ];

    const trendData = [
      { month: 'Jan', matches: 92, discrepancies: 8 },
      { month: 'Feb', matches: 94, discrepancies: 6 },
      { month: 'Mar', matches: 89, discrepancies: 11 },
      { month: 'Apr', matches: 96, discrepancies: 4 },
      { month: 'May', matches: 91, discrepancies: 9 },
      { month: 'Jun', matches: 93, discrepancies: 7 },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-blue-700 flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Total Matches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                {analysisData?.summary?.total_matches || 245}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                PO-GRN-Invoice matches
              </p>
              <div className="mt-2">
                <Progress value={85} className="h-2" />
                <p className="text-xs text-muted-foreground mt-1">85% of total documents</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-amber-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Discrepancies
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-amber-600">
                {analysisData?.summary?.discrepancies || 35}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Quantity mismatches found
              </p>
              <div className="mt-2">
                <Progress value={12} className="h-2" />
                <p className="text-xs text-muted-foreground mt-1">12% discrepancy rate</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-green-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Match Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {analysisData?.summary?.match_percentage || 93}%
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Overall accuracy
              </p>
              <div className="mt-2">
                <Progress value={93} className="h-2" />
                <p className="text-xs text-green-600 mt-1">↗ +2% from last month</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pie Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Match Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={matchingData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {matchingData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Trend Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Monthly Matching Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="matches" 
                    stackId="1" 
                    stroke="#10B981" 
                    fill="#10B981" 
                    fillOpacity={0.8}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="discrepancies" 
                    stackId="1" 
                    stroke="#F59E0B" 
                    fill="#F59E0B" 
                    fillOpacity={0.8}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Results */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Matching Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">PO Number</th>
                    <th className="text-left p-2">GRN Number</th>
                    <th className="text-left p-2">Invoice Number</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-left p-2">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { po: 'PO-2024-001', grn: 'GRN-2024-001', invoice: 'INV-2024-001', status: 'Matched', amount: '$1,250.00' },
                    { po: 'PO-2024-002', grn: 'GRN-2024-002', invoice: 'INV-2024-002', status: 'Discrepancy', amount: '$890.50' },
                    { po: 'PO-2024-003', grn: 'GRN-2024-003', invoice: 'INV-2024-003', status: 'Matched', amount: '$2,100.75' },
                    { po: 'PO-2024-004', grn: 'GRN-2024-004', invoice: 'INV-2024-004', status: 'Pending', amount: '$750.25' },
                  ].map((row, index) => (
                    <tr key={index} className="border-b hover:bg-gray-50">
                      <td className="p-2 font-mono text-xs">{row.po}</td>
                      <td className="p-2 font-mono text-xs">{row.grn}</td>
                      <td className="p-2 font-mono text-xs">{row.invoice}</td>
                      <td className="p-2">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          row.status === 'Matched' ? 'bg-green-100 text-green-800' :
                          row.status === 'Discrepancy' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {row.status}
                        </span>
                      </td>
                      <td className="p-2 font-semibold">{row.amount}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  const renderVerificationResults = () => {
    const procurementData = [
      { status: 'Optimal', count: 187, value: 245000, color: '#10B981' },
      { status: 'Excess', count: 28, value: 45000, color: '#EF4444' },
      { status: 'Short', count: 15, value: 18000, color: '#F59E0B' },
    ];

    const trendData = [
      { month: 'Jan', excess: 5, short: 3, optimal: 92 },
      { month: 'Feb', excess: 8, short: 4, optimal: 88 },
      { month: 'Mar', excess: 12, short: 6, optimal: 82 },
      { month: 'Apr', excess: 15, short: 8, optimal: 77 },
      { month: 'May', excess: 18, short: 12, optimal: 70 },
      { month: 'Jun', excess: 22, short: 15, optimal: 63 },
    ];

    const criticalIssues = [
      { sku: 'SKU-445', item: 'Advanced Analytics Book', ordered: 100, received: 150, variance: 50, type: 'excess' },
      { sku: 'SKU-223', item: 'Popular Fiction Novel', ordered: 200, received: 120, variance: -80, type: 'short' },
      { sku: 'SKU-667', item: 'Technical Manual 2024', ordered: 75, received: 110, variance: 35, type: 'excess' },
      { sku: 'SKU-889', item: 'Study Guide Series', ordered: 150, received: 90, variance: -60, type: 'short' },
      { sku: 'SKU-334', item: 'Business Strategy Book', ordered: 80, received: 125, variance: 45, type: 'excess' },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-red-200 bg-gradient-to-br from-red-50 to-red-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-red-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Excess Procurement
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {analysisData?.excess_procurement_count || 28}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items over-procured
              </p>
              <div className="mt-2">
                <Progress value={18} className="h-2" />
                <p className="text-xs text-red-600 mt-1">18% of procurement</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-orange-200 bg-gradient-to-br from-orange-50 to-orange-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-orange-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Short Procurement
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600">
                {analysisData?.short_procurement_count || 15}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items under-procured
              </p>
              <div className="mt-2">
                <Progress value={10} className="h-2" />
                <p className="text-xs text-orange-600 mt-1">10% shortage rate</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-green-700 flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Optimal Procurement
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {analysisData?.optimal_procurement_count || 187}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items procured correctly
              </p>
              <div className="mt-2">
                <Progress value={72} className="h-2" />
                <p className="text-xs text-green-600 mt-1">72% accuracy rate</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-blue-700 flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Financial Impact
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                ${analysisData?.financial_impact?.toLocaleString() || '63,000'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Total variance value
              </p>
              <p className="text-xs text-blue-600 mt-1">Tied up capital</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Procurement Status Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Procurement Status Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={procurementData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    dataKey="count"
                    label={({ status, percent }) => `${status} ${(percent * 100).toFixed(0)}%`}
                  >
                    {procurementData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [value, 'Items']} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Procurement Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Procurement Accuracy Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="optimal" 
                    stackId="1" 
                    stroke="#10B981" 
                    fill="#10B981" 
                    fillOpacity={0.8}
                    name="Optimal"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="excess" 
                    stackId="1" 
                    stroke="#EF4444" 
                    fill="#EF4444" 
                    fillOpacity={0.8}
                    name="Excess"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="short" 
                    stackId="1" 
                    stroke="#F59E0B" 
                    fill="#F59E0B" 
                    fillOpacity={0.8}
                    name="Short"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Critical Issues Table */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              Critical Procurement Variances
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-red-200">
                    <th className="text-left p-3 text-red-700">SKU</th>
                    <th className="text-left p-3 text-red-700">Product</th>
                    <th className="text-left p-3 text-red-700">Ordered</th>
                    <th className="text-left p-3 text-red-700">Received</th>
                    <th className="text-left p-3 text-red-700">Variance</th>
                    <th className="text-left p-3 text-red-700">Type</th>
                    <th className="text-left p-3 text-red-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {criticalIssues.map((issue, index) => (
                    <tr key={index} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="p-3 font-mono text-xs">{issue.sku}</td>
                      <td className="p-3 text-sm">{issue.item}</td>
                      <td className="p-3 text-center font-semibold">{issue.ordered}</td>
                      <td className="p-3 text-center font-semibold">{issue.received}</td>
                      <td className="p-3 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-bold ${
                          issue.variance > 0 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-orange-100 text-orange-800'
                        }`}>
                          {issue.variance > 0 ? '+' : ''}{issue.variance}
                        </span>
                      </td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded-full text-xs capitalize ${
                          issue.type === 'excess' 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-orange-100 text-orange-800'
                        }`}>
                          {issue.type}
                        </span>
                      </td>
                      <td className="p-3">
                        <Button 
                          size="sm" 
                          variant={issue.type === 'excess' ? 'destructive' : 'default'}
                          className="text-xs"
                        >
                          {issue.type === 'excess' ? 'Liquidate' : 'Reorder'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Action Items */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="text-red-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Excess Inventory Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Implement discount strategies
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Return to suppliers if possible
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Bundle with popular items
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Review procurement policies
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-orange-200 bg-orange-50">
            <CardHeader>
              <CardTitle className="text-orange-700 flex items-center gap-2">
                <RefreshCw className="h-5 w-5" />
                Shortage Resolution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  Emergency reorder for 15 items
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  Check alternative suppliers
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  Implement safety stock levels
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-orange-500 rounded-full"></div>
                  Update demand forecasting
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-green-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Process Improvements
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Automate reorder points
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Implement ABC analysis
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Enhance supplier communication
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Regular procurement audits
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderInventoryCostResults = () => {
    const costTrendData = [
      { month: 'Jan', carryingCost: 15000, grossMargin: 28000 },
      { month: 'Feb', carryingCost: 16200, grossMargin: 29500 },
      { month: 'Mar', carryingCost: 14800, grossMargin: 27800 },
      { month: 'Apr', carryingCost: 17500, grossMargin: 31200 },
      { month: 'May', carryingCost: 16800, grossMargin: 28900 },
      { month: 'Jun', carryingCost: 18200, grossMargin: 32100 },
    ];

    const productCostData = [
      { product: 'Business Books', carryingCost: 4500, margin: 12500, ratio: 0.36 },
      { product: 'Fiction Novels', carryingCost: 3200, margin: 8900, ratio: 0.36 },
      { product: 'Technical Manuals', carryingCost: 5100, margin: 15600, ratio: 0.33 },
      { product: 'Children Books', carryingCost: 2800, margin: 7200, ratio: 0.39 },
      { product: 'Academic Texts', carryingCost: 6200, margin: 18500, ratio: 0.34 },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-purple-700 flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Total Carrying Cost
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                ${analysisData?.total_carrying_cost?.toLocaleString() || '18,200'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Monthly carrying costs
              </p>
              <p className="text-xs text-red-600 mt-1">↗ +8% from last month</p>
            </CardContent>
          </Card>
          
          <Card className="border-red-200 bg-gradient-to-br from-red-50 to-red-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-red-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Obsolete Products
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {analysisData?.obsolete_products_count || 23}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items with high carrying cost
              </p>
              <div className="mt-2">
                <Progress value={15} className="h-2" />
                <p className="text-xs text-muted-foreground mt-1">15% of inventory</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-amber-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Low Margin Items
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-amber-600">
                {analysisData?.low_margin_items_count || 18}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Margin below carrying cost
              </p>
              <p className="text-xs text-amber-600 mt-1">Requires pricing review</p>
            </CardContent>
          </Card>

          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-green-700 flex items-center gap-2">
                <Package className="h-5 w-5" />
                Cost Ratio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {analysisData?.cost_ratio || 0.35}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Carrying cost to margin ratio
              </p>
              <div className="mt-2">
                <Progress value={35} className="h-2" />
                <p className="text-xs text-green-600 mt-1">Optimal range: 0.2-0.4</p>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Cost vs Margin Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Cost vs Margin Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={costTrendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                  <Line 
                    type="monotone" 
                    dataKey="carryingCost" 
                    stroke="#8B5CF6" 
                    strokeWidth={3}
                    name="Carrying Cost"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="grossMargin" 
                    stroke="#10B981" 
                    strokeWidth={3}
                    name="Gross Margin"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Product Category Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Product Category Cost Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={productCostData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="product" angle={-45} textAnchor="end" height={80} />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    `$${value.toLocaleString()}`, 
                    name === 'carryingCost' ? 'Carrying Cost' : 'Gross Margin'
                  ]} />
                  <Bar dataKey="carryingCost" fill="#EF4444" name="Carrying Cost" />
                  <Bar dataKey="margin" fill="#10B981" name="Gross Margin" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Cost Analysis Insights */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* High Risk Products */}
          <Card className="border-red-200">
            <CardHeader>
              <CardTitle className="text-red-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                High Risk Products
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { sku: 'SKU-445', name: 'Old Edition Textbook', cost: 85, margin: 45 },
                  { sku: 'SKU-221', name: 'Outdated Tech Manual', cost: 92, margin: 38 },
                  { sku: 'SKU-156', name: 'Seasonal Fiction', cost: 78, margin: 52 },
                ].map((product) => (
                  <div key={product.sku} className="flex justify-between items-center p-3 bg-red-50 rounded-lg">
                    <div>
                      <p className="font-semibold text-sm">{product.name}</p>
                      <p className="text-xs text-muted-foreground">{product.sku}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-red-600">${product.cost}</p>
                      <p className="text-xs text-muted-foreground">Cost: ${product.margin}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Optimized Products */}
          <Card className="border-green-200">
            <CardHeader>
              <CardTitle className="text-green-700 flex items-center gap-2">
                <CheckCircle className="h-5 w-5" />
                Well Optimized
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { sku: 'SKU-012', name: 'Popular Business Book', cost: 45, margin: 180 },
                  { sku: 'SKU-089', name: 'Best Seller Novel', cost: 38, margin: 156 },
                  { sku: 'SKU-234', name: 'Study Guide', cost: 52, margin: 198 },
                ].map((product) => (
                  <div key={product.sku} className="flex justify-between items-center p-3 bg-green-50 rounded-lg">
                    <div>
                      <p className="font-semibold text-sm">{product.name}</p>
                      <p className="text-xs text-muted-foreground">{product.sku}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-green-600">${product.margin}</p>
                      <p className="text-xs text-muted-foreground">Cost: ${product.cost}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Action Items */}
          <Card className="border-blue-200">
            <CardHeader>
              <CardTitle className="text-blue-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Recommended Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-3 bg-blue-50 rounded-lg">
                  <h4 className="font-semibold text-sm text-blue-800">Immediate</h4>
                  <p className="text-xs text-blue-700 mt-1">Review pricing for 18 low-margin items</p>
                </div>
                <div className="p-3 bg-amber-50 rounded-lg">
                  <h4 className="font-semibold text-sm text-amber-800">Short Term</h4>
                  <p className="text-xs text-amber-700 mt-1">Liquidate 23 obsolete products</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg">
                  <h4 className="font-semibold text-sm text-green-800">Long Term</h4>
                  <p className="text-xs text-green-700 mt-1">Optimize inventory turnover rate</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderInventoryAgeingResults = () => {
    const ageingData = [
      { category: '0-30 days', value: 45000, count: 156, color: '#10B981' },
      { category: '31-60 days', value: 32000, count: 112, color: '#F59E0B' },
      { category: '61-90 days', value: 18000, count: 78, color: '#EF4444' },
      { category: '90+ days (Dead)', value: 12000, count: 45, color: '#7F1D1D' },
    ];

    const trendData = [
      { month: 'Jan', deadStock: 8, slowMoving: 23, fastMoving: 169 },
      { month: 'Feb', deadStock: 12, slowMoving: 28, fastMoving: 160 },
      { month: 'Mar', deadStock: 15, slowMoving: 35, fastMoving: 150 },
      { month: 'Apr', deadStock: 18, slowMoving: 31, fastMoving: 151 },
      { month: 'May', deadStock: 22, slowMoving: 29, fastMoving: 149 },
      { month: 'Jun', deadStock: 25, slowMoving: 26, fastMoving: 149 },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-red-200 bg-gradient-to-br from-red-50 to-red-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-red-700 flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Dead Stock Items
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {analysisData?.dead_stock_count || 45}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items not sold in 90+ days
              </p>
              <p className="text-xs text-red-600 mt-1">Urgent liquidation needed</p>
            </CardContent>
          </Card>
          
          <Card className="border-red-300 bg-gradient-to-br from-red-100 to-red-200">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-red-800 flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Dead Stock Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-700">
                ${analysisData?.dead_stock_value?.toLocaleString() || '12,000'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Value tied up in dead inventory
              </p>
              <div className="mt-2">
                <Progress value={8} className="h-2 bg-red-200" />
                <p className="text-xs text-red-700 mt-1">8% of total inventory value</p>
              </div>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-gradient-to-br from-amber-50 to-amber-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-amber-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Slow Moving
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-amber-600">
                {analysisData?.slow_moving_count || 78}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items aged 61-90 days
              </p>
              <p className="text-xs text-amber-600 mt-1">Monitor closely</p>
            </CardContent>
          </Card>

          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-green-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Fast Moving
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {analysisData?.fast_moving_count || 149}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Items sold within 30 days
              </p>
              <p className="text-xs text-green-600 mt-1">Healthy turnover</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Age Distribution */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Inventory Age Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={ageingData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={120}
                    dataKey="value"
                    label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
                  >
                    {ageingData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Value']} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Aging Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Inventory Movement Trend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Area 
                    type="monotone" 
                    dataKey="fastMoving" 
                    stackId="1" 
                    stroke="#10B981" 
                    fill="#10B981" 
                    fillOpacity={0.8}
                    name="Fast Moving"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="slowMoving" 
                    stackId="1" 
                    stroke="#F59E0B" 
                    fill="#F59E0B" 
                    fillOpacity={0.8}
                    name="Slow Moving"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="deadStock" 
                    stackId="1" 
                    stroke="#EF4444" 
                    fill="#EF4444" 
                    fillOpacity={0.8}
                    name="Dead Stock"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Critical Items Table */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-5 w-5" />
              Critical Dead Stock Items - Immediate Action Required
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-red-200">
                    <th className="text-left p-3 text-red-700">SKU</th>
                    <th className="text-left p-3 text-red-700">Product Name</th>
                    <th className="text-left p-3 text-red-700">Days in Stock</th>
                    <th className="text-left p-3 text-red-700">Quantity</th>
                    <th className="text-left p-3 text-red-700">Value</th>
                    <th className="text-left p-3 text-red-700">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { sku: 'SKU-789', name: 'Outdated Programming Guide', days: 156, qty: 25, value: 875 },
                    { sku: 'SKU-456', name: 'Last Year\'s Calendar', days: 145, qty: 50, value: 250 },
                    { sku: 'SKU-123', name: 'Obsolete Software Manual', days: 134, qty: 12, value: 360 },
                    { sku: 'SKU-321', name: 'Old Edition Textbook', days: 128, qty: 18, value: 720 },
                    { sku: 'SKU-654', name: 'Seasonal Poetry Book', days: 115, qty: 8, value: 160 },
                  ].map((item, index) => (
                    <tr key={index} className="border-b border-red-100 hover:bg-red-50">
                      <td className="p-3 font-mono text-xs">{item.sku}</td>
                      <td className="p-3 text-sm">{item.name}</td>
                      <td className="p-3">
                        <span className="px-2 py-1 bg-red-100 text-red-800 rounded-full text-xs font-bold">
                          {item.days} days
                        </span>
                      </td>
                      <td className="p-3 text-center">{item.qty}</td>
                      <td className="p-3 font-semibold">${item.value}</td>
                      <td className="p-3">
                        <Button size="sm" variant="destructive" className="text-xs">
                          Liquidate
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Action Recommendations */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="text-red-700 text-lg">Immediate Actions</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Liquidate 45 dead stock items
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Discount slow-moving inventory
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  Review procurement policies
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-amber-200 bg-amber-50">
            <CardHeader>
              <CardTitle className="text-amber-700 text-lg">Prevention Strategies</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                  Implement better demand forecasting
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                  Set automated reorder points
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full"></div>
                  Regular inventory audits
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-green-700 text-lg">Optimization Goals</CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Reduce dead stock to &lt;5%
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Increase inventory turnover
                </li>
                <li className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  Maintain 30-day average age
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderInventoryValuationResults = () => {
    const valuationData = [
      { category: 'Business Books', fifoValue: 45000, sellingValue: 58000, difference: 13000 },
      { category: 'Fiction', fifoValue: 32000, sellingValue: 39000, difference: 7000 },
      { category: 'Technical', fifoValue: 28000, sellingValue: 35000, difference: 7000 },
      { category: 'Academic', fifoValue: 35000, sellingValue: 42000, difference: 7000 },
      { category: 'Children', fifoValue: 18000, sellingValue: 22000, difference: 4000 },
    ];

    const trendData = [
      { month: 'Jan', fifo: 145000, market: 168000 },
      { month: 'Feb', fifo: 148000, market: 172000 },
      { month: 'Mar', fifo: 152000, market: 178000 },
      { month: 'Apr', fifo: 156000, market: 182000 },
      { month: 'May', fifo: 159000, market: 186000 },
      { month: 'Jun', fifo: 158000, market: 196000 },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-indigo-200 bg-gradient-to-br from-indigo-50 to-indigo-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-indigo-700 flex items-center gap-2">
                <Package className="h-5 w-5" />
                FIFO Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-indigo-600">
                ${analysisData?.fifo_value?.toLocaleString() || '158,000'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Based on purchase invoices
              </p>
              <div className="mt-2">
                <Progress value={75} className="h-2" />
                <p className="text-xs text-muted-foreground mt-1">Historical cost basis</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-green-700 flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Market Value
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                ${analysisData?.selling_price_value?.toLocaleString() || '196,000'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Current selling price
              </p>
              <div className="mt-2">
                <Progress value={95} className="h-2" />
                <p className="text-xs text-green-600 mt-1">↗ +24% above FIFO</p>
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-blue-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Unrealized Gain
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                ${analysisData?.valuation_difference?.toLocaleString() || '38,000'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Potential profit on inventory
              </p>
              <p className="text-xs text-blue-600 mt-1">24% markup potential</p>
            </CardContent>
          </Card>

          <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-purple-700 flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Turnover Rate
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {analysisData?.turnover_rate || '4.2'}x
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Annual inventory turns
              </p>
              <p className="text-xs text-purple-600 mt-1">Above industry average</p>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Valuation Comparison by Category */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                FIFO vs Market Value by Category
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={valuationData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                  <Bar dataKey="fifoValue" fill="#6366F1" name="FIFO Value" />
                  <Bar dataKey="sellingValue" fill="#10B981" name="Market Value" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Valuation Trend */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <LineChart className="h-5 w-5" />
                Valuation Trend Over Time
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={trendData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, '']} />
                  <Line 
                    type="monotone" 
                    dataKey="fifo" 
                    stroke="#6366F1" 
                    strokeWidth={3}
                    name="FIFO Value"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="market" 
                    stroke="#10B981" 
                    strokeWidth={3}
                    name="Market Value"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Category Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Category Performance Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {valuationData.map((category, index) => {
                const profitMargin = ((category.difference / category.fifoValue) * 100).toFixed(1);
                return (
                  <div key={category.category} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg border">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-indigo-500 to-green-500 text-white rounded-full font-bold text-sm">
                        {index + 1}
                      </div>
                      <div>
                        <h4 className="font-semibold text-gray-900">{category.category}</h4>
                        <p className="text-sm text-muted-foreground">
                          FIFO: ${category.fifoValue.toLocaleString()}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <div className="text-right">
                        <p className="text-lg font-bold text-green-600">
                          ${category.sellingValue.toLocaleString()}
                        </p>
                        <p className="text-sm text-muted-foreground">Market Value</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold text-blue-600">+{profitMargin}%</p>
                        <p className="text-sm text-muted-foreground">Profit Margin</p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-semibold text-gray-900">
                          ${category.difference.toLocaleString()}
                        </p>
                        <p className="text-sm text-muted-foreground">Unrealized Gain</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>

        {/* Strategic Insights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card className="border-green-200 bg-green-50">
            <CardHeader>
              <CardTitle className="text-green-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Strong Performers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span>Business Books</span>
                  <span className="font-bold text-green-600">+28.9%</span>
                </li>
                <li className="flex justify-between">
                  <span>Technical Books</span>
                  <span className="font-bold text-green-600">+25.0%</span>
                </li>
                <li className="flex justify-between">
                  <span>Children's Books</span>
                  <span className="font-bold text-green-600">+22.2%</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
              <CardTitle className="text-blue-700 flex items-center gap-2">
                <Package className="h-5 w-5" />
                Inventory Health
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span>Total Inventory</span>
                  <span className="font-bold">$158K</span>
                </li>
                <li className="flex justify-between">
                  <span>Market Potential</span>
                  <span className="font-bold text-blue-600">$196K</span>
                </li>
                <li className="flex justify-between">
                  <span>Turnover Rate</span>
                  <span className="font-bold text-blue-600">4.2x/year</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          <Card className="border-purple-200 bg-purple-50">
            <CardHeader>
              <CardTitle className="text-purple-700 flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Financial Impact
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-2 text-sm">
                <li className="flex justify-between">
                  <span>Unrealized Gains</span>
                  <span className="font-bold text-purple-600">$38K</span>
                </li>
                <li className="flex justify-between">
                  <span>Margin Potential</span>
                  <span className="font-bold text-purple-600">24.1%</span>
                </li>
                <li className="flex justify-between">
                  <span>Monthly Appreciation</span>
                  <span className="font-bold text-purple-600">$2.1K</span>
                </li>
              </ul>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  };

  const renderProfitabilityResults = () => {
    const vendorMarginData = [
      { vendor: 'Vendor A', margin: 25.5, revenue: 125000 },
      { vendor: 'Vendor B', margin: 18.2, revenue: 89000 },
      { vendor: 'Vendor C', margin: 32.1, revenue: 156000 },
      { vendor: 'Vendor D', margin: 12.8, revenue: 67000 },
      { vendor: 'Vendor E', margin: 28.7, revenue: 134000 },
    ];

    const categoryData = [
      { category: 'Literature', profit: 45000, margin: 22.5 },
      { category: 'Self-help', profit: 38000, margin: 19.2 },
      { category: 'Finance', profit: 52000, margin: 26.1 },
      { category: 'Technology', profit: 41000, margin: 20.8 },
      { category: 'Fiction', profit: 36000, margin: 18.3 },
    ];

    const topSKUs = [
      { sku: 'SKU-001', product: 'Advanced Finance Guide', margin: 45.2, sales: 1250 },
      { sku: 'SKU-002', product: 'Tech Leadership Book', margin: 38.7, sales: 980 },
      { sku: 'SKU-003', product: 'Investment Strategies', margin: 42.1, sales: 1100 },
      { sku: 'SKU-004', product: 'Business Analytics', margin: 36.5, sales: 890 },
      { sku: 'SKU-005', product: 'Digital Marketing', margin: 33.8, sales: 750 },
    ];

    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <Card className="border-green-200 bg-gradient-to-br from-green-50 to-green-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-green-700 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Best Vendor Margin
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">
                {analysisData?.best_vendor_margin || 32.1}%
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Vendor C - Top performer
              </p>
              <div className="mt-2">
                <Progress value={32.1} className="h-2" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="border-red-200 bg-gradient-to-br from-red-50 to-red-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-red-700 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Negative Margin SKUs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">
                {analysisData?.negative_margin_skus_count || 12}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Products losing money
              </p>
              <p className="text-xs text-red-600 mt-1">Requires immediate attention</p>
            </CardContent>
          </Card>

          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-blue-700 flex items-center gap-2">
                <DollarSign className="h-5 w-5" />
                Total Revenue
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">
                ${analysisData?.total_revenue?.toLocaleString() || '571,000'}
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                This quarter
              </p>
              <p className="text-xs text-green-600 mt-1">↗ +8.5% vs last quarter</p>
            </CardContent>
          </Card>

          <Card className="border-purple-200 bg-gradient-to-br from-purple-50 to-purple-100">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg text-purple-700 flex items-center gap-2">
                <Package className="h-5 w-5" />
                Avg Margin
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-600">
                {analysisData?.average_margin || 24.2}%
              </div>
              <p className="text-sm text-muted-foreground mt-1">
                Across all products
              </p>
              <div className="mt-2">
                <Progress value={24.2} className="h-2" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Vendor Margin Chart */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Vendor Margin Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={vendorMarginData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="vendor" />
                  <YAxis />
                  <Tooltip formatter={(value, name) => [
                    name === 'margin' ? `${value}%` : `$${value.toLocaleString()}`, 
                    name === 'margin' ? 'Margin' : 'Revenue'
                  ]} />
                  <Bar dataKey="margin" fill="#10B981" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Category Profitability */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Category Profitability
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categoryData} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" />
                  <YAxis dataKey="category" type="category" width={80} />
                  <Tooltip formatter={(value) => [`$${value.toLocaleString()}`, 'Profit']} />
                  <Bar dataKey="profit" fill="#8B5CF6" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Top Performing SKUs */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Top 5 Products by Gross Margin
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topSKUs.map((sku, index) => (
                <div key={sku.sku} className="flex items-center justify-between p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center justify-center w-8 h-8 bg-gradient-to-r from-green-500 to-blue-500 text-white rounded-full font-bold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-900">{sku.product}</h4>
                      <p className="text-sm text-muted-foreground">SKU: {sku.sku}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-lg font-bold text-green-600">{sku.margin}%</p>
                      <p className="text-sm text-muted-foreground">Margin</p>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-semibold text-gray-900">{sku.sales}</p>
                      <p className="text-sm text-muted-foreground">Units Sold</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Negative Margin Alert */}
        {(analysisData?.negative_margin_skus_count || 12) > 0 && (
          <Card className="border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-700">
                <AlertTriangle className="h-5 w-5" />
                Negative Margin Products - Immediate Action Required
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <p className="text-red-800">
                  {analysisData?.negative_margin_skus_count || 12} products are currently operating at a loss. 
                  These require immediate pricing review or cost optimization.
                </p>
                <div className="flex flex-wrap gap-2">
                  {['SKU-089', 'SKU-156', 'SKU-203', 'SKU-267', 'SKU-334'].map((sku) => (
                    <span key={sku} className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-mono">
                      {sku}: -2.3%
                    </span>
                  ))}
                  <span className="px-3 py-1 bg-red-200 text-red-800 rounded-full text-sm">
                    +{(analysisData?.negative_margin_skus_count || 12) - 5} more
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    );
  };

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 pt-24 pb-12">
        <div className="container max-w-7xl mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Business Intelligence Analysis
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Choose from our comprehensive analysis modules to get detailed insights into your business data
            </p>
          </motion.div>

          {!selectedAnalysis ? (
            /* Analysis Cards Grid */
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {analysisCards.map((card, index) => (
                <motion.div
                  key={card.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.1 * index }}
                >
                  <Card 
                    className="h-full cursor-pointer transition-all duration-300 hover:shadow-lg hover:scale-105 border-2 hover:border-blue-300"
                    onClick={() => handleCardClick(card)}
                  >
                    <CardHeader className="pb-4">
                      <div className="flex items-center gap-3 mb-3">
                        <div className={`p-3 rounded-lg ${card.bgColor}`}>
                          <div className={card.color}>
                            {card.icon}
                          </div>
                        </div>
                        <CardTitle className="text-lg">{card.title}</CardTitle>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <CardDescription className="text-sm leading-relaxed">
                        {card.description}
                      </CardDescription>
                      <div className="flex items-center justify-between mt-4">
                        <Button variant="outline" size="sm" className="pointer-events-none">
                          <Eye className="h-4 w-4 mr-2" />
                          View Analysis
                        </Button>
                        <ArrowRight className="h-5 w-5 text-muted-foreground" />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>
          ) : (
            /* Analysis Results */
            loading ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col items-center justify-center py-20"
              >
                <RefreshCw className="h-12 w-12 animate-spin text-blue-600 mb-4" />
                <h2 className="text-2xl font-semibold text-gray-900 mb-2">
                  Analyzing Data...
                </h2>
                <p className="text-muted-foreground">
                  Please wait while we process your analysis request.
                </p>
              </motion.div>
            ) : (
              renderAnalysisResults()
            )
          )}
        </div>
      </div>
      <FloatingScrollToTop />
    </>
  );
};