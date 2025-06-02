#!/usr/bin/env python3
"""
Production Setup - Orion Vision Core Production Deployment
Sprint 8.8 - Final Integration and Production Readiness
Orion Vision Core - Autonomous AI Operating System

This module provides production deployment setup and configuration
for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.8.0
Date: 31 Mayıs 2025
"""

import os
import sys
import json
import shutil
import logging
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ProductionSetup")

class DeploymentType(Enum):
    """Deployment type enumeration"""
    STANDALONE = "standalone"
    SERVICE = "service"
    DOCKER = "docker"
    SYSTEMD = "systemd"

class Platform(Enum):
    """Platform enumeration"""
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"

@dataclass
class DeploymentConfig:
    """Deployment configuration"""
    deployment_type: DeploymentType
    platform: Platform
    install_path: str
    data_path: str
    log_path: str
    config_path: str
    enable_gui: bool = True
    enable_voice: bool = True
    enable_dashboard: bool = True
    enable_automation: bool = True
    enable_workflows: bool = True
    auto_start: bool = False
    service_name: str = "orion-vision-core"

class ProductionSetup:
    """
    Production deployment setup for Orion Vision Core.
    
    This class handles the complete production deployment process including
    installation, configuration, service setup, and system integration.
    """
    
    def __init__(self):
        """Initialize production setup"""
        self.version = "8.8.0"
        self.current_platform = self._detect_platform()
        self.setup_complete = False
        
        # Default paths
        self.default_paths = self._get_default_paths()
        
        logger.info(f"🚀 Orion Production Setup v{self.version}")
        logger.info(f"🖥️ Platform: {self.current_platform.value}")
    
    def setup_production_environment(self, config: DeploymentConfig) -> bool:
        """Setup complete production environment"""
        try:
            logger.info("🔧 Setting up production environment...")
            
            # Create directory structure
            self._create_directory_structure(config)
            
            # Copy application files
            self._copy_application_files(config)
            
            # Create configuration files
            self._create_configuration_files(config)
            
            # Setup dependencies
            self._setup_dependencies(config)
            
            # Setup service (if applicable)
            if config.deployment_type in [DeploymentType.SERVICE, DeploymentType.SYSTEMD]:
                self._setup_service(config)
            
            # Setup desktop integration
            if config.enable_gui:
                self._setup_desktop_integration(config)
            
            # Create startup scripts
            self._create_startup_scripts(config)
            
            # Validate installation
            self._validate_installation(config)
            
            self.setup_complete = True
            logger.info("✅ Production environment setup complete")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error setting up production environment: {e}")
            return False
    
    def _detect_platform(self) -> Platform:
        """Detect current platform"""
        system = platform.system().lower()
        if system == "windows":
            return Platform.WINDOWS
        elif system == "linux":
            return Platform.LINUX
        elif system == "darwin":
            return Platform.MACOS
        else:
            logger.warning(f"Unknown platform: {system}, defaulting to Linux")
            return Platform.LINUX
    
    def _get_default_paths(self) -> Dict[str, str]:
        """Get default installation paths for current platform"""
        if self.current_platform == Platform.WINDOWS:
            return {
                'install': 'C:\\Program Files\\Orion Vision Core',
                'data': os.path.expanduser('~\\AppData\\Local\\Orion Vision Core'),
                'config': os.path.expanduser('~\\AppData\\Local\\Orion Vision Core\\config'),
                'logs': os.path.expanduser('~\\AppData\\Local\\Orion Vision Core\\logs')
            }
        elif self.current_platform == Platform.MACOS:
            return {
                'install': '/Applications/Orion Vision Core',
                'data': os.path.expanduser('~/Library/Application Support/Orion Vision Core'),
                'config': os.path.expanduser('~/Library/Application Support/Orion Vision Core/config'),
                'logs': os.path.expanduser('~/Library/Logs/Orion Vision Core')
            }
        else:  # Linux
            return {
                'install': '/opt/orion-vision-core',
                'data': os.path.expanduser('~/.local/share/orion-vision-core'),
                'config': os.path.expanduser('~/.config/orion-vision-core'),
                'logs': os.path.expanduser('~/.local/share/orion-vision-core/logs')
            }
    
    def _create_directory_structure(self, config: DeploymentConfig):
        """Create directory structure"""
        logger.info("📁 Creating directory structure...")
        
        directories = [
            config.install_path,
            config.data_path,
            config.config_path,
            config.log_path,
            os.path.join(config.install_path, 'bin'),
            os.path.join(config.install_path, 'lib'),
            os.path.join(config.install_path, 'share'),
            os.path.join(config.data_path, 'workflows'),
            os.path.join(config.data_path, 'tasks'),
            os.path.join(config.data_path, 'cache')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"📁 Created: {directory}")
    
    def _copy_application_files(self, config: DeploymentConfig):
        """Copy application files to installation directory"""
        logger.info("📋 Copying application files...")
        
        # Get source directory
        current_dir = Path(__file__).parent.parent
        src_dir = current_dir
        
        # Copy main application files
        lib_dir = os.path.join(config.install_path, 'lib')
        
        # Copy source code
        if src_dir.exists():
            dest_src = os.path.join(lib_dir, 'jobone')
            if os.path.exists(dest_src):
                shutil.rmtree(dest_src)
            shutil.copytree(src_dir, dest_src)
            logger.info(f"📋 Copied source code to {dest_src}")
        
        # Copy main executable
        main_script = current_dir / 'orion_main.py'
        if main_script.exists():
            dest_main = os.path.join(config.install_path, 'bin', 'orion_main.py')
            shutil.copy2(main_script, dest_main)
            logger.info(f"📋 Copied main script to {dest_main}")
    
    def _create_configuration_files(self, config: DeploymentConfig):
        """Create configuration files"""
        logger.info("⚙️ Creating configuration files...")
        
        # Main configuration
        main_config = {
            'version': self.version,
            'deployment_type': config.deployment_type.value,
            'platform': config.platform.value,
            'paths': {
                'install': config.install_path,
                'data': config.data_path,
                'config': config.config_path,
                'logs': config.log_path
            },
            'features': {
                'gui': config.enable_gui,
                'voice': config.enable_voice,
                'dashboard': config.enable_dashboard,
                'automation': config.enable_automation,
                'workflows': config.enable_workflows
            },
            'service': {
                'auto_start': config.auto_start,
                'service_name': config.service_name
            }
        }
        
        config_file = os.path.join(config.config_path, 'orion.json')
        with open(config_file, 'w') as f:
            json.dump(main_config, f, indent=2)
        logger.info(f"⚙️ Created configuration: {config_file}")
        
        # Logging configuration
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'file': {
                    'class': 'logging.FileHandler',
                    'filename': os.path.join(config.log_path, 'orion.log'),
                    'formatter': 'standard',
                    'level': 'INFO'
                },
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'standard',
                    'level': 'INFO'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['file', 'console']
            }
        }
        
        logging_file = os.path.join(config.config_path, 'logging.json')
        with open(logging_file, 'w') as f:
            json.dump(logging_config, f, indent=2)
        logger.info(f"⚙️ Created logging config: {logging_file}")
    
    def _setup_dependencies(self, config: DeploymentConfig):
        """Setup dependencies"""
        logger.info("📦 Setting up dependencies...")
        
        # Create requirements file
        requirements = [
            'PyQt6>=6.0.0',
            'psutil>=5.8.0',
            'requests>=2.25.0',
            'aiohttp>=3.7.0',
            'numpy>=1.20.0',
            'pandas>=1.3.0'
        ]
        
        # Add optional dependencies
        if config.enable_voice:
            requirements.extend([
                'speechrecognition>=3.8.0',
                'pyttsx3>=2.90',
                'pyaudio>=0.2.11'
            ])
        
        requirements_file = os.path.join(config.install_path, 'requirements.txt')
        with open(requirements_file, 'w') as f:
            f.write('\n'.join(requirements))
        logger.info(f"📦 Created requirements: {requirements_file}")
    
    def _setup_service(self, config: DeploymentConfig):
        """Setup system service"""
        logger.info("⚙️ Setting up system service...")
        
        if config.platform == Platform.LINUX and config.deployment_type == DeploymentType.SYSTEMD:
            self._create_systemd_service(config)
        elif config.platform == Platform.WINDOWS:
            self._create_windows_service(config)
        elif config.platform == Platform.MACOS:
            self._create_launchd_service(config)
    
    def _create_systemd_service(self, config: DeploymentConfig):
        """Create systemd service file"""
        service_content = f"""[Unit]
Description=Orion Vision Core - Autonomous AI Operating System
After=network.target

[Service]
Type=simple
User=orion
Group=orion
WorkingDirectory={config.install_path}
Environment=PYTHONPATH={config.install_path}/lib
ExecStart=/usr/bin/python3 {config.install_path}/bin/orion_main.py --service
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
        
        service_file = f"/etc/systemd/system/{config.service_name}.service"
        try:
            with open(service_file, 'w') as f:
                f.write(service_content)
            logger.info(f"⚙️ Created systemd service: {service_file}")
        except PermissionError:
            logger.warning("⚠️ Cannot create systemd service (requires root)")
    
    def _create_windows_service(self, config: DeploymentConfig):
        """Create Windows service"""
        logger.info("⚙️ Windows service setup not implemented")
    
    def _create_launchd_service(self, config: DeploymentConfig):
        """Create macOS launchd service"""
        logger.info("⚙️ macOS launchd service setup not implemented")
    
    def _setup_desktop_integration(self, config: DeploymentConfig):
        """Setup desktop integration"""
        logger.info("🖥️ Setting up desktop integration...")
        
        if config.platform == Platform.LINUX:
            self._create_desktop_file(config)
        elif config.platform == Platform.WINDOWS:
            self._create_windows_shortcuts(config)
        elif config.platform == Platform.MACOS:
            self._create_macos_app_bundle(config)
    
    def _create_desktop_file(self, config: DeploymentConfig):
        """Create Linux desktop file"""
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=Orion Vision Core
Comment=Autonomous AI Operating System
Exec=python3 {config.install_path}/bin/orion_main.py
Icon={config.install_path}/share/orion.png
Terminal=false
Categories=Development;System;
"""
        
        desktop_file = os.path.expanduser('~/.local/share/applications/orion-vision-core.desktop')
        os.makedirs(os.path.dirname(desktop_file), exist_ok=True)
        
        with open(desktop_file, 'w') as f:
            f.write(desktop_content)
        
        # Make executable
        os.chmod(desktop_file, 0o755)
        logger.info(f"🖥️ Created desktop file: {desktop_file}")
    
    def _create_windows_shortcuts(self, config: DeploymentConfig):
        """Create Windows shortcuts"""
        logger.info("🖥️ Windows shortcuts setup not implemented")
    
    def _create_macos_app_bundle(self, config: DeploymentConfig):
        """Create macOS app bundle"""
        logger.info("🖥️ macOS app bundle setup not implemented")
    
    def _create_startup_scripts(self, config: DeploymentConfig):
        """Create startup scripts"""
        logger.info("📜 Creating startup scripts...")
        
        # Create main startup script
        if config.platform == Platform.WINDOWS:
            script_name = 'start_orion.bat'
            script_content = f"""@echo off
cd /d "{config.install_path}"
python bin\\orion_main.py %*
"""
        else:
            script_name = 'start_orion.sh'
            script_content = f"""#!/bin/bash
cd "{config.install_path}"
export PYTHONPATH="{config.install_path}/lib:$PYTHONPATH"
python3 bin/orion_main.py "$@"
"""
        
        script_path = os.path.join(config.install_path, script_name)
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make executable on Unix systems
        if config.platform != Platform.WINDOWS:
            os.chmod(script_path, 0o755)
        
        logger.info(f"📜 Created startup script: {script_path}")
    
    def _validate_installation(self, config: DeploymentConfig):
        """Validate installation"""
        logger.info("✅ Validating installation...")
        
        # Check required files
        required_files = [
            os.path.join(config.install_path, 'bin', 'orion_main.py'),
            os.path.join(config.config_path, 'orion.json'),
            os.path.join(config.install_path, 'requirements.txt')
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Required file missing: {file_path}")
        
        # Check directories
        required_dirs = [
            config.install_path,
            config.data_path,
            config.config_path,
            config.log_path
        ]
        
        for dir_path in required_dirs:
            if not os.path.exists(dir_path):
                raise FileNotFoundError(f"Required directory missing: {dir_path}")
        
        logger.info("✅ Installation validation complete")
    
    def get_deployment_info(self) -> Dict[str, Any]:
        """Get deployment information"""
        return {
            'version': self.version,
            'platform': self.current_platform.value,
            'default_paths': self.default_paths,
            'setup_complete': self.setup_complete,
            'supported_deployment_types': [dt.value for dt in DeploymentType],
            'supported_platforms': [p.value for p in Platform]
        }
