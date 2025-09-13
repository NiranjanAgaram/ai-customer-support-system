import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import io from 'socket.io-client';

const ChatInterface = ({ isConnected }) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [socket, setSocket] = useState(null);
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  const [customerId] = useState(() => `customer_${Math.random().toString(36).substr(2, 6)}`);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isConnected) {
      // Initialize WebSocket connection
      const newSocket = io('http://localhost:8000', {
        transports: ['websocket']
      });

      newSocket.on('connect', () => {
        console.log('WebSocket connected');
        addSystemMessage('Connected to AI Customer Support');
      });

      newSocket.on('disconnect', () => {
        console.log('WebSocket disconnected');
        addSystemMessage('Disconnected from server');
      });

      newSocket.on('ai_response', (data) => {
        const aiMessage = {
          id: Date.now(),
          type: 'ai',
          content: data.response,
          timestamp: new Date(),
          agentType: data.agent_type,
          confidence: data.confidence,
          responseTime: data.response_time
        };
        setMessages(prev => [...prev, aiMessage]);
        setIsLoading(false);
      });

      setSocket(newSocket);

      // Add welcome message
      addSystemMessage('Welcome to AI Customer Support! How can I help you today?');

      return () => {
        newSocket.close();
      };
    }
  }, [isConnected]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addSystemMessage = (content) => {
    const systemMessage = {
      id: Date.now(),
      type: 'system',
      content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !isConnected) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    if (socket && socket.connected) {
      // Send via WebSocket
      socket.emit('message', {
        query: inputMessage,
        customer_id: customerId,
        session_id: sessionId,
        priority: 'medium'
      });
    } else {
      // Fallback to HTTP API
      try {
        const response = await fetch('http://localhost:8000/api/v1/query', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: inputMessage,
            customer_id: customerId,
            session_id: sessionId,
            priority: 'medium'
          }),
        });

        if (response.ok) {
          const data = await response.json();
          const aiMessage = {
            id: Date.now(),
            type: 'ai',
            content: data.response,
            timestamp: new Date(),
            agentType: data.agent_type,
            confidence: data.confidence,
            responseTime: data.response_time
          };
          setMessages(prev => [...prev, aiMessage]);
        } else {
          addSystemMessage('Error: Failed to get response from server');
        }
      } catch (error) {
        console.error('Error sending message:', error);
        addSystemMessage('Error: Could not connect to server');
      }
      setIsLoading(false);
    }

    setInputMessage('');
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const getAgentIcon = (agentType) => {
    switch (agentType) {
      case 'technical':
        return '🔧';
      case 'billing':
        return '💳';
      case 'general':
        return '💬';
      default:
        return '🤖';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 h-[600px] flex flex-col">
      {/* Chat Header */}
      <div className="p-4 border-b border-white/10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">AI Support Agent</h3>
              <p className="text-sm text-gray-300">Multi-Agent Customer Service</p>
            </div>
          </div>
          <div className="text-xs text-gray-400">
            Session: {sessionId}
          </div>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user'
                  ? 'bg-blue-600 text-white'
                  : message.type === 'system'
                  ? 'bg-gray-600 text-gray-200'
                  : 'bg-white/10 text-white border border-white/20'
              }`}
            >
              {message.type === 'ai' && (
                <div className="flex items-center space-x-2 mb-2 text-xs">
                  <span>{getAgentIcon(message.agentType)}</span>
                  <span className="capitalize text-gray-300">{message.agentType} Agent</span>
                  {message.confidence && (
                    <span className={`${getConfidenceColor(message.confidence)}`}>
                      {(message.confidence * 100).toFixed(0)}%
                    </span>
                  )}
                  {message.responseTime && (
                    <span className="text-gray-400">
                      {message.responseTime.toFixed(1)}s
                    </span>
                  )}
                </div>
              )}
              
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              
              <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
                <span>
                  {message.timestamp.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
                {message.type === 'user' && (
                  <CheckCircle className="w-3 h-3" />
                )}
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white/10 border border-white/20 rounded-lg px-4 py-2 max-w-xs">
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-400"></div>
                <span className="text-sm text-gray-300">AI is thinking...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/10">
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Type your message..." : "Connect to server first..."}
            disabled={!isConnected || isLoading}
            className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows="2"
          />
          <button
            onClick={sendMessage}
            disabled={!isConnected || !inputMessage.trim() || isLoading}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 transition-colors flex items-center justify-center"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        
        <div className="flex items-center justify-between mt-2 text-xs text-gray-400">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>Customer ID: {customerId}</span>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;