"""
Rate Limiting Middleware
Apply rate limiting to requests based on user/IP and endpoint
"""

import logging
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from ..core.rate_limiter import rate_limiter

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware to apply rate limiting to requests"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Map endpoints to rate limit keys
        self.endpoint_limits = {
            "/auth/login": "auth",
            "/auth/register": "auth",
            "/query": "query",
            "/rag/upload": "upload",
            "/batch/queries": "api",
            "/batch/documents": "upload",
        }
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting based on endpoint"""
        # Get rate limit key for endpoint
        limit_key = None
        for endpoint, key in self.endpoint_limits.items():
            if request.url.path.startswith(endpoint):
                limit_key = key
                break
        
        # Default to API limit if no specific limit found
        if limit_key is None and request.url.path.startswith("/"):
            limit_key = "api"
        
        # Apply rate limiting if configured
        if limit_key:
            # Get identifier (user ID or IP address)
            identifier = request.headers.get("X-User-ID", request.client.host if request.client else "unknown")
            
            allowed, info = await rate_limiter.check_rate_limit(identifier, limit_key)
            
            if not allowed:
                logger.warning(
                    f"Rate limit exceeded: {identifier} on {request.url.path} "
                    f"(limit: {info['limit']}, retry_after: {info['retry_after']}s)"
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Please try again in {info['retry_after']} seconds.",
                        "limit": info["limit"],
                        "retry_after": info["retry_after"],
                        "reset_at": info["reset_at"]
                    },
                    headers={
                        "X-RateLimit-Limit": str(info["limit"]),
                        "X-RateLimit-Remaining": str(info["remaining"]),
                        "X-RateLimit-Reset": info["reset_at"],
                        "Retry-After": str(info["retry_after"])
                    }
                )
            
            # Add rate limit headers to response
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(info["limit"])
            response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
            response.headers["X-RateLimit-Reset"] = info["reset_at"]
            return response
        
        # No rate limiting for this endpoint
        return await call_next(request)

