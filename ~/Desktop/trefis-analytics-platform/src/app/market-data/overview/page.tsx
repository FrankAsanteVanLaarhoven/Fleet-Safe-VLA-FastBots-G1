'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrefisChart } from '@/components/charts/TrefisChart';
import { Globe, TrendingUp, BarChart3, DollarSign } from 'lucide-react';

export default function MarketOverviewPage() {
  const [marketData, setMarketData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        const mockData = {
          global_markets: {
            sp500: { value: 4850.43, change: 0.8 },
            nasdaq: { value: 15234.12, change: 1.2 },
            dow: { value: 37850.67, change: 0.5 },
            ftse: { value: 7689.12, change: -0.3 }
          },
          sector_performance: [
            { name: 'Technology', performance: 15.2, change: 2.3 },
            { name: 'Healthcare', performance: 8.7, change: 1.8 },
            { name: 'Financial Services', performance: 6.4, change: 1.2 },
            { name: 'Consumer Discretionary', performance: 5.8, change: 0.9 },
            { name: 'Energy', performance: 4.2, change: -0.8 }
          ],
          market_indicators: {
            vix: 18.5,
            treasury_10y: 4.25,
            gold: 2050.00,
            oil: 78.50
          }
        };
        setMarketData(mockData);
      } catch (error) {
        console.error('Error fetching market data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchMarketData();
  }, []);

  const formatPercent = (value: number) => {
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {[...Array(4)].map((_, i) => (
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
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Market Overview</h1>
            <p className="text-gray-600">Global market trends and performance indicators</p>
          </div>

          {/* Global Markets */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Global Markets</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {Object.entries(marketData?.global_markets || {}).map(([index, data]: [string, any]) => (
                <Card key={index} className="p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">{index.toUpperCase()}</p>
                      <p className="text-2xl font-bold text-gray-900">{data.value.toLocaleString()}</p>
                      <p className={`text-sm font-medium ${
                        data.change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(data.change)}
                      </p>
                    </div>
                    <div className="p-3 bg-blue-100 rounded-lg">
                      <Globe className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>

          {/* Sector Performance */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Sector Performance</h2>
            <Card className="p-6">
              <div className="space-y-4">
                {marketData?.sector_performance?.map((sector: any, index: number) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{sector.name}</p>
                      <p className="text-sm text-gray-600">{sector.performance}% performance</p>
                    </div>
                    <div className="text-right">
                      <p className={`text-lg font-semibold ${
                        sector.change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatPercent(sector.change)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>

          {/* Market Indicators */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Market Indicators</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card className="p-6">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">VIX (Fear Index)</p>
                  <p className="text-2xl font-bold text-gray-900">{marketData?.market_indicators.vix}</p>
                  <p className="text-sm text-gray-600">Low Volatility</p>
                </div>
              </Card>
              <Card className="p-6">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">10Y Treasury</p>
                  <p className="text-2xl font-bold text-gray-900">{marketData?.market_indicators.treasury_10y}%</p>
                  <p className="text-sm text-gray-600">Yield</p>
                </div>
              </Card>
              <Card className="p-6">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Gold</p>
                  <p className="text-2xl font-bold text-gray-900">${marketData?.market_indicators.gold}</p>
                  <p className="text-sm text-gray-600">Per Ounce</p>
                </div>
              </Card>
              <Card className="p-6">
                <div className="text-center">
                  <p className="text-sm text-gray-600 mb-1">Oil (WTI)</p>
                  <p className="text-2xl font-bold text-gray-900">${marketData?.market_indicators.oil}</p>
                  <p className="text-sm text-gray-600">Per Barrel</p>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 