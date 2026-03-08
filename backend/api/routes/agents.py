#!/usr/bin/env python3
"""
Agent API Routes
===============

FastAPI routes for the microservices agent system.
Handles agent registration, task submission, and status monitoring.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import asyncio

from core.security import verify_token
from microservices_orchestrator import orchestrator
from agents.testing_agent import TestingAgent
from agents.frontend_clean_code_agent import FrontendCleanCodeAgent

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agents
testing_agent = TestingAgent()
frontend_clean_code_agent = FrontendCleanCodeAgent()

# Dependency for authentication
async def get_current_user(token: str = Depends(verify_token)):
    return token

@router.on_event("startup")
async def startup_event():
    """Initialize agents on startup."""
    try:
        # Register agents with orchestrator
        await testing_agent.register_with_orchestrator(orchestrator)
        await frontend_clean_code_agent.register_with_orchestrator(orchestrator)
        logger.info("All agents registered successfully")
    except Exception as e:
        logger.error(f"Error registering agents: {e}")

@router.get("/status")
async def get_system_status():
    """Get overall system status."""
    try:
        status = await orchestrator.get_system_status()
        return JSONResponse(content=status)
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents")
async def get_all_agents():
    """Get all registered agents."""
    try:
        agents = []
        for agent_id in orchestrator.agents:
            agent_status = await orchestrator.get_agent_status(agent_id)
            if agent_status:
                agents.append(agent_status)
        
        return JSONResponse(content={
            "agents": agents,
            "total_count": len(agents),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting agents: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/agents/{agent_id}")
async def get_agent_status(agent_id: str):
    """Get status of a specific agent."""
    try:
        agent_status = await orchestrator.get_agent_status(agent_id)
        if not agent_status:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return JSONResponse(content=agent_status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/tasks")
async def submit_task(
    task_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Submit a new task to the orchestrator."""
    try:
        # Validate task data
        required_fields = ["type", "payload"]
        for field in required_fields:
            if field not in task_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Add user context to task
        task_data["user_id"] = current_user.get("user_id")
        task_data["submitted_at"] = datetime.now().isoformat()
        
        # Submit task
        task_id = await orchestrator.submit_task(task_data)
        
        return JSONResponse(content={
            "task_id": task_id,
            "status": "submitted",
            "message": "Task submitted successfully",
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    """Get status of a specific task."""
    try:
        task_status = await orchestrator.get_task_status(task_id)
        if not task_status:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return JSONResponse(content=task_status)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/tasks")
async def get_all_tasks(
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """Get all tasks with optional filtering."""
    try:
        tasks = []
        
        # Get active tasks
        for task_id, task in orchestrator.active_tasks.items():
            if status and task.status != status:
                continue
            tasks.append({
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "assigned_agent": task.assigned_agent,
                "created_at": task.created_at.isoformat(),
                "priority": task.priority.value
            })
        
        # Get queued tasks
        for task in orchestrator.task_queue:
            if status and task.status != status:
                continue
            tasks.append({
                "id": task.id,
                "type": task.type,
                "status": task.status,
                "assigned_agent": task.assigned_agent,
                "created_at": task.created_at.isoformat(),
                "priority": task.priority.value
            })
        
        # Sort by creation time (newest first)
        tasks.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        total_count = len(tasks)
        tasks = tasks[offset:offset + limit]
        
        return JSONResponse(content={
            "tasks": tasks,
            "total_count": total_count,
            "limit": limit,
            "offset": offset,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/register")
async def register_agent(agent_data: Dict[str, Any]):
    """Register a new agent with the orchestrator."""
    try:
        # Validate agent data
        required_fields = ["name", "type", "capabilities"]
        for field in required_fields:
            if field not in agent_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Register agent
        agent_id = await orchestrator.register_agent(agent_data)
        
        return JSONResponse(content={
            "agent_id": agent_id,
            "status": "registered",
            "message": "Agent registered successfully",
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/mcp-servers/register")
async def register_mcp_server(server_data: Dict[str, Any]):
    """Register a new MCP server."""
    try:
        # Validate server data
        required_fields = ["name", "tool_categories", "available_tools"]
        for field in required_fields:
            if field not in server_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        # Register MCP server
        server_id = await orchestrator.register_mcp_server(server_data)
        
        return JSONResponse(content={
            "server_id": server_id,
            "status": "registered",
            "message": "MCP server registered successfully",
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering MCP server: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/mcp-servers")
async def get_mcp_servers():
    """Get all registered MCP servers."""
    try:
        servers = []
        for server_id, server_data in orchestrator.mcp_servers.items():
            servers.append({
                "id": server_id,
                "name": server_data.get("name"),
                "tool_categories": server_data.get("tool_categories", []),
                "status": server_data.get("status"),
                "registered_at": server_data.get("registered_at").isoformat() if server_data.get("registered_at") else None
            })
        
        return JSONResponse(content={
            "servers": servers,
            "total_count": len(servers),
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting MCP servers: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/testing/execute")
async def execute_testing_task(
    task_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Execute a testing task directly with the testing agent."""
    try:
        # Validate task data
        if "test_type" not in task_data or "target_url" not in task_data:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: test_type, target_url"
            )
        
        # Execute task
        result = await testing_agent.execute_test_task(task_data)
        
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing testing task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/clean-code/execute")
async def execute_clean_code_task(
    task_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Execute a clean code task directly with the frontend clean code agent."""
    try:
        # Validate task data
        if "task_type" not in task_data or "file_path" not in task_data:
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: task_type, file_path"
            )
        
        # Execute task
        result = await frontend_clean_code_agent.execute_clean_code_task(task_data)
        
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing clean code task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/performance/metrics")
async def get_performance_metrics():
    """Get performance metrics for all agents."""
    try:
        metrics = {}
        
        # Get testing agent metrics
        testing_status = await testing_agent.get_agent_status()
        metrics["testing_agent"] = testing_status.get("performance_metrics", {})
        
        # Get frontend clean code agent metrics
        clean_code_status = await frontend_clean_code_agent.get_agent_status()
        metrics["frontend_clean_code_agent"] = clean_code_status.get("performance_metrics", {})
        
        # Get orchestrator metrics
        system_status = await orchestrator.get_system_status()
        metrics["orchestrator"] = {
            "total_agents": system_status.get("total_agents", 0),
            "available_agents": system_status.get("available_agents", 0),
            "active_tasks": system_status.get("active_tasks", 0),
            "system_health": system_status.get("system_health", 0.0)
        }
        
        return JSONResponse(content={
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/agents/{agent_id}/heartbeat")
async def agent_heartbeat(agent_id: str, heartbeat_data: Dict[str, Any]):
    """Update agent heartbeat and status."""
    try:
        if agent_id not in orchestrator.agents:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        agent = orchestrator.agents[agent_id]
        agent.last_heartbeat = datetime.now()
        
        # Update agent status if provided
        if "status" in heartbeat_data:
            try:
                agent.status = AgentStatus(heartbeat_data["status"])
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status value")
        
        # Update current load if provided
        if "current_load" in heartbeat_data:
            agent.current_load = heartbeat_data["current_load"]
        
        return JSONResponse(content={
            "agent_id": agent_id,
            "status": "updated",
            "message": "Agent heartbeat updated successfully",
            "timestamp": datetime.now().isoformat()
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent heartbeat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """Cancel a pending task."""
    try:
        # Check if task is in queue
        for i, task in enumerate(orchestrator.task_queue):
            if task.id == task_id:
                if task.status == "pending":
                    orchestrator.task_queue.pop(i)
                    return JSONResponse(content={
                        "task_id": task_id,
                        "status": "cancelled",
                        "message": "Task cancelled successfully",
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    raise HTTPException(
                        status_code=400,
                        detail="Cannot cancel task that is not pending"
                    )
        
        # Check if task is active
        if task_id in orchestrator.active_tasks:
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel task that is already being executed"
            )
        
        raise HTTPException(status_code=404, detail="Task not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling task: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 