#!/usr/bin/env python3
"""
Scenarios Module - High-level task scenario execution
"""

__version__ = "1.0.0"
__author__ = "Atlas-orion"

# Scenarios module imports
from .scenario_executor import ScenarioExecutor
from .task_planner import TaskPlanner
from .integration_manager import IntegrationManager
from .validation_engine import ValidationEngine

__all__ = [
    "ScenarioExecutor",
    "TaskPlanner", 
    "IntegrationManager",
    "ValidationEngine"
]

# Scenario module constants
SUPPORTED_SCENARIOS = [
    "terminal_only",
    "terminal_keyboard", 
    "screen_mouse_keyboard",
    "file_operations",
    "text_editing",
    "web_browsing",
    "application_control",
    "system_administration"
]

# Validation criteria
VALIDATION_CRITERIA = {
    "file_creation": {
        "method": "file_exists",
        "timeout": 10.0
    },
    "text_content": {
        "method": "content_match",
        "timeout": 5.0
    },
    "ui_interaction": {
        "method": "visual_verification",
        "timeout": 15.0
    },
    "command_execution": {
        "method": "output_verification",
        "timeout": 30.0
    }
}

# Performance targets
PERFORMANCE_TARGETS = {
    "scenario_execution": 60.0,    # seconds max per scenario
    "task_planning": 5.0,          # seconds max for planning
    "validation": 10.0,            # seconds max for validation
    "integration_overhead": 2.0    # seconds max overhead
}

def get_scenarios_info():
    """Get scenarios module information"""
    return {
        'module': 'computer_access.scenarios',
        'version': __version__,
        'author': __author__,
        'components': {
            'ScenarioExecutor': 'Main scenario execution engine',
            'TaskPlanner': 'Intelligent task planning and sequencing',
            'IntegrationManager': 'Module integration and coordination',
            'ValidationEngine': 'Scenario validation and verification'
        },
        'capabilities': [
            'High-level task automation',
            'Multi-module coordination',
            'Intelligent task planning',
            'Real-time validation',
            'Error recovery',
            'Performance monitoring',
            'Scenario templating',
            'Custom scenario creation'
        ],
        'supported_scenarios': SUPPORTED_SCENARIOS,
        'validation_criteria': VALIDATION_CRITERIA,
        'performance_targets': PERFORMANCE_TARGETS
    }

def get_scenario_templates():
    """Get predefined scenario templates"""
    return {
        'terminal_file_creation': {
            'description': 'Create file using terminal commands',
            'steps': [
                {'type': 'terminal', 'action': 'create_file', 'params': {'filename': 'test.txt'}},
                {'type': 'terminal', 'action': 'write_content', 'params': {'content': 'Hello Orion'}},
                {'type': 'validation', 'action': 'verify_file', 'params': {'filename': 'test.txt'}}
            ],
            'validation': 'file_creation',
            'timeout': 30.0
        },
        'text_editor_interaction': {
            'description': 'Open text editor and create content',
            'steps': [
                {'type': 'vision', 'action': 'find_element', 'params': {'element': 'text_editor'}},
                {'type': 'mouse', 'action': 'click', 'params': {'target': 'text_editor'}},
                {'type': 'keyboard', 'action': 'type_text', 'params': {'text': 'Orion Vision Core Test'}},
                {'type': 'keyboard', 'action': 'shortcut', 'params': {'shortcut': 'save'}},
                {'type': 'validation', 'action': 'verify_content', 'params': {'expected': 'Orion Vision Core Test'}}
            ],
            'validation': 'ui_interaction',
            'timeout': 45.0
        },
        'web_form_filling': {
            'description': 'Fill web form using vision and input',
            'steps': [
                {'type': 'vision', 'action': 'find_form', 'params': {'form_type': 'contact'}},
                {'type': 'input_coordinator', 'action': 'fill_form', 'params': {
                    'fields': [
                        {'name': 'name', 'value': 'Orion AI'},
                        {'name': 'email', 'value': 'orion@ai.com'},
                        {'name': 'message', 'value': 'Testing autonomous form filling'}
                    ]
                }},
                {'type': 'validation', 'action': 'verify_form_data', 'params': {}}
            ],
            'validation': 'ui_interaction',
            'timeout': 60.0
        }
    }

