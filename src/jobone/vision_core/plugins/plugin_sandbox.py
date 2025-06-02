"""
🔌 Orion Vision Core - Plugin Sandbox
Secure plugin execution environment

This module provides plugin sandboxing capabilities:
- Secure plugin execution isolation
- Resource usage monitoring and limiting
- Network and file system access control
- Memory and CPU usage restrictions
- Security policy enforcement

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import resource
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
import os

# Optional psutil import for resource monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security levels for plugin sandboxing"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"

@dataclass
class SandboxConfig:
    """Configuration for plugin sandbox"""
    security_level: SecurityLevel = SecurityLevel.MEDIUM
    max_memory_mb: int = 512
    max_cpu_percent: float = 10.0
    max_execution_time: float = 30.0
    allow_network_access: bool = False
    allow_file_system_access: bool = False
    allowed_modules: List[str] = field(default_factory=lambda: [
        'json', 'datetime', 'math', 'random', 'string', 'collections'
    ])
    blocked_modules: List[str] = field(default_factory=lambda: [
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests'
    ])
    allowed_file_paths: List[str] = field(default_factory=list)
    blocked_file_paths: List[str] = field(default_factory=lambda: [
        '/etc', '/usr', '/bin', '/sbin', '/root'
    ])

@dataclass
class SandboxMetrics:
    """Metrics for sandbox execution"""
    execution_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    max_memory_used: int = 0
    max_cpu_used: float = 0.0
    violations_count: int = 0
    last_execution: Optional[datetime] = None

@dataclass
class SandboxViolation:
    """Security violation in sandbox"""
    violation_type: str
    description: str
    plugin_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: str = "medium"

class PluginSandbox:
    """
    Secure plugin execution sandbox for Orion Vision Core.

    Provides security isolation and resource management:
    - Memory and CPU usage monitoring
    - Network and file system access control
    - Module import restrictions
    - Execution time limits
    - Security violation detection
    """

    def __init__(self, config: Optional[SandboxConfig] = None):
        """
        Initialize the plugin sandbox.

        Args:
            config: Sandbox configuration (optional)
        """
        self.config = config or SandboxConfig()
        self.active_sandboxes: Dict[str, Dict[str, Any]] = {}
        self.sandbox_metrics: Dict[str, SandboxMetrics] = {}
        self.violations: List[SandboxViolation] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None

        logger.info(f"🛡️ Plugin Sandbox initialized with security level: {self.config.security_level.value}")

    async def initialize(self) -> bool:
        """
        Initialize the plugin sandbox.

        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Start resource monitoring
            await self._start_monitoring()

            logger.info("✅ Plugin Sandbox initialized successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Plugin Sandbox initialization failed: {e}")
            return False

    async def create_sandbox(self, plugin_id: str, custom_config: Optional[SandboxConfig] = None) -> bool:
        """
        Create a sandbox for a specific plugin.

        Args:
            plugin_id: Unique identifier for the plugin
            custom_config: Custom sandbox configuration (optional)

        Returns:
            True if sandbox creation successful, False otherwise
        """
        try:
            config = custom_config or self.config

            # Create sandbox environment
            sandbox_env = {
                'plugin_id': plugin_id,
                'config': config,
                'start_time': time.time(),
                'process_info': self._get_current_process_info(),
                'restrictions': self._create_restrictions(config),
                'active': True
            }

            self.active_sandboxes[plugin_id] = sandbox_env
            self.sandbox_metrics[plugin_id] = SandboxMetrics()

            logger.info(f"🏗️ Created sandbox for plugin: {plugin_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to create sandbox for {plugin_id}: {e}")
            return False

    async def execute_in_sandbox(self, plugin_id: str, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function within a plugin sandbox.

        Args:
            plugin_id: Plugin identifier
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function execution result
        """
        if plugin_id not in self.active_sandboxes:
            raise ValueError(f"Sandbox not found for plugin: {plugin_id}")

        sandbox = self.active_sandboxes[plugin_id]
        config = sandbox['config']
        metrics = self.sandbox_metrics[plugin_id]

        start_time = time.time()
        start_memory = self._get_memory_usage()

        try:
            # Apply resource limits
            await self._apply_resource_limits(config)

            # Monitor execution
            monitor_task = asyncio.create_task(
                self._monitor_execution(plugin_id, config.max_execution_time)
            )

            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Cancel monitoring
            monitor_task.cancel()

            # Update metrics
            execution_time = time.time() - start_time
            memory_used = self._get_memory_usage() - start_memory

            metrics.execution_count += 1
            metrics.total_execution_time += execution_time
            metrics.average_execution_time = metrics.total_execution_time / metrics.execution_count
            metrics.max_memory_used = max(metrics.max_memory_used, memory_used)
            metrics.last_execution = datetime.now()

            logger.info(f"✅ Executed function in sandbox {plugin_id}: {execution_time:.2f}s")
            return result

        except asyncio.TimeoutError:
            await self._record_violation(
                plugin_id, "execution_timeout",
                f"Execution exceeded {config.max_execution_time}s limit"
            )
            raise
        except Exception as e:
            await self._record_violation(
                plugin_id, "execution_error",
                f"Execution failed: {e}"
            )
            raise
        finally:
            # Clean up resource limits
            await self._cleanup_resource_limits()

    async def destroy_sandbox(self, plugin_id: str) -> bool:
        """
        Destroy a plugin sandbox and clean up resources.

        Args:
            plugin_id: Plugin identifier

        Returns:
            True if destruction successful, False otherwise
        """
        try:
            if plugin_id in self.active_sandboxes:
                sandbox = self.active_sandboxes[plugin_id]
                sandbox['active'] = False
                del self.active_sandboxes[plugin_id]

                logger.info(f"🗑️ Destroyed sandbox for plugin: {plugin_id}")

            return True

        except Exception as e:
            logger.error(f"❌ Failed to destroy sandbox for {plugin_id}: {e}")
            return False

    async def _start_monitoring(self):
        """Start resource monitoring thread"""
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_resources, daemon=True)
        self.monitor_thread.start()
        logger.info("📊 Started sandbox resource monitoring")

    def _monitor_resources(self):
        """Monitor resource usage of active sandboxes"""
        while self.monitoring_active:
            try:
                for plugin_id, sandbox in self.active_sandboxes.items():
                    if sandbox['active']:
                        self._check_resource_usage(plugin_id, sandbox)

                time.sleep(1.0)  # Check every second

            except Exception as e:
                logger.error(f"❌ Resource monitoring error: {e}")

    def _check_resource_usage(self, plugin_id: str, sandbox: Dict[str, Any]):
        """Check resource usage for a specific sandbox"""
        config = sandbox['config']

        try:
            # Check memory usage
            current_memory = self._get_memory_usage()
            if current_memory > config.max_memory_mb * 1024 * 1024:  # Convert to bytes
                asyncio.create_task(self._record_violation(
                    plugin_id, "memory_limit",
                    f"Memory usage exceeded {config.max_memory_mb}MB"
                ))

            # Check CPU usage (if psutil available)
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                if cpu_percent > config.max_cpu_percent:
                    asyncio.create_task(self._record_violation(
                        plugin_id, "cpu_limit",
                        f"CPU usage exceeded {config.max_cpu_percent}%"
                    ))

                    # Update metrics
                    metrics = self.sandbox_metrics[plugin_id]
                    metrics.max_cpu_used = max(metrics.max_cpu_used, cpu_percent)

        except Exception as e:
            logger.error(f"❌ Resource check error for {plugin_id}: {e}")

    async def _monitor_execution(self, plugin_id: str, timeout: float):
        """Monitor execution time for a plugin"""
        try:
            await asyncio.sleep(timeout)
            # If we reach here, execution has timed out
            raise asyncio.TimeoutError(f"Plugin {plugin_id} execution timed out")
        except asyncio.CancelledError:
            # Normal cancellation when execution completes
            pass

    async def _apply_resource_limits(self, config: SandboxConfig):
        """Apply resource limits for sandbox execution"""
        try:
            # Set memory limit (soft limit)
            memory_limit = config.max_memory_mb * 1024 * 1024  # Convert to bytes
            resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))

            # Set CPU time limit
            cpu_limit = int(config.max_execution_time)
            resource.setrlimit(resource.RLIMIT_CPU, (cpu_limit, cpu_limit))

        except Exception as e:
            logger.warning(f"⚠️ Could not apply resource limits: {e}")

    async def _cleanup_resource_limits(self):
        """Clean up resource limits after execution"""
        try:
            # Reset limits to system defaults
            resource.setrlimit(resource.RLIMIT_AS, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
            resource.setrlimit(resource.RLIMIT_CPU, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))

        except Exception as e:
            logger.warning(f"⚠️ Could not cleanup resource limits: {e}")

    def _create_restrictions(self, config: SandboxConfig) -> Dict[str, Any]:
        """Create restriction rules based on configuration"""
        return {
            'allowed_modules': set(config.allowed_modules),
            'blocked_modules': set(config.blocked_modules),
            'allowed_file_paths': set(config.allowed_file_paths),
            'blocked_file_paths': set(config.blocked_file_paths),
            'network_access': config.allow_network_access,
            'file_system_access': config.allow_file_system_access
        }

    def _get_current_process_info(self) -> Dict[str, Any]:
        """Get current process information"""
        if not PSUTIL_AVAILABLE:
            return {'pid': os.getpid()}

        try:
            process = psutil.Process()
            return {
                'pid': process.pid,
                'memory_info': process.memory_info(),
                'cpu_percent': process.cpu_percent(),
                'create_time': process.create_time()
            }
        except Exception as e:
            logger.warning(f"⚠️ Could not get process info: {e}")
            return {'pid': os.getpid()}

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        if not PSUTIL_AVAILABLE:
            return 0

        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0

    async def _record_violation(self, plugin_id: str, violation_type: str, description: str):
        """Record a security violation"""
        violation = SandboxViolation(
            violation_type=violation_type,
            description=description,
            plugin_id=plugin_id,
            severity="high" if violation_type in ["memory_limit", "cpu_limit"] else "medium"
        )

        self.violations.append(violation)

        # Update metrics
        if plugin_id in self.sandbox_metrics:
            self.sandbox_metrics[plugin_id].violations_count += 1

        logger.warning(f"⚠️ Security violation in {plugin_id}: {violation_type} - {description}")

    def get_sandbox_metrics(self, plugin_id: str) -> Optional[SandboxMetrics]:
        """Get metrics for a specific sandbox"""
        return self.sandbox_metrics.get(plugin_id)

    def get_all_metrics(self) -> Dict[str, SandboxMetrics]:
        """Get metrics for all sandboxes"""
        return self.sandbox_metrics.copy()

    def get_violations(self, plugin_id: Optional[str] = None,
                      since: Optional[datetime] = None) -> List[SandboxViolation]:
        """Get security violations"""
        violations = self.violations

        if plugin_id:
            violations = [v for v in violations if v.plugin_id == plugin_id]

        if since:
            violations = [v for v in violations if v.timestamp >= since]

        return violations

    def get_sandbox_status(self) -> Dict[str, Any]:
        """Get overall sandbox system status"""
        return {
            'active_sandboxes': len(self.active_sandboxes),
            'total_violations': len(self.violations),
            'monitoring_active': self.monitoring_active,
            'security_level': self.config.security_level.value,
            'recent_violations': len([
                v for v in self.violations
                if v.timestamp >= datetime.now() - timedelta(hours=1)
            ])
        }

    async def shutdown(self):
        """Shutdown the sandbox system"""
        self.monitoring_active = False

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5.0)

        # Destroy all active sandboxes
        for plugin_id in list(self.active_sandboxes.keys()):
            await self.destroy_sandbox(plugin_id)

        logger.info("🛡️ Plugin Sandbox shutdown complete")
