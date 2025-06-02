"""
Real-time Communication Manager for Orion Vision Core

This module provides real-time communication capabilities including WebSocket,
Server-Sent Events, and real-time messaging.
Part of Sprint 9.3 Advanced Networking & Communication development.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.3 - Advanced Networking & Communication
"""

import asyncio
import json
import time
import threading
from typing import Dict, List, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
import uuid

from ...agent.core.agent_logger import AgentLogger
from ...monitoring.core.metrics_collector import MetricsCollector, MetricType


class MessageType(Enum):
    """Real-time message type enumeration"""
    TEXT = "text"
    BINARY = "binary"
    JSON = "json"
    PING = "ping"
    PONG = "pong"
    SYSTEM = "system"
    BROADCAST = "broadcast"
    PRIVATE = "private"


class ChannelType(Enum):
    """Communication channel type enumeration"""
    PUBLIC = "public"
    PRIVATE = "private"
    SYSTEM = "system"
    BROADCAST = "broadcast"


class ClientState(Enum):
    """Client connection state enumeration"""
    CONNECTING = "connecting"
    CONNECTED = "connected"
    DISCONNECTING = "disconnecting"
    DISCONNECTED = "disconnected"
    ERROR = "error"


@dataclass
class RealtimeMessage:
    """Real-time message data structure"""
    message_id: str
    message_type: MessageType
    channel: str
    sender_id: str
    content: Any
    timestamp: float = field(default_factory=time.time)
    recipients: Optional[List[str]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'channel': self.channel,
            'sender_id': self.sender_id,
            'content': self.content,
            'timestamp': self.timestamp,
            'recipients': self.recipients,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RealtimeMessage':
        """Create message from dictionary"""
        return cls(
            message_id=data['message_id'],
            message_type=MessageType(data['message_type']),
            channel=data['channel'],
            sender_id=data['sender_id'],
            content=data['content'],
            timestamp=data.get('timestamp', time.time()),
            recipients=data.get('recipients'),
            metadata=data.get('metadata', {})
        )


@dataclass
class RealtimeClient:
    """Real-time client data structure"""
    client_id: str
    session_id: str
    state: ClientState = ClientState.CONNECTING
    connected_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    subscribed_channels: Set[str] = field(default_factory=set)
    messages_sent: int = 0
    messages_received: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self.state == ClientState.CONNECTED
    
    def get_uptime(self) -> float:
        """Get client uptime in seconds"""
        if self.state == ClientState.CONNECTED:
            return time.time() - self.connected_at
        return 0.0


@dataclass
class RealtimeChannel:
    """Real-time communication channel"""
    channel_id: str
    channel_type: ChannelType
    name: str
    description: str = ""
    max_clients: int = 1000
    created_at: float = field(default_factory=time.time)
    clients: Set[str] = field(default_factory=set)
    message_history: List[RealtimeMessage] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_client(self, client_id: str) -> bool:
        """Add client to channel"""
        if len(self.clients) >= self.max_clients:
            return False
        
        self.clients.add(client_id)
        return True
    
    def remove_client(self, client_id: str) -> bool:
        """Remove client from channel"""
        if client_id in self.clients:
            self.clients.remove(client_id)
            return True
        return False
    
    def get_client_count(self) -> int:
        """Get number of clients in channel"""
        return len(self.clients)


class RealtimeManager:
    """
    Real-time communication management system
    
    Provides WebSocket-like real-time communication, channel management,
    message broadcasting, and real-time event handling.
    """
    
    def __init__(self, metrics_collector: Optional[MetricsCollector] = None,
                 logger: Optional[AgentLogger] = None):
        """Initialize real-time manager"""
        self.logger = logger or AgentLogger("realtime_manager")
        self.metrics_collector = metrics_collector or MetricsCollector(self.logger)
        
        # Client and channel management
        self.clients: Dict[str, RealtimeClient] = {}
        self.channels: Dict[str, RealtimeChannel] = {}
        
        # Message handling
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.message_handlers: Dict[MessageType, List[Callable]] = {}
        
        # Configuration
        self.max_clients = 10000
        self.max_message_size = 1024 * 1024  # 1MB
        self.message_history_limit = 1000
        self.ping_interval = 30.0
        
        # Event loop and tasks
        self.loop = None
        self.running = False
        self.message_processor_task = None
        self.ping_task = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.realtime_stats = {
            'total_clients': 0,
            'active_clients': 0,
            'total_channels': 0,
            'total_messages': 0,
            'messages_per_second': 0.0,
            'broadcast_messages': 0,
            'private_messages': 0,
            'connection_errors': 0,
            'message_errors': 0
        }
        
        # Create default channels
        self._create_default_channels()
        
        self.logger.info("Real-time Manager initialized")
    
    def start(self):
        """Start real-time communication system"""
        if self.running:
            self.logger.warning("Real-time manager already running")
            return
        
        self.running = True
        
        # Start event loop in separate thread
        self.loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self.loop_thread.start()
        
        self.logger.info("Real-time communication system started")
    
    def stop(self):
        """Stop real-time communication system"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel tasks
        if self.loop and not self.loop.is_closed():
            if self.message_processor_task:
                self.message_processor_task.cancel()
            if self.ping_task:
                self.ping_task.cancel()
        
        self.logger.info("Real-time communication system stopped")
    
    def connect_client(self, client_id: str, session_id: Optional[str] = None) -> bool:
        """Connect real-time client"""
        try:
            with self._lock:
                # Check client limit
                if len(self.clients) >= self.max_clients:
                    self.logger.warning("Client limit reached", max_clients=self.max_clients)
                    return False
                
                # Generate session ID if not provided
                if not session_id:
                    session_id = str(uuid.uuid4())
                
                # Create client
                client = RealtimeClient(
                    client_id=client_id,
                    session_id=session_id,
                    state=ClientState.CONNECTED
                )
                
                # Store client
                self.clients[client_id] = client
                
                # Update statistics
                self.realtime_stats['total_clients'] += 1
                self.realtime_stats['active_clients'] = len(self.clients)
                
                # Collect metrics
                self.metrics_collector.collect_metric(
                    name="realtime.client_connected",
                    value=1,
                    metric_type=MetricType.COUNTER,
                    tags={'client_id': client_id}
                )
                
                self.logger.info(
                    "Real-time client connected",
                    client_id=client_id,
                    session_id=session_id,
                    total_clients=len(self.clients)
                )
                
                return True
                
        except Exception as e:
            self.realtime_stats['connection_errors'] += 1
            self.logger.error("Failed to connect client", client_id=client_id, error=str(e))
            return False
    
    def disconnect_client(self, client_id: str) -> bool:
        """Disconnect real-time client"""
        try:
            with self._lock:
                if client_id not in self.clients:
                    self.logger.warning("Client not found", client_id=client_id)
                    return False
                
                client = self.clients[client_id]
                
                # Remove client from all channels
                for channel in self.channels.values():
                    channel.remove_client(client_id)
                
                # Remove client
                del self.clients[client_id]
                
                # Update statistics
                self.realtime_stats['active_clients'] = len(self.clients)
                
                self.logger.info(
                    "Real-time client disconnected",
                    client_id=client_id,
                    uptime=client.get_uptime(),
                    messages_sent=client.messages_sent,
                    messages_received=client.messages_received
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Failed to disconnect client", client_id=client_id, error=str(e))
            return False
    
    def create_channel(self, channel_id: str, channel_type: ChannelType, 
                      name: str, description: str = "", max_clients: int = 1000) -> bool:
        """Create communication channel"""
        try:
            with self._lock:
                if channel_id in self.channels:
                    self.logger.warning("Channel already exists", channel_id=channel_id)
                    return False
                
                # Create channel
                channel = RealtimeChannel(
                    channel_id=channel_id,
                    channel_type=channel_type,
                    name=name,
                    description=description,
                    max_clients=max_clients
                )
                
                # Store channel
                self.channels[channel_id] = channel
                
                # Update statistics
                self.realtime_stats['total_channels'] = len(self.channels)
                
                self.logger.info(
                    "Real-time channel created",
                    channel_id=channel_id,
                    channel_type=channel_type.value,
                    name=name,
                    max_clients=max_clients
                )
                
                return True
                
        except Exception as e:
            self.logger.error("Failed to create channel", channel_id=channel_id, error=str(e))
            return False
    
    def subscribe_to_channel(self, client_id: str, channel_id: str) -> bool:
        """Subscribe client to channel"""
        try:
            with self._lock:
                if client_id not in self.clients:
                    self.logger.warning("Client not found", client_id=client_id)
                    return False
                
                if channel_id not in self.channels:
                    self.logger.warning("Channel not found", channel_id=channel_id)
                    return False
                
                client = self.clients[client_id]
                channel = self.channels[channel_id]
                
                # Add client to channel
                if channel.add_client(client_id):
                    client.subscribed_channels.add(channel_id)
                    
                    self.logger.info(
                        "Client subscribed to channel",
                        client_id=client_id,
                        channel_id=channel_id,
                        channel_clients=channel.get_client_count()
                    )
                    
                    return True
                else:
                    self.logger.warning("Channel is full", channel_id=channel_id, max_clients=channel.max_clients)
                    return False
                
        except Exception as e:
            self.logger.error("Failed to subscribe to channel", client_id=client_id, channel_id=channel_id, error=str(e))
            return False
    
    def send_message(self, message: RealtimeMessage) -> bool:
        """Send real-time message"""
        try:
            # Validate message size
            message_size = len(json.dumps(message.to_dict()).encode('utf-8'))
            if message_size > self.max_message_size:
                self.logger.warning("Message too large", message_size=message_size, max_size=self.max_message_size)
                return False
            
            # Add to message queue
            if self.loop and not self.loop.is_closed():
                asyncio.run_coroutine_threadsafe(
                    self.message_queue.put(message),
                    self.loop
                )
            
            # Update statistics
            self.realtime_stats['total_messages'] += 1
            
            if message.message_type == MessageType.BROADCAST:
                self.realtime_stats['broadcast_messages'] += 1
            elif message.message_type == MessageType.PRIVATE:
                self.realtime_stats['private_messages'] += 1
            
            # Collect metrics
            self.metrics_collector.collect_metric(
                name="realtime.message_sent",
                value=1,
                metric_type=MetricType.COUNTER,
                tags={
                    'message_type': message.message_type.value,
                    'channel': message.channel
                }
            )
            
            self.logger.debug(
                "Real-time message queued",
                message_id=message.message_id,
                message_type=message.message_type.value,
                channel=message.channel,
                sender_id=message.sender_id
            )
            
            return True
            
        except Exception as e:
            self.realtime_stats['message_errors'] += 1
            self.logger.error("Failed to send message", message_id=message.message_id, error=str(e))
            return False
    
    def broadcast_message(self, channel_id: str, sender_id: str, content: Any) -> bool:
        """Broadcast message to all clients in channel"""
        message = RealtimeMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.BROADCAST,
            channel=channel_id,
            sender_id=sender_id,
            content=content
        )
        
        return self.send_message(message)
    
    def send_private_message(self, sender_id: str, recipient_id: str, content: Any) -> bool:
        """Send private message to specific client"""
        message = RealtimeMessage(
            message_id=str(uuid.uuid4()),
            message_type=MessageType.PRIVATE,
            channel="private",
            sender_id=sender_id,
            content=content,
            recipients=[recipient_id]
        )
        
        return self.send_message(message)
    
    def _create_default_channels(self):
        """Create default communication channels"""
        default_channels = [
            ("system", ChannelType.SYSTEM, "System Channel", "System notifications and updates"),
            ("general", ChannelType.PUBLIC, "General Channel", "General public communication"),
            ("broadcast", ChannelType.BROADCAST, "Broadcast Channel", "System-wide broadcasts")
        ]
        
        for channel_id, channel_type, name, description in default_channels:
            self.create_channel(channel_id, channel_type, name, description)
    
    def _run_event_loop(self):
        """Run asyncio event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Start background tasks
        self.message_processor_task = self.loop.create_task(self._process_messages())
        self.ping_task = self.loop.create_task(self._ping_clients())
        
        try:
            self.loop.run_forever()
        except Exception as e:
            self.logger.error("Event loop error", error=str(e))
        finally:
            self.loop.close()
    
    async def _process_messages(self):
        """Process message queue"""
        while self.running:
            try:
                # Get message from queue
                message = await asyncio.wait_for(self.message_queue.get(), timeout=1.0)
                
                # Process message based on type
                await self._deliver_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.logger.error("Message processing error", error=str(e))
    
    async def _deliver_message(self, message: RealtimeMessage):
        """Deliver message to recipients"""
        try:
            if message.message_type == MessageType.BROADCAST:
                # Deliver to all clients in channel
                if message.channel in self.channels:
                    channel = self.channels[message.channel]
                    for client_id in channel.clients:
                        if client_id in self.clients:
                            client = self.clients[client_id]
                            client.messages_received += 1
                            client.last_activity = time.time()
            
            elif message.message_type == MessageType.PRIVATE:
                # Deliver to specific recipients
                if message.recipients:
                    for recipient_id in message.recipients:
                        if recipient_id in self.clients:
                            client = self.clients[recipient_id]
                            client.messages_received += 1
                            client.last_activity = time.time()
            
            # Add to channel history
            if message.channel in self.channels:
                channel = self.channels[message.channel]
                channel.message_history.append(message)
                
                # Limit history size
                if len(channel.message_history) > self.message_history_limit:
                    channel.message_history = channel.message_history[-self.message_history_limit:]
            
        except Exception as e:
            self.logger.error("Message delivery error", message_id=message.message_id, error=str(e))
    
    async def _ping_clients(self):
        """Send ping to all connected clients"""
        while self.running:
            try:
                current_time = time.time()
                
                for client in self.clients.values():
                    if client.is_connected():
                        # Send ping message
                        ping_message = RealtimeMessage(
                            message_id=str(uuid.uuid4()),
                            message_type=MessageType.PING,
                            channel="system",
                            sender_id="system",
                            content={"timestamp": current_time}
                        )
                        
                        await self.message_queue.put(ping_message)
                
                await asyncio.sleep(self.ping_interval)
                
            except Exception as e:
                self.logger.error("Ping error", error=str(e))
    
    def get_client_info(self, client_id: str) -> Optional[Dict[str, Any]]:
        """Get client information"""
        if client_id not in self.clients:
            return None
        
        client = self.clients[client_id]
        return {
            'client_id': client.client_id,
            'session_id': client.session_id,
            'state': client.state.value,
            'uptime': client.get_uptime(),
            'subscribed_channels': list(client.subscribed_channels),
            'messages_sent': client.messages_sent,
            'messages_received': client.messages_received,
            'last_activity': client.last_activity
        }
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict[str, Any]]:
        """Get channel information"""
        if channel_id not in self.channels:
            return None
        
        channel = self.channels[channel_id]
        return {
            'channel_id': channel.channel_id,
            'channel_type': channel.channel_type.value,
            'name': channel.name,
            'description': channel.description,
            'client_count': channel.get_client_count(),
            'max_clients': channel.max_clients,
            'message_count': len(channel.message_history),
            'created_at': channel.created_at
        }
    
    def get_realtime_stats(self) -> Dict[str, Any]:
        """Get real-time communication statistics"""
        with self._lock:
            return {
                'running': self.running,
                'total_clients': len(self.clients),
                'total_channels': len(self.channels),
                'max_clients': self.max_clients,
                'max_message_size': self.max_message_size,
                'ping_interval': self.ping_interval,
                'stats': self.realtime_stats.copy()
            }
