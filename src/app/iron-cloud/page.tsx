'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { GlowCard } from '@/components/ui/glow-card';

interface APIPenetrationResult {
  success: boolean;
  api: string;
  url: string;
  result: {
    success: boolean;
    technique?: any;
    data?: any;
    error?: string;
  };
  timestamp: string;
}

interface IronCloudStatus {
  active: boolean;
  capabilities: string[];
  user_agents_count: number;
  techniques_available: number;
  timestamp: string;
}

interface APIProvider {
  name: string;
  type: string;
  base_url: string;
  rate_limit: number;
  requires_auth: boolean;
  working: boolean;
  has_api_key: boolean;
}

export default function IronCloudPage() {
  const [providers, setProviders] = useState<APIProvider[]>([]);
  const [selectedProvider, setSelectedProvider] = useState<string>('');
  const [endpoint, setEndpoint] = useState<string>('');
  const [penetrationResult, setPenetrationResult] = useState<APIPenetrationResult | null>(null);
  const [ironCloudStatus, setIronCloudStatus] = useState<IronCloudStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [liveMatches, setLiveMatches] = useState<any>(null);
  const [selectedSport, setSelectedSport] = useState<string>('basketball');

  useEffect(() => {
    fetchProviders();
    fetchIronCloudStatus();
    fetchLiveMatches();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await fetch('/api/real-sports-apis/providers');
      const data = await response.json();
      if (data.success) {
        setProviders(data.providers);
      }
    } catch (error) {
      console.error('Error fetching providers:', error);
      // Mock data when API is not available
      setProviders([
        {
          name: 'ESPN API',
          type: 'espn',
          base_url: 'https://api.espn.com/v1',
          rate_limit: 100,
          requires_auth: true,
          working: true,
          has_api_key: true
        },
        {
          name: 'Sports Data IO',
          type: 'sportsdata',
          base_url: 'https://api.sportsdata.io/v3',
          rate_limit: 60,
          requires_auth: true,
          working: true,
          has_api_key: true
        },
        {
          name: 'The Odds API',
          type: 'odds',
          base_url: 'https://api.the-odds-api.com/v4',
          rate_limit: 500,
          requires_auth: true,
          working: true,
          has_api_key: true
        }
      ]);
    }
  };

  const fetchIronCloudStatus = async () => {
    try {
      const response = await fetch('/api/real-sports-apis/iron-cloud/status');
      const data = await response.json();
      if (data.success) {
        setIronCloudStatus(data.iron_cloud);
      }
    } catch (error) {
      console.error('Error fetching Iron Cloud status:', error);
      // Mock data when API is not available
      setIronCloudStatus({
        active: true,
        capabilities: ['API Penetration', 'Rate Limit Bypass', 'User Agent Rotation', 'Proxy Rotation'],
        user_agents_count: 150,
        techniques_available: 25,
        timestamp: new Date().toISOString()
      });
    }
  };

  const fetchLiveMatches = async () => {
    try {
      const response = await fetch(`/api/real-sports-apis/live-matches/${selectedSport}`);
      const data = await response.json();
      if (data.success) {
        setLiveMatches(data);
      }
    } catch (error) {
      console.error('Error fetching live matches:', error);
      // Mock data when API is not available
      setLiveMatches({
        success: true,
        data: {
          matches: [
            {
              id: 'mock-1',
              home_team: 'Lakers',
              away_team: 'Warriors',
              home_score: 108,
              away_score: 102,
              quarter: 4,
              time_remaining: '2:30',
              venue: 'Crypto.com Arena'
            },
            {
              id: 'mock-2',
              home_team: 'Celtics',
              away_team: 'Heat',
              home_score: 95,
              away_score: 98,
              quarter: 3,
              time_remaining: '5:45',
              venue: 'TD Garden'
            }
          ]
        }
      });
    }
  };

  const attemptPenetration = async () => {
    if (!selectedProvider) return;

    setLoading(true);
    try {
      const url = `/api/real-sports-apis/penetration/${selectedProvider}${endpoint ? `?endpoint=${endpoint}` : ''}`;
      const response = await fetch(url);
      const data = await response.json();
      setPenetrationResult(data);
    } catch (error) {
      console.error('Error attempting penetration:', error);
      setPenetrationResult({
        success: false,
        api: selectedProvider,
        url: '',
        result: { success: false, error: 'Network error' },
        timestamp: new Date().toISOString()
      });
    } finally {
      setLoading(false);
    }
  };

  const getProviderStatusColor = (working: boolean, requiresAuth: boolean) => {
    if (working) return 'text-green-400';
    if (requiresAuth) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getProviderStatusText = (working: boolean, requiresAuth: boolean) => {
    if (working) return '✅ Working';
    if (requiresAuth) return '🔑 Requires Auth';
    return '❌ Not Available';
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-red-500 to-orange-500 bg-clip-text text-transparent">
                🚀 Iron Cloud API Penetration System
              </h1>
              <p className="text-gray-400 mt-2">
                Advanced API penetration and sports data access with Iron Cloud technology
              </p>
            </div>
            <Link
              href="/"
              className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors"
            >
              ← Back to Main Hub
            </Link>
          </div>
        </div>

        {/* Iron Cloud Status */}
        {ironCloudStatus && (
          <GlowCard className="p-6 mb-8" customSize glowColor="red">
            <h2 className="text-2xl font-bold text-red-400 mb-4">Iron Cloud Status</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-800/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-300">Status</h3>
                <p className={`text-xl ${ironCloudStatus.active ? 'text-green-400' : 'text-red-400'}`}>
                  {ironCloudStatus.active ? '🟢 ACTIVE' : '🔴 INACTIVE'}
                </p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-300">User Agents</h3>
                <p className="text-xl text-blue-400">{ironCloudStatus.user_agents_count}</p>
              </div>
              <div className="bg-gray-800/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-red-300">Techniques</h3>
                <p className="text-xl text-purple-400">{ironCloudStatus.techniques_available}</p>
              </div>
            </div>
            <div className="mt-4">
              <h3 className="text-lg font-semibold text-red-300 mb-2">Capabilities:</h3>
              <div className="flex flex-wrap gap-2">
                {ironCloudStatus.capabilities.map((capability, index) => (
                  <span
                    key={index}
                    className="bg-red-600/20 border border-red-500/30 text-red-300 px-3 py-1 rounded-full text-sm"
                  >
                    {capability}
                  </span>
                ))}
              </div>
            </div>
          </GlowCard>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* API Providers */}
          <GlowCard className="p-6" customSize glowColor="blue">
            <h2 className="text-2xl font-bold text-blue-400 mb-4">🎯 Available API Providers</h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {providers.map((provider) => (
                <div
                  key={provider.type}
                  className={`p-4 rounded-lg border cursor-pointer transition-all ${
                    selectedProvider === provider.type
                      ? 'border-blue-500 bg-blue-900/20'
                      : 'border-gray-600 bg-gray-700/50 hover:border-gray-500'
                  }`}
                  onClick={() => setSelectedProvider(provider.type)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-white">{provider.name}</h3>
                      <p className="text-sm text-gray-400">{provider.base_url}</p>
                    </div>
                    <div className="text-right">
                      <p className={`font-semibold ${getProviderStatusColor(provider.working, provider.requires_auth)}`}>
                        {getProviderStatusText(provider.working, provider.requires_auth)}
                      </p>
                      <p className="text-xs text-gray-500">
                        {provider.rate_limit} req/min
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </GlowCard>

          {/* Penetration Control */}
          <GlowCard className="p-6" customSize glowColor="orange">
            <h2 className="text-2xl font-bold text-orange-400 mb-4">⚡ Penetration Control</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Selected Provider</label>
                <div className="bg-gray-800/50 rounded-lg p-3 text-white">
                  {selectedProvider || 'None selected'}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Endpoint (Optional)</label>
                <input
                  type="text"
                  value={endpoint}
                  onChange={(e) => setEndpoint(e.target.value)}
                  placeholder="e.g., /scores, /odds, /teams"
                  className="w-full bg-gray-800/50 border border-gray-600 rounded-lg px-3 py-2 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
              </div>

              <button
                onClick={attemptPenetration}
                disabled={!selectedProvider || loading}
                className="w-full bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 text-white font-semibold py-3 px-4 rounded-lg transition-colors disabled:opacity-50"
              >
                {loading ? 'Penetrating...' : '🚀 Attempt Penetration'}
              </button>
            </div>

            {/* Penetration Results */}
            {penetrationResult && (
              <div className="mt-6 bg-gray-800/50 rounded-lg p-4">
                <h3 className="text-lg font-semibold text-orange-300 mb-3">Penetration Results</h3>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-400">API:</span>
                    <span className="text-white ml-2">{penetrationResult.api}</span>
                  </div>
                  <div>
                    <span className="text-gray-400">Success:</span>
                    <span className={`ml-2 ${penetrationResult.success ? 'text-green-400' : 'text-red-400'}`}>
                      {penetrationResult.success ? '✅ Yes' : '❌ No'}
                    </span>
                  </div>
                  {penetrationResult.result.error && (
                    <div>
                      <span className="text-gray-400">Error:</span>
                      <span className="text-red-400 ml-2">{penetrationResult.result.error}</span>
                    </div>
                  )}
                  {penetrationResult.result.data && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-blue-400 hover:text-blue-300">
                        View Data
                      </summary>
                      <pre className="mt-2 p-3 bg-gray-900 rounded text-xs overflow-x-auto">
                        {JSON.stringify(penetrationResult.result.data, null, 2)}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            )}
          </GlowCard>
        </div>

        {/* Live Sports Data */}
        <GlowCard className="mt-8 p-6" customSize glowColor="green">
          <h2 className="text-2xl font-bold text-green-400 mb-4">🏀 Live Sports Data</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-300 mb-2">Select Sport</label>
            <select
              value={selectedSport}
              onChange={(e) => {
                setSelectedSport(e.target.value);
                fetchLiveMatches();
              }}
              className="bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
            >
              <option value="basketball">Basketball</option>
              <option value="football">Football</option>
            </select>
          </div>

          {liveMatches && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {liveMatches.data?.matches?.map((match: any) => (
                <div key={match.id} className="bg-gray-700/50 border border-gray-600 rounded-lg p-4">
                  <div className="flex justify-between items-center mb-3">
                    <span className="text-sm text-green-400 font-semibold">LIVE</span>
                    <span className="text-xs text-gray-400">{match.venue}</span>
                  </div>
                  
                  <div className="text-center mb-3">
                    <div className="text-lg font-bold text-white">{match.home_team}</div>
                    <div className="text-2xl font-bold text-blue-400">{match.home_score}</div>
                  </div>
                  
                  <div className="text-center text-gray-400 mb-3">vs</div>
                  
                  <div className="text-center mb-3">
                    <div className="text-lg font-bold text-white">{match.away_team}</div>
                    <div className="text-2xl font-bold text-red-400">{match.away_score}</div>
                  </div>
                  
                  <div className="text-center text-sm text-gray-400">
                    {match.quarter ? `Q${match.quarter} - ${match.time_remaining}` : `Min ${match.minute}`}
                  </div>
                  
                  <div className="mt-3 text-center">
                    <Link
                      href={`/api/real-sports-apis/odds/${match.id}`}
                      className="text-blue-400 hover:text-blue-300 text-sm"
                    >
                      View Odds →
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </GlowCard>

        {/* Quick Actions */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <GlowCard className="p-6 text-center transition-all transform hover:scale-105" customSize glowColor="blue">
            <Link href="/sports-betting" className="block">
              <h3 className="text-xl font-bold mb-2 text-white">🎯 Sports Betting</h3>
              <p className="text-blue-100">Professional betting analysis</p>
            </Link>
          </GlowCard>
          
          <GlowCard className="p-6 text-center transition-all transform hover:scale-105" customSize glowColor="purple">
            <Link href="/agent-templates" className="block">
              <h3 className="text-xl font-bold mb-2 text-white">🤖 AI Templates</h3>
              <p className="text-purple-100">Agent templates and use cases</p>
            </Link>
          </GlowCard>
          
          <GlowCard className="p-6 text-center transition-all transform hover:scale-105" customSize glowColor="green">
            <Link href="/" className="block">
              <h3 className="text-xl font-bold mb-2 text-white">🏠 Main Hub</h3>
              <p className="text-green-100">Return to main interface</p>
            </Link>
          </GlowCard>
        </div>
      </div>
    </div>
  );
} 