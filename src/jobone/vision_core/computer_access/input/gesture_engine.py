#!/usr/bin/env python3
"""
Gesture Engine - Complex gesture and movement pattern execution
"""

import logging
import time
import math
import threading
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

class GestureType(Enum):
    """Types of gestures"""
    SWIPE = "swipe"
    PINCH = "pinch"
    ROTATE = "rotate"
    CIRCLE = "circle"
    SPIRAL = "spiral"
    ZIGZAG = "zigzag"
    WAVE = "wave"
    CUSTOM_PATH = "custom_path"

class GestureDirection(Enum):
    """Gesture directions"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    CLOCKWISE = "clockwise"
    COUNTERCLOCKWISE = "counterclockwise"

@dataclass
class GesturePoint:
    """Point in a gesture path"""
    x: float
    y: float
    timestamp: float
    pressure: float = 1.0

@dataclass
class GesturePattern:
    """Gesture pattern definition"""
    gesture_type: GestureType
    points: List[GesturePoint]
    duration: float
    parameters: Dict[str, Any]

class GestureEngine:
    """
    Advanced gesture engine for complex movement patterns
    Supports various gesture types and custom path execution
    """
    
    def __init__(self, mouse_controller=None):
        self.logger = logging.getLogger('orion.computer_access.input.gesture')
        
        # Controllers
        self.mouse = mouse_controller
        self.initialized = False
        
        # Gesture library
        self.gesture_library = {}
        self.custom_gestures = {}
        
        # Performance tracking
        self.gestures_executed = 0
        self.successful_gestures = 0
        self.failed_gestures = 0
        
        # Configuration
        self.default_speed = 1.0
        self.smoothing_enabled = True
        self.precision_mode = False
        
        # Thread safety
        self.execution_lock = threading.Lock()
        
        self._initialize_gesture_library()
        
        self.logger.info("🎨 GestureEngine initialized")
    
    def initialize(self, mouse_controller) -> bool:
        """
        Initialize gesture engine with mouse controller
        
        Args:
            mouse_controller: MouseController instance
            
        Returns:
            bool: True if initialization successful
        """
        try:
            self.logger.info("🚀 Initializing gesture engine...")
            
            if not mouse_controller:
                raise ValueError("Mouse controller is required")
            
            if not mouse_controller.is_ready():
                raise RuntimeError("Mouse controller must be initialized")
            
            self.mouse = mouse_controller
            
            self.initialized = True
            self.logger.info("✅ Gesture engine initialized successfully")
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Gesture engine initialization failed: {e}")
            return False
    
    def _initialize_gesture_library(self):
        """Initialize built-in gesture library"""
        self.gesture_library = {
            'swipe_up': self._create_swipe_gesture('up'),
            'swipe_down': self._create_swipe_gesture('down'),
            'swipe_left': self._create_swipe_gesture('left'),
            'swipe_right': self._create_swipe_gesture('right'),
            'circle_clockwise': self._create_circle_gesture('clockwise'),
            'circle_counterclockwise': self._create_circle_gesture('counterclockwise'),
            'spiral_in': self._create_spiral_gesture('in'),
            'spiral_out': self._create_spiral_gesture('out'),
            'zigzag_horizontal': self._create_zigzag_gesture('horizontal'),
            'zigzag_vertical': self._create_zigzag_gesture('vertical'),
            'wave_horizontal': self._create_wave_gesture('horizontal'),
            'wave_vertical': self._create_wave_gesture('vertical')
        }
    
    def execute_gesture(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a gesture
        
        Args:
            parameters: Gesture parameters
            
        Returns:
            Dict containing execution result
        """
        if not self.initialized:
            raise RuntimeError("Gesture engine not initialized")
        
        gesture_name = parameters.get('gesture_name')
        gesture_type = parameters.get('gesture_type')
        custom_points = parameters.get('points')
        
        with self.execution_lock:
            try:
                start_time = time.time()
                
                if gesture_name and gesture_name in self.gesture_library:
                    # Execute predefined gesture
                    pattern = self.gesture_library[gesture_name]
                    result = self._execute_pattern(pattern, parameters)
                    
                elif gesture_name and gesture_name in self.custom_gestures:
                    # Execute custom gesture
                    pattern = self.custom_gestures[gesture_name]
                    result = self._execute_pattern(pattern, parameters)
                    
                elif gesture_type:
                    # Create and execute gesture by type
                    pattern = self._create_gesture_by_type(gesture_type, parameters)
                    result = self._execute_pattern(pattern, parameters)
                    
                elif custom_points:
                    # Execute custom point path
                    pattern = self._create_custom_pattern(custom_points, parameters)
                    result = self._execute_pattern(pattern, parameters)
                    
                else:
                    raise ValueError("Gesture name, type, or custom points required")
                
                execution_time = time.time() - start_time
                
                result.update({
                    'gesture_name': gesture_name,
                    'gesture_type': gesture_type,
                    'execution_time': execution_time,
                    'success': True
                })
                
                self.gestures_executed += 1
                self.successful_gestures += 1
                
                self.logger.info(f"✅ Gesture executed: {gesture_name or gesture_type}")
                
                return result
                
            except Exception as e:
                self.gestures_executed += 1
                self.failed_gestures += 1
                
                self.logger.error(f"❌ Gesture execution failed: {e}")
                
                return {
                    'gesture_name': gesture_name,
                    'gesture_type': gesture_type,
                    'success': False,
                    'error': str(e)
                }
    
    def _execute_pattern(self, pattern: GesturePattern, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a gesture pattern"""
        if not pattern.points:
            raise ValueError("Gesture pattern has no points")
        
        # Get execution parameters
        speed_multiplier = parameters.get('speed', self.default_speed)
        start_x = parameters.get('start_x', pattern.points[0].x)
        start_y = parameters.get('start_y', pattern.points[0].y)
        scale = parameters.get('scale', 1.0)
        
        # Calculate scaled and positioned points
        scaled_points = []
        for point in pattern.points:
            scaled_x = start_x + (point.x - pattern.points[0].x) * scale
            scaled_y = start_y + (point.y - pattern.points[0].y) * scale
            scaled_points.append((scaled_x, scaled_y))
        
        # Execute movement
        total_distance = 0
        movement_count = 0
        
        # Move to start position
        self.mouse.execute_action({
            'action_type': 'move',
            'x': int(scaled_points[0][0]),
            'y': int(scaled_points[0][1]),
            'movement_type': 'instant'
        })
        
        # Execute gesture path
        for i in range(1, len(scaled_points)):
            prev_x, prev_y = scaled_points[i-1]
            curr_x, curr_y = scaled_points[i]
            
            # Calculate movement duration
            distance = math.sqrt((curr_x - prev_x)**2 + (curr_y - prev_y)**2)
            duration = (distance / 1000.0) / speed_multiplier  # Base speed adjustment
            
            # Move to point
            self.mouse.execute_action({
                'action_type': 'move',
                'x': int(curr_x),
                'y': int(curr_y),
                'movement_type': 'smooth' if self.smoothing_enabled else 'linear',
                'duration': max(0.01, duration)
            })
            
            total_distance += distance
            movement_count += 1
        
        return {
            'pattern_type': pattern.gesture_type.value,
            'points_executed': len(scaled_points),
            'total_distance': total_distance,
            'movement_count': movement_count,
            'scale': scale,
            'speed_multiplier': speed_multiplier
        }
    
    def _create_gesture_by_type(self, gesture_type: str, parameters: Dict[str, Any]) -> GesturePattern:
        """Create gesture pattern by type"""
        gesture_enum = GestureType(gesture_type)
        
        if gesture_enum == GestureType.SWIPE:
            direction = parameters.get('direction', 'right')
            return self._create_swipe_gesture(direction)
            
        elif gesture_enum == GestureType.CIRCLE:
            direction = parameters.get('direction', 'clockwise')
            return self._create_circle_gesture(direction)
            
        elif gesture_enum == GestureType.SPIRAL:
            direction = parameters.get('direction', 'out')
            return self._create_spiral_gesture(direction)
            
        elif gesture_enum == GestureType.ZIGZAG:
            orientation = parameters.get('orientation', 'horizontal')
            return self._create_zigzag_gesture(orientation)
            
        elif gesture_enum == GestureType.WAVE:
            orientation = parameters.get('orientation', 'horizontal')
            return self._create_wave_gesture(orientation)
            
        else:
            raise ValueError(f"Unsupported gesture type: {gesture_type}")
    
    def _create_swipe_gesture(self, direction: str) -> GesturePattern:
        """Create swipe gesture pattern"""
        points = []
        
        if direction == 'up':
            points = [GesturePoint(0, 100, 0), GesturePoint(0, 0, 1)]
        elif direction == 'down':
            points = [GesturePoint(0, 0, 0), GesturePoint(0, 100, 1)]
        elif direction == 'left':
            points = [GesturePoint(100, 0, 0), GesturePoint(0, 0, 1)]
        elif direction == 'right':
            points = [GesturePoint(0, 0, 0), GesturePoint(100, 0, 1)]
        
        return GesturePattern(
            gesture_type=GestureType.SWIPE,
            points=points,
            duration=0.5,
            parameters={'direction': direction}
        )
    
    def _create_circle_gesture(self, direction: str) -> GesturePattern:
        """Create circle gesture pattern"""
        points = []
        radius = 50
        steps = 36  # 10-degree increments
        
        for i in range(steps + 1):
            angle = (i * 2 * math.pi / steps)
            if direction == 'counterclockwise':
                angle = -angle
            
            x = radius + radius * math.cos(angle)
            y = radius + radius * math.sin(angle)
            timestamp = i / steps
            
            points.append(GesturePoint(x, y, timestamp))
        
        return GesturePattern(
            gesture_type=GestureType.CIRCLE,
            points=points,
            duration=1.0,
            parameters={'direction': direction, 'radius': radius}
        )
    
    def _create_spiral_gesture(self, direction: str) -> GesturePattern:
        """Create spiral gesture pattern"""
        points = []
        max_radius = 50
        steps = 72  # 5-degree increments
        
        for i in range(steps + 1):
            angle = (i * 4 * math.pi / steps)  # 2 full rotations
            
            if direction == 'in':
                radius = max_radius * (1 - i / steps)
            else:  # 'out'
                radius = max_radius * (i / steps)
            
            x = max_radius + radius * math.cos(angle)
            y = max_radius + radius * math.sin(angle)
            timestamp = i / steps
            
            points.append(GesturePoint(x, y, timestamp))
        
        return GesturePattern(
            gesture_type=GestureType.SPIRAL,
            points=points,
            duration=1.5,
            parameters={'direction': direction, 'max_radius': max_radius}
        )
    
    def _create_zigzag_gesture(self, orientation: str) -> GesturePattern:
        """Create zigzag gesture pattern"""
        points = []
        amplitude = 30
        wavelength = 25
        length = 100
        
        if orientation == 'horizontal':
            steps = int(length / 5)
            for i in range(steps + 1):
                x = i * length / steps
                y = amplitude * math.sin(2 * math.pi * x / wavelength)
                timestamp = i / steps
                points.append(GesturePoint(x, y + amplitude, timestamp))
        else:  # vertical
            steps = int(length / 5)
            for i in range(steps + 1):
                y = i * length / steps
                x = amplitude * math.sin(2 * math.pi * y / wavelength)
                timestamp = i / steps
                points.append(GesturePoint(x + amplitude, y, timestamp))
        
        return GesturePattern(
            gesture_type=GestureType.ZIGZAG,
            points=points,
            duration=1.0,
            parameters={'orientation': orientation, 'amplitude': amplitude}
        )
    
    def _create_wave_gesture(self, orientation: str) -> GesturePattern:
        """Create wave gesture pattern"""
        points = []
        amplitude = 20
        wavelength = 50
        length = 150
        
        if orientation == 'horizontal':
            steps = int(length / 3)
            for i in range(steps + 1):
                x = i * length / steps
                y = amplitude * math.sin(2 * math.pi * x / wavelength)
                timestamp = i / steps
                points.append(GesturePoint(x, y + amplitude, timestamp))
        else:  # vertical
            steps = int(length / 3)
            for i in range(steps + 1):
                y = i * length / steps
                x = amplitude * math.sin(2 * math.pi * y / wavelength)
                timestamp = i / steps
                points.append(GesturePoint(x + amplitude, y, timestamp))
        
        return GesturePattern(
            gesture_type=GestureType.WAVE,
            points=points,
            duration=1.2,
            parameters={'orientation': orientation, 'amplitude': amplitude}
        )
    
    def _create_custom_pattern(self, points: List[Dict], parameters: Dict[str, Any]) -> GesturePattern:
        """Create custom gesture pattern from points"""
        gesture_points = []
        
        for i, point in enumerate(points):
            x = point.get('x', 0)
            y = point.get('y', 0)
            timestamp = point.get('timestamp', i / len(points))
            pressure = point.get('pressure', 1.0)
            
            gesture_points.append(GesturePoint(x, y, timestamp, pressure))
        
        duration = parameters.get('duration', 1.0)
        
        return GesturePattern(
            gesture_type=GestureType.CUSTOM_PATH,
            points=gesture_points,
            duration=duration,
            parameters=parameters
        )
    
    def register_custom_gesture(self, name: str, pattern: GesturePattern) -> bool:
        """Register a custom gesture pattern"""
        try:
            self.custom_gestures[name] = pattern
            self.logger.info(f"🎨 Custom gesture registered: {name}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to register custom gesture: {e}")
            return False
    
    def get_available_gestures(self) -> Dict[str, List[str]]:
        """Get list of available gestures"""
        return {
            'built_in': list(self.gesture_library.keys()),
            'custom': list(self.custom_gestures.keys())
        }
    
    def is_ready(self) -> bool:
        """Check if gesture engine is ready"""
        return self.initialized and self.mouse and self.mouse.is_ready()
    
    def get_status(self) -> Dict[str, Any]:
        """Get gesture engine status"""
        return {
            'initialized': self.initialized,
            'gestures_executed': self.gestures_executed,
            'successful_gestures': self.successful_gestures,
            'failed_gestures': self.failed_gestures,
            'success_rate': (self.successful_gestures / max(self.gestures_executed, 1)) * 100,
            'available_gestures': len(self.gesture_library) + len(self.custom_gestures),
            'built_in_gestures': len(self.gesture_library),
            'custom_gestures': len(self.custom_gestures),
            'mouse_ready': self.mouse.is_ready() if self.mouse else False,
            'smoothing_enabled': self.smoothing_enabled,
            'precision_mode': self.precision_mode
        }
    
    def shutdown(self):
        """Shutdown gesture engine"""
        self.logger.info("🛑 Shutting down gesture engine")
        self.initialized = False
        self.logger.info("✅ Gesture engine shutdown complete")
