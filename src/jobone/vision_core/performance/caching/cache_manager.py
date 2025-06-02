"""
Cache Manager for Orion Vision Core

This module provides comprehensive caching capabilities including
multi-level caching, cache strategies, and performance optimization.
Part of Sprint 9.8 Advanced Performance & Optimization development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.8 - Advanced Performance & Optimization
"""

import time
import threading
import json
import hashlib
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class CacheStrategy(Enum):
    """Cache strategy enumeration"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive strategy


class CacheLevel(Enum):
    """Cache level enumeration"""
    L1_MEMORY = "l1_memory"
    L2_DISK = "l2_disk"
    L3_DISTRIBUTED = "l3_distributed"
    L4_REMOTE = "l4_remote"


class CacheStatus(Enum):
    """Cache status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    WARMING = "warming"
    FLUSHING = "flushing"
    ERROR = "error"


@dataclass
class CacheEntry:
    """Cache entry data structure"""
    key: str
    value: Any
    size_bytes: int = 0
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    access_count: int = 0
    ttl_seconds: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl_seconds is None:
            return False
        return time.time() > (self.created_at + self.ttl_seconds)
    
    def get_age_seconds(self) -> float:
        """Get entry age in seconds"""
        return time.time() - self.created_at
    
    def touch(self):
        """Update last accessed time and increment access count"""
        self.last_accessed = time.time()
        self.access_count += 1


@dataclass
class CacheConfig:
    """Cache configuration"""
    cache_id: str
    cache_name: str
    strategy: CacheStrategy
    level: CacheLevel
    max_size_mb: float = 100.0
    max_entries: int = 10000
    default_ttl_seconds: Optional[float] = None
    compression_enabled: bool = False
    encryption_enabled: bool = False
    persistence_enabled: bool = False
    
    def validate(self) -> bool:
        """Validate cache configuration"""
        if not self.cache_name or not self.cache_id:
            return False
        if self.max_size_mb <= 0 or self.max_entries <= 0:
            return False
        return True


@dataclass
class CacheStats:
    """Cache statistics"""
    cache_id: str
    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    evictions: int = 0
    current_entries: int = 0
    current_size_mb: float = 0.0
    hit_rate: float = 0.0
    miss_rate: float = 0.0
    average_access_time_ms: float = 0.0
    last_updated: float = field(default_factory=time.time)
    
    def update_hit_rate(self):
        """Update hit and miss rates"""
        if self.total_requests > 0:
            self.hit_rate = (self.cache_hits / self.total_requests) * 100
            self.miss_rate = (self.cache_misses / self.total_requests) * 100
        else:
            self.hit_rate = 0.0
            self.miss_rate = 0.0


