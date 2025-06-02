"""
Cache Manager for Orion Vision Core

This module provides comprehensive multi-level caching system.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import time
import threading
import pickle
from typing import Dict, List, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import OrderedDict
import weakref

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class CacheLevel(Enum):
    """Cache level enumeration"""
    L1_MEMORY = "l1_memory"
    L2_MEMORY = "l2_memory"
    L3_DISK = "l3_disk"
    DISTRIBUTED = "distributed"


class CachePolicy(Enum):
    """Cache eviction policy enumeration"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    RANDOM = "random"


@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl: Optional[float] = None
    size_bytes: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Calculate entry size after initialization"""
        try:
            self.size_bytes = len(pickle.dumps(self.value))
        except:
            self.size_bytes = 1024  # Default size if pickle fails
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() > (self.created_at + self.ttl)
    
    def touch(self):
        """Update access information"""
        self.last_accessed = time.time()
        self.access_count += 1


class CacheManager:
    """
    Multi-level caching system
    
    Provides L1 (fast memory), L2 (larger memory), and L3 (disk) caching
    with configurable eviction policies and automatic cache warming.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize cache manager"""
        self.logger = logger or AgentLogger("cache_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Cache storage
        self.l1_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.l2_cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.l3_cache: Dict[str, str] = {}  # key -> file_path for disk cache
        
        # Cache configuration
        self.l1_max_size = 100  # entries
        self.l2_max_size = 1000  # entries
        self.l3_max_size = 10000  # entries
        self.l1_max_memory = 10 * 1024 * 1024  # 10MB
        self.l2_max_memory = 100 * 1024 * 1024  # 100MB
        
        # Cache policies
        self.l1_policy = CachePolicy.LRU
        self.l2_policy = CachePolicy.LRU
        self.l3_policy = CachePolicy.TTL
        
        # Cache warming
        self.cache_warmers: Dict[str, Callable] = {}
        self.auto_warm_enabled = True
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.cache_stats = {
            'l1_hits': 0,
            'l1_misses': 0,
            'l2_hits': 0,
            'l2_misses': 0,
            'l3_hits': 0,
            'l3_misses': 0,
            'total_sets': 0,
            'total_deletes': 0,
            'evictions': 0,
            'cache_warming_runs': 0
        }
        
        self.logger.info("Cache Manager initialized")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache with multi-level lookup"""
        try:
            with self._lock:
                # Try L1 cache first
                if key in self.l1_cache:
                    entry = self.l1_cache[key]
                    if not entry.is_expired():
                        entry.touch()
                        self._move_to_front(self.l1_cache, key)
                        self.cache_stats['l1_hits'] += 1
                        
                        self.metrics_collector.collect_metric(
                            name="cache.hit",
                            value=1,
                            metric_type=MetricType.COUNTER,
                            tags={'level': 'l1', 'key': key}
                        )
                        
                        self.logger.debug("L1 cache hit", key=key)
                        return entry.value
                    else:
                        # Remove expired entry
                        del self.l1_cache[key]
                
                self.cache_stats['l1_misses'] += 1
                
                # Try L2 cache
                if key in self.l2_cache:
                    entry = self.l2_cache[key]
                    if not entry.is_expired():
                        entry.touch()
                        self._move_to_front(self.l2_cache, key)
                        
                        # Promote to L1
                        self._promote_to_l1(key, entry)
                        
                        self.cache_stats['l2_hits'] += 1
                        
                        self.metrics_collector.collect_metric(
                            name="cache.hit",
                            value=1,
                            metric_type=MetricType.COUNTER,
                            tags={'level': 'l2', 'key': key}
                        )
                        
                        self.logger.debug("L2 cache hit, promoted to L1", key=key)
                        return entry.value
                    else:
                        # Remove expired entry
                        del self.l2_cache[key]
                
                self.cache_stats['l2_misses'] += 1
                
                # Try L3 cache (disk)
                if key in self.l3_cache:
                    try:
                        file_path = self.l3_cache[key]
                        with open(file_path, 'rb') as f:
                            entry = pickle.load(f)
                        
                        if not entry.is_expired():
                            entry.touch()
                            
                            # Promote to L2
                            self._promote_to_l2(key, entry)
                            
                            self.cache_stats['l3_hits'] += 1
                            
                            self.metrics_collector.collect_metric(
                                name="cache.hit",
                                value=1,
                                metric_type=MetricType.COUNTER,
                                tags={'level': 'l3', 'key': key}
                            )
                            
                            self.logger.debug("L3 cache hit, promoted to L2", key=key)
                            return entry.value
                        else:
                            # Remove expired entry
                            import os
                            if os.path.exists(file_path):
                                os.remove(file_path)
                            del self.l3_cache[key]
                    except Exception as e:
                        self.logger.warning("L3 cache read failed", key=key, error=str(e))
                        if key in self.l3_cache:
                            del self.l3_cache[key]
                
                self.cache_stats['l3_misses'] += 1
                
                # Cache miss - try cache warming
                if self.auto_warm_enabled and key in self.cache_warmers:
                    try:
                        warmer = self.cache_warmers[key]
                        value = warmer()
                        self.set(key, value)
                        self.cache_stats['cache_warming_runs'] += 1
                        
                        self.logger.debug("Cache warmed", key=key)
                        return value
                    except Exception as e:
                        self.logger.warning("Cache warming failed", key=key, error=str(e))
                
                # Complete miss
                self.metrics_collector.collect_metric(
                    name="cache.miss",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={'key': key}
                )
                
                return default
                
        except Exception as e:
            self.logger.error("Cache get failed", key=key, error=str(e))
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, 
           level: CacheLevel = CacheLevel.L1_MEMORY) -> bool:
        """Set value in cache at specified level"""
        try:
            with self._lock:
                entry = CacheEntry(key=key, value=value, ttl=ttl)
                
                if level == CacheLevel.L1_MEMORY:
                    self._set_l1(key, entry)
                elif level == CacheLevel.L2_MEMORY:
                    self._set_l2(key, entry)
                elif level == CacheLevel.L3_DISK:
                    self._set_l3(key, entry)
                
                self.cache_stats['total_sets'] += 1
                
                self.metrics_collector.collect_metric(
                    name="cache.set",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={'level': level.value, 'key': key}
                )
                
                self.logger.debug("Cache set", key=key, level=level.value)
                return True
                
        except Exception as e:
            self.logger.error("Cache set failed", key=key, level=level.value, error=str(e))
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from all cache levels"""
        try:
            with self._lock:
                deleted = False
                
                # Remove from L1
                if key in self.l1_cache:
                    del self.l1_cache[key]
                    deleted = True
                
                # Remove from L2
                if key in self.l2_cache:
                    del self.l2_cache[key]
                    deleted = True
                
                # Remove from L3
                if key in self.l3_cache:
                    try:
                        file_path = self.l3_cache[key]
                        import os
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        del self.l3_cache[key]
                        deleted = True
                    except Exception as e:
                        self.logger.warning("L3 cache delete failed", key=key, error=str(e))
                
                if deleted:
                    self.cache_stats['total_deletes'] += 1
                    
                    self.metrics_collector.collect_metric(
                        name="cache.delete",
                        value=1,
                        metric_type=MetricType.COUNTER,
                        tags={'key': key}
                    )
                    
                    self.logger.debug("Cache delete", key=key)
                
                return deleted
                
        except Exception as e:
            self.logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    def clear(self, level: Optional[CacheLevel] = None):
        """Clear cache at specified level or all levels"""
        try:
            with self._lock:
                if level is None or level == CacheLevel.L1_MEMORY:
                    self.l1_cache.clear()
                
                if level is None or level == CacheLevel.L2_MEMORY:
                    self.l2_cache.clear()
                
                if level is None or level == CacheLevel.L3_DISK:
                    # Clean up disk files
                    import os
                    for file_path in self.l3_cache.values():
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except:
                            pass
                    self.l3_cache.clear()
                
                level_name = level.value if level else "all"
                self.logger.info("Cache cleared", level=level_name)
                
        except Exception as e:
            self.logger.error("Cache clear failed", level=level.value if level else "all", error=str(e))
    
    def register_cache_warmer(self, key: str, warmer_func: Callable[[], Any]):
        """Register cache warming function for a key"""
        self.cache_warmers[key] = warmer_func
        
        self.logger.info("Cache warmer registered", key=key)
    
    def warm_cache(self, keys: Optional[List[str]] = None):
        """Manually warm cache for specified keys or all registered warmers"""
        try:
            keys_to_warm = keys or list(self.cache_warmers.keys())
            
            for key in keys_to_warm:
                if key in self.cache_warmers:
                    try:
                        warmer = self.cache_warmers[key]
                        value = warmer()
                        self.set(key, value)
                        self.cache_stats['cache_warming_runs'] += 1
                        
                        self.logger.debug("Cache warmed", key=key)
                    except Exception as e:
                        self.logger.warning("Cache warming failed", key=key, error=str(e))
            
            self.logger.info("Cache warming completed", keys_count=len(keys_to_warm))
            
        except Exception as e:
            self.logger.error("Cache warming failed", error=str(e))
    
    def _set_l1(self, key: str, entry: CacheEntry):
        """Set entry in L1 cache"""
        self.l1_cache[key] = entry
        self._enforce_l1_limits()
    
    def _set_l2(self, key: str, entry: CacheEntry):
        """Set entry in L2 cache"""
        self.l2_cache[key] = entry
        self._enforce_l2_limits()
    
    def _set_l3(self, key: str, entry: CacheEntry):
        """Set entry in L3 cache (disk)"""
        try:
            import tempfile
            import os
            
            # Create temp file
            fd, file_path = tempfile.mkstemp(prefix=f"cache_{key}_", suffix=".pkl")
            os.close(fd)
            
            # Write entry to file
            with open(file_path, 'wb') as f:
                pickle.dump(entry, f)
            
            self.l3_cache[key] = file_path
            self._enforce_l3_limits()
            
        except Exception as e:
            self.logger.error("L3 cache set failed", key=key, error=str(e))
    
    def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote entry from L2 to L1"""
        self.l1_cache[key] = entry
        self._enforce_l1_limits()
    
    def _promote_to_l2(self, key: str, entry: CacheEntry):
        """Promote entry from L3 to L2"""
        self.l2_cache[key] = entry
        self._enforce_l2_limits()
    
    def _enforce_l1_limits(self):
        """Enforce L1 cache size limits"""
        while len(self.l1_cache) > self.l1_max_size:
            self._evict_from_cache(self.l1_cache, self.l1_policy)
    
    def _enforce_l2_limits(self):
        """Enforce L2 cache size limits"""
        while len(self.l2_cache) > self.l2_max_size:
            self._evict_from_cache(self.l2_cache, self.l2_policy)
    
    def _enforce_l3_limits(self):
        """Enforce L3 cache size limits"""
        while len(self.l3_cache) > self.l3_max_size:
            # Remove oldest entry
            if self.l3_cache:
                oldest_key = next(iter(self.l3_cache))
                file_path = self.l3_cache[oldest_key]
                try:
                    import os
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
                del self.l3_cache[oldest_key]
                self.cache_stats['evictions'] += 1
    
    def _evict_from_cache(self, cache: OrderedDict, policy: CachePolicy):
        """Evict entry from cache based on policy"""
        if not cache:
            return
        
        if policy == CachePolicy.LRU:
            # Remove least recently used (first in OrderedDict)
            cache.popitem(last=False)
        elif policy == CachePolicy.FIFO:
            # Remove first in (first in OrderedDict)
            cache.popitem(last=False)
        else:
            # Default to LRU
            cache.popitem(last=False)
        
        self.cache_stats['evictions'] += 1
    
    def _move_to_front(self, cache: OrderedDict, key: str):
        """Move key to front of OrderedDict (most recently used)"""
        cache.move_to_end(key)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_hits = (self.cache_stats['l1_hits'] + 
                         self.cache_stats['l2_hits'] + 
                         self.cache_stats['l3_hits'])
            total_misses = (self.cache_stats['l1_misses'] + 
                           self.cache_stats['l2_misses'] + 
                           self.cache_stats['l3_misses'])
            total_requests = total_hits + total_misses
            
            hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'l1_size': len(self.l1_cache),
                'l2_size': len(self.l2_cache),
                'l3_size': len(self.l3_cache),
                'l1_max_size': self.l1_max_size,
                'l2_max_size': self.l2_max_size,
                'l3_max_size': self.l3_max_size,
                'hit_rate_percent': hit_rate,
                'cache_warmers_count': len(self.cache_warmers),
                'auto_warm_enabled': self.auto_warm_enabled,
                'stats': self.cache_stats.copy()
            }
