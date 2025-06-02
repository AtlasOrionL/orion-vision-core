"""
Performance Optimizer for Orion Vision Core

This module provides comprehensive system optimization and performance tuning.
Part of Sprint 9.2 Advanced Features development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.2 - Advanced Features & Enhanced Capabilities
"""

import time
import threading
import gc
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType
from ...monitoring.core.performance_monitor import PerformanceMonitor
from ..cache.cache_manager import CacheManager


class OptimizationLevel(Enum):
    """Optimization level enumeration"""
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    MAXIMUM = "maximum"


class OptimizationType(Enum):
    """Optimization type enumeration"""
    MEMORY = "memory"
    CPU = "cpu"
    IO = "io"
    NETWORK = "network"
    CACHE = "cache"
    GARBAGE_COLLECTION = "garbage_collection"


@dataclass
class OptimizationRule:
    """Optimization rule data structure"""
    name: str
    optimization_type: OptimizationType
    condition: Callable[[], bool]
    action: Callable[[], Any]
    level: OptimizationLevel = OptimizationLevel.BALANCED
    cooldown: float = 60.0  # seconds
    last_executed: float = 0.0
    execution_count: int = 0
    success_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def can_execute(self) -> bool:
        """Check if rule can be executed"""
        return time.time() - self.last_executed >= self.cooldown
    
    def should_execute(self) -> bool:
        """Check if rule should be executed"""
        try:
            return self.can_execute() and self.condition()
        except:
            return False


