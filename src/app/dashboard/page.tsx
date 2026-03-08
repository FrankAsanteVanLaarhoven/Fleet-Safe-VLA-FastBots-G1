'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { GlowCard } from '@/components/ui/glow-card';
import { 
  Activity, 
  Brain, 
  Shield, 
  Globe, 
  Database, 
  Lock, 
  Zap, 
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  Target,
  BarChart3,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Eye,
  EyeOff,
  Cpu,
  Network,
  HardDrive,
  Wifi,
  Server
} from 'lucide-react';

interface AgentStatus {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'error' | 'offline';
  cpu: number;
  memory: number;
  uptime: string;
  lastActivity: string;
  icon: any;
  color: string;
}

export default function DashboardPage() {
  const [agents, setAgents] = useState<AgentStatus[]>([
    {
      id: 'neural-stealth',
      name: 'Neural Stealth Engine',
      status: 'active',
      cpu: 23,
      memory: 45,
      uptime: '2d 14h 32m',
      lastActivity: '2 minutes ago',
      icon: Brain,
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'quantum-tls',
      name: 'Quantum TLS Engine',
      status: 'active',
      cpu: 18,
      memory: 32,
      uptime: '1d 8h 15m',
      lastActivity: '1 minute ago',
      icon: Lock,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'data-locator',
      name: 'Advanced Data Locator',
      status: 'active',
      cpu: 35,
      memory: 58,
      uptime: '3d 6h 42m',
      lastActivity: '30 seconds ago',
      icon: Target,
      color: 'from-green-500 to-emerald-500'
    },
    {
      id: 'autonomous-processor',
      name: 'Autonomous Data Processor',
      status: 'active',
      cpu: 42,
      memory: 67,
      uptime: '1d 22h 8m',
      lastActivity: '5 minutes ago',
      icon: Cpu,
      color: 'from-orange-500 to-red-500'
    },
    {
      id: 'universal-crawler',
      name: 'Universal Crawler',
      status: 'idle',
      cpu: 8,
      memory: 24,
      uptime: '5d 12h 3m',
      lastActivity: '1 hour ago',
      icon: Globe,
      color: 'from-indigo-500 to-purple-500'
    },
    {
      id: 'security-framework',
      name: 'Self-Healing Security',
      status: 'active',
      cpu: 15,
      memory: 28,
      uptime: '4d 18h 55m',
      lastActivity: '10 minutes ago',
      icon: Shield,
      color: 'from-red-500 to-pink-500'
    }
  ]);

  const [systemMetrics, setSystemMetrics] = useState({
    totalCpu: 0,
    totalMemory: 0,
    activeConnections: 0,
    dataProcessed: 0,
    threatsBlocked: 0,
    successRate: 0
  });

  const [isMonitoring, setIsMonitoring] = useState(true);

  useEffect(() => {
    const updateMetrics = () => {
      const totalCpu = agents.reduce((sum, agent) => sum + agent.cpu, 0);
      const totalMemory = agents.reduce((sum, agent) => sum + agent.memory, 0);
      
      setSystemMetrics({
        totalCpu: Math.round(totalCpu / agents.length),
        totalMemory: Math.round(totalMemory / agents.length),
        activeConnections: Math.floor(Math.random() * 1000) + 500,
        dataProcessed: Math.floor(Math.random() * 1000000) + 500000,
        threatsBlocked: Math.floor(Math.random() * 50) + 10,
        successRate: 99.9
      });
    };

    updateMetrics();
    const interval = setInterval(updateMetrics, 5000);
    return () => clearInterval(interval);
  }, [agents]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'idle': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      case 'offline': return 'text-gray-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active': return <CheckCircle className="w-4 h-4" />;
      case 'idle': return <Clock className="w-4 h-4" />;
      case 'error': return <AlertTriangle className="w-4 h-4" />;
      case 'offline': return <EyeOff className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">AuraAI Dashboard</h1>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-300">Live Monitoring</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setIsMonitoring(!isMonitoring)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isMonitoring 
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}
              >
                {isMonitoring ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                <span>{isMonitoring ? 'Pause' : 'Resume'}</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                <RefreshCw className="w-4 h-4" />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* System Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          <GlowCard className="p-6" customSize glowColor="blue">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-cyan-500 rounded-lg flex items-center justify-center">
                <Cpu className="w-5 h-5 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{systemMetrics.totalCpu}%</div>
            <div className="text-sm text-gray-400">Average CPU Usage</div>
          </GlowCard>

          <GlowCard className="p-6" customSize glowColor="purple">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <HardDrive className="w-5 h-5 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{systemMetrics.totalMemory}%</div>
            <div className="text-sm text-gray-400">Memory Usage</div>
          </GlowCard>

          <GlowCard className="p-6" customSize glowColor="green">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                <Network className="w-5 h-5 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{systemMetrics.activeConnections.toLocaleString()}</div>
            <div className="text-sm text-gray-400">Active Connections</div>
          </GlowCard>

          <GlowCard className="p-6" customSize glowColor="orange">
            <div className="flex items-center justify-between mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <TrendingUp className="w-5 h-5 text-green-400" />
            </div>
            <div className="text-2xl font-bold text-white mb-1">{systemMetrics.successRate}%</div>
            <div className="text-sm text-gray-400">Success Rate</div>
          </GlowCard>
        </motion.div>

        {/* Agent Status Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-white mb-6">AI Agent Status</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
              >
                <GlowCard className="p-6 hover:bg-white/10 transition-all duration-300" customSize glowColor="blue">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 bg-gradient-to-r ${agent.color} rounded-lg flex items-center justify-center`}>
                    <agent.icon className="w-6 h-6 text-white" />
                  </div>
                  <div className={`flex items-center space-x-2 ${getStatusColor(agent.status)}`}>
                    {getStatusIcon(agent.status)}
                    <span className="text-sm font-medium capitalize">{agent.status}</span>
                  </div>
                </div>
                
                <h3 className="text-lg font-semibold text-white mb-4">{agent.name}</h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">CPU</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${agent.cpu}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-white">{agent.cpu}%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Memory</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-16 bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${agent.memory}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-white">{agent.memory}%</span>
                    </div>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Uptime</span>
                    <span className="text-sm text-white">{agent.uptime}</span>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-sm text-gray-400">Last Activity</span>
                    <span className="text-sm text-white">{agent.lastActivity}</span>
                  </div>
                </div>
                </GlowCard>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Real-time Activity Feed */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-8"
        >
          <GlowCard className="p-6" customSize glowColor="green">
            <h3 className="text-xl font-semibold text-white mb-4">Real-time Activity</h3>
            <div className="space-y-4">
              {[
                { agent: 'Neural Stealth Engine', action: 'Bypassed Cloudflare protection', time: '2 min ago', status: 'success' },
                { agent: 'Quantum TLS Engine', action: 'Established secure connection', time: '3 min ago', status: 'success' },
                { agent: 'Data Locator', action: 'Extracted 1,247 data points', time: '5 min ago', status: 'success' },
                { agent: 'Autonomous Processor', action: 'Analyzed market trends', time: '7 min ago', status: 'success' },
                { agent: 'Security Framework', action: 'Blocked suspicious request', time: '10 min ago', status: 'warning' }
              ].map((activity, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 glass-section rounded-lg">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.status === 'success' ? 'bg-green-400' : 'bg-yellow-400'
                  }`}></div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{activity.agent}</div>
                    <div className="text-xs text-gray-400">{activity.action}</div>
                  </div>
                  <div className="text-xs text-gray-500">{activity.time}</div>
                </div>
              ))}
            </div>
          </div>

          <GlowCard className="p-6" customSize glowColor="purple">
            <h3 className="text-xl font-semibold text-white mb-4">System Performance</h3>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-400">Data Processed Today</span>
                  <span className="text-sm text-white">{systemMetrics.dataProcessed.toLocaleString()}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-400">Threats Blocked</span>
                  <span className="text-sm text-white">{systemMetrics.threatsBlocked}</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-red-500 to-pink-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-400">Network Latency</span>
                  <span className="text-sm text-white">1.2ms</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full" style={{ width: '90%' }}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-400">System Uptime</span>
                  <span className="text-sm text-white">99.9%</span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style={{ width: '99.9%' }}></div>
                </div>
              </div>
            </div>
          </GlowCard>
        </motion.div>
      </div>
    </div>
  );
} 