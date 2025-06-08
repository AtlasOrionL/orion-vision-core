#!/usr/bin/env python3
"""
🎯 Q02.1.2 - Dynamic Target Selection System
💖 DUYGULANDIK! SEN YAPARSIN! HEDEF BELİRLEME GÜCÜYLE!

Bu modül Q02.1.1 Environment Sensor'dan gelen çevre analizine göre
akıllı hedef seçimi ve önceliklendirme yapar. ALT_LAS'ın ne yapacağını
dinamik olarak belirler.

Author: Orion Vision Core Team
Status: 🎯 Q02.1.2 DEVELOPMENT STARTED
"""

import os
import sys
import time
import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Q02.1.1 Environment Sensor import
try:
    from q02_environment_sensor import EnvironmentSensor, EnvironmentContext, EnvironmentType, ContextLevel
    print("✅ Q02.1.1 Environment Sensor imported successfully")
except ImportError as e:
    print(f"⚠️ Q02.1.1 import warning: {e}")

class TargetType(Enum):
    """Target types for dynamic selection"""
    UI_ELEMENT = "ui_element"
    TEXT_CONTENT = "text_content"
    WINDOW = "window"
    APPLICATION = "application"
    COORDINATE = "coordinate"
    REGION = "region"
    UNKNOWN = "unknown"

class TargetPriority(Enum):
    """Target priority levels"""
    CRITICAL = "critical"      # Must be handled immediately
    HIGH = "high"             # Important, handle soon
    MEDIUM = "medium"         # Normal priority
    LOW = "low"              # Can be delayed
    BACKGROUND = "background" # Handle when idle

class SelectionStrategy(Enum):
    """Target selection strategies"""
    PROXIMITY = "proximity"           # Closest to current position
    PRIORITY = "priority"            # Highest priority first
    CONTEXT_AWARE = "context_aware"  # Based on current context
    USER_INTENT = "user_intent"      # Based on predicted user intent
    EFFICIENCY = "efficiency"        # Most efficient path
    ADAPTIVE = "adaptive"            # Learning-based selection

@dataclass
class Target:
    """Target data structure"""
    target_id: str
    target_type: TargetType
    position: Tuple[int, int]
    size: Tuple[int, int]
    priority: TargetPriority
    confidence: float
    metadata: Dict[str, Any]
    timestamp: datetime
    context_relevance: float = 0.0
    accessibility_score: float = 0.0

@dataclass
class TargetSelection:
    """Target selection result"""
    selected_target: Optional[Target]
    alternative_targets: List[Target]
    selection_strategy: SelectionStrategy
    selection_confidence: float
    selection_time: float
    reasoning: str

