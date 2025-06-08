#!/usr/bin/env python3
"""
⚖️ Conflict Resolution System - Gaming AI

Decision arbitration and conflict resolution for multi-agent coordination.

Sprint 4 - Task 4.1 Module 3: Conflict Resolution
- Decision arbitration mechanisms
- Priority-based resolution
- Consensus algorithms
- <50ms conflict resolution time

Author: Nexus - Quantum AI Architect
Sprint: 4.1.3 - Advanced Gaming Features
"""

import time
import threading
import logging
import json
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

# Import previous modules
try:
    from agent_communication import AgentCommunication, MessageType, MessagePriority, Message
    from strategy_coordination import StrategyCoordination, StrategyType, CoordinationMode
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False
    warnings.warn("🔗 Previous modules not available", ImportWarning)

class ConflictType(Enum):
    """Conflict type enumeration"""
    RESOURCE_CONFLICT = "resource_conflict"
    POSITION_CONFLICT = "position_conflict"
    STRATEGY_CONFLICT = "strategy_conflict"
    PRIORITY_CONFLICT = "priority_conflict"
    TIMING_CONFLICT = "timing_conflict"
    ROLE_CONFLICT = "role_conflict"

class ResolutionMethod(Enum):
    """Conflict resolution method"""
    PRIORITY_BASED = "priority_based"
    CONSENSUS = "consensus"
    ARBITRATION = "arbitration"
    VOTING = "voting"
    PERFORMANCE_BASED = "performance_based"
    RANDOM = "random"

