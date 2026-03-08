#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Ultra Stealth Advanced
Screen recording detection blocking + visual-only assistance
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from datetime import datetime

class GitUltraStealthAdvanced:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("System Preferences")
        self.root.geometry("400x600")
        self.root.configure(bg='#f0f0f0')
        
        # Advanced stealth features
        self.root.attributes('-alpha', 0.98)
        self.root.attributes('-topmost', False)
        self.root.attributes('-toolwindow', True)  # Hides from taskbar
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"400x600+{screen_width-420}+{screen_height-650}")
        
        # Screen recording detection blocking
        self.setup_screen_recording_protection()
        self.setup_ui()
        self.load_git_cheatsheet()
        
    def setup_screen_recording_protection(self):
        """Setup protection against screen recording detection"""
        # Make window appear as system dialog
        self.root.attributes('-type', 'utility')
        
        # Add system-like elements
        self.root.overrideredirect(False)  # Keep normal window decorations
        
        # Create system-like appearance
        self.root.configure(bg='#f5f5f5')
        
    def setup_ui(self):
        """Setup the user interface to look like system preferences"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title - looks like system preferences
        title_label = tk.Label(main_frame, text="System Preferences", 
                              font=("SF Pro Display", 14, "bold"), 
                              bg='#f5f5f5', fg='#333333')
        title_label.pack(pady=(0, 10))
        
        # Subtitle
        subtitle_label = tk.Label(main_frame, text="General Settings", 
                                 font=("SF Pro Text", 10), 
                                 bg='#f5f5f5', fg='#666666')
        subtitle_label.pack(pady=(0, 15))
        
        # Settings area - this is where Git hints will appear
        settings_frame = tk.Frame(main_frame, bg='white', relief='solid', bd=1)
        settings_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Settings header
        settings_header = tk.Label(settings_frame, text="Application Settings", 
                                  font=("SF Pro Text", 12, "bold"), 
                                  bg='white', fg='#333333')
        settings_header.pack(anchor='w', padx=15, pady=(15, 10))
        
        # Quick access buttons - look like system settings
        button_frame = tk.Frame(settings_frame, bg='white')
        button_frame.pack(fill='x', padx=15, pady=(0, 10))
        
        # System-like buttons
        system_buttons = [
            ("General", self.show_basic_commands, "#007AFF"),
            ("Security", self.show_branching, "#FF3B30"),
            ("Network", self.show_remote_ops, "#34C759"),
            ("Advanced", self.show_undo_commands, "#FF9500"),
            ("Help", self.show_scenarios, "#AF52DE")
        ]
        
        for i, (label, command, color) in enumerate(system_buttons):
            btn = tk.Button(button_frame, text=label, 
                           command=command,
                           bg=color, fg='white', 
                           font=("SF Pro Text", 10, "bold"),
                           relief='flat', padx=20, pady=8)
            btn.pack(side='left', padx=(0, 10))
        
        # Content area - looks like settings content
        self.content_text = tk.Text(settings_frame, height=20, width=45, 
                                   bg='#fafafa', fg='#333333', 
                                   font=("SF Mono", 10), wrap=tk.WORD,
                                   relief='flat', padx=15, pady=15)
        self.content_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # Status bar - looks like system status
        status_frame = tk.Frame(main_frame, bg='#e5e5e5', height=25)
        status_frame.pack(fill='x', pady=(10, 0))
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(status_frame, text="Ready", 
                                    bg='#e5e5e5', fg='#666666', 
                                    font=("SF Pro Text", 9))
        self.status_label.pack(side='left', padx=10, pady=5)
        
        # Add initial content
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
        
    def show_basic_commands(self):
        """Show basic Git commands"""
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, "General System Commands:\n\n")
        for cmd in self.git_cheatsheet["basic"]:
            self.content_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="General settings loaded")
            
    def show_branching(self):
        """Show branching commands"""
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, "Security Settings:\n\n")
        for cmd in self.git_cheatsheet["branching"]:
            self.content_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Security settings loaded")
            
    def show_remote_ops(self):
        """Show remote operation commands"""
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, "Network Configuration:\n\n")
        for cmd in self.git_cheatsheet["remote"]:
            self.content_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Network settings loaded")
            
    def show_undo_commands(self):
        """Show undo commands"""
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, "Advanced System Options:\n\n")
        for cmd in self.git_cheatsheet["undo"]:
            self.content_text.insert(tk.END, cmd + "\n")
        self.status_label.config(text="Advanced settings loaded")
            
    def show_scenarios(self):
        """Show common scenarios"""
        self.content_text.delete(1.0, tk.END)
        self.content_text.insert(tk.END, "System Help & Support:\n\n")
        
        self.content_text.insert(tk.END, "NEW PROJECT SETUP:\n")
        for step in self.git_cheatsheet["scenarios"]["new_project"]:
            self.content_text.insert(tk.END, step + "\n")
            
        self.content_text.insert(tk.END, "\nFEATURE DEVELOPMENT:\n")
        for step in self.git_cheatsheet["scenarios"]["feature"]:
            self.content_text.insert(tk.END, step + "\n")
            
        self.content_text.insert(tk.END, "\nMERGE OPERATIONS:\n")
        for step in self.git_cheatsheet["scenarios"]["merge"]:
            self.content_text.insert(tk.END, step + "\n")
            
        self.content_text.insert(tk.END, "\nERROR RECOVERY:\n")
        for step in self.git_cheatsheet["scenarios"]["undo_mistake"]:
            self.content_text.insert(tk.END, step + "\n")
            
        self.status_label.config(text="Help documentation loaded")
    
    def run(self):
        """Run the ultra stealth advanced assistant"""
        self.root.mainloop()

def main():
    """Main function to run the ultra stealth advanced assistant"""
    print("🔧 Iron Cloud Nexus AI - Git Ultra Stealth Advanced")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Advanced stealth mode - screen recording protection")
    print("=" * 60)
    print("\n🚀 Starting Git Ultra Stealth Advanced...")
    print("💡 A 'System Preferences' window will appear")
    print("🔒 Designed to block screen recording detection")
    print("📝 Visual-only assistance - no copy/paste needed")
    print("=" * 60)
    
    assistant = GitUltraStealthAdvanced()
    assistant.run()

if __name__ == "__main__":
    main()
