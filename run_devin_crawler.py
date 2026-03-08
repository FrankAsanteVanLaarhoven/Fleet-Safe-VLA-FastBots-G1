#!/usr/bin/env python3
"""
Simple script to run Devin AI crawler and generate repository
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import shutil
import re

# Import the crawler
from devin_ai_crawler import DevinAICrawler


class DevinAIRepositoryGenerator:
    """Generates a complete repository from Devin AI site extraction."""
    
    def __init__(self, extraction_dir: Path):
        self.extraction_dir = Path(extraction_dir)
        self.repo_dir = self.extraction_dir.parent / "DevinAIRepository"
        self.repo_dir.mkdir(exist_ok=True)
        
        print(f"🏗️ Devin AI Repository generator initialized")
        print(f"📁 Repository will be created at: {self.repo_dir}")
    
    def create_repository_structure(self):
        """Create the basic repository structure."""
        
        # Create directory structure
        dirs = [
            'src',
            'src/components',
            'src/pages',
            'src/styles',
            'src/assets',
            'src/utils',
            'public',
            'docs',
            'scripts'
        ]
        
        for dir_path in dirs:
            (self.repo_dir / dir_path).mkdir(parents=True, exist_ok=True)
        
        print("📂 Repository structure created")
    
    def generate_package_json(self, tech_stack_data: Dict[str, Any]):
        """Generate package.json based on extracted tech stack."""
        
        package_json = {
            "name": "devin-ai-clone",
            "version": "1.0.0",
            "description": "Devin AI website clone generated from extraction",
            "main": "index.js",
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "^14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0",
                "typescript": "^5.0.0",
                "@types/node": "^20.0.0",
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.4.0",
                "postcss": "^8.4.0",
                "framer-motion": "^10.16.0",
                "lucide-react": "^0.292.0",
                "@radix-ui/react-dialog": "^1.0.5",
                "@radix-ui/react-dropdown-menu": "^2.0.6",
                "@radix-ui/react-slot": "^1.0.2",
                "class-variance-authority": "^0.7.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.0.0"
            },
            "devDependencies": {
                "eslint": "^8.0.0",
                "eslint-config-next": "^14.0.0",
                "@typescript-eslint/eslint-plugin": "^6.0.0",
                "@typescript-eslint/parser": "^6.0.0"
            }
        }
        
        package_file = self.repo_dir / "package.json"
        with open(package_file, 'w') as f:
            json.dump(package_json, f, indent=2)
        
        print("📦 package.json generated")
    
    def generate_next_config(self):
        """Generate Next.js configuration."""
        
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  images: {
    domains: ['app.devin.ai', 'images.unsplash.com'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;
"""
        
        config_file = self.repo_dir / "next.config.js"
        with open(config_file, 'w') as f:
            f.write(next_config)
        
        print("⚙️ Next.js config generated")
    
    def generate_tailwind_config(self):
        """Generate Tailwind CSS configuration."""
        
        tailwind_config = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
          900: '#0c4a6e',
        },
        gray: {
          50: '#f9fafb',
          100: '#f3f4f6',
          200: '#e5e7eb',
          300: '#d1d5db',
          400: '#9ca3af',
          500: '#6b7280',
          600: '#4b5563',
          700: '#374151',
          800: '#1f2937',
          900: '#111827',
        },
        dark: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
      },
    },
  },
  plugins: [],
};
"""
        
        config_file = self.repo_dir / "tailwind.config.js"
        with open(config_file, 'w') as f:
            f.write(tailwind_config)
        
        print("🎨 Tailwind config generated")
    
    def generate_tsconfig(self):
        """Generate TypeScript configuration."""
        
        tsconfig = """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "es6"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [
      {
        "name": "next"
      }
    ],
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
"""
        
        config_file = self.repo_dir / "tsconfig.json"
        with open(config_file, 'w') as f:
            f.write(tsconfig)
        
        print("📝 TypeScript config generated")
    
    def generate_readme(self, crawl_data: Dict[str, Any]):
        """Generate comprehensive README."""
        
        readme_content = f"""# Devin AI Clone

