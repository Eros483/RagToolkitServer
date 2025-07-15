# RAG-Toolkit React Frontend

A modern, responsive React frontend for the RAG-Toolkit application, built with TypeScript and Tailwind CSS.

## 🚀 Features

- **Modern Design**: Clean, Apple-inspired UI with smooth animations
- **Responsive Layout**: Works perfectly on desktop, tablet, and mobile
- **TypeScript**: Full type safety throughout the application
- **Real-time Chat**: Interactive chat interface with message history
- **File Upload**: Drag-and-drop file upload with progress feedback
- **Toast Notifications**: User-friendly feedback for all actions
- **Loading States**: Beautiful loading indicators for better UX

## 🛠️ Tech Stack

- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Framer Motion** for animations
- **React Router** for navigation
- **Axios** for API communication
- **React Toastify** for notifications
- **Lucide React** for icons

## 📦 Installation

1. Navigate to the frontend directory:
```bash
cd react_frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm start
```

The application will open at `http://localhost:3000`

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Layout.tsx      # Main layout with sidebar
│   ├── FileUpload.tsx  # Drag-and-drop file upload
│   ├── LoadingSpinner.tsx
│   └── ChatMessage.tsx # Chat message component
├── pages/              # Page components
│   ├── Dashboard.tsx
│   ├── RAGChatbot.tsx
│   ├── DocumentSummarizer.tsx
│   ├── EvaluationAssistant.tsx
│   └── KnowledgeBaseManager.tsx
├── services/           # API service layer
│   └── api.ts         # Axios configuration and API calls
├── App.tsx            # Main app component
└── index.tsx          # Entry point
```

## 🎨 Design System

The application uses a consistent design system with:

- **Colors**: Purple/blue gradient theme with semantic colors
- **Typography**: Inter font family with consistent sizing
- **Spacing**: 8px grid system
- **Components**: Reusable button, card, and input styles
- **Animations**: Smooth transitions and micro-interactions

## 🔧 Configuration

The frontend is configured to connect to the FastAPI backend at `http://127.0.0.1:8000`. Update the `API_BASE_URL` in `src/services/api.ts` if your backend runs on a different port.

## 📱 Responsive Design

The application is fully responsive with:
- Mobile-first approach
- Collapsible sidebar on mobile
- Adaptive grid layouts
- Touch-friendly interactions

## 🚀 Build for Production

```bash
npm run build
```

This creates an optimized production build in the `build` folder.

## 🤝 API Integration

The frontend seamlessly integrates with all backend endpoints:
- RAG Chatbot API
- Document Summarizer API
- Evaluation Assistant API
- Knowledge Base Manager API
- Translation API

All API calls include proper error handling, loading states, and user feedback.