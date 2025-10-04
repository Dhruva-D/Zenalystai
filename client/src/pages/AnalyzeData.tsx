import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Play, 
  BarChart3, 
  TrendingUp, 
  PieChart, 
  FileText, 
  Settings,
  Zap,
  Brain,
  Target,
  Clock
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Navbar } from "@/components/Navbar";
import { FloatingScrollToTop } from "@/components/FloatingScrollToTop";

export const AnalyzeData = () => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleStartAnalysis = () => {
    setIsAnalyzing(true);
    // Simulate progress
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 500);
  };

  const analysisTypes = [
    {
      icon: TrendingUp,
      title: "Trend Analysis",
      description: "Identify patterns and trends in your data over time",
      color: "from-blue-500 to-cyan-500",
      badge: "Popular"
    },
    {
      icon: PieChart,
      title: "Distribution Analysis",
      description: "Understand data distribution and segment insights",
      color: "from-purple-500 to-pink-500",
      badge: "Recommended"
    },
    {
      icon: BarChart3,
      title: "Comparative Analysis",
      description: "Compare different data sets and metrics",
      color: "from-green-500 to-emerald-500",
      badge: "Advanced"
    },
    {
      icon: Brain,
      title: "Predictive Analysis",
      description: "AI-powered predictions and forecasting",
      color: "from-orange-500 to-red-500",
      badge: "AI-Powered"
    }
  ];

  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "Process thousands of records in seconds"
    },
    {
      icon: Target,
      title: "High Accuracy",
      description: "99.9% accuracy with AI-powered algorithms"
    },
    {
      icon: Brain,
      title: "Smart Insights",
      description: "Automated pattern recognition and anomaly detection"
    },
    {
      icon: FileText,
      title: "Detailed Reports",
      description: "Comprehensive reports with actionable insights"
    }
  ];

  return (
    <>
      <Navbar />
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-purple-50 pt-24 pb-12">
        <div className="container max-w-7xl mx-auto px-4">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Analyze Your{" "}
            <span className="bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              Data Insights
            </span>
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Transform your raw data into actionable business intelligence with our advanced analytics engine
          </p>
        </motion.div>

        {!isAnalyzing ? (
          <>
            {/* Analysis Types */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12"
            >
              {analysisTypes.map((type, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                  className="relative"
                >
                  <Card className="h-full bg-white/80 backdrop-blur-sm border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                    <CardHeader className="pb-3">
                      <div className="flex items-center justify-between mb-2">
                        <div className={`w-12 h-12 bg-gradient-to-r ${type.color} rounded-lg flex items-center justify-center`}>
                          <type.icon className="w-6 h-6 text-white" />
                        </div>
                        <Badge variant="secondary" className="text-xs">
                          {type.badge}
                        </Badge>
                      </div>
                      <CardTitle className="text-lg">{type.title}</CardTitle>
                    </CardHeader>
                    <CardContent className="pt-0">
                      <p className="text-muted-foreground text-sm">{type.description}</p>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </motion.div>

            {/* Main Analysis Card */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="max-w-4xl mx-auto mb-12"
            >
              <Card className="bg-gradient-to-br from-white to-blue-50/50 backdrop-blur-sm border-2 border-blue-100 shadow-2xl">
                <CardContent className="p-12 text-center">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.6, type: "spring", stiffness: 200 }}
                    className="w-24 h-24 mx-auto mb-6 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center shadow-xl"
                  >
                    <BarChart3 className="w-12 h-12 text-white" />
                  </motion.div>
                  
                  <h2 className="text-3xl font-bold mb-4">Ready to Analyze</h2>
                  <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
                    Your data is ready for processing. Click the button below to start the comprehensive analysis and generate insights.
                  </p>

                  <motion.div
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    <Button
                      size="lg"
                      onClick={handleStartAnalysis}
                      className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white px-12 py-6 text-lg shadow-xl hover:shadow-2xl transition-all duration-300"
                    >
                      <Play className="mr-3 w-6 h-6" />
                      Start Analysis
                    </Button>
                  </motion.div>

                  <div className="flex items-center justify-center gap-6 mt-8 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4" />
                      <span>~2-5 minutes</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Zap className="w-4 h-4" />
                      <span>AI-Powered</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Settings className="w-4 h-4" />
                      <span>Automated</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Features Grid */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
              className="grid md:grid-cols-2 lg:grid-cols-4 gap-6"
            >
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.7 + index * 0.1 }}
                  className="bg-white/80 backdrop-blur-sm rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300"
                >
                  <div className="w-12 h-12 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                  <p className="text-muted-foreground text-sm">{feature.description}</p>
                </motion.div>
              ))}
            </motion.div>
          </>
        ) : (
          /* Analysis Progress */
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="max-w-2xl mx-auto"
          >
            <Card className="bg-white/90 backdrop-blur-sm shadow-2xl">
              <CardContent className="p-12 text-center">
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                  className="w-16 h-16 mx-auto mb-6 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center"
                >
                  <Brain className="w-8 h-8 text-white" />
                </motion.div>
                
                <h2 className="text-2xl font-bold mb-4">Analyzing Your Data</h2>
                <p className="text-muted-foreground mb-8">
                  Our AI is processing your data and generating insights...
                </p>

                <div className="space-y-4">
                  <Progress value={progress} className="w-full h-3" />
                  <p className="text-sm text-muted-foreground">
                    {progress < 30 && "Reading and parsing data files..."}
                    {progress >= 30 && progress < 60 && "Performing pattern analysis..."}
                    {progress >= 60 && progress < 90 && "Generating insights and reports..."}
                    {progress >= 90 && "Finalizing analysis..."}
                  </p>
                </div>

                {progress >= 100 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="mt-8"
                  >
                    <Button
                      size="lg"
                      className="bg-gradient-to-r from-green-600 to-emerald-600 text-white"
                    >
                      View Results
                      <TrendingUp className="ml-2 w-5 h-5" />
                    </Button>
                  </motion.div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        )}
        </div>
      </div>
      <FloatingScrollToTop />
    </>
  );
};