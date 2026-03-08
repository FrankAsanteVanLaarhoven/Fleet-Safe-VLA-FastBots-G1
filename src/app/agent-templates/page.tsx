'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { GlowCard } from '@/components/ui/glow-card';

interface AgentTemplate {
  name: string;
  description: string;
  use_cases: string[];
  case_studies: Array<{
    title: string;
    description: string;
    success_rate: string;
    profit_margin?: string;
    impact?: string;
    return?: string;
  }>;
  request_templates: string[];
  industry_specific: Record<string, string[]>;
}

interface AgentTemplates {
  [key: string]: AgentTemplate;
}

export default function AgentTemplatesPage() {
  const [templates, setTemplates] = useState<AgentTemplates>({});
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [customQuery, setCustomQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);

  const agents = [
    { id: 'sports_betting', name: '🎯 Sports Betting Intelligence', icon: '🎯' },
    { id: 'business_insights', name: '💼 Business Intelligence', icon: '💼' },
    { id: 'stock_market', name: '📈 Stock Market Intelligence', icon: '📈' },
    { id: 'resource_agent', name: '🕵️ God-Level Resource Agent', icon: '🕵️' },
    { id: 'web_crawler', name: '🕷️ Advanced Web Crawler', icon: '🕷️' },
    { id: 'computer_vision', name: '👁️ Computer Vision Intelligence', icon: '👁️' },
    { id: 'research_agents', name: '🔬 Research Intelligence', icon: '🔬' },
    { id: 'climate_disaster', name: '🌍 Climate & Disaster Intelligence', icon: '🌍' },
    { id: 'real_estate', name: '🏠 Real Estate Intelligence', icon: '🏠' },
    { id: 'health_agent', name: '🏥 Health Intelligence', icon: '🏥' },
    { id: 'journalism', name: '📰 Journalism Intelligence', icon: '📰' },
    { id: 'global_politics', name: '🌍 Global Politics Intelligence', icon: '🌍' }
  ];

  useEffect(() => {
    loadAgentTemplates();
  }, []);

  const loadAgentTemplates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agent-templates/');
      const data = await response.json();
      setTemplates(data.templates);
    } catch (error) {
      console.error('Error loading agent templates:', error);
      // Mock data when API is not available
      setTemplates({
        sports_betting: {
          name: "Sports Betting Intelligence",
          description: "Professional sports betting analysis with real-time odds, statistical modeling, and predictive analytics.",
          use_cases: [
            "Live match analysis and prediction",
            "Odds comparison across multiple bookmakers",
            "Statistical modeling for bet selection",
            "Risk assessment and bankroll management"
          ],
          case_studies: [
            {
              title: "Premier League Success",
              description: "Achieved 78% win rate over 6 months using advanced statistical modeling",
              success_rate: "78%",
              profit_margin: "+45%",
              impact: "High",
              return: "ROI: 145%"
            }
          ],
          request_templates: [
            "Analyze Manchester United vs Liverpool match with current form and head-to-head statistics",
            "Compare odds across top 5 bookmakers for today's Premier League matches",
            "Generate betting recommendations for NBA games based on recent performance data"
          ],
          industry_specific: {
            football: ["Match prediction", "Goal statistics", "Player performance"],
            basketball: ["Point spreads", "Player props", "Team statistics"]
          }
        },
        business_insights: {
          name: "Business Intelligence",
          description: "Comprehensive business analysis and market intelligence for strategic decision making.",
          use_cases: [
            "Market trend analysis and forecasting",
            "Competitor intelligence gathering",
            "Financial performance analysis"
          ],
          case_studies: [
            {
              title: "Tech Market Analysis",
              description: "Identified emerging market opportunities leading to 200% revenue growth",
              success_rate: "92%",
              profit_margin: "+200%",
              impact: "Very High",
              return: "ROI: 300%"
            }
          ],
          request_templates: [
            "Analyze market trends in the AI industry for Q4 2024",
            "Compare financial performance of top 10 tech companies",
            "Generate competitive analysis report for e-commerce market"
          ],
          industry_specific: {
            technology: ["Market analysis", "Product development", "Competitive intelligence"],
            finance: ["Investment analysis", "Risk assessment", "Portfolio optimization"]
          }
        },
        stock_market: {
          name: "Stock Market Intelligence",
          description: "Advanced stock market analysis with real-time data, technical indicators, and predictive modeling.",
          use_cases: [
            "Real-time market monitoring and alerts",
            "Technical analysis and pattern recognition",
            "Portfolio optimization and risk management"
          ],
          case_studies: [
            {
              title: "Portfolio Optimization",
              description: "Achieved 25% annual returns with 15% lower volatility than market average",
              success_rate: "85%",
              profit_margin: "+25%",
              impact: "High",
              return: "ROI: 125%"
            }
          ],
          request_templates: [
            "Analyze current market sentiment and identify oversold/overbought conditions",
            "Generate technical analysis report for AAPL, GOOGL, and MSFT",
            "Create portfolio optimization recommendations for 100k investment"
          ],
          industry_specific: {
            technology: ["Growth stocks", "Innovation analysis", "Market disruption"],
            healthcare: ["Biotech analysis", "FDA approvals", "Clinical trials"]
          }
        }
      });
    }
  };

  const submitCustomQuery = async () => {
    if (!customQuery.trim() || !selectedAgent) return;
    
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/host-agent/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          prompt: customQuery,
          mode: 'search',
          download_format: 'pdf',
          storage_location: 'local'
        })
      });
      const data = await response.json();
      setResponse(data);
    } catch (error) {
      console.error('Error submitting custom query:', error);
    } finally {
      setLoading(false);
    }
  };

  const fillTemplate = (template: string) => {
    setCustomQuery(template);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32">
        <div className="text-center mb-8">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            🤖 AI Agent Templates
            <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
              {" "}Hub
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto">
            Professional templates, use cases, and case studies for all AI agents. Access comprehensive intelligence across business, sports, finance, security, and more.
          </p>
        </div>

        {/* Agent Selection */}
        <GlowCard className="p-8 mb-8" customSize glowColor="purple">
          <h2 className="text-3xl font-bold text-white mb-6">🤖 Select AI Agent</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.map((agent) => (
              <GlowCard
                key={agent.id}
                className={`p-6 transition-all duration-300 text-left cursor-pointer ${
                  selectedAgent === agent.id
                    ? 'border-2 border-blue-500/50 text-blue-400'
                    : 'text-white hover:bg-white/10'
                }`}
                customSize
                glowColor={selectedAgent === agent.id ? 'blue' : 'purple'}
                onClick={() => setSelectedAgent(agent.id)}
              >
                <div className="text-3xl mb-3">{agent.icon}</div>
                <div className="text-lg font-semibold">{agent.name.split(' ').slice(1).join(' ')}</div>
              </GlowCard>
            ))}
          </div>
        </GlowCard>

        {/* Agent Details */}
        {selectedAgent && templates[selectedAgent] && (
          <div className="space-y-8">
            {/* Agent Overview */}
            <GlowCard className="p-8" customSize glowColor="blue">
              <h2 className="text-3xl font-bold text-white mb-4">{templates[selectedAgent].name}</h2>
              <p className="text-xl text-gray-300 mb-6">{templates[selectedAgent].description}</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Use Cases */}
                <div>
                  <h3 className="text-2xl font-bold text-green-400 mb-4">🎯 Use Cases</h3>
                  <div className="space-y-3">
                    {templates[selectedAgent].use_cases.map((useCase, index) => (
                      <div key={index} className="bg-white/5 rounded-lg p-4 text-white">
                        {useCase}
                      </div>
                    ))}
                  </div>
                </div>

                {/* Industry Specific */}
                <div>
                  <h3 className="text-2xl font-bold text-blue-400 mb-4">🏭 Industry Specific</h3>
                  <div className="space-y-4">
                    {Object.entries(templates[selectedAgent].industry_specific).map(([industry, features]) => (
                      <div key={industry} className="bg-white/5 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-purple-400 mb-2 capitalize">{industry}</h4>
                        <div className="space-y-1">
                          {features.map((feature, index) => (
                            <div key={index} className="text-sm text-gray-300">• {feature}</div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </GlowCard>

            {/* Case Studies */}
            <GlowCard className="p-8" customSize glowColor="green">
              <h3 className="text-3xl font-bold text-white mb-6">📊 Case Studies</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {templates[selectedAgent].case_studies.map((study, index) => (
                  <div key={index} className="bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/30 rounded-lg p-6">
                    <h4 className="text-xl font-bold text-green-400 mb-3">{study.title}</h4>
                    <p className="text-gray-300 mb-4">{study.description}</p>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">{study.success_rate}</div>
                        <div className="text-sm text-gray-400">Success Rate</div>
                      </div>
                      {study.profit_margin && (
                        <div className="text-center">
                          <div className="text-2xl font-bold text-green-400">{study.profit_margin}</div>
                          <div className="text-sm text-gray-400">Profit Margin</div>
                        </div>
                      )}
                      {study.impact && (
                        <div className="text-center">
                          <div className="text-2xl font-bold text-purple-400">{study.impact}</div>
                          <div className="text-sm text-gray-400">Impact</div>
                        </div>
                      )}
                      {study.return && (
                        <div className="text-center">
                          <div className="text-2xl font-bold text-yellow-400">{study.return}</div>
                          <div className="text-sm text-gray-400">Return</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </GlowCard>

            {/* Request Templates */}
            <GlowCard className="p-8" customSize glowColor="purple">
              <h3 className="text-3xl font-bold text-white mb-6">📝 Request Templates</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                {templates[selectedAgent].request_templates.map((template, index) => (
                  <button
                    key={index}
                    onClick={() => fillTemplate(template)}
                    className="bg-white/5 border border-white/10 rounded-lg p-4 text-left text-white hover:bg-white/10 transition-colors"
                  >
                    <div className="text-sm text-gray-400 mb-2">Template {index + 1}</div>
                    <div>{template}</div>
                  </button>
                ))}
              </div>

              {/* Custom Query */}
              <div className="bg-white/5 rounded-lg p-6">
                <h4 className="text-xl font-bold text-white mb-4">🔍 Custom Analysis Request</h4>
                <div className="flex gap-4 mb-4">
                  <input
                    type="text"
                    value={customQuery}
                    onChange={(e) => setCustomQuery(e.target.value)}
                    placeholder="Enter your custom analysis request or select a template above..."
                    className="flex-1 bg-white/10 border border-white/20 rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    onClick={submitCustomQuery}
                    disabled={loading || !customQuery.trim()}
                    className="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-800 text-white font-semibold px-6 py-3 rounded-lg transition-colors"
                  >
                    {loading ? 'Analyzing...' : 'Analyze'}
                  </button>
                </div>

                {/* Response Display */}
                {response && (
                  <div className="bg-white/5 border border-white/10 rounded-lg p-4">
                    <h5 className="text-lg font-semibold text-white mb-3">🤖 Analysis Results</h5>
                    {response.error ? (
                      <div className="text-red-400">{response.error}</div>
                    ) : (
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-400">Request ID:</span>
                            <div className="text-white font-mono">{response.request_id}</div>
                          </div>
                          <div>
                            <span className="text-gray-400">Confidence:</span>
                            <div className="text-green-400 font-bold">{(response.confidence * 100).toFixed(1)}%</div>
                          </div>
                          <div>
                            <span className="text-gray-400">Processing Time:</span>
                            <div className="text-blue-400">{(response.processing_time * 1000).toFixed(2)}ms</div>
                          </div>
                          <div>
                            <span className="text-gray-400">Agents Used:</span>
                            <div className="text-purple-400">{response.agents_used.join(', ')}</div>
                          </div>
                        </div>
                        
                        <div className="bg-black/20 rounded-lg p-4">
                          <h6 className="text-white font-semibold mb-2">Response Data:</h6>
                          <pre className="text-green-400 text-sm overflow-auto max-h-64">
                            {JSON.stringify(response.response_data, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </GlowCard>
          </div>
        )}

        {/* Quick Access to Other Systems */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 mb-8">
          <h3 className="text-3xl font-bold text-white mb-6">🚀 Quick Access</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Link
              href="/sports-betting"
              className="bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 text-center"
            >
              🎯 Live Sports Intelligence
            </Link>
            <Link
              href="/"
              className="bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 text-center"
            >
              🏠 Main Intelligence Hub
            </Link>
            <Link
              href="/dashboard"
              className="bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-4 px-6 rounded-lg transition-all duration-300 transform hover:scale-105 text-center"
            >
              📊 Analytics Dashboard
            </Link>
          </div>
        </div>

        {/* Back to Main */}
        <div className="text-center">
          <Link href="/" className="inline-block bg-purple-600 hover:bg-purple-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors">
            ← Back to Main Hub
          </Link>
        </div>
      </div>
    </div>
  );
} 