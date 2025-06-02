#!/usr/bin/env python3
"""
⚙️ ORION VISION CORE - CONFIGURATION MANAGER
Tüm Orion bileşenlerinin konfigürasyonunu yöneten merkezi sistem

Bu dosya şunları yapar:
1. Tüm modüller için merkezi konfigürasyon
2. Port çakışmalarını önler
3. Bileşen bağımlılıklarını yönetir
4. Environment variables'ları yönetir
5. Güvenlik ayarlarını koordine eder
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import logging

@dataclass
class ServerConfig:
    """Server konfigürasyonu"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    reload: bool = False
    workers: int = 1
    log_level: str = "info"

@dataclass
class DatabaseConfig:
    """Veritabanı konfigürasyonu"""
    type: str = "sqlite"
    host: str = "localhost"
    port: int = 5432
    name: str = "orion.db"
    user: str = "orion"
    password: str = ""
    path: str = "data/orion.db"

@dataclass
class OllamaConfig:
    """Ollama konfigürasyonu"""
    enabled: bool = True
    host: str = "localhost"
    port: int = 11434
    base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2:1b"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class AgentConfig:
    """Agent sistemi konfigürasyonu"""
    enabled: bool = True
    max_agents: int = 10
    heartbeat_interval: int = 30
    cleanup_interval: int = 300
    log_level: str = "INFO"
    registry_path: str = "data/agent_registry.json"

@dataclass
class CommunicationConfig:
    """İletişim konfigürasyonu"""
    rabbitmq_enabled: bool = False
    rabbitmq_host: str = "localhost"
    rabbitmq_port: int = 5672
    rabbitmq_user: str = "guest"
    rabbitmq_password: str = "guest"
    
    grpc_enabled: bool = True
    grpc_port: int = 50051
    
    websocket_enabled: bool = True
    websocket_port: int = 8001

@dataclass
class GUIConfig:
    """GUI konfigürasyonu"""
    enabled: bool = True
    streamlit_port: int = 8501
    dashboard_port: int = 8502
    auto_open: bool = False
    theme: str = "dark"

@dataclass
class VoiceConfig:
    """Voice konfigürasyonu"""
    enabled: bool = True
    input_device: Optional[str] = None
    output_device: Optional[str] = None
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024

@dataclass
class SecurityConfig:
    """Güvenlik konfigürasyonu"""
    enable_cors: bool = True
    allowed_origins: List[str] = None
    enable_rate_limiting: bool = True
    max_requests_per_minute: int = 100
    enable_authentication: bool = False
    secret_key: str = "orion-secret-key-change-in-production"

@dataclass
class LoggingConfig:
    """Logging konfigürasyonu"""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: str = "logs/orion.log"
    max_file_size: int = 10485760  # 10MB
    backup_count: int = 5
    console_output: bool = True

