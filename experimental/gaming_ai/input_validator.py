#!/usr/bin/env python3
"""
🔍 Input Validator - Gaming AI

Comprehensive input validation and action queue management for 100% safe execution.

Sprint 2 - Task 2.3: Input Validation System
- Action queue management
- Input sanitization and validation
- Boundary checking system
- Action rollback mechanisms

Author: Nexus - Quantum AI Architect
Sprint: 2.3 - Control & Action System
"""

import time
import threading
import logging
import copy
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

# Import precision control and safety manager
try:
    from precision_control import PrecisionAction, ActionType, MovementType
    from safety_manager import SafetyManager, SafetyLevel
    CONTROL_MODULES_AVAILABLE = True
except ImportError:
    CONTROL_MODULES_AVAILABLE = False
    warnings.warn("🎮 Control modules not available", ImportWarning)

class ValidationResult(Enum):
    """Validation result enumeration"""
    VALID = "valid"
    INVALID = "invalid"
    BLOCKED = "blocked"
    QUEUED = "queued"
    ROLLBACK = "rollback"

class ActionStatus(Enum):
    """Action status enumeration"""
    PENDING = "pending"
    VALIDATED = "validated"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"

@dataclass
class ValidationRule:
    """Input validation rule"""
    rule_id: str
    rule_type: str  # 'boundary', 'type', 'range', 'custom'
    parameters: Dict[str, Any]
    error_message: str
    severity: str = "error"  # 'warning', 'error', 'critical'

@dataclass
class ActionContext:
    """Action execution context"""
    action_id: str
    action: PrecisionAction
    timestamp: float
    status: ActionStatus
    validation_results: List[Tuple[str, ValidationResult, str]]
    retry_count: int = 0
    rollback_data: Optional[Dict[str, Any]] = None

@dataclass
class BoundaryLimits:
    """Screen boundary limits"""
    min_x: int = 0
    min_y: int = 0
    max_x: int = 1920
    max_y: int = 1080
    safe_margin: int = 10

@dataclass
class ValidationMetrics:
    """Validation performance metrics"""
    actions_validated: int = 0
    actions_blocked: int = 0
    actions_rolled_back: int = 0
    validation_errors: int = 0
    average_validation_time: float = 0.0

