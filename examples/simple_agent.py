#!/usr/bin/env python3
"""
Simple Agent Example - Atlas Prompt 2.1.1
Orion Vision Core - Basit Agent Örneği

Bu script, agent_core.py modülünü kullanarak basit bir agent implement eder.
"""

import sys
import os
import time
import random

# Agent core'u import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agent_core import Agent, AgentConfig, AgentStatus, create_agent_config


class SimpleAgent(Agent):
    """
    Basit Agent Implementasyonu
    
    Bu agent, temel agent_core.py işlevselliğini göstermek için
    basit bir çalışma döngüsü implement eder.
    """
    
    def __init__(self, config: AgentConfig):
        """
        Simple Agent başlatıcı
        
        Args:
            config: Agent konfigürasyon objesi
        """
        super().__init__(config)
        
        # Agent'a özel değişkenler
        self.task_count = 0
        self.work_interval = 2.0  # Saniye
        self.max_tasks = 10
        
        # Capabilities ekle
        self.add_capability("simple_processing")
        self.add_capability("task_counting")
        self.add_capability("random_work")
    
    def initialize(self) -> bool:
        """
        Agent'a özel başlatma işlemleri
        
        Returns:
            bool: Başlatma başarılı ise True
        """
        try:
            self.logger.info("Initializing Simple Agent...")
            
            # Başlatma işlemleri
            self.task_count = 0
            self.logger.info(f"Work interval: {self.work_interval}s")
            self.logger.info(f"Max tasks: {self.max_tasks}")
            
            # Başlatma başarılı
            self.logger.info("Simple Agent initialization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Simple Agent initialization failed: {e}")
            return False
    
    def run(self):
        """
        Agent'ın ana çalışma döngüsü
        """
        self.logger.info("Simple Agent main loop started")
        
        try:
            while not self.stop_event.is_set() and self.task_count < self.max_tasks:
                # Simulated work
                self._do_work()
                
                # Work interval kadar bekle
                if self.stop_event.wait(self.work_interval):
                    break  # Stop event set edildi
                
        except Exception as e:
            self.logger.error(f"Simple Agent run error: {e}")
            raise
        finally:
            self.logger.info("Simple Agent main loop ended")
    
    def cleanup(self):
        """
        Agent'a özel temizlik işlemleri
        """
        try:
            self.logger.info("Cleaning up Simple Agent...")
            
            # Temizlik işlemleri
            self.logger.info(f"Total tasks completed: {self.task_count}")
            
            # İstatistikleri güncelle
            self.stats['tasks_completed'] = self.task_count
            
            self.logger.info("Simple Agent cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Simple Agent cleanup error: {e}")
    
    def _do_work(self):
        """Simulated work function"""
        try:
            self.task_count += 1
            
            # Random work simulation
            work_type = random.choice(['processing', 'analyzing', 'computing', 'calculating'])
            work_duration = random.uniform(0.1, 0.5)
            
            self.logger.info(f"Task {self.task_count}: {work_type} (duration: {work_duration:.2f}s)")
            
            # Simulate work
            time.sleep(work_duration)
            
            # Random success/failure
            if random.random() < 0.9:  # 90% success rate
                self.logger.info(f"Task {self.task_count} completed successfully")
                self.stats['tasks_completed'] += 1
            else:
                self.logger.warning(f"Task {self.task_count} failed")
                self.stats['tasks_failed'] += 1
                
        except Exception as e:
            self.logger.error(f"Work error: {e}")
            self.stats['tasks_failed'] += 1
    
    def get_task_count(self) -> int:
        """Tamamlanan görev sayısını döndür"""
        return self.task_count
    
    def set_work_interval(self, interval: float):
        """Çalışma aralığını ayarla"""
        self.work_interval = interval
        self.logger.info(f"Work interval updated: {interval}s")
    
    def set_max_tasks(self, max_tasks: int):
        """Maksimum görev sayısını ayarla"""
        self.max_tasks = max_tasks
        self.logger.info(f"Max tasks updated: {max_tasks}")


def create_simple_agent(agent_id: str = "simple_agent") -> SimpleAgent:
    """
    Simple Agent oluştur
    
    Args:
        agent_id: Agent kimliği
        
    Returns:
        SimpleAgent: Oluşturulan agent
    """
    config = create_agent_config(
        agent_id=agent_id,
        agent_name="Simple Test Agent",
        agent_type="simple_agent",
        auto_start=False,
        max_retries=3,
        retry_delay=1.0,
        heartbeat_interval=10.0,
        timeout=60.0,
        log_level="INFO"
    )
    
    return SimpleAgent(config)


