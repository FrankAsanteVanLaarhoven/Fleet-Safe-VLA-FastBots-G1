'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Check, 
  X, 
  Star, 
  Zap, 
  Shield, 
  Brain, 
  Globe, 
  Database,
  Lock,
  Target,
  Cpu,
  Crown,
  Sparkles,
  ArrowRight,
  Users,
  Clock,
  TrendingUp,
  Activity
} from 'lucide-react';

interface PricingTier {
  id: string;
  name: string;
  description: string;
  price: {
    monthly: number;
    yearly: number;
  };
  features: {
    name: string;
    included: boolean;
    limit?: string;
  }[];
  popular?: boolean;
  icon: any;
  color: string;
}

export default function PricingPage() {
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'yearly'>('monthly');
  const [selectedTier, setSelectedTier] = useState<string | null>(null);

  const pricingTiers: PricingTier[] = [
    {
      id: 'starter',
      name: 'Starter',
      description: 'Perfect for individual developers and small projects',
      price: {
        monthly: 29,
        yearly: 290
      },
      features: [
        { name: 'Neural Stealth Engine', included: true, limit: '1,000 requests/month' },
        { name: 'Quantum TLS Engine', included: true, limit: 'Basic encryption' },
        { name: 'Advanced Data Locator', included: true, limit: '10,000 data points/month' },
        { name: 'Autonomous Data Processor', included: false },
        { name: 'Universal Crawler', included: false },
        { name: 'Self-Healing Security', included: false },
        { name: 'Priority Support', included: false },
        { name: 'Custom AI Models', included: false },
        { name: 'Dedicated Infrastructure', included: false },
        { name: 'SLA Guarantee', included: false }
      ],
      icon: Zap,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      id: 'professional',
      name: 'Professional',
      description: 'Ideal for growing businesses and advanced use cases',
      price: {
        monthly: 99,
        yearly: 990
      },
      features: [
        { name: 'Neural Stealth Engine', included: true, limit: '10,000 requests/month' },
        { name: 'Quantum TLS Engine', included: true, limit: 'Advanced encryption' },
        { name: 'Advanced Data Locator', included: true, limit: '100,000 data points/month' },
        { name: 'Autonomous Data Processor', included: true, limit: '5,000 analyses/month' },
        { name: 'Universal Crawler', included: true, limit: '50,000 pages/month' },
        { name: 'Self-Healing Security', included: true, limit: 'Basic protection' },
        { name: 'Priority Support', included: true },
        { name: 'Custom AI Models', included: false },
        { name: 'Dedicated Infrastructure', included: false },
        { name: 'SLA Guarantee', included: false }
      ],
      popular: true,
      icon: Crown,
      color: 'from-purple-500 to-pink-500'
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      description: 'For large organizations requiring maximum performance and security',
      price: {
        monthly: 299,
        yearly: 2990
      },
      features: [
        { name: 'Neural Stealth Engine', included: true, limit: 'Unlimited' },
        { name: 'Quantum TLS Engine', included: true, limit: 'Quantum-resistant' },
        { name: 'Advanced Data Locator', included: true, limit: 'Unlimited' },
        { name: 'Autonomous Data Processor', included: true, limit: 'Unlimited' },
        { name: 'Universal Crawler', included: true, limit: 'Unlimited' },
        { name: 'Self-Healing Security', included: true, limit: 'Advanced protection' },
        { name: 'Priority Support', included: true },
        { name: 'Custom AI Models', included: true },
        { name: 'Dedicated Infrastructure', included: true },
        { name: 'SLA Guarantee', included: true }
      ],
      icon: Sparkles,
      color: 'from-orange-500 to-red-500'
    }
  ];

  const features = [
    {
      name: 'Neural Stealth Engine',
      description: 'AI-powered protection bypass with neural network learning',
      icon: Brain,
      color: 'from-purple-500 to-pink-500'
    },
    {
      name: 'Quantum TLS Engine',
      description: 'Quantum-resistant TLS connections with advanced encryption',
      icon: Lock,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      name: 'Advanced Data Locator',
      description: 'Intelligent data discovery and extraction from any source',
      icon: Target,
      color: 'from-green-500 to-emerald-500'
    },
    {
      name: 'Autonomous Data Processor',
      description: 'AI-powered data analysis and insights generation',
      icon: Cpu,
      color: 'from-orange-500 to-red-500'
    },
    {
      name: 'Universal Crawler',
      description: 'Universal web crawling with advanced protection bypass',
      icon: Globe,
      color: 'from-indigo-500 to-purple-500'
    },
    {
      name: 'Self-Healing Security',
      description: 'Zero-day threat detection and autonomous security response',
      icon: Shield,
      color: 'from-red-500 to-pink-500'
    }
  ];

  const savings = billingCycle === 'yearly' ? 17 : 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">Pricing</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors">
                <Users className="w-4 h-4" />
                <span>Contact Sales</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="text-center mb-16"
        >
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Choose Your AI Power Level
          </h2>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto mb-8">
            Scale from individual developer to enterprise with our flexible pricing tiers. 
            All plans include access to our advanced AI agent system.
          </p>

          {/* Billing Toggle */}
          <div className="flex items-center justify-center space-x-4 mb-8">
            <span className={`text-sm ${billingCycle === 'monthly' ? 'text-white' : 'text-gray-400'}`}>
              Monthly
            </span>
            <button
              onClick={() => setBillingCycle(billingCycle === 'monthly' ? 'yearly' : 'monthly')}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                billingCycle === 'yearly' ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-gray-600'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  billingCycle === 'yearly' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-sm ${billingCycle === 'yearly' ? 'text-white' : 'text-gray-400'}`}>
              Yearly
            </span>
            {billingCycle === 'yearly' && (
              <span className="bg-green-500/20 text-green-400 px-2 py-1 rounded-full text-xs font-medium">
                Save {savings}%
              </span>
            )}
          </div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {pricingTiers.map((tier, index) => (
            <motion.div
              key={tier.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: index * 0.1 }}
              className={`relative bg-white/5 backdrop-blur-sm border rounded-2xl p-8 ${
                tier.popular 
                  ? 'border-purple-500/50 bg-gradient-to-br from-purple-500/10 to-pink-500/10' 
                  : 'border-white/10'
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                </div>
              )}

              <div className="text-center mb-8">
                <div className={`w-16 h-16 bg-gradient-to-r ${tier.color} rounded-2xl flex items-center justify-center mx-auto mb-4`}>
                  <tier.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">{tier.name}</h3>
                <p className="text-gray-300 mb-6">{tier.description}</p>
                
                <div className="mb-6">
                  <div className="text-4xl font-bold text-white">
                    ${billingCycle === 'monthly' ? tier.price.monthly : tier.price.yearly}
                    <span className="text-lg text-gray-400">/{billingCycle === 'monthly' ? 'mo' : 'year'}</span>
                  </div>
                  {billingCycle === 'yearly' && (
                    <div className="text-sm text-gray-400 mt-1">
                      ${tier.price.monthly}/mo when billed monthly
                    </div>
                  )}
                </div>

                <button
                  onClick={() => setSelectedTier(tier.id)}
                  className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-300 ${
                    tier.popular
                      ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:opacity-90'
                      : 'bg-white/10 text-white hover:bg-white/20 border border-white/20'
                  }`}
                >
                  Get Started
                </button>
              </div>

              <div className="space-y-4">
                <h4 className="font-semibold text-white mb-4">What's included:</h4>
                {tier.features.map((feature, featureIndex) => (
                  <div key={featureIndex} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      {feature.included ? (
                        <Check className="w-5 h-5 text-green-400" />
                      ) : (
                        <X className="w-5 h-5 text-gray-500" />
                      )}
                      <span className={`text-sm ${feature.included ? 'text-white' : 'text-gray-500'}`}>
                        {feature.name}
                      </span>
                    </div>
                    {feature.limit && feature.included && (
                      <span className="text-xs text-gray-400">{feature.limit}</span>
                    )}
                  </div>
                ))}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Features Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Powered by Advanced AI Agents
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.5 + index * 0.1 }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all duration-300"
              >
                <div className={`w-12 h-12 bg-gradient-to-r ${feature.color} rounded-lg flex items-center justify-center mb-4`}>
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">{feature.name}</h3>
                <p className="text-gray-300 text-sm">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Comparison Table */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mb-16"
        >
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Detailed Feature Comparison
          </h2>
          
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left p-6 text-white font-semibold">Feature</th>
                    <th className="text-center p-6 text-white font-semibold">Starter</th>
                    <th className="text-center p-6 text-white font-semibold">Professional</th>
                    <th className="text-center p-6 text-white font-semibold">Enterprise</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-white/5">
                    <td className="p-6 text-white">API Requests</td>
                    <td className="p-6 text-center text-gray-300">1,000/month</td>
                    <td className="p-6 text-center text-gray-300">10,000/month</td>
                    <td className="p-6 text-center text-gray-300">Unlimited</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-6 text-white">Data Processing</td>
                    <td className="p-6 text-center text-gray-300">10K points/month</td>
                    <td className="p-6 text-center text-gray-300">100K points/month</td>
                    <td className="p-6 text-center text-gray-300">Unlimited</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-6 text-white">Support</td>
                    <td className="p-6 text-center text-gray-300">Email</td>
                    <td className="p-6 text-center text-gray-300">Priority</td>
                    <td className="p-6 text-center text-gray-300">24/7 Dedicated</td>
                  </tr>
                  <tr className="border-b border-white/5">
                    <td className="p-6 text-white">SLA</td>
                    <td className="p-6 text-center text-gray-300">99%</td>
                    <td className="p-6 text-center text-gray-300">99.5%</td>
                    <td className="p-6 text-center text-gray-300">99.9%</td>
                  </tr>
                  <tr>
                    <td className="p-6 text-white">Custom AI Models</td>
                    <td className="p-6 text-center text-gray-300">-</td>
                    <td className="p-6 text-center text-gray-300">-</td>
                    <td className="p-6 text-center text-green-400">✓</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.7 }}
          className="text-center"
        >
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl p-12">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Join thousands of developers who are already using our AI-powered platform 
              to build the next generation of applications.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:opacity-90 transition-opacity flex items-center justify-center space-x-2">
                <span>Start Free Trial</span>
                <ArrowRight className="w-5 h-5" />
              </button>
              <button className="border border-white/20 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white/10 transition-colors">
                Contact Sales
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
} 