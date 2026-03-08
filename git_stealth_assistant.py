#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Stealth Assistant
Real-time assistance during Outlier Git screening without detection
"""

import tkinter as tk
from tkinter import ttk
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any
import re

class GitStealthAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Git Helper")
        self.root.geometry("400x600")
        self.root.configure(bg='#2b2b2b')
        
        # Make window semi-transparent and always on top
        self.root.attributes('-alpha', 0.9)
        self.root.attributes('-topmost', True)
        
        # Position window in top-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"400x600+{screen_width-420}+20")
        
        self.setup_ui()
        self.load_git_knowledge()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="Git Quick Helper", 
                              font=("Arial", 14, "bold"), 
                              bg='#2b2b2b', fg='#00ff00')
        title_label.pack(pady=(0, 10))
        
        # Question input
        tk.Label(main_frame, text="Type your question:", 
                bg='#2b2b2b', fg='white').pack(anchor='w')
        
        self.question_entry = tk.Entry(main_frame, width=50, bg='#3b3b3b', fg='white')
        self.question_entry.pack(fill='x', pady=(5, 10))
        self.question_entry.bind('<Return>', self.analyze_question)
        
        # Analyze button
        analyze_btn = tk.Button(main_frame, text="Get Hint", 
                               command=self.analyze_question,
                               bg='#4CAF50', fg='white', font=("Arial", 10, "bold"))
        analyze_btn.pack(pady=(0, 10))
        
        # Results area
        tk.Label(main_frame, text="Quick Hints:", 
                bg='#2b2b2b', fg='white', font=("Arial", 12, "bold")).pack(anchor='w')
        
        self.results_text = tk.Text(main_frame, height=15, width=50, 
                                   bg='#1e1e1e', fg='#00ff00', 
                                   font=("Consolas", 10))
        self.results_text.pack(fill='both', expand=True, pady=(5, 10))
        
        # Quick reference buttons
        tk.Label(main_frame, text="Quick Commands:", 
                bg='#2b2b2b', fg='white', font=("Arial", 12, "bold")).pack(anchor='w')
        
        # Create button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(5, 10))
        
        # Quick command buttons
        quick_commands = [
            ("Init", "git init"),
            ("Add", "git add ."),
            ("Commit", "git commit -m \"message\""),
            ("Status", "git status"),
            ("Branch", "git checkout -b <branch>"),
            ("Push", "git push origin <branch>"),
            ("Pull", "git pull origin <branch>"),
            ("Reset", "git reset --soft HEAD~1"),
            ("Stash", "git stash"),
            ("Log", "git log")
        ]
        
        for i, (label, command) in enumerate(quick_commands):
            btn = tk.Button(button_frame, text=label, 
                           command=lambda cmd=command: self.show_command(cmd),
                           bg='#2196F3', fg='white', font=("Arial", 9))
            btn.grid(row=i//2, column=i%2, padx=2, pady=2, sticky='ew')
        
        # Configure grid weights
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        # Hide/Show button
        self.hide_btn = tk.Button(main_frame, text="Hide Window", 
                                 command=self.toggle_visibility,
                                 bg='#FF5722', fg='white')
        self.hide_btn.pack(pady=(10, 0))
        
        # Status bar
        self.status_label = tk.Label(main_frame, text="Ready to help!", 
                                    bg='#2b2b2b', fg='#00ff00')
        self.status_label.pack(pady=(5, 0))
        
    def load_git_knowledge(self):
        """Load Git knowledge base"""
        self.git_knowledge = {
            "basic_commands": {
                "init": {
                    "command": "git init",
                    "hint": "Start a new Git repository",
                    "when": "Creating a new project"
                },
                "add": {
                    "command": "git add .",
                    "hint": "Stage all modified files",
                    "when": "Before committing changes"
                },
                "commit": {
                    "command": "git commit -m \"message\"",
                    "hint": "Save staged changes with a message",
                    "when": "After staging files"
                },
                "status": {
                    "command": "git status",
                    "hint": "Check what files are staged/modified",
                    "when": "Want to see repository state"
                },
                "log": {
                    "command": "git log",
                    "hint": "View commit history",
                    "when": "Need to see previous commits"
                }
            },
            "branching": {
                "branch": {
                    "command": "git branch",
                    "hint": "List all branches",
                    "when": "Want to see available branches"
                },
                "checkout": {
                    "command": "git checkout <branch>",
                    "hint": "Switch to a different branch",
                    "when": "Need to work on different branch"
                },
                "checkout_b": {
                    "command": "git checkout -b <branch>",
                    "hint": "Create and switch to new branch",
                    "when": "Starting work on new feature"
                },
                "merge": {
                    "command": "git merge <branch>",
                    "hint": "Combine changes from another branch",
                    "when": "Want to integrate feature branch"
                }
            },
            "remote": {
                "push": {
                    "command": "git push origin <branch>",
                    "hint": "Upload commits to remote repository",
                    "when": "Want to share your work"
                },
                "pull": {
                    "command": "git pull origin <branch>",
                    "hint": "Download and merge remote changes",
                    "when": "Want to get latest updates"
                },
                "fetch": {
                    "command": "git fetch origin",
                    "hint": "Download remote changes without merging",
                    "when": "Want to see what's new without merging"
                }
            },
            "undo": {
                "reset_soft": {
                    "command": "git reset --soft HEAD~1",
                    "hint": "Undo last commit but keep changes staged",
                    "when": "Made a mistake in commit message"
                },
                "reset_hard": {
                    "command": "git reset --hard HEAD~1",
                    "hint": "Undo last commit and discard all changes",
                    "when": "Want to completely undo last commit"
                },
                "stash": {
                    "command": "git stash",
                    "hint": "Temporarily save uncommitted changes",
                    "when": "Need to switch branches but have uncommitted work"
                }
            }
        }
        
        self.scenarios = {
            "new_project": ["git init", "git add .", "git commit -m \"Initial commit\""],
            "feature_branch": ["git checkout -b feature", "git add .", "git commit -m \"feat: add feature\"", "git push -u origin feature"],
            "merge_feature": ["git checkout main", "git pull origin main", "git merge feature", "git push origin main"],
            "undo_commit": ["git reset --soft HEAD~1"],
            "save_work": ["git stash", "git checkout other-branch", "git stash pop"]
        }
    
    def analyze_question(self, event=None):
        """Analyze the question and provide hints"""
        question = self.question_entry.get().strip()
        if not question:
            return
        
        self.status_label.config(text="Analyzing question...")
        
        # Clear previous results
        self.results_text.delete(1.0, tk.END)
        
        question_lower = question.lower()
        
        # Identify question type and provide hints
        hints = []
        
        if "initialize" in question_lower or "new repository" in question_lower:
            hints.append("🔧 Use 'git init' to start a new repository")
            hints.append("💡 This creates a .git folder to track changes")
            
        elif "stage" in question_lower or "add" in question_lower:
            hints.append("📁 Use 'git add .' to stage all files")
            hints.append("💡 Or 'git add <filename>' for specific files")
            
        elif "commit" in question_lower:
            hints.append("💾 Use 'git commit -m \"your message\"'")
            hints.append("💡 Always include a descriptive message")
            
        elif "branch" in question_lower:
            if "create" in question_lower or "new" in question_lower:
                hints.append("🌿 Use 'git checkout -b <branch-name>'")
                hints.append("💡 This creates AND switches to the new branch")
            else:
                hints.append("🌿 Use 'git checkout <branch-name>' to switch")
                hints.append("💡 Use 'git branch' to see all branches")
                
        elif "push" in question_lower or "upload" in question_lower:
            hints.append("⬆️ Use 'git push origin <branch>'")
            hints.append("💡 Use '-u' flag for new branches: 'git push -u origin <branch>'")
            
        elif "pull" in question_lower or "download" in question_lower:
            hints.append("⬇️ Use 'git pull origin <branch>'")
            hints.append("💡 This downloads AND merges remote changes")
            
        elif "undo" in question_lower or "reset" in question_lower:
            if "keep" in question_lower or "changes" in question_lower:
                hints.append("↩️ Use 'git reset --soft HEAD~1'")
                hints.append("💡 This undoes commit but keeps changes staged")
            else:
                hints.append("↩️ Use 'git reset --hard HEAD~1'")
                hints.append("💡 ⚠️ This will DELETE all changes!")
                
        elif "stash" in question_lower or "save work" in question_lower:
            hints.append("📦 Use 'git stash' to save work temporarily")
            hints.append("💡 Use 'git stash pop' to restore later")
            
        elif "status" in question_lower or "check" in question_lower:
            hints.append("📊 Use 'git status' to see repository state")
            hints.append("💡 Shows staged, modified, and untracked files")
            
        elif "history" in question_lower or "log" in question_lower:
            hints.append("📜 Use 'git log' to see commit history")
            hints.append("💡 Use 'git log --oneline' for compact view")
            
        else:
            hints.append("🤔 Try these common commands:")
            hints.append("• git init - Start new repository")
            hints.append("• git add . - Stage all files")
            hints.append("• git commit -m \"message\" - Save changes")
            hints.append("• git push origin <branch> - Upload to remote")
            hints.append("• git pull origin <branch> - Download from remote")
        
        # Display hints
        for hint in hints:
            self.results_text.insert(tk.END, hint + "\n")
        
        self.status_label.config(text="Hints provided!")
        
    def show_command(self, command):
        """Show a specific command with explanation"""
        self.results_text.delete(1.0, tk.END)
        
        # Find command in knowledge base
        for category, commands in self.git_knowledge.items():
            for cmd_name, cmd_info in commands.items():
                if cmd_info["command"] == command:
                    self.results_text.insert(tk.END, f"🔧 Command: {command}\n")
                    self.results_text.insert(tk.END, f"💡 Hint: {cmd_info['hint']}\n")
                    self.results_text.insert(tk.END, f"🎯 When: {cmd_info['when']}\n")
                    return
        
        # If not found, show basic info
        self.results_text.insert(tk.END, f"🔧 Command: {command}\n")
        self.results_text.insert(tk.END, "💡 Use this command for Git operations\n")
        
    def toggle_visibility(self):
        """Toggle window visibility"""
        if self.root.state() == 'withdrawn':
            self.root.deiconify()
            self.hide_btn.config(text="Hide Window")
        else:
            self.root.withdraw()
            self.hide_btn.config(text="Show Window")
    
    def run(self):
        """Run the stealth assistant"""
        self.root.mainloop()

def main():
    """Main function to run the stealth assistant"""
    print("🔧 Iron Cloud Nexus AI - Git Stealth Assistant")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Stealth assistance without detection")
    print("=" * 60)
    print("\n🚀 Starting Git Stealth Assistant...")
    print("💡 A small window will appear in the top-right corner")
    print("📋 Type your Git questions and get instant hints")
    print("🔒 Use 'Hide Window' to minimize when needed")
    print("=" * 60)
    
    assistant = GitStealthAssistant()
    assistant.run()

if __name__ == "__main__":
    main()
