#!/usr/bin/env python3
"""
Service Discovery Demo - Sprint 4.1
Orion Vision Core - Distributed Agent Coordination

Bu demo, Service Discovery sisteminin tüm özelliklerini
gösterir ve test eder.

Author: Orion Development Team
Version: 1.0.0
Date: 2025-05-29
"""

import asyncio
import time
import random
import sys
import os
from typing import List, Dict, Any

# Orion modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from jobone.vision_core.service_discovery import (
    ServiceDiscoveryManager,
    ServiceInfo,
    ServiceStatus,
    LoadBalancingStrategy
)


class MockAgent:
    """Mock Agent - Service Discovery test için"""
    
    def __init__(self, agent_id: str, capabilities: List[str] = None):
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        self.service_id = None
        self.running = False
        self.response_time_base = random.uniform(0.1, 2.0)  # Base response time
        
    async def start(self, discovery_manager: ServiceDiscoveryManager):
        """Agent'ı başlat ve service discovery'ye kaydet"""
        if self.running:
            return
        
        self.running = True
        
        # Service'i kaydet
        self.service_id = discovery_manager.register_agent_service(
            agent_id=self.agent_id,
            service_name=f"agent_{self.agent_id}",
            host="localhost",
            port=random.randint(8000, 9000),
            capabilities=self.capabilities,
            metadata={"type": "mock_agent", "version": "1.0.0"},
            tags=["test", "mock"]
        )
        
        print(f"🤖 Mock Agent {self.agent_id} started with service ID: {self.service_id}")
    
    async def stop(self, discovery_manager: ServiceDiscoveryManager):
        """Agent'ı durdur ve service discovery'den çıkar"""
        if not self.running:
            return
        
        self.running = False
        
        if self.service_id:
            discovery_manager.unregister_agent_service(self.service_id)
            print(f"🛑 Mock Agent {self.agent_id} stopped and unregistered")
    
    async def simulate_work(self, discovery_manager: ServiceDiscoveryManager):
        """İş simülasyonu - response time kaydı için"""
        if not self.running or not self.service_id:
            return
        
        # Simulated work time
        work_time = self.response_time_base + random.uniform(-0.5, 0.5)
        await asyncio.sleep(max(0.1, work_time))
        
        # Response time'ı kaydet
        discovery_manager.record_agent_response_time(self.service_id, work_time)
        
        return f"Work completed by {self.agent_id} in {work_time:.2f}s"


async def demo_service_registration():
    """Service Registration Demo"""
    print("\n" + "="*70)
    print("🔍 SERVICE REGISTRATION DEMO")
    print("="*70)
    
    # Service Discovery Manager oluştur
    discovery_manager = ServiceDiscoveryManager(
        registry_id="demo_registry",
        health_check_interval=10.0,
        cleanup_interval=30.0,
        load_balancing_strategy=LoadBalancingStrategy.ROUND_ROBIN
    )
    
    # Manager'ı başlat
    await discovery_manager.start()
    
    # Mock agent'ları oluştur
    agents = [
        MockAgent("agent_001", ["calculation", "data_processing"]),
        MockAgent("agent_002", ["file_handling", "data_processing"]),
        MockAgent("agent_003", ["calculation", "reporting"]),
        MockAgent("agent_004", ["monitoring", "alerting"]),
        MockAgent("agent_005", ["data_processing", "analytics"])
    ]
    
    # Agent'ları başlat
    print("\n📝 Registering agents...")
    for agent in agents:
        await agent.start(discovery_manager)
        await asyncio.sleep(0.5)  # Staggered registration
    
    # Registry durumunu göster
    stats = discovery_manager.get_comprehensive_stats()
    print(f"\n📊 Registry Stats:")
    print(f"   Active Services: {stats['registry_stats']['active_services']}")
    print(f"   Total Registrations: {stats['manager_stats']['total_service_registrations']}")
    
    return discovery_manager, agents


async def demo_service_discovery(discovery_manager: ServiceDiscoveryManager):
    """Service Discovery Demo"""
    print("\n" + "="*70)
    print("🔍 SERVICE DISCOVERY DEMO")
    print("="*70)
    
    # Capability-based discovery
    print("\n🔍 Discovering agents with 'calculation' capability...")
    calc_agents = discovery_manager.discover_agents(capability="calculation")
    print(f"Found {len(calc_agents)} calculation agents:")
    for agent in calc_agents:
        print(f"   - {agent.service_name} ({agent.agent_id}) @ {agent.get_endpoint_url()}")
    
    # Tag-based discovery
    print("\n🔍 Discovering agents with 'test' tag...")
    test_agents = discovery_manager.discover_agents(tags=["test"])
    print(f"Found {len(test_agents)} test agents:")
    for agent in test_agents:
        print(f"   - {agent.service_name} capabilities: {agent.capabilities}")
    
    # All agents discovery
    print("\n🔍 Discovering all agents...")
    all_agents = discovery_manager.get_all_agents()
    print(f"Total agents in registry: {len(all_agents)}")
    
    # Discovery stats
    stats = discovery_manager.get_comprehensive_stats()
    print(f"\n📊 Discovery Stats:")
    print(f"   Total Discoveries: {stats['manager_stats']['total_service_discoveries']}")


