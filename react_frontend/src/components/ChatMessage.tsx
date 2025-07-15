import React from 'react';
import { User, Bot } from 'lucide-react';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  imageUrls?: string[];
  timestamp?: Date;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ 
  role, 
  content, 
  imageUrls = [],
  timestamp 
}) => {
  const isUser = role === 'user';

  return (
    <div className={`flex space-x-4 ${isUser ? 'justify-end' : 'justify-start'} mb-6`}>
      {!isUser && (
        <div className="flex-shrink-0">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-full flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
        </div>
      )}
      
      <div className={`max-w-3xl ${isUser ? 'order-1' : 'order-2'}`}>
        <div className={`
          px-4 py-3 rounded-2xl
          ${isUser 
            ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white ml-auto' 
            : 'bg-white border border-gray-200 shadow-sm'
          }
        `}>
          <div className="prose prose-sm max-w-none">
            {content.split('\n').map((line, index) => (
              <p key={index} className={`
                ${index === 0 ? 'mt-0' : 'mt-2'} 
                ${isUser ? 'text-white' : 'text-gray-900'}
              `}>
                {line}
              </p>
            ))}
          </div>
        </div>

        {/* Images */}
        {imageUrls.length > 0 && (
          <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {imageUrls.map((url, index) => (
              <div key={index} className="relative group">
                <img
                  src={url}
                  alt={`Relevant image ${index + 1}`}
                  className="w-full h-32 object-cover rounded-lg border border-gray-200 shadow-sm group-hover:shadow-md transition-shadow"
                />
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 rounded-lg transition-all" />
              </div>
            ))}
          </div>
        )}

        {timestamp && (
          <p className="text-xs text-gray-500 mt-2">
            {timestamp.toLocaleTimeString()}
          </p>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 order-2">
          <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-600" />
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;