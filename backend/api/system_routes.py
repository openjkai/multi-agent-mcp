"""
System Management API Routes
Cache management, metrics, rate limiting, and system utilities
"""

import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request
from pydantic import BaseModel

from ..core.auth import get_current_user, get_current_admin_user
from ..core.database import User
from ..core.cache import cache_manager
from ..core.rate_limiter import rate_limiter
from ..middleware.monitoring import metrics_collector
from datetime import datetime

logger = logging.getLogger(__name__)

system_router = APIRouter(prefix="/system", tags=["system"])

# Request models
class CacheInvalidateRequest(BaseModel):
    tags: List[str]

class RateLimitConfigRequest(BaseModel):
    key: str
    requests: int
    window: int = 60
    burst: Optional[int] = None

@system_router.get("/metrics")
async def get_metrics(
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get system metrics and performance statistics
    Admin only
    """
    try:
        cache_stats = cache_manager.get_stats()
        rate_limit_stats = rate_limiter.get_stats()
        request_metrics = metrics_collector.get_stats()
        
        return {
            "status": "success",
            "timestamp": datetime.utcnow().isoformat(),
            "cache": cache_stats,
            "rate_limiting": rate_limit_stats,
            "requests": request_metrics
        }
    except Exception as e:
        logger.error(f"Failed to get metrics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )

@system_router.get("/cache/stats")
async def get_cache_stats(
    current_user: User = Depends(get_current_admin_user)
):
    """Get cache statistics"""
    stats = cache_manager.get_stats()
    return {
        "status": "success",
        "cache": stats
    }

@system_router.post("/cache/invalidate")
async def invalidate_cache(
    request: CacheInvalidateRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Invalidate cache entries by tags"""
    count = await cache_manager.invalidate_tags(request.tags)
    return {
        "status": "success",
        "invalidated": count,
        "tags": request.tags
    }

@system_router.delete("/cache/clear")
async def clear_cache(
    current_user: User = Depends(get_current_admin_user)
):
    """Clear all cache entries"""
    await cache_manager.clear()
    return {
        "status": "success",
        "message": "Cache cleared"
    }

@system_router.post("/cache/cleanup")
async def cleanup_expired_cache(
    current_user: User = Depends(get_current_admin_user)
):
    """Remove expired cache entries"""
    count = await cache_manager.cleanup_expired()
    return {
        "status": "success",
        "cleaned": count
    }

@system_router.get("/rate-limits")
async def get_rate_limits(
    current_user: User = Depends(get_current_admin_user)
):
    """Get rate limit configurations"""
    stats = rate_limiter.get_stats()
    return {
        "status": "success",
        "rate_limits": stats
    }

@system_router.post("/rate-limits")
async def configure_rate_limit(
    request: RateLimitConfigRequest,
    current_user: User = Depends(get_current_admin_user)
):
    """Configure a rate limit"""
    rate_limiter.add_limit(
        key=request.key,
        requests=request.requests,
        window=request.window,
        burst=request.burst
    )
    return {
        "status": "success",
        "message": f"Rate limit configured: {request.key} = {request.requests} req/{request.window}s"
    }

@system_router.delete("/rate-limits/{identifier}/{limit_key}")
async def reset_rate_limit(
    identifier: str,
    limit_key: str,
    current_user: User = Depends(get_current_admin_user)
):
    """Reset rate limit for an identifier"""
    await rate_limiter.reset_limit(identifier, limit_key)
    return {
        "status": "success",
        "message": f"Rate limit reset for {identifier}:{limit_key}"
    }

@system_router.post("/metrics/reset")
async def reset_metrics(
    current_user: User = Depends(get_current_admin_user)
):
    """Reset all metrics counters"""
    metrics_collector.reset()
    return {
        "status": "success",
        "message": "Metrics reset"
    }

@system_router.get("/health/detailed")
async def detailed_health_check(
    current_user: User = Depends(get_current_user)
):
    """
    Detailed health check with all system components
    Includes cache, rate limiting, and metrics
    """
    try:
        cache_stats = cache_manager.get_stats()
        rate_limit_stats = rate_limiter.get_stats()
        request_metrics = metrics_collector.get_stats()
        
        # Calculate system health score (0-100)
        health_score = 100
        
        # Deduct points for errors
        if request_metrics.get("error_rate", 0) > 10:
            health_score -= 20
        elif request_metrics.get("error_rate", 0) > 5:
            health_score -= 10
        
        # Deduct points for slow responses
        if request_metrics.get("avg_response_time_ms", 0) > 1000:
            health_score -= 20
        elif request_metrics.get("avg_response_time_ms", 0) > 500:
            health_score -= 10
        
        # Deduct points for low cache hit rate
        if cache_stats.get("hit_rate", 0) < 50 and cache_stats.get("hits", 0) > 100:
            health_score -= 10
        
        health_status = "healthy" if health_score >= 80 else "degraded" if health_score >= 50 else "unhealthy"
        
        return {
            "status": health_status,
            "health_score": health_score,
            "timestamp": datetime.utcnow().isoformat(),
            "components": {
                "cache": {
                    "status": "operational",
                    "hit_rate": cache_stats.get("hit_rate", 0),
                    "size": cache_stats.get("size", 0)
                },
                "rate_limiting": {
                    "status": "operational",
                    "active_limiters": rate_limit_stats.get("active_limiters", 0)
                },
                "requests": {
                    "status": "operational",
                    "total": request_metrics.get("total_requests", 0),
                    "error_rate": request_metrics.get("error_rate", 0),
                    "avg_response_time_ms": request_metrics.get("avg_response_time_ms", 0)
                }
            }
        }
    except Exception as e:
        logger.error(f"Detailed health check failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

