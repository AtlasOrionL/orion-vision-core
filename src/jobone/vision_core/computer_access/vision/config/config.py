#!/usr/bin/env python3
"""
🔧 Orion Vision Core - Configuration Management System
💖 DUYGULANDIK! SEN YAPARSIN! CONFIGURATION POWER!

Bu modül tüm vision sisteminin konfigürasyonunu merkezi olarak yönetir.
Hardcoded değerleri ortadan kaldırır ve esnek yapılandırma sağlar.

Author: Orion Vision Core Team
Status: 🚀 ACTIVE DEVELOPMENT
"""

import os
import json
import yaml
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from pathlib import Path

@dataclass
class ScreenCaptureConfig:
    """📸 Screen Capture Configuration"""
    timeout_seconds: int = 5
    default_quality: int = 85
    max_memory_mb: int = 50
    simulation_mode: bool = False
    pil_fallback: bool = True
    
@dataclass
class OCRConfig:
    """🔤 OCR Engine Configuration"""
    confidence_threshold: float = 0.8
    language: str = 'eng+tur'
    timeout_seconds: int = 10
    simulation_mode: bool = False
    tesseract_path: Optional[str] = None

@dataclass
class UIDetectionConfig:
    """🎯 UI Detection Configuration"""
    timeout_seconds: int = 3
    confidence_threshold: float = 0.7
    max_elements: int = 100
    simulation_mode: bool = False

@dataclass
class PipelineConfig:
    """🎬 Visual Pipeline Configuration"""
    max_pipelines: int = 10
    timeout_seconds: int = 30
    quality_threshold: float = 0.8
    parallel_processing: bool = False

@dataclass
class AutonomousConfig:
    """🤖 Autonomous Action Configuration"""
    max_actions: int = 5
    timeout_seconds: int = 60
    retry_attempts: int = 3
    context_threshold: float = 0.7

@dataclass
class TaskEngineConfig:
    """📝 Task Engine Configuration"""
    max_tasks: int = 50
    timeout_seconds: int = 120
    retry_attempts: int = 2
    history_size: int = 100

@dataclass
class ChatConfig:
    """💬 Chat Executor Configuration"""
    typing_delay: float = 0.05
    click_delay: float = 0.5
    timeout_seconds: int = 30
    simulation_mode: bool = False

@dataclass
class PerformanceConfig:
    """⚡ Performance Configuration"""
    enable_caching: bool = True
    cache_size: int = 100
    enable_metrics: bool = True
    log_performance: bool = True