class OrionConfigManager:
    """🔧 Orion Vision Core Configuration Manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "orion_config.yaml"
        self.project_root = Path(__file__).parent.absolute()
        
        # Default configurations
        self.server = ServerConfig()
        self.database = DatabaseConfig()
        self.ollama = OllamaConfig()
        self.agents = AgentConfig()
        self.communication = CommunicationConfig()
        self.gui = GUIConfig()
        self.voice = VoiceConfig()
        self.security = SecurityConfig()
        self.logging = LoggingConfig()
        
        # Port registry to prevent conflicts
        self.port_registry = {
            "main_server": self.server.port,
            "ollama": self.ollama.port,
            "grpc": self.communication.grpc_port,
            "websocket": self.communication.websocket_port,
            "streamlit": self.gui.streamlit_port,
            "dashboard": self.gui.dashboard_port,
            "rabbitmq": self.communication.rabbitmq_port
        }
        
        self.logger = self._setup_logging()
        self._load_config()
        self._setup_environment()
    
    def _setup_logging(self) -> logging.Logger:
        """Logging sistemini kur"""
        logger = logging.getLogger("OrionConfig")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _load_config(self):
        """Konfigürasyon dosyasını yükle"""
        config_path = Path(self.config_file)
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix.lower() == '.yaml' or config_path.suffix.lower() == '.yml':
                        config_data = yaml.safe_load(f)
                    else:
                        config_data = json.load(f)
                
                self._apply_config(config_data)
                self.logger.info(f"✅ Configuration loaded from {config_path}")
                
            except Exception as e:
                self.logger.warning(f"⚠️ Failed to load config from {config_path}: {e}")
                self.logger.info("🔄 Using default configuration")
        else:
            self.logger.info(f"📝 Config file {config_path} not found, creating default...")
            self.save_config()
    
    def _apply_config(self, config_data: Dict[str, Any]):
        """Konfigürasyon verilerini uygula"""
        for section_name, section_data in config_data.items():
            if hasattr(self, section_name) and isinstance(section_data, dict):
                section_obj = getattr(self, section_name)
                for key, value in section_data.items():
                    if hasattr(section_obj, key):
                        setattr(section_obj, key, value)
    
    def _setup_environment(self):
        """Environment variables'ları ayarla"""
        env_mappings = {
            "ORION_HOST": self.server.host,
            "ORION_PORT": str(self.server.port),
            "ORION_DEBUG": str(self.server.debug),
            "ORION_LOG_LEVEL": self.logging.level,
            "OLLAMA_HOST": self.ollama.host,
            "OLLAMA_PORT": str(self.ollama.port),
            "OLLAMA_MODEL": self.ollama.default_model,
            "DATABASE_PATH": self.database.path,
            "AGENT_REGISTRY_PATH": self.agents.registry_path,
            "RABBITMQ_HOST": self.communication.rabbitmq_host,
            "RABBITMQ_PORT": str(self.communication.rabbitmq_port),
            "STREAMLIT_PORT": str(self.gui.streamlit_port),
            "DASHBOARD_PORT": str(self.gui.dashboard_port)
        }
        
        for env_var, value in env_mappings.items():
            if env_var not in os.environ:
                os.environ[env_var] = value
    
    def check_port_conflicts(self) -> List[str]:
        """Port çakışmalarını kontrol et"""
        conflicts = []
        used_ports = {}
        
        for service, port in self.port_registry.items():
            if port in used_ports:
                conflicts.append(f"Port {port} conflict: {service} vs {used_ports[port]}")
            else:
                used_ports[port] = service
        
        return conflicts
    
    def get_available_port(self, start_port: int = 8000) -> int:
        """Kullanılabilir port bul"""
        import socket
        
        for port in range(start_port, start_port + 100):
            if port not in self.port_registry.values():
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        return port
                except OSError:
                    continue
        
        raise RuntimeError("No available ports found")
    
    def resolve_port_conflicts(self):
        """Port çakışmalarını çöz"""
        conflicts = self.check_port_conflicts()
        
        if conflicts:
            self.logger.warning(f"⚠️ Port conflicts detected: {conflicts}")
            
            # Çakışan portları yeniden ata
            for service, port in list(self.port_registry.items()):
                if any(str(port) in conflict for conflict in conflicts):
                    new_port = self.get_available_port(port + 1)
                    self.port_registry[service] = new_port
                    
                    # İlgili config'i güncelle
                    if service == "main_server":
                        self.server.port = new_port
                    elif service == "streamlit":
                        self.gui.streamlit_port = new_port
                    elif service == "dashboard":
                        self.gui.dashboard_port = new_port
                    elif service == "grpc":
                        self.communication.grpc_port = new_port
                    elif service == "websocket":
                        self.communication.websocket_port = new_port
                    
                    self.logger.info(f"🔄 {service} port changed from {port} to {new_port}")
    
    def save_config(self):
        """Konfigürasyonu dosyaya kaydet"""
        config_data = {
            "server": asdict(self.server),
            "database": asdict(self.database),
            "ollama": asdict(self.ollama),
            "agents": asdict(self.agents),
            "communication": asdict(self.communication),
            "gui": asdict(self.gui),
            "voice": asdict(self.voice),
            "security": asdict(self.security),
            "logging": asdict(self.logging)
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            
            self.logger.info(f"💾 Configuration saved to {self.config_file}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save config: {e}")
    
    def get_component_config(self, component: str) -> Dict[str, Any]:
        """Belirli bir bileşenin konfigürasyonunu al"""
        if hasattr(self, component):
            return asdict(getattr(self, component))
        else:
            raise ValueError(f"Unknown component: {component}")
    
    def update_component_config(self, component: str, updates: Dict[str, Any]):
        """Bileşen konfigürasyonunu güncelle"""
        if hasattr(self, component):
            component_obj = getattr(self, component)
            for key, value in updates.items():
                if hasattr(component_obj, key):
                    setattr(component_obj, key, value)
            self.save_config()
        else:
            raise ValueError(f"Unknown component: {component}")
    
    def validate_config(self) -> List[str]:
        """Konfigürasyonu doğrula"""
        errors = []
        
        # Port çakışmalarını kontrol et
        conflicts = self.check_port_conflicts()
        errors.extend(conflicts)
        
        # Gerekli dizinleri kontrol et
        required_dirs = [
            Path(self.database.path).parent,
            Path(self.agents.registry_path).parent,
            Path(self.logging.file_path).parent
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.logger.info(f"📁 Created directory: {dir_path}")
                except Exception as e:
                    errors.append(f"Cannot create directory {dir_path}: {e}")
        
        # Ollama bağlantısını kontrol et
        if self.ollama.enabled:
            try:
                import requests
                response = requests.get(f"{self.ollama.base_url}/api/tags", timeout=5)
                if response.status_code != 200:
                    errors.append(f"Ollama not accessible at {self.ollama.base_url}")
            except Exception as e:
                errors.append(f"Ollama connection failed: {e}")
        
        return errors
    
    def print_config_summary(self):
        """Konfigürasyon özetini yazdır"""
        print("\n" + "="*60)
        print("🔧 ORION VISION CORE - CONFIGURATION SUMMARY")
        print("="*60)
        print(f"🌐 Main Server: http://{self.server.host}:{self.server.port}")
        print(f"🤖 Ollama: {self.ollama.base_url} (Model: {self.ollama.default_model})")
        print(f"🖥️ Streamlit GUI: http://localhost:{self.gui.streamlit_port}")
        print(f"📊 Dashboard: http://localhost:{self.gui.dashboard_port}")
        print(f"🔌 gRPC: localhost:{self.communication.grpc_port}")
        print(f"🌐 WebSocket: localhost:{self.communication.websocket_port}")
        print(f"💾 Database: {self.database.path}")
        print(f"📝 Logs: {self.logging.file_path}")
        print(f"🔐 Debug Mode: {self.server.debug}")
        print("="*60)

# Global config instance
config_manager = OrionConfigManager()

def get_config() -> OrionConfigManager:
    """Global config manager'ı al"""
    return config_manager

if __name__ == "__main__":
    # Test the configuration manager
    config = OrionConfigManager()
    
    # Validate configuration
    errors = config.validate_config()
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration is valid")
    
    # Print summary
    config.print_config_summary()
    
    # Save config
    config.save_config()
