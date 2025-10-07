/**
 * ChatInterface.tsx - AI Chat Assistant Component
 * 
 * Context-aware chat interface for business intelligence insights
 * Integrates with profitability analysis and other business data
 */

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Badge } from '@/components/ui/badge';
import { 
  MessageCircle, 
  Send, 
  Brain, 
  User, 
  Bot, 
  Loader2, 
  RefreshCw,
  X,
  Minimize2,
  Maximize2
} from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
}

interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  context_loaded: string;
  created_at: string;
}

interface ChatInterfaceProps {
  analysisType?: string;
  initialContext?: any;
  onClose?: () => void;
  minimized?: boolean;
  onMinimize?: () => void;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  analysisType = 'profitability',
  initialContext,
  onClose,
  minimized = false,
  onMinimize
}) => {
  const [session, setSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStartingSession, setIsStartingSession] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const API_BASE = 'http://localhost:8000';

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when component mounts or session starts
  useEffect(() => {
    if (session && !minimized) {
      inputRef.current?.focus();
    }
  }, [session, minimized]);

  const startChatSession = async () => {
    setIsStartingSession(true);
    try {
      const response = await fetch(`${API_BASE}/chat/start-session?analysis_type=${analysisType}`, {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        const newSession: ChatSession = {
          session_id: data.session_id,
          messages: [
            {
              role: 'assistant',
              content: data.welcome_message,
              timestamp: new Date().toISOString()
            }
          ],
          context_loaded: data.context_loaded,
          created_at: data.session_info.created_at
        };

        setSession(newSession);
        setMessages(newSession.messages);
        
        toast({
          title: "Chat Started! 🤖",
          description: `AI assistant ready with ${analysisType} analysis context`,
        });
      } else {
        throw new Error(`Failed to start session: ${response.status}`);
      }
    } catch (error) {
      console.error('Error starting chat session:', error);
      toast({
        title: "Chat Unavailable",
        description: "Unable to start AI chat session. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsStartingSession(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !session || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE}/chat/${session.session_id}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: userMessage.content }),
      });

      if (response.ok) {
        const data = await response.json();
        const aiMessage: ChatMessage = {
          role: 'assistant',
          content: data.ai_response,
          timestamp: data.timestamp
        };

        setMessages(prev => [...prev, aiMessage]);
      } else {
        throw new Error(`Failed to send message: ${response.status}`);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add fallback error message
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: "I apologize, I'm experiencing technical difficulties. Please try again or check the detailed analysis reports for insights.",
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
      
      toast({
        title: "Message Failed",
        description: "Unable to get AI response. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const endSession = async () => {
    if (!session) return;

    try {
      await fetch(`${API_BASE}/chat/${session.session_id}`, {
        method: 'DELETE',
      });
      
      setSession(null);
      setMessages([]);
      
      toast({
        title: "Chat Ended",
        description: "AI chat session ended successfully",
      });
    } catch (error) {
      console.error('Error ending session:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Minimized view
  if (minimized) {
    return (
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="fixed bottom-4 right-4 z-50"
      >
        <Button
          onClick={onMinimize}
          className="h-12 w-12 rounded-full bg-blue-600 hover:bg-blue-700 shadow-lg"
        >
          <MessageCircle className="h-6 w-6 text-white" />
        </Button>
        {session && messages.length > 1 && (
          <Badge className="absolute -top-2 -right-2 bg-red-500 text-white">
            {messages.length - 1}
          </Badge>
        )}
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 20 }}
      className="fixed bottom-4 right-4 w-96 h-[600px] z-50 shadow-2xl"
    >
      <Card className="h-full flex flex-col">
        <CardHeader className="flex-shrink-0 pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-blue-600" />
              <CardTitle className="text-lg">AI Business Assistant</CardTitle>
            </div>
            <div className="flex items-center gap-1">
              {onMinimize && (
                <Button variant="ghost" size="sm" onClick={onMinimize}>
                  <Minimize2 className="h-4 w-4" />
                </Button>
              )}
              {onClose && (
                <Button variant="ghost" size="sm" onClick={onClose}>
                  <X className="h-4 w-4" />
                </Button>
              )}
            </div>
          </div>
          
          {session && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="secondary" className="text-xs">
                {session.context_loaded}
              </Badge>
              <span>•</span>
              <span>{formatTimestamp(session.created_at)}</span>
            </div>
          )}
        </CardHeader>

        <CardContent className="flex-1 flex flex-col p-4 pt-0 min-h-0">
          {!session ? (
            // Start session view
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
              <Brain className="h-12 w-12 text-blue-600" />
              <div>
                <h3 className="text-lg font-semibold mb-2">Start AI Chat</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Get intelligent insights about your {analysisType} analysis with context-aware conversations.
                </p>
              </div>
              <Button 
                onClick={startChatSession}
                disabled={isStartingSession}
                className="w-full"
              >
                {isStartingSession ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Starting Chat...
                  </>
                ) : (
                  <>
                    <MessageCircle className="mr-2 h-4 w-4" />
                    Start Chat Session
                  </>
                )}
              </Button>
            </div>
          ) : (
            // Chat interface
            <>
              {/* Messages area */}
              <ScrollArea className="flex-1 pr-4">
                <div className="space-y-4">
                  <AnimatePresence>
                    {messages.map((message, index) => (
                      <motion.div
                        key={index}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className={`flex gap-3 ${
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        {message.role !== 'user' && (
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                              <Bot className="h-4 w-4 text-blue-600" />
                            </div>
                          </div>
                        )}
                        
                        <div
                          className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-100 text-gray-900'
                          }`}
                        >
                          <div className="whitespace-pre-wrap">{message.content}</div>
                          <div className={`text-xs mt-1 ${
                            message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
                          }`}>
                            {formatTimestamp(message.timestamp)}
                          </div>
                        </div>
                        
                        {message.role === 'user' && (
                          <div className="flex-shrink-0">
                            <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                              <User className="h-4 w-4 text-gray-600" />
                            </div>
                          </div>
                        )}
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  
                  {isLoading && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex gap-3 justify-start"
                    >
                      <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                        <Bot className="h-4 w-4 text-blue-600" />
                      </div>
                      <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm">
                        <div className="flex items-center gap-2">
                          <Loader2 className="h-4 w-4 animate-spin" />
                          AI is thinking...
                        </div>
                      </div>
                    </motion.div>
                  )}
                </div>
                <div ref={messagesEndRef} />
              </ScrollArea>

              {/* Input area */}
              <div className="flex-shrink-0 pt-3 border-t">
                <div className="flex gap-2">
                  <Input
                    ref={inputRef}
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask about your business data..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button
                    onClick={sendMessage}
                    disabled={!inputMessage.trim() || isLoading}
                    size="sm"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
                
                <div className="flex justify-between items-center mt-2">
                  <div className="text-xs text-muted-foreground">
                    {messages.length > 1 ? `${messages.length - 1} messages` : 'Start conversation'}
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={endSession}
                    className="text-xs h-6 px-2"
                  >
                    End Chat
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default ChatInterface;