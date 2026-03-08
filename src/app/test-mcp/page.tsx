'use client';

import { useState, useEffect } from 'react';

export default function TestMCPPage() {
  const [healthStatus, setHealthStatus] = useState<any>(null);
  const [agentsStatus, setAgentsStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const testMCPConnection = async () => {
      try {
        setLoading(true);
        setError(null);

        // Test health endpoint
        const healthResponse = await fetch('http://localhost:8000/health');
        const healthData = await healthResponse.json();
        setHealthStatus(healthData);

        // Test agents endpoint
        const agentsResponse = await fetch('http://localhost:8000/api/mcp/agents');
        const agentsData = await agentsResponse.json();
        setAgentsStatus(agentsData);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    testMCPConnection();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg text-white">Testing MCP Connection...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold text-white mb-8 text-center">
          MCP Integration Test
        </h1>

        {error && (
          <div className="bg-red-900 border border-red-500 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold text-red-200 mb-2">Connection Error</h2>
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {healthStatus && (
          <div className="bg-slate-800 rounded-lg p-6 mb-8 border border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">Health Status</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-gray-400 text-sm">Status</p>
                <p className="text-white font-semibold">{healthStatus.status}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Version</p>
                <p className="text-white font-semibold">{healthStatus.version}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Security Level</p>
                <p className="text-white font-semibold">{healthStatus.security_level}</p>
              </div>
              <div>
                <p className="text-gray-400 text-sm">Active Agents</p>
                <p className="text-white font-semibold">{healthStatus.active_agents}</p>
              </div>
            </div>
          </div>
        )}

        {agentsStatus && (
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h2 className="text-xl font-semibold text-white mb-4">
              Agents Status ({agentsStatus.agents?.length || 0} agents)
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {agentsStatus.agents?.slice(0, 9).map((agent: any, index: number) => (
                <div key={index} className="bg-slate-700 rounded-lg p-4 border border-slate-600">
                  <h3 className="text-white font-semibold mb-2">
                    {agent.name.replace(/_/g, ' ').toUpperCase()}
                  </h3>
                  <p className="text-gray-300 text-sm mb-2">{agent.description}</p>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Security:</span>
                    <span className="text-white">{agent.security_level}</span>
                  </div>
                  <div className="flex justify-between text-xs">
                    <span className="text-gray-400">Status:</span>
                    <span className="text-green-400">{agent.status}</span>
                  </div>
                </div>
              ))}
            </div>
            {agentsStatus.agents?.length > 9 && (
              <p className="text-gray-400 text-center mt-4">
                ... and {agentsStatus.agents.length - 9} more agents
              </p>
            )}
          </div>
        )}

        <div className="mt-8 text-center">
          <a
            href="/"
            className="inline-block bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Main Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}


