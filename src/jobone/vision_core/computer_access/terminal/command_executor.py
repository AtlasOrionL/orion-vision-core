#!/usr/bin/env python3
"""
Command Executor - Advanced command execution engine with real-time streaming
"""

import logging
import subprocess
import threading
import time
import queue
import select
import os
import signal
from typing import Dict, List, Any, Optional, Callable, Generator
from dataclasses import dataclass
from enum import Enum

class ExecutionMode(Enum):
    """Command execution modes"""
    BLOCKING = "blocking"
    NON_BLOCKING = "non_blocking"
    STREAMING = "streaming"
    INTERACTIVE = "interactive"

@dataclass
class StreamingOutput:
    """Real-time streaming output"""
    line: str
    stream_type: str  # 'stdout' or 'stderr'
    timestamp: float

class CommandExecutor:
    """
    Advanced command execution engine with real-time capabilities
    Supports blocking, non-blocking, streaming, and interactive execution
    """
    
    def __init__(self, terminal_controller):
        self.logger = logging.getLogger('orion.computer_access.terminal.executor')
        self.terminal_controller = terminal_controller
        
        # Execution tracking
        self.running_processes = {}
        self.process_counter = 0
        self.process_lock = threading.Lock()
        
        # Streaming support
        self.stream_callbacks = {}
        self.stream_threads = {}
        
        # Performance metrics
        self.total_executions = 0
        self.streaming_executions = 0
        self.interactive_executions = 0
        
        self.logger.info("⚡ CommandExecutor initialized")
    
    def execute_blocking(self, command: str, **kwargs) -> Dict[str, Any]:
        """
        Execute command in blocking mode (wait for completion)
        
        Args:
            command: Command to execute
            **kwargs: Additional execution parameters
            
        Returns:
            Dict containing execution result
        """
        timeout = kwargs.get('timeout', 30.0)
        working_dir = kwargs.get('working_dir')
        env = kwargs.get('env')
        shell = kwargs.get('shell', True)
        
        self.logger.info(f"🔄 Executing blocking command: {command}")
        
        start_time = time.time()
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell,
                cwd=working_dir,
                env=env
            )
            
            stdout, stderr = process.communicate(timeout=timeout)
            execution_time = time.time() - start_time
            
            result = {
                'success': process.returncode == 0,
                'return_code': process.returncode,
                'stdout': stdout,
                'stderr': stderr,
                'execution_time': execution_time,
                'mode': ExecutionMode.BLOCKING.value
            }
            
            self.total_executions += 1
            self.logger.info(f"✅ Blocking execution completed: {execution_time:.3f}s")
            
            return result
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            execution_time = time.time() - start_time
            
            result = {
                'success': False,
                'return_code': -1,
                'stdout': stdout,
                'stderr': stderr + "\nCommand timed out",
                'execution_time': execution_time,
                'mode': ExecutionMode.BLOCKING.value,
                'timeout': True
            }
            
            self.logger.warning(f"⏰ Command timed out: {command}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = {
                'success': False,
                'return_code': -1,
                'stdout': "",
                'stderr': str(e),
                'execution_time': execution_time,
                'mode': ExecutionMode.BLOCKING.value,
                'error': str(e)
            }
            
            self.logger.error(f"❌ Blocking execution failed: {e}")
            return result
    
    def execute_streaming(self, command: str, callback: Callable[[StreamingOutput], None], **kwargs) -> int:
        """
        Execute command with real-time output streaming
        
        Args:
            command: Command to execute
            callback: Function to call for each output line
            **kwargs: Additional execution parameters
            
        Returns:
            int: Process ID for tracking
        """
        working_dir = kwargs.get('working_dir')
        env = kwargs.get('env')
        shell = kwargs.get('shell', True)
        
        self.logger.info(f"📡 Starting streaming execution: {command}")
        
        try:
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell,
                cwd=working_dir,
                env=env,
                bufsize=1,
                universal_newlines=True
            )
            
            with self.process_lock:
                self.process_counter += 1
                process_id = self.process_counter
                self.running_processes[process_id] = process
                self.stream_callbacks[process_id] = callback
            
            # Start streaming thread
            stream_thread = threading.Thread(
                target=self._stream_output,
                args=(process_id, process),
                daemon=True
            )
            stream_thread.start()
            self.stream_threads[process_id] = stream_thread
            
            self.streaming_executions += 1
            self.total_executions += 1
            
            self.logger.info(f"📡 Streaming started: Process ID {process_id}")
            return process_id
            
        except Exception as e:
            self.logger.error(f"❌ Streaming execution failed: {e}")
            raise
    
    def _stream_output(self, process_id: int, process: subprocess.Popen):
        """Stream output from process in real-time"""
        try:
            # Create queues for stdout and stderr
            stdout_queue = queue.Queue()
            stderr_queue = queue.Queue()
            
            # Start reader threads
            stdout_thread = threading.Thread(
                target=self._read_stream,
                args=(process.stdout, stdout_queue, 'stdout'),
                daemon=True
            )
            stderr_thread = threading.Thread(
                target=self._read_stream,
                args=(process.stderr, stderr_queue, 'stderr'),
                daemon=True
            )
            
            stdout_thread.start()
            stderr_thread.start()
            
            callback = self.stream_callbacks.get(process_id)
            
            # Stream output until process completes
            while process.poll() is None:
                # Check stdout queue
                try:
                    line, stream_type = stdout_queue.get_nowait()
                    if callback:
                        output = StreamingOutput(line, stream_type, time.time())
                        callback(output)
                except queue.Empty:
                    pass
                
                # Check stderr queue
                try:
                    line, stream_type = stderr_queue.get_nowait()
                    if callback:
                        output = StreamingOutput(line, stream_type, time.time())
                        callback(output)
                except queue.Empty:
                    pass
                
                time.sleep(0.01)  # Small delay to prevent busy waiting
            
            # Process remaining output
            while True:
                try:
                    line, stream_type = stdout_queue.get_nowait()
                    if callback:
                        output = StreamingOutput(line, stream_type, time.time())
                        callback(output)
                except queue.Empty:
                    break
            
            while True:
                try:
                    line, stream_type = stderr_queue.get_nowait()
                    if callback:
                        output = StreamingOutput(line, stream_type, time.time())
                        callback(output)
                except queue.Empty:
                    break
            
            self.logger.info(f"📡 Streaming completed: Process ID {process_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Streaming error: {e}")
        
        finally:
            # Cleanup
            with self.process_lock:
                self.running_processes.pop(process_id, None)
                self.stream_callbacks.pop(process_id, None)
                self.stream_threads.pop(process_id, None)
    
    def _read_stream(self, stream, output_queue: queue.Queue, stream_type: str):
        """Read from stream and put lines in queue"""
        try:
            for line in iter(stream.readline, ''):
                if line:
                    output_queue.put((line.rstrip(), stream_type))
        except Exception as e:
            self.logger.error(f"❌ Stream reading error: {e}")
        finally:
            stream.close()
    
    def execute_interactive(self, command: str, input_data: str = "", **kwargs) -> Dict[str, Any]:
        """
        Execute command in interactive mode with input
        
        Args:
            command: Command to execute
            input_data: Input to send to command
            **kwargs: Additional execution parameters
            
        Returns:
            Dict containing execution result
        """
        timeout = kwargs.get('timeout', 30.0)
        working_dir = kwargs.get('working_dir')
        env = kwargs.get('env')
        shell = kwargs.get('shell', True)
        
        self.logger.info(f"🔄 Executing interactive command: {command}")
        
        start_time = time.time()
        
        try:
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=shell,
                cwd=working_dir,
                env=env
            )
            
            stdout, stderr = process.communicate(input=input_data, timeout=timeout)
            execution_time = time.time() - start_time
            
            result = {
                'success': process.returncode == 0,
                'return_code': process.returncode,
                'stdout': stdout,
                'stderr': stderr,
                'execution_time': execution_time,
                'mode': ExecutionMode.INTERACTIVE.value,
                'input_sent': input_data
            }
            
            self.interactive_executions += 1
            self.total_executions += 1
            
            self.logger.info(f"✅ Interactive execution completed: {execution_time:.3f}s")
            return result
            
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
            execution_time = time.time() - start_time
            
            result = {
                'success': False,
                'return_code': -1,
                'stdout': stdout,
                'stderr': stderr + "\nInteractive command timed out",
                'execution_time': execution_time,
                'mode': ExecutionMode.INTERACTIVE.value,
                'timeout': True
            }
            
            self.logger.warning(f"⏰ Interactive command timed out: {command}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = {
                'success': False,
                'return_code': -1,
                'stdout': "",
                'stderr': str(e),
                'execution_time': execution_time,
                'mode': ExecutionMode.INTERACTIVE.value,
                'error': str(e)
            }
            
            self.logger.error(f"❌ Interactive execution failed: {e}")
            return result
    
    def terminate_process(self, process_id: int) -> bool:
        """Terminate a running process"""
        with self.process_lock:
            if process_id in self.running_processes:
                try:
                    process = self.running_processes[process_id]
                    process.terminate()
                    self.logger.info(f"🛑 Process terminated: {process_id}")
                    return True
                except Exception as e:
                    self.logger.error(f"❌ Failed to terminate process {process_id}: {e}")
                    return False
        return False
    
    def kill_process(self, process_id: int) -> bool:
        """Force kill a running process"""
        with self.process_lock:
            if process_id in self.running_processes:
                try:
                    process = self.running_processes[process_id]
                    process.kill()
                    self.logger.info(f"💀 Process killed: {process_id}")
                    return True
                except Exception as e:
                    self.logger.error(f"❌ Failed to kill process {process_id}: {e}")
                    return False
        return False
    
    def get_running_processes(self) -> List[int]:
        """Get list of running process IDs"""
        with self.process_lock:
            return list(self.running_processes.keys())
    
    def get_process_status(self, process_id: int) -> Optional[Dict[str, Any]]:
        """Get status of a specific process"""
        with self.process_lock:
            if process_id in self.running_processes:
                process = self.running_processes[process_id]
                return {
                    'process_id': process_id,
                    'pid': process.pid,
                    'poll': process.poll(),
                    'running': process.poll() is None
                }
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics"""
        return {
            'total_executions': self.total_executions,
            'streaming_executions': self.streaming_executions,
            'interactive_executions': self.interactive_executions,
            'running_processes': len(self.running_processes),
            'active_streams': len(self.stream_threads)
        }
