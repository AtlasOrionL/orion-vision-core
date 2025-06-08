#!/usr/bin/env python3
"""
Scenario Executor - Main scenario execution engine
"""

import logging
import time
import threading
import uuid
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from . import ScenarioStatus, ScenarioMode, ErrorStrategy, scenarios_metrics

@dataclass
class ScenarioStep:
    """Individual scenario step definition"""
    step_id: str
    step_type: str  # 'terminal', 'mouse', 'keyboard', 'vision', 'input_coordinator', 'validation'
    action: str
    parameters: Dict[str, Any]
    timeout: float = 30.0
    retry_count: int = 3
    error_strategy: ErrorStrategy = ErrorStrategy.RETRY

@dataclass
class Scenario:
    """Complete scenario definition"""
    scenario_id: str
    name: str
    description: str
    steps: List[ScenarioStep]
    mode: ScenarioMode = ScenarioMode.CONTINUOUS
    timeout: float = 300.0
    validation_criteria: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class ScenarioResult:
    """Scenario execution result"""
    scenario_id: str
    status: ScenarioStatus
    success: bool
    steps_completed: int
    total_steps: int
    execution_time: float
    error_message: Optional[str] = None
    step_results: List[Dict[str, Any]] = None
    validation_result: Optional[Dict[str, Any]] = None

