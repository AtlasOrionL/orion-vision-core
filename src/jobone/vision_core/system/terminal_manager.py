#!/usr/bin/env python3
"""
Terminal Manager - Safe Terminal Command Execution
Sprint 8.3 - Basic Computer Management and First Autonomous Task
Orion Vision Core - Autonomous AI Operating System

This module provides safe terminal command execution with sandboxing,
permission management, and comprehensive logging for the Orion Vision Core
autonomous AI operating system.

Author: Orion Development Team
Version: 8.3.0
Date: 30 Mayıs 2025
"""

import logging
import subprocess
import shlex
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QThread, pyqtSlot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TerminalManager")

class CommandSafety(Enum):
    """Command safety level enumeration"""
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"
    FORBIDDEN = "forbidden"

class ExecutionStatus(Enum):
    """Command execution status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    FORBIDDEN = "forbidden"

@dataclass
class CommandResult:
    """Command execution result"""
    command_id: str
    command: str
    status: ExecutionStatus
    return_code: Optional[int]
    stdout: str
    stderr: str
    execution_time: float
    timestamp: datetime
    safety_level: CommandSafety
    working_directory: str

class CommandExecutor(QThread):
    """Background command executor thread"""
    
    # Signals
    command_started = pyqtSignal(str)  # command_id
    command_finished = pyqtSignal(str, dict)  # command_id, result
    command_output = pyqtSignal(str, str, str)  # command_id, output_type, data
    
    def __init__(self, command_id: str, command: str, working_dir: str, timeout: int = 30):
        super().__init__()
        self.command_id = command_id
        self.command = command
        self.working_dir = working_dir
        self.timeout = timeout
        self.process = None
        self.cancelled = False
    
    def run(self):
        """Execute command in background thread"""
        try:
            self.command_started.emit(self.command_id)
            
            start_time = time.time()
            
            # Execute command
            self.process = subprocess.Popen(
                shlex.split(self.command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.working_dir,
                env=os.environ.copy()
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = self.process.communicate(timeout=self.timeout)
                return_code = self.process.returncode
                status = ExecutionStatus.COMPLETED if return_code == 0 else ExecutionStatus.FAILED
                
            except subprocess.TimeoutExpired:
                self.process.kill()
                stdout, stderr = self.process.communicate()
                return_code = -1
                status = ExecutionStatus.TIMEOUT
                
            except Exception as e:
                stdout, stderr = "", str(e)
                return_code = -1
                status = ExecutionStatus.FAILED
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Create result
            result = {
                'command_id': self.command_id,
                'command': self.command,
                'status': status.value,
                'return_code': return_code,
                'stdout': stdout,
                'stderr': stderr,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat(),
                'working_directory': self.working_dir
            }
            
            if not self.cancelled:
                self.command_finished.emit(self.command_id, result)
                
        except Exception as e:
            logger.error(f"❌ Error executing command {self.command_id}: {e}")
            error_result = {
                'command_id': self.command_id,
                'command': self.command,
                'status': ExecutionStatus.FAILED.value,
                'return_code': -1,
                'stdout': '',
                'stderr': str(e),
                'execution_time': 0.0,
                'timestamp': datetime.now().isoformat(),
                'working_directory': self.working_dir
            }
            if not self.cancelled:
                self.command_finished.emit(self.command_id, error_result)
    
    def cancel(self):
        """Cancel command execution"""
        self.cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
            time.sleep(1)
            if self.process.poll() is None:
                self.process.kill()

class TerminalManager(QObject):
    """
    Safe terminal command execution manager.
    
    Features:
    - Command safety classification
    - Sandboxed execution environment
    - Permission-based access control
    - Comprehensive logging and monitoring
    - Background execution with timeout
    - Command history and analytics
    """
    
    # Signals
    command_executed = pyqtSignal(dict)  # CommandResult as dict
    command_blocked = pyqtSignal(str, str)  # command, reason
    safety_violation = pyqtSignal(str, str)  # command, violation_type
    execution_stats_updated = pyqtSignal(dict)  # execution statistics
    
    def __init__(self):
        """Initialize Terminal Manager"""
        super().__init__()
        
        # Safety configuration
        self.safe_commands = {
            # File operations
            'ls', 'dir', 'cat', 'head', 'tail', 'less', 'more', 'file', 'stat',
            'find', 'locate', 'which', 'whereis', 'pwd', 'basename', 'dirname',
            
            # System information
            'ps', 'top', 'htop', 'free', 'df', 'du', 'lscpu', 'lsblk', 'lsusb',
            'uname', 'whoami', 'id', 'groups', 'uptime', 'date', 'cal',
            
            # Network (read-only)
            'ping', 'traceroute', 'nslookup', 'dig', 'host', 'netstat', 'ss',
            
            # Text processing
            'grep', 'awk', 'sed', 'sort', 'uniq', 'wc', 'cut', 'tr', 'tee',
            
            # Archive operations (read-only)
            'tar', 'zip', 'unzip', 'gzip', 'gunzip',
            
            # Development tools (read-only)
            'git status', 'git log', 'git diff', 'git branch', 'python --version',
            'node --version', 'npm --version', 'pip list', 'pip show'
        }
        
        self.moderate_commands = {
            # File operations with modification
            'touch', 'mkdir', 'cp', 'mv', 'ln', 'chmod', 'chown',
            
            # Text editors
            'nano', 'vim', 'emacs', 'gedit',
            
            # Package management (with confirmation)
            'apt list', 'apt search', 'apt show', 'yum list', 'dnf list',
            
            # Development operations
            'git add', 'git commit', 'git push', 'git pull', 'npm install',
            'pip install', 'python', 'node', 'npm run'
        }
        
        self.dangerous_commands = {
            # System modification
            'rm', 'rmdir', 'dd', 'fdisk', 'mkfs', 'mount', 'umount',
            'systemctl', 'service', 'crontab', 'at',
            
            # Network operations
            'wget', 'curl', 'ssh', 'scp', 'rsync', 'ftp', 'sftp',
            
            # Package management
            'apt install', 'apt remove', 'apt update', 'apt upgrade',
            'yum install', 'dnf install', 'pip uninstall',
            
            # Process management
            'kill', 'killall', 'pkill', 'nohup'
        }
        
        self.forbidden_commands = {
            # System destruction
            'rm -rf /', 'mkfs', 'dd if=/dev/zero', 'format', 'fdisk',
            
            # Security risks
            'sudo su', 'su -', 'passwd', 'useradd', 'userdel', 'usermod',
            
            # Network security
            'nc', 'netcat', 'telnet', 'nmap', 'wireshark',
            
            # System shutdown
            'shutdown', 'reboot', 'halt', 'poweroff', 'init 0', 'init 6'
        }
        
        # Execution configuration
        self.max_concurrent_commands = 5
        self.default_timeout = 30
        self.max_output_size = 1024 * 1024  # 1MB
        self.allowed_working_dirs = [
            os.path.expanduser("~"),
            "/tmp",
            "/var/tmp",
            os.getcwd()
        ]
        
        # State management
        self.active_executors: Dict[str, CommandExecutor] = {}
        self.command_history: List[CommandResult] = []
        self.execution_stats = {
            'total_commands': 0,
            'successful_commands': 0,
            'failed_commands': 0,
            'blocked_commands': 0,
            'average_execution_time': 0.0,
            'commands_by_safety': {
                'safe': 0,
                'moderate': 0,
                'dangerous': 0,
                'forbidden': 0
            }
        }
        self.command_counter = 0
        
        # Monitoring
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_finished_executors)
        self.cleanup_timer.start(5000)  # Cleanup every 5 seconds
        
        logger.info("🖥️ Terminal Manager initialized")
    
    def execute_command(self, command: str, 
                       working_dir: Optional[str] = None,
                       timeout: int = None,
                       force_execution: bool = False) -> Optional[str]:
        """
        Execute terminal command safely.
        
        Args:
            command: Command to execute
            working_dir: Working directory (optional)
            timeout: Execution timeout in seconds
            force_execution: Force execution of moderate/dangerous commands
            
        Returns:
            Command ID if execution started, None if blocked
        """
        try:
            # Validate inputs
            if not command or not command.strip():
                logger.warning("⚠️ Empty command provided")
                return None
            
            command = command.strip()
            
            # Set defaults
            if working_dir is None:
                working_dir = os.getcwd()
            if timeout is None:
                timeout = self.default_timeout
            
            # Validate working directory
            if not self._is_allowed_working_dir(working_dir):
                reason = f"Working directory not allowed: {working_dir}"
                logger.warning(f"⚠️ {reason}")
                self.command_blocked.emit(command, reason)
                return None
            
            # Check concurrent command limit
            if len(self.active_executors) >= self.max_concurrent_commands:
                reason = f"Maximum concurrent commands ({self.max_concurrent_commands}) reached"
                logger.warning(f"⚠️ {reason}")
                self.command_blocked.emit(command, reason)
                return None
            
            # Classify command safety
            safety_level = self._classify_command_safety(command)
            
            # Check if command is allowed
            if not self._is_command_allowed(command, safety_level, force_execution):
                reason = f"Command blocked due to safety level: {safety_level.value}"
                logger.warning(f"⚠️ Command blocked: {command} ({reason})")
                self.command_blocked.emit(command, reason)
                self.safety_violation.emit(command, safety_level.value)
                self._update_stats('blocked')
                return None
            
            # Generate command ID
            command_id = self._generate_command_id()
            
            # Create and start executor
            executor = CommandExecutor(command_id, command, working_dir, timeout)
            executor.command_finished.connect(self._on_command_finished)
            
            self.active_executors[command_id] = executor
            executor.start()
            
            logger.info(f"🖥️ Executing command: {command} (ID: {command_id}, Safety: {safety_level.value})")
            return command_id
            
        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            return None
    
    def _classify_command_safety(self, command: str) -> CommandSafety:
        """Classify command safety level"""
        command_lower = command.lower().strip()
        
        # Check forbidden commands first
        for forbidden in self.forbidden_commands:
            if forbidden in command_lower:
                return CommandSafety.FORBIDDEN
        
        # Check dangerous commands
        for dangerous in self.dangerous_commands:
            if command_lower.startswith(dangerous.lower()):
                return CommandSafety.DANGEROUS
        
        # Check moderate commands
        for moderate in self.moderate_commands:
            if command_lower.startswith(moderate.lower()):
                return CommandSafety.MODERATE
        
        # Check safe commands
        for safe in self.safe_commands:
            if command_lower.startswith(safe.lower()):
                return CommandSafety.SAFE
        
        # Unknown commands are considered dangerous by default
        return CommandSafety.DANGEROUS
    
    def _is_command_allowed(self, command: str, safety_level: CommandSafety, 
                           force_execution: bool) -> bool:
        """Check if command is allowed to execute"""
        if safety_level == CommandSafety.FORBIDDEN:
            return False
        
        if safety_level == CommandSafety.SAFE:
            return True
        
        if safety_level in [CommandSafety.MODERATE, CommandSafety.DANGEROUS]:
            return force_execution
        
        return False
    
    def _is_allowed_working_dir(self, working_dir: str) -> bool:
        """Check if working directory is allowed"""
        try:
            abs_working_dir = os.path.abspath(working_dir)
            
            for allowed_dir in self.allowed_working_dirs:
                abs_allowed_dir = os.path.abspath(allowed_dir)
                if abs_working_dir.startswith(abs_allowed_dir):
                    return True
            
            return False
            
        except Exception:
            return False
    
    @pyqtSlot(str, dict)
    def _on_command_finished(self, command_id: str, result_dict: dict):
        """Handle command completion"""
        try:
            # Remove from active executors
            if command_id in self.active_executors:
                del self.active_executors[command_id]
            
            # Create CommandResult
            result = CommandResult(
                command_id=result_dict['command_id'],
                command=result_dict['command'],
                status=ExecutionStatus(result_dict['status']),
                return_code=result_dict['return_code'],
                stdout=result_dict['stdout'],
                stderr=result_dict['stderr'],
                execution_time=result_dict['execution_time'],
                timestamp=datetime.fromisoformat(result_dict['timestamp']),
                safety_level=self._classify_command_safety(result_dict['command']),
                working_directory=result_dict['working_directory']
            )
            
            # Add to history
            self.command_history.append(result)
            if len(self.command_history) > 1000:  # Keep last 1000 commands
                self.command_history.pop(0)
            
            # Update statistics
            if result.status == ExecutionStatus.COMPLETED:
                self._update_stats('success', result.execution_time)
            else:
                self._update_stats('failed')
            
            # Emit signal
            self.command_executed.emit(self._command_result_to_dict(result))
            
            logger.info(f"🖥️ Command completed: {command_id} (Status: {result.status.value})")
            
        except Exception as e:
            logger.error(f"❌ Error handling command completion: {e}")
    
    def _cleanup_finished_executors(self):
        """Clean up finished executor threads"""
        finished_executors = []
        
        for command_id, executor in self.active_executors.items():
            if executor.isFinished():
                finished_executors.append(command_id)
        
        for command_id in finished_executors:
            executor = self.active_executors.pop(command_id)
            executor.deleteLater()
    
    def _generate_command_id(self) -> str:
        """Generate unique command ID"""
        self.command_counter += 1
        return f"cmd_{self.command_counter:06d}"
    
    def _update_stats(self, result_type: str, execution_time: float = 0.0):
        """Update execution statistics"""
        self.execution_stats['total_commands'] += 1
        
        if result_type == 'success':
            self.execution_stats['successful_commands'] += 1
        elif result_type == 'failed':
            self.execution_stats['failed_commands'] += 1
        elif result_type == 'blocked':
            self.execution_stats['blocked_commands'] += 1
        
        # Update average execution time
        if result_type == 'success' and execution_time > 0:
            total_time = (self.execution_stats['average_execution_time'] * 
                         (self.execution_stats['successful_commands'] - 1) + execution_time)
            self.execution_stats['average_execution_time'] = total_time / self.execution_stats['successful_commands']
        
        # Emit stats update
        self.execution_stats_updated.emit(self.execution_stats.copy())
    
    def _command_result_to_dict(self, result: CommandResult) -> dict:
        """Convert CommandResult to dictionary"""
        return {
            'command_id': result.command_id,
            'command': result.command,
            'status': result.status.value,
            'return_code': result.return_code,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'execution_time': result.execution_time,
            'timestamp': result.timestamp.isoformat(),
            'safety_level': result.safety_level.value,
            'working_directory': result.working_directory
        }
    
    def cancel_command(self, command_id: str) -> bool:
        """Cancel running command"""
        try:
            if command_id in self.active_executors:
                executor = self.active_executors[command_id]
                executor.cancel()
                logger.info(f"🖥️ Command cancelled: {command_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Error cancelling command: {e}")
            return False
    
    def get_command_history(self, limit: int = 100) -> List[dict]:
        """Get command execution history"""
        history = self.command_history[-limit:] if limit > 0 else self.command_history
        return [self._command_result_to_dict(result) for result in history]
    
    def get_active_commands(self) -> List[str]:
        """Get list of active command IDs"""
        return list(self.active_executors.keys())
    
    def get_execution_stats(self) -> dict:
        """Get execution statistics"""
        return self.execution_stats.copy()
    
    def add_safe_command(self, command: str):
        """Add command to safe commands list"""
        self.safe_commands.add(command.lower())
        logger.info(f"🖥️ Added safe command: {command}")
    
    def remove_safe_command(self, command: str):
        """Remove command from safe commands list"""
        self.safe_commands.discard(command.lower())
        logger.info(f"🖥️ Removed safe command: {command}")
    
    def get_safety_info(self) -> dict:
        """Get command safety configuration"""
        return {
            'safe_commands': sorted(list(self.safe_commands)),
            'moderate_commands': sorted(list(self.moderate_commands)),
            'dangerous_commands': sorted(list(self.dangerous_commands)),
            'forbidden_commands': sorted(list(self.forbidden_commands)),
            'allowed_working_dirs': self.allowed_working_dirs,
            'max_concurrent_commands': self.max_concurrent_commands,
            'default_timeout': self.default_timeout
        }

# Singleton instance
_terminal_manager = None

def get_terminal_manager() -> TerminalManager:
    """Get the singleton Terminal Manager instance"""
    global _terminal_manager
    if _terminal_manager is None:
        _terminal_manager = TerminalManager()
    return _terminal_manager
