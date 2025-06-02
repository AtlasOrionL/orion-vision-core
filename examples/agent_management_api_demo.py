#!/usr/bin/env python3
"""
Agent Management API Demo - Atlas Prompt 3.1.2
Orion Vision Core - Agent Yönetim API'si Demonstrasyonu

Bu script, Agent Management API'sinin yeteneklerini gösterir ve
RESTful endpoints'leri test eder.
"""

import sys
import os
import time
import requests
import json
import threading
from typing import Dict, Any

# API base URL
API_BASE_URL = "http://localhost:8000"


class AgentManagementAPIDemo:
    """
    Agent Management API Demo
    
    Bu sınıf, agent management API'sinin özelliklerini
    göstermek için tasarlanmıştır.
    """
    
    def __init__(self, api_url: str = API_BASE_URL):
        """Demo başlatıcı"""
        self.api_url = api_url
        self.session = requests.Session()
        
        print("🚀 Agent Management API Demo - Atlas Prompt 3.1.2")
        print("=" * 60)
        print(f"API URL: {self.api_url}")
    
    def api_call(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict[str, Any]:
        """API çağrısı yap"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            if method == "GET":
                response = self.session.get(url)
            elif method == "POST":
                response = self.session.post(url, json=data)
            elif method == "DELETE":
                response = self.session.delete(url)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API call failed: {e}")
            return {"success": False, "error": str(e)}
    
    def run_demo(self):
        """Ana demo fonksiyonu"""
        try:
            # 1. API sağlık kontrolü
            self._demo_health_check()
            
            # 2. Sistem istatistikleri
            self._demo_system_stats()
            
            # 3. Modül yönetimi
            self._demo_module_management()
            
            # 4. Agent yönetimi
            self._demo_agent_management()
            
            # 5. Agent yaşam döngüsü
            self._demo_agent_lifecycle()
            
            # 6. Sistem sağlık durumu
            self._demo_system_health()
            
            print("\n🎉 API Demo completed successfully!")
            
        except KeyboardInterrupt:
            print("\n⚠️ Demo interrupted by user")
        except Exception as e:
            print(f"\n❌ Demo error: {e}")
    
    def _demo_health_check(self):
        """API sağlık kontrolü demosu"""
        print("\n📋 1. API Health Check")
        print("-" * 40)
        
        response = self.api_call("/health")
        
        if response.get("success"):
            print("✅ API is healthy")
            print(f"   Status: {response['data']['status']}")
            print(f"   Loader: {response['data']['loader_status']}")
            print(f"   Registry: {response['data']['registry_status']}")
        else:
            print("❌ API health check failed")
            return False
        
        return True
    
    def _demo_system_stats(self):
        """Sistem istatistikleri demosu"""
        print("\n📊 2. System Statistics")
        print("-" * 40)
        
        response = self.api_call("/system/stats")
        
        if response.get("success"):
            stats = response["data"]
            loader_stats = stats["loader"]
            registry_stats = stats["registry"]
            
            print("✅ System statistics retrieved")
            print(f"   📦 Modules: {loader_stats['total_modules']} total, {loader_stats['loaded_modules']} loaded")
            print(f"   🤖 Agents: {loader_stats['total_agents']} total, {loader_stats['running_agents']} running")
            print(f"   💚 Healthy: {registry_stats['healthy_agents']} agents")
            print(f"   🏷️ Types: {registry_stats['agent_types']} different types")
        else:
            print("❌ Failed to get system statistics")
    
    def _demo_module_management(self):
        """Modül yönetimi demosu"""
        print("\n📦 3. Module Management")
        print("-" * 40)
        
        # Modülleri listele
        print("🔍 Listing modules...")
        response = self.api_call("/modules")
        
        if response.get("success"):
            modules = response["data"]
            print(f"✅ Found {len(modules)} modules")
            
            for module in modules:
                status = "✅ Loaded" if module["is_loaded"] else "⏸️ Not Loaded"
                print(f"   📄 {module['module_name']}: {status}")
                if module["agent_class_name"]:
                    print(f"      Class: {module['agent_class_name']}")
        
        # Modül tarama
        print("\n🔍 Scanning for modules...")
        response = self.api_call("/modules/scan", "POST")
        
        if response.get("success"):
            found_modules = response["data"]["modules"]
            print(f"✅ Scan completed: {len(found_modules)} modules found")
        
        # Modül yükleme
        print("\n📥 Loading modules...")
        response = self.api_call("/modules")
        
        if response.get("success"):
            modules = response["data"]
            unloaded_modules = [m for m in modules if not m["is_loaded"]]
            
            for module in unloaded_modules[:2]:  # İlk 2 modülü yükle
                module_name = module["module_name"]
                print(f"🔄 Loading module: {module_name}")
                
                load_response = self.api_call("/modules/load", "POST", {"module_name": module_name})
                
                if load_response.get("success"):
                    print(f"   ✅ Module {module_name} loaded successfully")
                else:
                    print(f"   ❌ Failed to load module {module_name}")
    
    def _demo_agent_management(self):
        """Agent yönetimi demosu"""
        print("\n🤖 4. Agent Management")
        print("-" * 40)
        
        # Mevcut agent'ları listele
        print("🔍 Listing existing agents...")
        response = self.api_call("/agents")
        
        if response.get("success"):
            agents = response["data"]
            print(f"✅ Found {len(agents)} agents")
            
            for agent in agents:
                status_icon = "🟢" if agent["status"] == "running" else "🔴"
                health_icon = "💚" if agent["is_healthy"] else "💔"
                print(f"   {status_icon} {agent['agent_id']}: {agent['status']} {health_icon}")
                print(f"      Type: {agent['agent_type']}, Uptime: {agent['uptime']:.1f}s")
        
        # Yeni agent oluştur
        print("\n🏗️ Creating new agents...")
        
        # Calculator agent oluştur
        calc_data = {
            "module_name": "calculator_agent",
            "agent_id": "api_demo_calculator_001",
            "auto_start": True
        }
        
        print(f"🔄 Creating calculator agent: {calc_data['agent_id']}")
        response = self.api_call("/agents", "POST", calc_data)
        
        if response.get("success"):
            print(f"   ✅ Calculator agent created successfully")
        else:
            print(f"   ❌ Failed to create calculator agent")
        
        # File monitor agent oluştur
        monitor_data = {
            "module_name": "file_monitor_agent",
            "agent_id": "api_demo_monitor_001",
            "auto_start": True
        }
        
        print(f"🔄 Creating file monitor agent: {monitor_data['agent_id']}")
        response = self.api_call("/agents", "POST", monitor_data)
        
        if response.get("success"):
            print(f"   ✅ File monitor agent created successfully")
        else:
            print(f"   ❌ Failed to create file monitor agent")
    
    def _demo_agent_lifecycle(self):
        """Agent yaşam döngüsü demosu"""
        print("\n🔄 5. Agent Lifecycle Management")
        print("-" * 40)
        
        # Test agent'ları
        test_agents = ["api_demo_calculator_001", "api_demo_monitor_001"]
        
        for agent_id in test_agents:
            print(f"\n🎯 Testing lifecycle for: {agent_id}")
            
            # Agent durumunu kontrol et
            print("   📊 Checking agent status...")
            response = self.api_call(f"/agents/{agent_id}")
            
            if response.get("success"):
                agent_data = response["data"]
                print(f"   ✅ Agent status: {agent_data['status']}")
                print(f"      Health: {'Healthy' if agent_data['is_healthy'] else 'Unhealthy'}")
                print(f"      Uptime: {agent_data['uptime']:.1f}s")
                
                # Agent'ı durdur
                if agent_data["status"] == "running":
                    print("   ⏹️ Stopping agent...")
                    stop_response = self.api_call(f"/agents/{agent_id}/stop", "POST")
                    
                    if stop_response.get("success"):
                        print("   ✅ Agent stopped successfully")
                        time.sleep(1)  # Biraz bekle
                        
                        # Tekrar başlat
                        print("   ▶️ Starting agent...")
                        start_response = self.api_call(f"/agents/{agent_id}/start", "POST")
                        
                        if start_response.get("success"):
                            print("   ✅ Agent started successfully")
                        else:
                            print("   ❌ Failed to start agent")
                    else:
                        print("   ❌ Failed to stop agent")
            else:
                print(f"   ❌ Agent not found: {agent_id}")
    
    def _demo_system_health(self):
        """Sistem sağlık durumu demosu"""
        print("\n💚 6. System Health Monitoring")
        print("-" * 40)
        
        response = self.api_call("/system/health")
        
        if response.get("success"):
            health = response["data"]
            
            print("✅ System health status retrieved")
            print(f"   🏥 Overall Health: {health['overall_health'].upper()}")
            print(f"   📊 Total Agents: {health['total_agents']}")
            print(f"   🏃 Running Agents: {health['running_agents']}")
            print(f"   💚 Healthy Agents: {health['healthy_agents']}")
            print(f"   🔧 Loader Status: {health['loader_status']}")
            print(f"   📋 Registry Status: {health['registry_status']}")
            
            # Sağlık durumu analizi
            if health["overall_health"] == "healthy":
                print("   🎉 System is operating normally!")
            else:
                print("   ⚠️ System requires attention!")
        else:
            print("❌ Failed to get system health")
    
    def cleanup_demo_agents(self):
        """Demo agent'larını temizle"""
        print("\n🧹 Cleaning up demo agents...")
        
        demo_agents = ["api_demo_calculator_001", "api_demo_monitor_001"]
        
        for agent_id in demo_agents:
            print(f"🗑️ Deleting agent: {agent_id}")
            response = self.api_call(f"/agents/{agent_id}", "DELETE")
            
            if response.get("success"):
                print(f"   ✅ Agent {agent_id} deleted successfully")
            else:
                print(f"   ❌ Failed to delete agent {agent_id}")
    
    def interactive_mode(self):
        """İnteraktif mod"""
        print("\n🎮 Interactive API Mode")
        print("-" * 40)
        print("Commands:")
        print("  health    - Check API health")
        print("  stats     - Show system statistics")
        print("  modules   - List modules")
        print("  agents    - List agents")
        print("  create    - Create an agent")
        print("  cleanup   - Clean up demo agents")
        print("  quit      - Exit")
        
        while True:
            try:
                command = input("\nAPI> ").strip().lower()
                
                if command == "quit":
                    break
                elif command == "health":
                    self._demo_health_check()
                elif command == "stats":
                    self._demo_system_stats()
                elif command == "modules":
                    response = self.api_call("/modules")
                    if response.get("success"):
                        for module in response["data"]:
                            status = "Loaded" if module["is_loaded"] else "Not Loaded"
                            print(f"  {module['module_name']}: {status}")
                elif command == "agents":
                    response = self.api_call("/agents")
                    if response.get("success"):
                        for agent in response["data"]:
                            print(f"  {agent['agent_id']}: {agent['status']}")
                elif command == "create":
                    module_name = input("Module name: ").strip()
                    agent_id = input("Agent ID: ").strip()
                    if module_name and agent_id:
                        data = {
                            "module_name": module_name,
                            "agent_id": agent_id,
                            "auto_start": True
                        }
                        response = self.api_call("/agents", "POST", data)
                        if response.get("success"):
                            print(f"✅ Agent {agent_id} created successfully")
                        else:
                            print(f"❌ Failed to create agent")
                elif command == "cleanup":
                    self.cleanup_demo_agents()
                else:
                    print("Unknown command")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")


def check_api_server():
    """API sunucusunun çalışıp çalışmadığını kontrol et"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def main():
    """Ana fonksiyon"""
    print("🔍 Checking if API server is running...")
    
    if not check_api_server():
        print("❌ API server is not running!")
        print("Please start the API server first:")
        print("  python src/jobone/vision_core/agent_management_api.py")
        return
    
    print("✅ API server is running")
    
    demo = AgentManagementAPIDemo()
    
    try:
        # Ana demo'yu çalıştır
        demo.run_demo()
        
        # İnteraktif mod (opsiyonel)
        response = input("\n🎮 Enter interactive mode? (y/n): ").strip().lower()
        if response == 'y':
            demo.interactive_mode()
        
        # Temizlik
        cleanup_response = input("\n🧹 Clean up demo agents? (y/n): ").strip().lower()
        if cleanup_response == 'y':
            demo.cleanup_demo_agents()
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
    finally:
        print("\n🏁 Agent Management API Demo completed")


if __name__ == "__main__":
    main()
