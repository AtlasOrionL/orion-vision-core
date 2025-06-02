#!/usr/bin/env python3
"""
Config Based Agent Loader - Atlas Prompt 2.1.2
Orion Vision Core - JSON Konfigürasyondan Agent Yükleme

Bu script, JSON konfigürasyon dosyalarından agent'ları yükleyip
çalıştıran bir loader sistemi sağlar.
"""

import sys
import os
import time
import signal
from typing import Dict, List, Optional
from pathlib import Path

# Agent modüllerini import et
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'jobone', 'vision_core'))
from agent_core import (
    Agent, AgentConfig, AgentManager, AgentStatus,
    load_agent_config, load_agent_configs_from_directory, 
    validate_agent_config
)
from agent_registry import AgentRegistry, get_global_registry
from communication_enabled_agent import CommunicationEnabledAgent


class ConfigBasedAgentLoader:
    """
    Config Based Agent Loader
    
    JSON konfigürasyon dosyalarından agent'ları yükleyip yöneten sınıf.
    """
    
    def __init__(self, config_directory: str = "config/agents"):
        """
        Agent Loader başlatıcı
        
        Args:
            config_directory: Agent konfigürasyon dosyalarının bulunduğu dizin
        """
        self.config_directory = config_directory
        self.agent_manager = AgentManager()
        self.registry = get_global_registry()
        self.loaded_agents: Dict[str, Agent] = {}
        self.agent_configs: Dict[str, AgentConfig] = {}
        
        # Agent type mappings
        self.agent_type_mappings = {
            'simple_agent': self._create_simple_agent,
            'communication_agent': self._create_communication_agent,
            'communication_enabled_agent': self._create_communication_enabled_agent,
            'echo_agent': self._create_communication_enabled_agent  # Echo agent is a type of comm agent
        }
        
        print(f"🔧 Agent Loader initialized with config directory: {config_directory}")
    
    def load_configs(self) -> bool:
        """
        Konfigürasyon dosyalarını yükle
        
        Returns:
            bool: Yükleme başarılı ise True
        """
        try:
            print(f"📂 Loading agent configurations from: {self.config_directory}")
            
            # Konfigürasyonları yükle
            self.agent_configs = load_agent_configs_from_directory(self.config_directory)
            
            if not self.agent_configs:
                print(f"⚠️ No agent configurations found in: {self.config_directory}")
                return False
            
            # Konfigürasyonları doğrula
            valid_configs = {}
            for agent_id, config in self.agent_configs.items():
                errors = validate_agent_config(config)
                if errors:
                    print(f"❌ Invalid config for {agent_id}: {errors}")
                else:
                    valid_configs[agent_id] = config
                    print(f"✅ Valid config loaded: {agent_id}")
            
            self.agent_configs = valid_configs
            print(f"📊 Loaded {len(self.agent_configs)} valid agent configurations")
            
            return len(self.agent_configs) > 0
            
        except Exception as e:
            print(f"❌ Config loading error: {e}")
            return False
    
    def create_agents(self) -> bool:
        """
        Konfigürasyonlardan agent'ları oluştur
        
        Returns:
            bool: Oluşturma başarılı ise True
        """
        try:
            print(f"🏗️ Creating agents from configurations...")
            
            created_count = 0
            for agent_id, config in self.agent_configs.items():
                try:
                    agent = self._create_agent_from_config(config)
                    if agent:
                        self.loaded_agents[agent_id] = agent
                        self.agent_manager.register_agent(agent)
                        created_count += 1
                        print(f"✅ Created agent: {agent_id} ({config.agent_type})")
                    else:
                        print(f"❌ Failed to create agent: {agent_id}")
                        
                except Exception as e:
                    print(f"❌ Error creating agent {agent_id}: {e}")
            
            print(f"📊 Created {created_count}/{len(self.agent_configs)} agents")
            return created_count > 0
            
        except Exception as e:
            print(f"❌ Agent creation error: {e}")
            return False
    
    def _create_agent_from_config(self, config: AgentConfig) -> Optional[Agent]:
        """
        Konfigürasyondan agent oluştur
        
        Args:
            config: Agent konfigürasyonu
            
        Returns:
            Agent: Oluşturulan agent veya None
        """
        try:
            agent_type = config.agent_type
            
            if agent_type in self.agent_type_mappings:
                creator_func = self.agent_type_mappings[agent_type]
                return creator_func(config)
            else:
                print(f"⚠️ Unknown agent type: {agent_type}")
                # Default olarak communication enabled agent oluştur
                return self._create_communication_enabled_agent(config)
                
        except Exception as e:
            print(f"❌ Agent creation error for {config.agent_id}: {e}")
            return None
    
    def _create_simple_agent(self, config: AgentConfig) -> Optional[Agent]:
        """Simple agent oluştur"""
        try:
            # Simple agent için import
            from simple_agent import SimpleAgent
            return SimpleAgent(config)
        except ImportError:
            print(f"⚠️ SimpleAgent not available, using CommunicationEnabledAgent")
            return self._create_communication_enabled_agent(config)
    
    def _create_communication_agent(self, config: AgentConfig) -> Optional[Agent]:
        """Communication agent oluştur"""
        return self._create_communication_enabled_agent(config)
    
    def _create_communication_enabled_agent(self, config: AgentConfig) -> Optional[Agent]:
        """Communication enabled agent oluştur"""
        return CommunicationEnabledAgent(config)
    
    def start_agents(self, auto_start_only: bool = True) -> Dict[str, bool]:
        """
        Agent'ları başlat
        
        Args:
            auto_start_only: Sadece auto_start=True olan agent'ları başlat
            
        Returns:
            Dict[str, bool]: Agent ID -> başlatma sonucu
        """
        try:
            print(f"🚀 Starting agents (auto_start_only={auto_start_only})...")
            
            results = {}
            
            for agent_id, agent in self.loaded_agents.items():
                try:
                    # Auto start kontrolü
                    if auto_start_only and not agent.config.auto_start:
                        print(f"⏭️ Skipping {agent_id} (auto_start=False)")
                        results[agent_id] = False
                        continue
                    
                    # Agent'ı başlat
                    success = agent.start()
                    results[agent_id] = success
                    
                    if success:
                        print(f"✅ Started agent: {agent_id}")
                    else:
                        print(f"❌ Failed to start agent: {agent_id}")
                        
                except Exception as e:
                    print(f"❌ Error starting agent {agent_id}: {e}")
                    results[agent_id] = False
            
            started_count = sum(1 for success in results.values() if success)
            print(f"📊 Started {started_count}/{len(results)} agents")
            
            return results
            
        except Exception as e:
            print(f"❌ Agent starting error: {e}")
            return {}
    
    def stop_agents(self) -> Dict[str, bool]:
        """
        Tüm agent'ları durdur
        
        Returns:
            Dict[str, bool]: Agent ID -> durdurma sonucu
        """
        try:
            print(f"🛑 Stopping all agents...")
            
            results = self.agent_manager.stop_all()
            
            stopped_count = sum(1 for success in results.values() if success)
            print(f"📊 Stopped {stopped_count}/{len(results)} agents")
            
            return results
            
        except Exception as e:
            print(f"❌ Agent stopping error: {e}")
            return {}
    
    def get_agent_status(self) -> Dict[str, dict]:
        """Tüm agent'ların durumunu getir"""
        return self.agent_manager.get_all_status()
    
    def get_registry_stats(self) -> dict:
        """Registry istatistiklerini getir"""
        return self.registry.get_registry_stats()
    
    def monitor_agents(self, duration: int = 60):
        """
        Agent'ları belirtilen süre boyunca izle
        
        Args:
            duration: İzleme süresi (saniye)
        """
        try:
            print(f"👁️ Monitoring agents for {duration} seconds...")
            
            start_time = time.time()
            
            while time.time() - start_time < duration:
                # Agent durumlarını kontrol et
                status = self.get_agent_status()
                registry_stats = self.get_registry_stats()
                
                running_count = sum(1 for s in status.values() if s['status'] == 'running')
                healthy_count = len(self.registry.get_healthy_agents())
                
                print(f"📊 Status: {running_count} running, {healthy_count} healthy, "
                      f"{registry_stats['total_agents']} total")
                
                # 10 saniye bekle
                time.sleep(10)
            
            print(f"✅ Monitoring completed")
            
        except KeyboardInterrupt:
            print(f"\n⚠️ Monitoring interrupted by user")
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
    
    def shutdown(self):
        """Loader'ı kapat"""
        try:
            print(f"🔄 Shutting down agent loader...")
            
            # Tüm agent'ları durdur
            self.stop_agents()
            
            # Registry'yi kapat
            self.registry.shutdown()
            
            print(f"✅ Agent loader shutdown completed")
            
        except Exception as e:
            print(f"❌ Shutdown error: {e}")


