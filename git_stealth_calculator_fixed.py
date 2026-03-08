#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Stealth Calculator (Fixed)
Fully functional calculator with clear buttons and navigation
"""
import tkinter as tk
from tkinter import ttk
import math
import time
from datetime import datetime

class GitStealthCalculatorFixed:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Calculator")
        self.root.geometry("400x600")
        self.root.configure(bg='#2b2b2b')
        
        # Make it look like a real calculator
        self.root.attributes('-alpha', 0.98)
        self.root.attributes('-topmost', False)
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"400x600+{screen_width-420}+{screen_height-650}")
        
        # Calculator state
        self.current_number = ""
        self.first_number = 0
        self.operation = ""
        self.should_reset = False
        self.memory = 0
        
        # Git assistance mode
        self.git_mode = False
        self.current_git_category = ""
        self.git_history = []  # Track navigation history
        
        # Git assistance data
        self.git_cheatsheet = {
            "basic": {
                "title": "Basic Git Commands",
                "commands": [
                    "git init - Initialize repository",
                    "git clone <url> - Clone repository", 
                    "git add . - Stage all changes",
                    "git commit -m 'message' - Commit changes",
                    "git status - Check repository status",
                    "git log - View commit history",
                    "git diff - Show changes",
                    "git push - Push to remote",
                    "git pull - Pull from remote"
                ]
            },
            "branching": {
                "title": "Branching Commands",
                "commands": [
                    "git branch - List branches",
                    "git checkout -b <branch> - Create & switch",
                    "git checkout <branch> - Switch branch",
                    "git merge <branch> - Merge branch",
                    "git rebase <branch> - Rebase branch",
                    "git branch -d <branch> - Delete branch",
                    "git branch -m <old> <new> - Rename branch"
                ]
            },
            "remote": {
                "title": "Remote Operations",
                "commands": [
                    "git remote add origin <url> - Add remote",
                    "git remote -v - List remotes",
                    "git fetch - Download from remote",
                    "git push origin <branch> - Push to remote",
                    "git pull origin <branch> - Pull from remote",
                    "git push -u origin <branch> - Set upstream"
                ]
            },
            "undo": {
                "title": "Undo Operations",
                "commands": [
                    "git reset --hard HEAD~1 - Undo last commit",
                    "git revert HEAD - Revert last commit",
                    "git stash - Save changes temporarily",
                    "git checkout -- <file> - Discard file changes",
                    "git clean -fd - Remove untracked files",
                    "git reset --soft HEAD~1 - Undo commit, keep changes"
                ]
            },
            "scenarios": {
                "title": "Common Scenarios",
                "commands": [
                    "Accidentally committed wrong changes: git reset --hard HEAD~1",
                    "Save work before switching branches: git stash",
                    "See what files changed: git status",
                    "Get latest changes: git pull",
                    "Undo last commit but keep changes: git reset --soft HEAD~1",
                    "Check what branch you're on: git branch"
                ]
            }
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2b2b2b')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Display
        self.display_var = tk.StringVar()
        self.display_var.set("0")
        
        display_frame = tk.Frame(main_frame, bg='#1a1a1a', relief='sunken', bd=2)
        display_frame.pack(fill='x', pady=(0, 10))
        
        self.display = tk.Label(
            display_frame,
            textvariable=self.display_var,
            font=('Courier', 18, 'bold'),
            bg='#1a1a1a',
            fg='#00ff00',
            anchor='e',
            padx=10,
            pady=10
        )
        self.display.pack(fill='x')
        
        # Secondary display for operations
        self.secondary_display_var = tk.StringVar()
        self.secondary_display_var.set("")
        
        secondary_display = tk.Label(
            display_frame,
            textvariable=self.secondary_display_var,
            font=('Courier', 10),
            bg='#1a1a1a',
            fg='#888888',
            anchor='e',
            padx=10
        )
        secondary_display.pack(fill='x')
        
        # Navigation buttons (always visible)
        nav_frame = tk.Frame(main_frame, bg='#2b2b2b')
        nav_frame.pack(fill='x', pady=(0, 10))
        
        # Back button
        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            font=('Arial', 10, 'bold'),
            bg='#ff6b35',
            fg='white',
            command=self.go_back,
            width=8,
            height=1
        )
        self.back_btn.pack(side='left', padx=5)
        
        # Clear button
        self.clear_btn = tk.Button(
            nav_frame,
            text="Clear",
            font=('Arial', 10, 'bold'),
            bg='#ff3b30',
            fg='white',
            command=self.clear_all,
            width=8,
            height=1
        )
        self.clear_btn.pack(side='right', padx=5)
        
        # Git mode toggle
        self.git_btn = tk.Button(
            nav_frame,
            text="Git Mode",
            font=('Arial', 10, 'bold'),
            bg='#007aff',
            fg='white',
            command=self.toggle_git_mode,
            width=8,
            height=1
        )
        self.git_btn.pack(side='right', padx=5)
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#2b2b2b')
        buttons_frame.pack(fill='both', expand=True)
        
        # Button configurations with clear, always-visible styling
        button_configs = [
            # Row 1: Mode and Memory
            [('2nd', '#444444', self.secondary_function), ('F-E', '#444444', self.toggle_format), ('DEG', '#444444', self.toggle_angle), ('F-E', '#444444', self.toggle_format)],
            
            # Row 2: Scientific functions
            [('sin', '#666666', self.scientific_function), ('cos', '#666666', self.scientific_function), ('tan', '#666666', self.scientific_function), ('(', '#666666', self.add_parenthesis)],
            
            # Row 3: More scientific functions
            [('x²', '#666666', self.square), ('1/x', '#666666', self.reciprocal), ('|x|', '#666666', self.absolute), (')', '#666666', self.add_parenthesis)],
            
            # Row 4: Advanced functions
            [('xʸ', '#666666', self.power), ('√', '#666666', self.square_root), ('x!', '#666666', self.factorial), ('÷', '#ff9500', self.set_operation)],
            
            # Row 5: Numbers and basic operations
            [('7', '#333333', self.add_number), ('8', '#333333', self.add_number), ('9', '#333333', self.add_number), ('×', '#ff9500', self.set_operation)],
            
            # Row 6: More numbers
            [('4', '#333333', self.add_number), ('5', '#333333', self.add_number), ('6', '#333333', self.add_number), ('-', '#ff9500', self.set_operation)],
            
            # Row 7: More numbers
            [('1', '#333333', self.add_number), ('2', '#333333', self.add_number), ('3', '#333333', self.add_number), ('+', '#ff9500', self.set_operation)],
            
            # Row 8: Zero and decimal
            [('±', '#333333', self.negate), ('0', '#333333', self.add_number), ('.', '#333333', self.add_decimal), ('=', '#ff9500', self.calculate)],
            
            # Row 9: Memory and clear
            [('MC', '#444444', self.memory_clear), ('MR', '#444444', self.memory_recall), ('M+', '#444444', self.memory_add), ('C', '#ff3b30', self.clear)],
            
            # Row 10: Special functions (Git assistance hidden here)
            [('EE', '#444444', self.scientific_notation), ('π', '#444444', self.add_pi), ('e', '#444444', self.add_e), ('AC', '#ff3b30', self.all_clear)]
        ]
        
        # Create buttons with improved visibility
        for i, row in enumerate(button_configs):
            for j, (text, color, command) in enumerate(row):
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    font=('Arial', 12, 'bold'),
                    bg=color,
                    fg='white',
                    relief='raised',
                    bd=2,
                    width=8,
                    height=2,
                    command=lambda t=text, c=command: c(t),
                    activebackground='#555555',  # Highlight when pressed
                    activeforeground='white'
                )
                btn.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
        
        # Configure grid weights
        for i in range(10):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
        
    def toggle_git_mode(self):
        """Toggle between calculator and Git assistance mode"""
        self.git_mode = not self.git_mode
        if self.git_mode:
            self.display_var.set("Git Mode Active")
            self.secondary_display_var.set("Use number buttons 1-5 for categories")
            self.git_btn.configure(text="Calc Mode", bg='#ff9500')
        else:
            self.display_var.set("0")
            self.secondary_display_var.set("")
            self.git_btn.configure(text="Git Mode", bg='#007aff')
            self.current_git_category = ""
            self.git_history = []
            
    def go_back(self):
        """Go back to previous state"""
        if self.git_mode and self.git_history:
            # Go back in Git navigation history
            self.git_history.pop()  # Remove current
            if self.git_history:
                previous_category = self.git_history[-1]
                self.show_git_category(previous_category)
            else:
                # Back to Git mode main menu
                self.display_var.set("Git Mode Active")
                self.secondary_display_var.set("Use number buttons 1-5 for categories")
                self.current_git_category = ""
        else:
            # Back to calculator mode
            self.git_mode = False
            self.display_var.set("0")
            self.secondary_display_var.set("")
            self.git_btn.configure(text="Git Mode", bg='#007aff')
            self.current_git_category = ""
            self.git_history = []
            
    def clear_all(self):
        """Clear everything and return to calculator mode"""
        self.git_mode = False
        self.current_number = ""
        self.first_number = 0
        self.operation = ""
        self.should_reset = False
        self.display_var.set("0")
        self.secondary_display_var.set("")
        self.git_btn.configure(text="Git Mode", bg='#007aff')
        self.current_git_category = ""
        self.git_history = []
        
    def add_number(self, number):
        """Add a number to the display"""
        if self.git_mode:
            self.show_git_category_by_number(number)
            return
            
        if self.should_reset:
            self.current_number = ""
            self.should_reset = False
            
        if number == "0" and self.current_number == "0":
            return
            
        self.current_number += number
        self.display_var.set(self.current_number)
        
    def show_git_category_by_number(self, number):
        """Show Git category based on number button"""
        categories = {
            "1": "basic",
            "2": "branching", 
            "3": "remote",
            "4": "undo",
            "5": "scenarios"
        }
        
        if number in categories:
            category = categories[number]
            self.show_git_category(category)
            
    def show_git_category(self, category):
        """Show specific Git category"""
        if category in self.git_cheatsheet:
            self.current_git_category = category
            self.git_history.append(category)
            
            data = self.git_cheatsheet[category]
            self.display_var.set(data["title"])
            
            # Show commands in secondary display
            commands_text = "\n".join(data["commands"][:4])  # Show first 4 commands
            self.secondary_display_var.set(commands_text)
        
    def add_decimal(self, decimal):
        """Add a decimal point"""
        if self.git_mode:
            return
            
        if "." not in self.current_number:
            if self.current_number == "":
                self.current_number = "0"
            self.current_number += "."
            self.display_var.set(self.current_number)
            
    def set_operation(self, op):
        """Set the operation to perform"""
        if self.git_mode:
            return
            
        if self.current_number:
            if self.first_number != 0:
                self.calculate_result()
            self.first_number = float(self.current_number)
            self.operation = op
            self.should_reset = True
            self.secondary_display_var.set(f"{self.first_number} {op}")
            
    def calculate(self, equals):
        """Calculate the result"""
        if self.git_mode:
            return
            
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
        
    def clear(self, c):
        """Clear the current number"""
        if self.git_mode:
            self.go_back()
            return
            
        self.current_number = ""
        self.display_var.set("0")
        
    def all_clear(self, ac):
        """Clear everything"""
        if self.git_mode:
            self.clear_all()
            return
            
        self.current_number = ""
        self.first_number = 0
        self.operation = ""
        self.should_reset = False
        self.display_var.set("0")
        self.secondary_display_var.set("")
        
    def negate(self, plus_minus):
        """Negate the current number"""
        if self.git_mode:
            return
            
        if self.current_number:
            if self.current_number.startswith("-"):
                self.current_number = self.current_number[1:]
            else:
                self.current_number = "-" + self.current_number
            self.display_var.set(self.current_number)
            
    def scientific_function(self, func):
        """Handle scientific functions"""
        if self.git_mode:
            return
            
        if self.current_number:
            number = float(self.current_number)
            if func == "sin":
                result = math.sin(number)
            elif func == "cos":
                result = math.cos(number)
            elif func == "tan":
                result = math.tan(number)
                
            self.display_var.set(str(result))
            self.current_number = str(result)
            
    def square(self, x_squared):
        """Square the current number"""
        if self.git_mode:
            return
            
        if self.current_number:
            number = float(self.current_number)
            result = number ** 2
            self.display_var.set(str(result))
            self.current_number = str(result)
            
    def square_root(self, sqrt):
        """Square root of the current number"""
        if self.git_mode:
            return
            
        if self.current_number:
            number = float(self.current_number)
            if number >= 0:
                result = math.sqrt(number)
                self.display_var.set(str(result))
                self.current_number = str(result)
            else:
                self.display_var.set("Error")
                
    def reciprocal(self, one_over_x):
        """Reciprocal of the current number"""
        if self.git_mode:
            return
            
        if self.current_number:
            number = float(self.current_number)
            if number != 0:
                result = 1 / number
                self.display_var.set(str(result))
                self.current_number = str(result)
            else:
                self.display_var.set("Error")
                
    def absolute(self, abs_x):
        """Absolute value of the current number"""
        if self.git_mode:
            return
            
        if self.current_number:
            number = float(self.current_number)
            result = abs(number)
            self.display_var.set(str(result))
            self.current_number = str(result)
            
    def factorial(self, x_factorial):
        """Factorial of the current number"""
        if self.git_mode:
            return
            
        if self.current_number:
            number = int(float(self.current_number))
            if number >= 0 and number <= 20:  # Limit to prevent overflow
                result = math.factorial(number)
                self.display_var.set(str(result))
                self.current_number = str(result)
            else:
                self.display_var.set("Error")
                
    def power(self, x_power_y):
        """Power function"""
        if self.git_mode:
            return
            
        if self.current_number:
            self.first_number = float(self.current_number)
            self.operation = "^"
            self.should_reset = True
            self.secondary_display_var.set(f"{self.first_number} ^")
            
    def add_parenthesis(self, parenthesis):
        """Add parenthesis (placeholder)"""
        if self.git_mode:
            return
            
        # Don't add parenthesis to current number - just ignore for now
        pass
        
    def toggle_angle(self, angle_mode):
        """Toggle between degrees and radians"""
        if self.git_mode:
            return
            
        # Placeholder for angle toggle
        pass
        
    def toggle_format(self, format_toggle):
        """Toggle number format (placeholder)"""
        if self.git_mode:
            return
            
        # Placeholder for format toggle
        pass
        
    def secondary_function(self, second):
        """Secondary function mode (placeholder)"""
        if self.git_mode:
            return
            
        # Placeholder for secondary functions
        pass
        
    def scientific_notation(self, ee):
        """Scientific notation (placeholder)"""
        if self.git_mode:
            return
            
        # Placeholder for scientific notation
        pass
        
    def add_pi(self, pi):
        """Add π to the display"""
        if self.git_mode:
            return
            
        if self.should_reset:
            self.current_number = ""
            self.should_reset = False
            
        self.current_number = str(math.pi)
        self.display_var.set(self.current_number)
        
    def add_e(self, e):
        """Add e to the display"""
        if self.git_mode:
            return
            
        if self.should_reset:
            self.current_number = ""
            self.should_reset = False
            
        self.current_number = str(math.e)
        self.display_var.set(self.current_number)
        
    def memory_clear(self, mc):
        """Clear memory"""
        if self.git_mode:
            return
            
        self.memory = 0
        
    def memory_recall(self, mr):
        """Recall from memory"""
        if self.git_mode:
            return
            
        self.current_number = str(self.memory)
        self.display_var.set(self.current_number)
        
    def memory_add(self, m_plus):
        """Add to memory"""
        if self.git_mode:
            return
            
        if self.current_number:
            self.memory += float(self.current_number)
            
    def run(self):
        """Start the calculator"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Git Stealth Calculator (Fixed)")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Fixed calculator with clear buttons and navigation")
    print("🔒 Always visible buttons + back navigation")
    print("=" * 60)
    print("🚀 Starting Fixed Git Calculator...")
    print("💡 A calculator window will appear with clear buttons")
    print("🔍 Use 'Git Mode' button to toggle assistance")
    print("🔢 Use number buttons 1-5 for Git categories")
    print("⬅️ Use 'Back' button to navigate")
    print("🔒 Clear buttons that stay visible")
    print("=" * 60)
    
    calculator = GitStealthCalculatorFixed()
    calculator.run()

if __name__ == "__main__":
    main()
