#!/usr/bin/env python3
"""
Event-Driven Communication Tests - Atlas Prompt 3.2.2
Orion Vision Core - Event-Driven Architecture Testleri

Bu script, event_driven_communication.py modülünün unit testlerini içerir.
"""

import unittest
import asyncio
import sys
import os
import time
import tempfile
from unittest.mock import Mock, patch, AsyncMock

# Test modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))

from event_driven_communication import (
    Event, EventType, EventPriority, EventSubscription,
    EventBus, EventStore, AsyncMessageHandler,
    EventDrivenCommunicationManager, EventDrivenAgent
)
from communication_agent import OrionMessage, MessageType, MessagePriority


class TestEvent(unittest.TestCase):
    """Event class testleri"""
    
    def test_event_creation(self):
        """Event oluşturma testi"""
        event = Event(
            event_type=EventType.TASK_CREATED.value,
            source_agent_id="test_agent",
            data={"task_id": "test_task"},
            priority=EventPriority.HIGH
        )
        
        self.assertEqual(event.event_type, EventType.TASK_CREATED.value)
        self.assertEqual(event.source_agent_id, "test_agent")
        self.assertEqual(event.data["task_id"], "test_task")
        self.assertEqual(event.priority, EventPriority.HIGH)
        self.assertIsNotNone(event.event_id)
        self.assertIsNotNone(event.timestamp)
    
    def test_event_to_dict(self):
        """Event to dict conversion testi"""
        event = Event(
            event_type=EventType.AGENT_STARTED.value,
            source_agent_id="test_agent",
            data={"start_time": time.time()}
        )
        
        event_dict = event.to_dict()
        
        self.assertIn('event_id', event_dict)
        self.assertIn('event_type', event_dict)
        self.assertIn('source_agent_id', event_dict)
        self.assertIn('data', event_dict)
        self.assertEqual(event_dict['event_type'], EventType.AGENT_STARTED.value)
    
    def test_event_from_dict(self):
        """Event from dict creation testi"""
        event_data = {
            'event_id': 'test_id',
            'event_type': EventType.TASK_COMPLETED.value,
            'source_agent_id': 'test_agent',
            'data': {'result': 'success'},
            'priority': EventPriority.NORMAL.value
        }
        
        event = Event.from_dict(event_data)
        
        self.assertEqual(event.event_id, 'test_id')
        self.assertEqual(event.event_type, EventType.TASK_COMPLETED.value)
        self.assertEqual(event.source_agent_id, 'test_agent')
        self.assertEqual(event.data['result'], 'success')
    
    def test_event_json_serialization(self):
        """Event JSON serialization testi"""
        event = Event(
            event_type=EventType.SYSTEM_ALERT.value,
            source_agent_id="test_agent",
            data={"alert": "test"}
        )
        
        json_str = event.to_json()
        restored_event = Event.from_json(json_str)
        
        self.assertEqual(event.event_type, restored_event.event_type)
        self.assertEqual(event.source_agent_id, restored_event.source_agent_id)
        self.assertEqual(event.data, restored_event.data)


class TestEventSubscription(unittest.TestCase):
    """EventSubscription testleri"""
    
    def test_subscription_creation(self):
        """Subscription oluşturma testi"""
        def test_handler(event):
            pass
        
        subscription = EventSubscription(
            subscriber_id="test_subscriber",
            event_type=EventType.TASK_CREATED.value,
            handler=test_handler,
            priority=EventPriority.HIGH
        )
        
        self.assertEqual(subscription.subscriber_id, "test_subscriber")
        self.assertEqual(subscription.event_type, EventType.TASK_CREATED.value)
        self.assertEqual(subscription.handler, test_handler)
        self.assertEqual(subscription.priority, EventPriority.HIGH)
        self.assertTrue(subscription.active)


