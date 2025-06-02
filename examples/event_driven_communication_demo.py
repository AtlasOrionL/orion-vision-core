#!/usr/bin/env python3
"""
Event-Driven Communication Demo - Atlas Prompt 3.2.2
Orion Vision Core - Asenkron Mesajlaşma ve Event-Driven Architecture Demonstrasyonu

Bu script, event-driven communication sisteminin yeteneklerini gösterir ve
asenkron mesajlaşma, event sourcing, pub/sub patterns'ı test eder.
"""

import sys
import os
import time
import asyncio
import signal
import json
from pathlib import Path

# Event-driven modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from event_driven_communication import (
    EventBus, EventStore, Event, EventType, EventPriority,
    EventDrivenCommunicationManager, AsyncMessageHandler
)
from communication_agent import OrionMessage, MessageType, MessagePriority
from dynamic_agent_loader import DynamicAgentLoader, get_global_loader


class EventDrivenCommunicationDemo:
    """
    Event-Driven Communication Demo
    
    Bu sınıf, event-driven communication sisteminin özelliklerini
    göstermek için tasarlanmıştır.
    """
    
    def __init__(self):
        """Demo başlatıcı"""
        self.running = True
        self.event_bus = EventBus()
        self.event_store = EventStore("data/demo_events")
        self.communication_managers = {}
        self.test_agents = []
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🚀 Event-Driven Communication Demo - Atlas Prompt 3.2.2")
        print("=" * 70)
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        print(f"\n🛑 Signal {signum} received, shutting down...")
        self.running = False
        asyncio.create_task(self._cleanup_all())
        sys.exit(0)
    
    async def run_demo(self):
        """Ana demo fonksiyonu"""
        try:
            # 1. Event Bus demonstrasyonu
            await self._demo_event_bus()
            
            # 2. Event Store ve Event Sourcing
            await self._demo_event_store()
            
            # 3. Async Message Handler
            await self._demo_async_message_handler()
            
            # 4. Event-Driven Communication Manager
            await self._demo_event_driven_manager()
            
            # 5. Dynamic Event-Driven Agent
            await self._demo_dynamic_event_agent()
            
            # 6. Event Correlation ve Patterns
            await self._demo_event_correlation()
            
            print("\n🎉 Event-Driven Communication Demo completed successfully!")
            
        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            await self._cleanup_all()
    
    async def _demo_event_bus(self):
        """Event Bus demonstrasyonu"""
        print("\n📋 1. Event Bus - Pub/Sub Pattern")
        print("-" * 50)
        
        # Event bus'ı başlat
        await self.event_bus.start()
        
        # Event handler'ları tanımla
        received_events = []
        
        def task_event_handler(event: Event):
            received_events.append(event)
            print(f"   📨 Task Event: {event.event_type} from {event.source_agent_id}")
        
        def agent_event_handler(event: Event):
            received_events.append(event)
            print(f"   🤖 Agent Event: {event.event_type} from {event.source_agent_id}")
        
        # Subscribe to events
        task_sub_id = self.event_bus.subscribe(
            "demo_subscriber_1",
            EventType.TASK_CREATED.value,
            task_event_handler,
            priority=EventPriority.HIGH
        )
        
        agent_sub_id = self.event_bus.subscribe(
            "demo_subscriber_2", 
            EventType.AGENT_STARTED.value,
            agent_event_handler,
            priority=EventPriority.NORMAL
        )
        
        print(f"✅ Subscribed to events: {task_sub_id}, {agent_sub_id}")
        
        # Test event'leri yayınla
        test_events = [
            Event(
                event_type=EventType.TASK_CREATED.value,
                source_agent_id="demo_agent_001",
                data={"task_id": "demo_task_001", "task_type": "computation"},
                priority=EventPriority.HIGH
            ),
            Event(
                event_type=EventType.AGENT_STARTED.value,
                source_agent_id="demo_agent_002",
                data={"agent_type": "SmartAgent", "start_time": time.time()},
                priority=EventPriority.NORMAL
            ),
            Event(
                event_type=EventType.TASK_COMPLETED.value,
                source_agent_id="demo_agent_001",
                data={"task_id": "demo_task_001", "result": "success"},
                priority=EventPriority.HIGH
            )
        ]
        
        print("\n📤 Publishing test events...")
        for event in test_events:
            await self.event_bus.publish(event)
            await asyncio.sleep(0.1)  # Small delay for processing
        
        # Wait for processing
        await asyncio.sleep(1.0)
        
        # Event bus istatistikleri
        stats = self.event_bus.get_stats()
        print(f"\n📊 Event Bus Statistics:")
        print(f"   Events published: {stats['events_published']}")
        print(f"   Events delivered: {stats['events_delivered']}")
        print(f"   Active subscriptions: {stats['active_subscriptions']}")
        print(f"   Received events: {len(received_events)}")
    
    async def _demo_event_store(self):
        """Event Store ve Event Sourcing demonstrasyonu"""
        print("\n📋 2. Event Store - Event Sourcing Pattern")
        print("-" * 50)
        
        stream_id = "demo_stream_001"
        
        # Event'leri store'a ekle
        events_to_store = [
            Event(
                event_type=EventType.AGENT_STARTED.value,
                source_agent_id="demo_agent_003",
                data={"agent_type": "EventSourcedAgent"},
                version=1
            ),
            Event(
                event_type=EventType.TASK_CREATED.value,
                source_agent_id="demo_agent_003",
                data={"task_id": "store_task_001", "task_type": "data_processing"},
                version=2
            ),
            Event(
                event_type=EventType.TASK_COMPLETED.value,
                source_agent_id="demo_agent_003",
                data={"task_id": "store_task_001", "result": {"processed_items": 100}},
                version=3
            )
        ]
        
        print(f"💾 Storing {len(events_to_store)} events to stream: {stream_id}")
        for event in events_to_store:
            await self.event_store.append_event(stream_id, event)
            print(f"   ✅ Stored event: {event.event_type} (v{event.version})")
        
        # Event'leri geri oku
        stored_events = await self.event_store.get_events(stream_id)
        print(f"\n📖 Retrieved {len(stored_events)} events from stream")
        
        # Snapshot oluştur
        current_state = {
            "agent_id": "demo_agent_003",
            "status": "running",
            "completed_tasks": 1,
            "last_task_result": {"processed_items": 100}
        }
        
        await self.event_store.create_snapshot(stream_id, current_state, 3)
        print("📸 Created snapshot at version 3")
        
        # Snapshot'ı geri oku
        snapshot = await self.event_store.get_snapshot(stream_id)
        if snapshot:
            print(f"📸 Retrieved snapshot: version {snapshot['version']}")
            print(f"   State: {snapshot['state']}")
    
    async def _demo_async_message_handler(self):
        """Async Message Handler demonstrasyonu"""
        print("\n📋 3. Async Message Handler")
        print("-" * 50)
        
        handler = AsyncMessageHandler("demo_handler")
        
        # Message handler'ları kaydet
        async def task_request_handler(message: OrionMessage):
            print(f"   📨 Processing task request: {message.content}")
            await asyncio.sleep(0.1)  # Simulate processing
            return True
        
        def communication_handler(message: OrionMessage):
            print(f"   💬 Processing communication: {message.content}")
            return True
        
        handler.register_handler(MessageType.TASK_REQUEST.value, task_request_handler)
        handler.register_handler(MessageType.AGENT_COMMUNICATION.value, communication_handler)
        
        # Middleware ekle
        def logging_middleware(message: OrionMessage):
            print(f"   🔍 Middleware: Processing message {message.message_id}")
            return message
        
        handler.add_middleware(logging_middleware)
        
        # Test mesajları
        test_messages = [
            OrionMessage(
                message_type=MessageType.TASK_REQUEST.value,
                content="Process data batch #1",
                sender_id="demo_client",
                priority=MessagePriority.HIGH.value
            ),
            OrionMessage(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content="Hello from demo client",
                sender_id="demo_client",
                priority=MessagePriority.NORMAL.value
            )
        ]
        
        print(f"🔄 Processing {len(test_messages)} test messages...")
        for message in test_messages:
            success = await handler.handle_message(message)
            status = "✅" if success else "❌"
            print(f"   {status} Message processed: {message.message_type}")
        
        # Handler istatistikleri
        stats = handler.get_stats()
        print(f"\n📊 Handler Statistics:")
        print(f"   Messages processed: {stats['messages_processed']}")
        print(f"   Average processing time: {stats['avg_processing_time']:.3f}s")
        print(f"   Registered handlers: {len(stats['registered_handlers'])}")
    
    async def _demo_event_driven_manager(self):
        """Event-Driven Communication Manager demonstrasyonu"""
        print("\n📋 4. Event-Driven Communication Manager")
        print("-" * 50)
        
        # Manager'ları oluştur
        manager1 = EventDrivenCommunicationManager("demo_manager_001")
        manager2 = EventDrivenCommunicationManager("demo_manager_002")
        
        self.communication_managers["manager1"] = manager1
        self.communication_managers["manager2"] = manager2
        
        # Manager'ları başlat
        await manager1.start()
        await manager2.start()
        print("✅ Started event-driven communication managers")
        
        # Event handler'ları kur
        received_events = []
        
        def event_logger(event: Event):
            received_events.append(event)
            print(f"   📨 Event received: {event.event_type} from {event.source_agent_id}")
        
        manager1.subscribe_to_event(EventType.MESSAGE_SENT.value, event_logger)
        manager2.subscribe_to_event(EventType.MESSAGE_RECEIVED.value, event_logger)
        
        # Test event'leri yayınla
        test_event = Event(
            event_type=EventType.SYSTEM_ALERT.value,
            source_agent_id="demo_manager_001",
            data={
                "alert_type": "info",
                "message": "System status check",
                "timestamp": time.time()
            },
            priority=EventPriority.NORMAL
        )
        
        await manager1.publish_event(test_event)
        print("📤 Published system alert event")
        
        # Wait for processing
        await asyncio.sleep(1.0)
        
        # Manager istatistikleri
        stats1 = manager1.get_comprehensive_stats()
        stats2 = manager2.get_comprehensive_stats()
        
        print(f"\n📊 Manager Statistics:")
        print(f"   Manager 1 events processed: {stats1['manager_stats']['events_processed']}")
        print(f"   Manager 2 events processed: {stats2['manager_stats']['events_processed']}")
        print(f"   Total received events: {len(received_events)}")
    
    async def _demo_dynamic_event_agent(self):
        """Dynamic Event-Driven Agent demonstrasyonu"""
        print("\n📋 5. Dynamic Event-Driven Agent")
        print("-" * 50)
        
        try:
            # Dynamic agent loader'ı al
            loader = get_global_loader()
            
            # Modülleri tara
            modules = loader.scan_modules()
            print(f"🔍 Scanned modules: {len(modules)} found")
            
            # Event-driven agent modülünü yükle
            if "event_driven_agent" in modules:
                print("🔄 Loading event-driven agent module...")
                success = loader.load_module("event_driven_agent")
                
                if success:
                    print("✅ Event-driven agent module loaded successfully")
                    
                    # Agent oluştur
                    agent = loader.create_agent(
                        module_name="event_driven_agent",
                        agent_id="demo_event_agent_001",
                        config_path="config/agents/event_driven_agent_dynamic.json"
                    )
                    
                    if agent:
                        print("✅ Event-driven agent created successfully")
                        self.test_agents.append(agent)
                        
                        # Agent'ı başlat
                        start_success = loader.start_agent("demo_event_agent_001")
                        if start_success:
                            print("✅ Event-driven agent started successfully")
                            
                            # Agent ile etkileşim
                            await self._interact_with_agent(agent)
                        else:
                            print("❌ Failed to start event-driven agent")
                    else:
                        print("❌ Failed to create event-driven agent")
                else:
                    print("❌ Failed to load event-driven agent module")
            else:
                print("⚠️ Event-driven agent module not found")
                
        except Exception as e:
            print(f"❌ Dynamic agent loading error: {e}")
    
    async def _interact_with_agent(self, agent):
        """Agent ile etkileşim"""
        print("\n🤖 Interacting with event-driven agent...")
        
        # Agent'ın enhanced stats'ını al
        if hasattr(agent, 'get_enhanced_stats'):
            stats = agent.get_enhanced_stats()
            print(f"   Agent capabilities: {stats.get('capabilities', [])}")
            print(f"   Active tasks: {stats.get('task_management', {}).get('active_tasks', 0)}")
        
        # Test task oluştur
        if hasattr(agent, 'create_task'):
            task_id = await agent.create_task('demo_task', {
                'description': 'Demo task for testing',
                'priority': 'normal'
            })
            print(f"   ✅ Created task: {task_id}")
            
            # Task'ı tamamla
            await asyncio.sleep(1.0)
            await agent.complete_task(task_id, {'status': 'success', 'result': 'Demo completed'})
            print(f"   ✅ Completed task: {task_id}")
    
    async def _demo_event_correlation(self):
        """Event Correlation demonstrasyonu"""
        print("\n📋 6. Event Correlation and Patterns")
        print("-" * 50)
        
        # Correlation ID ile ilişkili event'ler oluştur
        correlation_id = f"demo_correlation_{int(time.time())}"
        
        correlated_events = [
            Event(
                event_type=EventType.TASK_CREATED.value,
                source_agent_id="demo_agent_004",
                data={"task_id": "corr_task_001", "task_type": "workflow"},
                correlation_id=correlation_id,
                priority=EventPriority.NORMAL
            ),
            Event(
                event_type=EventType.TASK_COMPLETED.value,
                source_agent_id="demo_agent_004",
                data={"task_id": "corr_task_001", "result": "workflow_completed"},
                correlation_id=correlation_id,
                causation_id=correlation_id,
                priority=EventPriority.NORMAL
            ),
            Event(
                event_type=EventType.AGENT_HEARTBEAT.value,
                source_agent_id="demo_agent_004",
                data={"status": "active", "timestamp": time.time()},
                correlation_id=correlation_id,
                priority=EventPriority.LOW
            )
        ]
        
        print(f"🔗 Publishing {len(correlated_events)} correlated events...")
        print(f"   Correlation ID: {correlation_id}")
        
        for i, event in enumerate(correlated_events):
            await self.event_bus.publish(event)
            print(f"   📤 Event {i+1}: {event.event_type}")
            await asyncio.sleep(0.2)
        
        # Event history'yi kontrol et
        await asyncio.sleep(1.0)
        history = self.event_bus.get_event_history(limit=10)
        
        correlated_in_history = [
            e for e in history 
            if e.correlation_id == correlation_id
        ]
        
        print(f"\n📊 Correlation Analysis:")
        print(f"   Events in correlation: {len(correlated_in_history)}")
        print(f"   Event types: {[e.event_type for e in correlated_in_history]}")
        
        # Pattern detection simulation
        patterns = {}
        for event in history:
            pattern_key = f"{event.event_type}:{event.source_agent_id}"
            patterns[pattern_key] = patterns.get(pattern_key, 0) + 1
        
        print(f"   Detected patterns: {len(patterns)}")
        top_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:3]
        for pattern, count in top_patterns:
            print(f"     {pattern}: {count} occurrences")
    
    async def _cleanup_all(self):
        """Tüm kaynakları temizle"""
        try:
            print("\n🧹 Cleaning up resources...")
            
            # Event bus'ı durdur
            await self.event_bus.stop()
            print("✅ Event bus stopped")
            
            # Communication manager'ları durdur
            for name, manager in self.communication_managers.items():
                try:
                    await manager.stop()
                    print(f"✅ Stopped manager: {name}")
                except Exception as e:
                    print(f"❌ Stop error for {name}: {e}")
            
            # Dynamic agent'ları durdur
            if self.test_agents:
                loader = get_global_loader()
                for agent in self.test_agents:
                    try:
                        loader.stop_agent(agent.agent_id)
                        print(f"✅ Stopped agent: {agent.agent_id}")
                    except Exception as e:
                        print(f"❌ Stop error for {agent.agent_id}: {e}")
            
            print("✅ Cleanup completed")
            
        except Exception as e:
            print(f"❌ Cleanup error: {e}")
    
    async def interactive_mode(self):
        """İnteraktif mod"""
        print("\n🎮 Interactive Event-Driven Mode")
        print("-" * 50)
        print("Commands:")
        print("  publish <event_type> <data>   - Publish event")
        print("  stats                         - Show statistics")
        print("  history <limit>               - Show event history")
        print("  correlate <correlation_id>    - Show correlated events")
        print("  quit                          - Exit")
        
        while self.running:
            try:
                command = input("\nEventDriven> ").strip().split()
                
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "publish" and len(command) >= 3:
                    event_type = command[1]
                    data_str = " ".join(command[2:])
                    await self._interactive_publish_event(event_type, data_str)
                elif command[0] == "stats":
                    self._interactive_show_stats()
                elif command[0] == "history":
                    limit = int(command[1]) if len(command) > 1 else 10
                    self._interactive_show_history(limit)
                elif command[0] == "correlate" and len(command) >= 2:
                    correlation_id = command[1]
                    self._interactive_show_correlation(correlation_id)
                else:
                    print("Unknown command or invalid syntax")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def _interactive_publish_event(self, event_type: str, data_str: str):
        """İnteraktif event yayınlama"""
        try:
            # Parse data
            try:
                data = json.loads(data_str)
            except:
                data = {"message": data_str}
            
            # Create event
            event = Event(
                event_type=event_type,
                source_agent_id="interactive_user",
                data=data,
                priority=EventPriority.NORMAL
            )
            
            # Publish event
            await self.event_bus.publish(event)
            print(f"✅ Published event: {event_type}")
            
        except Exception as e:
            print(f"Publish error: {e}")
    
    def _interactive_show_stats(self):
        """İnteraktif istatistik gösterme"""
        stats = self.event_bus.get_stats()
        print(f"\n📊 Event Bus Statistics:")
        print(f"   Events published: {stats['events_published']}")
        print(f"   Events delivered: {stats['events_delivered']}")
        print(f"   Active subscriptions: {stats['active_subscriptions']}")
        print(f"   History size: {stats['history_size']}")
    
    def _interactive_show_history(self, limit: int):
        """İnteraktif event history gösterme"""
        history = self.event_bus.get_event_history(limit=limit)
        print(f"\n📖 Event History (last {len(history)} events):")
        for i, event in enumerate(history[-limit:]):
            print(f"   {i+1}. {event.event_type} from {event.source_agent_id} at {event.timestamp}")
    
    def _interactive_show_correlation(self, correlation_id: str):
        """İnteraktif correlation gösterme"""
        history = self.event_bus.get_event_history()
        correlated = [e for e in history if e.correlation_id == correlation_id]
        
        print(f"\n🔗 Correlated Events for {correlation_id}:")
        if correlated:
            for i, event in enumerate(correlated):
                print(f"   {i+1}. {event.event_type} from {event.source_agent_id}")
        else:
            print("   No correlated events found")


async def main():
    """Ana fonksiyon"""
    demo = EventDrivenCommunicationDemo()
    
    try:
        # Ana demo'yu çalıştır
        await demo.run_demo()
        
        # İnteraktif mod (opsiyonel)
        response = input("\n🎮 Enter interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            await demo.interactive_mode()
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        print("\n🏁 Event-Driven Communication Demo completed")


if __name__ == "__main__":
    asyncio.run(main())
