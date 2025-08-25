"""
Agent Interface - Basic interface for MCP agents
Defines the contract that all agents must implement
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """Base class for all MCP agents"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.is_active = False
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
    
    @abstractmethod
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process a query and return response"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if agent is healthy"""
        pass
    
    async def activate(self):
        """Activate the agent"""
        self.is_active = True
        self.last_activity = datetime.utcnow()
        logger.info(f"Agent {self.agent_id} activated")
    
    async def deactivate(self):
        """Deactivate the agent"""
        self.is_active = False
        logger.info(f"Agent {self.agent_id} deactivated")
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "capabilities": self.capabilities,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }

class MockAgent(BaseAgent):
    """Mock agent for testing purposes"""
    
    def __init__(self, agent_id: str, name: str, capabilities: List[str]):
        super().__init__(agent_id, name, capabilities)
    
    async def process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process query with mock response"""
        self.last_activity = datetime.utcnow()
        
        response = {
            "response": f"Mock response from {self.name}: {query}",
            "confidence": 0.85,
            "agent_id": self.agent_id,
            "capabilities_used": self.capabilities[:1],  # Use first capability
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Mock agent {self.agent_id} processed query: {query}")
        return response
    
    async def health_check(self) -> bool:
        """Always healthy for mock agent"""
        return self.is_active 