class DynamicTargetSelector:
    """
    🎯 Q02.1.2: Dynamic Target Selector
    
    Environment Sensor'dan gelen çevre analizine göre akıllı hedef seçimi yapar.
    WAKE UP ORION! HEDEF BELİRLEME GÜCÜYLE!
    """
    
    def __init__(self):
        self.logger = logging.getLogger('orion.q02.target_selector')
        
        # Environment Sensor integration
        self.environment_sensor = None
        self.current_context = None
        
        # Target selection settings
        self.selection_strategy = SelectionStrategy.CONTEXT_AWARE
        self.priority_weights = {
            TargetPriority.CRITICAL: 1.0,
            TargetPriority.HIGH: 0.8,
            TargetPriority.MEDIUM: 0.6,
            TargetPriority.LOW: 0.4,
            TargetPriority.BACKGROUND: 0.2
        }
        
        # State tracking
        self.detected_targets = []
        self.selection_history = []
        self.performance_metrics = {
            'total_selections': 0,
            'successful_selections': 0,
            'average_selection_time': 0.0,
            'strategy_usage': {strategy: 0 for strategy in SelectionStrategy},
            'target_type_distribution': {target_type: 0 for target_type in TargetType}
        }
        
        self.initialized = False
        
        self.logger.info("🎯 Dynamic Target Selector initialized")
        self.logger.info("💖 DUYGULANDIK! Q02.1.2 HEDEF BELİRLEME!")
    
    def initialize(self) -> bool:
        """Initialize target selector with environment sensor"""
        try:
            self.logger.info("🚀 Initializing Dynamic Target Selector...")
            self.logger.info("🔗 Setting up Environment Sensor connection...")
            
            # Initialize Environment Sensor
            self.environment_sensor = EnvironmentSensor()
            if not self.environment_sensor.initialize():
                self.logger.warning("⚠️ Environment Sensor initialization failed, using simulation")
            
            # Test target detection
            test_result = self._test_target_detection()
            
            if test_result['success']:
                self.initialized = True
                self.logger.info("✅ Dynamic Target Selector initialized successfully!")
                self.logger.info("🎯 Q02.1.2: HEDEF BELİRLEME HAZIR!")
                return True
            else:
                self.logger.error(f"❌ Target Selector initialization failed: {test_result['error']}")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Target Selector initialization error: {e}")
            return False
    
    def _test_target_detection(self) -> Dict[str, Any]:
        """Test basic target detection functionality"""
        try:
            # Test environment context retrieval
            if self.environment_sensor:
                context = self.environment_sensor.analyze_environment()
                if not context:
                    return {'success': False, 'error': 'Environment context test failed'}
            
            # Test basic target detection
            test_targets = self._detect_targets_from_context(None)
            
            if test_targets:
                return {
                    'success': True,
                    'targets_detected': len(test_targets),
                    'test_mode': 'simulation'
                }
            else:
                return {'success': False, 'error': 'Target detection test failed'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def select_target(self, strategy: Optional[SelectionStrategy] = None) -> Optional[TargetSelection]:
        """
        Select optimal target based on current environment and strategy
        
        Args:
            strategy: Selection strategy to use (default: current strategy)
            
        Returns:
            TargetSelection with selected target and alternatives
        """
        if not self.initialized:
            self.logger.error("❌ Target Selector not initialized")
            return None
        
        start_time = time.time()
        
        try:
            self.logger.info("🎯 Selecting optimal target...")
            
            # Use provided strategy or default
            selection_strategy = strategy or self.selection_strategy
            
            # Get current environment context
            context = self._get_current_context()
            if not context:
                self.logger.warning("⚠️ No environment context available")
                return None
            
            # Detect available targets
            targets = self._detect_targets_from_context(context)
            if not targets:
                self.logger.warning("⚠️ No targets detected in current context")
                return None
            
            # Select optimal target based on strategy
            selection = self._apply_selection_strategy(targets, selection_strategy, context)
            
            if selection:
                # Update performance metrics
                selection_time = time.time() - start_time
                self.performance_metrics['total_selections'] += 1
                self.performance_metrics['successful_selections'] += 1
                self.performance_metrics['average_selection_time'] = (
                    (self.performance_metrics['average_selection_time'] * 
                     (self.performance_metrics['total_selections'] - 1) + selection_time) /
                    self.performance_metrics['total_selections']
                )
                self.performance_metrics['strategy_usage'][selection_strategy] += 1
                
                if selection.selected_target:
                    self.performance_metrics['target_type_distribution'][selection.selected_target.target_type] += 1
                
                # Update selection history
                self.selection_history.append(selection)
                if len(self.selection_history) > 100:  # Keep last 100 selections
                    self.selection_history.pop(0)
                
                self.logger.info(f"✅ Target selected: {selection.selected_target.target_type.value if selection.selected_target else 'None'} "
                               f"(confidence: {selection.selection_confidence:.2f})")
                return selection
            else:
                self.logger.warning("⚠️ Target selection failed")
                return None
                
        except Exception as e:
            selection_time = time.time() - start_time
            self.logger.error(f"❌ Target selection error: {e}")
            return None
    
    def _get_current_context(self) -> Optional[EnvironmentContext]:
        """Get current environment context"""
        try:
            if self.environment_sensor:
                context = self.environment_sensor.analyze_environment()
                self.current_context = context
                return context
            else:
                # Simulation fallback
                from q02_environment_sensor import EnvironmentContext, EnvironmentType, ContextLevel
                return EnvironmentContext(
                    environment_type=EnvironmentType.DESKTOP,
                    active_windows=['Simulated Window'],
                    ui_elements=[{'type': 'simulation', 'text': 'Simulated UI'}],
                    text_content=['Simulation mode active'],
                    visual_features={'simulation': True},
                    context_level=ContextLevel.BASIC,
                    confidence=0.5,
                    timestamp=datetime.now(),
                    metadata={'simulation_mode': True}
                )
        except Exception as e:
            self.logger.error(f"❌ Context retrieval error: {e}")
            return None
    
    def _detect_targets_from_context(self, context: Optional[EnvironmentContext]) -> List[Target]:
        """Detect available targets from environment context"""
        try:
            targets = []
            
            if context:
                # Extract targets from UI elements
                for i, ui_element in enumerate(context.ui_elements):
                    target = Target(
                        target_id=f"ui_{i}",
                        target_type=TargetType.UI_ELEMENT,
                        position=ui_element.get('position', (100 + i * 50, 100 + i * 30)),
                        size=(100, 30),
                        priority=self._determine_ui_priority(ui_element),
                        confidence=0.8,
                        metadata=ui_element,
                        timestamp=datetime.now(),
                        context_relevance=self._calculate_context_relevance(ui_element, context),
                        accessibility_score=self._calculate_accessibility_score(ui_element)
                    )
                    targets.append(target)
                
                # Extract targets from text content
                for i, text in enumerate(context.text_content):
                    if len(text.strip()) > 3:  # Only meaningful text
                        target = Target(
                            target_id=f"text_{i}",
                            target_type=TargetType.TEXT_CONTENT,
                            position=(200 + i * 60, 150 + i * 25),
                            size=(len(text) * 8, 20),
                            priority=self._determine_text_priority(text),
                            confidence=0.7,
                            metadata={'text': text},
                            timestamp=datetime.now(),
                            context_relevance=self._calculate_text_relevance(text, context),
                            accessibility_score=0.9  # Text is usually accessible
                        )
                        targets.append(target)
            else:
                # Simulation targets
                simulation_targets = [
                    Target(
                        target_id="sim_button",
                        target_type=TargetType.UI_ELEMENT,
                        position=(100, 100),
                        size=(100, 30),
                        priority=TargetPriority.HIGH,
                        confidence=0.8,
                        metadata={'type': 'button', 'text': 'Simulated Button'},
                        timestamp=datetime.now(),
                        context_relevance=0.7,
                        accessibility_score=0.9
                    ),
                    Target(
                        target_id="sim_input",
                        target_type=TargetType.UI_ELEMENT,
                        position=(200, 150),
                        size=(150, 25),
                        priority=TargetPriority.MEDIUM,
                        confidence=0.7,
                        metadata={'type': 'input', 'text': 'Simulated Input'},
                        timestamp=datetime.now(),
                        context_relevance=0.6,
                        accessibility_score=0.8
                    )
                ]
                targets.extend(simulation_targets)
            
            self.detected_targets = targets
            return targets
            
        except Exception as e:
            self.logger.error(f"❌ Target detection error: {e}")
            return []
    
    def _apply_selection_strategy(self, targets: List[Target], strategy: SelectionStrategy, 
                                context: EnvironmentContext) -> Optional[TargetSelection]:
        """Apply selection strategy to choose optimal target"""
        try:
            if not targets:
                return None
            
            start_time = time.time()
            
            if strategy == SelectionStrategy.PRIORITY:
                selected = self._select_by_priority(targets)
                reasoning = "Selected highest priority target"
            elif strategy == SelectionStrategy.PROXIMITY:
                selected = self._select_by_proximity(targets)
                reasoning = "Selected closest target"
            elif strategy == SelectionStrategy.CONTEXT_AWARE:
                selected = self._select_by_context(targets, context)
                reasoning = "Selected most context-relevant target"
            elif strategy == SelectionStrategy.EFFICIENCY:
                selected = self._select_by_efficiency(targets)
                reasoning = "Selected most efficient target"
            elif strategy == SelectionStrategy.ADAPTIVE:
                selected = self._select_by_adaptive_learning(targets, context)
                reasoning = "Selected based on learning patterns"
            else:
                selected = targets[0] if targets else None
                reasoning = "Default selection (first target)"
            
            if selected:
                # Remove selected from alternatives
                alternatives = [t for t in targets if t.target_id != selected.target_id]
                
                # Calculate selection confidence
                confidence = self._calculate_selection_confidence(selected, alternatives, strategy)
                
                selection_time = time.time() - start_time
                
                return TargetSelection(
                    selected_target=selected,
                    alternative_targets=alternatives,
                    selection_strategy=strategy,
                    selection_confidence=confidence,
                    selection_time=selection_time,
                    reasoning=reasoning
                )
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Selection strategy error: {e}")
            return None
    
    def _select_by_priority(self, targets: List[Target]) -> Optional[Target]:
        """Select target by priority"""
        if not targets:
            return None
        return max(targets, key=lambda t: self.priority_weights[t.priority])
    
    def _select_by_proximity(self, targets: List[Target]) -> Optional[Target]:
        """Select target by proximity (closest to center)"""
        if not targets:
            return None
        center = (960, 540)  # Assume 1920x1080 screen
        return min(targets, key=lambda t: 
                  ((t.position[0] - center[0])**2 + (t.position[1] - center[1])**2)**0.5)
    
    def _select_by_context(self, targets: List[Target], context: EnvironmentContext) -> Optional[Target]:
        """Select target by context relevance"""
        if not targets:
            return None
        return max(targets, key=lambda t: t.context_relevance)
    
    def _select_by_efficiency(self, targets: List[Target]) -> Optional[Target]:
        """Select target by efficiency (accessibility + confidence)"""
        if not targets:
            return None
        return max(targets, key=lambda t: t.accessibility_score * t.confidence)
    
    def _select_by_adaptive_learning(self, targets: List[Target], context: EnvironmentContext) -> Optional[Target]:
        """Select target based on learning patterns (simplified)"""
        # For now, use context-aware selection
        # In future, implement ML-based selection
        return self._select_by_context(targets, context)
    
    def _determine_ui_priority(self, ui_element: Dict[str, Any]) -> TargetPriority:
        """Determine priority of UI element"""
        element_type = ui_element.get('type', '').lower()
        if 'button' in element_type:
            return TargetPriority.HIGH
        elif 'input' in element_type:
            return TargetPriority.MEDIUM
        elif 'window' in element_type:
            return TargetPriority.LOW
        else:
            return TargetPriority.MEDIUM
    
    def _determine_text_priority(self, text: str) -> TargetPriority:
        """Determine priority of text content"""
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ['error', 'warning', 'alert']):
            return TargetPriority.CRITICAL
        elif any(keyword in text_lower for keyword in ['button', 'click', 'submit']):
            return TargetPriority.HIGH
        else:
            return TargetPriority.MEDIUM
    
    def _calculate_context_relevance(self, element: Dict[str, Any], context: EnvironmentContext) -> float:
        """Calculate how relevant element is to current context"""
        # Simplified relevance calculation
        base_relevance = 0.5
        
        # Boost relevance based on environment type
        if context.environment_type == EnvironmentType.WEB_BROWSER:
            if 'link' in element.get('type', '').lower():
                base_relevance += 0.3
        elif context.environment_type == EnvironmentType.APPLICATION:
            if 'button' in element.get('type', '').lower():
                base_relevance += 0.2
        
        return min(base_relevance, 1.0)
    
    def _calculate_text_relevance(self, text: str, context: EnvironmentContext) -> float:
        """Calculate text relevance to context"""
        # Simplified text relevance
        base_relevance = 0.4
        
        # Boost for action words
        action_words = ['click', 'submit', 'save', 'open', 'close']
        if any(word in text.lower() for word in action_words):
            base_relevance += 0.3
        
        return min(base_relevance, 1.0)
    
    def _calculate_accessibility_score(self, element: Dict[str, Any]) -> float:
        """Calculate how accessible/clickable element is"""
        # Simplified accessibility scoring
        base_score = 0.7
        
        element_type = element.get('type', '').lower()
        if 'button' in element_type:
            base_score = 0.9
        elif 'input' in element_type:
            base_score = 0.8
        elif 'text' in element_type:
            base_score = 0.6
        
        return base_score
    
    def _calculate_selection_confidence(self, selected: Target, alternatives: List[Target], 
                                      strategy: SelectionStrategy) -> float:
        """Calculate confidence in target selection"""
        base_confidence = selected.confidence
        
        # Boost confidence based on strategy match
        if strategy == SelectionStrategy.PRIORITY and selected.priority in [TargetPriority.CRITICAL, TargetPriority.HIGH]:
            base_confidence += 0.1
        elif strategy == SelectionStrategy.CONTEXT_AWARE and selected.context_relevance > 0.7:
            base_confidence += 0.1
        
        # Reduce confidence if many similar alternatives
        if len(alternatives) > 5:
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get target selector performance metrics"""
        return {
            'total_selections': self.performance_metrics['total_selections'],
            'successful_selections': self.performance_metrics['successful_selections'],
            'success_rate': (
                self.performance_metrics['successful_selections'] / 
                self.performance_metrics['total_selections']
                if self.performance_metrics['total_selections'] > 0 else 0
            ),
            'average_selection_time': self.performance_metrics['average_selection_time'],
            'strategy_usage': dict(self.performance_metrics['strategy_usage']),
            'target_type_distribution': dict(self.performance_metrics['target_type_distribution']),
            'current_strategy': self.selection_strategy.value,
            'detected_targets_count': len(self.detected_targets),
            'selection_history_size': len(self.selection_history)
        }
    
    def set_selection_strategy(self, strategy: SelectionStrategy):
        """Set target selection strategy"""
        self.selection_strategy = strategy
        self.logger.info(f"🎯 Selection strategy changed to: {strategy.value}")

# Example usage and testing
if __name__ == "__main__":
    print("🎯 Q02.1.2 - Dynamic Target Selector Test")
    print("💖 DUYGULANDIK! SEN YAPARSIN!")
    print("🌟 WAKE UP ORION! HEDEF BELİRLEME GÜCÜYLE!")
    print()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    # Test target selector
    selector = DynamicTargetSelector()
    if selector.initialize():
        print("✅ Target Selector initialized")
        
        # Test target selection
        selection = selector.select_target()
        if selection and selection.selected_target:
            print(f"✅ Target selected: {selection.selected_target.target_type.value}")
            print(f"📊 Confidence: {selection.selection_confidence:.2f}")
            print(f"🎯 Strategy: {selection.selection_strategy.value}")
            print(f"💭 Reasoning: {selection.reasoning}")
            print(f"🔍 Alternatives: {len(selection.alternative_targets)}")
        else:
            print("❌ Target selection failed")
        
        # Show performance metrics
        metrics = selector.get_performance_metrics()
        print(f"📊 Success Rate: {metrics['success_rate']:.2f}")
        print(f"⏱️ Avg Selection Time: {metrics['average_selection_time']:.3f}s")
        
    else:
        print("❌ Target Selector initialization failed")
    
    print()
    print("🎉 Q02.1.2 Target Selector test completed!")
    print("💖 DUYGULANDIK! HEDEF BELİRLEME ÇALIŞIYOR!")
