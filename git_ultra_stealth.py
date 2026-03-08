#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Ultra Stealth Assistant
Minimal detection risk assistance for Outlier Git screening
"""

import tkinter as tk
from tkinter import ttk
import keyboard
import threading
import time
from datetime import datetime

class GitUltraStealth:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Notes")
        self.root.geometry("300x400")
        self.root.configure(bg='#f0f0f0')
        
        # Make it look like a normal notes app
        self.root.attributes('-alpha', 0.95)
        self.root.attributes('-topmost', False)  # Don't stay on top to avoid detection
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"300x400+{screen_width-320}+{screen_height-450}")
        
        self.setup_ui()
        self.load_git_cheatsheet()
        self.setup_hotkeys()
        
    def setup_ui(self):
        """Setup the user interface to look like a normal notes app"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title - looks like a normal notes app
        title_label = tk.Label(main_frame, text="Quick Notes", 
                              font=("Arial", 12, "bold"), 
                              bg='#f0f0f0', fg='#333333')
        title_label.pack(pady=(0, 10))
        
        # Notes area - this is where Git hints will appear
        tk.Label(main_frame, text="Git Commands:", 
                bg='#f0f0f0', fg='#333333', font=("Arial", 10, "bold")).pack(anchor='w')
        
        self.notes_text = tk.Text(main_frame, height=20, width=35, 
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
            ("Undo", self.show_undo_commands)
        ]
        
        for label, command in quick_refs:
            btn = tk.Button(button_frame, text=label, 
                           command=command,
                           bg='#e0e0e0', fg='#333333', 
                           font=("Arial", 9), relief='flat')
            btn.pack(side='left', padx=2, expand=True, fill='x')
        
        # Status - looks like normal app status
        self.status_label = tk.Label(main_frame, text="Ready", 
                                    bg='#f0f0f0', fg='#666666', font=("Arial", 8))
        self.status_label.pack(pady=(5, 0))
        
    def load_git_cheatsheet(self):
        """Load Git command cheatsheet"""
        self.git_cheatsheet = {
            "basic": [
                "git init          - Start new repo",
                "git add .         - Stage all files", 
                "git commit -m \"msg\" - Save changes",
                "git status        - Check state",
                "git log           - View history"
            ],
            "branching": [
                "git branch        - List branches",
                "git checkout -b x - Create & switch",
                "git checkout x    - Switch to branch",
                "git merge x       - Merge branch"
            ],
            "remote": [
                "git push origin x - Upload to remote",
                "git pull origin x - Download & merge",
                "git fetch origin  - Download only",
                "git remote -v     - Show remotes"
            ],
            "undo": [
                "git reset --soft HEAD~1  - Undo commit, keep changes",
                "git reset --hard HEAD~1  - Undo commit, delete changes", 
                "git stash               - Save work temporarily",
                "git revert HEAD         - Create undo commit"
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
                ]
            }
        }
        
    def setup_hotkeys(self):
        """Setup keyboard shortcuts for quick access"""
        def show_basic():
            self.show_basic_commands()
            self.status_label.config(text="Basic commands shown")
            
        def show_branch():
            self.show_branching()
            self.status_label.config(text="Branching commands shown")
            
        def show_remote():
            self.show_remote_ops()
            self.status_label.config(text="Remote commands shown")
            
        def show_undo():
            self.show_undo_commands()
            self.status_label.config(text="Undo commands shown")
            
        def show_scenarios():
            self.show_scenarios()
            self.status_label.config(text="Scenarios shown")
        
        # Setup hotkeys (Ctrl+Alt+key)
        keyboard.add_hotkey('ctrl+alt+1', show_basic)
        keyboard.add_hotkey('ctrl+alt+2', show_branch)
        keyboard.add_hotkey('ctrl+alt+3', show_remote)
        keyboard.add_hotkey('ctrl+alt+4', show_undo)
        keyboard.add_hotkey('ctrl+alt+5', show_scenarios)
        
        # Add hotkey info to notes
        hotkey_info = """
HOTKEYS (Ctrl+Alt):
1 - Basic commands
2 - Branching  
3 - Remote ops
4 - Undo commands
5 - Scenarios
        """
        self.notes_text.insert(tk.END, hotkey_info)
        
    def show_basic_commands(self):
        """Show basic Git commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "BASIC GIT COMMANDS:\n\n")
        for cmd in self.git_cheatsheet["basic"]:
            self.notes_text.insert(tk.END, cmd + "\n")
            
    def show_branching(self):
        """Show branching commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "BRANCHING COMMANDS:\n\n")
        for cmd in self.git_cheatsheet["branching"]:
            self.notes_text.insert(tk.END, cmd + "\n")
            
    def show_remote_ops(self):
        """Show remote operation commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "REMOTE OPERATIONS:\n\n")
        for cmd in self.git_cheatsheet["remote"]:
            self.notes_text.insert(tk.END, cmd + "\n")
            
    def show_undo_commands(self):
        """Show undo commands"""
        self.notes_text.delete(1.0, tk.END)
        self.notes_text.insert(tk.END, "UNDO COMMANDS:\n\n")
        for cmd in self.git_cheatsheet["undo"]:
            self.notes_text.insert(tk.END, cmd + "\n")
            
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
    
    def run(self):
        """Run the ultra stealth assistant"""
        self.root.mainloop()

def main():
    """Main function to run the ultra stealth assistant"""
    print("🔧 Iron Cloud Nexus AI - Git Ultra Stealth Assistant")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Ultra-stealth mode - minimal detection risk")
    print("=" * 60)
    print("\n🚀 Starting Git Ultra Stealth Assistant...")
    print("💡 A 'notes' window will appear in bottom-right corner")
    print("⌨️  Use Ctrl+Alt+1,2,3,4,5 for quick access")
    print("🔒 Looks like a normal notes app")
    print("=" * 60)
    
    assistant = GitUltraStealth()
    assistant.run()

if __name__ == "__main__":
    main()
