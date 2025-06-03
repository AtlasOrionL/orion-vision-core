#!/usr/bin/env python3
"""
🛡️ Safety Manager - Gaming AI

Enhanced safety mechanisms with anti-detection and human behavior simulation.

Sprint 2 - Task 2.2: Safety Mechanisms Development
- Enhanced rate limiting algorithms
- Anti-detection pattern randomization
- Human behavior simulation
- Emergency stop mechanisms

Author: Nexus - Quantum AI Architect
Sprint: 2.2 - Control & Action System
"""

import time
import random
import numpy as np
import threading
import logging
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

class SafetyLevel(Enum):
    """Safety level enumeration"""
    MINIMAL = "minimal"
    STANDARD = "standard"
    PARANOID = "paranoid"
    STEALTH = "stealth"

class ThreatLevel(Enum):
    """Threat level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ActionPattern:
    """Action pattern for behavior analysis"""
    timestamp: float
    action_type: str
    position: Optional[Tuple[float, float]]
    duration: float
    interval_since_last: float

@dataclass
class SafetyMetrics:
    """Safety performance metrics"""
    actions_blocked: int = 0
    patterns_detected: int = 0
    emergency_stops: int = 0
    threat_level: ThreatLevel = ThreatLevel.LOW
    safety_score: float = 100.0
    human_likeness_score: float = 0.0

@dataclass
class SafetyLimits:
    """Safety limits configuration"""
    max_actions_per_second: int = 20
    max_actions_per_minute: int = 600
    min_action_interval: float = 0.05
    max_continuous_actions: int = 50
    pattern_detection_threshold: float = 0.8
    human_variance_factor: float = 0.15

class SafetyManager:
    """
    Advanced Safety Manager for Gaming AI
    
    Features:
    - Enhanced rate limiting with adaptive algorithms
    - Anti-detection pattern randomization
    - Human behavior simulation and validation
    - Emergency stop mechanisms
    - Real-time threat assessment
    """
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.STANDARD):
        self.safety_level = safety_level
        self.logger = logging.getLogger("SafetyManager")
        
        # Safety configuration
        self.limits = self._configure_safety_limits()
        self.metrics = SafetyMetrics()
        
        # Action tracking
        self.action_history = deque(maxlen=1000)
        self.pattern_history = deque(maxlen=100)
        self.last_action_time = 0.0
        
        # Threading and locks
        self.safety_lock = threading.RLock()
        self.emergency_stop_event = threading.Event()
        
        # Human behavior simulation
        self.human_patterns = self._initialize_human_patterns()
        self.current_session_id = self._generate_session_id()
        
        # Anti-detection mechanisms
        self.detection_countermeasures = self._initialize_countermeasures()
        
        # Monitoring thread
        self.monitoring_active = False
        self.monitoring_thread = None
        
        self.logger.info(f"🛡️ Safety Manager initialized (level: {safety_level.value})")
    
    def _configure_safety_limits(self) -> SafetyLimits:
        """Configure safety limits based on safety level"""
        if self.safety_level == SafetyLevel.MINIMAL:
            return SafetyLimits(
                max_actions_per_second=30,
                max_actions_per_minute=1000,
                min_action_interval=0.03,
                max_continuous_actions=100,
                pattern_detection_threshold=0.9,
                human_variance_factor=0.1
            )
        elif self.safety_level == SafetyLevel.STANDARD:
            return SafetyLimits(
                max_actions_per_second=20,
                max_actions_per_minute=600,
                min_action_interval=0.05,
                max_continuous_actions=50,
                pattern_detection_threshold=0.8,
                human_variance_factor=0.15
            )
        elif self.safety_level == SafetyLevel.PARANOID:
            return SafetyLimits(
                max_actions_per_second=10,
                max_actions_per_minute=300,
                min_action_interval=0.1,
                max_continuous_actions=25,
                pattern_detection_threshold=0.6,
                human_variance_factor=0.25
            )
        elif self.safety_level == SafetyLevel.STEALTH:
            return SafetyLimits(
                max_actions_per_second=5,
                max_actions_per_minute=150,
                min_action_interval=0.2,
                max_continuous_actions=10,
                pattern_detection_threshold=0.5,
                human_variance_factor=0.3
            )
    
    def _initialize_human_patterns(self) -> Dict[str, Any]:
        """Initialize human behavior patterns"""
        return {
            'reaction_time': {
                'min': 0.15,  # 150ms minimum human reaction
                'max': 0.8,   # 800ms maximum reasonable reaction
                'average': 0.25,
                'variance': 0.1
            },
            'movement_patterns': {
                'acceleration_curve': 'ease_in_out',
                'overshoot_probability': 0.15,
                'correction_probability': 0.1,
                'pause_probability': 0.05
            },
            'typing_patterns': {
                'wpm_range': (30, 120),
                'error_rate': 0.02,
                'backspace_probability': 0.08,
                'pause_between_words': (0.1, 0.5)
            },
            'session_patterns': {
                'break_probability': 0.001,  # Per action
                'fatigue_factor': 0.95,      # Gradual slowdown
                'attention_span': 1800       # 30 minutes
            }
        }
    
    def _initialize_countermeasures(self) -> Dict[str, Any]:
        """Initialize anti-detection countermeasures"""
        return {
            'timing_randomization': {
                'enabled': True,
                'variance_factor': 0.2,
                'distribution': 'normal'
            },
            'pattern_breaking': {
                'enabled': True,
                'break_frequency': 0.1,
                'random_actions': ['pause', 'micro_movement', 'false_start']
            },
            'behavioral_mimicry': {
                'enabled': True,
                'human_error_simulation': True,
                'fatigue_simulation': True,
                'attention_variation': True
            }
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = str(time.time())
        random_data = str(random.random())
        session_data = f"{timestamp}_{random_data}_{self.safety_level.value}"
        return hashlib.md5(session_data.encode()).hexdigest()[:12]
    
    def validate_action_safety(self, action_type: str, position: Optional[Tuple[float, float]] = None,
                              duration: float = 0.0) -> Tuple[bool, str]:
        """Validate if action is safe to execute"""
        with self.safety_lock:
            current_time = time.time()
            
            # Check emergency stop
            if self.emergency_stop_event.is_set():
                return False, "Emergency stop activated"
            
            # Rate limiting checks
            rate_check = self._check_rate_limits(current_time)
            if not rate_check[0]:
                self.metrics.actions_blocked += 1
                return rate_check
            
            # Pattern detection
            pattern_check = self._check_suspicious_patterns(action_type, position, current_time)
            if not pattern_check[0]:
                self.metrics.actions_blocked += 1
                self.metrics.patterns_detected += 1
                return pattern_check
            
            # Human behavior validation
            human_check = self._validate_human_behavior(action_type, current_time)
            if not human_check[0]:
                self.metrics.actions_blocked += 1
                return human_check
            
            # Record action for future analysis
            self._record_action(action_type, position, duration, current_time)
            
            return True, "Action approved"
    
    def _check_rate_limits(self, current_time: float) -> Tuple[bool, str]:
        """Check rate limiting constraints"""
        # Time since last action
        if self.last_action_time > 0:
            interval = current_time - self.last_action_time
            if interval < self.limits.min_action_interval:
                return False, f"Action too fast: {interval:.3f}s < {self.limits.min_action_interval}s"
        
        # Actions per second
        recent_actions = [a for a in self.action_history 
                         if current_time - a.timestamp <= 1.0]
        if len(recent_actions) >= self.limits.max_actions_per_second:
            return False, f"Too many actions per second: {len(recent_actions)}"
        
        # Actions per minute
        minute_actions = [a for a in self.action_history 
                         if current_time - a.timestamp <= 60.0]
        if len(minute_actions) >= self.limits.max_actions_per_minute:
            return False, f"Too many actions per minute: {len(minute_actions)}"
        
        # Continuous actions
        continuous_count = 0
        for action in reversed(list(self.action_history)):
            if current_time - action.timestamp > 5.0:  # 5 second window
                break
            continuous_count += 1
        
        if continuous_count >= self.limits.max_continuous_actions:
            return False, f"Too many continuous actions: {continuous_count}"
        
        return True, "Rate limits OK"
    
    def _check_suspicious_patterns(self, action_type: str, position: Optional[Tuple[float, float]],
                                  current_time: float) -> Tuple[bool, str]:
        """Check for suspicious automation patterns"""
        if len(self.action_history) < 5:
            return True, "Insufficient history for pattern detection"
        
        # Check for repetitive patterns
        recent_actions = list(self.action_history)[-10:]
        
        # Timing pattern detection
        intervals = []
        for i in range(1, len(recent_actions)):
            interval = recent_actions[i].timestamp - recent_actions[i-1].timestamp
            intervals.append(interval)
        
        if len(intervals) >= 3:
            # Check for too-regular timing
            interval_variance = np.var(intervals)
            if interval_variance < 0.001:  # Very low variance indicates automation
                pattern_score = 1.0 - interval_variance
                if pattern_score > self.limits.pattern_detection_threshold:
                    return False, f"Suspicious timing pattern detected: {pattern_score:.3f}"
        
        # Position pattern detection
        if position and len(recent_actions) >= 5:
            positions = [a.position for a in recent_actions if a.position]
            if len(positions) >= 3:
                # Check for geometric patterns
                pattern_score = self._analyze_position_patterns(positions)
                if pattern_score > self.limits.pattern_detection_threshold:
                    return False, f"Suspicious position pattern detected: {pattern_score:.3f}"
        
        return True, "No suspicious patterns detected"
    
    def _analyze_position_patterns(self, positions: List[Tuple[float, float]]) -> float:
        """Analyze position patterns for automation detection"""
        if len(positions) < 3:
            return 0.0
        
        # Calculate distances and angles
        distances = []
        angles = []
        
        for i in range(1, len(positions)):
            dx = positions[i][0] - positions[i-1][0]
            dy = positions[i][1] - positions[i-1][1]
            distance = math.sqrt(dx**2 + dy**2)
            distances.append(distance)
            
            if i >= 2:
                # Calculate angle change
                prev_dx = positions[i-1][0] - positions[i-2][0]
                prev_dy = positions[i-1][1] - positions[i-2][1]
                
                if prev_dx != 0 or prev_dy != 0:
                    angle = math.atan2(dy, dx) - math.atan2(prev_dy, prev_dx)
                    angles.append(abs(angle))
        
        # Analyze patterns
        pattern_score = 0.0
        
        # Too-regular distances
        if len(distances) >= 3:
            distance_variance = np.var(distances)
            if distance_variance < 10:  # Very similar distances
                pattern_score += 0.3
        
        # Too-regular angles
        if len(angles) >= 2:
            angle_variance = np.var(angles)
            if angle_variance < 0.1:  # Very similar angles
                pattern_score += 0.4
        
        # Perfect geometric shapes
        if len(positions) >= 4:
            # Check for perfect rectangles, circles, etc.
            geometric_score = self._detect_geometric_patterns(positions)
            pattern_score += geometric_score * 0.3
        
        return min(1.0, pattern_score)
    
    def _detect_geometric_patterns(self, positions: List[Tuple[float, float]]) -> float:
        """Detect perfect geometric patterns"""
        # Simplified geometric pattern detection
        if len(positions) == 4:
            # Check for rectangle
            distances = []
            for i in range(len(positions)):
                next_i = (i + 1) % len(positions)
                dx = positions[next_i][0] - positions[i][0]
                dy = positions[next_i][1] - positions[i][1]
                distance = math.sqrt(dx**2 + dy**2)
                distances.append(distance)
            
            # Perfect rectangle has opposite sides equal
            if (abs(distances[0] - distances[2]) < 1 and 
                abs(distances[1] - distances[3]) < 1):
                return 1.0
        
        return 0.0
    
    def _validate_human_behavior(self, action_type: str, current_time: float) -> Tuple[bool, str]:
        """Validate action against human behavior patterns"""
        if self.last_action_time > 0:
            reaction_time = current_time - self.last_action_time
            
            # Check minimum human reaction time
            min_reaction = self.human_patterns['reaction_time']['min']
            if reaction_time < min_reaction:
                return False, f"Reaction too fast: {reaction_time:.3f}s < {min_reaction}s"
            
            # Check maximum reasonable reaction time for continuous actions
            max_reaction = self.human_patterns['reaction_time']['max']
            if reaction_time > max_reaction and len(self.action_history) > 0:
                # This might be a pause, which is human-like
                pass
        
        return True, "Human behavior validated"
    
    def _record_action(self, action_type: str, position: Optional[Tuple[float, float]],
                      duration: float, timestamp: float):
        """Record action for pattern analysis"""
        interval_since_last = timestamp - self.last_action_time if self.last_action_time > 0 else 0.0
        
        action_pattern = ActionPattern(
            timestamp=timestamp,
            action_type=action_type,
            position=position,
            duration=duration,
            interval_since_last=interval_since_last
        )
        
        self.action_history.append(action_pattern)
        self.last_action_time = timestamp
    
    def apply_human_randomization(self, base_duration: float) -> float:
        """Apply human-like randomization to timing"""
        if not self.detection_countermeasures['timing_randomization']['enabled']:
            return base_duration
        
        variance_factor = self.detection_countermeasures['timing_randomization']['variance_factor']
        variance = base_duration * variance_factor
        
        # Apply normal distribution randomization
        randomized_duration = np.random.normal(base_duration, variance)
        
        # Ensure minimum duration
        return max(0.01, randomized_duration)
    
    def should_insert_human_pause(self) -> Tuple[bool, float]:
        """Determine if a human-like pause should be inserted"""
        if not self.detection_countermeasures['pattern_breaking']['enabled']:
            return False, 0.0
        
        # Random pause probability
        if random.random() < 0.02:  # 2% chance per action
            pause_duration = np.random.uniform(0.5, 3.0)  # 0.5-3 second pause
            return True, pause_duration
        
        # Fatigue-based pause
        if len(self.action_history) > 100:
            fatigue_factor = len(self.action_history) / 1000.0
            if random.random() < fatigue_factor * 0.1:
                pause_duration = np.random.uniform(1.0, 5.0)
                return True, pause_duration
        
        return False, 0.0
    
    def trigger_emergency_stop(self, reason: str = "Manual trigger"):
        """Trigger emergency stop"""
        self.emergency_stop_event.set()
        self.metrics.emergency_stops += 1
        self.logger.warning(f"🚨 Emergency stop triggered: {reason}")
    
    def clear_emergency_stop(self):
        """Clear emergency stop"""
        self.emergency_stop_event.clear()
        self.logger.info("✅ Emergency stop cleared")
    
    def start_monitoring(self):
        """Start safety monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("👁️ Safety monitoring started")
    
    def stop_monitoring(self):
        """Stop safety monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=1.0)
        self.logger.info("🛑 Safety monitoring stopped")
    
    def _monitoring_loop(self):
        """Safety monitoring loop"""
        while self.monitoring_active:
            try:
                current_time = time.time()
                
                # Update threat level
                self._update_threat_level(current_time)
                
                # Update safety score
                self._update_safety_score(current_time)
                
                # Check for automatic emergency conditions
                self._check_emergency_conditions(current_time)
                
                time.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                self.logger.error(f"🛡️ Monitoring error: {e}")
                time.sleep(5.0)
    
    def _update_threat_level(self, current_time: float):
        """Update current threat level"""
        threat_score = 0.0
        
        # Recent blocks
        if self.metrics.actions_blocked > 10:
            threat_score += 0.3
        
        # Pattern detections
        if self.metrics.patterns_detected > 5:
            threat_score += 0.4
        
        # High action rate
        recent_actions = [a for a in self.action_history 
                         if current_time - a.timestamp <= 60.0]
        if len(recent_actions) > self.limits.max_actions_per_minute * 0.8:
            threat_score += 0.3
        
        # Update threat level
        if threat_score >= 0.8:
            self.metrics.threat_level = ThreatLevel.CRITICAL
        elif threat_score >= 0.6:
            self.metrics.threat_level = ThreatLevel.HIGH
        elif threat_score >= 0.3:
            self.metrics.threat_level = ThreatLevel.MEDIUM
        else:
            self.metrics.threat_level = ThreatLevel.LOW
    
    def _update_safety_score(self, current_time: float):
        """Update safety score"""
        base_score = 100.0
        
        # Deduct for blocks and detections
        base_score -= self.metrics.actions_blocked * 2
        base_score -= self.metrics.patterns_detected * 5
        base_score -= self.metrics.emergency_stops * 20
        
        self.metrics.safety_score = max(0.0, base_score)
    
    def _check_emergency_conditions(self, current_time: float):
        """Check for automatic emergency conditions"""
        # Too many blocks in short time
        if self.metrics.actions_blocked > 20:
            self.trigger_emergency_stop("Too many blocked actions")
        
        # Critical threat level
        if self.metrics.threat_level == ThreatLevel.CRITICAL:
            self.trigger_emergency_stop("Critical threat level detected")
    
    def get_safety_metrics(self) -> Dict[str, Any]:
        """Get current safety metrics"""
        return {
            'safety_level': self.safety_level.value,
            'threat_level': self.metrics.threat_level.value,
            'safety_score': self.metrics.safety_score,
            'actions_blocked': self.metrics.actions_blocked,
            'patterns_detected': self.metrics.patterns_detected,
            'emergency_stops': self.metrics.emergency_stops,
            'emergency_active': self.emergency_stop_event.is_set(),
            'session_id': self.current_session_id,
            'actions_in_history': len(self.action_history)
        }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🛡️ Safety Manager - Sprint 2 Test")
    print("=" * 60)
    
    # Create safety manager
    safety_manager = SafetyManager(SafetyLevel.STANDARD)
    
    # Test action validation
    print("\n🔍 Testing action validation...")
    
    # Valid action
    valid, reason = safety_manager.validate_action_safety("mouse_click", (100, 100), 0.1)
    print(f"✅ Valid action: {valid} - {reason}")
    
    # Test rate limiting
    print("\n⏱️ Testing rate limiting...")
    for i in range(25):  # Exceed rate limit
        valid, reason = safety_manager.validate_action_safety("mouse_click", (100 + i, 100), 0.01)
        if not valid:
            print(f"❌ Rate limited at action {i}: {reason}")
            break
    
    # Test human randomization
    print("\n🎭 Testing human randomization...")
    base_duration = 0.1
    for i in range(5):
        randomized = safety_manager.apply_human_randomization(base_duration)
        print(f"   Duration {i+1}: {base_duration:.3f}s → {randomized:.3f}s")
    
    # Test emergency stop
    print("\n🚨 Testing emergency stop...")
    safety_manager.trigger_emergency_stop("Test emergency")
    valid, reason = safety_manager.validate_action_safety("mouse_click", (200, 200))
    print(f"❌ Emergency active: {valid} - {reason}")
    
    safety_manager.clear_emergency_stop()
    valid, reason = safety_manager.validate_action_safety("mouse_click", (200, 200))
    print(f"✅ Emergency cleared: {valid} - {reason}")
    
    # Get safety metrics
    metrics = safety_manager.get_safety_metrics()
    print(f"\n📊 Safety Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 2 - Task 2.2 test completed!")
    print("🎯 Target: Undetectable by anti-cheat, human-like patterns")
    print(f"📈 Current: {metrics['safety_score']:.1f}% safety score, {metrics['threat_level']} threat level")