# Scenario execution modes
class ScenarioMode:
    """Scenario execution modes"""
    STEP_BY_STEP = "step_by_step"
    CONTINUOUS = "continuous"
    INTERACTIVE = "interactive"
    BATCH = "batch"

# Error handling strategies
class ErrorStrategy:
    """Error handling strategies"""
    ABORT = "abort"
    RETRY = "retry"
    SKIP = "skip"
    FALLBACK = "fallback"

# Scenario status
class ScenarioStatus:
    """Scenario execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

# Performance monitoring
class ScenariosMetrics:
    """Scenarios performance metrics tracking"""
    
    def __init__(self):
        self.scenarios_executed = 0
        self.successful_scenarios = 0
        self.failed_scenarios = 0
        self.total_execution_time = 0.0
        self.planning_time = 0.0
        self.validation_time = 0.0
        self.integration_overhead = 0.0
        
        # Detailed tracking
        self.scenario_times = {}
        self.step_times = {}
        self.error_counts = {}
    
    def record_scenario_start(self, scenario_id: str):
        """Record scenario start"""
        self.scenario_times[scenario_id] = {'start': time.time()}
    
    def record_scenario_end(self, scenario_id: str, success: bool):
        """Record scenario completion"""
        if scenario_id in self.scenario_times:
            end_time = time.time()
            duration = end_time - self.scenario_times[scenario_id]['start']
            self.scenario_times[scenario_id]['end'] = end_time
            self.scenario_times[scenario_id]['duration'] = duration
            
            self.scenarios_executed += 1
            self.total_execution_time += duration
            
            if success:
                self.successful_scenarios += 1
            else:
                self.failed_scenarios += 1
    
    def record_planning_time(self, duration: float):
        """Record task planning time"""
        self.planning_time += duration
    
    def record_validation_time(self, duration: float):
        """Record validation time"""
        self.validation_time += duration
    
    def record_integration_overhead(self, duration: float):
        """Record integration overhead"""
        self.integration_overhead += duration
    
    def record_error(self, error_type: str):
        """Record error occurrence"""
        if error_type not in self.error_counts:
            self.error_counts[error_type] = 0
        self.error_counts[error_type] += 1
    
    def get_summary(self):
        """Get performance metrics summary"""
        avg_execution_time = self.total_execution_time / max(self.scenarios_executed, 1)
        success_rate = (self.successful_scenarios / max(self.scenarios_executed, 1)) * 100
        
        return {
            'scenarios_executed': self.scenarios_executed,
            'successful_scenarios': self.successful_scenarios,
            'failed_scenarios': self.failed_scenarios,
            'success_rate': success_rate,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_execution_time,
            'planning_time': self.planning_time,
            'validation_time': self.validation_time,
            'integration_overhead': self.integration_overhead,
            'error_counts': self.error_counts.copy(),
            'performance_targets_met': {
                'execution_time': avg_execution_time <= PERFORMANCE_TARGETS['scenario_execution'],
                'planning_time': self.planning_time <= PERFORMANCE_TARGETS['task_planning'],
                'validation_time': self.validation_time <= PERFORMANCE_TARGETS['validation'],
                'integration_overhead': self.integration_overhead <= PERFORMANCE_TARGETS['integration_overhead']
            }
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.__init__()

# Global metrics instance
scenarios_metrics = ScenariosMetrics()

# Logging configuration
import logging
import time

def setup_scenarios_logging():
    """Setup logging for scenarios module"""
    logger = logging.getLogger('orion.computer_access.scenarios')
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

# Initialize logging
scenarios_logger = setup_scenarios_logging()

# Module initialization message
scenarios_logger.info("🎯 Scenarios Module initialized")
scenarios_logger.info(f"📊 Version: {__version__}")
scenarios_logger.info(f"👤 Author: {__author__}")
scenarios_logger.info(f"🎮 Supported Scenarios: {len(SUPPORTED_SCENARIOS)}")
scenarios_logger.info("🚀 Ready for high-level task automation")
