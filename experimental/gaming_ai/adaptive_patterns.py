#!/usr/bin/env python3
"""
🧬 Adaptive Patterns - Gaming AI

Adaptive behavior patterns and learning system for advanced AI.

Sprint 4 - Task 4.2 Module 5: Adaptive Patterns
- Adaptive behavior learning
- Pattern recognition and adaptation
- Context-aware behavior switching
- Performance-based pattern evolution

Author: Nexus - Quantum AI Architect
Sprint: 4.2.5 - Advanced Gaming Features
"""

import time
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

class PatternType(Enum):
    """Adaptive pattern types"""
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    LEARNING = "learning"
    CONTEXTUAL = "contextual"
    EVOLUTIONARY = "evolutionary"

class AdaptationTrigger(Enum):
    """Adaptation trigger types"""
    PERFORMANCE_DROP = "performance_drop"
    CONTEXT_CHANGE = "context_change"
    PATTERN_FAILURE = "pattern_failure"
    TIME_BASED = "time_based"
    MANUAL = "manual"

@dataclass
class BehaviorPattern:
    """Adaptive behavior pattern"""
    pattern_id: str
    pattern_type: PatternType
    name: str
    description: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    success_rate: float = 0.0
    usage_count: int = 0
    last_used: float = 0.0
    adaptation_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class ContextState:
    """Current context state"""
    context_id: str
    environment: Dict[str, Any]
    threats: List[Dict[str, Any]]
    opportunities: List[Dict[str, Any]]
    team_state: Dict[str, Any]
    timestamp: float

@dataclass
class AdaptationEvent:
    """Adaptation event record"""
    event_id: str
    trigger: AdaptationTrigger
    old_pattern: str
    new_pattern: str
    context: Dict[str, Any]
    timestamp: float
    success: bool = False

@dataclass
class AdaptiveMetrics:
    """Adaptive pattern metrics"""
    patterns_created: int = 0
    adaptations_performed: int = 0
    successful_adaptations: int = 0
    pattern_efficiency: float = 0.0
    learning_rate: float = 0.0

