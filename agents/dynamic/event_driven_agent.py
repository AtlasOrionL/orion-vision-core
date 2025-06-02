#!/usr/bin/env python3
"""
Event-Driven Agent - Dynamic Agent Example
Orion Vision Core - Event-Driven Architecture Agent

Bu agent, event-driven communication sistemini kullanan gelişmiş bir agent örneğidir.
Asenkron mesajlaşma, event sourcing ve pub/sub patterns kullanır.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import time
import json
import random
from typing import Dict, Any, List

# Agent core'u import et
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'jobone', 'vision_core'))

from agent_core import Agent, AgentConfig, AgentStatus
from event_driven_communication import (
    EventDrivenCommunicationManager, Event, EventType, EventPriority,
    EventDrivenAgent
)
from communication_agent import OrionMessage, MessageType, MessagePriority
from multi_protocol_communication import ProtocolType


class SmartEventDrivenAgent(EventDrivenAgent):
    """
    Smart Event-Driven Agent
    
    Event-driven architecture ile gelişmiş özellikler sunan agent.
    Task management, event correlation ve adaptive behavior içerir.
    """
    
    def __init__(self, agent_id: str):
        """
        Smart Event-Driven Agent başlatıcı
        
        Args:
            agent_id: Agent'ın benzersiz ID'si
        """
        super().__init__(agent_id)
        
        # Task management
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: List[Dict[str, Any]] = []
        self.task_counter = 0
        
        # Event correlation
        self.event_correlations: Dict[str, List[str]] = {}
        self.correlation_patterns: Dict[str, int] = {}
        
        # Adaptive behavior
        self.behavior_stats = {
            'event_response_times': [],
            'task_success_rate': 0.0,
            'preferred_protocols': {},
            'communication_patterns': {}
        }
        
        # Agent capabilities
        self.capabilities = [
            "event_processing",
            "task_management", 
            "adaptive_behavior",
            "event_correlation",
            "async_communication"
        ]
        
        # Setup event handlers
        self._setup_event_handlers()
        
        # Setup message handlers
        self._setup_message_handlers()
    
    async def start(self):
        """Agent'ı başlat"""
        await super().start()
        
        # Start background tasks
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._task_monitor_loop())
        asyncio.create_task(self._adaptive_behavior_loop())
        
        print(f"🚀 Smart Event-Driven Agent {self.agent_id} started")
    
    def _setup_event_handlers(self):
        """Event handler'ları kur"""
        # Task events
        self.subscribe_to_event(
            EventType.TASK_CREATED.value,
            self._handle_task_created_event
        )
        
        self.subscribe_to_event(
            EventType.TASK_COMPLETED.value,
            self._handle_task_completed_event
        )
        
        self.subscribe_to_event(
            EventType.TASK_FAILED.value,
            self._handle_task_failed_event
        )
        
        # Agent events
        self.subscribe_to_event(
            EventType.AGENT_STARTED.value,
            self._handle_agent_started_event
        )
        
        self.subscribe_to_event(
            EventType.AGENT_HEARTBEAT.value,
            self._handle_agent_heartbeat_event
        )
        
        # Protocol events
        self.subscribe_to_event(
            EventType.PROTOCOL_CONNECTED.value,
            self._handle_protocol_connected_event
        )
        
        # System events
        self.subscribe_to_event(
            EventType.SYSTEM_ALERT.value,
            self._handle_system_alert_event
        )
    
    def _setup_message_handlers(self):
        """Message handler'ları kur"""
        self.register_message_handler(
            MessageType.TASK_REQUEST.value,
            self._handle_task_request_message
        )
        
        self.register_message_handler(
            MessageType.AGENT_COMMUNICATION.value,
            self._handle_agent_communication_message
        )
        
        self.register_message_handler(
            MessageType.SYSTEM_STATUS.value,
            self._handle_system_status_message
        )
    
    async def create_task(self, task_type: str, task_data: Dict[str, Any]) -> str:
        """
        Yeni task oluştur
        
        Args:
            task_type: Task tipi
            task_data: Task verisi
            
        Returns:
            str: Task ID
        """
        self.task_counter += 1
        task_id = f"{self.agent_id}_task_{self.task_counter}"
        
        task = {
            'task_id': task_id,
            'task_type': task_type,
            'data': task_data,
            'status': 'created',
            'created_at': time.time(),
            'started_at': None,
            'completed_at': None,
            'result': None,
            'error': None
        }
        
        self.active_tasks[task_id] = task
        
        # Task created event'i yayınla
        event = Event(
            event_type=EventType.TASK_CREATED.value,
            source_agent_id=self.agent_id,
            data={
                'task_id': task_id,
                'task_type': task_type,
                'task_data': task_data
            },
            metadata={
                'created_at': task['created_at']
            }
        )
        
        await self.send_event(event)
        
        return task_id
    
    async def complete_task(self, task_id: str, result: Any = None):
        """
        Task'ı tamamla
        
        Args:
            task_id: Task ID
            result: Task sonucu
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task['status'] = 'completed'
            task['completed_at'] = time.time()
            task['result'] = result
            
            # Task completed event'i yayınla
            event = Event(
                event_type=EventType.TASK_COMPLETED.value,
                source_agent_id=self.agent_id,
                data={
                    'task_id': task_id,
                    'task_type': task['task_type'],
                    'result': result,
                    'duration': task['completed_at'] - task['created_at']
                },
                metadata={
                    'completed_at': task['completed_at']
                }
            )
            
            await self.send_event(event)
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
    
    async def fail_task(self, task_id: str, error: str):
        """
        Task'ı başarısız olarak işaretle
        
        Args:
            task_id: Task ID
            error: Hata mesajı
        """
        if task_id in self.active_tasks:
            task = self.active_tasks[task_id]
            task['status'] = 'failed'
            task['completed_at'] = time.time()
            task['error'] = error
            
            # Task failed event'i yayınla
            event = Event(
                event_type=EventType.TASK_FAILED.value,
                source_agent_id=self.agent_id,
                data={
                    'task_id': task_id,
                    'task_type': task['task_type'],
                    'error': error,
                    'duration': task['completed_at'] - task['created_at']
                },
                metadata={
                    'failed_at': task['completed_at']
                }
            )
            
            await self.send_event(event)
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
    
    async def _handle_task_created_event(self, event: Event):
        """Task created event handler"""
        task_id = event.data.get('task_id')
        task_type = event.data.get('task_type')
        
        print(f"📋 Task created: {task_id} ({task_type}) by {event.source_agent_id}")
        
        # Event correlation
        self._correlate_event(event)
    
    async def _handle_task_completed_event(self, event: Event):
        """Task completed event handler"""
        task_id = event.data.get('task_id')
        duration = event.data.get('duration', 0)
        
        print(f"✅ Task completed: {task_id} in {duration:.2f}s by {event.source_agent_id}")
        
        # Update behavior stats
        self._update_task_success_rate()
        
        # Event correlation
        self._correlate_event(event)
    
    async def _handle_task_failed_event(self, event: Event):
        """Task failed event handler"""
        task_id = event.data.get('task_id')
        error = event.data.get('error')
        
        print(f"❌ Task failed: {task_id} - {error} by {event.source_agent_id}")
        
        # Update behavior stats
        self._update_task_success_rate()
        
        # Event correlation
        self._correlate_event(event)
    
    async def _handle_agent_started_event(self, event: Event):
        """Agent started event handler"""
        agent_id = event.source_agent_id
        agent_type = event.data.get('agent_type', 'Unknown')
        
        print(f"🚀 Agent started: {agent_id} ({agent_type})")
        
        # Send welcome message if it's a different agent
        if agent_id != self.agent_id:
            welcome_message = OrionMessage(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=f"Welcome to the system, {agent_id}! I'm {self.agent_id}.",
                sender_id=self.agent_id,
                priority=MessagePriority.NORMAL.value,
                metadata={
                    'welcome': True,
                    'capabilities': self.capabilities
                }
            )
            
            await self.send_message(welcome_message, agent_id)
    
    async def _handle_agent_heartbeat_event(self, event: Event):
        """Agent heartbeat event handler"""
        agent_id = event.source_agent_id
        
        # Track communication patterns
        if agent_id not in self.behavior_stats['communication_patterns']:
            self.behavior_stats['communication_patterns'][agent_id] = 0
        self.behavior_stats['communication_patterns'][agent_id] += 1
    
    async def _handle_protocol_connected_event(self, event: Event):
        """Protocol connected event handler"""
        protocol = event.data.get('protocol')
        agent_id = event.source_agent_id
        
        print(f"🔗 Protocol connected: {protocol} for {agent_id}")
        
        # Update preferred protocols
        if protocol not in self.behavior_stats['preferred_protocols']:
            self.behavior_stats['preferred_protocols'][protocol] = 0
        self.behavior_stats['preferred_protocols'][protocol] += 1
    
    async def _handle_system_alert_event(self, event: Event):
        """System alert event handler"""
        alert_type = event.data.get('alert_type', 'unknown')
        message = event.data.get('message', '')
        
        print(f"🚨 System Alert: {alert_type} - {message}")
        
        # React to critical alerts
        if event.priority == EventPriority.CRITICAL:
            # Create emergency response task
            await self.create_task('emergency_response', {
                'alert_type': alert_type,
                'alert_message': message,
                'alert_source': event.source_agent_id
            })
    
    async def _handle_task_request_message(self, message: OrionMessage):
        """Task request message handler"""
        try:
            task_data = json.loads(message.content) if message.content else {}
            task_type = task_data.get('task_type', 'generic')
            
            # Create task
            task_id = await self.create_task(task_type, task_data)
            
            # Simulate task processing
            await asyncio.sleep(random.uniform(0.1, 2.0))
            
            # Complete task with result
            result = {
                'task_id': task_id,
                'status': 'completed',
                'processed_by': self.agent_id,
                'processing_time': time.time()
            }
            
            await self.complete_task(task_id, result)
            
            # Send response
            response = OrionMessage(
                message_type=MessageType.TASK_RESPONSE.value,
                content=json.dumps(result),
                sender_id=self.agent_id,
                correlation_id=message.correlation_id,
                priority=MessagePriority.HIGH.value,
                metadata=result
            )
            
            await self.send_message(response, message.sender_id)
            
        except Exception as e:
            print(f"Task request handling error: {e}")
    
    async def _handle_agent_communication_message(self, message: OrionMessage):
        """Agent communication message handler"""
        print(f"💬 Received message from {message.sender_id}: {message.content}")
        
        # Echo response with enhancement
        response_content = f"Echo from {self.agent_id}: {message.content}"
        
        # Add agent capabilities to response
        if message.metadata.get('welcome'):
            response_content += f"\nMy capabilities: {', '.join(self.capabilities)}"
        
        response = OrionMessage(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content=response_content,
            sender_id=self.agent_id,
            correlation_id=message.correlation_id,
            priority=MessagePriority.NORMAL.value,
            metadata={
                'response_to': message.sender_id,
                'capabilities': self.capabilities
            }
        )
        
        await self.send_message(response, message.sender_id)
    
    async def _handle_system_status_message(self, message: OrionMessage):
        """System status message handler"""
        status_report = {
            'agent_id': self.agent_id,
            'status': self.state['status'],
            'uptime': time.time() - self.state['start_time'] if self.state['start_time'] else 0,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks),
            'capabilities': self.capabilities,
            'behavior_stats': self.behavior_stats
        }
        
        response = OrionMessage(
            message_type=MessageType.SYSTEM_STATUS.value,
            content=json.dumps(status_report),
            sender_id=self.agent_id,
            correlation_id=message.correlation_id,
            priority=MessagePriority.NORMAL.value,
            metadata=status_report
        )
        
        await self.send_message(response, message.sender_id)
    
    async def _heartbeat_loop(self):
        """Heartbeat döngüsü"""
        while self.running:
            try:
                # Heartbeat event'i yayınla
                event = Event(
                    event_type=EventType.AGENT_HEARTBEAT.value,
                    source_agent_id=self.agent_id,
                    data={
                        'timestamp': time.time(),
                        'status': self.state['status'],
                        'active_tasks': len(self.active_tasks)
                    },
                    priority=EventPriority.LOW
                )
                
                await self.send_event(event)
                
                # 30 saniye bekle
                await asyncio.sleep(30.0)
                
            except Exception as e:
                print(f"Heartbeat error: {e}")
                await asyncio.sleep(5.0)
    
    async def _task_monitor_loop(self):
        """Task monitoring döngüsü"""
        while self.running:
            try:
                current_time = time.time()
                
                # Timeout olan task'ları kontrol et
                for task_id, task in list(self.active_tasks.items()):
                    task_age = current_time - task['created_at']
                    
                    # 5 dakikadan eski task'ları timeout yap
                    if task_age > 300:
                        await self.fail_task(task_id, "Task timeout")
                
                # 60 saniye bekle
                await asyncio.sleep(60.0)
                
            except Exception as e:
                print(f"Task monitor error: {e}")
                await asyncio.sleep(10.0)
    
    async def _adaptive_behavior_loop(self):
        """Adaptive behavior döngüsü"""
        while self.running:
            try:
                # Behavior stats'ı güncelle
                self._analyze_behavior_patterns()
                
                # 5 dakika bekle
                await asyncio.sleep(300.0)
                
            except Exception as e:
                print(f"Adaptive behavior error: {e}")
                await asyncio.sleep(30.0)
    
    def _correlate_event(self, event: Event):
        """Event correlation işle"""
        if event.correlation_id:
            if event.correlation_id not in self.event_correlations:
                self.event_correlations[event.correlation_id] = []
            
            self.event_correlations[event.correlation_id].append(event.event_id)
            
            # Pattern detection
            pattern_key = f"{event.event_type}:{event.source_agent_id}"
            if pattern_key not in self.correlation_patterns:
                self.correlation_patterns[pattern_key] = 0
            self.correlation_patterns[pattern_key] += 1
    
    def _update_task_success_rate(self):
        """Task success rate'i güncelle"""
        if self.completed_tasks:
            successful_tasks = sum(1 for task in self.completed_tasks if task['status'] == 'completed')
            self.behavior_stats['task_success_rate'] = successful_tasks / len(self.completed_tasks)
    
    def _analyze_behavior_patterns(self):
        """Behavior pattern'larını analiz et"""
        # Most used protocol
        if self.behavior_stats['preferred_protocols']:
            most_used_protocol = max(
                self.behavior_stats['preferred_protocols'],
                key=self.behavior_stats['preferred_protocols'].get
            )
            print(f"📊 Most used protocol: {most_used_protocol}")
        
        # Most active communication partner
        if self.behavior_stats['communication_patterns']:
            most_active_partner = max(
                self.behavior_stats['communication_patterns'],
                key=self.behavior_stats['communication_patterns'].get
            )
            print(f"📊 Most active communication partner: {most_active_partner}")
    
    def get_enhanced_stats(self) -> Dict[str, Any]:
        """Gelişmiş istatistikleri getir"""
        base_stats = self.get_stats()
        
        return {
            **base_stats,
            'task_management': {
                'active_tasks': len(self.active_tasks),
                'completed_tasks': len(self.completed_tasks),
                'task_success_rate': self.behavior_stats['task_success_rate']
            },
            'event_correlation': {
                'correlation_count': len(self.event_correlations),
                'pattern_count': len(self.correlation_patterns),
                'top_patterns': dict(sorted(
                    self.correlation_patterns.items(),
                    key=lambda x: x[1],
                    reverse=True
                )[:5])
            },
            'behavior_stats': self.behavior_stats,
            'capabilities': self.capabilities
        }
