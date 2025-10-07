import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { 
  Brain, 
  TrendingUp, 
  AlertTriangle, 
  Target, 
  Lightbulb,
  Clock,
  ArrowRight,
  Star,
  CheckCircle,
  XCircle,
  Eye,
  Download,
  RefreshCw,
  MessageCircle,
  Send,
  User,
  Bot,
  Loader2,
  X
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Input } from '@/components/ui/input';
import { createApiEndpoint } from '@/lib/api';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useToast } from '@/components/ui/use-toast';

interface AIInsight {
  category: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  impact: 'financial' | 'operational' | 'strategic';
  confidence_score: number;
  action_required: boolean;
  timeline: 'immediate' | 'short_term' | 'long_term';
}

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

interface AIInsightsData {
  status: string;
  message: string;
  analysis_type: string;
  timestamp: string;
  overall_assessment: string;
  key_findings: string[];
  executive_summary: string;
  detailed_analysis: string;
  confidence_score: number;
  insights: {
    performance: AIInsight[];
    risks: AIInsight[];
    opportunities: AIInsight[];
    recommendations: AIInsight[];
  };
  summary: {
    total_insights: number;
    high_priority_actions: number;
    critical_issues: number;
    immediate_opportunities: number;
  };
  ai_model: {
    provider: string;
    model: string;
    confidence_score: number;
  };
}

interface AIInsightsPanelProps {
  analysisType?: string;
  onClose?: () => void;
}