class InputValidator:
    """
    Comprehensive Input Validation System for Gaming AI
    
    Features:
    - Action queue management with priority handling
    - Input sanitization and validation
    - Boundary checking and constraint enforcement
    - Action rollback mechanisms
    - Real-time validation metrics
    """
    
    def __init__(self, safety_manager: Optional[SafetyManager] = None):
        self.logger = logging.getLogger("InputValidator")
        
        # Safety integration
        self.safety_manager = safety_manager or SafetyManager(SafetyLevel.STANDARD)
        
        # Validation configuration
        self.boundary_limits = BoundaryLimits()
        self.validation_rules = []
        self.metrics = ValidationMetrics()
        
        # Action queue and tracking
        self.action_queue = deque()
        self.action_history = deque(maxlen=1000)
        self.active_actions = {}
        
        # Threading and synchronization
        self.queue_lock = threading.RLock()
        self.validation_lock = threading.Lock()
        
        # Queue processing
        self.queue_active = False
        self.queue_thread = None
        
        # Rollback system
        self.rollback_stack = deque(maxlen=100)
        self.rollback_enabled = True
        
        # Initialize validation rules
        self._initialize_validation_rules()
        
        # Auto-detect screen boundaries
        self._detect_screen_boundaries()
        
        self.logger.info("🔍 Input Validator initialized")
    
    def _initialize_validation_rules(self):
        """Initialize default validation rules"""
        self.validation_rules = [
            # Boundary validation
            ValidationRule(
                "screen_boundary",
                "boundary",
                {"check_screen_limits": True},
                "Action position outside screen boundaries",
                "error"
            ),
            
            # Position validation
            ValidationRule(
                "position_range",
                "range",
                {"min_x": 0, "min_y": 0, "max_x": 9999, "max_y": 9999},
                "Position coordinates out of valid range",
                "error"
            ),
            
            # Duration validation
            ValidationRule(
                "duration_range",
                "range",
                {"min_duration": 0.0, "max_duration": 10.0},
                "Action duration out of valid range",
                "warning"
            ),
            
            # Action type validation
            ValidationRule(
                "action_type",
                "type",
                {"valid_types": [t.value for t in ActionType]},
                "Invalid action type",
                "error"
            ),
            
            # Movement type validation
            ValidationRule(
                "movement_type",
                "type",
                {"valid_types": [t.value for t in MovementType]},
                "Invalid movement type",
                "warning"
            ),
            
            # Safety validation
            ValidationRule(
                "safety_check",
                "custom",
                {"function": self._validate_safety},
                "Action blocked by safety manager",
                "critical"
            )
        ]
    
    def _detect_screen_boundaries(self):
        """Auto-detect screen boundaries"""
        try:
            # Try to get screen size from various sources
            screen_width, screen_height = 1920, 1080  # Default
            
            # Try pyautogui
            try:
                import pyautogui
                screen_width, screen_height = pyautogui.size()
            except ImportError:
                pass
            
            # Try tkinter
            try:
                import tkinter as tk
                root = tk.Tk()
                screen_width = root.winfo_screenwidth()
                screen_height = root.winfo_screenheight()
                root.destroy()
            except ImportError:
                pass
            
            # Update boundary limits
            self.boundary_limits.max_x = screen_width
            self.boundary_limits.max_y = screen_height
            
            self.logger.info(f"📺 Screen boundaries detected: {screen_width}x{screen_height}")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Could not detect screen boundaries: {e}")
    
    def add_validation_rule(self, rule: ValidationRule):
        """Add custom validation rule"""
        with self.validation_lock:
            self.validation_rules.append(rule)
            self.logger.info(f"📋 Added validation rule: {rule.rule_id}")
    
    def remove_validation_rule(self, rule_id: str) -> bool:
        """Remove validation rule by ID"""
        with self.validation_lock:
            for i, rule in enumerate(self.validation_rules):
                if rule.rule_id == rule_id:
                    del self.validation_rules[i]
                    self.logger.info(f"🗑️ Removed validation rule: {rule_id}")
                    return True
            return False
    
    def validate_action(self, action: PrecisionAction) -> Tuple[ValidationResult, List[str]]:
        """Validate single action against all rules"""
        validation_start = time.time()
        errors = []
        warnings = []
        
        try:
            with self.validation_lock:
                for rule in self.validation_rules:
                    try:
                        result = self._apply_validation_rule(action, rule)
                        
                        if result[0] == ValidationResult.INVALID:
                            if rule.severity == "critical":
                                errors.append(f"CRITICAL: {result[1]}")
                                return ValidationResult.BLOCKED, errors
                            elif rule.severity == "error":
                                errors.append(f"ERROR: {result[1]}")
                            else:
                                warnings.append(f"WARNING: {result[1]}")
                    
                    except Exception as e:
                        error_msg = f"Validation rule '{rule.rule_id}' failed: {e}"
                        errors.append(error_msg)
                        self.logger.error(f"❌ {error_msg}")
                
                # Update metrics
                validation_time = time.time() - validation_start
                self.metrics.actions_validated += 1
                self.metrics.average_validation_time = (
                    (self.metrics.average_validation_time * (self.metrics.actions_validated - 1) + validation_time) /
                    self.metrics.actions_validated
                )
                
                # Determine final result
                if errors:
                    self.metrics.validation_errors += 1
                    return ValidationResult.INVALID, errors + warnings
                elif warnings:
                    return ValidationResult.VALID, warnings
                else:
                    return ValidationResult.VALID, []
        
        except Exception as e:
            self.logger.error(f"❌ Validation failed: {e}")
            return ValidationResult.INVALID, [f"Validation system error: {e}"]
    
    def _apply_validation_rule(self, action: PrecisionAction, rule: ValidationRule) -> Tuple[ValidationResult, str]:
        """Apply single validation rule"""
        if rule.rule_type == "boundary":
            return self._validate_boundary(action, rule)
        elif rule.rule_type == "range":
            return self._validate_range(action, rule)
        elif rule.rule_type == "type":
            return self._validate_type(action, rule)
        elif rule.rule_type == "custom":
            return self._validate_custom(action, rule)
        else:
            return ValidationResult.VALID, "Unknown rule type"
    
    def _validate_boundary(self, action: PrecisionAction, rule: ValidationRule) -> Tuple[ValidationResult, str]:
        """Validate boundary constraints"""
        if not action.target_position:
            return ValidationResult.VALID, "No position to validate"
        
        x, y = action.target_position
        
        # Check screen boundaries
        if rule.parameters.get("check_screen_limits", False):
            margin = self.boundary_limits.safe_margin
            
            if (x < self.boundary_limits.min_x + margin or 
                x > self.boundary_limits.max_x - margin or
                y < self.boundary_limits.min_y + margin or 
                y > self.boundary_limits.max_y - margin):
                
                return ValidationResult.INVALID, f"Position ({x}, {y}) outside safe boundaries"
        
        return ValidationResult.VALID, "Boundary check passed"
    
    def _validate_range(self, action: PrecisionAction, rule: ValidationRule) -> Tuple[ValidationResult, str]:
        """Validate range constraints"""
        params = rule.parameters
        
        # Position range
        if action.target_position and "min_x" in params:
            x, y = action.target_position
            if not (params.get("min_x", 0) <= x <= params.get("max_x", 9999) and
                    params.get("min_y", 0) <= y <= params.get("max_y", 9999)):
                return ValidationResult.INVALID, f"Position ({x}, {y}) out of range"
        
        # Duration range
        if "min_duration" in params:
            if not (params.get("min_duration", 0) <= action.duration <= params.get("max_duration", 10)):
                return ValidationResult.INVALID, f"Duration {action.duration} out of range"
        
        return ValidationResult.VALID, "Range check passed"
    
    def _validate_type(self, action: PrecisionAction, rule: ValidationRule) -> Tuple[ValidationResult, str]:
        """Validate type constraints"""
        params = rule.parameters
        
        # Action type
        if "valid_types" in params and hasattr(action, 'action_type'):
            if action.action_type.value not in params["valid_types"]:
                return ValidationResult.INVALID, f"Invalid action type: {action.action_type.value}"
        
        # Movement type
        if "valid_movement_types" in params and hasattr(action, 'movement_type'):
            if action.movement_type.value not in params["valid_movement_types"]:
                return ValidationResult.INVALID, f"Invalid movement type: {action.movement_type.value}"
        
        return ValidationResult.VALID, "Type check passed"
    
    def _validate_custom(self, action: PrecisionAction, rule: ValidationRule) -> Tuple[ValidationResult, str]:
        """Validate using custom function"""
        custom_function = rule.parameters.get("function")
        if custom_function and callable(custom_function):
            try:
                return custom_function(action)
            except Exception as e:
                return ValidationResult.INVALID, f"Custom validation failed: {e}"
        
        return ValidationResult.VALID, "No custom validation function"
    
    def _validate_safety(self, action: PrecisionAction) -> Tuple[ValidationResult, str]:
        """Safety manager validation"""
        if not self.safety_manager:
            return ValidationResult.VALID, "No safety manager"
        
        try:
            is_safe, reason = self.safety_manager.validate_action_safety(
                action.action_type.value,
                action.target_position,
                action.duration
            )
            
            if is_safe:
                return ValidationResult.VALID, "Safety check passed"
            else:
                return ValidationResult.INVALID, f"Safety check failed: {reason}"
        
        except Exception as e:
            return ValidationResult.INVALID, f"Safety validation error: {e}"
    
    def queue_action(self, action: PrecisionAction, priority: int = 0) -> str:
        """Queue action for validation and execution"""
        action_id = f"action_{int(time.time() * 1000000)}"
        
        action_context = ActionContext(
            action_id=action_id,
            action=action,
            timestamp=time.time(),
            status=ActionStatus.PENDING,
            validation_results=[]
        )
        
        with self.queue_lock:
            # Insert based on priority (higher priority first)
            inserted = False
            for i, (existing_priority, existing_context) in enumerate(self.action_queue):
                if priority > existing_priority:
                    self.action_queue.insert(i, (priority, action_context))
                    inserted = True
                    break
            
            if not inserted:
                self.action_queue.append((priority, action_context))
            
            self.active_actions[action_id] = action_context
        
        self.logger.debug(f"📥 Queued action {action_id} with priority {priority}")
        return action_id
    
    def start_queue_processing(self):
        """Start action queue processing"""
        if self.queue_active:
            return
        
        self.queue_active = True
        self.queue_thread = threading.Thread(target=self._queue_processing_loop, daemon=True)
        self.queue_thread.start()
        self.logger.info("🔄 Action queue processing started")
    
    def stop_queue_processing(self):
        """Stop action queue processing"""
        self.queue_active = False
        if self.queue_thread:
            self.queue_thread.join(timeout=1.0)
        self.logger.info("🛑 Action queue processing stopped")
    
    def _queue_processing_loop(self):
        """Action queue processing loop"""
        while self.queue_active:
            try:
                with self.queue_lock:
                    if not self.action_queue:
                        time.sleep(0.01)  # 10ms polling
                        continue
                    
                    priority, action_context = self.action_queue.popleft()
                
                # Process action
                self._process_action(action_context)
                
            except Exception as e:
                self.logger.error(f"❌ Queue processing error: {e}")
                time.sleep(0.1)
    
    def _process_action(self, action_context: ActionContext):
        """Process single action"""
        try:
            action_context.status = ActionStatus.VALIDATED
            
            # Validate action
            validation_result, messages = self.validate_action(action_context.action)
            action_context.validation_results.append(("validation", validation_result, "; ".join(messages)))
            
            if validation_result == ValidationResult.VALID:
                # Create rollback data before execution
                if self.rollback_enabled:
                    rollback_data = self._create_rollback_data(action_context.action)
                    action_context.rollback_data = rollback_data
                    self.rollback_stack.append(action_context)
                
                # Execute action (placeholder - would integrate with precision controller)
                action_context.status = ActionStatus.EXECUTING
                success = self._execute_action(action_context.action)
                
                if success:
                    action_context.status = ActionStatus.COMPLETED
                    self.logger.debug(f"✅ Action {action_context.action_id} completed")
                else:
                    action_context.status = ActionStatus.FAILED
                    self.logger.warning(f"❌ Action {action_context.action_id} failed")
            
            elif validation_result == ValidationResult.INVALID:
                action_context.status = ActionStatus.FAILED
                self.metrics.actions_blocked += 1
                self.logger.warning(f"🚫 Action {action_context.action_id} blocked: {messages}")
            
            # Move to history
            self.action_history.append(action_context)
            
            # Remove from active actions
            with self.queue_lock:
                if action_context.action_id in self.active_actions:
                    del self.active_actions[action_context.action_id]
        
        except Exception as e:
            self.logger.error(f"❌ Action processing failed: {e}")
            action_context.status = ActionStatus.FAILED
    
    def _create_rollback_data(self, action: PrecisionAction) -> Dict[str, Any]:
        """Create rollback data for action"""
        rollback_data = {
            "timestamp": time.time(),
            "action_type": action.action_type.value,
            "original_position": None,
            "target_position": action.target_position
        }
        
        # Get current position for rollback
        try:
            import pyautogui
            current_pos = pyautogui.position()
            rollback_data["original_position"] = (current_pos.x, current_pos.y)
        except ImportError:
            pass
        
        return rollback_data
    
    def _execute_action(self, action: PrecisionAction) -> bool:
        """Execute validated action (placeholder)"""
        # This would integrate with the precision controller
        # For now, just simulate execution
        time.sleep(action.duration)
        return True
    
    def rollback_last_action(self) -> bool:
        """Rollback the last executed action"""
        if not self.rollback_enabled or not self.rollback_stack:
            return False
        
        try:
            last_action_context = self.rollback_stack.pop()
            rollback_data = last_action_context.rollback_data
            
            if rollback_data and rollback_data.get("original_position"):
                # Restore original position
                original_pos = rollback_data["original_position"]
                
                # Create rollback action
                rollback_action = PrecisionAction(
                    action_type=ActionType.MOUSE_MOVE,
                    target_position=original_pos,
                    duration=0.1,
                    movement_type=MovementType.LINEAR
                )
                
                # Execute rollback
                success = self._execute_action(rollback_action)
                
                if success:
                    last_action_context.status = ActionStatus.ROLLED_BACK
                    self.metrics.actions_rolled_back += 1
                    self.logger.info(f"↩️ Rolled back action {last_action_context.action_id}")
                    return True
        
        except Exception as e:
            self.logger.error(f"❌ Rollback failed: {e}")
        
        return False
    
    def rollback_actions(self, count: int) -> int:
        """Rollback multiple actions"""
        rolled_back = 0
        for _ in range(count):
            if self.rollback_last_action():
                rolled_back += 1
            else:
                break
        
        self.logger.info(f"↩️ Rolled back {rolled_back}/{count} actions")
        return rolled_back
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        with self.queue_lock:
            return {
                "queue_length": len(self.action_queue),
                "active_actions": len(self.active_actions),
                "processing_active": self.queue_active,
                "rollback_stack_size": len(self.rollback_stack),
                "rollback_enabled": self.rollback_enabled
            }
    
    def get_validation_metrics(self) -> Dict[str, Any]:
        """Get validation metrics"""
        return {
            "actions_validated": self.metrics.actions_validated,
            "actions_blocked": self.metrics.actions_blocked,
            "actions_rolled_back": self.metrics.actions_rolled_back,
            "validation_errors": self.metrics.validation_errors,
            "average_validation_time": self.metrics.average_validation_time,
            "validation_rules_count": len(self.validation_rules),
            "block_rate": (self.metrics.actions_blocked / max(1, self.metrics.actions_validated)) * 100
        }
    
    def clear_history(self):
        """Clear action history and reset metrics"""
        with self.queue_lock:
            self.action_history.clear()
            self.rollback_stack.clear()
            self.metrics = ValidationMetrics()
        
        self.logger.info("🧹 Validation history cleared")

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔍 Input Validator - Sprint 2 Test")
    print("=" * 60)
    
    # Create input validator
    validator = InputValidator()
    
    # Test action validation
    print("\n✅ Testing action validation...")
    
    if CONTROL_MODULES_AVAILABLE:
        test_action = PrecisionAction(
            action_type=ActionType.MOUSE_CLICK,
            target_position=(100, 100),
            duration=0.1
        )
        
        result, messages = validator.validate_action(test_action)
        print(f"Validation result: {result.value}")
        for msg in messages:
            print(f"  - {msg}")
    
    # Test queue processing
    print("\n🔄 Testing queue processing...")
    validator.start_queue_processing()
    
    if CONTROL_MODULES_AVAILABLE:
        # Queue some test actions
        for i in range(3):
            action = PrecisionAction(
                action_type=ActionType.MOUSE_MOVE,
                target_position=(100 + i * 10, 100 + i * 10),
                duration=0.1
            )
            action_id = validator.queue_action(action, priority=i)
            print(f"Queued action: {action_id}")
    
    time.sleep(1)  # Let queue process
    
    # Get status
    queue_status = validator.get_queue_status()
    metrics = validator.get_validation_metrics()
    
    print(f"\n📊 Queue Status:")
    for key, value in queue_status.items():
        print(f"   {key}: {value}")
    
    print(f"\n📈 Validation Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    # Test rollback
    print(f"\n↩️ Testing rollback...")
    rolled_back = validator.rollback_last_action()
    print(f"Rollback success: {rolled_back}")
    
    validator.stop_queue_processing()
    
    print("\n🎉 Sprint 2 - Task 2.3 test completed!")
    print("🎯 Target: 100% safe action execution")
    print(f"📈 Current: {metrics['actions_validated']} actions validated, {metrics['block_rate']:.1f}% block rate")
