/**
 * ChatButton.tsx - Floating Chat Button for AI Assistant
 * 
 * A floating action button that opens the AI chat interface
 * Integrates seamlessly with existing analysis dashboards
 */

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, Brain, Sparkles } from 'lucide-react';
import ChatInterface from './ChatInterface';

interface ChatButtonProps {
  analysisType?: string;
  initialContext?: any;
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  showLabel?: boolean;
  variant?: 'floating' | 'inline';
}

export const ChatButton: React.FC<ChatButtonProps> = ({
  analysisType = 'profitability',
  initialContext,
  position = 'bottom-right',
  showLabel = true,
  variant = 'floating'
}) => {
  const [showChat, setShowChat] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);

  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6'
  };

  const toggleChat = () => {
    if (showChat) {
      if (isMinimized) {
        setIsMinimized(false);
      } else {
        setShowChat(false);
        setIsMinimized(false);
      }
    } else {
      setShowChat(true);
      setIsMinimized(false);
    }
  };

  const minimizeChat = () => {
    setIsMinimized(true);
  };

  const closeChat = () => {
    setShowChat(false);
    setIsMinimized(false);
  };

  if (variant === 'inline') {
    return (
      <>
        <Button
          onClick={toggleChat}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white shadow-lg"
          size="lg"
        >
          <Brain className="mr-2 h-5 w-5" />
          Ask AI Assistant
          <Sparkles className="ml-2 h-4 w-4" />
        </Button>

        <AnimatePresence>
          {showChat && (
            <ChatInterface
              analysisType={analysisType}
              initialContext={initialContext}
              onClose={closeChat}
              minimized={isMinimized}
              onMinimize={minimizeChat}
            />
          )}
        </AnimatePresence>
      </>
    );
  }

  return (
    <>
      {/* Floating Action Button */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className={`fixed ${positionClasses[position]} z-40`}
      >
        {!showChat && (
          <div className="relative">
            <Button
              onClick={toggleChat}
              className="h-14 w-14 rounded-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-xl hover:shadow-2xl transition-all duration-300"
              size="lg"
            >
              <MessageCircle className="h-6 w-6 text-white" />
            </Button>
            
            {showLabel && (
              <motion.div
                initial={{ opacity: 0, x: 10 }}
                animate={{ opacity: 1, x: 0 }}
                className="absolute right-16 top-1/2 transform -translate-y-1/2 bg-black text-white px-3 py-1 rounded-lg text-sm whitespace-nowrap shadow-lg"
              >
                Ask AI About Your Data
                <div className="absolute right-0 top-1/2 transform translate-x-1 -translate-y-1/2 w-0 h-0 border-l-4 border-l-black border-t-2 border-b-2 border-t-transparent border-b-transparent"></div>
              </motion.div>
            )}

            {/* Pulsing dot for attention */}
            <motion.div
              animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
              className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white"
            />
          </div>
        )}
      </motion.div>

      {/* Chat Interface */}
      <AnimatePresence>
        {showChat && (
          <ChatInterface
            analysisType={analysisType}
            initialContext={initialContext}
            onClose={closeChat}
            minimized={isMinimized}
            onMinimize={minimizeChat}
          />
        )}
      </AnimatePresence>
    </>
  );
};

export default ChatButton;