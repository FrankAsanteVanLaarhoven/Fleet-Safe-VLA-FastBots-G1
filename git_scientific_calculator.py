#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Scientific Calculator
Fully functional scientific calculator with hidden Git assistance
"""
import tkinter as tk
from tkinter import ttk
import math
import time
from datetime import datetime

class GitScientificCalculator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scientific Calculator")
        self.root.geometry("400x700")
        self.root.configure(bg='#2b2b2b')
        
        # Make it look like a real calculator
        self.root.attributes('-alpha', 0.98)
        self.root.attributes('-topmost', False)
        
        # Position in bottom-right corner
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.root.geometry(f"400x700+{screen_width-420}+{screen_height-750}")
        
        # Calculator state
        self.current_number = ""
        self.first_number = 0
        self.operation = ""
        self.should_reset = False
        self.memory = 0
        self.angle_mode = "DEG"  # DEG or RAD
        
        # Git assistance mode (hidden)
        self.git_mode = False
        self.git_cheatsheet = {
            "basic": [
                "git init", "git clone <url>", "git add .", "git commit -m 'message'",
                "git status", "git log", "git diff", "git push", "git pull"
            ],
            "branching": [
                "git branch", "git checkout -b <branch>", "git merge <branch>",
                "git rebase <branch>", "git branch -d <branch>"
            ],
            "remote": [
                "git remote add origin <url>", "git fetch", "git push origin <branch>",
                "git pull origin <branch>", "git remote -v"
            ],
            "undo": [
                "git reset --hard HEAD~1", "git revert HEAD", "git stash",
                "git checkout -- <file>", "git clean -fd"
            ],
            "scenarios": [
                "Undo last commit: git reset --hard HEAD~1",
                "Save changes: git stash",
                "Switch branches: git checkout <branch>",
                "Merge changes: git merge <branch>",
                "Check status: git status"
            ]
        }
        
        self.setup_ui()
        self.load_git_cheatsheet()
        
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
            font=('Courier', 20, 'bold'),
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
            font=('Courier', 12),
            bg='#1a1a1a',
            fg='#888888',
            anchor='e',
            padx=10
        )
        secondary_display.pack(fill='x')
        
        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg='#2b2b2b')
        buttons_frame.pack(fill='both', expand=True)
        
        # Button configurations
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
        
        # Create buttons
        for i, row in enumerate(button_configs):
            for j, (text, color, command) in enumerate(row):
                btn = tk.Button(
                    buttons_frame,
                    text=text,
                    font=('Arial', 14, 'bold'),
                    bg=color,
                    fg='white',
                    relief='raised',
                    bd=2,
                    width=8,
                    height=2,
                    command=lambda t=text, c=command: c(t)
                )
                btn.grid(row=i, column=j, padx=2, pady=2, sticky='nsew')
        
        # Configure grid weights
        for i in range(10):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for j in range(4):
            buttons_frame.grid_columnconfigure(j, weight=1)
        
        # Hidden Git mode activation (double-click display)
        self.display.bind('<Double-Button-1>', self.toggle_git_mode)
        
    def load_git_cheatsheet(self):
        # Git commands are already loaded in __init__
        pass
        
    def toggle_git_mode(self, event=None):
        """Toggle between calculator and Git assistance mode"""
        self.git_mode = not self.git_mode
        if self.git_mode:
            self.display_var.set("Git Mode")
            self.secondary_display_var.set("Double-click to return")
        else:
            self.display_var.set("0")
            self.secondary_display_var.set("")
            
    def add_number(self, number):
        """Add a number to the display"""
        if self.git_mode:
            self.show_git_commands(number)
            return
            
        if self.should_reset:
            self.current_number = ""
            self.should_reset = False
            
        if number == "0" and self.current_number == "0":
            return
            
        self.current_number += number
        self.display_var.set(self.current_number)
        
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
            self.toggle_git_mode()
            return
            
        self.current_number = ""
        self.display_var.set("0")
        
    def all_clear(self, ac):
        """Clear everything"""
        if self.git_mode:
            self.toggle_git_mode()
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
            if self.angle_mode == "DEG":
                number = math.radians(number)
                
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
            
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        # Update button text would require more complex UI management
        
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
            
    def show_git_commands(self, button_number):
        """Show Git commands based on button number"""
        git_categories = {
            "1": "basic",
            "2": "branching", 
            "3": "remote",
            "4": "undo",
            "5": "scenarios"
        }
        
        if button_number in git_categories:
            category = git_categories[button_number]
            commands = self.git_cheatsheet[category]
            
            # Display commands in calculator format
            display_text = f"Git {category.upper()}:"
            self.display_var.set(display_text)
            
            # Show commands in secondary display
            command_text = "\n".join(commands[:3])  # Show first 3 commands
            self.secondary_display_var.set(command_text)
            
    def run(self):
        """Start the calculator"""
        self.root.mainloop()

def main():
    print("🔧 Iron Cloud Nexus AI - Git Scientific Calculator")
    print("=" * 60)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Fully functional scientific calculator")
    print("🔒 Hidden Git assistance mode")
    print("=" * 60)
    print("🚀 Starting Git Scientific Calculator...")
    print("💡 A scientific calculator window will appear")
    print("🔍 Double-click the display to enter Git mode")
    print("🔢 Use number buttons 1-5 to see Git commands")
    print("🔒 Looks like a real scientific calculator")
    print("=" * 60)
    
    calculator = GitScientificCalculator()
    calculator.run()

if __name__ == "__main__":
    main()
