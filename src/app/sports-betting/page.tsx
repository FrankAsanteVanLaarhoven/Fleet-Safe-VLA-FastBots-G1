'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { GlowCard } from '@/components/ui/glow-card';

interface LiveMatch {
  match_id: string;
  sport: string;
  home_team: string;
  away_team: string;
  kickoff_time: string;
  venue: string;
  competition: string;
  status: string;
  live_odds: Record<string, Record<string, number>>;
  team_news: Record<string, string[]>;
  weather?: string;
  pitch_condition?: string;
}

interface BettingAnalysis {
  match_id: string;
  sport: string;
  recommendation_type: string;
  confidence_level: number;
  stake_recommendation: string;
  odds_analysis: Record<string, number>;
  expected_value: number;
  risk_level: string;
  reasoning: string[];
  alternative_bets: any[];
  combination_options: any[];
}

interface SportTemplate {
  name: string;
  description: string;
  options: string[];
  quick_picks: string[];
}

export default function SportsBettingPage() {
  const [selectedSport, setSelectedSport] = useState('football');
  const [liveMatches, setLiveMatches] = useState<LiveMatch[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<LiveMatch | null>(null);
  const [bettingAnalysis, setBettingAnalysis] = useState<BettingAnalysis | null>(null);
  const [sportTemplates, setSportTemplates] = useState<Record<string, SportTemplate>>({});
  const [bettingProviders, setBettingProviders] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [customQuery, setCustomQuery] = useState('');

  const sports = [
    { id: 'football', name: '⚽ Football', icon: '⚽' },
    { id: 'basketball', name: '🏀 Basketball', icon: '🏀' },
    { id: 'tennis', name: '🎾 Tennis', icon: '🎾' },
    { id: 'cricket', name: '🏏 Cricket', icon: '🏏' },
    { id: 'rugby', name: '🏉 Rugby', icon: '🏉' },
    { id: 'boxing', name: '🥊 Boxing', icon: '🥊' },
    { id: 'ufc', name: '🥋 UFC', icon: '🥋' },
    { id: 'horse_racing', name: '🐎 Horse Racing', icon: '🐎' },
    { id: 'golf', name: '⛳ Golf', icon: '⛳' },
    { id: 'baseball', name: '⚾ Baseball', icon: '⚾' },
    { id: 'ice_hockey', name: '🏒 Ice Hockey', icon: '🏒' },
    { id: 'american_football', name: '🏈 American Football', icon: '🏈' }
  ];

  useEffect(() => {
    loadSportTemplates();
    loadBettingProviders();
  }, []);

  useEffect(() => {
    if (selectedSport) {
      loadLiveMatches(selectedSport);
    }
  }, [selectedSport]);

  const loadSportTemplates = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/live-sports/sport-templates');
      const data = await response.json();
      setSportTemplates(data.templates);
    } catch (error) {
      console.error('Error loading sport templates:', error);
      // Mock data when API is not available
      setSportTemplates({
        football: {
          name: 'Football',
          description: 'Professional football betting templates',
          options: ['Match Winner', 'Over/Under Goals', 'Both Teams to Score', 'Correct Score', 'First Goalscorer'],
          quick_picks: ['Home Win', 'Over 2.5 Goals', 'BTTS Yes', '1-0 or 2-1']
        },
        basketball: {
          name: 'Basketball',
          description: 'Professional basketball betting templates',
          options: ['Match Winner', 'Over/Under Points', 'Handicap', 'Player Props', 'Quarter Winner'],
          quick_picks: ['Home Win', 'Over 200 Points', '-5.5 Handicap', 'High Scoring']
        },
        tennis: {
          name: 'Tennis',
          description: 'Professional tennis betting templates',
          options: ['Match Winner', 'Set Winner', 'Games Over/Under', 'Aces', 'Double Faults'],
          quick_picks: ['Favourite Win', 'Over 20.5 Games', 'Straight Sets', 'High Aces']
        }
      });
    }
  };

  const loadBettingProviders = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/live-sports/betting-providers');
      const data = await response.json();
      setBettingProviders(data.providers);
    } catch (error) {
      console.error('Error loading betting providers:', error);
      // Mock data when API is not available
      setBettingProviders([
        { name: 'Bet365', odds: { home: 2.10, draw: 3.40, away: 3.20 } },
        { name: 'William Hill', odds: { home: 2.05, draw: 3.50, away: 3.15 } },
        { name: 'Ladbrokes', odds: { home: 2.15, draw: 3.30, away: 3.25 } }
      ]);
    }
  };

  const loadLiveMatches = async (sport: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/live-sports/live-matches/${sport}`);
      const data = await response.json();
      setLiveMatches(data.matches);
    } catch (error) {
      console.error('Error loading live matches:', error);
      // Mock data when API is not available
      if (sport === 'football') {
        setLiveMatches([
          {
            match_id: 'football-1',
            sport: 'football',
            home_team: 'Manchester United',
            away_team: 'Liverpool',
            kickoff_time: new Date(Date.now() + 3600000).toISOString(),
            venue: 'Old Trafford',
            competition: 'Premier League',
            status: 'live',
            live_odds: {
              'Bet365': { home: 2.10, draw: 3.40, away: 3.20 },
              'William Hill': { home: 2.05, draw: 3.50, away: 3.15 }
            },
            team_news: {
              'Manchester United': ['Rashford fit to play', 'Bruno Fernandes available'],
              'Liverpool': ['Salah doubtful', 'Van Dijk returns']
            }
          },
          {
            match_id: 'football-2',
            sport: 'football',
            home_team: 'Arsenal',
            away_team: 'Chelsea',
            kickoff_time: new Date(Date.now() + 7200000).toISOString(),
            venue: 'Emirates Stadium',
            competition: 'Premier League',
            status: 'upcoming',
            live_odds: {
              'Bet365': { home: 1.85, draw: 3.60, away: 4.20 },
              'William Hill': { home: 1.80, draw: 3.70, away: 4.15 }
            },
            team_news: {
              'Arsenal': ['Odegaard in form', 'Saka available'],
              'Chelsea': ['Pulisic injured', 'Mount returns']
            }
          }
        ]);
      } else if (sport === 'basketball') {
        setLiveMatches([
          {
            match_id: 'basketball-1',
            sport: 'basketball',
            home_team: 'Lakers',
            away_team: 'Warriors',
            kickoff_time: new Date(Date.now() + 1800000).toISOString(),
            venue: 'Crypto.com Arena',
            competition: 'NBA',
            status: 'live',
            live_odds: {
              'Bet365': { home: 1.90, away: 1.90 },
              'William Hill': { home: 1.85, away: 1.95 }
            },
            team_news: {
              'Lakers': ['LeBron James playing', 'AD available'],
              'Warriors': ['Curry in form', 'Green suspended']
            }
          }
        ]);
      } else {
        setLiveMatches([]);
      }
    } finally {
      setLoading(false);
    }
  };

  const getBettingAnalysis = async (matchId: string) => {
    setLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/api/live-sports/betting-analysis/${matchId}`);
      const data = await response.json();
      setBettingAnalysis(data.betting_analysis);
      setSelectedMatch(data.match);
    } catch (error) {
      console.error('Error getting betting analysis:', error);
    } finally {
      setLoading(false);
    }
  };

  const submitCustomQuery = async () => {
    if (!customQuery.trim()) return;
    
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
      // Handle the response as needed
    } catch (error) {
      console.error('Error submitting custom query:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatKickoffTime = (timeString: string) => {
    const date = new Date(timeString);
    return date.toLocaleString('en-GB', {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getBestOdds = (odds: Record<string, Record<string, number>>) => {
    const bestOdds: Record<string, number> = {};
    const betTypes = ['home', 'draw', 'away'];
    
    betTypes.forEach(type => {
      const typeOdds = Object.values(odds).map(provider => provider[type]).filter(Boolean);
      if (typeOdds.length > 0) {
        bestOdds[type] = Math.max(...typeOdds);
      }
    });
    
    return bestOdds;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-32">
        <div className="text-center mb-8">
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6">
            🎯 Live Sports Intelligence
            <span className="bg-gradient-to-r from-green-400 to-blue-400 bg-clip-text text-transparent">
              {" "}Hub
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Professional-grade live sports betting intelligence with real-time data, institutional analysis, and multi-provider odds comparison.
          </p>
        </div>

        {/* Sport Selection */}
        <GlowCard className="p-8 mb-8" customSize glowColor="green">
          <h2 className="text-3xl font-bold text-white mb-6">🏆 Select Sport</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {sports.map((sport) => (
              <GlowCard
                key={sport.id}
                className={`p-4 transition-all duration-300 cursor-pointer ${
                  selectedSport === sport.id
                    ? 'border-2 border-green-500/50 text-green-400'
                    : 'text-white hover:bg-white/10'
                }`}
                customSize
                glowColor={selectedSport === sport.id ? 'green' : 'blue'}
                onClick={() => setSelectedSport(sport.id)}
              >
                <div className="text-3xl mb-2">{sport.icon}</div>
                <div className="text-sm font-semibold">{sport.name.split(' ')[1]}</div>
              </GlowCard>
            ))}
          </div>
        </GlowCard>

        {/* Sport Templates */}
        {sportTemplates[selectedSport] && (
          <GlowCard className="p-8 mb-8" customSize glowColor="blue">
            <h2 className="text-3xl font-bold text-white mb-6">📋 {sportTemplates[selectedSport].name} Templates</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-xl font-semibold text-green-400 mb-4">🎯 Betting Options</h3>
                <div className="space-y-2">
                  {sportTemplates[selectedSport].options.map((option, index) => (
                    <div key={index} className="glass-section p-3 text-white">
                      {option}
                    </div>
                  ))}
                </div>
              </div>
              <div>
                <h3 className="text-xl font-semibold text-blue-400 mb-4">⚡ Quick Picks</h3>
                <div className="space-y-2">
                  {sportTemplates[selectedSport].quick_picks.map((pick, index) => (
                    <div key={index} className="glass-section p-3 text-white">
                      {pick}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </GlowCard>
        )}

        {/* Custom Query */}
        <GlowCard className="p-8 mb-8" customSize glowColor="purple">
          <h2 className="text-3xl font-bold text-white mb-6">🔍 Custom Analysis Request</h2>
          <div className="flex gap-4">
            <input
              type="text"
              value={customQuery}
              onChange={(e) => setCustomQuery(e.target.value)}
              placeholder="Enter your custom betting analysis request..."
              className="flex-1 glass-input rounded-lg px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-green-500"
            />
            <button
              onClick={submitCustomQuery}
              disabled={loading || !customQuery.trim()}
              className="glass-button text-white font-semibold px-6 py-3 rounded-lg disabled:opacity-50"
            >
              {loading ? 'Analyzing...' : 'Analyze'}
            </button>
          </div>
        </GlowCard>

        {/* Live Matches */}
        <GlowCard className="p-8 mb-8" customSize glowColor="orange">
          <h2 className="text-3xl font-bold text-white mb-6">📺 Live Matches - {selectedSport.toUpperCase()}</h2>
          
          {loading ? (
            <div className="text-center text-white">Loading matches...</div>
          ) : liveMatches.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {liveMatches.map((match) => (
                <div key={match.match_id} className="bg-white/5 border border-white/10 rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-sm text-green-400 font-semibold">LIVE</span>
                    <span className="text-xs text-gray-400">{match.venue}</span>
                  </div>
                  
                  <div className="text-center mb-4">
                    <div className="text-lg font-bold text-white">{match.home_team}</div>
                    <div className="text-2xl font-bold text-blue-400">vs</div>
                    <div className="text-lg font-bold text-white">{match.away_team}</div>
                  </div>
                  
                  <div className="text-center text-sm text-gray-400 mb-4">
                    {formatKickoffTime(match.kickoff_time)}
                  </div>
                  
                  <div className="text-center">
                    <button
                      onClick={() => getBettingAnalysis(match.match_id)}
                      className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
                    >
                      Get Analysis
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center text-white">No live matches available</div>
          )}
        </GlowCard>

        {/* Betting Analysis */}
        {bettingAnalysis && selectedMatch && (
          <GlowCard className="p-8 mb-8" customSize glowColor="red">
            <h2 className="text-3xl font-bold text-white mb-6">💡 Betting Analysis</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Match Info */}
              <div className="bg-white/5 rounded-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4">🏟️ Match Information</h3>
                <div className="space-y-3">
                  <div className="text-white">
                    <strong>Home:</strong> {selectedMatch.home_team}
                  </div>
                  <div className="text-white">
                    <strong>Away:</strong> {selectedMatch.away_team}
                  </div>
                  <div className="text-gray-300">
                    <strong>Venue:</strong> {selectedMatch.venue}
                  </div>
                  <div className="text-gray-300">
                    <strong>Competition:</strong> {selectedMatch.competition}
                  </div>
                </div>
              </div>

              {/* Betting Recommendation */}
              <div className="bg-white/5 rounded-lg p-6">
                <h3 className="text-xl font-bold text-white mb-4">💡 Betting Recommendation</h3>
                <div className="space-y-3">
                  <div className="text-green-400">
                    <strong>Recommendation:</strong> {bettingAnalysis.recommendation_type.toUpperCase()}
                  </div>
                  <div className="text-blue-400">
                    <strong>Confidence:</strong> {(bettingAnalysis.confidence_level * 100).toFixed(1)}%
                  </div>
                  <div className="text-yellow-400">
                    <strong>Expected Value:</strong> {(bettingAnalysis.expected_value * 100).toFixed(2)}%
                  </div>
                  <div className="text-purple-400">
                    <strong>Risk Level:</strong> {bettingAnalysis.risk_level}
                  </div>
                  <div className="text-white">
                    <strong>Stake:</strong> {bettingAnalysis.stake_recommendation}
                  </div>
                </div>
              </div>
            </div>

            {/* Reasoning */}
            <div className="mt-6 bg-white/5 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">🧠 Analysis Reasoning</h3>
              <div className="space-y-2">
                {bettingAnalysis.reasoning.map((reason, index) => (
                  <div key={index} className="text-gray-300">• {reason}</div>
                ))}
              </div>
            </div>

            {/* Alternative Bets */}
            <div className="mt-6 bg-white/5 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">🎲 Alternative Betting Options</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {bettingAnalysis.alternative_bets.map((bet, index) => (
                  <div key={index} className="bg-white/5 rounded-lg p-4">
                    <div className="text-green-400 font-semibold">{bet.type}</div>
                    <div className="text-white">{bet.recommendation}</div>
                    <div className="text-blue-400">Confidence: {(bet.confidence * 100).toFixed(1)}%</div>
                    <div className="text-yellow-400">Odds: {bet.odds}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Combination Options */}
            <div className="mt-6 bg-white/5 rounded-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">🎯 Combination Betting</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {bettingAnalysis.combination_options.map((combo, index) => (
                  <div key={index} className="bg-white/5 rounded-lg p-4">
                    <div className="text-green-400 font-semibold">{combo.type}</div>
                    <div className="text-white">{combo.description}</div>
                    <div className="text-blue-400">Odds: {combo.odds}</div>
                    <div className="text-yellow-400">Confidence: {(combo.confidence * 100).toFixed(1)}%</div>
                    <div className="text-purple-400">Stake: {combo.stake_recommendation}</div>
                  </div>
                ))}
              </div>
            </div>
          </GlowCard>
        )}

        {/* Betting Providers */}
        <div className="bg-white/5 border border-white/10 rounded-2xl p-8 mb-8">
          <h2 className="text-3xl font-bold text-white mb-6">🏪 Betting Providers</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {bettingProviders.map((provider, index) => (
              <div key={index} className="bg-white/5 border border-white/10 rounded-lg p-6">
                <h3 className="text-xl font-bold text-white mb-2">{provider.name}</h3>
                <div className="text-sm text-gray-400 mb-4">{provider.type}</div>
                
                <div className="mb-4">
                  <h4 className="text-green-400 font-semibold mb-2">Current Offers:</h4>
                  <div className="space-y-1">
                    {provider.current_offers.map((offer: string, offerIndex: number) => (
                      <div key={offerIndex} className="text-sm text-gray-300">• {offer}</div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-blue-400 font-semibold mb-2">Best Features:</h4>
                  <div className="space-y-1">
                    {provider.best_features.map((feature: string, featureIndex: number) => (
                      <div key={featureIndex} className="text-sm text-gray-300">• {feature}</div>
                    ))}
                  </div>
                </div>
              </div>
            ))}
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