def test_simple_agent():
    """Simple Agent test fonksiyonu"""
    print("🚀 Simple Agent Test - Atlas Prompt 2.1.1")
    print("=" * 50)
    
    # Agent oluştur
    agent = create_simple_agent("test_simple_agent")
    
    try:
        # Agent bilgilerini göster
        print(f"📋 Agent Info:")
        print(f"  ID: {agent.agent_id}")
        print(f"  Name: {agent.agent_name}")
        print(f"  Type: {agent.agent_type}")
        print(f"  Capabilities: {agent.config.capabilities}")
        
        # Agent'ı başlat
        print(f"\n🚀 Starting agent...")
        success = agent.start()
        
        if success:
            print(f"✅ Agent started successfully")
            print(f"📊 Status: {agent.status.value}")
            
            # Biraz çalışmasını bekle
            print(f"\n⏳ Letting agent work for 15 seconds...")
            time.sleep(15)
            
            # Durum bilgilerini göster
            status = agent.get_status()
            print(f"\n📊 Agent Status:")
            print(f"  Status: {status['status']}")
            print(f"  Uptime: {status['uptime']:.2f}s")
            print(f"  Is Healthy: {status['is_healthy']}")
            print(f"  Task Count: {agent.get_task_count()}")
            print(f"  Error Count: {status['error_count']}")
            
            # Agent'ı durdur
            print(f"\n🛑 Stopping agent...")
            stop_success = agent.stop()
            
            if stop_success:
                print(f"✅ Agent stopped successfully")
                
                # Final status
                final_status = agent.get_status()
                print(f"\n📊 Final Status:")
                print(f"  Total Uptime: {final_status['uptime']:.2f}s")
                print(f"  Tasks Completed: {final_status['stats']['tasks_completed']}")
                print(f"  Tasks Failed: {final_status['stats']['tasks_failed']}")
                
            else:
                print(f"❌ Agent stop failed")
                
        else:
            print(f"❌ Agent start failed")
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Test interrupted by user")
        agent.stop()
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        agent.stop()
    
    print(f"\n🏁 Simple Agent test completed")


def test_agent_manager():
    """Agent Manager test fonksiyonu"""
    print("\n🚀 Agent Manager Test")
    print("=" * 50)
    
    from agent_core import AgentManager
    
    # Agent Manager oluştur
    manager = AgentManager()
    
    try:
        # Birden fazla agent oluştur
        agents = []
        for i in range(3):
            agent = create_simple_agent(f"managed_agent_{i+1}")
            agent.set_max_tasks(5)  # Daha az görev
            agent.set_work_interval(1.0)  # Daha hızlı
            agents.append(agent)
            
            # Manager'a kaydet
            manager.register_agent(agent)
        
        print(f"📋 Created and registered {len(agents)} agents")
        
        # Tüm agent'ları başlat
        print(f"\n🚀 Starting all agents...")
        start_results = manager.start_all()
        
        for agent_id, success in start_results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {agent_id}: {'Started' if success else 'Failed'}")
        
        # Biraz çalışmalarını bekle
        print(f"\n⏳ Letting agents work for 10 seconds...")
        time.sleep(10)
        
        # Tüm agent durumlarını göster
        print(f"\n📊 All Agent Status:")
        all_status = manager.get_all_status()
        
        for agent_id, status in all_status.items():
            print(f"  {agent_id}:")
            print(f"    Status: {status['status']}")
            print(f"    Uptime: {status['uptime']:.2f}s")
            print(f"    Healthy: {status['is_healthy']}")
        
        # Sağlıklı ve çalışan agent'ları göster
        healthy_agents = manager.get_healthy_agents()
        running_agents = manager.get_running_agents()
        
        print(f"\n📈 Agent Summary:")
        print(f"  Healthy agents: {len(healthy_agents)} - {healthy_agents}")
        print(f"  Running agents: {len(running_agents)} - {running_agents}")
        
        # Tüm agent'ları durdur
        print(f"\n🛑 Stopping all agents...")
        stop_results = manager.stop_all()
        
        for agent_id, success in stop_results.items():
            status = "✅" if success else "❌"
            print(f"  {status} {agent_id}: {'Stopped' if success else 'Failed'}")
        
    except Exception as e:
        print(f"❌ Agent Manager test error: {e}")
        manager.stop_all()
    
    print(f"🏁 Agent Manager test completed")


def main():
    """Ana test fonksiyonu"""
    print("🚀 Agent Core Test Suite - Atlas Prompt 2.1.1")
    print("=" * 60)
    
    try:
        # Test 1: Simple Agent
        test_simple_agent()
        
        # Test 2: Agent Manager
        test_agent_manager()
        
        print(f"\n🎉 All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
