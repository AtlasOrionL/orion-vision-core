#!/usr/bin/env python3
"""
🚀 ORION VISION CORE - INTEGRATED MAIN LAUNCHER
Tüm Orion bileşenlerini çakışma olmadan başlatan ana dosya

Bu dosya şunları yapar:
1. Tüm Orion Vision Core modüllerini yükler
2. VS Code Extension server'ını başlatır
3. Chat, Terminal, File System API'lerini aktif eder
4. Ollama entegrasyonunu sağlar
5. Agent sistemlerini koordine eder
6. Dashboard ve GUI'yi başlatır

Kullanım:
    python orion_integrated_main.py
    python orion_integrated_main.py --port 8000
    python orion_integrated_main.py --debug
"""

import sys
import os
import asyncio
import argparse
import signal
import threading
import time
from pathlib import Path

# Proje root'unu sys.path'e ekle
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "jobone"))
sys.path.insert(0, str(PROJECT_ROOT / "src" / "jobone" / "vision_core"))

# Ana imports
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

# Orion Vision Core imports
try:
    from src.jobone.vision_core.runner_service import app as runner_app
    from src.jobone.vision_core.orion_main import OrionMain
    from src.jobone.vision_core.agent_core import AgentCore
    from src.jobone.vision_core.core_ai_manager import CoreAIManager
    from src.jobone.vision_core.dynamic_agent_loader import DynamicAgentLoader
    from src.jobone.vision_core.agent_management_api import AgentManagementAPI
    from src.jobone.vision_core.service_discovery import ServiceDiscovery
    from src.jobone.vision_core.task_orchestration import TaskOrchestrator
    from src.jobone.vision_core.event_driven_communication import EventDrivenCommunication
    from src.jobone.vision_core.multi_protocol_communication import MultiProtocolCommunication
except ImportError as e:
    print(f"⚠️ Warning: Some Orion modules not found: {e}")
    print("🔄 Continuing with available modules...")

# FastAPI ve Uvicorn
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    print("❌ FastAPI/Uvicorn not found. Installing...")
    os.system("pip install fastapi uvicorn[standard]")
    import uvicorn
    from fastapi import FastAPI

@dataclass
class OrionConfig:
    """Orion konfigürasyon sınıfı"""
    port: int = 8000
    host: str = "0.0.0.0"
    debug: bool = False
    enable_gui: bool = True
    enable_voice: bool = True
    enable_agents: bool = True
    enable_ollama: bool = True
    enable_dashboard: bool = True
    log_level: str = "INFO"
    max_workers: int = 4

