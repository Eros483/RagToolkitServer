import React, { useState, useRef, useEffect } from 'react';
import { Send, Upload, CheckCircle } from 'lucide-react';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import ChatMessage from '../components/ChatMessage';
import { evaluatorAPI } from '../services/api';

interface EvaluationAssistantProps {
  maxTokens: number;
}

interface ChatHistory {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const EvaluationAssistant: React.FC<EvaluationAssistantProps> = ({ maxTokens }) => {
  const [contextFile, setContextFile] = useState<File | null>(null);
  const [metricsFile, setMetricsFile] = useState<File | null>(null);
  const [filesProcessed, setFilesProcessed] = useState(false);
  const [chatHistory, setChatHistory] = useState<ChatHistory[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessingFiles, setIsProcessingFiles] = useState(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [chatHistory]);

  const handleContextFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setContextFile(files[0]);
    }
  };

  const handleMetricsFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setMetricsFile(files[0]);
    }
  };

  const handleProcessFiles = async () => {
    if (!contextFile || !metricsFile) {
      toast.error('Please upload both context and metrics files');
      return;
    }

    setIsProcessingFiles(true);
    setFilesProcessed(false);
    setChatHistory([]);

    try {
      await evaluatorAPI.uploadFiles(contextFile, metricsFile);
      setFilesProcessed(true);
      toast.success('Files processed successfully! You can now ask questions.');
    } catch (error) {
      toast.error('Error processing files. Please try again.');
      console.error('File processing error:', error);
    } finally {
      setIsProcessingFiles(false);
    }
  };

  const handleSendMessage = async () => {
    if (!currentMessage.trim() || isLoading || !filesProcessed) return;

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

      const historyString = JSON.stringify(formattedHistory);
      const response = await evaluatorAPI.askEvaluation(
        currentMessage,
        historyString,
        maxTokens
      );

      const assistantMessage: ChatHistory = {
        role: 'assistant',
        content: response.data.feedback,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, assistantMessage]);
    } catch (error) {
      toast.error('Error getting evaluation feedback. Please try again.');
      console.error('Evaluation error:', error);
      
      const errorMessage: ChatHistory = {
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your evaluation request.',
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

  return (
    <div className="max-w-6xl mx-auto h-full flex flex-col">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Evaluation Assistant</h1>
        <p className="text-gray-600">
          Upload your context and metrics files to get intelligent evaluation feedback and analysis.
        </p>
      </motion.div>

      {/* File Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6"
      >
        {/* Context File Upload */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Context File</h3>
          <FileUpload
            onFileSelect={handleContextFileSelect}
            acceptedTypes={['.pdf', '.json']}
            multiple={false}
            disabled={isProcessingFiles}
          />
          {contextFile && (
            <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                ✅ Context file ready: {contextFile.name}
              </p>
            </div>
          )}
        </div>

        {/* Metrics File Upload */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Metrics File (JSON)</h3>
          <FileUpload
            onFileSelect={handleMetricsFileSelect}
            acceptedTypes={['.json']}
            multiple={false}
            disabled={isProcessingFiles}
          />
          {metricsFile && (
            <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-700">
                ✅ Metrics file ready: {metricsFile.name}
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Process Files Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="mb-6"
      >
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold text-gray-900">Process Files</h3>
              <p className="text-sm text-gray-600">
                Upload both files above, then click to process them for evaluation.
              </p>
            </div>
            <button
              onClick={handleProcessFiles}
              disabled={!contextFile || !metricsFile || isProcessingFiles}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isProcessingFiles ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Processing...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Process Files
                </>
              )}
            </button>
          </div>
          
          {filesProcessed && (
            <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <CheckCircle className="w-5 h-5 text-green-600" />
                <p className="text-sm text-green-700 font-medium">
                  Files processed successfully! You can now ask evaluation questions.
                </p>
              </div>
            </div>
          )}
        </div>
      </motion.div>

      {/* Chat Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex-1 flex flex-col min-h-0"
      >
        <div className="card flex-1 flex flex-col">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Evaluation Feedback Chat</h3>
          
          {/* Chat Messages */}
          <div
            ref={chatContainerRef}
            className="flex-1 overflow-y-auto p-4 space-y-4 min-h-96"
          >
            {!filesProcessed ? (
              <div className="text-center text-gray-500 mt-8">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <CheckCircle className="w-8 h-8 text-white" />
                </div>
                <p className="text-lg font-medium mb-2">Upload and process files first</p>
                <p>Upload both context and metrics files above to enable the evaluation chat.</p>
              </div>
            ) : chatHistory.length === 0 ? (
              <div className="text-center text-gray-500 mt-8">
                <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Send className="w-8 h-8 text-white" />
                </div>
                <p className="text-lg font-medium mb-2">Ready for evaluation questions!</p>
                <p>Ask questions about the evaluation data and get intelligent feedback.</p>
              </div>
            ) : (
              chatHistory.map((message, index) => (
                <ChatMessage
                  key={index}
                  role={message.role}
                  content={message.content}
                  timestamp={message.timestamp}
                />
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="flex items-center space-x-2 bg-gray-100 rounded-2xl px-4 py-3">
                  <LoadingSpinner size="sm" />
                  <span className="text-sm text-gray-600">Analyzing evaluation data...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-3">
              <textarea
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={
                  filesProcessed 
                    ? "Ask a question about the evaluation..." 
                    : "Process files first to enable chat"
                }
                className="input-field resize-none flex-1"
                rows={1}
                disabled={isLoading || !filesProcessed}
              />
              <button
                onClick={handleSendMessage}
                disabled={!currentMessage.trim() || isLoading || !filesProcessed}
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

export default EvaluationAssistant;