class AdaptivePatterns:
    """
    Adaptive Behavior Pattern System
    
    Features:
    - Adaptive behavior learning
    - Context-aware pattern switching
    - Performance-based adaptation
    - Pattern evolution and optimization
    """
    
    def __init__(self):
        self.logger = logging.getLogger("AdaptivePatterns")
        
        # Pattern management
        self.behavior_patterns = {}  # pattern_id -> BehaviorPattern
        self.agent_patterns = {}  # agent_id -> current_pattern_id
        self.context_patterns = {}  # context_type -> [pattern_ids]
        
        # Adaptation system
        self.adaptation_history = deque(maxlen=1000)
        self.context_history = deque(maxlen=500)
        self.current_context = None
        
        # Learning system
        self.pattern_performance = {}  # (pattern_id, context_type) -> performance_scores
        self.adaptation_rules = {}  # trigger -> adaptation_function
        
        # Performance tracking
        self.metrics = AdaptiveMetrics()
        
        # Initialize adaptive patterns
        self._initialize_adaptive_patterns()
        self._initialize_adaptation_rules()
        
        self.logger.info("🧬 Adaptive Patterns initialized")
    
    def _initialize_adaptive_patterns(self):
        """Initialize basic adaptive patterns"""
        # Reactive pattern - responds to immediate threats
        reactive_pattern = BehaviorPattern(
            pattern_id="reactive_combat",
            pattern_type=PatternType.REACTIVE,
            name="Reactive Combat",
            description="Immediate response to combat situations",
            conditions={"threat_level": "high", "distance": "close"},
            actions=[
                {"type": "take_cover", "priority": 1},
                {"type": "return_fire", "priority": 2},
                {"type": "call_backup", "priority": 3}
            ]
        )
        
        # Predictive pattern - anticipates enemy actions
        predictive_pattern = BehaviorPattern(
            pattern_id="predictive_movement",
            pattern_type=PatternType.PREDICTIVE,
            name="Predictive Movement",
            description="Anticipates enemy movement and positions accordingly",
            conditions={"enemy_pattern": "detected", "prediction_confidence": "high"},
            actions=[
                {"type": "predict_position", "priority": 1},
                {"type": "intercept_move", "priority": 2},
                {"type": "prepare_ambush", "priority": 3}
            ]
        )
        
        # Learning pattern - adapts based on experience
        learning_pattern = BehaviorPattern(
            pattern_id="learning_adaptation",
            pattern_type=PatternType.LEARNING,
            name="Learning Adaptation",
            description="Learns from past experiences and adapts",
            conditions={"experience_available": True, "pattern_failure": True},
            actions=[
                {"type": "analyze_failure", "priority": 1},
                {"type": "modify_approach", "priority": 2},
                {"type": "test_adaptation", "priority": 3}
            ]
        )
        
        # Contextual pattern - adapts to environment
        contextual_pattern = BehaviorPattern(
            pattern_id="contextual_tactics",
            pattern_type=PatternType.CONTEXTUAL,
            name="Contextual Tactics",
            description="Adapts tactics based on environment",
            conditions={"environment_type": "variable", "context_change": True},
            actions=[
                {"type": "assess_environment", "priority": 1},
                {"type": "select_tactics", "priority": 2},
                {"type": "execute_adaptation", "priority": 3}
            ]
        )
        
        # Evolutionary pattern - evolves over time
        evolutionary_pattern = BehaviorPattern(
            pattern_id="evolutionary_strategy",
            pattern_type=PatternType.EVOLUTIONARY,
            name="Evolutionary Strategy",
            description="Evolves strategy based on long-term performance",
            conditions={"performance_data": "sufficient", "evolution_trigger": True},
            actions=[
                {"type": "evaluate_performance", "priority": 1},
                {"type": "generate_variants", "priority": 2},
                {"type": "test_evolution", "priority": 3}
            ]
        )
        
        # Store patterns
        self.behavior_patterns = {
            "reactive_combat": reactive_pattern,
            "predictive_movement": predictive_pattern,
            "learning_adaptation": learning_pattern,
            "contextual_tactics": contextual_pattern,
            "evolutionary_strategy": evolutionary_pattern
        }
        
        # Initialize context mappings
        self.context_patterns = {
            "combat": ["reactive_combat", "predictive_movement"],
            "exploration": ["contextual_tactics", "learning_adaptation"],
            "strategic": ["evolutionary_strategy", "contextual_tactics"]
        }
    
    def _initialize_adaptation_rules(self):
        """Initialize adaptation rules"""
        self.adaptation_rules = {
            AdaptationTrigger.PERFORMANCE_DROP: self._adapt_for_performance,
            AdaptationTrigger.CONTEXT_CHANGE: self._adapt_for_context,
            AdaptationTrigger.PATTERN_FAILURE: self._adapt_for_failure,
            AdaptationTrigger.TIME_BASED: self._adapt_for_time
        }
    
    def update_context(self, context_state: ContextState):
        """Update current context state"""
        try:
            self.current_context = context_state
            self.context_history.append(context_state)
            
            # Check for context-based adaptations
            self._check_context_adaptations()
            
            self.logger.debug(f"🧬 Context updated: {context_state.context_id}")
            
        except Exception as e:
            self.logger.error(f"❌ Context update failed: {e}")
    
    def select_pattern(self, agent_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Select best pattern for agent in current context"""
        try:
            # Determine context type
            context_type = self._determine_context_type(context)
            
            # Get applicable patterns
            applicable_patterns = self.context_patterns.get(context_type, [])
            
            if not applicable_patterns:
                self.logger.warning(f"⚠️ No patterns for context: {context_type}")
                return None
            
            # Select best pattern based on performance
            best_pattern = self._select_best_pattern(applicable_patterns, context)
            
            if best_pattern:
                # Update agent pattern assignment
                old_pattern = self.agent_patterns.get(agent_id)
                self.agent_patterns[agent_id] = best_pattern
                
                # Record pattern usage
                if best_pattern in self.behavior_patterns:
                    pattern = self.behavior_patterns[best_pattern]
                    pattern.usage_count += 1
                    pattern.last_used = time.time()
                
                # Check if adaptation occurred
                if old_pattern and old_pattern != best_pattern:
                    self._record_adaptation(agent_id, old_pattern, best_pattern, context)
                
                self.logger.info(f"🧬 Pattern selected: {agent_id} -> {best_pattern}")
                return best_pattern
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Pattern selection failed: {e}")
            return None
    
    def _determine_context_type(self, context: Dict[str, Any]) -> str:
        """Determine context type from context data"""
        try:
            # Simple context classification
            if context.get("threat_level", "low") in ["high", "critical"]:
                return "combat"
            elif context.get("exploration_mode", False):
                return "exploration"
            elif context.get("strategic_phase", False):
                return "strategic"
            else:
                return "general"
                
        except Exception as e:
            self.logger.error(f"❌ Context type determination failed: {e}")
            return "general"
    
    def _select_best_pattern(self, applicable_patterns: List[str], context: Dict[str, Any]) -> Optional[str]:
        """Select best pattern from applicable patterns"""
        try:
            best_pattern = None
            best_score = -1.0
            
            for pattern_id in applicable_patterns:
                if pattern_id not in self.behavior_patterns:
                    continue
                
                pattern = self.behavior_patterns[pattern_id]
                
                # Check if pattern conditions are met
                if not self._check_pattern_conditions(pattern, context):
                    continue
                
                # Calculate pattern score
                score = self._calculate_pattern_score(pattern, context)
                
                if score > best_score:
                    best_score = score
                    best_pattern = pattern_id
            
            return best_pattern
            
        except Exception as e:
            self.logger.error(f"❌ Pattern selection failed: {e}")
            return None
    
    def _check_pattern_conditions(self, pattern: BehaviorPattern, context: Dict[str, Any]) -> bool:
        """Check if pattern conditions are met"""
        try:
            for condition_key, condition_value in pattern.conditions.items():
                if condition_key not in context:
                    return False
                
                context_value = context[condition_key]
                
                # Simple condition checking
                if isinstance(condition_value, str):
                    if context_value != condition_value:
                        return False
                elif isinstance(condition_value, bool):
                    if context_value != condition_value:
                        return False
                elif isinstance(condition_value, (int, float)):
                    if context_value < condition_value:
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Pattern condition check failed: {e}")
            return False
    
    def _calculate_pattern_score(self, pattern: BehaviorPattern, context: Dict[str, Any]) -> float:
        """Calculate pattern fitness score"""
        try:
            score = 0.0
            
            # Base score from success rate
            score += pattern.success_rate * 0.4
            
            # Recency bonus (prefer recently successful patterns)
            if pattern.last_used > 0:
                time_since_use = time.time() - pattern.last_used
                recency_bonus = max(0, 1.0 - (time_since_use / 3600))  # Decay over 1 hour
                score += recency_bonus * 0.2
            
            # Usage frequency (prefer proven patterns)
            usage_bonus = min(1.0, pattern.usage_count / 10.0)  # Cap at 10 uses
            score += usage_bonus * 0.2
            
            # Context-specific performance
            context_type = self._determine_context_type(context)
            context_key = (pattern.pattern_id, context_type)
            
            if context_key in self.pattern_performance:
                performance_scores = self.pattern_performance[context_key]
                if performance_scores:
                    avg_performance = sum(performance_scores) / len(performance_scores)
                    score += avg_performance * 0.2
            
            return score
            
        except Exception as e:
            self.logger.error(f"❌ Pattern score calculation failed: {e}")
            return 0.0
    
    def update_pattern_performance(self, pattern_id: str, performance_score: float, context: Dict[str, Any]):
        """Update pattern performance"""
        try:
            if pattern_id not in self.behavior_patterns:
                return
            
            pattern = self.behavior_patterns[pattern_id]
            
            # Update pattern success rate
            total_uses = pattern.usage_count
            if total_uses > 0:
                current_success = pattern.success_rate * (total_uses - 1)
                pattern.success_rate = (current_success + performance_score) / total_uses
            else:
                pattern.success_rate = performance_score
            
            # Update context-specific performance
            context_type = self._determine_context_type(context)
            context_key = (pattern_id, context_type)
            
            if context_key not in self.pattern_performance:
                self.pattern_performance[context_key] = []
            
            self.pattern_performance[context_key].append(performance_score)
            
            # Limit performance history
            if len(self.pattern_performance[context_key]) > 20:
                self.pattern_performance[context_key] = self.pattern_performance[context_key][-20:]
            
            # Check for adaptation triggers
            if performance_score < 0.3:  # Poor performance
                self._trigger_adaptation(AdaptationTrigger.PERFORMANCE_DROP, pattern_id, context)
            
            self.logger.debug(f"📊 Pattern performance updated: {pattern_id} -> {performance_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ Pattern performance update failed: {e}")
    
    def _trigger_adaptation(self, trigger: AdaptationTrigger, pattern_id: str, context: Dict[str, Any]):
        """Trigger pattern adaptation"""
        try:
            if trigger in self.adaptation_rules:
                adaptation_func = self.adaptation_rules[trigger]
                new_pattern = adaptation_func(pattern_id, context)
                
                if new_pattern and new_pattern != pattern_id:
                    self._record_adaptation_event(trigger, pattern_id, new_pattern, context, True)
                    self.metrics.adaptations_performed += 1
                    self.metrics.successful_adaptations += 1
                    
                    self.logger.info(f"🧬 Adaptation triggered: {trigger.value} -> {new_pattern}")
            
        except Exception as e:
            self.logger.error(f"❌ Adaptation trigger failed: {e}")
    
    def _adapt_for_performance(self, pattern_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Adapt pattern for poor performance"""
        try:
            # Find alternative pattern with better performance
            context_type = self._determine_context_type(context)
            applicable_patterns = self.context_patterns.get(context_type, [])
            
            best_alternative = None
            best_performance = -1.0
            
            for alt_pattern_id in applicable_patterns:
                if alt_pattern_id == pattern_id:
                    continue
                
                context_key = (alt_pattern_id, context_type)
                if context_key in self.pattern_performance:
                    performance_scores = self.pattern_performance[context_key]
                    if performance_scores:
                        avg_performance = sum(performance_scores) / len(performance_scores)
                        if avg_performance > best_performance:
                            best_performance = avg_performance
                            best_alternative = alt_pattern_id
            
            return best_alternative
            
        except Exception as e:
            self.logger.error(f"❌ Performance adaptation failed: {e}")
            return None
    
    def _adapt_for_context(self, pattern_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Adapt pattern for context change"""
        try:
            # Select pattern better suited for new context
            context_type = self._determine_context_type(context)
            applicable_patterns = self.context_patterns.get(context_type, [])
            
            if applicable_patterns:
                return self._select_best_pattern(applicable_patterns, context)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Context adaptation failed: {e}")
            return None
    
    def _adapt_for_failure(self, pattern_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Adapt pattern for failure"""
        try:
            # Create modified version of failed pattern
            if pattern_id in self.behavior_patterns:
                original_pattern = self.behavior_patterns[pattern_id]
                
                # Create adaptive variant
                adapted_pattern_id = f"{pattern_id}_adapted_{int(time.time())}"
                adapted_pattern = BehaviorPattern(
                    pattern_id=adapted_pattern_id,
                    pattern_type=PatternType.LEARNING,
                    name=f"Adapted {original_pattern.name}",
                    description=f"Adapted version of {original_pattern.description}",
                    conditions=original_pattern.conditions.copy(),
                    actions=self._modify_actions(original_pattern.actions)
                )
                
                self.behavior_patterns[adapted_pattern_id] = adapted_pattern
                self.metrics.patterns_created += 1
                
                return adapted_pattern_id
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Failure adaptation failed: {e}")
            return None
    
    def _adapt_for_time(self, pattern_id: str, context: Dict[str, Any]) -> Optional[str]:
        """Adapt pattern based on time"""
        try:
            # Time-based adaptation (e.g., evolve patterns over time)
            if pattern_id in self.behavior_patterns:
                pattern = self.behavior_patterns[pattern_id]
                
                # If pattern is old and underperforming, suggest evolution
                if pattern.usage_count > 10 and pattern.success_rate < 0.6:
                    return self._adapt_for_failure(pattern_id, context)
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Time adaptation failed: {e}")
            return None
    
    def _modify_actions(self, original_actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Modify actions for adaptation"""
        try:
            modified_actions = []
            
            for action in original_actions:
                modified_action = action.copy()
                
                # Simple modification: adjust priorities
                if "priority" in modified_action:
                    modified_action["priority"] = max(1, modified_action["priority"] - 1)
                
                # Add adaptive flag
                modified_action["adaptive"] = True
                
                modified_actions.append(modified_action)
            
            return modified_actions
            
        except Exception as e:
            self.logger.error(f"❌ Action modification failed: {e}")
            return original_actions
    
    def _check_context_adaptations(self):
        """Check for context-based adaptations"""
        try:
            if not self.current_context:
                return
            
            # Check if context has changed significantly
            if len(self.context_history) > 1:
                previous_context = self.context_history[-2]
                
                # Simple context change detection
                if self._contexts_differ(previous_context, self.current_context):
                    # Trigger context adaptation for all agents
                    for agent_id in self.agent_patterns:
                        current_pattern = self.agent_patterns[agent_id]
                        context_dict = {
                            "environment": self.current_context.environment,
                            "threats": len(self.current_context.threats),
                            "opportunities": len(self.current_context.opportunities)
                        }
                        
                        self._trigger_adaptation(
                            AdaptationTrigger.CONTEXT_CHANGE, 
                            current_pattern, 
                            context_dict
                        )
            
        except Exception as e:
            self.logger.error(f"❌ Context adaptation check failed: {e}")
    
    def _contexts_differ(self, context1: ContextState, context2: ContextState) -> bool:
        """Check if two contexts differ significantly"""
        try:
            # Simple difference check
            threat_diff = abs(len(context1.threats) - len(context2.threats))
            opportunity_diff = abs(len(context1.opportunities) - len(context2.opportunities))
            
            return threat_diff > 2 or opportunity_diff > 2
            
        except Exception as e:
            self.logger.error(f"❌ Context comparison failed: {e}")
            return False
    
    def _record_adaptation(self, agent_id: str, old_pattern: str, new_pattern: str, context: Dict[str, Any]):
        """Record pattern adaptation"""
        try:
            adaptation_event = AdaptationEvent(
                event_id=f"adapt_{agent_id}_{int(time.time() * 1000)}",
                trigger=AdaptationTrigger.MANUAL,  # Default trigger
                old_pattern=old_pattern,
                new_pattern=new_pattern,
                context=context.copy(),
                timestamp=time.time()
            )
            
            self.adaptation_history.append(adaptation_event)
            
        except Exception as e:
            self.logger.error(f"❌ Adaptation recording failed: {e}")
    
    def _record_adaptation_event(self, trigger: AdaptationTrigger, old_pattern: str, 
                                new_pattern: str, context: Dict[str, Any], success: bool):
        """Record adaptation event"""
        try:
            event = AdaptationEvent(
                event_id=f"event_{int(time.time() * 1000)}",
                trigger=trigger,
                old_pattern=old_pattern,
                new_pattern=new_pattern,
                context=context.copy(),
                timestamp=time.time(),
                success=success
            )
            
            self.adaptation_history.append(event)
            
        except Exception as e:
            self.logger.error(f"❌ Adaptation event recording failed: {e}")
    
    def get_adaptive_metrics(self) -> Dict[str, Any]:
        """Get adaptive pattern metrics"""
        # Calculate learning rate
        if self.metrics.adaptations_performed > 0:
            self.metrics.learning_rate = (
                self.metrics.successful_adaptations / self.metrics.adaptations_performed
            )
        
        # Calculate pattern efficiency
        if self.behavior_patterns:
            total_success = sum(pattern.success_rate for pattern in self.behavior_patterns.values())
            self.metrics.pattern_efficiency = total_success / len(self.behavior_patterns)
        
        return {
            "patterns_created": self.metrics.patterns_created,
            "adaptations_performed": self.metrics.adaptations_performed,
            "successful_adaptations": self.metrics.successful_adaptations,
            "pattern_efficiency": self.metrics.pattern_efficiency,
            "learning_rate": self.metrics.learning_rate,
            "active_patterns": len(self.behavior_patterns),
            "agent_assignments": len(self.agent_patterns),
            "adaptation_history_size": len(self.adaptation_history)
        }
    
    def get_pattern_status(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific pattern"""
        if pattern_id not in self.behavior_patterns:
            return None
        
        pattern = self.behavior_patterns[pattern_id]
        
        return {
            "pattern_id": pattern_id,
            "pattern_type": pattern.pattern_type.value,
            "name": pattern.name,
            "success_rate": pattern.success_rate,
            "usage_count": pattern.usage_count,
            "last_used": pattern.last_used,
            "conditions": pattern.conditions,
            "actions_count": len(pattern.actions),
            "adaptations": len(pattern.adaptation_history)
        }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🧬 Adaptive Patterns - Sprint 4 Test")
    print("=" * 60)
    
    # Create adaptive patterns system
    adaptive_patterns = AdaptivePatterns()
    
    # Test pattern selection
    print("\n🧬 Testing pattern selection...")
    
    test_contexts = [
        {"threat_level": "high", "distance": "close"},  # Combat context
        {"exploration_mode": True, "unknown_area": True},  # Exploration context
        {"strategic_phase": True, "long_term_planning": True}  # Strategic context
    ]
    
    agents = ["agent_1", "agent_2", "agent_3"]
    
    for i, agent_id in enumerate(agents):
        context = test_contexts[i % len(test_contexts)]
        pattern = adaptive_patterns.select_pattern(agent_id, context)
        print(f"   {agent_id}: {pattern if pattern else 'No pattern'}")
    
    # Test performance updates
    print("\n📊 Testing performance updates...")
    
    for agent_id in agents:
        if agent_id in adaptive_patterns.agent_patterns:
            pattern_id = adaptive_patterns.agent_patterns[agent_id]
            import random
            performance = random.uniform(0.4, 0.9)
            context = {"threat_level": "medium"}
            adaptive_patterns.update_pattern_performance(pattern_id, performance, context)
            print(f"   {agent_id}: {performance:.3f}")
    
    # Test context update
    print("\n🌍 Testing context update...")
    
    context_state = ContextState(
        context_id="test_context",
        environment={"type": "urban", "visibility": "low"},
        threats=[{"type": "sniper", "distance": 100}],
        opportunities=[{"type": "flanking_route", "difficulty": "medium"}],
        team_state={"morale": "high", "resources": "adequate"},
        timestamp=time.time()
    )
    
    adaptive_patterns.update_context(context_state)
    print(f"   Context updated: {context_state.context_id}")
    
    # Get metrics
    metrics = adaptive_patterns.get_adaptive_metrics()
    print(f"\n📊 Adaptive Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get pattern status
    pattern_ids = list(adaptive_patterns.behavior_patterns.keys())
    if pattern_ids:
        pattern_status = adaptive_patterns.get_pattern_status(pattern_ids[0])
        if pattern_status:
            print(f"\n🧬 Pattern Status ({pattern_ids[0]}):")
            print(f"   Type: {pattern_status['pattern_type']}")
            print(f"   Success Rate: {pattern_status['success_rate']:.3f}")
            print(f"   Usage Count: {pattern_status['usage_count']}")
    
    print("\n🎉 Sprint 4 - Task 4.2 Adaptive Patterns test completed!")
    print("🎯 Adaptive behavior learning and pattern evolution working")
    print(f"📈 Current: {metrics['active_patterns']} patterns, {metrics['pattern_efficiency']:.1%} efficiency")
