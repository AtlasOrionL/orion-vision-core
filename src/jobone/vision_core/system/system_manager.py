#!/usr/bin/env python3
"""
System Manager - Core System Management
Sprint 8.3 - Basic Computer Management and First Autonomous Task
Orion Vision Core - Autonomous AI Operating System

This module provides core system management capabilities including
system information, process management, and system operations
for the Orion Vision Core autonomous AI operating system.

Author: Orion Development Team
Version: 8.3.0
Date: 30 Mayıs 2025
"""

import os
import sys
import platform
import psutil
import logging
import subprocess
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SystemManager")

class SystemStatus(Enum):
    """System status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

@dataclass
class SystemInfo:
    """System information data"""
    platform: str
    platform_version: str
    python_version: str
    cpu_count: int
    memory_total: int
    disk_total: int
    uptime: float
    timestamp: datetime

class SystemManager:
    """
    Core system management for Orion Vision Core.
    
    This class provides comprehensive system management capabilities
    including system information, process management, and system operations.
    """
    
    def __init__(self):
        """Initialize System Manager"""
        self.version = "8.3.0"
        self.start_time = datetime.now()
        
        # System information
        self.platform_info = self._get_platform_info()
        self.system_status = SystemStatus.HEALTHY
        
        # Statistics
        self.stats = {
            'operations_count': 0,
            'commands_executed': 0,
            'files_managed': 0,
            'processes_monitored': 0
        }
        
        logger.info(f"🖥️ System Manager v{self.version} initialized")
    
    def _get_platform_info(self) -> Dict[str, Any]:
        """Get platform information"""
        try:
            return {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': sys.version,
                'python_executable': sys.executable
            }
        except Exception as e:
            logger.error(f"❌ Error getting platform info: {e}")
            return {}
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information"""
        try:
            # CPU information
            cpu_info = {
                'count': psutil.cpu_count(),
                'count_logical': psutil.cpu_count(logical=True),
                'usage_percent': psutil.cpu_percent(interval=1),
                'frequency': psutil.cpu_freq()._asdict() if psutil.cpu_freq() else None
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percentage': memory.percent
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                'total': disk.total,
                'used': disk.used,
                'free': disk.free,
                'percentage': (disk.used / disk.total) * 100
            }
            
            # Network information
            network = psutil.net_io_counters()
            network_info = {
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv,
                'packets_sent': network.packets_sent,
                'packets_recv': network.packets_recv
            }
            
            # Process information
            process_info = {
                'count': len(psutil.pids()),
                'current_pid': os.getpid(),
                'parent_pid': os.getppid()
            }
            
            # Uptime
            uptime = datetime.now() - self.start_time
            
            return {
                'platform': self.platform_info,
                'cpu': cpu_info,
                'memory': memory_info,
                'disk': disk_info,
                'network': network_info,
                'processes': process_info,
                'uptime': uptime.total_seconds(),
                'status': self.system_status.value,
                'timestamp': datetime.now().isoformat(),
                'version': self.version
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting system info: {e}")
            return {'error': str(e)}
    
    def execute_command(self, command: str, shell: bool = True, 
                       timeout: int = 30) -> Dict[str, Any]:
        """Execute system command safely"""
        try:
            logger.info(f"🔧 Executing command: {command}")
            
            # Security check - basic command validation
            if not self._is_safe_command(command):
                return {
                    'success': False,
                    'error': 'Command not allowed for security reasons',
                    'output': '',
                    'return_code': -1
                }
            
            # Execute command
            result = subprocess.run(
                command,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            self.stats['commands_executed'] += 1
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode,
                'command': command
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timeout: {command}")
            return {
                'success': False,
                'error': 'Command timed out',
                'output': '',
                'return_code': -1
            }
        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': '',
                'return_code': -1
            }
    
    def _is_safe_command(self, command: str) -> bool:
        """Check if command is safe to execute"""
        # Basic security checks
        dangerous_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk',
            'shutdown', 'reboot', 'halt', 'poweroff',
            'passwd', 'sudo su', 'chmod 777'
        ]
        
        command_lower = command.lower()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return False
        
        return True
    
    def get_process_list(self) -> List[Dict[str, Any]]:
        """Get list of running processes"""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.stats['processes_monitored'] = len(processes)
            return processes
            
        except Exception as e:
            logger.error(f"❌ Error getting process list: {e}")
            return []
    
    def monitor_system_health(self) -> SystemStatus:
        """Monitor system health and return status"""
        try:
            # Check CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Check memory usage
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # Check disk usage
            disk = psutil.disk_usage('/')
            disk_usage = (disk.used / disk.total) * 100
            
            # Determine system status
            if cpu_usage > 90 or memory_usage > 95 or disk_usage > 95:
                self.system_status = SystemStatus.CRITICAL
            elif cpu_usage > 80 or memory_usage > 85 or disk_usage > 85:
                self.system_status = SystemStatus.WARNING
            else:
                self.system_status = SystemStatus.HEALTHY
            
            return self.system_status
            
        except Exception as e:
            logger.error(f"❌ Error monitoring system health: {e}")
            self.system_status = SystemStatus.UNKNOWN
            return self.system_status
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system manager statistics"""
        return {
            'version': self.version,
            'uptime': (datetime.now() - self.start_time).total_seconds(),
            'status': self.system_status.value,
            'statistics': self.stats.copy(),
            'platform': self.platform_info
        }

# Singleton instance
_system_manager = None

def get_system_manager() -> SystemManager:
    """Get the singleton System Manager instance"""
    global _system_manager
    if _system_manager is None:
        _system_manager = SystemManager()
    return _system_manager

def get_system_info() -> Dict[str, Any]:
    """Get system module information"""
    return {
        'module': 'orion_vision_core.system',
        'version': '8.3.0',
        'author': 'Orion Development Team',
        'status': 'Production Ready',
        'features': [
            'System information gathering',
            'Safe command execution',
            'Process monitoring',
            'System health monitoring',
            'Platform detection',
            'Resource usage tracking',
            'Security validation',
            'Statistics collection'
        ]
    }