class ScenarioExecutor:
    """
    Main scenario execution engine
    Coordinates all computer access modules to execute complex scenarios
    """
    
    def __init__(self, computer_access_manager):
        self.logger = logging.getLogger('orion.computer_access.scenarios.executor')
        
        # Computer access manager reference
        self.computer_access_manager = computer_access_manager
        
        # Execution state
        self.initialized = False
        self.active_scenarios = {}
        self.completed_scenarios = {}
        
        # Components (will be set during initialization)
        self.task_planner = None
        self.integration_manager = None
        self.validation_engine = None
        
        # Threading
        self.execution_lock = threading.Lock()
        self.scenario_threads = {}
        
        # Performance tracking
        self.scenarios_executed = 0
        self.successful_scenarios = 0
        self.failed_scenarios = 0
        
        self.logger.info("🎯 ScenarioExecutor initialized")
    
    def initialize(self) -> bool:
        """
        Initialize scenario executor
        
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing scenario executor...")
            
            # Verify computer access manager is ready
            if not self.computer_access_manager or not self.computer_access_manager.initialized:
                raise RuntimeError("Computer access manager not ready")
            
            # Initialize components
            from .task_planner import TaskPlanner
            from .integration_manager import IntegrationManager
            from .validation_engine import ValidationEngine
            
            self.task_planner = TaskPlanner()
            self.integration_manager = IntegrationManager(self.computer_access_manager)
            self.validation_engine = ValidationEngine(self.computer_access_manager)
            
            # Initialize components
            if not self.task_planner.initialize():
                raise RuntimeError("Failed to initialize task planner")
            
            if not self.integration_manager.initialize():
                raise RuntimeError("Failed to initialize integration manager")
            
            if not self.validation_engine.initialize():
                raise RuntimeError("Failed to initialize validation engine")
            
            self.initialized = True
            self.logger.info("✅ Scenario executor initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Scenario executor initialization failed: {e}")
            return False
    
    def execute_scenario(self, parameters: Dict[str, Any]) -> ScenarioResult:
        """
        Execute a scenario
        
        Args:
            parameters: Scenario parameters including scenario definition or template name
            
        Returns:
            ScenarioResult: Execution result
        """
        if not self.initialized:
            raise RuntimeError("Scenario executor not initialized")
        
        start_time = time.time()
        
        try:
            # Parse scenario from parameters
            scenario = self._parse_scenario(parameters)
            
            # Record scenario start
            scenarios_metrics.record_scenario_start(scenario.scenario_id)
            
            self.logger.info(f"🎯 Executing scenario: {scenario.name}")
            self.logger.info(f"📋 Steps: {len(scenario.steps)}")
            
            with self.execution_lock:
                self.active_scenarios[scenario.scenario_id] = scenario
            
            # Execute scenario based on mode
            if scenario.mode == ScenarioMode.STEP_BY_STEP:
                result = self._execute_step_by_step(scenario)
            elif scenario.mode == ScenarioMode.CONTINUOUS:
                result = self._execute_continuous(scenario)
            elif scenario.mode == ScenarioMode.INTERACTIVE:
                result = self._execute_interactive(scenario)
            elif scenario.mode == ScenarioMode.BATCH:
                result = self._execute_batch(scenario)
            else:
                raise ValueError(f"Unknown scenario mode: {scenario.mode}")
            
            # Perform validation if specified
            if scenario.validation_criteria and result.success:
                validation_result = self.validation_engine.validate_scenario(
                    scenario, result
                )
                result.validation_result = validation_result
                
                # Update success based on validation
                if not validation_result.get('success', True):
                    result.success = False
                    result.error_message = validation_result.get('error', 'Validation failed')
            
            # Update metrics
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            scenarios_metrics.record_scenario_end(scenario.scenario_id, result.success)
            
            # Move to completed scenarios
            with self.execution_lock:
                self.active_scenarios.pop(scenario.scenario_id, None)
                self.completed_scenarios[scenario.scenario_id] = result
            
            if result.success:
                self.successful_scenarios += 1
                self.logger.info(f"✅ Scenario completed successfully: {scenario.name} ({execution_time:.3f}s)")
            else:
                self.failed_scenarios += 1
                self.logger.error(f"❌ Scenario failed: {scenario.name} - {result.error_message}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            # Create failure result
            result = ScenarioResult(
                scenario_id=parameters.get('scenario_id', str(uuid.uuid4())),
                status=ScenarioStatus.FAILED,
                success=False,
                steps_completed=0,
                total_steps=0,
                execution_time=execution_time,
                error_message=str(e)
            )
            
            self.failed_scenarios += 1
            scenarios_metrics.record_scenario_end(result.scenario_id, False)
            
            self.logger.error(f"❌ Scenario execution failed: {e}")
            return result
    
    def _parse_scenario(self, parameters: Dict[str, Any]) -> Scenario:
        """Parse scenario from parameters"""
        # Check if it's a predefined template
        template_name = parameters.get('template_name')
        if template_name:
            return self._create_from_template(template_name, parameters)
        
        # Check if it's a custom scenario
        scenario_definition = parameters.get('scenario')
        if scenario_definition:
            return self._create_from_definition(scenario_definition)
        
        # Check for individual scenario components
        scenario_id = parameters.get('scenario_id', str(uuid.uuid4()))
        name = parameters.get('name', 'Custom Scenario')
        description = parameters.get('description', 'Custom scenario execution')
        steps_data = parameters.get('steps', [])
        
        # Convert steps data to ScenarioStep objects
        steps = []
        for i, step_data in enumerate(steps_data):
            step = ScenarioStep(
                step_id=f"{scenario_id}_step_{i}",
                step_type=step_data.get('type', 'terminal'),
                action=step_data.get('action', ''),
                parameters=step_data.get('params', {}),
                timeout=step_data.get('timeout', 30.0),
                retry_count=step_data.get('retry_count', 3)
            )
            steps.append(step)
        
        return Scenario(
            scenario_id=scenario_id,
            name=name,
            description=description,
            steps=steps,
            mode=ScenarioMode(parameters.get('mode', ScenarioMode.CONTINUOUS)),
            timeout=parameters.get('timeout', 300.0),
            validation_criteria=parameters.get('validation_criteria')
        )
    
    def _create_from_template(self, template_name: str, parameters: Dict[str, Any]) -> Scenario:
        """Create scenario from predefined template"""
        from . import get_scenario_templates
        
        templates = get_scenario_templates()
        if template_name not in templates:
            raise ValueError(f"Unknown scenario template: {template_name}")
        
        template = templates[template_name]
        scenario_id = parameters.get('scenario_id', str(uuid.uuid4()))
        
        # Create steps from template
        steps = []
        for i, step_data in enumerate(template['steps']):
            step = ScenarioStep(
                step_id=f"{scenario_id}_step_{i}",
                step_type=step_data['type'],
                action=step_data['action'],
                parameters=step_data['params'],
                timeout=step_data.get('timeout', 30.0)
            )
            steps.append(step)
        
        return Scenario(
            scenario_id=scenario_id,
            name=template.get('name', template_name),
            description=template['description'],
            steps=steps,
            timeout=template.get('timeout', 300.0),
            validation_criteria=template.get('validation')
        )
    
    def _create_from_definition(self, definition: Dict[str, Any]) -> Scenario:
        """Create scenario from complete definition"""
        # This would parse a complete scenario definition
        # Implementation depends on the specific format used
        pass
    
    def _execute_continuous(self, scenario: Scenario) -> ScenarioResult:
        """Execute scenario continuously without pauses"""
        result = ScenarioResult(
            scenario_id=scenario.scenario_id,
            status=ScenarioStatus.RUNNING,
            success=True,
            steps_completed=0,
            total_steps=len(scenario.steps),
            execution_time=0.0,
            step_results=[]
        )
        
        try:
            for i, step in enumerate(scenario.steps):
                self.logger.info(f"🔄 Executing step {i+1}/{len(scenario.steps)}: {step.action}")
                
                step_result = self._execute_step(step)
                result.step_results.append(step_result)
                
                if step_result['success']:
                    result.steps_completed += 1
                else:
                    # Handle step failure based on error strategy
                    if step.error_strategy == ErrorStrategy.ABORT:
                        result.success = False
                        result.error_message = f"Step {i+1} failed: {step_result.get('error', 'Unknown error')}"
                        break
                    elif step.error_strategy == ErrorStrategy.SKIP:
                        self.logger.warning(f"⚠️ Skipping failed step {i+1}")
                        continue
                    elif step.error_strategy == ErrorStrategy.RETRY:
                        # Retry logic would go here
                        pass
                
                # Small delay between steps
                time.sleep(0.1)
            
            result.status = ScenarioStatus.COMPLETED if result.success else ScenarioStatus.FAILED
            
        except Exception as e:
            result.success = False
            result.status = ScenarioStatus.FAILED
            result.error_message = str(e)
        
        return result
    
    def _execute_step_by_step(self, scenario: Scenario) -> ScenarioResult:
        """Execute scenario step by step with pauses"""
        # Similar to continuous but with user interaction points
        return self._execute_continuous(scenario)
    
    def _execute_interactive(self, scenario: Scenario) -> ScenarioResult:
        """Execute scenario with user interaction"""
        # Interactive execution with user prompts
        return self._execute_continuous(scenario)
    
    def _execute_batch(self, scenario: Scenario) -> ScenarioResult:
        """Execute scenario in batch mode"""
        # Batch execution for multiple scenarios
        return self._execute_continuous(scenario)
    
    def _execute_step(self, step: ScenarioStep) -> Dict[str, Any]:
        """Execute individual scenario step"""
        start_time = time.time()
        
        try:
            # Route step to appropriate module
            if step.step_type == 'terminal':
                result = self.integration_manager.execute_terminal_action(step.action, step.parameters)
            elif step.step_type == 'mouse':
                result = self.integration_manager.execute_mouse_action(step.action, step.parameters)
            elif step.step_type == 'keyboard':
                result = self.integration_manager.execute_keyboard_action(step.action, step.parameters)
            elif step.step_type == 'vision':
                result = self.integration_manager.execute_vision_action(step.action, step.parameters)
            elif step.step_type == 'input_coordinator':
                result = self.integration_manager.execute_coordinated_action(step.action, step.parameters)
            elif step.step_type == 'validation':
                result = self.validation_engine.validate_step(step)
            else:
                raise ValueError(f"Unknown step type: {step.step_type}")
            
            execution_time = time.time() - start_time
            
            return {
                'step_id': step.step_id,
                'success': result.get('success', True),
                'result': result,
                'execution_time': execution_time,
                'error': result.get('error') if not result.get('success', True) else None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return {
                'step_id': step.step_id,
                'success': False,
                'result': None,
                'execution_time': execution_time,
                'error': str(e)
            }
    
    def get_active_scenarios(self) -> List[str]:
        """Get list of active scenario IDs"""
        with self.execution_lock:
            return list(self.active_scenarios.keys())
    
    def get_scenario_status(self, scenario_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific scenario"""
        with self.execution_lock:
            if scenario_id in self.active_scenarios:
                return {
                    'scenario_id': scenario_id,
                    'status': 'active',
                    'scenario': self.active_scenarios[scenario_id]
                }
            elif scenario_id in self.completed_scenarios:
                return {
                    'scenario_id': scenario_id,
                    'status': 'completed',
                    'result': self.completed_scenarios[scenario_id]
                }
        
        return None
    
    def cancel_scenario(self, scenario_id: str) -> bool:
        """Cancel running scenario"""
        with self.execution_lock:
            if scenario_id in self.active_scenarios:
                # In a full implementation, this would signal the execution thread to stop
                self.logger.info(f"🛑 Cancelling scenario: {scenario_id}")
                return True
        
        return False
    
    def is_ready(self) -> bool:
        """Check if scenario executor is ready"""
        return (self.initialized and 
                self.task_planner and self.task_planner.is_ready() and
                self.integration_manager and self.integration_manager.is_ready() and
                self.validation_engine and self.validation_engine.is_ready())
    
    def get_status(self) -> Dict[str, Any]:
        """Get scenario executor status"""
        return {
            'initialized': self.initialized,
            'scenarios_executed': self.scenarios_executed,
            'successful_scenarios': self.successful_scenarios,
            'failed_scenarios': self.failed_scenarios,
            'success_rate': (self.successful_scenarios / max(self.scenarios_executed, 1)) * 100,
            'active_scenarios': len(self.active_scenarios),
            'completed_scenarios': len(self.completed_scenarios),
            'components_ready': {
                'task_planner': self.task_planner.is_ready() if self.task_planner else False,
                'integration_manager': self.integration_manager.is_ready() if self.integration_manager else False,
                'validation_engine': self.validation_engine.is_ready() if self.validation_engine else False
            },
            'performance_metrics': scenarios_metrics.get_summary()
        }
    
    def shutdown(self):
        """Shutdown scenario executor"""
        self.logger.info("🛑 Shutting down scenario executor")
        
        # Cancel all active scenarios
        with self.execution_lock:
            for scenario_id in list(self.active_scenarios.keys()):
                self.cancel_scenario(scenario_id)
        
        # Shutdown components
        if self.task_planner:
            self.task_planner.shutdown()
        
        if self.integration_manager:
            self.integration_manager.shutdown()
        
        if self.validation_engine:
            self.validation_engine.shutdown()
        
        self.initialized = False
        self.logger.info("✅ Scenario executor shutdown complete")
