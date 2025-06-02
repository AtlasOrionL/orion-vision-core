#!/usr/bin/env python3
"""
Event-Driven Communication System - Atlas Prompt 3.2.2
Orion Vision Core - Asenkron Mesajlaşma ve Event-Driven Architecture

Bu modül, agent'lar arası event-driven communication için gelişmiş
asenkron mesajlaşma sistemi sağlar. Event bus, pub/sub patterns,
event sourcing ve CQRS desteği içerir.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import json
import time
import uuid
import threading
from typing import Dict, List, Optional, Any, Callable, Union, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
import weakref

# Mevcut communication modüllerini import et
import sys
import os
sys.path.append(os.path.dirname(__file__))

from communication_agent import OrionMessage, MessageType, MessagePriority
from multi_protocol_communication import MultiProtocolCommunicationManager, ProtocolType


class EventType(Enum):
    """Event tipleri"""
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    AGENT_HEARTBEAT = "agent_heartbeat"
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    PROTOCOL_CONNECTED = "protocol_connected"
    PROTOCOL_DISCONNECTED = "protocol_disconnected"
    SYSTEM_ALERT = "system_alert"
    CUSTOM_EVENT = "custom_event"


class EventPriority(Enum):
    """Event öncelik seviyeleri"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


@dataclass
class Event:
    """
    Event veri yapısı

    Event-driven architecture'ın temel veri yapısı.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    source_agent_id: str = ""
    target_agent_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    priority: EventPriority = EventPriority.NORMAL
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    version: int = 1

    def to_dict(self) -> Dict[str, Any]:
        """Event'i dictionary'ye çevir"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'source_agent_id': self.source_agent_id,
            'target_agent_id': self.target_agent_id,
            'timestamp': self.timestamp,
            'priority': self.priority.value,
            'data': self.data,
            'metadata': self.metadata,
            'correlation_id': self.correlation_id,
            'causation_id': self.causation_id,
            'version': self.version
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Event':
        """Dictionary'den Event oluştur"""
        return cls(
            event_id=data.get('event_id', str(uuid.uuid4())),
            event_type=data.get('event_type', ''),
            source_agent_id=data.get('source_agent_id', ''),
            target_agent_id=data.get('target_agent_id'),
            timestamp=data.get('timestamp', time.time()),
            priority=EventPriority(data.get('priority', EventPriority.NORMAL.value)),
            data=data.get('data', {}),
            metadata=data.get('metadata', {}),
            correlation_id=data.get('correlation_id'),
            causation_id=data.get('causation_id'),
            version=data.get('version', 1)
        )

    def to_json(self) -> str:
        """Event'i JSON string'e çevir"""
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, json_str: str) -> 'Event':
        """JSON string'den Event oluştur"""
        return cls.from_dict(json.loads(json_str))


@dataclass
class EventSubscription:
    """Event subscription bilgisi"""
    subscriber_id: str
    event_type: str
    handler: Callable[[Event], None]
    filter_func: Optional[Callable[[Event], bool]] = None
    priority: EventPriority = EventPriority.NORMAL
    created_at: float = field(default_factory=time.time)
    active: bool = True


