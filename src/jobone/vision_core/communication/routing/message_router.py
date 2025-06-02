"""
Message Router for Orion Vision Core

This module provides intelligent message routing and protocol bridging.
Extracted from multi_protocol_communication.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import asyncio
import time
import threading
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict, deque
from enum import Enum

from ..core.base_protocol import (
    ProtocolAdapter, CommunicationMessage, MessageRoute, 
    ProtocolType, MessageType, MessagePriority
)
from ...agent.core.agent_logger import AgentLogger


class RoutingStrategy(Enum):
    """Message routing strategies"""
    DIRECT = "direct"
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED = "weighted"
    FAILOVER = "failover"


class MessageRouter:
    """
    Message Router
    
    Routes messages between different protocols and agents with load balancing.
    """
    
    def __init__(self, logger: Optional[AgentLogger] = None):
        """Initialize message router"""
        self.logger = logger or AgentLogger("message_router")
        
        # Protocol adapters
        self.adapters: Dict[str, ProtocolAdapter] = {}  # adapter_id -> adapter
        self.protocol_adapters: Dict[ProtocolType, List[str]] = defaultdict(list)  # protocol -> adapter_ids
        
        # Routing configuration
        self.routes: Dict[str, MessageRoute] = {}  # route_id -> route
        self.agent_routes: Dict[str, List[str]] = defaultdict(list)  # agent_id -> route_ids
        
        # Load balancing
        self.routing_strategy = RoutingStrategy.ROUND_ROBIN
        self.adapter_weights: Dict[str, float] = {}  # adapter_id -> weight
        self.adapter_connections: Dict[str, int] = defaultdict(int)  # adapter_id -> connection_count
        self.round_robin_counters: Dict[ProtocolType, int] = defaultdict(int)
        
        # Message queues
        self.message_queues: Dict[MessagePriority, deque] = {
            priority: deque() for priority in MessagePriority
        }
        self.pending_messages: Dict[str, CommunicationMessage] = {}  # message_id -> message
        
        # Router state
        self.running = False
        self.router_task = None
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self.router_stats = {
            'total_messages_routed': 0,
            'total_messages_failed': 0,
            'total_routes_created': 0,
            'average_routing_time': 0.0,
            'protocol_distribution': defaultdict(int)
        }
        
        self.logger.info("Message Router initialized")
    
    async def start(self):
        """Start message router"""
        if self.running:
            self.logger.warning("Message router already running")
            return
        
        self.running = True
        self.router_task = asyncio.create_task(self._routing_loop())
        
        self.logger.info("Message Router started")
    
    async def stop(self):
        """Stop message router"""
        if not self.running:
            self.logger.debug("Message router not running")
            return
        
        self.running = False
        
        if self.router_task:
            self.router_task.cancel()
            try:
                await self.router_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Message Router stopped")
    
    def register_adapter(self, adapter_id: str, adapter: ProtocolAdapter, weight: float = 1.0):
        """Register protocol adapter"""
        with self._lock:
            self.adapters[adapter_id] = adapter
            self.protocol_adapters[adapter.config.protocol_type].append(adapter_id)
            self.adapter_weights[adapter_id] = weight
            
            self.logger.info(
                "Protocol adapter registered",
                adapter_id=adapter_id,
                protocol_type=adapter.config.protocol_type.value,
                weight=weight
            )
    
    def unregister_adapter(self, adapter_id: str):
        """Unregister protocol adapter"""
        with self._lock:
            if adapter_id in self.adapters:
                adapter = self.adapters[adapter_id]
                protocol_type = adapter.config.protocol_type
                
                # Remove from protocol list
                if adapter_id in self.protocol_adapters[protocol_type]:
                    self.protocol_adapters[protocol_type].remove(adapter_id)
                
                # Clean up
                del self.adapters[adapter_id]
                if adapter_id in self.adapter_weights:
                    del self.adapter_weights[adapter_id]
                if adapter_id in self.adapter_connections:
                    del self.adapter_connections[adapter_id]
                
                self.logger.info("Protocol adapter unregistered", adapter_id=adapter_id)
    
    def add_route(self, route_id: str, route: MessageRoute):
        """Add message route"""
        with self._lock:
            self.routes[route_id] = route
            
            # Index by source and target addresses
            if route.source_address not in self.agent_routes:
                self.agent_routes[route.source_address] = []
            self.agent_routes[route.source_address].append(route_id)
            
            self.router_stats['total_routes_created'] += 1
            
            self.logger.info(
                "Message route added",
                route_id=route_id,
                source_protocol=route.source_protocol.value,
                target_protocol=route.target_protocol.value,
                source_address=route.source_address,
                target_address=route.target_address
            )
    
    def remove_route(self, route_id: str):
        """Remove message route"""
        with self._lock:
            if route_id in self.routes:
                route = self.routes[route_id]
                
                # Remove from agent routes
                if route.source_address in self.agent_routes:
                    if route_id in self.agent_routes[route.source_address]:
                        self.agent_routes[route.source_address].remove(route_id)
                
                del self.routes[route_id]
                
                self.logger.info("Message route removed", route_id=route_id)
    
    async def route_message(self, message: CommunicationMessage) -> bool:
        """Route message to appropriate protocol adapter"""
        start_time = time.time()
        
        try:
            with self._lock:
                # Find route for message
                route = self._find_route(message)
                if not route:
                    self.logger.warning(
                        "No route found for message",
                        message_id=message.message_id,
                        sender_id=message.sender_id,
                        recipient_id=message.recipient_id
                    )
                    self.router_stats['total_messages_failed'] += 1
                    return False
                
                # Select adapter based on routing strategy
                adapter_id = self._select_adapter(route.target_protocol)
                if not adapter_id:
                    self.logger.warning(
                        "No adapter available for protocol",
                        protocol_type=route.target_protocol.value,
                        message_id=message.message_id
                    )
                    self.router_stats['total_messages_failed'] += 1
                    return False
                
                adapter = self.adapters[adapter_id]
                
                # Check if adapter is connected
                if not adapter.is_connected():
                    self.logger.warning(
                        "Adapter not connected",
                        adapter_id=adapter_id,
                        message_id=message.message_id
                    )
                    self.router_stats['total_messages_failed'] += 1
                    return False
                
                # Apply transformation rules if needed
                transformed_message = self._transform_message(message, route)
                
                # Route message
                success = await adapter.send_message(transformed_message, route.target_address)
                
                if success:
                    # Update statistics
                    self.router_stats['total_messages_routed'] += 1
                    self.router_stats['protocol_distribution'][route.target_protocol.value] += 1
                    self.adapter_connections[adapter_id] += 1
                    
                    # Update average routing time
                    routing_time = time.time() - start_time
                    current_avg = self.router_stats['average_routing_time']
                    total_routed = self.router_stats['total_messages_routed']
                    new_avg = ((current_avg * (total_routed - 1)) + routing_time) / total_routed
                    self.router_stats['average_routing_time'] = new_avg
                    
                    self.logger.debug(
                        "Message routed successfully",
                        message_id=message.message_id,
                        adapter_id=adapter_id,
                        routing_time=f"{routing_time:.3f}s"
                    )
                    
                    return True
                else:
                    self.router_stats['total_messages_failed'] += 1
                    return False
                    
        except Exception as e:
            self.router_stats['total_messages_failed'] += 1
            self.logger.error(
                "Message routing failed",
                message_id=message.message_id,
                error=str(e)
            )
            return False
    
    def queue_message(self, message: CommunicationMessage):
        """Queue message for routing"""
        with self._lock:
            self.message_queues[message.priority].append(message.message_id)
            self.pending_messages[message.message_id] = message
            
            self.logger.debug(
                "Message queued for routing",
                message_id=message.message_id,
                priority=message.priority.value
            )
    
    def _find_route(self, message: CommunicationMessage) -> Optional[MessageRoute]:
        """Find appropriate route for message"""
        # Look for specific routes first
        for route_id in self.agent_routes.get(message.sender_id, []):
            route = self.routes[route_id]
            if route.target_address == message.recipient_id:
                return route
        
        # Look for wildcard routes
        for route_id in self.agent_routes.get("*", []):
            route = self.routes[route_id]
            if route.target_address == message.recipient_id or route.target_address == "*":
                return route
        
        return None
    
    def _select_adapter(self, protocol_type: ProtocolType) -> Optional[str]:
        """Select adapter based on routing strategy"""
        available_adapters = [
            adapter_id for adapter_id in self.protocol_adapters[protocol_type]
            if self.adapters[adapter_id].is_connected()
        ]
        
        if not available_adapters:
            return None
        
        if self.routing_strategy == RoutingStrategy.DIRECT:
            return available_adapters[0]
        
        elif self.routing_strategy == RoutingStrategy.ROUND_ROBIN:
            counter = self.round_robin_counters[protocol_type]
            selected = available_adapters[counter % len(available_adapters)]
            self.round_robin_counters[protocol_type] = (counter + 1) % len(available_adapters)
            return selected
        
        elif self.routing_strategy == RoutingStrategy.LEAST_CONNECTIONS:
            return min(available_adapters, key=lambda aid: self.adapter_connections[aid])
        
        elif self.routing_strategy == RoutingStrategy.WEIGHTED:
            # Weighted random selection
            total_weight = sum(self.adapter_weights.get(aid, 1.0) for aid in available_adapters)
            if total_weight == 0:
                return available_adapters[0]
            
            import random
            target = random.uniform(0, total_weight)
            current = 0
            
            for adapter_id in available_adapters:
                current += self.adapter_weights.get(adapter_id, 1.0)
                if current >= target:
                    return adapter_id
            
            return available_adapters[-1]
        
        else:
            return available_adapters[0]
    
    def _transform_message(self, message: CommunicationMessage, route: MessageRoute) -> CommunicationMessage:
        """Apply transformation rules to message"""
        if not route.transformation_rules:
            return message
        
        # Create a copy of the message
        transformed = CommunicationMessage(
            message_id=message.message_id,
            message_type=message.message_type,
            sender_id=message.sender_id,
            recipient_id=message.recipient_id,
            content=message.content.copy(),
            priority=message.priority,
            timestamp=message.timestamp,
            ttl=message.ttl,
            correlation_id=message.correlation_id,
            reply_to=message.reply_to,
            metadata=message.metadata.copy()
        )
        
        # Apply transformation rules
        for rule_name, rule_value in route.transformation_rules.items():
            if rule_name == "add_metadata":
                transformed.metadata.update(rule_value)
            elif rule_name == "modify_content":
                transformed.content.update(rule_value)
            elif rule_name == "change_priority":
                transformed.priority = MessagePriority(rule_value)
        
        return transformed
    
    async def _routing_loop(self):
        """Main routing loop"""
        while self.running:
            try:
                await asyncio.sleep(0.1)  # Process messages every 100ms
                
                if not self.running:
                    break
                
                # Process messages by priority (highest first)
                for priority in sorted(MessagePriority, key=lambda p: p.value, reverse=True):
                    queue = self.message_queues[priority]
                    
                    # Process up to 10 messages per priority per iteration
                    for _ in range(min(10, len(queue))):
                        if not queue:
                            break
                        
                        message_id = queue.popleft()
                        if message_id in self.pending_messages:
                            message = self.pending_messages[message_id]
                            del self.pending_messages[message_id]
                            
                            # Route message
                            await self.route_message(message)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Routing loop error", error=str(e))
    
    def set_routing_strategy(self, strategy: RoutingStrategy):
        """Set routing strategy"""
        self.routing_strategy = strategy
        self.logger.info("Routing strategy changed", strategy=strategy.value)
    
    def get_router_stats(self) -> Dict[str, Any]:
        """Get router statistics"""
        with self._lock:
            return {
                'running': self.running,
                'adapters_count': len(self.adapters),
                'routes_count': len(self.routes),
                'pending_messages': len(self.pending_messages),
                'routing_strategy': self.routing_strategy.value,
                'stats': self.router_stats.copy(),
                'adapter_stats': {
                    adapter_id: adapter.get_stats() 
                    for adapter_id, adapter in self.adapters.items()
                },
                'queue_sizes': {
                    priority.name: len(queue) for priority, queue in self.message_queues.items()
                }
            }
    
    def get_adapter_health(self) -> Dict[str, bool]:
        """Get health status of all adapters"""
        return {
            adapter_id: adapter.is_healthy() 
            for adapter_id, adapter in self.adapters.items()
        }
