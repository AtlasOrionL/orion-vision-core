#!/usr/bin/env python3
"""
🧠 Behavior Core - Gaming AI

Core behavior system for advanced AI behaviors.

Sprint 4 - Task 4.2 Module 1: Behavior Core
- Basic behavior framework
- Behavior execution engine
- Simple behavior patterns
- Performance tracking

Author: Nexus - Quantum AI Architect
Sprint: 4.2.1 - Advanced Gaming Features
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

class BehaviorType(Enum):
    """Basic behavior types"""
    IDLE = "idle"
    MOVE = "move"
    ATTACK = "attack"
    DEFEND = "defend"
    SUPPORT = "support"
    RETREAT = "retreat"
    PATROL = "patrol"
    FOLLOW = "follow"

class BehaviorState(Enum):
    """Behavior execution states"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    INTERRUPTED = "interrupted"

class BehaviorPriority(Enum):
    """Behavior priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class BehaviorAction:
    """Single behavior action"""
    action_id: str
    action_type: str
    parameters: Dict[str, Any]
    duration: float = 1.0
    priority: BehaviorPriority = BehaviorPriority.NORMAL

@dataclass
class Behavior:
    """Complete behavior definition"""
    behavior_id: str
    behavior_type: BehaviorType
    name: str
    description: str
    actions: List[BehaviorAction]
    conditions: Dict[str, Any] = field(default_factory=dict)
    state: BehaviorState = BehaviorState.INACTIVE
    created_at: float = 0.0
    last_executed: float = 0.0
    execution_count: int = 0
    success_rate: float = 0.0

@dataclass
class BehaviorMetrics:
    """Behavior system metrics"""
    behaviors_created: int = 0
    behaviors_executed: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0

class BehaviorCore:
    """
    Core Behavior System for Gaming AI
    
    Features:
    - Basic behavior framework
    - Behavior execution engine
    - Simple behavior patterns
    - Performance tracking
    - Extensible architecture
    """
    
    def __init__(self):
        self.logger = logging.getLogger("BehaviorCore")
        
        # Behavior management
        self.behaviors = {}  # behavior_id -> Behavior
        self.behavior_templates = {}  # behavior_type -> template
        self.active_behaviors = {}  # agent_id -> behavior_id
        
        # Execution engine
        self.execution_queue = deque(maxlen=1000)
        self.execution_lock = threading.RLock()
        self.execution_active = False
        self.execution_thread = None
        
        # Performance tracking
        self.metrics = BehaviorMetrics()
        self.execution_history = deque(maxlen=500)
        
        # Behavior callbacks
        self.behavior_callbacks = {}  # behavior_type -> callback_function
        
        # Initialize basic behavior templates
        self._initialize_behavior_templates()
        
        self.logger.info("🧠 Behavior Core initialized")
    
    def _initialize_behavior_templates(self):
        """Initialize basic behavior templates"""
        self.behavior_templates = {
            BehaviorType.IDLE: {
                "name": "Idle Behavior",
                "description": "Agent waits and observes",
                "actions": [
                    {
                        "action_type": "wait",
                        "parameters": {"duration": 1.0},
                        "duration": 1.0
                    }
                ],
                "conditions": {}
            },
            
            BehaviorType.MOVE: {
                "name": "Movement Behavior", 
                "description": "Agent moves to target position",
                "actions": [
                    {
                        "action_type": "move_to",
                        "parameters": {"target": None, "speed": 1.0},
                        "duration": 2.0
                    }
                ],
                "conditions": {"target_position": "required"}
            },
            
            BehaviorType.ATTACK: {
                "name": "Attack Behavior",
                "description": "Agent attacks target",
                "actions": [
                    {
                        "action_type": "aim",
                        "parameters": {"target": None},
                        "duration": 0.5
                    },
                    {
                        "action_type": "fire",
                        "parameters": {"weapon": "primary"},
                        "duration": 0.2
                    }
                ],
                "conditions": {"target": "required", "weapon_ready": True}
            },
            
            BehaviorType.DEFEND: {
                "name": "Defensive Behavior",
                "description": "Agent takes defensive position",
                "actions": [
                    {
                        "action_type": "take_cover",
                        "parameters": {"cover_type": "any"},
                        "duration": 1.0
                    },
                    {
                        "action_type": "watch",
                        "parameters": {"direction": "forward"},
                        "duration": 3.0
                    }
                ],
                "conditions": {"threat_detected": True}
            },
            
            BehaviorType.SUPPORT: {
                "name": "Support Behavior",
                "description": "Agent provides support to allies",
                "actions": [
                    {
                        "action_type": "heal",
                        "parameters": {"target": "ally", "item": "medkit"},
                        "duration": 2.0
                    }
                ],
                "conditions": {"ally_injured": True, "has_medkit": True}
            }
        }
    
    def create_behavior(self, behavior_type: BehaviorType, 
                       custom_parameters: Optional[Dict[str, Any]] = None) -> str:
        """Create new behavior from template"""
        try:
            behavior_id = f"behavior_{int(time.time() * 1000000)}"
            
            # Get template
            if behavior_type not in self.behavior_templates:
                self.logger.error(f"❌ Unknown behavior type: {behavior_type}")
                return ""
            
            template = self.behavior_templates[behavior_type]
            
            # Create actions from template
            actions = []
            for i, action_template in enumerate(template["actions"]):
                action_id = f"{behavior_id}_action_{i}"
                
                # Merge custom parameters
                parameters = action_template["parameters"].copy()
                if custom_parameters:
                    parameters.update(custom_parameters)
                
                action = BehaviorAction(
                    action_id=action_id,
                    action_type=action_template["action_type"],
                    parameters=parameters,
                    duration=action_template.get("duration", 1.0)
                )
                actions.append(action)
            
            # Create behavior
            behavior = Behavior(
                behavior_id=behavior_id,
                behavior_type=behavior_type,
                name=template["name"],
                description=template["description"],
                actions=actions,
                conditions=template.get("conditions", {}),
                created_at=time.time()
            )
            
            # Store behavior
            self.behaviors[behavior_id] = behavior
            self.metrics.behaviors_created += 1
            
            self.logger.info(f"🧠 Behavior created: {behavior_type.value} ({behavior_id[:8]}...)")
            return behavior_id
            
        except Exception as e:
            self.logger.error(f"❌ Behavior creation failed: {e}")
            return ""
    
    def execute_behavior(self, agent_id: str, behavior_id: str, 
                        context: Dict[str, Any]) -> bool:
        """Execute behavior for agent"""
        try:
            if behavior_id not in self.behaviors:
                self.logger.error(f"❌ Unknown behavior: {behavior_id}")
                return False
            
            behavior = self.behaviors[behavior_id]
            
            # Check conditions
            if not self._check_behavior_conditions(behavior, context):
                self.logger.warning(f"⚠️ Behavior conditions not met: {behavior_id}")
                return False
            
            # Queue for execution
            execution_request = {
                "agent_id": agent_id,
                "behavior_id": behavior_id,
                "context": context.copy(),
                "timestamp": time.time()
            }
            
            with self.execution_lock:
                self.execution_queue.append(execution_request)
                self.active_behaviors[agent_id] = behavior_id
            
            self.logger.info(f"🎯 Behavior queued: {agent_id} -> {behavior.behavior_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Behavior execution failed: {e}")
            return False
    
    def _check_behavior_conditions(self, behavior: Behavior, context: Dict[str, Any]) -> bool:
        """Check if behavior conditions are met"""
        try:
            for condition_key, condition_value in behavior.conditions.items():
                if condition_value == "required":
                    if condition_key not in context:
                        return False
                elif isinstance(condition_value, bool):
                    if context.get(condition_key, False) != condition_value:
                        return False
                elif condition_key not in context:
                    return False
                elif context[condition_key] != condition_value:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Condition check failed: {e}")
            return False
    
    def start_execution_engine(self):
        """Start behavior execution engine"""
        if self.execution_active:
            return
        
        self.execution_active = True
        self.execution_thread = threading.Thread(target=self._execution_loop, daemon=True)
        self.execution_thread.start()
        self.logger.info("🔄 Behavior execution engine started")
    
    def stop_execution_engine(self):
        """Stop behavior execution engine"""
        self.execution_active = False
        if self.execution_thread:
            self.execution_thread.join(timeout=1.0)
        self.logger.info("🛑 Behavior execution engine stopped")
    
    def _execution_loop(self):
        """Main behavior execution loop"""
        while self.execution_active:
            try:
                # Process execution queue
                with self.execution_lock:
                    if self.execution_queue:
                        request = self.execution_queue.popleft()
                        self._process_execution_request(request)
                
                time.sleep(0.1)  # 100ms processing interval
                
            except Exception as e:
                self.logger.error(f"❌ Execution loop error: {e}")
                time.sleep(1.0)
    
    def _process_execution_request(self, request: Dict[str, Any]):
        """Process single execution request"""
        try:
            agent_id = request["agent_id"]
            behavior_id = request["behavior_id"]
            context = request["context"]
            
            if behavior_id not in self.behaviors:
                return
            
            behavior = self.behaviors[behavior_id]
            execution_start = time.time()
            
            # Update behavior state
            behavior.state = BehaviorState.EXECUTING
            behavior.last_executed = execution_start
            behavior.execution_count += 1
            
            # Execute actions
            success = self._execute_behavior_actions(agent_id, behavior, context)
            
            # Update behavior state and metrics
            execution_time = time.time() - execution_start
            
            if success:
                behavior.state = BehaviorState.COMPLETED
                self.metrics.successful_executions += 1
                
                # Update success rate
                total_executions = behavior.execution_count
                current_successes = behavior.success_rate * (total_executions - 1) + 1
                behavior.success_rate = current_successes / total_executions
                
            else:
                behavior.state = BehaviorState.FAILED
                self.metrics.failed_executions += 1
                
                # Update success rate
                total_executions = behavior.execution_count
                current_successes = behavior.success_rate * (total_executions - 1)
                behavior.success_rate = current_successes / total_executions
            
            # Update metrics
            self.metrics.behaviors_executed += 1
            self._update_execution_metrics(execution_time)
            
            # Record execution
            execution_record = {
                "agent_id": agent_id,
                "behavior_id": behavior_id,
                "behavior_type": behavior.behavior_type.value,
                "success": success,
                "execution_time": execution_time,
                "timestamp": execution_start
            }
            self.execution_history.append(execution_record)
            
            # Clear active behavior
            if agent_id in self.active_behaviors:
                del self.active_behaviors[agent_id]
            
            self.logger.debug(f"🎯 Behavior executed: {behavior.behavior_type.value} ({'✅' if success else '❌'})")
            
        except Exception as e:
            self.logger.error(f"❌ Execution processing failed: {e}")
    
    def _execute_behavior_actions(self, agent_id: str, behavior: Behavior, 
                                 context: Dict[str, Any]) -> bool:
        """Execute all actions in behavior"""
        try:
            for action in behavior.actions:
                # Execute action
                success = self._execute_single_action(agent_id, action, context)
                
                if not success:
                    self.logger.warning(f"⚠️ Action failed: {action.action_type}")
                    return False
                
                # Wait for action duration (simulated)
                time.sleep(min(action.duration, 0.1))  # Max 100ms for testing
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Action execution failed: {e}")
            return False
    
    def _execute_single_action(self, agent_id: str, action: BehaviorAction, 
                              context: Dict[str, Any]) -> bool:
        """Execute single action"""
        try:
            # Check if callback is registered for this action type
            if action.action_type in self.behavior_callbacks:
                callback = self.behavior_callbacks[action.action_type]
                return callback(agent_id, action, context)
            
            # Default action execution (simulation)
            self.logger.debug(f"🎬 Executing action: {action.action_type} for {agent_id}")
            
            # Simulate action success/failure
            import random
            success_rate = 0.8  # 80% success rate for simulation
            return random.random() < success_rate
            
        except Exception as e:
            self.logger.error(f"❌ Single action execution failed: {e}")
            return False
    
    def register_action_callback(self, action_type: str, callback: Callable):
        """Register callback for specific action type"""
        self.behavior_callbacks[action_type] = callback
        self.logger.info(f"📝 Action callback registered: {action_type}")
    
    def get_agent_behavior(self, agent_id: str) -> Optional[str]:
        """Get current behavior for agent"""
        return self.active_behaviors.get(agent_id)
    
    def stop_agent_behavior(self, agent_id: str) -> bool:
        """Stop current behavior for agent"""
        try:
            if agent_id in self.active_behaviors:
                behavior_id = self.active_behaviors[agent_id]
                
                if behavior_id in self.behaviors:
                    behavior = self.behaviors[behavior_id]
                    behavior.state = BehaviorState.INTERRUPTED
                
                del self.active_behaviors[agent_id]
                self.logger.info(f"🛑 Behavior stopped for {agent_id}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Behavior stop failed: {e}")
            return False
    
    def _update_execution_metrics(self, execution_time: float):
        """Update execution time metrics"""
        current_avg = self.metrics.average_execution_time
        executed_count = self.metrics.behaviors_executed
        
        if executed_count > 0:
            self.metrics.average_execution_time = (
                (current_avg * (executed_count - 1) + execution_time) / executed_count
            )
        else:
            self.metrics.average_execution_time = execution_time
    
    def get_behavior_metrics(self) -> Dict[str, Any]:
        """Get behavior system metrics"""
        return {
            "behaviors_created": self.metrics.behaviors_created,
            "behaviors_executed": self.metrics.behaviors_executed,
            "successful_executions": self.metrics.successful_executions,
            "failed_executions": self.metrics.failed_executions,
            "success_rate": (self.metrics.successful_executions / max(1, self.metrics.behaviors_executed)) * 100,
            "average_execution_time": self.metrics.average_execution_time,
            "active_behaviors": len(self.active_behaviors),
            "execution_queue_size": len(self.execution_queue),
            "execution_active": self.execution_active
        }
    
    def get_behavior_list(self) -> List[Dict[str, Any]]:
        """Get list of all behaviors"""
        return [
            {
                "behavior_id": behavior.behavior_id,
                "behavior_type": behavior.behavior_type.value,
                "name": behavior.name,
                "state": behavior.state.value,
                "execution_count": behavior.execution_count,
                "success_rate": behavior.success_rate,
                "last_executed": behavior.last_executed,
                "actions_count": len(behavior.actions)
            }
            for behavior in self.behaviors.values()
        ]

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧠 Behavior Core - Sprint 4 Test")
    print("=" * 60)
    
    # Create behavior core
    behavior_core = BehaviorCore()
    
    # Start execution engine
    behavior_core.start_execution_engine()
    
    # Test behavior creation
    print("\n🧠 Testing behavior creation...")
    
    behaviors = []
    for behavior_type in [BehaviorType.MOVE, BehaviorType.ATTACK, BehaviorType.DEFEND]:
        behavior_id = behavior_core.create_behavior(behavior_type)
        behaviors.append((behavior_type, behavior_id))
        print(f"   {behavior_type.value}: {behavior_id[:8]}...")
    
    # Test behavior execution
    print("\n🎯 Testing behavior execution...")
    
    test_contexts = [
        {"target_position": {"x": 100, "y": 100}},  # For MOVE
        {"target": "enemy_1", "weapon_ready": True},  # For ATTACK
        {"threat_detected": True}  # For DEFEND
    ]
    
    for i, (behavior_type, behavior_id) in enumerate(behaviors):
        context = test_contexts[i] if i < len(test_contexts) else {}
        success = behavior_core.execute_behavior(f"agent_{i+1}", behavior_id, context)
        print(f"   {behavior_type.value}: {'✅' if success else '❌'}")
    
    # Wait for execution
    time.sleep(1.0)
    
    # Get metrics
    metrics = behavior_core.get_behavior_metrics()
    print(f"\n📊 Behavior Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get behavior list
    behavior_list = behavior_core.get_behavior_list()
    print(f"\n🧠 Behavior Status:")
    for behavior in behavior_list:
        print(f"   {behavior['behavior_type']}: {behavior['state']} (success: {behavior['success_rate']:.1%})")
    
    # Stop execution engine
    behavior_core.stop_execution_engine()
    
    print("\n🎉 Sprint 4 - Task 4.2 Core Module test completed!")
    print("🎯 Core behavior system ready for extensions")
    print(f"📈 Current: {metrics['behaviors_created']} behaviors, {metrics['success_rate']:.1f}% success rate")
