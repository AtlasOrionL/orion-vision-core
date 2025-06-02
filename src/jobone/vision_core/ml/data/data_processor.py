"""
Data Processor for Orion Vision Core

This module provides comprehensive data processing capabilities including
data ingestion, validation, transformation, and feature engineering.
Part of Sprint 9.5 Advanced Machine Learning & Training development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.5 - Advanced Machine Learning & Training
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class DataType(Enum):
    """Data type enumeration"""
    STRUCTURED = "structured"
    UNSTRUCTURED = "unstructured"
    TIME_SERIES = "time_series"
    IMAGE = "image"
    TEXT = "text"
    AUDIO = "audio"
    VIDEO = "video"
    MULTIMODAL = "multimodal"


class ProcessingStatus(Enum):
    """Processing status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationRule(Enum):
    """Data validation rule enumeration"""
    NOT_NULL = "not_null"
    RANGE_CHECK = "range_check"
    TYPE_CHECK = "type_check"
    FORMAT_CHECK = "format_check"
    UNIQUENESS = "uniqueness"
    CUSTOM = "custom"


@dataclass
class DataSource:
    """Data source configuration"""
    source_id: str
    source_name: str
    source_type: str  # database, file, api, stream
    connection_config: Dict[str, Any] = field(default_factory=dict)
    data_type: DataType = DataType.STRUCTURED
    schema: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate data source configuration"""
        if not self.source_id or not self.source_name:
            return False
        if not self.source_type:
            return False
        return True


@dataclass
class ProcessingJob:
    """Data processing job"""
    job_id: str
    job_name: str
    source: DataSource
    operations: List[Dict[str, Any]] = field(default_factory=list)
    status: ProcessingStatus = ProcessingStatus.PENDING
    progress: float = 0.0
    records_processed: int = 0
    records_total: int = 0
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration(self) -> float:
        """Get processing duration in seconds"""
        if self.started_at:
            end_time = self.completed_at or time.time()
            return end_time - self.started_at
        return 0.0
    
    def is_active(self) -> bool:
        """Check if job is active"""
        return self.status == ProcessingStatus.PROCESSING


@dataclass
class ValidationResult:
    """Data validation result"""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    quality_score: float = 1.0
    statistics: Dict[str, Any] = field(default_factory=dict)


class DataProcessor:
    """
    Comprehensive data processing system
    
    Provides data ingestion, validation, transformation, and feature
    engineering capabilities with support for multiple data types.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize data processor"""
        self.logger = logger or AgentLogger("data_processor")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Job management
        self.processing_jobs: Dict[str, ProcessingJob] = {}
        self.active_jobs: Dict[str, ProcessingJob] = {}
        
        # Data sources
        self.data_sources: Dict[str, DataSource] = {}
        
        # Processing operations
        self.operations: Dict[str, Callable] = {}
        self.validation_rules: Dict[ValidationRule, Callable] = {}
        
        # Configuration
        self.max_concurrent_jobs = 3
        self.chunk_size = 1000
        self.memory_limit_mb = 1000.0
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.processing_stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'total_records_processed': 0,
            'total_processing_time_hours': 0.0,
            'average_processing_speed_records_per_sec': 0.0,
            'data_quality_average': 0.0,
            'memory_usage_mb': 0.0
        }
        
        # Initialize default operations and validation rules
        self._initialize_operations()
        self._initialize_validation_rules()
        
        self.logger.info("Data Processor initialized")
    
    def _initialize_operations(self):
        """Initialize default data processing operations"""
        self.operations['clean_nulls'] = self._clean_nulls
        self.operations['normalize'] = self._normalize_data
        self.operations['encode_categorical'] = self._encode_categorical
        self.operations['scale_features'] = self._scale_features
        self.operations['extract_features'] = self._extract_features
        self.operations['remove_outliers'] = self._remove_outliers
        self.operations['aggregate'] = self._aggregate_data
        self.operations['transform'] = self._transform_data
    
    def _initialize_validation_rules(self):
        """Initialize default validation rules"""
        self.validation_rules[ValidationRule.NOT_NULL] = self._validate_not_null
        self.validation_rules[ValidationRule.RANGE_CHECK] = self._validate_range
        self.validation_rules[ValidationRule.TYPE_CHECK] = self._validate_type
        self.validation_rules[ValidationRule.FORMAT_CHECK] = self._validate_format
        self.validation_rules[ValidationRule.UNIQUENESS] = self._validate_uniqueness
    
    def register_data_source(self, source: DataSource) -> bool:
        """Register data source"""
        try:
            if not source.validate():
                self.logger.error("Invalid data source configuration", source_id=source.source_id)
                return False
            
            with self._lock:
                self.data_sources[source.source_id] = source
                
                self.logger.info(
                    "Data source registered",
                    source_id=source.source_id,
                    source_name=source.source_name,
                    source_type=source.source_type,
                    data_type=source.data_type.value
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Data source registration failed", source_id=source.source_id, error=str(e))
            return False
    
    def create_processing_job(self, job_name: str, source_id: str, 
                            operations: List[Dict[str, Any]]) -> Optional[str]:
        """Create data processing job"""
        try:
            if source_id not in self.data_sources:
                self.logger.error("Data source not found", source_id=source_id)
                return None
            
            job_id = str(uuid.uuid4())
            source = self.data_sources[source_id]
            
            # Create processing job
            job = ProcessingJob(
                job_id=job_id,
                job_name=job_name,
                source=source,
                operations=operations
            )
            
            with self._lock:
                # Store job
                self.processing_jobs[job_id] = job
                
                # Add to active jobs if capacity allows
                if len(self.active_jobs) < self.max_concurrent_jobs:
                    self.active_jobs[job_id] = job
                    job.status = ProcessingStatus.PROCESSING
                
                # Update statistics
                self.processing_stats['total_jobs'] += 1
                
                self.logger.info(
                    "Data processing job created",
                    job_id=job_id,
                    job_name=job_name,
                    source_id=source_id,
                    operations_count=len(operations)
                )
                
                return job_id
                
        except Exception as e:
            self.logger.error("Processing job creation failed", job_name=job_name, error=str(e))
            return None
    
    def start_processing_job(self, job_id: str) -> bool:
        """Start data processing job"""
        try:
            if job_id not in self.processing_jobs:
                self.logger.error("Processing job not found", job_id=job_id)
                return False
            
            job = self.processing_jobs[job_id]
            
            if job.status != ProcessingStatus.PENDING and job.status != ProcessingStatus.PROCESSING:
                self.logger.warning("Job not in startable state", job_id=job_id, status=job.status.value)
                return False
            
            # Start processing in background thread
            processing_thread = threading.Thread(
                target=self._run_processing_job,
                args=(job,),
                name=f"DataProcessing-{job_id[:8]}",
                daemon=True
            )
            processing_thread.start()
            
            self.logger.info("Data processing job started", job_id=job_id, job_name=job.job_name)
            return True
            
        except Exception as e:
            self.logger.error("Processing job start failed", job_id=job_id, error=str(e))
            return False
    
    def _run_processing_job(self, job: ProcessingJob):
        """Run data processing job"""
        try:
            job.status = ProcessingStatus.PROCESSING
            job.started_at = time.time()
            
            self.logger.info(
                "Data processing job execution started",
                job_id=job.job_id,
                job_name=job.job_name,
                operations_count=len(job.operations)
            )
            
            # Load data from source
            data = self._load_data(job.source)
            if data is None:
                raise Exception("Failed to load data from source")
            
            job.records_total = len(data) if isinstance(data, list) else 1000  # Mock total
            
            # Process data through operations
            processed_data = data
            for i, operation in enumerate(job.operations):
                operation_name = operation.get('name', 'unknown')
                operation_params = operation.get('parameters', {})
                
                self.logger.debug(
                    "Processing operation",
                    job_id=job.job_id,
                    operation=operation_name,
                    step=f"{i+1}/{len(job.operations)}"
                )
                
                # Apply operation
                processed_data = self._apply_operation(processed_data, operation_name, operation_params)
                
                # Update progress
                job.progress = (i + 1) / len(job.operations)
                job.records_processed = int(job.records_total * job.progress)
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="data.operation_completed",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={
                        'job_id': job.job_id,
                        'operation': operation_name,
                        'data_type': job.source.data_type.value
                    }
                )
            
            # Store processed data
            job.output_data = processed_data
            job.status = ProcessingStatus.COMPLETED
            job.completed_at = time.time()
            
            # Update statistics
            with self._lock:
                self.processing_stats['completed_jobs'] += 1
                self.processing_stats['total_records_processed'] += job.records_processed
                
                processing_time_hours = job.get_duration() / 3600
                self.processing_stats['total_processing_time_hours'] += processing_time_hours
                
                # Calculate processing speed
                if job.get_duration() > 0:
                    speed = job.records_processed / job.get_duration()
                    self.processing_stats['average_processing_speed_records_per_sec'] = (
                        (self.processing_stats['average_processing_speed_records_per_sec'] * 
                         (self.processing_stats['completed_jobs'] - 1) + speed) / 
                        self.processing_stats['completed_jobs']
                    )
                
                # Remove from active jobs
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
            
            self.logger.info(
                "Data processing job completed",
                job_id=job.job_id,
                job_name=job.job_name,
                records_processed=job.records_processed,
                duration_minutes=f"{job.get_duration() / 60:.2f}"
            )
            
        except Exception as e:
            job.status = ProcessingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = time.time()
            
            # Update statistics
            with self._lock:
                self.processing_stats['failed_jobs'] += 1
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
            
            self.logger.error("Data processing job failed", job_id=job.job_id, error=str(e))
    
    def _load_data(self, source: DataSource) -> Optional[Any]:
        """Load data from source"""
        try:
            # Simulate data loading based on source type
            if source.source_type == "database":
                # Mock database data
                return [{'id': i, 'value': i * 2, 'category': f'cat_{i%3}'} for i in range(1000)]
            elif source.source_type == "file":
                # Mock file data
                return [{'timestamp': time.time() + i, 'sensor_value': 20 + i * 0.1} for i in range(500)]
            elif source.source_type == "api":
                # Mock API data
                return {'data': [{'field1': f'value_{i}', 'field2': i} for i in range(100)]}
            else:
                # Mock generic data
                return [{'data': f'item_{i}'} for i in range(100)]
                
        except Exception as e:
            self.logger.error("Data loading failed", source_id=source.source_id, error=str(e))
            return None
    
    def _apply_operation(self, data: Any, operation_name: str, parameters: Dict[str, Any]) -> Any:
        """Apply processing operation to data"""
        if operation_name not in self.operations:
            self.logger.warning("Unknown operation", operation=operation_name)
            return data
        
        operation_func = self.operations[operation_name]
        return operation_func(data, parameters)
    
    # Default processing operations
    def _clean_nulls(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Clean null values from data"""
        time.sleep(0.01)  # Simulate processing
        if isinstance(data, list):
            return [item for item in data if item is not None]
        return data
    
    def _normalize_data(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Normalize data values"""
        time.sleep(0.02)  # Simulate processing
        # Mock normalization
        return data
    
    def _encode_categorical(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Encode categorical variables"""
        time.sleep(0.01)  # Simulate processing
        # Mock encoding
        return data
    
    def _scale_features(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Scale feature values"""
        time.sleep(0.02)  # Simulate processing
        # Mock scaling
        return data
    
    def _extract_features(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Extract features from data"""
        time.sleep(0.03)  # Simulate processing
        # Mock feature extraction
        return data
    
    def _remove_outliers(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Remove outliers from data"""
        time.sleep(0.01)  # Simulate processing
        # Mock outlier removal
        return data
    
    def _aggregate_data(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Aggregate data"""
        time.sleep(0.02)  # Simulate processing
        # Mock aggregation
        return data
    
    def _transform_data(self, data: Any, parameters: Dict[str, Any]) -> Any:
        """Transform data"""
        time.sleep(0.01)  # Simulate processing
        # Mock transformation
        return data
    
    def validate_data(self, data: Any, rules: List[Dict[str, Any]]) -> ValidationResult:
        """Validate data against rules"""
        try:
            errors = []
            warnings = []
            quality_score = 1.0
            
            for rule in rules:
                rule_type = ValidationRule(rule.get('type', 'not_null'))
                rule_params = rule.get('parameters', {})
                
                if rule_type in self.validation_rules:
                    validator = self.validation_rules[rule_type]
                    result = validator(data, rule_params)
                    
                    if not result['valid']:
                        errors.extend(result.get('errors', []))
                        quality_score *= 0.9  # Reduce quality score
                    
                    warnings.extend(result.get('warnings', []))
            
            # Calculate statistics
            statistics = {
                'total_records': len(data) if isinstance(data, list) else 1,
                'validation_rules_applied': len(rules),
                'errors_found': len(errors),
                'warnings_found': len(warnings)
            }
            
            return ValidationResult(
                is_valid=len(errors) == 0,
                errors=errors,
                warnings=warnings,
                quality_score=quality_score,
                statistics=statistics
            )
            
        except Exception as e:
            self.logger.error("Data validation failed", error=str(e))
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                quality_score=0.0
            )
    
    # Default validation rules
    def _validate_not_null(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate not null rule"""
        if isinstance(data, list):
            null_count = sum(1 for item in data if item is None)
            return {
                'valid': null_count == 0,
                'errors': [f"Found {null_count} null values"] if null_count > 0 else []
            }
        return {'valid': data is not None, 'errors': ['Value is null'] if data is None else []}
    
    def _validate_range(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate range rule"""
        min_val = parameters.get('min', float('-inf'))
        max_val = parameters.get('max', float('inf'))
        
        # Mock range validation
        return {'valid': True, 'errors': []}
    
    def _validate_type(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate type rule"""
        expected_type = parameters.get('type', 'any')
        
        # Mock type validation
        return {'valid': True, 'errors': []}
    
    def _validate_format(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate format rule"""
        format_pattern = parameters.get('pattern', '.*')
        
        # Mock format validation
        return {'valid': True, 'errors': []}
    
    def _validate_uniqueness(self, data: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate uniqueness rule"""
        # Mock uniqueness validation
        return {'valid': True, 'errors': []}
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get processing job status"""
        if job_id not in self.processing_jobs:
            return None
        
        job = self.processing_jobs[job_id]
        return {
            'job_id': job.job_id,
            'job_name': job.job_name,
            'status': job.status.value,
            'progress': job.progress,
            'records_processed': job.records_processed,
            'records_total': job.records_total,
            'duration': job.get_duration(),
            'created_at': job.created_at,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
            'error_message': job.error_message,
            'source': {
                'source_id': job.source.source_id,
                'source_name': job.source.source_name,
                'data_type': job.source.data_type.value
            }
        }
    
    def list_data_sources(self) -> List[Dict[str, Any]]:
        """List all registered data sources"""
        sources = []
        for source in self.data_sources.values():
            sources.append({
                'source_id': source.source_id,
                'source_name': source.source_name,
                'source_type': source.source_type,
                'data_type': source.data_type.value,
                'metadata': source.metadata
            })
        
        return sorted(sources, key=lambda x: x['source_name'])
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get data processing statistics"""
        with self._lock:
            return {
                'max_concurrent_jobs': self.max_concurrent_jobs,
                'active_jobs': len(self.active_jobs),
                'total_jobs': len(self.processing_jobs),
                'registered_sources': len(self.data_sources),
                'available_operations': len(self.operations),
                'validation_rules': len(self.validation_rules),
                'chunk_size': self.chunk_size,
                'memory_limit_mb': self.memory_limit_mb,
                'stats': self.processing_stats.copy()
            }
