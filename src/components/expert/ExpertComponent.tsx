/**
 * Expert Component - Advanced UI component with expert-level animations and styling
 */

import React from 'react';
import { motion } from 'framer-motion';

interface ExpertComponentProps {
  children: React.ReactNode;
  variant?: 'expert' | 'enterprise' | 'premium';
  animationLevel?: 'smooth' | 'immersive' | 'subtle';
  className?: string;
}

export const ExpertComponent: React.FC<ExpertComponentProps> = ({
  children,
  variant = 'expert',
  animationLevel = 'smooth',
  className = ''
}) => {
  const getVariantStyles = () => {
    switch (variant) {
      case 'expert':
        return 'bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 border border-blue-500/20';
      case 'enterprise':
        return 'bg-gradient-to-br from-slate-800 via-gray-800 to-slate-900 border border-slate-600/20';
      case 'premium':
        return 'bg-gradient-to-br from-amber-900 via-yellow-800 to-orange-900 border border-amber-500/20';
      default:
        return 'bg-gradient-to-br from-slate-800 via-gray-800 to-slate-900 border border-slate-600/20';
    }
  };

  const getAnimationProps = () => {
    switch (animationLevel) {
      case 'immersive':
        return {
          initial: { opacity: 0, y: 50 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.8, ease: "easeOut" }
        };
      case 'smooth':
        return {
          initial: { opacity: 0, y: 20 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.5, ease: "easeOut" }
        };
      case 'subtle':
        return {
          initial: { opacity: 0 },
          animate: { opacity: 1 },
          transition: { duration: 0.3 }
        };
      default:
        return {
          initial: { opacity: 0, y: 20 },
          animate: { opacity: 1, y: 0 },
          transition: { duration: 0.5, ease: "easeOut" }
        };
    }
  };

  return (
    <motion.div
      className={`rounded-xl p-6 shadow-2xl backdrop-blur-sm ${getVariantStyles()} ${className}`}
      {...getAnimationProps()}
    >
      {children}
    </motion.div>
  );
};
