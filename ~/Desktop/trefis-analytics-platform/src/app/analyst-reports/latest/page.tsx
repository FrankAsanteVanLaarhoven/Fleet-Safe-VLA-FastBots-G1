'use client';

import React, { useEffect, useState } from 'react';
import { Sidebar } from '@/components/navigation/sidebar';
import { trefisApi, AnalystReport } from '@/lib/api';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search, Filter, Calendar, User, TrendingUp, FileText } from 'lucide-react';

export default function LatestReportsPage() {
  const [reports, setReports] = useState<AnalystReport[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSector, setSelectedSector] = useState('');
  const [selectedAuthor, setSelectedAuthor] = useState('');

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

  const authors = [
    'Dr. Sarah Chen',
    'Michael Rodriguez',
    'Jennifer Thompson',
    'David Kim',
    'Lisa Wang',
    'Robert Johnson'
  ];

  useEffect(() => {
    const fetchReports = async () => {
      try {
        setLoading(true);
        // Mock data for demonstration
        const mockReports: AnalystReport[] = [
          {
            report_id: 'TREFIS-TECH-2024-Q3',
            title: 'Technology Sector Q3 2024: AI Revolution and Cloud Migration Acceleration',
            author: 'Dr. Sarah Chen',
            date: '2024-07-21',
            summary: 'The technology sector continues to experience unprecedented growth driven by AI adoption, cloud migration, and digital transformation initiatives. Our analysis reveals 23% YoY growth in cloud services, 156% increase in AI/ML investments, and emerging opportunities in quantum computing and edge infrastructure.',
            key_findings: [
              'Cloud computing market reached $650B in Q2 2024, up 18% from Q1',
              'AI/ML spending increased 156% YoY across enterprise sectors',
              'Cybersecurity investments grew 34% due to rising threat landscape',
              'Edge computing adoption accelerated by 89% in manufacturing and IoT',
              'Quantum computing market projected to reach $8.6B by 2027'
            ],
            company_analysis: {
              microsoft: {
                rating: 'Strong Buy',
                target_price: 485,
                current_price: 412,
                upside: '17.7%',
                key_drivers: ['Azure growth', 'AI integration', 'Enterprise adoption']
              },
              amazon: {
                rating: 'Buy',
                target_price: 185,
                current_price: 168,
                upside: '10.1%',
                key_drivers: ['AWS dominance', 'E-commerce recovery', 'AI services']
              }
            },
            sector_outlook: {
              short_term: 'Bullish - Continued AI adoption and cloud migration',
              medium_term: 'Very Bullish - Quantum computing and edge infrastructure growth',
              long_term: 'Bullish - Sustainable technology transformation across industries'
            },
            investment_recommendations: [
              'Overweight technology sector allocation',
              'Focus on AI/ML and cloud service providers',
              'Consider cybersecurity and quantum computing exposure',
              'Monitor regulatory developments closely'
            ]
          },
          {
            report_id: 'TREFIS-HEALTH-2024-Q3',
            title: 'Healthcare Sector Outlook: Biotech Innovation and Digital Health Transformation',
            author: 'Michael Rodriguez',
            date: '2024-07-20',
            summary: 'The healthcare sector is undergoing a digital transformation with significant investments in biotechnology, telemedicine, and AI-driven diagnostics. Our analysis shows 28% growth in digital health spending and breakthrough developments in gene therapy and personalized medicine.',
            key_findings: [
              'Digital health market reached $180B in 2024, growing 28% YoY',
              'Biotech funding increased 45% with focus on gene therapy',
              'Telemedicine adoption reached 78% of healthcare providers',
              'AI diagnostics market projected to reach $12B by 2026',
              'Personalized medicine spending grew 67% in Q2 2024'
            ],
            company_analysis: {
              moderna: {
                rating: 'Buy',
                target_price: 145,
                current_price: 128,
                upside: '13.3%',
                key_drivers: ['mRNA technology', 'Pipeline expansion', 'Partnerships']
              }
            },
            sector_outlook: {
              short_term: 'Bullish - Continued innovation and regulatory support',
              medium_term: 'Very Bullish - Breakthrough therapies and digital adoption',
              long_term: 'Bullish - Personalized medicine and AI integration'
            },
            investment_recommendations: [
              'Focus on biotech companies with strong pipelines',
              'Consider digital health and telemedicine providers',
              'Monitor regulatory approval timelines',
              'Diversify across therapeutic areas'
            ]
          },
          {
            report_id: 'TREFIS-FIN-2024-Q3',
            title: 'Financial Services Evolution: Fintech Disruption and Digital Banking Growth',
            author: 'Jennifer Thompson',
            date: '2024-07-19',
            summary: 'The financial services sector is experiencing rapid digital transformation with fintech companies disrupting traditional banking models. Our analysis reveals 42% growth in digital banking adoption and significant investments in blockchain and AI-powered financial services.',
            key_findings: [
              'Digital banking adoption reached 67% globally in 2024',
              'Fintech investment increased 89% YoY to $45B',
              'Blockchain in finance market grew 156% to $8.2B',
              'AI-powered financial services market reached $15B',
              'Mobile payments volume increased 78% YoY'
            ],
            company_analysis: {
              jpmorgan: {
                rating: 'Hold',
                target_price: 185,
                current_price: 178,
                upside: '3.9%',
                key_drivers: ['Digital transformation', 'Investment banking', 'Cost efficiency']
              }
            },
            sector_outlook: {
              short_term: 'Neutral - Regulatory uncertainty and competition',
              medium_term: 'Bullish - Digital transformation and efficiency gains',
              long_term: 'Bullish - Fintech integration and global expansion'
            },
            investment_recommendations: [
              'Focus on banks with strong digital initiatives',
              'Consider fintech companies with proven business models',
              'Monitor regulatory developments in crypto and fintech',
              'Diversify across traditional and digital financial services'
            ]
          }
        ];

        setReports(mockReports);
      } catch (error) {
        console.error('Error fetching reports:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchReports();
  }, []);

  const filteredReports = reports.filter(report => {
    const matchesSearch = report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         report.summary.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSector = !selectedSector || report.sector_outlook?.short_term?.toLowerCase().includes(selectedSector.toLowerCase());
    const matchesAuthor = !selectedAuthor || report.author === selectedAuthor;
    return matchesSearch && matchesSector && matchesAuthor;
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
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
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Latest Analyst Reports</h1>
            <p className="text-gray-600">Comprehensive market analysis and investment insights</p>
          </div>

          {/* Search and Filters */}
          <div className="mb-6 space-y-4">
            <div className="flex gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="Search reports..."
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
                value={selectedAuthor}
                onChange={(e) => setSelectedAuthor(e.target.value)}
                className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">All Authors</option>
                {authors.map(author => (
                  <option key={author} value={author}>{author}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Reports */}
          <div className="space-y-6">
            {filteredReports.map((report) => (
              <Card key={report.report_id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">{report.title}</h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <User className="w-4 h-4 mr-1" />
                        {report.author}
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        {formatDate(report.date)}
                      </div>
                      <div className="flex items-center">
                        <FileText className="w-4 h-4 mr-1" />
                        {report.report_id}
                      </div>
                    </div>
                  </div>
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    View Full Report
                  </Button>
                </div>

                <p className="text-gray-700 mb-4">{report.summary}</p>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-4">
                  {/* Key Findings */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Key Findings</h4>
                    <ul className="space-y-1">
                      {report.key_findings?.slice(0, 3).map((finding, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start">
                          <span className="text-blue-600 mr-2">•</span>
                          {finding}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Investment Recommendations */}
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Investment Recommendations</h4>
                    <ul className="space-y-1">
                      {report.investment_recommendations?.slice(0, 3).map((rec, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start">
                          <span className="text-green-600 mr-2">•</span>
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Company Analysis Preview */}
                {report.company_analysis && Object.keys(report.company_analysis).length > 0 && (
                  <div className="mb-4">
                    <h4 className="font-semibold text-gray-900 mb-2">Featured Companies</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                      {Object.entries(report.company_analysis).slice(0, 3).map(([company, analysis]: [string, any]) => (
                        <div key={company} className="p-3 bg-gray-50 rounded-lg">
                          <div className="flex justify-between items-center mb-1">
                            <span className="font-medium text-gray-900 capitalize">{company}</span>
                            <span className={`px-2 py-1 text-xs rounded-full ${
                              analysis.rating === 'Strong Buy' ? 'bg-green-100 text-green-800' :
                              analysis.rating === 'Buy' ? 'bg-blue-100 text-blue-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {analysis.rating}
                            </span>
                          </div>
                          <div className="text-sm text-gray-600">
                            <div>Target: ${analysis.target_price}</div>
                            <div className="text-green-600">Upside: {analysis.upside}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Sector Outlook */}
                <div className="border-t pt-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Sector Outlook</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-600">Short Term</p>
                      <p className="font-medium text-gray-900">{report.sector_outlook?.short_term}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Medium Term</p>
                      <p className="font-medium text-gray-900">{report.sector_outlook?.medium_term}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Long Term</p>
                      <p className="font-medium text-gray-900">{report.sector_outlook?.long_term}</p>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {filteredReports.length === 0 && (
            <div className="text-center py-12">
              <p className="text-gray-500">No reports found matching your criteria.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
} 