def signal_handler(signum, frame):
    """Signal handler for graceful shutdown"""
    print(f"\n🛑 Signal {signum} received, shutting down...")
    if 'loader' in globals():
        loader.shutdown()
    sys.exit(0)


def main():
    """Ana fonksiyon"""
    print("🚀 Config Based Agent Loader - Atlas Prompt 2.1.2")
    print("=" * 60)
    
    # Signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    global loader
    loader = None
    
    try:
        # Config directory'yi belirle
        config_dir = os.path.join(os.path.dirname(__file__), '..', 'config', 'agents')
        
        # Agent loader oluştur
        loader = ConfigBasedAgentLoader(config_dir)
        
        # Konfigürasyonları yükle
        if not loader.load_configs():
            print("❌ Failed to load configurations")
            return
        
        # Agent'ları oluştur
        if not loader.create_agents():
            print("❌ Failed to create agents")
            return
        
        # Agent'ları başlat
        start_results = loader.start_agents(auto_start_only=True)
        
        if not any(start_results.values()):
            print("❌ No agents started successfully")
            return
        
        # Registry stats göster
        registry_stats = loader.get_registry_stats()
        print(f"\n📊 Registry Stats:")
        print(f"  Total Agents: {registry_stats['total_agents']}")
        print(f"  Healthy Agents: {registry_stats['healthy_agents']}")
        print(f"  Agent Types: {registry_stats['agent_types']}")
        
        # Agent'ları izle
        loader.monitor_agents(duration=30)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Main error: {e}")
    finally:
        if loader:
            loader.shutdown()
    
    print(f"\n🏁 Config Based Agent Loader completed")


if __name__ == "__main__":
    main()