class EventBus:
    """
    Event Bus - Merkezi Event Yönetimi

    Pub/Sub pattern implementasyonu ile event'lerin
    merkezi yönetimini sağlar.
    """

    def __init__(self, max_history: int = 1000):
        """
        Event Bus başlatıcı

        Args:
            max_history: Tutulacak maksimum event geçmişi
        """
        self.subscriptions: Dict[str, List[EventSubscription]] = defaultdict(list)
        self.event_history: deque = deque(maxlen=max_history)
        self.stats = {
            'events_published': 0,
            'events_delivered': 0,
            'subscription_count': 0,
            'failed_deliveries': 0,
            'last_activity': None
        }

        # Async event processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_task: Optional[asyncio.Task] = None
        self.running = False

        # Thread safety
        self._lock = threading.RLock()

        # Weak references for automatic cleanup
        self._weak_handlers: Set[weakref.ref] = set()

    async def start(self):
        """Event bus'ı başlat"""
        if not self.running:
            self.running = True
            self.processing_task = asyncio.create_task(self._process_events())

    async def stop(self):
        """Event bus'ı durdur"""
        if self.running:
            self.running = False
            if self.processing_task:
                self.processing_task.cancel()
                try:
                    await self.processing_task
                except asyncio.CancelledError:
                    pass

    def subscribe(self,
                  subscriber_id: str,
                  event_type: str,
                  handler: Callable[[Event], None],
                  filter_func: Optional[Callable[[Event], bool]] = None,
                  priority: EventPriority = EventPriority.NORMAL) -> str:
        """
        Event'e subscribe ol

        Args:
            subscriber_id: Subscriber'ın ID'si
            event_type: Subscribe olunacak event tipi
            handler: Event handler fonksiyonu
            filter_func: Event filtreleme fonksiyonu
            priority: Subscription önceliği

        Returns:
            str: Subscription ID
        """
        with self._lock:
            subscription = EventSubscription(
                subscriber_id=subscriber_id,
                event_type=event_type,
                handler=handler,
                filter_func=filter_func,
                priority=priority
            )

            self.subscriptions[event_type].append(subscription)
            self.stats['subscription_count'] += 1

            # Weak reference for cleanup
            weak_handler = weakref.ref(handler)
            self._weak_handlers.add(weak_handler)

            return f"{subscriber_id}:{event_type}:{int(time.time())}"

    def unsubscribe(self, subscriber_id: str, event_type: str = None):
        """
        Event subscription'ı iptal et

        Args:
            subscriber_id: Subscriber'ın ID'si
            event_type: İptal edilecek event tipi (None ise tümü)
        """
        with self._lock:
            if event_type:
                # Specific event type
                if event_type in self.subscriptions:
                    self.subscriptions[event_type] = [
                        sub for sub in self.subscriptions[event_type]
                        if sub.subscriber_id != subscriber_id
                    ]
            else:
                # All event types
                for event_type_key in self.subscriptions:
                    self.subscriptions[event_type_key] = [
                        sub for sub in self.subscriptions[event_type_key]
                        if sub.subscriber_id != subscriber_id
                    ]

    async def publish(self, event: Event):
        """
        Event yayınla

        Args:
            event: Yayınlanacak event
        """
        # Event history'ye ekle
        self.event_history.append(event)
        self.stats['events_published'] += 1
        self.stats['last_activity'] = time.time()

        # Event queue'ya ekle
        await self.event_queue.put(event)

    async def _process_events(self):
        """Event processing döngüsü"""
        while self.running:
            try:
                # Event'i queue'dan al
                event = await asyncio.wait_for(self.event_queue.get(), timeout=1.0)

                # Subscribers'a deliver et
                await self._deliver_event(event)

            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Event processing error: {e}")

    async def _deliver_event(self, event: Event):
        """Event'i subscribers'a deliver et"""
        with self._lock:
            subscribers = self.subscriptions.get(event.event_type, [])

            # Priority'ye göre sırala
            subscribers.sort(key=lambda s: s.priority.value)

            for subscription in subscribers:
                if not subscription.active:
                    continue

                try:
                    # Filter kontrolü
                    if subscription.filter_func and not subscription.filter_func(event):
                        continue

                    # Handler'ı çağır
                    if asyncio.iscoroutinefunction(subscription.handler):
                        await subscription.handler(event)
                    else:
                        subscription.handler(event)

                    self.stats['events_delivered'] += 1

                except Exception as e:
                    self.stats['failed_deliveries'] += 1
                    print(f"Event delivery error to {subscription.subscriber_id}: {e}")

    def get_event_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """
        Event geçmişini getir

        Args:
            event_type: Filtrelenecek event tipi
            limit: Maksimum event sayısı

        Returns:
            List[Event]: Event listesi
        """
        events = list(self.event_history)

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        return events[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        """Event bus istatistiklerini getir"""
        with self._lock:
            return {
                **self.stats,
                'active_subscriptions': sum(
                    len(subs) for subs in self.subscriptions.values()
                ),
                'event_types': list(self.subscriptions.keys()),
                'history_size': len(self.event_history)
            }


class EventStore:
    """
    Event Store - Event Sourcing Implementation

    Event'lerin kalıcı olarak saklanması ve
    event sourcing pattern'inin implementasyonu.
    """

    def __init__(self, storage_path: str = "data/events"):
        """
        Event Store başlatıcı

        Args:
            storage_path: Event'lerin saklanacağı dizin
        """
        self.storage_path = storage_path
        self.events: Dict[str, List[Event]] = defaultdict(list)
        self.snapshots: Dict[str, Dict[str, Any]] = {}

        # Ensure storage directory exists
        os.makedirs(storage_path, exist_ok=True)

        # Load existing events
        self._load_events()

    async def append_event(self, stream_id: str, event: Event):
        """
        Event'i stream'e ekle

        Args:
            stream_id: Stream ID'si
            event: Eklenecek event
        """
        self.events[stream_id].append(event)
        await self._persist_event(stream_id, event)

    async def get_events(self, stream_id: str, from_version: int = 0) -> List[Event]:
        """
        Stream'den event'leri getir

        Args:
            stream_id: Stream ID'si
            from_version: Başlangıç versiyonu

        Returns:
            List[Event]: Event listesi
        """
        events = self.events.get(stream_id, [])
        return [e for e in events if e.version >= from_version]

    async def create_snapshot(self, stream_id: str, state: Dict[str, Any], version: int):
        """
        Snapshot oluştur

        Args:
            stream_id: Stream ID'si
            state: State bilgisi
            version: Snapshot versiyonu
        """
        self.snapshots[stream_id] = {
            'state': state,
            'version': version,
            'timestamp': time.time()
        }
        await self._persist_snapshot(stream_id)

    async def get_snapshot(self, stream_id: str) -> Optional[Dict[str, Any]]:
        """
        Snapshot getir

        Args:
            stream_id: Stream ID'si

        Returns:
            Optional[Dict]: Snapshot bilgisi
        """
        return self.snapshots.get(stream_id)

    def _load_events(self):
        """Mevcut event'leri yükle"""
        try:
            # Implementation for loading persisted events
            pass
        except Exception as e:
            print(f"Event loading error: {e}")

    async def _persist_event(self, stream_id: str, event: Event):
        """Event'i kalıcı olarak sakla"""
        try:
            # Implementation for persisting events
            pass
        except Exception as e:
            print(f"Event persistence error: {e}")

    async def _persist_snapshot(self, stream_id: str):
        """Snapshot'ı kalıcı olarak sakla"""
        try:
            # Implementation for persisting snapshots
            pass
        except Exception as e:
            print(f"Snapshot persistence error: {e}")


class AsyncMessageHandler:
    """
    Async Message Handler

    Asenkron mesaj işleme için gelişmiş handler sistemi.
    """

    def __init__(self, handler_id: str):
        """
        Async Message Handler başlatıcı

        Args:
            handler_id: Handler'ın benzersiz ID'si
        """
        self.handler_id = handler_id
        self.handlers: Dict[str, Callable] = {}
        self.middleware: List[Callable] = []
        self.stats = {
            'messages_processed': 0,
            'processing_time_total': 0.0,
            'errors': 0,
            'last_activity': None
        }

    def register_handler(self, message_type: str, handler: Callable):
        """
        Message handler kaydet

        Args:
            message_type: Mesaj tipi
            handler: Handler fonksiyonu
        """
        self.handlers[message_type] = handler

    def add_middleware(self, middleware: Callable):
        """
        Middleware ekle

        Args:
            middleware: Middleware fonksiyonu
        """
        self.middleware.append(middleware)

    async def handle_message(self, message: OrionMessage) -> bool:
        """
        Mesajı asenkron olarak işle

        Args:
            message: İşlenecek mesaj

        Returns:
            bool: İşlem başarılı ise True
        """
        start_time = time.time()

        try:
            # Middleware'leri çalıştır
            for middleware in self.middleware:
                if asyncio.iscoroutinefunction(middleware):
                    message = await middleware(message)
                else:
                    message = middleware(message)

                if message is None:
                    return False

            # Handler'ı bul ve çalıştır
            handler = self.handlers.get(message.message_type)
            if handler:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)

                # İstatistikleri güncelle
                processing_time = time.time() - start_time
                self.stats['messages_processed'] += 1
                self.stats['processing_time_total'] += processing_time
                self.stats['last_activity'] = time.time()

                return True
            else:
                print(f"No handler found for message type: {message.message_type}")
                return False

        except Exception as e:
            self.stats['errors'] += 1
            print(f"Message handling error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Handler istatistiklerini getir"""
        avg_processing_time = 0.0
        if self.stats['messages_processed'] > 0:
            avg_processing_time = self.stats['processing_time_total'] / self.stats['messages_processed']

        return {
            **self.stats,
            'handler_id': self.handler_id,
            'registered_handlers': list(self.handlers.keys()),
            'middleware_count': len(self.middleware),
            'avg_processing_time': avg_processing_time
        }


class EventDrivenCommunicationManager:
    """
    Event-Driven Communication Manager

    Multi-protocol communication ile event-driven architecture'ı
    birleştiren ana yönetici sınıf.
    """

    def __init__(self, agent_id: str):
        """
        Event-Driven Communication Manager başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
        """
        self.agent_id = agent_id

        # Core components
        self.event_bus = EventBus()
        self.event_store = EventStore(f"data/events/{agent_id}")
        self.message_handler = AsyncMessageHandler(f"{agent_id}_handler")
        self.multi_protocol_manager = MultiProtocolCommunicationManager(agent_id)

        # Event-to-message mapping
        self.event_to_message_mapping: Dict[str, str] = {}
        self.message_to_event_mapping: Dict[str, str] = {}

        # Async processing
        self.running = False
        self.processing_tasks: List[asyncio.Task] = []

        # Statistics
        self.stats = {
            'events_processed': 0,
            'messages_converted': 0,
            'protocol_events': 0,
            'last_activity': None
        }

        # Setup default event handlers
        self._setup_default_handlers()

    async def start(self):
        """Event-driven communication manager'ı başlat"""
        if not self.running:
            self.running = True

            # Event bus'ı başlat
            await self.event_bus.start()

            # Multi-protocol manager'ı başlat
            await self.multi_protocol_manager.connect_all()
            await self.multi_protocol_manager.start_all_listening()

            # Event processing task'ları başlat
            self.processing_tasks = [
                asyncio.create_task(self._event_to_message_processor()),
                asyncio.create_task(self._message_to_event_processor())
            ]

    async def stop(self):
        """Event-driven communication manager'ı durdur"""
        if self.running:
            self.running = False

            # Processing task'ları durdur
            for task in self.processing_tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            # Event bus'ı durdur
            await self.event_bus.stop()

            # Multi-protocol manager'ı durdur
            await self.multi_protocol_manager.disconnect_all()

    def subscribe_to_event(self,
                          event_type: str,
                          handler: Callable[[Event], None],
                          filter_func: Optional[Callable[[Event], bool]] = None,
                          priority: EventPriority = EventPriority.NORMAL) -> str:
        """
        Event'e subscribe ol

        Args:
            event_type: Subscribe olunacak event tipi
            handler: Event handler fonksiyonu
            filter_func: Event filtreleme fonksiyonu
            priority: Subscription önceliği

        Returns:
            str: Subscription ID
        """
        return self.event_bus.subscribe(
            self.agent_id, event_type, handler, filter_func, priority
        )

    async def publish_event(self, event: Event):
        """
        Event yayınla

        Args:
            event: Yayınlanacak event
        """
        # Event store'a kaydet
        await self.event_store.append_event(self.agent_id, event)

        # Event bus'a yayınla
        await self.event_bus.publish(event)

        self.stats['events_processed'] += 1
        self.stats['last_activity'] = time.time()

    async def send_message_as_event(self, message: OrionMessage, target: str, protocol: ProtocolType = None):
        """
        Mesajı event olarak gönder

        Args:
            message: Gönderilecek mesaj
            target: Hedef agent
            protocol: Kullanılacak protokol
        """
        # Mesajı gönder
        success = await self.multi_protocol_manager.send_message(message, target, protocol)

        if success:
            # Message sent event'i oluştur
            event = Event(
                event_type=EventType.MESSAGE_SENT.value,
                source_agent_id=self.agent_id,
                target_agent_id=target,
                data={
                    'message_type': message.message_type,
                    'message_id': message.message_id,
                    'protocol': protocol.value if protocol else 'auto',
                    'content_preview': message.content[:100] if message.content else ''
                },
                metadata={
                    'success': True,
                    'timestamp': time.time()
                }
            )

            await self.publish_event(event)

    def register_message_handler(self, message_type: str, handler: Callable):
        """
        Message handler kaydet

        Args:
            message_type: Mesaj tipi
            handler: Handler fonksiyonu
        """
        self.message_handler.register_handler(message_type, handler)

        # Multi-protocol manager'a da kaydet
        self.multi_protocol_manager.add_global_message_handler(message_type, self._message_received_wrapper)

    def map_event_to_message(self, event_type: str, message_type: str):
        """
        Event tipini mesaj tipine map et

        Args:
            event_type: Event tipi
            message_type: Mesaj tipi
        """
        self.event_to_message_mapping[event_type] = message_type
        self.message_to_event_mapping[message_type] = event_type

    async def _event_to_message_processor(self):
        """Event'leri mesaja çeviren processor"""
        while self.running:
            try:
                # Event bus'dan event'leri dinle ve mesaja çevir
                await asyncio.sleep(0.1)  # Placeholder for actual implementation

            except Exception as e:
                print(f"Event to message processing error: {e}")
                await asyncio.sleep(1.0)

    async def _message_to_event_processor(self):
        """Mesajları event'e çeviren processor"""
        while self.running:
            try:
                # Mesajları dinle ve event'e çevir
                await asyncio.sleep(0.1)  # Placeholder for actual implementation

            except Exception as e:
                print(f"Message to event processing error: {e}")
                await asyncio.sleep(1.0)

    async def _message_received_wrapper(self, message: OrionMessage):
        """Mesaj alındığında çağrılan wrapper"""
        try:
            # Message received event'i oluştur
            event = Event(
                event_type=EventType.MESSAGE_RECEIVED.value,
                source_agent_id=message.sender_id,
                target_agent_id=self.agent_id,
                data={
                    'message_type': message.message_type,
                    'message_id': message.message_id,
                    'content_preview': message.content[:100] if message.content else ''
                },
                metadata={
                    'timestamp': time.time(),
                    'correlation_id': message.correlation_id
                }
            )

            await self.publish_event(event)

            # Original handler'ı çağır
            await self.message_handler.handle_message(message)

        except Exception as e:
            print(f"Message received wrapper error: {e}")

    def _setup_default_handlers(self):
        """Default event handler'ları kur"""
        # Agent lifecycle events
        self.subscribe_to_event(
            EventType.AGENT_STARTED.value,
            self._handle_agent_started
        )

        self.subscribe_to_event(
            EventType.AGENT_STOPPED.value,
            self._handle_agent_stopped
        )

        # Protocol events
        self.subscribe_to_event(
            EventType.PROTOCOL_CONNECTED.value,
            self._handle_protocol_connected
        )

        self.subscribe_to_event(
            EventType.PROTOCOL_DISCONNECTED.value,
            self._handle_protocol_disconnected
        )

        # Task events
        self.subscribe_to_event(
            EventType.TASK_COMPLETED.value,
            self._handle_task_completed
        )

        self.subscribe_to_event(
            EventType.TASK_FAILED.value,
            self._handle_task_failed
        )

    def _handle_agent_started(self, event: Event):
        """Agent started event handler"""
        print(f"Agent started: {event.source_agent_id}")
        self.stats['protocol_events'] += 1

    def _handle_agent_stopped(self, event: Event):
        """Agent stopped event handler"""
        print(f"Agent stopped: {event.source_agent_id}")
        self.stats['protocol_events'] += 1

    def _handle_protocol_connected(self, event: Event):
        """Protocol connected event handler"""
        protocol = event.data.get('protocol', 'unknown')
        print(f"Protocol connected: {protocol} for agent {event.source_agent_id}")
        self.stats['protocol_events'] += 1

    def _handle_protocol_disconnected(self, event: Event):
        """Protocol disconnected event handler"""
        protocol = event.data.get('protocol', 'unknown')
        print(f"Protocol disconnected: {protocol} for agent {event.source_agent_id}")
        self.stats['protocol_events'] += 1

    def _handle_task_completed(self, event: Event):
        """Task completed event handler"""
        task_id = event.data.get('task_id', 'unknown')
        print(f"Task completed: {task_id} by agent {event.source_agent_id}")

    def _handle_task_failed(self, event: Event):
        """Task failed event handler"""
        task_id = event.data.get('task_id', 'unknown')
        error = event.data.get('error', 'unknown')
        print(f"Task failed: {task_id} by agent {event.source_agent_id}, error: {error}")

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Kapsamlı istatistikleri getir"""
        return {
            'agent_id': self.agent_id,
            'manager_stats': self.stats,
            'event_bus_stats': self.event_bus.get_stats(),
            'message_handler_stats': self.message_handler.get_stats(),
            'multi_protocol_stats': self.multi_protocol_manager.get_comprehensive_stats(),
            'event_mappings': {
                'event_to_message': self.event_to_message_mapping,
                'message_to_event': self.message_to_event_mapping
            }
        }


class EventDrivenAgent:
    """
    Event-Driven Agent Base Class

    Event-driven architecture kullanan agent'lar için temel sınıf.
    """

    def __init__(self, agent_id: str):
        """
        Event-Driven Agent başlatıcı

        Args:
            agent_id: Agent'ın benzersiz ID'si
        """
        self.agent_id = agent_id
        self.communication_manager = EventDrivenCommunicationManager(agent_id)
        self.running = False

        # Agent state
        self.state = {
            'status': 'initialized',
            'start_time': None,
            'last_activity': None
        }

    async def start(self):
        """Agent'ı başlat"""
        if not self.running:
            self.running = True
            self.state['status'] = 'starting'
            self.state['start_time'] = time.time()

            # Communication manager'ı başlat
            await self.communication_manager.start()

            # Agent started event'i yayınla
            event = Event(
                event_type=EventType.AGENT_STARTED.value,
                source_agent_id=self.agent_id,
                data={
                    'agent_type': self.__class__.__name__,
                    'start_time': self.state['start_time']
                }
            )

            await self.communication_manager.publish_event(event)

            self.state['status'] = 'running'

    async def stop(self):
        """Agent'ı durdur"""
        if self.running:
            self.running = False
            self.state['status'] = 'stopping'

            # Agent stopped event'i yayınla
            event = Event(
                event_type=EventType.AGENT_STOPPED.value,
                source_agent_id=self.agent_id,
                data={
                    'agent_type': self.__class__.__name__,
                    'stop_time': time.time(),
                    'uptime': time.time() - self.state['start_time'] if self.state['start_time'] else 0
                }
            )

            await self.communication_manager.publish_event(event)

            # Communication manager'ı durdur
            await self.communication_manager.stop()

            self.state['status'] = 'stopped'

    async def send_event(self, event: Event):
        """Event gönder"""
        await self.communication_manager.publish_event(event)

    async def send_message(self, message: OrionMessage, target: str, protocol: ProtocolType = None):
        """Mesaj gönder"""
        await self.communication_manager.send_message_as_event(message, target, protocol)

    def subscribe_to_event(self, event_type: str, handler: Callable[[Event], None]):
        """Event'e subscribe ol"""
        return self.communication_manager.subscribe_to_event(event_type, handler)

    def register_message_handler(self, message_type: str, handler: Callable):
        """Message handler kaydet"""
        self.communication_manager.register_message_handler(message_type, handler)

    def get_state(self) -> Dict[str, Any]:
        """Agent state'ini getir"""
        return {
            **self.state,
            'agent_id': self.agent_id,
            'running': self.running
        }

    def get_stats(self) -> Dict[str, Any]:
        """Agent istatistiklerini getir"""
        return {
            'agent_state': self.get_state(),
            'communication_stats': self.communication_manager.get_comprehensive_stats()
        }