export const AIInsightsPanel: React.FC<AIInsightsPanelProps> = ({ 
  analysisType = 'profitability', 
  onClose 
}) => {
  const [insightsData, setInsightsData] = useState<AIInsightsData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [chatSessionId, setChatSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const fetchAIInsights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(createApiEndpoint(`/analyze/${analysisType}/ai-insights`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch AI insights: ${response.statusText}`);
      }

      const data = await response.json();
      setInsightsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error occurred');
      console.error('AI Insights Error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Auto-scroll chat to bottom
  const scrollChatToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollChatToBottom();
  }, [chatMessages]);

  // Initialize chat session
  const startChatSession = async () => {
    setChatLoading(true);
    try {
      const response = await fetch(createApiEndpoint(`/chat/start-session?analysis_type=${analysisType}`), {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        setChatSessionId(data.session_id);
        setChatMessages([{
          role: 'assistant',
          content: data.welcome_message,
          timestamp: new Date().toISOString()
        }]);
      }
    } catch (error) {
      console.error('Error starting chat session:', error);
      toast({
        title: "Chat Error",
        description: "Failed to start chat session",
        variant: "destructive",
      });
    } finally {
      setChatLoading(false);
    }
  };

  // Send chat message
  const sendChatMessage = async () => {
    if (!chatInput.trim() || !chatSessionId) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date().toISOString()
    };

    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setChatLoading(true);

    try {
      const response = await fetch(createApiEndpoint(`/chat/${chatSessionId}`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: chatInput,
          context: insightsData
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: ChatMessage = {
          role: 'assistant',
          content: data.ai_response,
          timestamp: data.timestamp
        };
        setChatMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm sorry, I'm experiencing technical difficulties. Please try again.",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Handle chat start
  const handleStartChat = () => {
    setShowChat(true);
    if (!chatSessionId) {
      startChatSession();
    }
  };

  useEffect(() => {
    // Use real Gemini AI API
    fetchAIInsights();
  }, [analysisType]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-200';
      case 'high': return 'bg-orange-100 text-orange-800 border-orange-200';
      case 'medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'low': return 'bg-green-100 text-green-800 border-green-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTimelineColor = (timeline: string) => {
    switch (timeline) {
      case 'immediate': return 'bg-red-500';
      case 'short_term': return 'bg-orange-500';
      case 'long_term': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  };

  const getImpactIcon = (impact: string) => {
    switch (impact) {
      case 'financial': return <TrendingUp className="h-4 w-4" />;
      case 'operational': return <Target className="h-4 w-4" />;
      case 'strategic': return <Eye className="h-4 w-4" />;
      default: return <Star className="h-4 w-4" />;
    }
  };

  const InsightCard: React.FC<{ insight: AIInsight; index: number }> = ({ insight, index }) => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.1 }}
      className="mb-4"
    >
      <Card className="hover:shadow-md transition-shadow">
        <CardHeader className="pb-3">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              {getImpactIcon(insight.impact)}
              <div>
                <CardTitle className="text-base font-semibold">
                  {insight.title}
                </CardTitle>
                <div className="flex items-center gap-2 mt-1">
                  <Badge className={getSeverityColor(insight.severity)}>
                    {insight.severity.toUpperCase()}
                  </Badge>
                  <div className={`w-2 h-2 rounded-full ${getTimelineColor(insight.timeline)}`} />
                  <span className="text-xs text-gray-500">
                    {insight.timeline.replace('_', ' ')}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="text-xs text-gray-500">
                {Math.round(insight.confidence_score * 100)}% confidence
              </div>
              {insight.action_required ? (
                <CheckCircle className="h-4 w-4 text-green-600" />
              ) : (
                <Eye className="h-4 w-4 text-gray-400" />
              )}
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-gray-700 leading-relaxed">
            {insight.description}
          </p>
          <div className="flex items-center justify-between mt-3">
            <div className="flex items-center gap-2">
              <span className="text-xs font-medium text-gray-500">Impact:</span>
              <Badge variant="outline" className="text-xs">
                {insight.impact}
              </Badge>
            </div>
            <Progress 
              value={insight.confidence_score * 100} 
              className="w-20 h-2"
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
          <h3 className="text-lg font-semibold mb-2">🧠 Generating Real AI Insights</h3>
          <p className="text-gray-600 mb-2">Analyzing your data with Google Gemini AI...</p>
          <p className="text-sm text-gray-500">⏳ This may take 30-60 seconds for real AI processing</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert className="m-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertTitle>AI Insights Unavailable</AlertTitle>
        <AlertDescription>
          {error}
          <Button onClick={fetchAIInsights} variant="outline" size="sm" className="ml-4">
            Retry
          </Button>
        </AlertDescription>
      </Alert>
    );
  }

  if (!insightsData) {
    return (
      <div className="text-center p-8">
        <Brain className="h-12 w-12 mx-auto mb-4 text-gray-400" />
        <h3 className="text-lg font-semibold mb-2">No AI Insights Available</h3>
        <Button onClick={fetchAIInsights}>Generate Insights</Button>
      </div>
    );
  }

  return (
    <div className="w-full max-w-7xl mx-auto p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Brain className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                AI Business Insights
              </h1>
              <p className="text-gray-600">
                Powered by {insightsData.ai_model.provider} {insightsData.ai_model.model}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Badge className="bg-green-100 text-green-800">
              {Math.round(insightsData.confidence_score * 100)}% Confidence
            </Badge>
            <Button onClick={fetchAIInsights} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            {onClose && (
              <Button onClick={onClose} variant="outline" size="sm">
                <XCircle className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </motion.div>

      {/* Summary Cards */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
      >
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {insightsData.summary.total_insights}
            </div>
            <div className="text-sm text-gray-600">Total Insights</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-orange-600">
              {insightsData.summary.high_priority_actions}
            </div>
            <div className="text-sm text-gray-600">Priority Actions</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-red-600">
              {insightsData.summary.critical_issues}
            </div>
            <div className="text-sm text-gray-600">Critical Issues</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600">
              {insightsData.summary.immediate_opportunities}
            </div>
            <div className="text-sm text-gray-600">Opportunities</div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Overall Assessment */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="mb-8"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Overall Assessment
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed">
              {insightsData.overall_assessment}
            </p>
          </CardContent>
        </Card>
      </motion.div>

      {/* Key Findings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="mb-8"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Eye className="h-5 w-5" />
              Key Findings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {insightsData.key_findings.map((finding, index) => (
                <motion.li
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 * index }}
                  className="flex items-start gap-2"
                >
                  <ArrowRight className="h-4 w-4 mt-0.5 text-blue-600 flex-shrink-0" />
                  <span className="text-gray-700">{finding}</span>
                </motion.li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </motion.div>

      {/* Detailed Insights Tabs */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Tabs defaultValue="recommendations" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="recommendations" className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4" />
              Recommendations ({insightsData.insights.recommendations.length})
            </TabsTrigger>
            <TabsTrigger value="opportunities" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Opportunities ({insightsData.insights.opportunities.length})
            </TabsTrigger>
            <TabsTrigger value="risks" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Risks ({insightsData.insights.risks.length})
            </TabsTrigger>
            <TabsTrigger value="performance" className="flex items-center gap-2">
              <Star className="h-4 w-4" />
              Performance ({insightsData.insights.performance.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="recommendations" className="mt-6">
            <div className="space-y-4">
              {insightsData.insights.recommendations.map((insight, index) => (
                <InsightCard key={index} insight={insight} index={index} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="opportunities" className="mt-6">
            <div className="space-y-4">
              {insightsData.insights.opportunities.map((insight, index) => (
                <InsightCard key={index} insight={insight} index={index} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="risks" className="mt-6">
            <div className="space-y-4">
              {insightsData.insights.risks.map((insight, index) => (
                <InsightCard key={index} insight={insight} index={index} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="performance" className="mt-6">
            <div className="space-y-4">
              {insightsData.insights.performance.map((insight, index) => (
                <InsightCard key={index} insight={insight} index={index} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </motion.div>

      {/* Executive Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="mt-8"
      >
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Star className="h-5 w-5" />
              Executive Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 leading-relaxed">
              {insightsData.executive_summary}
            </p>
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <div className="text-xs text-gray-500">
                Generated on {new Date(insightsData.timestamp).toLocaleString()}
              </div>
              <div className="flex gap-2">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export Insights
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Integrated Chat Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
        className="mt-6"
      >
        {!showChat ? (
          <Card className="border-blue-200 bg-gradient-to-br from-blue-50 to-purple-50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-700">
                <Brain className="h-5 w-5" />
                Chat with AI Assistant
              </CardTitle>
              <CardDescription>
                Ask questions about these insights and get personalized advice and deeper analysis.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex-1 pr-4">
                  <p className="text-sm text-muted-foreground mb-3">
                    Ask follow-up questions like:
                  </p>
                  <ul className="text-xs text-muted-foreground space-y-1 mb-4">
                    <li>• "How do I implement these recommendations?"</li>
                    <li>• "What's the expected ROI of these changes?"</li>
                    <li>• "Which recommendation should I prioritize first?"</li>
                    <li>• "Can you explain this insight in more detail?"</li>
                  </ul>
                </div>
                <div className="flex items-center justify-center">
                  <Button
                    onClick={handleStartChat}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <MessageCircle className="h-4 w-4 mr-2" />
                    Start AI Chat
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="border-blue-200 bg-white">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-blue-600" />
                  <CardTitle className="text-lg">AI Business Assistant</CardTitle>
                </div>
                <Button 
                  variant="ghost" 
                  size="sm" 
                  onClick={() => setShowChat(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <CardDescription>
                Ask questions about your profitability insights
              </CardDescription>
            </CardHeader>
            
            <CardContent className="flex flex-col h-[400px]">
              {/* Chat Messages */}
              <ScrollArea className="flex-1 pr-4 mb-4">
                <div className="space-y-4">
                  {chatMessages.map((message, index) => (
                    <div
                      key={index}
                      className={`flex items-start gap-3 ${
                        message.role === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.role === 'assistant' && (
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                          <Bot className="h-4 w-4 text-blue-600" />
                        </div>
                      )}
                      
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-2 ${
                          message.role === 'user'
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-900'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className={`text-xs mt-1 ${
                          message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                      
                      {message.role === 'user' && (
                        <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center flex-shrink-0">
                          <User className="h-4 w-4 text-white" />
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {chatLoading && (
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center flex-shrink-0">
                        <Bot className="h-4 w-4 text-blue-600" />
                      </div>
                      <div className="bg-gray-100 rounded-lg px-4 py-2">
                        <Loader2 className="h-4 w-4 animate-spin" />
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>
              
              {/* Chat Input */}
              <div className="flex items-center gap-2 pt-2 border-t">
                <Input
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask me about your profitability insights..."
                  onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                  disabled={chatLoading}
                  className="flex-1"
                />
                <Button
                  onClick={sendChatMessage}
                  disabled={!chatInput.trim() || chatLoading}
                  size="sm"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </motion.div>
    </div>
  );
};