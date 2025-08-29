"""
Agent Manager - Orchestrates all agents and handles query routing
Advanced agent management system for today's major update
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from .agent_registry import AgentRegistry
from .agent_interface import BaseAgent, MockAgent
from .mcp_client import MCPClient

logger = logging.getLogger(__name__)

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    average_response_time: float = 0.0
    last_query_time: Optional[datetime] = None
    uptime: timedelta = timedelta(0)

class AgentManager:
    """Advanced agent manager with orchestration capabilities"""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.query_history: List[Dict] = []
        self.start_time = datetime.utcnow()
        self._health_monitor_task: Optional[asyncio.Task] = None
        
    async def initialize(self):
        """Initialize the agent manager"""
        logger.info("Initializing Agent Manager")
        
        # Start health monitoring
        self._health_monitor_task = asyncio.create_task(self._health_monitor_loop())
        
        # Register default agents
        await self._register_default_agents()
        
        logger.info("Agent Manager initialized successfully")
    
    async def _register_default_agents(self):
        """Register default agents for testing"""
        default_agents = [
            {
                "id": "docs-agent-001",
                "name": "Document Analysis Agent",
                "capabilities": ["document_processing", "qa", "summarization"],
                "mcp_endpoint": "http://localhost:8001"
            },
            {
                "id": "code-agent-001",
                "name": "Code Assistant Agent",
                "capabilities": ["code_analysis", "refactoring", "generation"],
                "mcp_endpoint": "http://localhost:8002"
            },
            {
                "id": "web-agent-001",
                "name": "Web Search Agent",
                "capabilities": ["web_search", "news_fetching", "fact_checking"],
                "mcp_endpoint": "http://localhost:8003"
            },
            {
                "id": "chat-agent-001",
                "name": "General Chat Agent",
                "capabilities": ["conversation", "coordination", "routing"],
                "mcp_endpoint": "http://localhost:8004"
            }
        ]
        
        for agent_config in default_agents:
            try:
                # Create mock agent for now
                agent = MockAgent(
                    agent_id=agent_config["id"],
                    name=agent_config["name"],
                    capabilities=agent_config["capabilities"]
                )
                
                # Register agent
                await self.registry.register_agent(agent)
                
                # Create MCP client
                mcp_client = MCPClient()
                await mcp_client.connect(agent_config["mcp_endpoint"], agent_config["id"])
                self.mcp_clients[agent_config["id"]] = mcp_client
                
                # Initialize metrics
                self.agent_metrics[agent_config["id"]] = AgentMetrics()
                
                # Activate agent
                await agent.activate()
                
                logger.info(f"Registered and activated agent: {agent_config['id']}")
                
            except Exception as e:
                logger.error(f"Failed to register default agent {agent_config['id']}: {e}")
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route query to the most appropriate agent(s)"""
        start_time = datetime.utcnow()
        
        # Simple routing logic based on query content
        query_lower = query.lower()
        selected_agent_id = None
        
        # Route based on keywords
        if any(word in query_lower for word in ["pdf", "document", "file", "read", "analyze", "summarize"]):
            selected_agent_id = "docs-agent-001"
        elif any(word in query_lower for word in ["code", "program", "function", "class", "bug", "refactor"]):
            selected_agent_id = "code-agent-001"
        elif any(word in query_lower for word in ["search", "web", "news", "current", "latest", "fact"]):
            selected_agent_id = "web-agent-001"
        else:
            selected_agent_id = "chat-agent-001"
        
        # Get agent and process query
        agent = self.registry.get_agent(selected_agent_id)
        if not agent:
            raise RuntimeError(f"Agent {selected_agent_id} not found")
        
        try:
            # Process query
            response = await agent.process_query(query, context or {})
            
            # Update metrics
            await self._update_metrics(selected_agent_id, start_time, True)
            
            # Add to query history
            self.query_history.append({
                "query": query,
                "agent_id": selected_agent_id,
                "response": response,
                "timestamp": start_time.isoformat(),
                "response_time": (datetime.utcnow() - start_time).total_seconds()
            })
            
            return {
                "response": response,
                "agent_id": selected_agent_id,
                "agent_name": agent.name,
                "routing_logic": "keyword_based",
                "response_time": (datetime.utcnow() - start_time).total_seconds()
            }
            
        except Exception as e:
            # Update metrics
            await self._update_metrics(selected_agent_id, start_time, False)
            logger.error(f"Error processing query with agent {selected_agent_id}: {e}")
            raise
    
    async def _update_metrics(self, agent_id: str, start_time: datetime, success: bool):
        """Update agent metrics"""
        if agent_id not in self.agent_metrics:
            return
        
        metrics = self.agent_metrics[agent_id]
        response_time = (datetime.utcnow() - start_time).total_seconds()
        
        metrics.total_queries += 1
        if success:
            metrics.successful_queries += 1
        else:
            metrics.failed_queries += 1
        
        # Update average response time
        if metrics.total_queries == 1:
            metrics.average_response_time = response_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_queries - 1) + response_time) 
                / metrics.total_queries
            )
        
        metrics.last_query_time = datetime.utcnow()
        metrics.uptime = datetime.utcnow() - self.start_time
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        registry_status = self.registry.get_registry_status()
        health_status = await self.registry.health_check_all()
        
        # Calculate overall metrics
        total_queries = sum(m.total_queries for m in self.agent_metrics.values())
        total_successful = sum(m.successful_queries for m in self.agent_metrics.values())
        overall_success_rate = total_successful / total_queries if total_queries > 0 else 0
        
        return {
            "system_status": "running",
            "uptime": (datetime.utcnow() - self.start_time).total_seconds(),
            "registry": registry_status,
            "health": health_status,
            "metrics": {
                "total_queries": total_queries,
                "success_rate": overall_success_rate,
                "agent_count": len(self.agent_metrics)
            },
            "recent_queries": self.query_history[-5:] if self.query_history else []
        }
    
    async def _health_monitor_loop(self):
        """Background health monitoring"""
        while True:
            try:
                # Check all agents health
                health_status = await self.registry.health_check_all()
                
                # Log any unhealthy agents
                for agent_id, is_healthy in health_status.items():
                    if not is_healthy:
                        logger.warning(f"Agent {agent_id} is unhealthy")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                await asyncio.sleep(60)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Cleanup MCP clients
        for client in self.mcp_clients.values():
            await client.cleanup()
        
        logger.info("Agent Manager cleanup completed") 