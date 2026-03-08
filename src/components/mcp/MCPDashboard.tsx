/**
 * Iron Cloud Nexus AI - MCP Dashboard Component
 * Comprehensive dashboard for MCP server integration and agent management
 */

import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MCPClient, 
  IntelligenceRequest, 
  AgentExecutionRequest, 
  SecurityAuditRequest,
  AgentType,
  SecurityLevel 
} from '@/lib/mcp-client';
import { 
  AgentStatus, 
  PerformanceMetricsDetail, 
  SecurityStatus, 
  StreamingProgress 
} from '@/lib/types/mcp';

// Icons (using Lucide React)
import { 
  Brain, 
  Shield, 
  BarChart3, 
  Zap, 
  Users, 
  Globe, 
  Database, 
  Activity,
  Play,
  Pause,
  RotateCcw,
  Settings,
  Eye,
  Lock,
  Unlock,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  Target,
  Network
} from 'lucide-react';

interface MCPDashboardProps {
  client?: MCPClient;
  className?: string;
}

export const MCPDashboard: React.FC<MCPDashboardProps> = ({ 
  client = new MCPClient({
    baseUrl: process.env.NEXT_PUBLIC_MCP_BASE_URL || 'http://localhost:8000/api/mcp',
    securityLevel: SecurityLevel.MILITARY,
    timeout: 30000,
    retryAttempts: 3
  }),
  className = ''
}) => {
  // State management
  const [isInitialized, setIsInitialized] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Dashboard data
  const [agents, setAgents] = useState<AgentStatus[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetricsDetail | null>(null);
  const [securityStatus, setSecurityStatus] = useState<SecurityStatus | null>(null);
  const [healthStatus, setHealthStatus] = useState<any>(null);
  
  // Intelligence gathering
  const [intelligenceQuery, setIntelligenceQuery] = useState('');
  const [intelligenceResult, setIntelligenceResult] = useState<any>(null);
  const [streamingProgress, setStreamingProgress] = useState<StreamingProgress | null>(null);
  
  // Agent execution
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [agentArguments, setAgentArguments] = useState('');
  const [agentResult, setAgentResult] = useState<any>(null);
  
  // Security audit
  const [auditType, setAuditType] = useState<'basic' | 'comprehensive' | 'military'>('comprehensive');
  const [auditResult, setAuditResult] = useState<any>(null);

  // Initialize MCP client
  useEffect(() => {
    const initializeClient = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const success = await client.initialize();
        setIsInitialized(success);
        
        if (success) {
          await loadDashboardData();
        } else {
          setError('Failed to initialize MCP client');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Initialization failed');
      } finally {
        setIsLoading(false);
      }
    };

    initializeClient();
  }, [client]);

  // Load dashboard data
  const loadDashboardData = useCallback(async () => {
    try {
      const [agentsData, metricsData, securityData, healthData] = await Promise.all([
        client.listAgents(),
        client.getPerformanceMetrics(),
        client.getSecurityStatus(),
        client.healthCheck()
      ]);

      setAgents(agentsData.agents);
      setPerformanceMetrics(metricsData);
      setSecurityStatus(securityData);
      setHealthStatus(healthData);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    }
  }, [client]);

  // Intelligence gathering
  const handleIntelligenceGathering = async () => {
    if (!intelligenceQuery.trim()) return;

    try {
      setIsLoading(true);
      setError(null);
      setIntelligenceResult(null);

      const request: IntelligenceRequest = {
        query: { text: intelligenceQuery },
        priority: 'high',
        timeout: 300
      };

      // Use streaming for real-time progress
      await client.streamIntelligenceGathering(
        request,
        (progress, status) => {
          setStreamingProgress({ progress, status });
        },
        (result) => {
          setIntelligenceResult(result);
          setStreamingProgress(null);
        },
        (error) => {
          setError(error);
          setStreamingProgress(null);
        }
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Intelligence gathering failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Agent execution
  const handleAgentExecution = async () => {
    if (!selectedAgent || !agentArguments.trim()) return;

    try {
      setIsLoading(true);
      setError(null);
      setAgentResult(null);

      const request: AgentExecutionRequest = {
        agentType: selectedAgent,
        arguments: JSON.parse(agentArguments),
        securityLevel: SecurityLevel.MILITARY
      };

      const result = await client.executeAgent(request);
      setAgentResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Agent execution failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Security audit
  const handleSecurityAudit = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setAuditResult(null);

      const request: SecurityAuditRequest = {
        auditType,
        complianceStandards: ['FIPS_140_2_Level_4', 'GDPR', 'HIPAA']
      };

      const result = await client.performSecurityAudit(request);
      setAuditResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Security audit failed');
    } finally {
      setIsLoading(false);
    }
  };

  // Refresh dashboard
  const handleRefresh = () => {
    loadDashboardData();
  };

  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  if (isLoading && !isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg text-gray-600">Initializing Iron Cloud Nexus AI...</p>
        </div>
      </div>
    );
  }

  if (error && !isInitialized) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <XCircle className="h-16 w-16 text-red-500 mx-auto" />
          <h2 className="mt-4 text-xl font-semibold text-red-600">Initialization Failed</h2>
          <p className="mt-2 text-gray-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-6 ${className}`}>
      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <motion.div variants={itemVariants} className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold text-white mb-2">
                Iron Cloud Nexus AI
              </h1>
              <p className="text-gray-300">
                Advanced MCP Server Dashboard - Military-Grade Intelligence Platform
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${isInitialized ? 'bg-green-500' : 'bg-red-500'}`}></div>
                <span className="text-gray-300">
                  {isInitialized ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <button
                onClick={handleRefresh}
                className="p-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
              >
                <RotateCcw className="h-5 w-5 text-white" />
              </button>
            </div>
          </div>
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6 p-4 bg-red-900 border border-red-500 rounded-lg"
          >
            <div className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <span className="text-red-200">{error}</span>
            </div>
          </motion.div>
        )}

        {/* Main Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
          
          {/* System Status */}
          <motion.div variants={itemVariants} className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <Activity className="h-6 w-6 text-blue-400" />
              <h3 className="text-xl font-semibold text-white">System Status</h3>
            </div>
            
            {healthStatus && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Status:</span>
                  <span className={`font-semibold ${
                    healthStatus.status === 'healthy' ? 'text-green-400' : 
                    healthStatus.status === 'degraded' ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {healthStatus.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Active Agents:</span>
                  <span className="text-white">{healthStatus.activeAgents}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Security Level:</span>
                  <span className="text-white">{healthStatus.securityLevel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Uptime:</span>
                  <span className="text-white">{Math.floor(healthStatus.uptime / 3600)}h</span>
                </div>
              </div>
            )}
          </motion.div>

          {/* Security Status */}
          <motion.div variants={itemVariants} className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <Shield className="h-6 w-6 text-green-400" />
              <h3 className="text-xl font-semibold text-white">Security Status</h3>
            </div>
            
            {securityStatus && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Level:</span>
                  <span className="text-white">{securityStatus.securityLevel}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Encryption:</span>
                  <span className="text-white">{securityStatus.encryptionStatus}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Active Sessions:</span>
                  <span className="text-white">{securityStatus.activeSessions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Compliance:</span>
                  <span className="text-green-400">{securityStatus.complianceStandards.length} Standards</span>
                </div>
              </div>
            )}
          </motion.div>

          {/* Performance Metrics */}
          <motion.div variants={itemVariants} className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <BarChart3 className="h-6 w-6 text-purple-400" />
              <h3 className="text-xl font-semibold text-white">Performance</h3>
            </div>
            
            {performanceMetrics?.orchestratorMetrics && (
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-400">Success Rate:</span>
                  <span className="text-white">
                    {(performanceMetrics.orchestratorMetrics.successRate * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Executions:</span>
                  <span className="text-white">{performanceMetrics.orchestratorMetrics.totalExecutions}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Avg Time:</span>
                  <span className="text-white">
                    {performanceMetrics.orchestratorMetrics.averageExecutionTime.toFixed(2)}s
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Total Cost:</span>
                  <span className="text-white">${performanceMetrics.orchestratorMetrics.totalCost.toFixed(2)}</span>
                </div>
              </div>
            )}
          </motion.div>

          {/* Intelligence Gathering */}
          <motion.div variants={itemVariants} className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <Brain className="h-6 w-6 text-blue-400" />
              <h3 className="text-xl font-semibold text-white">Intelligence Gathering</h3>
            </div>
            
            <div className="space-y-4">
              <textarea
                value={intelligenceQuery}
                onChange={(e) => setIntelligenceQuery(e.target.value)}
                placeholder="Enter your intelligence query..."
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 resize-none"
                rows={3}
              />
              
              {streamingProgress && (
                <div className="bg-slate-700 rounded-lg p-3">
                  <div className="flex justify-between text-sm text-gray-300 mb-2">
                    <span>Progress: {streamingProgress.progress}%</span>
                    <span>{streamingProgress.status}</span>
                  </div>
                  <div className="w-full bg-slate-600 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                      style={{ width: `${streamingProgress.progress}%` }}
                    ></div>
                  </div>
                </div>
              )}
              
              <button
                onClick={handleIntelligenceGathering}
                disabled={isLoading || !intelligenceQuery.trim()}
                className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                <Zap className="h-4 w-4" />
                <span>Gather Intelligence</span>
              </button>
              
              {intelligenceResult && (
                <div className="bg-slate-700 rounded-lg p-3 max-h-40 overflow-y-auto">
                  <pre className="text-xs text-gray-300">
                    {JSON.stringify(intelligenceResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>

          {/* Agent Execution */}
          <motion.div variants={itemVariants} className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <Target className="h-6 w-6 text-green-400" />
              <h3 className="text-xl font-semibold text-white">Agent Execution</h3>
            </div>
            
            <div className="space-y-4">
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="">Select Agent</option>
                {agents.map((agent) => (
                  <option key={agent.name} value={agent.name}>
                    {agent.name.replace(/_/g, ' ').toUpperCase()}
                  </option>
                ))}
              </select>
              
              <textarea
                value={agentArguments}
                onChange={(e) => setAgentArguments(e.target.value)}
                placeholder="Enter agent arguments (JSON)..."
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-gray-400 resize-none"
                rows={3}
              />
              
              <button
                onClick={handleAgentExecution}
                disabled={isLoading || !selectedAgent || !agentArguments.trim()}
                className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                <Play className="h-4 w-4" />
                <span>Execute Agent</span>
              </button>
              
              {agentResult && (
                <div className="bg-slate-700 rounded-lg p-3 max-h-40 overflow-y-auto">
                  <pre className="text-xs text-gray-300">
                    {JSON.stringify(agentResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>

          {/* Security Audit */}
          <motion.div variants={itemVariants} className="bg-slate-800 rounded-xl p-6 border border-slate-700">
            <div className="flex items-center space-x-3 mb-4">
              <Lock className="h-6 w-6 text-red-400" />
              <h3 className="text-xl font-semibold text-white">Security Audit</h3>
            </div>
            
            <div className="space-y-4">
              <select
                value={auditType}
                onChange={(e) => setAuditType(e.target.value as any)}
                className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg text-white"
              >
                <option value="basic">Basic Audit</option>
                <option value="comprehensive">Comprehensive Audit</option>
                <option value="military">Military-Grade Audit</option>
              </select>
              
              <button
                onClick={handleSecurityAudit}
                disabled={isLoading}
                className="w-full py-2 px-4 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
              >
                <Shield className="h-4 w-4" />
                <span>Run Security Audit</span>
              </button>
              
              {auditResult && (
                <div className="bg-slate-700 rounded-lg p-3 max-h-40 overflow-y-auto">
                  <pre className="text-xs text-gray-300">
                    {JSON.stringify(auditResult, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          </motion.div>
        </div>

        {/* Agents List */}
        <motion.div variants={itemVariants} className="mt-8 bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center space-x-3 mb-6">
            <Users className="h-6 w-6 text-purple-400" />
            <h3 className="text-xl font-semibold text-white">Active Agents ({agents.length})</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {agents.map((agent) => (
              <div
                key={agent.name}
                className="bg-slate-700 rounded-lg p-4 border border-slate-600 hover:border-slate-500 transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-white text-sm">
                    {agent.name.replace(/_/g, ' ').toUpperCase()}
                  </h4>
                  <div className={`w-2 h-2 rounded-full ${
                    agent.status === 'active' ? 'bg-green-500' : 
                    agent.status === 'inactive' ? 'bg-yellow-500' : 'bg-red-500'
                  }`}></div>
                </div>
                
                <div className="space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Success Rate:</span>
                    <span className="text-white">{(agent.successRate * 100).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Executions:</span>
                    <span className="text-white">{agent.executionCount}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Cost:</span>
                    <span className="text-white">${agent.totalCost.toFixed(2)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};
