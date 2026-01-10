"""
Monitoring and Metrics Middleware
Request/response metrics, performance tracking, and observability
"""

import logging
import time
from typing import Dict, Any
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from datetime import datetime

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.endpoint_stats: Dict[str, Dict[str, Any]] = {}
        self.status_code_counts: Dict[int, int] = {}
        
    def record_request(
        self, 
        endpoint: str, 
        method: str,
        status_code: int,
        response_time: float
    ):
        """Record a request metric"""
        self.request_count += 1
        self.total_response_time += response_time
        
        if status_code >= 400:
            self.error_count += 1
        
        # Track status codes
        if status_code not in self.status_code_counts:
            self.status_code_counts[status_code] = 0
        self.status_code_counts[status_code] += 1
        
        # Track endpoint stats
        endpoint_key = f"{method} {endpoint}"
        if endpoint_key not in self.endpoint_stats:
            self.endpoint_stats[endpoint_key] = {
                "count": 0,
                "total_time": 0.0,
                "avg_time": 0.0,
                "errors": 0
            }
        
        stats = self.endpoint_stats[endpoint_key]
        stats["count"] += 1
        stats["total_time"] += response_time
        stats["avg_time"] = stats["total_time"] / stats["count"]
        
        if status_code >= 400:
            stats["errors"] += 1
    
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregated statistics"""
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 
            else 0.0
        )
        
        error_rate = (
            (self.error_count / self.request_count * 100)
            if self.request_count > 0
            else 0.0
        )
        
        return {
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "error_rate": round(error_rate, 2),
            "avg_response_time_ms": round(avg_response_time * 1000, 2),
            "status_codes": self.status_code_counts,
            "top_endpoints": dict(
                sorted(
                    self.endpoint_stats.items(),
                    key=lambda x: x[1]["count"],
                    reverse=True
                )[:10]
            )
        }
    
    def reset(self):
        """Reset all metrics"""
        self.request_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.endpoint_stats.clear()
        self.status_code_counts.clear()

# Global metrics collector
metrics_collector = MetricsCollector()

class MonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response monitoring"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics"""
        start_time = time.time()
        
        # Extract endpoint info
        endpoint = request.url.path
        method = request.method
        
        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as e:
            status_code = 500
            logger.error(f"Request error: {endpoint} - {str(e)}")
            raise
        finally:
            # Calculate response time
            response_time = time.time() - start_time
            
            # Record metrics
            metrics_collector.record_request(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                response_time=response_time
            )
            
            # Add response headers
            response.headers["X-Response-Time"] = f"{response_time:.4f}s"
            response.headers["X-Request-ID"] = request.headers.get("X-Request-ID", "unknown")
        
        return response

class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and optimization"""
    
    async def dispatch(self, request: Request, call_next):
        """Add performance headers and track slow requests"""
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Log slow requests (>1 second)
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} "
                f"took {duration:.3f}s"
            )
        
        # Add performance headers
        response.headers["X-Process-Time"] = f"{duration:.4f}"
        response.headers["X-Served-By"] = "multi-agent-mcp"
        
        return response

