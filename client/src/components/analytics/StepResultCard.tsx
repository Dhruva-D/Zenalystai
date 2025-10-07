import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CheckCircle, Clock, AlertCircle, TrendingUp, DollarSign, Package, BarChart3 } from "lucide-react";
import { motion } from "framer-motion";

interface StepResult {
  id: string;
  title: string;
  data?: any;
  completed: boolean;
  loading: boolean;
  error?: string;
}

interface StepResultCardProps {
  step: StepResult;
  stepNumber: number;
}

export const StepResultCard = ({ step, stepNumber }: StepResultCardProps) => {
  const getStepIcon = (id: string) => {
    switch (id) {
      case 'extract':
        return <Package className="h-5 w-5" />;
      case 'three-way-matching':
        return <CheckCircle className="h-5 w-5" />;
      case 'verification':
        return <AlertCircle className="h-5 w-5" />;
      case 'cost-analysis':
        return <DollarSign className="h-5 w-5" />;
      case 'ageing-analysis':
        return <Clock className="h-5 w-5" />;
      case 'fifo-valuation':
        return <BarChart3 className="h-5 w-5" />;
      case 'profitability':
        return <TrendingUp className="h-5 w-5" />;
      default:
        return <Package className="h-5 w-5" />;
    }
  };

  const getStatusBadge = () => {
    if (step.error) {
      return <Badge variant="destructive" className="flex items-center gap-1">
        <AlertCircle className="h-3 w-3" />
        Error
      </Badge>;
    }
    if (step.loading) {
      return <Badge variant="secondary" className="flex items-center gap-1">
        <Clock className="h-3 w-3" />
        Processing...
      </Badge>;
    }
    if (step.completed) {
      return <Badge variant="default" className="flex items-center gap-1 bg-green-600">
        <CheckCircle className="h-3 w-3" />
        Completed
      </Badge>;
    }
    return <Badge variant="outline">Pending</Badge>;
  };

  const renderDataSummary = () => {
    if (!step.data || step.error || step.loading) return null;

    switch (step.id) {
      case 'extract':
        return (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">{step.data.inventory_items?.length || 0}</div>
              <div className="text-sm text-muted-foreground">Inventory Items</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">{step.data.purchase_orders?.length || 0}</div>
              <div className="text-sm text-muted-foreground">Purchase Orders</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">{step.data.invoices?.length || 0}</div>
              <div className="text-sm text-muted-foreground">Invoices</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">{step.data.grns?.length || 0}</div>
              <div className="text-sm text-muted-foreground">GRNs</div>
            </div>
          </div>
        );

      case 'cost-analysis':
        const costData = step.data;
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                ${costData.summary?.total_inventory_value?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-muted-foreground">Total Inventory Value</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {costData.summary?.unique_vendors || 0}
              </div>
              <div className="text-sm text-muted-foreground">Active Vendors</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {costData.summary?.categories_analyzed || 0}
              </div>
              <div className="text-sm text-muted-foreground">Categories</div>
            </div>
          </div>
        );

      case 'ageing-analysis':
        const ageingData = step.data;
        return (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {ageingData.summary?.age_distribution?.['0-30_days'] || 0}
              </div>
              <div className="text-sm text-muted-foreground">0-30 Days</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {ageingData.summary?.age_distribution?.['31-60_days'] || 0}
              </div>
              <div className="text-sm text-muted-foreground">31-60 Days</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {ageingData.summary?.age_distribution?.['61-90_days'] || 0}
              </div>
              <div className="text-sm text-muted-foreground">61-90 Days</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {ageingData.summary?.age_distribution?.['90+_days'] || 0}
              </div>
              <div className="text-sm text-muted-foreground">90+ Days</div>
            </div>
          </div>
        );

      case 'fifo-valuation':
        const fifoData = step.data;
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                ${fifoData.summary?.total_fifo_value?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-muted-foreground">FIFO Valuation</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                ${fifoData.summary?.total_cost_of_goods_sold?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-muted-foreground">COGS</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {fifoData.summary?.items_analyzed || 0}
              </div>
              <div className="text-sm text-muted-foreground">Items Analyzed</div>
            </div>
          </div>
        );

      case 'three-way-matching':
        const matchingData = step.data;
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {matchingData.dashboard?.perfect_matches || 0}
              </div>
              <div className="text-sm text-muted-foreground">Perfect Matches</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {matchingData.dashboard?.partial_matches || 0}
              </div>
              <div className="text-sm text-muted-foreground">Partial Matches</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {matchingData.dashboard?.discrepancies || 0}
              </div>
              <div className="text-sm text-muted-foreground">Discrepancies</div>
            </div>
          </div>
        );

      case 'verification':
        const verificationData = step.data;
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {verificationData.summary?.excess_procurement || 0}
              </div>
              <div className="text-sm text-muted-foreground">Excess Procurement</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {verificationData.summary?.short_procurement || 0}
              </div>
              <div className="text-sm text-muted-foreground">Short Procurement</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {verificationData.summary?.perfect_matches || 0}
              </div>
              <div className="text-sm text-muted-foreground">Perfect Matches</div>
            </div>
          </div>
        );

      case 'profitability':
        const profitData = step.data;
        return (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                ${profitData.summary?.total_revenue?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-muted-foreground">Total Revenue</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                ${profitData.summary?.total_profit?.toLocaleString() || '0'}
              </div>
              <div className="text-sm text-muted-foreground">Total Profit</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {profitData.summary?.profit_margin_percentage?.toFixed(1) || '0'}%
              </div>
              <div className="text-sm text-muted-foreground">Profit Margin</div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: stepNumber * 0.1 }}
    >
      <Card className={`transition-all duration-300 ${
        step.completed ? 'border-green-200 bg-green-50/50' : 
        step.error ? 'border-red-200 bg-red-50/50' : 
        step.loading ? 'border-blue-200 bg-blue-50/50' : 
        'border-gray-200'
      }`}>
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className={`p-2 rounded-lg ${
                step.completed ? 'bg-green-100 text-green-600' :
                step.error ? 'bg-red-100 text-red-600' :
                step.loading ? 'bg-blue-100 text-blue-600' :
                'bg-gray-100 text-gray-600'
              }`}>
                {getStepIcon(step.id)}
              </div>
              <div>
                <CardTitle className="text-lg">
                  Step {stepNumber}: {step.title}
                </CardTitle>
                <CardDescription className="mt-1">
                  {step.error ? `Error: ${step.error}` : 
                   step.loading ? 'Processing...' :
                   step.completed ? 'Analysis completed successfully' :
                   'Ready to execute'}
                </CardDescription>
              </div>
            </div>
            {getStatusBadge()}
          </div>
        </CardHeader>
        
        {(step.completed || step.loading) && (
          <CardContent>
            {step.loading && (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                <span className="ml-3 text-sm text-muted-foreground">Processing analysis...</span>
              </div>
            )}
            
            {step.completed && renderDataSummary()}
          </CardContent>
        )}
      </Card>
    </motion.div>
  );
};