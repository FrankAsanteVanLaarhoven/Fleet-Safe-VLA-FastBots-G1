#!/usr/bin/env python3
"""
Frontend Clean Code Agent
=========================

Specialized agent for code analysis, refactoring, best practices,
code quality, and optimization for frontend technologies.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import ast
import tempfile
import os

logger = logging.getLogger(__name__)

@dataclass
class CodeAnalysisResult:
    file_path: str
    language: str
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    quality_score: float
    timestamp: datetime

class FrontendCleanCodeAgent:
    def __init__(self):
        self.agent_id = None
        self.name = "Frontend Clean Code Agent"
        self.type = "FrontendCleanCodeAgent"
        self.capabilities = [
            {
                "name": "code_analysis",
                "description": "Static code analysis and quality assessment",
                "performance_score": 0.93,
                "success_rate": 0.91,
                "avg_response_time": 4000
            },
            {
                "name": "refactoring",
                "description": "Automated code refactoring and improvement",
                "performance_score": 0.92,
                "success_rate": 0.90,
                "avg_response_time": 6000
            },
            {
                "name": "best_practices",
                "description": "Enforcement of coding best practices",
                "performance_score": 0.94,
                "success_rate": 0.92,
                "avg_response_time": 3000
            },
            {
                "name": "code_quality",
                "description": "Code quality metrics and improvement",
                "performance_score": 0.91,
                "success_rate": 0.89,
                "avg_response_time": 5000
            },
            {
                "name": "optimization",
                "description": "Performance and bundle optimization",
                "performance_score": 0.90,
                "success_rate": 0.88,
                "avg_response_time": 8000
            }
        ]
        self.max_concurrent_tasks = 3
        self.performance_metrics = {
            "success_rate": 0.91,
            "avg_response_time": 4000,
            "files_analyzed": 0,
            "issues_found": 0,
            "refactoring_suggestions": 0
        }
        self.analysis_results: List[CodeAnalysisResult] = []
    
    async def register_with_orchestrator(self, orchestrator):
        """Register this agent with the orchestrator."""
        agent_data = {
            "name": self.name,
            "type": self.type,
            "capabilities": self.capabilities,
            "max_concurrent_tasks": self.max_concurrent_tasks,
            "performance_metrics": self.performance_metrics
        }
        
        self.agent_id = await orchestrator.register_agent(agent_data)
        logger.info(f"Frontend Clean Code Agent registered with ID: {self.agent_id}")
        return self.agent_id
    
    async def execute_clean_code_task(self, task_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a clean code task based on the payload."""
        start_time = datetime.now()
        
        try:
            task_type = task_payload.get('task_type', 'code_analysis')
            file_path = task_payload.get('file_path')
            code_content = task_payload.get('code_content')
            language = task_payload.get('language', 'javascript')
            config = task_payload.get('config', {})
            
            logger.info(f"Executing {task_type} for {file_path}")
            
            if task_type == 'code_analysis':
                result = await self._analyze_code(code_content, language, config)
            elif task_type == 'refactoring':
                result = await self._refactor_code(code_content, language, config)
            elif task_type == 'best_practices':
                result = await self._check_best_practices(code_content, language, config)
            elif task_type == 'code_quality':
                result = await self._assess_code_quality(code_content, language, config)
            elif task_type == 'optimization':
                result = await self._optimize_code(code_content, language, config)
            else:
                result = {
                    "status": "failed",
                    "error": f"Unknown task type: {task_type}",
                    "details": {}
                }
            
            # Record analysis result
            duration = (datetime.now() - start_time).total_seconds()
            analysis_result = CodeAnalysisResult(
                file_path=file_path,
                language=language,
                issues=result.get("issues", []),
                suggestions=result.get("suggestions", []),
                quality_score=result.get("quality_score", 0.0),
                timestamp=datetime.now()
            )
            self.analysis_results.append(analysis_result)
            
            # Update performance metrics
            self._update_performance_metrics(analysis_result)
            
            return {
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "task_type": task_type,
                "file_path": file_path,
                "language": language,
                "result": result,
                "duration": duration,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error executing clean code task: {e}")
            return {
                "agent_id": self.agent_id,
                "agent_name": self.name,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _analyze_code(self, code_content: str, language: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code for issues and improvements."""
        try:
            issues = []
            suggestions = []
            
            if language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                issues, suggestions = await self._analyze_javascript_code(code_content)
            elif language.lower() in ['css', 'scss', 'sass']:
                issues, suggestions = await self._analyze_css_code(code_content)
            elif language.lower() in ['html', 'htm']:
                issues, suggestions = await self._analyze_html_code(code_content)
            elif language.lower() in ['jsx', 'tsx']:
                issues, suggestions = await self._analyze_react_code(code_content)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(issues, suggestions)
            
            return {
                "status": "completed",
                "issues": issues,
                "suggestions": suggestions,
                "quality_score": quality_score,
                "language": language,
                "lines_of_code": len(code_content.split('\n')),
                "complexity_score": self._calculate_complexity(code_content)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "issues": [],
                "suggestions": []
            }
    
    async def _analyze_javascript_code(self, code_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Analyze JavaScript/TypeScript code."""
        issues = []
        suggestions = []
        
        # Check for common JavaScript issues
        lines = code_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for console.log statements
            if 'console.log(' in line:
                issues.append({
                    "type": "warning",
                    "line": i,
                    "message": "Console.log statement found - consider removing for production",
                    "severity": "medium",
                    "suggestion": "Use proper logging framework or remove console.log"
                })
            
            # Check for var declarations
            if re.search(r'\bvar\s+', line):
                issues.append({
                    "type": "warning",
                    "line": i,
                    "message": "Using 'var' instead of 'let' or 'const'",
                    "severity": "medium",
                    "suggestion": "Replace 'var' with 'let' or 'const'"
                })
            
            # Check for long functions
            if len(line.strip()) > 120:
                issues.append({
                    "type": "warning",
                    "line": i,
                    "message": "Line exceeds 120 characters",
                    "severity": "low",
                    "suggestion": "Break long lines for better readability"
                })
        
        # Check for unused variables (simplified)
        if 'function' in code_content and 'return' not in code_content:
            suggestions.append({
                "type": "improvement",
                "message": "Function might not return a value",
                "suggestion": "Add explicit return statement or use arrow function"
            })
        
        return issues, suggestions
    
    async def _analyze_css_code(self, code_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Analyze CSS code."""
        issues = []
        suggestions = []
        
        lines = code_content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for !important usage
            if '!important' in line:
                issues.append({
                    "type": "warning",
                    "line": i,
                    "message": "Using !important - consider refactoring",
                    "severity": "medium",
                    "suggestion": "Use more specific selectors instead of !important"
                })
            
            # Check for inline styles
            if 'style=' in line:
                issues.append({
                    "type": "warning",
                    "line": i,
                    "message": "Inline styles found",
                    "severity": "medium",
                    "suggestion": "Move styles to external CSS file"
                })
        
        return issues, suggestions
    
    async def _analyze_html_code(self, code_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Analyze HTML code."""
        issues = []
        suggestions = []
        
        # Check for missing alt attributes
        if '<img' in code_content and 'alt=' not in code_content:
            issues.append({
                "type": "warning",
                "message": "Images without alt attributes found",
                "severity": "high",
                "suggestion": "Add alt attributes to all images for accessibility"
            })
        
        # Check for semantic HTML
        if '<div' in code_content and '<section>' not in code_content:
            suggestions.append({
                "type": "improvement",
                "message": "Consider using semantic HTML elements",
                "suggestion": "Use <section>, <article>, <nav>, <header>, <footer> instead of <div>"
            })
        
        return issues, suggestions
    
    async def _analyze_react_code(self, code_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Analyze React/JSX code."""
        issues = []
        suggestions = []
        
        # Check for React hooks usage
        if 'useState' in code_content or 'useEffect' in code_content:
            if 'import' not in code_content or 'react' not in code_content:
                issues.append({
                    "type": "error",
                    "message": "React hooks used without React import",
                    "severity": "high",
                    "suggestion": "Add 'import React from \"react\"' at the top"
                })
        
        # Check for prop types
        if 'function' in code_content and 'props' in code_content:
            suggestions.append({
                "type": "improvement",
                "message": "Consider adding PropTypes or TypeScript for type safety",
                "suggestion": "Add PropTypes or convert to TypeScript"
            })
        
        return issues, suggestions
    
    async def _refactor_code(self, code_content: str, language: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Refactor code for better quality."""
        try:
            refactored_code = code_content
            changes = []
            
            if language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                refactored_code, changes = await self._refactor_javascript_code(code_content)
            elif language.lower() in ['css', 'scss', 'sass']:
                refactored_code, changes = await self._refactor_css_code(code_content)
            
            return {
                "status": "completed",
                "refactored_code": refactored_code,
                "changes": changes,
                "improvement_score": len(changes) * 0.1
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "refactored_code": code_content,
                "changes": []
            }
    
    async def _refactor_javascript_code(self, code_content: str) -> tuple[str, List[Dict[str, Any]]]:
        """Refactor JavaScript code."""
        refactored_code = code_content
        changes = []
        
        # Replace var with const/let
        var_pattern = r'\bvar\s+(\w+)'
        matches = re.findall(var_pattern, code_content)
        for var_name in matches:
            refactored_code = re.sub(f'\\bvar\\s+{var_name}\\b', f'const {var_name}', refactored_code, count=1)
            changes.append({
                "type": "refactor",
                "description": f"Replaced 'var {var_name}' with 'const {var_name}'",
                "improvement": "Better variable scoping"
            })
        
        # Remove console.log statements
        console_pattern = r'console\.log\([^)]*\);?\s*'
        if re.search(console_pattern, refactored_code):
            refactored_code = re.sub(console_pattern, '', refactored_code)
            changes.append({
                "type": "cleanup",
                "description": "Removed console.log statements",
                "improvement": "Cleaner production code"
            })
        
        return refactored_code, changes
    
    async def _refactor_css_code(self, code_content: str) -> tuple[str, List[Dict[str, Any]]]:
        """Refactor CSS code."""
        refactored_code = code_content
        changes = []
        
        # Remove !important declarations
        important_pattern = r'!important\s*;?'
        if re.search(important_pattern, refactored_code):
            refactored_code = re.sub(important_pattern, ';', refactored_code)
            changes.append({
                "type": "refactor",
                "description": "Removed !important declarations",
                "improvement": "Better CSS specificity management"
            })
        
        return refactored_code, changes
    
    async def _check_best_practices(self, code_content: str, language: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check code against best practices."""
        try:
            violations = []
            recommendations = []
            
            if language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                violations, recommendations = await self._check_javascript_best_practices(code_content)
            
            compliance_score = max(0, 100 - len(violations) * 10)
            
            return {
                "status": "completed",
                "violations": violations,
                "recommendations": recommendations,
                "compliance_score": compliance_score,
                "best_practices_followed": len(violations) == 0
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "violations": [],
                "recommendations": []
            }
    
    async def _check_javascript_best_practices(self, code_content: str) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Check JavaScript best practices."""
        violations = []
        recommendations = []
        
        # Check for proper error handling
        if 'try' in code_content and 'catch' not in code_content:
            violations.append({
                "rule": "error_handling",
                "message": "Try block without catch",
                "severity": "medium"
            })
        
        # Check for consistent naming conventions
        if re.search(r'[A-Z][a-z]*[A-Z]', code_content):
            recommendations.append({
                "rule": "naming_convention",
                "message": "Consider using camelCase for variables and functions",
                "severity": "low"
            })
        
        return violations, recommendations
    
    async def _assess_code_quality(self, code_content: str, language: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall code quality."""
        try:
            metrics = {
                "lines_of_code": len(code_content.split('\n')),
                "characters": len(code_content),
                "complexity": self._calculate_complexity(code_content),
                "readability": self._calculate_readability(code_content),
                "maintainability": self._calculate_maintainability(code_content)
            }
            
            overall_score = (
                metrics["readability"] * 0.4 +
                metrics["maintainability"] * 0.4 +
                (1 - metrics["complexity"]) * 0.2
            )
            
            return {
                "status": "completed",
                "metrics": metrics,
                "overall_score": overall_score,
                "quality_level": self._get_quality_level(overall_score)
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "metrics": {},
                "overall_score": 0.0
            }
    
    async def _optimize_code(self, code_content: str, language: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize code for performance."""
        try:
            optimizations = []
            optimized_code = code_content
            
            if language.lower() in ['javascript', 'js', 'typescript', 'ts']:
                optimized_code, optimizations = await self._optimize_javascript_code(code_content)
            
            return {
                "status": "completed",
                "optimized_code": optimized_code,
                "optimizations": optimizations,
                "performance_improvement": len(optimizations) * 0.05
            }
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "optimized_code": code_content,
                "optimizations": []
            }
    
    async def _optimize_javascript_code(self, code_content: str) -> tuple[str, List[Dict[str, Any]]]:
        """Optimize JavaScript code."""
        optimized_code = code_content
        optimizations = []
        
        # Optimize loops
        if 'for (let i = 0; i <' in optimized_code:
            optimizations.append({
                "type": "loop_optimization",
                "description": "Consider using forEach or map for array operations",
                "improvement": "Better performance and readability"
            })
        
        return optimized_code, optimizations
    
    def _calculate_quality_score(self, issues: List[Dict[str, Any]], suggestions: List[Dict[str, Any]]) -> float:
        """Calculate overall quality score."""
        base_score = 1.0
        
        # Deduct points for issues
        for issue in issues:
            severity = issue.get("severity", "medium")
            if severity == "high":
                base_score -= 0.1
            elif severity == "medium":
                base_score -= 0.05
            elif severity == "low":
                base_score -= 0.02
        
        # Add points for suggestions
        base_score += len(suggestions) * 0.01
        
        return max(0.0, min(1.0, base_score))
    
    def _calculate_complexity(self, code_content: str) -> float:
        """Calculate code complexity score."""
        # Simplified complexity calculation
        complexity_factors = [
            len(re.findall(r'\bif\b', code_content)),
            len(re.findall(r'\bfor\b', code_content)),
            len(re.findall(r'\bwhile\b', code_content)),
            len(re.findall(r'\bfunction\b', code_content))
        ]
        
        return sum(complexity_factors) / 100.0
    
    def _calculate_readability(self, code_content: str) -> float:
        """Calculate code readability score."""
        lines = code_content.split('\n')
        long_lines = sum(1 for line in lines if len(line.strip()) > 120)
        
        return max(0.0, 1.0 - (long_lines / len(lines)))
    
    def _calculate_maintainability(self, code_content: str) -> float:
        """Calculate code maintainability score."""
        # Simplified maintainability calculation
        factors = [
            1.0 if 'function' in code_content else 0.8,
            1.0 if 'const' in code_content or 'let' in code_content else 0.7,
            1.0 if 'import' in code_content else 0.9
        ]
        
        return sum(factors) / len(factors)
    
    def _get_quality_level(self, score: float) -> str:
        """Get quality level based on score."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "fair"
        elif score >= 0.6:
            return "poor"
        else:
            return "very_poor"
    
    def _update_performance_metrics(self, analysis_result: CodeAnalysisResult):
        """Update agent performance metrics."""
        self.performance_metrics["files_analyzed"] += 1
        self.performance_metrics["issues_found"] += len(analysis_result.issues)
        self.performance_metrics["refactoring_suggestions"] += len(analysis_result.suggestions)
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current status of the frontend clean code agent."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.type,
            "capabilities": self.capabilities,
            "performance_metrics": self.performance_metrics,
            "recent_analyses": [
                {
                    "file_path": result.file_path,
                    "language": result.language,
                    "quality_score": result.quality_score,
                    "issues_count": len(result.issues),
                    "timestamp": result.timestamp.isoformat()
                }
                for result in self.analysis_results[-10:]  # Last 10 results
            ]
        } 