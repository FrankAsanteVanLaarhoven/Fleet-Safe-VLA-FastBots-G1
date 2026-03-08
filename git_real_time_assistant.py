#!/usr/bin/env python3
"""
Iron Cloud Nexus AI - Git Real-Time Assistant
Real-time assistance for Outlier Git skill screening
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, List, Any
import re

class GitRealTimeAssistant:
    def __init__(self):
        self.git_knowledge_base = {
            "basic_commands": {
                "init": {
                    "command": "git init",
                    "description": "Initialize a new Git repository",
                    "when_to_use": "Starting a new project",
                    "examples": ["git init", "git init my-project"]
                },
                "clone": {
                    "command": "git clone <repository>",
                    "description": "Clone a repository from remote source",
                    "when_to_use": "Getting an existing project",
                    "examples": ["git clone https://github.com/user/repo.git"]
                },
                "add": {
                    "command": "git add <files>",
                    "description": "Stage files for commit",
                    "when_to_use": "Before committing changes",
                    "examples": ["git add .", "git add file.txt", "git add *.js"]
                },
                "commit": {
                    "command": "git commit -m \"message\"",
                    "description": "Commit staged changes",
                    "when_to_use": "After staging files",
                    "examples": ["git commit -m \"Initial commit\""]
                },
                "status": {
                    "command": "git status",
                    "description": "Show repository status",
                    "when_to_use": "Check what files are staged/modified",
                    "examples": ["git status", "git status --short"]
                },
                "log": {
                    "command": "git log",
                    "description": "Show commit history",
                    "when_to_use": "View previous commits",
                    "examples": ["git log", "git log --oneline"]
                }
            },
            "branching": {
                "branch": {
                    "command": "git branch",
                    "description": "List, create, or delete branches",
                    "when_to_use": "Manage branches",
                    "examples": ["git branch", "git branch feature-branch"]
                },
                "checkout": {
                    "command": "git checkout <branch>",
                    "description": "Switch between branches",
                    "when_to_use": "Change working branch",
                    "examples": ["git checkout main", "git checkout -b new-branch"]
                },
                "merge": {
                    "command": "git merge <branch>",
                    "description": "Merge branches",
                    "when_to_use": "Combine changes from different branches",
                    "examples": ["git merge feature-branch"]
                }
            },
            "remote_operations": {
                "remote": {
                    "command": "git remote",
                    "description": "Manage remote repositories",
                    "when_to_use": "Configure remote connections",
                    "examples": ["git remote -v", "git remote add origin <url>"]
                },
                "push": {
                    "command": "git push <remote> <branch>",
                    "description": "Push commits to remote repository",
                    "when_to_use": "Upload local changes to remote",
                    "examples": ["git push origin main", "git push -u origin feature-branch"]
                },
                "pull": {
                    "command": "git pull <remote> <branch>",
                    "description": "Fetch and merge from remote repository",
                    "when_to_use": "Get latest changes from remote",
                    "examples": ["git pull origin main"]
                },
                "fetch": {
                    "command": "git fetch <remote>",
                    "description": "Download objects from remote repository",
                    "when_to_use": "Get remote changes without merging",
                    "examples": ["git fetch origin"]
                }
            },
            "advanced_concepts": {
                "reset": {
                    "command": "git reset <mode> <commit>",
                    "description": "Reset current branch to specified commit",
                    "when_to_use": "Undo commits or changes",
                    "examples": ["git reset --soft HEAD~1", "git reset --hard HEAD~1"]
                },
                "revert": {
                    "command": "git revert <commit>",
                    "description": "Create new commit that undoes changes",
                    "when_to_use": "Safely undo changes",
                    "examples": ["git revert HEAD"]
                },
                "stash": {
                    "command": "git stash",
                    "description": "Temporarily save changes",
                    "when_to_use": "Save work in progress",
                    "examples": ["git stash", "git stash pop"]
                },
                "rebase": {
                    "command": "git rebase <branch>",
                    "description": "Reapply commits on top of another branch",
                    "when_to_use": "Clean up commit history",
                    "examples": ["git rebase main"]
                }
            }
        }
        
        self.common_patterns = {
            "initialize_repository": ["git init"],
            "stage_files": ["git add .", "git add <file>"],
            "commit_changes": ["git commit -m \"<message>\""],
            "check_status": ["git status"],
            "view_history": ["git log"],
            "create_branch": ["git checkout -b <branch>", "git branch <branch>"],
            "switch_branch": ["git checkout <branch>"],
            "merge_branch": ["git merge <branch>"],
            "push_to_remote": ["git push origin <branch>", "git push -u origin <branch>"],
            "pull_from_remote": ["git pull origin <branch>"],
            "undo_commit_keep_changes": ["git reset --soft HEAD~1"],
            "undo_commit_discard_changes": ["git reset --hard HEAD~1"],
            "save_work_progress": ["git stash"],
            "restore_work_progress": ["git stash pop"]
        }
        
        self.scenario_solutions = {
            "new_project_setup": [
                "git init",
                "git add .",
                "git commit -m \"Initial commit\""
            ],
            "feature_development": [
                "git checkout -b feature/new-feature",
                "git add .",
                "git commit -m \"feat: add new feature\"",
                "git push -u origin feature/new-feature"
            ],
            "merge_feature": [
                "git checkout main",
                "git pull origin main",
                "git merge feature/new-feature",
                "git push origin main"
            ],
            "undo_last_commit": [
                "git reset --soft HEAD~1"
            ],
            "save_and_switch": [
                "git stash",
                "git checkout other-branch",
                "git stash pop"
            ]
        }
    
    def analyze_question(self, question_text: str) -> Dict[str, Any]:
        """Analyze a Git question and provide assistance"""
        question_lower = question_text.lower()
        
        # Identify question type
        question_type = "unknown"
        if "initialize" in question_lower or "new repository" in question_lower:
            question_type = "initialization"
        elif "stage" in question_lower or "add" in question_lower:
            question_type = "staging"
        elif "commit" in question_lower:
            question_type = "committing"
        elif "branch" in question_lower:
            question_type = "branching"
        elif "push" in question_lower or "remote" in question_lower:
            question_type = "remote_operations"
        elif "undo" in question_lower or "reset" in question_lower:
            question_type = "undoing_changes"
        elif "stash" in question_lower:
            question_type = "stashing"
        elif "merge" in question_lower:
            question_type = "merging"
        elif "pull" in question_lower:
            question_type = "pulling"
        elif "log" in question_lower or "history" in question_lower:
            question_type = "viewing_history"
        
        # Extract key concepts
        concepts = []
        for category, commands in self.git_knowledge_base.items():
            for command_name, details in commands.items():
                if command_name in question_lower or details['command'].split()[1] in question_lower:
                    concepts.append({
                        "category": category,
                        "command": details['command'],
                        "description": details['description'],
                        "when_to_use": details['when_to_use'],
                        "examples": details['examples']
                    })
        
        return {
            "question_type": question_type,
            "concepts": concepts,
            "suggested_commands": self.get_suggested_commands(question_type),
            "explanation": self.get_explanation(question_type)
        }
    
    def get_suggested_commands(self, question_type: str) -> List[str]:
        """Get suggested commands based on question type"""
        suggestions = {
            "initialization": ["git init"],
            "staging": ["git add .", "git add <file>"],
            "committing": ["git commit -m \"<message>\""],
            "branching": ["git checkout -b <branch>", "git branch <branch>"],
            "remote_operations": ["git push origin <branch>", "git remote add origin <url>"],
            "undoing_changes": ["git reset --soft HEAD~1", "git reset --hard HEAD~1"],
            "stashing": ["git stash", "git stash pop"],
            "merging": ["git merge <branch>"],
            "pulling": ["git pull origin <branch>"],
            "viewing_history": ["git log", "git log --oneline"]
        }
        
        return suggestions.get(question_type, [])
    
    def get_explanation(self, question_type: str) -> str:
        """Get explanation based on question type"""
        explanations = {
            "initialization": "Use 'git init' to start a new Git repository. This creates a .git directory that tracks all changes.",
            "staging": "Use 'git add' to stage files before committing. 'git add .' stages all modified files.",
            "committing": "Use 'git commit -m \"message\"' to create a new commit with staged changes. Always include a descriptive message.",
            "branching": "Use 'git checkout -b <branch>' to create and switch to a new branch. This keeps main branch clean.",
            "remote_operations": "Use 'git push origin <branch>' to upload commits to remote repository. Use -u flag for new branches.",
            "undoing_changes": "Use 'git reset --soft HEAD~1' to undo last commit but keep changes staged. Use --hard to discard changes.",
            "stashing": "Use 'git stash' to temporarily save uncommitted changes. Use 'git stash pop' to restore them.",
            "merging": "Use 'git merge <branch>' to combine changes from different branches into current branch.",
            "pulling": "Use 'git pull origin <branch>' to download and merge changes from remote repository.",
            "viewing_history": "Use 'git log' to view commit history. Use 'git log --oneline' for compact view."
        }
        
        return explanations.get(question_type, "This appears to be a Git-related question. Consider the basic Git workflow: init → add → commit → push.")
    
    def provide_real_time_assistance(self, question: str) -> Dict[str, Any]:
        """Provide real-time assistance for a Git question"""
        print(f"\n🔍 Analyzing question: {question}")
        print("-" * 60)
        
        analysis = self.analyze_question(question)
        
        print(f"📋 Question Type: {analysis['question_type'].replace('_', ' ').title()}")
        print(f"💡 Explanation: {analysis['explanation']}")
        
        if analysis['suggested_commands']:
            print(f"\n🎯 Suggested Commands:")
            for i, command in enumerate(analysis['suggested_commands'], 1):
                print(f"  {i}. {command}")
        
        if analysis['concepts']:
            print(f"\n📚 Related Concepts:")
            for concept in analysis['concepts']:
                print(f"  • {concept['command']} - {concept['description']}")
                print(f"    When to use: {concept['when_to_use']}")
        
        return analysis
    
    def handle_scenario_question(self, scenario: str) -> List[str]:
        """Handle scenario-based questions"""
        scenario_lower = scenario.lower()
        
        if "new project" in scenario_lower or "initialize" in scenario_lower:
            return self.scenario_solutions["new_project_setup"]
        elif "feature" in scenario_lower and "branch" in scenario_lower:
            return self.scenario_solutions["feature_development"]
        elif "merge" in scenario_lower:
            return self.scenario_solutions["merge_feature"]
        elif "undo" in scenario_lower and "commit" in scenario_lower:
            return self.scenario_solutions["undo_last_commit"]
        elif "save" in scenario_lower and "switch" in scenario_lower:
            return self.scenario_solutions["save_and_switch"]
        
        return ["git status", "git add .", "git commit -m \"<message>\""]
    
    def quick_reference(self) -> Dict[str, List[str]]:
        """Provide quick reference for common Git operations"""
        return {
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
    
    def start_assistance_mode(self):
        """Start real-time assistance mode"""
        print("🔧 Iron Cloud Nexus AI - Git Real-Time Assistant")
        print("=" * 70)
        print("🎯 Ready to assist with Outlier Git screening!")
        print("💡 Type your Git questions and I'll help you answer them")
        print("📋 Type 'help' for quick reference, 'quit' to exit")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\n❓ Enter your Git question or scenario: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Good luck with your Git screening!")
                    break
                elif user_input.lower() == 'help':
                    self.show_quick_reference()
                elif user_input.lower() == 'scenarios':
                    self.show_common_scenarios()
                else:
                    self.provide_real_time_assistance(user_input)
                    
            except KeyboardInterrupt:
                print("\n👋 Good luck with your Git screening!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_quick_reference(self):
        """Show quick reference guide"""
        print("\n📖 Git Quick Reference")
        print("=" * 60)
        
        quick_ref = self.quick_reference()
        for category, commands in quick_ref.items():
            print(f"\n📋 {category}:")
            for command in commands:
                print(f"  • {command}")
    
    def show_common_scenarios(self):
        """Show common Git scenarios"""
        print("\n🎯 Common Git Scenarios")
        print("=" * 60)
        
        for scenario_name, steps in self.scenario_solutions.items():
            print(f"\n📋 {scenario_name.replace('_', ' ').title()}:")
            for i, step in enumerate(steps, 1):
                print(f"  {i}. {step}")

def main():
    """Main Git real-time assistant program"""
    assistant = GitRealTimeAssistant()
    
    print("🔧 Iron Cloud Nexus AI - Git Real-Time Assistant")
    print("=" * 70)
    print("🎯 Target: Outlier Git Skill Screening")
    print("⚡ Real-time assistance and guidance")
    print("=" * 70)
    
    # Example questions for demonstration
    example_questions = [
        "What command initializes a new Git repository?",
        "How do you stage all files for commit?",
        "What command creates and switches to a new branch?",
        "How do you push a new branch to remote?",
        "What does git pull do?",
        "How do you undo the last commit but keep changes?"
    ]
    
    print("\n🚀 Testing Git Real-Time Assistant...")
    
    for question in example_questions:
        assistant.provide_real_time_assistance(question)
        print("\n" + "=" * 60)
        time.sleep(1)
    
    print("\n🎉 Git Real-Time Assistant Ready!")
    print("💡 You can now use this during your Git screening")
    print("📋 Type 'python git_real_time_assistant.py' to start assistance mode")
    
    # Start interactive mode
    print("\n🔧 Starting Interactive Assistance Mode...")
    assistant.start_assistance_mode()

if __name__ == "__main__":
    main()
