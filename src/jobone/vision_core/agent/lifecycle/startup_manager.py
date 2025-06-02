"""
Agent Startup Manager for Orion Vision Core

This module handles agent startup sequences and initialization.
Extracted from agent_core.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import time
import threading
from typing import Optional, Callable, List, Dict, Any
from ..core.agent_config import AgentConfig
from ..core.agent_status import AgentStatus
from ..core.agent_logger import AgentLogger


class StartupManager:
    """Manages agent startup sequence and initialization callbacks"""
    
    def __init__(self, config: AgentConfig, logger: AgentLogger):
        self.config = config
        self.logger = logger
        self.startup_callbacks: List[Callable] = []
        self.startup_time: Optional[float] = None
        self.startup_success: bool = False
        self.startup_errors: List[str] = []
        
    def add_startup_callback(self, callback: Callable, priority: int = 0):
        """Add startup callback with priority (higher priority runs first)"""
        self.startup_callbacks.append((priority, callback))
        # Sort by priority (descending)
        self.startup_callbacks.sort(key=lambda x: x[0], reverse=True)
        
        self.logger.info(
            "Startup callback added",
            callback_name=callback.__name__,
            priority=priority,
            total_callbacks=len(self.startup_callbacks)
        )
    
    def execute_startup(self) -> bool:
        """Execute complete startup sequence"""
        start_time = time.time()
        self.startup_errors.clear()
        
        self.logger.info(
            "Starting agent startup sequence",
            agent_id=self.config.agent_id,
            agent_type=self.config.agent_type,
            callbacks_count=len(self.startup_callbacks)
        )
        
        try:
            # Phase 1: Pre-startup validation
            if not self._validate_prerequisites():
                return False
            
            # Phase 2: Execute startup callbacks
            if not self._execute_callbacks():
                return False
            
            # Phase 3: Post-startup verification
            if not self._verify_startup():
                return False
            
            # Success
            self.startup_time = time.time() - start_time
            self.startup_success = True
            
            self.logger.info(
                "Agent startup completed successfully",
                startup_time=f"{self.startup_time:.3f}s",
                callbacks_executed=len(self.startup_callbacks),
                status="SUCCESS"
            )
            
            return True
            
        except Exception as e:
            self.startup_time = time.time() - start_time
            self.startup_success = False
            error_msg = f"Startup failed: {e}"
            self.startup_errors.append(error_msg)
            
            self.logger.error(
                "Agent startup failed",
                error=str(e),
                startup_time=f"{self.startup_time:.3f}s",
                errors_count=len(self.startup_errors)
            )
            
            return False
    
    def _validate_prerequisites(self) -> bool:
        """Validate prerequisites before startup"""
        self.logger.debug("Validating startup prerequisites")
        
        # Validate configuration
        if not self.config.validate():
            self.startup_errors.append("Invalid agent configuration")
            return False
        
        # Check dependencies
        for dependency in self.config.dependencies:
            if not self._check_dependency(dependency):
                self.startup_errors.append(f"Missing dependency: {dependency}")
                return False
        
        return True
    
    def _execute_callbacks(self) -> bool:
        """Execute all startup callbacks in priority order"""
        self.logger.debug("Executing startup callbacks")
        
        for priority, callback in self.startup_callbacks:
            try:
                self.logger.debug(
                    "Executing startup callback",
                    callback_name=callback.__name__,
                    priority=priority
                )
                
                callback()
                
            except Exception as e:
                error_msg = f"Startup callback {callback.__name__} failed: {e}"
                self.startup_errors.append(error_msg)
                self.logger.error(
                    "Startup callback failed",
                    callback_name=callback.__name__,
                    error=str(e)
                )
                return False
        
        return True
    
    def _verify_startup(self) -> bool:
        """Verify startup completed successfully"""
        self.logger.debug("Verifying startup completion")
        
        # Add any post-startup verification logic here
        # For now, just return True if no errors
        return len(self.startup_errors) == 0
    
    def _check_dependency(self, dependency: str) -> bool:
        """Check if a dependency is available"""
        # Basic dependency checking - can be enhanced
        try:
            __import__(dependency)
            return True
        except ImportError:
            return False
    
    def get_startup_stats(self) -> Dict[str, Any]:
        """Get startup statistics"""
        return {
            'startup_time': self.startup_time,
            'startup_success': self.startup_success,
            'callbacks_count': len(self.startup_callbacks),
            'errors_count': len(self.startup_errors),
            'errors': self.startup_errors.copy()
        }
