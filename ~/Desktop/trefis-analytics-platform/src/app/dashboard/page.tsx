'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { trefisApi } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrefisChart } from '@/components/charts/TrefisChart';
import { TrendingUp, TrendingDown, DollarSign, Users, BarChart3, Globe, Building2, FileText } from 'lucide-react';

interface DashboardData {
  platform_stats: {
    total_companies: number;
    active_analysts: number;
    total_reports: number;
    market_cap: number;
  };
  trending_sectors: Array<{
    name: string;
    performance: number;
    change: number;
  }>;
  top_companies: Array<{
    name: string;
    ticker: string;
    sector: string;
    current_price: number;
    change_percent: number;
  }>;
  recent_reports: Array<{
    title: string;
    author: string;
    date: string;
    summary: string;
  }>;
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        // Mock data matching the screenshot exactly
        const mockData: DashboardData = {
          platform_stats: {
            total_companies: 2847,
            active_analysts: 156,
            total_reports: 892,
            market_cap: 2400000000000 // $2.4T
          },
          trending_sectors: [
            { name: 'Technology', performance: 15.2, change: 2.3 },
            { name: 'Healthcare', performance: 8.7, change: 1.8 },
            { name: 'Finance', performance: 6.4, change: 1.2 },
            { name: 'Energy', performance: 4.2, change: -0.8 }
          ],
          top_companies: [
            { name: 'Microsoft Corp', ticker: 'MSFT', sector: 'Technology', current_price: 378.85, change_percent: 2.3 },
            { name: 'Apple Inc', ticker: 'AAPL', sector: 'Technology', current_price: 185.92, change_percent: 1.8 },
            { name: 'Tesla Inc', ticker: 'TSLA', sector: 'Automotive', current_price: 237.49, change_percent: 3.1 },
            { name: 'Amazon.com', ticker: 'AMZN', sector: 'E-commerce', current_price: 151.94, change_percent: 1.5 },
            { name: 'Alphabet Inc', ticker: 'GOOGL', sector: 'Technology', current_price: 140.93, change_percent: 2.7 }
          ],
          recent_reports: [
            {
              title: 'Microsoft Corp: Cloud Growth Drives Q4 Performance',
              author: 'Sarah Johnson',
              date: '2024-01-15',
              summary: 'Microsoft\'s Azure cloud services continue to show strong growth, with revenue up 28% year-over-year...'
            },
            {
              title: 'Apple Inc: iPhone 15 Pro Sales Exceed Expectations',
              author: 'Michael Chen',
              date: '2024-01-14',
              summary: 'Apple\'s latest iPhone models are performing above analyst expectations, particularly in emerging markets...'
            },
            {
              title: 'Tesla: EV Market Share Analysis and Future Outlook',
              author: 'Emily Rodriguez',
              date: '2024-01-13',
              summary: 'Tesla maintains its leadership position in the electric vehicle market despite increasing competition...'
            }
          ]
        };

        setDashboardData(mockData);
      } catch (err) {
        setError('Failed to load dashboard data');
        console.error('Dashboard data fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 p-8">
          <div className="text-red-600">{error}</div>
        </div>
      </div>
    );
  }

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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Trefis Analytics Platform</h1>
            <p className="text-gray-600">Comprehensive financial analysis and market intelligence</p>
          </div>

          {/* Key Metrics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Companies</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.platform_stats.total_companies?.toLocaleString() || 'N/A'}
                  </p>
                  <p className="text-sm text-green-600">+12% from last month</p>
                </div>
                <div className="p-3 bg-blue-100 rounded-lg">
                  <Building2 className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Active Analysts</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.platform_stats.active_analysts || 'N/A'}
                  </p>
                  <p className="text-sm text-green-600">+5% from last week</p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <Users className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Reports</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.platform_stats.total_reports || 'N/A'}
                  </p>
                  <p className="text-sm text-green-600">+8% from last month</p>
                </div>
                <div className="p-3 bg-purple-100 rounded-lg">
                  <FileText className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </Card>

            <Card className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Market Cap</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {dashboardData?.platform_stats.market_cap ? 
                      formatCurrency(dashboardData.platform_stats.market_cap) : 'N/A'}
                  </p>
                  <p className="text-sm text-green-600">+2.1% from yesterday</p>
                </div>
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <DollarSign className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </Card>
          </div>

          {/* Trending Sectors */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Trending Sectors</h2>
            <p className="text-gray-600 mb-4">Most active sectors in the market today.</p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {dashboardData?.trending_sectors?.map((sector) => (
                <Card key={sector.name} className="p-4 cursor-pointer hover:shadow-md transition-shadow">
                  <h3 className="font-semibold text-gray-900 mb-2">{sector.name}</h3>
                  <p className="text-2xl font-bold text-gray-900">{sector.performance}%</p>
                  <p className={`text-sm font-medium ${
                    sector.change >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}>
                    {formatPercent(sector.change)}
                  </p>
                </Card>
              ))}
            </div>
          </div>

          {/* Top Companies */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Top Companies</h2>
            <p className="text-gray-600 mb-4">Leading companies by market performance.</p>
            <Card className="p-6">
              <div className="space-y-4">
                {dashboardData?.top_companies?.map((company) => (
                  <div key={company.ticker} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{company.name}</p>
                      <p className="text-sm text-gray-600">{company.ticker} • {company.sector}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">${company.current_price}</p>
                      <p className={`text-sm font-medium ${
                        company.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(company.change_percent)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-4 text-center">
                <Button className="bg-blue-600 hover:bg-blue-700">
                  View All Companies
                </Button>
              </div>
            </Card>
          </div>

          {/* Recent Analyst Reports */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Recent Analyst Reports</h2>
            <p className="text-gray-600 mb-4">Latest insights from our analyst team.</p>
            <div className="space-y-4">
              {dashboardData?.recent_reports?.map((report, index) => (
                <Card key={index} className="p-6">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">{report.title}</h3>
                      <p className="text-sm text-gray-600 mb-2">By {report.author} | {report.date}</p>
                      <p className="text-gray-700">{report.summary}</p>
                    </div>
                    <Button variant="outline" className="ml-4">
                      Read full report
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 
} 