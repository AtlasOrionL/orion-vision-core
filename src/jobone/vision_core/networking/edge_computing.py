"""
🌐 Orion Vision Core - Edge Computing Infrastructure
Distributed edge computing and processing capabilities

This module provides edge computing features:
- Edge node management and orchestration
- Distributed AI processing capabilities
- Edge-cloud hybrid architecture
- Resource optimization and scheduling
- Edge security and data privacy

Sprint 9.3: Advanced Networking and Edge Computing
"""

import asyncio
import logging
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EdgeNodeType(Enum):
    """Edge node types"""
    COMPUTE = "compute"
    STORAGE = "storage"
    GATEWAY = "gateway"
    SENSOR = "sensor"
    HYBRID = "hybrid"

class EdgeNodeStatus(Enum):
    """Edge node status"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    INITIALIZING = "initializing"

class ProcessingPriority(Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    REAL_TIME = "real_time"

class ResourceType(Enum):
    """Resource types"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"

@dataclass
class EdgeNodeResources:
    """Edge node resource specifications"""
    cpu_cores: int = 4
    memory_gb: float = 8.0
    storage_gb: float = 100.0
    network_mbps: float = 100.0
    gpu_count: int = 0
    available_cpu: float = 100.0  # Percentage
    available_memory: float = 100.0  # Percentage
    available_storage: float = 100.0  # Percentage

@dataclass
class EdgeNode:
    """Edge computing node"""
    node_id: str
    name: str
    node_type: EdgeNodeType
    location: str
    resources: EdgeNodeResources
    status: EdgeNodeStatus = EdgeNodeStatus.INITIALIZING
    last_heartbeat: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    workloads: List[str] = field(default_factory=list)

@dataclass
class EdgeCluster:
    """Edge computing cluster"""
    cluster_id: str
    name: str
    nodes: List[EdgeNode] = field(default_factory=list)
    load_balancer_config: Dict[str, Any] = field(default_factory=dict)
    auto_scaling_enabled: bool = True
    min_nodes: int = 1
    max_nodes: int = 10

@dataclass
class EdgeWorkload:
    """Edge computing workload"""
    workload_id: str
    name: str
    priority: ProcessingPriority
    resource_requirements: EdgeNodeResources
    code: Optional[str] = None
    data: Optional[Any] = None
    assigned_node: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Any] = None

