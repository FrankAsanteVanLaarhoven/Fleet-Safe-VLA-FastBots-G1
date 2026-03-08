#!/usr/bin/env python3
"""
Microservices Agent Orchestrator
================================

Main orchestrator for the comprehensive microservices agent system.
Manages agent registration, task routing, and MCP server integration.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class AgentCapability:
    name: str
    description: str
    performance_score: float
    success_rate: float
    avg_response_time: float

@dataclass
class Agent:
    id: str
    name: str
    type: str
    status: AgentStatus
    capabilities: List[AgentCapability]
    current_load: int
    max_concurrent_tasks: int
    performance_metrics: Dict[str, Any]
    last_heartbeat: datetime

@dataclass
class Task:
    id: str
    type: str
    priority: TaskPriority
    payload: Dict[str, Any]
    assigned_agent: Optional[str]
    status: str
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[Dict[str, Any]]

class MicroservicesOrchestrator:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.mcp_servers: Dict[str, Dict[str, Any]] = {}
        self.task_queue: List[Task] = []
        self.active_tasks: Dict[str, Task] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}
        
    async def register_agent(self, agent_data: Dict[str, Any]) -> str:
        """Register a new agent with the orchestrator."""
        agent_id = str(uuid.uuid4())
        
        capabilities = [
            AgentCapability(**cap) for cap in agent_data.get('capabilities', [])
        ]
        
        agent = Agent(
            id=agent_id,
            name=agent_data['name'],
            type=agent_data['type'],
            status=AgentStatus.AVAILABLE,
            capabilities=capabilities,
            current_load=0,
            max_concurrent_tasks=agent_data.get('max_concurrent_tasks', 5),
            performance_metrics=agent_data.get('performance_metrics', {}),
            last_heartbeat=datetime.now()
        )
        
        self.agents[agent_id] = agent
        logger.info(f"Registered agent: {agent.name} ({agent_id})")
        return agent_id
    
    async def register_mcp_server(self, server_data: Dict[str, Any]) -> str:
        """Register a new MCP server."""
        server_id = str(uuid.uuid4())
        server_data['id'] = server_id
        server_data['registered_at'] = datetime.now()
        server_data['status'] = 'active'
        
        self.mcp_servers[server_id] = server_data
        logger.info(f"Registered MCP server: {server_data['name']} ({server_id})")
        return server_id
    
    async def submit_task(self, task_data: Dict[str, Any]) -> str:
        """Submit a new task to the orchestrator."""
        task_id = str(uuid.uuid4())
        
        task = Task(
            id=task_id,
            type=task_data['type'],
            priority=TaskPriority(task_data.get('priority', 2)),
            payload=task_data['payload'],
            assigned_agent=None,
            status='pending',
            created_at=datetime.now(),
            started_at=None,
            completed_at=None,
            result=None
        )
        
        self.task_queue.append(task)
        logger.info(f"Submitted task: {task.type} ({task_id})")
        
        # Trigger task processing
        asyncio.create_task(self._process_task_queue())
        return task_id
    
    async def _process_task_queue(self):
        """Process the task queue and assign tasks to available agents."""
        while self.task_queue:
            # Sort tasks by priority
            self.task_queue.sort(key=lambda t: t.priority.value, reverse=True)
            
            task = self.task_queue[0]
            
            # Find best available agent
            best_agent = await self._find_best_agent(task)
            
            if best_agent:
                await self._assign_task_to_agent(task, best_agent)
                self.task_queue.pop(0)
            else:
                # No available agents, wait a bit
                await asyncio.sleep(1)
    
    async def _find_best_agent(self, task: Task) -> Optional[Agent]:
        """Find the best available agent for a given task."""
        available_agents = [
            agent for agent in self.agents.values()
            if agent.status == AgentStatus.AVAILABLE and 
               agent.current_load < agent.max_concurrent_tasks
        ]
        
        if not available_agents:
            return None
        
        # Score agents based on capabilities and performance
        scored_agents = []
        for agent in available_agents:
            score = await self._calculate_agent_score(agent, task)
            scored_agents.append((agent, score))
        
        # Return the agent with the highest score
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        return scored_agents[0][0] if scored_agents else None
    
    async def _calculate_agent_score(self, agent: Agent, task: Task) -> float:
        """Calculate a score for how well an agent can handle a task."""
        base_score = 0.0
        
        # Check capability match
        for capability in agent.capabilities:
            if capability.name.lower() in task.type.lower():
                base_score += capability.performance_score
        
        # Consider current load
        load_factor = 1.0 - (agent.current_load / agent.max_concurrent_tasks)
        base_score *= load_factor
        
        # Consider success rate
        success_rate = agent.performance_metrics.get('success_rate', 0.8)
        base_score *= success_rate
        
        return base_score
    
    async def _assign_task_to_agent(self, task: Task, agent: Agent):
        """Assign a task to an agent."""
        task.assigned_agent = agent.id
        task.status = 'assigned'
        task.started_at = datetime.now()
        
        agent.current_load += 1
        if agent.current_load >= agent.max_concurrent_tasks:
            agent.status = AgentStatus.BUSY
        
        self.active_tasks[task.id] = task
        
        logger.info(f"Assigned task {task.id} to agent {agent.name}")
        
        # Simulate task execution
        asyncio.create_task(self._execute_task(task, agent))
    
    async def _execute_task(self, task: Task, agent: Agent):
        """Execute a task with the assigned agent."""
        try:
            # Simulate task execution time
            execution_time = agent.performance_metrics.get('avg_response_time', 5000) / 1000
            await asyncio.sleep(execution_time)
            
            # Generate result
            result = await self._generate_task_result(task, agent)
            
            task.result = result
            task.status = 'completed'
            task.completed_at = datetime.now()
            
            # Update agent metrics
            agent.current_load -= 1
            if agent.current_load < agent.max_concurrent_tasks:
                agent.status = AgentStatus.AVAILABLE
            
            # Update performance history
            await self._update_performance_metrics(task, agent)
            
            logger.info(f"Completed task {task.id} with agent {agent.name}")
            
        except Exception as e:
            logger.error(f"Error executing task {task.id}: {e}")
            task.status = 'error'
            task.result = {'error': str(e)}
            
            # Update agent metrics
            agent.current_load -= 1
            if agent.current_load < agent.max_concurrent_tasks:
                agent.status = AgentStatus.AVAILABLE
    
    async def _generate_task_result(self, task: Task, agent: Agent) -> Dict[str, Any]:
        """Generate a result for a completed task."""
        return {
            'task_id': task.id,
            'agent_id': agent.id,
            'agent_name': agent.name,
            'result_type': task.type,
            'timestamp': datetime.now().isoformat(),
            'data': {
                'message': f"Task {task.type} completed successfully by {agent.name}",
                'payload': task.payload,
                'performance_metrics': agent.performance_metrics
            }
        }
    
    async def _update_performance_metrics(self, task: Task, agent: Agent):
        """Update performance metrics for the agent."""
        if agent.id not in self.performance_history:
            self.performance_history[agent.id] = []
        
        metrics = {
            'task_id': task.id,
            'task_type': task.type,
            'execution_time': (task.completed_at - task.started_at).total_seconds(),
            'timestamp': datetime.now().isoformat(),
            'success': task.status == 'completed'
        }
        
        self.performance_history[agent.id].append(metrics)
        
        # Keep only last 100 metrics
        if len(self.performance_history[agent.id]) > 100:
            self.performance_history[agent.id] = self.performance_history[agent.id][-100:]
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get the current status of the orchestrator."""
        return {
            'total_agents': len(self.agents),
            'available_agents': len([a for a in self.agents.values() if a.status == AgentStatus.AVAILABLE]),
            'busy_agents': len([a for a in self.agents.values() if a.status == AgentStatus.BUSY]),
            'total_mcp_servers': len(self.mcp_servers),
            'active_tasks': len(self.active_tasks),
            'queued_tasks': len(self.task_queue),
            'system_health': await self._calculate_system_health(),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _calculate_system_health(self) -> float:
        """Calculate overall system health score."""
        if not self.agents:
            return 0.0
        
        total_health = 0.0
        for agent in self.agents.values():
            # Calculate agent health based on performance metrics
            success_rate = agent.performance_metrics.get('success_rate', 0.8)
            uptime = 1.0 if agent.status != AgentStatus.OFFLINE else 0.0
            load_factor = 1.0 - (agent.current_load / agent.max_concurrent_tasks)
            
            agent_health = (success_rate + uptime + load_factor) / 3
            total_health += agent_health
        
        return total_health / len(self.agents)
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific agent."""
        if agent_id not in self.agents:
            return None
        
        agent = self.agents[agent_id]
        return {
            'id': agent.id,
            'name': agent.name,
            'type': agent.type,
            'status': agent.status.value,
            'current_load': agent.current_load,
            'max_concurrent_tasks': agent.max_concurrent_tasks,
            'performance_metrics': agent.performance_metrics,
            'last_heartbeat': agent.last_heartbeat.isoformat(),
            'capabilities': [asdict(cap) for cap in agent.capabilities]
        }
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        # Check active tasks
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            return {
                'id': task.id,
                'type': task.type,
                'status': task.status,
                'assigned_agent': task.assigned_agent,
                'created_at': task.created_at.isoformat(),
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'result': task.result
            }
        
        # Check queued tasks
        for task in self.task_queue:
            if task.id == task_id:
                return {
                    'id': task.id,
                    'type': task.type,
                    'status': task.status,
                    'assigned_agent': task.assigned_agent,
                    'created_at': task.created_at.isoformat(),
                    'started_at': None,
                    'completed_at': None,
                    'result': None
                }
        
        return None

# Global orchestrator instance
orchestrator = MicroservicesOrchestrator() 