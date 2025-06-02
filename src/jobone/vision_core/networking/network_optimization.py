"""
📈 Orion Vision Core - Network Optimization
Network performance optimization and content delivery

This module provides network optimization features:
- Content delivery network integration
- Intelligent caching strategies
- Data compression and optimization
- Bandwidth optimization
- Network performance monitoring

Sprint 9.3: Advanced Networking and Edge Computing
"""

import asyncio
import logging
import json
import time
import gzip
import zlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import hashlib
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Caching strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    FIFO = "fifo"  # First In, First Out
    TTL = "ttl"  # Time To Live
    ADAPTIVE = "adaptive"  # Adaptive based on usage patterns

class CompressionType(Enum):
    """Compression algorithms"""
    NONE = "none"
    GZIP = "gzip"
    DEFLATE = "deflate"
    BROTLI = "brotli"
    LZ4 = "lz4"
    ZSTD = "zstd"

class CDNProvider(Enum):
    """CDN providers"""
    CLOUDFLARE = "cloudflare"
    AMAZON_CLOUDFRONT = "amazon_cloudfront"
    GOOGLE_CLOUD_CDN = "google_cloud_cdn"
    AZURE_CDN = "azure_cdn"
    FASTLY = "fastly"
    CUSTOM = "custom"

class OptimizationLevel(Enum):
    """Optimization levels"""
    NONE = "none"
    BASIC = "basic"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"

