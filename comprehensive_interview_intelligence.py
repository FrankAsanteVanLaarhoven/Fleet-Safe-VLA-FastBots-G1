#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Comprehensive Interview Intelligence System
Advanced real-time teleprompter with transcript analysis, reports, and PhD-level topics
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import speech_recognition as sr
import threading
import time
import json
import re
from datetime import datetime
import queue
import webbrowser
from collections import deque
import os
import zipfile
import csv

class ComprehensiveInterviewIntelligence:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Meeting Notes")
        self.root.geometry("800x1000")
        self.root.configure(bg='#f0f0f0')
        
        # Position strategically
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"800x1000+{screen_width-820}+{screen_height-1050}")
        
        # Interview state
        self.is_listening = False
        self.current_domain = "general"
        self.conversation_history = deque(maxlen=100)
        self.interview_start_time = None
        self.interview_end_time = None
        
        # Analysis data
        self.interview_analysis = {
            "transcript": [],
            "sentiment_scores": [],
            "confidence_ratings": [],
            "topic_coverage": {},
            "question_analysis": [],
            "response_quality": [],
            "overall_rating": 0
        }
        
        # PhD-level topic data
        self.phd_topics = self.load_phd_topics()
        
        # Domain expertise data
        self.domain_data = self.load_comprehensive_domain_data()
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.setup_microphone()
        
        # UI setup
        self.setup_ui()
        
    def load_phd_topics(self):
        """Load PhD-level topic analysis capabilities"""
        return {
            "why_analysis": {
                "purpose": "Understanding motivations, reasons, and underlying causes",
                "questions": [
                    "Why did you choose this approach?",
                    "Why is this solution optimal?",
                    "Why does this problem exist?",
                    "Why is this technology relevant?",
                    "Why should we prioritize this?"
                ],
                "analysis_framework": [
                    "Motivational factors",
                    "Causal relationships",
                    "Strategic reasoning",
                    "Value proposition",
                    "Impact assessment"
                ]
            },
            "who_analysis": {
                "purpose": "Identifying stakeholders, team dynamics, and responsibilities",
                "questions": [
                    "Who are the key stakeholders?",
                    "Who would be responsible for this?",
                    "Who benefits from this solution?",
                    "Who are the decision makers?",
                    "Who would be affected?"
                ],
                "analysis_framework": [
                    "Stakeholder mapping",
                    "Role identification",
                    "Team composition",
                    "Responsibility matrix",
                    "Influence analysis"
                ]
            },
            "what_analysis": {
                "purpose": "Defining objectives, requirements, and deliverables",
                "questions": [
                    "What are the specific requirements?",
                    "What is the expected outcome?",
                    "What resources are needed?",
                    "What are the constraints?",
                    "What defines success?"
                ],
                "analysis_framework": [
                    "Requirement analysis",
                    "Scope definition",
                    "Deliverable specification",
                    "Constraint identification",
                    "Success metrics"
                ]
            },
            "where_analysis": {
                "purpose": "Understanding context, location, and environment",
                "questions": [
                    "Where will this be implemented?",
                    "Where are the bottlenecks?",
                    "Where do we see opportunities?",
                    "Where are the risks?",
                    "Where should we focus?"
                ],
                "analysis_framework": [
                    "Context analysis",
                    "Location mapping",
                    "Environment assessment",
                    "Geographic factors",
                    "Deployment strategy"
                ]
            },
            "when_analysis": {
                "purpose": "Timeline planning, sequencing, and temporal factors",
                "questions": [
                    "When should this be completed?",
                    "When are the critical milestones?",
                    "When do we need to decide?",
                    "When will we see results?",
                    "When should we reassess?"
                ],
                "analysis_framework": [
                    "Timeline planning",
                    "Milestone identification",
                    "Critical path analysis",
                    "Dependency mapping",
                    "Risk timing"
                ]
            },
            "how_analysis": {
                "purpose": "Implementation strategy, methodology, and execution",
                "questions": [
                    "How will this be implemented?",
                    "How do we measure progress?",
                    "How do we handle challenges?",
                    "How do we ensure quality?",
                    "How do we scale this?"
                ],
                "analysis_framework": [
                    "Implementation strategy",
                    "Methodology selection",
                    "Execution plan",
                    "Quality assurance",
                    "Scalability approach"
                ]
            }
        }
        
    def load_comprehensive_domain_data(self):
        """Load comprehensive domain expertise with PhD-level analysis"""
        return {
            "software_engineering": {
                "name": "Software Engineering",
                "keywords": ["coding", "programming", "development", "software", "code", "algorithm", "database", "api", "frontend", "backend", "testing", "deployment", "architecture", "microservices", "cloud", "devops", "ci/cd", "agile", "scrum", "design patterns", "clean code", "refactoring", "technical debt", "scalability", "performance", "security", "monitoring", "observability"],
                "phd_level_topics": {
                    "software_architecture": {
                        "why": "Architecture decisions impact scalability, maintainability, and system evolution",
                        "who": "Architects, senior developers, and technical leads make architectural decisions",
                        "what": "System design patterns, component interactions, and technology choices",
                        "where": "Enterprise systems, cloud platforms, and distributed environments",
                        "when": "During system design, refactoring phases, and technology migrations",
                        "how": "Through design reviews, prototyping, and iterative development"
                    },
                    "algorithm_complexity": {
                        "why": "Understanding complexity helps optimize performance and resource usage",
                        "who": "Algorithm designers, performance engineers, and system architects",
                        "what": "Time and space complexity analysis, optimization strategies",
                        "where": "Data processing, search algorithms, and computational systems",
                        "when": "During algorithm design, performance optimization, and system scaling",
                        "how": "Through complexity analysis, benchmarking, and profiling"
                    },
                    "software_quality": {
                        "why": "Quality ensures reliability, maintainability, and user satisfaction",
                        "who": "QA engineers, developers, and product managers",
                        "what": "Testing strategies, code quality metrics, and quality assurance processes",
                        "where": "Development pipelines, production systems, and user environments",
                        "when": "Throughout development lifecycle, from design to deployment",
                        "how": "Through automated testing, code reviews, and quality metrics"
                    }
                },
                "expert_answers": {
                    "architecture": [
                        "I design systems with scalability, maintainability, and performance in mind, using microservices for complex systems and proper separation of concerns.",
                        "I follow established architectural patterns like CQRS, Event Sourcing, and Domain-Driven Design for enterprise applications.",
                        "I implement proper security practices, monitoring, and observability from the ground up."
                    ],
                    "testing": [
                        "I believe in comprehensive testing including unit, integration, end-to-end, and performance tests with high coverage.",
                        "I use TDD (Test-Driven Development) and BDD (Behavior-Driven Development) to ensure code quality from the start.",
                        "I implement automated testing pipelines and continuous integration to catch issues early."
                    ]
                }
            },
            "data_science": {
                "name": "Data Science",
                "keywords": ["data", "machine learning", "ai", "analytics", "statistics", "model", "algorithm", "prediction", "analysis", "visualization", "python", "r", "deep learning", "neural networks", "nlp", "computer vision", "big data", "spark", "hadoop", "feature engineering", "model validation", "overfitting", "bias", "interpretability", "mlops"],
                "phd_level_topics": {
                    "machine_learning_theory": {
                        "why": "Understanding theory enables better model selection and problem-solving",
                        "who": "ML researchers, data scientists, and algorithm developers",
                        "what": "Statistical learning theory, optimization algorithms, and model complexity",
                        "where": "Research institutions, tech companies, and academic settings",
                        "when": "During model development, algorithm design, and research phases",
                        "how": "Through mathematical analysis, experimentation, and validation"
                    },
                    "ethical_ai": {
                        "why": "AI systems must be fair, transparent, and accountable",
                        "who": "AI ethicists, data scientists, and policy makers",
                        "what": "Bias detection, fairness metrics, and explainable AI",
                        "where": "AI systems, decision-making processes, and automated systems",
                        "when": "Throughout AI development lifecycle and deployment",
                        "how": "Through bias testing, fairness evaluation, and transparency measures"
                    },
                    "mlops": {
                        "why": "MLOps ensures reliable, scalable, and maintainable ML systems",
                        "who": "ML engineers, DevOps engineers, and data scientists",
                        "what": "Model deployment, monitoring, and lifecycle management",
                        "where": "Production ML systems, cloud platforms, and enterprise environments",
                        "when": "During model deployment, monitoring, and maintenance phases",
                        "how": "Through automated pipelines, monitoring systems, and version control"
                    }
                },
                "expert_answers": {
                    "machine_learning": [
                        "I follow a structured approach to ML projects: data collection, preprocessing, feature engineering, model selection, validation, and deployment with MLOps practices.",
                        "I use cross-validation, holdout sets, and proper evaluation metrics to ensure model generalization and avoid overfitting.",
                        "I prioritize interpretability, business impact, and ethical considerations over just model accuracy."
                    ]
                }
            },
            "research_methodology": {
                "name": "Research Methodology",
                "keywords": ["research", "methodology", "hypothesis", "experiment", "analysis", "statistics", "data collection", "literature review", "sampling", "validity", "reliability", "bias", "confounding", "causation", "correlation", "significance", "p-value", "confidence interval"],
                "phd_level_topics": {
                    "experimental_design": {
                        "why": "Proper experimental design ensures valid and reliable results",
                        "who": "Researchers, statisticians, and methodologists",
                        "what": "Randomized controlled trials, quasi-experiments, and observational studies",
                        "where": "Academic research, clinical trials, and social science studies",
                        "when": "During research planning, data collection, and analysis phases",
                        "how": "Through randomization, control groups, and statistical analysis"
                    },
                    "statistical_analysis": {
                        "why": "Statistical analysis provides evidence for research conclusions",
                        "who": "Statisticians, researchers, and data analysts",
                        "what": "Hypothesis testing, regression analysis, and multivariate methods",
                        "where": "Research studies, surveys, and experimental data",
                        "when": "After data collection and during analysis phases",
                        "how": "Through statistical software, model fitting, and significance testing"
                    }
                }
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
        """Setup the comprehensive user interface"""
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
            text="Start Interview",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            command=self.toggle_listening,
            width=15,
            height=2
        )
        self.listen_btn.pack(side='left', padx=5)
        
        self.analyze_btn = tk.Button(
            button_frame,
            text="Analyze Interview",
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='#ffffff',
            command=self.analyze_interview,
            width=15,
            height=2
        )
        self.analyze_btn.pack(side='left', padx=5)
        
        self.report_btn = tk.Button(
            button_frame,
            text="Generate Report",
            font=('Arial', 12, 'bold'),
            bg='#FF9800',
            fg='#ffffff',
            command=self.generate_report,
            width=15,
            height=2
        )
        self.report_btn.pack(side='left', padx=5)
        
        # Status and metrics
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
        
        # Interview metrics
        metrics_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        metrics_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            metrics_frame,
            text="Interview Metrics:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        self.metrics_label = tk.Label(
            metrics_frame,
            text="Duration: 0:00 | Questions: 0 | Sentiment: Neutral | Confidence: 0%",
            font=('Arial', 9),
            bg='#ffffff',
            fg='#666666'
        )
        self.metrics_label.pack(anchor='w', padx=10, pady=(0, 5))
        
        # Notes area
        notes_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        notes_frame.pack(fill='both', expand=True)
        
        tk.Label(
            notes_frame,
            text="Live Intelligence & Analysis:",
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
        self.add_note("🎯 Comprehensive Interview Intelligence System Ready\n")
        self.add_note("Features: Real-time analysis, transcript generation, downloadable reports\n")
        self.add_note("PhD-level topic analysis: Why, Who, What, Where, When, How\n")
        
    def on_domain_change(self, event):
        """Handle domain selection change"""
        self.current_domain = self.domain_var.get()
        domain_info = self.domain_data[self.current_domain]
        self.add_note(f"\n📋 Domain changed to: {domain_info['name']}\n")
        self.add_note(f"💡 PhD-level analysis available for {domain_info['name']}\n")
        
    def toggle_listening(self):
        """Toggle listening mode"""
        if not self.is_listening:
            self.start_interview()
        else:
            self.end_interview()
            
    def start_interview(self):
        """Start the interview session"""
        if not self.microphone:
            self.add_note("❌ Microphone not available\n")
            return
            
        self.is_listening = True
        self.interview_start_time = datetime.now()
        self.listen_btn.configure(text="End Interview", bg='#f44336')
        self.status_label.configure(text="Status: Interview in Progress", fg='#4CAF50')
        
        self.add_note(f"\n🎤 Interview started at {self.interview_start_time.strftime('%H:%M:%S')}\n")
        self.add_note("📝 Recording transcript and analyzing responses...\n")
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
        
    def end_interview(self):
        """End the interview session"""
        self.is_listening = False
        self.interview_end_time = datetime.now()
        self.listen_btn.configure(text="Start Interview", bg='#4CAF50')
        self.status_label.configure(text="Status: Interview Complete", fg='#f44336')
        
        duration = self.interview_end_time - self.interview_start_time
        self.add_note(f"\n⏹️ Interview ended at {self.interview_end_time.strftime('%H:%M:%S')}\n")
        self.add_note(f"⏱️ Duration: {duration}\n")
        self.add_note("📊 Ready for analysis and report generation\n")
        
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
                timestamp = datetime.now()
                
                # Add to conversation history
                self.conversation_history.append({
                    'timestamp': timestamp,
                    'text': text.lower(),
                    'speaker': 'interviewer' if self.is_question(text) else 'candidate'
                })
                
                # Add to transcript
                self.interview_analysis['transcript'].append({
                    'timestamp': timestamp.strftime('%H:%M:%S'),
                    'speaker': 'Interviewer' if self.is_question(text) else 'Candidate',
                    'text': text
                })
                
                # Analyze response
                self.analyze_response(text, timestamp)
                
                # Update metrics
                self.update_metrics()
                
        except sr.UnknownValueError:
            pass
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            
    def is_question(self, text):
        """Determine if text is a question"""
        question_words = ['what', 'how', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'will', 'do', 'does', 'did']
        return any(word in text.lower().split() for word in question_words) or text.strip().endswith('?')
        
    def analyze_response(self, text, timestamp):
        """Analyze individual response"""
        text_lower = text.lower()
        
        # Sentiment analysis
        sentiment = self.analyze_sentiment(text_lower)
        self.interview_analysis['sentiment_scores'].append({
            'timestamp': timestamp,
            'sentiment': sentiment,
            'text': text
        })
        
        # Confidence analysis
        confidence = self.analyze_confidence(text_lower)
        self.interview_analysis['confidence_ratings'].append({
            'timestamp': timestamp,
            'confidence': confidence,
            'text': text
        })
        
        # Topic analysis
        self.analyze_topics(text_lower, timestamp)
        
        # PhD-level analysis
        self.analyze_phd_topics(text_lower, timestamp)
        
        # Display analysis
        self.add_note(f"\n🎯 Analysis: {text}\n")
        self.add_note(f"😊 Sentiment: {sentiment.capitalize()}\n")
        self.add_note(f"💪 Confidence: {confidence}%\n")
        
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        positive_words = ['great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'good', 'positive', 'successful', 'happy', 'excited', 'confident', 'strong', 'impressive']
        negative_words = ['bad', 'terrible', 'awful', 'difficult', 'challenging', 'problem', 'issue', 'concern', 'worried', 'frustrated', 'weak', 'poor', 'unsure']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
            
    def analyze_confidence(self, text):
        """Analyze confidence level in response"""
        confidence_indicators = {
            'high': ['definitely', 'certainly', 'absolutely', 'clearly', 'obviously', 'without doubt', 'confident', 'sure'],
            'medium': ['probably', 'likely', 'maybe', 'perhaps', 'possibly', 'think', 'believe'],
            'low': ['unsure', 'uncertain', 'doubt', 'maybe not', 'not sure', 'don\'t know']
        }
        
        score = 50  # Base confidence
        
        for level, words in confidence_indicators.items():
            count = sum(1 for word in words if word in text)
            if level == 'high':
                score += count * 20
            elif level == 'medium':
                score += count * 5
            elif level == 'low':
                score -= count * 15
                
        return max(0, min(100, score))
        
    def analyze_topics(self, text, timestamp):
        """Analyze topics covered in response"""
        domain_info = self.domain_data[self.current_domain]
        
        for keyword in domain_info['keywords']:
            if keyword in text:
                if keyword not in self.interview_analysis['topic_coverage']:
                    self.interview_analysis['topic_coverage'][keyword] = []
                    
                self.interview_analysis['topic_coverage'][keyword].append({
                    'timestamp': timestamp,
                    'context': text
                })
                
    def analyze_phd_topics(self, text, timestamp):
        """Analyze PhD-level topics (Why, Who, What, Where, When, How)"""
        for topic_type, analysis in self.phd_topics.items():
            if any(word in text for word in analysis['questions']):
                self.add_note(f"\n🎓 PhD Analysis - {topic_type.upper()}:\n")
                self.add_note(f"   Purpose: {analysis['purpose']}\n")
                self.add_note(f"   Framework: {', '.join(analysis['analysis_framework'][:3])}\n")
                
    def update_metrics(self):
        """Update interview metrics display"""
        if self.interview_start_time:
            duration = datetime.now() - self.interview_start_time
            duration_str = f"{duration.seconds // 60}:{duration.seconds % 60:02d}"
        else:
            duration_str = "0:00"
            
        question_count = len([entry for entry in self.conversation_history if entry['speaker'] == 'interviewer'])
        
        if self.interview_analysis['sentiment_scores']:
            recent_sentiments = [score['sentiment'] for score in self.interview_analysis['sentiment_scores'][-5:]]
            sentiment = max(set(recent_sentiments), key=recent_sentiments.count)
        else:
            sentiment = "Neutral"
            
        if self.interview_analysis['confidence_ratings']:
            avg_confidence = sum(rating['confidence'] for rating in self.interview_analysis['confidence_ratings']) / len(self.interview_analysis['confidence_ratings'])
        else:
            avg_confidence = 0
            
        metrics_text = f"Duration: {duration_str} | Questions: {question_count} | Sentiment: {sentiment.capitalize()} | Confidence: {avg_confidence:.0f}%"
        self.metrics_label.configure(text=metrics_text)
        
    def analyze_interview(self):
        """Perform comprehensive interview analysis"""
        if not self.interview_analysis['transcript']:
            messagebox.showwarning("No Data", "No interview data to analyze. Please conduct an interview first.")
            return
            
        self.add_note("\n📊 COMPREHENSIVE INTERVIEW ANALYSIS\n")
        self.add_note("=" * 50 + "\n")
        
        # Overall statistics
        total_responses = len(self.interview_analysis['transcript'])
        questions_asked = len([entry for entry in self.interview_analysis['transcript'] if entry['speaker'] == 'Interviewer'])
        
        self.add_note(f"📈 Overall Statistics:\n")
        self.add_note(f"   Total responses: {total_responses}\n")
        self.add_note(f"   Questions asked: {questions_asked}\n")
        
        # Sentiment analysis
        sentiments = [score['sentiment'] for score in self.interview_analysis['sentiment_scores']]
        sentiment_distribution = {sentiment: sentiments.count(sentiment) for sentiment in set(sentiments)}
        
        self.add_note(f"😊 Sentiment Analysis:\n")
        for sentiment, count in sentiment_distribution.items():
            percentage = (count / len(sentiments)) * 100
            self.add_note(f"   {sentiment.capitalize()}: {count} ({percentage:.1f}%)\n")
            
        # Confidence analysis
        confidences = [rating['confidence'] for rating in self.interview_analysis['confidence_ratings']]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        self.add_note(f"💪 Confidence Analysis:\n")
        self.add_note(f"   Average confidence: {avg_confidence:.1f}%\n")
        self.add_note(f"   High confidence responses: {len([c for c in confidences if c >= 70])}\n")
        self.add_note(f"   Low confidence responses: {len([c for c in confidences if c <= 30])}\n")
        
        # Topic coverage
        self.add_note(f"🎯 Topic Coverage:\n")
        for topic, entries in self.interview_analysis['topic_coverage'].items():
            self.add_note(f"   {topic}: {len(entries)} mentions\n")
            
        # Overall rating
        self.interview_analysis['overall_rating'] = self.calculate_overall_rating()
        self.add_note(f"⭐ Overall Rating: {self.interview_analysis['overall_rating']:.1f}/10\n")
        
    def calculate_overall_rating(self):
        """Calculate overall interview rating"""
        if not self.interview_analysis['sentiment_scores'] or not self.interview_analysis['confidence_ratings']:
            return 0
            
        # Sentiment score (0-10)
        sentiments = [score['sentiment'] for score in self.interview_analysis['sentiment_scores']]
        positive_ratio = sentiments.count('positive') / len(sentiments)
        sentiment_score = positive_ratio * 10
        
        # Confidence score (0-10)
        confidences = [rating['confidence'] for rating in self.interview_analysis['confidence_ratings']]
        avg_confidence = sum(confidences) / len(confidences)
        confidence_score = avg_confidence / 10
        
        # Topic coverage score (0-10)
        topic_score = min(len(self.interview_analysis['topic_coverage']) * 2, 10)
        
        # Overall rating
        overall = (sentiment_score + confidence_score + topic_score) / 3
        return overall
        
    def generate_report(self):
        """Generate comprehensive interview report"""
        if not self.interview_analysis['transcript']:
            messagebox.showwarning("No Data", "No interview data to report. Please conduct an interview first.")
            return
            
        # Ask user for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".zip",
            filetypes=[("ZIP files", "*.zip")],
            title="Save Interview Report"
        )
        
        if not filename:
            return
            
        try:
            # Create report directory
            report_dir = filename.replace('.zip', '_report')
            os.makedirs(report_dir, exist_ok=True)
            
            # Generate transcript
            self.generate_transcript_file(report_dir)
            
            # Generate analysis report
            self.generate_analysis_report(report_dir)
            
            # Generate metrics CSV
            self.generate_metrics_csv(report_dir)
            
            # Create ZIP file
            with zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(report_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, report_dir)
                        zipf.write(file_path, arcname)
                        
            # Clean up
            import shutil
            shutil.rmtree(report_dir)
            
            messagebox.showinfo("Success", f"Interview report generated successfully!\nSaved as: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report: {str(e)}")
            
    def generate_transcript_file(self, report_dir):
        """Generate transcript file"""
        transcript_file = os.path.join(report_dir, "interview_transcript.txt")
        
        with open(transcript_file, 'w') as f:
            f.write("INTERVIEW TRANSCRIPT\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in self.interview_analysis['transcript']:
                f.write(f"[{entry['timestamp']}] {entry['speaker']}: {entry['text']}\n\n")
                
    def generate_analysis_report(self, report_dir):
        """Generate analysis report"""
        report_file = os.path.join(report_dir, "interview_analysis.html")
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Interview Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; background-color: #e8f4fd; border-radius: 5px; }}
                .rating {{ font-size: 24px; color: #4CAF50; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Interview Analysis Report</h1>
                <p>Domain: {self.domain_data[self.current_domain]['name']}</p>
                <p>Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Overall Rating</h2>
                <div class="rating">{self.interview_analysis['overall_rating']:.1f}/10</div>
            </div>
            
            <div class="section">
                <h2>Interview Statistics</h2>
                <div class="metric">
                    <strong>Total Responses:</strong><br>
                    {len(self.interview_analysis['transcript'])}
                </div>
                <div class="metric">
                    <strong>Questions Asked:</strong><br>
                    {len([entry for entry in self.interview_analysis['transcript'] if entry['speaker'] == 'Interviewer'])}
                </div>
                <div class="metric">
                    <strong>Duration:</strong><br>
                    {self.interview_end_time - self.interview_start_time if self.interview_end_time else 'N/A'}
                </div>
            </div>
            
            <div class="section">
                <h2>Sentiment Analysis</h2>
                {self.generate_sentiment_html()}
            </div>
            
            <div class="section">
                <h2>Confidence Analysis</h2>
                {self.generate_confidence_html()}
            </div>
            
            <div class="section">
                <h2>Topic Coverage</h2>
                {self.generate_topic_html()}
            </div>
        </body>
        </html>
        """
        
        with open(report_file, 'w') as f:
            f.write(html_content)
            
    def generate_sentiment_html(self):
        """Generate sentiment analysis HTML"""
        sentiments = [score['sentiment'] for score in self.interview_analysis['sentiment_scores']]
        sentiment_distribution = {sentiment: sentiments.count(sentiment) for sentiment in set(sentiments)}
        
        html = ""
        for sentiment, count in sentiment_distribution.items():
            percentage = (count / len(sentiments)) * 100
            color = "#4CAF50" if sentiment == "positive" else "#f44336" if sentiment == "negative" else "#FF9800"
            html += f'<div class="metric" style="background-color: {color}; color: white;">{sentiment.capitalize()}: {count} ({percentage:.1f}%)</div>'
            
        return html
        
    def generate_confidence_html(self):
        """Generate confidence analysis HTML"""
        confidences = [rating['confidence'] for rating in self.interview_analysis['confidence_ratings']]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return f"""
        <div class="metric">
            <strong>Average Confidence:</strong><br>
            {avg_confidence:.1f}%
        </div>
        <div class="metric">
            <strong>High Confidence (≥70%):</strong><br>
            {len([c for c in confidences if c >= 70])} responses
        </div>
        <div class="metric">
            <strong>Low Confidence (≤30%):</strong><br>
            {len([c for c in confidences if c <= 30])} responses
        </div>
        """
        
    def generate_topic_html(self):
        """Generate topic coverage HTML"""
        html = ""
        for topic, entries in self.interview_analysis['topic_coverage'].items():
            html += f'<div class="metric">{topic}: {len(entries)} mentions</div>'
        return html
        
    def generate_metrics_csv(self, report_dir):
        """Generate metrics CSV file"""
        csv_file = os.path.join(report_dir, "interview_metrics.csv")
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Speaker', 'Text', 'Sentiment', 'Confidence'])
            
            for i, entry in enumerate(self.interview_analysis['transcript']):
                sentiment = self.interview_analysis['sentiment_scores'][i]['sentiment'] if i < len(self.interview_analysis['sentiment_scores']) else 'N/A'
                confidence = self.interview_analysis['confidence_ratings'][i]['confidence'] if i < len(self.interview_analysis['confidence_ratings']) else 0
                
                writer.writerow([entry['timestamp'], entry['speaker'], entry['text'], sentiment, confidence])
                
    def add_note(self, text):
        """Add note to the text area"""
        self.notes_text.insert(tk.END, text)
        self.notes_text.see(tk.END)
        
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Comprehensive Interview Intelligence System")
    print("=" * 75)
    print("🎯 Target: Live Interviews with Advanced Analysis")
    print("⚡ Real-time teleprompter with transcript analysis")
    print("📊 Comprehensive reports with ratings and sentiment analysis")
    print("🎓 PhD-level topic analysis: Why, Who, What, Where, When, How")
    print("=" * 75)
    print("🚀 Starting Comprehensive Interview Intelligence...")
    print("💡 A 'Meeting Notes' window will appear")
    print("🎤 Start interview, analyze responses, generate reports")
    print("📈 Get detailed ratings, sentiment analysis, and downloadable reports")
    print("🎓 Access PhD-level topic analysis for any domain")
    print("=" * 75)
    
    # Check for speech recognition
    try:
        import speech_recognition as sr
    except ImportError:
        print("❌ Speech recognition not available.")
        print("Install with: pip install SpeechRecognition pyaudio")
        return
        
    intelligence_system = ComprehensiveInterviewIntelligence()
    intelligence_system.run()

if __name__ == "__main__":
    main()
