#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Outlier Stealth Master System
Comprehensive stealth assistance for all Outlier skill screenings
Designed for highly proctored camera environments
"""
import tkinter as tk
from tkinter import ttk
import json
import time
import threading
from datetime import datetime
import random

class OutlierStealthMaster:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Monitor")
        self.root.geometry("350x500")
        self.root.configure(bg='#f0f0f0')
        
        # Advanced stealth features for proctored environment
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', False)
        
        # Position strategically for camera avoidance
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"350x500+{screen_width-370}+{screen_height-550}")
        
        # Skill test data
        self.current_skill = "git"
        self.skill_data = self.load_skill_data()
        
        # Stealth mode
        self.stealth_mode = "system_monitor"  # system_monitor, calculator, notes
        self.setup_ui()
        
    def load_skill_data(self):
        """Load comprehensive skill test data"""
        return {
            "git": {
                "name": "Git",
                "difficulty": "Easy",
                "duration": "15-20 minutes",
                "questions": [
                    "What command initializes a new Git repository?",
                    "How do you stage all changes for commit?",
                    "What command creates and switches to a new branch?",
                    "How do you undo the last commit?",
                    "What command shows the status of your repository?",
                    "How do you merge changes from another branch?",
                    "What command pushes changes to remote repository?",
                    "How do you view commit history?",
                    "What command discards changes in working directory?",
                    "How do you rename a branch?"
                ],
                "answers": [
                    "git init",
                    "git add .",
                    "git checkout -b <branch-name>",
                    "git reset --hard HEAD~1",
                    "git status",
                    "git merge <branch-name>",
                    "git push",
                    "git log",
                    "git checkout -- <file>",
                    "git branch -m <old-name> <new-name>"
                ],
                "scenarios": [
                    "You accidentally committed wrong changes. How to undo?",
                    "You need to save work in progress before switching branches.",
                    "You want to see what files have been modified.",
                    "You need to get latest changes from remote repository."
                ],
                "scenario_answers": [
                    "git reset --hard HEAD~1",
                    "git stash",
                    "git status",
                    "git pull"
                ]
            },
            "docker": {
                "name": "Docker",
                "difficulty": "Medium",
                "duration": "20-25 minutes",
                "questions": [
                    "What command builds a Docker image?",
                    "How do you run a container in detached mode?",
                    "What command lists running containers?",
                    "How do you stop a running container?",
                    "What command removes all stopped containers?",
                    "How do you view container logs?",
                    "What command maps a port from container to host?",
                    "How do you execute commands in a running container?",
                    "What command creates a Docker network?",
                    "How do you copy files from host to container?"
                ],
                "answers": [
                    "docker build -t <image-name> .",
                    "docker run -d <image-name>",
                    "docker ps",
                    "docker stop <container-id>",
                    "docker container prune",
                    "docker logs <container-id>",
                    "docker run -p <host-port>:<container-port> <image>",
                    "docker exec -it <container-id> /bin/bash",
                    "docker network create <network-name>",
                    "docker cp <host-file> <container-id>:<container-path>"
                ]
            },
            "sql": {
                "name": "SQL",
                "difficulty": "Medium",
                "duration": "20-25 minutes",
                "questions": [
                    "How do you select all columns from a table?",
                    "What clause filters results?",
                    "How do you join two tables?",
                    "What function counts rows?",
                    "How do you group results?",
                    "What clause sorts results?",
                    "How do you insert data into a table?",
                    "What command updates existing data?",
                    "How do you delete rows from a table?",
                    "What clause limits results?"
                ],
                "answers": [
                    "SELECT * FROM table_name",
                    "WHERE",
                    "SELECT * FROM table1 JOIN table2 ON table1.id = table2.id",
                    "COUNT()",
                    "GROUP BY",
                    "ORDER BY",
                    "INSERT INTO table_name VALUES (value1, value2)",
                    "UPDATE table_name SET column = value WHERE condition",
                    "DELETE FROM table_name WHERE condition",
                    "LIMIT"
                ]
            },
            "javascript": {
                "name": "JavaScript",
                "difficulty": "Medium",
                "duration": "25-30 minutes",
                "questions": [
                    "How do you declare a variable?",
                    "What is the difference between == and ===?",
                    "How do you create an array?",
                    "What method adds elements to array end?",
                    "How do you create an object?",
                    "What is a callback function?",
                    "How do you handle asynchronous operations?",
                    "What is the spread operator?",
                    "How do you destructure an object?",
                    "What is a closure?"
                ],
                "answers": [
                    "let, const, or var",
                    "== checks value, === checks value and type",
                    "const arr = [] or const arr = new Array()",
                    "push()",
                    "const obj = {} or const obj = new Object()",
                    "Function passed as argument to another function",
                    "async/await or Promises",
                    "... (three dots)",
                    "const {prop1, prop2} = object",
                    "Function with access to variables in outer scope"
                ]
            },
            "python": {
                "name": "Python",
                "difficulty": "Medium",
                "duration": "25-30 minutes",
                "questions": [
                    "How do you create a list?",
                    "What is list comprehension?",
                    "How do you handle exceptions?",
                    "What is a decorator?",
                    "How do you create a virtual environment?",
                    "What is the difference between list and tuple?",
                    "How do you read a file?",
                    "What is a generator?",
                    "How do you import modules?",
                    "What is the GIL?"
                ],
                "answers": [
                    "my_list = [] or my_list = list()",
                    "[expression for item in iterable]",
                    "try/except/finally",
                    "Function that modifies another function",
                    "python -m venv env_name",
                    "List is mutable, tuple is immutable",
                    "with open('file.txt', 'r') as f: content = f.read()",
                    "Function using yield instead of return",
                    "import module or from module import function",
                    "Global Interpreter Lock - Python's threading limitation"
                ]
            },
            "java": {
                "name": "Java",
                "difficulty": "Hard",
                "duration": "30-35 minutes",
                "questions": [
                    "What is the main method signature?",
                    "How do you create an object?",
                    "What is inheritance?",
                    "How do you handle exceptions?",
                    "What is the difference between == and equals()?",
                    "How do you create a thread?",
                    "What is polymorphism?",
                    "How do you implement an interface?",
                    "What is the garbage collector?",
                    "How do you read from a file?"
                ],
                "answers": [
                    "public static void main(String[] args)",
                    "ClassName obj = new ClassName()",
                    "Class inheriting properties from another class",
                    "try/catch/finally",
                    "== compares references, equals() compares content",
                    "extends Thread or implements Runnable",
                    "Same interface, different implementations",
                    "class MyClass implements InterfaceName",
                    "Automatic memory management system",
                    "FileReader, BufferedReader, or Scanner"
                ]
            },
            "data_science": {
                "name": "Data Science",
                "difficulty": "Hard",
                "duration": "35-40 minutes",
                "questions": [
                    "What is overfitting?",
                    "How do you handle missing data?",
                    "What is cross-validation?",
                    "How do you normalize data?",
                    "What is the bias-variance tradeoff?",
                    "How do you select features?",
                    "What is regularization?",
                    "How do you evaluate classification models?",
                    "What is dimensionality reduction?",
                    "How do you handle imbalanced datasets?"
                ],
                "answers": [
                    "Model performs well on training data but poorly on new data",
                    "Remove rows, impute values, or use algorithms that handle missing data",
                    "Technique to assess model performance on unseen data",
                    "Scale features to same range (0-1 or standard normal)",
                    "Balance between model complexity and generalization",
                    "Feature selection, feature importance, or domain knowledge",
                    "Technique to prevent overfitting (L1/L2 regularization)",
                    "Accuracy, precision, recall, F1-score, ROC-AUC",
                    "Reduce number of features while preserving information",
                    "Oversampling, undersampling, or using balanced algorithms"
                ]
            },
            "mathematical_reasoning": {
                "name": "Mathematical Reasoning",
                "difficulty": "Very Hard",
                "duration": "40-45 minutes",
                "questions": [
                    "What is the derivative of x²?",
                    "How do you solve a quadratic equation?",
                    "What is the probability of rolling a 6 on a fair die?",
                    "How do you calculate compound interest?",
                    "What is the area of a circle?",
                    "How do you find the mean of a dataset?",
                    "What is the standard deviation formula?",
                    "How do you solve a system of linear equations?",
                    "What is the binomial theorem?",
                    "How do you calculate correlation coefficient?"
                ],
                "answers": [
                    "2x",
                    "ax² + bx + c = 0, x = (-b ± √(b² - 4ac)) / 2a",
                    "1/6",
                    "A = P(1 + r/n)^(nt)",
                    "πr²",
                    "Sum of all values divided by number of values",
                    "√(Σ(x - μ)² / n)",
                    "Substitution, elimination, or matrix methods",
                    "(a + b)^n = Σ(n choose k) * a^(n-k) * b^k",
                    "r = Σ((x-x̄)(y-ȳ)) / √(Σ(x-x̄)² * Σ(y-ȳ)²)"
                ]
            }
        }
        
    def setup_ui(self):
        """Setup the UI based on current stealth mode"""
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()
            
        if self.stealth_mode == "system_monitor":
            self.setup_system_monitor_ui()
        elif self.stealth_mode == "calculator":
            self.setup_calculator_ui()
        elif self.stealth_mode == "notes":
            self.setup_notes_ui()
            
    def setup_system_monitor_ui(self):
        """Setup System Monitor UI (looks like system monitoring tool)"""
        self.root.title("System Monitor")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Label(
            main_frame,
            text="System Monitor v2.1",
            font=('Arial', 14, 'bold'),
            bg='#f0f0f0',
            fg='#333333'
        )
        header.pack(pady=(0, 10))
        
        # CPU Usage
        cpu_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        cpu_frame.pack(fill='x', pady=2)
        
        tk.Label(cpu_frame, text="CPU Usage:", font=('Arial', 10, 'bold'), bg='#ffffff').pack(anchor='w', padx=5, pady=2)
        self.cpu_bar = tk.Frame(cpu_frame, bg='#4CAF50', height=20)
        self.cpu_bar.pack(fill='x', padx=5, pady=(0, 5))
        
        # Memory Usage
        mem_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        mem_frame.pack(fill='x', pady=2)
        
        tk.Label(mem_frame, text="Memory Usage:", font=('Arial', 10, 'bold'), bg='#ffffff').pack(anchor='w', padx=5, pady=2)
        self.mem_bar = tk.Frame(mem_frame, bg='#2196F3', height=20)
        self.mem_bar.pack(fill='x', padx=5, pady=(0, 5))
        
        # Network Status
        net_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        net_frame.pack(fill='x', pady=2)
        
        tk.Label(net_frame, text="Network Status:", font=('Arial', 10, 'bold'), bg='#ffffff').pack(anchor='w', padx=5, pady=2)
        tk.Label(net_frame, text="Connected - 1.2 Gbps", font=('Arial', 9), bg='#ffffff', fg='#4CAF50').pack(anchor='w', padx=5, pady=(0, 5))
        
        # Process List (hidden skill assistance)
        process_frame = tk.Frame(main_frame, bg='#ffffff', relief='raised', bd=1)
        process_frame.pack(fill='both', expand=True, pady=2)
        
        tk.Label(process_frame, text="Active Processes:", font=('Arial', 10, 'bold'), bg='#ffffff').pack(anchor='w', padx=5, pady=2)
        
        # Process list with skill assistance
        self.process_text = tk.Text(
            process_frame,
            height=8,
            font=('Courier', 8),
            bg='#f8f8f8',
            fg='#333333',
            relief='sunken',
            bd=1
        )
        self.process_text.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        # Add skill assistance to process list
        self.update_process_list()
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='x', pady=10)
        
        tk.Button(
            button_frame,
            text="Refresh",
            command=self.refresh_system_monitor,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9)
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Switch Mode",
            command=self.switch_stealth_mode,
            bg='#2196F3',
            fg='white',
            font=('Arial', 9)
        ).pack(side='right', padx=5)
        
    def setup_calculator_ui(self):
        """Setup Calculator UI (looks like a real calculator)"""
        self.root.title("Calculator")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Display
        self.calc_display = tk.Label(
            main_frame,
            text="0",
            font=('Courier', 20, 'bold'),
            bg='#1a1a1a',
            fg='#00ff00',
            anchor='e',
            padx=10,
            pady=10
        )
        self.calc_display.pack(fill='x', pady=(0, 10))
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#2b2b2b')
        buttons_frame.pack(fill='both', expand=True)
        
        # Calculator buttons
        calc_buttons = [
            ['7', '8', '9', '/'],
            ['4', '5', '6', '*'],
            ['1', '2', '3', '-'],
            ['0', '.', '=', '+']
        ]
        
        for i, row in enumerate(calc_buttons):
            for j, text in enumerate(row):
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    font=('Arial', 12, 'bold'),
                    bg='#333333' if text.isdigit() or text == '.' else '#ff9500',
                    fg='white',
                    width=6,
                    height=2,
                    command=lambda t=text: self.calculator_button_click(t)
                )
                btn.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
        
        # Configure grid
        for i in range(4):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
            
    def setup_notes_ui(self):
        """Setup Notes UI (looks like a simple notes app)"""
        self.root.title("Notes")
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#f5f5f5')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        header = tk.Label(
            main_frame,
            text="Quick Notes",
            font=('Arial', 14, 'bold'),
            bg='#f5f5f5',
            fg='#333333'
        )
        header.pack(pady=(0, 10))
        
        # Notes area
        self.notes_text = tk.Text(
            main_frame,
            font=('Arial', 10),
            bg='#ffffff',
            fg='#333333',
            relief='sunken',
            bd=1,
            wrap='word'
        )
        self.notes_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Add some initial notes
        self.notes_text.insert('1.0', "Meeting Notes:\n- Project deadline: Friday\n- Team sync: 2 PM\n- Review pending tasks\n\nTodo:\n- Update documentation\n- Test new features\n- Prepare presentation")
        
        # Control buttons
        button_frame = tk.Frame(main_frame, bg='#f5f5f5')
        button_frame.pack(fill='x')
        
        tk.Button(
            button_frame,
            text="Save",
            command=self.save_notes,
            bg='#4CAF50',
            fg='white',
            font=('Arial', 9)
        ).pack(side='left', padx=5)
        
        tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_notes,
            bg='#f44336',
            fg='white',
            font=('Arial', 9)
        ).pack(side='right', padx=5)
        
    def update_process_list(self):
        """Update process list with hidden skill assistance"""
        current_skill = self.skill_data[self.current_skill]
        
        # Create fake process list with skill assistance embedded
        processes = [
            "chrome.exe - 1,234 MB - CPU: 15%",
            "code.exe - 567 MB - CPU: 8%",
            "python.exe - 89 MB - CPU: 3%",
            "node.exe - 234 MB - CPU: 5%",
            "git.exe - 12 MB - CPU: 1%",
            "",
            f"# {current_skill['name']} Quick Ref:",
            f"# Duration: {current_skill['duration']}",
            f"# Difficulty: {current_skill['difficulty']}",
            ""
        ]
        
        # Add some key answers as "process parameters"
        for i, question in enumerate(current_skill['questions'][:3]):
            answer = current_skill['answers'][i]
            processes.append(f"# Q{i+1}: {answer}")
            
        # Add scenarios
        if 'scenarios' in current_skill:
            for i, scenario in enumerate(current_skill['scenarios'][:2]):
                answer = current_skill['scenario_answers'][i]
                processes.append(f"# Scenario {i+1}: {answer}")
        
        process_text = "\n".join(processes)
        self.process_text.delete('1.0', tk.END)
        self.process_text.insert('1.0', process_text)
        
    def refresh_system_monitor(self):
        """Refresh system monitor (updates skill assistance)"""
        # Update CPU and memory bars randomly
        import random
        cpu_width = random.randint(20, 80)
        mem_width = random.randint(30, 90)
        
        self.cpu_bar.configure(width=cpu_width)
        self.mem_bar.configure(width=mem_width)
        
        # Update process list with new skill assistance
        self.update_process_list()
        
    def switch_stealth_mode(self):
        """Switch between different stealth modes"""
        modes = ["system_monitor", "calculator", "notes"]
        current_index = modes.index(self.stealth_mode)
        next_index = (current_index + 1) % len(modes)
        self.stealth_mode = modes[next_index]
        self.setup_ui()
        
    def calculator_button_click(self, button):
        """Handle calculator button clicks"""
        # This is a fake calculator - just update display
        current = self.calc_display.cget("text")
        
        if button == "=":
            # Show skill assistance instead of calculation
            self.show_calculator_assistance()
        elif button in "0123456789":
            self.calc_display.configure(text=current + button if current != "0" else button)
        else:
            self.calc_display.configure(text="0")
            
    def show_calculator_assistance(self):
        """Show skill assistance in calculator mode"""
        current_skill = self.skill_data[self.current_skill]
        
        # Show key commands as "calculation result"
        key_answers = current_skill['answers'][:3]
        display_text = " | ".join(key_answers)
        self.calc_display.configure(text=display_text)
        
    def save_notes(self):
        """Save notes (placeholder)"""
        pass
        
    def clear_notes(self):
        """Clear notes and show skill assistance"""
        current_skill = self.skill_data[self.current_skill]
        
        # Show skill assistance as "notes"
        notes_content = f"""
{current_skill['name']} Quick Reference:
Duration: {current_skill['duration']}
Difficulty: {current_skill['difficulty']}

Key Commands:
{chr(10).join([f"- {answer}" for answer in current_skill['answers'][:5]])}

Common Scenarios:
{chr(10).join([f"- {scenario}: {answer}" for scenario, answer in zip(current_skill.get('scenarios', []), current_skill.get('scenario_answers', []))])}
        """
        
        self.notes_text.delete('1.0', tk.END)
        self.notes_text.insert('1.0', notes_content)
        
    def set_skill(self, skill_name):
        """Set the current skill for assistance"""
        if skill_name in self.skill_data:
            self.current_skill = skill_name
            self.update_process_list()
            
    def run(self):
        """Start the stealth master system"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Outlier Stealth Master System")
    print("=" * 60)
    print("🎯 Target: All Outlier Skill Screenings")
    print("⚡ Advanced stealth for proctored environments")
    print("🔒 Multiple disguise modes")
    print("=" * 60)
    print("🚀 Starting Outlier Stealth Master...")
    print("💡 A 'System Monitor' window will appear")
    print("🔍 Switch between modes: System Monitor, Calculator, Notes")
    print("🔒 Designed for camera proctored environments")
    print("=" * 60)
    
    stealth_system = OutlierStealthMaster()
    stealth_system.run()

if __name__ == "__main__":
    main()
