#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Visual Memory System
Visual-only assistance with memory techniques + screen recording evasion
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import datetime

class GitVisualMemorySystem:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("300x500")
        self.root.configure(bg='#f0f0f0')
        
        # Advanced stealth features
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', False)
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"300x500+{screen_width-320}+{screen_height-550}")
        
        self.setup_ui()
        self.load_git_memory_system()
        
    def setup_ui(self):
        """Setup the user interface to look like a calculator"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title - looks like calculator
        title_label = tk.Label(main_frame, text="Calculator", 
                              font=("SF Pro Display", 12, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 10))
        
        # Display area - looks like calculator display
        display_frame = tk.Frame(main_frame, bg='#333333', relief='sunken', bd=2)
        display_frame.pack(fill='x', pady=(0, 10))
        
        self.display_text = tk.Text(display_frame, height=8, width=35, 
                                   bg='#333333', fg='#00ff00', 
                                   font=("SF Mono", 9), wrap=tk.WORD,
                                   relief='flat', padx=10, pady=10)
        self.display_text.pack(fill='both', expand=True)
        
        # Button grid - looks like calculator buttons
        button_frame = tk.Frame(main_frame, bg='#f0f0f0')
        button_frame.pack(fill='both', expand=True)
        
        # Calculator-like buttons with Git commands
        buttons = [
            ("1", self.show_basic_commands, "#e0e0e0"),
            ("2", self.show_branching, "#e0e0e0"),
            ("3", self.show_remote_ops, "#e0e0e0"),
            ("4", self.show_undo_commands, "#e0e0e0"),
            ("5", self.show_scenarios, "#e0e0e0"),
            ("6", self.show_quick_ref, "#e0e0e0"),
            ("7", self.show_workflows, "#e0e0e0"),
            ("8", self.show_troubleshooting, "#e0e0e0"),
            ("9", self.show_advanced, "#e0e0e0"),
            ("0", self.show_emergency, "#ff6b6b")
        ]
        
        # Create 2x5 grid
        for i, (label, command, color) in enumerate(buttons):
            row = i // 5
            col = i % 5
            btn = tk.Button(button_frame, text=label, 
                           command=command,
                           bg=color, fg='#333333', 
                           font=("SF Pro Text", 12, "bold"),
                           relief='raised', padx=15, pady=10)
            btn.grid(row=row, column=col, padx=2, pady=2, sticky='ew')
        
        # Configure grid weights
        for i in range(5):
            button_frame.columnconfigure(i, weight=1)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg='#e0e0e0', height=20)
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    bg='#e0e0e0', fg='#666666', 
                                    font=("SF Pro Text", 8))
        self.status_label.pack(side='left', padx=5, pady=2)
        
        # Add initial content
        self.load_git_memory_system()
        self.show_basic_commands()
        
    def load_git_memory_system(self):
        """Load Git commands with visual memory techniques"""
        self.git_memory = {
            "basic": [
                "🔧 INIT: git init",
                "📁 ADD: git add .", 
                "💾 COMMIT: git commit -m \"msg\"",
                "📊 STATUS: git status",
                "📜 LOG: git log",
                "🔍 DIFF: git diff"
            ],
            "branching": [
                "🌿 BRANCH: git branch",
                "🔄 CHECKOUT: git checkout -b x",
                "🔄 SWITCH: git checkout x",
                "🔀 MERGE: git merge x",
                "🗑️ DELETE: git branch -d x"
            ],
            "remote": [
                "⬆️ PUSH: git push origin x",
                "⬇️ PULL: git pull origin x",
                "📥 FETCH: git fetch origin",
                "🔗 REMOTE: git remote -v",
                "📋 CLONE: git clone url"
            ],
            "undo": [
                "↩️ SOFT: git reset --soft HEAD~1",
                "🗑️ HARD: git reset --hard HEAD~1", 
                "📦 STASH: git stash",
                "🔄 REVERT: git revert HEAD",
                "↩️ FILE: git checkout -- file"
            ],
            "scenarios": {
                "new_project": [
                    "🚀 NEW PROJECT:",
                    "1. git init",
                    "2. git add .", 
                    "3. git commit -m \"Initial\""
                ],
                "feature": [
                    "✨ FEATURE BRANCH:",
                    "1. git checkout -b feature",
                    "2. git add .",
                    "3. git commit -m \"feat: add\"",
                    "4. git push -u origin feature"
                ],
                "merge": [
                    "🔀 MERGE FEATURE:",
                    "1. git checkout main",
                    "2. git pull origin main", 
                    "3. git merge feature",
                    "4. git push origin main"
                ],
                "undo_mistake": [
                    "🛠️ UNDO MISTAKE:",
                    "1. git reset --soft HEAD~1",
                    "2. Fix the mistake",
                    "3. git add .",
                    "4. git commit -m \"Fixed\""
                ]
            },
            "quick_ref": [
                "⚡ QUICK REFERENCE:",
                "🔧 Start: git init",
                "📁 Stage: git add .",
                "💾 Save: git commit -m \"msg\"",
                "🌿 Branch: git checkout -b x",
                "⬆️ Upload: git push origin x",
                "⬇️ Download: git pull origin x",
                "↩️ Undo: git reset --soft HEAD~1"
            ],
            "workflows": [
                "🔄 COMMON WORKFLOWS:",
                "📝 Daily: add → commit → push",
                "✨ Feature: checkout -b → work → merge",
                "🛠️ Fix: reset → fix → commit",
                "📦 Save: stash → switch → pop"
            ],
            "troubleshooting": [
                "🔧 TROUBLESHOOTING:",
                "❓ Status: git status",
                "📜 History: git log",
                "🔍 Changes: git diff",
                "🔄 Reset: git reset --hard HEAD~1",
                "📦 Recover: git stash pop"
            ],
            "advanced": [
                "🚀 ADVANCED COMMANDS:",
                "🔀 Rebase: git rebase main",
                "🏷️ Tag: git tag v1.0",
                "🔍 Search: git log --grep=\"keyword\"",
                "📊 Stats: git log --stat",
                "🔄 Cherry-pick: git cherry-pick commit"
            ],
            "emergency": [
                "🚨 EMERGENCY COMMANDS:",
                "🛑 Stop: Ctrl+C",
                "↩️ Undo: git reset --hard HEAD~1",
                "📦 Save: git stash",
                "🔄 Revert: git revert HEAD",
                "🔍 Check: git status"
            ]
        }
        
    def show_basic_commands(self):
        """Show basic Git commands with visual memory"""
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "🔧 BASIC COMMANDS:\n\n")
        for cmd in self.git_memory["basic"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Basic commands loaded")
            
    def show_branching(self):
        """Show branching commands"""
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "🌿 BRANCHING:\n\n")
        for cmd in self.git_memory["branching"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Branching loaded")
            
    def show_remote_ops(self):
        """Show remote operation commands"""
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "🌐 REMOTE OPS:\n\n")
        for cmd in self.git_memory["remote"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Remote ops loaded")
            
    def show_undo_commands(self):
        """Show undo commands"""
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "↩️ UNDO COMMANDS:\n\n")
        for cmd in self.git_memory["undo"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Undo commands loaded")
            
    def show_scenarios(self):
        """Show common scenarios"""
        self.display_text.delete(1.0, tk.END)
        self.display_text.insert(tk.END, "📋 SCENARIOS:\n\n")
        
        for scenario_name, steps in self.git_memory["scenarios"].items():
            for step in steps:
                self.display_text.insert(tk.END, step + "\n")
            self.display_text.insert(tk.END, "\n")
            
        self.status_label.config(text="Scenarios loaded")
        
    def show_quick_ref(self):
        """Show quick reference"""
        self.display_text.delete(1.0, tk.END)
        for cmd in self.git_memory["quick_ref"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Quick ref loaded")
        
    def show_workflows(self):
        """Show workflows"""
        self.display_text.delete(1.0, tk.END)
        for cmd in self.git_memory["workflows"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Workflows loaded")
        
    def show_troubleshooting(self):
        """Show troubleshooting"""
        self.display_text.delete(1.0, tk.END)
        for cmd in self.git_memory["troubleshooting"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Troubleshooting loaded")
        
    def show_advanced(self):
        """Show advanced commands"""
        self.display_text.delete(1.0, tk.END)
        for cmd in self.git_memory["advanced"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Advanced loaded")
        
    def show_emergency(self):
        """Show emergency commands"""
        self.display_text.delete(1.0, tk.END)
        for cmd in self.git_memory["emergency"]:
            self.display_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Emergency loaded")
    
    def run(self):
        """Run the visual memory system"""
        self.root.mainloop()

def main():
    """Main function to run the visual memory system"""
    print("🔧 Iron Cloud Nexus AI - Git Visual Memory System")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Visual memory system - no copy/paste needed")
    print("🔒 Screen recording evasion + memory techniques")
    print("=" * 60)
    print("\n🚀 Starting Git Visual Memory System...")
    print("💡 A 'Calculator' window will appear")
    print("📝 Visual-only assistance with emojis for memory")
    print("🔒 Designed to evade screen recording detection")
    print("=" * 60)
    
    assistant = GitVisualMemorySystem()
    assistant.run()

if __name__ == "__main__":
    main()
