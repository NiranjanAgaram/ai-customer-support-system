import React, { useState, useEffect } from 'react';
import ChatInterface from './components/ChatInterface';
import Dashboard from './components/Dashboard';
import { Bot, BarChart3, Settings, Users } from 'lucide-react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Check backend connection
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        setIsConnected(true);
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
      setIsConnected(false);
    }
  };

  const tabs = [
    { id: 'chat', label: 'Customer Chat', icon: Bot },
    { id: 'dashboard', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">AI Customer Support</h1>
                <p className="text-xs text-blue-200">Enterprise Multi-Agent System</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${
                isConnected 
                  ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                  : 'bg-red-500/20 text-red-300 border border-red-500/30'
              }`}>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'}`}></div>
                <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-black/10 backdrop-blur-sm border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center space-x-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-400 text-blue-300'
                      : 'border-transparent text-gray-300 hover:text-white hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {!isConnected && (
          <div className="mb-6 bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <p className="text-red-300 text-sm">
                Backend server is not running. Please start the FastAPI server on port 8000.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'chat' && <ChatInterface isConnected={isConnected} />}
        {activeTab === 'dashboard' && <Dashboard isConnected={isConnected} />}
        {activeTab === 'settings' && (
          <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10">
            <h2 className="text-2xl font-bold text-white mb-4">Settings</h2>
            <p className="text-gray-300">Settings panel coming soon...</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-black/20 backdrop-blur-sm border-t border-white/10 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <p className="text-gray-400 text-sm">
              © 2024 AI Customer Support System. Built with React + FastAPI.
            </p>
            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <span>Version 1.0.0</span>
              <span>•</span>
              <span>Enterprise Grade</span>
              <span>•</span>
              <span>100% Free & Open Source</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;