class OrionIntegratedSystem:
    """🚀 Orion Vision Core Entegre Sistem"""
    
    def __init__(self, config: OrionConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.components: Dict[str, Any] = {}
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=config.max_workers)
        
        # Shutdown handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _setup_logging(self) -> logging.Logger:
        """Logging sistemini kur"""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('orion_integrated.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger("OrionIntegrated")
    
    def _signal_handler(self, signum, frame):
        """Graceful shutdown handler"""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    async def initialize_components(self):
        """Tüm Orion bileşenlerini başlat"""
        self.logger.info("🚀 Initializing Orion Vision Core components...")
        
        try:
            # 1. Core AI Manager
            if self.config.enable_ollama:
                self.logger.info("🤖 Initializing Core AI Manager...")
                self.components['ai_manager'] = CoreAIManager()
                
            # 2. Agent Core
            if self.config.enable_agents:
                self.logger.info("🤖 Initializing Agent Core...")
                self.components['agent_core'] = AgentCore()
                
            # 3. Dynamic Agent Loader
            if self.config.enable_agents:
                self.logger.info("🔄 Initializing Dynamic Agent Loader...")
                self.components['agent_loader'] = DynamicAgentLoader()
                
            # 4. Service Discovery
            self.logger.info("🔍 Initializing Service Discovery...")
            self.components['service_discovery'] = ServiceDiscovery()
            
            # 5. Task Orchestrator
            self.logger.info("📋 Initializing Task Orchestrator...")
            self.components['task_orchestrator'] = TaskOrchestrator()
            
            # 6. Event Communication
            self.logger.info("📡 Initializing Event Communication...")
            self.components['event_comm'] = EventDrivenCommunication()
            
            # 7. Multi Protocol Communication
            self.logger.info("🌐 Initializing Multi Protocol Communication...")
            self.components['multi_comm'] = MultiProtocolCommunication()
            
            # 8. Agent Management API
            if self.config.enable_agents:
                self.logger.info("🔧 Initializing Agent Management API...")
                self.components['agent_api'] = AgentManagementAPI()
            
            self.logger.info("✅ All components initialized successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization failed: {e}")
            raise
    
    async def start_web_server(self):
        """FastAPI web server'ı başlat"""
        self.logger.info(f"🌐 Starting web server on {self.config.host}:{self.config.port}")
        
        # Uvicorn config
        uvicorn_config = uvicorn.Config(
            runner_app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level.lower(),
            reload=self.config.debug,
            access_log=True
        )
        
        server = uvicorn.Server(uvicorn_config)
        await server.serve()
    
    def start_gui_components(self):
        """GUI bileşenlerini başlat"""
        if not self.config.enable_gui:
            return
            
        self.logger.info("🖥️ Starting GUI components...")
        
        try:
            # GUI modüllerini import et ve başlat
            gui_modules = [
                "src.jobone.vision_core.gui",
                "src.jobone.vision_core.dashboard", 
                "src.jobone.presentation.streamlit_app"
            ]
            
            for module_name in gui_modules:
                try:
                    self.executor.submit(self._start_gui_module, module_name)
                except Exception as e:
                    self.logger.warning(f"⚠️ GUI module {module_name} failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ GUI startup failed: {e}")
    
    def _start_gui_module(self, module_name: str):
        """GUI modülünü thread'de başlat"""
        try:
            # GUI modülünü dinamik olarak yükle ve başlat
            self.logger.info(f"🖥️ Starting GUI module: {module_name}")
            # Implementation will be added based on available modules
        except Exception as e:
            self.logger.error(f"❌ GUI module {module_name} failed: {e}")
    
    def start_voice_components(self):
        """Voice bileşenlerini başlat"""
        if not self.config.enable_voice:
            return
            
        self.logger.info("🎤 Starting voice components...")
        
        try:
            # Voice modüllerini başlat
            voice_modules = [
                "src.jobone.vision_core.voice",
                "src.jobone.audio_processing"
            ]
            
            for module_name in voice_modules:
                try:
                    self.executor.submit(self._start_voice_module, module_name)
                except Exception as e:
                    self.logger.warning(f"⚠️ Voice module {module_name} failed: {e}")
                    
        except Exception as e:
            self.logger.error(f"❌ Voice startup failed: {e}")
    
    def _start_voice_module(self, module_name: str):
        """Voice modülünü thread'de başlat"""
        try:
            self.logger.info(f"🎤 Starting voice module: {module_name}")
            # Implementation will be added based on available modules
        except Exception as e:
            self.logger.error(f"❌ Voice module {module_name} failed: {e}")
    
    async def run(self):
        """Ana çalıştırma fonksiyonu"""
        try:
            self.running = True
            self.logger.info("🚀 Starting Orion Vision Core Integrated System...")
            
            # Bileşenleri başlat
            await self.initialize_components()
            
            # GUI ve Voice bileşenlerini paralel başlat
            self.start_gui_components()
            self.start_voice_components()
            
            # Ana web server'ı başlat (blocking)
            await self.start_web_server()
            
        except KeyboardInterrupt:
            self.logger.info("🛑 Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"❌ System error: {e}")
            raise
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Sistemi kapat"""
        if not self.running:
            return
            
        self.logger.info("🛑 Shutting down Orion Vision Core...")
        self.running = False
        
        # Bileşenleri kapat
        for name, component in self.components.items():
            try:
                if hasattr(component, 'shutdown'):
                    component.shutdown()
                self.logger.info(f"✅ {name} shut down successfully")
            except Exception as e:
                self.logger.error(f"❌ Error shutting down {name}: {e}")
        
        # Thread pool'u kapat
        self.executor.shutdown(wait=True)
        self.logger.info("✅ Orion Vision Core shutdown complete")

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(description="🚀 Orion Vision Core Integrated System")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--no-gui", action="store_true", help="Disable GUI")
    parser.add_argument("--no-voice", action="store_true", help="Disable voice")
    parser.add_argument("--no-agents", action="store_true", help="Disable agents")
    parser.add_argument("--no-ollama", action="store_true", help="Disable Ollama")
    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    
    args = parser.parse_args()
    
    # Konfigürasyon oluştur
    config = OrionConfig(
        port=args.port,
        host=args.host,
        debug=args.debug,
        enable_gui=not args.no_gui,
        enable_voice=not args.no_voice,
        enable_agents=not args.no_agents,
        enable_ollama=not args.no_ollama,
        log_level=args.log_level
    )
    
    # Banner göster
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                  🚀 ORION VISION CORE                        ║
    ║                 Integrated System v1.0.0                    ║
    ║                                                              ║
    ║  🤖 AI Chat + 🖥️ Terminal + 📁 File System + 🔌 APIs        ║
    ║  🎤 Voice + 🖼️ GUI + 🤖 Agents + 🧠 Ollama                  ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    print(f"🌐 Server: http://{config.host}:{config.port}")
    print(f"📚 API Docs: http://{config.host}:{config.port}/docs")
    print(f"🔧 Debug Mode: {config.debug}")
    print(f"📊 Components: GUI={config.enable_gui}, Voice={config.enable_voice}, Agents={config.enable_agents}, Ollama={config.enable_ollama}")
    print("=" * 60)
    
    # Sistemi başlat
    system = OrionIntegratedSystem(config)
    
    try:
        asyncio.run(system.run())
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        print(f"❌ System error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
