'use client';

import { motion } from 'framer-motion';
import { 
  Brain, 
  Shield, 
  Globe, 
  Database, 
  Lock, 
  Target, 
  Cpu, 
  Sparkles,
  Users,
  Award,
  TrendingUp,
  Zap,
  ArrowRight,
  Star,
  CheckCircle,
  Lightbulb,
  Rocket,
  Heart
} from 'lucide-react';

export default function AboutPage() {
  const values = [
    {
      icon: Brain,
      title: 'Innovation',
      description: 'Pushing the boundaries of AI technology with cutting-edge research and development',
      color: 'from-purple-500 to-pink-500'
    },
    {
      icon: Shield,
      title: 'Security',
      description: 'Military-grade protection ensuring your data and applications are always secure',
      color: 'from-blue-500 to-cyan-500'
    },
    {
      icon: Users,
      title: 'Community',
      description: 'Building a global community of developers and AI enthusiasts',
      color: 'from-green-500 to-emerald-500'
    },
    {
      icon: Zap,
      title: 'Performance',
      description: 'Lightning-fast AI processing with sub-millisecond response times',
      color: 'from-orange-500 to-red-500'
    }
  ];

  const team = [
    {
      name: 'Dr. Sarah Chen',
      role: 'Chief AI Officer',
      bio: 'Former Google AI researcher with 15+ years in machine learning and neural networks',
      avatar: '/images/team/sarah.jpg',
      expertise: ['Neural Networks', 'Deep Learning', 'AI Ethics']
    },
    {
      name: 'Marcus Rodriguez',
      role: 'Chief Technology Officer',
      bio: 'Ex-Netflix engineering leader specializing in scalable AI infrastructure',
      avatar: '/images/team/marcus.jpg',
      expertise: ['Distributed Systems', 'Cloud Architecture', 'DevOps']
    },
    {
      name: 'Dr. Emily Watson',
      role: 'Head of Security',
      bio: 'Cybersecurity expert with background in quantum-resistant encryption',
      avatar: '/images/team/emily.jpg',
      expertise: ['Quantum Security', 'Threat Detection', 'Zero-Day Research']
    },
    {
      name: 'Alex Kim',
      role: 'VP of Engineering',
      bio: 'Former SpaceX engineer focused on autonomous systems and robotics',
      avatar: '/images/team/alex.jpg',
      expertise: ['Autonomous Systems', 'Robotics', 'Real-time Processing']
    }
  ];

  const milestones = [
    {
      year: '2024',
      title: 'AuraAI Platform Launch',
      description: 'Released our comprehensive AI development platform with 6 specialized agents'
    },
    {
      year: '2023',
      title: 'Quantum Security Breakthrough',
      description: 'Developed quantum-resistant TLS engine for future-proof security'
    },
    {
      year: '2022',
      title: 'Neural Stealth Engine',
      description: 'Created AI-powered protection bypass system with 99.9% success rate'
    },
    {
      year: '2021',
      title: 'Company Founded',
      description: 'Started with a vision to democratize advanced AI capabilities'
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-md border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-white">About AuraAI</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity">
                <span>Join Our Team</span>
                <ArrowRight className="w-4 h-4" />
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
          <h2 className="text-4xl md:text-6xl font-bold text-white mb-6">
            Building the Future of
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              {" "}AI Development
            </span>
          </h2>
          <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto mb-8">
            We're on a mission to democratize advanced AI capabilities, making cutting-edge 
            artificial intelligence accessible to developers and businesses worldwide.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <div className="flex items-center space-x-2 text-gray-300">
              <Users className="w-5 h-5" />
              <span>50,000+ Developers</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-300">
              <Award className="w-5 h-5" />
              <span>99.9% Uptime</span>
            </div>
            <div className="flex items-center space-x-2 text-gray-300">
              <TrendingUp className="w-5 h-5" />
              <span>10M+ API Calls</span>
            </div>
          </div>
        </motion.div>

        {/* Story Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="mb-16"
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-3xl font-bold text-white mb-6">Our Story</h3>
              <div className="space-y-4 text-gray-300">
                <p>
                  Founded in 2021 by a team of AI researchers and engineers from leading tech companies, 
                  AuraAI was born from a simple observation: while AI technology was advancing rapidly, 
                  the tools to build and deploy AI applications remained complex and inaccessible.
                </p>
                <p>
                  We set out to change that by creating a comprehensive platform that combines 
                  cutting-edge AI research with practical, developer-friendly tools. Our team of 
                  experts in machine learning, cybersecurity, and distributed systems worked 
                  tirelessly to build something truly revolutionary.
                </p>
                <p>
                  Today, AuraAI powers thousands of applications worldwide, from startups to 
                  Fortune 500 companies, helping developers build the next generation of 
                  AI-powered solutions.
                </p>
              </div>
            </div>
            <div className="bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-2xl p-8">
              <div className="text-center">
                <Sparkles className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                <h4 className="text-2xl font-bold text-white mb-4">Our Mission</h4>
                <p className="text-gray-300 mb-6">
                  To democratize advanced AI capabilities and empower developers to build 
                  the future of intelligent applications.
                </p>
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-green-400">6</div>
                    <div className="text-sm text-gray-400">AI Agents</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-blue-400">99.9%</div>
                    <div className="text-sm text-gray-400">Success Rate</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Values Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="mb-16"
        >
          <h3 className="text-3xl font-bold text-white text-center mb-12">Our Values</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.5 + index * 0.1 }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 text-center hover:bg-white/10 transition-all duration-300"
              >
                <div className={`w-12 h-12 bg-gradient-to-r ${value.color} rounded-lg flex items-center justify-center mx-auto mb-4`}>
                  <value.icon className="w-6 h-6 text-white" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-3">{value.title}</h4>
                <p className="text-gray-300 text-sm">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Team Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6 }}
          className="mb-16"
        >
          <h3 className="text-3xl font-bold text-white text-center mb-12">Meet Our Team</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {team.map((member, index) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.7 + index * 0.1 }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 text-center hover:bg-white/10 transition-all duration-300"
              >
                <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Users className="w-10 h-10 text-white" />
                </div>
                <h4 className="text-xl font-semibold text-white mb-2">{member.name}</h4>
                <p className="text-purple-400 font-medium mb-3">{member.role}</p>
                <p className="text-gray-300 text-sm mb-4">{member.bio}</p>
                <div className="space-y-2">
                  {member.expertise.map((skill, skillIndex) => (
                    <div key={skillIndex} className="flex items-center space-x-2">
                      <CheckCircle className="w-4 h-4 text-green-400" />
                      <span className="text-xs text-gray-400">{skill}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Milestones Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mb-16"
        >
          <h3 className="text-3xl font-bold text-white text-center mb-12">Our Journey</h3>
          <div className="relative">
            <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gradient-to-b from-purple-500 to-pink-500"></div>
            <div className="space-y-8">
              {milestones.map((milestone, index) => (
                <motion.div
                  key={milestone.year}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.8, delay: 0.9 + index * 0.1 }}
                  className={`flex items-center ${index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'}`}
                >
                  <div className="w-1/2 flex justify-center">
                    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 max-w-sm">
                      <div className="text-2xl font-bold text-purple-400 mb-2">{milestone.year}</div>
                      <h4 className="text-lg font-semibold text-white mb-2">{milestone.title}</h4>
                      <p className="text-gray-300 text-sm">{milestone.description}</p>
                    </div>
                  </div>
                  <div className="w-4 h-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full border-4 border-slate-900"></div>
                  <div className="w-1/2"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.0 }}
          className="text-center"
        >
          <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-2xl p-12">
            <h3 className="text-3xl font-bold text-white mb-4">
              Join Us in Building the Future
            </h3>
            <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
              Whether you're a developer looking to build amazing AI applications or a company 
              seeking to transform your business with AI, we're here to help.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-purple-500 to-pink-500 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:opacity-90 transition-opacity flex items-center justify-center space-x-2">
                <Rocket className="w-5 h-5" />
                <span>Start Building</span>
              </button>
              <button className="border border-white/20 text-white px-8 py-4 rounded-lg text-lg font-semibold hover:bg-white/10 transition-colors flex items-center justify-center space-x-2">
                <Heart className="w-5 h-5" />
                <span>Join Our Team</span>
              </button>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
} 