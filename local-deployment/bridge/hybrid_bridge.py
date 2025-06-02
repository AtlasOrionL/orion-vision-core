#!/usr/bin/env python3
"""
Hybrid Bridge Service - Python ↔ Kubernetes Integration
Orion Vision Core - Phase 3 Hybrid Local Deployment

Bu servis, Python core agents ile Kubernetes services arasında
köprü görevi görür ve unified communication sağlar.

Author: Orion Development Team
Version: 1.0.0
Date: 29 Mayıs 2025
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
from aiohttp import web
import pika
import threading

# Kubernetes client
try:
    from kubernetes import client, config, watch
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    print("Kubernetes client not available - running in bridge-only mode")


class BridgeStatus(Enum):
    """Bridge durumları"""
    INITIALIZING = "initializing"
    RUNNING = "running"
    ERROR = "error"
    STOPPING = "stopping"


@dataclass
class BridgeConfig:
    """Bridge konfigürasyonu"""
    # Network
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Python Core
    python_core_host: str = "localhost"
    python_core_port: int = 8001
    
    # Kubernetes
    kubernetes_namespace: str = "orion-system"
    kubernetes_enabled: bool = True
    
    # RabbitMQ
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "orion"
    rabbitmq_pass: str = "orion123"
    
    # Communication
    message_timeout: float = 30.0
    retry_attempts: int = 3
    
    # Monitoring
    metrics_enabled: bool = True
    health_check_interval: float = 10.0


class MessageRouter:
    """Mesaj yönlendirme sistemi"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.routes: Dict[str, str] = {}  # target -> protocol
        self.logger = logging.getLogger("MessageRouter")
    
    def add_route(self, target: str, protocol: str):
        """Yeni route ekle"""
        self.routes[target] = protocol
        self.logger.info(f"Route added: {target} -> {protocol}")
    
    def get_protocol(self, target: str) -> str:
        """Target için en uygun protokolü belirle"""
        # Explicit route varsa kullan
        if target in self.routes:
            return self.routes[target]
        
        # Target pattern'ına göre otomatik belirle
        if target.startswith("k8s://"):
            return "kubernetes"
        elif target.startswith("python://"):
            return "python"
        elif target.startswith("rabbitmq://"):
            return "rabbitmq"
        else:
            # Default: RabbitMQ
            return "rabbitmq"