class TestEventBus(unittest.IsolatedAsyncioTestCase):
    """EventBus testleri"""
    
    async def asyncSetUp(self):
        """Async test setup"""
        self.event_bus = EventBus(max_history=100)
        await self.event_bus.start()
    
    async def asyncTearDown(self):
        """Async test teardown"""
        await self.event_bus.stop()
    
    def test_event_bus_initialization(self):
        """Event bus başlatma testi"""
        self.assertIsInstance(self.event_bus.subscriptions, dict)
        self.assertIsInstance(self.event_bus.event_history, object)
        self.assertTrue(self.event_bus.running)
    
    def test_subscribe(self):
        """Event subscription testi"""
        def test_handler(event):
            pass
        
        subscription_id = self.event_bus.subscribe(
            "test_subscriber",
            EventType.TASK_CREATED.value,
            test_handler
        )
        
        self.assertIsInstance(subscription_id, str)
        self.assertIn(EventType.TASK_CREATED.value, self.event_bus.subscriptions)
        self.assertEqual(len(self.event_bus.subscriptions[EventType.TASK_CREATED.value]), 1)
    
    def test_unsubscribe(self):
        """Event unsubscription testi"""
        def test_handler(event):
            pass
        
        # Subscribe
        self.event_bus.subscribe(
            "test_subscriber",
            EventType.TASK_CREATED.value,
            test_handler
        )
        
        # Unsubscribe
        self.event_bus.unsubscribe("test_subscriber", EventType.TASK_CREATED.value)
        
        subscriptions = self.event_bus.subscriptions[EventType.TASK_CREATED.value]
        remaining = [s for s in subscriptions if s.subscriber_id == "test_subscriber"]
        self.assertEqual(len(remaining), 0)
    
    async def test_publish_and_deliver(self):
        """Event publish ve delivery testi"""
        received_events = []
        
        def test_handler(event):
            received_events.append(event)
        
        # Subscribe
        self.event_bus.subscribe(
            "test_subscriber",
            EventType.TASK_CREATED.value,
            test_handler
        )
        
        # Publish event
        test_event = Event(
            event_type=EventType.TASK_CREATED.value,
            source_agent_id="test_agent",
            data={"task_id": "test_task"}
        )
        
        await self.event_bus.publish(test_event)
        
        # Wait for processing
        await asyncio.sleep(0.1)
        
        self.assertEqual(len(received_events), 1)
        self.assertEqual(received_events[0].event_type, EventType.TASK_CREATED.value)
    
    def test_get_event_history(self):
        """Event history testi"""
        # Add some events to history
        for i in range(5):
            event = Event(
                event_type=EventType.AGENT_HEARTBEAT.value,
                source_agent_id=f"agent_{i}",
                data={"count": i}
            )
            self.event_bus.event_history.append(event)
        
        history = self.event_bus.get_event_history(limit=3)
        self.assertEqual(len(history), 3)
        
        # Test event type filtering
        history_filtered = self.event_bus.get_event_history(
            event_type=EventType.AGENT_HEARTBEAT.value,
            limit=10
        )
        self.assertEqual(len(history_filtered), 5)
    
    def test_get_stats(self):
        """Event bus istatistikleri testi"""
        stats = self.event_bus.get_stats()
        
        self.assertIn('events_published', stats)
        self.assertIn('events_delivered', stats)
        self.assertIn('active_subscriptions', stats)
        self.assertIn('event_types', stats)
        self.assertIn('history_size', stats)


class TestEventStore(unittest.IsolatedAsyncioTestCase):
    """EventStore testleri"""
    
    async def asyncSetUp(self):
        """Async test setup"""
        self.temp_dir = tempfile.mkdtemp()
        self.event_store = EventStore(self.temp_dir)
    
    async def test_append_and_get_events(self):
        """Event append ve get testi"""
        stream_id = "test_stream"
        
        test_events = [
            Event(
                event_type=EventType.AGENT_STARTED.value,
                source_agent_id="test_agent",
                data={"start_time": time.time()},
                version=1
            ),
            Event(
                event_type=EventType.TASK_CREATED.value,
                source_agent_id="test_agent",
                data={"task_id": "test_task"},
                version=2
            )
        ]
        
        # Append events
        for event in test_events:
            await self.event_store.append_event(stream_id, event)
        
        # Get events
        retrieved_events = await self.event_store.get_events(stream_id)
        
        self.assertEqual(len(retrieved_events), 2)
        self.assertEqual(retrieved_events[0].version, 1)
        self.assertEqual(retrieved_events[1].version, 2)
    
    async def test_get_events_from_version(self):
        """Belirli versiyondan event getirme testi"""
        stream_id = "test_stream"
        
        # Add multiple events
        for i in range(5):
            event = Event(
                event_type=EventType.AGENT_HEARTBEAT.value,
                source_agent_id="test_agent",
                data={"count": i},
                version=i + 1
            )
            await self.event_store.append_event(stream_id, event)
        
        # Get events from version 3
        events_from_v3 = await self.event_store.get_events(stream_id, from_version=3)
        
        self.assertEqual(len(events_from_v3), 3)  # versions 3, 4, 5
        self.assertTrue(all(e.version >= 3 for e in events_from_v3))
    
    async def test_snapshot_operations(self):
        """Snapshot operations testi"""
        stream_id = "test_stream"
        
        test_state = {
            "agent_id": "test_agent",
            "status": "running",
            "task_count": 5
        }
        
        # Create snapshot
        await self.event_store.create_snapshot(stream_id, test_state, 5)
        
        # Get snapshot
        snapshot = await self.event_store.get_snapshot(stream_id)
        
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot['state'], test_state)
        self.assertEqual(snapshot['version'], 5)
        self.assertIn('timestamp', snapshot)


