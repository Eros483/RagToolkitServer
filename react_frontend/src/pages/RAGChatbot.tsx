import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, Mic, MicOff } from 'lucide-react';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import ChatMessage from '../components/ChatMessage';
import { ragAPI } from '../services/api';

interface RAGChatbotProps {
  maxTokens: number;
}

interface ChatHistory {
  role: 'user' | 'assistant';
  content: string;
  imageUrls?: string[];
  timestamp: Date;
}

const RAGChatbot: React.FC<RAGChatbotProps> = ({ maxTokens }) => {
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [fileUploaded, setFileUploaded] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('English');
  
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const languages = ['English', 'Hindi', 'Tamil'];

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleFileUpload = async (files: File[]) => {
    if (files.length === 0) return;

    setIsLoading(true);
    try {
      await ragAPI.uploadFiles(files);
      setFileUploaded(true);
      setChatHistory([]);
      toast.success(`File "${files[0].name}" processed successfully for RAG!`);
    } catch (error) {
      toast.error('Error processing file. Please try again.');
      console.error('File upload error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    const userMessage: ChatHistory = {
      role: 'user',
      content: currentMessage,
      timestamp: new Date()
    };

    setChatHistory(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      // Format history for backend
      const formattedHistory: [string, string][] = [];
      for (let i = 0; i < chatHistory.length - 1; i += 2) {
        if (chatHistory[i] && chatHistory[i + 1]) {
          formattedHistory.push([
            chatHistory[i].content,
            chatHistory[i + 1].content
          ]);
        }
      }

      const response = await ragAPI.chat(currentMessage, formattedHistory, maxTokens);
      const { answer, image_urls } = response.data;

      const assistantMessage: ChatHistory = {
        role: 'assistant',
        content: answer,
        imageUrls: image_urls || [],
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast.error('Error communicating with RAG system. Please try again.');
      console.error('Chat error:', error);
      
      const errorMessage: ChatHistory = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please ensure the backend is running and try again.',
        timestamp: new Date()
      };
      setChatHistory(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // TODO: Implement voice recording functionality
    toast.info('Voice recording feature coming soon!');
  };

  return (
    <div className="max-w-6xl mx-auto h-full flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">RAG Chatbot</h1>
        <p className="text-gray-600">
          Chat with your documents using advanced AI. Upload files or use the global knowledge base.
        </p>
      </motion.div>

      {/* Settings Bar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col sm:flex-row gap-4 mb-6"
      >
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Output Language
          </label>
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="input-field"
          >
            {languages.map(lang => (
              <option key={lang} value={lang}>{lang}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* File Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-6"
      >
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Upload Session Document (Optional)
          </h3>
          <FileUpload
            onFileSelect={handleFileUpload}
            acceptedTypes={['.pdf', '.txt', '.json']}
            disabled={isLoading}
          />
          {fileUploaded && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-700">
                ✅ Document processed successfully! You can now chat with its content.
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Chat Container */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex-1 flex flex-col min-h-0"
      >
        <div className="card flex-1 flex flex-col">
          {/* Chat Messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 min-h-96"
          >
            {chatHistory.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <div className="w-16 h-16 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send className="w-8 h-8 text-white" />
                </div>
                <p className="text-lg font-medium mb-2">Ready to chat!</p>
                <p>Upload a document or start asking questions about your knowledge base.</p>
              </div>
            ) : (
              chatHistory.map((message, index) => (
                <ChatMessage
                  key={index}
                  role={message.role}
                  content={message.content}
                  imageUrls={message.imageUrls}
                  timestamp={message.timestamp}
                />
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2 bg-gray-100 rounded-2xl px-4 py-3">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-3">
              <div className="flex-1 relative">
                <textarea
                  ref={textareaRef}
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask a question about your documents..."
                  className="input-field resize-none pr-12"
                  rows={1}
                  disabled={isLoading}
                />
                <button
                  onClick={toggleRecording}
                  className={`absolute right-3 top-3 p-1 rounded-full transition-colors ${
                    isRecording 
                      ? 'text-red-500 hover:bg-red-50' 
                      : 'text-gray-400 hover:bg-gray-100'
                  }`}
                  disabled={isLoading}
                >
                  {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                </button>
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!currentMessage.trim() || isLoading}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {isLoading ? (
                  <LoadingSpinner size="sm" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default RAGChatbot;