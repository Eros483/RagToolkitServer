import React from 'react';
import { Link } from 'react-router-dom';
import { 
  MessageCircle, 
  FileText, 
  CheckCircle, 
  Database,
  ArrowRight,
  Sparkles,
  Zap,
  Shield
} from 'lucide-react';
import { motion } from 'framer-motion';

const Dashboard: React.FC = () => {
  const features = [
    {
      icon: MessageCircle,
      title: 'RAG Chatbot',
      description: 'Intelligent conversations powered by your documents with multimodal support',
      href: '/rag-chatbot',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: FileText,
      title: 'Document Summarizer',
      description: 'Get concise summaries of your documents using advanced clustering',
      href: '/document-summarizer',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: CheckCircle,
      title: 'Evaluation Assistant',
      description: 'Analyze and evaluate performance with contextual insights',
      href: '/evaluation-assistant',
      color: 'from-orange-500 to-red-500'
    },
    {
      icon: Database,
      title: 'Knowledge Base Manager',
      description: 'Build and manage your persistent knowledge repository',
      href: '/knowledge-base',
      color: 'from-purple-500 to-pink-500'
    }
  ];

  const highlights = [
    {
      icon: Zap,
      title: 'Lightning Fast',
      description: 'Optimized for speed with local processing'
    },
    {
      icon: Shield,
      title: 'Privacy First',
      description: 'All data processed locally, no external dependencies'
    },
    {
      icon: Sparkles,
      title: 'AI Powered',
      description: 'Advanced LLM integration with custom embeddings'
    }
  ];

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hero Section */}
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="text-center mb-12"
      >
        <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent mb-6">
          Welcome to RAG-Toolkit
        </h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
          Your powerful suite for advanced document understanding, summarization, and intelligent chatbot interactions, 
          all built with cutting-edge AI technology.
        </p>
      </motion.div>

      {/* Feature Cards */}
      <motion.div 
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12"
      >
        {features.map((feature, index) => (
          <motion.div
            key={feature.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 * index }}
            whileHover={{ y: -5 }}
            className="group"
          >
            <Link to={feature.href} className="block">
              <div className="card hover:shadow-xl transition-all duration-300 group-hover:border-gray-300">
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-r ${feature.color} shadow-lg`}>
                    <feature.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-purple-600 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-gray-600 mb-4">
                      {feature.description}
                    </p>
                    <div className="flex items-center text-purple-600 font-medium group-hover:text-purple-700">
                      Get Started
                      <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                    </div>
                  </div>
                </div>
              </div>
            </Link>
          </motion.div>
        ))}
      </motion.div>

      {/* Highlights Section */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.4 }}
        className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-2xl p-8 mb-12"
      >
        <h2 className="text-2xl font-bold text-center text-gray-900 mb-8">
          Why Choose RAG-Toolkit?
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {highlights.map((highlight, index) => (
            <motion.div
              key={highlight.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.5 + 0.1 * index }}
              className="text-center"
            >
              <div className="w-12 h-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4">
                <highlight.icon className="w-6 h-6 text-white" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {highlight.title}
              </h3>
              <p className="text-gray-600">
                {highlight.description}
              </p>
            </motion.div>
          ))}
        </div>
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.6 }}
        className="text-center"
      >
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          Ready to get started?
        </h2>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/rag-chatbot" className="btn-primary inline-flex items-center">
            <MessageCircle className="w-5 h-5 mr-2" />
            Start Chatting
          </Link>
          <Link to="/knowledge-base" className="btn-secondary inline-flex items-center">
            <Database className="w-5 h-5 mr-2" />
            Manage Knowledge Base
          </Link>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;