class CacheManager:
    """
    Comprehensive cache management system
    
    Provides multi-level caching, cache strategies, performance optimization,
    and intelligent cache management with real-time monitoring.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize cache manager"""
        self.logger = logger or AgentLogger("cache_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Cache storage
        self.caches: Dict[str, Dict[str, CacheEntry]] = {}
        self.cache_configs: Dict[str, CacheConfig] = {}
        self.cache_stats: Dict[str, CacheStats] = {}
        
        # Cache strategies
        self.cache_strategies: Dict[CacheStrategy, Callable] = {}
        
        # Configuration
        self.global_max_size_mb = 1000.0
        self.cleanup_interval_seconds = 300  # 5 minutes
        self.stats_update_interval = 60  # 1 minute
        
        # Cleanup control
        self.cleanup_active = False
        self.cleanup_thread: Optional[threading.Thread] = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Global statistics
        self.global_stats = {
            'total_caches': 0,
            'active_caches': 0,
            'total_entries': 0,
            'total_size_mb': 0.0,
            'global_hit_rate': 0.0,
            'global_miss_rate': 0.0,
            'total_evictions': 0,
            'memory_pressure': 0.0
        }
        
        # Initialize cache strategies
        self._initialize_cache_strategies()
        
        # Start cleanup thread
        self._start_cleanup_thread()
        
        self.logger.info("Cache Manager initialized")
    
    def _initialize_cache_strategies(self):
        """Initialize cache strategies"""
        self.cache_strategies[CacheStrategy.LRU] = self._evict_lru
        self.cache_strategies[CacheStrategy.LFU] = self._evict_lfu
        self.cache_strategies[CacheStrategy.FIFO] = self._evict_fifo
        self.cache_strategies[CacheStrategy.TTL] = self._evict_ttl
        self.cache_strategies[CacheStrategy.ADAPTIVE] = self._evict_adaptive
    
    def _start_cleanup_thread(self):
        """Start cache cleanup thread"""
        try:
            self.cleanup_active = True
            self.cleanup_thread = threading.Thread(
                target=self._cleanup_loop,
                name="CacheCleanup",
                daemon=True
            )
            self.cleanup_thread.start()
            
        except Exception as e:
            self.logger.error("Failed to start cleanup thread", error=str(e))
    
    def _cleanup_loop(self):
        """Cache cleanup loop"""
        while self.cleanup_active:
            try:
                # Cleanup expired entries
                self._cleanup_expired_entries()
                
                # Update statistics
                self._update_global_stats()
                
                # Check memory pressure
                self._check_memory_pressure()
                
                time.sleep(self.cleanup_interval_seconds)
                
            except Exception as e:
                self.logger.error("Error in cleanup loop", error=str(e))
                time.sleep(self.cleanup_interval_seconds)
    
    def create_cache(self, config: CacheConfig) -> bool:
        """Create new cache"""
        try:
            # Validate configuration
            if not config.validate():
                self.logger.error("Invalid cache configuration", cache_id=config.cache_id)
                return False
            
            with self._lock:
                # Check if cache already exists
                if config.cache_id in self.caches:
                    self.logger.warning("Cache already exists", cache_id=config.cache_id)
                    return False
                
                # Create cache
                self.caches[config.cache_id] = {}
                self.cache_configs[config.cache_id] = config
                self.cache_stats[config.cache_id] = CacheStats(cache_id=config.cache_id)
                
                # Update global statistics
                self.global_stats['total_caches'] += 1
                self.global_stats['active_caches'] += 1
            
            self.logger.info(
                "Cache created",
                cache_id=config.cache_id,
                cache_name=config.cache_name,
                strategy=config.strategy.value,
                level=config.level.value,
                max_size_mb=config.max_size_mb,
                max_entries=config.max_entries
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Cache creation failed", cache_id=config.cache_id, error=str(e))
            return False
    
    def put(self, cache_id: str, key: str, value: Any, ttl_seconds: Optional[float] = None) -> bool:
        """Put value in cache"""
        try:
            if cache_id not in self.caches:
                self.logger.error("Cache not found", cache_id=cache_id)
                return False
            
            config = self.cache_configs[cache_id]
            cache = self.caches[cache_id]
            stats = self.cache_stats[cache_id]
            
            # Calculate value size (mock)
            value_size = len(str(value).encode('utf-8'))
            
            # Check cache limits
            if len(cache) >= config.max_entries:
                self._evict_entries(cache_id, 1)
            
            current_size_mb = sum(entry.size_bytes for entry in cache.values()) / (1024 * 1024)
            if current_size_mb + (value_size / (1024 * 1024)) > config.max_size_mb:
                self._evict_entries(cache_id, 1)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=value_size,
                ttl_seconds=ttl_seconds or config.default_ttl_seconds
            )
            
            with self._lock:
                # Store entry
                cache[key] = entry
                
                # Update statistics
                stats.current_entries = len(cache)
                stats.current_size_mb = sum(e.size_bytes for e in cache.values()) / (1024 * 1024)
            
            self.logger.debug(
                "Cache entry stored",
                cache_id=cache_id,
                key=key,
                size_bytes=value_size,
                ttl_seconds=entry.ttl_seconds
            )
            
            return True
            
        except Exception as e:
            self.logger.error("Cache put failed", cache_id=cache_id, key=key, error=str(e))
            return False
    
    def get(self, cache_id: str, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if cache_id not in self.caches:
                self.logger.error("Cache not found", cache_id=cache_id)
                return None
            
            cache = self.caches[cache_id]
            stats = self.cache_stats[cache_id]
            
            start_time = time.time()
            
            with self._lock:
                stats.total_requests += 1
                
                if key in cache:
                    entry = cache[key]
                    
                    # Check if expired
                    if entry.is_expired():
                        del cache[key]
                        stats.cache_misses += 1
                        stats.update_hit_rate()
                        return None
                    
                    # Update entry access
                    entry.touch()
                    
                    # Update statistics
                    stats.cache_hits += 1
                    access_time_ms = (time.time() - start_time) * 1000
                    stats.average_access_time_ms = (
                        (stats.average_access_time_ms * (stats.cache_hits - 1) + access_time_ms) / 
                        stats.cache_hits
                    )
                    stats.update_hit_rate()
                    
                    # Collect metrics
                    self.metrics_collector.collect_metric(
                        name="cache.hit",
                        value=1,
                        metric_type=MetricType.COUNTER,
                        tags={'cache_id': cache_id}
                    )
                    
                    self.logger.debug(
                        "Cache hit",
                        cache_id=cache_id,
                        key=key,
                        access_time_ms=f"{access_time_ms:.2f}"
                    )
                    
                    return entry.value
                else:
                    # Cache miss
                    stats.cache_misses += 1
                    stats.update_hit_rate()
                    
                    # Collect metrics
                    self.metrics_collector.collect_metric(
                        name="cache.miss",
                        value=1,
                        metric_type=MetricType.COUNTER,
                        tags={'cache_id': cache_id}
                    )
                    
                    self.logger.debug("Cache miss", cache_id=cache_id, key=key)
                    return None
                    
        except Exception as e:
            self.logger.error("Cache get failed", cache_id=cache_id, key=key, error=str(e))
            return None
    
    def delete(self, cache_id: str, key: str) -> bool:
        """Delete entry from cache"""
        try:
            if cache_id not in self.caches:
                self.logger.error("Cache not found", cache_id=cache_id)
                return False
            
            cache = self.caches[cache_id]
            stats = self.cache_stats[cache_id]
            
            with self._lock:
                if key in cache:
                    del cache[key]
                    stats.current_entries = len(cache)
                    stats.current_size_mb = sum(e.size_bytes for e in cache.values()) / (1024 * 1024)
                    
                    self.logger.debug("Cache entry deleted", cache_id=cache_id, key=key)
                    return True
                else:
                    return False
                    
        except Exception as e:
            self.logger.error("Cache delete failed", cache_id=cache_id, key=key, error=str(e))
            return False
    
    def clear_cache(self, cache_id: str) -> bool:
        """Clear all entries from cache"""
        try:
            if cache_id not in self.caches:
                self.logger.error("Cache not found", cache_id=cache_id)
                return False
            
            with self._lock:
                entries_count = len(self.caches[cache_id])
                self.caches[cache_id].clear()
                
                # Update statistics
                stats = self.cache_stats[cache_id]
                stats.current_entries = 0
                stats.current_size_mb = 0.0
            
            self.logger.info("Cache cleared", cache_id=cache_id, entries_removed=entries_count)
            return True
            
        except Exception as e:
            self.logger.error("Cache clear failed", cache_id=cache_id, error=str(e))
            return False
    
    def _evict_entries(self, cache_id: str, count: int):
        """Evict entries from cache based on strategy"""
        try:
            config = self.cache_configs[cache_id]
            cache = self.caches[cache_id]
            stats = self.cache_stats[cache_id]
            
            if len(cache) == 0:
                return
            
            # Get eviction strategy
            strategy_func = self.cache_strategies.get(config.strategy, self._evict_lru)
            
            # Get keys to evict
            keys_to_evict = strategy_func(cache, count)
            
            # Evict entries
            with self._lock:
                for key in keys_to_evict:
                    if key in cache:
                        del cache[key]
                        stats.evictions += 1
                
                # Update statistics
                stats.current_entries = len(cache)
                stats.current_size_mb = sum(e.size_bytes for e in cache.values()) / (1024 * 1024)
            
            self.logger.debug(
                "Cache entries evicted",
                cache_id=cache_id,
                strategy=config.strategy.value,
                entries_evicted=len(keys_to_evict)
            )
            
        except Exception as e:
            self.logger.error("Cache eviction failed", cache_id=cache_id, error=str(e))
    
    # Eviction strategies
    def _evict_lru(self, cache: Dict[str, CacheEntry], count: int) -> List[str]:
        """Evict least recently used entries"""
        sorted_entries = sorted(cache.items(), key=lambda x: x[1].last_accessed)
        return [key for key, _ in sorted_entries[:count]]
    
    def _evict_lfu(self, cache: Dict[str, CacheEntry], count: int) -> List[str]:
        """Evict least frequently used entries"""
        sorted_entries = sorted(cache.items(), key=lambda x: x[1].access_count)
        return [key for key, _ in sorted_entries[:count]]
    
    def _evict_fifo(self, cache: Dict[str, CacheEntry], count: int) -> List[str]:
        """Evict first in first out entries"""
        sorted_entries = sorted(cache.items(), key=lambda x: x[1].created_at)
        return [key for key, _ in sorted_entries[:count]]
    
    def _evict_ttl(self, cache: Dict[str, CacheEntry], count: int) -> List[str]:
        """Evict entries with shortest TTL"""
        # First evict expired entries
        expired_keys = [key for key, entry in cache.items() if entry.is_expired()]
        if len(expired_keys) >= count:
            return expired_keys[:count]
        
        # Then evict by remaining TTL
        remaining_entries = [(key, entry) for key, entry in cache.items() if not entry.is_expired()]
        sorted_entries = sorted(remaining_entries, key=lambda x: x[1].ttl_seconds or float('inf'))
        
        return expired_keys + [key for key, _ in sorted_entries[:count - len(expired_keys)]]
    
    def _evict_adaptive(self, cache: Dict[str, CacheEntry], count: int) -> List[str]:
        """Adaptive eviction strategy"""
        # Combine LRU and LFU strategies
        lru_candidates = self._evict_lru(cache, count * 2)
        lfu_candidates = self._evict_lfu(cache, count * 2)
        
        # Prioritize entries that appear in both lists
        combined_candidates = []
        for key in lru_candidates:
            if key in lfu_candidates:
                combined_candidates.append(key)
        
        # Add remaining LRU candidates
        for key in lru_candidates:
            if key not in combined_candidates:
                combined_candidates.append(key)
        
        return combined_candidates[:count]
    
    def _cleanup_expired_entries(self):
        """Cleanup expired entries from all caches"""
        try:
            total_cleaned = 0
            
            for cache_id in list(self.caches.keys()):
                cache = self.caches[cache_id]
                stats = self.cache_stats[cache_id]
                
                expired_keys = [key for key, entry in cache.items() if entry.is_expired()]
                
                if expired_keys:
                    with self._lock:
                        for key in expired_keys:
                            if key in cache:
                                del cache[key]
                                total_cleaned += 1
                        
                        # Update statistics
                        stats.current_entries = len(cache)
                        stats.current_size_mb = sum(e.size_bytes for e in cache.values()) / (1024 * 1024)
            
            if total_cleaned > 0:
                self.logger.debug("Expired cache entries cleaned", entries_cleaned=total_cleaned)
                
        except Exception as e:
            self.logger.error("Cache cleanup failed", error=str(e))
    
    def _update_global_stats(self):
        """Update global cache statistics"""
        try:
            with self._lock:
                total_entries = sum(len(cache) for cache in self.caches.values())
                total_size_mb = sum(stats.current_size_mb for stats in self.cache_stats.values())
                
                # Calculate global hit rate
                total_hits = sum(stats.cache_hits for stats in self.cache_stats.values())
                total_requests = sum(stats.total_requests for stats in self.cache_stats.values())
                
                global_hit_rate = (total_hits / max(1, total_requests)) * 100
                global_miss_rate = 100 - global_hit_rate
                
                total_evictions = sum(stats.evictions for stats in self.cache_stats.values())
                
                # Calculate memory pressure
                memory_pressure = (total_size_mb / self.global_max_size_mb) * 100
                
                self.global_stats.update({
                    'total_entries': total_entries,
                    'total_size_mb': total_size_mb,
                    'global_hit_rate': global_hit_rate,
                    'global_miss_rate': global_miss_rate,
                    'total_evictions': total_evictions,
                    'memory_pressure': memory_pressure
                })
                
        except Exception as e:
            self.logger.error("Global stats update failed", error=str(e))
    
    def _check_memory_pressure(self):
        """Check and handle memory pressure"""
        try:
            memory_pressure = self.global_stats['memory_pressure']
            
            if memory_pressure > 90:
                # High memory pressure - aggressive cleanup
                self.logger.warning("High cache memory pressure", pressure_percent=f"{memory_pressure:.1f}")
                
                # Evict from largest caches first
                cache_sizes = [(cache_id, stats.current_size_mb) for cache_id, stats in self.cache_stats.items()]
                cache_sizes.sort(key=lambda x: x[1], reverse=True)
                
                for cache_id, _ in cache_sizes[:3]:  # Top 3 largest caches
                    self._evict_entries(cache_id, 10)
                    
            elif memory_pressure > 75:
                # Medium memory pressure - moderate cleanup
                self.logger.info("Medium cache memory pressure", pressure_percent=f"{memory_pressure:.1f}")
                
                # Cleanup expired entries more aggressively
                self._cleanup_expired_entries()
                
        except Exception as e:
            self.logger.error("Memory pressure check failed", error=str(e))
    
    def get_cache_stats(self, cache_id: str) -> Optional[Dict[str, Any]]:
        """Get cache statistics"""
        if cache_id not in self.cache_stats:
            return None
        
        stats = self.cache_stats[cache_id]
        config = self.cache_configs[cache_id]
        
        return {
            'cache_id': cache_id,
            'cache_name': config.cache_name,
            'strategy': config.strategy.value,
            'level': config.level.value,
            'total_requests': stats.total_requests,
            'cache_hits': stats.cache_hits,
            'cache_misses': stats.cache_misses,
            'hit_rate': stats.hit_rate,
            'miss_rate': stats.miss_rate,
            'evictions': stats.evictions,
            'current_entries': stats.current_entries,
            'max_entries': config.max_entries,
            'current_size_mb': stats.current_size_mb,
            'max_size_mb': config.max_size_mb,
            'average_access_time_ms': stats.average_access_time_ms,
            'utilization_percent': (stats.current_entries / config.max_entries) * 100
        }
    
    def list_caches(self) -> List[Dict[str, Any]]:
        """List all caches"""
        caches = []
        
        for cache_id in self.caches.keys():
            cache_info = self.get_cache_stats(cache_id)
            if cache_info:
                caches.append(cache_info)
        
        return sorted(caches, key=lambda x: x['current_size_mb'], reverse=True)
    
    def get_global_stats(self) -> Dict[str, Any]:
        """Get global cache statistics"""
        with self._lock:
            return {
                'total_caches': len(self.caches),
                'active_caches': len([c for c in self.caches.values() if c]),
                'global_max_size_mb': self.global_max_size_mb,
                'cleanup_interval_seconds': self.cleanup_interval_seconds,
                'cleanup_active': self.cleanup_active,
                'supported_strategies': [s.value for s in CacheStrategy],
                'supported_levels': [l.value for l in CacheLevel],
                'stats': self.global_stats.copy()
            }
