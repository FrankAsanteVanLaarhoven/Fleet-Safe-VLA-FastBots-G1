'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrefisChart } from '@/components/charts/TrefisChart';
import { Search, TrendingUp, Calculator, Target } from 'lucide-react';

export default function ValuationPage() {
  const [valuations, setValuations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchValuations = async () => {
      try {
        setLoading(true);
        const mockData = [
          {
            company_id: 'MSFT',
            name: 'Microsoft Corporation',
            current_price: 412.50,
            fair_value: 485.00,
            upside_potential: 17.7,
            valuation_methods: {
              dcf: 485.00,
              pe_ratio: 472.00,
              ev_ebitda: 498.00,
              sum_of_parts: 490.00
            },
            key_assumptions: {
              growth_rate: 12.5,
              discount_rate: 8.2,
              terminal_growth: 3.0
            }
          },
          {
            company_id: 'AAPL',
            name: 'Apple Inc.',
            current_price: 185.00,
            fair_value: 210.00,
            upside_potential: 13.5,
            valuation_methods: {
              dcf: 210.00,
              pe_ratio: 205.00,
              ev_ebitda: 215.00,
              sum_of_parts: 208.00
            },
            key_assumptions: {
              growth_rate: 8.2,
              discount_rate: 7.8,
              terminal_growth: 2.5
            }
          }
        ];
        setValuations(mockData);
      } catch (error) {
        console.error('Error fetching valuations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchValuations();
  }, []);

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 2
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
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 rounded"></div>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Valuation Models</h1>
            <p className="text-gray-600">Advanced valuation analysis and fair value estimates</p>
          </div>

          <div className="space-y-6">
            {valuations.map((valuation) => (
              <Card key={valuation.company_id} className="p-6">
                <div className="mb-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{valuation.name}</h3>
                  <p className="text-gray-600">{valuation.company_id}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="text-center p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Current Price</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(valuation.current_price)}</p>
                  </div>
                  <div className="text-center p-4 bg-green-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Fair Value</p>
                    <p className="text-2xl font-bold text-gray-900">{formatCurrency(valuation.fair_value)}</p>
                  </div>
                  <div className="text-center p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Upside Potential</p>
                    <p className="text-2xl font-bold text-green-600">{formatPercent(valuation.upside_potential)}</p>
                  </div>
                </div>

                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Valuation Methods</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-3 border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-600">DCF Model</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(valuation.valuation_methods.dcf)}</p>
                    </div>
                    <div className="p-3 border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-600">P/E Ratio</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(valuation.valuation_methods.pe_ratio)}</p>
                    </div>
                    <div className="p-3 border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-600">EV/EBITDA</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(valuation.valuation_methods.ev_ebitda)}</p>
                    </div>
                    <div className="p-3 border border-gray-200 rounded-lg">
                      <p className="text-sm text-gray-600">Sum of Parts</p>
                      <p className="text-lg font-semibold text-gray-900">{formatCurrency(valuation.valuation_methods.sum_of_parts)}</p>
                    </div>
                  </div>
                </div>

                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-3">Key Assumptions</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Growth Rate</p>
                      <p className="text-lg font-semibold text-gray-900">{valuation.key_assumptions.growth_rate}%</p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Discount Rate</p>
                      <p className="text-lg font-semibold text-gray-900">{valuation.key_assumptions.discount_rate}%</p>
                    </div>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-600">Terminal Growth</p>
                      <p className="text-lg font-semibold text-gray-900">{valuation.key_assumptions.terminal_growth}%</p>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2">
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    View Detailed Model
                  </Button>
                  <Button variant="outline">
                    Download Valuation
                  </Button>
                  <Button variant="outline">
                    Sensitivity Analysis
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 