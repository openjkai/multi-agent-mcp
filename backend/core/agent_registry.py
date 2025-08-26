"""
Agent Registry - Manages registration and tracking of all agents
Simple registry system for today's foundation
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
from .agent_interface import BaseAgent, MockAgent

logger = logging.getLogger(__name__)

class AgentRegistry:
    """Simple registry for managing agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agent_types: Dict[str, List[str]] = {}
        self.created_at = datetime.utcnow()
    
    async def register_agent(self, agent: BaseAgent) -> bool:
        """Register a new agent"""
        if agent.agent_id in self.agents:
            logger.warning(f"Agent {agent.agent_id} already registered")
            return False
        
        # Register agent
        self.agents[agent.agent_id] = agent
        
        # Track by type (using first capability as type for now)
        agent_type = agent.capabilities[0] if agent.capabilities else "general"
        if agent_type not in self.agent_types:
            self.agent_types[agent_type] = []
        self.agent_types[agent_type].append(agent.agent_id)
        
        logger.info(f"Registered agent: {agent.agent_id} ({agent.name})")
        return True
    
    async def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent"""
        if agent_id not in self.agents:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        agent = self.agents[agent_id]
        
        # Remove from type tracking
        for agent_type, agent_ids in self.agent_types.items():
            if agent_id in agent_ids:
                agent_ids.remove(agent_id)
                if not agent_ids:  # Remove empty type
                    del self.agent_types[agent_type]
                break
        
        # Remove agent
        del self.agents[agent_id]
        
        logger.info(f"Unregistered agent: {agent_id}")
        return True
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[BaseAgent]:
        """List all registered agents"""
        return list(self.agents.values())
    
    def list_agents_by_type(self, agent_type: str) -> List[BaseAgent]:
        """List agents by type"""
        agent_ids = self.agent_types.get(agent_type, [])
        return [self.agents[aid] for aid in agent_ids if aid in self.agents]
    
    def get_registry_status(self) -> Dict:
        """Get registry status"""
        return {
            "total_agents": len(self.agents),
            "agent_types": {t: len(ids) for t, ids in self.agent_types.items()},
            "created_at": self.created_at.isoformat(),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all agents"""
        health_status = {}
        for agent_id, agent in self.agents.items():
            try:
                health_status[agent_id] = await agent.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {agent_id}: {e}")
                health_status[agent_id] = False
        return health_status 