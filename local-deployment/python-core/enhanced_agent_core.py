#!/usr/bin/env python3
"""
Enhanced Agent Core for Hybrid Local Deployment - Sprint 6.1
Orion Vision Core - Hybrid Local Architecture

Bu dosya, mevcut src/jobone/vision_core/agent_core.py'yi optimize ederek
local Kubernetes ile entegrasyon için hazırlar.

Author: Orion Development Team
Version: 1.0.0
Date: 29 Mayıs 2025
"""

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Callable
import requests
import pika
from datetime import datetime

# Kubernetes integration
try:
    from kubernetes import client, config
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    print("Kubernetes client not available - running in pure Python mode")


class AgentStatus(Enum):
    """Agent durumları"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class AgentPriority(Enum):
    """Agent öncelik seviyeleri"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5


@dataclass
class AgentConfig:
    """Enhanced agent configuration"""
    agent_id: str
    name: str
    description: str
    priority: AgentPriority
    auto_start: bool = True
    heartbeat_interval: float = 30.0
    max_retries: int = 3
    timeout: float = 300.0
    
    # Hybrid local specific
    local_mode: bool = True
    kubernetes_integration: bool = False
    bridge_enabled: bool = True
    
    # Resource limits
    cpu_limit: float = 1.0
    memory_limit: str = "512Mi"
    
    # Communication
    rabbitmq_enabled: bool = True
    grpc_enabled: bool = False
    rest_api_enabled: bool = True
    
    # Monitoring
    metrics_enabled: bool = True
    logging_level: str = "INFO"
    
    # Security
    auth_required: bool = False
    encryption_enabled: bool = False


