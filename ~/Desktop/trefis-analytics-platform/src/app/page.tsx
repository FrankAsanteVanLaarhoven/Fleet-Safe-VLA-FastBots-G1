'use client';

import React from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { 
  LayoutDashboard, 
  Building2, 
  FileText, 
  BarChart3, 
  Globe, 
  TrendingUp, 
  Shield, 
  Settings,
  ArrowRight,
  DollarSign,
  Users,
  BarChart
} from 'lucide-react';

export default function HomePage() {
  const quickActions = [
    {
      title: 'Dashboard',
      description: 'Real-time market overview and key metrics',
      href: '/dashboard',
      icon: <LayoutDashboard className="w-6 h-6" />,
      color: 'bg-blue-500'
    },
    {
      title: 'Company Profiles',
      description: 'Comprehensive company information and analysis',
      href: '/company-analysis/profiles',
      icon: <Building2 className="w-6 h-6" />,
      color: 'bg-green-500'
    },
    {
      title: 'Analyst Reports',
      description: 'Latest market analysis and investment insights',
      href: '/analyst-reports/latest',
      icon: <FileText className="w-6 h-6" />,
      color: 'bg-purple-500'
    },
    {
      title: 'Performance Charts',
      description: 'Interactive charts and data visualization',
      href: '/charts/performance',
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'bg-orange-500'
    },
    {
      title: 'Market Data',
      description: 'Global market trends and sector analysis',
      href: '/market-data/overview',
      icon: <Globe className="w-6 h-6" />,
      color: 'bg-red-500'
    },
    {
      title: 'Data Analytics',
      description: 'Advanced financial metrics and risk analysis',
      href: '/analytics/metrics',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'bg-indigo-500'
    }
  ];

  const stats = [
    {
      label: 'Total Market Cap',
      value: '$45.2T',
      icon: <DollarSign className="w-5 h-5" />,
      change: '+2.3%',
      trend: 'up'
    },
    {
      label: 'Active Companies',
      value: '8,500+',
      icon: <Users className="w-5 h-5" />,
      change: '+156',
      trend: 'up'
    },
    {
      label: 'Analyst Reports',
      value: '15,000+',
      icon: <FileText className="w-5 h-5" />,
      change: '+45',
      trend: 'up'
    },
    {
      label: 'Data Accuracy',
      value: '99.2%',
      icon: <BarChart className="w-5 h-5" />,
      change: '+0.3%',
      trend: 'up'
    }
  ];

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Welcome to Trefis Analytics</h1>
            <p className="text-xl text-gray-600">Your comprehensive financial analytics and market intelligence platform</p>
          </div>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => (
              <Card key={index} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">{stat.label}</p>
                    <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                    <p className={`text-sm font-medium ${
                      stat.trend === 'up' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </p>
                  </div>
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <div className="text-blue-600">
                      {stat.icon}
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Quick Actions */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Quick Actions</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {quickActions.map((action, index) => (
                <Link key={index} href={action.href}>
                  <Card className="p-6 hover:shadow-lg transition-shadow cursor-pointer group">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white mb-4 ${action.color}`}>
                          {action.icon}
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{action.title}</h3>
                        <p className="text-gray-600 text-sm">{action.description}</p>
                      </div>
                      <ArrowRight className="w-5 h-5 text-gray-400 group-hover:text-gray-600 transition-colors" />
                    </div>
                  </Card>
                </Link>
              ))}
            </div>
          </div>

          {/* Recent Activity */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Recent Activity</h2>
            <Card className="p-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Technology Sector Report Updated</p>
                    <p className="text-sm text-gray-600">Dr. Sarah Chen • 2 hours ago</p>
                  </div>
                  <Button size="sm" variant="outline">View</Button>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">Microsoft Financial Data Refreshed</p>
                    <p className="text-sm text-gray-600">System • 4 hours ago</p>
                  </div>
                  <Button size="sm" variant="outline">View</Button>
                </div>
                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">New Market Analysis Published</p>
                    <p className="text-sm text-gray-600">Michael Rodriguez • 6 hours ago</p>
                  </div>
                  <Button size="sm" variant="outline">View</Button>
                </div>
              </div>
            </Card>
          </div>

          {/* Platform Features */}
          <div>
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Platform Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Real-Time Data</h3>
                <p className="text-gray-600 mb-4">
                  Access live market data, real-time stock prices, and up-to-the-minute financial metrics with 99.2% accuracy.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Live stock prices and market data</li>
                  <li>• Real-time financial metrics</li>
                  <li>• Instant alerts and notifications</li>
                </ul>
              </Card>
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Advanced Analytics</h3>
                <p className="text-gray-600 mb-4">
                  Leverage AI-powered analytics, risk assessment models, and predictive insights for informed investment decisions.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• AI-powered valuation models</li>
                  <li>• Risk analysis and assessment</li>
                  <li>• Growth projections and forecasts</li>
                </ul>
              </Card>
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Expert Analysis</h3>
                <p className="text-gray-600 mb-4">
                  Access comprehensive analyst reports, sector analysis, and investment recommendations from industry experts.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Professional analyst reports</li>
                  <li>• Sector and industry analysis</li>
                  <li>• Investment recommendations</li>
                </ul>
              </Card>
              <Card className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">Interactive Charts</h3>
                <p className="text-gray-600 mb-4">
                  Visualize data with interactive charts, customizable dashboards, and comprehensive data visualization tools.
                </p>
                <ul className="space-y-2 text-sm text-gray-600">
                  <li>• Interactive performance charts</li>
                  <li>• Customizable dashboards</li>
                  <li>• Export and sharing capabilities</li>
                </ul>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 