class EdgeComputing:
    """
    Edge computing infrastructure manager for Orion Vision Core.
    
    Provides distributed edge computing capabilities with:
    - Edge node management and orchestration
    - Distributed processing and load balancing
    - Resource optimization and scheduling
    - Edge-cloud hybrid architecture
    - Fault tolerance and recovery
    """
    
    def __init__(self):
        """Initialize the edge computing manager."""
        
        # Edge infrastructure
        self.nodes: Dict[str, EdgeNode] = {}
        self.clusters: Dict[str, EdgeCluster] = {}
        self.workloads: Dict[str, EdgeWorkload] = {}
        
        # Scheduling and orchestration
        self.scheduler_enabled = True
        self.auto_scaling_enabled = True
        self.load_balancing_enabled = True
        
        # Performance metrics
        self.metrics = {
            'total_nodes': 0,
            'active_nodes': 0,
            'total_workloads': 0,
            'completed_workloads': 0,
            'average_processing_time': 0.0,
            'resource_utilization': {
                'cpu': 0.0,
                'memory': 0.0,
                'storage': 0.0
            }
        }
        
        # Event handlers
        self.node_handlers: List[Callable] = []
        self.workload_handlers: List[Callable] = []
        self.cluster_handlers: List[Callable] = []
        
        # Background tasks
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.scheduler_task: Optional[asyncio.Task] = None
        
        logger.info("🌐 Edge Computing manager initialized")
    
    async def initialize(self) -> bool:
        """
        Initialize the edge computing infrastructure.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Start heartbeat monitoring
            await self._start_heartbeat_monitoring()
            
            # Start workload scheduler
            await self._start_workload_scheduler()
            
            # Initialize default cluster
            await self._create_default_cluster()
            
            logger.info("✅ Edge Computing infrastructure initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Edge Computing initialization failed: {e}")
            return False
    
    async def _start_heartbeat_monitoring(self):
        """Start heartbeat monitoring for edge nodes"""
        
        if self.heartbeat_task and not self.heartbeat_task.done():
            return
        
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        logger.info("💓 Heartbeat monitoring started")
    
    async def _heartbeat_loop(self):
        """Heartbeat monitoring loop"""
        
        while True:
            try:
                current_time = datetime.now()
                
                for node_id, node in self.nodes.items():
                    if node.last_heartbeat:
                        time_since_heartbeat = current_time - node.last_heartbeat
                        
                        # Mark node as offline if no heartbeat for 60 seconds
                        if time_since_heartbeat.total_seconds() > 60:
                            if node.status == EdgeNodeStatus.ONLINE:
                                node.status = EdgeNodeStatus.OFFLINE
                                logger.warning(f"📴 Node {node_id} marked as offline")
                                
                                # Trigger node handlers
                                for handler in self.node_handlers:
                                    try:
                                        await handler("node_offline", node)
                                    except Exception as e:
                                        logger.error(f"❌ Node handler error: {e}")
                
                # Wait before next heartbeat check
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Heartbeat monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _start_workload_scheduler(self):
        """Start workload scheduler"""
        
        if not self.scheduler_enabled:
            return
        
        if self.scheduler_task and not self.scheduler_task.done():
            return
        
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        logger.info("📋 Workload scheduler started")
    
    async def _scheduler_loop(self):
        """Workload scheduling loop"""
        
        while self.scheduler_enabled:
            try:
                # Find pending workloads
                pending_workloads = [
                    workload for workload in self.workloads.values()
                    if workload.status == "pending"
                ]
                
                # Schedule workloads
                for workload in pending_workloads:
                    await self._schedule_workload(workload)
                
                # Wait before next scheduling cycle
                await asyncio.sleep(5)  # Schedule every 5 seconds
                
            except Exception as e:
                logger.error(f"❌ Scheduler error: {e}")
                await asyncio.sleep(10)
    
    async def _schedule_workload(self, workload: EdgeWorkload):
        """Schedule a workload to an appropriate edge node"""
        
        try:
            # Find suitable nodes
            suitable_nodes = await self._find_suitable_nodes(workload)
            
            if not suitable_nodes:
                logger.warning(f"⚠️ No suitable nodes for workload {workload.workload_id}")
                return
            
            # Select best node (simple algorithm - first available)
            selected_node = suitable_nodes[0]
            
            # Assign workload to node
            workload.assigned_node = selected_node.node_id
            workload.status = "assigned"
            workload.started_at = datetime.now()
            
            # Add to node's workload list
            selected_node.workloads.append(workload.workload_id)
            
            # Update resource allocation
            await self._allocate_resources(selected_node, workload)
            
            # Start workload execution
            asyncio.create_task(self._execute_workload(workload, selected_node))
            
            logger.info(f"📋 Workload {workload.workload_id} scheduled to node {selected_node.node_id}")
            
        except Exception as e:
            logger.error(f"❌ Workload scheduling error: {e}")
            workload.status = "error"
    
    async def _find_suitable_nodes(self, workload: EdgeWorkload) -> List[EdgeNode]:
        """Find nodes suitable for the workload"""
        
        suitable_nodes = []
        
        for node in self.nodes.values():
            if (node.status == EdgeNodeStatus.ONLINE and
                await self._check_resource_availability(node, workload)):
                suitable_nodes.append(node)
        
        # Sort by available resources (simple scoring)
        suitable_nodes.sort(key=lambda n: n.resources.available_cpu, reverse=True)
        
        return suitable_nodes
    
    async def _check_resource_availability(self, node: EdgeNode, workload: EdgeWorkload) -> bool:
        """Check if node has sufficient resources for workload"""
        
        required = workload.resource_requirements
        available = node.resources
        
        # Check CPU
        cpu_needed = (required.cpu_cores / available.cpu_cores) * 100
        if cpu_needed > available.available_cpu:
            return False
        
        # Check memory
        memory_needed = (required.memory_gb / available.memory_gb) * 100
        if memory_needed > available.available_memory:
            return False
        
        # Check storage
        storage_needed = (required.storage_gb / available.storage_gb) * 100
        if storage_needed > available.available_storage:
            return False
        
        return True
    
    async def _allocate_resources(self, node: EdgeNode, workload: EdgeWorkload):
        """Allocate resources for workload on node"""
        
        required = workload.resource_requirements
        
        # Calculate resource usage percentages
        cpu_usage = (required.cpu_cores / node.resources.cpu_cores) * 100
        memory_usage = (required.memory_gb / node.resources.memory_gb) * 100
        storage_usage = (required.storage_gb / node.resources.storage_gb) * 100
        
        # Update available resources
        node.resources.available_cpu -= cpu_usage
        node.resources.available_memory -= memory_usage
        node.resources.available_storage -= storage_usage
        
        logger.info(f"📊 Resources allocated on node {node.node_id}: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%, Storage {storage_usage:.1f}%")
    
    async def _execute_workload(self, workload: EdgeWorkload, node: EdgeNode):
        """Execute workload on edge node"""
        
        try:
            workload.status = "running"
            
            # Simulate workload execution
            execution_time = 2.0  # Base execution time
            
            # Adjust based on priority
            if workload.priority == ProcessingPriority.REAL_TIME:
                execution_time *= 0.5
            elif workload.priority == ProcessingPriority.HIGH:
                execution_time *= 0.7
            elif workload.priority == ProcessingPriority.LOW:
                execution_time *= 1.5
            
            await asyncio.sleep(execution_time)
            
            # Generate result
            workload.result = {
                'status': 'completed',
                'execution_time': execution_time,
                'node_id': node.node_id,
                'timestamp': datetime.now().isoformat()
            }
            
            workload.status = "completed"
            workload.completed_at = datetime.now()
            
            # Release resources
            await self._release_resources(node, workload)
            
            # Remove from node's workload list
            if workload.workload_id in node.workloads:
                node.workloads.remove(workload.workload_id)
            
            # Update metrics
            await self._update_metrics()
            
            # Trigger workload handlers
            for handler in self.workload_handlers:
                try:
                    await handler("workload_completed", workload)
                except Exception as e:
                    logger.error(f"❌ Workload handler error: {e}")
            
            logger.info(f"✅ Workload {workload.workload_id} completed on node {node.node_id}")
            
        except Exception as e:
            workload.status = "error"
            workload.result = {'error': str(e)}
            logger.error(f"❌ Workload execution error: {e}")
    
    async def _release_resources(self, node: EdgeNode, workload: EdgeWorkload):
        """Release resources after workload completion"""
        
        required = workload.resource_requirements
        
        # Calculate resource usage percentages
        cpu_usage = (required.cpu_cores / node.resources.cpu_cores) * 100
        memory_usage = (required.memory_gb / node.resources.memory_gb) * 100
        storage_usage = (required.storage_gb / node.resources.storage_gb) * 100
        
        # Release resources
        node.resources.available_cpu = min(100.0, node.resources.available_cpu + cpu_usage)
        node.resources.available_memory = min(100.0, node.resources.available_memory + memory_usage)
        node.resources.available_storage = min(100.0, node.resources.available_storage + storage_usage)
    
    async def _create_default_cluster(self):
        """Create default edge cluster"""
        
        default_cluster = EdgeCluster(
            cluster_id="default",
            name="Default Edge Cluster",
            auto_scaling_enabled=True,
            min_nodes=1,
            max_nodes=5
        )
        
        self.clusters["default"] = default_cluster
        logger.info("🏗️ Default edge cluster created")
    
    async def _update_metrics(self):
        """Update edge computing metrics"""
        
        self.metrics['total_nodes'] = len(self.nodes)
        self.metrics['active_nodes'] = len([n for n in self.nodes.values() if n.status == EdgeNodeStatus.ONLINE])
        self.metrics['total_workloads'] = len(self.workloads)
        self.metrics['completed_workloads'] = len([w for w in self.workloads.values() if w.status == "completed"])
        
        # Calculate resource utilization
        if self.nodes:
            total_cpu = sum(100 - n.resources.available_cpu for n in self.nodes.values())
            total_memory = sum(100 - n.resources.available_memory for n in self.nodes.values())
            total_storage = sum(100 - n.resources.available_storage for n in self.nodes.values())
            
            self.metrics['resource_utilization']['cpu'] = total_cpu / len(self.nodes)
            self.metrics['resource_utilization']['memory'] = total_memory / len(self.nodes)
            self.metrics['resource_utilization']['storage'] = total_storage / len(self.nodes)
    
    async def add_edge_node(self, node: EdgeNode) -> bool:
        """
        Add an edge node to the infrastructure.
        
        Args:
            node: Edge node to add
            
        Returns:
            True if node added successfully, False otherwise
        """
        try:
            self.nodes[node.node_id] = node
            node.status = EdgeNodeStatus.ONLINE
            node.last_heartbeat = datetime.now()
            
            # Add to default cluster
            if "default" in self.clusters:
                self.clusters["default"].nodes.append(node)
            
            await self._update_metrics()
            
            # Trigger node handlers
            for handler in self.node_handlers:
                try:
                    await handler("node_added", node)
                except Exception as e:
                    logger.error(f"❌ Node handler error: {e}")
            
            logger.info(f"🌐 Edge node added: {node.node_id} ({node.node_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to add edge node: {e}")
            return False
    
    async def remove_edge_node(self, node_id: str) -> bool:
        """
        Remove an edge node from the infrastructure.
        
        Args:
            node_id: Node ID to remove
            
        Returns:
            True if node removed successfully, False otherwise
        """
        try:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            
            # Cancel running workloads
            for workload_id in node.workloads.copy():
                if workload_id in self.workloads:
                    workload = self.workloads[workload_id]
                    workload.status = "cancelled"
                    workload.assigned_node = None
            
            # Remove from clusters
            for cluster in self.clusters.values():
                cluster.nodes = [n for n in cluster.nodes if n.node_id != node_id]
            
            # Remove node
            del self.nodes[node_id]
            
            await self._update_metrics()
            
            logger.info(f"🗑️ Edge node removed: {node_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove edge node: {e}")
            return False
    
    async def submit_workload(self, workload: EdgeWorkload) -> str:
        """
        Submit a workload for processing.
        
        Args:
            workload: Workload to submit
            
        Returns:
            Workload ID
        """
        try:
            self.workloads[workload.workload_id] = workload
            
            logger.info(f"📋 Workload submitted: {workload.workload_id} (priority: {workload.priority.value})")
            return workload.workload_id
            
        except Exception as e:
            logger.error(f"❌ Failed to submit workload: {e}")
            return ""
    
    async def get_workload_status(self, workload_id: str) -> Optional[Dict[str, Any]]:
        """Get workload status and result"""
        
        if workload_id not in self.workloads:
            return None
        
        workload = self.workloads[workload_id]
        
        return {
            'workload_id': workload.workload_id,
            'status': workload.status,
            'assigned_node': workload.assigned_node,
            'created_at': workload.created_at.isoformat(),
            'started_at': workload.started_at.isoformat() if workload.started_at else None,
            'completed_at': workload.completed_at.isoformat() if workload.completed_at else None,
            'result': workload.result
        }
    
    async def heartbeat(self, node_id: str) -> bool:
        """
        Process heartbeat from edge node.
        
        Args:
            node_id: Node ID sending heartbeat
            
        Returns:
            True if heartbeat processed, False otherwise
        """
        if node_id not in self.nodes:
            return False
        
        node = self.nodes[node_id]
        node.last_heartbeat = datetime.now()
        
        if node.status == EdgeNodeStatus.OFFLINE:
            node.status = EdgeNodeStatus.ONLINE
            logger.info(f"📡 Node {node_id} back online")
        
        return True
    
    def register_node_handler(self, handler: Callable):
        """Register node event handler"""
        self.node_handlers.append(handler)
        logger.info("📡 Registered node handler")
    
    def register_workload_handler(self, handler: Callable):
        """Register workload event handler"""
        self.workload_handlers.append(handler)
        logger.info("📡 Registered workload handler")
    
    def register_cluster_handler(self, handler: Callable):
        """Register cluster event handler"""
        self.cluster_handlers.append(handler)
        logger.info("📡 Registered cluster handler")
    
    def get_edge_metrics(self) -> Dict[str, Any]:
        """Get edge computing metrics"""
        return self.metrics.copy()
    
    def get_node_status(self) -> Dict[str, Any]:
        """Get status of all edge nodes"""
        
        node_status = {}
        for node_id, node in self.nodes.items():
            node_status[node_id] = {
                'name': node.name,
                'type': node.node_type.value,
                'status': node.status.value,
                'location': node.location,
                'workloads': len(node.workloads),
                'resources': {
                    'cpu_available': node.resources.available_cpu,
                    'memory_available': node.resources.available_memory,
                    'storage_available': node.resources.available_storage
                }
            }
        
        return node_status
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information"""
        
        cluster_info = {}
        for cluster_id, cluster in self.clusters.items():
            cluster_info[cluster_id] = {
                'name': cluster.name,
                'nodes': len(cluster.nodes),
                'auto_scaling': cluster.auto_scaling_enabled,
                'min_nodes': cluster.min_nodes,
                'max_nodes': cluster.max_nodes
            }
        
        return cluster_info
    
    def get_edge_info(self) -> Dict[str, Any]:
        """Get comprehensive edge computing information"""
        
        return {
            'infrastructure': {
                'total_nodes': len(self.nodes),
                'active_nodes': len([n for n in self.nodes.values() if n.status == EdgeNodeStatus.ONLINE]),
                'total_clusters': len(self.clusters)
            },
            'workloads': {
                'total': len(self.workloads),
                'pending': len([w for w in self.workloads.values() if w.status == "pending"]),
                'running': len([w for w in self.workloads.values() if w.status == "running"]),
                'completed': len([w for w in self.workloads.values() if w.status == "completed"])
            },
            'metrics': self.get_edge_metrics(),
            'nodes': self.get_node_status(),
            'clusters': self.get_cluster_info(),
            'configuration': {
                'scheduler_enabled': self.scheduler_enabled,
                'auto_scaling_enabled': self.auto_scaling_enabled,
                'load_balancing_enabled': self.load_balancing_enabled
            }
        }
    
    async def shutdown(self):
        """Shutdown edge computing infrastructure"""
        
        # Stop background tasks
        if self.heartbeat_task and not self.heartbeat_task.done():
            self.heartbeat_task.cancel()
            try:
                await self.heartbeat_task
            except asyncio.CancelledError:
                pass
        
        if self.scheduler_task and not self.scheduler_task.done():
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running workloads
        for workload in self.workloads.values():
            if workload.status == "running":
                workload.status = "cancelled"
        
        logger.info("🌐 Edge Computing infrastructure shutdown complete")