@dataclass
class CacheEntry:
    """Cache entry"""
    key: str
    data: Any
    size: int
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl: Optional[int] = None  # seconds
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompressionResult:
    """Compression result"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    algorithm: CompressionType
    compression_time: float
    data: bytes

@dataclass
class CDNConfig:
    """CDN configuration"""
    provider: CDNProvider
    endpoint: str
    api_key: Optional[str] = None
    cache_ttl: int = 3600  # 1 hour
    compression_enabled: bool = True
    minify_enabled: bool = True
    image_optimization: bool = True

@dataclass
class OptimizationConfig:
    """Network optimization configuration"""
    cache_strategy: CacheStrategy = CacheStrategy.LRU
    compression_type: CompressionType = CompressionType.GZIP
    optimization_level: OptimizationLevel = OptimizationLevel.STANDARD
    max_cache_size_mb: int = 1024  # 1GB
    cache_ttl_seconds: int = 3600  # 1 hour
    compression_threshold: int = 1024  # Compress files > 1KB
    bandwidth_limit_mbps: Optional[float] = None
    enable_prefetching: bool = True
    enable_minification: bool = True

class NetworkOptimization:
    """
    Network optimization and performance manager for Orion Vision Core.
    
    Provides comprehensive network optimization with:
    - Intelligent caching with multiple strategies
    - Data compression and minification
    - CDN integration and management
    - Bandwidth optimization and throttling
    - Performance monitoring and analytics
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        """
        Initialize the network optimization manager.
        
        Args:
            config: Optimization configuration
        """
        self.config = config or OptimizationConfig()
        
        # Caching system
        self.cache: Dict[str, CacheEntry] = {}
        self.cache_size_bytes = 0
        self.max_cache_size_bytes = self.config.max_cache_size_mb * 1024 * 1024
        
        # CDN configuration
        self.cdn_configs: Dict[str, CDNConfig] = {}
        self.active_cdn: Optional[str] = None
        
        # Performance metrics
        self.metrics = {
            'cache_hits': 0,
            'cache_misses': 0,
            'cache_hit_ratio': 0.0,
            'total_requests': 0,
            'bytes_saved_compression': 0,
            'bytes_saved_cache': 0,
            'average_response_time': 0.0,
            'bandwidth_usage_mbps': 0.0,
            'compression_ratio': 0.0
        }
        
        # Optimization history
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Background tasks
        self.cache_cleanup_task: Optional[asyncio.Task] = None
        self.metrics_task: Optional[asyncio.Task] = None
        
        # Event handlers
        self.cache_handlers: List[Callable] = []
        self.compression_handlers: List[Callable] = []
        self.cdn_handlers: List[Callable] = []
        
        logger.info(f"📈 Network Optimization initialized with {self.config.cache_strategy.value} caching")
    
    async def initialize(self) -> bool:
        """
        Initialize the network optimization system.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Start cache cleanup
            await self._start_cache_cleanup()
            
            # Start metrics collection
            await self._start_metrics_collection()
            
            # Initialize compression algorithms
            await self._initialize_compression()
            
            logger.info("✅ Network Optimization system initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Network Optimization initialization failed: {e}")
            return False
    
    async def _start_cache_cleanup(self):
        """Start cache cleanup task"""
        
        if self.cache_cleanup_task and not self.cache_cleanup_task.done():
            return
        
        self.cache_cleanup_task = asyncio.create_task(self._cache_cleanup_loop())
        logger.info("🧹 Cache cleanup started")
    
    async def _cache_cleanup_loop(self):
        """Cache cleanup loop"""
        
        while True:
            try:
                await self._cleanup_expired_cache()
                await self._enforce_cache_size_limit()
                
                # Wait before next cleanup
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
            except Exception as e:
                logger.error(f"❌ Cache cleanup error: {e}")
                await asyncio.sleep(600)  # Wait longer on error
    
    async def _cleanup_expired_cache(self):
        """Remove expired cache entries"""
        
        current_time = datetime.now()
        expired_keys = []
        
        for key, entry in self.cache.items():
            if entry.ttl:
                age_seconds = (current_time - entry.created_at).total_seconds()
                if age_seconds > entry.ttl:
                    expired_keys.append(key)
        
        # Remove expired entries
        for key in expired_keys:
            await self._remove_cache_entry(key)
        
        if expired_keys:
            logger.info(f"🧹 Removed {len(expired_keys)} expired cache entries")
    
    async def _enforce_cache_size_limit(self):
        """Enforce cache size limits using configured strategy"""
        
        if self.cache_size_bytes <= self.max_cache_size_bytes:
            return
        
        # Calculate how much to remove (remove 20% when limit exceeded)
        target_size = int(self.max_cache_size_bytes * 0.8)
        bytes_to_remove = self.cache_size_bytes - target_size
        
        # Get entries to remove based on strategy
        entries_to_remove = await self._select_entries_for_removal(bytes_to_remove)
        
        # Remove selected entries
        for key in entries_to_remove:
            await self._remove_cache_entry(key)
        
        logger.info(f"🧹 Cache size limit enforced: removed {len(entries_to_remove)} entries")
    
    async def _select_entries_for_removal(self, bytes_to_remove: int) -> List[str]:
        """Select cache entries for removal based on strategy"""
        
        entries_to_remove = []
        bytes_removed = 0
        
        if self.config.cache_strategy == CacheStrategy.LRU:
            # Remove least recently used
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
        elif self.config.cache_strategy == CacheStrategy.LFU:
            # Remove least frequently used
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].access_count
            )
        elif self.config.cache_strategy == CacheStrategy.FIFO:
            # Remove oldest entries
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].created_at
            )
        else:
            # Default to LRU
            sorted_entries = sorted(
                self.cache.items(),
                key=lambda x: x[1].last_accessed
            )
        
        # Select entries until we have enough bytes to remove
        for key, entry in sorted_entries:
            entries_to_remove.append(key)
            bytes_removed += entry.size
            
            if bytes_removed >= bytes_to_remove:
                break
        
        return entries_to_remove
    
    async def _remove_cache_entry(self, key: str):
        """Remove a cache entry"""
        
        if key in self.cache:
            entry = self.cache[key]
            self.cache_size_bytes -= entry.size
            del self.cache[key]
    
    async def _start_metrics_collection(self):
        """Start metrics collection task"""
        
        if self.metrics_task and not self.metrics_task.done():
            return
        
        self.metrics_task = asyncio.create_task(self._metrics_loop())
        logger.info("📊 Metrics collection started")
    
    async def _metrics_loop(self):
        """Metrics collection loop"""
        
        while True:
            try:
                # Update cache hit ratio
                total_cache_requests = self.metrics['cache_hits'] + self.metrics['cache_misses']
                if total_cache_requests > 0:
                    self.metrics['cache_hit_ratio'] = self.metrics['cache_hits'] / total_cache_requests
                
                # Calculate average compression ratio
                if self.optimization_history:
                    compression_ratios = [
                        h.get('compression_ratio', 1.0) 
                        for h in self.optimization_history 
                        if 'compression_ratio' in h
                    ]
                    if compression_ratios:
                        self.metrics['compression_ratio'] = sum(compression_ratios) / len(compression_ratios)
                
                # Wait before next collection
                await asyncio.sleep(60)  # Collect every minute
                
            except Exception as e:
                logger.error(f"❌ Metrics collection error: {e}")
                await asyncio.sleep(120)
    
    async def _initialize_compression(self):
        """Initialize compression algorithms"""
        
        # Test compression algorithms availability
        compression_support = {}
        
        try:
            # Test gzip
            test_data = b"test data for compression"
            gzip.compress(test_data)
            compression_support[CompressionType.GZIP] = True
        except Exception:
            compression_support[CompressionType.GZIP] = False
        
        try:
            # Test deflate
            zlib.compress(test_data)
            compression_support[CompressionType.DEFLATE] = True
        except Exception:
            compression_support[CompressionType.DEFLATE] = False
        
        # Other compression algorithms would be tested here
        compression_support[CompressionType.BROTLI] = False  # Requires brotli library
        compression_support[CompressionType.LZ4] = False     # Requires lz4 library
        compression_support[CompressionType.ZSTD] = False    # Requires zstd library
        
        logger.info(f"🗜️ Compression support: {sum(compression_support.values())}/{len(compression_support)} algorithms")
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """
        Get data from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if found, None otherwise
        """
        try:
            if key in self.cache:
                entry = self.cache[key]
                
                # Check TTL
                if entry.ttl:
                    age_seconds = (datetime.now() - entry.created_at).total_seconds()
                    if age_seconds > entry.ttl:
                        await self._remove_cache_entry(key)
                        self.metrics['cache_misses'] += 1
                        return None
                
                # Update access info
                entry.last_accessed = datetime.now()
                entry.access_count += 1
                
                # Update metrics
                self.metrics['cache_hits'] += 1
                self.metrics['bytes_saved_cache'] += entry.size
                
                logger.debug(f"💾 Cache hit: {key}")
                return entry.data
            else:
                self.metrics['cache_misses'] += 1
                logger.debug(f"💾 Cache miss: {key}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Cache get error: {e}")
            self.metrics['cache_misses'] += 1
            return None
    
    async def cache_set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """
        Store data in cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time to live in seconds
            
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            # Calculate data size
            data_str = json.dumps(data) if not isinstance(data, (str, bytes)) else str(data)
            data_size = len(data_str.encode('utf-8'))
            
            # Check if we need to make space
            if self.cache_size_bytes + data_size > self.max_cache_size_bytes:
                await self._enforce_cache_size_limit()
            
            # Remove existing entry if present
            if key in self.cache:
                await self._remove_cache_entry(key)
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                data=data,
                size=data_size,
                ttl=ttl or self.config.cache_ttl_seconds
            )
            
            # Store entry
            self.cache[key] = entry
            self.cache_size_bytes += data_size
            
            # Trigger cache handlers
            for handler in self.cache_handlers:
                try:
                    await handler("cache_set", key, data_size)
                except Exception as e:
                    logger.error(f"❌ Cache handler error: {e}")
            
            logger.debug(f"💾 Cache set: {key} ({data_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Cache set error: {e}")
            return False
    
    async def compress_data(self, data: bytes, algorithm: Optional[CompressionType] = None) -> CompressionResult:
        """
        Compress data using specified algorithm.
        
        Args:
            data: Data to compress
            algorithm: Compression algorithm (uses config default if None)
            
        Returns:
            CompressionResult with compression details
        """
        start_time = time.time()
        
        try:
            compression_algo = algorithm or self.config.compression_type
            original_size = len(data)
            
            # Skip compression for small data
            if original_size < self.config.compression_threshold:
                return CompressionResult(
                    original_size=original_size,
                    compressed_size=original_size,
                    compression_ratio=1.0,
                    algorithm=CompressionType.NONE,
                    compression_time=0.0,
                    data=data
                )
            
            # Perform compression
            if compression_algo == CompressionType.GZIP:
                compressed_data = gzip.compress(data)
            elif compression_algo == CompressionType.DEFLATE:
                compressed_data = zlib.compress(data)
            else:
                # Fallback to no compression
                compressed_data = data
                compression_algo = CompressionType.NONE
            
            compressed_size = len(compressed_data)
            compression_ratio = original_size / compressed_size if compressed_size > 0 else 1.0
            compression_time = time.time() - start_time
            
            # Update metrics
            bytes_saved = original_size - compressed_size
            if bytes_saved > 0:
                self.metrics['bytes_saved_compression'] += bytes_saved
            
            # Store optimization history
            self.optimization_history.append({
                'timestamp': datetime.now().isoformat(),
                'operation': 'compression',
                'algorithm': compression_algo.value,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'compression_time': compression_time
            })
            
            # Limit history size
            if len(self.optimization_history) > 1000:
                self.optimization_history = self.optimization_history[-500:]
            
            # Trigger compression handlers
            for handler in self.compression_handlers:
                try:
                    await handler("compression_completed", compression_algo, compression_ratio)
                except Exception as e:
                    logger.error(f"❌ Compression handler error: {e}")
            
            result = CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=compression_ratio,
                algorithm=compression_algo,
                compression_time=compression_time,
                data=compressed_data
            )
            
            logger.debug(f"🗜️ Compressed data: {original_size} → {compressed_size} bytes ({compression_ratio:.2f}x)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Compression failed: {e}")
            return CompressionResult(
                original_size=len(data),
                compressed_size=len(data),
                compression_ratio=1.0,
                algorithm=CompressionType.NONE,
                compression_time=time.time() - start_time,
                data=data
            )
    
    async def decompress_data(self, compressed_data: bytes, algorithm: CompressionType) -> bytes:
        """
        Decompress data using specified algorithm.
        
        Args:
            compressed_data: Compressed data
            algorithm: Compression algorithm used
            
        Returns:
            Decompressed data
        """
        try:
            if algorithm == CompressionType.GZIP:
                return gzip.decompress(compressed_data)
            elif algorithm == CompressionType.DEFLATE:
                return zlib.decompress(compressed_data)
            else:
                return compressed_data
                
        except Exception as e:
            logger.error(f"❌ Decompression failed: {e}")
            return compressed_data
    
    async def add_cdn_config(self, name: str, config: CDNConfig):
        """Add CDN configuration"""
        
        self.cdn_configs[name] = config
        
        if not self.active_cdn:
            self.active_cdn = name
        
        logger.info(f"🌐 CDN configuration added: {name} ({config.provider.value})")
    
    async def set_active_cdn(self, name: str) -> bool:
        """Set active CDN"""
        
        if name not in self.cdn_configs:
            return False
        
        self.active_cdn = name
        logger.info(f"🌐 Active CDN set to: {name}")
        return True
    
    async def optimize_request(self, url: str, data: Optional[bytes] = None) -> Dict[str, Any]:
        """
        Optimize a network request with caching and compression.
        
        Args:
            url: Request URL
            data: Request data
            
        Returns:
            Optimization result
        """
        start_time = time.time()
        
        try:
            # Generate cache key
            cache_key = hashlib.md5(url.encode()).hexdigest()
            
            # Check cache first
            cached_data = await self.cache_get(cache_key)
            if cached_data:
                return {
                    'url': url,
                    'cache_hit': True,
                    'data': cached_data,
                    'response_time': time.time() - start_time,
                    'bytes_saved': len(str(cached_data).encode('utf-8'))
                }
            
            # Simulate network request (in real implementation, make actual request)
            await asyncio.sleep(0.1)  # Simulate network delay
            
            # Generate mock response data
            response_data = {
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'data': f"Response data for {url}",
                'size': 1024
            }
            
            # Compress response if applicable
            if data and len(data) > self.config.compression_threshold:
                compression_result = await self.compress_data(data)
                response_data['compression'] = {
                    'algorithm': compression_result.algorithm.value,
                    'ratio': compression_result.compression_ratio,
                    'bytes_saved': compression_result.original_size - compression_result.compressed_size
                }
            
            # Cache the response
            await self.cache_set(cache_key, response_data)
            
            # Update metrics
            self.metrics['total_requests'] += 1
            response_time = time.time() - start_time
            
            # Update average response time
            total_requests = self.metrics['total_requests']
            current_avg = self.metrics['average_response_time']
            self.metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
            
            return {
                'url': url,
                'cache_hit': False,
                'data': response_data,
                'response_time': response_time,
                'cached': True
            }
            
        except Exception as e:
            logger.error(f"❌ Request optimization failed: {e}")
            return {
                'url': url,
                'cache_hit': False,
                'error': str(e),
                'response_time': time.time() - start_time
            }
    
    def register_cache_handler(self, handler: Callable):
        """Register cache event handler"""
        self.cache_handlers.append(handler)
        logger.info("📡 Registered cache handler")
    
    def register_compression_handler(self, handler: Callable):
        """Register compression event handler"""
        self.compression_handlers.append(handler)
        logger.info("📡 Registered compression handler")
    
    def register_cdn_handler(self, handler: Callable):
        """Register CDN event handler"""
        self.cdn_handlers.append(handler)
        logger.info("📡 Registered CDN handler")
    
    def get_optimization_metrics(self) -> Dict[str, Any]:
        """Get network optimization metrics"""
        
        return {
            **self.metrics,
            'cache_size_mb': self.cache_size_bytes / (1024 * 1024),
            'cache_entries': len(self.cache),
            'cache_utilization': (self.cache_size_bytes / self.max_cache_size_bytes) * 100,
            'optimization_history_size': len(self.optimization_history)
        }
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get cache information"""
        
        return {
            'strategy': self.config.cache_strategy.value,
            'size_mb': self.cache_size_bytes / (1024 * 1024),
            'max_size_mb': self.config.max_cache_size_mb,
            'entries': len(self.cache),
            'hit_ratio': self.metrics['cache_hit_ratio'],
            'ttl_seconds': self.config.cache_ttl_seconds
        }
    
    def get_cdn_info(self) -> Dict[str, Any]:
        """Get CDN information"""
        
        cdn_info = {}
        for name, config in self.cdn_configs.items():
            cdn_info[name] = {
                'provider': config.provider.value,
                'endpoint': config.endpoint,
                'cache_ttl': config.cache_ttl,
                'compression_enabled': config.compression_enabled,
                'active': name == self.active_cdn
            }
        
        return cdn_info
    
    def get_optimization_info(self) -> Dict[str, Any]:
        """Get comprehensive optimization information"""
        
        return {
            'configuration': {
                'cache_strategy': self.config.cache_strategy.value,
                'compression_type': self.config.compression_type.value,
                'optimization_level': self.config.optimization_level.value,
                'compression_threshold': self.config.compression_threshold
            },
            'metrics': self.get_optimization_metrics(),
            'cache': self.get_cache_info(),
            'cdn': self.get_cdn_info(),
            'recent_optimizations': self.optimization_history[-10:] if self.optimization_history else []
        }
    
    async def shutdown(self):
        """Shutdown network optimization system"""
        
        # Stop background tasks
        tasks = [self.cache_cleanup_task, self.metrics_task]
        
        for task in tasks:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Clear cache
        self.cache.clear()
        self.cache_size_bytes = 0
        
        logger.info("📈 Network Optimization system shutdown complete")
