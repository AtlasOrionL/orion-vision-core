#!/usr/bin/env python3
"""
🤝 Agent Communication Core - Gaming AI

Core communication system for multi-agent coordination.

Sprint 4 - Task 4.1 Module 1: Agent Communication
- Basic agent-to-agent messaging
- Communication protocols  
- Message routing and delivery
- <10ms communication latency

Author: Nexus - Quantum AI Architect
Sprint: 4.1.1 - Advanced Gaming Features
"""

import time
import threading
import logging
import json
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

class MessageType(Enum):
    """Message type enumeration"""
    STRATEGY_UPDATE = "strategy_update"
    POSITION_UPDATE = "position_update"
    THREAT_ALERT = "threat_alert"
    RESOURCE_REQUEST = "resource_request"
    COORDINATION_REQUEST = "coordination_request"
    STATUS_UPDATE = "status_update"
    EMERGENCY = "emergency"

class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class Message:
    """Communication message between agents"""
    message_id: str
    sender_id: str
    recipient_id: str  # Can be "ALL" for broadcast
    message_type: MessageType
    priority: MessagePriority
    content: Dict[str, Any]
    timestamp: float
    expires_at: Optional[float] = None
    requires_ack: bool = False

@dataclass
class Agent:
    """Agent information for communication"""
    agent_id: str
    agent_type: str
    status: str = "active"
    last_seen: float = 0.0
    message_queue: deque = field(default_factory=lambda: deque(maxlen=100))
    capabilities: List[str] = field(default_factory=list)