class AgentLogger:
    """Enhanced logging with Kubernetes integration"""
    
    def __init__(self, agent_id: str, config: AgentConfig):
        self.agent_id = agent_id
        self.config = config
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        """Setup enhanced logger"""
        logger = logging.getLogger(f"orion.agent.{self.agent_id}")
        logger.setLevel(getattr(logging, self.config.logging_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter(
            f'%(asctime)s - {self.agent_id} - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(f"{log_dir}/{self.agent_id}.log")
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        return logger
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
        if self.config.kubernetes_integration:
            self._send_to_kubernetes_logs(message, "INFO", **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
        if self.config.kubernetes_integration:
            self._send_to_kubernetes_logs(message, "ERROR", **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
        if self.config.kubernetes_integration:
            self._send_to_kubernetes_logs(message, "WARNING", **kwargs)
    
    def _send_to_kubernetes_logs(self, message: str, level: str, **kwargs):
        """Send logs to Kubernetes logging system"""
        if not KUBERNETES_AVAILABLE:
            return
            
        try:
            # Kubernetes structured logging
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id,
                "level": level,
                "message": message,
                "metadata": kwargs
            }
            
            # Send to Kubernetes logging endpoint (if available)
            # This would integrate with Fluentd/Fluent Bit in K8s
            print(f"K8S_LOG: {json.dumps(log_entry)}")
            
        except Exception as e:
            self.logger.error(f"Failed to send log to Kubernetes: {e}")


class HybridCommunicationManager:
    """Hybrid communication manager for Python ↔ Kubernetes bridge"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.rabbitmq_connection = None
        self.kubernetes_client = None
        self.grpc_channel = None
        
    async def initialize(self):
        """Initialize communication channels"""
        if self.config.rabbitmq_enabled:
            await self._setup_rabbitmq()
            
        if self.config.kubernetes_integration and KUBERNETES_AVAILABLE:
            await self._setup_kubernetes_client()
            
        if self.config.grpc_enabled:
            await self._setup_grpc_channel()
    
    async def _setup_rabbitmq(self):
        """Setup RabbitMQ connection"""
        try:
            connection_params = pika.ConnectionParameters(
                host=os.getenv('RABBITMQ_HOST', 'localhost'),
                port=int(os.getenv('RABBITMQ_PORT', 5672)),
                virtual_host=os.getenv('RABBITMQ_VHOST', '/'),
                credentials=pika.PlainCredentials(
                    os.getenv('RABBITMQ_USER', 'guest'),
                    os.getenv('RABBITMQ_PASS', 'guest')
                )
            )
            self.rabbitmq_connection = pika.BlockingConnection(connection_params)
            print("✅ RabbitMQ connection established")
        except Exception as e:
            print(f"❌ RabbitMQ connection failed: {e}")
    
    async def _setup_kubernetes_client(self):
        """Setup Kubernetes client"""
        try:
            # Try in-cluster config first, then local config
            try:
                config.load_incluster_config()
            except:
                config.load_kube_config()
            
            self.kubernetes_client = client.CoreV1Api()
            print("✅ Kubernetes client initialized")
        except Exception as e:
            print(f"❌ Kubernetes client failed: {e}")
    
    async def _setup_grpc_channel(self):
        """Setup gRPC channel for Istio communication"""
        try:
            # This would connect to Istio sidecar
            import grpc
            self.grpc_channel = grpc.aio.insecure_channel('localhost:15001')  # Istio sidecar
            print("✅ gRPC channel established")
        except Exception as e:
            print(f"❌ gRPC channel failed: {e}")
    
    async def send_message(self, target: str, message: Dict[str, Any], protocol: str = "auto"):
        """Send message via appropriate protocol"""
        if protocol == "auto":
            protocol = self._select_best_protocol(target)
        
        if protocol == "rabbitmq" and self.rabbitmq_connection:
            return await self._send_rabbitmq(target, message)
        elif protocol == "grpc" and self.grpc_channel:
            return await self._send_grpc(target, message)
        elif protocol == "kubernetes" and self.kubernetes_client:
            return await self._send_kubernetes(target, message)
        else:
            raise Exception(f"Protocol {protocol} not available")
    
    def _select_best_protocol(self, target: str) -> str:
        """Select best protocol based on target and availability"""
        if target.startswith("k8s://"):
            return "kubernetes"
        elif target.startswith("grpc://"):
            return "grpc"
        else:
            return "rabbitmq"
    
    async def _send_rabbitmq(self, target: str, message: Dict[str, Any]):
        """Send via RabbitMQ"""
        if not self.rabbitmq_connection:
            raise Exception("RabbitMQ not connected")
        
        channel = self.rabbitmq_connection.channel()
        channel.queue_declare(queue=target, durable=True)
        channel.basic_publish(
            exchange='',
            routing_key=target,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        channel.close()
    
    async def _send_grpc(self, target: str, message: Dict[str, Any]):
        """Send via gRPC (Istio)"""
        # This would use Istio service mesh
        print(f"Sending gRPC message to {target}: {message}")
    
    async def _send_kubernetes(self, target: str, message: Dict[str, Any]):
        """Send via Kubernetes API"""
        if not self.kubernetes_client:
            raise Exception("Kubernetes client not available")
        
        # Create ConfigMap or send to service
        print(f"Sending K8s message to {target}: {message}")


class EnhancedAgent(ABC):
    """Enhanced abstract agent class for hybrid local deployment"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.agent_id = config.agent_id
        self.status = AgentStatus.INITIALIZING
        self.logger = AgentLogger(self.agent_id, config)
        self.communication = HybridCommunicationManager(config)
        
        # Threading
        self._stop_event = threading.Event()
        self._heartbeat_thread = None
        self._main_thread = None
        
        # Metrics
        self.metrics = {
            "start_time": None,
            "uptime": 0,
            "messages_sent": 0,
            "messages_received": 0,
            "errors": 0,
            "last_heartbeat": None
        }
        
        # Kubernetes integration
        self.kubernetes_pod_name = os.getenv('HOSTNAME', f"{self.agent_id}-local")
        self.kubernetes_namespace = os.getenv('POD_NAMESPACE', 'default')
        
        self.logger.info(f"Enhanced agent {self.agent_id} initialized in hybrid local mode")
    
    async def start(self):
        """Start the enhanced agent"""
        try:
            self.status = AgentStatus.RUNNING
            self.metrics["start_time"] = time.time()
            
            # Initialize communication
            await self.communication.initialize()
            
            # Start heartbeat
            self._start_heartbeat()
            
            # Register with Kubernetes if available
            if self.config.kubernetes_integration:
                await self._register_with_kubernetes()
            
            # Start main agent logic
            self._main_thread = threading.Thread(target=self._run_main_loop, daemon=True)
            self._main_thread.start()
            
            self.logger.info(f"Enhanced agent {self.agent_id} started successfully")
            
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.logger.error(f"Failed to start agent: {e}")
            raise
    
    async def stop(self):
        """Stop the enhanced agent"""
        self.status = AgentStatus.STOPPING
        self.logger.info(f"Stopping enhanced agent {self.agent_id}")
        
        # Stop threads
        self._stop_event.set()
        
        if self._heartbeat_thread and self._heartbeat_thread.is_alive():
            self._heartbeat_thread.join(timeout=5)
        
        if self._main_thread and self._main_thread.is_alive():
            self._main_thread.join(timeout=10)
        
        # Cleanup
        await self._cleanup()
        
        self.status = AgentStatus.STOPPED
        self.logger.info(f"Enhanced agent {self.agent_id} stopped")
    
    def _start_heartbeat(self):
        """Start heartbeat thread"""
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()
    
    def _heartbeat_loop(self):
        """Heartbeat loop"""
        while not self._stop_event.is_set():
            try:
                self._send_heartbeat()
                self._stop_event.wait(self.config.heartbeat_interval)
            except Exception as e:
                self.logger.error(f"Heartbeat error: {e}")
    
    def _send_heartbeat(self):
        """Send heartbeat"""
        self.metrics["last_heartbeat"] = time.time()
        self.metrics["uptime"] = time.time() - self.metrics["start_time"]
        
        heartbeat_data = {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "timestamp": self.metrics["last_heartbeat"],
            "uptime": self.metrics["uptime"],
            "metrics": self.metrics
        }
        
        # Send to local registry and Kubernetes
        self._send_heartbeat_local(heartbeat_data)
        if self.config.kubernetes_integration:
            asyncio.create_task(self._send_heartbeat_kubernetes(heartbeat_data))
    
    def _send_heartbeat_local(self, data: Dict[str, Any]):
        """Send heartbeat to local registry"""
        try:
            # Update local agent registry
            registry_file = "data/agent_registry.json"
            if os.path.exists(registry_file):
                with open(registry_file, 'r') as f:
                    registry = json.load(f)
            else:
                registry = {}
            
            registry[self.agent_id] = data
            
            os.makedirs(os.path.dirname(registry_file), exist_ok=True)
            with open(registry_file, 'w') as f:
                json.dump(registry, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Local heartbeat failed: {e}")
    
    async def _send_heartbeat_kubernetes(self, data: Dict[str, Any]):
        """Send heartbeat to Kubernetes"""
        try:
            if self.communication.kubernetes_client:
                # Update pod annotations or create ConfigMap
                pass
        except Exception as e:
            self.logger.error(f"Kubernetes heartbeat failed: {e}")
    
    async def _register_with_kubernetes(self):
        """Register agent with Kubernetes"""
        if not KUBERNETES_AVAILABLE:
            return
        
        try:
            # Create or update agent registration in Kubernetes
            registration_data = {
                "agent_id": self.agent_id,
                "config": asdict(self.config),
                "pod_name": self.kubernetes_pod_name,
                "namespace": self.kubernetes_namespace,
                "registration_time": datetime.now().isoformat()
            }
            
            self.logger.info(f"Registered with Kubernetes: {registration_data}")
            
        except Exception as e:
            self.logger.error(f"Kubernetes registration failed: {e}")
    
    def _run_main_loop(self):
        """Main agent loop"""
        while not self._stop_event.is_set():
            try:
                # Run agent-specific logic
                asyncio.run(self.execute())
                time.sleep(1)  # Prevent busy loop
            except Exception as e:
                self.metrics["errors"] += 1
                self.logger.error(f"Main loop error: {e}")
                time.sleep(5)  # Error backoff
    
    @abstractmethod
    async def execute(self):
        """Agent-specific execution logic"""
        pass
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            if self.communication.rabbitmq_connection:
                self.communication.rabbitmq_connection.close()
            
            if self.communication.grpc_channel:
                await self.communication.grpc_channel.close()
                
        except Exception as e:
            self.logger.error(f"Cleanup error: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "agent_id": self.agent_id,
            "status": self.status.value,
            "config": asdict(self.config),
            "metrics": self.metrics,
            "kubernetes_integration": self.config.kubernetes_integration,
            "local_mode": self.config.local_mode
        }


# Example enhanced agent implementation
class ExampleEnhancedAgent(EnhancedAgent):
    """Example enhanced agent for testing"""
    
    async def execute(self):
        """Example execution logic"""
        self.logger.info(f"Enhanced agent {self.agent_id} executing in hybrid mode")
        
        # Send test message
        if self.config.bridge_enabled:
            try:
                await self.communication.send_message(
                    "test_queue",
                    {"message": "Hello from enhanced agent", "timestamp": time.time()}
                )
                self.metrics["messages_sent"] += 1
            except Exception as e:
                self.logger.error(f"Message send failed: {e}")


if __name__ == "__main__":
    # Test enhanced agent
    config = AgentConfig(
        agent_id="enhanced_test_agent",
        name="Enhanced Test Agent",
        description="Test agent for hybrid local deployment",
        priority=AgentPriority.NORMAL,
        local_mode=True,
        kubernetes_integration=KUBERNETES_AVAILABLE,
        bridge_enabled=True
    )
    
    agent = ExampleEnhancedAgent(config)
    
    async def main():
        await agent.start()
        await asyncio.sleep(10)  # Run for 10 seconds
        await agent.stop()
    
    asyncio.run(main())
