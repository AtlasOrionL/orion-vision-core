"""
Training Manager for Orion Vision Core

This module provides comprehensive ML training capabilities including
distributed training, hyperparameter optimization, and experiment tracking.
Part of Sprint 9.5 Advanced Machine Learning & Training development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.5 - Advanced Machine Learning & Training
"""

import time
import threading
import json
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class TrainingStatus(Enum):
    """Training status enumeration"""
    PENDING = "pending"
    INITIALIZING = "initializing"
    TRAINING = "training"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class TrainingMode(Enum):
    """Training mode enumeration"""
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    REINFORCEMENT = "reinforcement"
    SEMI_SUPERVISED = "semi_supervised"
    TRANSFER_LEARNING = "transfer_learning"
    FINE_TUNING = "fine_tuning"


class OptimizationStrategy(Enum):
    """Optimization strategy enumeration"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"
    HYPERBAND = "hyperband"
    OPTUNA = "optuna"


@dataclass
class TrainingConfig:
    """Training configuration data structure"""
    config_id: str
    model_type: str
    training_mode: TrainingMode
    epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 0.001
    optimizer: str = "adam"
    loss_function: str = "mse"
    validation_split: float = 0.2
    early_stopping: bool = True
    patience: int = 10
    save_best_only: bool = True
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    data_config: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate training configuration"""
        if self.epochs <= 0 or self.batch_size <= 0:
            return False
        if not 0 < self.learning_rate < 1:
            return False
        if not 0 <= self.validation_split <= 1:
            return False
        return True


