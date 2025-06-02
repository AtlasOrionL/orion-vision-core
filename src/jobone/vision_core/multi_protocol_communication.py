#!/usr/bin/env python3
"""
Multi-Protocol Communication System - Atlas Prompt 3.2.1
Orion Vision Core - Gelişmiş Agent İletişim Protokolleri

Bu modül, agent'lar arası iletişim için çoklu protokol desteği sağlar.
RabbitMQ, WebSocket, gRPC ve HTTP/2 protokollerini destekler.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import json
import time
import threading
import websockets
import grpc
import httpx
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor

# Mevcut communication modüllerini import et
import sys
import os
sys.path.append(os.path.dirname(__file__))

from .agents.communication_agent import CommunicationAgent, OrionMessage, MessageType, MessagePriority


class ProtocolType(Enum):
    """Desteklenen protokol tipleri"""
    RABBITMQ = "rabbitmq"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    HTTP2 = "http2"
    HTTP = "http"


class ConnectionStatus(Enum):
    """Bağlantı durumu"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


@dataclass
class ProtocolConfig:
    """Protokol konfigürasyon veri yapısı"""
    protocol_type: ProtocolType
    host: str = "localhost"
    port: int = 8080
    path: str = "/"
    ssl_enabled: bool = False
    auth_token: Optional[str] = None
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class MessageRoute:
    """Mesaj routing bilgisi"""
    source_protocol: ProtocolType
    target_protocol: ProtocolType
    source_address: str
    target_address: str
    transformation_rules: Dict[str, Any] = None

    def __post_init__(self):
        if self.transformation_rules is None:
            self.transformation_rules = {}


