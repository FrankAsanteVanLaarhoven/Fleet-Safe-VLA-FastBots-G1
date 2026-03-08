'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Code, 
  Copy, 
  Check, 
  Play, 
  BookOpen, 
  Shield, 
  Brain, 
  Globe,
  Database,
  Lock,
  Target,
  Cpu,
  Zap,
  ArrowRight,
  ExternalLink,
  Terminal,
  FileText,
  Settings,
  Key,
  Eye,
  EyeOff
} from 'lucide-react';

interface ApiEndpoint {
  id: string;
  name: string;
  description: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  agent: string;
  icon: any;
  color: string;
  example: {
    request: string;
    response: string;
  };
}

export default function ApiDocsPage() {
  const [copiedEndpoint, setCopiedEndpoint] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [showApiKey, setShowApiKey] = useState(false);

  const endpoints: ApiEndpoint[] = [
    {
      id: 'neural-stealth',
      name: 'Neural Stealth Engine',
      description: 'Advanced AI-powered protection bypass with neural network learning',
      method: 'POST',
      path: '/api/v1/neural-stealth/bypass',
      agent: 'Neural Stealth Engine',
      icon: Brain,
      color: 'from-purple-500 to-pink-500',
      example: {
        request: `{
  "target_url": "https://example.com",
  "protection_type": "cloudflare",
  "stealth_level": "maximum",
  "learning_mode": true
}`,
        response: `{
  "success": true,
  "bypass_technique": "neural_stealth_v2",
  "response_time": 1.2,
  "confidence_score": 0.98,
  "session_token": "ns_xyz123...",
  "headers": {
    "User-Agent": "Mozilla/5.0...",
    "Accept": "text/html,application/xhtml+xml..."
  }
}`
      }
    },
    {
      id: 'quantum-tls',
      name: 'Quantum TLS Engine',
      description: 'Quantum-resistant TLS connections with advanced encryption',
      method: 'POST',
      path: '/api/v1/quantum-tls/connect',
      agent: 'Quantum TLS Engine',
      icon: Lock,
      color: 'from-blue-500 to-cyan-500',
      example: {
        request: `{
  "target_host": "api.example.com",
  "port": 443,
  "quantum_resistant": true,
  "cipher_suite": "TLS_AES_256_GCM_SHA384"
}`,
        response: `{
  "success": true,
  "connection_id": "qt_abc456...",
  "encryption_level": "quantum_resistant",
  "handshake_time": 0.8,
  "certificate_verified": true,
  "cipher_suite": "TLS_AES_256_GCM_SHA384"
}`
      }
    },
    {
      id: 'data-locator',
      name: 'Advanced Data Locator',
      description: 'Intelligent data discovery and extraction from any source',
      method: 'POST',
      path: '/api/v1/data-locator/extract',
      agent: 'Advanced Data Locator',
      icon: Target,
      color: 'from-green-500 to-emerald-500',
      example: {
        request: `{
  "source_url": "https://example.com/data",
  "data_patterns": ["prices", "ratings", "reviews"],
  "extraction_mode": "intelligent",
  "depth": 3,
  "filters": {
    "date_range": "2024-01-01:2024-12-31",
    "language": "en"
  }
}`,
        response: `{
  "success": true,
  "extracted_data": {
    "prices": [...],
    "ratings": [...],
    "reviews": [...]
  },
  "total_records": 1247,
  "confidence_score": 0.95,
  "processing_time": 2.3
}`
      }
    },
    {
      id: 'autonomous-processor',
      name: 'Autonomous Data Processor',
      description: 'AI-powered data analysis and insights generation',
      method: 'POST',
      path: '/api/v1/autonomous-processor/analyze',
      agent: 'Autonomous Data Processor',
      icon: Cpu,
      color: 'from-orange-500 to-red-500',
      example: {
        request: `{
  "data": [...],
  "analysis_type": "market_trends",
  "timeframe": "30d",
  "insights_level": "deep",
  "output_format": "json"
}`,
        response: `{
  "success": true,
  "analysis_results": {
    "trends": [...],
    "predictions": [...],
    "anomalies": [...]
  },
  "confidence_intervals": {...},
  "processing_time": 5.2,
  "model_version": "autonomous_v3.1"
}`
      }
    },
    {
      id: 'universal-crawler',
      name: 'Universal Crawler',
      description: 'Universal web crawling with advanced protection bypass',
      method: 'POST',
      path: '/api/v1/universal-crawler/crawl',
      agent: 'Universal Crawler',
      icon: Globe,
      color: 'from-indigo-500 to-purple-500',
      example: {
        request: `{
  "urls": ["https://example1.com", "https://example2.com"],
  "crawl_depth": 2,
  "respect_robots": false,
  "parallel_requests": 10,
  "extract_metadata": true
}`,
        response: `{
  "success": true,
  "crawled_pages": 45,
  "extracted_data": {...},
  "metadata": {...},
  "processing_time": 12.5,
  "success_rate": 0.98
}`
      }
    },
    {
      id: 'security-framework',
      name: 'Self-Healing Security',
      description: 'Zero-day threat detection and autonomous security response',
      method: 'POST',
      path: '/api/v1/security-framework/protect',
      agent: 'Self-Healing Security',
      icon: Shield,
      color: 'from-red-500 to-pink-500',
      example: {
        request: `{
  "threat_scan": true,
  "vulnerability_assessment": true,
  "auto_response": true,
  "threat_intelligence": true
}`,
        response: `{
  "success": true,
  "threats_detected": 3,
  "threats_blocked": 3,
  "vulnerabilities_found": 2,
  "auto_patches_applied": 2,
  "security_score": 95,
  "response_time": 0.3
}`
      }
    }
  ];

  const copyToClipboard = async (text: string, endpointId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedEndpoint(endpointId);
      setTimeout(() => setCopiedEndpoint(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-green-500';
      case 'POST': return 'bg-blue-500';
      case 'PUT': return 'bg-yellow-500';
      case 'DELETE': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">API Documentation</h1>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-300">v1.0.0</span>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                <ExternalLink className="w-4 h-4" />
                <span>OpenAPI Spec</span>
              </button>
              <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity">
                <Key className="w-4 h-4" />
                <span>Get API Key</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="flex space-x-1 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg p-1 mb-8">
          {['overview', 'authentication', 'endpoints', 'examples', 'errors'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === tab
                  ? 'bg-white/10 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab.charAt(0).toUpperCase() + tab.slice(1)}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'overview' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-4">Welcome to AuraAI API</h2>
              <p className="text-xl text-gray-300 mb-6">
                Access the full power of our AI agent system through our comprehensive REST API. 
                Each endpoint is powered by specialized AI agents designed for specific tasks.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center">
                  <div className="text-3xl font-bold text-white mb-2">6</div>
                  <div className="text-gray-400">AI Agents</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-white mb-2">99.9%</div>
                  <div className="text-gray-400">Uptime</div>
                </div>
                <div className="text-center">
                  <div className="text-3xl font-bold text-white mb-2">&lt;1ms</div>
                  <div className="text-gray-400">Latency</div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg p-6">
                <h3 className="text-xl font-semibold text-white mb-4">Base URL</h3>
                <div className="flex items-center space-x-4">
                  <code className="flex-1 bg-black/30 text-green-400 p-3 rounded-lg font-mono text-sm">
                    https://api.auraai.com
                  </code>
                  <button
                    onClick={() => copyToClipboard('https://api.auraai.com', 'base-url')}
                    className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                  >
                    {copiedEndpoint === 'base-url' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-white" />}
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'authentication' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">Authentication</h2>
              <p className="text-gray-300 mb-8">
                All API requests require authentication using your API key. Include it in the Authorization header.
              </p>

              <div className="space-y-6">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">API Key</h3>
                  <div className="bg-black/30 rounded-lg p-4">
                    <div className="flex items-center space-x-4">
                      <div className="flex-1">
                        <div className="text-sm text-gray-400 mb-2">Your API Key</div>
                        <div className="font-mono text-white">
                          {showApiKey ? 'aura_live_sk_1234567890abcdef' : '••••••••••••••••••••••••••••••••'}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <button
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                        >
                          {showApiKey ? <EyeOff className="w-4 h-4 text-white" /> : <Eye className="w-4 h-4 text-white" />}
                        </button>
                        <button
                          onClick={() => copyToClipboard('aura_live_sk_1234567890abcdef', 'api-key')}
                          className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                        >
                          {copiedEndpoint === 'api-key' ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-white" />}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">Usage Example</h3>
                  <div className="bg-black/30 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm text-gray-400">cURL</span>
                      <button
                        onClick={() => copyToClipboard(`curl -X POST https://api.auraai.com/api/v1/neural-stealth/bypass \\
  -H "Authorization: Bearer aura_live_sk_1234567890abcdef" \\
  -H "Content-Type: application/json" \\
  -d '{"target_url": "https://example.com"}'`, 'curl-example')}
                        className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                      >
                        {copiedEndpoint === 'curl-example' ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3 text-white" />}
                      </button>
                    </div>
                    <pre className="text-sm text-green-400 overflow-x-auto">
{`curl -X POST https://api.auraai.com/api/v1/neural-stealth/bypass \\
  -H "Authorization: Bearer aura_live_sk_1234567890abcdef" \\
  -H "Content-Type: application/json" \\
  -d '{"target_url": "https://example.com"}'`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'endpoints' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <h2 className="text-3xl font-bold text-white mb-6">API Endpoints</h2>
            
            {endpoints.map((endpoint, index) => (
              <motion.div
                key={endpoint.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8"
              >
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 bg-gradient-to-r ${endpoint.color} rounded-lg flex items-center justify-center`}>
                      <endpoint.icon className="w-6 h-6 text-white" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-white">{endpoint.name}</h3>
                      <p className="text-gray-300">{endpoint.description}</p>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-full text-sm font-medium text-white ${getMethodColor(endpoint.method)}`}>
                    {endpoint.method}
                  </div>
                </div>

                <div className="space-y-6">
                  <div>
                    <h4 className="text-lg font-semibold text-white mb-3">Endpoint</h4>
                    <div className="flex items-center space-x-4">
                      <code className="flex-1 bg-black/30 text-green-400 p-3 rounded-lg font-mono text-sm">
                        {endpoint.path}
                      </code>
                      <button
                        onClick={() => copyToClipboard(endpoint.path, `endpoint-${endpoint.id}`)}
                        className="p-2 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                      >
                        {copiedEndpoint === `endpoint-${endpoint.id}` ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4 text-white" />}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3">Request Example</h4>
                      <div className="bg-black/30 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-400">JSON</span>
                          <button
                            onClick={() => copyToClipboard(endpoint.example.request, `request-${endpoint.id}`)}
                            className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                          >
                            {copiedEndpoint === `request-${endpoint.id}` ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3 text-white" />}
                          </button>
                        </div>
                        <pre className="text-sm text-blue-400 overflow-x-auto">{endpoint.example.request}</pre>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-lg font-semibold text-white mb-3">Response Example</h4>
                      <div className="bg-black/30 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm text-gray-400">JSON</span>
                          <button
                            onClick={() => copyToClipboard(endpoint.example.response, `response-${endpoint.id}`)}
                            className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                          >
                            {copiedEndpoint === `response-${endpoint.id}` ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3 text-white" />}
                          </button>
                        </div>
                        <pre className="text-sm text-green-400 overflow-x-auto">{endpoint.example.response}</pre>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center space-x-4">
                    <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity">
                      <Play className="w-4 h-4" />
                      <span>Try it out</span>
                    </button>
                    <button className="flex items-center space-x-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                      <FileText className="w-4 h-4" />
                      <span>View Schema</span>
                    </button>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {activeTab === 'examples' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">Code Examples</h2>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">JavaScript/Node.js</h3>
                  <div className="bg-black/30 rounded-lg p-4">
                    <pre className="text-sm text-yellow-400 overflow-x-auto">
{`const response = await fetch('https://api.auraai.com/api/v1/neural-stealth/bypass', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer aura_live_sk_1234567890abcdef',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    target_url: 'https://example.com',
    protection_type: 'cloudflare',
    stealth_level: 'maximum'
  })
});

const data = await response.json();
console.log(data);`}
                    </pre>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold text-white mb-4">Python</h3>
                  <div className="bg-black/30 rounded-lg p-4">
                    <pre className="text-sm text-blue-400 overflow-x-auto">
{`import requests

response = requests.post(
    'https://api.auraai.com/api/v1/neural-stealth/bypass',
    headers={
        'Authorization': 'Bearer aura_live_sk_1234567890abcdef',
        'Content-Type': 'application/json'
    },
    json={
        'target_url': 'https://example.com',
        'protection_type': 'cloudflare',
        'stealth_level': 'maximum'
    }
)

data = response.json()
print(data)`}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {activeTab === 'errors' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-8">
              <h2 className="text-3xl font-bold text-white mb-6">Error Codes</h2>
              
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-400 mb-2">400 - Bad Request</h3>
                    <p className="text-gray-300 text-sm">Invalid request parameters or malformed JSON</p>
                  </div>
                  
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-400 mb-2">401 - Unauthorized</h3>
                    <p className="text-gray-300 text-sm">Invalid or missing API key</p>
                  </div>
                  
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-400 mb-2">429 - Rate Limited</h3>
                    <p className="text-gray-300 text-sm">Too many requests, please slow down</p>
                  </div>
                  
                  <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
                    <h3 className="text-lg font-semibold text-red-400 mb-2">500 - Server Error</h3>
                    <p className="text-gray-300 text-sm">Internal server error, please try again</p>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
} 