"""
Base Protocol Classes for Orion Vision Core

This module contains base communication protocol definitions and interfaces.
Extracted from multi_protocol_communication.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from ...agent.core.agent_logger import AgentLogger


class ProtocolType(Enum):
    """Supported protocol types"""
    RABBITMQ = "rabbitmq"
    WEBSOCKET = "websocket"
    GRPC = "grpc"
    HTTP2 = "http2"
    HTTP = "http"
    TCP = "tcp"


class ConnectionStatus(Enum):
    """Connection status enumeration"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    RECONNECTING = "reconnecting"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    URGENT = 5


class MessageType(Enum):
    """Message type enumeration"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    HEARTBEAT = "heartbeat"
    DISCOVERY = "discovery"
    NOTIFICATION = "notification"
    ERROR = "error"
    COMMAND = "command"


@dataclass
class ProtocolConfig:
    """Protocol configuration data structure"""
    protocol_type: ProtocolType
    host: str = "localhost"
    port: int = 8080
    path: str = "/"
    ssl_enabled: bool = False
    auth_token: Optional[str] = None
    timeout: float = 30.0
    retry_attempts: int = 3
    retry_delay: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.host:
            raise ValueError("host cannot be empty")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("port must be between 1 and 65535")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.retry_attempts < 0:
            raise ValueError("retry_attempts cannot be negative")
        if self.retry_delay < 0:
            raise ValueError("retry_delay cannot be negative")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'protocol_type': self.protocol_type.value,
            'host': self.host,
            'port': self.port,
            'path': self.path,
            'ssl_enabled': self.ssl_enabled,
            'auth_token': self.auth_token,
            'timeout': self.timeout,
            'retry_attempts': self.retry_attempts,
            'retry_delay': self.retry_delay,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolConfig':
        """Create configuration from dictionary"""
        protocol_type = ProtocolType(data.get('protocol_type', 'http'))
        return cls(
            protocol_type=protocol_type,
            host=data.get('host', 'localhost'),
            port=data.get('port', 8080),
            path=data.get('path', '/'),
            ssl_enabled=data.get('ssl_enabled', False),
            auth_token=data.get('auth_token'),
            timeout=data.get('timeout', 30.0),
            retry_attempts=data.get('retry_attempts', 3),
            retry_delay=data.get('retry_delay', 1.0),
            metadata=data.get('metadata', {})
        )


@dataclass
class CommunicationMessage:
    """Communication message structure"""
    message_id: str
    message_type: MessageType
    sender_id: str
    recipient_id: str
    content: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: float = field(default_factory=time.time)
    ttl: Optional[float] = None  # Time to live in seconds
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate message after initialization"""
        if not self.message_id:
            raise ValueError("message_id cannot be empty")
        if not self.sender_id:
            raise ValueError("sender_id cannot be empty")
        if not self.recipient_id:
            raise ValueError("recipient_id cannot be empty")
        if not isinstance(self.content, dict):
            raise ValueError("content must be a dictionary")
    
    def is_expired(self) -> bool:
        """Check if message has expired"""
        if self.ttl is None:
            return False
        return time.time() > (self.timestamp + self.ttl)
    
    def get_age_seconds(self) -> float:
        """Get message age in seconds"""
        return time.time() - self.timestamp
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        return {
            'message_id': self.message_id,
            'message_type': self.message_type.value,
            'sender_id': self.sender_id,
            'recipient_id': self.recipient_id,
            'content': self.content,
            'priority': self.priority.value,
            'timestamp': self.timestamp,
            'ttl': self.ttl,
            'correlation_id': self.correlation_id,
            'reply_to': self.reply_to,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommunicationMessage':
        """Create message from dictionary"""
        message_type = MessageType(data.get('message_type', 'notification'))
        priority = MessagePriority(data.get('priority', MessagePriority.NORMAL.value))
        
        return cls(
            message_id=data.get('message_id', ''),
            message_type=message_type,
            sender_id=data.get('sender_id', ''),
            recipient_id=data.get('recipient_id', ''),
            content=data.get('content', {}),
            priority=priority,
            timestamp=data.get('timestamp', time.time()),
            ttl=data.get('ttl'),
            correlation_id=data.get('correlation_id'),
            reply_to=data.get('reply_to'),
            metadata=data.get('metadata', {})
        )


@dataclass
class MessageRoute:
    """Message routing information"""
    source_protocol: ProtocolType
    target_protocol: ProtocolType
    source_address: str
    target_address: str
    transformation_rules: Dict[str, Any] = field(default_factory=dict)
    load_balancing: bool = False
    failover_enabled: bool = False
    
    def __post_init__(self):
        """Validate route after initialization"""
        if not self.source_address:
            raise ValueError("source_address cannot be empty")
        if not self.target_address:
            raise ValueError("target_address cannot be empty")


class ProtocolAdapter(ABC):
    """
    Protocol Adapter Abstract Base Class
    
    Each protocol implements this interface for unified communication.
    """
    
    def __init__(self, config: ProtocolConfig, agent_id: str, logger: Optional[AgentLogger] = None):
        self.config = config
        self.agent_id = agent_id
        self.logger = logger or AgentLogger(f"protocol_{config.protocol_type.value}")
        self.status = ConnectionStatus.DISCONNECTED
        self.message_handlers: Dict[MessageType, Callable] = {}
        self.stats = {
            'messages_sent': 0,
            'messages_received': 0,
            'connection_attempts': 0,
            'last_activity': None,
            'errors': 0,
            'bytes_sent': 0,
            'bytes_received': 0
        }
        
        self.logger.info(
            "Protocol adapter initialized",
            protocol_type=config.protocol_type.value,
            agent_id=agent_id,
            host=config.host,
            port=config.port
        )
    
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to protocol"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from protocol"""
        pass
    
    @abstractmethod
    async def send_message(self, message: CommunicationMessage, target: str) -> bool:
        """Send message through protocol"""
        pass
    
    @abstractmethod
    async def start_listening(self) -> bool:
        """Start listening for messages"""
        pass
    
    @abstractmethod
    async def stop_listening(self) -> bool:
        """Stop listening for messages"""
        pass
    
    def add_message_handler(self, message_type: MessageType, handler: Callable):
        """Add message handler for specific message type"""
        self.message_handlers[message_type] = handler
        
        self.logger.info(
            "Message handler added",
            message_type=message_type.value,
            handler_name=handler.__name__
        )
    
    def remove_message_handler(self, message_type: MessageType):
        """Remove message handler"""
        if message_type in self.message_handlers:
            del self.message_handlers[message_type]
            
            self.logger.info(
                "Message handler removed",
                message_type=message_type.value
            )
    
    def handle_message(self, message: CommunicationMessage):
        """Handle incoming message"""
        try:
            # Update statistics
            self.stats['messages_received'] += 1
            self.stats['last_activity'] = time.time()
            
            # Check if message is expired
            if message.is_expired():
                self.logger.warning(
                    "Received expired message",
                    message_id=message.message_id,
                    age_seconds=message.get_age_seconds()
                )
                return
            
            # Call appropriate handler
            if message.message_type in self.message_handlers:
                handler = self.message_handlers[message.message_type]
                handler(message)
                
                self.logger.debug(
                    "Message handled successfully",
                    message_id=message.message_id,
                    message_type=message.message_type.value,
                    sender_id=message.sender_id
                )
            else:
                self.logger.warning(
                    "No handler found for message type",
                    message_type=message.message_type.value,
                    message_id=message.message_id
                )
                
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(
                "Message handling failed",
                message_id=message.message_id,
                error=str(e)
            )
    
    def update_stats(self, messages_sent: int = 0, messages_received: int = 0, 
                    bytes_sent: int = 0, bytes_received: int = 0, errors: int = 0):
        """Update adapter statistics"""
        self.stats['messages_sent'] += messages_sent
        self.stats['messages_received'] += messages_received
        self.stats['bytes_sent'] += bytes_sent
        self.stats['bytes_received'] += bytes_received
        self.stats['errors'] += errors
        self.stats['last_activity'] = time.time()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            'protocol': self.config.protocol_type.value,
            'status': self.status.value,
            'agent_id': self.agent_id,
            'config': {
                'host': self.config.host,
                'port': self.config.port,
                'ssl_enabled': self.config.ssl_enabled
            },
            'handlers_count': len(self.message_handlers),
            **self.stats
        }
    
    def is_connected(self) -> bool:
        """Check if adapter is connected"""
        return self.status == ConnectionStatus.CONNECTED
    
    def is_healthy(self) -> bool:
        """Check if adapter is healthy"""
        if not self.is_connected():
            return False
        
        # Check last activity (should be within last 60 seconds for healthy connection)
        if self.stats['last_activity']:
            time_since_activity = time.time() - self.stats['last_activity']
            return time_since_activity < 60.0
        
        return True