class ProtocolAdapter(ABC):
    """
    Protocol Adapter Abstract Base Class

    Her protokol için özel adapter implement edilir.
    """

    def __init__(self, config: ProtocolConfig, agent_id: str):
        self.config = config
        self.agent_id = agent_id
        self.status = ConnectionStatus.DISCONNECTED
        self.message_handlers: Dict[str, Callable] = {}
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connection_attempts': 0,
            'last_activity': None,
            'errors': 0
        }

    @abstractmethod
    async def connect(self) -> bool:
        """Protokole bağlan"""
        pass

    @abstractmethod
    async def disconnect(self) -> bool:
        """Protokol bağlantısını kapat"""
        pass

    @abstractmethod
    async def send_message(self, message: OrionMessage, target: str) -> bool:
        """Mesaj gönder"""
        pass

    @abstractmethod
    async def start_listening(self) -> bool:
        """Mesaj dinlemeyi başlat"""
        pass

    @abstractmethod
    async def stop_listening(self) -> bool:
        """Mesaj dinlemeyi durdur"""
        pass

    def add_message_handler(self, message_type: str, handler: Callable):
        """Mesaj handler ekle"""
        self.message_handlers[message_type] = handler

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri getir"""
        return {
            'protocol': self.config.protocol_type.value,
            'status': self.status.value,
            'agent_id': self.agent_id,
            **self.stats
        }


class WebSocketAdapter(ProtocolAdapter):
    """
    WebSocket Protocol Adapter

    Real-time bidirectional communication için WebSocket desteği.
    """

    def __init__(self, config: ProtocolConfig, agent_id: str):
        super().__init__(config, agent_id)
        self.websocket = None
        self.server = None
        self.is_server = False
        self.clients: Dict[str, websockets.WebSocketServerProtocol] = {}

    async def connect(self) -> bool:
        """WebSocket bağlantısı kur"""
        try:
            self.status = ConnectionStatus.CONNECTING
            self.stats['connection_attempts'] += 1

            # Client mode
            if not self.is_server:
                uri = f"{'wss' if self.config.ssl_enabled else 'ws'}://{self.config.host}:{self.config.port}{self.config.path}"

                headers = {}
                if self.config.auth_token:
                    headers['Authorization'] = f"Bearer {self.config.auth_token}"

                self.websocket = await websockets.connect(
                    uri,
                    extra_headers=headers,
                    timeout=self.config.timeout
                )

                self.status = ConnectionStatus.CONNECTED
                self.stats['last_activity'] = time.time()
                return True

            # Server mode
            else:
                self.server = await websockets.serve(
                    self._handle_client_connection,
                    self.config.host,
                    self.config.port
                )

                self.status = ConnectionStatus.CONNECTED
                return True

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.stats['errors'] += 1
            print(f"WebSocket connection error: {e}")
            return False

    async def disconnect(self) -> bool:
        """WebSocket bağlantısını kapat"""
        try:
            if self.websocket:
                await self.websocket.close()
                self.websocket = None

            if self.server:
                self.server.close()
                await self.server.wait_closed()
                self.server = None

            self.clients.clear()
            self.status = ConnectionStatus.DISCONNECTED
            return True

        except Exception as e:
            print(f"WebSocket disconnect error: {e}")
            return False

    async def send_message(self, message: OrionMessage, target: str) -> bool:
        """WebSocket üzerinden mesaj gönder"""
        try:
            if self.status != ConnectionStatus.CONNECTED:
                return False

            message_data = {
                'type': 'orion_message',
                'target': target,
                'message': asdict(message)
            }

            message_json = json.dumps(message_data)

            # Client mode
            if self.websocket:
                await self.websocket.send(message_json)

            # Server mode - broadcast to specific client
            elif target in self.clients:
                await self.clients[target].send(message_json)

            # Server mode - broadcast to all clients
            elif target == "broadcast":
                for client_ws in self.clients.values():
                    try:
                        await client_ws.send(message_json)
                    except:
                        pass  # Client disconnected

            self.stats['messages_sent'] += 1
            self.stats['last_activity'] = time.time()
            return True

        except Exception as e:
            self.stats['errors'] += 1
            print(f"WebSocket send error: {e}")
            return False

    async def start_listening(self) -> bool:
        """WebSocket mesaj dinlemeyi başlat"""
        try:
            if self.websocket:
                # Client mode listening
                asyncio.create_task(self._listen_client())

            return True

        except Exception as e:
            print(f"WebSocket listen start error: {e}")
            return False

    async def stop_listening(self) -> bool:
        """WebSocket mesaj dinlemeyi durdur"""
        # Listening tasks are handled by connection lifecycle
        return True

    async def _listen_client(self):
        """Client mode mesaj dinleme"""
        try:
            async for message in self.websocket:
                await self._handle_message(message)
        except Exception as e:
            print(f"WebSocket client listen error: {e}")
            self.status = ConnectionStatus.ERROR

    async def _handle_client_connection(self, websocket, path):
        """Server mode client bağlantısı işle"""
        client_id = f"client_{len(self.clients)}"
        self.clients[client_id] = websocket

        try:
            async for message in websocket:
                await self._handle_message(message, client_id)
        except Exception as e:
            print(f"WebSocket client error: {e}")
        finally:
            if client_id in self.clients:
                del self.clients[client_id]

    async def _handle_message(self, message_data: str, client_id: str = None):
        """Gelen mesajı işle"""
        try:
            data = json.loads(message_data)

            if data.get('type') == 'orion_message':
                message_dict = data.get('message', {})
                message = OrionMessage.from_dict(message_dict)

                # Message handler çağır
                message_type = message.message_type
                if message_type in self.message_handlers:
                    self.message_handlers[message_type](message)

                self.stats['messages_received'] += 1
                self.stats['last_activity'] = time.time()

        except Exception as e:
            self.stats['errors'] += 1
            print(f"WebSocket message handling error: {e}")


class HTTPAdapter(ProtocolAdapter):
    """
    HTTP/HTTP2 Protocol Adapter

    RESTful API ve HTTP/2 desteği için adapter.
    """

    def __init__(self, config: ProtocolConfig, agent_id: str):
        super().__init__(config, agent_id)
        self.client = None
        self.base_url = f"{'https' if self.config.ssl_enabled else 'http'}://{self.config.host}:{self.config.port}"

    async def connect(self) -> bool:
        """HTTP client bağlantısı kur"""
        try:
            self.status = ConnectionStatus.CONNECTING
            self.stats['connection_attempts'] += 1

            headers = {
                'Content-Type': 'application/json',
                'User-Agent': f'OrionAgent/{self.agent_id}'
            }

            if self.config.auth_token:
                headers['Authorization'] = f"Bearer {self.config.auth_token}"

            # HTTP/2 support
            http2_enabled = self.config.protocol_type == ProtocolType.HTTP2

            self.client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=self.config.timeout,
                http2=http2_enabled
            )

            # Connection test
            response = await self.client.get("/health")
            if response.status_code == 200:
                self.status = ConnectionStatus.CONNECTED
                self.stats['last_activity'] = time.time()
                return True
            else:
                self.status = ConnectionStatus.ERROR
                return False

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.stats['errors'] += 1
            print(f"HTTP connection error: {e}")
            return False

    async def disconnect(self) -> bool:
        """HTTP client bağlantısını kapat"""
        try:
            if self.client:
                await self.client.aclose()
                self.client = None

            self.status = ConnectionStatus.DISCONNECTED
            return True

        except Exception as e:
            print(f"HTTP disconnect error: {e}")
            return False

    async def send_message(self, message: OrionMessage, target: str) -> bool:
        """HTTP POST ile mesaj gönder"""
        try:
            if self.status != ConnectionStatus.CONNECTED:
                return False

            endpoint = f"/agents/{target}/messages"
            message_data = {
                'message': asdict(message),
                'sender': self.agent_id
            }

            response = await self.client.post(endpoint, json=message_data)

            if response.status_code in [200, 201, 202]:
                self.stats['messages_sent'] += 1
                self.stats['last_activity'] = time.time()
                return True
            else:
                self.stats['errors'] += 1
                return False

        except Exception as e:
            self.stats['errors'] += 1
            print(f"HTTP send error: {e}")
            return False

    async def start_listening(self) -> bool:
        """HTTP polling ile mesaj dinleme başlat"""
        try:
            # HTTP polling task başlat
            asyncio.create_task(self._polling_loop())
            return True

        except Exception as e:
            print(f"HTTP listen start error: {e}")
            return False

    async def stop_listening(self) -> bool:
        """HTTP polling durdur"""
        # Polling loop will stop when connection is closed
        return True

    async def _polling_loop(self):
        """HTTP polling döngüsü"""
        while self.status == ConnectionStatus.CONNECTED:
            try:
                # Agent'a gelen mesajları kontrol et
                response = await self.client.get(f"/agents/{self.agent_id}/messages")

                if response.status_code == 200:
                    messages = response.json().get('messages', [])

                    for msg_data in messages:
                        message = OrionMessage.from_dict(msg_data['message'])

                        # Message handler çağır
                        message_type = message.message_type
                        if message_type in self.message_handlers:
                            self.message_handlers[message_type](message)

                        self.stats['messages_received'] += 1

                    self.stats['last_activity'] = time.time()

                # Polling interval
                await asyncio.sleep(1.0)

            except Exception as e:
                self.stats['errors'] += 1
                print(f"HTTP polling error: {e}")
                await asyncio.sleep(5.0)  # Error recovery delay


class RabbitMQAdapter(ProtocolAdapter):
    """
    RabbitMQ Protocol Adapter

    Mevcut RabbitMQ altyapısını multi-protocol sistemine entegre eder.
    """

    def __init__(self, config: ProtocolConfig, agent_id: str):
        super().__init__(config, agent_id)
        self.communication_agent = None

    async def connect(self) -> bool:
        """RabbitMQ bağlantısı kur"""
        try:
            self.status = ConnectionStatus.CONNECTING
            self.stats['connection_attempts'] += 1

            # CommunicationAgent instance oluştur
            self.communication_agent = CommunicationAgent(
                agent_id=self.agent_id,
                host=self.config.host,
                port=self.config.port,
                username=self.config.metadata.get('username', 'guest'),
                password=self.config.metadata.get('password', 'guest')
            )

            # Sync connect call
            success = await asyncio.get_event_loop().run_in_executor(
                None, self.communication_agent.connect
            )

            if success:
                self.status = ConnectionStatus.CONNECTED
                self.stats['last_activity'] = time.time()
                return True
            else:
                self.status = ConnectionStatus.ERROR
                return False

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.stats['errors'] += 1
            print(f"RabbitMQ connection error: {e}")
            return False

    async def disconnect(self) -> bool:
        """RabbitMQ bağlantısını kapat"""
        try:
            if self.communication_agent:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.communication_agent.disconnect
                )
                self.communication_agent = None

            self.status = ConnectionStatus.DISCONNECTED
            return True

        except Exception as e:
            print(f"RabbitMQ disconnect error: {e}")
            return False

    async def send_message(self, message: OrionMessage, target: str) -> bool:
        """RabbitMQ üzerinden mesaj gönder"""
        try:
            if not self.communication_agent or self.status != ConnectionStatus.CONNECTED:
                return False

            success = await asyncio.get_event_loop().run_in_executor(
                None, self.communication_agent.publish_message, target, message
            )

            if success:
                self.stats['messages_sent'] += 1
                self.stats['last_activity'] = time.time()
                return True
            else:
                self.stats['errors'] += 1
                return False

        except Exception as e:
            self.stats['errors'] += 1
            print(f"RabbitMQ send error: {e}")
            return False

    async def start_listening(self) -> bool:
        """RabbitMQ mesaj dinleme başlat"""
        try:
            if not self.communication_agent:
                return False

            # Message handlers'ı communication agent'a aktar
            for msg_type, handler in self.message_handlers.items():
                self.communication_agent.add_message_handler(msg_type, handler)

            # Async consume başlat
            asyncio.create_task(self._consume_loop())
            return True

        except Exception as e:
            print(f"RabbitMQ listen start error: {e}")
            return False

    async def stop_listening(self) -> bool:
        """RabbitMQ mesaj dinleme durdur"""
        try:
            if self.communication_agent:
                await asyncio.get_event_loop().run_in_executor(
                    None, self.communication_agent.stop_consuming
                )
            return True

        except Exception as e:
            print(f"RabbitMQ listen stop error: {e}")
            return False

    async def _consume_loop(self):
        """RabbitMQ consume döngüsü"""
        try:
            await asyncio.get_event_loop().run_in_executor(
                None, self.communication_agent.consume_messages
            )
        except Exception as e:
            print(f"RabbitMQ consume error: {e}")
            self.status = ConnectionStatus.ERROR


class MultiProtocolCommunicationManager:
    """
    Multi-Protocol Communication Manager

    Çoklu protokol desteği sağlayan ana yönetici sınıf.
    Protocol routing, load balancing ve failover işlemlerini yönetir.
    """

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.adapters: Dict[ProtocolType, ProtocolAdapter] = {}
        self.routes: List[MessageRoute] = []
        self.default_protocol = ProtocolType.RABBITMQ
        self.load_balancer_enabled = False
        self.circuit_breaker_enabled = True

        # Statistics
        self.stats = {
            'total_messages_sent': 0,
            'total_messages_received': 0,
            'protocol_usage': {},
            'routing_decisions': {},
            'failover_events': 0,
            'last_activity': None
        }

        # Circuit breaker state
        self.circuit_breaker_state = {}

        # Message handlers
        self.global_message_handlers: Dict[str, Callable] = {}

    def add_protocol(self, protocol_type: ProtocolType, config: ProtocolConfig) -> bool:
        """Protokol adapter ekle"""
        try:
            if protocol_type == ProtocolType.RABBITMQ:
                adapter = RabbitMQAdapter(config, self.agent_id)
            elif protocol_type == ProtocolType.WEBSOCKET:
                adapter = WebSocketAdapter(config, self.agent_id)
            elif protocol_type in [ProtocolType.HTTP, ProtocolType.HTTP2]:
                adapter = HTTPAdapter(config, self.agent_id)
            else:
                print(f"Unsupported protocol: {protocol_type}")
                return False

            self.adapters[protocol_type] = adapter
            self.stats['protocol_usage'][protocol_type.value] = 0
            self.circuit_breaker_state[protocol_type] = {
                'failures': 0,
                'last_failure': None,
                'state': 'closed'  # closed, open, half-open
            }

            # Global message handlers'ı adapter'a aktar
            for msg_type, handler in self.global_message_handlers.items():
                adapter.add_message_handler(msg_type, handler)

            print(f"Protocol added: {protocol_type.value}")
            return True

        except Exception as e:
            print(f"Add protocol error: {e}")
            return False

    def add_message_route(self, route: MessageRoute):
        """Mesaj routing kuralı ekle"""
        self.routes.append(route)
        print(f"Route added: {route.source_protocol.value} -> {route.target_protocol.value}")

    def add_global_message_handler(self, message_type: str, handler: Callable):
        """Global mesaj handler ekle"""
        self.global_message_handlers[message_type] = handler

        # Mevcut adapter'lara da ekle
        for adapter in self.adapters.values():
            adapter.add_message_handler(message_type, handler)

    async def connect_all(self) -> Dict[ProtocolType, bool]:
        """Tüm protokollere bağlan"""
        results = {}

        for protocol_type, adapter in self.adapters.items():
            try:
                success = await adapter.connect()
                results[protocol_type] = success

                if success:
                    print(f"Connected to {protocol_type.value}")
                else:
                    print(f"Failed to connect to {protocol_type.value}")

            except Exception as e:
                print(f"Connection error for {protocol_type.value}: {e}")
                results[protocol_type] = False

        return results

    async def disconnect_all(self) -> Dict[ProtocolType, bool]:
        """Tüm protokol bağlantılarını kapat"""
        results = {}

        for protocol_type, adapter in self.adapters.items():
            try:
                success = await adapter.disconnect()
                results[protocol_type] = success

            except Exception as e:
                print(f"Disconnect error for {protocol_type.value}: {e}")
                results[protocol_type] = False

        return results

    async def start_all_listening(self) -> Dict[ProtocolType, bool]:
        """Tüm protokollerde mesaj dinleme başlat"""
        results = {}

        for protocol_type, adapter in self.adapters.items():
            try:
                success = await adapter.start_listening()
                results[protocol_type] = success

                if success:
                    print(f"Started listening on {protocol_type.value}")
                else:
                    print(f"Failed to start listening on {protocol_type.value}")

            except Exception as e:
                print(f"Listen start error for {protocol_type.value}: {e}")
                results[protocol_type] = False

        return results

    async def send_message(self, message: OrionMessage, target: str,
                          preferred_protocol: Optional[ProtocolType] = None) -> bool:
        """
        Mesaj gönder - protokol seçimi ve routing ile

        Args:
            message: Gönderilecek mesaj
            target: Hedef agent/queue
            preferred_protocol: Tercih edilen protokol

        Returns:
            bool: Gönderim başarılı ise True
        """
        try:
            # Protokol seçimi
            selected_protocol = self._select_protocol(preferred_protocol, target)

            if not selected_protocol:
                print("No available protocol for message sending")
                return False

            # Circuit breaker kontrolü
            if not self._check_circuit_breaker(selected_protocol):
                print(f"Circuit breaker open for {selected_protocol.value}")
                # Fallback protokol dene
                selected_protocol = self._select_fallback_protocol(selected_protocol)
                if not selected_protocol:
                    return False

            adapter = self.adapters[selected_protocol]

            # Mesaj gönder
            success = await adapter.send_message(message, target)

            if success:
                self.stats['total_messages_sent'] += 1
                self.stats['protocol_usage'][selected_protocol.value] += 1
                self.stats['last_activity'] = time.time()
                self._record_routing_decision(selected_protocol, target, True)
                self._reset_circuit_breaker_failure(selected_protocol)
            else:
                self._record_circuit_breaker_failure(selected_protocol)
                self._record_routing_decision(selected_protocol, target, False)

            return success

        except Exception as e:
            print(f"Send message error: {e}")
            if selected_protocol:
                self._record_circuit_breaker_failure(selected_protocol)
            return False

    def _select_protocol(self, preferred: Optional[ProtocolType], target: str) -> Optional[ProtocolType]:
        """Mesaj gönderimi için protokol seç"""
        # Preferred protocol varsa ve kullanılabilirse
        if preferred and preferred in self.adapters:
            adapter = self.adapters[preferred]
            if adapter.status == ConnectionStatus.CONNECTED:
                return preferred

        # Route kurallarını kontrol et
        for route in self.routes:
            if route.target_address == target:
                if route.target_protocol in self.adapters:
                    adapter = self.adapters[route.target_protocol]
                    if adapter.status == ConnectionStatus.CONNECTED:
                        return route.target_protocol

        # Default protocol
        if self.default_protocol in self.adapters:
            adapter = self.adapters[self.default_protocol]
            if adapter.status == ConnectionStatus.CONNECTED:
                return self.default_protocol

        # İlk kullanılabilir protokol
        for protocol_type, adapter in self.adapters.items():
            if adapter.status == ConnectionStatus.CONNECTED:
                return protocol_type

        return None

    def _select_fallback_protocol(self, failed_protocol: ProtocolType) -> Optional[ProtocolType]:
        """Başarısız protokol için fallback seç"""
        for protocol_type, adapter in self.adapters.items():
            if (protocol_type != failed_protocol and
                adapter.status == ConnectionStatus.CONNECTED and
                self._check_circuit_breaker(protocol_type)):
                return protocol_type
        return None

    def _check_circuit_breaker(self, protocol_type: ProtocolType) -> bool:
        """Circuit breaker durumunu kontrol et"""
        if not self.circuit_breaker_enabled:
            return True

        state = self.circuit_breaker_state.get(protocol_type, {})

        if state.get('state') == 'open':
            # Half-open durumuna geçiş kontrolü (30 saniye sonra)
            if state.get('last_failure') and time.time() - state['last_failure'] > 30:
                state['state'] = 'half-open'
                return True
            return False

        return True

    def _record_circuit_breaker_failure(self, protocol_type: ProtocolType):
        """Circuit breaker failure kaydet"""
        if not self.circuit_breaker_enabled:
            return

        state = self.circuit_breaker_state[protocol_type]
        state['failures'] += 1
        state['last_failure'] = time.time()

        # 5 başarısızlık sonrası circuit breaker aç
        if state['failures'] >= 5:
            state['state'] = 'open'
            self.stats['failover_events'] += 1
            print(f"Circuit breaker opened for {protocol_type.value}")

    def _reset_circuit_breaker_failure(self, protocol_type: ProtocolType):
        """Circuit breaker başarı durumunda sıfırla"""
        if not self.circuit_breaker_enabled:
            return

        state = self.circuit_breaker_state[protocol_type]
        state['failures'] = 0
        state['state'] = 'closed'

    def _record_routing_decision(self, protocol: ProtocolType, target: str, success: bool):
        """Routing kararını kaydet"""
        key = f"{protocol.value}:{target}"
        if key not in self.stats['routing_decisions']:
            self.stats['routing_decisions'][key] = {'success': 0, 'failure': 0}

        if success:
            self.stats['routing_decisions'][key]['success'] += 1
        else:
            self.stats['routing_decisions'][key]['failure'] += 1

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı istatistikleri getir"""
        adapter_stats = {}
        for protocol_type, adapter in self.adapters.items():
            adapter_stats[protocol_type.value] = adapter.get_stats()

        return {
            'agent_id': self.agent_id,
            'manager_stats': self.stats,
            'adapter_stats': adapter_stats,
            'circuit_breaker_state': self.circuit_breaker_state,
            'active_protocols': [
                p.value for p, a in self.adapters.items()
                if a.status == ConnectionStatus.CONNECTED
            ],
            'total_routes': len(self.routes)
        }

    def get_health_status(self) -> Dict[str, Any]:
        """Sistem sağlık durumunu getir"""
        connected_protocols = 0
        total_protocols = len(self.adapters)

        protocol_health = {}
        for protocol_type, adapter in self.adapters.items():
            is_healthy = adapter.status == ConnectionStatus.CONNECTED
            if is_healthy:
                connected_protocols += 1

            protocol_health[protocol_type.value] = {
                'status': adapter.status.value,
                'healthy': is_healthy,
                'error_rate': adapter.stats.get('errors', 0) / max(1, adapter.stats.get('messages_sent', 0) + adapter.stats.get('messages_received', 0))
            }

        overall_health = "healthy" if connected_protocols > 0 else "unhealthy"
        if connected_protocols < total_protocols:
            overall_health = "degraded"

        return {
            'overall_health': overall_health,
            'connected_protocols': connected_protocols,
            'total_protocols': total_protocols,
            'protocol_health': protocol_health,
            'circuit_breaker_enabled': self.circuit_breaker_enabled,
            'load_balancer_enabled': self.load_balancer_enabled
        }


