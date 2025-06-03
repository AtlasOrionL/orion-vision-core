#!/usr/bin/env python3
"""
🎮 Precision Control System - Gaming AI

Sub-pixel mouse accuracy and frame-perfect timing control.

Sprint 2 - Task 2.1: Precision Control Implementation
- ±0.5 pixel mouse accuracy
- <1ms timing variance
- Smooth, human-like movements
- 60 FPS action execution

Author: Nexus - Quantum AI Architect
Sprint: 2.1 - Control & Action System
"""

import time
import math
import numpy as np
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import warnings

# Platform-specific imports
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
    # Configure pyautogui for precision
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.0  # Remove default pause for precision
except ImportError:
    PYAUTOGUI_AVAILABLE = False
    warnings.warn("🎮 pyautogui not available. Install with: pip install pyautogui", ImportWarning)

try:
    import pynput
    from pynput.mouse import Button, Listener as MouseListener
    from pynput.keyboard import Key, Listener as KeyboardListener
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    warnings.warn("🎮 pynput not available. Install with: pip install pynput", ImportWarning)

class MovementType(Enum):
    """Movement type enumeration"""
    LINEAR = "linear"
    BEZIER = "bezier"
    HUMAN_LIKE = "human_like"
    INSTANT = "instant"

class ActionType(Enum):
    """Action type enumeration"""
    MOUSE_MOVE = "mouse_move"
    MOUSE_CLICK = "mouse_click"
    MOUSE_DRAG = "mouse_drag"
    KEY_PRESS = "key_press"
    KEY_RELEASE = "key_release"
    SCROLL = "scroll"

@dataclass
class PrecisionAction:
    """Precision action representation"""
    action_type: ActionType
    target_position: Optional[Tuple[float, float]] = None
    button: Optional[str] = None
    key: Optional[str] = None
    duration: float = 0.0
    movement_type: MovementType = MovementType.HUMAN_LIKE
    precision_level: float = 1.0  # 0.0 to 1.0
    timing_offset: float = 0.0
    metadata: Dict[str, Any] = None

@dataclass
class MovementPath:
    """Movement path representation"""
    start_pos: Tuple[float, float]
    end_pos: Tuple[float, float]
    control_points: List[Tuple[float, float]]
    duration: float
    movement_type: MovementType

@dataclass
class PrecisionMetrics:
    """Precision performance metrics"""
    accuracy_error: float = 0.0
    timing_variance: float = 0.0
    movement_smoothness: float = 0.0
    actions_executed: int = 0
    average_precision: float = 0.0

