'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { trefisApi, FinancialData } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrefisChart } from '@/components/charts/TrefisChart';
import { Search, TrendingUp, TrendingDown, DollarSign, BarChart3 } from 'lucide-react';

export default function FinancialDataPage() {
  const [financialData, setFinancialData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedPeriod, setSelectedPeriod] = useState('latest');

  useEffect(() => {
    const fetchFinancialData = async () => {
      try {
        setLoading(true);
        // Mock financial data
        const mockData = [
          {
            company_id: 'MSFT',
            name: 'Microsoft Corporation',
            period: 'Q4 2024',
            revenue: 62000000000,
            net_income: 21800000000,
            eps: 2.93,
            operating_margin: 35.2,
            debt_to_equity: 0.35,
            return_on_equity: 38.7,
            free_cash_flow: 18500000000,
            revenue_growth: 15.8,
            net_income_growth: 23.4
          },
          {
            company_id: 'AAPL',
            name: 'Apple Inc.',
            period: 'Q4 2024',
            revenue: 119600000000,
            net_income: 33916000000,
            eps: 2.18,
            operating_margin: 28.3,
            debt_to_equity: 1.45,
            return_on_equity: 147.8,
            free_cash_flow: 28500000000,
            revenue_growth: 8.1,
            net_income_growth: 13.1
          },
          {
            company_id: 'GOOGL',
            name: 'Alphabet Inc.',
            period: 'Q4 2024',
            revenue: 86310000000,
            net_income: 20687000000,
            eps: 1.64,
            operating_margin: 24.0,
            debt_to_equity: 0.12,
            return_on_equity: 25.3,
            free_cash_flow: 17500000000,
            revenue_growth: 13.5,
            net_income_growth: 52.3
          }
        ];

        setFinancialData(mockData);
      } catch (error) {
        console.error('Error fetching financial data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchFinancialData();
  }, []);

  const filteredData = financialData.filter(item => 
    item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.company_id.toLowerCase().includes(searchQuery.toLowerCase())
  );

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
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-48 bg-gray-200 rounded"></div>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Financial Data</h1>
            <p className="text-gray-600">Comprehensive financial statements and metrics</p>
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
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="latest">Latest Quarter</option>
                <option value="annual">Annual</option>
                <option value="trailing">Trailing 12 Months</option>
              </select>
            </div>
          </div>

          {/* Financial Data Cards */}
          <div className="space-y-6">
            {filteredData.map((item) => (
              <Card key={item.company_id} className="p-6">
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{item.name}</h3>
                  <p className="text-gray-600">{item.company_id} • {item.period}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Revenue</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(item.revenue)}</p>
                    <p className={`text-sm font-medium ${
                      item.revenue_growth >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercent(item.revenue_growth)}
                    </p>
                  </div>

                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Net Income</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(item.net_income)}</p>
                    <p className={`text-sm font-medium ${
                      item.net_income_growth >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {formatPercent(item.net_income_growth)}
                    </p>
                  </div>

                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">EPS</p>
                    <p className="text-2xl font-bold text-gray-900">${item.eps}</p>
                    <p className="text-sm text-gray-600">Per Share</p>
                  </div>

                  <div className="text-center p-4 bg-yellow-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Operating Margin</p>
                    <p className="text-2xl font-bold text-gray-900">{item.operating_margin}%</p>
                    <p className="text-sm text-gray-600">Profitability</p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Debt to Equity</p>
                    <p className="text-lg font-semibold text-gray-900">{item.debt_to_equity}</p>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Return on Equity</p>
                    <p className="text-lg font-semibold text-gray-900">{item.return_on_equity}%</p>
                  </div>
                  <div className="p-4 border border-gray-200 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Free Cash Flow</p>
                    <p className="text-lg font-semibold text-gray-900">{formatCurrency(item.free_cash_flow)}</p>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    View Full Financials
                  </Button>
                  <Button variant="outline">
                    Download Report
                  </Button>
                  <Button variant="outline">
                    Compare Peers
                  </Button>
                </div>
              </Card>
            ))}
          </div>

          {filteredData.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No financial data found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 