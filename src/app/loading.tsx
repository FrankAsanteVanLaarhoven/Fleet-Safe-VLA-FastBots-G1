import { Loader2, Sparkles } from 'lucide-react';

export default function Loading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <div className="relative">
          <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-6 animate-pulse">
            <Sparkles className="w-10 h-10 text-white" />
          </div>
          <div className="absolute inset-0 w-20 h-20 border-4 border-purple-500/30 rounded-full animate-spin"></div>
        </div>
        
        <h2 className="text-2xl font-bold text-white mb-4">
          Loading AuraAI
        </h2>
        
        <p className="text-gray-300 mb-6">
          Initializing specialized AI agents...
        </p>
        
        <div className="flex items-center justify-center gap-2">
          <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
          <span className="text-purple-400 text-sm">Please wait</span>
        </div>
        
        <div className="mt-8 space-y-2">
          <div className="flex items-center gap-3 text-sm text-gray-400">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            <span>Neural Stealth Engine</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-400">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <span>Universal Crawler</span>
          </div>
          <div className="flex items-center gap-3 text-sm text-gray-400">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse"></div>
            <span>AI Prompt Generator</span>
          </div>
        </div>
      </div>
    </div>
  );
} 