@dataclass
class VisionConfig:
    """🎯 Master Vision Configuration"""
    screen_capture: ScreenCaptureConfig
    ocr: OCRConfig
    ui_detection: UIDetectionConfig
    pipeline: PipelineConfig
    autonomous: AutonomousConfig
    task_engine: TaskEngineConfig
    chat: ChatConfig
    performance: PerformanceConfig
    
    # Global settings
    debug_mode: bool = False
    log_level: str = "INFO"
    simulation_mode: bool = False
    
    @classmethod
    def default(cls) -> 'VisionConfig':
        """🎯 Create default configuration"""
        return cls(
            screen_capture=ScreenCaptureConfig(),
            ocr=OCRConfig(),
            ui_detection=UIDetectionConfig(),
            pipeline=PipelineConfig(),
            autonomous=AutonomousConfig(),
            task_engine=TaskEngineConfig(),
            chat=ChatConfig(),
            performance=PerformanceConfig()
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'VisionConfig':
        """📁 Load configuration from file"""
        path = Path(config_path)
        
        if not path.exists():
            return cls.default()
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                if path.suffix.lower() == '.json':
                    data = json.load(f)
                elif path.suffix.lower() in ['.yml', '.yaml']:
                    data = yaml.safe_load(f)
                else:
                    raise ValueError(f"Unsupported config format: {path.suffix}")
            
            return cls.from_dict(data)
        except Exception as e:
            print(f"⚠️ Config load error: {e}, using defaults")
            return cls.default()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VisionConfig':
        """📊 Create configuration from dictionary"""
        return cls(
            screen_capture=ScreenCaptureConfig(**data.get('screen_capture', {})),
            ocr=OCRConfig(**data.get('ocr', {})),
            ui_detection=UIDetectionConfig(**data.get('ui_detection', {})),
            pipeline=PipelineConfig(**data.get('pipeline', {})),
            autonomous=AutonomousConfig(**data.get('autonomous', {})),
            task_engine=TaskEngineConfig(**data.get('task_engine', {})),
            chat=ChatConfig(**data.get('chat', {})),
            performance=PerformanceConfig(**data.get('performance', {})),
            debug_mode=data.get('debug_mode', False),
            log_level=data.get('log_level', 'INFO'),
            simulation_mode=data.get('simulation_mode', False)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """📊 Convert configuration to dictionary"""
        return asdict(self)
    
    def save_to_file(self, config_path: str):
        """💾 Save configuration to file"""
        path = Path(config_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self.to_dict()
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() == '.json':
                json.dump(data, f, indent=2, ensure_ascii=False)
            elif path.suffix.lower() in ['.yml', '.yaml']:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            else:
                raise ValueError(f"Unsupported config format: {path.suffix}")
    
    def enable_simulation_mode(self):
        """🎭 Enable simulation mode for all components"""
        self.simulation_mode = True
        self.screen_capture.simulation_mode = True
        self.ocr.simulation_mode = True
        self.ui_detection.simulation_mode = True
        self.chat.simulation_mode = True
    
    def enable_debug_mode(self):
        """🐛 Enable debug mode"""
        self.debug_mode = True
        self.log_level = "DEBUG"
        self.performance.log_performance = True

class ConfigManager:
    """🔧 Configuration Manager Singleton"""
    
    _instance = None
    _config = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self.load_config()
    
    def load_config(self, config_path: Optional[str] = None):
        """📁 Load configuration"""
        if config_path is None:
            # Try multiple default locations
            possible_paths = [
                'vision_config.json',
                'config/vision_config.json',
                'vision_config.yml',
                'config/vision_config.yml',
                os.path.expanduser('~/.orion/vision_config.json')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            self._config = VisionConfig.from_file(config_path)
            print(f"✅ Configuration loaded from: {config_path}")
        else:
            self._config = VisionConfig.default()
            print("✅ Using default configuration")
    
    @property
    def config(self) -> VisionConfig:
        """🎯 Get current configuration"""
        return self._config
    
    def update_config(self, **kwargs):
        """🔄 Update configuration"""
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
    
    def save_config(self, config_path: str):
        """💾 Save current configuration"""
        self._config.save_to_file(config_path)

# Global configuration instance
config_manager = ConfigManager()

def get_config() -> VisionConfig:
    """🎯 Get global configuration"""
    return config_manager.config

def update_config(**kwargs):
    """🔄 Update global configuration"""
    config_manager.update_config(**kwargs)

def save_config(config_path: str):
    """💾 Save global configuration"""
    config_manager.save_config(config_path)

# Example usage and testing
if __name__ == "__main__":
    print("🔧 Configuration Management System Test")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    
    # Test default config
    config = VisionConfig.default()
    print(f"✅ Default config created")
    print(f"📸 Screen capture timeout: {config.screen_capture.timeout_seconds}s")
    print(f"🔤 OCR confidence: {config.ocr.confidence_threshold}")
    
    # Test simulation mode
    config.enable_simulation_mode()
    print(f"🎭 Simulation mode: {config.simulation_mode}")
    
    # Test config manager
    manager = ConfigManager()
    global_config = get_config()
    print(f"🌍 Global config loaded: {global_config.log_level}")
    
    print("🎉 Configuration system test completed!")
