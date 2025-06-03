#!/usr/bin/env python3
"""
🎮 Configuration Manager - Gaming AI

Dynamic configuration management with runtime updates and validation.

Sprint 1 - Task 1.5: Configuration System
- Enhanced JSON configuration
- Runtime configuration updates
- Configuration validation
- Dynamic loading without restart

Author: Nexus - Quantum AI Architect
"""

import json
import os
import time
import threading
import logging
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
import warnings

@dataclass
class ConfigValidationRule:
    """Configuration validation rule"""
    field_path: str
    rule_type: str  # 'range', 'choices', 'type', 'custom'
    parameters: Dict[str, Any]
    error_message: str

class ConfigManager:
    """
    Dynamic Configuration Manager for Gaming AI
    
    Features:
    - Runtime configuration updates
    - Configuration validation
    - Change notifications
    - Backup and restore
    - Environment-specific configs
    """
    
    def __init__(self, config_file: str = "gaming_config.json"):
        self.config_file = Path(config_file)
        self.logger = logging.getLogger("ConfigManager")
        
        # Configuration data
        self.config = {}
        self.default_config = {}
        self.validation_rules = []
        
        # Change tracking
        self.change_callbacks = []
        self.last_modified = 0
        self.config_lock = threading.RLock()
        
        # File watching
        self.watch_thread = None
        self.watching = False
        
        # Initialize
        self._load_default_config()
        self._setup_validation_rules()
        self.load_config()
        
        self.logger.info(f"🎮 Configuration Manager initialized: {self.config_file}")
    
    def _load_default_config(self):
        """Load default configuration"""
        self.default_config = {
            "gaming_ai_config": {
                "version": "1.0.0",
                "experimental": True,
                "description": "Gaming AI Configuration"
            },
            "vision_settings": {
                "target_fps": 60,
                "detection_threshold": 0.7,
                "enable_yolo": True,
                "enable_ocr": True,
                "enable_color_detection": True,
                "max_detections": 100
            },
            "ocr_settings": {
                "languages": ["en", "tr"],
                "confidence_threshold": 0.6,
                "enable_preprocessing": True,
                "enable_multiple_engines": True,
                "gaming_font_optimization": True
            },
            "capture_settings": {
                "target_fps": 60,
                "max_memory_mb": 100,
                "enable_compression": True,
                "compression_quality": 85,
                "capture_method": "auto"
            },
            "control_settings": {
                "mouse_precision": "high",
                "keyboard_delay": 50,
                "action_delay": 0.05,
                "max_actions_per_second": 20,
                "safety_mode": True
            },
            "ai_settings": {
                "assistance_level": 0.3,
                "control_mode": "assistance",
                "enable_quantum_decisions": True,
                "quantum_randomness": 0.2,
                "learning_enabled": True
            },
            "safety_settings": {
                "rate_limiting": True,
                "human_verification_interval": 300,
                "anti_detection_enabled": True,
                "respect_game_tos": True,
                "ethical_gaming_mode": True
            },
            "performance_settings": {
                "gpu_acceleration": True,
                "memory_limit_mb": 1024,
                "cpu_threads": 4,
                "optimization_level": "balanced"
            }
        }
    
    def _setup_validation_rules(self):
        """Setup configuration validation rules"""
        self.validation_rules = [
            # Vision settings
            ConfigValidationRule(
                "vision_settings.target_fps",
                "range",
                {"min": 1, "max": 120},
                "FPS must be between 1 and 120"
            ),
            ConfigValidationRule(
                "vision_settings.detection_threshold",
                "range",
                {"min": 0.1, "max": 1.0},
                "Detection threshold must be between 0.1 and 1.0"
            ),
            
            # OCR settings
            ConfigValidationRule(
                "ocr_settings.confidence_threshold",
                "range",
                {"min": 0.1, "max": 1.0},
                "OCR confidence threshold must be between 0.1 and 1.0"
            ),
            ConfigValidationRule(
                "ocr_settings.languages",
                "type",
                {"expected_type": list},
                "Languages must be a list"
            ),
            
            # Capture settings
            ConfigValidationRule(
                "capture_settings.max_memory_mb",
                "range",
                {"min": 50, "max": 2048},
                "Memory limit must be between 50MB and 2GB"
            ),
            ConfigValidationRule(
                "capture_settings.capture_method",
                "choices",
                {"choices": ["auto", "pil", "win32", "xlib"]},
                "Capture method must be one of: auto, pil, win32, xlib"
            ),
            
            # Control settings
            ConfigValidationRule(
                "control_settings.max_actions_per_second",
                "range",
                {"min": 1, "max": 100},
                "Max actions per second must be between 1 and 100"
            ),
            ConfigValidationRule(
                "control_settings.mouse_precision",
                "choices",
                {"choices": ["low", "medium", "high", "ultra"]},
                "Mouse precision must be: low, medium, high, or ultra"
            ),
            
            # AI settings
            ConfigValidationRule(
                "ai_settings.assistance_level",
                "range",
                {"min": 0.0, "max": 1.0},
                "Assistance level must be between 0.0 and 1.0"
            ),
            ConfigValidationRule(
                "ai_settings.control_mode",
                "choices",
                {"choices": ["assistance", "ai", "shared"]},
                "Control mode must be: assistance, ai, or shared"
            )
        ]
    
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            with self.config_lock:
                if self.config_file.exists():
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded_config = json.load(f)
                    
                    # Merge with defaults
                    self.config = self._merge_configs(self.default_config, loaded_config)
                    
                    # Validate configuration
                    validation_errors = self.validate_config()
                    if validation_errors:
                        self.logger.warning(f"🎮 Configuration validation warnings: {validation_errors}")
                    
                    self.last_modified = self.config_file.stat().st_mtime
                    self.logger.info("✅ Configuration loaded successfully")
                    
                else:
                    # Create default config file
                    self.config = self.default_config.copy()
                    self.save_config()
                    self.logger.info("📄 Created default configuration file")
                
                # Notify callbacks
                self._notify_change_callbacks("config_loaded", self.config)
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to load configuration: {e}")
            self.config = self.default_config.copy()
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with self.config_lock:
                # Create backup
                self._create_backup()
                
                # Save configuration
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                
                self.last_modified = self.config_file.stat().st_mtime
                self.logger.info("✅ Configuration saved successfully")
                
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to save configuration: {e}")
            return False
    
    def get_config(self, path: Optional[str] = None) -> Any:
        """Get configuration value by path"""
        with self.config_lock:
            if path is None:
                return self.config.copy()
            
            # Navigate to nested value
            keys = path.split('.')
            value = self.config
            
            try:
                for key in keys:
                    value = value[key]
                return value
            except (KeyError, TypeError):
                # Return default value if path doesn't exist
                default_value = self.default_config
                try:
                    for key in keys:
                        default_value = default_value[key]
                    return default_value
                except (KeyError, TypeError):
                    return None
    
    def set_config(self, path: str, value: Any, save: bool = True) -> bool:
        """Set configuration value by path"""
        try:
            with self.config_lock:
                # Navigate to parent and set value
                keys = path.split('.')
                config_ref = self.config
                
                # Navigate to parent
                for key in keys[:-1]:
                    if key not in config_ref:
                        config_ref[key] = {}
                    config_ref = config_ref[key]
                
                # Set final value
                old_value = config_ref.get(keys[-1])
                config_ref[keys[-1]] = value
                
                # Validate change
                validation_errors = self.validate_config()
                if validation_errors:
                    # Revert change
                    if old_value is not None:
                        config_ref[keys[-1]] = old_value
                    else:
                        del config_ref[keys[-1]]
                    
                    self.logger.error(f"❌ Configuration validation failed: {validation_errors}")
                    return False
                
                # Save if requested
                if save:
                    self.save_config()
                
                # Notify callbacks
                self._notify_change_callbacks("config_changed", {
                    "path": path,
                    "old_value": old_value,
                    "new_value": value
                })
                
                self.logger.info(f"✅ Configuration updated: {path} = {value}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to set configuration: {e}")
            return False
    
    def validate_config(self) -> List[str]:
        """Validate current configuration"""
        errors = []
        
        for rule in self.validation_rules:
            try:
                value = self.get_config(rule.field_path)
                
                if value is None:
                    continue  # Skip validation for missing optional fields
                
                if rule.rule_type == "range":
                    min_val = rule.parameters.get("min")
                    max_val = rule.parameters.get("max")
                    if not (min_val <= value <= max_val):
                        errors.append(f"{rule.field_path}: {rule.error_message}")
                
                elif rule.rule_type == "choices":
                    choices = rule.parameters.get("choices", [])
                    if value not in choices:
                        errors.append(f"{rule.field_path}: {rule.error_message}")
                
                elif rule.rule_type == "type":
                    expected_type = rule.parameters.get("expected_type")
                    if not isinstance(value, expected_type):
                        errors.append(f"{rule.field_path}: {rule.error_message}")
                
            except Exception as e:
                errors.append(f"{rule.field_path}: Validation error - {e}")
        
        return errors
    
    def add_change_callback(self, callback: Callable[[str, Any], None]):
        """Add configuration change callback"""
        self.change_callbacks.append(callback)
    
    def remove_change_callback(self, callback: Callable[[str, Any], None]):
        """Remove configuration change callback"""
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def _notify_change_callbacks(self, change_type: str, data: Any):
        """Notify all change callbacks"""
        for callback in self.change_callbacks:
            try:
                callback(change_type, data)
            except Exception as e:
                self.logger.error(f"❌ Callback error: {e}")
    
    def start_file_watching(self):
        """Start watching configuration file for changes"""
        if self.watching:
            return
        
        self.watching = True
        self.watch_thread = threading.Thread(target=self._file_watch_loop, daemon=True)
        self.watch_thread.start()
        self.logger.info("👁️ Started configuration file watching")
    
    def stop_file_watching(self):
        """Stop watching configuration file"""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=1.0)
        self.logger.info("🛑 Stopped configuration file watching")
    
    def _file_watch_loop(self):
        """File watching loop"""
        while self.watching:
            try:
                if self.config_file.exists():
                    current_mtime = self.config_file.stat().st_mtime
                    
                    if current_mtime > self.last_modified:
                        self.logger.info("📄 Configuration file changed, reloading...")
                        self.load_config()
                
                time.sleep(1.0)  # Check every second
                
            except Exception as e:
                self.logger.error(f"❌ File watching error: {e}")
                time.sleep(5.0)  # Wait longer on error
    
    def _merge_configs(self, default: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded config with defaults"""
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _create_backup(self):
        """Create configuration backup"""
        try:
            if self.config_file.exists():
                backup_file = self.config_file.with_suffix('.json.backup')
                backup_file.write_text(self.config_file.read_text())
        except Exception as e:
            self.logger.warning(f"⚠️ Failed to create backup: {e}")
    
    def restore_backup(self) -> bool:
        """Restore configuration from backup"""
        try:
            backup_file = self.config_file.with_suffix('.json.backup')
            if backup_file.exists():
                self.config_file.write_text(backup_file.read_text())
                self.load_config()
                self.logger.info("✅ Configuration restored from backup")
                return True
            else:
                self.logger.warning("⚠️ No backup file found")
                return False
        except Exception as e:
            self.logger.error(f"❌ Failed to restore backup: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        try:
            with self.config_lock:
                self.config = self.default_config.copy()
                self.save_config()
                
                self._notify_change_callbacks("config_reset", self.config)
                self.logger.info("✅ Configuration reset to defaults")
                return True
        except Exception as e:
            self.logger.error(f"❌ Failed to reset configuration: {e}")
            return False
    
    def get_config_info(self) -> Dict[str, Any]:
        """Get configuration information"""
        return {
            "config_file": str(self.config_file),
            "file_exists": self.config_file.exists(),
            "last_modified": self.last_modified,
            "watching": self.watching,
            "validation_rules": len(self.validation_rules),
            "change_callbacks": len(self.change_callbacks),
            "config_size": len(json.dumps(self.config))
        }

# Global configuration manager instance
_config_manager = None

def get_config_manager(config_file: str = "gaming_config.json") -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_file)
    return _config_manager

# Convenience functions
def get_config(path: Optional[str] = None) -> Any:
    """Get configuration value"""
    return get_config_manager().get_config(path)

def set_config(path: str, value: Any, save: bool = True) -> bool:
    """Set configuration value"""
    return get_config_manager().set_config(path, value, save)

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 Configuration Manager - Sprint 1 Test")
    print("=" * 60)
    
    # Create configuration manager
    config_manager = ConfigManager("test_gaming_config.json")
    
    # Test configuration loading
    print("\n📄 Testing configuration loading...")
    vision_fps = config_manager.get_config("vision_settings.target_fps")
    print(f"✅ Vision FPS: {vision_fps}")
    
    # Test configuration setting
    print("\n⚙️ Testing configuration updates...")
    success = config_manager.set_config("vision_settings.target_fps", 30)
    print(f"✅ FPS update: {success}")
    
    # Test validation
    print("\n🔍 Testing validation...")
    config_manager.set_config("vision_settings.target_fps", 200, save=False)  # Should fail
    errors = config_manager.validate_config()
    print(f"✅ Validation errors: {len(errors)}")
    
    # Test file watching
    print("\n👁️ Testing file watching...")
    config_manager.start_file_watching()
    time.sleep(1)
    config_manager.stop_file_watching()
    print("✅ File watching test completed")
    
    # Configuration info
    info = config_manager.get_config_info()
    print(f"\n📊 Configuration Info:")
    for key, value in info.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 1 - Task 1.5 test completed!")
    print("🎯 Target: Dynamic config without restart")
    print("📈 Current: Runtime updates, validation, file watching implemented")
