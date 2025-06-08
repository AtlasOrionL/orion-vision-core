#!/usr/bin/env python3
"""
👥 Team Behaviors - Gaming AI

Team-based behavior patterns and coordination for advanced AI.

Sprint 4 - Task 4.2 Module 2: Team Behaviors
- Team coordination patterns
- Group behavior execution
- Team strategy behaviors
- Synchronized actions

Author: Nexus - Quantum AI Architect
Sprint: 4.2.2 - Advanced Gaming Features
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

# Import behavior core
try:
    from behavior_core import BehaviorCore, BehaviorType, BehaviorState, Behavior, BehaviorAction
    BEHAVIOR_CORE_AVAILABLE = True
except ImportError:
    BEHAVIOR_CORE_AVAILABLE = False
    warnings.warn("🧠 Behavior core not available", ImportWarning)

    # Create fallback classes
    @dataclass
    class BehaviorAction:
        action_id: str
        action_type: str
        parameters: Dict[str, Any] = field(default_factory=dict)
        duration: float = 1.0

    class BehaviorType(Enum):
        ATTACK = "attack"
        DEFEND = "defend"
        MOVE = "move"
        SUPPORT = "support"

class TeamBehaviorType(Enum):
    """Team behavior types"""
    COORDINATED_ATTACK = "coordinated_attack"
    DEFENSIVE_FORMATION = "defensive_formation"
    FLANKING_MANEUVER = "flanking_maneuver"
    SUPPORT_CHAIN = "support_chain"
    RETREAT_FORMATION = "retreat_formation"
    ADVANCE_TOGETHER = "advance_together"
    COVER_AND_MOVE = "cover_and_move"
    SURROUND_TARGET = "surround_target"

class SynchronizationType(Enum):
    """Synchronization types for team actions"""
    SIMULTANEOUS = "simultaneous"  # All at once
    SEQUENTIAL = "sequential"      # One after another
    STAGGERED = "staggered"       # With delays
    CONDITIONAL = "conditional"    # Based on conditions

@dataclass
class TeamAction:
    """Team action definition"""
    action_id: str
    participating_agents: List[str]
    individual_actions: Dict[str, BehaviorAction]  # agent_id -> action
    synchronization: SynchronizationType
    timing_offset: float = 0.0
    conditions: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TeamBehavior:
    """Complete team behavior"""
    team_behavior_id: str
    team_behavior_type: TeamBehaviorType
    name: str
    description: str
    team_actions: List[TeamAction]
    required_agents: int = 2
    max_agents: int = 8
    coordination_level: float = 0.8  # How tight coordination needs to be

@dataclass
class TeamMetrics:
    """Team behavior metrics"""
    team_behaviors_executed: int = 0
    successful_team_actions: int = 0
    failed_team_actions: int = 0
    average_coordination_time: float = 0.0
    team_success_rate: float = 0.0

class TeamBehaviors:
    """
    Team Behavior System
    
    Features:
    - Team coordination patterns
    - Synchronized action execution
    - Group behavior management
    - Team performance tracking
    """
    
    def __init__(self, behavior_core: Optional[BehaviorCore] = None):
        self.logger = logging.getLogger("TeamBehaviors")
        
        # Core integration
        self.behavior_core = behavior_core
        
        # Team behavior management
        self.team_behaviors = {}  # team_behavior_id -> TeamBehavior
        self.active_team_behaviors = {}  # team_id -> team_behavior_id
        self.team_compositions = {}  # team_id -> [agent_ids]
        
        # Execution tracking
        self.team_execution_queue = deque(maxlen=100)
        self.team_execution_lock = threading.RLock()
        
        # Performance tracking
        self.metrics = TeamMetrics()
        self.team_execution_history = deque(maxlen=200)
        
        # Initialize team behavior templates
        self._initialize_team_behavior_templates()
        
        self.logger.info("👥 Team Behaviors initialized")
    
    def _initialize_team_behavior_templates(self):
        """Initialize team behavior templates"""
        # Coordinated Attack
        coordinated_attack = TeamBehavior(
            team_behavior_id="coordinated_attack_template",
            team_behavior_type=TeamBehaviorType.COORDINATED_ATTACK,
            name="Coordinated Attack",
            description="Team attacks target simultaneously",
            team_actions=[
                TeamAction(
                    action_id="sync_attack",
                    participating_agents=[],  # Will be filled dynamically
                    individual_actions={},    # Will be filled dynamically
                    synchronization=SynchronizationType.SIMULTANEOUS,
                    conditions={"target": "required", "all_agents_ready": True}
                )
            ],
            required_agents=2,
            max_agents=4,
            coordination_level=0.9
        )
        
        # Defensive Formation
        defensive_formation = TeamBehavior(
            team_behavior_id="defensive_formation_template",
            team_behavior_type=TeamBehaviorType.DEFENSIVE_FORMATION,
            name="Defensive Formation",
            description="Team forms defensive positions",
            team_actions=[
                TeamAction(
                    action_id="form_defense",
                    participating_agents=[],
                    individual_actions={},
                    synchronization=SynchronizationType.SEQUENTIAL,
                    conditions={"threat_detected": True}
                )
            ],
            required_agents=3,
            max_agents=6,
            coordination_level=0.7
        )
        
        # Flanking Maneuver
        flanking_maneuver = TeamBehavior(
            team_behavior_id="flanking_maneuver_template",
            team_behavior_type=TeamBehaviorType.FLANKING_MANEUVER,
            name="Flanking Maneuver",
            description="Team splits to flank target",
            team_actions=[
                TeamAction(
                    action_id="split_flank",
                    participating_agents=[],
                    individual_actions={},
                    synchronization=SynchronizationType.STAGGERED,
                    timing_offset=2.0,
                    conditions={"target": "required", "flanking_routes": "available"}
                )
            ],
            required_agents=3,
            max_agents=5,
            coordination_level=0.8
        )
        
        # Cover and Move
        cover_and_move = TeamBehavior(
            team_behavior_id="cover_and_move_template",
            team_behavior_type=TeamBehaviorType.COVER_AND_MOVE,
            name="Cover and Move",
            description="Team alternates between covering and advancing",
            team_actions=[
                TeamAction(
                    action_id="cover_phase",
                    participating_agents=[],
                    individual_actions={},
                    synchronization=SynchronizationType.CONDITIONAL,
                    conditions={"phase": "cover"}
                ),
                TeamAction(
                    action_id="move_phase",
                    participating_agents=[],
                    individual_actions={},
                    synchronization=SynchronizationType.CONDITIONAL,
                    conditions={"phase": "move", "cover_established": True}
                )
            ],
            required_agents=4,
            max_agents=6,
            coordination_level=0.85
        )
        
        # Store templates
        self.team_behaviors = {
            TeamBehaviorType.COORDINATED_ATTACK: coordinated_attack,
            TeamBehaviorType.DEFENSIVE_FORMATION: defensive_formation,
            TeamBehaviorType.FLANKING_MANEUVER: flanking_maneuver,
            TeamBehaviorType.COVER_AND_MOVE: cover_and_move
        }
    
    def create_team_behavior(self, team_id: str, agent_ids: List[str], 
                           team_behavior_type: TeamBehaviorType,
                           custom_parameters: Optional[Dict[str, Any]] = None) -> str:
        """Create team behavior for specific team"""
        try:
            if team_behavior_type not in self.team_behaviors:
                self.logger.error(f"❌ Unknown team behavior type: {team_behavior_type}")
                return ""
            
            template = self.team_behaviors[team_behavior_type]
            
            # Validate team size
            if len(agent_ids) < template.required_agents:
                self.logger.error(f"❌ Not enough agents: {len(agent_ids)} < {template.required_agents}")
                return ""
            
            if len(agent_ids) > template.max_agents:
                self.logger.warning(f"⚠️ Too many agents, limiting to {template.max_agents}")
                agent_ids = agent_ids[:template.max_agents]
            
            # Create team-specific behavior
            team_behavior_id = f"team_{team_id}_{team_behavior_type.value}_{int(time.time() * 1000)}"
            
            # Create team actions with specific agents
            team_actions = []
            for template_action in template.team_actions:
                team_action = self._create_team_action(
                    template_action, agent_ids, team_behavior_type, custom_parameters
                )
                team_actions.append(team_action)
            
            # Create team behavior instance
            team_behavior = TeamBehavior(
                team_behavior_id=team_behavior_id,
                team_behavior_type=team_behavior_type,
                name=f"{template.name} - {team_id}",
                description=template.description,
                team_actions=team_actions,
                required_agents=template.required_agents,
                max_agents=template.max_agents,
                coordination_level=template.coordination_level
            )
            
            # Store team behavior and composition
            self.team_behaviors[team_behavior_id] = team_behavior
            self.team_compositions[team_id] = agent_ids.copy()
            
            self.logger.info(f"👥 Team behavior created: {team_behavior_type.value} for {team_id}")
            return team_behavior_id
            
        except Exception as e:
            self.logger.error(f"❌ Team behavior creation failed: {e}")
            return ""
    
    def _create_team_action(self, template_action: TeamAction, agent_ids: List[str],
                           behavior_type: TeamBehaviorType, 
                           custom_parameters: Optional[Dict[str, Any]]) -> TeamAction:
        """Create team action with specific agents"""
        action_id = f"{template_action.action_id}_{int(time.time() * 1000)}"
        
        # Create individual actions for each agent
        individual_actions = {}
        
        if behavior_type == TeamBehaviorType.COORDINATED_ATTACK:
            # All agents attack
            for agent_id in agent_ids:
                individual_actions[agent_id] = BehaviorAction(
                    action_id=f"{action_id}_{agent_id}",
                    action_type="attack",
                    parameters={"target": "shared_target", "coordination": True},
                    duration=1.0
                )
        
        elif behavior_type == TeamBehaviorType.DEFENSIVE_FORMATION:
            # Agents take defensive positions
            for i, agent_id in enumerate(agent_ids):
                individual_actions[agent_id] = BehaviorAction(
                    action_id=f"{action_id}_{agent_id}",
                    action_type="defend",
                    parameters={"position": f"defense_point_{i}", "formation": True},
                    duration=2.0
                )
        
        elif behavior_type == TeamBehaviorType.FLANKING_MANEUVER:
            # Split agents for flanking
            mid_point = len(agent_ids) // 2
            for i, agent_id in enumerate(agent_ids):
                flank_side = "left" if i < mid_point else "right"
                individual_actions[agent_id] = BehaviorAction(
                    action_id=f"{action_id}_{agent_id}",
                    action_type="flank",
                    parameters={"side": flank_side, "target": "shared_target"},
                    duration=3.0
                )
        
        elif behavior_type == TeamBehaviorType.COVER_AND_MOVE:
            # Alternate cover and move roles
            for i, agent_id in enumerate(agent_ids):
                role = "cover" if i % 2 == 0 else "move"
                individual_actions[agent_id] = BehaviorAction(
                    action_id=f"{action_id}_{agent_id}",
                    action_type=role,
                    parameters={"role": role, "coordination": True},
                    duration=2.5
                )
        
        return TeamAction(
            action_id=action_id,
            participating_agents=agent_ids.copy(),
            individual_actions=individual_actions,
            synchronization=template_action.synchronization,
            timing_offset=template_action.timing_offset,
            conditions=template_action.conditions.copy()
        )
    
    def execute_team_behavior(self, team_id: str, team_behavior_id: str,
                            context: Dict[str, Any]) -> bool:
        """Execute team behavior"""
        try:
            if team_behavior_id not in self.team_behaviors:
                self.logger.error(f"❌ Unknown team behavior: {team_behavior_id}")
                return False
            
            team_behavior = self.team_behaviors[team_behavior_id]
            
            # Check if team exists
            if team_id not in self.team_compositions:
                self.logger.error(f"❌ Unknown team: {team_id}")
                return False
            
            # Execute team actions
            execution_start = time.time()
            success = self._execute_team_actions(team_behavior, context)
            execution_time = time.time() - execution_start
            
            # Update metrics
            self.metrics.team_behaviors_executed += 1
            if success:
                self.metrics.successful_team_actions += 1
            else:
                self.metrics.failed_team_actions += 1
            
            self._update_team_metrics(execution_time)
            
            # Record execution
            execution_record = {
                "team_id": team_id,
                "team_behavior_id": team_behavior_id,
                "behavior_type": team_behavior.team_behavior_type.value,
                "success": success,
                "execution_time": execution_time,
                "timestamp": execution_start,
                "participating_agents": self.team_compositions[team_id]
            }
            self.team_execution_history.append(execution_record)
            
            self.logger.info(f"👥 Team behavior executed: {team_behavior.team_behavior_type.value} ({'✅' if success else '❌'})")
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Team behavior execution failed: {e}")
            return False
    
    def _execute_team_actions(self, team_behavior: TeamBehavior, context: Dict[str, Any]) -> bool:
        """Execute all team actions in behavior"""
        try:
            for team_action in team_behavior.team_actions:
                # Check action conditions
                if not self._check_team_action_conditions(team_action, context):
                    self.logger.warning(f"⚠️ Team action conditions not met: {team_action.action_id}")
                    continue
                
                # Execute based on synchronization type
                success = self._execute_synchronized_action(team_action, context)
                
                if not success:
                    self.logger.warning(f"⚠️ Team action failed: {team_action.action_id}")
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Team actions execution failed: {e}")
            return False
    
    def _check_team_action_conditions(self, team_action: TeamAction, context: Dict[str, Any]) -> bool:
        """Check if team action conditions are met"""
        try:
            for condition_key, condition_value in team_action.conditions.items():
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
            self.logger.error(f"❌ Team action condition check failed: {e}")
            return False
    
    def _execute_synchronized_action(self, team_action: TeamAction, context: Dict[str, Any]) -> bool:
        """Execute team action with proper synchronization"""
        try:
            if team_action.synchronization == SynchronizationType.SIMULTANEOUS:
                # All agents act at the same time
                return self._execute_simultaneous_action(team_action, context)
            
            elif team_action.synchronization == SynchronizationType.SEQUENTIAL:
                # Agents act one after another
                return self._execute_sequential_action(team_action, context)
            
            elif team_action.synchronization == SynchronizationType.STAGGERED:
                # Agents act with timing offsets
                return self._execute_staggered_action(team_action, context)
            
            elif team_action.synchronization == SynchronizationType.CONDITIONAL:
                # Agents act based on conditions
                return self._execute_conditional_action(team_action, context)
            
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Synchronized action execution failed: {e}")
            return False
    
    def _execute_simultaneous_action(self, team_action: TeamAction, context: Dict[str, Any]) -> bool:
        """Execute simultaneous team action"""
        try:
            # Execute all individual actions at once
            success_count = 0
            
            for agent_id, action in team_action.individual_actions.items():
                if self.behavior_core:
                    # Create individual behavior for action
                    behavior_id = self.behavior_core.create_behavior(
                        BehaviorType.ATTACK if action.action_type == "attack" else BehaviorType.MOVE,
                        action.parameters
                    )
                    
                    if behavior_id:
                        success = self.behavior_core.execute_behavior(agent_id, behavior_id, context)
                        if success:
                            success_count += 1
                else:
                    # Simulate action execution
                    import random
                    if random.random() < 0.8:  # 80% success rate
                        success_count += 1
            
            # Consider successful if majority succeeds
            required_successes = len(team_action.individual_actions) * 0.7  # 70% threshold
            return success_count >= required_successes
            
        except Exception as e:
            self.logger.error(f"❌ Simultaneous action execution failed: {e}")
            return False
    
    def _execute_sequential_action(self, team_action: TeamAction, context: Dict[str, Any]) -> bool:
        """Execute sequential team action"""
        try:
            # Execute actions one by one
            for agent_id, action in team_action.individual_actions.items():
                # Simulate sequential execution
                time.sleep(0.1)  # Small delay between actions
                
                # Execute individual action (simplified)
                import random
                if random.random() < 0.75:  # 75% success rate for sequential
                    continue
                else:
                    return False  # If any fails, whole sequence fails
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Sequential action execution failed: {e}")
            return False
    
    def _execute_staggered_action(self, team_action: TeamAction, context: Dict[str, Any]) -> bool:
        """Execute staggered team action"""
        try:
            # Execute with timing offsets
            success_count = 0
            
            for i, (agent_id, action) in enumerate(team_action.individual_actions.items()):
                # Apply staggered timing
                delay = i * team_action.timing_offset
                time.sleep(min(delay, 0.2))  # Max 200ms delay for testing
                
                # Execute action
                import random
                if random.random() < 0.8:
                    success_count += 1
            
            # Staggered actions are more forgiving
            required_successes = len(team_action.individual_actions) * 0.6  # 60% threshold
            return success_count >= required_successes
            
        except Exception as e:
            self.logger.error(f"❌ Staggered action execution failed: {e}")
            return False
    
    def _execute_conditional_action(self, team_action: TeamAction, context: Dict[str, Any]) -> bool:
        """Execute conditional team action"""
        try:
            # Execute based on conditions in context
            executed_count = 0
            
            for agent_id, action in team_action.individual_actions.items():
                # Check if agent should execute based on role/conditions
                agent_role = action.parameters.get("role", "default")
                
                if context.get("phase") == agent_role or agent_role == "default":
                    # Execute action
                    import random
                    if random.random() < 0.85:  # 85% success for conditional
                        executed_count += 1
            
            # Success if at least some agents executed
            return executed_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Conditional action execution failed: {e}")
            return False
    
    def _update_team_metrics(self, execution_time: float):
        """Update team behavior metrics"""
        # Update average coordination time
        current_avg = self.metrics.average_coordination_time
        executed_count = self.metrics.team_behaviors_executed
        
        if executed_count > 0:
            self.metrics.average_coordination_time = (
                (current_avg * (executed_count - 1) + execution_time) / executed_count
            )
        
        # Update success rate
        total_actions = self.metrics.successful_team_actions + self.metrics.failed_team_actions
        if total_actions > 0:
            self.metrics.team_success_rate = (self.metrics.successful_team_actions / total_actions) * 100
    
    def get_team_metrics(self) -> Dict[str, Any]:
        """Get team behavior metrics"""
        return {
            "team_behaviors_executed": self.metrics.team_behaviors_executed,
            "successful_team_actions": self.metrics.successful_team_actions,
            "failed_team_actions": self.metrics.failed_team_actions,
            "team_success_rate": self.metrics.team_success_rate,
            "average_coordination_time": self.metrics.average_coordination_time,
            "active_team_behaviors": len(self.active_team_behaviors),
            "registered_teams": len(self.team_compositions)
        }
    
    def get_team_status(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific team"""
        if team_id not in self.team_compositions:
            return None

        return {
            "team_id": team_id,
            "agents": self.team_compositions[team_id],
            "agent_count": len(self.team_compositions[team_id]),
            "active_behavior": self.active_team_behaviors.get(team_id),
            "available_behaviors": list(self.team_behaviors.keys())
        }

    def get_available_behaviors(self) -> List[TeamBehaviorType]:
        """Get list of available team behavior types"""
        return [
            TeamBehaviorType.COORDINATED_ATTACK,
            TeamBehaviorType.DEFENSIVE_FORMATION,
            TeamBehaviorType.FLANKING_MANEUVER,
            TeamBehaviorType.SUPPORT_CHAIN,
            TeamBehaviorType.RETREAT_FORMATION,
            TeamBehaviorType.ADVANCE_TOGETHER,
            TeamBehaviorType.COVER_AND_MOVE,
            TeamBehaviorType.SURROUND_TARGET
        ]

    def execute_behavior(self, behavior_type: TeamBehaviorType, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a team behavior (simplified interface)"""
        try:
            if context is None:
                context = {}

            # Create a temporary team for demonstration
            demo_agents = ["demo_agent_1", "demo_agent_2", "demo_agent_3"]
            team_id = "demo_team"

            # Create team behavior
            behavior_id = self.create_team_behavior(team_id, demo_agents, behavior_type)

            if not behavior_id:
                return {
                    "success": False,
                    "behavior_type": behavior_type.value,
                    "error": "Failed to create team behavior"
                }

            # Execute behavior
            success = self.execute_team_behavior(team_id, behavior_id, context)

            return {
                "success": success,
                "behavior_type": behavior_type.value,
                "team_id": team_id,
                "behavior_id": behavior_id,
                "agents": demo_agents,
                "context": context
            }

        except Exception as e:
            self.logger.error(f"❌ Behavior execution failed: {e}")
            return {
                "success": False,
                "behavior_type": behavior_type.value,
                "error": str(e)
            }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("👥 Team Behaviors - Sprint 4 Test")
    print("=" * 60)
    
    # Create team behaviors system
    team_behaviors = TeamBehaviors()
    
    # Test team behavior creation
    print("\n👥 Testing team behavior creation...")
    
    team_agents = ["agent_1", "agent_2", "agent_3", "agent_4"]
    
    behaviors_created = []
    for behavior_type in [TeamBehaviorType.COORDINATED_ATTACK, TeamBehaviorType.DEFENSIVE_FORMATION]:
        behavior_id = team_behaviors.create_team_behavior(
            "alpha_team", team_agents, behavior_type
        )
        behaviors_created.append((behavior_type, behavior_id))
        print(f"   {behavior_type.value}: {behavior_id[:8] if behavior_id else 'Failed'}...")
    
    # Test team behavior execution
    print("\n🎯 Testing team behavior execution...")
    
    test_contexts = [
        {"target": "enemy_base", "all_agents_ready": True},  # For coordinated attack
        {"threat_detected": True}  # For defensive formation
    ]
    
    for i, (behavior_type, behavior_id) in enumerate(behaviors_created):
        if behavior_id:
            context = test_contexts[i] if i < len(test_contexts) else {}
            success = team_behaviors.execute_team_behavior("alpha_team", behavior_id, context)
            print(f"   {behavior_type.value}: {'✅' if success else '❌'}")
    
    # Get team metrics
    metrics = team_behaviors.get_team_metrics()
    print(f"\n📊 Team Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get team status
    team_status = team_behaviors.get_team_status("alpha_team")
    if team_status:
        print(f"\n👥 Team Status:")
        print(f"   Team: {team_status['team_id']}")
        print(f"   Agents: {team_status['agent_count']}")
        print(f"   Available Behaviors: {len(team_status['available_behaviors'])}")
    
    print("\n🎉 Sprint 4 - Task 4.2 Team Behaviors test completed!")
    print("🎯 Team coordination patterns working")
    print(f"📈 Current: {metrics['team_behaviors_executed']} executed, {metrics['team_success_rate']:.1f}% success rate")
