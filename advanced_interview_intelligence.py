#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Advanced Interview Intelligence System
Advanced real-time teleprompter with sentiment analysis and context awareness
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import speech_recognition as sr
import threading
import time
import json
import re
from datetime import datetime
import queue
import webbrowser
from collections import deque

class AdvancedInterviewIntelligence:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Meeting Notes")
        self.root.geometry("700x900")
        self.root.configure(bg='#f0f0f0')
        
        # Position strategically (bottom-right, outside camera view)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"700x900+{screen_width-720}+{screen_height-950}")
        
        # Interview state
        self.is_listening = False
        self.current_domain = "general"
        self.conversation_history = deque(maxlen=50)
        self.audio_queue = queue.Queue()
        self.interview_context = {
            "current_topic": "",
            "interviewer_mood": "neutral",
            "question_count": 0,
            "technical_depth": "basic",
            "time_elapsed": 0
        }
        
        # Advanced features
        self.sentiment_analysis = True
        self.context_awareness = True
        self.real_time_suggestions = True
        
        # Domain expertise data
        self.domain_data = self.load_advanced_domain_expertise()
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.setup_microphone()
        
        # UI setup
        self.setup_ui()
        
    def load_advanced_domain_expertise(self):
        """Load comprehensive domain expertise with advanced features"""
        return {
            "software_engineering": {
                "name": "Software Engineering",
                "keywords": ["coding", "programming", "development", "software", "code", "algorithm", "database", "api", "frontend", "backend", "testing", "deployment", "architecture", "microservices", "cloud", "devops", "ci/cd", "agile", "scrum"],
                "expert_answers": {
                    "coding": [
                        "I approach coding with a systematic methodology, starting with requirements analysis and then designing a scalable architecture that follows SOLID principles.",
                        "I follow clean code principles and design patterns to ensure maintainable, readable, and testable code that can scale with the business.",
                        "I prioritize code quality through comprehensive testing, code reviews, and continuous integration practices."
                    ],
                    "architecture": [
                        "I design systems with scalability, maintainability, and performance in mind, using microservices for complex systems and proper separation of concerns.",
                        "I use cloud-native architectures and containerization to ensure portability and efficient resource utilization.",
                        "I implement proper security practices, monitoring, and observability from the ground up."
                    ],
                    "testing": [
                        "I believe in comprehensive testing including unit, integration, end-to-end, and performance tests with high coverage.",
                        "I use TDD (Test-Driven Development) and BDD (Behavior-Driven Development) to ensure code quality from the start.",
                        "I implement automated testing pipelines and continuous integration to catch issues early."
                    ],
                    "leadership": [
                        "I lead technical teams by setting clear standards, mentoring developers, and fostering a culture of continuous learning.",
                        "I make architectural decisions based on data, team capabilities, and business requirements.",
                        "I communicate technical concepts clearly to both technical and non-technical stakeholders."
                    ]
                },
                "intelligent_questions": [
                    "What's your approach to handling technical debt in legacy systems while maintaining business continuity?",
                    "How do you ensure code quality and consistency across a large, distributed development team?",
                    "What's your experience with cloud-native architectures and serverless computing?",
                    "How do you handle performance optimization and scalability challenges in production systems?",
                    "What's your strategy for managing database migrations and data integrity in microservices?",
                    "How do you approach security in your development lifecycle and handle vulnerabilities?",
                    "What's your experience with DevOps practices and infrastructure as code?"
                ],
                "follow_up_questions": [
                    "Can you give me a specific example of how you handled a similar situation?",
                    "What were the key challenges you faced and how did you overcome them?",
                    "What metrics did you use to measure success in that project?",
                    "How did you ensure team adoption of new practices or technologies?"
                ]
            },
            "data_science": {
                "name": "Data Science",
                "keywords": ["data", "machine learning", "ai", "analytics", "statistics", "model", "algorithm", "prediction", "analysis", "visualization", "python", "r", "deep learning", "neural networks", "nlp", "computer vision", "big data", "spark", "hadoop"],
                "expert_answers": {
                    "machine_learning": [
                        "I follow a structured approach to ML projects: data collection, preprocessing, feature engineering, model selection, validation, and deployment with MLOps practices.",
                        "I use cross-validation, holdout sets, and proper evaluation metrics to ensure model generalization and avoid overfitting.",
                        "I prioritize interpretability, business impact, and ethical considerations over just model accuracy."
                    ],
                    "data_analysis": [
                        "I start with exploratory data analysis to understand patterns, relationships, and data quality issues before any modeling.",
                        "I use statistical methods and hypothesis testing to validate findings and ensure statistical significance.",
                        "I communicate insights through clear visualizations, storytelling, and actionable recommendations."
                    ],
                    "modeling": [
                        "I select models based on the problem type, data characteristics, computational constraints, and business requirements.",
                        "I use ensemble methods, hyperparameter tuning, and advanced techniques like deep learning when appropriate.",
                        "I implement proper validation strategies, model monitoring, and retraining pipelines for production."
                    ],
                    "leadership": [
                        "I lead data science teams by setting clear objectives, establishing best practices, and fostering innovation.",
                        "I bridge the gap between technical capabilities and business needs through effective communication.",
                        "I ensure ethical AI practices and responsible data usage in all projects."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle imbalanced datasets and ensure fair model performance across different groups?",
                    "What's your approach to feature selection, engineering, and dimensionality reduction?",
                    "How do you ensure model interpretability and explainability for stakeholders?",
                    "What's your experience with deep learning frameworks and GPU computing?",
                    "How do you handle data quality issues, missing data, and data drift in production?",
                    "What's your approach to A/B testing and experimental design for ML models?",
                    "How do you manage model versioning, deployment, and monitoring in production?"
                ],
                "follow_up_questions": [
                    "Can you walk me through a specific project where you applied these techniques?",
                    "What were the business outcomes and ROI of your data science initiatives?",
                    "How did you handle stakeholder communication and change management?",
                    "What challenges did you face and how did you overcome them?"
                ]
            },
            "product_management": {
                "name": "Product Management",
                "keywords": ["product", "strategy", "roadmap", "user", "market", "feature", "launch", "metrics", "stakeholder", "agile", "scrum", "kanban", "user research", "analytics", "growth", "monetization", "competition"],
                "expert_answers": {
                    "strategy": [
                        "I develop product strategy by deeply understanding market needs, competitive landscape, business objectives, and user pain points through research.",
                        "I use data-driven decision making, market analysis, and user feedback to prioritize features and initiatives that drive business value.",
                        "I align product goals with company vision, stakeholder needs, and market opportunities while managing technical constraints."
                    ],
                    "execution": [
                        "I use agile methodologies and lean startup principles to deliver value incrementally, respond to feedback, and iterate quickly.",
                        "I work closely with cross-functional teams including engineering, design, marketing, and sales to ensure successful delivery.",
                        "I measure success through key metrics, user feedback, and business outcomes while maintaining product quality."
                    ],
                    "leadership": [
                        "I lead by example, foster a collaborative team environment, and inspire others through clear vision and communication.",
                        "I communicate clearly with stakeholders at all levels, from executives to individual contributors.",
                        "I make decisions based on data and user insights while considering business context and technical feasibility."
                    ],
                    "innovation": [
                        "I stay current with industry trends, emerging technologies, and best practices to drive innovation.",
                        "I encourage experimentation, risk-taking, and learning from failures to improve products.",
                        "I build products that not only meet current needs but anticipate future user and market requirements."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle competing priorities from different stakeholders while maintaining product focus?",
                    "What's your approach to product-market fit validation and user research?",
                    "How do you measure and communicate product success to executives and stakeholders?",
                    "What's your experience with user research, A/B testing, and data-driven product decisions?",
                    "How do you handle scope creep and maintain agile principles in complex projects?",
                    "What's your strategy for launching new products and managing product lifecycles?",
                    "How do you stay competitive and differentiate your products in crowded markets?"
                ],
                "follow_up_questions": [
                    "Can you share a specific example of how you handled a challenging stakeholder situation?",
                    "What metrics did you use to measure success in your most recent product launch?",
                    "How did you gather and incorporate user feedback in your product development process?",
                    "What was the biggest challenge you faced and how did you overcome it?"
                ]
            },
            "marketing": {
                "name": "Marketing",
                "keywords": ["marketing", "campaign", "brand", "social media", "content", "seo", "analytics", "conversion", "lead", "customer", "growth", "digital", "automation", "personalization", "retention", "acquisition"],
                "expert_answers": {
                    "strategy": [
                        "I develop comprehensive marketing strategies based on target audience insights, competitive analysis, and business objectives.",
                        "I use data-driven approaches, market research, and customer segmentation to optimize campaigns and improve ROI.",
                        "I integrate multiple channels and touchpoints for cohesive brand messaging and customer experience."
                    ],
                    "execution": [
                        "I create compelling, relevant content that resonates with target audiences and drives engagement and conversions.",
                        "I use A/B testing, multivariate testing, and optimization techniques to improve campaign performance.",
                        "I leverage analytics, attribution modeling, and marketing automation to scale efforts efficiently."
                    ],
                    "growth": [
                        "I focus on both customer acquisition and retention strategies to maximize customer lifetime value.",
                        "I use marketing automation, personalization, and customer journey mapping to build relationships.",
                        "I implement data-driven growth strategies and measure success through key performance indicators."
                    ],
                    "innovation": [
                        "I stay current with marketing trends, emerging technologies, and best practices to drive innovation.",
                        "I experiment with new channels, formats, and strategies to reach and engage audiences effectively.",
                        "I use technology and automation to scale marketing efforts while maintaining personalization."
                    ]
                },
                "intelligent_questions": [
                    "How do you measure marketing ROI across different channels and attribution models?",
                    "What's your approach to customer segmentation, targeting, and personalization?",
                    "How do you handle brand reputation management and crisis communication?",
                    "What's your experience with marketing automation tools and customer journey optimization?",
                    "How do you stay current with marketing trends and adapt strategies accordingly?",
                    "What's your approach to content strategy and social media management?",
                    "How do you balance acquisition and retention marketing efforts?"
                ],
                "follow_up_questions": [
                    "Can you share a specific campaign that exceeded expectations and what made it successful?",
                    "What tools and technologies do you use for marketing analytics and automation?",
                    "How do you handle budget allocation across different marketing channels?",
                    "What was your biggest marketing challenge and how did you solve it?"
                ]
            },
            "finance": {
                "name": "Finance",
                "keywords": ["finance", "financial", "budget", "forecast", "analysis", "investment", "risk", "compliance", "audit", "accounting", "trading", "portfolio", "valuation", "modeling", "reporting"],
                "expert_answers": {
                    "analysis": [
                        "I use advanced financial modeling, analysis, and forecasting to support strategic decision making and risk assessment.",
                        "I conduct thorough risk assessments, scenario planning, and sensitivity analysis to inform business decisions.",
                        "I ensure compliance with regulatory requirements, accounting standards, and best practices in all financial activities."
                    ],
                    "strategy": [
                        "I develop comprehensive financial strategies aligned with business objectives and market conditions.",
                        "I optimize capital allocation, investment decisions, and financial planning to maximize shareholder value.",
                        "I maintain strong internal controls, governance, and risk management frameworks."
                    ],
                    "reporting": [
                        "I provide clear, accurate, and timely financial reporting to stakeholders at all levels.",
                        "I use key performance indicators, dashboards, and analytics to track financial health and performance.",
                        "I communicate complex financial information effectively to non-financial stakeholders."
                    ],
                    "leadership": [
                        "I lead finance teams by setting high standards, fostering professional development, and promoting ethical practices.",
                        "I collaborate with other departments to ensure financial considerations are integrated into business decisions.",
                        "I stay current with financial regulations, market trends, and best practices to provide strategic guidance."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle financial risk management in volatile and uncertain market conditions?",
                    "What's your approach to financial forecasting, planning, and variance analysis?",
                    "How do you ensure compliance with changing regulations and accounting standards?",
                    "What's your experience with financial modeling, valuation, and investment analysis?",
                    "How do you communicate financial results and insights to non-financial stakeholders?",
                    "What's your approach to cost management and operational efficiency?",
                    "How do you handle financial technology and automation in your processes?"
                ],
                "follow_up_questions": [
                    "Can you share a specific example of how you handled a financial crisis or challenge?",
                    "What financial systems and tools do you use for analysis and reporting?",
                    "How do you stay current with financial regulations and market trends?",
                    "What was your biggest financial achievement and what made it successful?"
                ]
            },
            "sales": {
                "name": "Sales",
                "keywords": ["sales", "selling", "customer", "prospect", "pipeline", "quota", "negotiation", "closing", "relationship", "lead", "conversion", "commission", "territory", "presentation"],
                "expert_answers": {
                    "process": [
                        "I follow a consultative selling approach, focusing on understanding customer needs, pain points, and business objectives.",
                        "I build strong, long-term relationships through trust, value delivery, and consistent follow-up.",
                        "I use data, analytics, and CRM systems to optimize my sales process and improve conversion rates."
                    ],
                    "execution": [
                        "I qualify leads effectively using BANT criteria to focus on high-probability opportunities.",
                        "I handle objections professionally by addressing concerns and turning them into opportunities.",
                        "I close deals by creating urgency, demonstrating clear value, and building consensus with decision makers."
                    ],
                    "relationships": [
                        "I maintain long-term relationships with customers for repeat business and referrals.",
                        "I use CRM systems to track interactions, opportunities, and customer information.",
                        "I collaborate with internal teams including marketing, product, and support to deliver customer success."
                    ],
                    "leadership": [
                        "I lead sales teams by setting clear goals, providing coaching, and fostering a high-performance culture.",
                        "I develop sales strategies, processes, and best practices to improve team performance.",
                        "I stay current with sales methodologies, technologies, and industry trends."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle difficult customer objections and challenging negotiations?",
                    "What's your approach to building and maintaining long-term customer relationships?",
                    "How do you prioritize and manage your sales pipeline and territory?",
                    "What's your experience with consultative selling and solution-based approaches?",
                    "How do you stay motivated and achieve sales targets in competitive markets?",
                    "What's your approach to prospecting and lead generation?",
                    "How do you use technology and data to improve sales performance?"
                ],
                "follow_up_questions": [
                    "Can you share a specific example of how you handled a difficult customer situation?",
                    "What sales methodologies and tools do you use in your process?",
                    "How do you measure and track your sales performance and success?",
                    "What was your biggest sales achievement and what made it successful?"
                ]
            },
            "general": {
                "name": "General",
                "keywords": ["leadership", "teamwork", "communication", "problem solving", "innovation", "growth", "learning", "adaptability", "collaboration", "management", "strategy"],
                "expert_answers": {
                    "leadership": [
                        "I lead by example and inspire others through clear vision, effective communication, and consistent actions.",
                        "I empower team members to take ownership, make decisions, and grow professionally while providing support.",
                        "I make decisions based on data and input from others while considering long-term implications."
                    ],
                    "teamwork": [
                        "I believe in collaborative problem-solving and leveraging diverse perspectives to achieve better outcomes.",
                        "I communicate openly, build trust with team members, and create an inclusive environment.",
                        "I support others' success, celebrate team achievements, and foster a positive team culture."
                    ],
                    "growth": [
                        "I'm committed to continuous learning, professional development, and staying current with industry trends.",
                        "I adapt quickly to changing environments, new challenges, and evolving business needs.",
                        "I seek feedback actively, use it to improve my performance, and help others grow."
                    ],
                    "problem_solving": [
                        "I approach problems systematically by gathering information, analyzing options, and implementing solutions.",
                        "I think creatively and consider multiple perspectives to find innovative solutions.",
                        "I learn from failures and use them as opportunities for improvement and growth."
                    ]
                },
                "intelligent_questions": [
                    "How do you handle conflict within a team and difficult interpersonal situations?",
                    "What's your approach to continuous learning and professional development?",
                    "How do you adapt to changing priorities, requirements, and business environments?",
                    "What's your experience with remote or distributed teams and virtual collaboration?",
                    "How do you balance individual goals with team objectives and organizational needs?",
                    "What's your approach to decision-making and problem-solving in complex situations?",
                    "How do you motivate and inspire others to achieve their best performance?"
                ],
                "follow_up_questions": [
                    "Can you share a specific example of how you handled a challenging team situation?",
                    "What leadership or management methodologies do you follow?",
                    "How do you measure success in your leadership and team management?",
                    "What was your biggest leadership challenge and how did you overcome it?"
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
        
        # Advanced features toggles
        features_frame = tk.Frame(control_frame, bg='#ffffff')
        features_frame.pack(fill='x', padx=10, pady=5)
        
        self.sentiment_var = tk.BooleanVar(value=True)
        sentiment_check = tk.Checkbutton(
            features_frame,
            text="Sentiment Analysis",
            variable=self.sentiment_var,
            bg='#ffffff',
            font=('Arial', 9)
        )
        sentiment_check.pack(side='left', padx=(0, 20))
        
        self.context_var = tk.BooleanVar(value=True)
        context_check = tk.Checkbutton(
            features_frame,
            text="Context Awareness",
            variable=self.context_var,
            bg='#ffffff',
            font=('Arial', 9)
        )
        context_check.pack(side='left', padx=(0, 20))
        
        self.suggestions_var = tk.BooleanVar(value=True)
        suggestions_check = tk.Checkbutton(
            features_frame,
            text="Real-time Suggestions",
            variable=self.suggestions_var,
            bg='#ffffff',
            font=('Arial', 9)
        )
        suggestions_check.pack(side='left')
        
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
        
        # Context display
        context_display_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        context_display_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            context_display_frame,
            text="Interview Context:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        self.context_label = tk.Label(
            context_display_frame,
            text="Topic: None | Questions: 0 | Mood: Neutral",
            font=('Arial', 9),
            bg='#ffffff',
            fg='#666666'
        )
        self.context_label.pack(anchor='w', padx=10, pady=(0, 5))
        
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
        self.add_note("🎯 Advanced Interview Intelligence System Ready\n")
        self.add_note("Select your domain and click 'Start Listening'\n")
        self.add_note("Advanced features: Sentiment Analysis, Context Awareness, Real-time Suggestions\n")
        
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
                
                # Update interview context
                self.update_interview_context(text)
                
                # Analyze and provide intelligence
                self.analyze_conversation_advanced(text)
                
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            
    def update_interview_context(self, text):
        """Update interview context based on conversation"""
        text_lower = text.lower()
        
        # Update question count
        if any(word in text_lower for word in ['what', 'how', 'why', 'when', 'where', 'who', 'which']):
            self.interview_context["question_count"] += 1
            
        # Update current topic
        domain_info = self.domain_data[self.current_domain]
        for keyword in domain_info['keywords']:
            if keyword in text_lower:
                self.interview_context["current_topic"] = keyword
                break
                
        # Update technical depth
        technical_terms = self.extract_technical_terms(text_lower)
        if len(technical_terms) > 3:
            self.interview_context["technical_depth"] = "advanced"
        elif len(technical_terms) > 1:
            self.interview_context["technical_depth"] = "intermediate"
        else:
            self.interview_context["technical_depth"] = "basic"
            
        # Update context display
        self.update_context_display()
        
    def update_context_display(self):
        """Update the context display"""
        context = self.interview_context
        display_text = f"Topic: {context['current_topic']} | Questions: {context['question_count']} | Depth: {context['technical_depth']}"
        self.context_label.configure(text=display_text)
        
    def analyze_conversation_advanced(self, text):
        """Advanced conversation analysis with multiple features"""
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
            
            # Provide follow-up questions
            if 'follow_up_questions' in domain_info:
                self.add_note(f"💡 Consider asking follow-up questions:\n")
                for i, question in enumerate(domain_info['follow_up_questions'][:3], 1):
                    self.add_note(f"   {i}. {question}\n")
                    
        # Sentiment analysis
        if self.sentiment_var.get():
            sentiment = self.analyze_sentiment(text_lower)
            if sentiment != "neutral":
                self.add_note(f"\n😊 Sentiment: {sentiment.capitalize()}\n")
                if sentiment == "negative":
                    self.add_note(f"💡 Consider addressing concerns or providing reassurance\n")
                elif sentiment == "positive":
                    self.add_note(f"💡 Good opportunity to build rapport and enthusiasm\n")
                    
        # Context awareness
        if self.context_var.get():
            self.provide_context_aware_suggestions(text_lower)
            
        # Real-time suggestions
        if self.suggestions_var.get():
            self.provide_real_time_suggestions(text_lower)
            
        # Check for technical terms
        technical_terms = self.extract_technical_terms(text_lower)
        if technical_terms:
            self.add_note(f"\n🔧 Technical terms: {', '.join(technical_terms)}\n")
            self.add_note(f"💡 Be prepared to discuss these in detail\n")
            
    def analyze_sentiment(self, text):
        """Simple sentiment analysis"""
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'good', 'positive', 'successful', 'happy', 'excited']
        negative_words = ['bad', 'terrible', 'awful', 'difficult', 'challenging', 'problem', 'issue', 'concern', 'worried', 'frustrated']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
            
    def provide_context_aware_suggestions(self, text):
        """Provide context-aware suggestions"""
        context = self.interview_context
        
        if context["question_count"] > 5:
            self.add_note(f"\n📊 Interview Progress: {context['question_count']} questions asked\n")
            self.add_note(f"💡 Consider asking about next steps or timeline\n")
            
        if context["technical_depth"] == "advanced":
            self.add_note(f"\n🔬 Technical depth: Advanced\n")
            self.add_note(f"💡 Be prepared for detailed technical discussions\n")
            
        if context["current_topic"]:
            self.add_note(f"\n🎯 Current topic: {context['current_topic']}\n")
            self.add_note(f"💡 Stay focused on this area and provide specific examples\n")
            
    def provide_real_time_suggestions(self, text):
        """Provide real-time suggestions based on conversation"""
        # Check for specific patterns
        if 'experience' in text:
            self.add_note(f"\n💼 Experience question detected\n")
            self.add_note(f"💡 Be ready to share specific examples and achievements\n")
            
        if 'challenge' in text or 'problem' in text:
            self.add_note(f"\n⚡ Challenge/problem question detected\n")
            self.add_note(f"💡 Use STAR method: Situation, Task, Action, Result\n")
            
        if 'team' in text or 'leadership' in text:
            self.add_note(f"\n👥 Team/leadership question detected\n")
            self.add_note(f"💡 Emphasize collaboration, communication, and results\n")
            
        if 'future' in text or 'goals' in text:
            self.add_note(f"\n🎯 Future/goals question detected\n")
            self.add_note(f"💡 Align your goals with the company's vision\n")
            
    def extract_technical_terms(self, text):
        """Extract technical terms from text"""
        # Common technical terms
        tech_terms = [
            'api', 'database', 'algorithm', 'framework', 'protocol', 'architecture',
            'deployment', 'scalability', 'performance', 'security', 'testing',
            'machine learning', 'ai', 'analytics', 'visualization', 'statistics',
            'agile', 'scrum', 'kanban', 'waterfall', 'sprint', 'backlog',
            'roi', 'kpi', 'metrics', 'conversion', 'optimization', 'automation',
            'microservices', 'cloud', 'devops', 'ci/cd', 'docker', 'kubernetes',
            'python', 'javascript', 'java', 'sql', 'nosql', 'react', 'angular',
            'aws', 'azure', 'gcp', 'saas', 'paas', 'iaas'
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
    print("🔧 Iron Cloud Nexus AI - Advanced Interview Intelligence System")
    print("=" * 70)
    print("🎯 Target: Live Interviews (Zoom, Teams, etc.)")
    print("⚡ Advanced real-time teleprompter with AI features")
    print("🔒 Background listening with sentiment analysis")
    print("=" * 70)
    print("🚀 Starting Advanced Interview Intelligence...")
    print("💡 A 'Meeting Notes' window will appear")
    print("🎤 Select domain and click 'Start Listening'")
    print("💡 Advanced features: Sentiment, Context, Real-time suggestions")
    print("🔒 Works in background during interviews")
    print("=" * 70)
    
    # Check for speech recognition
    try:
        import speech_recognition as sr
    except ImportError:
        print("❌ Speech recognition not available.")
        print("Install with: pip install SpeechRecognition pyaudio")
        return
        
    intelligence_system = AdvancedInterviewIntelligence()
    intelligence_system.run()

if __name__ == "__main__":
    main()