class TestAsyncMessageHandler(unittest.IsolatedAsyncioTestCase):
    """AsyncMessageHandler testleri"""
    
    def setUp(self):
        """Test setup"""
        self.handler = AsyncMessageHandler("test_handler")
    
    def test_handler_initialization(self):
        """Handler başlatma testi"""
        self.assertEqual(self.handler.handler_id, "test_handler")
        self.assertIsInstance(self.handler.handlers, dict)
        self.assertIsInstance(self.handler.middleware, list)
    
    def test_register_handler(self):
        """Handler kaydetme testi"""
        def test_message_handler(message):
            pass
        
        self.handler.register_handler(MessageType.TASK_REQUEST.value, test_message_handler)
        
        self.assertIn(MessageType.TASK_REQUEST.value, self.handler.handlers)
        self.assertEqual(self.handler.handlers[MessageType.TASK_REQUEST.value], test_message_handler)
    
    def test_add_middleware(self):
        """Middleware ekleme testi"""
        def test_middleware(message):
            return message
        
        self.handler.add_middleware(test_middleware)
        
        self.assertEqual(len(self.handler.middleware), 1)
        self.assertEqual(self.handler.middleware[0], test_middleware)
    
    async def test_handle_message_sync(self):
        """Sync message handling testi"""
        handled_messages = []
        
        def test_handler(message):
            handled_messages.append(message)
        
        self.handler.register_handler(MessageType.AGENT_COMMUNICATION.value, test_handler)
        
        test_message = OrionMessage(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Test message",
            sender_id="test_sender"
        )
        
        success = await self.handler.handle_message(test_message)
        
        self.assertTrue(success)
        self.assertEqual(len(handled_messages), 1)
        self.assertEqual(handled_messages[0].content, "Test message")
    
    async def test_handle_message_async(self):
        """Async message handling testi"""
        handled_messages = []
        
        async def test_async_handler(message):
            handled_messages.append(message)
        
        self.handler.register_handler(MessageType.TASK_REQUEST.value, test_async_handler)
        
        test_message = OrionMessage(
            message_type=MessageType.TASK_REQUEST.value,
            content="Async test message",
            sender_id="test_sender"
        )
        
        success = await self.handler.handle_message(test_message)
        
        self.assertTrue(success)
        self.assertEqual(len(handled_messages), 1)
    
    async def test_middleware_processing(self):
        """Middleware processing testi"""
        processed_messages = []
        
        def logging_middleware(message):
            processed_messages.append(f"middleware: {message.content}")
            return message
        
        def test_handler(message):
            processed_messages.append(f"handler: {message.content}")
        
        self.handler.add_middleware(logging_middleware)
        self.handler.register_handler(MessageType.AGENT_COMMUNICATION.value, test_handler)
        
        test_message = OrionMessage(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Test",
            sender_id="test_sender"
        )
        
        await self.handler.handle_message(test_message)
        
        self.assertEqual(len(processed_messages), 2)
        self.assertEqual(processed_messages[0], "middleware: Test")
        self.assertEqual(processed_messages[1], "handler: Test")
    
    def test_get_stats(self):
        """Handler istatistikleri testi"""
        stats = self.handler.get_stats()
        
        self.assertIn('handler_id', stats)
        self.assertIn('messages_processed', stats)
        self.assertIn('registered_handlers', stats)
        self.assertIn('middleware_count', stats)
        self.assertIn('avg_processing_time', stats)
        
        self.assertEqual(stats['handler_id'], "test_handler")


