import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, DollarSign, Package, Users, BarChart3, PieChart, AlertTriangle } from "lucide-react";
import { motion } from "framer-motion";

interface SummaryDashboardProps {
  analysisData: {
    extract?: any;
    'cost-analysis'?: any;
    'ageing-analysis'?: any;
    'fifo-valuation'?: any;
    profitability?: any;
  };
}

export const SummaryDashboard = ({ analysisData }: SummaryDashboardProps) => {
  const extractData = analysisData.extract;
  const costData = analysisData['cost-analysis'];
  const ageingData = analysisData['ageing-analysis'];
  const fifoData = analysisData['fifo-valuation'];
  const profitData = analysisData.profitability;

  const keyMetrics = [
    {
      title: "Total Revenue",
      value: `$${profitData?.summary?.total_revenue?.toLocaleString() || '0'}`,
      icon: <DollarSign className="h-6 w-6" />,
      color: "text-green-600",
      bgColor: "bg-green-100",
    },
    {
      title: "Total Profit",
      value: `$${profitData?.summary?.total_profit?.toLocaleString() || '0'}`,
      icon: <TrendingUp className="h-6 w-6" />,
      color: "text-blue-600",
      bgColor: "bg-blue-100",
    },
    {
      title: "Profit Margin",
      value: `${profitData?.summary?.profit_margin_percentage?.toFixed(1) || '0'}%`,
      icon: <BarChart3 className="h-6 w-6" />,
      color: "text-purple-600",
      bgColor: "bg-purple-100",
    },
    {
      title: "Inventory Value",
      value: `$${costData?.summary?.total_inventory_value?.toLocaleString() || '0'}`,
      icon: <Package className="h-6 w-6" />,
      color: "text-orange-600",
      bgColor: "bg-orange-100",
    },
  ];

  const insights = [
    {
      title: "Top Performing Category",
      value: profitData?.top_categories?.[0]?.category || "N/A",
      metric: `$${profitData?.top_categories?.[0]?.total_profit?.toLocaleString() || '0'} profit`,
      trend: "up",
    },
    {
      title: "Best Vendor by Profit",
      value: profitData?.top_vendors?.[0]?.vendor || "N/A",
      metric: `${profitData?.top_vendors?.[0]?.profit_margin?.toFixed(1) || '0'}% margin`,
      trend: "up",
    },
    {
      title: "Slow Moving Stock",
      value: `${ageingData?.summary?.age_distribution?.['90+_days'] || 0} items`,
      metric: "Over 90 days old",
      trend: "down",
    },
    {
      title: "Active Vendors",
      value: `${costData?.summary?.unique_vendors || 0}`,
      metric: "suppliers tracked",
      trend: "neutral",
    },
  ];

  const riskAlerts = [
    ...(ageingData?.summary?.age_distribution?.['90+_days'] > 0 ? [{
      title: "Aged Inventory Risk",
      description: `${ageingData.summary.age_distribution['90+_days']} items over 90 days old`,
      severity: "high",
    }] : []),
    ...(profitData?.summary?.profit_margin_percentage < 10 ? [{
      title: "Low Profit Margin",
      description: `Overall margin at ${profitData.summary.profit_margin_percentage.toFixed(1)}%`,
      severity: "medium",
    }] : []),
    ...(costData?.summary?.unique_vendors < 5 ? [{
      title: "Vendor Concentration Risk",
      description: `Only ${costData.summary.unique_vendors} active vendors`,
      severity: "medium",
    }] : []),
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
      className="space-y-6"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">Analysis Summary</h2>
        <p className="text-lg text-muted-foreground">
          Comprehensive business intelligence insights from your data
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {keyMetrics.map((metric, index) => (
          <motion.div
            key={metric.title}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <Card className="relative overflow-hidden">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {metric.title}
                    </p>
                    <p className="text-2xl font-bold">{metric.value}</p>
                  </div>
                  <div className={`p-3 rounded-full ${metric.bgColor} ${metric.color}`}>
                    {metric.icon}
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Business Insights */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <PieChart className="h-5 w-5" />
            Key Business Insights
          </CardTitle>
          <CardDescription>
            Strategic insights derived from your business data analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {insights.map((insight, index) => (
              <motion.div
                key={insight.title}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className="flex items-start gap-4 p-4 rounded-lg border bg-card"
              >
                <div className={`p-2 rounded-full ${
                  insight.trend === 'up' ? 'bg-green-100 text-green-600' :
                  insight.trend === 'down' ? 'bg-red-100 text-red-600' :
                  'bg-gray-100 text-gray-600'
                }`}>
                  {insight.trend === 'up' ? <TrendingUp className="h-4 w-4" /> :
                   insight.trend === 'down' ? <TrendingDown className="h-4 w-4" /> :
                   <BarChart3 className="h-4 w-4" />}
                </div>
                <div>
                  <h4 className="font-semibold text-sm text-muted-foreground">
                    {insight.title}
                  </h4>
                  <p className="font-bold text-lg">{insight.value}</p>
                  <p className="text-sm text-muted-foreground">{insight.metric}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Risk Alerts */}
      {riskAlerts.length > 0 && (
        <Card className="border-orange-200 bg-orange-50/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-800">
              <AlertTriangle className="h-5 w-5" />
              Risk Alerts & Recommendations
            </CardTitle>
            <CardDescription>
              Areas that require attention for optimal business performance
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {riskAlerts.map((alert, index) => (
                <motion.div
                  key={alert.title}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-start gap-3 p-3 rounded-lg border bg-white"
                >
                  <Badge variant={alert.severity === 'high' ? 'destructive' : 'secondary'}>
                    {alert.severity.toUpperCase()}
                  </Badge>
                  <div>
                    <h4 className="font-semibold text-sm">{alert.title}</h4>
                    <p className="text-sm text-muted-foreground">{alert.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Data Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Data Processing Summary
          </CardTitle>
          <CardDescription>
            Overview of all processed business documents and records
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600">
                {extractData?.inventory_items?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Inventory Items</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {extractData?.purchase_orders?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Purchase Orders</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600">
                {extractData?.invoices?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">Sales Invoices</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-orange-600">
                {extractData?.grns?.length || 0}
              </div>
              <div className="text-sm text-muted-foreground">GRN Records</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};