#!/usr/bin/env python3
"""
Microservices Agent System Demo
===============================

Comprehensive demonstration of the microservices agent system
with real-world examples and performance metrics.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import logging

# Import our microservices components
from backend.microservices_orchestrator import MicroservicesOrchestrator
from backend.agents.testing_agent import TestingAgent
from backend.agents.frontend_clean_code_agent import FrontendCleanCodeAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MicroservicesAgentDemo:
    def __init__(self):
        self.orchestrator = MicroservicesOrchestrator()
        self.testing_agent = TestingAgent()
        self.frontend_clean_code_agent = FrontendCleanCodeAgent()
        self.demo_results = []
        
    async def run_comprehensive_demo(self):
        """Run a comprehensive demonstration of the microservices agent system."""
        logger.info("🚀 Starting Microservices Agent System Demo")
        
        try:
            # Step 1: Initialize the system
            await self._initialize_system()
            
            # Step 2: Register agents
            await self._register_agents()
            
            # Step 3: Register MCP servers
            await self._register_mcp_servers()
            
            # Step 4: Run demonstration scenarios
            await self._run_demo_scenarios()
            
            # Step 5: Performance analysis
            await self._analyze_performance()
            
            # Step 6: Generate demo report
            await self._generate_demo_report()
            
            logger.info("✅ Microservices Agent System Demo completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise
    
    async def _initialize_system(self):
        """Initialize the microservices orchestrator."""
        logger.info("📋 Initializing Microservices Orchestrator...")
        
        # The orchestrator is already initialized in the constructor
        system_status = await self.orchestrator.get_system_status()
        
        logger.info(f"✅ System initialized - Status: {system_status}")
        self.demo_results.append({
            "step": "system_initialization",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "details": system_status
        })
    
    async def _register_agents(self):
        """Register specialized agents with the orchestrator."""
        logger.info("🤖 Registering specialized agents...")
        
        # Register testing agent
        testing_agent_id = await self.testing_agent.register_with_orchestrator(self.orchestrator)
        logger.info(f"✅ Testing Agent registered: {testing_agent_id}")
        
        # Register frontend clean code agent
        clean_code_agent_id = await self.frontend_clean_code_agent.register_with_orchestrator(self.orchestrator)
        logger.info(f"✅ Frontend Clean Code Agent registered: {clean_code_agent_id}")
        
        self.demo_results.append({
            "step": "agent_registration",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "testing_agent_id": testing_agent_id,
                "clean_code_agent_id": clean_code_agent_id,
                "total_agents": 2
            }
        })
    
    async def _register_mcp_servers(self):
        """Register MCP servers for different tool categories."""
        logger.info("🔧 Registering MCP servers...")
        
        # Testing MCP Server
        testing_mcp_server = {
            "name": "Testing Tools MCP Server",
            "tool_categories": ["ui_testing", "javascript_testing", "accessibility_testing", "performance_testing"],
            "available_tools": {
                "puppeteer": {
                    "name": "Puppeteer",
                    "description": "Headless Chrome automation",
                    "version": "21.0.0",
                    "status": "available"
                },
                "playwright": {
                    "name": "Playwright",
                    "description": "Cross-browser automation",
                    "version": "1.40.0",
                    "status": "available"
                },
                "jest": {
                    "name": "Jest",
                    "description": "JavaScript testing framework",
                    "version": "29.0.0",
                    "status": "available"
                },
                "lighthouse": {
                    "name": "Lighthouse",
                    "description": "Performance auditing",
                    "version": "11.0.0",
                    "status": "available"
                }
            }
        }
        
        # Frontend MCP Server
        frontend_mcp_server = {
            "name": "Frontend Tools MCP Server",
            "tool_categories": ["code_analysis", "refactoring", "optimization", "linting"],
            "available_tools": {
                "eslint": {
                    "name": "ESLint",
                    "description": "JavaScript linting",
                    "version": "8.0.0",
                    "status": "available"
                },
                "prettier": {
                    "name": "Prettier",
                    "description": "Code formatting",
                    "version": "3.0.0",
                    "status": "available"
                },
                "webpack": {
                    "name": "Webpack",
                    "description": "Module bundler",
                    "version": "5.0.0",
                    "status": "available"
                },
                "babel": {
                    "name": "Babel",
                    "description": "JavaScript compiler",
                    "version": "7.0.0",
                    "status": "available"
                }
            }
        }
        
        testing_server_id = await self.orchestrator.register_mcp_server(testing_mcp_server)
        frontend_server_id = await self.orchestrator.register_mcp_server(frontend_mcp_server)
        
        logger.info(f"✅ Testing MCP Server registered: {testing_server_id}")
        logger.info(f"✅ Frontend MCP Server registered: {frontend_server_id}")
        
        self.demo_results.append({
            "step": "mcp_server_registration",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "testing_server_id": testing_server_id,
                "frontend_server_id": frontend_server_id,
                "total_servers": 2
            }
        })
    
    async def _run_demo_scenarios(self):
        """Run various demonstration scenarios."""
        logger.info("🎯 Running demonstration scenarios...")
        
        scenarios = [
            await self._scenario_1_ui_testing(),
            await self._scenario_2_code_analysis(),
            await self._scenario_3_performance_testing(),
            await self._scenario_4_accessibility_testing(),
            await self._scenario_5_code_refactoring(),
            await self._scenario_6_complex_workflow()
        ]
        
        self.demo_results.append({
            "step": "demo_scenarios",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "scenarios_run": len(scenarios),
                "scenarios": scenarios
            }
        })
    
    async def _scenario_1_ui_testing(self):
        """Scenario 1: UI Testing with Puppeteer."""
        logger.info("🎬 Scenario 1: UI Testing with Puppeteer")
        
        task_data = {
            "test_type": "ui_testing",
            "target_url": "https://example.com",
            "config": {
                "browser": "chrome",
                "viewport": "1920x1080",
                "screenshot": True,
                "check_elements": ["button", "form", "navigation"]
            }
        }
        
        start_time = time.time()
        result = await self.testing_agent.execute_test_task(task_data)
        duration = time.time() - start_time
        
        logger.info(f"✅ UI Testing completed in {duration:.2f}s")
        
        return {
            "scenario": "ui_testing",
            "duration": duration,
            "result": result,
            "status": "completed"
        }
    
    async def _scenario_2_code_analysis(self):
        """Scenario 2: Code Analysis and Quality Assessment."""
        logger.info("🎬 Scenario 2: Code Analysis and Quality Assessment")
        
        sample_code = """
        function calculateTotal(items) {
            var total = 0;
            for (var i = 0; i < items.length; i++) {
                total += items[i].price;
            }
            console.log('Total:', total);
            return total;
        }
        
        const products = [
            { name: 'Product 1', price: 10 },
            { name: 'Product 2', price: 20 },
            { name: 'Product 3', price: 30 }
        ];
        
        calculateTotal(products);
        """
        
        task_data = {
            "task_type": "code_analysis",
            "file_path": "sample.js",
            "code_content": sample_code,
            "language": "javascript",
            "config": {
                "check_best_practices": True,
                "suggest_refactoring": True,
                "quality_metrics": True
            }
        }
        
        start_time = time.time()
        result = await self.frontend_clean_code_agent.execute_clean_code_task(task_data)
        duration = time.time() - start_time
        
        logger.info(f"✅ Code Analysis completed in {duration:.2f}s")
        
        return {
            "scenario": "code_analysis",
            "duration": duration,
            "result": result,
            "status": "completed"
        }
    
    async def _scenario_3_performance_testing(self):
        """Scenario 3: Performance Testing with Lighthouse."""
        logger.info("🎬 Scenario 3: Performance Testing with Lighthouse")
        
        task_data = {
            "test_type": "performance_testing",
            "target_url": "https://example.com",
            "config": {
                "lighthouse_categories": ["performance", "accessibility", "best-practices", "seo"],
                "device": "desktop",
                "throttling": "fast3g"
            }
        }
        
        start_time = time.time()
        result = await self.testing_agent.execute_test_task(task_data)
        duration = time.time() - start_time
        
        logger.info(f"✅ Performance Testing completed in {duration:.2f}s")
        
        return {
            "scenario": "performance_testing",
            "duration": duration,
            "result": result,
            "status": "completed"
        }
    
    async def _scenario_4_accessibility_testing(self):
        """Scenario 4: Accessibility Testing."""
        logger.info("🎬 Scenario 4: Accessibility Testing")
        
        task_data = {
            "test_type": "accessibility_testing",
            "target_url": "https://example.com",
            "config": {
                "wcag_level": "AA",
                "check_contrast": True,
                "check_keyboard_navigation": True,
                "check_screen_reader": True
            }
        }
        
        start_time = time.time()
        result = await self.testing_agent.execute_test_task(task_data)
        duration = time.time() - start_time
        
        logger.info(f"✅ Accessibility Testing completed in {duration:.2f}s")
        
        return {
            "scenario": "accessibility_testing",
            "duration": duration,
            "result": result,
            "status": "completed"
        }
    
    async def _scenario_5_code_refactoring(self):
        """Scenario 5: Code Refactoring."""
        logger.info("🎬 Scenario 5: Code Refactoring")
        
        sample_code = """
        var userData = [];
        for (var i = 0; i < users.length; i++) {
            var user = users[i];
            if (user.active) {
                userData.push({
                    name: user.name,
                    email: user.email,
                    age: user.age
                });
            }
        }
        console.log('Active users:', userData);
        """
        
        task_data = {
            "task_type": "refactoring",
            "file_path": "user_processing.js",
            "code_content": sample_code,
            "language": "javascript",
            "config": {
                "modernize_syntax": True,
                "improve_readability": True,
                "remove_console_logs": True
            }
        }
        
        start_time = time.time()
        result = await self.frontend_clean_code_agent.execute_clean_code_task(task_data)
        duration = time.time() - start_time
        
        logger.info(f"✅ Code Refactoring completed in {duration:.2f}s")
        
        return {
            "scenario": "code_refactoring",
            "duration": duration,
            "result": result,
            "status": "completed"
        }
    
    async def _scenario_6_complex_workflow(self):
        """Scenario 6: Complex Multi-Agent Workflow."""
        logger.info("🎬 Scenario 6: Complex Multi-Agent Workflow")
        
        # Submit multiple tasks to the orchestrator
        tasks = [
            {
                "type": "ui_testing",
                "priority": 3,
                "payload": {
                    "test_type": "ui_testing",
                    "target_url": "https://example.com",
                    "config": {"browser": "chrome"}
                }
            },
            {
                "type": "code_analysis",
                "priority": 2,
                "payload": {
                    "task_type": "code_analysis",
                    "file_path": "app.js",
                    "code_content": "function test() { console.log('test'); }",
                    "language": "javascript"
                }
            },
            {
                "type": "performance_testing",
                "priority": 4,
                "payload": {
                    "test_type": "performance_testing",
                    "target_url": "https://example.com",
                    "config": {"lighthouse_categories": ["performance"]}
                }
            }
        ]
        
        start_time = time.time()
        task_ids = []
        
        for task in tasks:
            task_id = await self.orchestrator.submit_task(task)
            task_ids.append(task_id)
        
        # Wait for all tasks to complete
        completed_tasks = []
        for task_id in task_ids:
            while True:
                task_status = await self.orchestrator.get_task_status(task_id)
                if task_status and task_status.get("status") in ["completed", "error"]:
                    completed_tasks.append(task_status)
                    break
                await asyncio.sleep(1)
        
        duration = time.time() - start_time
        
        logger.info(f"✅ Complex Workflow completed in {duration:.2f}s")
        
        return {
            "scenario": "complex_workflow",
            "duration": duration,
            "tasks_submitted": len(tasks),
            "tasks_completed": len(completed_tasks),
            "task_ids": task_ids,
            "status": "completed"
        }
    
    async def _analyze_performance(self):
        """Analyze system performance and metrics."""
        logger.info("📊 Analyzing system performance...")
        
        # Get system status
        system_status = await self.orchestrator.get_system_status()
        
        # Get agent statuses
        agent_statuses = []
        for agent_id in self.orchestrator.agents:
            agent_status = await self.orchestrator.get_agent_status(agent_id)
            if agent_status:
                agent_statuses.append(agent_status)
        
        # Calculate performance metrics
        total_tasks = len(self.orchestrator.active_tasks) + len(self.orchestrator.task_queue)
        completed_tasks = len([task for task in self.orchestrator.active_tasks.values() if task.status == "completed"])
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        performance_analysis = {
            "system_health": system_status.get("system_health", 0.0),
            "total_agents": system_status.get("total_agents", 0),
            "available_agents": system_status.get("available_agents", 0),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": success_rate,
            "agent_performance": agent_statuses
        }
        
        self.demo_results.append({
            "step": "performance_analysis",
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "details": performance_analysis
        })
        
        logger.info(f"✅ Performance Analysis completed - Success Rate: {success_rate:.2%}")
    
    async def _generate_demo_report(self):
        """Generate a comprehensive demo report."""
        logger.info("📋 Generating demo report...")
        
        report = {
            "demo_title": "Microservices Agent System Demo",
            "demo_version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_steps": len(self.demo_results),
                "successful_steps": len([r for r in self.demo_results if r["status"] == "completed"]),
                "total_duration": self._calculate_total_duration(),
                "system_health": await self._get_final_system_health()
            },
            "steps": self.demo_results,
            "recommendations": [
                "Consider adding more specialized agents for different domains",
                "Implement agent-to-agent communication protocols",
                "Add real-time monitoring and alerting",
                "Implement agent learning and improvement mechanisms",
                "Add support for distributed deployment"
            ]
        }
        
        # Save report to file
        with open("microservices_agent_demo_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info("✅ Demo report generated: microservices_agent_demo_report.json")
        
        return report
    
    def _calculate_total_duration(self) -> float:
        """Calculate total demo duration."""
        if len(self.demo_results) < 2:
            return 0.0
        
        start_time = datetime.fromisoformat(self.demo_results[0]["timestamp"])
        end_time = datetime.fromisoformat(self.demo_results[-1]["timestamp"])
        return (end_time - start_time).total_seconds()
    
    async def _get_final_system_health(self) -> float:
        """Get final system health score."""
        try:
            system_status = await self.orchestrator.get_system_status()
            return system_status.get("system_health", 0.0)
        except:
            return 0.0

async def main():
    """Main function to run the demo."""
    demo = MicroservicesAgentDemo()
    await demo.run_comprehensive_demo()

if __name__ == "__main__":
    asyncio.run(main()) 