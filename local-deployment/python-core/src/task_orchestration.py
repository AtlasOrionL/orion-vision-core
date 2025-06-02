#!/usr/bin/env python3
"""
Distributed Task Orchestration System - Sprint 4.2
Orion Vision Core - Distributed Agent Coordination

Bu modül, cross-agent task coordination, distributed workflow management
ve consensus algorithms için orchestration sistemi sağlar.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import json
import time
import uuid
import threading
from typing import Dict, List, Optional, Any, Set, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod
import hashlib
from collections import defaultdict, deque
import logging

# Mevcut modüllerini import et
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from .service_discovery import ServiceDiscoveryManager, ServiceInfo
except ImportError:
    # Fallback for testing
    ServiceDiscoveryManager = None
    ServiceInfo = None


class TaskStatus(Enum):
    """Task durumları"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(Enum):
    """Task öncelikleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class WorkflowStatus(Enum):
    """Workflow durumları"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ConsensusType(Enum):
    """Consensus algoritma türleri"""
    MAJORITY = "majority"
    UNANIMOUS = "unanimous"
    WEIGHTED = "weighted"
    RAFT = "raft"
    PBFT = "pbft"


@dataclass
class TaskDefinition:
    """
    Task Definition Structure

    Distributed task'ların tanımlanması için veri yapısı.
    """
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str = ""
    task_type: str = "generic"
    description: str = ""

    # Task execution details
    required_capabilities: List[str] = field(default_factory=list)
    preferred_agents: List[str] = field(default_factory=list)
    excluded_agents: List[str] = field(default_factory=list)

    # Task parameters
    input_data: Dict[str, Any] = field(default_factory=dict)
    expected_output: Dict[str, Any] = field(default_factory=dict)
    timeout: float = 300.0  # 5 minutes default
    retry_count: int = 3

    # Priority and scheduling
    priority: TaskPriority = TaskPriority.NORMAL
    scheduled_time: Optional[float] = None
    deadline: Optional[float] = None

    # Dependencies
    dependencies: List[str] = field(default_factory=list)  # Task IDs
    dependent_tasks: List[str] = field(default_factory=list)  # Task IDs

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    created_time: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Task definition'ı dictionary'ye çevir"""
        return {
            'task_id': self.task_id,
            'task_name': self.task_name,
            'task_type': self.task_type,
            'description': self.description,
            'required_capabilities': self.required_capabilities,
            'preferred_agents': self.preferred_agents,
            'excluded_agents': self.excluded_agents,
            'input_data': self.input_data,
            'expected_output': self.expected_output,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'priority': self.priority.value,
            'scheduled_time': self.scheduled_time,
            'deadline': self.deadline,
            'dependencies': self.dependencies,
            'dependent_tasks': self.dependent_tasks,
            'metadata': self.metadata,
            'tags': self.tags,
            'created_time': self.created_time
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskDefinition':
        """Dictionary'den task definition oluştur"""
        return cls(
            task_id=data.get('task_id', str(uuid.uuid4())),
            task_name=data.get('task_name', ''),
            task_type=data.get('task_type', 'generic'),
            description=data.get('description', ''),
            required_capabilities=data.get('required_capabilities', []),
            preferred_agents=data.get('preferred_agents', []),
            excluded_agents=data.get('excluded_agents', []),
            input_data=data.get('input_data', {}),
            expected_output=data.get('expected_output', {}),
            timeout=data.get('timeout', 300.0),
            retry_count=data.get('retry_count', 3),
            priority=TaskPriority(data.get('priority', TaskPriority.NORMAL.value)),
            scheduled_time=data.get('scheduled_time'),
            deadline=data.get('deadline'),
            dependencies=data.get('dependencies', []),
            dependent_tasks=data.get('dependent_tasks', []),
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            created_time=data.get('created_time', time.time())
        )


@dataclass
class TaskExecution:
    """
    Task Execution State

    Task'ın çalışma durumu ve sonuçlarını takip eden veri yapısı.
    """
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = ""
    assigned_agent: str = ""
    assigned_service_id: str = ""

    # Execution state
    status: TaskStatus = TaskStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None

    # Results
    output_data: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    error_details: Dict[str, Any] = field(default_factory=dict)

    # Progress tracking
    progress_percentage: float = 0.0
    progress_message: str = ""
    checkpoints: List[Dict[str, Any]] = field(default_factory=list)

    # Retry information
    attempt_number: int = 1
    retry_history: List[Dict[str, Any]] = field(default_factory=list)

    # Performance metrics
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    network_usage: float = 0.0

    def start_execution(self, agent_id: str, service_id: str):
        """Task execution'ı başlat"""
        self.assigned_agent = agent_id
        self.assigned_service_id = service_id
        self.status = TaskStatus.RUNNING
        self.start_time = time.time()
        self.progress_percentage = 0.0
        self.progress_message = "Task started"

    def complete_execution(self, output_data: Dict[str, Any] = None):
        """Task execution'ı tamamla"""
        self.status = TaskStatus.COMPLETED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.progress_percentage = 100.0
        self.progress_message = "Task completed successfully"
        if output_data:
            self.output_data = output_data

    def fail_execution(self, error_message: str, error_details: Dict[str, Any] = None):
        """Task execution'ı başarısız olarak işaretle"""
        self.status = TaskStatus.FAILED
        self.end_time = time.time()
        if self.start_time:
            self.duration = self.end_time - self.start_time
        self.error_message = error_message
        self.error_details = error_details or {}
        self.progress_message = f"Task failed: {error_message}"

    def update_progress(self, percentage: float, message: str = ""):
        """Task progress'ini güncelle"""
        self.progress_percentage = max(0.0, min(100.0, percentage))
        if message:
            self.progress_message = message

        # Checkpoint ekle
        self.checkpoints.append({
            'timestamp': time.time(),
            'percentage': self.progress_percentage,
            'message': self.progress_message
        })

    def add_retry_attempt(self, error_message: str):
        """Retry attempt'i kaydet"""
        self.retry_history.append({
            'attempt': self.attempt_number,
            'timestamp': time.time(),
            'error': error_message,
            'duration': self.duration
        })
        self.attempt_number += 1

        # Reset execution state for retry
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time = None
        self.duration = None
        self.progress_percentage = 0.0
        self.progress_message = f"Retrying (attempt {self.attempt_number})"

    def to_dict(self) -> Dict[str, Any]:
        """Task execution'ı dictionary'ye çevir"""
        return {
            'execution_id': self.execution_id,
            'task_id': self.task_id,
            'assigned_agent': self.assigned_agent,
            'assigned_service_id': self.assigned_service_id,
            'status': self.status.value,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'duration': self.duration,
            'output_data': self.output_data,
            'error_message': self.error_message,
            'error_details': self.error_details,
            'progress_percentage': self.progress_percentage,
            'progress_message': self.progress_message,
            'checkpoints': self.checkpoints,
            'attempt_number': self.attempt_number,
            'retry_history': self.retry_history,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'network_usage': self.network_usage
        }


