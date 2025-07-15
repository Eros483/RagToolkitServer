import React, { useState, useEffect } from 'react';
import { Database, Upload, Trash2, RefreshCw, AlertTriangle } from 'lucide-react';
import { toast } from 'react-toastify';
import { motion } from 'framer-motion';

import FileUpload from '../components/FileUpload';
import LoadingSpinner from '../components/LoadingSpinner';
import { knowledgeBaseAPI } from '../services/api';

interface KnowledgeBaseManagerProps {
  maxTokens: number;
}

interface IndexStatus {
  is_loaded_in_memory: string;
  files_exist_on_disk: string;
  chunk_count: string;
  persistent_dir: string;
}

const KnowledgeBaseManager: React.FC<KnowledgeBaseManagerProps> = ({ maxTokens }) => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [isBuilding, setIsBuilding] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [indexStatus, setIndexStatus] = useState<IndexStatus | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);

  useEffect(() => {
    fetchIndexStatus();
  }, []);

  const fetchIndexStatus = async () => {
    setIsLoadingStatus(true);
    try {
      const response = await knowledgeBaseAPI.getStatus();
      setIndexStatus(response.data);
    } catch (error) {
      toast.error('Error fetching index status');
      console.error('Status fetch error:', error);
    } finally {
      setIsLoadingStatus(false);
    }
  };

  const handleFileSelect = (files: File[]) => {
    setSelectedFiles(files);
  };

  const handleBuildIndex = async () => {
    if (selectedFiles.length === 0) {
      toast.error('Please select at least one file to build the index');
      return;
    }

    setIsBuilding(true);
    try {
      const response = await knowledgeBaseAPI.uploadAndIndex(selectedFiles);
      toast.success(response.data.message || 'Index built successfully!');
      setSelectedFiles([]);
      await fetchIndexStatus();
    } catch (error) {
      toast.error('Error building index. Please try again.');
      console.error('Build index error:', error);
    } finally {
      setIsBuilding(false);
    }
  };

  const handleDeleteIndex = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }

    setIsDeleting(true);
    try {
      const response = await knowledgeBaseAPI.deleteIndex();
      toast.success(response.data.message || 'Index deleted successfully');
      setShowDeleteConfirm(false);
      await fetchIndexStatus();
    } catch (error) {
      toast.error('Error deleting index. Please try again.');
      console.error('Delete index error:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'True' ? 'text-green-600' : 'text-red-600';
  };

  const getStatusIcon = (status: string) => {
    return status === 'True' ? '✅' : '❌';
  };

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Knowledge Base Manager</h1>
        <p className="text-gray-600">
          Build and manage your persistent global knowledge base. This index will be used 
          to augment responses in the RAG Chatbot across all sessions.
        </p>
      </motion.div>

      {/* Current Status */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card mb-6"
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Current Index Status</h3>
          <button
            onClick={fetchIndexStatus}
            disabled={isLoadingStatus}
            className="btn-secondary flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isLoadingStatus ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>

        {isLoadingStatus ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner size="md" />
          </div>
        ) : indexStatus ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Loaded in Memory:</span>
                <span className={`text-sm font-semibold ${getStatusColor(indexStatus.is_loaded_in_memory)}`}>
                  {getStatusIcon(indexStatus.is_loaded_in_memory)} {indexStatus.is_loaded_in_memory}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Files on Disk:</span>
                <span className={`text-sm font-semibold ${getStatusColor(indexStatus.files_exist_on_disk)}`}>
                  {getStatusIcon(indexStatus.files_exist_on_disk)} {indexStatus.files_exist_on_disk}
                </span>
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Chunk Count:</span>
                <span className="text-sm font-semibold text-gray-900">
                  {indexStatus.chunk_count}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Storage Path:</span>
                <span className="text-xs text-gray-600 font-mono truncate max-w-48">
                  {indexStatus.persistent_dir}
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <p>Unable to fetch index status</p>
          </div>
        )}
      </motion.div>

      {/* File Upload */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card mb-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Upload Documents</h3>
        <p className="text-sm text-gray-600 mb-4">
          Upload PDF, TXT, or JSON files to build or update your permanent knowledge base.
        </p>
        
        <FileUpload
          onFileSelect={handleFileSelect}
          acceptedTypes={['.pdf', '.txt', '.json']}
          multiple={true}
          disabled={isBuilding}
        />

        {selectedFiles.length > 0 && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-600">
              {selectedFiles.length} file(s) selected
            </p>
            <button
              onClick={handleBuildIndex}
              disabled={isBuilding}
              className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {isBuilding ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Building Index...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Build/Update Index
                </>
              )}
            </button>
          </div>
        )}
      </motion.div>

      {/* Danger Zone */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card border-red-200"
      >
        <div className="flex items-center space-x-2 mb-4">
          <AlertTriangle className="w-5 h-5 text-red-500" />
          <h3 className="text-lg font-semibold text-red-700">Danger Zone</h3>
        </div>
        
        <p className="text-sm text-gray-600 mb-4">
          Permanently delete the knowledge base index. This action cannot be undone.
        </p>

        {indexStatus?.files_exist_on_disk === 'True' ? (
          <div className="flex items-center space-x-3">
            {!showDeleteConfirm ? (
              <button
                onClick={handleDeleteIndex}
                className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Delete Index
              </button>
            ) : (
              <div className="flex items-center space-x-3">
                <button
                  onClick={handleDeleteIndex}
                  disabled={isDeleting}
                  className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center disabled:opacity-50"
                >
                  {isDeleting ? (
                    <>
                      <LoadingSpinner size="sm" className="mr-2" />
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="w-4 h-4 mr-2" />
                      Confirm Delete
                    </>
                  )}
                </button>
                <button
                  onClick={() => setShowDeleteConfirm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-gray-500">No index found to delete.</p>
        )}
      </motion.div>
    </div>
  );
};

export default KnowledgeBaseManager;