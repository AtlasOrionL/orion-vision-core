"""
Agent Shutdown Manager for Orion Vision Core

This module handles graceful agent shutdown sequences.
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


class ShutdownManager:
    """Manages graceful agent shutdown sequence and cleanup callbacks"""
    
    def __init__(self, config: AgentConfig, logger: AgentLogger):
        self.config = config
        self.logger = logger
        self.shutdown_callbacks: List[Callable] = []
        self.shutdown_time: Optional[float] = None
        self.shutdown_success: bool = False
        self.shutdown_errors: List[str] = []
        self.force_shutdown: bool = False
        
    def add_shutdown_callback(self, callback: Callable, priority: int = 0):
        """Add shutdown callback with priority (higher priority runs first)"""
        self.shutdown_callbacks.append((priority, callback))
        # Sort by priority (descending)
        self.shutdown_callbacks.sort(key=lambda x: x[0], reverse=True)
        
        self.logger.info(
            "Shutdown callback added",
            callback_name=callback.__name__,
            priority=priority,
            total_callbacks=len(self.shutdown_callbacks)
        )
    
    def execute_shutdown(self, timeout: float = 30.0, force: bool = False) -> bool:
        """Execute graceful shutdown sequence with timeout"""
        start_time = time.time()
        self.shutdown_errors.clear()
        self.force_shutdown = force
        
        self.logger.info(
            "Starting agent shutdown sequence",
            agent_id=self.config.agent_id,
            timeout=timeout,
            force_shutdown=force,
            callbacks_count=len(self.shutdown_callbacks)
        )
        
        try:
            # Phase 1: Pre-shutdown preparation
            if not self._prepare_shutdown():
                return False
            
            # Phase 2: Execute shutdown callbacks with timeout
            if not self._execute_callbacks_with_timeout(timeout):
                if not force:
                    return False
                else:
                    self.logger.warning("Forcing shutdown despite callback failures")
            
            # Phase 3: Final cleanup
            if not self._final_cleanup():
                return False
            
            # Success
            self.shutdown_time = time.time() - start_time
            self.shutdown_success = True
            
            self.logger.info(
                "Agent shutdown completed successfully",
                shutdown_time=f"{self.shutdown_time:.3f}s",
                callbacks_executed=len(self.shutdown_callbacks),
                status="SUCCESS"
            )
            
            return True
            
        except Exception as e:
            self.shutdown_time = time.time() - start_time
            self.shutdown_success = False
            error_msg = f"Shutdown failed: {e}"
            self.shutdown_errors.append(error_msg)
            
            self.logger.error(
                "Agent shutdown failed",
                error=str(e),
                shutdown_time=f"{self.shutdown_time:.3f}s",
                errors_count=len(self.shutdown_errors)
            )
            
            return False
    
    def _prepare_shutdown(self) -> bool:
        """Prepare for shutdown"""
        self.logger.debug("Preparing for shutdown")
        
        # Signal shutdown intent
        # Add any pre-shutdown preparation logic here
        
        return True
    
    def _execute_callbacks_with_timeout(self, timeout: float) -> bool:
        """Execute shutdown callbacks with timeout protection"""
        self.logger.debug("Executing shutdown callbacks with timeout")
        
        callback_timeout = timeout / max(len(self.shutdown_callbacks), 1)
        
        for priority, callback in self.shutdown_callbacks:
            try:
                self.logger.debug(
                    "Executing shutdown callback",
                    callback_name=callback.__name__,
                    priority=priority,
                    timeout=callback_timeout
                )
                
                # Execute callback with timeout
                result = self._execute_with_timeout(callback, callback_timeout)
                
                if not result and not self.force_shutdown:
                    error_msg = f"Shutdown callback {callback.__name__} timed out"
                    self.shutdown_errors.append(error_msg)
                    return False
                
            except Exception as e:
                error_msg = f"Shutdown callback {callback.__name__} failed: {e}"
                self.shutdown_errors.append(error_msg)
                self.logger.error(
                    "Shutdown callback failed",
                    callback_name=callback.__name__,
                    error=str(e)
                )
                
                if not self.force_shutdown:
                    return False
        
        return True
    
    def _execute_with_timeout(self, callback: Callable, timeout: float) -> bool:
        """Execute callback with timeout"""
        result = [False]
        exception = [None]
        
        def target():
            try:
                callback()
                result[0] = True
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            # Timeout occurred
            return False
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def _final_cleanup(self) -> bool:
        """Perform final cleanup operations"""
        self.logger.debug("Performing final cleanup")
        
        # Add any final cleanup logic here
        # Close file handles, network connections, etc.
        
        return True
    
    def get_shutdown_stats(self) -> Dict[str, Any]:
        """Get shutdown statistics"""
        return {
            'shutdown_time': self.shutdown_time,
            'shutdown_success': self.shutdown_success,
            'callbacks_count': len(self.shutdown_callbacks),
            'errors_count': len(self.shutdown_errors),
            'errors': self.shutdown_errors.copy(),
            'force_shutdown': self.force_shutdown
        }
