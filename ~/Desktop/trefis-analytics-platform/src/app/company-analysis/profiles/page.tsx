'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { trefisApi, CompanyProfile } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, Filter, Star, TrendingUp, TrendingDown } from 'lucide-react';

export default function CompanyProfilesPage() {
  const [companies, setCompanies] = useState<CompanyProfile[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [sortBy, setSortBy] = useState('name');

  const sectors = [
    'Technology',
    'Healthcare',
    'Financial Services',
    'Consumer Discretionary',
    'Energy',
    'Industrials',
    'Materials',
    'Real Estate',
    'Utilities',
    'Communication Services'
  ];

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        setLoading(true);
        // For demo purposes, we'll use mock data since we don't have a real API
        const mockCompanies: CompanyProfile[] = [
          {
            company_id: 'MSFT',
            name: 'Microsoft Corporation',
            sector: 'Technology',
            industry: 'Software & Cloud Services',
            market_cap: 3120000000000,
            current_price: 412.50,
            trefis_score: 92,
            description: 'Microsoft is a global technology leader that develops, manufactures, licenses, supports, and sells computer software, consumer electronics, personal computers, and related services.',
            business_segments: {
              productivity_and_business_processes: { revenue: 69000000000, growth_yoy: 12.5 },
              intelligent_cloud: { revenue: 89000000000, growth_yoy: 23.8 },
              more_personal_computing: { revenue: 54000000000, growth_yoy: -2.1 }
            },
            financial_metrics: {
              revenue_2024: 212000000000,
              net_income_2024: 72300000000,
              operating_margin: 34.1,
              return_on_equity: 38.7
            },
            growth_drivers: ['Azure cloud services expansion', 'AI integration', 'Enterprise software adoption'],
            risk_factors: ['Intense competition in cloud services', 'Regulatory scrutiny', 'Cybersecurity threats'],
            analyst_consensus: {
              buy_ratings: 42,
              hold_ratings: 3,
              sell_ratings: 0,
              average_target: 485.00,
              upside_potential: 17.7
            }
          },
          {
            company_id: 'AAPL',
            name: 'Apple Inc.',
            sector: 'Technology',
            industry: 'Consumer Electronics',
            market_cap: 2850000000000,
            current_price: 185.00,
            trefis_score: 88,
            description: 'Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.',
            business_segments: {
              iphone: { revenue: 200000000000, growth_yoy: 8.2 },
              mac: { revenue: 35000000000, growth_yoy: 5.1 },
              ipad: { revenue: 28000000000, growth_yoy: -3.2 },
              wearables: { revenue: 42000000000, growth_yoy: 15.7 }
            },
            financial_metrics: {
              revenue_2024: 385000000000,
              net_income_2024: 97000000000,
              operating_margin: 25.2,
              return_on_equity: 147.8
            },
            growth_drivers: ['Services revenue growth', 'iPhone market share', 'Wearables expansion'],
            risk_factors: ['Supply chain disruptions', 'Regulatory challenges', 'Market saturation'],
            analyst_consensus: {
              buy_ratings: 38,
              hold_ratings: 8,
              sell_ratings: 1,
              average_target: 210.00,
              upside_potential: 13.5
            }
          },
          {
            company_id: 'GOOGL',
            name: 'Alphabet Inc.',
            sector: 'Technology',
            industry: 'Internet Services',
            market_cap: 1850000000000,
            current_price: 142.00,
            trefis_score: 85,
            description: 'Alphabet Inc. provides online advertising services in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America.',
            business_segments: {
              google_services: { revenue: 280000000000, growth_yoy: 18.5 },
              google_cloud: { revenue: 29000000000, growth_yoy: 25.1 },
              other_bets: { revenue: 1000000000, growth_yoy: 45.2 }
            },
            financial_metrics: {
              revenue_2024: 310000000000,
              net_income_2024: 74000000000,
              operating_margin: 23.9,
              return_on_equity: 25.3
            },
            growth_drivers: ['Cloud services growth', 'AI leadership', 'Advertising recovery'],
            risk_factors: ['Privacy regulations', 'Competition from social media', 'Economic downturn'],
            analyst_consensus: {
              buy_ratings: 35,
              hold_ratings: 5,
              sell_ratings: 0,
              average_target: 165.00,
              upside_potential: 16.2
            }
          }
        ];

        setCompanies(mockCompanies);
      } catch (error) {
        console.error('Error fetching companies:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  const filteredCompanies = companies.filter(company => {
    const matchesSearch = company.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         company.company_id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSector = !selectedSector || company.sector === selectedSector;
    return matchesSearch && matchesSector;
  });

  const sortedCompanies = [...filteredCompanies].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'market_cap':
        return b.market_cap - a.market_cap;
      case 'trefis_score':
        return b.trefis_score - a.trefis_score;
      case 'price':
        return b.current_price - a.current_price;
      default:
        return 0;
    }
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      notation: 'compact',
      maximumFractionDigits: 1
    }).format(value);
  };

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Company Profiles</h1>
            <p className="text-gray-600">Comprehensive company information and analysis</p>
          </div>

          {/* Search and Filters */}
          <div className="mb-6 space-y-4">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search companies..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <select
                value={selectedSector}
                onChange={(e) => setSelectedSector(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Sectors</option>
                {sectors.map(sector => (
                  <option key={sector} value={sector}>{sector}</option>
                ))}
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="name">Sort by Name</option>
                <option value="market_cap">Sort by Market Cap</option>
                <option value="trefis_score">Sort by Trefis Score</option>
                <option value="price">Sort by Price</option>
              </select>
            </div>
          </div>

          {/* Company Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {sortedCompanies.map((company) => (
              <Card key={company.company_id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-900">{company.name}</h3>
                    <p className="text-gray-600">{company.company_id} • {company.sector}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Star className="w-5 h-5 text-yellow-400 fill-current" />
                    <span className="text-lg font-bold text-gray-900">{company.trefis_score}</span>
                  </div>
                </div>

                <p className="text-gray-700 mb-4 line-clamp-2">{company.description}</p>

                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-sm text-gray-600">Market Cap</p>
                    <p className="font-semibold text-gray-900">{formatCurrency(company.market_cap)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Current Price</p>
                    <p className="font-semibold text-gray-900">${company.current_price?.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Revenue (2024)</p>
                    <p className="font-semibold text-gray-900">{formatCurrency(company.financial_metrics?.revenue_2024 || 0)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Operating Margin</p>
                    <p className="font-semibold text-gray-900">{company.financial_metrics?.operating_margin?.toFixed(1)}%</p>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-sm text-gray-600 mb-2">Growth Drivers</p>
                  <div className="flex flex-wrap gap-1">
                    {company.growth_drivers?.slice(0, 2).map((driver, index) => (
                      <span key={index} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        {driver}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-sm text-gray-600">Analyst Consensus</p>
                    <p className="font-semibold text-gray-900">
                      {company.analyst_consensus?.buy_ratings || 0} Buy • {company.analyst_consensus?.hold_ratings || 0} Hold
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Target Price</p>
                    <p className="font-semibold text-gray-900">${company.analyst_consensus?.average_target?.toFixed(2)}</p>
                    <p className="text-sm text-green-600">
                      {formatPercent(company.analyst_consensus?.upside_potential || 0)}
                    </p>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
                    View Details
                  </Button>
                  <Button variant="outline" className="flex-1">
                    Add to Watchlist
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {sortedCompanies.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No companies found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 