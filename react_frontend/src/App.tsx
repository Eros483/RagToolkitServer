import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import RAGChatbot from './pages/RAGChatbot';
import DocumentSummarizer from './pages/DocumentSummarizer';
import EvaluationAssistant from './pages/EvaluationAssistant';
import KnowledgeBaseManager from './pages/KnowledgeBaseManager';

function App() {
  return (
    <Router>
      <div className="App">
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/rag-chatbot" element={<RAGChatbot />} />
            <Route path="/document-summarizer" element={<DocumentSummarizer />} />
            <Route path="/evaluation-assistant" element={<EvaluationAssistant />} />
            <Route path="/knowledge-base" element={<KnowledgeBaseManager />} />
          </Routes>
        </Layout>
        <ToastContainer
          position="top-right"
          autoClose={5000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          rtl={false}
          pauseOnFocusLoss
          draggable
          pauseOnHover
          theme="light"
        />
      </div>
    </Router>
  );
}

export default App;