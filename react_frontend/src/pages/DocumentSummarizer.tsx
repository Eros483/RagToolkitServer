import React, { useState } from 'react';
import { FileText, Download } from 'lucide-react';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import { summarizerAPI } from '../services/api';

interface DocumentSummarizerProps {
  maxTokens: number;
}

const DocumentSummarizer: React.FC<DocumentSummarizerProps> = ({ maxTokens }) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [summary, setSummary] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [numClusters, setNumClusters] = useState(10);

  const handleFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setSelectedFile(files[0]);
      setSummary(''); // Clear previous summary
    }
  };

  const handleGenerateSummary = async () => {
    if (!selectedFile) {
      toast.error('Please select a file first');
      return;
    }

    setIsLoading(true);
    setSummary('');

    try {
      const response = await summarizerAPI.summarizeDocument(
        selectedFile,
        numClusters,
        maxTokens
      );
      
      setSummary(response.data.summary);
      toast.success('Summary generated successfully!');
    } catch (error) {
      toast.error('Error generating summary. Please try again.');
      console.error('Summary error:', error);
      setSummary('Error: Could not generate summary. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadSummary = () => {
    if (!summary) return;

    const blob = new Blob([summary], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${selectedFile?.name || 'document'}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    toast.success('Summary downloaded!');
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Document Summarizer</h1>
        <p className="text-gray-600">
          Upload a document to get a concise, intelligent summary using advanced clustering techniques.
        </p>
      </motion.div>

      {/* Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Summary Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Number of Clusters: {numClusters}
            </label>
            <input
              type="range"
              min="5"
              max="20"
              value={numClusters}
              onChange={(e) => setNumClusters(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>5</span>
              <span>20</span>
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Tokens: {maxTokens}
            </label>
            <p className="text-sm text-gray-500">
              Controlled via sidebar settings
            </p>
          </div>
        </div>
      </motion.div>

      {/* File Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card mb-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Document</h3>
        <FileUpload
          onFileSelect={handleFileSelect}
          acceptedTypes={['.pdf', '.txt', '.json']}
          multiple={false}
          disabled={isLoading}
        />
        
        {selectedFile && (
          <div className="mt-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <FileText className="w-5 h-5 text-gray-500" />
              <span className="text-sm font-medium text-gray-900">
                Ready to summarize: {selectedFile.name}
              </span>
            </div>
            <button
              onClick={handleGenerateSummary}
              disabled={isLoading}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Generating...
                </>
              ) : (
                'Generate Summary'
              )}
            </button>
          </div>
        )}
      </motion.div>

      {/* Summary Display */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Summary</h3>
          {summary && (
            <button
              onClick={handleDownloadSummary}
              className="btn-secondary flex items-center space-x-2"
            >
              <Download className="w-4 h-4" />
              <span>Download</span>
            </button>
          )}
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <LoadingSpinner size="lg" className="mb-4" />
              <p className="text-gray-600">Generating summary... This may take a moment.</p>
            </div>
          </div>
        ) : summary ? (
          <div className="prose max-w-none">
            <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <pre className="whitespace-pre-wrap text-sm text-gray-800 font-sans">
                {summary}
              </pre>
            </div>
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-4 text-gray-300" />
            <p className="text-lg font-medium mb-2">No summary yet</p>
            <p>Upload a document and click "Generate Summary" to see the results here.</p>
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default DocumentSummarizer;