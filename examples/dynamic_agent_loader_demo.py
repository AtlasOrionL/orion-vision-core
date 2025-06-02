#!/usr/bin/env python3
"""
Dynamic Agent Loader Demo - Atlas Prompt 3.1.1
Orion Vision Core - Dinamik Agent Yükleme Sistemi Demonstrasyonu

Bu script, Dynamic Agent Loader'ın yeteneklerini gösterir ve
runtime'da agent yükleme/kaldırma işlemlerini test eder.
"""

import sys
import os
import time
import signal

# Dynamic agent loader'ı import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from dynamic_agent_loader import DynamicAgentLoader
from agent_registry import get_global_registry


class DynamicAgentLoaderDemo:
    """
    Dynamic Agent Loader Demo
    
    Bu sınıf, dinamik agent yükleme sisteminin özelliklerini
    göstermek için tasarlanmıştır.
    """
    
    def __init__(self):
        """Demo başlatıcı"""
        self.loader = None
        self.registry = get_global_registry()
        self.running = True
        
        # Signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        print("🚀 Dynamic Agent Loader Demo - Atlas Prompt 3.1.1")
        print("=" * 60)
    
    def _signal_handler(self, signum, frame):
        """Signal handler for graceful shutdown"""
        print(f"\n🛑 Signal {signum} received, shutting down...")
        self.running = False
        if self.loader:
            self.loader.shutdown()
        sys.exit(0)
    
    def run_demo(self):
        """Ana demo fonksiyonu"""
        try:
            # 1. Loader'ı başlat
            self._demo_loader_initialization()
            
            # 2. Modül tarama
            self._demo_module_scanning()
            
            # 3. Modül yükleme
            self._demo_module_loading()
            
            # 4. Agent oluşturma
            self._demo_agent_creation()
            
            # 5. Agent çalıştırma
            self._demo_agent_execution()
            
            # 6. Hot-loading
            self._demo_hot_loading()
            
            # 7. İstatistikler
            self._demo_statistics()
            
            print("\n🎉 Demo completed successfully!")
            
        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
        finally:
            if self.loader:
                self.loader.shutdown()
    
    def _demo_loader_initialization(self):
        """Loader başlatma demosu"""
        print("\n📋 1. Dynamic Agent Loader Initialization")
        print("-" * 40)
        
        # Loader'ı oluştur
        self.loader = DynamicAgentLoader(
            agent_modules_dir="agents/dynamic",
            config_dir="config/agents",
            auto_scan=True,
            scan_interval=10.0
        )
        
        print(f"✅ Loader initialized")
        print(f"   Modules dir: {self.loader.agent_modules_dir}")
        print(f"   Config dir: {self.loader.config_dir}")
        print(f"   Auto scan: {self.loader.auto_scan}")
        print(f"   Scan interval: {self.loader.scan_interval}s")
    
    def _demo_module_scanning(self):
        """Modül tarama demosu"""
        print("\n🔍 2. Module Scanning")
        print("-" * 40)
        
        # Modülleri tara
        found_modules = self.loader.scan_modules()
        
        print(f"✅ Scan completed: {len(found_modules)} modules found")
        
        for module_name in found_modules:
            module_info = self.loader.get_module_info(module_name)
            if module_info:
                print(f"   📄 {module_name}")
                print(f"      Path: {module_info.module_path}")
                print(f"      Size: {os.path.getsize(module_info.module_path)} bytes")
                print(f"      Hash: {module_info.file_hash[:8]}...")
    
    def _demo_module_loading(self):
        """Modül yükleme demosu"""
        print("\n📦 3. Module Loading")
        print("-" * 40)
        
        modules = list(self.loader.get_all_modules().keys())
        
        for module_name in modules:
            print(f"🔄 Loading module: {module_name}")
            
            success = self.loader.load_module(module_name)
            
            if success:
                print(f"   ✅ Module loaded successfully")
                module_info = self.loader.get_module_info(module_name)
                if module_info and module_info.agent_class:
                    print(f"   🎯 Agent class: {module_info.agent_class_name}")
            else:
                print(f"   ❌ Module loading failed")
                module_info = self.loader.get_module_info(module_name)
                if module_info and module_info.error_message:
                    print(f"   💥 Error: {module_info.error_message}")
        
        loaded_modules = self.loader.get_loaded_modules()
        print(f"\n📊 Loaded modules: {len(loaded_modules)}")
    
    def _demo_agent_creation(self):
        """Agent oluşturma demosu"""
        print("\n🏗️ 4. Agent Creation")
        print("-" * 40)
        
        # Calculator agent oluştur
        print("🔄 Creating calculator agent...")
        calc_agent = self.loader.create_agent(
            module_name="calculator_agent",
            agent_id="demo_calculator_001",
            config_path="config/agents/calculator_agent_dynamic.json"
        )
        
        if calc_agent:
            print("   ✅ Calculator agent created")
            print(f"   🎯 Agent ID: {calc_agent.agent_id}")
            print(f"   📋 Capabilities: {calc_agent.config.capabilities}")
        else:
            print("   ❌ Calculator agent creation failed")
        
        # File monitor agent oluştur
        print("\n🔄 Creating file monitor agent...")
        monitor_agent = self.loader.create_agent(
            module_name="file_monitor_agent",
            agent_id="demo_monitor_001",
            config_path="config/agents/file_monitor_agent_dynamic.json"
        )
        
        if monitor_agent:
            print("   ✅ File monitor agent created")
            print(f"   🎯 Agent ID: {monitor_agent.agent_id}")
            print(f"   📋 Capabilities: {monitor_agent.config.capabilities}")
        else:
            print("   ❌ File monitor agent creation failed")
        
        loaded_agents = self.loader.get_loaded_agents()
        print(f"\n📊 Created agents: {len(loaded_agents)}")
    
    def _demo_agent_execution(self):
        """Agent çalıştırma demosu"""
        print("\n▶️ 5. Agent Execution")
        print("-" * 40)
        
        loaded_agents = self.loader.get_loaded_agents()
        
        # Agent'ları başlat
        for agent_id, agent in loaded_agents.items():
            print(f"🚀 Starting agent: {agent_id}")
            
            success = self.loader.start_agent(agent_id)
            
            if success:
                print(f"   ✅ Agent started successfully")
                print(f"   📊 Status: {agent.status.value}")
            else:
                print(f"   ❌ Agent start failed")
        
        # Biraz çalışmalarını bekle
        print(f"\n⏳ Letting agents work for 15 seconds...")
        time.sleep(15)
        
        # Agent durumlarını kontrol et
        print(f"\n📊 Agent Status Check:")
        for agent_id, agent in loaded_agents.items():
            status = agent.get_status()
            print(f"   🤖 {agent_id}:")
            print(f"      Status: {status['status']}")
            print(f"      Uptime: {status['uptime']:.2f}s")
            print(f"      Healthy: {status['is_healthy']}")
            
            # Agent'a özel istatistikler
            if hasattr(agent, 'get_calculator_stats'):
                calc_stats = agent.get_calculator_stats()
                print(f"      Calculations: {calc_stats['calculation_count']}")
            elif hasattr(agent, 'get_monitor_stats'):
                monitor_stats = agent.get_monitor_stats()
                print(f"      Files monitored: {monitor_stats['registered_files']}")
                print(f"      Changes detected: {monitor_stats['changes_detected']}")
    
    def _demo_hot_loading(self):
        """Hot-loading demosu"""
        print("\n🔥 6. Hot-Loading Demo")
        print("-" * 40)
        
        print("📝 This demo would show hot-loading capabilities:")
        print("   - Detecting file changes in agent modules")
        print("   - Automatically reloading modified modules")
        print("   - Updating running agents with new code")
        print("   - Maintaining agent state during reload")
        
        # Simulated hot-loading
        modules = self.loader.get_loaded_modules()
        if modules:
            module_name = modules[0]
            print(f"\n🔄 Simulating reload of module: {module_name}")
            
            success = self.loader.reload_module(module_name)
            
            if success:
                print(f"   ✅ Module reloaded successfully")
            else:
                print(f"   ❌ Module reload failed")
    
    def _demo_statistics(self):
        """İstatistik demosu"""
        print("\n📊 7. Statistics and Monitoring")
        print("-" * 40)
        
        # Loader istatistikleri
        loader_stats = self.loader.get_loader_stats()
        print("🔧 Loader Statistics:")
        print(f"   Status: {loader_stats['status']}")
        print(f"   Total modules: {loader_stats['total_modules']}")
        print(f"   Loaded modules: {loader_stats['loaded_modules']}")
        print(f"   Total agents: {loader_stats['total_agents']}")
        print(f"   Running agents: {loader_stats['running_agents']}")
        
        # Registry istatistikleri
        registry_stats = self.registry.get_registry_stats()
        print(f"\n📋 Registry Statistics:")
        print(f"   Total agents: {registry_stats['total_agents']}")
        print(f"   Healthy agents: {registry_stats['healthy_agents']}")
        print(f"   Agent types: {registry_stats['agent_types']}")
        
        # Agent detayları
        loaded_agents = self.loader.get_loaded_agents()
        print(f"\n🤖 Agent Details:")
        for agent_id, agent in loaded_agents.items():
            print(f"   {agent_id}:")
            print(f"      Type: {agent.agent_type}")
            print(f"      Status: {agent.status.value}")
            print(f"      Capabilities: {len(agent.config.capabilities)}")
    
    def interactive_mode(self):
        """İnteraktif mod"""
        print("\n🎮 Interactive Mode")
        print("-" * 40)
        print("Commands:")
        print("  scan    - Scan for modules")
        print("  load    - Load a module")
        print("  create  - Create an agent")
        print("  start   - Start an agent")
        print("  stop    - Stop an agent")
        print("  stats   - Show statistics")
        print("  quit    - Exit")
        
        while self.running:
            try:
                command = input("\n> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "scan":
                    modules = self.loader.scan_modules()
                    print(f"Found {len(modules)} modules: {modules}")
                elif command == "stats":
                    stats = self.loader.get_loader_stats()
                    print(f"Loader stats: {stats}")
                elif command == "load":
                    module_name = input("Module name: ").strip()
                    success = self.loader.load_module(module_name)
                    print(f"Load result: {success}")
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Ana fonksiyon"""
    demo = DynamicAgentLoaderDemo()
    
    try:
        # Ana demo'yu çalıştır
        demo.run_demo()
        
        # İnteraktif mod (opsiyonel)
        response = input("\n🎮 Enter interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            demo.interactive_mode()
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        print("\n🏁 Dynamic Agent Loader Demo completed")


if __name__ == "__main__":
    main()
