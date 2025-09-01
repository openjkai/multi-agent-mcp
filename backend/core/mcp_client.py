"""
MCP Client - Handles communication with MCP agents
Implements the Model Context Protocol for agent communication
"""

import logging
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import aiohttp
except ImportError:  # Graceful handling if not installed yet
    aiohttp = None

logger = logging.getLogger(__name__)

class MCPClient:
    """Client for communicating with MCP agents"""
    
    def __init__(self):
        self.endpoint: Optional[str] = None
        self.is_connected = False
        self.agent_id: Optional[str] = None
        self.session: Optional["aiohttp.ClientSession"] = None
        self.request_timeout_seconds: int = 10
        self.retry_count: int = 2
        
    async def connect(self, endpoint: str, agent_id: str = None) -> bool:
        """Connect to an MCP agent endpoint (HTTP). Falls back to mock if unavailable."""
        self.endpoint = endpoint.rstrip("/") if endpoint else None
        self.agent_id = agent_id
        
        # If aiohttp is unavailable, remain in mock mode
        if aiohttp is None or not self.endpoint:
            self.is_connected = False
            logger.warning("aiohttp not available or endpoint missing; MCP client in mock mode")
            return False
        
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
        # Probe health
        try:
            async with self.session.get(f"{self.endpoint}/health", timeout=self.request_timeout_seconds) as resp:
                self.is_connected = resp.status == 200
        except Exception as e:
            logger.info(f"MCP endpoint not reachable, using mock mode: {e}")
            self.is_connected = False
        
        logger.info(f"Connected to MCP agent at: {self.endpoint} (connected={self.is_connected})")
        return self.is_connected
    
    async def send_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a query to the MCP agent via HTTP; fallback to mock when disconnected."""
        payload = {
            "method": "query",
            "params": {
                "query": query,
                "context": context or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        if not self.is_connected or aiohttp is None or self.session is None or not self.endpoint:
            # Mock response
            logger.info("MCP client using mock response path")
            return {
                "response": f"Mock response from {self.agent_id or 'agent'}: {query}",
                "confidence": 0.8,
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": self.agent_id
            }
        
        last_error: Optional[Exception] = None
        for attempt in range(1, self.retry_count + 1):
            try:
                async with self.session.post(
                    f"{self.endpoint}/mcp",
                    json=payload,
                    timeout=self.request_timeout_seconds,
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data if isinstance(data, dict) else {"response": str(data)}
                    else:
                        text = await resp.text()
                        raise RuntimeError(f"MCP HTTP {resp.status}: {text}")
            except Exception as e:
                last_error = e
                logger.warning(f"MCP query attempt {attempt} failed: {e}")
                # Backoff
                await asyncio.sleep(0.3 * attempt)
        
        # Fallback to mock on persistent failure
        logger.error(f"MCP query failed after retries, falling back to mock: {last_error}")
        return {
            "response": f"Mock response (fallback) from {self.agent_id or 'agent'}: {query}",
            "confidence": 0.6,
            "error": str(last_error) if last_error else None,
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id
        }
    
    async def health_check(self) -> bool:
        """Check if the MCP agent is healthy"""
        if not self.endpoint or aiohttp is None:
            return False
        if self.session is None:
            return False
        try:
            async with self.session.get(f"{self.endpoint}/health", timeout=5) as resp:
                return resp.status == 200
        except Exception:
            return False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current client status"""
        return {
            "connected": self.is_connected,
            "endpoint": self.endpoint,
            "agent_id": self.agent_id,
            "last_activity": datetime.utcnow().isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        self.is_connected = False
        self.endpoint = None
        self.agent_id = None
        try:
            if self.session is not None:
                await self.session.close()
        finally:
            self.session = None
        logger.info("MCP Client cleanup completed") 