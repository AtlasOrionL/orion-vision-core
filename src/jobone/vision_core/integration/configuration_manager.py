"""
⚙️ Configuration Manager - PHASE 1 IMPROVEMENT

Centralized configuration management for PHASE 1 CONSOLIDATION.
Environment-aware, hierarchical, and dynamic configuration system.

Author: Orion Vision Core Team
Phase: PHASE 1 - IMPROVEMENT
Priority: HIGH
"""

import logging
import json
import yaml
import os
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Configuration Sources
class ConfigSource(Enum):
    """Configuration source types"""
    DEFAULT = "default"                             # Default values
    FILE = "file"                                   # Configuration file
    ENVIRONMENT = "environment"                     # Environment variables
    RUNTIME = "runtime"                             # Runtime overrides

# Configuration Formats
class ConfigFormat(Enum):
    """Configuration file formats"""
    JSON = "json"
    YAML = "yaml"
    TOML = "toml"

@dataclass
class IntegrationBridgeConfig:
    """Integration Bridge configuration"""
    
    # Environment settings
    environment_type: str = "hybrid"                # auto, headless, gui, hybrid
    display_available: bool = True
    headless_fallback: bool = True
    
    # Component settings
    enable_q01_vision: bool = True
    enable_q02_alt_las: bool = True
    enable_q03_tasks: bool = True
    enable_q04_ai: bool = True
    enable_q05_quantum: bool = True
    
    # Performance settings
    parallel_initialization: bool = True
    lazy_loading: bool = True
    cache_enabled: bool = True
    
    # Error handling
    graceful_degradation: bool = True
    retry_attempts: int = 3
    timeout_seconds: float = 30.0

@dataclass
class UnifiedInterfaceConfig:
    """Unified Interface configuration"""
    
    # Interface settings
    max_concurrent_requests: int = 100
    request_timeout: float = 30.0
    response_cache_size: int = 1000
    
    # Performance settings
    enable_request_batching: bool = True
    batch_size: int = 10
    batch_timeout: float = 1.0
    
    # Monitoring
    enable_metrics: bool = True
    metrics_interval: float = 60.0
    
    # Security
    enable_authentication: bool = False
    api_key_required: bool = False

@dataclass
class GracefulDegradationConfig:
    """Graceful Degradation configuration"""
    
    # Error thresholds
    error_threshold_critical: int = 10
    error_threshold_emergency: int = 20
    max_error_history: int = 1000
    
    # Recovery settings
    recovery_timeout: float = 30.0
    auto_recovery_enabled: bool = True
    fallback_enabled: bool = True
    
    # Health monitoring
    health_check_interval: float = 60.0
    component_timeout: float = 10.0

@dataclass
class ComponentIntegratorConfig:
    """Component Integrator configuration"""
    
    # Discovery settings
    auto_discovery: bool = True
    discovery_paths: List[str] = field(default_factory=lambda: [
        "jobone.vision_core.computer_access.vision",
        "jobone.vision_core.quantum",
        "jobone.vision_core.consciousness"
    ])
    
    # Loading settings
    lazy_loading: bool = True
    parallel_loading: bool = True
    load_timeout: float = 30.0
    
    # Health monitoring
    health_check_interval: float = 60.0
    auto_restart_failed: bool = True

@dataclass
class LoggingConfig:
    """Logging configuration"""
    
    # Log levels
    level: str = "INFO"                             # DEBUG, INFO, WARNING, ERROR
    console_level: str = "INFO"
    file_level: str = "DEBUG"
    
    # Log files
    log_file: str = "logs/orion_vision_core.log"
    error_log_file: str = "logs/orion_errors.log"
    max_file_size: int = 10 * 1024 * 1024          # 10MB
    backup_count: int = 5
    
    # Formatting
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"