class MultiProtocolCommunication(MultiProtocolCommunicationManager):
    """
    Backward compatibility alias for MultiProtocolCommunicationManager

    This class provides backward compatibility for components that
    expect a MultiProtocolCommunication class instead of MultiProtocolCommunicationManager.
    """
    pass


if __name__ == "__main__":
    # Test the multi-protocol communication system
    import asyncio

    async def test_multi_protocol():
        manager = MultiProtocolCommunicationManager("test_agent")

        # Add WebSocket protocol
        from .multi_protocol_communication import ProtocolConfig, ProtocolType
        ws_config = ProtocolConfig(
            protocol_type=ProtocolType.WEBSOCKET,
            host="localhost",
            port=8001
        )

        manager.add_protocol("websocket", ws_config)

        # Connect all protocols
        await manager.connect_all()

        # Test message sending
        from .agents.communication_agent import OrionMessage, MessageType
        test_message = OrionMessage(
            message_id="test_msg_1",
            sender_id="test_agent",
            recipient_id="target_agent",
            message_type=MessageType.CHAT,
            content="Hello from multi-protocol!"
        )

        success = await manager.send_message(test_message, "target_agent")
        print(f"Message sent: {success}")

        # Disconnect all
        await manager.disconnect_all()

    asyncio.run(test_multi_protocol())