class AgentCommunication:
    """
    Agent Communication Core System
    
    Features:
    - Ultra-fast message delivery (<10ms)
    - Priority-based message routing
    - Broadcast and unicast messaging
    - Message acknowledgment system
    - Agent discovery and registration
    """
    
    def __init__(self, max_agents: int = 8):
        self.max_agents = max_agents
        self.logger = logging.getLogger("AgentCommunication")
        
        # Agent management
        self.agents = {}  # agent_id -> Agent
        self.agent_callbacks = {}  # agent_id -> callback function
        
        # Message routing
        self.message_queue = deque(maxlen=1000)
        self.pending_acks = {}  # message_id -> (sender, timestamp)
        
        # Threading for message processing
        self.communication_active = False
        self.message_thread = None
        self.comm_lock = threading.RLock()
        
        # Performance tracking
        self.message_stats = {
            'messages_sent': 0,
            'messages_delivered': 0,
            'average_latency': 0.0,
            'failed_deliveries': 0
        }
        
        # Message routing table
        self.routing_table = {}
        
        self.logger.info(f"🤝 Agent Communication initialized (max agents: {max_agents})")
    
    def register_agent(self, agent_id: str, agent_type: str, 
                      capabilities: List[str], 
                      message_callback: Callable[[Message], None]) -> bool:
        """Register new agent for communication"""
        try:
            with self.comm_lock:
                if len(self.agents) >= self.max_agents:
                    self.logger.warning(f"⚠️ Maximum agents ({self.max_agents}) reached")
                    return False
                
                if agent_id in self.agents:
                    self.logger.warning(f"⚠️ Agent {agent_id} already registered")
                    return False
                
                # Create agent
                agent = Agent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    status="active",
                    last_seen=time.time(),
                    capabilities=capabilities.copy()
                )
                
                self.agents[agent_id] = agent
                self.agent_callbacks[agent_id] = message_callback
                
                # Update routing table
                self._update_routing_table()
                
                # Announce new agent to others
                self._broadcast_agent_announcement(agent)
                
                self.logger.info(f"✅ Agent registered: {agent_id} ({agent_type})")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Agent registration failed: {e}")
            return False
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister agent from communication"""
        try:
            with self.comm_lock:
                if agent_id not in self.agents:
                    return False
                
                # Remove agent
                del self.agents[agent_id]
                if agent_id in self.agent_callbacks:
                    del self.agent_callbacks[agent_id]
                
                # Update routing table
                self._update_routing_table()
                
                # Announce agent departure
                self._broadcast_agent_departure(agent_id)
                
                self.logger.info(f"🚪 Agent unregistered: {agent_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Agent unregistration failed: {e}")
            return False
    
    def send_message(self, sender_id: str, recipient_id: str, 
                    message_type: MessageType, content: Dict[str, Any],
                    priority: MessagePriority = MessagePriority.NORMAL,
                    requires_ack: bool = False, ttl_seconds: float = 30.0) -> str:
        """Send message between agents"""
        try:
            # Generate message ID
            message_id = str(uuid.uuid4())
            
            # Calculate expiration
            expires_at = time.time() + ttl_seconds if ttl_seconds > 0 else None
            
            # Create message
            message = Message(
                message_id=message_id,
                sender_id=sender_id,
                recipient_id=recipient_id,
                message_type=message_type,
                priority=priority,
                content=content.copy(),
                timestamp=time.time(),
                expires_at=expires_at,
                requires_ack=requires_ack
            )
            
            # Queue message for delivery
            with self.comm_lock:
                self.message_queue.append(message)
                
                # Track acknowledgment if required
                if requires_ack:
                    self.pending_acks[message_id] = (sender_id, time.time())
                
                self.message_stats['messages_sent'] += 1
            
            self.logger.debug(f"📤 Message queued: {message_id[:8]}... ({message_type.value})")
            return message_id
            
        except Exception as e:
            self.logger.error(f"❌ Message send failed: {e}")
            return ""
    
    def broadcast_message(self, sender_id: str, message_type: MessageType, 
                         content: Dict[str, Any],
                         priority: MessagePriority = MessagePriority.NORMAL) -> str:
        """Broadcast message to all agents"""
        return self.send_message(sender_id, "ALL", message_type, content, priority)
    
    def acknowledge_message(self, agent_id: str, message_id: str) -> bool:
        """Acknowledge received message"""
        try:
            with self.comm_lock:
                if message_id in self.pending_acks:
                    sender_id, sent_time = self.pending_acks[message_id]
                    
                    # Calculate latency
                    latency = time.time() - sent_time
                    self._update_latency_stats(latency)
                    
                    # Remove from pending
                    del self.pending_acks[message_id]
                    
                    # Notify sender of acknowledgment
                    ack_content = {
                        'original_message_id': message_id,
                        'acknowledged_by': agent_id,
                        'latency': latency
                    }
                    
                    self.send_message(
                        "SYSTEM", sender_id, 
                        MessageType.STATUS_UPDATE, ack_content,
                        MessagePriority.LOW
                    )
                    
                    self.logger.debug(f"✅ Message acknowledged: {message_id[:8]}... (latency: {latency:.3f}s)")
                    return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Message acknowledgment failed: {e}")
            return False
    
    def start_communication(self) -> bool:
        """Start message processing"""
        if self.communication_active:
            return True

        try:
            self.communication_active = True
            self.message_thread = threading.Thread(target=self._message_processing_loop, daemon=True)
            self.message_thread.start()
            self.logger.info("🔄 Communication started")
            return True
        except Exception as e:
            self.logger.error(f"❌ Communication start failed: {e}")
            return False
    
    def stop_communication(self):
        """Stop message processing"""
        self.communication_active = False
        if self.message_thread:
            self.message_thread.join(timeout=1.0)
        self.logger.info("🛑 Communication stopped")
    
    def _message_processing_loop(self):
        """Main message processing loop"""
        while self.communication_active:
            try:
                # Process pending messages
                messages_processed = 0
                
                with self.comm_lock:
                    # Process messages by priority
                    sorted_messages = sorted(
                        list(self.message_queue), 
                        key=lambda m: m.priority.value, 
                        reverse=True
                    )
                    
                    self.message_queue.clear()
                    
                    for message in sorted_messages:
                        if self._deliver_message(message):
                            messages_processed += 1
                
                # Clean up expired acknowledgments
                self._cleanup_expired_acks()
                
                # Update agent status
                self._update_agent_status()
                
                # Sleep briefly to maintain <10ms target
                time.sleep(0.001)  # 1ms sleep
                
            except Exception as e:
                self.logger.error(f"❌ Message processing error: {e}")
                time.sleep(0.01)
    
    def _deliver_message(self, message: Message) -> bool:
        """Deliver message to recipient(s)"""
        try:
            delivery_start = time.time()
            
            # Check if message expired
            if message.expires_at and time.time() > message.expires_at:
                self.logger.debug(f"⏰ Message expired: {message.message_id[:8]}...")
                return False
            
            # Determine recipients
            recipients = []
            if message.recipient_id == "ALL":
                recipients = [aid for aid in self.agents.keys() if aid != message.sender_id]
            elif message.recipient_id in self.agents:
                recipients = [message.recipient_id]
            else:
                self.logger.warning(f"⚠️ Unknown recipient: {message.recipient_id}")
                self.message_stats['failed_deliveries'] += 1
                return False
            
            # Deliver to each recipient
            delivered = False
            for recipient_id in recipients:
                if self._deliver_to_agent(message, recipient_id):
                    delivered = True
            
            if delivered:
                # Update latency stats
                latency = time.time() - delivery_start
                self._update_latency_stats(latency)
                self.message_stats['messages_delivered'] += 1
            
            return delivered
            
        except Exception as e:
            self.logger.error(f"❌ Message delivery failed: {e}")
            self.message_stats['failed_deliveries'] += 1
            return False
    
    def _deliver_to_agent(self, message: Message, recipient_id: str) -> bool:
        """Deliver message to specific agent"""
        try:
            if recipient_id not in self.agents:
                return False
            
            agent = self.agents[recipient_id]
            
            # Add to agent's message queue
            agent.message_queue.append(message)
            agent.last_seen = time.time()
            
            # Call agent's message callback
            if recipient_id in self.agent_callbacks:
                callback = self.agent_callbacks[recipient_id]
                # Call callback in separate thread to avoid blocking
                threading.Thread(
                    target=self._safe_callback_call,
                    args=(callback, message),
                    daemon=True
                ).start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Agent delivery failed: {e}")
            return False
    
    def _safe_callback_call(self, callback: Callable, message: Message):
        """Safely call agent callback"""
        try:
            callback(message)
        except Exception as e:
            self.logger.error(f"❌ Agent callback failed: {e}")
    
    def _update_latency_stats(self, latency: float):
        """Update latency statistics"""
        current_avg = self.message_stats['average_latency']
        delivered = self.message_stats['messages_delivered']
        
        if delivered > 0:
            self.message_stats['average_latency'] = (
                (current_avg * (delivered - 1) + latency) / delivered
            )
        else:
            self.message_stats['average_latency'] = latency
    
    def _cleanup_expired_acks(self):
        """Clean up expired acknowledgment requests"""
        current_time = time.time()
        expired_acks = []
        
        for message_id, (sender_id, sent_time) in self.pending_acks.items():
            if current_time - sent_time > 30.0:  # 30 second timeout
                expired_acks.append(message_id)
        
        for message_id in expired_acks:
            del self.pending_acks[message_id]
            self.logger.debug(f"⏰ Acknowledgment expired: {message_id[:8]}...")
    
    def _update_agent_status(self):
        """Update agent status based on activity"""
        current_time = time.time()
        
        for agent_id, agent in self.agents.items():
            if current_time - agent.last_seen > 10.0:  # 10 seconds inactive
                if agent.status == "active":
                    agent.status = "inactive"
                    self.logger.warning(f"⚠️ Agent inactive: {agent_id}")
    
    def _update_routing_table(self):
        """Update message routing table"""
        self.routing_table = {
            agent_id: {
                'type': agent.agent_type,
                'capabilities': agent.capabilities,
                'status': agent.status
            }
            for agent_id, agent in self.agents.items()
        }
    
    def _broadcast_agent_announcement(self, agent: Agent):
        """Broadcast new agent announcement"""
        content = {
            'agent_id': agent.agent_id,
            'agent_type': agent.agent_type,
            'capabilities': agent.capabilities,
            'event': 'agent_joined'
        }
        
        self.broadcast_message(
            "SYSTEM", MessageType.STATUS_UPDATE, content, MessagePriority.NORMAL
        )
    
    def _broadcast_agent_departure(self, agent_id: str):
        """Broadcast agent departure"""
        content = {
            'agent_id': agent_id,
            'event': 'agent_left'
        }
        
        self.broadcast_message(
            "SYSTEM", MessageType.STATUS_UPDATE, content, MessagePriority.NORMAL
        )
    
    def get_communication_stats(self) -> Dict[str, Any]:
        """Get communication statistics"""
        with self.comm_lock:
            return {
                'active_agents': len([a for a in self.agents.values() if a.status == "active"]),
                'total_agents': len(self.agents),
                'messages_sent': self.message_stats['messages_sent'],
                'messages_delivered': self.message_stats['messages_delivered'],
                'average_latency': self.message_stats['average_latency'],
                'failed_deliveries': self.message_stats['failed_deliveries'],
                'pending_acks': len(self.pending_acks),
                'queue_size': len(self.message_queue),
                'communication_active': self.communication_active
            }
    
    def get_agent_list(self) -> List[Dict[str, Any]]:
        """Get list of registered agents"""
        with self.comm_lock:
            return [
                {
                    'agent_id': agent.agent_id,
                    'agent_type': agent.agent_type,
                    'status': agent.status,
                    'last_seen': agent.last_seen,
                    'capabilities': agent.capabilities,
                    'queue_size': len(agent.message_queue)
                }
                for agent in self.agents.values()
            ]

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🤝 Agent Communication Core - Sprint 4 Test")
    print("=" * 60)
    
    # Create communication system
    comm = AgentCommunication(max_agents=4)
    
    # Test agent callbacks
    def agent_callback(agent_id: str):
        def callback(message: Message):
            print(f"📨 {agent_id} received: {message.message_type.value} from {message.sender_id}")
        return callback
    
    # Test agent registration
    print("\n🤝 Testing agent registration...")
    
    agents = [
        ("agent_1", "sniper", ["long_range", "precision"]),
        ("agent_2", "assault", ["close_combat", "mobility"]),
        ("agent_3", "support", ["healing", "resources"])
    ]
    
    for agent_id, agent_type, capabilities in agents:
        success = comm.register_agent(agent_id, agent_type, capabilities, agent_callback(agent_id))
        print(f"   {agent_id}: {'✅' if success else '❌'}")
    
    # Start communication
    comm.start_communication()
    
    # Test messaging
    print("\n📤 Testing messaging...")
    
    # Send some test messages
    msg_id1 = comm.send_message(
        "agent_1", "agent_2", 
        MessageType.POSITION_UPDATE, 
        {"x": 100, "y": 200, "facing": 45},
        MessagePriority.HIGH
    )
    
    msg_id2 = comm.broadcast_message(
        "agent_3",
        MessageType.THREAT_ALERT,
        {"threat_level": "high", "location": {"x": 150, "y": 180}},
        MessagePriority.CRITICAL
    )
    
    print(f"   Position update: {msg_id1[:8]}...")
    print(f"   Threat alert: {msg_id2[:8]}...")
    
    # Wait for message processing
    time.sleep(0.1)
    
    # Get statistics
    stats = comm.get_communication_stats()
    print(f"\n📊 Communication Stats:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get agent list
    agent_list = comm.get_agent_list()
    print(f"\n👥 Active Agents:")
    for agent in agent_list:
        print(f"   {agent['agent_id']}: {agent['agent_type']} ({agent['status']})")
    
    # Stop communication
    comm.stop_communication()
    
    print("\n🎉 Sprint 4 - Task 4.1 Module 1 test completed!")
    print("🎯 Target: <10ms communication latency")
    print(f"📈 Current: {stats['average_latency']*1000:.1f}ms average latency")
