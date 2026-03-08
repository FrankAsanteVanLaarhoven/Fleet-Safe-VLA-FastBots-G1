#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Simple Stealth Assistant
Real-time assistance during Outlier Git screening without detection
"""

import tkinter as tk
from tkinter import ttk
import time
from datetime import datetime

class GitSimpleStealth:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notes")
        self.root.geometry("350x500")
        self.root.configure(bg='#f5f5f5')
        
        # Make it look like a normal notes app
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', False)
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"350x500+{screen_width-370}+{screen_height-550}")
        
        self.setup_ui()
        self.load_git_cheatsheet()
        
    def setup_ui(self):
        """Setup the user interface to look like a normal notes app"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title - looks like a normal notes app
        title_label = tk.Label(main_frame, text="Quick Notes", 
                              font=("Arial", 12, "bold"), 
                              bg='#f5f5f5', fg='#333333')
        title_label.pack(pady=(0, 10))
        
        # Search box
        tk.Label(main_frame, text="Search Git commands:", 
                bg='#f5f5f5', fg='#333333', font=("Arial", 9)).pack(anchor='w')
        
        self.search_entry = tk.Entry(main_frame, width=40, bg='white', fg='#333333')
        self.search_entry.pack(fill='x', pady=(5, 10))
        self.search_entry.bind('<KeyRelease>', self.search_commands)
        
        # Notes area - this is where Git hints will appear
        tk.Label(main_frame, text="Git Commands:", 
                bg='#f5f5f5', fg='#333333', font=("Arial", 10, "bold")).pack(anchor='w')
        
        self.notes_text = tk.Text(main_frame, height=20, width=40, 
                                 bg='white', fg='#333333', 
                                 font=("Consolas", 9), wrap=tk.WORD)
        self.notes_text.pack(fill='both', expand=True, pady=(5, 10))
        
        # Quick buttons - look like normal app buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(5, 10))
        
        # Quick reference buttons
        quick_refs = [
            ("Basic", self.show_basic_commands),
            ("Branch", self.show_branching),
            ("Remote", self.show_remote_ops),
            ("Undo", self.show_undo_commands),
            ("Scenarios", self.show_scenarios)
        ]
        
        for i, (label, command) in enumerate(quick_refs):
            btn = tk.Button(button_frame, text=label, 
                           command=command,
                           bg='#e0e0e0', fg='#333333', 
                           font=("Arial", 9), relief='flat')
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
        
        # Configure grid weights
        for i in range(3):
            button_frame.columnconfigure(i, weight=1)
        
        # Status - looks like normal app status
        self.status_label = tk.Label(main_frame, text="Ready", 
                                    bg='#f5f5f5', fg='#666666', font=("Arial", 8))
        self.status_label.pack(pady=(5, 0))
        
        # Load cheatsheet first, then add initial content
        self.load_git_cheatsheet()
        self.show_basic_commands()
        
    def load_git_cheatsheet(self):
        """Load Git command cheatsheet"""
        self.git_cheatsheet = {
            "basic": [
                "git init          - Start new repo",
                "git add .         - Stage all files", 
                "git commit -m \"msg\" - Save changes",
                "git status        - Check state",
                "git log           - View history",
                "git diff          - Show changes"
            ],
            "branching": [
                "git branch        - List branches",
                "git checkout -b x - Create & switch",
                "git checkout x    - Switch to branch",
                "git merge x       - Merge branch",
                "git branch -d x   - Delete branch"
            ],
            "remote": [
                "git push origin x - Upload to remote",
                "git pull origin x - Download & merge",
                "git fetch origin  - Download only",
                "git remote -v     - Show remotes",
                "git clone url     - Clone repo"
            ],
            "undo": [
                "git reset --soft HEAD~1  - Undo commit, keep changes",
                "git reset --hard HEAD~1  - Undo commit, delete changes", 
                "git stash               - Save work temporarily",
                "git revert HEAD         - Create undo commit",
                "git checkout -- file    - Undo file changes"
            ],
            "scenarios": {
                "new_project": [
                    "1. git init",
                    "2. git add .", 
                    "3. git commit -m \"Initial\""
                ],
                "feature": [
                    "1. git checkout -b feature",
                    "2. git add .",
                    "3. git commit -m \"feat: add\"",
                    "4. git push -u origin feature"
                ],
                "merge": [
                    "1. git checkout main",
                    "2. git pull origin main", 
                    "3. git merge feature",
                    "4. git push origin main"
                ],
                "undo_mistake": [
                    "1. git reset --soft HEAD~1",
                    "2. Fix the mistake",
                    "3. git add .",
                    "4. git commit -m \"Fixed\""
                ]
            }
        }
        
    def search_commands(self, event=None):
        """Search through Git commands"""
        search_term = self.search_entry.get().lower()
        if not search_term:
            self.show_basic_commands()
            return
            
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, f"Search results for: '{search_term}'\n\n")
        
        found_commands = []
        
        # Search through all categories
        for category, commands in self.git_cheatsheet.items():
            if category == "scenarios":
                continue
                
            for cmd in commands:
                if search_term in cmd.lower():
                    found_commands.append(cmd)
        
        if found_commands:
            for cmd in found_commands:
                self.notes_text.insert(tk.END, cmd + "\n")
        else:
            self.notes_text.insert(tk.END, "No commands found. Try:\n")
            self.notes_text.insert(tk.END, "• init, add, commit\n")
            self.notes_text.insert(tk.END, "• branch, merge, push\n")
            self.notes_text.insert(tk.END, "• reset, stash, revert\n")
            
        self.status_label.config(text=f"Found {len(found_commands)} commands")
        
    def show_basic_commands(self):
        """Show basic Git commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "BASIC GIT COMMANDS:\n\n")
        for cmd in self.git_cheatsheet["basic"]:
            self.notes_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Basic commands shown")
            
    def show_branching(self):
        """Show branching commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "BRANCHING COMMANDS:\n\n")
        for cmd in self.git_cheatsheet["branching"]:
            self.notes_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Branching commands shown")
            
    def show_remote_ops(self):
        """Show remote operation commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "REMOTE OPERATIONS:\n\n")
        for cmd in self.git_cheatsheet["remote"]:
            self.notes_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Remote commands shown")
            
    def show_undo_commands(self):
        """Show undo commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "UNDO COMMANDS:\n\n")
        for cmd in self.git_cheatsheet["undo"]:
            self.notes_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Undo commands shown")
            
    def show_scenarios(self):
        """Show common scenarios"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "COMMON SCENARIOS:\n\n")
        
        self.notes_text.insert(tk.END, "NEW PROJECT:\n")
        for step in self.git_cheatsheet["scenarios"]["new_project"]:
            self.notes_text.insert(tk.END, step + "\n")
            
        self.notes_text.insert(tk.END, "\nFEATURE BRANCH:\n")
        for step in self.git_cheatsheet["scenarios"]["feature"]:
            self.notes_text.insert(tk.END, step + "\n")
            
        self.notes_text.insert(tk.END, "\nMERGE FEATURE:\n")
        for step in self.git_cheatsheet["scenarios"]["merge"]:
            self.notes_text.insert(tk.END, step + "\n")
            
        self.notes_text.insert(tk.END, "\nUNDO MISTAKE:\n")
        for step in self.git_cheatsheet["scenarios"]["undo_mistake"]:
            self.notes_text.insert(tk.END, step + "\n")
            
        self.status_label.config(text="Scenarios shown")
    
    def run(self):
        """Run the simple stealth assistant"""
        self.root.mainloop()

def main():
    """Main function to run the simple stealth assistant"""
    print("🔧 Iron Cloud Nexus AI - Git Simple Stealth Assistant")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Simple stealth mode - minimal detection risk")
    print("=" * 60)
    print("\n🚀 Starting Git Simple Stealth Assistant...")
    print("💡 A 'notes' window will appear in bottom-right corner")
    print("🔍 Use the search box to find specific commands")
    print("🔒 Looks like a normal notes app")
    print("=" * 60)
    
    assistant = GitSimpleStealth()
    assistant.run()

if __name__ == "__main__":
    main()
