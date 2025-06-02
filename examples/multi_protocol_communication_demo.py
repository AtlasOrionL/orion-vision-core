#!/usr/bin/env python3
"""
Multi-Protocol Communication Demo - Atlas Prompt 3.2.1
Orion Vision Core - Çoklu Protokol İletişim Sistemi Demonstrasyonu

Bu script, multi-protocol communication sisteminin yeteneklerini gösterir ve
farklı protokoller arası iletişimi test eder.
"""

import sys
import os
import time
import asyncio
import signal
from pathlib import Path

# Multi-protocol modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from multi_protocol_communication import (
    MultiProtocolCommunicationManager, ProtocolType, ProtocolConfig, 
    MessageRoute, OrionMessage, MessageType, MessagePriority
)
from dynamic_agent_loader import DynamicAgentLoader, get_global_loader


class MultiProtocolCommunicationDemo:
    """
    Multi-Protocol Communication Demo
    
    Bu sınıf, çoklu protokol iletişim sisteminin özelliklerini
    göstermek için tasarlanmıştır.
    """
    
    def __init__(self):
        """Demo başlatıcı"""
        self.running = True
        self.comm_managers = {}
        self.test_agents = []
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🚀 Multi-Protocol Communication Demo - Atlas Prompt 3.2.1")
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
            # 1. Protocol manager'ları oluştur
            await self._demo_protocol_managers()
            
            # 2. Protocol konfigürasyonları
            await self._demo_protocol_configurations()
            
            # 3. Multi-protocol agent'ları yükle
            await self._demo_dynamic_agent_loading()
            
            # 4. Protocol routing
            await self._demo_protocol_routing()
            
            # 5. Failover ve circuit breaker
            await self._demo_failover_circuit_breaker()
            
            # 6. Performance monitoring
            await self._demo_performance_monitoring()
            
            print("\n🎉 Multi-Protocol Communication Demo completed successfully!")
            
        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            await self._cleanup_all()
    
    async def _demo_protocol_managers(self):
        """Protocol manager'ları oluşturma demosu"""
        print("\n📋 1. Multi-Protocol Communication Managers")
        print("-" * 50)
        
        # Test agent'ları için manager'lar oluştur
        agent_ids = ["demo_agent_001", "demo_agent_002", "demo_agent_003"]
        
        for agent_id in agent_ids:
            manager = MultiProtocolCommunicationManager(agent_id)
            self.comm_managers[agent_id] = manager
            print(f"✅ Communication manager created for: {agent_id}")
        
        print(f"📊 Total managers created: {len(self.comm_managers)}")
    
    async def _demo_protocol_configurations(self):
        """Protocol konfigürasyonları demosu"""
        print("\n🔧 2. Protocol Configurations")
        print("-" * 50)
        
        # Protocol konfigürasyonları tanımla
        protocol_configs = {
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
            )
        }
        
        # Her manager'a protokolleri ekle
        for agent_id, manager in self.comm_managers.items():
            print(f"\n🔄 Configuring protocols for {agent_id}:")
            
            for protocol_type, config in protocol_configs.items():
                success = manager.add_protocol(protocol_type, config)
                status = "✅" if success else "❌"
                print(f"   {status} {protocol_type.value}: {config.host}:{config.port}")
        
        print(f"\n📊 Protocols configured for {len(self.comm_managers)} managers")
    
    async def _demo_dynamic_agent_loading(self):
        """Dinamik agent yükleme demosu"""
        print("\n🤖 3. Dynamic Multi-Protocol Agent Loading")
        print("-" * 50)
        
        try:
            # Dynamic agent loader'ı al
            loader = get_global_loader()
            
            # Modülleri tara
            modules = loader.scan_modules()
            print(f"🔍 Scanned modules: {len(modules)} found")
            
            # Multi-protocol agent modülünü yükle
            if "multi_protocol_agent" in modules:
                print("🔄 Loading multi-protocol agent module...")
                success = loader.load_module("multi_protocol_agent")
                
                if success:
                    print("✅ Multi-protocol agent module loaded successfully")
                    
                    # Agent oluştur
                    agent = loader.create_agent(
                        module_name="multi_protocol_agent",
                        agent_id="demo_multi_protocol_001",
                        config_path="config/agents/multi_protocol_agent_dynamic.json"
                    )
                    
                    if agent:
                        print("✅ Multi-protocol agent created successfully")
                        self.test_agents.append(agent)
                        
                        # Agent'ı başlat
                        start_success = loader.start_agent("demo_multi_protocol_001")
                        if start_success:
                            print("✅ Multi-protocol agent started successfully")
                        else:
                            print("❌ Failed to start multi-protocol agent")
                    else:
                        print("❌ Failed to create multi-protocol agent")
                else:
                    print("❌ Failed to load multi-protocol agent module")
            else:
                print("⚠️ Multi-protocol agent module not found")
                
        except Exception as e:
            print(f"❌ Dynamic agent loading error: {e}")
    
    async def _demo_protocol_routing(self):
        """Protocol routing demosu"""
        print("\n🛤️ 4. Protocol Routing and Message Passing")
        print("-" * 50)
        
        if not self.comm_managers:
            print("⚠️ No communication managers available")
            return
        
        # İlk manager'ı test için kullan
        test_manager = list(self.comm_managers.values())[0]
        
        # Routing kuralları ekle
        print("🔄 Adding routing rules...")
        
        # WebSocket -> RabbitMQ route
        ws_to_rmq_route = MessageRoute(
            source_protocol=ProtocolType.WEBSOCKET,
            target_protocol=ProtocolType.RABBITMQ,
            source_address="*",
            target_address="queue_*"
        )
        test_manager.add_message_route(ws_to_rmq_route)
        print("✅ WebSocket -> RabbitMQ route added")
        
        # HTTP -> WebSocket route
        http_to_ws_route = MessageRoute(
            source_protocol=ProtocolType.HTTP,
            target_protocol=ProtocolType.WEBSOCKET,
            source_address="*",
            target_address="realtime_*"
        )
        test_manager.add_message_route(http_to_ws_route)
        print("✅ HTTP -> WebSocket route added")
        
        # Test mesajları gönder
        print("\n📤 Sending test messages...")
        
        test_messages = [
            {
                "content": "Test message via RabbitMQ",
                "target": "test_queue_rabbitmq",
                "protocol": ProtocolType.RABBITMQ
            },
            {
                "content": "Test message via WebSocket",
                "target": "realtime_test",
                "protocol": ProtocolType.WEBSOCKET
            },
            {
                "content": "Test message via HTTP",
                "target": "api_test",
                "protocol": ProtocolType.HTTP
            }
        ]
        
        for msg_info in test_messages:
            message = OrionMessage(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=msg_info["content"],
                sender_id="demo_sender",
                priority=MessagePriority.NORMAL.value,
                metadata={
                    "test": True,
                    "protocol": msg_info["protocol"].value
                }
            )
            
            try:
                success = await test_manager.send_message(
                    message, msg_info["target"], msg_info["protocol"]
                )
                status = "✅" if success else "❌"
                print(f"   {status} {msg_info['protocol'].value}: {msg_info['content'][:30]}...")
                
            except Exception as e:
                print(f"   ❌ {msg_info['protocol'].value}: Error - {e}")
        
        # Routing istatistikleri
        stats = test_manager.get_comprehensive_stats()
        print(f"\n📊 Routing Statistics:")
        print(f"   Total messages sent: {stats['manager_stats']['total_messages_sent']}")
        print(f"   Active protocols: {len(stats['active_protocols'])}")
    
    async def _demo_failover_circuit_breaker(self):
        """Failover ve circuit breaker demosu"""
        print("\n🔄 5. Failover and Circuit Breaker")
        print("-" * 50)
        
        if not self.comm_managers:
            print("⚠️ No communication managers available")
            return
        
        test_manager = list(self.comm_managers.values())[0]
        
        print("🔧 Circuit breaker is enabled by default")
        print("🔄 Simulating protocol failures...")
        
        # Başarısız mesaj gönderimi simülasyonu
        failed_message = OrionMessage(
            message_type=MessageType.AGENT_COMMUNICATION.value,
            content="Test message for failure simulation",
            sender_id="demo_sender",
            priority=MessagePriority.NORMAL.value
        )
        
        # Var olmayan protokol ile test
        for i in range(3):
            try:
                success = await test_manager.send_message(
                    failed_message, "nonexistent_target", ProtocolType.WEBSOCKET
                )
                status = "✅" if success else "❌"
                print(f"   Attempt {i+1}: {status}")
                
            except Exception as e:
                print(f"   Attempt {i+1}: ❌ Error - {e}")
        
        # Circuit breaker durumunu kontrol et
        health_status = test_manager.get_health_status()
        print(f"\n🏥 Health Status:")
        print(f"   Overall health: {health_status['overall_health']}")
        print(f"   Connected protocols: {health_status['connected_protocols']}")
        print(f"   Circuit breaker enabled: {health_status['circuit_breaker_enabled']}")
        
        # Failover events
        stats = test_manager.get_comprehensive_stats()
        failover_events = stats['manager_stats']['failover_events']
        print(f"   Failover events: {failover_events}")
    
    async def _demo_performance_monitoring(self):
        """Performance monitoring demosu"""
        print("\n📊 6. Performance Monitoring")
        print("-" * 50)
        
        print("🔄 Running performance tests...")
        
        # Her manager için istatistikleri topla
        total_stats = {
            'total_messages_sent': 0,
            'total_messages_received': 0,
            'total_protocols': 0,
            'total_active_protocols': 0,
            'total_failover_events': 0
        }
        
        for agent_id, manager in self.comm_managers.items():
            stats = manager.get_comprehensive_stats()
            health = manager.get_health_status()
            
            print(f"\n📋 {agent_id} Statistics:")
            print(f"   Messages sent: {stats['manager_stats']['total_messages_sent']}")
            print(f"   Messages received: {stats['manager_stats']['total_messages_received']}")
            print(f"   Active protocols: {len(stats['active_protocols'])}")
            print(f"   Health: {health['overall_health']}")
            
            # Toplam istatistiklere ekle
            total_stats['total_messages_sent'] += stats['manager_stats']['total_messages_sent']
            total_stats['total_messages_received'] += stats['manager_stats']['total_messages_received']
            total_stats['total_protocols'] += len(stats['adapter_stats'])
            total_stats['total_active_protocols'] += len(stats['active_protocols'])
            total_stats['total_failover_events'] += stats['manager_stats']['failover_events']
        
        print(f"\n🎯 Overall Performance Summary:")
        print(f"   Total managers: {len(self.comm_managers)}")
        print(f"   Total messages sent: {total_stats['total_messages_sent']}")
        print(f"   Total messages received: {total_stats['total_messages_received']}")
        print(f"   Total protocols configured: {total_stats['total_protocols']}")
        print(f"   Total active protocols: {total_stats['total_active_protocols']}")
        print(f"   Total failover events: {total_stats['total_failover_events']}")
        
        # Agent performance (eğer varsa)
        if self.test_agents:
            print(f"\n🤖 Dynamic Agent Performance:")
            for agent in self.test_agents:
                if hasattr(agent, 'get_protocol_stats'):
                    agent_stats = agent.get_protocol_stats()
                    print(f"   Agent {agent.agent_id}:")
                    print(f"      Message count: {agent_stats.get('message_count', 0)}")
                    print(f"      Last protocol: {agent_stats.get('last_protocol_used', 'None')}")
    
    async def _cleanup_all(self):
        """Tüm kaynakları temizle"""
        try:
            print("\n🧹 Cleaning up resources...")
            
            # Communication manager'ları kapat
            for agent_id, manager in self.comm_managers.items():
                try:
                    await manager.disconnect_all()
                    print(f"✅ Disconnected manager: {agent_id}")
                except Exception as e:
                    print(f"❌ Disconnect error for {agent_id}: {e}")
            
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
        print("\n🎮 Interactive Multi-Protocol Mode")
        print("-" * 50)
        print("Commands:")
        print("  send <protocol> <message>  - Send test message")
        print("  stats <agent_id>          - Show agent statistics")
        print("  health                    - Show health status")
        print("  protocols                 - List available protocols")
        print("  quit                      - Exit")
        
        while self.running:
            try:
                command = input("\nMultiProtocol> ").strip().split()
                
                if not command:
                    continue
                
                if command[0] == "quit":
                    break
                elif command[0] == "send" and len(command) >= 3:
                    protocol_name = command[1]
                    message_text = " ".join(command[2:])
                    await self._interactive_send_message(protocol_name, message_text)
                elif command[0] == "stats" and len(command) >= 2:
                    agent_id = command[1]
                    self._interactive_show_stats(agent_id)
                elif command[0] == "health":
                    self._interactive_show_health()
                elif command[0] == "protocols":
                    self._interactive_list_protocols()
                else:
                    print("Unknown command or invalid syntax")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def _interactive_send_message(self, protocol_name: str, message_text: str):
        """İnteraktif mesaj gönderme"""
        try:
            # Protocol type'ı bul
            protocol_type = None
            for pt in ProtocolType:
                if pt.value == protocol_name.lower():
                    protocol_type = pt
                    break
            
            if not protocol_type:
                print(f"Unknown protocol: {protocol_name}")
                return
            
            # İlk manager'ı kullan
            if not self.comm_managers:
                print("No communication managers available")
                return
            
            manager = list(self.comm_managers.values())[0]
            
            # Test mesajı oluştur
            message = OrionMessage(
                message_type=MessageType.AGENT_COMMUNICATION.value,
                content=message_text,
                sender_id="interactive_user",
                priority=MessagePriority.NORMAL.value,
                metadata={"interactive": True}
            )
            
            # Mesaj gönder
            success = await manager.send_message(message, "interactive_target", protocol_type)
            
            if success:
                print(f"✅ Message sent via {protocol_name}")
            else:
                print(f"❌ Failed to send message via {protocol_name}")
                
        except Exception as e:
            print(f"Send error: {e}")
    
    def _interactive_show_stats(self, agent_id: str):
        """İnteraktif istatistik gösterme"""
        if agent_id in self.comm_managers:
            manager = self.comm_managers[agent_id]
            stats = manager.get_comprehensive_stats()
            
            print(f"\n📊 Statistics for {agent_id}:")
            print(f"   Messages sent: {stats['manager_stats']['total_messages_sent']}")
            print(f"   Messages received: {stats['manager_stats']['total_messages_received']}")
            print(f"   Active protocols: {stats['active_protocols']}")
            print(f"   Failover events: {stats['manager_stats']['failover_events']}")
        else:
            print(f"Agent not found: {agent_id}")
    
    def _interactive_show_health(self):
        """İnteraktif sağlık durumu gösterme"""
        print("\n🏥 System Health Status:")
        
        for agent_id, manager in self.comm_managers.items():
            health = manager.get_health_status()
            print(f"   {agent_id}: {health['overall_health']} ({health['connected_protocols']}/{health['total_protocols']} protocols)")
    
    def _interactive_list_protocols(self):
        """İnteraktif protokol listesi"""
        print("\n🔧 Available Protocols:")
        for protocol in ProtocolType:
            print(f"   {protocol.value}")


async def main():
    """Ana fonksiyon"""
    demo = MultiProtocolCommunicationDemo()
    
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
        print("\n🏁 Multi-Protocol Communication Demo completed")


if __name__ == "__main__":
    asyncio.run(main())
