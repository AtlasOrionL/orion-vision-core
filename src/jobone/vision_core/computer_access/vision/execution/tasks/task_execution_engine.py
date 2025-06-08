#!/usr/bin/env python3
"""
Task Execution Engine Module - Q01.2.4 Implementation
Otonom AI agent'ı kullanarak basit görevleri yürüten motor
ORION VISION CORE - DUYGULANDIK! SEN YAPARSIN! HEP BİRLİKTE! 💖
"""

import time
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import our autonomous action system
try:
    from ...integration.autonomous.autonomous_action_system import AutonomousActionSystem
except ImportError:
    try:
        from autonomous_action_system import AutonomousActionSystem
    except ImportError:
        AutonomousActionSystem = None

logger = logging.getLogger(__name__)

class TaskType(Enum):
    """Types of tasks that can be executed"""
    SIMPLE_CLICK = "simple_click"
    FORM_FILLING = "form_filling"
    NAVIGATION = "navigation"
    SEARCH = "search"
    DATA_ENTRY = "data_entry"
    WORKFLOW = "workflow"

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskStep:
    """Individual step in a task"""
    step_id: int
    description: str
    action_type: str
    parameters: Dict[str, Any]
    expected_outcome: str
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class Task:
    """Task definition"""
    task_id: str
    title: str
    description: str
    task_type: TaskType
    steps: List[TaskStep]
    priority: int = 5  # 1-10, 10 being highest
    timeout: float = 300.0  # 5 minutes default
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

@dataclass
class TaskResult:
    """Task execution result"""
    task_id: str
    status: TaskStatus
    execution_time: float
    steps_completed: int
    steps_total: int
    success_rate: float
    error_message: Optional[str] = None
    step_results: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.step_results is None:
            self.step_results = []

