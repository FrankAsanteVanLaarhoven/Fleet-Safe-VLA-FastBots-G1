import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { gsap } from 'gsap'
import { Brain, Database, Cpu, Network } from 'lucide-react'

export const LoadingScreen: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null)
  const particlesRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || !particlesRef.current) return

    // GSAP animation for floating particles
    const particles = gsap.utils.toArray('.particle')
    
    gsap.set(particles, { 
      opacity: 0, 
      scale: 0,
      rotation: 0 
    })

    gsap.to(particles, {
      opacity: 1,
      scale: 1,
      rotation: 360,
      duration: 1.5,
      stagger: 0.1,
      ease: "back.out(1.7)"
    })

    // Floating animation
    gsap.to(particles, {
      y: -20,
      duration: 2,
      stagger: 0.2,
      repeat: -1,
      yoyo: true,
      ease: "power1.inOut"
    })

    // Pulse animation for the main icon
    gsap.to('.main-icon', {
      scale: 1.1,
      duration: 1.5,
      repeat: -1,
      yoyo: true,
      ease: "power1.inOut"
    })

    // Data flow animation
    gsap.to('.data-flow', {
      x: '100%',
      duration: 2,
      repeat: -1,
      ease: "none"
    })

  }, [])

  return (
    <div 
      ref={containerRef}
      className="fixed inset-0 bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-900 flex items-center justify-center overflow-hidden"
    >
      {/* Animated background particles */}
      <div ref={particlesRef} className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="particle absolute w-2 h-2 bg-white/20 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 2}s`,
            }}
          />
        ))}
      </div>

      {/* Main loading content */}
      <div className="relative z-10 text-center">
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.8, ease: "back.out(1.7)" }}
          className="mb-8"
        >
          <div className="main-icon relative">
            <Brain className="w-24 h-24 text-white mx-auto mb-4" />
            
            {/* Orbiting icons */}
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              className="absolute inset-0"
            >
              <Database className="w-8 h-8 text-primary-300 absolute -top-4 left-1/2 transform -translate-x-1/2" />
              <Cpu className="w-8 h-8 text-secondary-300 absolute top-1/2 -right-4 transform -translate-y-1/2" />
              <Network className="w-8 h-8 text-accent-300 absolute -bottom-4 left-1/2 transform -translate-x-1/2" />
            </motion.div>
          </div>
        </motion.div>

        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="text-4xl font-bold text-white mb-4"
        >
          DataMinerAI
        </motion.h1>

        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="text-lg text-primary-200 mb-8"
        >
          World-Class AI-Powered Data Mining Platform
        </motion.p>

        {/* Loading bar */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "100%" }}
          transition={{ delay: 0.7, duration: 2, ease: "easeInOut" }}
          className="relative w-64 h-2 bg-white/20 rounded-full mx-auto overflow-hidden"
        >
          <div className="data-flow absolute inset-0 bg-gradient-to-r from-transparent via-white/40 to-transparent w-full h-full" />
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="text-sm text-primary-300 mt-4"
        >
          Initializing advanced AI systems...
        </motion.p>

        {/* Feature highlights */}
        <motion.div
          initial={{ y: 30, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 1.2, duration: 0.6 }}
          className="mt-12 grid grid-cols-3 gap-6 max-w-md mx-auto"
        >
          {[
            { icon: Database, label: "Smart Crawling" },
            { icon: Brain, label: "AI Analysis" },
            { icon: Network, label: "Real-time Data" },
          ].map((feature, index) => (
            <motion.div
              key={feature.label}
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 1.4 + index * 0.1, duration: 0.4 }}
              className="text-center"
            >
              <feature.icon className="w-6 h-6 text-primary-300 mx-auto mb-2" />
              <p className="text-xs text-primary-300">{feature.label}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>

      {/* Corner decorations */}
      <div className="absolute top-8 left-8 w-32 h-32 border border-white/10 rounded-full" />
      <div className="absolute bottom-8 right-8 w-24 h-24 border border-white/10 rounded-full" />
      
      {/* Floating data elements */}
      <motion.div
        animate={{ 
          y: [0, -10, 0],
          rotate: [0, 5, 0]
        }}
        transition={{ 
          duration: 3, 
          repeat: Infinity, 
          ease: "easeInOut" 
        }}
        className="absolute top-1/4 right-1/4 text-white/30 text-xs"
      >
        {"{data: 'mining'}"}
      </motion.div>

      <motion.div
        animate={{ 
          y: [0, 10, 0],
          rotate: [0, -5, 0]
        }}
        transition={{ 
          duration: 4, 
          repeat: Infinity, 
          ease: "easeInOut",
          delay: 1
        }}
        className="absolute bottom-1/4 left-1/4 text-white/30 text-xs"
      >
        {"AI.analyze()"}
      </motion.div>
    </div>
  )
}
