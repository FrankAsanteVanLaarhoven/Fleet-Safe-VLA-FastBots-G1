#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Skill Preparation System
Comprehensive preparation for Outlier Git skill screening
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import random

class GitSkillPreparation:
    def __init__(self):
        self.git_concepts = {
            "basic_commands": {
                "git_init": {
                    "command": "git init",
                    "description": "Initialize a new Git repository",
                    "usage": "Creates a .git directory in current folder",
                    "examples": ["git init", "git init my-project"]
                },
                "git_clone": {
                    "command": "git clone <repository>",
                    "description": "Clone a repository from remote source",
                    "usage": "Downloads repository to local machine",
                    "examples": ["git clone https://github.com/user/repo.git", "git clone https://github.com/user/repo.git my-folder"]
                },
                "git_add": {
                    "command": "git add <files>",
                    "description": "Stage files for commit",
                    "usage": "Adds files to staging area",
                    "examples": ["git add .", "git add file.txt", "git add *.js"]
                },
                "git_commit": {
                    "command": "git commit -m \"message\"",
                    "description": "Commit staged changes",
                    "usage": "Creates a new commit with staged changes",
                    "examples": ["git commit -m \"Initial commit\"", "git commit -m \"feat: add new feature\""]
                },
                "git_status": {
                    "command": "git status",
                    "description": "Show repository status",
                    "usage": "Displays working directory and staging area status",
                    "examples": ["git status", "git status --short"]
                },
                "git_log": {
                    "command": "git log",
                    "description": "Show commit history",
                    "usage": "Displays commit history with details",
                    "examples": ["git log", "git log --oneline", "git log --graph"]
                }
            },
            "branching": {
                "git_branch": {
                    "command": "git branch",
                    "description": "List, create, or delete branches",
                    "usage": "Manage branches in repository",
                    "examples": ["git branch", "git branch feature-branch", "git branch -d old-branch"]
                },
                "git_checkout": {
                    "command": "git checkout <branch>",
                    "description": "Switch between branches",
                    "usage": "Change working directory to specified branch",
                    "examples": ["git checkout main", "git checkout -b new-branch"]
                },
                "git_merge": {
                    "command": "git merge <branch>",
                    "description": "Merge branches",
                    "usage": "Combine changes from different branches",
                    "examples": ["git merge feature-branch", "git merge --no-ff feature-branch"]
                }
            },
            "remote_operations": {
                "git_remote": {
                    "command": "git remote",
                    "description": "Manage remote repositories",
                    "usage": "Configure remote repository connections",
                    "examples": ["git remote -v", "git remote add origin https://github.com/user/repo.git"]
                },
                "git_push": {
                    "command": "git push <remote> <branch>",
                    "description": "Push commits to remote repository",
                    "usage": "Upload local commits to remote repository",
                    "examples": ["git push origin main", "git push -u origin feature-branch"]
                },
                "git_pull": {
                    "command": "git pull <remote> <branch>",
                    "description": "Fetch and merge from remote repository",
                    "usage": "Download and integrate changes from remote",
                    "examples": ["git pull origin main", "git pull --rebase origin main"]
                },
                "git_fetch": {
                    "command": "git fetch <remote>",
                    "description": "Download objects from remote repository",
                    "usage": "Download changes without merging",
                    "examples": ["git fetch origin", "git fetch --all"]
                }
            },
            "advanced_concepts": {
                "git_reset": {
                    "command": "git reset <mode> <commit>",
                    "description": "Reset current branch to specified commit",
                    "usage": "Move HEAD and branch pointer to specified commit",
                    "examples": ["git reset --soft HEAD~1", "git reset --hard HEAD~1"]
                },
                "git_revert": {
                    "command": "git revert <commit>",
                    "description": "Create new commit that undoes changes",
                    "usage": "Safely undo changes by creating new commit",
                    "examples": ["git revert HEAD", "git revert abc1234"]
                },
                "git_stash": {
                    "command": "git stash",
                    "description": "Temporarily save changes",
                    "usage": "Save uncommitted changes for later use",
                    "examples": ["git stash", "git stash pop", "git stash list"]
                },
                "git_rebase": {
                    "command": "git rebase <branch>",
                    "description": "Reapply commits on top of another branch",
                    "usage": "Move commits to new base commit",
                    "examples": ["git rebase main", "git rebase -i HEAD~3"]
                }
            }
        }
        
        self.common_scenarios = [
            {
                "scenario": "Initialize a new repository and make first commit",
                "steps": [
                    "git init",
                    "git add .",
                    "git commit -m \"Initial commit\""
                ],
                "explanation": "This is the most basic Git workflow for starting a new project."
            },
            {
                "scenario": "Create and switch to a new feature branch",
                "steps": [
                    "git checkout -b feature/new-feature",
                    "git add .",
                    "git commit -m \"feat: add new feature\"",
                    "git push -u origin feature/new-feature"
                ],
                "explanation": "Standard workflow for developing new features without affecting main branch."
            },
            {
                "scenario": "Merge feature branch back to main",
                "steps": [
                    "git checkout main",
                    "git pull origin main",
                    "git merge feature/new-feature",
                    "git push origin main"
                ],
                "explanation": "Complete feature development workflow from branch creation to merge."
            },
            {
                "scenario": "Undo last commit while keeping changes",
                "steps": [
                    "git reset --soft HEAD~1"
                ],
                "explanation": "Removes last commit but keeps changes staged for recommit."
            },
            {
                "scenario": "Undo last commit and discard changes",
                "steps": [
                    "git reset --hard HEAD~1"
                ],
                "explanation": "Completely removes last commit and all changes (use with caution)."
            },
            {
                "scenario": "Save work in progress and switch branches",
                "steps": [
                    "git stash",
                    "git checkout other-branch",
                    "git stash pop"
                ],
                "explanation": "Temporarily save uncommitted changes to work on something else."
            }
        ]
        
        self.test_questions = [
            {
                "question": "What command initializes a new Git repository?",
                "options": ["git start", "git init", "git new", "git create"],
                "correct": "git init",
                "explanation": "git init creates a new Git repository in the current directory."
            },
            {
                "question": "What does 'git add .' do?",
                "options": ["Commits all changes", "Stages all files", "Shows status", "Creates branch"],
                "correct": "Stages all files",
                "explanation": "git add . stages all modified files in the current directory for commit."
            },
            {
                "question": "How do you create and switch to a new branch?",
                "options": ["git branch new-branch", "git checkout new-branch", "git checkout -b new-branch", "git switch new-branch"],
                "correct": "git checkout -b new-branch",
                "explanation": "git checkout -b creates a new branch and switches to it in one command."
            },
            {
                "question": "What command shows the commit history?",
                "options": ["git history", "git log", "git commits", "git show"],
                "correct": "git log",
                "explanation": "git log displays the commit history with details about each commit."
            },
            {
                "question": "How do you push a new branch to remote?",
                "options": ["git push branch", "git push -u origin branch", "git push origin", "git push new branch"],
                "correct": "git push -u origin branch",
                "explanation": "git push -u origin branch pushes the branch and sets upstream tracking."
            },
            {
                "question": "What does 'git pull' do?",
                "options": ["Push changes", "Fetch and merge", "Show status", "Create branch"],
                "correct": "Fetch and merge",
                "explanation": "git pull fetches changes from remote and merges them into current branch."
            },
            {
                "question": "How do you undo the last commit but keep changes staged?",
                "options": ["git reset --soft HEAD~1", "git reset --hard HEAD~1", "git revert HEAD", "git undo"],
                "correct": "git reset --soft HEAD~1",
                "explanation": "git reset --soft HEAD~1 undoes the last commit but keeps changes in staging area."
            },
            {
                "question": "What command temporarily saves uncommitted changes?",
                "options": ["git save", "git stash", "git store", "git cache"],
                "correct": "git stash",
                "explanation": "git stash temporarily saves uncommitted changes for later use."
            }
        ]
    
    def display_git_concepts(self):
        """Display all Git concepts organized by category"""
        print("🔧 Git Skill Preparation - Core Concepts")
        print("=" * 60)
        
        for category, commands in self.git_concepts.items():
            print(f"\n📚 {category.replace('_', ' ').title()}:")
            print("-" * 40)
            
            for command_name, details in commands.items():
                print(f"\n🔹 {details['command']}")
                print(f"   Description: {details['description']}")
                print(f"   Usage: {details['usage']}")
                print(f"   Examples: {', '.join(details['examples'])}")
    
    def practice_scenarios(self):
        """Practice common Git scenarios"""
        print("\n🎯 Git Practice Scenarios")
        print("=" * 60)
        
        for i, scenario in enumerate(self.common_scenarios, 1):
            print(f"\n📋 Scenario {i}: {scenario['scenario']}")
            print("-" * 50)
            print("Steps:")
            for j, step in enumerate(scenario['steps'], 1):
                print(f"  {j}. {step}")
            print(f"\n💡 Explanation: {scenario['explanation']}")
            print("\n" + "=" * 60)
    
    def take_practice_test(self):
        """Take a practice test with multiple choice questions"""
        print("\n📝 Git Practice Test")
        print("=" * 60)
        
        score = 0
        total_questions = len(self.test_questions)
        
        for i, question in enumerate(self.test_questions, 1):
            print(f"\n❓ Question {i}: {question['question']}")
            print("-" * 50)
            
            for j, option in enumerate(question['options'], 1):
                print(f"  {j}. {option}")
            
            # Simulate user input (in real scenario, this would be interactive)
            user_answer = question['correct']  # For demonstration, assume correct answer
            
            if user_answer == question['correct']:
                print("✅ Correct!")
                score += 1
            else:
                print(f"❌ Incorrect. The correct answer is: {question['correct']}")
            
            print(f"💡 {question['explanation']}")
            print("-" * 50)
        
        percentage = (score / total_questions) * 100
        print(f"\n🏆 Test Results: {score}/{total_questions} ({percentage:.1f}%)")
        
        if percentage >= 80:
            print("🎉 Excellent! You're ready for the Git screening!")
        elif percentage >= 60:
            print("👍 Good! Review the concepts and practice more.")
        else:
            print("📚 Keep studying! Focus on the concepts you missed.")
    
    def generate_quick_reference(self):
        """Generate a quick reference guide"""
        print("\n📖 Git Quick Reference Guide")
        print("=" * 60)
        
        quick_ref = {
            "Repository Setup": [
                "git init - Initialize new repository",
                "git clone <url> - Clone remote repository",
                "git remote add origin <url> - Add remote origin"
            ],
            "Basic Workflow": [
                "git add . - Stage all changes",
                "git commit -m \"message\" - Commit staged changes",
                "git status - Check repository status",
                "git log - View commit history"
            ],
            "Branching": [
                "git branch - List branches",
                "git checkout -b <branch> - Create and switch to branch",
                "git checkout <branch> - Switch to branch",
                "git merge <branch> - Merge branch into current"
            ],
            "Remote Operations": [
                "git push origin <branch> - Push to remote",
                "git pull origin <branch> - Pull from remote",
                "git fetch origin - Fetch from remote"
            ],
            "Undoing Changes": [
                "git reset --soft HEAD~1 - Undo commit, keep changes",
                "git reset --hard HEAD~1 - Undo commit, discard changes",
                "git revert <commit> - Create undo commit",
                "git stash - Save changes temporarily"
            ]
        }
        
        for category, commands in quick_ref.items():
            print(f"\n📋 {category}:")
            for command in commands:
                print(f"  • {command}")
    
    def save_preparation_guide(self, filename: str = None) -> str:
        """Save comprehensive preparation guide"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"~/Desktop/git_skill_preparation_guide_{timestamp}.md"
        
        filename = filename.replace("~/", f"{os.path.expanduser('~')}/")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 🔧 Git Skill Preparation Guide - Iron Cloud Nexus AI\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("**Target:** Outlier Git Skill Screening\n\n")
            
            f.write("## 📚 Core Git Concepts\n\n")
            
            for category, commands in self.git_concepts.items():
                f.write(f"### {category.replace('_', ' ').title()}\n\n")
                
                for command_name, details in commands.items():
                    f.write(f"#### `{details['command']}`\n")
                    f.write(f"- **Description:** {details['description']}\n")
                    f.write(f"- **Usage:** {details['usage']}\n")
                    f.write(f"- **Examples:**\n")
                    for example in details['examples']:
                        f.write(f"  ```bash\n{example}\n  ```\n")
                    f.write("\n")
            
            f.write("## 🎯 Common Scenarios\n\n")
            
            for i, scenario in enumerate(self.common_scenarios, 1):
                f.write(f"### Scenario {i}: {scenario['scenario']}\n\n")
                f.write("**Steps:**\n")
                for j, step in enumerate(scenario['steps'], 1):
                    f.write(f"{j}. `{step}`\n")
                f.write(f"\n**Explanation:** {scenario['explanation']}\n\n")
            
            f.write("## 📝 Practice Questions\n\n")
            
            for i, question in enumerate(self.test_questions, 1):
                f.write(f"### Question {i}\n")
                f.write(f"**{question['question']}**\n\n")
                f.write("**Options:**\n")
                for j, option in enumerate(question['options'], 1):
                    f.write(f"{j}. {option}\n")
                f.write(f"\n**Correct Answer:** {question['correct']}\n")
                f.write(f"**Explanation:** {question['explanation']}\n\n")
            
            f.write("## 🚀 Test Day Tips\n\n")
            f.write("1. **Stay Calm** - Git concepts are logical and systematic\n")
            f.write("2. **Read Carefully** - Pay attention to what each question asks\n")
            f.write("3. **Think Step by Step** - Break complex scenarios into parts\n")
            f.write("4. **Use Process of Elimination** - Eliminate obviously wrong answers\n")
            f.write("5. **Trust Your Knowledge** - You've prepared well!\n\n")
            
            f.write("## 📋 Quick Reference\n\n")
            
            quick_ref = {
                "Repository Setup": [
                    "git init - Initialize new repository",
                    "git clone <url> - Clone remote repository",
                    "git remote add origin <url> - Add remote origin"
                ],
                "Basic Workflow": [
                    "git add . - Stage all changes",
                    "git commit -m \"message\" - Commit staged changes",
                    "git status - Check repository status",
                    "git log - View commit history"
                ],
                "Branching": [
                    "git branch - List branches",
                    "git checkout -b <branch> - Create and switch to branch",
                    "git checkout <branch> - Switch to branch",
                    "git merge <branch> - Merge branch into current"
                ],
                "Remote Operations": [
                    "git push origin <branch> - Push to remote",
                    "git pull origin <branch> - Pull from remote",
                    "git fetch origin - Fetch from remote"
                ],
                "Undoing Changes": [
                    "git reset --soft HEAD~1 - Undo commit, keep changes",
                    "git reset --hard HEAD~1 - Undo commit, discard changes",
                    "git revert <commit> - Create undo commit",
                    "git stash - Save changes temporarily"
                ]
            }
            
            for category, commands in quick_ref.items():
                f.write(f"### {category}\n")
                for command in commands:
                    f.write(f"- {command}\n")
                f.write("\n")
            
            f.write("---\n")
            f.write("*Generated by Iron Cloud Nexus AI - Git Skill Preparation System*\n")
        
        print(f"\n📄 Git preparation guide saved to: {filename}")
        return filename

def main():
    """Main Git skill preparation program"""
    print("🔧 Iron Cloud Nexus AI - Git Skill Preparation")
    print("=" * 70)
    print("🎯 Target: Outlier Git Skill Screening")
    print("📚 Comprehensive preparation and practice system")
    print("=" * 70)
    
    # Initialize preparation system
    git_prep = GitSkillPreparation()
    
    print("\n🚀 Starting Git Skill Preparation...")
    
    # 1. Display core concepts
    git_prep.display_git_concepts()
    
    # 2. Practice scenarios
    git_prep.practice_scenarios()
    
    # 3. Take practice test
    git_prep.take_practice_test()
    
    # 4. Generate quick reference
    git_prep.generate_quick_reference()
    
    # 5. Save comprehensive guide
    guide_file = git_prep.save_preparation_guide()
    
    print("\n" + "=" * 70)
    print("🎉 Git Skill Preparation Complete!")
    print("📄 Comprehensive guide saved to your Desktop")
    print("🎯 You're now ready for the Outlier Git screening!")
    print("=" * 70)
    
    print("\n💡 Tips for Test Day:")
    print("• Stay calm and read questions carefully")
    print("• Think step by step for complex scenarios")
    print("• Use process of elimination for multiple choice")
    print("• Trust your preparation - you've got this!")
    print("• Remember: Git is logical and systematic")

if __name__ == "__main__":
    main()
