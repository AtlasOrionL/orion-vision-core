"""
ML Pipeline Manager for Orion Vision Core

This module provides comprehensive ML pipeline management including
data processing, feature engineering, model training, and deployment.
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


class PipelineStatus(Enum):
    """Pipeline status enumeration"""
    DRAFT = "draft"
    VALIDATING = "validating"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(Enum):
    """Pipeline step type enumeration"""
    DATA_INGESTION = "data_ingestion"
    DATA_VALIDATION = "data_validation"
    DATA_PREPROCESSING = "data_preprocessing"
    FEATURE_ENGINEERING = "feature_engineering"
    MODEL_TRAINING = "model_training"
    MODEL_VALIDATION = "model_validation"
    MODEL_DEPLOYMENT = "model_deployment"
    CUSTOM = "custom"


class ExecutionMode(Enum):
    """Pipeline execution mode enumeration"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"
    LOOP = "loop"


@dataclass
class PipelineStep:
    """Pipeline step data structure"""
    step_id: str
    step_name: str
    step_type: StepType
    execution_mode: ExecutionMode = ExecutionMode.SEQUENTIAL
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    timeout_seconds: float = 3600.0
    retry_count: int = 3
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate pipeline step"""
        if not self.step_name or not self.step_id:
            return False
        if self.timeout_seconds <= 0 or self.retry_count < 0:
            return False
        return True


@dataclass
class PipelineExecution:
    """Pipeline execution data structure"""
    execution_id: str
    pipeline_id: str
    status: PipelineStatus = PipelineStatus.READY
    current_step: Optional[str] = None
    completed_steps: List[str] = field(default_factory=list)
    failed_steps: List[str] = field(default_factory=list)
    step_results: Dict[str, Any] = field(default_factory=dict)
    execution_metrics: Dict[str, float] = field(default_factory=dict)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    
    def get_duration(self) -> float:
        """Get execution duration in seconds"""
        if self.started_at:
            end_time = self.completed_at or time.time()
            return end_time - self.started_at
        return 0.0
    
    def get_progress(self, total_steps: int) -> float:
        """Get execution progress percentage"""
        if total_steps == 0:
            return 0.0
        return len(self.completed_steps) / total_steps


@dataclass
class MLPipeline:
    """ML pipeline data structure"""
    pipeline_id: str
    pipeline_name: str
    description: str
    steps: List[PipelineStep] = field(default_factory=list)
    global_parameters: Dict[str, Any] = field(default_factory=dict)
    schedule: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    version: str = "1.0.0"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate pipeline configuration"""
        if not self.pipeline_name or not self.pipeline_id:
            return False
        
        # Validate all steps
        for step in self.steps:
            if not step.validate():
                return False
        
        # Check for circular dependencies
        return self._check_dependencies()
    
    def _check_dependencies(self) -> bool:
        """Check for circular dependencies"""
        step_ids = {step.step_id for step in self.steps}
        
        for step in self.steps:
            for dep in step.dependencies:
                if dep not in step_ids:
                    return False
        
        # Simple cycle detection (could be improved)
        visited = set()
        rec_stack = set()
        
        def has_cycle(step_id: str) -> bool:
            if step_id in rec_stack:
                return True
            if step_id in visited:
                return False
            
            visited.add(step_id)
            rec_stack.add(step_id)
            
            # Find step and check dependencies
            for step in self.steps:
                if step.step_id == step_id:
                    for dep in step.dependencies:
                        if has_cycle(dep):
                            return True
                    break
            
            rec_stack.remove(step_id)
            return False
        
        for step in self.steps:
            if step.step_id not in visited:
                if has_cycle(step.step_id):
                    return False
        
        return True
    
    def get_execution_order(self) -> List[str]:
        """Get topological order of steps for execution"""
        # Simple topological sort
        in_degree = {step.step_id: len(step.dependencies) for step in self.steps}
        queue = [step_id for step_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            # Find steps that depend on current
            for step in self.steps:
                if current in step.dependencies:
                    in_degree[step.step_id] -= 1
                    if in_degree[step.step_id] == 0:
                        queue.append(step.step_id)
        
        return result


class PipelineManager:
    """
    Comprehensive ML pipeline management system
    
    Provides pipeline creation, execution, monitoring, and optimization
    with support for complex workflows and distributed execution.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize pipeline manager"""
        self.logger = logger or AgentLogger("pipeline_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Pipeline storage
        self.pipelines: Dict[str, MLPipeline] = {}
        self.executions: Dict[str, PipelineExecution] = {}
        
        # Execution management
        self.active_executions: Dict[str, PipelineExecution] = {}
        self.execution_queue: List[str] = []
        self.max_concurrent_executions = 5
        
        # Step processors
        self.step_processors: Dict[StepType, Callable] = {}
        
        # Scheduling
        self.scheduled_pipelines: Dict[str, Dict[str, Any]] = {}
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.pipeline_stats = {
            'total_pipelines': 0,
            'total_executions': 0,
            'successful_executions': 0,
            'failed_executions': 0,
            'average_execution_time_minutes': 0.0,
            'total_execution_time_hours': 0.0,
            'step_success_rate': 0.0,
            'most_used_step_types': {}
        }
        
        # Initialize default step processors
        self._initialize_step_processors()
        
        self.logger.info("Pipeline Manager initialized")
    
    def _initialize_step_processors(self):
        """Initialize default step processors"""
        self.step_processors[StepType.DATA_INGESTION] = self._process_data_ingestion
        self.step_processors[StepType.DATA_VALIDATION] = self._process_data_validation
        self.step_processors[StepType.DATA_PREPROCESSING] = self._process_data_preprocessing
        self.step_processors[StepType.FEATURE_ENGINEERING] = self._process_feature_engineering
        self.step_processors[StepType.MODEL_TRAINING] = self._process_model_training
        self.step_processors[StepType.MODEL_VALIDATION] = self._process_model_validation
        self.step_processors[StepType.MODEL_DEPLOYMENT] = self._process_model_deployment
    
    def create_pipeline(self, pipeline: MLPipeline) -> bool:
        """Create new ML pipeline"""
        try:
            # Validate pipeline
            if not pipeline.validate():
                self.logger.error("Invalid pipeline configuration", pipeline_id=pipeline.pipeline_id)
                return False
            
            with self._lock:
                # Store pipeline
                self.pipelines[pipeline.pipeline_id] = pipeline
                
                # Update statistics
                self.pipeline_stats['total_pipelines'] = len(self.pipelines)
                
                self.logger.info(
                    "ML pipeline created",
                    pipeline_id=pipeline.pipeline_id,
                    pipeline_name=pipeline.pipeline_name,
                    steps_count=len(pipeline.steps),
                    version=pipeline.version
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Pipeline creation failed", pipeline_id=pipeline.pipeline_id, error=str(e))
            return False
    
    def execute_pipeline(self, pipeline_id: str, parameters: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Execute ML pipeline"""
        try:
            if pipeline_id not in self.pipelines:
                self.logger.error("Pipeline not found", pipeline_id=pipeline_id)
                return None
            
            pipeline = self.pipelines[pipeline_id]
            execution_id = str(uuid.uuid4())
            
            # Create execution
            execution = PipelineExecution(
                execution_id=execution_id,
                pipeline_id=pipeline_id
            )
            
            with self._lock:
                # Store execution
                self.executions[execution_id] = execution
                
                # Add to active executions or queue
                if len(self.active_executions) < self.max_concurrent_executions:
                    self.active_executions[execution_id] = execution
                    execution.status = PipelineStatus.RUNNING
                else:
                    self.execution_queue.append(execution_id)
                
                # Update statistics
                self.pipeline_stats['total_executions'] += 1
            
            # Start execution in background thread
            if execution.status == PipelineStatus.RUNNING:
                execution_thread = threading.Thread(
                    target=self._run_pipeline_execution,
                    args=(execution, pipeline, parameters or {}),
                    name=f"PipelineExecution-{execution_id[:8]}",
                    daemon=True
                )
                execution_thread.start()
            
            self.logger.info(
                "Pipeline execution started",
                pipeline_id=pipeline_id,
                execution_id=execution_id,
                steps_count=len(pipeline.steps)
            )
            
            return execution_id
            
        except Exception as e:
            self.logger.error("Pipeline execution failed", pipeline_id=pipeline_id, error=str(e))
            return None
    
    def _run_pipeline_execution(self, execution: PipelineExecution, pipeline: MLPipeline, parameters: Dict[str, Any]):
        """Run pipeline execution"""
        try:
            execution.started_at = time.time()
            
            # Get execution order
            execution_order = pipeline.get_execution_order()
            
            self.logger.info(
                "Pipeline execution started",
                execution_id=execution.execution_id,
                pipeline_id=pipeline.pipeline_id,
                execution_order=execution_order
            )
            
            # Execute steps in order
            for step_id in execution_order:
                if execution.status == PipelineStatus.CANCELLED:
                    break
                
                # Find step
                step = next((s for s in pipeline.steps if s.step_id == step_id), None)
                if not step or not step.enabled:
                    continue
                
                execution.current_step = step_id
                
                # Execute step
                success = self._execute_step(execution, step, parameters)
                
                if success:
                    execution.completed_steps.append(step_id)
                    
                    self.logger.debug(
                        "Pipeline step completed",
                        execution_id=execution.execution_id,
                        step_id=step_id,
                        step_name=step.step_name
                    )
                else:
                    execution.failed_steps.append(step_id)
                    execution.status = PipelineStatus.FAILED
                    execution.error_message = f"Step {step_id} failed"
                    
                    self.logger.error(
                        "Pipeline step failed",
                        execution_id=execution.execution_id,
                        step_id=step_id,
                        step_name=step.step_name
                    )
                    break
            
            # Complete execution
            if execution.status != PipelineStatus.FAILED and execution.status != PipelineStatus.CANCELLED:
                execution.status = PipelineStatus.COMPLETED
                
                # Update statistics
                with self._lock:
                    self.pipeline_stats['successful_executions'] += 1
            else:
                # Update statistics
                with self._lock:
                    self.pipeline_stats['failed_executions'] += 1
            
            execution.completed_at = time.time()
            execution.current_step = None
            
            # Calculate execution metrics
            execution.execution_metrics = {
                'total_duration_seconds': execution.get_duration(),
                'steps_completed': len(execution.completed_steps),
                'steps_failed': len(execution.failed_steps),
                'success_rate': len(execution.completed_steps) / len(pipeline.steps) if pipeline.steps else 0
            }
            
            # Update global statistics
            with self._lock:
                execution_time_hours = execution.get_duration() / 3600
                self.pipeline_stats['total_execution_time_hours'] += execution_time_hours
                
                total_executions = self.pipeline_stats['total_executions']
                self.pipeline_stats['average_execution_time_minutes'] = (
                    self.pipeline_stats['total_execution_time_hours'] * 60 / total_executions
                )
                
                # Remove from active executions
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
                
                # Start next execution in queue
                if self.execution_queue and len(self.active_executions) < self.max_concurrent_executions:
                    next_execution_id = self.execution_queue.pop(0)
                    if next_execution_id in self.executions:
                        next_execution = self.executions[next_execution_id]
                        next_pipeline = self.pipelines[next_execution.pipeline_id]
                        self.active_executions[next_execution_id] = next_execution
                        next_execution.status = PipelineStatus.RUNNING
                        
                        # Start next execution
                        execution_thread = threading.Thread(
                            target=self._run_pipeline_execution,
                            args=(next_execution, next_pipeline, {}),
                            name=f"PipelineExecution-{next_execution_id[:8]}",
                            daemon=True
                        )
                        execution_thread.start()
            
            self.logger.info(
                "Pipeline execution completed",
                execution_id=execution.execution_id,
                pipeline_id=pipeline.pipeline_id,
                status=execution.status.value,
                duration_minutes=f"{execution.get_duration() / 60:.2f}",
                steps_completed=len(execution.completed_steps),
                steps_failed=len(execution.failed_steps)
            )
            
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = time.time()
            
            # Update statistics
            with self._lock:
                self.pipeline_stats['failed_executions'] += 1
                if execution.execution_id in self.active_executions:
                    del self.active_executions[execution.execution_id]
            
            self.logger.error("Pipeline execution failed", execution_id=execution.execution_id, error=str(e))
    
    def _execute_step(self, execution: PipelineExecution, step: PipelineStep, parameters: Dict[str, Any]) -> bool:
        """Execute single pipeline step"""
        try:
            start_time = time.time()
            
            # Get step processor
            if step.step_type not in self.step_processors:
                self.logger.error("No processor for step type", step_type=step.step_type.value)
                return False
            
            processor = self.step_processors[step.step_type]
            
            # Execute step with retry logic
            for attempt in range(step.retry_count + 1):
                try:
                    # Execute step processor
                    result = processor(step, parameters, execution.step_results)
                    
                    # Store result
                    execution.step_results[step.step_id] = result
                    
                    # Collect metrics
                    execution_time = time.time() - start_time
                    self.metrics_collector.collect_metric(
                        name="pipeline.step_executed",
                        value=execution_time,
                        metric_type=MetricType.TIMER,
                        tags={
                            'pipeline_id': execution.pipeline_id,
                            'step_id': step.step_id,
                            'step_type': step.step_type.value,
                            'attempt': str(attempt + 1)
                        }
                    )
                    
                    return True
                    
                except Exception as e:
                    if attempt < step.retry_count:
                        self.logger.warning(
                            "Step execution failed, retrying",
                            step_id=step.step_id,
                            attempt=attempt + 1,
                            error=str(e)
                        )
                        time.sleep(1.0 * (attempt + 1))  # Exponential backoff
                    else:
                        raise e
            
            return False
            
        except Exception as e:
            self.logger.error("Step execution failed", step_id=step.step_id, error=str(e))
            return False
    
    # Default step processors
    def _process_data_ingestion(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process data ingestion step"""
        time.sleep(0.1)  # Simulate processing
        return {'data_loaded': True, 'records_count': 10000, 'data_source': 'database'}
    
    def _process_data_validation(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process data validation step"""
        time.sleep(0.05)  # Simulate processing
        return {'validation_passed': True, 'quality_score': 0.95, 'issues_found': 2}
    
    def _process_data_preprocessing(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process data preprocessing step"""
        time.sleep(0.1)  # Simulate processing
        return {'preprocessing_completed': True, 'features_created': 25, 'data_cleaned': True}
    
    def _process_feature_engineering(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process feature engineering step"""
        time.sleep(0.15)  # Simulate processing
        return {'features_engineered': True, 'feature_count': 50, 'feature_importance': [0.8, 0.6, 0.4]}
    
    def _process_model_training(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process model training step"""
        time.sleep(0.2)  # Simulate processing
        return {'model_trained': True, 'accuracy': 0.92, 'loss': 0.15, 'epochs': 100}
    
    def _process_model_validation(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process model validation step"""
        time.sleep(0.1)  # Simulate processing
        return {'validation_completed': True, 'test_accuracy': 0.89, 'precision': 0.91, 'recall': 0.87}
    
    def _process_model_deployment(self, step: PipelineStep, parameters: Dict[str, Any], results: Dict[str, Any]) -> Dict[str, Any]:
        """Process model deployment step"""
        time.sleep(0.05)  # Simulate processing
        return {'deployment_completed': True, 'endpoint_url': 'https://api.example.com/model', 'version': '1.0.0'}
    
    def get_pipeline(self, pipeline_id: str) -> Optional[MLPipeline]:
        """Get pipeline by ID"""
        return self.pipelines.get(pipeline_id)
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get execution status"""
        if execution_id not in self.executions:
            return None
        
        execution = self.executions[execution_id]
        pipeline = self.pipelines.get(execution.pipeline_id)
        
        return {
            'execution_id': execution.execution_id,
            'pipeline_id': execution.pipeline_id,
            'pipeline_name': pipeline.pipeline_name if pipeline else 'Unknown',
            'status': execution.status.value,
            'current_step': execution.current_step,
            'progress': execution.get_progress(len(pipeline.steps) if pipeline else 0),
            'completed_steps': len(execution.completed_steps),
            'failed_steps': len(execution.failed_steps),
            'duration': execution.get_duration(),
            'started_at': execution.started_at,
            'completed_at': execution.completed_at,
            'error_message': execution.error_message,
            'metrics': execution.execution_metrics
        }
    
    def list_pipelines(self) -> List[Dict[str, Any]]:
        """List all pipelines"""
        pipelines = []
        for pipeline in self.pipelines.values():
            pipelines.append({
                'pipeline_id': pipeline.pipeline_id,
                'pipeline_name': pipeline.pipeline_name,
                'description': pipeline.description,
                'steps_count': len(pipeline.steps),
                'version': pipeline.version,
                'created_at': pipeline.created_at,
                'updated_at': pipeline.updated_at,
                'tags': pipeline.tags
            })
        
        return sorted(pipelines, key=lambda x: x['created_at'], reverse=True)
    
    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline manager statistics"""
        with self._lock:
            return {
                'total_pipelines': len(self.pipelines),
                'active_executions': len(self.active_executions),
                'queued_executions': len(self.execution_queue),
                'max_concurrent_executions': self.max_concurrent_executions,
                'total_executions': len(self.executions),
                'stats': self.pipeline_stats.copy()
            }
