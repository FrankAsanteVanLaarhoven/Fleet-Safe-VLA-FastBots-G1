#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git High Contrast Calculator
High contrast, always-visible buttons for glasses wearers
"""
import tkinter as tk
from tkinter import ttk

class GitHighContrastCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("450x600")
        self.root.configure(bg='#000000')
        
        # Make it look like a real calculator
        self.root.attributes('-alpha', 0.98)
        self.root.attributes('-topmost', False)
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"450x600+{screen_width-470}+{screen_height-650}")
        
        # Calculator state
        self.current_number = ""
        self.first_number = 0
        self.operation = ""
        self.should_reset = False
        
        # Git assistance mode
        self.git_mode = False
        
        # Git commands with high contrast
        self.git_commands = {
            "1": [
                "git init - Initialize repository",
                "git clone <url> - Clone repository",
                "git add . - Stage all changes",
                "git commit -m 'message' - Commit changes",
                "git status - Check status"
            ],
            "2": [
                "git branch - List branches",
                "git checkout -b <branch> - Create & switch",
                "git checkout <branch> - Switch branch",
                "git merge <branch> - Merge branch",
                "git branch -d <branch> - Delete branch"
            ],
            "3": [
                "git remote add origin <url> - Add remote",
                "git push origin <branch> - Push to remote",
                "git pull origin <branch> - Pull from remote",
                "git fetch - Download from remote",
                "git remote -v - List remotes"
            ],
            "4": [
                "git reset --hard HEAD~1 - Undo last commit",
                "git revert HEAD - Revert last commit",
                "git stash - Save changes temporarily",
                "git checkout -- <file> - Discard changes",
                "git clean -fd - Remove untracked files"
            ],
            "5": [
                "Accidentally committed wrong: git reset --hard HEAD~1",
                "Save work before switching: git stash",
                "See what files changed: git status",
                "Get latest changes: git pull",
                "Check current branch: git branch"
            ]
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#000000')
        main_frame.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Display
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        display_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='sunken', bd=3)
        display_frame.pack(fill='x', pady=(0, 15))
        
        self.display = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=('Courier', 24, 'bold'),
            bg='#1a1a1a',
            fg='#00ff00',
            anchor='e',
            padx=15,
            pady=15
        )
        self.display.pack(fill='x')
        
        # Secondary display
        self.secondary_display_var = tk.StringVar()
        self.secondary_display_var.set("")
        
        secondary_display = tk.Label(
            display_frame,
            textvariable=self.secondary_display_var,
            font=('Courier', 12, 'bold'),
            bg='#1a1a1a',
            fg='#ffffff',
            anchor='e',
            padx=15
        )
        secondary_display.pack(fill='x')
        
        # Control buttons - HIGH CONTRAST
        control_frame = tk.Frame(main_frame, bg='#000000')
        control_frame.pack(fill='x', pady=(0, 15))
        
        # Git Mode button - BRIGHT BLUE
        self.git_btn = tk.Button(
            control_frame,
            text="GIT MODE",
            font=('Arial', 14, 'bold'),
            bg='#0066ff',
            fg='#ffffff',
            command=self.toggle_git_mode,
            width=12,
            height=2,
            relief='raised',
            bd=3
        )
        self.git_btn.pack(side='left', padx=5)
        
        # Clear button - BRIGHT RED
        self.clear_btn = tk.Button(
            control_frame,
            text="CLEAR ALL",
            font=('Arial', 14, 'bold'),
            bg='#ff0000',
            fg='#ffffff',
            command=self.clear_all,
            width=12,
            height=2,
            relief='raised',
            bd=3
        )
        self.clear_btn.pack(side='right', padx=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#000000')
        buttons_frame.pack(fill='both', expand=True)
        
        # High contrast button layout
        button_configs = [
            # Row 1: Numbers and operations
            [('7', '#ffffff', '#000000'), ('8', '#ffffff', '#000000'), ('9', '#ffffff', '#000000'), ('÷', '#ff6600', '#ffffff')],
            # Row 2: Numbers and operations
            [('4', '#ffffff', '#000000'), ('5', '#ffffff', '#000000'), ('6', '#ffffff', '#000000'), ('×', '#ff6600', '#ffffff')],
            # Row 3: Numbers and operations
            [('1', '#ffffff', '#000000'), ('2', '#ffffff', '#000000'), ('3', '#ffffff', '#000000'), ('-', '#ff6600', '#ffffff')],
            # Row 4: Numbers and operations
            [('0', '#ffffff', '#000000'), ('.', '#ffffff', '#000000'), ('=', '#ff6600', '#ffffff'), ('+', '#ff6600', '#ffffff')]
        ]
        
        # Create buttons with HIGH CONTRAST styling
        for i, row in enumerate(button_configs):
            for j, (text, bg_color, fg_color) in enumerate(row):
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    font=('Arial', 16, 'bold'),
                    bg=bg_color,
                    fg=fg_color,
                    relief='raised',
                    bd=4,
                    width=8,
                    height=3,
                    command=lambda t=text: self.button_click(t),
                    activebackground='#cccccc' if bg_color == '#ffffff' else '#ff8800',
                    activeforeground='#000000' if bg_color == '#ffffff' else '#ffffff'
                )
                btn.grid(row=i, column=j, padx=4, pady=4, sticky='nsew')
        
        # Configure grid weights
        for i in range(4):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
        
    def button_click(self, button):
        """Handle all button clicks"""
        if self.git_mode:
            self.handle_git_button(button)
        else:
            self.handle_calc_button(button)
            
    def handle_git_button(self, button):
        """Handle button clicks in Git mode"""
        if button in self.git_commands:
            commands = self.git_commands[button]
            self.display_var.set(f"GIT COMMANDS {button}")
            self.secondary_display_var.set("\n".join(commands))
        elif button == "=":
            # Show all Git categories
            self.display_var.set("GIT CATEGORIES")
            self.secondary_display_var.set("1=Basic, 2=Branching, 3=Remote, 4=Undo, 5=Scenarios")
        else:
            # Ignore other buttons in Git mode
            pass
            
    def handle_calc_button(self, button):
        """Handle button clicks in calculator mode"""
        if button.isdigit():
            self.add_number(button)
        elif button == ".":
            self.add_decimal()
        elif button in ["+", "-", "×", "÷"]:
            self.set_operation(button)
        elif button == "=":
            self.calculate()
            
    def add_number(self, number):
        """Add a number to the display"""
        if self.should_reset:
            self.current_number = ""
            self.should_reset = False
            
        if number == "0" and self.current_number == "0":
            return
            
        self.current_number += number
        self.display_var.set(self.current_number)
        
    def add_decimal(self):
        """Add a decimal point"""
        if "." not in self.current_number:
            if self.current_number == "":
                self.current_number = "0"
            self.current_number += "."
            self.display_var.set(self.current_number)
            
    def set_operation(self, op):
        """Set the operation to perform"""
        if self.current_number:
            if self.first_number != 0:
                self.calculate_result()
            self.first_number = float(self.current_number)
            self.operation = op
            self.should_reset = True
            self.secondary_display_var.set(f"{self.first_number} {op}")
            
    def calculate(self):
        """Calculate the result"""
        if self.current_number and self.operation:
            self.calculate_result()
            
    def calculate_result(self):
        """Perform the calculation"""
        second_number = float(self.current_number)
        result = 0
        
        if self.operation == "+":
            result = self.first_number + second_number
        elif self.operation == "-":
            result = self.first_number - second_number
        elif self.operation == "×":
            result = self.first_number * second_number
        elif self.operation == "÷":
            if second_number != 0:
                result = self.first_number / second_number
            else:
                self.display_var.set("Error")
                return
                
        self.display_var.set(str(result))
        self.current_number = str(result)
        self.first_number = 0
        self.operation = ""
        self.should_reset = True
        self.secondary_display_var.set("")
        
    def toggle_git_mode(self):
        """Toggle between calculator and Git assistance mode"""
        self.git_mode = not self.git_mode
        if self.git_mode:
            self.display_var.set("GIT MODE ACTIVE")
            self.secondary_display_var.set("Press 1-5 for commands, = for categories")
            self.git_btn.configure(text="CALC MODE", bg='#ff6600')
        else:
            # ALWAYS return to normal calculator state
            self.display_var.set("0")
            self.secondary_display_var.set("")
            self.git_btn.configure(text="GIT MODE", bg='#0066ff')
            
    def clear_all(self):
        """Clear everything and ALWAYS return to calculator mode"""
        self.git_mode = False
        self.current_number = ""
        self.first_number = 0
        self.operation = ""
        self.should_reset = False
        self.display_var.set("0")
        self.secondary_display_var.set("")
        self.git_btn.configure(text="GIT MODE", bg='#0066ff')
        
    def run(self):
        """Start the calculator"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Git High Contrast Calculator")
    print("=" * 55)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ High contrast for glasses wearers")
    print("🔒 Always visible buttons")
    print("=" * 55)
    print("🚀 Starting High Contrast Git Calculator...")
    print("💡 A high contrast calculator window will appear")
    print("🔍 Click 'GIT MODE' to toggle assistance")
    print("🔢 Press 1-5 for Git commands")
    print("🔒 High contrast, always visible buttons")
    print("👓 Easy to read with glasses")
    print("=" * 55)
    
    calculator = GitHighContrastCalculator()
    calculator.run()

if __name__ == "__main__":
    main()