class PythonCoreConnector:
    """Python core ile iletişim"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger("PythonConnector")
    
    async def initialize(self):
        """Connector'ı başlat"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.message_timeout)
        )
        self.logger.info("Python core connector initialized")
    
    async def send_message(self, target: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Python core'a mesaj gönder"""
        if not self.session:
            raise Exception("Connector not initialized")
        
        url = f"http://{self.config.python_core_host}:{self.config.python_core_port}/api/message"
        payload = {
            "target": target,
            "message": message,
            "timestamp": time.time()
        }
        
        try:
            async with self.session.post(url, json=payload) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Python core error: {response.status}")
        except Exception as e:
            self.logger.error(f"Failed to send message to Python core: {e}")
            raise
    
    async def get_status(self) -> Dict[str, Any]:
        """Python core durumunu al"""
        if not self.session:
            return {"status": "disconnected"}
        
        url = f"http://{self.config.python_core_host}:{self.config.python_core_port}/api/status"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {"status": "error", "code": response.status}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def cleanup(self):
        """Cleanup"""
        if self.session:
            await self.session.close()


class KubernetesConnector:
    """Kubernetes ile iletişim"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.k8s_client: Optional[client.CoreV1Api] = None
        self.logger = logging.getLogger("KubernetesConnector")
    
    async def initialize(self):
        """Kubernetes client'ı başlat"""
        if not KUBERNETES_AVAILABLE:
            self.logger.warning("Kubernetes client not available")
            return
        
        try:
            # Try in-cluster config first
            try:
                config.load_incluster_config()
                self.logger.info("Using in-cluster Kubernetes config")
            except:
                config.load_kube_config()
                self.logger.info("Using local Kubernetes config")
            
            self.k8s_client = client.CoreV1Api()
            self.logger.info("Kubernetes connector initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Kubernetes client: {e}")
    
    async def send_message(self, target: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Kubernetes service'e mesaj gönder"""
        if not self.k8s_client:
            raise Exception("Kubernetes client not available")
        
        # Parse target (e.g., "k8s://service-name" or "k8s://namespace/service-name")
        target_parts = target.replace("k8s://", "").split("/")
        if len(target_parts) == 1:
            service_name = target_parts[0]
            namespace = self.config.kubernetes_namespace
        else:
            namespace, service_name = target_parts
        
        try:
            # Get service endpoint
            service = self.k8s_client.read_namespaced_service(
                name=service_name,
                namespace=namespace
            )
            
            # Send HTTP request to service
            service_url = f"http://{service_name}.{namespace}.svc.cluster.local"
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{service_url}/api/message", json=message) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"Service error: {response.status}")
                        
        except ApiException as e:
            self.logger.error(f"Kubernetes API error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Failed to send message to Kubernetes: {e}")
            raise
    
    async def get_services(self) -> List[Dict[str, Any]]:
        """Namespace'deki servisleri listele"""
        if not self.k8s_client:
            return []
        
        try:
            services = self.k8s_client.list_namespaced_service(
                namespace=self.config.kubernetes_namespace
            )
            
            return [
                {
                    "name": svc.metadata.name,
                    "namespace": svc.metadata.namespace,
                    "cluster_ip": svc.spec.cluster_ip,
                    "ports": [{"port": port.port, "protocol": port.protocol} for port in svc.spec.ports]
                }
                for svc in services.items
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list services: {e}")
            return []
    
    async def get_pods(self) -> List[Dict[str, Any]]:
        """Namespace'deki pod'ları listele"""
        if not self.k8s_client:
            return []
        
        try:
            pods = self.k8s_client.list_namespaced_pod(
                namespace=self.config.kubernetes_namespace
            )
            
            return [
                {
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "ip": pod.status.pod_ip
                }
                for pod in pods.items
            ]
            
        except Exception as e:
            self.logger.error(f"Failed to list pods: {e}")
            return []


class RabbitMQConnector:
    """RabbitMQ ile iletişim"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
        self.logger = logging.getLogger("RabbitMQConnector")
    
    async def initialize(self):
        """RabbitMQ bağlantısını başlat"""
        try:
            credentials = pika.PlainCredentials(
                self.config.rabbitmq_user,
                self.config.rabbitmq_pass
            )
            
            parameters = pika.ConnectionParameters(
                host=self.config.rabbitmq_host,
                port=self.config.rabbitmq_port,
                credentials=credentials
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            self.logger.info("RabbitMQ connector initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize RabbitMQ: {e}")
    
    async def send_message(self, target: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """RabbitMQ'ya mesaj gönder"""
        if not self.channel:
            raise Exception("RabbitMQ not connected")
        
        # Parse target (e.g., "rabbitmq://queue-name")
        queue_name = target.replace("rabbitmq://", "")
        
        try:
            # Declare queue
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Publish message
            self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=json.dumps(message),
                properties=pika.BasicProperties(delivery_mode=2)
            )
            
            return {"status": "sent", "queue": queue_name}
            
        except Exception as e:
            self.logger.error(f"Failed to send RabbitMQ message: {e}")
            raise
    
    def cleanup(self):
        """Cleanup"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()


class HybridBridge:
    """Ana bridge servisi"""
    
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.status = BridgeStatus.INITIALIZING
        self.logger = self._setup_logger()
        
        # Connectors
        self.python_connector = PythonCoreConnector(config)
        self.kubernetes_connector = KubernetesConnector(config)
        self.rabbitmq_connector = RabbitMQConnector(config)
        
        # Router
        self.message_router = MessageRouter(config)
        
        # Web app
        self.app = web.Application()
        self._setup_routes()
        
        # Metrics
        self.metrics = {
            "start_time": time.time(),
            "messages_routed": 0,
            "errors": 0,
            "uptime": 0
        }
    
    def _setup_logger(self) -> logging.Logger:
        """Logger kurulumu"""
        logger = logging.getLogger("HybridBridge")
        logger.setLevel(logging.INFO)
        
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def _setup_routes(self):
        """Web routes kurulumu"""
        self.app.router.add_get('/', self.handle_index)
        self.app.router.add_get('/health', self.handle_health)
        self.app.router.add_get('/status', self.handle_status)
        self.app.router.add_post('/api/message', self.handle_message)
        self.app.router.add_get('/api/services', self.handle_services)
        self.app.router.add_get('/api/routes', self.handle_routes)
        self.app.router.add_post('/api/routes', self.handle_add_route)
    
    async def initialize(self):
        """Bridge'i başlat"""
        self.logger.info("Initializing Hybrid Bridge...")
        
        # Initialize connectors
        await self.python_connector.initialize()
        await self.kubernetes_connector.initialize()
        await self.rabbitmq_connector.initialize()
        
        # Setup default routes
        self.message_router.add_route("python-core", "python")
        self.message_router.add_route("orion-agents", "rabbitmq")
        
        self.status = BridgeStatus.RUNNING
        self.logger.info("Hybrid Bridge initialized successfully")
    
    async def handle_index(self, request):
        """Ana sayfa"""
        html = """
        <html>
        <head><title>Orion Hybrid Bridge</title></head>
        <body>
            <h1>🌉 Orion Hybrid Bridge</h1>
            <p>Python ↔ Kubernetes Integration Layer</p>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/status">System Status</a></li>
                <li><a href="/api/services">Services</a></li>
                <li><a href="/api/routes">Message Routes</a></li>
            </ul>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def handle_health(self, request):
        """Health check"""
        return web.json_response({
            "status": "healthy",
            "bridge_status": self.status.value,
            "timestamp": time.time()
        })
    
    async def handle_status(self, request):
        """Sistem durumu"""
        self.metrics["uptime"] = time.time() - self.metrics["start_time"]
        
        python_status = await self.python_connector.get_status()
        k8s_services = await self.kubernetes_connector.get_services()
        
        return web.json_response({
            "bridge": {
                "status": self.status.value,
                "metrics": self.metrics
            },
            "python_core": python_status,
            "kubernetes": {
                "available": KUBERNETES_AVAILABLE,
                "services_count": len(k8s_services)
            },
            "rabbitmq": {
                "connected": self.rabbitmq_connector.connection is not None
            }
        })
    
    async def handle_message(self, request):
        """Mesaj routing"""
        try:
            data = await request.json()
            target = data.get("target")
            message = data.get("message")
            
            if not target or not message:
                return web.json_response(
                    {"error": "Missing target or message"},
                    status=400
                )
            
            # Route message
            protocol = self.message_router.get_protocol(target)
            
            if protocol == "python":
                result = await self.python_connector.send_message(target, message)
            elif protocol == "kubernetes":
                result = await self.kubernetes_connector.send_message(target, message)
            elif protocol == "rabbitmq":
                result = await self.rabbitmq_connector.send_message(target, message)
            else:
                return web.json_response(
                    {"error": f"Unknown protocol: {protocol}"},
                    status=400
                )
            
            self.metrics["messages_routed"] += 1
            
            return web.json_response({
                "status": "routed",
                "protocol": protocol,
                "result": result
            })
            
        except Exception as e:
            self.metrics["errors"] += 1
            self.logger.error(f"Message routing error: {e}")
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def handle_services(self, request):
        """Kubernetes servisleri listele"""
        services = await self.kubernetes_connector.get_services()
        pods = await self.kubernetes_connector.get_pods()
        
        return web.json_response({
            "services": services,
            "pods": pods
        })
    
    async def handle_routes(self, request):
        """Mevcut route'ları listele"""
        return web.json_response({
            "routes": self.message_router.routes
        })
    
    async def handle_add_route(self, request):
        """Yeni route ekle"""
        try:
            data = await request.json()
            target = data.get("target")
            protocol = data.get("protocol")
            
            if not target or not protocol:
                return web.json_response(
                    {"error": "Missing target or protocol"},
                    status=400
                )
            
            self.message_router.add_route(target, protocol)
            
            return web.json_response({
                "status": "added",
                "target": target,
                "protocol": protocol
            })
            
        except Exception as e:
            return web.json_response(
                {"error": str(e)},
                status=500
            )
    
    async def start(self):
        """Bridge'i başlat"""
        await self.initialize()
        
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, self.config.host, self.config.port)
        await site.start()
        
        self.logger.info(f"Hybrid Bridge started on {self.config.host}:{self.config.port}")
    
    async def stop(self):
        """Bridge'i durdur"""
        self.status = BridgeStatus.STOPPING
        
        await self.python_connector.cleanup()
        self.rabbitmq_connector.cleanup()
        
        self.logger.info("Hybrid Bridge stopped")


async def main():
    """Ana fonksiyon"""
    # Configuration
    config = BridgeConfig(
        host="0.0.0.0",
        port=8000,
        kubernetes_namespace=os.getenv("KUBERNETES_NAMESPACE", "orion-system"),
        rabbitmq_host=os.getenv("RABBITMQ_HOST", "rabbitmq.orion-system.svc.cluster.local")
    )
    
    # Create and start bridge
    bridge = HybridBridge(config)
    
    try:
        await bridge.start()
        
        # Keep running
        while bridge.status == BridgeStatus.RUNNING:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        await bridge.stop()


if __name__ == "__main__":
    asyncio.run(main())
