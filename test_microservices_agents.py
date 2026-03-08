#!/usr/bin/env python3
"""
Test Microservices Agent System
==============================

Simple test script to verify the microservices agent system components.
"""

import asyncio
import json
import logging
from datetime import datetime

# Import our microservices components from root directory
from microservices_orchestrator import MicroservicesOrchestrator
from testing_agent import TestingAgent
from frontend_clean_code_agent import FrontendCleanCodeAgent

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_orchestrator():
    """Test the microservices orchestrator."""
    logger.info("🧪 Testing Microservices Orchestrator...")
    
    orchestrator = MicroservicesOrchestrator()
    
    # Test system status
    status = await orchestrator.get_system_status()
    assert status is not None
    assert "total_agents" in status
    assert "system_health" in status
    
    logger.info("✅ Orchestrator test passed")
    return True

async def test_testing_agent():
    """Test the testing agent."""
    logger.info("🧪 Testing Testing Agent...")
    
    agent = TestingAgent()
    orchestrator = MicroservicesOrchestrator()
    
    # Register agent
    agent_id = await agent.register_with_orchestrator(orchestrator)
    assert agent_id is not None
    
    # Test agent execution
    task_data = {
        "test_type": "ui_testing",
        "target_url": "https://example.com",
        "config": {"browser": "chrome"}
    }
    
    result = await agent.execute_test_task(task_data)
    assert result is not None
    assert "agent_id" in result
    assert "result" in result
    
    logger.info("✅ Testing Agent test passed")
    return True

async def test_frontend_clean_code_agent():
    """Test the frontend clean code agent."""
    logger.info("🧪 Testing Frontend Clean Code Agent...")
    
    agent = FrontendCleanCodeAgent()
    orchestrator = MicroservicesOrchestrator()
    
    # Register agent
    agent_id = await agent.register_with_orchestrator(orchestrator)
    assert agent_id is not None
    
    # Test agent execution
    task_data = {
        "task_type": "code_analysis",
        "file_path": "test.js",
        "code_content": "function test() { console.log('test'); }",
        "language": "javascript"
    }
    
    result = await agent.execute_clean_code_task(task_data)
    assert result is not None
    assert "agent_id" in result
    assert "result" in result
    
    logger.info("✅ Frontend Clean Code Agent test passed")
    return True

async def test_task_submission():
    """Test task submission and execution."""
    logger.info("🧪 Testing Task Submission...")
    
    orchestrator = MicroservicesOrchestrator()
    
    # Register agents first
    testing_agent = TestingAgent()
    clean_code_agent = FrontendCleanCodeAgent()
    
    await testing_agent.register_with_orchestrator(orchestrator)
    await clean_code_agent.register_with_orchestrator(orchestrator)
    
    # Submit a task
    task_data = {
        "type": "ui_testing",
        "priority": 2,
        "payload": {
            "test_type": "ui_testing",
            "target_url": "https://example.com",
            "config": {"browser": "chrome"}
        }
    }
    
    task_id = await orchestrator.submit_task(task_data)
    assert task_id is not None
    
    # Wait a bit for task processing
    await asyncio.sleep(2)
    
    # Check task status
    task_status = await orchestrator.get_task_status(task_id)
    assert task_status is not None
    assert "status" in task_status
    
    logger.info("✅ Task Submission test passed")
    return True

async def test_mcp_server_registration():
    """Test MCP server registration."""
    logger.info("🧪 Testing MCP Server Registration...")
    
    orchestrator = MicroservicesOrchestrator()
    
    # Register MCP server
    server_data = {
        "name": "Test MCP Server",
        "tool_categories": ["testing", "analysis"],
        "available_tools": {
            "test_tool": {
                "name": "Test Tool",
                "description": "A test tool",
                "status": "available"
            }
        }
    }
    
    server_id = await orchestrator.register_mcp_server(server_data)
    assert server_id is not None
    
    # Check if server is registered
    assert server_id in orchestrator.mcp_servers
    
    logger.info("✅ MCP Server Registration test passed")
    return True

async def run_all_tests():
    """Run all tests."""
    logger.info("🚀 Starting Microservices Agent System Tests...")
    
    tests = [
        test_orchestrator,
        test_testing_agent,
        test_frontend_clean_code_agent,
        test_task_submission,
        test_mcp_server_registration
    ]
    
    results = []
    
    for test in tests:
        try:
            result = await test()
            results.append({"test": test.__name__, "status": "passed", "result": result})
            logger.info(f"✅ {test.__name__} passed")
        except Exception as e:
            results.append({"test": test.__name__, "status": "failed", "error": str(e)})
            logger.error(f"❌ {test.__name__} failed: {e}")
    
    # Generate test report
    passed_tests = len([r for r in results if r["status"] == "passed"])
    total_tests = len(results)
    
    test_report = {
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
        "results": results
    }
    
    # Save test report
    with open("microservices_agent_test_report.json", "w") as f:
        json.dump(test_report, f, indent=2, default=str)
    
    logger.info(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
    logger.info(f"📊 Success Rate: {test_report['success_rate']:.2%}")
    
    if passed_tests == total_tests:
        logger.info("🎉 All tests passed! Microservices Agent System is working correctly.")
    else:
        logger.warning("⚠️  Some tests failed. Please check the test report for details.")
    
    return test_report

async def main():
    """Main function."""
    await run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 