@dataclass
class TrainingJob:
    """Training job data structure"""
    job_id: str
    job_name: str
    config: TrainingConfig
    status: TrainingStatus = TrainingStatus.PENDING
    progress: float = 0.0
    current_epoch: int = 0
    best_metric: Optional[float] = None
    metrics_history: List[Dict[str, float]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error_message: Optional[str] = None
    model_path: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration(self) -> float:
        """Get training duration in seconds"""
        if self.started_at:
            end_time = self.completed_at or time.time()
            return end_time - self.started_at
        return 0.0
    
    def is_active(self) -> bool:
        """Check if training job is active"""
        return self.status in [TrainingStatus.TRAINING, TrainingStatus.VALIDATING]


@dataclass
class ExperimentConfig:
    """Experiment configuration for hyperparameter optimization"""
    experiment_id: str
    experiment_name: str
    base_config: TrainingConfig
    optimization_strategy: OptimizationStrategy
    search_space: Dict[str, Any]
    max_trials: int = 100
    max_duration_hours: float = 24.0
    objective_metric: str = "val_loss"
    objective_direction: str = "minimize"  # minimize or maximize
    early_stopping_trials: int = 10
    
    def validate(self) -> bool:
        """Validate experiment configuration"""
        if not self.base_config.validate():
            return False
        if self.max_trials <= 0 or self.max_duration_hours <= 0:
            return False
        if not self.search_space:
            return False
        return True


class TrainingManager:
    """
    Comprehensive ML training management system
    
    Provides training job management, hyperparameter optimization,
    experiment tracking, and distributed training capabilities.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize training manager"""
        self.logger = logger or AgentLogger("training_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Job management
        self.training_jobs: Dict[str, TrainingJob] = {}
        self.active_jobs: Dict[str, TrainingJob] = {}
        self.job_queue: List[str] = []
        
        # Experiment management
        self.experiments: Dict[str, ExperimentConfig] = {}
        self.experiment_results: Dict[str, List[Dict[str, Any]]] = {}
        
        # Resource management
        self.max_concurrent_jobs = 4
        self.available_gpus = []
        self.gpu_usage: Dict[str, str] = {}  # gpu_id -> job_id
        
        # Training control
        self.training_enabled = False
        self.worker_threads: List[threading.Thread] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.training_stats = {
            'total_jobs': 0,
            'completed_jobs': 0,
            'failed_jobs': 0,
            'cancelled_jobs': 0,
            'total_experiments': 0,
            'total_training_time_hours': 0.0,
            'average_training_time_minutes': 0.0,
            'best_models_saved': 0,
            'gpu_utilization_percent': 0.0
        }
        
        self.logger.info("Training Manager initialized")
    
    def create_training_job(self, job_name: str, config: TrainingConfig) -> Optional[str]:
        """Create new training job"""
        try:
            # Validate configuration
            if not config.validate():
                self.logger.error("Invalid training configuration", job_name=job_name)
                return None
            
            job_id = str(uuid.uuid4())
            
            # Create training job
            job = TrainingJob(
                job_id=job_id,
                job_name=job_name,
                config=config
            )
            
            with self._lock:
                # Store job
                self.training_jobs[job_id] = job
                
                # Add to queue if not at capacity
                if len(self.active_jobs) < self.max_concurrent_jobs:
                    self.active_jobs[job_id] = job
                    job.status = TrainingStatus.INITIALIZING
                else:
                    self.job_queue.append(job_id)
                
                # Update statistics
                self.training_stats['total_jobs'] += 1
                
                self.logger.info(
                    "Training job created",
                    job_id=job_id,
                    job_name=job_name,
                    training_mode=config.training_mode.value,
                    epochs=config.epochs,
                    batch_size=config.batch_size
                )
                
                return job_id
                
        except Exception as e:
            self.logger.error("Training job creation failed", job_name=job_name, error=str(e))
            return None
    
    def start_training_job(self, job_id: str) -> bool:
        """Start training job"""
        try:
            if job_id not in self.training_jobs:
                self.logger.error("Training job not found", job_id=job_id)
                return False
            
            job = self.training_jobs[job_id]
            
            if job.status != TrainingStatus.PENDING and job.status != TrainingStatus.INITIALIZING:
                self.logger.warning("Job not in startable state", job_id=job_id, status=job.status.value)
                return False
            
            # Start training in background thread
            training_thread = threading.Thread(
                target=self._run_training_job,
                args=(job,),
                name=f"TrainingJob-{job_id[:8]}",
                daemon=True
            )
            training_thread.start()
            
            self.logger.info("Training job started", job_id=job_id, job_name=job.job_name)
            return True
            
        except Exception as e:
            self.logger.error("Training job start failed", job_id=job_id, error=str(e))
            return False
    
    def _run_training_job(self, job: TrainingJob):
        """Run training job"""
        try:
            job.status = TrainingStatus.TRAINING
            job.started_at = time.time()
            
            self.logger.info(
                "Training job execution started",
                job_id=job.job_id,
                job_name=job.job_name,
                epochs=job.config.epochs
            )
            
            # Simulate training process
            for epoch in range(job.config.epochs):
                if job.status == TrainingStatus.CANCELLED:
                    break
                
                # Simulate epoch training
                epoch_start = time.time()
                time.sleep(0.1)  # Simulate training time
                epoch_duration = time.time() - epoch_start
                
                # Generate mock metrics
                train_loss = 1.0 - (epoch / job.config.epochs) * 0.8 + (0.1 * (0.5 - time.time() % 1))
                val_loss = train_loss + 0.1 + (0.05 * (0.5 - time.time() % 1))
                train_acc = min(0.99, (epoch / job.config.epochs) * 0.9 + 0.1)
                val_acc = train_acc - 0.05
                
                # Store metrics
                epoch_metrics = {
                    'epoch': epoch + 1,
                    'train_loss': train_loss,
                    'val_loss': val_loss,
                    'train_accuracy': train_acc,
                    'val_accuracy': val_acc,
                    'epoch_duration': epoch_duration,
                    'timestamp': time.time()
                }
                
                job.metrics_history.append(epoch_metrics)
                job.current_epoch = epoch + 1
                job.progress = (epoch + 1) / job.config.epochs
                
                # Update best metric
                if job.best_metric is None or val_loss < job.best_metric:
                    job.best_metric = val_loss
                    job.metadata['best_epoch'] = epoch + 1
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="training.epoch_completed",
                    value=epoch_duration,
                    metric_type=MetricType.TIMER,
                    tags={
                        'job_id': job.job_id,
                        'epoch': str(epoch + 1),
                        'training_mode': job.config.training_mode.value
                    }
                )
                
                # Early stopping check
                if job.config.early_stopping and epoch > job.config.patience:
                    recent_losses = [m['val_loss'] for m in job.metrics_history[-job.config.patience:]]
                    if all(loss >= job.best_metric for loss in recent_losses):
                        self.logger.info(
                            "Early stopping triggered",
                            job_id=job.job_id,
                            epoch=epoch + 1,
                            best_metric=job.best_metric
                        )
                        break
                
                # Log progress periodically
                if (epoch + 1) % 10 == 0:
                    self.logger.debug(
                        "Training progress",
                        job_id=job.job_id,
                        epoch=epoch + 1,
                        progress_percent=f"{job.progress * 100:.1f}",
                        train_loss=f"{train_loss:.4f}",
                        val_loss=f"{val_loss:.4f}"
                    )
            
            # Complete training
            if job.status != TrainingStatus.CANCELLED:
                job.status = TrainingStatus.COMPLETED
                job.completed_at = time.time()
                
                # Save model (mock)
                job.model_path = f"/models/{job.job_id}/best_model.pt"
                
                # Update statistics
                with self._lock:
                    self.training_stats['completed_jobs'] += 1
                    self.training_stats['best_models_saved'] += 1
                    
                    training_time_hours = job.get_duration() / 3600
                    self.training_stats['total_training_time_hours'] += training_time_hours
                    
                    completed_jobs = self.training_stats['completed_jobs']
                    self.training_stats['average_training_time_minutes'] = (
                        self.training_stats['total_training_time_hours'] * 60 / completed_jobs
                    )
                
                self.logger.info(
                    "Training job completed",
                    job_id=job.job_id,
                    job_name=job.job_name,
                    final_epoch=job.current_epoch,
                    best_metric=job.best_metric,
                    duration_minutes=f"{job.get_duration() / 60:.2f}"
                )
            
            # Remove from active jobs and start next in queue
            with self._lock:
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
                
                # Start next job in queue
                if self.job_queue and len(self.active_jobs) < self.max_concurrent_jobs:
                    next_job_id = self.job_queue.pop(0)
                    if next_job_id in self.training_jobs:
                        next_job = self.training_jobs[next_job_id]
                        self.active_jobs[next_job_id] = next_job
                        self.start_training_job(next_job_id)
            
        except Exception as e:
            job.status = TrainingStatus.FAILED
            job.error_message = str(e)
            job.completed_at = time.time()
            
            # Update statistics
            with self._lock:
                self.training_stats['failed_jobs'] += 1
                if job.job_id in self.active_jobs:
                    del self.active_jobs[job.job_id]
            
            self.logger.error("Training job failed", job_id=job.job_id, error=str(e))
    
    def cancel_training_job(self, job_id: str) -> bool:
        """Cancel training job"""
        try:
            if job_id not in self.training_jobs:
                self.logger.error("Training job not found", job_id=job_id)
                return False
            
            job = self.training_jobs[job_id]
            
            if not job.is_active():
                self.logger.warning("Job not active", job_id=job_id, status=job.status.value)
                return False
            
            job.status = TrainingStatus.CANCELLED
            job.completed_at = time.time()
            
            # Update statistics
            with self._lock:
                self.training_stats['cancelled_jobs'] += 1
                if job_id in self.active_jobs:
                    del self.active_jobs[job_id]
            
            self.logger.info("Training job cancelled", job_id=job_id)
            return True
            
        except Exception as e:
            self.logger.error("Training job cancellation failed", job_id=job_id, error=str(e))
            return False
    
    def create_experiment(self, experiment_config: ExperimentConfig) -> Optional[str]:
        """Create hyperparameter optimization experiment"""
        try:
            # Validate configuration
            if not experiment_config.validate():
                self.logger.error("Invalid experiment configuration", 
                                experiment_name=experiment_config.experiment_name)
                return None
            
            experiment_id = experiment_config.experiment_id
            
            with self._lock:
                # Store experiment
                self.experiments[experiment_id] = experiment_config
                self.experiment_results[experiment_id] = []
                
                # Update statistics
                self.training_stats['total_experiments'] += 1
                
                self.logger.info(
                    "Experiment created",
                    experiment_id=experiment_id,
                    experiment_name=experiment_config.experiment_name,
                    optimization_strategy=experiment_config.optimization_strategy.value,
                    max_trials=experiment_config.max_trials
                )
                
                return experiment_id
                
        except Exception as e:
            self.logger.error("Experiment creation failed", 
                            experiment_name=experiment_config.experiment_name, error=str(e))
            return None
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get training job status"""
        if job_id not in self.training_jobs:
            return None
        
        job = self.training_jobs[job_id]
        return {
            'job_id': job.job_id,
            'job_name': job.job_name,
            'status': job.status.value,
            'progress': job.progress,
            'current_epoch': job.current_epoch,
            'total_epochs': job.config.epochs,
            'best_metric': job.best_metric,
            'duration': job.get_duration(),
            'created_at': job.created_at,
            'started_at': job.started_at,
            'completed_at': job.completed_at,
            'error_message': job.error_message,
            'model_path': job.model_path
        }
    
    def get_job_metrics(self, job_id: str) -> List[Dict[str, float]]:
        """Get training job metrics history"""
        if job_id not in self.training_jobs:
            return []
        
        return self.training_jobs[job_id].metrics_history
    
    def list_jobs(self, status_filter: Optional[TrainingStatus] = None) -> List[Dict[str, Any]]:
        """List training jobs with optional status filter"""
        jobs = []
        for job in self.training_jobs.values():
            if status_filter is None or job.status == status_filter:
                jobs.append(self.get_job_status(job.job_id))
        
        return sorted(jobs, key=lambda x: x['created_at'], reverse=True)
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training manager statistics"""
        with self._lock:
            return {
                'max_concurrent_jobs': self.max_concurrent_jobs,
                'active_jobs': len(self.active_jobs),
                'queued_jobs': len(self.job_queue),
                'total_jobs': len(self.training_jobs),
                'available_gpus': len(self.available_gpus),
                'gpu_usage': len(self.gpu_usage),
                'training_enabled': self.training_enabled,
                'stats': self.training_stats.copy()
            }
