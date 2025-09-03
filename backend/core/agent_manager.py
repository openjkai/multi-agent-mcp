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
from .specialized_agents import DocumentAgent, WebAgent, ChatAgent, CodeAgent
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
            DocumentAgent(
                agent_id="docs-agent-001",
                name="Document Analysis Agent",
                capabilities=["document_processing", "pdf_analysis", "text_extraction", "qa"]
            ),
            CodeAgent(
                agent_id="code-agent-001", 
                name="Code Assistant Agent",
                capabilities=["code_analysis", "refactoring", "code_generation", "debugging"]
            ),
            WebAgent(
                agent_id="web-agent-001",
                name="Web Search Agent", 
                capabilities=["web_search", "news_fetching", "fact_checking", "real_time_data"]
            ),
            ChatAgent(
                agent_id="chat-agent-001",
                name="General Chat Agent",
                capabilities=["conversation", "task_coordination", "agent_orchestration", "general_qa"]
            )
        ]
        
        for agent in default_agents:
            await self.registry.register_agent(agent)
            await agent.activate()
            self.agent_metrics[agent.agent_id] = AgentMetrics()
            logger.info(f"Registered and activated agent: {agent.name}")
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Route query to the most appropriate agent"""
        start_time = datetime.utcnow()
        
        try:
            # Analyze query to determine best agent
            agent_id = self._analyze_query_for_routing(query)
            agent = self.registry.get_agent(agent_id)
            
            if not agent:
                raise ValueError(f"Agent {agent_id} not found")
            
            if not agent.is_active:
                await agent.activate()
            
            # Process query
            result = await agent.process_query(query, context)
            
            # Update metrics
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            self._update_agent_metrics(agent_id, True, processing_time)
            
            # Log query
            self.query_history.append({
                "query": query,
                "agent_id": agent_id,
                "agent_name": agent.name,
                "timestamp": start_time.isoformat(),
                "processing_time": processing_time,
                "success": True
            })
            
            return {
                "agent_id": agent_id,
                "agent_name": agent.name,
                "response": result,
                "processing_time": processing_time,
                "timestamp": start_time.isoformat()
            }
            
        except Exception as e:
            processing_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Try fallback to chat agent
            try:
                chat_agent = self.registry.get_agent("chat-agent-001")
                if chat_agent and chat_agent.is_active:
                    result = await chat_agent.process_query(query, context)
                    self._update_agent_metrics("chat-agent-001", True, processing_time)
                    
                    return {
                        "agent_id": "chat-agent-001",
                        "agent_name": chat_agent.name,
                        "response": result,
                        "processing_time": processing_time,
                        "timestamp": start_time.isoformat(),
                        "fallback": True
                    }
            except:
                pass
            
            # Log failed query
            self.query_history.append({
                "query": query,
                "agent_id": None,
                "timestamp": start_time.isoformat(),
                "processing_time": processing_time,
                "success": False,
                "error": str(e)
            })
            
            logger.error(f"Query routing failed: {str(e)}")
            raise
    
    def _analyze_query_for_routing(self, query: str) -> str:
        """Analyze query to determine the best agent"""
        query_lower = query.lower()
        
        # Document-related keywords
        doc_keywords = ["pdf", "document", "analyze", "extract", "summarize", "text", "file", "upload"]
        if any(keyword in query_lower for keyword in doc_keywords):
            return "docs-agent-001"
        
        # Code-related keywords  
        code_keywords = ["code", "function", "class", "debug", "refactor", "programming", "python", "javascript"]
        if any(keyword in query_lower for keyword in code_keywords):
            return "code-agent-001"
        
        # Web search keywords
        web_keywords = ["search", "web", "news", "latest", "current", "find", "lookup", "internet"]
        if any(keyword in query_lower for keyword in web_keywords):
            return "web-agent-001"
        
        # Default to chat agent
        return "chat-agent-001"
    
    def _update_agent_metrics(self, agent_id: str, success: bool, processing_time: float):
        """Update agent performance metrics"""
        if agent_id not in self.agent_metrics:
            self.agent_metrics[agent_id] = AgentMetrics()
        
        metrics = self.agent_metrics[agent_id]
        metrics.total_queries += 1
        metrics.last_query_time = datetime.utcnow()
        
        if success:
            metrics.successful_queries += 1
        else:
            metrics.failed_queries += 1
        
        # Update average response time
        if metrics.total_queries == 1:
            metrics.average_response_time = processing_time
        else:
            metrics.average_response_time = (
                (metrics.average_response_time * (metrics.total_queries - 1) + processing_time) 
                / metrics.total_queries
            )
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        agents = self.registry.list_agents()
        active_agents = [agent for agent in agents if agent.is_active]
        
        # Calculate uptime for each agent
        current_time = datetime.utcnow()
        for agent in agents:
            if agent.agent_id in self.agent_metrics:
                self.agent_metrics[agent.agent_id].uptime = current_time - agent.created_at
        
        return {
            "total_agents": len(agents),
            "active_agents": len(active_agents),
            "registered_agents": [
                {
                    "agent_id": agent.agent_id,
                    "name": agent.name,
                    "capabilities": agent.capabilities,
                    "is_active": agent.is_active,
                    "metrics": self.agent_metrics.get(agent.agent_id, AgentMetrics()).__dict__
                }
                for agent in agents
            ],
            "total_queries_processed": sum(m.total_queries for m in self.agent_metrics.values()),
            "successful_queries": sum(m.successful_queries for m in self.agent_metrics.values()),
            "failed_queries": sum(m.failed_queries for m in self.agent_metrics.values()),
            "system_uptime": str(current_time - self.start_time),
            "last_updated": current_time.isoformat()
        }
    
    async def _health_monitor_loop(self):
        """Background task to monitor agent health"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                agents = self.registry.list_agents()
                for agent in agents:
                    if agent.is_active:
                        try:
                            healthy = await agent.health_check()
                            if not healthy:
                                logger.warning(f"Agent {agent.agent_id} failed health check")
                                # Could implement auto-restart logic here
                        except Exception as e:
                            logger.error(f"Health check failed for agent {agent.agent_id}: {str(e)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitor error: {str(e)}")
    
    async def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up Agent Manager")
        
        # Cancel health monitoring
        if self._health_monitor_task:
            self._health_monitor_task.cancel()
            try:
                await self._health_monitor_task
            except asyncio.CancelledError:
                pass
        
        # Deactivate all agents
        agents = self.registry.list_agents()
        for agent in agents:
            if agent.is_active:
                await agent.deactivate()
        
        # Cleanup MCP clients
        for client in self.mcp_clients.values():
            await client.cleanup()
        
        logger.info("Agent Manager cleanup completed") 