class BaseProtocol(ProtocolAdapter):
    """
    Base Protocol Implementation

    Provides a concrete implementation of ProtocolAdapter for basic
    communication needs with mock functionality for testing.
    """

    def __init__(self, config: ProtocolConfig, agent_id: str, logger: Optional[AgentLogger] = None):
        """Initialize base protocol"""
        super().__init__(config, agent_id, logger)
        self.connected = False
        self.listening = False

    async def connect(self) -> bool:
        """Connect to protocol (mock implementation)"""
        try:
            self.stats['connection_attempts'] += 1
            self.status = ConnectionStatus.CONNECTING

            # Mock connection delay
            import asyncio
            await asyncio.sleep(0.1)

            self.status = ConnectionStatus.CONNECTED
            self.connected = True
            self.stats['last_activity'] = time.time()

            self.logger.info(
                "Protocol connected successfully",
                protocol_type=self.config.protocol_type.value,
                host=self.config.host,
                port=self.config.port
            )

            return True

        except Exception as e:
            self.status = ConnectionStatus.ERROR
            self.stats['errors'] += 1
            self.logger.error("Protocol connection failed", error=str(e))
            return False

    async def disconnect(self) -> bool:
        """Disconnect from protocol"""
        try:
            if self.listening:
                await self.stop_listening()

            self.status = ConnectionStatus.DISCONNECTED
            self.connected = False

            self.logger.info("Protocol disconnected successfully")
            return True

        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error("Protocol disconnection failed", error=str(e))
            return False

    async def send_message(self, message: CommunicationMessage, target: str) -> bool:
        """Send message through protocol (mock implementation)"""
        try:
            if not self.connected:
                self.logger.error("Cannot send message: not connected")
                return False

            # Mock message sending
            self.stats['messages_sent'] += 1
            self.stats['bytes_sent'] += len(str(message.content))
            self.stats['last_activity'] = time.time()

            self.logger.debug(
                "Message sent successfully",
                message_id=message.message_id,
                target=target,
                message_type=message.message_type.value
            )

            return True

        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error("Message sending failed", message_id=message.message_id, error=str(e))
            return False

    async def start_listening(self) -> bool:
        """Start listening for messages (mock implementation)"""
        try:
            if not self.connected:
                self.logger.error("Cannot start listening: not connected")
                return False

            self.listening = True
            self.logger.info("Started listening for messages")
            return True

        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error("Failed to start listening", error=str(e))
            return False

    async def stop_listening(self) -> bool:
        """Stop listening for messages"""
        try:
            self.listening = False
            self.logger.info("Stopped listening for messages")
            return True

        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error("Failed to stop listening", error=str(e))
            return False

    def is_listening(self) -> bool:
        """Check if protocol is listening"""
        return self.listening