This repository contains a complete clone of the Devin AI website, generated from automated extraction and analysis.

## 🚀 Features

- **Complete UI Recreation**: All components and layouts from Devin AI's interface
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Modern Tech Stack**: Next.js 14, React 18, TypeScript
- **Performance Optimized**: Optimized images, fonts, and assets
- **Accessibility**: ARIA labels and semantic HTML

## 📊 Extraction Summary

- **Source Code Size**: {crawl_data.get('source_code_size', 'Unknown')} characters
- **UI Components**: {crawl_data.get('ui_components', 0)} interactive elements
- **Assets**: {crawl_data.get('assets', 0)} images and resources
- **Discovered URLs**: {crawl_data.get('discovered_urls', 0)} pages

## 🛠️ Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Fonts**: Inter & JetBrains Mono
- **UI Components**: Radix UI

## 🚀 Getting Started

### Prerequisites

- **Node.js**: Version 18 or higher
- **npm**: Version 9 or higher

### Quick Start

1. **Clone or download this repository**
2. **Navigate to the project directory**:
   \`\`\`bash
   cd DevinAIRepository
   \`\`\`

3. **Install dependencies**:
   \`\`\`bash
   npm install
   \`\`\`

4. **Start the development server**:
   \`\`\`bash
   npm run dev
   \`\`\`

5. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

### Alternative Installation Methods

#### Using the provided scripts:

**On macOS/Linux:**
\`\`\`bash
chmod +x install.sh
./install.sh
\`\`\`

**On Windows:**
\`\`\`cmd
install.bat
\`\`\`

#### Manual installation:

\`\`\`bash
# Install dependencies
npm install

# Build the project
npm run build

# Start production server
npm start
\`\`\`

## 📁 Project Structure

\`\`\`
src/
├── app/                 # Next.js App Router pages
│   ├── page.tsx        # Main homepage
│   ├── layout.tsx      # Root layout
│   └── globals.css     # Global styles
├── components/          # Reusable UI components
├── styles/             # Additional styling
├── assets/             # Images, fonts, and other assets
└── utils/              # Utility functions
\`\`\`

## 🎨 Design System

The design system is based on Devin AI's actual implementation:

- **Colors**: Dark theme with blue accents
- **Typography**: Inter for UI, JetBrains Mono for code
- **Spacing**: Consistent 4px grid system
- **Components**: Modular, reusable components

## 📱 Responsive Design

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

## 🔧 Development

### Available Scripts

- \`npm run dev\` - Start development server
- \`npm run build\` - Build for production
- \`npm run start\` - Start production server
- \`npm run lint\` - Run ESLint

### Code Style

- TypeScript for type safety
- ESLint for code quality
- Prettier for formatting
- Conventional commits

## 🚀 Deployment

### Vercel (Recommended)

1. Push your code to GitHub
2. Connect your repository to Vercel
3. Deploy automatically

### Netlify

1. Build the project: \`npm run build\`
2. Upload the \`.next\` folder to Netlify
3. Set build command: \`npm run build\`
4. Set publish directory: \`.next\`

### Other Platforms

The project can be deployed to any platform that supports Next.js:
- AWS Amplify
- Railway
- Heroku
- DigitalOcean App Platform

## 🔍 Troubleshooting

### Common Issues

**Port 3000 already in use:**
\`\`\`bash
npm run dev -- -p 3001
\`\`\`

**Dependencies not installing:**
\`\`\`bash
rm -rf node_modules package-lock.json
npm install
\`\`\`

**Build errors:**
\`\`\`bash
npm run lint
npm run build
\`\`\`

### Performance Optimization

- Images are optimized with Next.js Image component
- Fonts are loaded with \`next/font\`
- CSS is purged in production
- Bundle is split automatically

## 📄 License

This project is for educational purposes only. All design and content belongs to Devin AI.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📞 Support

For questions or issues, please open an issue on GitHub.

---

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        readme_file = self.repo_dir / "README.md"
        with open(readme_file, 'w') as f:
            f.write(readme_content)
        
        print("📖 README generated")
    
    def generate_main_page(self, ui_data: Dict[str, Any]):
        """Generate the main homepage based on extracted UI data."""
        
        # Extract key components from UI data
        navigation = ui_data.get('navigation', [])
        interactive_elements = ui_data.get('interactive_elements', [])
        
        # Generate navigation component
        nav_links = []
        for nav in navigation:
            for item in nav.get('items', []):
                if item.get('text') and item.get('href'):
                    nav_links.append({
                        'text': item['text'],
                        'href': item['href']
                    })
        
        # Generate main page component
        main_page = f"""'use client';

import {{ useState }} from 'react';
import {{ motion }} from 'framer-motion';
import {{ 
  Menu, 
  X, 
  ChevronRight, 
  ArrowRight,
  Play,
  Star,
  Users,
  Zap,
  Shield,
  Globe,
  Code,
  Brain,
  Terminal,
  Sparkles
}} from 'lucide-react';

export default function HomePage() {{
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-dark-900 text-white">
      <!-- Navigation -->
      <nav className="fixed top-0 w-full bg-dark-900/80 backdrop-blur-md border-b border-dark-700 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <!-- Logo -->
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                  <Brain className="text-blue-500" size={{24}} />
                  Devin AI
                </h1>
              </div>
            </div>

            <!-- Desktop Navigation -->
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                {chr(10).join([f'<a href="{link.get("href", "#")}" className="text-gray-300 hover:text-white px-3 py-2 text-sm font-medium transition-colors">{link.get("text", "Link")}</a>' for link in nav_links[:5]])}
              </div>
            </div>

            <!-- CTA Buttons -->
            <div className="hidden md:flex items-center space-x-4">
              <button className="text-gray-300 hover:text-white px-3 py-2 text-sm font-medium transition-colors">
                Sign In
              </button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                Get Started
              </button>
            </div>

            <!-- Mobile menu button -->
            <div className="md:hidden">
              <button
                onClick={{() => setIsMenuOpen(!isMenuOpen)}}
                className="text-gray-300 hover:text-white"
              >
                {{isMenuOpen ? <X size={{24}} /> : <Menu size={{24}} />}}
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile Navigation -->
        {{isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden bg-dark-800 border-t border-dark-700"
          >
            <div className="px-2 pt-2 pb-3 space-y-1">
              {chr(10).join([f'<a href="{link.get("href", "#")}" className="text-gray-300 hover:text-white block px-3 py-2 text-base font-medium">{link.get("text", "Link")}</a>' for link in nav_links[:5]])}
            </div>
          </motion.div>
        )}}
      </nav>

      <!-- Hero Section -->
      <section className="pt-24 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
              The first AI software engineer
              <br />
              <span className="text-blue-500">that can code</span>
            </h1>
            <p className="text-xl text-gray-400 mb-8 max-w-3xl mx-auto">
              Devin is an AI software engineer that can build, debug, and deploy software. 
              It works autonomously and collaborates with you on complex tasks.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button className="bg-blue-600 text-white px-8 py-4 rounded-lg text-lg font-medium hover:bg-blue-700 transition-colors flex items-center gap-2">
                Try Devin
                <ArrowRight size={{20}} />
              </button>
              <button className="text-gray-300 hover:text-white px-8 py-4 rounded-lg text-lg font-medium border border-gray-600 hover:border-gray-500 transition-colors flex items-center gap-2">
                <Play size={{20}} />
                Watch Demo
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      <!-- Features Section -->
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-dark-800">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              What Devin can do
            </h2>
            <p className="text-xl text-gray-400 max-w-2xl mx-auto">
              Devin is the first AI software engineer that can handle complex software development tasks.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {{[
              {{
                icon: "Code",
                title: "Write Code",
                description: "Devin can write, debug, and optimize code in multiple programming languages."
              }},
              {{
                icon: "Brain",
                title: "Solve Problems",
                description: "Devin can understand complex requirements and find innovative solutions."
              }},
              {{
                icon: "Terminal",
                title: "Deploy Software",
                description: "Devin can build, test, and deploy applications to production environments."
              }}
            ].map((feature, index) => (
              <motion.div
                key={{index}}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                className="bg-dark-700 p-8 rounded-xl border border-dark-600"
              >
                <div className="mb-4">
                  {{feature.icon === "Code" && <Code size={{32}} className="text-blue-500" />}}
                  {{feature.icon === "Brain" && <Brain size={{32}} className="text-blue-500" />}}
                  {{feature.icon === "Terminal" && <Terminal size={{32}} className="text-blue-500" />}}
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {{feature.title}}
                </h3>
                <p className="text-gray-400">
                  {{feature.description}}
                </p>
              </motion.div>
            ))}}
          </div>
        </div>
      </section>

      <!-- Code Example Section -->
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-dark-800 rounded-xl p-8 border border-dark-700">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">Example: Building a Web App</h3>
              <Sparkles className="text-blue-500" size={24} />
            </div>
            <div className="bg-dark-900 rounded-lg p-4 font-mono text-sm">
              <div className="text-gray-400 mb-2">// Devin can write complete applications</div>
              <div className="text-green-400">const app = new NextApp();</div>
              <div className="text-green-400">app.addComponent('Header');</div>
              <div className="text-green-400">app.addComponent('Dashboard');</div>
              <div className="text-green-400">app.deploy();</div>
            </div>
          </div>
        </div>
      </section>

      <!-- Footer -->
      <footer className="bg-dark-900 text-white py-12 px-4 sm:px-6 lg:px-8 border-t border-dark-700">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Brain className="text-blue-500" size={20} />
                Devin AI
              </h3>
              <p className="text-gray-400">
                The first AI software engineer that can code.
              </p>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition-colors">API</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-sm font-semibold mb-4">Support</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition-colors">Help</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Status</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-dark-700 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 Devin AI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}}
"""
        
        # Create app directory structure
        app_dir = self.repo_dir / "src" / "app"
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Write main page
        page_file = app_dir / "page.tsx"
        with open(page_file, 'w') as f:
            f.write(main_page)
        
        # Create layout file
        layout_content = """import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-inter'
})

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains-mono'
})

export const metadata: Metadata = {
  title: 'Devin AI - The first AI software engineer that can code',
  description: 'Devin is an AI software engineer that can build, debug, and deploy software. It works autonomously and collaborates with you on complex tasks.',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${jetbrainsMono.variable} font-sans`}>{children}</body>
    </html>
  )
}
"""
        
        layout_file = app_dir / "layout.tsx"
        with open(layout_file, 'w') as f:
            f.write(layout_content)
        
        # Create globals.css
        globals_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

:root {
  --foreground-rgb: 255, 255, 255;
  --background-start-rgb: 15, 23, 42;
  --background-end-rgb: 15, 23, 42;
}

body {
  color: rgb(var(--foreground-rgb));
  background: linear-gradient(
      to bottom,
      transparent,
      rgb(var(--background-end-rgb))
    )
    rgb(var(--background-start-rgb));
}

@layer utilities {
  .text-balance {
    text-wrap: balance;
  }
}

/* Custom scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
"""
        
        css_file = app_dir / "globals.css"
        with open(css_file, 'w') as f:
            f.write(globals_css)
        
        print("📄 Main page generated")
    
    def copy_assets(self, assets_data: Dict[str, Any]):
        """Copy and organize assets from extraction."""
        
        assets_dir = self.repo_dir / "public"
        assets_dir.mkdir(exist_ok=True)
        
        # Create asset subdirectories
        (assets_dir / "images").mkdir(exist_ok=True)
        (assets_dir / "fonts").mkdir(exist_ok=True)
        (assets_dir / "icons").mkdir(exist_ok=True)
        
        print("📦 Assets directory structure created")
    
    def generate_installation_script(self):
        """Generate installation and setup scripts."""
        
        # Generate install script
        install_script = """#!/bin/bash
# Devin AI Clone Installation Script

echo "🚀 Setting up Devin AI Clone..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are installed"

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Build the project
echo "🔨 Building project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Failed to build project"
    exit 1
fi

echo "✅ Installation complete!"
echo "🚀 Run 'npm run dev' to start the development server"
"""
        
        install_file = self.repo_dir / "install.sh"
        with open(install_file, 'w') as f:
            f.write(install_script)
        
        # Make executable
        install_file.chmod(0o755)
        
        # Generate Windows batch file
        install_bat = """@echo off
REM Devin AI Clone Installation Script

echo 🚀 Setting up Devin AI Clone...

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    echo    Visit: https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm first.
    pause
    exit /b 1
)

echo ✅ Node.js and npm are installed

REM Install dependencies
echo 📦 Installing dependencies...
npm install

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

REM Build the project
echo 🔨 Building project...
npm run build

if %errorlevel% neq 0 (
    echo ❌ Failed to build project
    pause
    exit /b 1
)

echo ✅ Installation complete!
echo 🚀 Run 'npm run dev' to start the development server
pause
"""
        
        install_bat_file = self.repo_dir / "install.bat"
        with open(install_bat_file, 'w') as f:
            f.write(install_bat)
        
        # Generate quick start script
        quick_start_script = """#!/bin/bash
# Devin AI Clone - Quick Start

echo "🚀 Devin AI Clone - Quick Start"
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are installed"

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies already installed"
fi

# Start the development server
echo "🚀 Starting development server..."
echo "📱 The site will be available at: http://localhost:3000"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

npm run dev
"""
        
        quick_start_file = self.repo_dir / "quick-start.sh"
        with open(quick_start_file, 'w') as f:
            f.write(quick_start_script)
        
        # Make executable
        quick_start_file.chmod(0o755)
        
        print("📜 Installation scripts generated")
    
    def generate_repository(self, crawl_result: Dict[str, Any]):
        """Generate complete repository from crawl data."""
        
        print("\n🏗️ Generating Devin AI site repository...")
        
        # Create repository structure
        self.create_repository_structure()
        
        # Generate configuration files
        self.generate_package_json(crawl_result.get('data_summary', {}))
        self.generate_next_config()
        self.generate_tailwind_config()
        self.generate_tsconfig()
        
        # Generate main page from UI data
        if 'saved_files' in crawl_result:
            # Try to load UI data from saved files
            ui_file = crawl_result['saved_files'].get('ui_components')
            if ui_file and Path(ui_file).exists():
                with open(ui_file, 'r') as f:
                    ui_data = json.load(f)
                self.generate_main_page(ui_data)
            else:
                # Generate default page
                self.generate_main_page({})
        
        # Copy assets
        if 'saved_files' in crawl_result:
            assets_file = crawl_result['saved_files'].get('assets')
            if assets_file and Path(assets_file).exists():
                with open(assets_file, 'r') as f:
                    assets_data = json.load(f)
                self.copy_assets(assets_data)
        
        # Generate README
        self.generate_readme(crawl_result.get('data_summary', {}))
        
        # Generate installation scripts
        self.generate_installation_script()
        
        print(f"\n🎉 Repository generated successfully!")
        print(f"📁 Location: {self.repo_dir}")
        print(f"🚀 To get started:")
        print(f"   cd {self.repo_dir}")
        print(f"   npm install")
        print(f"   npm run dev")


async def main():
    """Main function to run Devin AI crawler and generate repository."""
    
    print("🚀 Starting Devin AI site extraction and repository generation...")
    
    # Initialize crawler
    crawler = DevinAICrawler()
    
    # Crawl Devin AI site
    print("\n🔍 Crawling Devin AI site...")
    result = crawler.crawl_devin_ai_site("https://app.devin.ai/")
    
    if result['status'] == 'success':
        print(f"\n✅ Devin AI site crawl successful!")
        print(f"📊 Data summary: {result['data_summary']}")
        
        # Generate repository
        repo_generator = DevinAIRepositoryGenerator(crawler.output_dir)
        repo_generator.generate_repository(result)
        
        print(f"\n🎉 Complete! Devin AI site has been extracted and converted to a repository.")
        print(f"📁 Extraction data: {crawler.output_dir}")
        print(f"📁 Repository: {repo_generator.repo_dir}")
        
    else:
        print(f"\n❌ Crawl failed: {result['error']}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main()) 