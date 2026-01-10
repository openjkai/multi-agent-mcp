"""
Rate Limiting Middleware
Token bucket and sliding window rate limiting for API protection
"""

import logging
import asyncio
import time
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class RateLimitConfig:
    """Rate limit configuration"""
    requests: int  # Number of requests
    window: int  # Time window in seconds
    burst: Optional[int] = None  # Burst allowance
    
@dataclass
class RateLimitState:
    """Rate limit state for a key"""
    tokens: float
    last_refill: float
    requests: deque = field(default_factory=deque)

class RateLimiter:
    """
    Token bucket rate limiter with sliding window
    Supports multiple rate limit strategies
    """
    
    def __init__(self):
        self.limiters: Dict[str, RateLimitState] = {}
        self.configs: Dict[str, RateLimitConfig] = {}
        self._lock = asyncio.Lock()
        logger.info("Rate Limiter initialized")
    
    def add_limit(
        self, 
        key: str, 
        requests: int, 
        window: int = 60,
        burst: Optional[int] = None
    ):
        """Add rate limit configuration"""
        config = RateLimitConfig(
            requests=requests,
            window=window,
            burst=burst or requests
        )
        self.configs[key] = config
        logger.info(f"Rate limit added: {key} = {requests} req/{window}s")
    
    async def check_rate_limit(
        self, 
        identifier: str, 
        limit_key: str
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if request is allowed
        
        Returns:
            (allowed, info_dict)
        """
        if limit_key not in self.configs:
            return True, {"allowed": True, "reason": "no_limit"}
        
        config = self.configs[limit_key]
        full_key = f"{limit_key}:{identifier}"
        
        async with self._lock:
            state = self.limiters.get(full_key)
            now = time.time()
            
            if state is None:
                state = RateLimitState(
                    tokens=float(config.burst),
                    last_refill=now
                )
                self.limiters[full_key] = state
            
            # Refill tokens based on elapsed time
            elapsed = now - state.last_refill
            refill_amount = (elapsed / config.window) * config.requests
            state.tokens = min(config.burst, state.tokens + refill_amount)
            state.last_refill = now
            
            # Clean old requests from sliding window
            cutoff = now - config.window
            while state.requests and state.requests[0] < cutoff:
                state.requests.popleft()
            
            # Check if request is allowed
            if state.tokens >= 1.0 and len(state.requests) < config.requests:
                state.tokens -= 1.0
                state.requests.append(now)
                
                remaining = int(state.tokens)
                reset_time = now + config.window
                
                return True, {
                    "allowed": True,
                    "remaining": remaining,
                    "limit": config.requests,
                    "reset_at": datetime.utcfromtimestamp(reset_time).isoformat()
                }
            else:
                # Calculate retry after
                if state.requests:
                    oldest = state.requests[0]
                    retry_after = int(config.window - (now - oldest))
                else:
                    retry_after = int(config.window * (1 - state.tokens / config.requests))
                
                return False, {
                    "allowed": False,
                    "remaining": 0,
                    "limit": config.requests,
                    "retry_after": retry_after,
                    "reset_at": datetime.utcfromtimestamp(now + retry_after).isoformat()
                }
    
    async def reset_limit(self, identifier: str, limit_key: str):
        """Reset rate limit for an identifier"""
        full_key = f"{limit_key}:{identifier}"
        async with self._lock:
            if full_key in self.limiters:
                del self.limiters[full_key]
                logger.info(f"Rate limit reset: {full_key}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics"""
        return {
            "active_limiters": len(self.limiters),
            "configured_limits": len(self.configs),
            "configs": {
                key: {
                    "requests": config.requests,
                    "window": config.window,
                    "burst": config.burst
                }
                for key, config in self.configs.items()
            }
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

# Default rate limits
rate_limiter.add_limit("api", requests=100, window=60, burst=150)
rate_limiter.add_limit("auth", requests=10, window=60, burst=15)
rate_limiter.add_limit("query", requests=50, window=60, burst=75)
rate_limiter.add_limit("upload", requests=20, window=60, burst=30)

