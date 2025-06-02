#!/usr/bin/env python3
"""
🎯 ORION VISION CORE - COMPONENT COORDINATOR
Tüm Orion bileşenlerini koordine eden merkezi sistem

Bu dosya şunları yapar:
1. Bileşen yaşam döngüsünü yönetir
2. Bağımlılıkları çözer
3. Sağlık kontrolü yapar
4. Hata yönetimi ve recovery
5. Performans izleme
"""

import asyncio
import threading
import time
import traceback
from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, Future
import logging
from pathlib import Path
import sys

# Orion config manager'ı import et
from orion_config_manager import get_config

class ComponentState(Enum):
    """Bileşen durumları"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    RECOVERING = "recovering"

@dataclass
class ComponentInfo:
    """Bileşen bilgileri"""
    name: str
    module_path: str
    class_name: str
    dependencies: List[str]
    optional: bool = False
    auto_restart: bool = True
    max_restart_attempts: int = 3
    restart_delay: float = 5.0
    health_check_interval: float = 30.0
    timeout: float = 60.0

@dataclass
class ComponentStatus:
    """Bileşen durumu"""
    name: str
    state: ComponentState
    instance: Optional[Any] = None
    last_health_check: Optional[float] = None
    restart_count: int = 0
    error_message: Optional[str] = None
    start_time: Optional[float] = None
    stop_time: Optional[float] = None

class OrionComponentCoordinator:
    """🎯 Orion Vision Core Component Coordinator"""
    
    def __init__(self):
        self.config = get_config()
        self.logger = self._setup_logging()
        
        # Component registry
        self.components: Dict[str, ComponentInfo] = {}
        self.component_status: Dict[str, ComponentStatus] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Control flags
        self.running = False
        self.shutdown_requested = False
        
        # Health check thread
        self.health_check_thread: Optional[threading.Thread] = None
        
        # Register all Orion components
        self._register_components()
    
    def _setup_logging(self) -> logging.Logger:
        """Logging sistemini kur"""
        logger = logging.getLogger("OrionCoordinator")
        logger.setLevel(getattr(logging, self.config.logging.level))
        
        if not logger.handlers:
            # File handler
            log_path = Path(self.config.logging.file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_path)
            file_handler.setLevel(getattr(logging, self.config.logging.level))
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, self.config.logging.level))
            
            # Formatter
            formatter = logging.Formatter(self.config.logging.format)
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            if self.config.logging.console_output:
                logger.addHandler(console_handler)
        
        return logger
    
    def _register_components(self):
        """Tüm Orion bileşenlerini kaydet"""
        
        # Core components (always required)
        core_components = [
            ComponentInfo(
                name="runner_service",
                module_path="src.jobone.vision_core.runner_service",
                class_name="app",
                dependencies=[],
                optional=False
            ),
            ComponentInfo(
                name="core_ai_manager",
                module_path="src.jobone.vision_core.core_ai_manager",
                class_name="CoreAIManager",
                dependencies=[],
                optional=False
            )
        ]
        
        # Agent components
        agent_components = [
            ComponentInfo(
                name="agent_core",
                module_path="src.jobone.vision_core.agent_core",
                class_name="AgentCore",
                dependencies=["core_ai_manager"],
                optional=not self.config.agents.enabled
            ),
            ComponentInfo(
                name="dynamic_agent_loader",
                module_path="src.jobone.vision_core.dynamic_agent_loader",
                class_name="DynamicAgentLoader",
                dependencies=["agent_core"],
                optional=not self.config.agents.enabled
            ),
            ComponentInfo(
                name="agent_management_api",
                module_path="src.jobone.vision_core.agent_management_api",
                class_name="app",
                dependencies=["agent_core", "dynamic_agent_loader"],
                optional=not self.config.agents.enabled
            )
        ]
        
        # Communication components
        comm_components = [
            ComponentInfo(
                name="service_discovery",
                module_path="src.jobone.vision_core.service_discovery",
                class_name="ServiceDiscovery",
                dependencies=[],
                optional=True
            ),
            ComponentInfo(
                name="event_driven_communication",
                module_path="src.jobone.vision_core.event_driven_communication",
                class_name="EventDrivenCommunication",
                dependencies=["service_discovery"],
                optional=True
            ),
            ComponentInfo(
                name="multi_protocol_communication",
                module_path="src.jobone.vision_core.multi_protocol_communication",
                class_name="MultiProtocolCommunication",
                dependencies=["service_discovery"],
                optional=True
            ),
            ComponentInfo(
                name="task_orchestration",
                module_path="src.jobone.vision_core.task_orchestration",
                class_name="TaskScheduler",
                dependencies=["event_driven_communication"],
                optional=True
            )
        ]
        
        # GUI components
        gui_components = [
            ComponentInfo(
                name="streamlit_app",
                module_path="src.jobone.presentation.streamlit_app",
                class_name="StreamlitApp",
                dependencies=["core_ai_manager"],
                optional=True  # Streamlit is optional
            )
        ]
        
        # Voice components
        voice_components = [
            ComponentInfo(
                name="voice_system",
                module_path="src.jobone.vision_core.voice",
                class_name="VoiceSystem",
                dependencies=["core_ai_manager"],
                optional=True  # Voice system is optional
            )
        ]
        
        # Tüm bileşenleri kaydet
        all_components = (
            core_components + 
            agent_components + 
            comm_components + 
            gui_components + 
            voice_components
        )
        
        for component in all_components:
            self.register_component(component)
    
    def register_component(self, component_info: ComponentInfo):
        """Bileşen kaydet"""
        self.components[component_info.name] = component_info
        self.component_status[component_info.name] = ComponentStatus(
            name=component_info.name,
            state=ComponentState.UNINITIALIZED
        )
        self.logger.debug(f"📝 Registered component: {component_info.name}")
    
    def _resolve_dependencies(self) -> List[str]:
        """Bağımlılık sırasını çöz (topological sort)"""
        visited = set()
        temp_visited = set()
        result = []
        
        def visit(component_name: str):
            if component_name in temp_visited:
                raise ValueError(f"Circular dependency detected involving {component_name}")
            
            if component_name not in visited:
                temp_visited.add(component_name)
                
                component = self.components.get(component_name)
                if component:
                    for dep in component.dependencies:
                        if dep in self.components:
                            visit(dep)
                
                temp_visited.remove(component_name)
                visited.add(component_name)
                result.append(component_name)
        
        # Tüm bileşenleri ziyaret et
        for component_name in self.components:
            if component_name not in visited:
                visit(component_name)
        
        return result
    
    async def _load_component(self, component_name: str) -> bool:
        """Bileşeni yükle ve başlat"""
        component_info = self.components[component_name]
        status = self.component_status[component_name]
        
        try:
            status.state = ComponentState.INITIALIZING
            self.logger.info(f"🔄 Initializing component: {component_name}")
            
            # Modülü import et
            module_parts = component_info.module_path.split('.')
            module = __import__(component_info.module_path, fromlist=[module_parts[-1]])
            
            # Sınıfı al ve instance oluştur
            component_class = getattr(module, component_info.class_name)
            
            if component_info.class_name == "app":
                # FastAPI app için özel durum
                status.instance = component_class
            elif component_info.name in ["event_driven_communication", "multi_protocol_communication"]:
                # Communication modules need agent_id
                status.instance = component_class("orion_coordinator")
            else:
                # Normal sınıf instance'ı oluştur
                status.instance = component_class()
            
            # Başlatma metodunu çağır (varsa)
            if hasattr(status.instance, 'initialize'):
                if asyncio.iscoroutinefunction(status.instance.initialize):
                    await status.instance.initialize()
                else:
                    status.instance.initialize()
            
            status.state = ComponentState.RUNNING
            status.start_time = time.time()
            status.restart_count = 0
            status.error_message = None
            
            self.logger.info(f"✅ Component started: {component_name}")
            return True
            
        except Exception as e:
            status.state = ComponentState.ERROR
            status.error_message = str(e)
            
            if component_info.optional:
                self.logger.warning(f"⚠️ Optional component {component_name} failed: {e}")
                return True  # Continue with other components
            else:
                self.logger.error(f"❌ Critical component {component_name} failed: {e}")
                self.logger.error(traceback.format_exc())
                return False
    
    async def _stop_component(self, component_name: str):
        """Bileşeni durdur"""
        status = self.component_status[component_name]
        
        if status.state not in [ComponentState.RUNNING, ComponentState.ERROR]:
            return
        
        try:
            status.state = ComponentState.STOPPING
            self.logger.info(f"🛑 Stopping component: {component_name}")
            
            if status.instance and hasattr(status.instance, 'shutdown'):
                if asyncio.iscoroutinefunction(status.instance.shutdown):
                    await status.instance.shutdown()
                else:
                    status.instance.shutdown()
            
            status.state = ComponentState.STOPPED
            status.stop_time = time.time()
            status.instance = None
            
            self.logger.info(f"✅ Component stopped: {component_name}")
            
        except Exception as e:
            self.logger.error(f"❌ Error stopping component {component_name}: {e}")
            status.state = ComponentState.ERROR
            status.error_message = str(e)
    
    async def _health_check_component(self, component_name: str) -> bool:
        """Bileşen sağlık kontrolü"""
        status = self.component_status[component_name]
        
        if status.state != ComponentState.RUNNING:
            return False
        
        try:
            if status.instance and hasattr(status.instance, 'health_check'):
                if asyncio.iscoroutinefunction(status.instance.health_check):
                    result = await status.instance.health_check()
                else:
                    result = status.instance.health_check()
                
                status.last_health_check = time.time()
                return bool(result)
            else:
                # Sağlık kontrolü metodu yoksa, instance'ın varlığını kontrol et
                status.last_health_check = time.time()
                return status.instance is not None
                
        except Exception as e:
            self.logger.warning(f"⚠️ Health check failed for {component_name}: {e}")
            return False
    
    def _start_health_monitoring(self):
        """Sağlık izleme thread'ini başlat"""
        def health_monitor():
            while self.running and not self.shutdown_requested:
                try:
                    # Her bileşen için sağlık kontrolü
                    for component_name, component_info in self.components.items():
                        if not self.running:
                            break
                        
                        # Async health check'i sync context'te çalıştır
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        try:
                            is_healthy = loop.run_until_complete(
                                self._health_check_component(component_name)
                            )
                            
                            if not is_healthy and component_info.auto_restart:
                                status = self.component_status[component_name]
                                if status.restart_count < component_info.max_restart_attempts:
                                    self.logger.warning(f"🔄 Restarting unhealthy component: {component_name}")
                                    loop.run_until_complete(self._restart_component(component_name))
                                else:
                                    self.logger.error(f"❌ Component {component_name} exceeded restart attempts")
                        finally:
                            loop.close()
                    
                    time.sleep(30)  # Health check interval
                    
                except Exception as e:
                    self.logger.error(f"❌ Health monitoring error: {e}")
                    time.sleep(10)
        
        self.health_check_thread = threading.Thread(target=health_monitor, daemon=True)
        self.health_check_thread.start()
        self.logger.info("🏥 Health monitoring started")
    
    async def _restart_component(self, component_name: str):
        """Bileşeni yeniden başlat"""
        component_info = self.components[component_name]
        status = self.component_status[component_name]
        
        status.restart_count += 1
        self.logger.info(f"🔄 Restarting component {component_name} (attempt {status.restart_count})")
        
        # Durdur
        await self._stop_component(component_name)
        
        # Bekle
        await asyncio.sleep(component_info.restart_delay)
        
        # Yeniden başlat
        await self._load_component(component_name)
    
    async def start_all_components(self):
        """Tüm bileşenleri başlat"""
        self.running = True
        self.logger.info("🚀 Starting all Orion components...")
        
        try:
            # Bağımlılık sırasını çöz
            start_order = self._resolve_dependencies()
            self.logger.info(f"📋 Component start order: {start_order}")
            
            # Bileşenleri sırayla başlat
            for component_name in start_order:
                if self.shutdown_requested:
                    break
                
                success = await self._load_component(component_name)
                if not success:
                    component_info = self.components[component_name]
                    if not component_info.optional:
                        self.logger.error(f"❌ Critical component {component_name} failed, aborting startup")
                        return False
            
            # Sağlık izlemeyi başlat
            self._start_health_monitoring()
            
            self.logger.info("✅ All components started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Component startup failed: {e}")
            self.logger.error(traceback.format_exc())
            return False
    
    async def stop_all_components(self):
        """Tüm bileşenleri durdur"""
        self.shutdown_requested = True
        self.logger.info("🛑 Stopping all Orion components...")
        
        try:
            # Bağımlılık sırasının tersine durdur
            start_order = self._resolve_dependencies()
            stop_order = list(reversed(start_order))
            
            for component_name in stop_order:
                await self._stop_component(component_name)
            
            self.running = False
            
            # Health check thread'ini bekle
            if self.health_check_thread and self.health_check_thread.is_alive():
                self.health_check_thread.join(timeout=5)
            
            # Thread pool'u kapat
            self.executor.shutdown(wait=True)
            
            self.logger.info("✅ All components stopped")
            
        except Exception as e:
            self.logger.error(f"❌ Component shutdown error: {e}")
    
    def get_component_status(self, component_name: Optional[str] = None) -> Dict[str, Any]:
        """Bileşen durumunu al"""
        if component_name:
            if component_name in self.component_status:
                status = self.component_status[component_name]
                return {
                    "name": status.name,
                    "state": status.state.value,
                    "restart_count": status.restart_count,
                    "error_message": status.error_message,
                    "last_health_check": status.last_health_check,
                    "uptime": time.time() - status.start_time if status.start_time else None
                }
            else:
                return {"error": f"Component {component_name} not found"}
        else:
            # Tüm bileşenlerin durumunu döndür
            return {
                name: {
                    "state": status.state.value,
                    "restart_count": status.restart_count,
                    "error_message": status.error_message,
                    "last_health_check": status.last_health_check,
                    "uptime": time.time() - status.start_time if status.start_time else None
                }
                for name, status in self.component_status.items()
            }
    
    def print_status_summary(self):
        """Durum özetini yazdır"""
        print("\n" + "="*60)
        print("🎯 ORION COMPONENT STATUS SUMMARY")
        print("="*60)
        
        for name, status in self.component_status.items():
            state_emoji = {
                ComponentState.UNINITIALIZED: "⚪",
                ComponentState.INITIALIZING: "🟡",
                ComponentState.RUNNING: "🟢",
                ComponentState.STOPPING: "🟠",
                ComponentState.STOPPED: "🔴",
                ComponentState.ERROR: "❌",
                ComponentState.RECOVERING: "🔄"
            }
            
            emoji = state_emoji.get(status.state, "❓")
            uptime = f" (uptime: {int(time.time() - status.start_time)}s)" if status.start_time else ""
            error = f" - {status.error_message}" if status.error_message else ""
            
            print(f"{emoji} {name}: {status.state.value}{uptime}{error}")
        
        print("="*60)

# Global coordinator instance
coordinator = OrionComponentCoordinator()

def get_coordinator() -> OrionComponentCoordinator:
    """Global coordinator'ı al"""
    return coordinator

if __name__ == "__main__":
    # Test the coordinator
    import asyncio
    
    async def test_coordinator():
        coord = OrionComponentCoordinator()
        
        # Print initial status
        coord.print_status_summary()
        
        # Start components
        success = await coord.start_all_components()
        if success:
            print("✅ All components started")
            coord.print_status_summary()
            
            # Wait a bit
            await asyncio.sleep(5)
            
            # Stop components
            await coord.stop_all_components()
            print("✅ All components stopped")
        else:
            print("❌ Component startup failed")
    
    asyncio.run(test_coordinator())