class ConflictSeverity(Enum):
    """Conflict severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    EMERGENCY = 5

@dataclass
class Conflict:
    """Conflict definition"""
    conflict_id: str
    conflict_type: ConflictType
    severity: ConflictSeverity
    involved_agents: List[str]
    conflicting_decisions: List[Dict[str, Any]]
    context: Dict[str, Any]
    created_at: float
    deadline: Optional[float] = None
    resolved: bool = False
    resolution: Optional[Dict[str, Any]] = None

@dataclass
class ResolutionRule:
    """Conflict resolution rule"""
    rule_id: str
    conflict_types: List[ConflictType]
    conditions: Dict[str, Any]
    resolution_method: ResolutionMethod
    priority: int
    timeout_ms: float = 50.0

@dataclass
class ConflictMetrics:
    """Conflict resolution metrics"""
    conflicts_detected: int = 0
    conflicts_resolved: int = 0
    average_resolution_time: float = 0.0
    resolution_success_rate: float = 100.0
    consensus_achieved: int = 0

class ConflictResolution:
    """
    Conflict Resolution System for Multi-Agent Coordination
    
    Features:
    - Real-time conflict detection (<50ms resolution)
    - Multiple resolution strategies
    - Priority-based arbitration
    - Consensus mechanisms
    - Performance-based decisions
    """
    
    def __init__(self, communication_system: Optional[AgentCommunication] = None,
                 strategy_coordinator: Optional[StrategyCoordination] = None):
        self.logger = logging.getLogger("ConflictResolution")
        
        # System integration
        self.comm_system = communication_system
        self.strategy_coordinator = strategy_coordinator
        
        # Conflict management
        self.active_conflicts = {}  # conflict_id -> Conflict
        self.conflict_history = deque(maxlen=500)
        self.resolution_rules = []
        
        # Agent priorities and performance
        self.agent_priorities = {}  # agent_id -> priority_score
        self.agent_performance = {}  # agent_id -> performance_metrics
        
        # Threading
        self.resolution_lock = threading.RLock()
        self.resolution_active = False
        self.resolution_thread = None
        
        # Performance tracking
        self.metrics = ConflictMetrics()
        
        # Resolution strategies
        self.resolution_strategies = {
            ResolutionMethod.PRIORITY_BASED: self._resolve_by_priority,
            ResolutionMethod.CONSENSUS: self._resolve_by_consensus,
            ResolutionMethod.ARBITRATION: self._resolve_by_arbitration,
            ResolutionMethod.VOTING: self._resolve_by_voting,
            ResolutionMethod.PERFORMANCE_BASED: self._resolve_by_performance,
            ResolutionMethod.RANDOM: self._resolve_randomly
        }
        
        # Initialize resolution rules
        self._initialize_resolution_rules()
        
        self.logger.info("⚖️ Conflict Resolution System initialized")
    
    def _initialize_resolution_rules(self):
        """Initialize default resolution rules"""
        self.resolution_rules = [
            # Emergency conflicts - immediate arbitration
            ResolutionRule(
                "emergency_arbitration",
                [ConflictType.TIMING_CONFLICT, ConflictType.POSITION_CONFLICT],
                {"severity": ConflictSeverity.EMERGENCY},
                ResolutionMethod.ARBITRATION,
                priority=1,
                timeout_ms=10.0
            ),
            
            # Critical conflicts - priority-based
            ResolutionRule(
                "critical_priority",
                [ConflictType.RESOURCE_CONFLICT, ConflictType.STRATEGY_CONFLICT],
                {"severity": ConflictSeverity.CRITICAL},
                ResolutionMethod.PRIORITY_BASED,
                priority=2,
                timeout_ms=25.0
            ),
            
            # High severity - performance-based
            ResolutionRule(
                "high_performance",
                [ConflictType.ROLE_CONFLICT, ConflictType.STRATEGY_CONFLICT],
                {"severity": ConflictSeverity.HIGH},
                ResolutionMethod.PERFORMANCE_BASED,
                priority=3,
                timeout_ms=40.0
            ),
            
            # Medium severity - consensus
            ResolutionRule(
                "medium_consensus",
                [ConflictType.STRATEGY_CONFLICT, ConflictType.PRIORITY_CONFLICT],
                {"severity": ConflictSeverity.MEDIUM},
                ResolutionMethod.CONSENSUS,
                priority=4,
                timeout_ms=50.0
            ),
            
            # Low severity - voting
            ResolutionRule(
                "low_voting",
                [ConflictType.RESOURCE_CONFLICT, ConflictType.ROLE_CONFLICT],
                {"severity": ConflictSeverity.LOW},
                ResolutionMethod.VOTING,
                priority=5,
                timeout_ms=50.0
            )
        ]
    
    def detect_conflict(self, agents: List[str], decisions: List[Dict[str, Any]], 
                       context: Dict[str, Any]) -> Optional[str]:
        """Detect conflicts between agent decisions"""
        try:
            # Analyze decisions for conflicts
            conflict_type, severity = self._analyze_decisions(decisions, context)
            
            if conflict_type is None:
                return None  # No conflict detected
            
            # Create conflict record
            conflict_id = f"conflict_{int(time.time() * 1000000)}"
            
            conflict = Conflict(
                conflict_id=conflict_id,
                conflict_type=conflict_type,
                severity=severity,
                involved_agents=agents.copy(),
                conflicting_decisions=decisions.copy(),
                context=context.copy(),
                created_at=time.time(),
                deadline=time.time() + 0.1  # 100ms deadline
            )
            
            with self.resolution_lock:
                self.active_conflicts[conflict_id] = conflict
                self.metrics.conflicts_detected += 1
            
            self.logger.info(f"⚠️ Conflict detected: {conflict_type.value} ({severity.name})")
            
            # Trigger immediate resolution for high severity
            if severity.value >= ConflictSeverity.HIGH.value:
                self._resolve_conflict_immediately(conflict_id)
            
            return conflict_id
            
        except Exception as e:
            self.logger.error(f"❌ Conflict detection failed: {e}")
            return None
    
    def _analyze_decisions(self, decisions: List[Dict[str, Any]], 
                          context: Dict[str, Any]) -> Tuple[Optional[ConflictType], ConflictSeverity]:
        """Analyze decisions to identify conflicts"""
        if len(decisions) < 2:
            return None, ConflictSeverity.LOW
        
        # Resource conflicts
        if self._check_resource_conflict(decisions):
            severity = ConflictSeverity.HIGH if context.get("critical_resource", False) else ConflictSeverity.MEDIUM
            return ConflictType.RESOURCE_CONFLICT, severity
        
        # Position conflicts
        if self._check_position_conflict(decisions):
            severity = ConflictSeverity.CRITICAL if context.get("combat_zone", False) else ConflictSeverity.HIGH
            return ConflictType.POSITION_CONFLICT, severity
        
        # Strategy conflicts
        if self._check_strategy_conflict(decisions):
            return ConflictType.STRATEGY_CONFLICT, ConflictSeverity.MEDIUM
        
        # Timing conflicts
        if self._check_timing_conflict(decisions, context):
            severity = ConflictSeverity.EMERGENCY if context.get("time_critical", False) else ConflictSeverity.HIGH
            return ConflictType.TIMING_CONFLICT, severity
        
        # Priority conflicts
        if self._check_priority_conflict(decisions):
            return ConflictType.PRIORITY_CONFLICT, ConflictSeverity.MEDIUM
        
        # Role conflicts
        if self._check_role_conflict(decisions):
            return ConflictType.ROLE_CONFLICT, ConflictSeverity.LOW
        
        return None, ConflictSeverity.LOW
    
    def _check_resource_conflict(self, decisions: List[Dict[str, Any]]) -> bool:
        """Check for resource conflicts"""
        requested_resources = []
        
        for decision in decisions:
            resources = decision.get("required_resources", [])
            for resource in resources:
                if resource in requested_resources:
                    return True  # Same resource requested by multiple agents
                requested_resources.append(resource)
        
        return False
    
    def _check_position_conflict(self, decisions: List[Dict[str, Any]]) -> bool:
        """Check for position conflicts"""
        target_positions = []
        
        for decision in decisions:
            position = decision.get("target_position")
            if position:
                # Check if positions are too close (conflict zone)
                for existing_pos in target_positions:
                    if self._calculate_distance(position, existing_pos) < 10.0:  # 10 unit minimum distance
                        return True
                target_positions.append(position)
        
        return False
    
    def _check_strategy_conflict(self, decisions: List[Dict[str, Any]]) -> bool:
        """Check for strategy conflicts"""
        strategies = set()
        
        for decision in decisions:
            strategy = decision.get("strategy_type")
            if strategy:
                strategies.add(strategy)
        
        # Conflicting strategies
        conflicting_pairs = [
            ("offensive", "defensive"),
            ("advance", "retreat"),
            ("aggressive", "conservative")
        ]
        
        for strategy1, strategy2 in conflicting_pairs:
            if strategy1 in strategies and strategy2 in strategies:
                return True
        
        return False
    
    def _check_timing_conflict(self, decisions: List[Dict[str, Any]], context: Dict[str, Any]) -> bool:
        """Check for timing conflicts"""
        execution_times = []
        
        for decision in decisions:
            exec_time = decision.get("execution_time", 0.0)
            if exec_time > 0:
                execution_times.append(exec_time)
        
        # Check for simultaneous actions that can't be performed together
        if len(execution_times) > 1:
            time_diff = max(execution_times) - min(execution_times)
            if time_diff < 0.1:  # Less than 100ms apart
                return True
        
        return False
    
    def _check_priority_conflict(self, decisions: List[Dict[str, Any]]) -> bool:
        """Check for priority conflicts"""
        priorities = []
        
        for decision in decisions:
            priority = decision.get("priority", 0)
            priorities.append(priority)
        
        # Check if multiple high-priority decisions conflict
        high_priority_count = len([p for p in priorities if p >= 8])
        return high_priority_count > 1
    
    def _check_role_conflict(self, decisions: List[Dict[str, Any]]) -> bool:
        """Check for role conflicts"""
        roles = []
        
        for decision in decisions:
            role = decision.get("agent_role")
            if role:
                roles.append(role)
        
        # Check for role overlap (multiple agents trying same role)
        unique_roles = set(roles)
        return len(roles) != len(unique_roles)
    
    def _calculate_distance(self, pos1: Any, pos2: Any) -> float:
        """Calculate distance between positions"""
        try:
            if isinstance(pos1, dict) and isinstance(pos2, dict):
                x1, y1 = pos1.get("x", 0), pos1.get("y", 0)
                x2, y2 = pos2.get("x", 0), pos2.get("y", 0)
                return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        except:
            pass
        return 0.0
    
    def resolve_conflict(self, conflict_id: str) -> bool:
        """Resolve specific conflict"""
        try:
            with self.resolution_lock:
                if conflict_id not in self.active_conflicts:
                    return False
                
                conflict = self.active_conflicts[conflict_id]
                
                if conflict.resolved:
                    return True
                
                # Find applicable resolution rule
                resolution_rule = self._find_resolution_rule(conflict)
                
                if not resolution_rule:
                    self.logger.warning(f"⚠️ No resolution rule found for conflict: {conflict_id}")
                    return False
                
                # Apply resolution strategy
                resolution_start = time.time()
                resolution_method = resolution_rule.resolution_method
                
                if resolution_method in self.resolution_strategies:
                    strategy_func = self.resolution_strategies[resolution_method]
                    resolution = strategy_func(conflict)
                    
                    if resolution:
                        conflict.resolution = resolution
                        conflict.resolved = True
                        
                        # Calculate resolution time
                        resolution_time = time.time() - resolution_start
                        self._update_resolution_metrics(resolution_time, True)
                        
                        # Notify agents of resolution
                        self._notify_conflict_resolution(conflict)
                        
                        # Move to history
                        self.conflict_history.append(conflict)
                        del self.active_conflicts[conflict_id]
                        
                        self.logger.info(f"✅ Conflict resolved: {conflict_id[:8]}... ({resolution_time*1000:.1f}ms)")
                        return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Conflict resolution failed: {e}")
            return False
    
    def _find_resolution_rule(self, conflict: Conflict) -> Optional[ResolutionRule]:
        """Find applicable resolution rule for conflict"""
        applicable_rules = []
        
        for rule in self.resolution_rules:
            # Check conflict type match
            if conflict.conflict_type in rule.conflict_types:
                # Check conditions
                conditions_met = True
                for condition_key, condition_value in rule.conditions.items():
                    if condition_key == "severity":
                        if conflict.severity != condition_value:
                            conditions_met = False
                            break
                    elif condition_key not in conflict.context:
                        conditions_met = False
                        break
                    elif conflict.context[condition_key] != condition_value:
                        conditions_met = False
                        break
                
                if conditions_met:
                    applicable_rules.append(rule)
        
        # Return highest priority rule
        if applicable_rules:
            return min(applicable_rules, key=lambda r: r.priority)
        
        return None
    
    def _resolve_by_priority(self, conflict: Conflict) -> Optional[Dict[str, Any]]:
        """Resolve conflict using agent priorities"""
        try:
            # Find highest priority agent
            highest_priority = -1
            winning_agent = None
            winning_decision = None
            
            for i, agent_id in enumerate(conflict.involved_agents):
                agent_priority = self.agent_priorities.get(agent_id, 5)  # Default priority 5
                
                if agent_priority > highest_priority:
                    highest_priority = agent_priority
                    winning_agent = agent_id
                    winning_decision = conflict.conflicting_decisions[i]
            
            if winning_agent:
                return {
                    "method": "priority_based",
                    "winning_agent": winning_agent,
                    "winning_decision": winning_decision,
                    "priority_score": highest_priority
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Priority resolution failed: {e}")
            return None
    
    def _resolve_by_consensus(self, conflict: Conflict) -> Optional[Dict[str, Any]]:
        """Resolve conflict using consensus"""
        try:
            # Simple consensus: find most common decision type
            decision_types = {}
            
            for decision in conflict.conflicting_decisions:
                decision_type = decision.get("action_type", "unknown")
                decision_types[decision_type] = decision_types.get(decision_type, 0) + 1
            
            if decision_types:
                consensus_decision = max(decision_types, key=decision_types.get)
                consensus_count = decision_types[consensus_decision]
                
                # Find first decision of consensus type
                winning_decision = None
                for decision in conflict.conflicting_decisions:
                    if decision.get("action_type") == consensus_decision:
                        winning_decision = decision
                        break
                
                self.metrics.consensus_achieved += 1
                
                return {
                    "method": "consensus",
                    "consensus_decision": consensus_decision,
                    "winning_decision": winning_decision,
                    "consensus_count": consensus_count
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Consensus resolution failed: {e}")
            return None
    
    def _resolve_by_arbitration(self, conflict: Conflict) -> Optional[Dict[str, Any]]:
        """Resolve conflict using arbitration (system decides)"""
        try:
            # System arbitration based on context
            context = conflict.context
            
            # Emergency situations - choose fastest action
            if conflict.severity == ConflictSeverity.EMERGENCY:
                fastest_decision = min(
                    conflict.conflicting_decisions,
                    key=lambda d: d.get("execution_time", float('inf'))
                )
                
                return {
                    "method": "arbitration",
                    "winning_decision": fastest_decision,
                    "reason": "emergency_fastest"
                }
            
            # Default: choose first decision
            return {
                "method": "arbitration",
                "winning_decision": conflict.conflicting_decisions[0],
                "reason": "default_first"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Arbitration resolution failed: {e}")
            return None
    
    def _resolve_by_voting(self, conflict: Conflict) -> Optional[Dict[str, Any]]:
        """Resolve conflict using voting (simplified)"""
        try:
            # Simplified voting: random selection for now
            # In real implementation, would collect votes from agents
            import random
            
            winning_decision = random.choice(conflict.conflicting_decisions)
            
            return {
                "method": "voting",
                "winning_decision": winning_decision,
                "votes": len(conflict.involved_agents)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Voting resolution failed: {e}")
            return None
    
    def _resolve_by_performance(self, conflict: Conflict) -> Optional[Dict[str, Any]]:
        """Resolve conflict using agent performance"""
        try:
            # Find best performing agent
            best_performance = -1
            winning_agent = None
            winning_decision = None
            
            for i, agent_id in enumerate(conflict.involved_agents):
                performance = self.agent_performance.get(agent_id, {})
                performance_score = performance.get("success_rate", 0.5)
                
                if performance_score > best_performance:
                    best_performance = performance_score
                    winning_agent = agent_id
                    winning_decision = conflict.conflicting_decisions[i]
            
            if winning_agent:
                return {
                    "method": "performance_based",
                    "winning_agent": winning_agent,
                    "winning_decision": winning_decision,
                    "performance_score": best_performance
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"❌ Performance resolution failed: {e}")
            return None
    
    def _resolve_randomly(self, conflict: Conflict) -> Optional[Dict[str, Any]]:
        """Resolve conflict randomly"""
        try:
            import random
            
            winning_decision = random.choice(conflict.conflicting_decisions)
            winning_agent = random.choice(conflict.involved_agents)
            
            return {
                "method": "random",
                "winning_agent": winning_agent,
                "winning_decision": winning_decision
            }
            
        except Exception as e:
            self.logger.error(f"❌ Random resolution failed: {e}")
            return None
    
    def _resolve_conflict_immediately(self, conflict_id: str):
        """Resolve conflict immediately (for high priority)"""
        threading.Thread(
            target=self.resolve_conflict,
            args=(conflict_id,),
            daemon=True
        ).start()
    
    def _notify_conflict_resolution(self, conflict: Conflict):
        """Notify agents of conflict resolution"""
        if not self.comm_system:
            return
        
        try:
            content = {
                "conflict_id": conflict.conflict_id,
                "conflict_type": conflict.conflict_type.value,
                "resolution": conflict.resolution,
                "resolved_at": time.time()
            }
            
            for agent_id in conflict.involved_agents:
                self.comm_system.send_message(
                    "CONFLICT_RESOLVER", agent_id,
                    MessageType.STATUS_UPDATE, content,
                    MessagePriority.HIGH
                )
                
        except Exception as e:
            self.logger.error(f"❌ Resolution notification failed: {e}")
    
    def _update_resolution_metrics(self, resolution_time: float, success: bool):
        """Update resolution metrics"""
        if success:
            self.metrics.conflicts_resolved += 1
            
            # Update average resolution time
            current_avg = self.metrics.average_resolution_time
            resolved_count = self.metrics.conflicts_resolved
            
            self.metrics.average_resolution_time = (
                (current_avg * (resolved_count - 1) + resolution_time) / resolved_count
            )
        
        # Update success rate
        total_conflicts = self.metrics.conflicts_detected
        if total_conflicts > 0:
            self.metrics.resolution_success_rate = (
                self.metrics.conflicts_resolved / total_conflicts * 100
            )
    
    def set_agent_priority(self, agent_id: str, priority: int):
        """Set agent priority for conflict resolution"""
        self.agent_priorities[agent_id] = priority
    
    def update_agent_performance(self, agent_id: str, performance_data: Dict[str, Any]):
        """Update agent performance data"""
        self.agent_performance[agent_id] = performance_data
    
    def get_resolution_metrics(self) -> Dict[str, Any]:
        """Get conflict resolution metrics"""
        with self.resolution_lock:
            return {
                "conflicts_detected": self.metrics.conflicts_detected,
                "conflicts_resolved": self.metrics.conflicts_resolved,
                "average_resolution_time": self.metrics.average_resolution_time,
                "resolution_success_rate": self.metrics.resolution_success_rate,
                "consensus_achieved": self.metrics.consensus_achieved,
                "active_conflicts": len(self.active_conflicts),
                "resolution_rules": len(self.resolution_rules)
            }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("⚖️ Conflict Resolution System - Sprint 4 Test")
    print("=" * 60)
    
    # Create conflict resolution system
    resolver = ConflictResolution()
    
    # Set agent priorities
    resolver.set_agent_priority("agent_1", 8)
    resolver.set_agent_priority("agent_2", 6)
    resolver.set_agent_priority("agent_3", 7)
    
    # Test conflict detection
    print("\n⚠️ Testing conflict detection...")
    
    # Create conflicting decisions
    agents = ["agent_1", "agent_2"]
    decisions = [
        {
            "action_type": "move",
            "target_position": {"x": 100, "y": 100},
            "required_resources": ["position_A"],
            "priority": 8
        },
        {
            "action_type": "move", 
            "target_position": {"x": 105, "y": 102},
            "required_resources": ["position_A"],
            "priority": 9
        }
    ]
    
    context = {"combat_zone": True, "time_critical": False}
    
    conflict_id = resolver.detect_conflict(agents, decisions, context)
    print(f"   Conflict detected: {conflict_id[:8] if conflict_id else 'None'}...")
    
    # Test conflict resolution
    if conflict_id:
        print("\n✅ Testing conflict resolution...")
        resolved = resolver.resolve_conflict(conflict_id)
        print(f"   Conflict resolved: {'✅' if resolved else '❌'}")
    
    # Get metrics
    metrics = resolver.get_resolution_metrics()
    print(f"\n📊 Resolution Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 4 - Task 4.1 Module 3 test completed!")
    print("🎯 Target: <50ms conflict resolution")
    print(f"📈 Current: {metrics['average_resolution_time']*1000:.1f}ms average resolution time")
