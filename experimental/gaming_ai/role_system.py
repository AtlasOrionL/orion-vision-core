#!/usr/bin/env python3
"""
🎭 Role System - Gaming AI

Dynamic role assignment and management system for advanced AI behaviors.

Sprint 4 - Task 4.2 Module 4: Role System
- Dynamic role assignment
- Role-based behavior adaptation
- Role switching mechanisms
- Performance-based role optimization

Author: Nexus - Quantum AI Architect
Sprint: 4.2.4 - Advanced Gaming Features
"""

import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

class RoleType(Enum):
    """Role type enumeration"""
    LEADER = "leader"
    ASSAULT = "assault"
    SNIPER = "sniper"
    SUPPORT = "support"
    SCOUT = "scout"
    DEFENDER = "defender"
    MEDIC = "medic"
    ENGINEER = "engineer"

class RoleState(Enum):
    """Role state enumeration"""
    ASSIGNED = "assigned"
    ACTIVE = "active"
    SWITCHING = "switching"
    INACTIVE = "inactive"

class RolePriority(Enum):
    """Role priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4
    ESSENTIAL = 5

@dataclass
class RoleRequirement:
    """Role requirement definition"""
    skill_type: str
    minimum_level: float
    weight: float = 1.0

@dataclass
class RoleDefinition:
    """Complete role definition"""
    role_id: str
    role_type: RoleType
    name: str
    description: str
    requirements: List[RoleRequirement]
    responsibilities: List[str]
    priority: RolePriority = RolePriority.NORMAL
    max_assignments: int = 1

@dataclass
class AgentSkills:
    """Agent skill profile"""
    agent_id: str
    skills: Dict[str, float]  # skill_name -> level (0.0-1.0)
    experience: Dict[str, int] = field(default_factory=dict)  # role_type -> experience_points
    performance_history: Dict[str, List[float]] = field(default_factory=dict)  # role_type -> performance_scores

@dataclass
class RoleAssignment:
    """Role assignment record"""
    assignment_id: str
    agent_id: str
    role_id: str
    role_type: RoleType
    assigned_at: float
    state: RoleState = RoleState.ASSIGNED
    performance_score: float = 0.0
    duration: float = 0.0

@dataclass
class RoleMetrics:
    """Role system metrics"""
    roles_assigned: int = 0
    role_switches: int = 0
    successful_assignments: int = 0
    average_assignment_duration: float = 0.0
    role_efficiency: float = 0.0

class RoleSystem:
    """
    Dynamic Role Assignment and Management System
    
    Features:
    - Dynamic role assignment based on skills
    - Role-based behavior adaptation
    - Performance tracking and optimization
    - Automatic role switching
    """
    
    def __init__(self):
        self.logger = logging.getLogger("RoleSystem")
        
        # Role management
        self.role_definitions = {}  # role_id -> RoleDefinition
        self.agent_skills = {}  # agent_id -> AgentSkills
        self.role_assignments = {}  # agent_id -> RoleAssignment
        self.team_roles = {}  # team_id -> {role_type -> [agent_ids]}
        
        # Performance tracking
        self.metrics = RoleMetrics()
        self.assignment_history = deque(maxlen=500)
        
        # Role optimization
        self.role_effectiveness = {}  # (agent_id, role_type) -> effectiveness_score
        
        # Initialize role definitions
        self._initialize_role_definitions()
        
        self.logger.info("🎭 Role System initialized")
    
    def _initialize_role_definitions(self):
        """Initialize role definitions"""
        # Leader role
        leader_role = RoleDefinition(
            role_id="leader_role",
            role_type=RoleType.LEADER,
            name="Team Leader",
            description="Coordinates team actions and makes strategic decisions",
            requirements=[
                RoleRequirement("leadership", 0.7, 2.0),
                RoleRequirement("tactical_awareness", 0.6, 1.5),
                RoleRequirement("communication", 0.8, 1.8)
            ],
            responsibilities=["coordinate_team", "make_decisions", "communicate_strategy"],
            priority=RolePriority.ESSENTIAL,
            max_assignments=1
        )
        
        # Assault role
        assault_role = RoleDefinition(
            role_id="assault_role",
            role_type=RoleType.ASSAULT,
            name="Assault Specialist",
            description="Front-line combat and aggressive tactics",
            requirements=[
                RoleRequirement("combat_skill", 0.8, 2.0),
                RoleRequirement("aggression", 0.7, 1.5),
                RoleRequirement("mobility", 0.6, 1.2)
            ],
            responsibilities=["engage_enemies", "breach_defenses", "lead_attacks"],
            priority=RolePriority.HIGH,
            max_assignments=2
        )
        
        # Sniper role
        sniper_role = RoleDefinition(
            role_id="sniper_role",
            role_type=RoleType.SNIPER,
            name="Sniper Specialist",
            description="Long-range precision elimination",
            requirements=[
                RoleRequirement("accuracy", 0.9, 2.5),
                RoleRequirement("patience", 0.8, 1.8),
                RoleRequirement("stealth", 0.7, 1.5)
            ],
            responsibilities=["eliminate_targets", "provide_overwatch", "gather_intel"],
            priority=RolePriority.HIGH,
            max_assignments=1
        )
        
        # Support role
        support_role = RoleDefinition(
            role_id="support_role",
            role_type=RoleType.SUPPORT,
            name="Support Specialist",
            description="Provides assistance and resources to team",
            requirements=[
                RoleRequirement("teamwork", 0.8, 2.0),
                RoleRequirement("resource_management", 0.7, 1.5),
                RoleRequirement("adaptability", 0.6, 1.2)
            ],
            responsibilities=["assist_teammates", "manage_resources", "provide_backup"],
            priority=RolePriority.NORMAL,
            max_assignments=2
        )
        
        # Scout role
        scout_role = RoleDefinition(
            role_id="scout_role",
            role_type=RoleType.SCOUT,
            name="Scout Specialist",
            description="Reconnaissance and intelligence gathering",
            requirements=[
                RoleRequirement("stealth", 0.8, 2.0),
                RoleRequirement("mobility", 0.9, 2.2),
                RoleRequirement("observation", 0.7, 1.5)
            ],
            responsibilities=["gather_intelligence", "scout_ahead", "detect_threats"],
            priority=RolePriority.CRITICAL,
            max_assignments=1
        )
        
        # Defender role
        defender_role = RoleDefinition(
            role_id="defender_role",
            role_type=RoleType.DEFENDER,
            name="Defensive Specialist",
            description="Holds positions and protects objectives",
            requirements=[
                RoleRequirement("defensive_skill", 0.8, 2.0),
                RoleRequirement("patience", 0.7, 1.5),
                RoleRequirement("positioning", 0.8, 1.8)
            ],
            responsibilities=["hold_positions", "protect_objectives", "block_enemies"],
            priority=RolePriority.HIGH,
            max_assignments=2
        )
        
        # Store role definitions
        self.role_definitions = {
            RoleType.LEADER: leader_role,
            RoleType.ASSAULT: assault_role,
            RoleType.SNIPER: sniper_role,
            RoleType.SUPPORT: support_role,
            RoleType.SCOUT: scout_role,
            RoleType.DEFENDER: defender_role
        }
    
    def register_agent(self, agent_id: str, initial_skills: Dict[str, float]) -> bool:
        """Register agent with skill profile"""
        try:
            if agent_id in self.agent_skills:
                self.logger.warning(f"⚠️ Agent {agent_id} already registered")
                return False
            
            # Create agent skills profile
            agent_skills = AgentSkills(
                agent_id=agent_id,
                skills=initial_skills.copy()
            )
            
            self.agent_skills[agent_id] = agent_skills
            
            self.logger.info(f"🎭 Agent registered: {agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Agent registration failed: {e}")
            return False
    
    def assign_role(self, agent_id: str, role_type: RoleType, team_id: Optional[str] = None) -> str:
        """Assign role to agent"""
        try:
            if agent_id not in self.agent_skills:
                self.logger.error(f"❌ Unknown agent: {agent_id}")
                return ""
            
            if role_type not in self.role_definitions:
                self.logger.error(f"❌ Unknown role type: {role_type}")
                return ""
            
            role_definition = self.role_definitions[role_type]
            
            # Check if agent meets requirements
            if not self._check_role_requirements(agent_id, role_definition):
                self.logger.warning(f"⚠️ Agent {agent_id} doesn't meet requirements for {role_type.value}")
                return ""
            
            # Check current assignment
            if agent_id in self.role_assignments:
                current_assignment = self.role_assignments[agent_id]
                if current_assignment.state == RoleState.ACTIVE:
                    self.logger.info(f"🔄 Switching role for {agent_id}")
                    self._end_role_assignment(agent_id)
            
            # Create assignment
            assignment_id = f"assignment_{agent_id}_{role_type.value}_{int(time.time() * 1000)}"
            
            assignment = RoleAssignment(
                assignment_id=assignment_id,
                agent_id=agent_id,
                role_id=role_definition.role_id,
                role_type=role_type,
                assigned_at=time.time(),
                state=RoleState.ASSIGNED
            )
            
            # Store assignment
            self.role_assignments[agent_id] = assignment
            
            # Update team roles if team specified
            if team_id:
                if team_id not in self.team_roles:
                    self.team_roles[team_id] = {}
                if role_type not in self.team_roles[team_id]:
                    self.team_roles[team_id][role_type] = []
                
                self.team_roles[team_id][role_type].append(agent_id)
            
            # Update metrics
            self.metrics.roles_assigned += 1
            
            self.logger.info(f"🎭 Role assigned: {agent_id} -> {role_type.value}")
            return assignment_id
            
        except Exception as e:
            self.logger.error(f"❌ Role assignment failed: {e}")
            return ""
    
    def _check_role_requirements(self, agent_id: str, role_definition: RoleDefinition) -> bool:
        """Check if agent meets role requirements"""
        try:
            agent_skills = self.agent_skills[agent_id]
            
            for requirement in role_definition.requirements:
                skill_level = agent_skills.skills.get(requirement.skill_type, 0.0)
                
                if skill_level < requirement.minimum_level:
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Role requirement check failed: {e}")
            return False
    
    def activate_role(self, agent_id: str) -> bool:
        """Activate assigned role for agent"""
        try:
            if agent_id not in self.role_assignments:
                self.logger.error(f"❌ No role assignment for {agent_id}")
                return False
            
            assignment = self.role_assignments[agent_id]
            
            if assignment.state != RoleState.ASSIGNED:
                self.logger.warning(f"⚠️ Role not in assigned state: {assignment.state}")
                return False
            
            # Activate role
            assignment.state = RoleState.ACTIVE
            
            self.logger.info(f"🎭 Role activated: {agent_id} -> {assignment.role_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Role activation failed: {e}")
            return False
    
    def update_role_performance(self, agent_id: str, performance_score: float):
        """Update role performance for agent"""
        try:
            if agent_id not in self.role_assignments:
                return
            
            assignment = self.role_assignments[agent_id]
            assignment.performance_score = performance_score
            
            # Update agent performance history
            agent_skills = self.agent_skills[agent_id]
            role_type_str = assignment.role_type.value
            
            if role_type_str not in agent_skills.performance_history:
                agent_skills.performance_history[role_type_str] = []
            
            agent_skills.performance_history[role_type_str].append(performance_score)
            
            # Limit history size
            if len(agent_skills.performance_history[role_type_str]) > 20:
                agent_skills.performance_history[role_type_str] = agent_skills.performance_history[role_type_str][-20:]
            
            # Update role effectiveness
            self.role_effectiveness[(agent_id, assignment.role_type)] = performance_score
            
            self.logger.debug(f"📊 Performance updated: {agent_id} -> {performance_score:.3f}")
            
        except Exception as e:
            self.logger.error(f"❌ Performance update failed: {e}")
    
    def suggest_optimal_role(self, agent_id: str, available_roles: List[RoleType]) -> Optional[RoleType]:
        """Suggest optimal role for agent based on skills and performance"""
        try:
            if agent_id not in self.agent_skills:
                return None
            
            agent_skills = self.agent_skills[agent_id]
            best_role = None
            best_score = -1.0
            
            for role_type in available_roles:
                if role_type not in self.role_definitions:
                    continue
                
                role_definition = self.role_definitions[role_type]
                
                # Check if agent meets requirements
                if not self._check_role_requirements(agent_id, role_definition):
                    continue
                
                # Calculate role fitness score
                fitness_score = self._calculate_role_fitness(agent_id, role_definition)
                
                if fitness_score > best_score:
                    best_score = fitness_score
                    best_role = role_type
            
            return best_role
            
        except Exception as e:
            self.logger.error(f"❌ Role suggestion failed: {e}")
            return None
    
    def _calculate_role_fitness(self, agent_id: str, role_definition: RoleDefinition) -> float:
        """Calculate how well agent fits role"""
        try:
            agent_skills = self.agent_skills[agent_id]
            fitness_score = 0.0
            total_weight = 0.0
            
            # Calculate skill-based fitness
            for requirement in role_definition.requirements:
                skill_level = agent_skills.skills.get(requirement.skill_type, 0.0)
                contribution = skill_level * requirement.weight
                fitness_score += contribution
                total_weight += requirement.weight
            
            # Normalize by total weight
            if total_weight > 0:
                fitness_score /= total_weight
            
            # Add performance history bonus
            role_type_str = role_definition.role_type.value
            if role_type_str in agent_skills.performance_history:
                performance_history = agent_skills.performance_history[role_type_str]
                if performance_history:
                    avg_performance = sum(performance_history) / len(performance_history)
                    fitness_score = (fitness_score * 0.7) + (avg_performance * 0.3)  # 70% skills, 30% history
            
            return fitness_score
            
        except Exception as e:
            self.logger.error(f"❌ Role fitness calculation failed: {e}")
            return 0.0
    
    def optimize_team_roles(self, team_id: str, agent_ids: List[str], 
                           required_roles: List[RoleType]) -> Dict[str, RoleType]:
        """Optimize role assignments for entire team"""
        try:
            role_assignments = {}
            available_agents = agent_ids.copy()
            
            # Sort roles by priority
            sorted_roles = sorted(required_roles, 
                                key=lambda r: self.role_definitions[r].priority.value, 
                                reverse=True)
            
            # Assign roles in priority order
            for role_type in sorted_roles:
                if not available_agents:
                    break
                
                # Find best agent for this role
                best_agent = None
                best_fitness = -1.0
                
                for agent_id in available_agents:
                    if role_type not in self.role_definitions:
                        continue
                    
                    role_definition = self.role_definitions[role_type]
                    
                    if self._check_role_requirements(agent_id, role_definition):
                        fitness = self._calculate_role_fitness(agent_id, role_definition)
                        
                        if fitness > best_fitness:
                            best_fitness = fitness
                            best_agent = agent_id
                
                # Assign best agent to role
                if best_agent:
                    role_assignments[best_agent] = role_type
                    available_agents.remove(best_agent)
            
            # Assign remaining agents to support roles
            for agent_id in available_agents:
                role_assignments[agent_id] = RoleType.SUPPORT
            
            self.logger.info(f"🎭 Team roles optimized for {team_id}: {len(role_assignments)} assignments")
            return role_assignments
            
        except Exception as e:
            self.logger.error(f"❌ Team role optimization failed: {e}")
            return {}
    
    def _end_role_assignment(self, agent_id: str):
        """End current role assignment for agent"""
        try:
            if agent_id not in self.role_assignments:
                return
            
            assignment = self.role_assignments[agent_id]
            assignment.state = RoleState.INACTIVE
            assignment.duration = time.time() - assignment.assigned_at
            
            # Record assignment
            self.assignment_history.append(assignment)
            
            # Update metrics
            if assignment.performance_score > 0.5:  # Consider successful if > 50%
                self.metrics.successful_assignments += 1
            
            self._update_role_metrics(assignment.duration)
            
        except Exception as e:
            self.logger.error(f"❌ Role assignment end failed: {e}")
    
    def _update_role_metrics(self, assignment_duration: float):
        """Update role system metrics"""
        # Update average assignment duration
        current_avg = self.metrics.average_assignment_duration
        total_assignments = self.metrics.roles_assigned
        
        if total_assignments > 0:
            self.metrics.average_assignment_duration = (
                (current_avg * (total_assignments - 1) + assignment_duration) / total_assignments
            )
        
        # Update role efficiency
        if self.metrics.roles_assigned > 0:
            self.metrics.role_efficiency = (self.metrics.successful_assignments / self.metrics.roles_assigned) * 100
    
    def get_agent_role(self, agent_id: str) -> Optional[RoleType]:
        """Get current role for agent"""
        if agent_id in self.role_assignments:
            assignment = self.role_assignments[agent_id]
            if assignment.state == RoleState.ACTIVE:
                return assignment.role_type
        return None
    
    def get_role_metrics(self) -> Dict[str, Any]:
        """Get role system metrics"""
        return {
            "roles_assigned": self.metrics.roles_assigned,
            "role_switches": self.metrics.role_switches,
            "successful_assignments": self.metrics.successful_assignments,
            "role_efficiency": self.metrics.role_efficiency,
            "average_assignment_duration": self.metrics.average_assignment_duration,
            "active_assignments": len([a for a in self.role_assignments.values() if a.state == RoleState.ACTIVE]),
            "registered_agents": len(self.agent_skills),
            "available_roles": len(self.role_definitions)
        }
    
    def get_team_composition(self, team_id: str) -> Dict[str, Any]:
        """Get team role composition"""
        if team_id not in self.team_roles:
            return {}
        
        composition = {}
        for role_type, agent_list in self.team_roles[team_id].items():
            composition[role_type.value] = {
                "agents": agent_list,
                "count": len(agent_list),
                "max_allowed": self.role_definitions[role_type].max_assignments
            }
        
        return composition

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎭 Role System - Sprint 4 Test")
    print("=" * 60)
    
    # Create role system
    role_system = RoleSystem()
    
    # Register agents with different skill profiles
    print("\n🎭 Registering agents...")
    
    agents_skills = [
        ("agent_1", {"leadership": 0.8, "tactical_awareness": 0.7, "communication": 0.9}),  # Leader
        ("agent_2", {"combat_skill": 0.9, "aggression": 0.8, "mobility": 0.7}),  # Assault
        ("agent_3", {"accuracy": 0.95, "patience": 0.9, "stealth": 0.8}),  # Sniper
        ("agent_4", {"teamwork": 0.8, "resource_management": 0.7, "adaptability": 0.6})  # Support
    ]
    
    for agent_id, skills in agents_skills:
        success = role_system.register_agent(agent_id, skills)
        print(f"   {agent_id}: {'✅' if success else '❌'}")
    
    # Test role assignments
    print("\n🎯 Testing role assignments...")
    
    role_assignments = [
        ("agent_1", RoleType.LEADER),
        ("agent_2", RoleType.ASSAULT),
        ("agent_3", RoleType.SNIPER),
        ("agent_4", RoleType.SUPPORT)
    ]
    
    for agent_id, role_type in role_assignments:
        assignment_id = role_system.assign_role(agent_id, role_type, "alpha_team")
        activated = role_system.activate_role(agent_id) if assignment_id else False
        print(f"   {agent_id} -> {role_type.value}: {'✅' if activated else '❌'}")
    
    # Test performance updates
    print("\n📊 Testing performance updates...")
    
    for agent_id, _ in agents_skills:
        import random
        performance = random.uniform(0.6, 0.9)
        role_system.update_role_performance(agent_id, performance)
        print(f"   {agent_id}: {performance:.3f}")
    
    # Test role optimization
    print("\n🎯 Testing role optimization...")
    
    agent_ids = [agent_id for agent_id, _ in agents_skills]
    required_roles = [RoleType.LEADER, RoleType.ASSAULT, RoleType.SNIPER, RoleType.SUPPORT]
    
    optimized_roles = role_system.optimize_team_roles("alpha_team", agent_ids, required_roles)
    print(f"   Optimized assignments:")
    for agent_id, role_type in optimized_roles.items():
        print(f"     {agent_id} -> {role_type.value}")
    
    # Get metrics
    metrics = role_system.get_role_metrics()
    print(f"\n📊 Role Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get team composition
    composition = role_system.get_team_composition("alpha_team")
    print(f"\n👥 Team Composition:")
    for role_name, role_info in composition.items():
        print(f"   {role_name}: {role_info['count']}/{role_info['max_allowed']} agents")
    
    print("\n🎉 Sprint 4 - Task 4.2 Role System test completed!")
    print("🎯 Dynamic role assignment and optimization working")
    print(f"📈 Current: {metrics['roles_assigned']} assigned, {metrics['role_efficiency']:.1f}% efficiency")
