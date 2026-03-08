'use client';

import { MCPDashboard } from '@/components/mcp/MCPDashboard';
import { ExpertComponent } from '@/components/expert/ExpertComponent';
import { ExpertAnalyticsDashboard } from '@/components/expert/ExpertAnalyticsDashboard';
import { ExpertAccessibility } from '@/lib/accessibility/ExpertAccessibility';
import { PerformanceMonitor } from '@/lib/performance/PerformanceMonitor';
import { useEffect, useState } from 'react';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'mcp' | 'analytics'>('dashboard');

  useEffect(() => {
    // Initialize expert systems
    ExpertAccessibility.getInstance().setupExpertKeyboardNavigation();
    PerformanceMonitor.getInstance();
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-28">
        {/* Hero Section */}
        <ExpertComponent variant="expert" animationLevel="immersive" className="text-center mb-12">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 expert-fade-in">
            Iron Cloud Nexus AI
          </h1>
          <p className="text-xl text-gray-300 mb-8 expert-slide-in">
            World-Class Expert-Led Benchmarking Platform with Advanced MCP Integration
          </p>
          
          {/* Navigation Tabs */}
          <div className="flex justify-center space-x-4 mb-8">
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                activeTab === 'dashboard'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              Main Dashboard
            </button>
            <button
              onClick={() => setActiveTab('mcp')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                activeTab === 'mcp'
                  ? 'bg-green-600 text-white shadow-lg'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              MCP Integration
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
                activeTab === 'analytics'
                  ? 'bg-purple-600 text-white shadow-lg'
                  : 'bg-slate-700 text-gray-300 hover:bg-slate-600'
              }`}
            >
              Analytics
            </button>
          </div>
        </ExpertComponent>

        {/* Content based on active tab */}
        {activeTab === 'dashboard' && (
          <div className="space-y-8">
            {/* Main Dashboard Content */}
            <ExpertComponent variant="enterprise" animationLevel="smooth" className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6">Iron Cloud Nexus AI Platform</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-semibold text-white mb-4">25 Specialized Agents</h3>
                  <p className="text-gray-300 mb-4">
                    Advanced AI agents with military-grade security and autonomous operation capabilities.
                  </p>
                  <div className="text-sm text-gray-400">
                    <div>• LinkedIn Intelligence</div>
                    <div>• Web Scraping Master</div>
                    <div>• Financial Analysis</div>
                    <div>• Competitive Intelligence</div>
                    <div>• Security Audit</div>
                    <div>• And 20 more specialized agents...</div>
                  </div>
                </div>

                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-semibold text-white mb-4">Military-Grade Security</h3>
                  <p className="text-gray-300 mb-4">
                    FIPS 140-2 Level 4, EAL7, and quantum-safe cryptography for enterprise-grade protection.
                  </p>
                  <div className="text-sm text-gray-400">
                    <div>• FIPS 140-2 Level 4</div>
                    <div>• Common Criteria EAL7</div>
                    <div>• Quantum-Safe Encryption</div>
                    <div>• GDPR & HIPAA Compliant</div>
                    <div>• SOC 2 Type II</div>
                    <div>• Air-Gapped Deployment</div>
                  </div>
                </div>

                <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
                  <h3 className="text-xl font-semibold text-white mb-4">Cost Optimization</h3>
                  <p className="text-gray-300 mb-4">
                    100% LLM cost elimination through intelligent routing and autonomous operation.
                  </p>
                  <div className="text-sm text-gray-400">
                    <div>• Zero LLM Costs</div>
                    <div>• Intelligent Routing</div>
                    <div>• Autonomous Operation</div>
                    <div>• 60-70% Cost Savings</div>
                    <div>• Real-time Optimization</div>
                    <div>• Predictive Scaling</div>
                  </div>
                </div>
              </div>
            </ExpertComponent>

            {/* Competitive Advantages */}
            <ExpertComponent variant="expert" animationLevel="immersive" className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6">Competitive Advantages</h2>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">vs Lindy.ai</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Agent Sophistication:</span>
                      <span className="text-green-400 font-semibold">900% Superior</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Security Level:</span>
                      <span className="text-green-400 font-semibold">Military vs Consumer</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">LinkedIn Intelligence:</span>
                      <span className="text-green-400 font-semibold">Direct API vs Google Scraping</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Cost Structure:</span>
                      <span className="text-green-400 font-semibold">100% Savings vs Ongoing Costs</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">vs Scale AI</h3>
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-300">Independence:</span>
                      <span className="text-green-400 font-semibold">100% vs Meta-Owned</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Cost Savings:</span>
                      <span className="text-green-400 font-semibold">60-70% vs $93K-400K</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Security Level:</span>
                      <span className="text-green-400 font-semibold">Military vs Business</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-300">Market Access:</span>
                      <span className="text-green-400 font-semibold">Government + Enterprise</span>
                    </div>
                  </div>
                </div>
              </div>
            </ExpertComponent>

            {/* MCP Integration Preview */}
            <ExpertComponent variant="premium" animationLevel="smooth" className="p-8">
              <h2 className="text-3xl font-bold text-white mb-6">MCP Integration</h2>
              <p className="text-gray-300 mb-6">
                Advanced Model Context Protocol integration with 25 specialized agents, military-grade security, 
                and autonomous operation capabilities.
              </p>
              <button
                onClick={() => setActiveTab('mcp')}
                className="px-8 py-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors"
              >
                Launch MCP Dashboard
              </button>
            </ExpertComponent>
          </div>
        )}

        {activeTab === 'mcp' && (
          <MCPDashboard />
        )}

        {activeTab === 'analytics' && (
          <ExpertAnalyticsDashboard />
        )}
      </div>
    </div>
  );
} 