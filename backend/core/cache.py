"""
Caching Layer for Multi-Agent MCP
High-performance caching system with TTL support and invalidation
"""

import logging
import asyncio
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib
import json

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    value: Any
    created_at: datetime
    expires_at: Optional[datetime] = None
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)
    tags: list = field(default_factory=list)

class CacheManager:
    """
    High-performance in-memory cache with TTL and LRU eviction
    Supports cache tags for bulk invalidation
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 300):
        """
        Initialize cache manager
        
        Args:
            max_size: Maximum number of entries (LRU eviction)
            default_ttl: Default time-to-live in seconds
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: Dict[str, CacheEntry] = OrderedDict()
        self.tag_index: Dict[str, set] = {}  # tag -> set of keys
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0,
            "invalidations": 0
        }
        self._lock = asyncio.Lock()
        logger.info(f"Cache Manager initialized: max_size={max_size}, default_ttl={default_ttl}s")
    
    def _make_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a cache key from prefix and arguments"""
        key_data = {
            "prefix": prefix,
            "args": args,
            "kwargs": kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        async with self._lock:
            if key not in self.cache:
                self.stats["misses"] += 1
                return None
            
            entry = self.cache[key]
            
            # Check expiration
            if entry.expires_at and datetime.utcnow() > entry.expires_at:
                del self.cache[key]
                self._remove_from_tags(entry)
                self.stats["misses"] += 1
                logger.debug(f"Cache entry expired: {key}")
                return None
            
            # Update access tracking (LRU)
            self.cache.move_to_end(key)
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            
            self.stats["hits"] += 1
            logger.debug(f"Cache hit: {key}")
            return entry.value
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        tags: Optional[list] = None
    ):
        """Set value in cache"""
        async with self._lock:
            ttl = ttl or self.default_ttl
            expires_at = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=datetime.utcnow(),
                expires_at=expires_at,
                tags=tags or []
            )
            
            # Add to tag index
            if tags:
                for tag in tags:
                    if tag not in self.tag_index:
                        self.tag_index[tag] = set()
                    self.tag_index[tag].add(key)
            
            # Evict if needed
            if len(self.cache) >= self.max_size and key not in self.cache:
                await self._evict_lru()
            
            self.cache[key] = entry
            self.cache.move_to_end(key)
            self.stats["sets"] += 1
            logger.debug(f"Cache set: {key}, ttl={ttl}s, tags={tags}")
    
    async def delete(self, key: str) -> bool:
        """Delete a cache entry"""
        async with self._lock:
            if key not in self.cache:
                return False
            
            entry = self.cache[key]
            self._remove_from_tags(entry)
            del self.cache[key]
            logger.debug(f"Cache deleted: {key}")
            return True
    
    async def invalidate_tags(self, tags: list) -> int:
        """Invalidate all entries with specified tags"""
        async with self._lock:
            keys_to_delete = set()
            for tag in tags:
                if tag in self.tag_index:
                    keys_to_delete.update(self.tag_index[tag])
                    del self.tag_index[tag]
            
            count = 0
            for key in keys_to_delete:
                if key in self.cache:
                    del self.cache[key]
                    count += 1
            
            self.stats["invalidations"] += count
            logger.info(f"Invalidated {count} cache entries with tags: {tags}")
            return count
    
    async def clear(self):
        """Clear all cache entries"""
        async with self._lock:
            self.cache.clear()
            self.tag_index.clear()
            logger.info("Cache cleared")
    
    async def _evict_lru(self):
        """Evict least recently used entry"""
        if not self.cache:
            return
        
        # Remove first (oldest) entry
        key, entry = next(iter(self.cache.items()))
        self._remove_from_tags(entry)
        del self.cache[key]
        self.stats["evictions"] += 1
        logger.debug(f"LRU eviction: {key}")
    
    def _remove_from_tags(self, entry: CacheEntry):
        """Remove entry from tag index"""
        for tag in entry.tags:
            if tag in self.tag_index:
                self.tag_index[tag].discard(entry.key)
                if not self.tag_index[tag]:
                    del self.tag_index[tag]
    
    async def get_or_set(
        self, 
        key: str, 
        callable_fn: Callable, 
        ttl: Optional[int] = None,
        tags: Optional[list] = None
    ) -> Any:
        """Get from cache or compute and set"""
        value = await self.get(key)
        if value is not None:
            return value
        
        # Compute value
        if asyncio.iscoroutinefunction(callable_fn):
            value = await callable_fn()
        else:
            value = callable_fn()
        
        await self.set(key, value, ttl=ttl, tags=tags)
        return value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "size": len(self.cache),
            "max_size": self.max_size,
            "hit_rate": round(hit_rate, 2),
            "tags_count": len(self.tag_index)
        }
    
    async def cleanup_expired(self) -> int:
        """Remove all expired entries"""
        async with self._lock:
            now = datetime.utcnow()
            expired_keys = [
                key for key, entry in self.cache.items()
                if entry.expires_at and entry.expires_at < now
            ]
            
            for key in expired_keys:
                entry = self.cache[key]
                self._remove_from_tags(entry)
                del self.cache[key]
            
            logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
            return len(expired_keys)

# Global cache instance
cache_manager = CacheManager(max_size=2000, default_ttl=600)