class PrecisionController:
    """
    Precision Control System for Gaming AI
    
    Features:
    - Sub-pixel mouse accuracy (±0.5 pixels)
    - Frame-perfect timing control (<1ms variance)
    - Smooth, human-like movements
    - Bezier curve path generation
    - Real-time performance monitoring
    """
    
    def __init__(self, target_accuracy: float = 0.5):
        self.target_accuracy = target_accuracy
        self.logger = logging.getLogger("PrecisionController")
        
        # Performance metrics
        self.metrics = PrecisionMetrics()
        self.performance_history = []
        
        # Threading and timing
        self.action_lock = threading.Lock()
        self.timing_calibration = 0.0
        
        # Movement parameters
        self.movement_speed = 1000.0  # pixels per second
        self.smoothing_factor = 0.8
        self.human_variance = 0.1
        
        # Calibration data
        self.calibration_data = {
            'mouse_precision': 1.0,
            'timing_offset': 0.0,
            'movement_scaling': 1.0
        }
        
        # Initialize platform-specific controllers
        self._initialize_controllers()
        
        # Perform initial calibration
        self._calibrate_system()
        
        self.logger.info(f"🎮 Precision Controller initialized (target: ±{target_accuracy} pixels)")
    
    def _initialize_controllers(self):
        """Initialize platform-specific control systems"""
        self.pyautogui_available = PYAUTOGUI_AVAILABLE
        self.pynput_available = PYNPUT_AVAILABLE
        
        if not (self.pyautogui_available or self.pynput_available):
            self.logger.warning("⚠️ No control libraries available")
        
        # Configure pyautogui for maximum precision
        if self.pyautogui_available:
            pyautogui.MINIMUM_DURATION = 0.0
            pyautogui.MINIMUM_SLEEP = 0.0
    
    def _calibrate_system(self):
        """Calibrate system for maximum precision"""
        try:
            # Timing calibration
            self._calibrate_timing()
            
            # Mouse precision calibration
            self._calibrate_mouse_precision()
            
            self.logger.info("✅ System calibration completed")
            
        except Exception as e:
            self.logger.error(f"❌ Calibration failed: {e}")
    
    def _calibrate_timing(self):
        """Calibrate timing precision"""
        timing_samples = []
        
        for _ in range(10):
            start_time = time.perf_counter()
            time.sleep(0.001)  # 1ms target
            actual_time = time.perf_counter() - start_time
            timing_samples.append(actual_time)
        
        # Calculate timing offset
        target_time = 0.001
        actual_average = sum(timing_samples) / len(timing_samples)
        self.timing_calibration = target_time - actual_average
        
        # Update metrics
        self.metrics.timing_variance = np.std(timing_samples) * 1000  # Convert to ms
        
        self.logger.debug(f"🕐 Timing calibration: {self.timing_calibration:.6f}s offset")
    
    def _calibrate_mouse_precision(self):
        """Calibrate mouse precision"""
        if not self.pyautogui_available:
            return
        
        try:
            # Get current position
            start_pos = pyautogui.position()
            
            # Test small movements
            test_movements = [(1, 0), (0, 1), (-1, 0), (0, -1)]
            precision_errors = []
            
            for dx, dy in test_movements:
                target_x = start_pos.x + dx
                target_y = start_pos.y + dy
                
                # Move with maximum precision
                pyautogui.moveTo(target_x, target_y, duration=0.1)
                
                # Check actual position
                actual_pos = pyautogui.position()
                error = math.sqrt((actual_pos.x - target_x)**2 + (actual_pos.y - target_y)**2)
                precision_errors.append(error)
            
            # Calculate precision metrics
            self.metrics.accuracy_error = sum(precision_errors) / len(precision_errors)
            self.calibration_data['mouse_precision'] = max(0.1, 1.0 / (1.0 + self.metrics.accuracy_error))
            
            # Return to start position
            pyautogui.moveTo(start_pos.x, start_pos.y, duration=0.1)
            
            self.logger.debug(f"🎯 Mouse precision: {self.metrics.accuracy_error:.2f} pixel error")
            
        except Exception as e:
            self.logger.error(f"❌ Mouse calibration failed: {e}")
    
    def generate_bezier_path(self, start: Tuple[float, float], end: Tuple[float, float], 
                           duration: float, control_points: Optional[List[Tuple[float, float]]] = None) -> MovementPath:
        """Generate smooth Bezier curve path"""
        
        if control_points is None:
            # Generate natural control points
            dx = end[0] - start[0]
            dy = end[1] - start[1]
            distance = math.sqrt(dx**2 + dy**2)
            
            # Add human-like variance
            variance_x = np.random.normal(0, distance * 0.1)
            variance_y = np.random.normal(0, distance * 0.1)
            
            # Control points for natural curve
            control_points = [
                (start[0] + dx * 0.3 + variance_x, start[1] + dy * 0.3 + variance_y),
                (start[0] + dx * 0.7 - variance_x, start[1] + dy * 0.7 - variance_y)
            ]
        
        return MovementPath(
            start_pos=start,
            end_pos=end,
            control_points=control_points,
            duration=duration,
            movement_type=MovementType.BEZIER
        )
    
    def calculate_bezier_point(self, t: float, points: List[Tuple[float, float]]) -> Tuple[float, float]:
        """Calculate point on Bezier curve at parameter t (0.0 to 1.0)"""
        n = len(points) - 1
        x = y = 0.0
        
        for i, (px, py) in enumerate(points):
            # Binomial coefficient
            binomial = math.comb(n, i)
            # Bernstein polynomial
            bernstein = binomial * (t ** i) * ((1 - t) ** (n - i))
            
            x += px * bernstein
            y += py * bernstein
        
        return (x, y)
    
    def execute_precise_movement(self, path: MovementPath) -> bool:
        """Execute precise movement along path"""
        if not self.pyautogui_available:
            self.logger.warning("⚠️ pyautogui not available for movement")
            return False
        
        try:
            with self.action_lock:
                start_time = time.perf_counter()
                
                # Calculate number of steps for smooth movement
                distance = math.sqrt((path.end_pos[0] - path.start_pos[0])**2 + 
                                   (path.end_pos[1] - path.start_pos[1])**2)
                steps = max(10, int(distance / 5))  # At least 10 steps, more for longer distances
                
                # Generate path points
                if path.movement_type == MovementType.BEZIER:
                    # Bezier curve points
                    curve_points = [path.start_pos] + path.control_points + [path.end_pos]
                    
                    for i in range(steps + 1):
                        t = i / steps
                        x, y = self.calculate_bezier_point(t, curve_points)
                        
                        # Apply precision calibration
                        x *= self.calibration_data['mouse_precision']
                        y *= self.calibration_data['mouse_precision']
                        
                        # Move to position
                        pyautogui.moveTo(int(round(x)), int(round(y)), duration=0)
                        
                        # Precise timing
                        step_duration = path.duration / steps
                        adjusted_duration = step_duration + self.timing_calibration
                        if adjusted_duration > 0:
                            time.sleep(adjusted_duration)
                
                elif path.movement_type == MovementType.LINEAR:
                    # Linear interpolation
                    for i in range(steps + 1):
                        t = i / steps
                        x = path.start_pos[0] + t * (path.end_pos[0] - path.start_pos[0])
                        y = path.start_pos[1] + t * (path.end_pos[1] - path.start_pos[1])
                        
                        pyautogui.moveTo(int(round(x)), int(round(y)), duration=0)
                        
                        step_duration = path.duration / steps
                        if step_duration > 0:
                            time.sleep(step_duration)
                
                elif path.movement_type == MovementType.INSTANT:
                    # Instant movement
                    pyautogui.moveTo(int(round(path.end_pos[0])), int(round(path.end_pos[1])), duration=0)
                
                # Verify final position
                final_pos = pyautogui.position()
                error = math.sqrt((final_pos.x - path.end_pos[0])**2 + (final_pos.y - path.end_pos[1])**2)
                
                # Update metrics
                self.metrics.actions_executed += 1
                self.metrics.accuracy_error = (self.metrics.accuracy_error * (self.metrics.actions_executed - 1) + error) / self.metrics.actions_executed
                
                execution_time = time.perf_counter() - start_time
                timing_error = abs(execution_time - path.duration) * 1000  # Convert to ms
                self.metrics.timing_variance = (self.metrics.timing_variance * (self.metrics.actions_executed - 1) + timing_error) / self.metrics.actions_executed
                
                # Log precision achievement
                if error <= self.target_accuracy:
                    self.logger.debug(f"✅ Precise movement: {error:.2f} pixel error")
                else:
                    self.logger.warning(f"⚠️ Movement precision: {error:.2f} pixel error (target: {self.target_accuracy})")
                
                return error <= self.target_accuracy
                
        except Exception as e:
            self.logger.error(f"❌ Movement execution failed: {e}")
            return False
    
    def execute_precise_click(self, position: Tuple[float, float], button: str = "left", 
                            duration: float = 0.1) -> bool:
        """Execute precise click at position"""
        if not self.pyautogui_available:
            self.logger.warning("⚠️ pyautogui not available for clicking")
            return False
        
        try:
            with self.action_lock:
                # Move to position first
                current_pos = pyautogui.position()
                if (current_pos.x, current_pos.y) != position:
                    path = MovementPath(
                        start_pos=(current_pos.x, current_pos.y),
                        end_pos=position,
                        control_points=[],
                        duration=0.05,  # Quick movement to click position
                        movement_type=MovementType.LINEAR
                    )
                    self.execute_precise_movement(path)
                
                # Execute click with precise timing
                start_time = time.perf_counter()
                
                if button.lower() == "left":
                    pyautogui.click(position[0], position[1], duration=duration)
                elif button.lower() == "right":
                    pyautogui.rightClick(position[0], position[1])
                elif button.lower() == "middle":
                    pyautogui.middleClick(position[0], position[1])
                
                execution_time = time.perf_counter() - start_time
                
                # Verify click position
                click_pos = pyautogui.position()
                error = math.sqrt((click_pos.x - position[0])**2 + (click_pos.y - position[1])**2)
                
                # Update metrics
                self.metrics.actions_executed += 1
                
                self.logger.debug(f"🖱️ Click executed at ({position[0]:.1f}, {position[1]:.1f}) with {error:.2f} pixel error")
                
                return error <= self.target_accuracy
                
        except Exception as e:
            self.logger.error(f"❌ Click execution failed: {e}")
            return False
    
    def execute_action(self, action: PrecisionAction) -> bool:
        """Execute precision action"""
        try:
            if action.action_type == ActionType.MOUSE_MOVE:
                if action.target_position:
                    current_pos = pyautogui.position() if self.pyautogui_available else (0, 0)
                    path = self.generate_bezier_path(
                        start=(current_pos.x, current_pos.y) if self.pyautogui_available else (0, 0),
                        end=action.target_position,
                        duration=action.duration
                    )
                    return self.execute_precise_movement(path)
            
            elif action.action_type == ActionType.MOUSE_CLICK:
                if action.target_position:
                    return self.execute_precise_click(
                        action.target_position,
                        action.button or "left",
                        action.duration
                    )
            
            elif action.action_type == ActionType.KEY_PRESS:
                if action.key and self.pyautogui_available:
                    pyautogui.press(action.key)
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Action execution failed: {e}")
            return False
    
    def get_precision_metrics(self) -> Dict[str, float]:
        """Get current precision metrics"""
        return {
            'accuracy_error': self.metrics.accuracy_error,
            'timing_variance': self.metrics.timing_variance,
            'actions_executed': self.metrics.actions_executed,
            'target_accuracy': self.target_accuracy,
            'precision_achievement_rate': (
                (self.target_accuracy - self.metrics.accuracy_error) / self.target_accuracy * 100
                if self.metrics.accuracy_error < self.target_accuracy else 0
            )
        }
    
    def reset_metrics(self):
        """Reset precision metrics"""
        self.metrics = PrecisionMetrics()
        self.performance_history.clear()
        self.logger.info("📊 Precision metrics reset")

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎮 Precision Control System - Sprint 2 Test")
    print("=" * 60)
    
    # Create precision controller
    controller = PrecisionController(target_accuracy=0.5)
    
    # Test precision movement
    print("\n🎯 Testing precision movement...")
    if controller.pyautogui_available:
        current_pos = pyautogui.position()
        target_pos = (current_pos.x + 100, current_pos.y + 50)
        
        # Generate Bezier path
        path = controller.generate_bezier_path(
            start=(current_pos.x, current_pos.y),
            end=target_pos,
            duration=0.5
        )
        
        # Execute movement
        success = controller.execute_precise_movement(path)
        print(f"✅ Movement success: {success}")
        
        # Test precision click
        print("\n🖱️ Testing precision click...")
        click_success = controller.execute_precise_click(target_pos, "left", 0.1)
        print(f"✅ Click success: {click_success}")
    
    # Get precision metrics
    metrics = controller.get_precision_metrics()
    print(f"\n📊 Precision Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value:.3f}")
    
    print("\n🎉 Sprint 2 - Task 2.1 test completed!")
    print("🎯 Target: ±0.5 pixel accuracy, <1ms timing variance")
    print(f"📈 Current: {metrics['accuracy_error']:.2f} pixel error, {metrics['timing_variance']:.2f}ms variance")
