#!/usr/bin/env python3
"""
Multi-Protocol Agent - Dynamic Agent Example
Orion Vision Core - Çoklu Protokol Destekli Agent

Bu agent, multi-protocol communication sistemini kullanan dinamik bir agent örneğidir.
RabbitMQ, WebSocket, HTTP ve HTTP/2 protokollerini destekler.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import time
import json
from typing import Dict, Any, List

# Agent core'u import et
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'jobone', 'vision_core'))

from agent_core import Agent, AgentConfig, AgentStatus
from multi_protocol_communication import (
    MultiProtocolCommunicationManager, ProtocolType, ProtocolConfig, 
    MessageRoute, OrionMessage, MessageType, MessagePriority
)


class MultiProtocolAgent(Agent):
    """
    Multi-Protocol Agent - Çoklu Protokol Destekli Agent
    
    Bu agent, farklı protokoller üzerinden iletişim kurabilen gelişmiş bir agent'tır.
    Protocol routing, failover ve load balancing özelliklerini destekler.
    """
    
    def __init__(self, config: AgentConfig, auto_register: bool = True):
        """
        Multi-Protocol Agent başlatıcı
        
        Args:
            config: Agent konfigürasyon objesi
            auto_register: Otomatik registry'ye kayıt
        """
        super().__init__(config, auto_register)
        
        # Multi-protocol manager
        self.comm_manager = MultiProtocolCommunicationManager(self.agent_id)
        
        # Protocol configurations
        self.protocol_configs = {
            ProtocolType.RABBITMQ: ProtocolConfig(
                protocol_type=ProtocolType.RABBITMQ,
                host="localhost",
                port=5672,
                metadata={"username": "guest", "password": "guest"}
            ),
            ProtocolType.WEBSOCKET: ProtocolConfig(
                protocol_type=ProtocolType.WEBSOCKET,
                host="localhost",
                port=8765,
                path="/ws"
            ),
            ProtocolType.HTTP: ProtocolConfig(
                protocol_type=ProtocolType.HTTP,
                host="localhost",
                port=8000,
                path="/api"
            ),
            ProtocolType.HTTP2: ProtocolConfig(
                protocol_type=ProtocolType.HTTP2,
                host="localhost",
                port=8443,
                ssl_enabled=True
            )
        }
        
        # Agent statistics
        self.protocol_stats = {}
        self.message_count = 0
        self.last_protocol_used = None
        self.protocol_preferences = [
            ProtocolType.WEBSOCKET,  # Real-time için tercih
            ProtocolType.RABBITMQ,   # Güvenilir mesajlaşma
            ProtocolType.HTTP2,      # Yüksek performans
            ProtocolType.HTTP        # Fallback
        ]
        
        # Agent yetenekleri ekle
        self.add_capability("multi_protocol_communication")
        self.add_capability("protocol_routing")
        self.add_capability("failover_support")
        self.add_capability("load_balancing")
        self.add_capability("circuit_breaker")
        
        self.logger.info(f"Multi-Protocol Agent initialized with {len(self.protocol_configs)} protocols")
    
    def initialize(self) -> bool:
        """
        Agent'a özel başlatma işlemleri
        
        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            self.logger.info("Initializing Multi-Protocol Agent...")
            
            # Protocol manager'ı konfigüre et
            self._setup_protocols()
            self._setup_message_handlers()
            self._setup_routing_rules()
            
            # Async initialization
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Protokollere bağlan
            connection_results = loop.run_until_complete(self.comm_manager.connect_all())
            
            # Başarılı bağlantıları kontrol et
            successful_connections = sum(1 for success in connection_results.values() if success)
            
            if successful_connections == 0:
                self.logger.error("No protocol connections established")
                return False
            
            self.logger.info(f"Connected to {successful_connections}/{len(connection_results)} protocols")
            
            # Mesaj dinlemeyi başlat
            listen_results = loop.run_until_complete(self.comm_manager.start_all_listening())
            
            self.logger.info("Multi-Protocol Agent initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Multi-Protocol Agent initialization failed: {e}")
            return False
    
    def run(self):
        """
        Agent'ın ana çalışma döngüsü
        """
        self.logger.info("Multi-Protocol Agent main loop started")
        
        try:
            # Async event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Ana async döngüyü çalıştır
            loop.run_until_complete(self._async_main_loop())
            
        except Exception as e:
            self.logger.error(f"Multi-Protocol Agent run error: {e}")
            raise
        finally:
            self.logger.info("Multi-Protocol Agent main loop ended")
    
    async def _async_main_loop(self):
        """Async ana döngü"""
        while not self.stop_event.is_set():
            try:
                # Protocol health check
                await self._check_protocol_health()
                
                # Test mesajları gönder
                await self._send_test_messages()
                
                # İstatistikleri güncelle
                self._update_statistics()
                
                # Work interval kadar bekle
                await asyncio.sleep(5.0)
                
            except Exception as e:
                self.logger.error(f"Async main loop error: {e}")
                await asyncio.sleep(1.0)
    
    def cleanup(self):
        """
        Agent'a özel temizlik işlemleri
        """
        try:
            self.logger.info("Cleaning up Multi-Protocol Agent...")
            
            # Async cleanup
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Tüm bağlantıları kapat
            disconnect_results = loop.run_until_complete(self.comm_manager.disconnect_all())
            
            # İstatistikleri kaydet
            final_stats = self.comm_manager.get_comprehensive_stats()
            self.logger.info(f"Final protocol statistics: {final_stats}")
            
            # Agent istatistiklerini güncelle
            self.stats['messages_sent'] = final_stats['manager_stats']['total_messages_sent']
            self.stats['messages_received'] = final_stats['manager_stats']['total_messages_received']
            self.stats['protocol_usage'] = final_stats['manager_stats']['protocol_usage']
            
            self.logger.info("Multi-Protocol Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Multi-Protocol Agent cleanup error: {e}")
    
    def _setup_protocols(self):
        """Protokolleri konfigüre et"""
        try:
            for protocol_type, config in self.protocol_configs.items():
                success = self.comm_manager.add_protocol(protocol_type, config)
                if success:
                    self.logger.info(f"Protocol configured: {protocol_type.value}")
                else:
                    self.logger.warning(f"Failed to configure protocol: {protocol_type.value}")
            
        except Exception as e:
            self.logger.error(f"Protocol setup error: {e}")
    
    def _setup_message_handlers(self):
        """Mesaj handler'larını konfigüre et"""
        try:
            # Global message handlers
            self.comm_manager.add_global_message_handler(
                MessageType.AGENT_COMMUNICATION.value, 
                self._handle_agent_communication
            )
            self.comm_manager.add_global_message_handler(
                MessageType.TASK_REQUEST.value, 
                self._handle_task_request
            )
            self.comm_manager.add_global_message_handler(
                MessageType.SYSTEM_STATUS.value, 
                self._handle_system_status
            )
            self.comm_manager.add_global_message_handler(
                MessageType.HEARTBEAT.value, 
                self._handle_heartbeat
            )
            
            self.logger.info("Message handlers configured")
            
        except Exception as e:
            self.logger.error(f"Message handler setup error: {e}")
    
    def _setup_routing_rules(self):
        """Routing kurallarını konfigüre et"""
        try:
            # Örnek routing kuralları
            
            # Real-time mesajlar için WebSocket tercih et
            realtime_route = MessageRoute(
                source_protocol=ProtocolType.RABBITMQ,
                target_protocol=ProtocolType.WEBSOCKET,
                source_address="*",
                target_address="realtime_*"
            )
            self.comm_manager.add_message_route(realtime_route)
            
            # API çağrıları için HTTP/2 tercih et
            api_route = MessageRoute(
                source_protocol=ProtocolType.WEBSOCKET,
                target_protocol=ProtocolType.HTTP2,
                source_address="*",
                target_address="api_*"
            )
            self.comm_manager.add_message_route(api_route)
            
            self.logger.info("Routing rules configured")
            
        except Exception as e:
            self.logger.error(f"Routing setup error: {e}")
    
    async def _check_protocol_health(self):
        """Protokol sağlık durumunu kontrol et"""
        try:
            health_status = self.comm_manager.get_health_status()
            
            if health_status['overall_health'] != 'healthy':
                self.logger.warning(f"Protocol health degraded: {health_status['overall_health']}")
                
                # Unhealthy protokolleri logla
                for protocol, health in health_status['protocol_health'].items():
                    if not health['healthy']:
                        self.logger.warning(f"Protocol {protocol} is unhealthy: {health['status']}")
            
        except Exception as e:
            self.logger.error(f"Protocol health check error: {e}")
    
    async def _send_test_messages(self):
        """Test mesajları gönder"""
        try:
            # Her protokol için test mesajı
            for protocol_type in self.protocol_preferences:
                if protocol_type in self.comm_manager.adapters:
                    test_message = OrionMessage(
                        message_type=MessageType.AGENT_COMMUNICATION.value,
                        content=f"Test message from {self.agent_id} via {protocol_type.value}",
                        sender_id=self.agent_id,
                        priority=MessagePriority.LOW.value,
                        metadata={
                            'test': True,
                            'protocol': protocol_type.value,
                            'timestamp': time.time()
                        }
                    )
                    
                    # Test target
                    target = f"test_queue_{protocol_type.value}"
                    
                    success = await self.comm_manager.send_message(
                        test_message, target, protocol_type
                    )
                    
                    if success:
                        self.message_count += 1
                        self.last_protocol_used = protocol_type
                        self.logger.debug(f"Test message sent via {protocol_type.value}")
                    else:
                        self.logger.warning(f"Test message failed via {protocol_type.value}")
            
        except Exception as e:
            self.logger.error(f"Test message sending error: {e}")
    
    def _update_statistics(self):
        """İstatistikleri güncelle"""
        try:
            # Communication manager istatistikleri
            comm_stats = self.comm_manager.get_comprehensive_stats()
            
            # Agent istatistiklerini güncelle
            self.stats['total_messages_sent'] = comm_stats['manager_stats']['total_messages_sent']
            self.stats['total_messages_received'] = comm_stats['manager_stats']['total_messages_received']
            self.stats['active_protocols'] = len(comm_stats['active_protocols'])
            self.stats['failover_events'] = comm_stats['manager_stats']['failover_events']
            self.stats['last_protocol_used'] = self.last_protocol_used.value if self.last_protocol_used else None
            
            # Protocol-specific stats
            self.protocol_stats = comm_stats['adapter_stats']
            
        except Exception as e:
            self.logger.error(f"Statistics update error: {e}")
    
    def _handle_agent_communication(self, message: OrionMessage):
        """Agent communication mesajını işle"""
        try:
            self.logger.info(f"Received agent communication from {message.sender_id}: {message.content}")
            
            # Echo response gönder
            response = OrionMessage(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=f"Echo from {self.agent_id}: {message.content}",
                sender_id=self.agent_id,
                correlation_id=message.correlation_id,
                priority=MessagePriority.NORMAL.value,
                metadata={
                    'response_to': message.sender_id,
                    'original_protocol': message.metadata.get('protocol', 'unknown')
                }
            )
            
            # Async response gönder
            asyncio.create_task(self._send_response(response, message.sender_id))
            
        except Exception as e:
            self.logger.error(f"Agent communication handler error: {e}")
    
    def _handle_task_request(self, message: OrionMessage):
        """Task request mesajını işle"""
        try:
            self.logger.info(f"Received task request from {message.sender_id}: {message.content}")
            
            # Task completion simulation
            task_result = {
                'task_id': message.metadata.get('task_id', 'unknown'),
                'status': 'completed',
                'result': f"Task processed by {self.agent_id}",
                'processing_time': 0.1
            }
            
            response = OrionMessage(
                message_type=MessageType.TASK_RESPONSE.value,
                content=json.dumps(task_result),
                sender_id=self.agent_id,
                correlation_id=message.correlation_id,
                priority=MessagePriority.HIGH.value,
                metadata=task_result
            )
            
            # Async response gönder
            asyncio.create_task(self._send_response(response, message.sender_id))
            
        except Exception as e:
            self.logger.error(f"Task request handler error: {e}")
    
    def _handle_system_status(self, message: OrionMessage):
        """System status mesajını işle"""
        try:
            self.logger.info(f"Received system status request from {message.sender_id}")
            
            # System status raporu oluştur
            status_report = {
                'agent_id': self.agent_id,
                'status': self.status.value,
                'uptime': time.time() - self.start_time if self.start_time else 0,
                'protocol_stats': self.protocol_stats,
                'health': self.comm_manager.get_health_status(),
                'capabilities': self.config.capabilities
            }
            
            response = OrionMessage(
                message_type=MessageType.SYSTEM_STATUS.value,
                content=json.dumps(status_report),
                sender_id=self.agent_id,
                correlation_id=message.correlation_id,
                priority=MessagePriority.NORMAL.value,
                metadata=status_report
            )
            
            # Async response gönder
            asyncio.create_task(self._send_response(response, message.sender_id))
            
        except Exception as e:
            self.logger.error(f"System status handler error: {e}")
    
    def _handle_heartbeat(self, message: OrionMessage):
        """Heartbeat mesajını işle"""
        try:
            self.logger.debug(f"Received heartbeat from {message.sender_id}")
            # Heartbeat'e genellikle response gerekmez
            
        except Exception as e:
            self.logger.error(f"Heartbeat handler error: {e}")
    
    async def _send_response(self, response: OrionMessage, target: str):
        """Async response gönder"""
        try:
            success = await self.comm_manager.send_message(response, target)
            if success:
                self.logger.debug(f"Response sent to {target}")
            else:
                self.logger.warning(f"Failed to send response to {target}")
                
        except Exception as e:
            self.logger.error(f"Response sending error: {e}")
    
    def get_protocol_stats(self) -> Dict[str, Any]:
        """Protocol istatistiklerini getir"""
        return {
            'agent_id': self.agent_id,
            'message_count': self.message_count,
            'last_protocol_used': self.last_protocol_used.value if self.last_protocol_used else None,
            'protocol_stats': self.protocol_stats,
            'communication_manager_stats': self.comm_manager.get_comprehensive_stats(),
            'health_status': self.comm_manager.get_health_status()
        }
    
    def switch_primary_protocol(self, protocol_type: ProtocolType) -> bool:
        """Ana protokolü değiştir"""
        try:
            if protocol_type in self.comm_manager.adapters:
                self.comm_manager.default_protocol = protocol_type
                self.logger.info(f"Primary protocol switched to {protocol_type.value}")
                return True
            else:
                self.logger.warning(f"Protocol not available: {protocol_type.value}")
                return False
                
        except Exception as e:
            self.logger.error(f"Protocol switch error: {e}")
            return False
