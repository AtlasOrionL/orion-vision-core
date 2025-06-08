#!/usr/bin/env python3
"""
Computer Access Manager - Main coordinator for autonomous computer control
"""

import logging
import time
import platform
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class AccessMode(Enum):
    """Computer access operation modes"""
    TERMINAL_ONLY = "terminal_only"
    INPUT_ONLY = "input_only"
    VISION_ONLY = "vision_only"
    FULL_ACCESS = "full_access"
    SAFE_MODE = "safe_mode"

class TaskPriority(Enum):
    """Task execution priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class ComputerTask:
    """Computer access task definition"""
    task_id: str
    task_type: str
    description: str
    priority: TaskPriority
    mode: AccessMode
    parameters: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 3
    callback: Optional[Callable] = None

@dataclass
class TaskResult:
    """Computer access task result"""
    task_id: str
    success: bool
    result: Any
    error: Optional[str]
    execution_time: float
    timestamp: float

class ComputerAccessManager:
    """
    Main coordinator for all computer access operations
    Manages terminal, input, vision, and scenario execution
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.computer_access.manager')
        self.platform = platform.system()
        self.initialized = False
        self.access_mode = AccessMode.SAFE_MODE
        
        # Component references (will be initialized later)
        self.terminal = None
        self.mouse = None
        self.keyboard = None
        self.screen = None
        self.scenarios = None
        
        # Task management
        self.task_queue = []
        self.active_tasks = {}
        self.completed_tasks = []
        self.task_lock = threading.Lock()
        
        # Performance tracking
        self.start_time = time.time()
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        
        # Safety mechanisms
        self.safety_enabled = True
        self.max_concurrent_tasks = 5
        self.emergency_stop = False
        
        self.logger.info("🤖 ComputerAccessManager initialized")
    
    def initialize(self) -> bool:
        """
        Initialize all computer access components
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing computer access components...")
            
            # Import components (lazy loading to avoid circular imports)
            from .terminal.terminal_controller import TerminalController
            from .input.mouse_controller import MouseController
            from .input.keyboard_controller import KeyboardController
            from .vision.screen_agent import ScreenAgent
            from .scenarios.scenario_executor import ScenarioExecutor
            
            # Initialize components
            self.terminal = TerminalController()
            self.mouse = MouseController()
            self.keyboard = KeyboardController()
            self.screen = ScreenAgent()
            self.scenarios = ScenarioExecutor(self)
            
            # Verify platform compatibility
            if not self._verify_platform_compatibility():
                raise RuntimeError(f"Platform {self.platform} not fully supported")
            
            # Initialize components
            init_results = {
                'terminal': self.terminal.initialize(),
                'mouse': self.mouse.initialize(),
                'keyboard': self.keyboard.initialize(),
                'screen': self.screen.initialize(),
                'scenarios': self.scenarios.initialize()
            }
            
            # Check initialization results
            failed_components = [comp for comp, result in init_results.items() if not result]
            if failed_components:
                self.logger.error(f"❌ Failed to initialize: {failed_components}")
                return False
            
            self.initialized = True
            self.access_mode = AccessMode.FULL_ACCESS
            
            self.logger.info("✅ All computer access components initialized successfully")
            self.logger.info(f"🖥️ Platform: {self.platform}")
            self.logger.info(f"🎯 Access Mode: {self.access_mode.value}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Computer access initialization failed: {e}")
            return False
    
    def _verify_platform_compatibility(self) -> bool:
        """Verify current platform compatibility"""
        supported_platforms = ['Windows', 'Linux', 'Darwin']
        
        if self.platform not in supported_platforms:
            self.logger.warning(f"⚠️ Platform {self.platform} may not be fully supported")
            return False
        
        self.logger.info(f"✅ Platform {self.platform} is supported")
        return True
    
    def set_access_mode(self, mode: AccessMode) -> bool:
        """
        Set computer access mode
        
        Args:
            mode: Access mode to set
            
        Returns:
            bool: True if mode set successfully
        """
        if not self.initialized:
            self.logger.error("❌ Cannot set access mode: Manager not initialized")
            return False
        
        self.access_mode = mode
        self.logger.info(f"🎯 Access mode set to: {mode.value}")
        return True
    
    def execute_task(self, task: ComputerTask) -> TaskResult:
        """
        Execute a computer access task
        
        Args:
            task: Task to execute
            
        Returns:
            TaskResult: Task execution result
        """
        start_time = time.time()
        
        try:
            if not self.initialized:
                raise RuntimeError("Computer access manager not initialized")
            
            if self.emergency_stop:
                raise RuntimeError("Emergency stop activated")
            
            # Validate task
            if not self._validate_task(task):
                raise ValueError("Invalid task parameters")
            
            # Check access mode compatibility
            if not self._check_mode_compatibility(task.mode):
                raise RuntimeError(f"Task mode {task.mode.value} not compatible with current mode {self.access_mode.value}")
            
            # Add to active tasks
            with self.task_lock:
                self.active_tasks[task.task_id] = task
                self.total_tasks += 1
            
            self.logger.info(f"🎯 Executing task: {task.task_id} ({task.task_type})")
            
            # Route task to appropriate component
            result = self._route_task(task)
            
            # Create success result
            execution_time = time.time() - start_time
            task_result = TaskResult(
                task_id=task.task_id,
                success=True,
                result=result,
                error=None,
                execution_time=execution_time,
                timestamp=time.time()
            )
            
            self.successful_tasks += 1
            self.logger.info(f"✅ Task completed: {task.task_id} ({execution_time:.3f}s)")
            
        except Exception as e:
            execution_time = time.time() - start_time
            task_result = TaskResult(
                task_id=task.task_id,
                success=False,
                result=None,
                error=str(e),
                execution_time=execution_time,
                timestamp=time.time()
            )
            
            self.failed_tasks += 1
            self.logger.error(f"❌ Task failed: {task.task_id} - {e}")
        
        finally:
            # Remove from active tasks
            with self.task_lock:
                self.active_tasks.pop(task.task_id, None)
                self.completed_tasks.append(task_result)
            
            # Execute callback if provided
            if task.callback:
                try:
                    task.callback(task_result)
                except Exception as e:
                    self.logger.error(f"❌ Task callback failed: {e}")
        
        return task_result
    
    def _validate_task(self, task: ComputerTask) -> bool:
        """Validate task parameters"""
        if not task.task_id or not task.task_type:
            return False
        
        if task.timeout <= 0 or task.retry_count < 0:
            return False
        
        return True
    
    def _check_mode_compatibility(self, task_mode: AccessMode) -> bool:
        """Check if task mode is compatible with current access mode"""
        if self.access_mode == AccessMode.FULL_ACCESS:
            return True
        
        if self.access_mode == AccessMode.SAFE_MODE:
            return task_mode in [AccessMode.TERMINAL_ONLY, AccessMode.SAFE_MODE]
        
        return self.access_mode == task_mode
    
    def _route_task(self, task: ComputerTask) -> Any:
        """Route task to appropriate component"""
        task_type = task.task_type.lower()
        
        if task_type.startswith('terminal'):
            return self.terminal.execute_command(task.parameters)
        elif task_type.startswith('mouse'):
            return self.mouse.execute_action(task.parameters)
        elif task_type.startswith('keyboard'):
            return self.keyboard.execute_action(task.parameters)
        elif task_type.startswith('screen'):
            return self.screen.capture_and_analyze(task.parameters)
        elif task_type.startswith('scenario'):
            return self.scenarios.execute_scenario(task.parameters)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get computer access manager status"""
        uptime = time.time() - self.start_time
        
        return {
            'initialized': self.initialized,
            'platform': self.platform,
            'access_mode': self.access_mode.value,
            'uptime': uptime,
            'total_tasks': self.total_tasks,
            'successful_tasks': self.successful_tasks,
            'failed_tasks': self.failed_tasks,
            'success_rate': (self.successful_tasks / max(self.total_tasks, 1)) * 100,
            'active_tasks': len(self.active_tasks),
            'emergency_stop': self.emergency_stop,
            'safety_enabled': self.safety_enabled,
            'components': {
                'terminal': self.terminal.is_ready() if self.terminal else False,
                'mouse': self.mouse.is_ready() if self.mouse else False,
                'keyboard': self.keyboard.is_ready() if self.keyboard else False,
                'screen': self.screen.is_ready() if self.screen else False,
                'scenarios': self.scenarios.is_ready() if self.scenarios else False
            }
        }
    
    def emergency_shutdown(self) -> bool:
        """Emergency shutdown of all computer access operations"""
        self.logger.warning("🚨 Emergency shutdown initiated")
        
        self.emergency_stop = True
        
        # Stop all active tasks
        with self.task_lock:
            for task_id in list(self.active_tasks.keys()):
                self.logger.warning(f"🛑 Stopping task: {task_id}")
        
        # Shutdown components
        if self.terminal:
            self.terminal.shutdown()
        if self.mouse:
            self.mouse.shutdown()
        if self.keyboard:
            self.keyboard.shutdown()
        if self.screen:
            self.screen.shutdown()
        if self.scenarios:
            self.scenarios.shutdown()
        
        self.logger.warning("🛑 Emergency shutdown completed")
        return True
    
    def reset(self) -> bool:
        """Reset computer access manager to initial state"""
        self.logger.info("🔄 Resetting computer access manager")
        
        self.emergency_stop = False
        self.task_queue.clear()
        self.active_tasks.clear()
        self.completed_tasks.clear()
        
        self.total_tasks = 0
        self.successful_tasks = 0
        self.failed_tasks = 0
        
        return self.initialize()
