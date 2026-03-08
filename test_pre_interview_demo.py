#!/usr/bin/env python3
"""
Test Demo - Pre-Interview Analysis Capabilities
Demonstrates the pre-interview analysis features
"""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

class PreInterviewDemo:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Pre-Interview Analysis Demo")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Demo data
        self.demo_company = "TechCorp Solutions"
        self.demo_position = "Senior Software Engineer"
        self.demo_interviewer = "Sarah Johnson"
        self.demo_industry = "Technology"
        self.demo_location = "San Francisco, CA"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the demo interface"""
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        header_frame.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header_frame,
            text="Pre-Interview Analysis Demo",
            font=('Arial', 16, 'bold'),
            bg='#ffffff',
            fg='#333333'
        )
        title.pack(pady=10)
        
        # Demo info
        info_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        info_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            info_frame,
            text="Demo Data:",
            font=('Arial', 12, 'bold'),
            bg='#ffffff'
        ).pack(anchor='w', padx=10, pady=(5, 0))
        
        demo_text = f"""
Company: {self.demo_company}
Position: {self.demo_position}
Interviewer: {self.demo_interviewer}
Industry: {self.demo_industry}
Location: {self.demo_location}
        """
        
        tk.Label(
            info_frame,
            text=demo_text,
            font=('Arial', 10),
            bg='#ffffff',
            justify='left'
        ).pack(anchor='w', padx=10, pady=(0, 5))
        
        # Analysis buttons
        button_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        button_frame.pack(fill='x', pady=(0, 10))
        
        self.analyze_company_btn = tk.Button(
            button_frame,
            text="Analyze Company Background",
            font=('Arial', 12, 'bold'),
            bg='#4CAF50',
            fg='#ffffff',
            command=self.analyze_company_demo,
            width=25,
            height=2
        )
        self.analyze_company_btn.pack(side='left', padx=10, pady=10)
        
        self.analyze_interviewer_btn = tk.Button(
            button_frame,
            text="Analyze Interviewer",
            font=('Arial', 12, 'bold'),
            bg='#2196F3',
            fg='#ffffff',
            command=self.analyze_interviewer_demo,
            width=20,
            height=2
        )
        self.analyze_interviewer_btn.pack(side='left', padx=10, pady=10)
        
        self.recommendations_btn = tk.Button(
            button_frame,
            text="Generate Recommendations",
            font=('Arial', 12, 'bold'),
            bg='#FF9800',
            fg='#ffffff',
            command=self.generate_recommendations_demo,
            width=25,
            height=2
        )
        self.recommendations_btn.pack(side='left', padx=10, pady=10)
        
        # Results area
        results_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        results_frame.pack(fill='both', expand=True)
        
        tk.Label(
            results_frame,
            text="Analysis Results:",
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            fg='#333333'
        ).pack(pady=(10, 5))
        
        # Results text area
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            font=('Arial', 11),
            bg='#f8f8f8',
            fg='#333333',
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.results_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # Add initial content
        self.add_result("🎯 Pre-Interview Analysis Demo Ready\n")
        self.add_result("Click the buttons above to see analysis capabilities\n")
        self.add_result("This demonstrates the pre-interview research features\n")
        
    def analyze_company_demo(self):
        """Demo company analysis"""
        self.add_result("\n🔍 COMPANY BACKGROUND ANALYSIS\n")
        self.add_result("=" * 50 + "\n")
        
        self.add_result("🏢 COMPANY PROFILE:\n")
        self.add_result(f"Company: {self.demo_company}\n")
        self.add_result("Founded: 2018\n")
        self.add_result("Size: 150-300 employees\n")
        self.add_result("Funding: Series C ($50M)\n")
        self.add_result("Revenue: $25M-$50M\n")
        self.add_result("Growth: High growth (200% YoY)\n")
        self.add_result("Culture: Innovative, fast-paced, remote-first\n")
        self.add_result("Benefits: Competitive health, 401k, equity, unlimited PTO\n")
        
        self.add_result("\n📊 MARKET POSITION:\n")
        self.add_result("Industry: Enterprise SaaS\n")
        self.add_result("Competitors: Salesforce, HubSpot, Pipedrive\n")
        self.add_result("Market Share: Growing rapidly in mid-market segment\n")
        self.add_result("Recent News: Series C funding, product expansion\n")
        
        self.add_result("\n💼 POSITION ANALYSIS:\n")
        self.add_result(f"Role: {self.demo_position}\n")
        self.add_result("Level: Senior (5-8 years experience)\n")
        self.add_result("Salary Range: $140K-$180K base + equity\n")
        self.add_result("Tech Stack: Python, React, AWS, Kubernetes\n")
        self.add_result("Team Size: 8-12 engineers\n")
        
    def analyze_interviewer_demo(self):
        """Demo interviewer analysis"""
        self.add_result("\n👤 INTERVIEWER ANALYSIS\n")
        self.add_result("=" * 50 + "\n")
        
        self.add_result("📋 INTERVIEWER PROFILE:\n")
        self.add_result(f"Name: {self.demo_interviewer}\n")
        self.add_result("Role: Engineering Manager\n")
        self.add_result("Experience: 12+ years in software engineering\n")
        self.add_result("Background: Ex-Google, Stanford CS graduate\n")
        self.add_result("Specialties: Backend systems, scalability, team leadership\n")
        
        self.add_result("\n🎯 INTERVIEW STYLE:\n")
        self.add_result("Approach: Technical + behavioral questions\n")
        self.add_result("Focus: System design, problem-solving, leadership\n")
        self.add_result("Communication: Direct, values clear explanations\n")
        self.add_result("Decision Power: High - hiring manager\n")
        
        self.add_result("\n🔍 INTERVIEW PATTERNS:\n")
        self.add_result("• Starts with technical deep-dive\n")
        self.add_result("• Asks about leadership experience\n")
        self.add_result("• Values specific examples and metrics\n")
        self.add_result("• Interested in growth and learning\n")
        
    def generate_recommendations_demo(self):
        """Demo recommendations generation"""
        self.add_result("\n💡 INTELLIGENT RECOMMENDATIONS\n")
        self.add_result("=" * 50 + "\n")
        
        self.add_result("🎯 INTERVIEW PREPARATION:\n")
        self.add_result("• Research TechCorp's recent product launches\n")
        self.add_result("• Prepare system design examples (scalability focus)\n")
        self.add_result("• Review Python, React, AWS, Kubernetes\n")
        self.add_result("• Prepare leadership and mentoring examples\n")
        self.add_result("• Study their competitive landscape\n")
        
        self.add_result("\n💬 DIALOGUE SUGGESTIONS:\n")
        self.add_result("💭 'I'm excited about TechCorp's growth in the enterprise space'\n")
        self.add_result("💭 'How does the engineering team handle rapid scaling?'\n")
        self.add_result("💭 'What opportunities exist for technical leadership?'\n")
        self.add_result("💭 'How does the team approach system architecture decisions?'\n")
        
        self.add_result("\n💰 SALARY NEGOTIATION:\n")
        self.add_result("• Target Range: $150K-$170K base\n")
        self.add_result("• Emphasize: Technical leadership, scalability experience\n")
        self.add_result("• Discuss: Equity package, vesting schedule\n")
        self.add_result("• Request: Signing bonus, performance bonuses\n")
        self.add_result("• Negotiate: Additional PTO, remote flexibility\n")
        
        self.add_result("\n📋 OFFER CONSIDERATIONS:\n")
        self.add_result("• Request 2-3 weeks to consider\n")
        self.add_result("• Ask about career growth opportunities\n")
        self.add_result("• Discuss team structure and reporting\n")
        self.add_result("• Inquire about professional development budget\n")
        
    def add_result(self, text):
        """Add result to the text area"""
        self.results_text.insert(tk.END, text)
        self.results_text.see(tk.END)
        
    def run(self):
        """Start the demo"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Pre-Interview Analysis Demo")
    print("=" * 60)
    print("🎯 Target: Demonstrate Pre-Interview Analysis Capabilities")
    print("⚡ Company and interviewer background analysis")
    print("💡 Intelligent recommendations and dialogue suggestions")
    print("💰 Salary negotiation and offer recommendations")
    print("=" * 60)
    print("🚀 Starting Pre-Interview Analysis Demo...")
    print("💡 A demo window will appear")
    print("🔍 Click buttons to see analysis capabilities")
    print("📊 Demonstrates pre-interview research features")
    print("=" * 60)
    
    demo = PreInterviewDemo()
    demo.run()

if __name__ == "__main__":
    main()
