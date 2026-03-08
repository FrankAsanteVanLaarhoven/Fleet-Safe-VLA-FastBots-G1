'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Building2, 
  FileText, 
  BarChart3, 
  Globe, 
  TrendingUp, 
  Shield, 
  Settings,
  ChevronRight,
  ChevronLeft
} from 'lucide-react';

interface SidebarItem {
  name: string;
  href: string;
  icon: React.ReactNode;
  children?: SidebarItem[];
}

const sidebarItems: SidebarItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: <LayoutDashboard className="w-5 h-5" />
  },
  {
    name: 'Company Analysis',
    href: '/company-analysis',
    icon: <FileText className="w-5 h-5" />,
    children: [
      { name: 'Company Profiles', href: '/company-analysis/profiles', icon: <FileText className="w-4 h-4" /> },
      { name: 'Financial Data', href: '/company-analysis/financials', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'Valuation Models', href: '/company-analysis/valuation', icon: <TrendingUp className="w-4 h-4" /> }
    ]
  },
  {
    name: 'Market Data',
    href: '/market-data',
    icon: <Globe className="w-5 h-5" />,
    children: [
      { name: 'Market Overview', href: '/market-data/overview', icon: <TrendingUp className="w-4 h-4" /> },
      { name: 'Sector Analysis', href: '/market-data/sectors', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'Economic Indicators', href: '/market-data/indicators', icon: <TrendingUp className="w-4 h-4" /> }
    ]
  },
  {
    name: 'Analyst Reports',
    href: '/analyst-reports',
    icon: <FileText className="w-5 h-5" />,
    children: [
      { name: 'Latest Reports', href: '/analyst-reports/latest', icon: <TrendingUp className="w-4 h-4" /> },
      { name: 'Sector Reports', href: '/analyst-reports/sectors', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'Company Reports', href: '/analyst-reports/companies', icon: <FileText className="w-4 h-4" /> }
    ]
  },
  {
    name: 'Charts & Graphs',
    href: '/charts',
    icon: <BarChart3 className="w-5 h-5" />,
    children: [
      { name: 'Performance Charts', href: '/charts/performance', icon: <TrendingUp className="w-4 h-4" /> },
      { name: 'Comparison Tools', href: '/charts/comparison', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'Interactive Dashboards', href: '/charts/dashboards', icon: <TrendingUp className="w-4 h-4" /> }
    ]
  },
  {
    name: 'Data Analytics',
    href: '/analytics',
    icon: <TrendingUp className="w-5 h-5" />,
    children: [
      { name: 'Financial Metrics', href: '/analytics/metrics', icon: <BarChart3 className="w-4 h-4" /> },
      { name: 'Risk Analysis', href: '/analytics/risk', icon: <Shield className="w-4 h-4" /> },
      { name: 'Growth Projections', href: '/analytics/projections', icon: <TrendingUp className="w-4 h-4" /> }
    ]
  },
  {
    name: 'Security & Compliance',
    href: '/security',
    icon: <Shield className="w-5 h-5" />
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: <Settings className="w-5 h-5" />
  }
];

export function Sidebar() {
  const [expandedItems, setExpandedItems] = useState<string[]>([]);
  const pathname = usePathname();

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev => 
      prev.includes(itemName) 
        ? prev.filter(name => name !== itemName)
        : [...prev, itemName]
    );
  };

  const isActive = (href: string) => pathname === href;

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">T</span>
          </div>
          <span className="text-gray-900 font-semibold">Trefis Analytics</span>
        </div>
        <div className="flex items-center mt-2">
          <span className="text-lg font-bold text-gray-900">Trefis Analytics</span>
          <ChevronLeft className="w-4 h-4 ml-2 text-gray-500" />
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2">
        {sidebarItems.map((item) => (
          <div key={item.name}>
            <Link
              href={item.href}
              className={`flex items-center justify-between px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive(item.href)
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
              onClick={() => item.children && toggleExpanded(item.name)}
            >
              <div className="flex items-center space-x-3">
                {item.icon}
                <span>{item.name}</span>
              </div>
              {item.children && (
                <ChevronRight 
                  className={`w-4 h-4 transition-transform ${
                    expandedItems.includes(item.name) ? 'rotate-90' : ''
                  }`}
                />
              )}
            </Link>
            
            {item.children && expandedItems.includes(item.name) && (
              <div className="ml-8 mt-1 space-y-1">
                {item.children.map((child) => (
                  <Link
                    key={child.name}
                    href={child.href}
                    className={`flex items-center space-x-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                      isActive(child.href)
                        ? 'bg-blue-50 text-blue-700'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    {child.icon}
                    <span>{child.name}</span>
                  </Link>
                ))}
              </div>
            )}
          </div>
        ))}
      </nav>
    </div>
  );
} 