class TestEventDrivenCommunicationManager(unittest.IsolatedAsyncioTestCase):
    """EventDrivenCommunicationManager testleri"""
    
    async def asyncSetUp(self):
        """Async test setup"""
        self.manager = EventDrivenCommunicationManager("test_agent")
    
    async def asyncTearDown(self):
        """Async test teardown"""
        if self.manager.running:
            await self.manager.stop()
    
    def test_manager_initialization(self):
        """Manager başlatma testi"""
        self.assertEqual(self.manager.agent_id, "test_agent")
        self.assertIsNotNone(self.manager.event_bus)
        self.assertIsNotNone(self.manager.event_store)
        self.assertIsNotNone(self.manager.message_handler)
        self.assertIsNotNone(self.manager.multi_protocol_manager)
    
    async def test_start_stop(self):
        """Manager start/stop testi"""
        # Start
        await self.manager.start()
        self.assertTrue(self.manager.running)
        self.assertTrue(self.manager.event_bus.running)
        
        # Stop
        await self.manager.stop()
        self.assertFalse(self.manager.running)
    
    def test_subscribe_to_event(self):
        """Event subscription testi"""
        def test_handler(event):
            pass
        
        subscription_id = self.manager.subscribe_to_event(
            EventType.TASK_CREATED.value,
            test_handler
        )
        
        self.assertIsInstance(subscription_id, str)
    
    async def test_publish_event(self):
        """Event publishing testi"""
        await self.manager.start()
        
        test_event = Event(
            event_type=EventType.AGENT_STARTED.value,
            source_agent_id="test_agent",
            data={"start_time": time.time()}
        )
        
        await self.manager.publish_event(test_event)
        
        self.assertEqual(self.manager.stats['events_processed'], 1)
    
    def test_register_message_handler(self):
        """Message handler kaydetme testi"""
        def test_handler(message):
            pass
        
        self.manager.register_message_handler(MessageType.TASK_REQUEST.value, test_handler)
        
        # Check if handler is registered
        handlers = self.manager.message_handler.handlers
        self.assertIn(MessageType.TASK_REQUEST.value, handlers)
    
    def test_map_event_to_message(self):
        """Event-message mapping testi"""
        self.manager.map_event_to_message(
            EventType.TASK_CREATED.value,
            MessageType.TASK_REQUEST.value
        )
        
        self.assertIn(EventType.TASK_CREATED.value, self.manager.event_to_message_mapping)
        self.assertIn(MessageType.TASK_REQUEST.value, self.manager.message_to_event_mapping)
    
    def test_get_comprehensive_stats(self):
        """Kapsamlı istatistik testi"""
        stats = self.manager.get_comprehensive_stats()
        
        self.assertIn('agent_id', stats)
        self.assertIn('manager_stats', stats)
        self.assertIn('event_bus_stats', stats)
        self.assertIn('message_handler_stats', stats)
        self.assertIn('multi_protocol_stats', stats)
        self.assertIn('event_mappings', stats)


def run_event_driven_tests():
    """Event-driven communication testlerini çalıştır"""
    print("🚀 Event-Driven Communication Tests - Atlas Prompt 3.2.2")
    print("=" * 70)
    
    # Test suite oluştur
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    suite.addTests(loader.loadTestsFromTestCase(TestEvent))
    suite.addTests(loader.loadTestsFromTestCase(TestEventSubscription))
    suite.addTests(loader.loadTestsFromTestCase(TestEventBus))
    suite.addTests(loader.loadTestsFromTestCase(TestEventStore))
    suite.addTests(loader.loadTestsFromTestCase(TestAsyncMessageHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestEventDrivenCommunicationManager))
    
    # Test runner oluştur
    runner = unittest.TextTestRunner(verbosity=2)
    
    # Testleri çalıştır
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("🎉 Tüm Event-Driven Communication testleri başarılı!")
        return True
    else:
        print("❌ Bazı testler başarısız oldu!")
        print(f"Başarısız testler: {len(result.failures)}")
        print(f"Hatalar: {len(result.errors)}")
        return False


if __name__ == "__main__":
    success = run_event_driven_tests()
    sys.exit(0 if success else 1)
