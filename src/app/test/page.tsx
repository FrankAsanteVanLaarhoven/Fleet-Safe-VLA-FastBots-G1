'use client';

import React from 'react';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-white mb-4">
          ✅ Test Page Working!
        </h1>
        <p className="text-gray-300">
          Your Iron Cloud application is running successfully!
        </p>
        <div className="mt-8 space-y-4">
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-white font-semibold">Backend Status</h3>
            <p className="text-green-400">✅ FastAPI running on port 8000</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <h3 className="text-white font-semibold">Frontend Status</h3>
            <p className="text-green-400">✅ Next.js running on port 3000</p>
          </div>
        </div>
      </div>
    </div>
  );
}