class PerformanceOptimizer:
    """
    Comprehensive performance optimization system
    
    Provides automatic performance tuning, resource optimization,
    and system performance monitoring with adaptive optimization.
    """
    
    def __init__(self, performance_monitor: Optional[PerformanceMonitor] = None,
                 cache_manager: Optional[CacheManager] = None,
                 metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize performance optimizer"""
        self.logger = logger or AgentLogger("performance_optimizer")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        self.performance_monitor = performance_monitor or PerformanceMonitor(self.metrics_collector, self.logger)
        self.cache_manager = cache_manager or CacheManager(self.metrics_collector, self.logger)
        
        # Optimization configuration
        self.optimization_level = OptimizationLevel.BALANCED
        self.auto_optimization_enabled = True
        self.optimization_interval = 30.0  # seconds
        
        # Optimization rules
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        self.optimization_history: deque = deque(maxlen=1000)
        
        # Performance baselines
        self.performance_baselines: Dict[str, float] = {}
        self.performance_targets: Dict[str, float] = {}
        
        # Optimization state
        self.optimizing = False
        self.optimization_thread = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.optimizer_stats = {
            'total_optimizations': 0,
            'successful_optimizations': 0,
            'failed_optimizations': 0,
            'memory_optimizations': 0,
            'cpu_optimizations': 0,
            'cache_optimizations': 0,
            'gc_runs': 0,
            'performance_improvements': 0
        }
        
        # Setup default optimization rules
        self._setup_default_rules()
        
        self.logger.info("Performance Optimizer initialized")
    
    def start_optimization(self):
        """Start automatic optimization"""
        if self.optimizing:
            self.logger.warning("Performance optimization already running")
            return
        
        self.optimizing = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        
        self.logger.info("Performance optimization started", interval=self.optimization_interval)
    
    def stop_optimization(self):
        """Stop automatic optimization"""
        if not self.optimizing:
            self.logger.debug("Performance optimization not running")
            return
        
        self.optimizing = False
        
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5.0)
        
        self.logger.info("Performance optimization stopped")
    
    def add_optimization_rule(self, rule: OptimizationRule):
        """Add optimization rule"""
        with self._lock:
            self.optimization_rules[rule.name] = rule
            
            self.logger.info(
                "Optimization rule added",
                rule_name=rule.name,
                optimization_type=rule.optimization_type.value,
                level=rule.level.value
            )
    
    def remove_optimization_rule(self, rule_name: str) -> bool:
        """Remove optimization rule"""
        with self._lock:
            if rule_name in self.optimization_rules:
                del self.optimization_rules[rule_name]
                
                self.logger.info("Optimization rule removed", rule_name=rule_name)
                return True
            
            return False
    
    def run_optimization(self, optimization_types: Optional[List[OptimizationType]] = None) -> Dict[str, Any]:
        """Run optimization manually"""
        try:
            with self._lock:
                start_time = time.time()
                results = {
                    'executed_rules': [],
                    'successful_rules': [],
                    'failed_rules': [],
                    'performance_before': {},
                    'performance_after': {},
                    'improvements': {}
                }
                
                # Capture performance before optimization
                results['performance_before'] = self._capture_performance_snapshot()
                
                # Filter rules by type if specified
                rules_to_run = []
                for rule in self.optimization_rules.values():
                    if optimization_types is None or rule.optimization_type in optimization_types:
                        if rule.should_execute():
                            rules_to_run.append(rule)
                
                # Execute optimization rules
                for rule in rules_to_run:
                    try:
                        rule.execution_count += 1
                        rule.last_executed = time.time()
                        
                        # Execute rule action
                        result = rule.action()
                        
                        rule.success_count += 1
                        results['executed_rules'].append(rule.name)
                        results['successful_rules'].append(rule.name)
                        
                        # Record optimization
                        self.optimization_history.append({
                            'rule_name': rule.name,
                            'optimization_type': rule.optimization_type.value,
                            'timestamp': time.time(),
                            'success': True,
                            'result': result
                        })
                        
                        self.optimizer_stats['successful_optimizations'] += 1
                        self.optimizer_stats[f'{rule.optimization_type.value}_optimizations'] += 1
                        
                        self.logger.debug(
                            "Optimization rule executed successfully",
                            rule_name=rule.name,
                            optimization_type=rule.optimization_type.value
                        )
                        
                    except Exception as e:
                        results['executed_rules'].append(rule.name)
                        results['failed_rules'].append(rule.name)
                        
                        # Record failed optimization
                        self.optimization_history.append({
                            'rule_name': rule.name,
                            'optimization_type': rule.optimization_type.value,
                            'timestamp': time.time(),
                            'success': False,
                            'error': str(e)
                        })
                        
                        self.optimizer_stats['failed_optimizations'] += 1
                        
                        self.logger.warning(
                            "Optimization rule failed",
                            rule_name=rule.name,
                            optimization_type=rule.optimization_type.value,
                            error=str(e)
                        )
                
                # Capture performance after optimization
                results['performance_after'] = self._capture_performance_snapshot()
                
                # Calculate improvements
                results['improvements'] = self._calculate_improvements(
                    results['performance_before'],
                    results['performance_after']
                )
                
                # Update statistics
                self.optimizer_stats['total_optimizations'] += 1
                if results['improvements']:
                    self.optimizer_stats['performance_improvements'] += 1
                
                execution_time = time.time() - start_time
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="optimizer.optimization_run",
                    value=execution_time * 1000,  # ms
                    metric_type=MetricType.TIMER,
                    tags={
                        'rules_executed': str(len(results['executed_rules'])),
                        'successful': str(len(results['successful_rules'])),
                        'failed': str(len(results['failed_rules']))
                    }
                )
                
                self.logger.info(
                    "Optimization run completed",
                    execution_time_ms=f"{execution_time * 1000:.2f}",
                    rules_executed=len(results['executed_rules']),
                    successful=len(results['successful_rules']),
                    failed=len(results['failed_rules'])
                )
                
                return results
                
        except Exception as e:
            self.logger.error("Optimization run failed", error=str(e))
            return {'error': str(e)}
    
    def set_performance_baseline(self, metric_name: str, baseline_value: float):
        """Set performance baseline for optimization"""
        self.performance_baselines[metric_name] = baseline_value
        
        self.logger.info(
            "Performance baseline set",
            metric_name=metric_name,
            baseline_value=baseline_value
        )
    
    def set_performance_target(self, metric_name: str, target_value: float):
        """Set performance target for optimization"""
        self.performance_targets[metric_name] = target_value
        
        self.logger.info(
            "Performance target set",
            metric_name=metric_name,
            target_value=target_value
        )
    
    def _setup_default_rules(self):
        """Setup default optimization rules"""
        # Memory optimization rule
        memory_rule = OptimizationRule(
            name="memory_cleanup",
            optimization_type=OptimizationType.MEMORY,
            condition=lambda: self._check_memory_usage() > 80.0,  # > 80% memory usage
            action=self._optimize_memory,
            level=OptimizationLevel.BALANCED,
            cooldown=60.0
        )
        self.add_optimization_rule(memory_rule)
        
        # Garbage collection rule
        gc_rule = OptimizationRule(
            name="garbage_collection",
            optimization_type=OptimizationType.GARBAGE_COLLECTION,
            condition=lambda: self._check_gc_needed(),
            action=self._run_garbage_collection,
            level=OptimizationLevel.CONSERVATIVE,
            cooldown=30.0
        )
        self.add_optimization_rule(gc_rule)
        
        # Cache optimization rule
        cache_rule = OptimizationRule(
            name="cache_optimization",
            optimization_type=OptimizationType.CACHE,
            condition=lambda: self._check_cache_efficiency() < 50.0,  # < 50% hit rate
            action=self._optimize_cache,
            level=OptimizationLevel.BALANCED,
            cooldown=120.0
        )
        self.add_optimization_rule(cache_rule)
    
    def _optimization_loop(self):
        """Main optimization loop"""
        while self.optimizing:
            try:
                if self.auto_optimization_enabled:
                    self.run_optimization()
                
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                self.logger.error("Optimization loop error", error=str(e))
                time.sleep(5.0)  # Error recovery delay
    
    def _capture_performance_snapshot(self) -> Dict[str, float]:
        """Capture current performance metrics"""
        try:
            import psutil
            
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Process metrics
            process = psutil.Process()
            process_memory_mb = process.memory_info().rss / 1024 / 1024
            process_cpu_percent = process.cpu_percent()
            
            # Cache metrics
            cache_stats = self.cache_manager.get_cache_stats()
            cache_hit_rate = cache_stats.get('hit_rate_percent', 0)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'process_memory_mb': process_memory_mb,
                'process_cpu_percent': process_cpu_percent,
                'cache_hit_rate': cache_hit_rate
            }
            
        except Exception as e:
            self.logger.warning("Failed to capture performance snapshot", error=str(e))
            return {}
    
    def _calculate_improvements(self, before: Dict[str, float], after: Dict[str, float]) -> Dict[str, float]:
        """Calculate performance improvements"""
        improvements = {}
        
        for metric, before_value in before.items():
            if metric in after:
                after_value = after[metric]
                
                # For metrics where lower is better (CPU, memory usage)
                if metric in ['cpu_percent', 'memory_percent', 'process_cpu_percent']:
                    if before_value > 0:
                        improvement = ((before_value - after_value) / before_value) * 100
                        if improvement > 0:
                            improvements[metric] = improvement
                
                # For metrics where higher is better (cache hit rate)
                elif metric in ['cache_hit_rate']:
                    if before_value > 0:
                        improvement = ((after_value - before_value) / before_value) * 100
                        if improvement > 0:
                            improvements[metric] = improvement
        
        return improvements
    
    def _check_memory_usage(self) -> float:
        """Check current memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0.0
    
    def _check_gc_needed(self) -> bool:
        """Check if garbage collection is needed"""
        try:
            import gc
            # Simple heuristic: run GC if there are many objects
            return len(gc.get_objects()) > 10000
        except:
            return False
    
    def _check_cache_efficiency(self) -> float:
        """Check cache hit rate efficiency"""
        try:
            cache_stats = self.cache_manager.get_cache_stats()
            return cache_stats.get('hit_rate_percent', 0)
        except:
            return 0.0
    
    def _optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage"""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            
            # Clear cache if memory is critically low
            memory_usage = self._check_memory_usage()
            if memory_usage > 90:
                self.cache_manager.clear()
            
            self.optimizer_stats['memory_optimizations'] += 1
            
            return {
                'action': 'memory_optimization',
                'objects_collected': collected,
                'cache_cleared': memory_usage > 90
            }
            
        except Exception as e:
            raise Exception(f"Memory optimization failed: {e}")
    
    def _run_garbage_collection(self) -> Dict[str, Any]:
        """Run garbage collection"""
        try:
            import gc
            
            # Run garbage collection
            collected = gc.collect()
            
            self.optimizer_stats['gc_runs'] += 1
            
            return {
                'action': 'garbage_collection',
                'objects_collected': collected
            }
            
        except Exception as e:
            raise Exception(f"Garbage collection failed: {e}")
    
    def _optimize_cache(self) -> Dict[str, Any]:
        """Optimize cache performance"""
        try:
            # Warm frequently accessed cache entries
            self.cache_manager.warm_cache()
            
            self.optimizer_stats['cache_optimizations'] += 1
            
            return {
                'action': 'cache_optimization',
                'cache_warmed': True
            }
            
        except Exception as e:
            raise Exception(f"Cache optimization failed: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        with self._lock:
            return {
                'optimizing': self.optimizing,
                'optimization_level': self.optimization_level.value,
                'auto_optimization_enabled': self.auto_optimization_enabled,
                'optimization_interval': self.optimization_interval,
                'total_rules': len(self.optimization_rules),
                'optimization_history_size': len(self.optimization_history),
                'performance_baselines_count': len(self.performance_baselines),
                'performance_targets_count': len(self.performance_targets),
                'stats': self.optimizer_stats.copy()
            }
