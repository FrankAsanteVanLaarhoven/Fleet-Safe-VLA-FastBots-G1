#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Advanced Interview Intelligence System
Real-time audio listening, instant responses, and mobile web interface
Enhanced for Frank's AI/Web3 Frontend Engineer Interview with Anika Bansal
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import requests
from datetime import datetime
import threading
import time
import webbrowser
import os
import speech_recognition as sr
import pyaudio
import wave
import numpy as np
from flask import Flask, render_template, jsonify, request
import queue
import re
from transformers import pipeline
import torch

class AdvancedInterviewAnalyzer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎯 Advanced Interview Intelligence System")
        self.root.geometry("1400x1000")
        self.root.configure(bg='#1a1a1a')
        
        # Interview context from conversation
        self.interview_context = {
            "recruiter": "Anika Bansal",
            "company": "Seed-funded startup (backed by ex-Meta/Amazon leaders)",
            "position": "Lead Front-End Engineer (AI + Web3)",
            "industry": "Web3/Blockchain/AI",
            "location": "Remote/Hybrid",
            "funding": "Seed-funded",
            "backers": "Ex-Meta/Amazon leaders + top Web3 angels",
            "tech_stack": "React + TypeScript, real-time on-chain data",
            "scale": "1,000+ socket events/min",
            "impact": "Founder-level, define patterns, scale design systems",
            "product": "Platform for devs to spin up on-chain apps in minutes"
        }
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Response generation
        self.response_generator = None
        self.try_load_ai_model()
        
        # Web server for mobile interface
        self.web_app = Flask(__name__)
        self.setup_web_routes()
        self.web_thread = None
        self.web_port = 5000
        
        # Current conversation state
        self.current_question = ""
        self.last_response = ""
        self.conversation_history = []
        
        # UI setup
        self.setup_ui()
        
        # Start web server
        self.start_web_server()
        
    def try_load_ai_model(self):
        """Try to load AI model for response generation"""
        try:
            # Use a lightweight model for quick responses
            self.response_generator = pipeline(
                "text-generation",
                model="gpt2",  # Lightweight model
                device=-1  # CPU only for speed
            )
        except Exception as e:
            print(f"AI model not available: {e}")
            self.response_generator = None
            
    def setup_web_routes(self):
        """Setup web routes for mobile interface"""
        @self.web_app.route('/')
        def index():
            return render_template('teleprompter.html')
            
        @self.web_app.route('/api/current_response')
        def get_current_response():
            return jsonify({
                'question': self.current_question,
                'response': self.last_response,
                'timestamp': datetime.now().isoformat()
            })
            
        @self.web_app.route('/api/conversation_history')
        def get_conversation_history():
            return jsonify(self.conversation_history)
            
        @self.web_app.route('/api/next_response')
        def next_response():
            self.next_question()
            return jsonify({
                'question': self.current_question,
                'response': self.last_response
            })
            
    def start_web_server(self):
        """Start web server in background thread"""
        def run_server():
            self.web_app.run(host='0.0.0.0', port=self.web_port, debug=False)
            
        self.web_thread = threading.Thread(target=run_server, daemon=True)
        self.web_thread.start()
        
        # Open mobile interface
        webbrowser.open(f'http://localhost:{self.web_port}')
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#1a1a1a')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=1)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header_frame,
            text="🎯 ADVANCED INTERVIEW INTELLIGENCE SYSTEM",
            font=('Arial', 18, 'bold'),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        title.pack(pady=10)
        
        subtitle = tk.Label(
            header_frame,
            text="Real-time Audio Listening + Mobile Interface - AI/Web3 Role",
            font=('Arial', 12),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        subtitle.pack(pady=(0, 10))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=1)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Audio controls
        audio_frame = tk.Frame(control_frame, bg='#2d2d2d')
        audio_frame.pack(fill='x', padx=10, pady=10)
        
        self.audio_btn = tk.Button(
            audio_frame,
            text="🎤 START AUDIO LISTENING",
            font=('Arial', 12, 'bold'),
            bg='#ff6b35',
            fg='#ffffff',
            command=self.toggle_audio_listening,
            width=25,
            height=2
        )
        self.audio_btn.pack(side='left', padx=10, pady=10)
        
        self.quick_analyze_btn = tk.Button(
            audio_frame,
            text="🚀 QUICK ANALYSIS",
            font=('Arial', 12, 'bold'),
            bg='#00ff88',
            fg='#000000',
            command=self.quick_analysis,
            width=20,
            height=2
        )
        self.quick_analyze_btn.pack(side='left', padx=10, pady=10)
        
        self.mobile_btn = tk.Button(
            audio_frame,
            text="📱 OPEN MOBILE INTERFACE",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            command=self.open_mobile_interface,
            width=25,
            height=2
        )
        self.mobile_btn.pack(side='left', padx=10, pady=10)
        
        # Status indicators
        status_frame = tk.Frame(control_frame, bg='#2d2d2d')
        status_frame.pack(fill='x', padx=10, pady=10)
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready | Mobile Interface: http://localhost:5000",
            font=('Arial', 10),
            bg='#2d2d2d',
            fg='#00ff88'
        )
        self.status_label.pack(side='left')
        
        # Real-time conversation area
        conversation_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=1)
        conversation_frame.pack(fill='x', pady=(0, 10))
        
        conv_label = tk.Label(
            conversation_frame,
            text="🎤 REAL-TIME CONVERSATION MONITORING",
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg='#ffffff'
        )
        conv_label.pack(pady=5)
        
        self.conversation_text = scrolledtext.ScrolledText(
            conversation_frame,
            font=('Consolas', 10),
            bg='#1a1a1a',
            fg='#00ff88',
            height=8,
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.conversation_text.pack(fill='x', padx=10, pady=(0, 10))
        
        # Results area
        results_frame = tk.Frame(main_frame, bg='#2d2d2d', relief='raised', bd=1)
        results_frame.pack(fill='both', expand=True)
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=('Consolas', 11),
            bg='#1a1a1a',
            fg='#00ff88',
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.results_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Add initial content
        self.add_result("🎯 ADVANCED INTERVIEW INTELLIGENCE SYSTEM READY\n")
        self.add_result("=" * 60 + "\n")
        self.add_result("📋 INTERVIEW CONTEXT:\n")
        self.add_result(f"• Recruiter: {self.interview_context['recruiter']}\n")
        self.add_result(f"• Company: {self.interview_context['company']}\n")
        self.add_result(f"• Position: {self.interview_context['position']}\n")
        self.add_result(f"• Tech Stack: {self.interview_context['tech_stack']}\n")
        self.add_result(f"• Scale: {self.interview_context['scale']}\n")
        self.add_result(f"• Impact: {self.interview_context['impact']}\n")
        self.add_result("=" * 60 + "\n")
        self.add_result("🎤 Click 'START AUDIO LISTENING' to begin real-time monitoring\n")
        self.add_result("📱 Mobile interface available at: http://localhost:5000\n")
        self.add_result("🚀 Click 'QUICK ANALYSIS' for comprehensive insights\n")
        
    def toggle_audio_listening(self):
        """Toggle audio listening on/off"""
        if not self.is_listening:
            self.is_listening = True
            self.audio_btn.config(text="🛑 STOP AUDIO LISTENING", bg='#ff4444')
            self.status_label.config(text="Status: Listening to audio...")
            self.add_result("\n🎤 AUDIO LISTENING ACTIVATED!\n")
            self.add_result("=" * 40 + "\n")
            self.add_result("💡 Listening for questions and generating responses...\n")
            self.add_result("📱 Check mobile interface for real-time responses\n")
            self.add_result("=" * 40 + "\n")
            
            # Start audio listening thread
            threading.Thread(target=self.audio_listening_loop, daemon=True).start()
        else:
            self.is_listening = False
            self.audio_btn.config(text="🎤 START AUDIO LISTENING", bg='#ff6b35')
            self.status_label.config(text="Status: Audio listening stopped")
            self.add_result("\n🛑 AUDIO LISTENING STOPPED\n")
            
    def audio_listening_loop(self):
        """Main audio listening loop"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                # Convert speech to text
                text = self.recognizer.recognize_google(audio)
                if text:
                    self.process_speech_input(text)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                print(f"Audio processing error: {e}")
                continue
                
    def process_speech_input(self, text):
        """Process speech input and generate response"""
        # Add to conversation history
        self.conversation_history.append({
            'speaker': 'interviewer',
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Update conversation display
        self.conversation_text.insert(tk.END, f"🎤 Interviewer: {text}\n")
        self.conversation_text.see(tk.END)
        
        # Analyze for questions and generate response
        response = self.generate_response_to_question(text)
        
        if response:
            self.current_question = text
            self.last_response = response
            
            # Add response to conversation history
            self.conversation_history.append({
                'speaker': 'assistant',
                'text': response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update conversation display
            self.conversation_text.insert(tk.END, f"💡 Suggested Response: {response}\n")
            self.conversation_text.insert(tk.END, "-" * 50 + "\n")
            self.conversation_text.see(tk.END)
            
            # Update status
            self.status_label.config(text=f"Status: Response generated for: {text[:50]}...")
            
    def generate_response_to_question(self, question):
        """Generate response based on detected question"""
        question_lower = question.lower()
        
        # Pre-defined response patterns
        response_patterns = {
            'react': "I have extensive experience with React and TypeScript, having built scalable applications handling real-time data. I've led teams in developing complex frontend architectures that can handle thousands of concurrent users and real-time updates.",
            'typescript': "I'm deeply experienced with TypeScript and believe strongly in type safety. I've implemented comprehensive type systems that catch errors at compile time and improve code maintainability.",
            'real-time': "I've worked with WebSocket connections handling 10,000+ concurrent users and implemented efficient state management patterns. Key strategies include connection pooling, message queuing, and optimistic updates.",
            'web3': "I have experience integrating with blockchain APIs, handling wallet connections, and managing on-chain data. I understand the challenges of real-time blockchain data and user experience in Web3 applications.",
            'leadership': "I believe in leading by example through code quality, architecture decisions, and mentoring. I focus on establishing clear patterns, documentation, and knowledge sharing.",
            'team': "I've built and scaled engineering teams, always prioritizing both technical excellence and team growth. I believe in creating an environment where engineers can thrive and grow.",
            'experience': "I have extensive experience in AI/ML, real-time systems, and technical leadership. My background combines deep technical expertise with proven leadership skills.",
            'salary': "I'm looking for a competitive package that reflects the value I can bring to the company. I'm particularly interested in equity given the early-stage nature of the company.",
            'why': "The combination of AI agents, real-time Web3 data, and founder-level impact is incredibly compelling. I'm excited about the technical challenges and the opportunity to define patterns that will shape the platform's future."
        }
        
        # Find matching pattern
        for keyword, response in response_patterns.items():
            if keyword in question_lower:
                return response
                
        # If no pattern matches, use AI model if available
        if self.response_generator:
            try:
                # Generate contextual response
                prompt = f"Interview question: {question}\nContext: AI/Web3 frontend engineer role\nResponse:"
                generated = self.response_generator(prompt, max_length=100, num_return_sequences=1)
                return generated[0]['generated_text'].split('Response:')[-1].strip()
            except:
                pass
                
        # Fallback response
        return "That's a great question. Based on my experience with AI/ML and technical leadership, I would approach this by focusing on scalable solutions and clear communication with stakeholders."
        
    def open_mobile_interface(self):
        """Open mobile interface in browser"""
        webbrowser.open(f'http://localhost:{self.web_port}')
        
    def quick_analysis(self):
        """Perform quick comprehensive analysis"""
        self.add_result("\n🚀 STARTING QUICK INTERVIEW ANALYSIS...\n")
        self.add_result("=" * 60 + "\n")
        
        # Run analysis in separate thread
        threading.Thread(target=self.perform_quick_analysis, daemon=True).start()
        
    def perform_quick_analysis(self):
        """Perform comprehensive quick analysis"""
        try:
            # Company analysis
            self.add_result("🏢 COMPANY ANALYSIS\n")
            self.add_result("-" * 40 + "\n")
            
            company_analysis = self.analyze_company_background()
            
            # Position analysis
            self.add_result("\n💼 POSITION ANALYSIS\n")
            self.add_result("-" * 40 + "\n")
            
            position_analysis = self.analyze_position_details()
            
            # Technical requirements
            self.add_result("\n⚡ TECHNICAL REQUIREMENTS\n")
            self.add_result("-" * 40 + "\n")
            
            tech_analysis = self.analyze_technical_requirements()
            
            # Interview strategy
            self.add_result("\n🎯 INTERVIEW STRATEGY\n")
            self.add_result("-" * 40 + "\n")
            
            strategy_analysis = self.generate_interview_strategy()
            
            # Key talking points
            self.add_result("\n💬 KEY TALKING POINTS\n")
            self.add_result("-" * 40 + "\n")
            
            talking_points = self.generate_talking_points()
            
            # Questions to ask
            self.add_result("\n❓ QUESTIONS TO ASK\n")
            self.add_result("-" * 40 + "\n")
            
            questions = self.generate_questions_to_ask()
            
            # Red flags and concerns
            self.add_result("\n⚠️ RED FLAGS & CONCERNS\n")
            self.add_result("-" * 40 + "\n")
            
            red_flags = self.analyze_red_flags()
            
            # Salary negotiation
            self.add_result("\n💰 SALARY NEGOTIATION\n")
            self.add_result("-" * 40 + "\n")
            
            salary_analysis = self.generate_salary_strategy()
            
            self.add_result("\n✅ ANALYSIS COMPLETE! Audio listening ready.\n")
            
        except Exception as e:
            self.add_result(f"\n❌ Analysis Error: {str(e)}\n")
            
    def analyze_company_background(self):
        """Analyze company background"""
        analysis = {
            "stage": "Seed-funded startup",
            "backers": "Ex-Meta/Amazon leaders + top Web3 angels",
            "size": "10-50 employees (typical seed stage)",
            "culture": "Fast-paced, innovative, founder-driven",
            "risk_level": "High (seed stage startup)",
            "growth_potential": "Very high (backed by strong investors)",
            "stability": "Medium (depends on funding runway)",
            "equity_value": "High potential (early stage equity)"
        }
        
        self.add_result("🏢 COMPANY PROFILE:\n")
        for key, value in analysis.items():
            self.add_result(f"• {key.title()}: {value}\n")
        
        return analysis
        
    def analyze_position_details(self):
        """Analyze position details"""
        analysis = {
            "level": "Lead/Senior level",
            "responsibilities": "Frontend architecture, real-time data handling, AI integration",
            "impact": "Founder-level impact on product and team",
            "growth": "Define patterns, scale systems, hire engineers",
            "ownership": "Own the frontend completely",
            "technical_scope": "React + TypeScript, Web3 integration, AI agents",
            "scale": "1,000+ socket events/min",
            "innovation": "Shape UX for AI agents"
        }
        
        self.add_result("💼 POSITION DETAILS:\n")
        for key, value in analysis.items():
            self.add_result(f"• {key.title()}: {value}\n")
        
        return analysis
        
    def analyze_technical_requirements(self):
        """Analyze technical requirements"""
        requirements = {
            "frontend": "React + TypeScript expertise",
            "real_time": "WebSocket handling, 1,000+ events/min",
            "web3": "Blockchain integration, on-chain data",
            "ai": "AI agent UX design and integration",
            "architecture": "Scalable frontend architecture",
            "performance": "High-performance real-time applications",
            "design_systems": "Design system development and scaling",
            "leadership": "Technical leadership and team building"
        }
        
        self.add_result("⚡ TECHNICAL REQUIREMENTS:\n")
        for key, value in requirements.items():
            self.add_result(f"• {key.title()}: {value}\n")
        
        return requirements
        
    def generate_interview_strategy(self):
        """Generate interview strategy"""
        strategy = {
            "approach": "Confident but humble, emphasize leadership potential",
            "focus_areas": "Technical depth, leadership experience, Web3 knowledge",
            "storytelling": "Use specific examples of technical leadership",
            "questions": "Ask about technical challenges and team growth",
            "red_flags": "Avoid appearing too junior or lacking confidence",
            "strengths": "Emphasize AI/ML background, technical leadership",
            "weaknesses": "Address any gaps in Web3 experience honestly"
        }
        
        self.add_result("🎯 INTERVIEW STRATEGY:\n")
        for key, value in strategy.items():
            self.add_result(f"• {key.title()}: {value}\n")
        
        return strategy
        
    def generate_talking_points(self):
        """Generate key talking points"""
        talking_points = [
            "Your experience with real-time data systems and WebSocket handling",
            "Technical leadership experience and team building",
            "AI/ML background and how it applies to AI agent UX",
            "Experience with React + TypeScript at scale",
            "Understanding of Web3/blockchain technology",
            "Examples of defining technical patterns and architecture",
            "Experience with design systems and UX scaling",
            "Interest in the intersection of AI and Web3",
            "Your approach to mentoring and developing engineers",
            "Experience with high-performance frontend applications"
        ]
        
        self.add_result("💬 KEY TALKING POINTS:\n")
        for i, point in enumerate(talking_points, 1):
            self.add_result(f"{i}. {point}\n")
        
        return talking_points
        
    def generate_questions_to_ask(self):
        """Generate questions to ask"""
        questions = [
            "What are the biggest technical challenges with handling 1,000+ socket events/min?",
            "How do you envision AI agents integrating with the Web3 platform?",
            "What's the current team structure and how do you plan to scale?",
            "What are the most critical technical decisions you need to make in the next 6 months?",
            "How do you handle real-time data consistency across the frontend?",
            "What's your approach to design system scaling and maintenance?",
            "How do you balance rapid development with code quality and architecture?",
            "What's the funding runway and what are the key milestones?",
            "How do you see this role evolving as the company grows?",
            "What's the biggest risk or challenge facing the platform right now?"
        ]
        
        self.add_result("❓ QUESTIONS TO ASK:\n")
        for i, question in enumerate(questions, 1):
            self.add_result(f"{i}. {question}\n")
        
        return questions
        
    def analyze_red_flags(self):
        """Analyze potential red flags"""
        red_flags = [
            "Seed stage startup - high risk of failure",
            "Limited funding runway (need to verify)",
            "High technical complexity with small team",
            "Potential for overwork and burnout",
            "Unclear equity structure and vesting",
            "Limited benefits compared to larger companies",
            "High pressure to deliver quickly",
            "Potential technical debt from rapid development"
        ]
        
        self.add_result("⚠️ RED FLAGS & CONCERNS:\n")
        for i, flag in enumerate(red_flags, 1):
            self.add_result(f"{i}. {flag}\n")
        
        return red_flags
        
    def generate_salary_strategy(self):
        """Generate salary negotiation strategy"""
        strategy = {
            "target_range": "$150K-$180K base + significant equity",
            "equity_importance": "High - early stage equity has high potential",
            "negotiation_points": "Emphasize technical leadership and AI expertise",
            "benefits": "Focus on equity, flexibility, and growth potential",
            "timing": "Wait for offer before discussing specific numbers",
            "leverage": "Your AI/ML background and technical leadership",
            "fallback": "Be prepared to walk away if terms aren't right"
        }
        
        self.add_result("💰 SALARY NEGOTIATION:\n")
        for key, value in strategy.items():
            self.add_result(f"• {key.title()}: {value}\n")
        
        return strategy
        
    def add_result(self, text):
        """Add result to the text area"""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def create_mobile_template():
    """Create mobile web template"""
    template_dir = "templates"
    if not os.path.exists(template_dir):
        os.makedirs(template_dir)
        
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Interview Teleprompter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
            color: #00ff88;
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .status {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 20px;
            text-align: center;
        }
        
        .question-card {
            background: rgba(255, 107, 53, 0.1);
            border: 1px solid #ff6b35;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .question-card h3 {
            color: #ff6b35;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .response-card {
            background: rgba(0, 255, 136, 0.1);
            border: 1px solid #00ff88;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .response-card h3 {
            color: #00ff88;
            margin-bottom: 10px;
            font-size: 18px;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .btn {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .btn-primary {
            background: #00ff88;
            color: #000;
        }
        
        .btn-secondary {
            background: #ff6b35;
            color: #fff;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }
        
        .conversation-history {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            padding: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .conversation-item {
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
        }
        
        .interviewer {
            background: rgba(255, 107, 53, 0.2);
            border-left: 3px solid #ff6b35;
        }
        
        .assistant {
            background: rgba(0, 255, 136, 0.2);
            border-left: 3px solid #00ff88;
        }
        
        .timestamp {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Interview Teleprompter</h1>
            <p>AI/Web3 Frontend Engineer Role</p>
        </div>
        
        <div class="status" id="status">
            <strong>Status:</strong> <span id="statusText">Connecting...</span>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="nextResponse()">⏭️ Next Response</button>
            <button class="btn btn-secondary" onclick="refreshData()">🔄 Refresh</button>
        </div>
        
        <div class="question-card">
            <h3>🎤 Current Question</h3>
            <div id="currentQuestion">Waiting for question...</div>
        </div>
        
        <div class="response-card">
            <h3>💡 Suggested Response</h3>
            <div id="currentResponse">Waiting for response...</div>
        </div>
        
        <div class="conversation-history">
            <h3>📝 Conversation History</h3>
            <div id="conversationHistory">No conversation yet...</div>
        </div>
    </div>
    
    <script>
        let lastUpdate = null;
        
        function updateStatus(text) {
            document.getElementById('statusText').textContent = text;
        }
        
        function updateQuestion(question) {
            document.getElementById('currentQuestion').textContent = question || 'Waiting for question...';
        }
        
        function updateResponse(response) {
            document.getElementById('currentResponse').textContent = response || 'Waiting for response...';
        }
        
        function updateConversationHistory(history) {
            const container = document.getElementById('conversationHistory');
            if (!history || history.length === 0) {
                container.innerHTML = 'No conversation yet...';
                return;
            }
            
            container.innerHTML = history.map(item => `
                <div class="conversation-item ${item.speaker}">
                    <strong>${item.speaker === 'interviewer' ? '🎤 Interviewer' : '💡 Assistant'}:</strong>
                    <div>${item.text}</div>
                    <div class="timestamp">${new Date(item.timestamp).toLocaleTimeString()}</div>
                </div>
            `).join('');
            
            container.scrollTop = container.scrollHeight;
        }
        
        async function fetchData() {
            try {
                const response = await fetch('/api/current_response');
                const data = await response.json();
                
                if (data.timestamp !== lastUpdate) {
                    lastUpdate = data.timestamp;
                    updateQuestion(data.question);
                    updateResponse(data.response);
                    updateStatus('Connected - Real-time updates active');
                }
                
                // Fetch conversation history
                const historyResponse = await fetch('/api/conversation_history');
                const historyData = await historyResponse.json();
                updateConversationHistory(historyData);
                
            } catch (error) {
                updateStatus('Connection error - Retrying...');
                console.error('Error fetching data:', error);
            }
        }
        
        async function nextResponse() {
            try {
                const response = await fetch('/api/next_response');
                const data = await response.json();
                updateQuestion(data.question);
                updateResponse(data.response);
                updateStatus('Manual response requested');
            } catch (error) {
                updateStatus('Error getting next response');
                console.error('Error:', error);
            }
        }
        
        function refreshData() {
            fetchData();
            updateStatus('Manual refresh requested');
        }
        
        // Auto-refresh every 2 seconds
        setInterval(fetchData, 2000);
        
        // Initial load
        fetchData();
    </script>
</body>
</html>
"""
    
    with open(os.path.join(template_dir, "teleprompter.html"), "w") as f:
        f.write(html_content)

def main():
    print("🎯 Iron Cloud Nexus AI - Advanced Interview Intelligence System")
    print("=" * 70)
    print("🎯 Target: AI/Web3 Frontend Engineer Interview")
    print("👤 Recruiter: Anika Bansal (The DATAHEAD)")
    print("🏢 Company: Seed-funded startup (ex-Meta/Amazon backed)")
    print("⚡ Tech: React + TypeScript, Web3, AI agents")
    print("🎤 Features: Real-time audio listening + Mobile interface")
    print("📱 Mobile Interface: http://localhost:5000")
    print("=" * 70)
    print("🚀 Starting Advanced Interview Intelligence System...")
    print("💡 Creating mobile web template...")
    
    # Create mobile template
    create_mobile_template()
    
    print("📱 Mobile interface template created")
    print("🎤 Audio listening system ready")
    print("🌐 Web server starting on port 5000")
    print("=" * 70)
    
    analyzer = AdvancedInterviewAnalyzer()
    analyzer.run()

if __name__ == "__main__":
    main()