class TaskScheduler:
    """
    Task Scheduler - Intelligent Task Scheduling

    Task'ları priority, dependencies ve agent availability'ye göre
    akıllı şekilde schedule eden sistem.
    """

    def __init__(self, discovery_manager: Optional[ServiceDiscoveryManager] = None):
        """
        Task Scheduler başlatıcı

        Args:
            discovery_manager: Service discovery manager referansı
        """
        self.discovery_manager = discovery_manager

        # Task queues by priority
        self.task_queues: Dict[TaskPriority, deque] = {
            priority: deque() for priority in TaskPriority
        }

        # Task storage
        self.pending_tasks: Dict[str, TaskDefinition] = {}  # task_id -> TaskDefinition
        self.running_tasks: Dict[str, TaskExecution] = {}  # task_id -> TaskExecution
        self.completed_tasks: Dict[str, TaskExecution] = {}  # task_id -> TaskExecution

        # Dependency tracking
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)  # task_id -> dependencies
        self.dependent_graph: Dict[str, Set[str]] = defaultdict(set)  # task_id -> dependents

        # Scheduling state
        self.running = False
        self.scheduler_task = None

        # Thread safety
        self._lock = threading.RLock()

        # Statistics
        self.scheduler_stats = {
            'total_tasks_scheduled': 0,
            'total_tasks_completed': 0,
            'total_tasks_failed': 0,
            'average_scheduling_time': 0.0,
            'average_execution_time': 0.0
        }

        print("📅 Task Scheduler initialized")

    async def start(self):
        """Task scheduler'ı başlat"""
        if self.running:
            return

        self.running = True

        # Scheduler task'ını başlat
        self.scheduler_task = asyncio.create_task(self._scheduling_loop())

        print("🚀 Task Scheduler started")

    async def stop(self):
        """Task scheduler'ı durdur"""
        if not self.running:
            return

        self.running = False

        # Scheduler task'ını durdur
        if self.scheduler_task:
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass

        print("🛑 Task Scheduler stopped")

    def submit_task(self, task_definition: TaskDefinition) -> bool:
        """
        Task'ı scheduler'a gönder

        Args:
            task_definition: Task tanımı

        Returns:
            bool: Gönderme başarısı
        """
        with self._lock:
            try:
                # Task'ı pending tasks'a ekle
                self.pending_tasks[task_definition.task_id] = task_definition

                # Priority queue'ya ekle
                self.task_queues[task_definition.priority].append(task_definition.task_id)

                # Dependency graph'ı güncelle
                for dep_task_id in task_definition.dependencies:
                    self.dependency_graph[task_definition.task_id].add(dep_task_id)
                    self.dependent_graph[dep_task_id].add(task_definition.task_id)

                self.scheduler_stats['total_tasks_scheduled'] += 1

                print(f"📝 Task submitted: {task_definition.task_name} ({task_definition.task_id})")
                return True

            except Exception as e:
                print(f"❌ Task submission error: {e}")
                return False

    def cancel_task(self, task_id: str) -> bool:
        """
        Task'ı iptal et

        Args:
            task_id: Task ID

        Returns:
            bool: İptal başarısı
        """
        with self._lock:
            try:
                # Pending task'ı iptal et
                if task_id in self.pending_tasks:
                    task_def = self.pending_tasks[task_id]

                    # Queue'dan çıkar
                    try:
                        self.task_queues[task_def.priority].remove(task_id)
                    except ValueError:
                        pass

                    # Pending'den çıkar
                    del self.pending_tasks[task_id]

                    print(f"🚫 Pending task cancelled: {task_id}")
                    return True

                # Running task'ı iptal et
                if task_id in self.running_tasks:
                    execution = self.running_tasks[task_id]
                    execution.status = TaskStatus.CANCELLED
                    execution.end_time = time.time()
                    if execution.start_time:
                        execution.duration = execution.end_time - execution.start_time

                    # Running'den completed'a taşı
                    self.completed_tasks[task_id] = execution
                    del self.running_tasks[task_id]

                    print(f"🚫 Running task cancelled: {task_id}")
                    return True

                return False

            except Exception as e:
                print(f"❌ Task cancellation error: {e}")
                return False

    def get_next_task(self) -> Optional[TaskDefinition]:
        """
        Bir sonraki çalıştırılacak task'ı getir

        Returns:
            Optional[TaskDefinition]: Çalıştırılacak task
        """
        with self._lock:
            # Priority sırasına göre kontrol et (yüksek öncelik önce)
            for priority in sorted(TaskPriority, key=lambda p: p.value, reverse=True):
                queue = self.task_queues[priority]

                while queue:
                    task_id = queue.popleft()

                    # Task hala pending mi kontrol et
                    if task_id not in self.pending_tasks:
                        continue

                    task_def = self.pending_tasks[task_id]

                    # Dependency kontrolü
                    if self._are_dependencies_satisfied(task_id):
                        # Scheduled time kontrolü
                        if task_def.scheduled_time and time.time() < task_def.scheduled_time:
                            # Henüz zamanı gelmemiş, queue'ya geri koy
                            queue.append(task_id)
                            continue

                        # Task'ı pending'den çıkar
                        del self.pending_tasks[task_id]
                        return task_def
                    else:
                        # Dependencies henüz hazır değil, queue'ya geri koy
                        queue.append(task_id)

            return None

    def _are_dependencies_satisfied(self, task_id: str) -> bool:
        """Task'ın dependency'lerinin tamamlanıp tamamlanmadığını kontrol et"""
        dependencies = self.dependency_graph.get(task_id, set())

        for dep_task_id in dependencies:
            # Dependency completed mi?
            if dep_task_id in self.completed_tasks:
                execution = self.completed_tasks[dep_task_id]
                if execution.status != TaskStatus.COMPLETED:
                    return False  # Dependency failed
            else:
                return False  # Dependency not completed yet

        return True

    def start_task_execution(self, task_def: TaskDefinition, agent_id: str, service_id: str) -> TaskExecution:
        """
        Task execution'ı başlat

        Args:
            task_def: Task definition
            agent_id: Assigned agent ID
            service_id: Assigned service ID

        Returns:
            TaskExecution: Task execution object
        """
        with self._lock:
            execution = TaskExecution(task_id=task_def.task_id)
            execution.start_execution(agent_id, service_id)

            self.running_tasks[task_def.task_id] = execution

            print(f"▶️ Task execution started: {task_def.task_name} on {agent_id}")
            return execution

    def complete_task_execution(self, task_id: str, output_data: Dict[str, Any] = None) -> bool:
        """
        Task execution'ı tamamla

        Args:
            task_id: Task ID
            output_data: Task output data

        Returns:
            bool: Tamamlama başarısı
        """
        with self._lock:
            if task_id not in self.running_tasks:
                return False

            execution = self.running_tasks[task_id]
            execution.complete_execution(output_data)

            # Running'den completed'a taşı
            self.completed_tasks[task_id] = execution
            del self.running_tasks[task_id]

            self.scheduler_stats['total_tasks_completed'] += 1

            # Dependent task'ları kontrol et ve uygun olanları queue'ya ekle
            self._check_dependent_tasks(task_id)

            print(f"✅ Task execution completed: {task_id}")
            return True

    def fail_task_execution(self, task_id: str, error_message: str, error_details: Dict[str, Any] = None) -> bool:
        """
        Task execution'ı başarısız olarak işaretle

        Args:
            task_id: Task ID
            error_message: Hata mesajı
            error_details: Hata detayları

        Returns:
            bool: İşaretleme başarısı
        """
        with self._lock:
            if task_id not in self.running_tasks:
                return False

            execution = self.running_tasks[task_id]
            execution.fail_execution(error_message, error_details)

            # Running'den completed'a taşı
            self.completed_tasks[task_id] = execution
            del self.running_tasks[task_id]

            self.scheduler_stats['total_tasks_failed'] += 1

            print(f"❌ Task execution failed: {task_id} - {error_message}")
            return True

    def _check_dependent_tasks(self, completed_task_id: str):
        """Tamamlanan task'ın dependent task'larını kontrol et"""
        dependents = self.dependent_graph.get(completed_task_id, set())

        for dependent_task_id in dependents:
            if dependent_task_id in self.pending_tasks:
                # Dependent task'ın tüm dependency'leri tamamlandı mı kontrol et
                if self._are_dependencies_satisfied(dependent_task_id):
                    # Task'ı priority queue'ya ekle (eğer yoksa)
                    task_def = self.pending_tasks[dependent_task_id]
                    if dependent_task_id not in self.task_queues[task_def.priority]:
                        self.task_queues[task_def.priority].append(dependent_task_id)

    async def _scheduling_loop(self):
        """Task scheduling döngüsü"""
        while self.running:
            try:
                await asyncio.sleep(1.0)  # 1 saniye aralıklarla kontrol et

                if not self.running:
                    break

                # Timeout olan task'ları kontrol et
                await self._check_task_timeouts()

                # Deadline'ı geçen task'ları kontrol et
                await self._check_task_deadlines()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Scheduling loop error: {e}")

    async def _check_task_timeouts(self):
        """Timeout olan task'ları kontrol et"""
        with self._lock:
            current_time = time.time()
            timeout_tasks = []

            for task_id, execution in self.running_tasks.items():
                if execution.start_time:
                    task_def = None
                    # Task definition'ı bul
                    for completed_task_id, completed_execution in self.completed_tasks.items():
                        if completed_task_id == task_id:
                            continue

                    # Pending task'larda ara
                    for pending_task_id, pending_task_def in self.pending_tasks.items():
                        if pending_task_id == task_id:
                            task_def = pending_task_def
                            break

                    if task_def and (current_time - execution.start_time) > task_def.timeout:
                        timeout_tasks.append(task_id)

            # Timeout olan task'ları işaretle
            for task_id in timeout_tasks:
                self.fail_task_execution(task_id, "Task timeout", {"timeout_duration": task_def.timeout})

    async def _check_task_deadlines(self):
        """Deadline'ı geçen task'ları kontrol et"""
        with self._lock:
            current_time = time.time()
            deadline_tasks = []

            for task_id, task_def in self.pending_tasks.items():
                if task_def.deadline and current_time > task_def.deadline:
                    deadline_tasks.append(task_id)

            # Deadline'ı geçen task'ları iptal et
            for task_id in deadline_tasks:
                self.cancel_task(task_id)

    def get_scheduler_stats(self) -> Dict[str, Any]:
        """Scheduler istatistiklerini getir"""
        with self._lock:
            return {
                'running': self.running,
                'pending_tasks': len(self.pending_tasks),
                'running_tasks': len(self.running_tasks),
                'completed_tasks': len(self.completed_tasks),
                'stats': self.scheduler_stats.copy(),
                'queue_sizes': {
                    priority.name: len(queue) for priority, queue in self.task_queues.items()
                }
            }

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Task durumunu getir"""
        with self._lock:
            # Pending task'larda ara
            if task_id in self.pending_tasks:
                return {
                    'status': 'pending',
                    'task_definition': self.pending_tasks[task_id].to_dict()
                }

            # Running task'larda ara
            if task_id in self.running_tasks:
                return {
                    'status': 'running',
                    'task_execution': self.running_tasks[task_id].to_dict()
                }

            # Completed task'larda ara
            if task_id in self.completed_tasks:
                return {
                    'status': 'completed',
                    'task_execution': self.completed_tasks[task_id].to_dict()
                }

            return None


class TaskOrchestrator:
    """
    Task Orchestrator - Cross-Agent Task Coordination

    Multiple agent'lar arasında task coordination ve
    distributed execution yönetimi yapan sistem.
    """

    def __init__(self, discovery_manager: Optional[ServiceDiscoveryManager] = None):
        """
        Task Orchestrator başlatıcı

        Args:
            discovery_manager: Service discovery manager referansı
        """
        self.discovery_manager = discovery_manager
        self.task_scheduler = TaskScheduler(discovery_manager)

        # Orchestration state
        self.running = False
        self.orchestration_task = None

        # Agent assignment tracking
        self.agent_assignments: Dict[str, Set[str]] = defaultdict(set)  # agent_id -> task_ids
        self.task_assignments: Dict[str, str] = {}  # task_id -> agent_id

        # Performance tracking
        self.agent_performance: Dict[str, Dict[str, float]] = defaultdict(lambda: {
            'total_tasks': 0,
            'completed_tasks': 0,
            'failed_tasks': 0,
            'avg_execution_time': 0.0,
            'success_rate': 0.0
        })

        # Statistics
        self.orchestrator_stats = {
            'total_tasks_orchestrated': 0,
            'total_agents_used': 0,
            'average_task_distribution_time': 0.0,
            'load_balancing_efficiency': 0.0
        }

        print("🎭 Task Orchestrator initialized")

    async def start(self):
        """Task orchestrator'ı başlat"""
        if self.running:
            return

        self.running = True

        # Task scheduler'ı başlat
        await self.task_scheduler.start()

        # Orchestration task'ını başlat
        self.orchestration_task = asyncio.create_task(self._orchestration_loop())

        print("🚀 Task Orchestrator started")

    async def stop(self):
        """Task orchestrator'ı durdur"""
        if not self.running:
            return

        self.running = False

        # Orchestration task'ını durdur
        if self.orchestration_task:
            self.orchestration_task.cancel()
            try:
                await self.orchestration_task
            except asyncio.CancelledError:
                pass

        # Task scheduler'ı durdur
        await self.task_scheduler.stop()

        print("🛑 Task Orchestrator stopped")

    async def submit_task(self, task_definition: TaskDefinition) -> str:
        """
        Task'ı orchestrator'a gönder

        Args:
            task_definition: Task tanımı

        Returns:
            str: Task ID
        """
        # Task'ı scheduler'a gönder
        success = self.task_scheduler.submit_task(task_definition)

        if success:
            self.orchestrator_stats['total_tasks_orchestrated'] += 1
            print(f"🎭 Task submitted to orchestrator: {task_definition.task_name}")
            return task_definition.task_id
        else:
            raise Exception(f"Failed to submit task: {task_definition.task_name}")

    async def cancel_task(self, task_id: str) -> bool:
        """
        Task'ı iptal et

        Args:
            task_id: Task ID

        Returns:
            bool: İptal başarısı
        """
        return self.task_scheduler.cancel_task(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Task durumunu getir

        Args:
            task_id: Task ID

        Returns:
            Optional[Dict[str, Any]]: Task durumu
        """
        return self.task_scheduler.get_task_status(task_id)

    async def _orchestration_loop(self):
        """Task orchestration döngüsü"""
        while self.running:
            try:
                await asyncio.sleep(0.5)  # 500ms aralıklarla kontrol et

                if not self.running:
                    break

                # Bir sonraki task'ı al
                next_task = self.task_scheduler.get_next_task()
                if not next_task:
                    continue

                # Task için uygun agent bul
                selected_agent = await self._select_agent_for_task(next_task)
                if not selected_agent:
                    # Uygun agent bulunamadı, task'ı geri queue'ya koy
                    self.task_scheduler.submit_task(next_task)
                    continue

                # Task'ı agent'a assign et
                await self._assign_task_to_agent(next_task, selected_agent)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Orchestration loop error: {e}")

    async def _select_agent_for_task(self, task_def: TaskDefinition) -> Optional[ServiceInfo]:
        """
        Task için uygun agent seç

        Args:
            task_def: Task definition

        Returns:
            Optional[ServiceInfo]: Seçilen agent
        """
        if not self.discovery_manager:
            return None

        # Preferred agent'ları kontrol et
        if task_def.preferred_agents:
            for agent_id in task_def.preferred_agents:
                agents = self.discovery_manager.discover_agents()
                for agent in agents:
                    if agent.agent_id == agent_id and agent_id not in task_def.excluded_agents:
                        return agent

        # Capability-based selection
        suitable_agents = []
        if task_def.required_capabilities:
            for capability in task_def.required_capabilities:
                agents = self.discovery_manager.discover_agents(capability=capability)
                suitable_agents.extend([a for a in agents if a.agent_id not in task_def.excluded_agents])
        else:
            # Tüm agent'ları al
            agents = self.discovery_manager.discover_agents()
            suitable_agents = [a for a in agents if a.agent_id not in task_def.excluded_agents]

        if not suitable_agents:
            return None

        # Load balancing ile en uygun agent'ı seç
        return self._select_best_agent(suitable_agents, task_def)

    def _select_best_agent(self, agents: List[ServiceInfo], task_def: TaskDefinition) -> Optional[ServiceInfo]:
        """
        Agent'lar arasından en uygun olanını seç

        Args:
            agents: Uygun agent'lar
            task_def: Task definition

        Returns:
            Optional[ServiceInfo]: En uygun agent
        """
        if not agents:
            return None

        # Performance-based selection
        best_agent = None
        best_score = -1

        for agent in agents:
            # Agent performance'ını al
            perf = self.agent_performance[agent.agent_id]

            # Current load'ı hesapla
            current_load = len(self.agent_assignments[agent.agent_id])

            # Score hesapla (success rate - current load)
            score = perf['success_rate'] - (current_load * 10)  # Load penalty

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent or agents[0]  # Fallback to first agent

    async def _assign_task_to_agent(self, task_def: TaskDefinition, agent: ServiceInfo):
        """
        Task'ı agent'a assign et

        Args:
            task_def: Task definition
            agent: Selected agent
        """
        try:
            # Task execution'ı başlat
            execution = self.task_scheduler.start_task_execution(
                task_def, agent.agent_id, agent.service_id
            )

            # Assignment tracking'i güncelle
            self.agent_assignments[agent.agent_id].add(task_def.task_id)
            self.task_assignments[task_def.task_id] = agent.agent_id

            # Agent performance tracking'i güncelle
            self.agent_performance[agent.agent_id]['total_tasks'] += 1

            # Simulated task execution (gerçek implementasyonda agent'a HTTP request gönderilir)
            asyncio.create_task(self._simulate_task_execution(task_def, agent, execution))

            print(f"📋 Task assigned: {task_def.task_name} -> {agent.agent_id}")

        except Exception as e:
            print(f"❌ Task assignment error: {e}")
            # Task'ı geri scheduler'a koy
            self.task_scheduler.submit_task(task_def)

    async def _simulate_task_execution(self, task_def: TaskDefinition, agent: ServiceInfo, execution: TaskExecution):
        """
        Task execution simülasyonu (demo için)

        Args:
            task_def: Task definition
            agent: Assigned agent
            execution: Task execution
        """
        try:
            # Simulated execution time
            import random
            execution_time = random.uniform(1.0, 5.0)

            # Progress updates
            for progress in [25, 50, 75, 90]:
                await asyncio.sleep(execution_time / 4)
                execution.update_progress(progress, f"Processing... {progress}%")

            # Simulated success/failure
            success_rate = self.agent_performance[agent.agent_id].get('success_rate', 90.0)
            if random.uniform(0, 100) < success_rate:
                # Success
                output_data = {
                    'result': f"Task {task_def.task_name} completed successfully",
                    'execution_time': execution_time,
                    'agent_id': agent.agent_id
                }

                self.task_scheduler.complete_task_execution(task_def.task_id, output_data)
                self.agent_performance[agent.agent_id]['completed_tasks'] += 1
            else:
                # Failure
                error_message = f"Simulated failure for task {task_def.task_name}"
                self.task_scheduler.fail_task_execution(task_def.task_id, error_message)
                self.agent_performance[agent.agent_id]['failed_tasks'] += 1

            # Update agent performance
            self._update_agent_performance(agent.agent_id)

            # Clean up assignment tracking
            self.agent_assignments[agent.agent_id].discard(task_def.task_id)
            if task_def.task_id in self.task_assignments:
                del self.task_assignments[task_def.task_id]

        except Exception as e:
            print(f"❌ Task execution simulation error: {e}")
            self.task_scheduler.fail_task_execution(task_def.task_id, str(e))

    def _update_agent_performance(self, agent_id: str):
        """Agent performance'ını güncelle"""
        perf = self.agent_performance[agent_id]

        if perf['total_tasks'] > 0:
            perf['success_rate'] = (perf['completed_tasks'] / perf['total_tasks']) * 100
        else:
            perf['success_rate'] = 100.0

    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Orchestrator istatistiklerini getir"""
        return {
            'running': self.running,
            'stats': self.orchestrator_stats.copy(),
            'scheduler_stats': self.task_scheduler.get_scheduler_stats(),
            'agent_assignments': {
                agent_id: list(task_ids) for agent_id, task_ids in self.agent_assignments.items()
            },
            'agent_performance': dict(self.agent_performance)
        }

    def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """Agent'ın workload'ını getir"""
        return {
            'agent_id': agent_id,
            'current_tasks': list(self.agent_assignments[agent_id]),
            'task_count': len(self.agent_assignments[agent_id]),
            'performance': self.agent_performance[agent_id].copy()
        }


@dataclass
class ConsensusProposal:
    """
    Consensus Proposal Structure

    Distributed decision making için proposal veri yapısı.
    """
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    proposer_id: str = ""
    proposal_type: str = "decision"
    proposal_data: Dict[str, Any] = field(default_factory=dict)

    # Consensus parameters
    consensus_type: ConsensusType = ConsensusType.MAJORITY
    required_votes: int = 0
    timeout: float = 30.0  # 30 seconds default

    # Voting state
    votes: Dict[str, bool] = field(default_factory=dict)  # agent_id -> vote (True/False)
    vote_weights: Dict[str, float] = field(default_factory=dict)  # agent_id -> weight

    # Status
    status: str = "pending"  # pending, accepted, rejected, timeout
    created_time: float = field(default_factory=time.time)
    decision_time: Optional[float] = None

    def add_vote(self, agent_id: str, vote: bool, weight: float = 1.0):
        """Vote ekle"""
        self.votes[agent_id] = vote
        self.vote_weights[agent_id] = weight

    def get_vote_summary(self) -> Dict[str, Any]:
        """Vote özetini getir"""
        total_votes = len(self.votes)
        yes_votes = sum(1 for vote in self.votes.values() if vote)
        no_votes = total_votes - yes_votes

        # Weighted votes
        total_weight = sum(self.vote_weights.values())
        yes_weight = sum(weight for agent_id, weight in self.vote_weights.items()
                        if self.votes.get(agent_id, False))
        no_weight = total_weight - yes_weight

        return {
            'total_votes': total_votes,
            'yes_votes': yes_votes,
            'no_votes': no_votes,
            'total_weight': total_weight,
            'yes_weight': yes_weight,
            'no_weight': no_weight,
            'yes_percentage': (yes_votes / max(1, total_votes)) * 100,
            'yes_weight_percentage': (yes_weight / max(1, total_weight)) * 100
        }

    def check_consensus(self) -> bool:
        """Consensus'ın sağlanıp sağlanmadığını kontrol et"""
        summary = self.get_vote_summary()

        if self.consensus_type == ConsensusType.MAJORITY:
            return summary['yes_votes'] > summary['no_votes']
        elif self.consensus_type == ConsensusType.UNANIMOUS:
            return summary['yes_votes'] == summary['total_votes'] and summary['total_votes'] > 0
        elif self.consensus_type == ConsensusType.WEIGHTED:
            return summary['yes_weight'] > summary['no_weight']
        else:
            return summary['yes_votes'] >= self.required_votes

    def to_dict(self) -> Dict[str, Any]:
        """Proposal'ı dictionary'ye çevir"""
        return {
            'proposal_id': self.proposal_id,
            'proposer_id': self.proposer_id,
            'proposal_type': self.proposal_type,
            'proposal_data': self.proposal_data,
            'consensus_type': self.consensus_type.value,
            'required_votes': self.required_votes,
            'timeout': self.timeout,
            'votes': self.votes,
            'vote_weights': self.vote_weights,
            'status': self.status,
            'created_time': self.created_time,
            'decision_time': self.decision_time,
            'vote_summary': self.get_vote_summary()
        }


class ConsensusManager:
    """
    Consensus Manager - Distributed Decision Making

    Agent'lar arasında distributed consensus algorithms
    ile karar verme süreçlerini yöneten sistem.
    """

    def __init__(self, discovery_manager: Optional[ServiceDiscoveryManager] = None):
        """
        Consensus Manager başlatıcı

        Args:
            discovery_manager: Service discovery manager referansı
        """
        self.discovery_manager = discovery_manager

        # Consensus state
        self.running = False
        self.consensus_task = None

        # Proposal storage
        self.active_proposals: Dict[str, ConsensusProposal] = {}  # proposal_id -> proposal
        self.completed_proposals: Dict[str, ConsensusProposal] = {}  # proposal_id -> proposal

        # Agent participation tracking
        self.agent_participation: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_proposals': 0,
            'votes_cast': 0,
            'participation_rate': 0.0,
            'agreement_rate': 0.0
        })

        # Statistics
        self.consensus_stats = {
            'total_proposals': 0,
            'accepted_proposals': 0,
            'rejected_proposals': 0,
            'timeout_proposals': 0,
            'average_decision_time': 0.0,
            'consensus_success_rate': 0.0
        }

        print("🤝 Consensus Manager initialized")

    async def start(self):
        """Consensus manager'ı başlat"""
        if self.running:
            return

        self.running = True

        # Consensus task'ını başlat
        self.consensus_task = asyncio.create_task(self._consensus_loop())

        print("🚀 Consensus Manager started")

    async def stop(self):
        """Consensus manager'ı durdur"""
        if not self.running:
            return

        self.running = False

        # Consensus task'ını durdur
        if self.consensus_task:
            self.consensus_task.cancel()
            try:
                await self.consensus_task
            except asyncio.CancelledError:
                pass

        print("🛑 Consensus Manager stopped")

    async def propose_decision(self,
                              proposer_id: str,
                              proposal_type: str,
                              proposal_data: Dict[str, Any],
                              consensus_type: ConsensusType = ConsensusType.MAJORITY,
                              timeout: float = 30.0) -> str:
        """
        Yeni bir decision proposal oluştur

        Args:
            proposer_id: Proposal'ı yapan agent ID
            proposal_type: Proposal tipi
            proposal_data: Proposal verisi
            consensus_type: Consensus algoritması
            timeout: Timeout süresi

        Returns:
            str: Proposal ID
        """
        proposal = ConsensusProposal(
            proposer_id=proposer_id,
            proposal_type=proposal_type,
            proposal_data=proposal_data,
            consensus_type=consensus_type,
            timeout=timeout
        )

        # Required votes'u hesapla
        if self.discovery_manager:
            agents = self.discovery_manager.discover_agents()
            if consensus_type == ConsensusType.MAJORITY:
                proposal.required_votes = len(agents) // 2 + 1
            elif consensus_type == ConsensusType.UNANIMOUS:
                proposal.required_votes = len(agents)
            else:
                proposal.required_votes = max(1, len(agents) // 2)
        else:
            proposal.required_votes = 1

        # Proposal'ı active proposals'a ekle
        self.active_proposals[proposal.proposal_id] = proposal
        self.consensus_stats['total_proposals'] += 1

        print(f"📋 Consensus proposal created: {proposal_type} ({proposal.proposal_id})")

        # Agent'lara proposal'ı gönder (simulated)
        await self._broadcast_proposal(proposal)

        return proposal.proposal_id

    async def cast_vote(self, proposal_id: str, agent_id: str, vote: bool, weight: float = 1.0) -> bool:
        """
        Proposal'a vote ver

        Args:
            proposal_id: Proposal ID
            agent_id: Vote veren agent ID
            vote: Vote (True/False)
            weight: Vote weight'i

        Returns:
            bool: Vote verme başarısı
        """
        if proposal_id not in self.active_proposals:
            return False

        proposal = self.active_proposals[proposal_id]

        # Vote'u ekle
        proposal.add_vote(agent_id, vote, weight)

        # Agent participation'ı güncelle
        self.agent_participation[agent_id]['votes_cast'] += 1

        print(f"🗳️ Vote cast: {agent_id} -> {vote} for {proposal_id}")

        # Consensus kontrolü
        if proposal.check_consensus():
            await self._finalize_proposal(proposal, "accepted")

        return True

    async def _broadcast_proposal(self, proposal: ConsensusProposal):
        """
        Proposal'ı tüm agent'lara gönder (simulated)

        Args:
            proposal: Consensus proposal
        """
        if not self.discovery_manager:
            return

        agents = self.discovery_manager.discover_agents()

        for agent in agents:
            # Agent participation'ı güncelle
            self.agent_participation[agent.agent_id]['total_proposals'] += 1

            # Simulated vote (gerçek implementasyonda HTTP request gönderilir)
            asyncio.create_task(self._simulate_agent_vote(proposal, agent.agent_id))

    async def _simulate_agent_vote(self, proposal: ConsensusProposal, agent_id: str):
        """
        Agent vote simülasyonu (demo için)

        Args:
            proposal: Consensus proposal
            agent_id: Agent ID
        """
        try:
            # Simulated thinking time
            import random
            await asyncio.sleep(random.uniform(1.0, 5.0))

            # Simulated vote decision (80% yes, 20% no)
            vote = random.uniform(0, 100) < 80
            weight = random.uniform(0.5, 2.0)

            await self.cast_vote(proposal.proposal_id, agent_id, vote, weight)

        except Exception as e:
            print(f"❌ Simulated vote error: {e}")

    async def _consensus_loop(self):
        """Consensus monitoring döngüsü"""
        while self.running:
            try:
                await asyncio.sleep(1.0)  # 1 saniye aralıklarla kontrol et

                if not self.running:
                    break

                # Timeout olan proposal'ları kontrol et
                await self._check_proposal_timeouts()

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Consensus loop error: {e}")

    async def _check_proposal_timeouts(self):
        """Timeout olan proposal'ları kontrol et"""
        current_time = time.time()
        timeout_proposals = []

        for proposal_id, proposal in self.active_proposals.items():
            if (current_time - proposal.created_time) > proposal.timeout:
                timeout_proposals.append(proposal)

        # Timeout olan proposal'ları finalize et
        for proposal in timeout_proposals:
            await self._finalize_proposal(proposal, "timeout")

    async def _finalize_proposal(self, proposal: ConsensusProposal, status: str):
        """
        Proposal'ı finalize et

        Args:
            proposal: Consensus proposal
            status: Final status (accepted, rejected, timeout)
        """
        proposal.status = status
        proposal.decision_time = time.time()

        # Active'den completed'a taşı
        if proposal.proposal_id in self.active_proposals:
            del self.active_proposals[proposal.proposal_id]
        self.completed_proposals[proposal.proposal_id] = proposal

        # İstatistikleri güncelle
        if status == "accepted":
            self.consensus_stats['accepted_proposals'] += 1
        elif status == "rejected":
            self.consensus_stats['rejected_proposals'] += 1
        elif status == "timeout":
            self.consensus_stats['timeout_proposals'] += 1

        # Decision time'ı güncelle
        decision_time = proposal.decision_time - proposal.created_time
        total_decisions = (self.consensus_stats['accepted_proposals'] +
                          self.consensus_stats['rejected_proposals'] +
                          self.consensus_stats['timeout_proposals'])

        if total_decisions > 0:
            self.consensus_stats['average_decision_time'] = (
                (self.consensus_stats['average_decision_time'] * (total_decisions - 1) + decision_time) /
                total_decisions
            )

        # Success rate'i güncelle
        successful_decisions = (self.consensus_stats['accepted_proposals'] +
                               self.consensus_stats['rejected_proposals'])
        if total_decisions > 0:
            self.consensus_stats['consensus_success_rate'] = (successful_decisions / total_decisions) * 100

        print(f"✅ Consensus proposal finalized: {proposal.proposal_id} -> {status}")

    def get_proposal_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Proposal durumunu getir

        Args:
            proposal_id: Proposal ID

        Returns:
            Optional[Dict[str, Any]]: Proposal durumu
        """
        # Active proposal'larda ara
        if proposal_id in self.active_proposals:
            return self.active_proposals[proposal_id].to_dict()

        # Completed proposal'larda ara
        if proposal_id in self.completed_proposals:
            return self.completed_proposals[proposal_id].to_dict()

        return None

    def get_consensus_stats(self) -> Dict[str, Any]:
        """Consensus istatistiklerini getir"""
        return {
            'running': self.running,
            'active_proposals': len(self.active_proposals),
            'completed_proposals': len(self.completed_proposals),
            'stats': self.consensus_stats.copy(),
            'agent_participation': dict(self.agent_participation)
        }

    def get_active_proposals(self) -> List[Dict[str, Any]]:
        """Aktif proposal'ları getir"""
        return [proposal.to_dict() for proposal in self.active_proposals.values()]


class DistributedTaskOrchestrationManager:
    """
    Distributed Task Orchestration Manager - Integrated System

    Task Orchestrator ve Consensus Manager'ı entegre eden
    ana distributed task coordination sistemi.
    """

    def __init__(self, discovery_manager: Optional[ServiceDiscoveryManager] = None):
        """
        Distributed Task Orchestration Manager başlatıcı

        Args:
            discovery_manager: Service discovery manager referansı
        """
        self.discovery_manager = discovery_manager

        # Core components
        self.task_orchestrator = TaskOrchestrator(discovery_manager)
        self.consensus_manager = ConsensusManager(discovery_manager)

        # Manager state
        self.running = False
        self.manager_id = f"orchestration_manager_{int(time.time())}"

        # Statistics
        self.manager_stats = {
            'start_time': 0,
            'uptime': 0,
            'total_tasks_processed': 0,
            'total_decisions_made': 0,
            'coordination_efficiency': 0.0
        }

        print(f"🎭 Distributed Task Orchestration Manager {self.manager_id} initialized")

    async def start(self):
        """Orchestration manager'ı başlat"""
        if self.running:
            return

        self.running = True
        self.manager_stats['start_time'] = time.time()

        # Core component'leri başlat
        await self.task_orchestrator.start()
        await self.consensus_manager.start()

        print(f"🚀 Distributed Task Orchestration Manager {self.manager_id} started")

    async def stop(self):
        """Orchestration manager'ı durdur"""
        if not self.running:
            return

        self.running = False

        # Core component'leri durdur
        await self.consensus_manager.stop()
        await self.task_orchestrator.stop()

        print(f"🛑 Distributed Task Orchestration Manager {self.manager_id} stopped")

    async def submit_distributed_task(self,
                                     task_name: str,
                                     task_type: str,
                                     input_data: Dict[str, Any],
                                     required_capabilities: List[str] = None,
                                     priority: TaskPriority = TaskPriority.NORMAL,
                                     timeout: float = 300.0,
                                     dependencies: List[str] = None,
                                     require_consensus: bool = False,
                                     consensus_type: ConsensusType = ConsensusType.MAJORITY) -> str:
        """
        Distributed task gönder

        Args:
            task_name: Task adı
            task_type: Task tipi
            input_data: Input verisi
            required_capabilities: Gerekli yetenekler
            priority: Task önceliği
            timeout: Timeout süresi
            dependencies: Dependency'ler
            require_consensus: Consensus gerekli mi
            consensus_type: Consensus tipi

        Returns:
            str: Task ID
        """
        # Task definition oluştur
        task_def = TaskDefinition(
            task_name=task_name,
            task_type=task_type,
            input_data=input_data,
            required_capabilities=required_capabilities or [],
            priority=priority,
            timeout=timeout,
            dependencies=dependencies or []
        )

        # Consensus gerekiyorsa önce consensus al
        if require_consensus:
            proposal_data = {
                'action': 'submit_task',
                'task_definition': task_def.to_dict()
            }

            proposal_id = await self.consensus_manager.propose_decision(
                proposer_id="orchestration_manager",
                proposal_type="task_submission",
                proposal_data=proposal_data,
                consensus_type=consensus_type,
                timeout=30.0
            )

            # Consensus sonucunu bekle (simulated)
            await asyncio.sleep(10.0)  # Consensus için bekleme süresi

            proposal_status = self.consensus_manager.get_proposal_status(proposal_id)
            if not proposal_status or proposal_status['status'] != 'accepted':
                raise Exception(f"Task submission rejected by consensus: {proposal_id}")

        # Task'ı orchestrator'a gönder
        task_id = await self.task_orchestrator.submit_task(task_def)
        self.manager_stats['total_tasks_processed'] += 1

        print(f"🎭 Distributed task submitted: {task_name} ({task_id})")
        return task_id

    async def cancel_distributed_task(self, task_id: str, require_consensus: bool = False) -> bool:
        """
        Distributed task'ı iptal et

        Args:
            task_id: Task ID
            require_consensus: Consensus gerekli mi

        Returns:
            bool: İptal başarısı
        """
        # Consensus gerekiyorsa önce consensus al
        if require_consensus:
            proposal_data = {
                'action': 'cancel_task',
                'task_id': task_id
            }

            proposal_id = await self.consensus_manager.propose_decision(
                proposer_id="orchestration_manager",
                proposal_type="task_cancellation",
                proposal_data=proposal_data,
                consensus_type=ConsensusType.MAJORITY,
                timeout=15.0
            )

            # Consensus sonucunu bekle (simulated)
            await asyncio.sleep(5.0)

            proposal_status = self.consensus_manager.get_proposal_status(proposal_id)
            if not proposal_status or proposal_status['status'] != 'accepted':
                return False

        # Task'ı iptal et
        return await self.task_orchestrator.cancel_task(task_id)

    async def make_distributed_decision(self,
                                       decision_type: str,
                                       decision_data: Dict[str, Any],
                                       consensus_type: ConsensusType = ConsensusType.MAJORITY,
                                       timeout: float = 30.0) -> str:
        """
        Distributed decision yap

        Args:
            decision_type: Decision tipi
            decision_data: Decision verisi
            consensus_type: Consensus tipi
            timeout: Timeout süresi

        Returns:
            str: Proposal ID
        """
        proposal_id = await self.consensus_manager.propose_decision(
            proposer_id="orchestration_manager",
            proposal_type=decision_type,
            proposal_data=decision_data,
            consensus_type=consensus_type,
            timeout=timeout
        )

        self.manager_stats['total_decisions_made'] += 1

        print(f"🤝 Distributed decision initiated: {decision_type} ({proposal_id})")
        return proposal_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Task durumunu getir

        Args:
            task_id: Task ID

        Returns:
            Optional[Dict[str, Any]]: Task durumu
        """
        return self.task_orchestrator.get_task_status(task_id)

    def get_decision_status(self, proposal_id: str) -> Optional[Dict[str, Any]]:
        """
        Decision durumunu getir

        Args:
            proposal_id: Proposal ID

        Returns:
            Optional[Dict[str, Any]]: Decision durumu
        """
        return self.consensus_manager.get_proposal_status(proposal_id)

    def get_agent_workload(self, agent_id: str) -> Dict[str, Any]:
        """
        Agent workload'ını getir

        Args:
            agent_id: Agent ID

        Returns:
            Dict[str, Any]: Agent workload
        """
        return self.task_orchestrator.get_agent_workload(agent_id)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı sistem istatistiklerini getir"""
        current_time = time.time()
        if self.running:
            self.manager_stats['uptime'] = current_time - self.manager_stats['start_time']

        # Coordination efficiency hesapla
        orchestrator_stats = self.task_orchestrator.get_orchestrator_stats()
        consensus_stats = self.consensus_manager.get_consensus_stats()

        total_operations = (self.manager_stats['total_tasks_processed'] +
                           self.manager_stats['total_decisions_made'])

        if total_operations > 0:
            successful_tasks = orchestrator_stats['scheduler_stats']['stats']['total_tasks_completed']
            successful_decisions = consensus_stats['stats']['accepted_proposals']

            self.manager_stats['coordination_efficiency'] = (
                (successful_tasks + successful_decisions) / total_operations
            ) * 100

        return {
            'manager_id': self.manager_id,
            'running': self.running,
            'manager_stats': self.manager_stats.copy(),
            'orchestrator_stats': orchestrator_stats,
            'consensus_stats': consensus_stats
        }

    def get_active_tasks(self) -> List[Dict[str, Any]]:
        """Aktif task'ları getir"""
        scheduler_stats = self.task_orchestrator.get_orchestrator_stats()['scheduler_stats']

        active_tasks = []

        # Pending tasks
        for _ in range(scheduler_stats['pending_tasks']):
            active_tasks.append({'status': 'pending'})

        # Running tasks
        for _ in range(scheduler_stats['running_tasks']):
            active_tasks.append({'status': 'running'})

        return active_tasks

    def get_active_decisions(self) -> List[Dict[str, Any]]:
        """Aktif decision'ları getir"""
        return self.consensus_manager.get_active_proposals()

    async def coordinate_multi_agent_workflow(self,
                                            workflow_name: str,
                                            workflow_tasks: List[Dict[str, Any]],
                                            require_consensus: bool = True) -> Dict[str, Any]:
        """
        Multi-agent workflow coordination

        Args:
            workflow_name: Workflow adı
            workflow_tasks: Workflow task'ları
            require_consensus: Consensus gerekli mi

        Returns:
            Dict[str, Any]: Workflow sonucu
        """
        workflow_id = str(uuid.uuid4())

        print(f"🔄 Starting multi-agent workflow: {workflow_name} ({workflow_id})")

        # Workflow için consensus al
        if require_consensus:
            proposal_data = {
                'action': 'start_workflow',
                'workflow_id': workflow_id,
                'workflow_name': workflow_name,
                'task_count': len(workflow_tasks)
            }

            proposal_id = await self.make_distributed_decision(
                "workflow_approval",
                proposal_data,
                ConsensusType.MAJORITY,
                30.0
            )

            # Consensus bekle
            await asyncio.sleep(10.0)

            proposal_status = self.get_decision_status(proposal_id)
            if not proposal_status or proposal_status['status'] != 'accepted':
                return {
                    'workflow_id': workflow_id,
                    'status': 'rejected',
                    'reason': 'Workflow rejected by consensus'
                }

        # Task'ları sırayla gönder
        submitted_tasks = []

        for i, task_config in enumerate(workflow_tasks):
            task_id = await self.submit_distributed_task(
                task_name=f"{workflow_name}_task_{i+1}",
                task_type=task_config.get('type', 'generic'),
                input_data=task_config.get('input_data', {}),
                required_capabilities=task_config.get('capabilities', []),
                priority=TaskPriority(task_config.get('priority', TaskPriority.NORMAL.value)),
                dependencies=task_config.get('dependencies', []),
                require_consensus=False  # Workflow zaten onaylandı
            )

            submitted_tasks.append(task_id)

            # Task'lar arası delay
            await asyncio.sleep(0.5)

        return {
            'workflow_id': workflow_id,
            'status': 'started',
            'submitted_tasks': submitted_tasks,
            'task_count': len(submitted_tasks)
        }