class TaskExecutionEngine:
    """
    Q01.2.4: Basit Görev Yürütme Motoru
    
    Otonom AI agent'ı kullanarak basit görevleri yürüten motor
    DUYGULANDIK! SEN YAPARSIN! HEP BİRLİKTE! 💖
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.vision.task_engine')
        
        # Engine settings
        self.max_concurrent_tasks = 1  # For now, execute one task at a time
        self.default_step_timeout = 30.0
        self.retry_delay = 2.0
        
        # Task parsing patterns
        self.task_patterns = {
            'click': r'click\s+(?:on\s+)?(?:the\s+)?(.+)',
            'type': r'type\s+["\'](.+)["\'](?:\s+(?:in|into)\s+(.+))?',
            'search': r'search\s+(?:for\s+)?["\'](.+)["\']',
            'navigate': r'(?:go\s+to|navigate\s+to|open)\s+(.+)',
            'fill': r'fill\s+(?:in\s+)?(.+)\s+with\s+["\'](.+)["\']'
        }
        
        # Performance tracking
        self.total_tasks = 0
        self.completed_tasks = 0
        self.failed_tasks = 0
        self.total_execution_time = 0.0
        self.task_history: List[TaskResult] = []
        
        # Component instances
        self.autonomous_system = None
        
        self.initialized = False
        
        self.logger.info("🤖 Task Execution Engine initialized - DUYGULANDIK!")
    
    def initialize(self) -> bool:
        """Initialize task execution engine"""
        try:
            self.logger.info("🚀 Initializing Task Execution Engine...")
            self.logger.info("💖 DUYGULANDIK! SEN YAPARSIN!")
            self.logger.info("🧘‍♂️ Sabırla son adımı tamamlıyoruz...")
            
            # Initialize Autonomous Action System
            self.logger.info("🤖 Autonomous System başlatılıyor...")
            self.autonomous_system = AutonomousActionSystem()
            if not self.autonomous_system.initialize():
                self.logger.error("❌ Autonomous System initialization failed")
                return False
            self.logger.info("✅ Autonomous System hazır!")
            
            # Test system integration
            self.logger.info("🧪 Engine integration test yapılıyor...")
            test_result = self._test_engine_integration()
            
            if test_result['success']:
                self.initialized = True
                self.logger.info("🎉 Task Execution Engine başarıyla başlatıldı!")
                self.logger.info("💖 DUYGULANDIK! GÖREV MOTORU READY!")
                return True
            else:
                self.logger.error(f"❌ Engine integration test failed: {test_result.get('error')}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Task engine initialization error: {e}")
            return False
    
    def _test_engine_integration(self) -> Dict[str, Any]:
        """Test engine integration"""
        try:
            # Test autonomous system is ready
            if not self.autonomous_system or not self.autonomous_system.initialized:
                return {'success': False, 'error': 'Autonomous system not ready'}
            
            return {'success': True, 'method': 'engine_integration_test'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def parse_task_description(self, description: str) -> Task:
        """
        Parse natural language task description into structured task
        
        Args:
            description: Natural language task description
            
        Returns:
            Structured Task object
        """
        task_id = f"task_{int(time.time())}"
        description = description.strip()
        
        self.logger.info(f"📝 Parsing task: '{description}'")
        
        # Determine task type and create steps
        steps = []
        task_type = TaskType.SIMPLE_CLICK  # Default
        
        # Split description into sentences for multi-step tasks
        sentences = re.split(r'[.!;]|\s+and\s+|\s+then\s+', description.lower())
        sentences = [s.strip() for s in sentences if s.strip()]
        
        step_id = 1
        for sentence in sentences:
            step = self._parse_sentence_to_step(step_id, sentence)
            if step:
                steps.append(step)
                step_id += 1
        
        # If no steps parsed, create a general step
        if not steps:
            steps.append(TaskStep(
                step_id=1,
                description=description,
                action_type="general",
                parameters={'goal': description},
                expected_outcome="Task completed successfully"
            ))
        
        # Determine task type based on steps
        if len(steps) > 1:
            task_type = TaskType.WORKFLOW
        elif any('search' in step.action_type for step in steps):
            task_type = TaskType.SEARCH
        elif any('type' in step.action_type for step in steps):
            task_type = TaskType.FORM_FILLING
        elif any('navigate' in step.action_type for step in steps):
            task_type = TaskType.NAVIGATION
        
        task = Task(
            task_id=task_id,
            title=f"Task: {description[:50]}...",
            description=description,
            task_type=task_type,
            steps=steps
        )
        
        self.logger.info(f"📋 Task parsed: {len(steps)} steps, type: {task_type.value}")
        return task
    
    def _parse_sentence_to_step(self, step_id: int, sentence: str) -> Optional[TaskStep]:
        """Parse a sentence into a task step"""
        sentence = sentence.strip()
        if not sentence:
            return None
        
        # Try to match patterns
        for action_type, pattern in self.task_patterns.items():
            match = re.search(pattern, sentence, re.IGNORECASE)
            if match:
                if action_type == 'click':
                    target = match.group(1).strip()
                    return TaskStep(
                        step_id=step_id,
                        description=f"Click on {target}",
                        action_type="click",
                        parameters={'target': target},
                        expected_outcome=f"Successfully clicked on {target}"
                    )
                
                elif action_type == 'type':
                    text = match.group(1).strip()
                    target = match.group(2).strip() if match.group(2) else "input field"
                    return TaskStep(
                        step_id=step_id,
                        description=f"Type '{text}' in {target}",
                        action_type="type",
                        parameters={'text': text, 'target': target},
                        expected_outcome=f"Successfully typed '{text}'"
                    )
                
                elif action_type == 'search':
                    query = match.group(1).strip()
                    return TaskStep(
                        step_id=step_id,
                        description=f"Search for '{query}'",
                        action_type="search",
                        parameters={'query': query},
                        expected_outcome=f"Successfully searched for '{query}'"
                    )
                
                elif action_type == 'navigate':
                    destination = match.group(1).strip()
                    return TaskStep(
                        step_id=step_id,
                        description=f"Navigate to {destination}",
                        action_type="navigate",
                        parameters={'destination': destination},
                        expected_outcome=f"Successfully navigated to {destination}"
                    )
                
                elif action_type == 'fill':
                    field = match.group(1).strip()
                    value = match.group(2).strip()
                    return TaskStep(
                        step_id=step_id,
                        description=f"Fill {field} with '{value}'",
                        action_type="fill",
                        parameters={'field': field, 'value': value},
                        expected_outcome=f"Successfully filled {field}"
                    )
        
        # If no pattern matched, create a general step
        return TaskStep(
            step_id=step_id,
            description=sentence,
            action_type="general",
            parameters={'goal': sentence},
            expected_outcome="Step completed successfully"
        )
    
    def execute_task(self, task: Task) -> TaskResult:
        """
        Execute a structured task
        
        Args:
            task: Task to execute
            
        Returns:
            Task execution result
        """
        if not self.initialized:
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                execution_time=0.0,
                steps_completed=0,
                steps_total=len(task.steps),
                success_rate=0.0,
                error_message="Engine not initialized"
            )
        
        start_time = time.time()
        self.total_tasks += 1
        
        self.logger.info(f"🚀 Executing Task {task.task_id}: '{task.title}'")
        self.logger.info(f"📋 Task type: {task.task_type.value}, Steps: {len(task.steps)}")
        
        try:
            step_results = []
            steps_completed = 0
            
            for step in task.steps:
                self.logger.info(f"⚡ Executing Step {step.step_id}: {step.description}")
                
                step_result = self._execute_step(step)
                step_results.append(step_result)
                
                if step_result['success']:
                    steps_completed += 1
                    self.logger.info(f"✅ Step {step.step_id} completed successfully")
                else:
                    self.logger.warning(f"⚠️ Step {step.step_id} failed: {step_result.get('error')}")
                    
                    # Retry logic
                    if step.retry_count < step.max_retries:
                        step.retry_count += 1
                        self.logger.info(f"🔄 Retrying step {step.step_id} (attempt {step.retry_count})")
                        time.sleep(self.retry_delay)
                        
                        retry_result = self._execute_step(step)
                        step_results.append(retry_result)
                        
                        if retry_result['success']:
                            steps_completed += 1
                            self.logger.info(f"✅ Step {step.step_id} completed on retry")
                        else:
                            self.logger.error(f"❌ Step {step.step_id} failed after retry")
                            break
                    else:
                        self.logger.error(f"❌ Step {step.step_id} failed after max retries")
                        break
                
                # Small delay between steps
                time.sleep(0.5)
            
            # Calculate results
            total_time = time.time() - start_time
            self.total_execution_time += total_time
            success_rate = steps_completed / len(task.steps)
            
            # Determine final status
            if success_rate >= 0.8:  # 80% success threshold
                status = TaskStatus.COMPLETED
                self.completed_tasks += 1
            else:
                status = TaskStatus.FAILED
                self.failed_tasks += 1
            
            result = TaskResult(
                task_id=task.task_id,
                status=status,
                execution_time=total_time,
                steps_completed=steps_completed,
                steps_total=len(task.steps),
                success_rate=success_rate,
                step_results=step_results
            )
            
            # Store in history
            self.task_history.append(result)
            
            self.logger.info(f"🎉 Task {task.task_id} execution completed!")
            self.logger.info(f"📊 Status: {status.value}, Success rate: {success_rate:.1%}")
            self.logger.info(f"⏱️ Total time: {total_time:.3f}s")
            self.logger.info("💖 DUYGULANDIK! GÖREV TAMAMLANDI!")
            
            return result
            
        except Exception as e:
            total_time = time.time() - start_time
            self.failed_tasks += 1
            
            result = TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                execution_time=total_time,
                steps_completed=0,
                steps_total=len(task.steps),
                success_rate=0.0,
                error_message=str(e)
            )
            
            self.task_history.append(result)
            self.logger.error(f"❌ Task {task.task_id} execution failed: {e}")
            
            return result
    
    def _execute_step(self, step: TaskStep) -> Dict[str, Any]:
        """Execute a single task step"""
        start_time = time.time()
        
        try:
            # Map step action to autonomous system goal
            if step.action_type == "click":
                target = step.parameters.get('target', '')
                goal = f"Click on {target}"
                
            elif step.action_type == "type":
                text = step.parameters.get('text', '')
                target = step.parameters.get('target', 'input field')
                goal = f"Type '{text}' in {target}"
                
            elif step.action_type == "search":
                query = step.parameters.get('query', '')
                goal = f"Search for '{query}'"
                
            elif step.action_type == "navigate":
                destination = step.parameters.get('destination', '')
                goal = f"Navigate to {destination}"
                
            elif step.action_type == "fill":
                field = step.parameters.get('field', '')
                value = step.parameters.get('value', '')
                goal = f"Fill {field} with '{value}'"
                
            else:  # general
                goal = step.parameters.get('goal', step.description)
            
            # Execute using autonomous system
            result = self.autonomous_system.analyze_and_act(goal, max_actions=3)
            
            execution_time = time.time() - start_time
            
            return {
                'success': result.get('success', False),
                'step_id': step.step_id,
                'execution_time': execution_time,
                'goal': goal,
                'autonomous_result': result,
                'error': result.get('error') if not result.get('success') else None
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            return {
                'success': False,
                'step_id': step.step_id,
                'execution_time': execution_time,
                'error': str(e)
            }

    def execute_task_from_description(self, description: str) -> TaskResult:
        """
        Parse and execute task from natural language description

        Args:
            description: Natural language task description

        Returns:
            Task execution result
        """
        self.logger.info(f"📝 Executing task from description: '{description}'")

        # Parse description into structured task
        task = self.parse_task_description(description)

        # Execute the task
        return self.execute_task(task)

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get engine performance statistics"""
        success_rate = self.completed_tasks / self.total_tasks if self.total_tasks > 0 else 0
        avg_execution_time = self.total_execution_time / self.total_tasks if self.total_tasks > 0 else 0

        return {
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'success_rate': success_rate,
            'total_execution_time': self.total_execution_time,
            'average_execution_time': avg_execution_time,
            'task_history_length': len(self.task_history),
            'initialized': self.initialized
        }

    def get_task_history(self, limit: int = 10) -> List[TaskResult]:
        """Get recent task execution history"""
        return self.task_history[-limit:] if limit > 0 else self.task_history

    def get_status(self) -> Dict[str, Any]:
        """Get current engine status"""
        return {
            'initialized': self.initialized,
            'components': {
                'autonomous_system': self.autonomous_system.initialized if self.autonomous_system else False
            },
            'capabilities': {
                'task_parsing': True,
                'natural_language_processing': True,
                'multi_step_execution': True,
                'retry_logic': True,
                'performance_tracking': True,
                'task_history': True
            },
            'supported_task_types': [task_type.value for task_type in TaskType],
            'performance': self.get_performance_stats(),
            'settings': {
                'max_concurrent_tasks': self.max_concurrent_tasks,
                'default_step_timeout': self.default_step_timeout,
                'retry_delay': self.retry_delay
            },
            'duygulandik_mode': True,  # DUYGULANDIK SPECIAL FLAG! 💖
            'sen_yaparsin_power': True,  # SEN YAPARSIN SPECIAL FLAG! 💪
            'hep_birlikte_spirit': True  # HEP BİRLİKTE SPECIAL FLAG! 🤝
        }

    def create_sample_tasks(self) -> List[Task]:
        """Create sample tasks for testing"""
        sample_descriptions = [
            "Click the submit button",
            "Type 'Hello World' in the search box and click search",
            "Navigate to the main menu and click settings",
            "Fill the name field with 'John Doe' and click save",
            "Search for 'artificial intelligence' and click the first result"
        ]

        tasks = []
        for desc in sample_descriptions:
            task = self.parse_task_description(desc)
            tasks.append(task)

        return tasks

    def run_sample_tasks(self) -> List[TaskResult]:
        """Run sample tasks for demonstration"""
        self.logger.info("🧪 Running sample tasks for demonstration...")

        sample_tasks = self.create_sample_tasks()
        results = []

        for i, task in enumerate(sample_tasks):
            self.logger.info(f"🔄 Running sample task {i+1}/{len(sample_tasks)}")
            result = self.execute_task(task)
            results.append(result)

            # Small delay between tasks
            time.sleep(1.0)

        # Print summary
        successful = sum(1 for r in results if r.status == TaskStatus.COMPLETED)
        self.logger.info(f"📊 Sample tasks completed: {successful}/{len(results)} successful")

        return results

    def shutdown(self):
        """Shutdown task execution engine"""
        self.logger.info("🛑 Shutting down Task Execution Engine")
        self.logger.info("💖 DUYGULANDIK! SEN YAPARSIN! HEP BİRLİKTE!")

        if self.autonomous_system:
            self.autonomous_system.shutdown()

        self.initialized = False
        self.logger.info("✅ Task Execution Engine shutdown complete")

# Global instance for easy access
task_execution_engine = TaskExecutionEngine()

def get_task_execution_engine() -> TaskExecutionEngine:
    """Get global task execution engine instance"""
    return task_execution_engine

def execute_task_simple(description: str) -> TaskResult:
    """
    Simple function to execute a task from description

    Args:
        description: Natural language task description

    Returns:
        Task execution result
    """
    engine = get_task_execution_engine()
    if not engine.initialized:
        engine.initialize()

    return engine.execute_task_from_description(description)
