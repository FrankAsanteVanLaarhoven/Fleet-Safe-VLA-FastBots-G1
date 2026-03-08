#!/usr/bin/env python3
"""
Web-Only Interview Teleprompter
Real-time audio listening and mobile interface for interview assistance
"""
import json
import requests
from datetime import datetime
import threading
import time
import webbrowser
import os
import speech_recognition as sr
import pyaudio
import queue
import re
from flask import Flask, render_template, jsonify, request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebInterviewTeleprompter:
    def __init__(self):
        # Interview context
        self.interview_context = {
            "recruiter": "Anika Bansal",
            "company": "Seed-funded startup (backed by ex-Meta/Amazon leaders)",
            "position": "Lead Front-End Engineer (AI + Web3)",
            "tech_stack": "React + TypeScript, real-time on-chain data",
            "scale": "1,000+ socket events/min",
            "impact": "Founder-level, define patterns, scale design systems"
        }
        
        # Audio processing
        self.audio_queue = queue.Queue()
        self.is_listening = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Current conversation state
        self.current_question = ""
        self.last_response = ""
        self.conversation_history = []
        self.current_question_index = 0
        
        # Pre-defined Q&A pairs
        self.qa_pairs = [
            {
                "question": "Tell me about your experience with React and TypeScript",
                "response": "I have extensive experience with React and TypeScript, having built scalable applications handling real-time data. I've led teams in developing complex frontend architectures that can handle thousands of concurrent users and real-time updates. My approach focuses on type safety, performance optimization, and maintainable code patterns."
            },
            {
                "question": "How do you handle real-time data at scale?",
                "response": "I've worked with WebSocket connections handling 10,000+ concurrent users and implemented efficient state management patterns. Key strategies include connection pooling, message queuing, optimistic updates, and intelligent reconnection logic. I also focus on performance monitoring and graceful degradation."
            },
            {
                "question": "What's your experience with Web3 and blockchain?",
                "response": "I have experience integrating with blockchain APIs, handling wallet connections, and managing on-chain data. I understand the challenges of real-time blockchain data, transaction states, and user experience in Web3 applications. I'm particularly interested in the intersection of AI and Web3."
            },
            {
                "question": "How do you approach technical leadership?",
                "response": "I believe in leading by example through code quality, architecture decisions, and mentoring. I focus on establishing clear patterns, documentation, and knowledge sharing. I've built and scaled engineering teams, always prioritizing both technical excellence and team growth."
            },
            {
                "question": "What interests you about this role?",
                "response": "The combination of AI agents, real-time Web3 data, and founder-level impact is incredibly compelling. I'm excited about the technical challenges of scaling to 1,000+ socket events per minute and the opportunity to define patterns that will shape the platform's future. The backing from ex-Meta/Amazon leaders shows strong validation."
            },
            {
                "question": "How do you handle rapid development vs. code quality?",
                "response": "I believe in sustainable development practices. I establish clear patterns early, use automated testing, and maintain technical debt awareness. For rapid development, I focus on building the right abstractions and maintaining flexibility while ensuring we can scale and maintain the codebase."
            },
            {
                "question": "What questions do you have for us?",
                "response": "I'd love to understand the technical challenges you're facing with the 1,000+ socket events per minute. How do you envision AI agents integrating with the platform? What's the current team structure and how do you plan to scale? What are the biggest technical decisions you need to make in the next 6 months?"
            }
        ]
        
        # Web server setup
        self.app = Flask(__name__)
        self.setup_routes()
        self.web_port = 8080
        
        # Start web server
        self.start_web_server()
        
    def setup_routes(self):
        """Setup web routes"""
        @self.app.route('/')
        def index():
            return render_template('teleprompter.html')
            
        @self.app.route('/api/current_response')
        def get_current_response():
            return jsonify({
                'question': self.current_question,
                'response': self.last_response,
                'timestamp': datetime.now().isoformat()
            })
            
        @self.app.route('/api/conversation_history')
        def get_conversation_history():
            return jsonify(self.conversation_history)
            
        @self.app.route('/api/next_response')
        def next_response():
            self.next_question()
            return jsonify({
                'question': self.current_question,
                'response': self.last_response
            })
            
        @self.app.route('/api/start_listening')
        def start_listening():
            if not self.is_listening:
                self.is_listening = True
                threading.Thread(target=self.audio_listening_loop, daemon=True).start()
                return jsonify({'status': 'started', 'message': 'Audio listening started'})
            return jsonify({'status': 'already_running', 'message': 'Already listening'})
            
        @self.app.route('/api/stop_listening')
        def stop_listening():
            self.is_listening = False
            return jsonify({'status': 'stopped', 'message': 'Audio listening stopped'})
            
        @self.app.route('/api/status')
        def get_status():
            return jsonify({
                'is_listening': self.is_listening,
                'conversation_count': len(self.conversation_history),
                'current_question': self.current_question
            })
            
    def start_web_server(self):
        """Start web server"""
        def run_server():
            logger.info(f"Starting web server on port {self.web_port}")
            self.app.run(host='0.0.0.0', port=self.web_port, debug=False)
            
        self.web_thread = threading.Thread(target=run_server, daemon=True)
        self.web_thread.start()
        
        # Wait a moment for server to start
        time.sleep(2)
        
        # Open mobile interface
        try:
            webbrowser.open(f'http://localhost:{self.web_port}')
            logger.info(f"Mobile interface opened at http://localhost:{self.web_port}")
        except Exception as e:
            logger.error(f"Could not open browser: {e}")
            
    def audio_listening_loop(self):
        """Main audio listening loop"""
        logger.info("Starting audio listening loop")
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
                logger.info("Microphone calibrated for ambient noise")
        except Exception as e:
            logger.error(f"Error setting up microphone: {e}")
            return
            
        while self.is_listening:
            try:
                with self.microphone as source:
                    logger.info("Listening for speech...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                # Convert speech to text
                text = self.recognizer.recognize_google(audio)
                if text:
                    logger.info(f"Detected speech: {text}")
                    self.process_speech_input(text)
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception as e:
                logger.error(f"Audio processing error: {e}")
                continue
                
    def process_speech_input(self, text):
        """Process speech input and generate response"""
        # Add to conversation history
        self.conversation_history.append({
            'speaker': 'interviewer',
            'text': text,
            'timestamp': datetime.now().isoformat()
        })
        
        # Generate response
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
            
            logger.info(f"Generated response for: {text[:50]}...")
            
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
                
        # Fallback response
        return "That's a great question. Based on my experience with AI/ML and technical leadership, I would approach this by focusing on scalable solutions and clear communication with stakeholders."
        
    def next_question(self):
        """Show next question/response"""
        if self.current_question_index >= len(self.qa_pairs):
            self.current_question_index = 0
            
        current = self.qa_pairs[self.current_question_index]
        self.current_question = current['question']
        self.last_response = current['response']
        self.current_question_index += 1
        
        logger.info(f"Showing question {self.current_question_index}: {self.current_question[:50]}...")

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
        
        .controls {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            flex: 1;
            min-width: 120px;
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
        
        .btn-danger {
            background: #ff4444;
            color: #fff;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
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
        
        .audio-status {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .audio-active {
            background: #00ff88;
            animation: pulse 2s infinite;
        }
        
        .audio-inactive {
            background: #ff4444;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
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
            <div class="audio-status" id="audioStatus"></div>
        </div>
        
        <div class="controls">
            <button class="btn btn-primary" onclick="nextResponse()">⏭️ Next Response</button>
            <button class="btn btn-secondary" onclick="startListening()">🎤 Start Listening</button>
            <button class="btn btn-danger" onclick="stopListening()">🛑 Stop Listening</button>
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
        let isListening = false;
        
        function updateStatus(text) {
            document.getElementById('statusText').textContent = text;
        }
        
        function updateAudioStatus(listening) {
            const statusElement = document.getElementById('audioStatus');
            if (listening) {
                statusElement.className = 'audio-status audio-active';
                statusElement.title = 'Audio listening active';
            } else {
                statusElement.className = 'audio-status audio-inactive';
                statusElement.title = 'Audio listening inactive';
            }
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
                
                // Fetch status
                const statusResponse = await fetch('/api/status');
                const statusData = await statusResponse.json();
                updateAudioStatus(statusData.is_listening);
                
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
        
        async function startListening() {
            try {
                const response = await fetch('/api/start_listening');
                const data = await response.json();
                updateStatus(data.message);
                updateAudioStatus(true);
            } catch (error) {
                updateStatus('Error starting audio listening');
                console.error('Error:', error);
            }
        }
        
        async function stopListening() {
            try {
                const response = await fetch('/api/stop_listening');
                const data = await response.json();
                updateStatus(data.message);
                updateAudioStatus(false);
            } catch (error) {
                updateStatus('Error stopping audio listening');
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
    print("📱 Mobile interface template created")

def main():
    print("🎯 Web-Only Interview Teleprompter")
    print("=" * 50)
    print("🎯 Target: AI/Web3 Frontend Engineer Interview")
    print("👤 Recruiter: Anika Bansal (The DATAHEAD)")
    print("🏢 Company: Seed-funded startup (ex-Meta/Amazon backed)")
    print("⚡ Tech: React + TypeScript, Web3, AI agents")
    print("🎤 Features: Real-time audio listening + Mobile interface")
    print("📱 Mobile Interface: http://localhost:8080")
    print("=" * 50)
    print("🚀 Starting Web-Only Interview Teleprompter...")
    print("💡 Creating mobile web template...")
    
    # Create mobile template
    create_mobile_template()
    
    print("📱 Mobile interface template created")
    print("🎤 Audio listening system ready")
    print("🌐 Web server starting on port 8080")
    print("=" * 50)
    
    # Start the teleprompter
    teleprompter = WebInterviewTeleprompter()
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down teleprompter...")
        teleprompter.is_listening = False

if __name__ == "__main__":
    main()
