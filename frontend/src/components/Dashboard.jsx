import React, { useState, useEffect } from 'react';
import { BarChart3, Users, Clock, TrendingUp, Bot, AlertCircle } from 'lucide-react';

const Dashboard = ({ isConnected }) => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isConnected) {
      fetchAnalytics();
      // Refresh analytics every 30 seconds
      const interval = setInterval(fetchAnalytics, 30000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/analytics');
      if (response.ok) {
        const data = await response.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!isConnected) {
    return (
      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10">
        <div className="flex items-center space-x-2 text-yellow-400">
          <AlertCircle className="w-5 h-5" />
          <span>Connect to server to view analytics</span>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-8 border border-white/10">
        <div className="flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-400"></div>
          <span className="ml-2 text-white">Loading analytics...</span>
        </div>
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Queries',
      value: analytics?.total_queries || 0,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      change: '+12%'
    },
    {
      title: 'Avg Response Time',
      value: `${analytics?.avg_response_time || 0}s`,
      icon: Clock,
      color: 'from-green-500 to-green-600',
      change: '-15%'
    },
    {
      title: 'Satisfaction Score',
      value: `${analytics?.satisfaction_score || 0}/5`,
      icon: TrendingUp,
      color: 'from-purple-500 to-purple-600',
      change: '+8%'
    },
    {
      title: 'AI Accuracy',
      value: '94%',
      icon: Bot,
      color: 'from-orange-500 to-orange-600',
      change: '+3%'
    }
  ];

  const agentData = analytics?.agent_distribution || {};
  const totalAgentQueries = Object.values(agentData).reduce((sum, count) => sum + count, 0);

  return (
    <div className="space-y-6">
      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-400 text-sm font-medium">{stat.title}</p>
                  <p className="text-2xl font-bold text-white mt-1">{stat.value}</p>
                  <p className="text-green-400 text-sm mt-1">{stat.change} from last week</p>
                </div>
                <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-lg flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Agent Distribution */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Agent Distribution</h3>
          <div className="space-y-4">
            {Object.entries(agentData).map(([agent, count]) => {
              const percentage = totalAgentQueries > 0 ? (count / totalAgentQueries) * 100 : 0;
              const colors = {
                technical: 'bg-blue-500',
                billing: 'bg-green-500',
                general: 'bg-purple-500'
              };
              
              return (
                <div key={agent} className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-300 capitalize">{agent} Agent</span>
                    <span className="text-white">{count} queries ({percentage.toFixed(1)}%)</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${colors[agent] || 'bg-gray-500'}`}
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
          <h3 className="text-lg font-semibold text-white mb-4">Performance Metrics</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-gray-300">First Contact Resolution</span>
              <span className="text-green-400 font-semibold">78%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-gray-300">Average Confidence Score</span>
              <span className="text-blue-400 font-semibold">87%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-gray-300">Escalation Rate</span>
              <span className="text-yellow-400 font-semibold">12%</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
              <span className="text-gray-300">System Uptime</span>
              <span className="text-green-400 font-semibold">99.9%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[
            { time: '2 min ago', event: 'Technical query resolved', agent: 'Technical Agent', confidence: '92%' },
            { time: '5 min ago', event: 'Billing inquiry handled', agent: 'Billing Agent', confidence: '88%' },
            { time: '8 min ago', event: 'General support provided', agent: 'General Agent', confidence: '75%' },
            { time: '12 min ago', event: 'Query escalated to human', agent: 'Technical Agent', confidence: '45%' },
            { time: '15 min ago', event: 'Password reset assisted', agent: 'Technical Agent', confidence: '95%' }
          ].map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
              <div className="flex items-center space-x-3">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <div>
                  <p className="text-white text-sm">{activity.event}</p>
                  <p className="text-gray-400 text-xs">{activity.agent} • {activity.time}</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-300">Confidence</p>
                <p className={`text-sm font-semibold ${
                  parseInt(activity.confidence) >= 80 ? 'text-green-400' :
                  parseInt(activity.confidence) >= 60 ? 'text-yellow-400' : 'text-red-400'
                }`}>
                  {activity.confidence}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* System Status */}
      <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
        <h3 className="text-lg font-semibold text-white mb-4">System Status</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="w-3 h-3 bg-green-400 rounded-full mx-auto mb-2"></div>
            <p className="text-green-400 font-semibold">API Server</p>
            <p className="text-gray-300 text-sm">Operational</p>
          </div>
          <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="w-3 h-3 bg-green-400 rounded-full mx-auto mb-2"></div>
            <p className="text-green-400 font-semibold">AI Models</p>
            <p className="text-gray-300 text-sm">Loaded</p>
          </div>
          <div className="text-center p-4 bg-green-500/10 border border-green-500/20 rounded-lg">
            <div className="w-3 h-3 bg-green-400 rounded-full mx-auto mb-2"></div>
            <p className="text-green-400 font-semibold">Database</p>
            <p className="text-gray-300 text-sm">Connected</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;