async def demo_load_balancing(discovery_manager: ServiceDiscoveryManager, agents: List[MockAgent]):
    """Load Balancing Demo"""
    print("\n" + "="*70)
    print("⚖️ LOAD BALANCING DEMO")
    print("="*70)
    
    # Round Robin Strategy
    print("\n⚖️ Testing Round Robin Load Balancing...")
    discovery_manager.change_load_balancing_strategy(LoadBalancingStrategy.ROUND_ROBIN)
    
    for i in range(10):
        selected = discovery_manager.select_agent(capability="data_processing")
        if selected:
            print(f"   Request {i+1}: Selected {selected.agent_id}")
            discovery_manager.release_agent(selected.service_id)
        await asyncio.sleep(0.1)
    
    # Least Connections Strategy
    print("\n⚖️ Testing Least Connections Load Balancing...")
    discovery_manager.change_load_balancing_strategy(LoadBalancingStrategy.LEAST_CONNECTIONS)
    
    # Simulate some connections
    active_connections = []
    for i in range(5):
        selected = discovery_manager.select_agent(capability="data_processing")
        if selected:
            print(f"   Connection {i+1}: Selected {selected.agent_id}")
            active_connections.append(selected.service_id)
        await asyncio.sleep(0.1)
    
    # Release some connections
    for i, service_id in enumerate(active_connections[:3]):
        discovery_manager.release_agent(service_id)
        print(f"   Released connection from {service_id}")
    
    # Health-based Strategy
    print("\n⚖️ Testing Health-based Load Balancing...")
    discovery_manager.change_load_balancing_strategy(LoadBalancingStrategy.HEALTH_BASED)
    
    for i in range(5):
        selected = discovery_manager.select_agent()
        if selected:
            print(f"   Health-based selection {i+1}: {selected.agent_id} (heartbeat: {selected.last_heartbeat:.2f})")
            discovery_manager.release_agent(selected.service_id)
        await asyncio.sleep(0.2)
    
    # Load balancer stats
    stats = discovery_manager.get_comprehensive_stats()
    print(f"\n📊 Load Balancer Stats:")
    lb_stats = stats['load_balancer_stats']
    print(f"   Strategy: {lb_stats['strategy']}")
    print(f"   Total Requests: {lb_stats['stats']['total_requests']}")
    print(f"   Success Rate: {lb_stats['success_rate']:.1f}%")


async def demo_health_monitoring(discovery_manager: ServiceDiscoveryManager, agents: List[MockAgent]):
    """Health Monitoring Demo"""
    print("\n" + "="*70)
    print("🏥 HEALTH MONITORING DEMO")
    print("="*70)
    
    print("\n🏥 Starting health monitoring...")
    
    # Simulate some work to generate response times
    print("\n💼 Simulating agent work...")
    for _ in range(10):
        for agent in agents[:3]:  # Use first 3 agents
            if agent.running:
                result = await agent.simulate_work(discovery_manager)
                print(f"   {result}")
        await asyncio.sleep(0.5)
    
    # Show performance stats
    print("\n📊 Agent Performance Stats:")
    for agent in agents[:3]:
        if agent.service_id:
            perf = discovery_manager.get_agent_performance(agent.service_id)
            print(f"   {agent.agent_id}:")
            print(f"     - Avg Response Time: {perf['avg_response_time']:.3f}s")
            print(f"     - Total Requests: {perf['total_requests']}")
            print(f"     - Connection Count: {perf['connection_count']}")
    
    # Health stats
    stats = discovery_manager.get_comprehensive_stats()
    health_stats = stats['health_stats']
    print(f"\n🏥 Health Monitor Stats:")
    print(f"   Total Checks: {health_stats['stats']['total_checks']}")
    print(f"   Success Rate: {health_stats['success_rate']:.1f}%")
    print(f"   Check Interval: {health_stats['check_interval']}s")


