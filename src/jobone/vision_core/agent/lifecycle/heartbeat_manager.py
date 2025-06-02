"""
Agent Heartbeat Manager for Orion Vision Core

This module handles agent heartbeat monitoring and health checks.
Extracted from agent_core.py as part of Sprint 9.1.1.1 modularization.

Author: Atlas-orion (Augment Agent)
Date: 1 Haziran 2025
Sprint: 9.1.1.1 - Core Framework Optimization
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, List, Dict, Any
from ..core.agent_config import AgentConfig
from ..core.agent_status import AgentStatus
from ..core.agent_logger import AgentLogger


class HeartbeatManager:
    """Manages agent heartbeat monitoring and health status"""
    
    def __init__(self, config: AgentConfig, logger: AgentLogger):
        self.config = config
        self.logger = logger
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.last_heartbeat: Optional[datetime] = None
        self.heartbeat_count: int = 0
        self.missed_heartbeats: int = 0
        self.health_callbacks: List[Callable] = []
        self.is_healthy: bool = True
        self.health_status: Dict[str, Any] = {}
        
    def add_health_callback(self, callback: Callable):
        """Add health check callback"""
        self.health_callbacks.append(callback)
        self.logger.info(
            "Health callback added",
            callback_name=callback.__name__,
            total_callbacks=len(self.health_callbacks)
        )
    
    def start_heartbeat(self):
        """Start heartbeat monitoring"""
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.logger.warning("Heartbeat already running")
            return
        
        self.stop_event.clear()
        self.heartbeat_thread = threading.Thread(
            target=self._heartbeat_loop,
            name=f"heartbeat-{self.config.agent_id}"
        )
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        
        self.logger.info(
            "Heartbeat monitoring started",
            agent_id=self.config.agent_id,
            interval=self.config.heartbeat_interval,
            thread_name=self.heartbeat_thread.name
        )
    
    def stop_heartbeat(self, timeout: float = 5.0):
        """Stop heartbeat monitoring"""
        if not self.heartbeat_thread or not self.heartbeat_thread.is_alive():
            self.logger.debug("Heartbeat not running")
            return
        
        self.logger.info("Stopping heartbeat monitoring")
        self.stop_event.set()
        
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout)
            if self.heartbeat_thread.is_alive():
                self.logger.warning(
                    "Heartbeat thread did not stop gracefully",
                    timeout=timeout
                )
            else:
                self.logger.info("Heartbeat monitoring stopped")
    
    def _heartbeat_loop(self):
        """Main heartbeat monitoring loop"""
        self.logger.debug("Heartbeat loop started")
        
        while not self.stop_event.is_set():
            try:
                # Perform heartbeat
                self._perform_heartbeat()
                
                # Wait for next interval
                if self.stop_event.wait(self.config.heartbeat_interval):
                    break  # Stop event was set
                    
            except Exception as e:
                self.logger.error(
                    "Heartbeat loop error",
                    error=str(e),
                    heartbeat_count=self.heartbeat_count
                )
                self.missed_heartbeats += 1
        
        self.logger.debug("Heartbeat loop ended")
    
    def _perform_heartbeat(self):
        """Perform single heartbeat check"""
        current_time = datetime.now()
        
        try:
            # Update heartbeat timestamp
            self.last_heartbeat = current_time
            self.heartbeat_count += 1
            
            # Perform health checks
            health_results = self._perform_health_checks()
            
            # Update health status
            self.is_healthy = all(health_results.values())
            self.health_status = {
                'timestamp': current_time.isoformat(),
                'heartbeat_count': self.heartbeat_count,
                'missed_heartbeats': self.missed_heartbeats,
                'is_healthy': self.is_healthy,
                'health_checks': health_results
            }
            
            # Log heartbeat (debug level to avoid spam)
            self.logger.debug(
                "Heartbeat performed",
                heartbeat_count=self.heartbeat_count,
                is_healthy=self.is_healthy,
                health_checks_passed=sum(health_results.values()),
                health_checks_total=len(health_results)
            )
            
            # Log health issues at warning level
            if not self.is_healthy:
                failed_checks = [name for name, result in health_results.items() if not result]
                self.logger.warning(
                    "Health check failures detected",
                    failed_checks=failed_checks,
                    heartbeat_count=self.heartbeat_count
                )
            
        except Exception as e:
            self.missed_heartbeats += 1
            self.is_healthy = False
            self.logger.error(
                "Heartbeat failed",
                error=str(e),
                missed_heartbeats=self.missed_heartbeats
            )
    
    def _perform_health_checks(self) -> Dict[str, bool]:
        """Perform all registered health checks"""
        health_results = {}
        
        for callback in self.health_callbacks:
            try:
                result = callback()
                health_results[callback.__name__] = bool(result)
            except Exception as e:
                health_results[callback.__name__] = False
                self.logger.error(
                    "Health check failed",
                    callback_name=callback.__name__,
                    error=str(e)
                )
        
        return health_results
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status.copy()
    
    def is_heartbeat_alive(self) -> bool:
        """Check if heartbeat thread is alive"""
        return self.heartbeat_thread is not None and self.heartbeat_thread.is_alive()
    
    def get_heartbeat_stats(self) -> Dict[str, Any]:
        """Get heartbeat statistics"""
        uptime = None
        if self.last_heartbeat and self.heartbeat_count > 0:
            # Estimate uptime based on heartbeat count and interval
            uptime = self.heartbeat_count * self.config.heartbeat_interval
        
        return {
            'heartbeat_count': self.heartbeat_count,
            'missed_heartbeats': self.missed_heartbeats,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'is_healthy': self.is_healthy,
            'is_alive': self.is_heartbeat_alive(),
            'uptime_seconds': uptime,
            'health_callbacks_count': len(self.health_callbacks)
        }
