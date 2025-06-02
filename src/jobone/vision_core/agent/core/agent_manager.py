"""
Agent Manager for Orion Vision Core

This module provides comprehensive agent lifecycle management including
creation, monitoring, and coordination of distributed agents.
Part of Sprint 9.1.1.1 Core Framework Optimization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import time
import threading
import uuid
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

from .agent_status import AgentStatus
from .agent_config import AgentConfig
from .agent_logger import AgentLogger


class AgentState(Enum):
    """Agent state enumeration"""
    CREATED = "created"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    TERMINATED = "terminated"


@dataclass
class AgentInfo:
    """Agent information data structure"""
    agent_id: str
    agent_name: str
    agent_type: str
    state: AgentState = AgentState.CREATED
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_time: float = field(default_factory=time.time)
    last_heartbeat: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent info to dictionary"""
        return {
            'agent_id': self.agent_id,
            'agent_name': self.agent_name,
            'agent_type': self.agent_type,
            'state': self.state.value,
            'capabilities': self.capabilities,
            'metadata': self.metadata,
            'created_time': self.created_time,
            'last_heartbeat': self.last_heartbeat
        }


class AgentManager:
    """
    Comprehensive Agent Management System
    
    Manages the complete lifecycle of agents including creation, monitoring,
    coordination, and cleanup with enterprise-grade reliability.
    """
    
    def __init__(self, metrics_collector=None, logger: Optional[AgentLogger] = None):
        """Initialize agent manager"""
        self.logger = logger or AgentLogger("agent_manager")
        self.metrics_collector = metrics_collector
        
        # Agent storage
        self.agents: Dict[str, AgentInfo] = {}
        self.agent_instances: Dict[str, Any] = {}
        self.agent_threads: Dict[str, threading.Thread] = {}
        
        # Configuration
        self.max_agents = 1000
        self.heartbeat_timeout = 30.0  # seconds
        self.cleanup_interval = 60.0   # seconds
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Monitoring
        self._monitoring_active = False
        self._monitoring_thread = None
        
        # Statistics
        self.stats = {
            'total_created': 0,
            'total_terminated': 0,
            'current_active': 0,
            'failed_creations': 0,
            'average_lifetime': 0.0
        }
        
        # Start monitoring
        self.start_monitoring()
        
        self.logger.info("Agent Manager initialized")
    
    def create_agent(self, agent_name: str, agent_type: str, 
                    capabilities: Optional[List[str]] = None,
                    config: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Create a new agent"""
        try:
            # Validate inputs
            if not agent_name or not agent_type:
                self.logger.error("Agent name and type are required")
                return None
            
            # Check limits
            with self._lock:
                if len(self.agents) >= self.max_agents:
                    self.logger.error("Maximum agent limit reached", max_agents=self.max_agents)
                    return None
            
            # Generate agent ID
            agent_id = str(uuid.uuid4())
            
            # Create agent info
            agent_info = AgentInfo(
                agent_id=agent_id,
                agent_name=agent_name,
                agent_type=agent_type,
                capabilities=capabilities or [],
                metadata=config or {}
            )
            
            # Store agent
            with self._lock:
                self.agents[agent_id] = agent_info
                self.stats['total_created'] += 1
                self.stats['current_active'] += 1
            
            # Initialize agent (mock implementation)
            agent_info.state = AgentState.INITIALIZING
            
            # Start agent (mock implementation)
            self._start_agent_instance(agent_id, agent_info)
            
            self.logger.info(
                "Agent created successfully",
                agent_id=agent_id,
                agent_name=agent_name,
                agent_type=agent_type
            )
            
            return agent_id
            
        except Exception as e:
            with self._lock:
                self.stats['failed_creations'] += 1
            self.logger.error("Agent creation failed", agent_name=agent_name, error=str(e))
            return None
    
    def _start_agent_instance(self, agent_id: str, agent_info: AgentInfo):
        """Start agent instance (mock implementation)"""
        try:
            # Mock agent instance creation
            mock_agent = {
                'id': agent_id,
                'name': agent_info.agent_name,
                'type': agent_info.agent_type,
                'running': True
            }
            
            self.agent_instances[agent_id] = mock_agent
            agent_info.state = AgentState.RUNNING
            
            # Start agent thread (mock)
            agent_thread = threading.Thread(
                target=self._agent_worker,
                args=(agent_id,),
                name=f"Agent-{agent_info.agent_name}",
                daemon=True
            )
            agent_thread.start()
            self.agent_threads[agent_id] = agent_thread
            
        except Exception as e:
            agent_info.state = AgentState.ERROR
            self.logger.error("Agent instance start failed", agent_id=agent_id, error=str(e))
    
    def _agent_worker(self, agent_id: str):
        """Agent worker thread (mock implementation)"""
        try:
            while agent_id in self.agents and self.agents[agent_id].state == AgentState.RUNNING:
                # Mock agent work
                time.sleep(1)
                
                # Update heartbeat
                with self._lock:
                    if agent_id in self.agents:
                        self.agents[agent_id].last_heartbeat = time.time()
                
        except Exception as e:
            self.logger.error("Agent worker error", agent_id=agent_id, error=str(e))
            if agent_id in self.agents:
                self.agents[agent_id].state = AgentState.ERROR
    
    def terminate_agent(self, agent_id: str) -> bool:
        """Terminate an agent"""
        try:
            with self._lock:
                if agent_id not in self.agents:
                    self.logger.error("Agent not found", agent_id=agent_id)
                    return False
                
                agent_info = self.agents[agent_id]
                agent_info.state = AgentState.STOPPING
            
            # Stop agent instance
            if agent_id in self.agent_instances:
                self.agent_instances[agent_id]['running'] = False
                del self.agent_instances[agent_id]
            
            # Wait for thread to finish
            if agent_id in self.agent_threads:
                thread = self.agent_threads[agent_id]
                thread.join(timeout=5.0)
                del self.agent_threads[agent_id]
            
            # Remove agent
            with self._lock:
                agent_info.state = AgentState.TERMINATED
                del self.agents[agent_id]
                self.stats['total_terminated'] += 1
                self.stats['current_active'] -= 1
            
            self.logger.info("Agent terminated successfully", agent_id=agent_id)
            return True
            
        except Exception as e:
            self.logger.error("Agent termination failed", agent_id=agent_id, error=str(e))
            return False
    
    def get_agent(self, agent_id: str) -> Optional[AgentInfo]:
        """Get agent information"""
        with self._lock:
            return self.agents.get(agent_id)
    
    def list_agents(self, agent_type: Optional[str] = None, 
                   state: Optional[AgentState] = None) -> List[AgentInfo]:
        """List agents with optional filtering"""
        with self._lock:
            agents = list(self.agents.values())
        
        # Apply filters
        if agent_type:
            agents = [a for a in agents if a.agent_type == agent_type]
        
        if state:
            agents = [a for a in agents if a.state == state]
        
        return agents
    
    def get_agent_count(self) -> int:
        """Get total number of active agents"""
        with self._lock:
            return len(self.agents)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent manager statistics"""
        with self._lock:
            return {
                'max_agents': self.max_agents,
                'heartbeat_timeout': self.heartbeat_timeout,
                'cleanup_interval': self.cleanup_interval,
                'monitoring_active': self._monitoring_active,
                'stats': self.stats.copy()
            }
    
    def start_monitoring(self):
        """Start agent monitoring"""
        if self._monitoring_active:
            return
        
        self._monitoring_active = True
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_worker,
            name="AgentMonitoring",
            daemon=True
        )
        self._monitoring_thread.start()
        
        self.logger.info("Agent monitoring started")
    
    def stop_monitoring(self):
        """Stop agent monitoring"""
        self._monitoring_active = False
        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)
        
        self.logger.info("Agent monitoring stopped")
    
    def _monitoring_worker(self):
        """Agent monitoring worker"""
        while self._monitoring_active:
            try:
                self._cleanup_dead_agents()
                self._update_statistics()
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.error("Monitoring worker error", error=str(e))
                time.sleep(5.0)
    
    def _cleanup_dead_agents(self):
        """Clean up dead or unresponsive agents"""
        current_time = time.time()
        dead_agents = []
        
        with self._lock:
            for agent_id, agent_info in self.agents.items():
                # Check heartbeat timeout
                if current_time - agent_info.last_heartbeat > self.heartbeat_timeout:
                    dead_agents.append(agent_id)
        
        # Terminate dead agents
        for agent_id in dead_agents:
            self.logger.warning("Terminating unresponsive agent", agent_id=agent_id)
            self.terminate_agent(agent_id)
    
    def _update_statistics(self):
        """Update agent statistics"""
        with self._lock:
            self.stats['current_active'] = len(self.agents)
            
            # Calculate average lifetime
            if self.stats['total_terminated'] > 0:
                total_lifetime = 0
                for agent_info in self.agents.values():
                    total_lifetime += time.time() - agent_info.created_time
                
                if total_lifetime > 0:
                    self.stats['average_lifetime'] = total_lifetime / len(self.agents)
    
    def shutdown(self):
        """Shutdown agent manager"""
        self.logger.info("Shutting down agent manager")
        
        # Stop monitoring
        self.stop_monitoring()
        
        # Terminate all agents
        agent_ids = list(self.agents.keys())
        for agent_id in agent_ids:
            self.terminate_agent(agent_id)
        
        self.logger.info("Agent manager shutdown complete")
    
    def __del__(self):
        """Cleanup on destruction"""
        try:
            self.shutdown()
        except:
            pass