async def demo_fault_tolerance(discovery_manager: ServiceDiscoveryManager, agents: List[MockAgent]):
    """Fault Tolerance Demo"""
    print("\n" + "="*70)
    print("🛡️ FAULT TOLERANCE DEMO")
    print("="*70)
    
    print("\n🛡️ Testing fault tolerance...")
    
    # Show initial state
    initial_agents = discovery_manager.get_all_agents()
    print(f"Initial agent count: {len(initial_agents)}")
    
    # Simulate agent failure
    failing_agent = agents[0]
    print(f"\n💥 Simulating failure of {failing_agent.agent_id}...")
    await failing_agent.stop(discovery_manager)
    
    await asyncio.sleep(1)
    
    # Check remaining agents
    remaining_agents = discovery_manager.discover_agents(healthy_only=True)
    print(f"Healthy agents after failure: {len(remaining_agents)}")
    
    # Test load balancing with failed agent
    print("\n⚖️ Testing load balancing after failure...")
    for i in range(5):
        selected = discovery_manager.select_agent()
        if selected:
            print(f"   Request {i+1}: Selected {selected.agent_id}")
            discovery_manager.release_agent(selected.service_id)
    
    # Simulate agent recovery
    print(f"\n🔄 Simulating recovery of {failing_agent.agent_id}...")
    await failing_agent.start(discovery_manager)
    
    await asyncio.sleep(1)
    
    # Check recovered state
    recovered_agents = discovery_manager.get_all_agents()
    print(f"Total agents after recovery: {len(recovered_agents)}")


async def demo_comprehensive_stats(discovery_manager: ServiceDiscoveryManager):
    """Comprehensive Stats Demo"""
    print("\n" + "="*70)
    print("📊 COMPREHENSIVE STATS DEMO")
    print("="*70)
    
    stats = discovery_manager.get_comprehensive_stats()
    
    print(f"\n🌐 Service Discovery Manager Stats:")
    print(f"   Manager ID: {stats['manager_id']}")
    print(f"   Running: {stats['running']}")
    print(f"   Uptime: {stats['manager_stats']['uptime']:.1f}s")
    
    print(f"\n🔍 Registry Stats:")
    reg_stats = stats['registry_stats']
    print(f"   Active Services: {reg_stats['active_services']}")
    print(f"   Service Types: {reg_stats['service_types']}")
    print(f"   Total Registrations: {reg_stats['stats']['total_registrations']}")
    
    print(f"\n🏥 Health Monitor Stats:")
    health_stats = stats['health_stats']
    print(f"   Total Checks: {health_stats['stats']['total_checks']}")
    print(f"   Successful Checks: {health_stats['stats']['successful_checks']}")
    print(f"   Failed Checks: {health_stats['stats']['failed_checks']}")
    print(f"   Success Rate: {health_stats['success_rate']:.1f}%")
    
    print(f"\n⚖️ Load Balancer Stats:")
    lb_stats = stats['load_balancer_stats']
    print(f"   Strategy: {lb_stats['strategy']}")
    print(f"   Total Requests: {lb_stats['stats']['total_requests']}")
    print(f"   Successful Distributions: {lb_stats['stats']['successful_distributions']}")
    print(f"   Success Rate: {lb_stats['success_rate']:.1f}%")


async def cleanup_demo(discovery_manager: ServiceDiscoveryManager, agents: List[MockAgent]):
    """Demo cleanup"""
    print("\n" + "="*70)
    print("🧹 CLEANUP")
    print("="*70)
    
    # Stop all agents
    print("\n🛑 Stopping all agents...")
    for agent in agents:
        if agent.running:
            await agent.stop(discovery_manager)
    
    # Stop discovery manager
    print("\n🛑 Stopping Service Discovery Manager...")
    await discovery_manager.stop()
    
    print("\n✅ Cleanup completed!")


async def main():
    """Ana demo fonksiyonu"""
    print("🚀 Service Discovery System Demo - Sprint 4.1")
    print("Orion Vision Core - Distributed Agent Coordination")
    print("="*70)
    
    try:
        # Service Registration Demo
        discovery_manager, agents = await demo_service_registration()
        
        await asyncio.sleep(2)
        
        # Service Discovery Demo
        await demo_service_discovery(discovery_manager)
        
        await asyncio.sleep(2)
        
        # Load Balancing Demo
        await demo_load_balancing(discovery_manager, agents)
        
        await asyncio.sleep(2)
        
        # Health Monitoring Demo
        await demo_health_monitoring(discovery_manager, agents)
        
        await asyncio.sleep(2)
        
        # Fault Tolerance Demo
        await demo_fault_tolerance(discovery_manager, agents)
        
        await asyncio.sleep(2)
        
        # Comprehensive Stats Demo
        await demo_comprehensive_stats(discovery_manager)
        
        # Cleanup
        await cleanup_demo(discovery_manager, agents)
        
        print("\n🎉 Service Discovery Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
