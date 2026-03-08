'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { trefisApi, ChartData } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { TrefisChart } from '@/components/charts/TrefisChart';
import { Search, TrendingUp, TrendingDown, BarChart3, LineChart, PieChart } from 'lucide-react';

export default function PerformanceChartsPage() {
  const [charts, setCharts] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeframe, setSelectedTimeframe] = useState('1Y');
  const [selectedChartType, setSelectedChartType] = useState('all');

  const timeframes = ['1M', '3M', '6M', '1Y', '3Y', '5Y'];
  const chartTypes = ['line', 'bar', 'area', 'candlestick'];

  useEffect(() => {
    const fetchCharts = async () => {
      try {
        setLoading(true);
        // Mock chart data for demonstration
        const mockCharts: ChartData[] = [
          {
            chart_id: 'TECH-SECTOR-PERF-2024',
            title: 'Technology Sector Performance Q1-Q3 2024',
            type: 'line',
            data: {
              labels: ['Q1 2024', 'Q2 2024', 'Q3 2024'],
              datasets: [
                {
                  label: 'Microsoft (MSFT)',
                  data: [412.50, 445.20, 485.00],
                  borderColor: '#00A4EF',
                  backgroundColor: 'rgba(0, 164, 239, 0.1)',
                  tension: 0.4
                },
                {
                  label: 'Amazon (AMZN)',
                  data: [168.00, 175.30, 185.00],
                  borderColor: '#FF9900',
                  backgroundColor: 'rgba(255, 153, 0, 0.1)',
                  tension: 0.4
                },
                {
                  label: 'Alphabet (GOOGL)',
                  data: [142.00, 155.80, 165.00],
                  borderColor: '#4285F4',
                  backgroundColor: 'rgba(66, 133, 244, 0.1)',
                  tension: 0.4
                },
                {
                  label: 'Apple (AAPL)',
                  data: [185.00, 198.50, 210.00],
                  borderColor: '#A2AAAD',
                  backgroundColor: 'rgba(162, 170, 173, 0.1)',
                  tension: 0.4
                },
                {
                  label: 'NVIDIA (NVDA)',
                  data: [875.00, 950.00, 1100.00],
                  borderColor: '#76B900',
                  backgroundColor: 'rgba(118, 185, 0, 0.1)',
                  tension: 0.4
                }
              ]
            },
            options: {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: 'Technology Sector Stock Performance (Q1-Q3 2024)'
                },
                legend: {
                  position: 'top'
                }
              },
              scales: {
                y: {
                  beginAtZero: false,
                  title: {
                    display: true,
                    text: 'Stock Price ($)'
                  }
                },
                x: {
                  title: {
                    display: true,
                    text: 'Quarter'
                  }
                }
              }
            }
          },
          {
            chart_id: 'MARKET-CAP-COMPARISON',
            title: 'Market Capitalization Comparison',
            type: 'bar',
            data: {
              labels: ['Microsoft', 'Apple', 'Alphabet', 'Amazon', 'NVIDIA'],
              datasets: [
                {
                  label: 'Market Cap ($B)',
                  data: [3120, 2850, 1850, 1680, 1100],
                  backgroundColor: [
                    'rgba(0, 164, 239, 0.8)',
                    'rgba(162, 170, 173, 0.8)',
                    'rgba(66, 133, 244, 0.8)',
                    'rgba(255, 153, 0, 0.8)',
                    'rgba(118, 185, 0, 0.8)'
                  ],
                  borderColor: [
                    '#00A4EF',
                    '#A2AAAD',
                    '#4285F4',
                    '#FF9900',
                    '#76B900'
                  ],
                  borderWidth: 1
                }
              ]
            },
            options: {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: 'Market Capitalization Comparison (Billions USD)'
                },
                legend: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Market Cap ($B)'
                  }
                }
              }
            }
          },
          {
            chart_id: 'REVENUE-GROWTH',
            title: 'Revenue Growth Comparison',
            type: 'bar',
            data: {
              labels: ['Microsoft', 'Apple', 'Alphabet', 'Amazon', 'NVIDIA'],
              datasets: [
                {
                  label: 'Revenue Growth YoY (%)',
                  data: [14.3, 8.2, 18.5, 12.1, 156.2],
                  backgroundColor: [
                    'rgba(0, 164, 239, 0.8)',
                    'rgba(162, 170, 173, 0.8)',
                    'rgba(66, 133, 244, 0.8)',
                    'rgba(255, 153, 0, 0.8)',
                    'rgba(118, 185, 0, 0.8)'
                  ],
                  borderColor: [
                    '#00A4EF',
                    '#A2AAAD',
                    '#4285F4',
                    '#FF9900',
                    '#76B900'
                  ],
                  borderWidth: 1
                }
              ]
            },
            options: {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: 'Revenue Growth Year-over-Year (%)'
                },
                legend: {
                  display: false
                }
              },
              scales: {
                y: {
                  beginAtZero: true,
                  title: {
                    display: true,
                    text: 'Growth (%)'
                  }
                }
              }
            }
          },
          {
            chart_id: 'SECTOR-ALLOCATION',
            title: 'Sector Allocation by Market Cap',
            type: 'doughnut',
            data: {
              labels: ['Technology', 'Healthcare', 'Financial Services', 'Consumer Discretionary', 'Energy', 'Others'],
              datasets: [
                {
                  data: [35, 18, 15, 12, 8, 12],
                  backgroundColor: [
                    'rgba(0, 164, 239, 0.8)',
                    'rgba(76, 175, 80, 0.8)',
                    'rgba(255, 193, 7, 0.8)',
                    'rgba(233, 30, 99, 0.8)',
                    'rgba(255, 152, 0, 0.8)',
                    'rgba(156, 39, 176, 0.8)'
                  ],
                  borderColor: [
                    '#00A4EF',
                    '#4CAF50',
                    '#FFC107',
                    '#E91E63',
                    '#FF9800',
                    '#9C27B0'
                  ],
                  borderWidth: 2
                }
              ]
            },
            options: {
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: 'S&P 500 Sector Allocation by Market Cap (%)'
                },
                legend: {
                  position: 'right'
                }
              }
            }
          }
        ];

        setCharts(mockCharts);
      } catch (error) {
        console.error('Error fetching charts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCharts();
  }, []);

  const filteredCharts = charts.filter(chart => {
    if (selectedChartType === 'all') return true;
    return chart.type === selectedChartType;
  });

  if (loading) {
    return (
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex-1 p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-6">
              {[...Array(2)].map((_, i) => (
                <div key={i} className="h-96 bg-gray-200 rounded"></div>
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Performance Charts</h1>
            <p className="text-gray-600">Interactive charts and data visualization</p>
          </div>

          {/* Controls */}
          <div className="mb-6 space-y-4">
            <div className="flex gap-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">Timeframe:</span>
                <div className="flex space-x-1">
                  {timeframes.map((timeframe) => (
                    <button
                      key={timeframe}
                      onClick={() => setSelectedTimeframe(timeframe)}
                      className={`px-3 py-1 text-sm rounded-lg transition-colors ${
                        selectedTimeframe === timeframe
                          ? 'bg-blue-600 text-white'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      }`}
                    >
                      {timeframe}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-medium text-gray-700">Chart Type:</span>
                <select
                  value={selectedChartType}
                  onChange={(e) => setSelectedChartType(e.target.value)}
                  className="px-3 py-1 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Types</option>
                  <option value="line">Line Charts</option>
                  <option value="bar">Bar Charts</option>
                  <option value="area">Area Charts</option>
                  <option value="doughnut">Doughnut Charts</option>
                </select>
              </div>
            </div>
          </div>

          {/* Charts Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {filteredCharts.map((chart) => (
              <Card key={chart.chart_id} className="p-6">
                <div className="mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">{chart.title}</h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center">
                      {chart.type === 'line' && <LineChart className="w-4 h-4 mr-1" />}
                      {chart.type === 'bar' && <BarChart3 className="w-4 h-4 mr-1" />}
                      {chart.type === 'doughnut' && <PieChart className="w-4 h-4 mr-1" />}
                      {chart.type.charAt(0).toUpperCase() + chart.type.slice(1)} Chart
                    </div>
                    <div className="flex items-center">
                      <span className="w-2 h-2 bg-blue-500 rounded-full mr-1"></span>
                      {chart.data.datasets.length} datasets
                    </div>
                  </div>
                </div>
                
                <div className="h-80">
                  <TrefisChart
                    data={chart.data}
                    options={chart.options}
                    title={chart.title}
                  />
                </div>

                <div className="mt-4 flex justify-between items-center">
                  <div className="text-sm text-gray-600">
                    Last updated: {new Date().toLocaleDateString()}
                  </div>
                  <div className="flex space-x-2">
                    <Button variant="outline" size="sm">
                      Export
                    </Button>
                    <Button variant="outline" size="sm">
                      Share
                    </Button>
                    <Button size="sm">
                      Full Screen
                    </Button>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {filteredCharts.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No charts found matching your criteria.</p>
            </div>
          )}

          {/* Quick Stats */}
          <div className="mt-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Quick Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <Card className="p-4">
                <div className="flex items-center">
                  <TrendingUp className="w-8 h-8 text-green-600 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600">Best Performer</p>
                    <p className="text-lg font-bold text-gray-900">NVIDIA</p>
                    <p className="text-sm text-green-600">+156.2%</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center">
                  <TrendingDown className="w-8 h-8 text-red-600 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600">Worst Performer</p>
                    <p className="text-lg font-bold text-gray-900">Apple</p>
                    <p className="text-sm text-red-600">+8.2%</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center">
                  <BarChart3 className="w-8 h-8 text-blue-600 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600">Avg Growth</p>
                    <p className="text-lg font-bold text-gray-900">41.8%</p>
                    <p className="text-sm text-gray-600">YoY</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center">
                  <TrendingUp className="w-8 h-8 text-purple-600 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600">Total Market Cap</p>
                    <p className="text-lg font-bold text-gray-900">$10.6T</p>
                    <p className="text-sm text-gray-600">Top 5 Tech</p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 