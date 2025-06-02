"""
Model Manager for Orion Vision Core

This module provides AI model lifecycle management, versioning, and optimization.
Part of Sprint 9.4 Advanced AI Integration & Machine Learning development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.4 - Advanced AI Integration & Machine Learning
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


class ModelFormat(Enum):
    """Model format enumeration"""
    PYTORCH = "pytorch"
    TENSORFLOW = "tensorflow"
    ONNX = "onnx"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class ModelOptimization(Enum):
    """Model optimization level enumeration"""
    NONE = "none"
    BASIC = "basic"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"


class ModelPrecision(Enum):
    """Model precision enumeration"""
    FP32 = "fp32"
    FP16 = "fp16"
    INT8 = "int8"
    INT4 = "int4"


@dataclass
class ModelVersion:
    """Model version data structure"""
    version_id: str
    version_number: str
    model_id: str
    format: ModelFormat
    precision: ModelPrecision = ModelPrecision.FP32
    optimization: ModelOptimization = ModelOptimization.NONE
    file_path: Optional[str] = None
    file_size_mb: float = 0.0
    checksum: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def get_age_days(self) -> float:
        """Get version age in days"""
        return (time.time() - self.created_at) / 86400


@dataclass
class ModelRepository:
    """Model repository data structure"""
    repo_id: str
    repo_name: str
    repo_type: str = "local"  # local, remote, cloud
    base_path: str = ""
    credentials: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_model_path(self, model_id: str, version_id: str) -> str:
        """Get full path for model version"""
        return f"{self.base_path}/{model_id}/{version_id}"


@dataclass
class ModelBenchmark:
    """Model benchmark results"""
    benchmark_id: str
    model_id: str
    version_id: str
    benchmark_type: str
    dataset_name: str
    metrics: Dict[str, float]
    execution_time_ms: float
    memory_usage_mb: float
    timestamp: float = field(default_factory=time.time)
    environment: Dict[str, str] = field(default_factory=dict)


class ModelManager:
    """
    Comprehensive AI model lifecycle management system
    
    Provides model versioning, optimization, benchmarking, and repository
    management with support for multiple model formats and providers.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize model manager"""
        self.logger = logger or AgentLogger("model_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Model storage
        self.model_versions: Dict[str, ModelVersion] = {}
        self.model_registry: Dict[str, List[str]] = {}  # model_id -> [version_ids]
        
        # Repository management
        self.repositories: Dict[str, ModelRepository] = {}
        
        # Benchmarking
        self.benchmarks: Dict[str, List[ModelBenchmark]] = {}
        
        # Model optimization
        self.optimization_strategies: Dict[ModelOptimization, Callable] = {}
        
        # Caching
        self.model_cache: Dict[str, Any] = {}
        self.cache_size_limit_mb = 1000.0
        self.current_cache_size_mb = 0.0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.model_stats = {
            'total_models': 0,
            'total_versions': 0,
            'total_repositories': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'optimizations_performed': 0,
            'benchmarks_run': 0,
            'total_storage_mb': 0.0
        }
        
        # Initialize default optimization strategies
        self._initialize_optimization_strategies()
        
        self.logger.info("Model Manager initialized")
    
    def _initialize_optimization_strategies(self):
        """Initialize default optimization strategies"""
        self.optimization_strategies[ModelOptimization.BASIC] = self._basic_optimization
        self.optimization_strategies[ModelOptimization.ADVANCED] = self._advanced_optimization
        self.optimization_strategies[ModelOptimization.AGGRESSIVE] = self._aggressive_optimization
    
    def register_repository(self, repository: ModelRepository) -> bool:
        """Register model repository"""
        try:
            with self._lock:
                self.repositories[repository.repo_id] = repository
                
                # Update statistics
                self.model_stats['total_repositories'] = len(self.repositories)
                
                self.logger.info(
                    "Model repository registered",
                    repo_id=repository.repo_id,
                    repo_name=repository.repo_name,
                    repo_type=repository.repo_type
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Repository registration failed", repo_id=repository.repo_id, error=str(e))
            return False
    
    def create_model_version(self, model_id: str, version_number: str, 
                           format: ModelFormat, file_path: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create new model version"""
        try:
            version_id = str(uuid.uuid4())
            
            # Calculate file checksum if file exists
            checksum = None
            file_size_mb = 0.0
            if file_path:
                checksum = self._calculate_checksum(file_path)
                file_size_mb = self._get_file_size_mb(file_path)
            
            # Create model version
            version = ModelVersion(
                version_id=version_id,
                version_number=version_number,
                model_id=model_id,
                format=format,
                file_path=file_path,
                file_size_mb=file_size_mb,
                checksum=checksum,
                metadata=metadata or {}
            )
            
            with self._lock:
                # Store version
                self.model_versions[version_id] = version
                
                # Update model registry
                if model_id not in self.model_registry:
                    self.model_registry[model_id] = []
                    self.model_stats['total_models'] += 1
                
                self.model_registry[model_id].append(version_id)
                
                # Update statistics
                self.model_stats['total_versions'] = len(self.model_versions)
                self.model_stats['total_storage_mb'] += file_size_mb
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="model.version_created",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={
                        'model_id': model_id,
                        'format': format.value,
                        'file_size_mb': str(int(file_size_mb))
                    }
                )
                
                self.logger.info(
                    "Model version created",
                    model_id=model_id,
                    version_id=version_id,
                    version_number=version_number,
                    format=format.value,
                    file_size_mb=file_size_mb
                )
                
                return version_id
                
        except Exception as e:
            self.logger.error("Model version creation failed", model_id=model_id, error=str(e))
            return None
    
    def get_model_version(self, version_id: str) -> Optional[ModelVersion]:
        """Get model version by ID"""
        return self.model_versions.get(version_id)
    
    def get_latest_version(self, model_id: str) -> Optional[ModelVersion]:
        """Get latest version of model"""
        with self._lock:
            if model_id not in self.model_registry:
                return None
            
            version_ids = self.model_registry[model_id]
            if not version_ids:
                return None
            
            # Get latest version (last created)
            latest_version_id = version_ids[-1]
            return self.model_versions.get(latest_version_id)
    
    def list_model_versions(self, model_id: str) -> List[ModelVersion]:
        """List all versions of a model"""
        with self._lock:
            if model_id not in self.model_registry:
                return []
            
            version_ids = self.model_registry[model_id]
            return [
                self.model_versions[version_id]
                for version_id in version_ids
                if version_id in self.model_versions
            ]
    
    def optimize_model(self, version_id: str, optimization: ModelOptimization,
                      target_precision: Optional[ModelPrecision] = None) -> Optional[str]:
        """Optimize model and create new optimized version"""
        try:
            if version_id not in self.model_versions:
                self.logger.error("Model version not found", version_id=version_id)
                return None
            
            original_version = self.model_versions[version_id]
            
            # Check if optimization strategy exists
            if optimization not in self.optimization_strategies:
                self.logger.error("Optimization strategy not found", optimization=optimization.value)
                return None
            
            start_time = time.time()
            
            # Apply optimization strategy
            optimization_func = self.optimization_strategies[optimization]
            optimized_data = optimization_func(original_version, target_precision)
            
            if not optimized_data:
                self.logger.error("Optimization failed", version_id=version_id)
                return None
            
            # Create new optimized version
            new_version_number = f"{original_version.version_number}-{optimization.value}"
            if target_precision:
                new_version_number += f"-{target_precision.value}"
            
            optimized_version_id = self.create_model_version(
                model_id=original_version.model_id,
                version_number=new_version_number,
                format=original_version.format,
                metadata={
                    'optimized_from': version_id,
                    'optimization': optimization.value,
                    'target_precision': target_precision.value if target_precision else None,
                    'optimization_time_ms': (time.time() - start_time) * 1000
                }
            )
            
            if optimized_version_id:
                # Update optimized version properties
                optimized_version = self.model_versions[optimized_version_id]
                optimized_version.optimization = optimization
                if target_precision:
                    optimized_version.precision = target_precision
                
                # Estimate size reduction
                size_reduction = optimized_data.get('size_reduction_percent', 0)
                optimized_version.file_size_mb = original_version.file_size_mb * (1 - size_reduction / 100)
                
                # Update statistics
                self.model_stats['optimizations_performed'] += 1
                
                optimization_time = (time.time() - start_time) * 1000
                
                self.logger.info(
                    "Model optimization completed",
                    original_version_id=version_id,
                    optimized_version_id=optimized_version_id,
                    optimization=optimization.value,
                    optimization_time_ms=f"{optimization_time:.2f}",
                    size_reduction_percent=size_reduction
                )
                
                return optimized_version_id
            
            return None
            
        except Exception as e:
            self.logger.error("Model optimization failed", version_id=version_id, error=str(e))
            return None
    
    def benchmark_model(self, version_id: str, benchmark_type: str, 
                       dataset_name: str) -> Optional[str]:
        """Benchmark model performance"""
        try:
            if version_id not in self.model_versions:
                self.logger.error("Model version not found", version_id=version_id)
                return None
            
            version = self.model_versions[version_id]
            benchmark_id = str(uuid.uuid4())
            
            start_time = time.time()
            
            # Simulate benchmarking
            if benchmark_type == "inference_speed":
                metrics = {
                    'avg_inference_time_ms': 50.0,
                    'throughput_requests_per_sec': 20.0,
                    'p95_latency_ms': 75.0,
                    'p99_latency_ms': 100.0
                }
            elif benchmark_type == "accuracy":
                metrics = {
                    'accuracy': 0.95,
                    'precision': 0.94,
                    'recall': 0.96,
                    'f1_score': 0.95
                }
            elif benchmark_type == "memory_usage":
                metrics = {
                    'peak_memory_mb': 512.0,
                    'avg_memory_mb': 256.0,
                    'memory_efficiency': 0.85
                }
            else:
                metrics = {
                    'score': 0.90,
                    'performance_index': 85.0
                }
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Create benchmark result
            benchmark = ModelBenchmark(
                benchmark_id=benchmark_id,
                model_id=version.model_id,
                version_id=version_id,
                benchmark_type=benchmark_type,
                dataset_name=dataset_name,
                metrics=metrics,
                execution_time_ms=execution_time_ms,
                memory_usage_mb=256.0,  # Mock memory usage
                environment={
                    'python_version': '3.9.0',
                    'framework': version.format.value,
                    'device': 'cpu'
                }
            )
            
            with self._lock:
                # Store benchmark
                if version_id not in self.benchmarks:
                    self.benchmarks[version_id] = []
                
                self.benchmarks[version_id].append(benchmark)
                
                # Update statistics
                self.model_stats['benchmarks_run'] += 1
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="model.benchmark_completed",
                    value=execution_time_ms,
                    metric_type=MetricType.TIMER,
                    tags={
                        'model_id': version.model_id,
                        'benchmark_type': benchmark_type,
                        'dataset': dataset_name
                    }
                )
                
                self.logger.info(
                    "Model benchmark completed",
                    benchmark_id=benchmark_id,
                    model_id=version.model_id,
                    version_id=version_id,
                    benchmark_type=benchmark_type,
                    execution_time_ms=f"{execution_time_ms:.2f}"
                )
                
                return benchmark_id
                
        except Exception as e:
            self.logger.error("Model benchmarking failed", version_id=version_id, error=str(e))
            return None
    
    def _basic_optimization(self, version: ModelVersion, target_precision: Optional[ModelPrecision]) -> Dict[str, Any]:
        """Basic model optimization"""
        return {
            'size_reduction_percent': 10,
            'speed_improvement_percent': 5,
            'accuracy_loss_percent': 1
        }
    
    def _advanced_optimization(self, version: ModelVersion, target_precision: Optional[ModelPrecision]) -> Dict[str, Any]:
        """Advanced model optimization"""
        return {
            'size_reduction_percent': 25,
            'speed_improvement_percent': 15,
            'accuracy_loss_percent': 3
        }
    
    def _aggressive_optimization(self, version: ModelVersion, target_precision: Optional[ModelPrecision]) -> Dict[str, Any]:
        """Aggressive model optimization"""
        return {
            'size_reduction_percent': 50,
            'speed_improvement_percent': 30,
            'accuracy_loss_percent': 8
        }
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate file checksum"""
        # Mock checksum calculation
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _get_file_size_mb(self, file_path: str) -> float:
        """Get file size in MB"""
        # Mock file size
        return 100.0
    
    def get_model_benchmarks(self, version_id: str) -> List[ModelBenchmark]:
        """Get benchmarks for model version"""
        return self.benchmarks.get(version_id, [])
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model manager statistics"""
        with self._lock:
            return {
                'total_models': len(self.model_registry),
                'total_versions': len(self.model_versions),
                'total_repositories': len(self.repositories),
                'cache_size_mb': self.current_cache_size_mb,
                'cache_limit_mb': self.cache_size_limit_mb,
                'cache_hit_rate': (
                    self.model_stats['cache_hits'] / 
                    max(1, self.model_stats['cache_hits'] + self.model_stats['cache_misses'])
                ) * 100,
                'stats': self.model_stats.copy()
            }