@dataclass
class Phase1Config:
    """Complete PHASE 1 configuration"""
    
    # Component configurations
    integration_bridge: IntegrationBridgeConfig = field(default_factory=IntegrationBridgeConfig)
    unified_interface: UnifiedInterfaceConfig = field(default_factory=UnifiedInterfaceConfig)
    graceful_degradation: GracefulDegradationConfig = field(default_factory=GracefulDegradationConfig)
    component_integrator: ComponentIntegratorConfig = field(default_factory=ComponentIntegratorConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Global settings
    version: str = "1.0.0"
    environment: str = "development"                # development, testing, production
    debug_mode: bool = True
    
    # Paths
    base_path: str = ""
    config_path: str = "config"
    logs_path: str = "logs"
    cache_path: str = "cache"

class ConfigurationManager:
    """
    Configuration Manager
    
    PHASE 1 IMPROVEMENT - Centralized configuration management.
    Hierarchical, environment-aware, and dynamic configuration.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        
        # Configuration storage
        self.config = Phase1Config()
        self.config_sources: Dict[str, ConfigSource] = {}
        self.config_file = config_file or "config/phase1_config.yaml"
        
        # Environment detection
        self.environment = os.getenv("ORION_ENV", "development")
        self.config.environment = self.environment
        
        # Threading
        self._lock = threading.Lock()
        
        # Initialize
        self._setup_paths()
        self._load_configuration()
        
        self.logger.info("⚙️ ConfigurationManager initialized - PHASE 1 IMPROVEMENT")
    
    def _setup_paths(self):
        """Setup configuration paths"""
        try:
            # Determine base path
            if not self.config.base_path:
                self.config.base_path = os.getcwd()
            
            # Create directories
            paths_to_create = [
                self.config.config_path,
                self.config.logs_path,
                self.config.cache_path
            ]
            
            for path in paths_to_create:
                full_path = os.path.join(self.config.base_path, path)
                os.makedirs(full_path, exist_ok=True)
            
            self.logger.info(f"✅ Configuration paths setup: {self.config.base_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to setup paths: {e}")
    
    def _load_configuration(self):
        """Load configuration from various sources"""
        try:
            # 1. Load from file if exists
            config_file_path = os.path.join(self.config.base_path, self.config_file)
            if os.path.exists(config_file_path):
                self._load_from_file(config_file_path)
            else:
                self.logger.info(f"📄 Config file not found: {config_file_path}, using defaults")
                self._save_default_config(config_file_path)
            
            # 2. Override with environment variables
            self._load_from_environment()
            
            # 3. Apply environment-specific settings
            self._apply_environment_settings()
            
            self.logger.info(f"✅ Configuration loaded for environment: {self.environment}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
    
    def _load_from_file(self, file_path: str):
        """Load configuration from file"""
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    data = yaml.safe_load(f)
                else:
                    data = json.load(f)
            
            # Update configuration
            self._update_config_from_dict(data)
            self.logger.info(f"✅ Configuration loaded from file: {file_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load config file {file_path}: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables"""
        try:
            env_mappings = {
                'ORION_DEBUG': ('debug_mode', bool),
                'ORION_LOG_LEVEL': ('logging.level', str),
                'ORION_PARALLEL_INIT': ('integration_bridge.parallel_initialization', bool),
                'ORION_HEADLESS_FALLBACK': ('integration_bridge.headless_fallback', bool),
                'ORION_ENABLE_Q01': ('integration_bridge.enable_q01_vision', bool),
                'ORION_ENABLE_Q02': ('integration_bridge.enable_q02_alt_las', bool),
                'ORION_ENABLE_Q03': ('integration_bridge.enable_q03_tasks', bool),
                'ORION_ENABLE_Q04': ('integration_bridge.enable_q04_ai', bool),
                'ORION_ENABLE_Q05': ('integration_bridge.enable_q05_quantum', bool),
                'ORION_TIMEOUT': ('integration_bridge.timeout_seconds', float),
                'ORION_MAX_REQUESTS': ('unified_interface.max_concurrent_requests', int),
                'ORION_ERROR_THRESHOLD': ('graceful_degradation.error_threshold_critical', int)
            }
            
            for env_var, (config_path, value_type) in env_mappings.items():
                env_value = os.getenv(env_var)
                if env_value is not None:
                    try:
                        # Convert value
                        if value_type == bool:
                            converted_value = env_value.lower() in ('true', '1', 'yes', 'on')
                        elif value_type == int:
                            converted_value = int(env_value)
                        elif value_type == float:
                            converted_value = float(env_value)
                        else:
                            converted_value = env_value
                        
                        # Set configuration value
                        self._set_config_value(config_path, converted_value)
                        self.config_sources[config_path] = ConfigSource.ENVIRONMENT
                        
                    except ValueError as e:
                        self.logger.warning(f"⚠️ Invalid environment value {env_var}={env_value}: {e}")
            
            self.logger.info("✅ Environment variables loaded")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to load environment variables: {e}")
    
    def _apply_environment_settings(self):
        """Apply environment-specific settings"""
        try:
            if self.environment == "production":
                # Production settings
                self.config.debug_mode = False
                self.config.logging.level = "WARNING"
                self.config.logging.console_level = "ERROR"
                self.config.integration_bridge.graceful_degradation = True
                self.config.graceful_degradation.auto_recovery_enabled = True
                
            elif self.environment == "testing":
                # Testing settings
                self.config.debug_mode = True
                self.config.logging.level = "DEBUG"
                self.config.integration_bridge.timeout_seconds = 10.0
                self.config.unified_interface.request_timeout = 10.0
                
            elif self.environment == "development":
                # Development settings
                self.config.debug_mode = True
                self.config.logging.level = "DEBUG"
                self.config.logging.console_level = "DEBUG"
            
            self.logger.info(f"✅ Environment-specific settings applied: {self.environment}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to apply environment settings: {e}")
    
    def _update_config_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary"""
        try:
            # Recursively update configuration
            def update_nested(obj, data_dict):
                for key, value in data_dict.items():
                    if hasattr(obj, key):
                        attr = getattr(obj, key)
                        if isinstance(value, dict) and hasattr(attr, '__dict__'):
                            update_nested(attr, value)
                        else:
                            setattr(obj, key, value)
            
            update_nested(self.config, data)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to update config from dict: {e}")
    
    def _set_config_value(self, path: str, value: Any):
        """Set configuration value by path"""
        try:
            parts = path.split('.')
            obj = self.config
            
            # Navigate to parent object
            for part in parts[:-1]:
                obj = getattr(obj, part)
            
            # Set final value
            setattr(obj, parts[-1], value)
            
        except Exception as e:
            self.logger.error(f"❌ Failed to set config value {path}={value}: {e}")
    
    def _save_default_config(self, file_path: str):
        """Save default configuration to file"""
        try:
            # Convert config to dictionary
            config_dict = asdict(self.config)
            
            # Save to file
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"✅ Default configuration saved: {file_path}")
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save default config: {e}")
    
    def get_config(self) -> Phase1Config:
        """Get complete configuration"""
        with self._lock:
            return self.config
    
    def get_integration_bridge_config(self) -> IntegrationBridgeConfig:
        """Get integration bridge configuration"""
        return self.config.integration_bridge
    
    def get_unified_interface_config(self) -> UnifiedInterfaceConfig:
        """Get unified interface configuration"""
        return self.config.unified_interface
    
    def get_graceful_degradation_config(self) -> GracefulDegradationConfig:
        """Get graceful degradation configuration"""
        return self.config.graceful_degradation
    
    def get_component_integrator_config(self) -> ComponentIntegratorConfig:
        """Get component integrator configuration"""
        return self.config.component_integrator
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration"""
        return self.config.logging
    
    def update_config(self, updates: Dict[str, Any]) -> bool:
        """Update configuration at runtime"""
        try:
            with self._lock:
                self._update_config_from_dict(updates)
                
                # Mark as runtime override
                for key in updates.keys():
                    self.config_sources[key] = ConfigSource.RUNTIME
                
                self.logger.info(f"✅ Configuration updated: {list(updates.keys())}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to update configuration: {e}")
            return False
    
    def save_config(self, file_path: Optional[str] = None) -> bool:
        """Save current configuration to file"""
        try:
            save_path = file_path or os.path.join(self.config.base_path, self.config_file)
            
            with self._lock:
                config_dict = asdict(self.config)
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'w') as f:
                if save_path.endswith('.yaml') or save_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, indent=2)
                else:
                    json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"✅ Configuration saved: {save_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        with self._lock:
            return {
                'environment': self.environment,
                'config_file': self.config_file,
                'base_path': self.config.base_path,
                'version': self.config.version,
                'debug_mode': self.config.debug_mode,
                'config_sources': dict(self.config_sources),
                'last_updated': datetime.now().isoformat()
            }

# Global configuration manager instance
_config_manager: Optional[ConfigurationManager] = None

def get_config_manager() -> ConfigurationManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigurationManager()
    return _config_manager

def get_config() -> Phase1Config:
    """Get current configuration"""
    return get_config_manager().get_config()

# Utility functions
def test_configuration_manager():
    """Test configuration manager"""
    print("⚙️ Testing Configuration Manager...")
    
    # Create manager
    config_manager = ConfigurationManager()
    print("✅ Configuration manager created")
    
    # Get configuration
    config = config_manager.get_config()
    print(f"✅ Configuration loaded: {config.environment}")
    
    # Test updates
    updates = {'debug_mode': False, 'logging': {'level': 'WARNING'}}
    config_manager.update_config(updates)
    print("✅ Configuration updated")
    
    # Get info
    info = config_manager.get_config_info()
    print(f"✅ Config info: {info['environment']}")
    
    print("🚀 Configuration Manager test completed!")

if __name__ == "__main__":
    test_configuration_manager()
