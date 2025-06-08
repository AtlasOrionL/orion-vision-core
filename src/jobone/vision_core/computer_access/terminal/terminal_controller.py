#!/usr/bin/env python3
"""
Terminal Controller - Main interface for terminal command execution
"""

import logging
import platform
import subprocess
import threading
import time
import queue
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class CommandStatus(Enum):
    """Command execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"

@dataclass
class CommandResult:
    """Command execution result"""
    command: str
    status: CommandStatus
    return_code: int
    stdout: str
    stderr: str
    execution_time: float
    timestamp: float

class TerminalController:
    """
    Main terminal controller for autonomous command execution
    Provides cross-platform terminal access with real-time output
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.terminal')
        self.platform = platform.system()
        self.initialized = False
        
        # Command execution
        self.active_processes = {}
        self.command_history = []
        self.max_history = 1000
        
        # Session management
        self.current_session = None
        self.session_lock = threading.Lock()
        
        # Performance tracking
        self.commands_executed = 0
        self.successful_commands = 0
        self.failed_commands = 0
        
        # Configuration
        self.default_timeout = 30.0
        self.default_encoding = 'utf-8'
        self.max_output_size = 1024 * 1024  # 1MB
        
        # Shell configuration
        self.shell_config = self._get_shell_config()
        
        self.logger.info("🖥️ TerminalController initialized")
    
    def initialize(self) -> bool:
        """
        Initialize terminal controller
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing terminal controller...")
            
            # Test basic command execution
            test_result = self._test_basic_execution()
            if not test_result:
                raise RuntimeError("Basic command execution test failed")
            
            # Initialize components
            from .command_executor import CommandExecutor
            from .output_parser import OutputParser
            from .session_manager import SessionManager
            
            self.executor = CommandExecutor(self)
            self.parser = OutputParser()
            self.session_manager = SessionManager(self)
            
            self.initialized = True
            self.logger.info("✅ Terminal controller initialized successfully")
            self.logger.info(f"🖥️ Platform: {self.platform}")
            self.logger.info(f"🐚 Shell: {self.shell_config['default_shell']}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Terminal controller initialization failed: {e}")
            return False
    
    def _get_shell_config(self) -> Dict[str, Any]:
        """Get platform-specific shell configuration"""
        if self.platform == "Windows":
            return {
                'default_shell': 'cmd',
                'shells': ['cmd', 'powershell', 'pwsh'],
                'shell_args': {
                    'cmd': ['/c'],
                    'powershell': ['-Command'],
                    'pwsh': ['-Command']
                }
            }
        else:  # Linux, Darwin
            return {
                'default_shell': 'bash',
                'shells': ['bash', 'sh', 'zsh', 'fish'],
                'shell_args': {
                    'bash': ['-c'],
                    'sh': ['-c'],
                    'zsh': ['-c'],
                    'fish': ['-c']
                }
            }
    
    def _test_basic_execution(self) -> bool:
        """Test basic command execution capability"""
        try:
            if self.platform == "Windows":
                test_cmd = ["cmd", "/c", "echo test"]
            else:
                test_cmd = ["echo", "test"]
            
            result = subprocess.run(
                test_cmd,
                capture_output=True,
                text=True,
                timeout=5.0
            )
            
            return result.returncode == 0 and "test" in result.stdout
            
        except Exception as e:
            self.logger.error(f"❌ Basic execution test failed: {e}")
            return False
    
    def execute_command(self, parameters: Dict[str, Any]) -> CommandResult:
        """
        Execute a terminal command
        
        Args:
            parameters: Command parameters including:
                - command: Command to execute
                - timeout: Execution timeout (optional)
                - shell: Shell to use (optional)
                - working_dir: Working directory (optional)
                - env: Environment variables (optional)
        
        Returns:
            CommandResult: Command execution result
        """
        if not self.initialized:
            raise RuntimeError("Terminal controller not initialized")
        
        command = parameters.get('command')
        if not command:
            raise ValueError("Command parameter is required")
        
        timeout = parameters.get('timeout', self.default_timeout)
        shell = parameters.get('shell', self.shell_config['default_shell'])
        working_dir = parameters.get('working_dir')
        env = parameters.get('env')
        
        self.logger.info(f"🎯 Executing command: {command}")
        
        start_time = time.time()
        
        try:
            # Prepare command for execution
            cmd_args = self._prepare_command(command, shell)
            
            # Execute command
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                env=env
            )
            
            # Store active process
            process_id = id(process)
            self.active_processes[process_id] = process
            
            try:
                # Wait for completion with timeout
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode
                status = CommandStatus.COMPLETED if return_code == 0 else CommandStatus.FAILED
                
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                return_code = -1
                status = CommandStatus.TIMEOUT
                
            finally:
                # Remove from active processes
                self.active_processes.pop(process_id, None)
            
            execution_time = time.time() - start_time
            
            # Create result
            result = CommandResult(
                command=command,
                status=status,
                return_code=return_code,
                stdout=stdout,
                stderr=stderr,
                execution_time=execution_time,
                timestamp=time.time()
            )
            
            # Update statistics
            self.commands_executed += 1
            if status == CommandStatus.COMPLETED:
                self.successful_commands += 1
            else:
                self.failed_commands += 1
            
            # Add to history
            self._add_to_history(result)
            
            self.logger.info(f"✅ Command completed: {command} ({execution_time:.3f}s)")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = CommandResult(
                command=command,
                status=CommandStatus.FAILED,
                return_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=execution_time,
                timestamp=time.time()
            )
            
            self.failed_commands += 1
            self._add_to_history(result)
            
            self.logger.error(f"❌ Command failed: {command} - {e}")
            return result
    
    def _prepare_command(self, command: str, shell: str) -> List[str]:
        """Prepare command for execution based on shell"""
        if shell not in self.shell_config['shells']:
            raise ValueError(f"Unsupported shell: {shell}")
        
        shell_args = self.shell_config['shell_args'][shell]
        return [shell] + shell_args + [command]
    
    def _add_to_history(self, result: CommandResult):
        """Add command result to history"""
        self.command_history.append(result)
        
        # Maintain history size limit
        if len(self.command_history) > self.max_history:
            self.command_history = self.command_history[-self.max_history:]
    
    def get_command_history(self, limit: int = 10) -> List[CommandResult]:
        """Get recent command history"""
        return self.command_history[-limit:]
    
    def cancel_command(self, process_id: int) -> bool:
        """Cancel a running command"""
        if process_id in self.active_processes:
            try:
                process = self.active_processes[process_id]
                process.terminate()
                self.logger.info(f"🛑 Command cancelled: {process_id}")
                return True
            except Exception as e:
                self.logger.error(f"❌ Failed to cancel command: {e}")
                return False
        return False
    
    def get_active_commands(self) -> List[int]:
        """Get list of active command process IDs"""
        return list(self.active_processes.keys())
    
    def is_ready(self) -> bool:
        """Check if terminal controller is ready"""
        return self.initialized
    
    def get_status(self) -> Dict[str, Any]:
        """Get terminal controller status"""
        return {
            'initialized': self.initialized,
            'platform': self.platform,
            'shell': self.shell_config['default_shell'],
            'commands_executed': self.commands_executed,
            'successful_commands': self.successful_commands,
            'failed_commands': self.failed_commands,
            'success_rate': (self.successful_commands / max(self.commands_executed, 1)) * 100,
            'active_commands': len(self.active_processes),
            'history_size': len(self.command_history)
        }
    
    def shutdown(self):
        """Shutdown terminal controller"""
        self.logger.info("🛑 Shutting down terminal controller")
        
        # Cancel all active commands
        for process_id in list(self.active_processes.keys()):
            self.cancel_command(process_id)
        
        self.initialized = False
        self.logger.info("✅ Terminal controller shutdown complete")
