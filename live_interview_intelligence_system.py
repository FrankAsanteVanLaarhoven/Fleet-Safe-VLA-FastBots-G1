#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Live Interview Intelligence System
Real-time teleprompter for live interviews on Zoom, Teams, etc.
Provides live answers and intelligent questions based on conversation
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import speech_recognition as sr
import threading
import time
import json
import re
from datetime import datetime
import queue
import webbrowser

class LiveInterviewIntelligence:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Meeting Notes")
        self.root.geometry("600x800")
        self.root.configure(bg='#f0f0f0')
        
        # Position strategically (bottom-right, outside camera view)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"600x800+{screen_width-620}+{screen_height-850}")
        
        # Interview state
        self.is_listening = False
        self.current_domain = "general"
        self.conversation_history = []
        self.audio_queue = queue.Queue()
        
        # Domain expertise data
        self.domain_data = self.load_domain_expertise()
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.setup_microphone()
        
        # UI setup
        self.setup_ui()
        
    def load_domain_expertise(self):
        """Load comprehensive domain expertise data"""
        return {
            "software_engineering": {
                "name": "Software Engineering",
                "keywords": ["coding", "programming", "development", "software", "code", "algorithm", "database", "api", "frontend", "backend", "testing", "deployment"],
                "expert_answers": {
                    "coding": [
                        "I approach coding with a systematic methodology, starting with requirements analysis and then designing a scalable architecture.",
                        "I follow clean code principles and design patterns to ensure maintainable and readable code.",
                        "I prioritize code quality through comprehensive testing and code reviews."
                    ],
                    "architecture": [
                        "I design systems with scalability, maintainability, and performance in mind.",
                        "I use microservices architecture for complex systems to ensure modularity.",
                        "I implement proper separation of concerns and follow SOLID principles."
                    ],
                    "testing": [
                        "I believe in comprehensive testing including unit, integration, and end-to-end tests.",
                        "I use TDD (Test-Driven Development) to ensure code quality from the start.",
                        "I implement automated testing pipelines for continuous integration."
                    ]
                },
                "intelligent_questions": [
                    "What's your approach to handling technical debt in legacy systems?",
                    "How do you ensure code quality across a large development team?",
                    "What's your experience with cloud-native architectures?",
                    "How do you handle performance optimization in your applications?",
                    "What's your strategy for managing database migrations?"
                ]
            },
            "data_science": {
                "name": "Data Science",
                "keywords": ["data", "machine learning", "ai", "analytics", "statistics", "model", "algorithm", "prediction", "analysis", "visualization", "python", "r"],
                "expert_answers": {
                    "machine_learning": [
                        "I follow a structured approach to ML projects: data collection, preprocessing, feature engineering, model selection, and validation.",
                        "I use cross-validation and holdout sets to ensure model generalization.",
                        "I prioritize interpretability and business impact over just model accuracy."
                    ],
                    "data_analysis": [
                        "I start with exploratory data analysis to understand patterns and relationships.",
                        "I use statistical methods to validate findings and ensure significance.",
                        "I communicate insights through clear visualizations and storytelling."
                    ],
                    "modeling": [
                        "I select models based on the problem type, data characteristics, and business requirements.",
                        "I use ensemble methods when appropriate to improve performance.",
                        "I implement proper validation strategies to avoid overfitting."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle imbalanced datasets in your ML projects?",
                    "What's your approach to feature selection and engineering?",
                    "How do you ensure model interpretability for stakeholders?",
                    "What's your experience with deep learning frameworks?",
                    "How do you handle data quality issues in production?"
                ]
            },
            "product_management": {
                "name": "Product Management",
                "keywords": ["product", "strategy", "roadmap", "user", "market", "feature", "launch", "metrics", "stakeholder", "agile", "scrum", "kanban"],
                "expert_answers": {
                    "strategy": [
                        "I develop product strategy by understanding market needs, competitive landscape, and business objectives.",
                        "I use data-driven decision making to prioritize features and initiatives.",
                        "I align product goals with company vision and stakeholder needs."
                    ],
                    "execution": [
                        "I use agile methodologies to deliver value incrementally and respond to feedback.",
                        "I work closely with cross-functional teams to ensure successful delivery.",
                        "I measure success through key metrics and user feedback."
                    ],
                    "leadership": [
                        "I lead by example and foster a collaborative team environment.",
                        "I communicate clearly with stakeholders at all levels.",
                        "I make decisions based on data while considering business context."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle competing priorities from different stakeholders?",
                    "What's your approach to product-market fit validation?",
                    "How do you measure and communicate product success?",
                    "What's your experience with user research and feedback collection?",
                    "How do you handle scope creep in agile environments?"
                ]
            },
            "marketing": {
                "name": "Marketing",
                "keywords": ["marketing", "campaign", "brand", "social media", "content", "seo", "analytics", "conversion", "lead", "customer", "growth", "digital"],
                "expert_answers": {
                    "strategy": [
                        "I develop marketing strategies based on target audience insights and business objectives.",
                        "I use data-driven approaches to optimize campaigns and improve ROI.",
                        "I integrate multiple channels for cohesive brand messaging."
                    ],
                    "execution": [
                        "I create compelling content that resonates with target audiences.",
                        "I use A/B testing to optimize campaigns and improve performance.",
                        "I leverage analytics to measure success and inform future strategies."
                    ],
                    "growth": [
                        "I focus on customer acquisition and retention strategies.",
                        "I use marketing automation to scale efforts efficiently.",
                        "I build relationships with customers through personalized experiences."
                    ]
                },
                "intelligent_questions": [
                    "How do you measure marketing ROI across different channels?",
                    "What's your approach to customer segmentation and targeting?",
                    "How do you handle brand reputation management?",
                    "What's your experience with marketing automation tools?",
                    "How do you stay current with marketing trends and technologies?"
                ]
            },
            "finance": {
                "name": "Finance",
                "keywords": ["finance", "financial", "budget", "forecast", "analysis", "investment", "risk", "compliance", "audit", "accounting", "trading", "portfolio"],
                "expert_answers": {
                    "analysis": [
                        "I use financial modeling and analysis to support strategic decision making.",
                        "I conduct thorough risk assessments and scenario planning.",
                        "I ensure compliance with regulatory requirements and best practices."
                    ],
                    "strategy": [
                        "I develop financial strategies aligned with business objectives.",
                        "I optimize capital allocation and investment decisions.",
                        "I maintain strong internal controls and governance."
                    ],
                    "reporting": [
                        "I provide clear and accurate financial reporting to stakeholders.",
                        "I use key performance indicators to track financial health.",
                        "I communicate complex financial information effectively."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle financial risk management in volatile markets?",
                    "What's your approach to financial forecasting and planning?",
                    "How do you ensure compliance with changing regulations?",
                    "What's your experience with financial modeling and analysis?",
                    "How do you communicate financial results to non-financial stakeholders?"
                ]
            },
            "sales": {
                "name": "Sales",
                "keywords": ["sales", "selling", "customer", "prospect", "pipeline", "quota", "negotiation", "closing", "relationship", "lead", "conversion", "commission"],
                "expert_answers": {
                    "process": [
                        "I follow a consultative selling approach, focusing on understanding customer needs.",
                        "I build strong relationships through trust and value delivery.",
                        "I use data and analytics to optimize my sales process."
                    ],
                    "execution": [
                        "I qualify leads effectively to focus on high-probability opportunities.",
                        "I handle objections professionally and turn them into opportunities.",
                        "I close deals by creating urgency and demonstrating clear value."
                    ],
                    "relationships": [
                        "I maintain long-term relationships with customers for repeat business.",
                        "I use CRM systems to track interactions and opportunities.",
                        "I collaborate with internal teams to deliver customer success."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle difficult customer objections?",
                    "What's your approach to building long-term customer relationships?",
                    "How do you prioritize and manage your sales pipeline?",
                    "What's your experience with consultative selling?",
                    "How do you stay motivated and achieve sales targets?"
                ]
            },
            "general": {
                "name": "General",
                "keywords": ["leadership", "teamwork", "communication", "problem solving", "innovation", "growth", "learning", "adaptability", "collaboration"],
                "expert_answers": {
                    "leadership": [
                        "I lead by example and inspire others through clear vision and communication.",
                        "I empower team members to take ownership and grow professionally.",
                        "I make decisions based on data while considering team input."
                    ],
                    "teamwork": [
                        "I believe in collaborative problem-solving and leveraging diverse perspectives.",
                        "I communicate openly and build trust with team members.",
                        "I support others' success and celebrate team achievements."
                    ],
                    "growth": [
                        "I'm committed to continuous learning and professional development.",
                        "I adapt quickly to changing environments and new challenges.",
                        "I seek feedback and use it to improve my performance."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle conflict within a team?",
                    "What's your approach to continuous learning and development?",
                    "How do you adapt to changing priorities and requirements?",
                    "What's your experience with remote or distributed teams?",
                    "How do you balance individual goals with team objectives?"
                ]
            }
        }
        
    def setup_microphone(self):
        """Setup microphone for speech recognition"""
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Microphone setup error: {e}")
            
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header_frame,
            text="Meeting Notes",
            font=('Arial', 16, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        title.pack(pady=10)
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        control_frame.pack(fill='x', pady=(0, 10))
        
        # Domain selection
        domain_frame = tk.Frame(control_frame, bg='#ffffff')
        domain_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(
            domain_frame,
            text="Domain:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff'
        ).pack(side='left')
        
        self.domain_var = tk.StringVar(value="general")
        domain_dropdown = ttk.Combobox(
            domain_frame,
            textvariable=self.domain_var,
            values=list(self.domain_data.keys()),
            font=('Arial', 10),
            state='readonly',
            width=20
        )
        domain_dropdown.pack(side='left', padx=(10, 0))
        domain_dropdown.bind('<<ComboboxSelected>>', self.on_domain_change)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#ffffff')
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.listen_btn = tk.Button(
            button_frame,
            text="Start Listening",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            command=self.toggle_listening,
            width=15,
            height=2
        )
        self.listen_btn.pack(side='left', padx=5)
        
        self.clear_btn = tk.Button(
            button_frame,
            text="Clear Notes",
            font=('Arial', 12, 'bold'),
            bg='#f44336',
            fg='#ffffff',
            command=self.clear_notes,
            width=15,
            height=2
        )
        self.clear_btn.pack(side='left', padx=5)
        
        # Status display
        status_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        status_frame.pack(fill='x', pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="Status: Ready",
            font=('Arial', 10),
            bg='#ffffff',
            fg='#666666'
        )
        self.status_label.pack(pady=5)
        
        # Notes area
        notes_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        notes_frame.pack(fill='both', expand=True)
        
        tk.Label(
            notes_frame,
            text="Live Intelligence Notes:",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            fg='#333333'
        ).pack(pady=(10, 5))
        
        # Notes text area
        self.notes_text = scrolledtext.ScrolledText(
            notes_frame,
            font=('Arial', 11),
            bg='#f8f8f8',
            fg='#333333',
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.notes_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Add initial content
        self.add_note("🎯 Live Interview Intelligence System Ready\n")
        self.add_note("Select your domain and click 'Start Listening'\n")
        self.add_note("The system will provide real-time answers and questions\n")
        
    def on_domain_change(self, event):
        """Handle domain selection change"""
        self.current_domain = self.domain_var.get()
        domain_info = self.domain_data[self.current_domain]
        self.add_note(f"\n📋 Domain changed to: {domain_info['name']}\n")
        self.add_note(f"💡 Ready to provide {domain_info['name']} expertise\n")
        
    def toggle_listening(self):
        """Toggle listening mode"""
        if not self.is_listening:
            self.start_listening()
        else:
            self.stop_listening()
            
    def start_listening(self):
        """Start listening to audio"""
        if not self.microphone:
            self.add_note("❌ Microphone not available\n")
            return
            
        self.is_listening = True
        self.listen_btn.configure(text="Stop Listening", bg='#f44336')
        self.status_label.configure(text="Status: Listening...", fg='#4CAF50')
        
        self.add_note("\n🎤 Started listening to interview...\n")
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
        
    def stop_listening(self):
        """Stop listening to audio"""
        self.is_listening = False
        self.listen_btn.configure(text="Start Listening", bg='#4CAF50')
        self.status_label.configure(text="Status: Stopped", fg='#f44336')
        
        self.add_note("\n⏹️ Stopped listening\n")
        
    def listen_loop(self):
        """Main listening loop"""
        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=10)
                    
                # Process audio in separate thread
                threading.Thread(target=self.process_audio, args=(audio,), daemon=True).start()
                
            except sr.WaitTimeoutError:
                continue
            except Exception as e:
                print(f"Listening error: {e}")
                continue
                
    def process_audio(self, audio):
        """Process captured audio"""
        try:
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            
            if text:
                # Add to conversation history
                self.conversation_history.append({
                    'timestamp': datetime.now(),
                    'text': text.lower()
                })
                
                # Analyze and provide intelligence
                self.analyze_conversation(text)
                
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            
    def analyze_conversation(self, text):
        """Analyze conversation and provide intelligence"""
        text_lower = text.lower()
        domain_info = self.domain_data[self.current_domain]
        
        # Check for domain keywords
        detected_keywords = []
        for keyword in domain_info['keywords']:
            if keyword in text_lower:
                detected_keywords.append(keyword)
                
        if detected_keywords:
            self.add_note(f"\n🎯 Detected keywords: {', '.join(detected_keywords)}\n")
            
            # Provide expert answers
            for keyword in detected_keywords:
                if keyword in domain_info['expert_answers']:
                    answers = domain_info['expert_answers'][keyword]
                    self.add_note(f"💡 Expert answer for '{keyword}':\n")
                    self.add_note(f"   {answers[0]}\n")
                    
            # Provide intelligent questions
            self.add_note(f"❓ Intelligent questions to ask:\n")
            for i, question in enumerate(domain_info['intelligent_questions'][:3], 1):
                self.add_note(f"   {i}. {question}\n")
                
        # Check for question patterns
        if any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            self.add_note(f"\n❓ Question detected: {text}\n")
            self.add_note(f"💡 Consider asking follow-up questions about:\n")
            self.add_note(f"   - Your experience with similar situations\n")
            self.add_note(f"   - Specific examples from your background\n")
            self.add_note(f"   - Your approach to problem-solving\n")
            
        # Check for technical terms
        technical_terms = self.extract_technical_terms(text_lower)
        if technical_terms:
            self.add_note(f"\n🔧 Technical terms: {', '.join(technical_terms)}\n")
            self.add_note(f"💡 Be prepared to discuss these in detail\n")
            
    def extract_technical_terms(self, text):
        """Extract technical terms from text"""
        # Common technical terms
        tech_terms = [
            'api', 'database', 'algorithm', 'framework', 'protocol', 'architecture',
            'deployment', 'scalability', 'performance', 'security', 'testing',
            'machine learning', 'ai', 'analytics', 'visualization', 'statistics',
            'agile', 'scrum', 'kanban', 'waterfall', 'sprint', 'backlog',
            'roi', 'kpi', 'metrics', 'conversion', 'optimization', 'automation'
        ]
        
        found_terms = []
        for term in tech_terms:
            if term in text:
                found_terms.append(term)
                
        return found_terms
        
    def add_note(self, text):
        """Add note to the text area"""
        self.notes_text.insert(tk.END, text)
        self.notes_text.see(tk.END)
        
    def clear_notes(self):
        """Clear all notes"""
        self.notes_text.delete(1.0, tk.END)
        self.add_note("🎯 Notes cleared. Ready for new session.\n")
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Live Interview Intelligence System")
    print("=" * 65)
    print("🎯 Target: Live Interviews (Zoom, Teams, etc.)")
    print("⚡ Real-time teleprompter with live answers")
    print("🔒 Background listening and intelligence")
    print("=" * 65)
    print("🚀 Starting Live Interview Intelligence...")
    print("💡 A 'Meeting Notes' window will appear")
    print("🎤 Select domain and click 'Start Listening'")
    print("💡 System provides real-time answers and questions")
    print("🔒 Works in background during interviews")
    print("=" * 65)
    
    # Check for speech recognition
    try:
        import speech_recognition as sr
    except ImportError:
        print("❌ Speech recognition not available.")
        print("Install with: pip install SpeechRecognition pyaudio")
        return
        
    intelligence_system = LiveInterviewIntelligence()
    intelligence_system.run()

if __name__ == "__main__":
    main()
