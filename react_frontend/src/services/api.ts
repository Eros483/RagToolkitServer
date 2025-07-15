import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// RAG Chatbot API
export const ragAPI = {
  uploadFiles: async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    return api.post('/rag/upload_files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  chat: async (question: string, history: [string, string][], maxTokens: number) => {
    return api.post('/rag/chat/', {
      question,
      history,
      max_tokens: maxTokens
    });
  }
};

// Document Summarizer API
export const summarizerAPI = {
  summarizeDocument: async (file: File, numClusters: number, maxTokens: number) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('num_clusters', numClusters.toString());
    formData.append('max_tokens', maxTokens.toString());
    
    return api.post('/summarizer/summarize_document/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  }
};

// Evaluation Assistant API
export const evaluatorAPI = {
  uploadFiles: async (contextFile: File, metricsFile: File) => {
    const formData = new FormData();
    formData.append('context_file', contextFile);
    formData.append('metrics_file', metricsFile);
    
    return api.post('/evaluator/upload_eval_files/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  askEvaluation: async (question: string, history: string, maxTokens: number) => {
    return api.post('/evaluator/ask_evaluation/', {
      question,
      history,
      max_tokens: maxTokens
    });
  }
};

// Knowledge Base Manager API
export const knowledgeBaseAPI = {
  uploadAndIndex: async (files: File[]) => {
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    return api.post('/persistent_rag/upload_and_index/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
  },

  deleteIndex: async () => {
    return api.post('/persistent_rag/delete_index/');
  },

  getStatus: async () => {
    return api.get('/persistent_rag/status/');
  }
};

// Translator API
export const translatorAPI = {
  translateText: async (text: string, targetLanguage: string) => {
    return api.post('/translator/translate_text/', {
      text,
      target_language: targetLanguage
    });
  }
};

export default api;