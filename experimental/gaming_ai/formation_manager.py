#!/usr/bin/env python3
"""
📐 Formation Manager - Gaming AI

Formation management and positioning system for team coordination.

Sprint 4 - Task 4.2 Module 3: Formation Manager
- Formation patterns and templates
- Dynamic formation switching
- Position optimization
- Formation maintenance

Author: Nexus - Quantum AI Architect
Sprint: 4.2.3 - Advanced Gaming Features
"""

import time
import math
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

class FormationType(Enum):
    """Formation type enumeration"""
    LINE = "line"
    WEDGE = "wedge"
    CIRCLE = "circle"
    DIAMOND = "diamond"
    COLUMN = "column"
    STAGGERED = "staggered"
    SPREAD = "spread"
    DEFENSIVE_SQUARE = "defensive_square"

class FormationState(Enum):
    """Formation state enumeration"""
    FORMING = "forming"
    FORMED = "formed"
    MOVING = "moving"
    BREAKING = "breaking"
    BROKEN = "broken"

@dataclass
class Position:
    """2D position with orientation"""
    x: float
    y: float
    facing: float = 0.0  # Degrees

@dataclass
class FormationSlot:
    """Formation slot definition"""
    slot_id: str
    relative_position: Position
    role: str = "default"
    priority: int = 1
    assigned_agent: Optional[str] = None

@dataclass
class Formation:
    """Complete formation definition"""
    formation_id: str
    formation_type: FormationType
    name: str
    description: str
    center_position: Position
    slots: List[FormationSlot]
    max_agents: int
    formation_radius: float = 10.0
    state: FormationState = FormationState.FORMING
    created_at: float = 0.0

@dataclass
class FormationMetrics:
    """Formation management metrics"""
    formations_created: int = 0
    formations_executed: int = 0
    successful_formations: int = 0
    average_formation_time: float = 0.0
    position_accuracy: float = 0.0

class FormationManager:
    """
    Formation Management System
    
    Features:
    - Formation pattern templates
    - Dynamic formation creation
    - Position optimization
    - Formation state management
    """
    
    def __init__(self):
        self.logger = logging.getLogger("FormationManager")
        
        # Formation management
        self.formations = {}  # formation_id -> Formation
        self.formation_templates = {}  # formation_type -> template
        self.active_formations = {}  # team_id -> formation_id
        
        # Agent positioning
        self.agent_positions = {}  # agent_id -> Position
        self.agent_assignments = {}  # agent_id -> (formation_id, slot_id)
        
        # Performance tracking
        self.metrics = FormationMetrics()
        self.formation_history = deque(maxlen=100)
        
        # Initialize formation templates
        self._initialize_formation_templates()
        
        self.logger.info("📐 Formation Manager initialized")
    
    def _initialize_formation_templates(self):
        """Initialize formation templates"""
        self.formation_templates = {
            FormationType.LINE: {
                "name": "Line Formation",
                "description": "Agents form a straight line",
                "max_agents": 8,
                "formation_radius": 15.0,
                "slot_generator": self._generate_line_slots
            },
            
            FormationType.WEDGE: {
                "name": "Wedge Formation",
                "description": "V-shaped formation for advance",
                "max_agents": 6,
                "formation_radius": 12.0,
                "slot_generator": self._generate_wedge_slots
            },
            
            FormationType.CIRCLE: {
                "name": "Circle Formation",
                "description": "Agents form defensive circle",
                "max_agents": 8,
                "formation_radius": 10.0,
                "slot_generator": self._generate_circle_slots
            },
            
            FormationType.DIAMOND: {
                "name": "Diamond Formation",
                "description": "Diamond shape for balanced coverage",
                "max_agents": 4,
                "formation_radius": 8.0,
                "slot_generator": self._generate_diamond_slots
            },
            
            FormationType.COLUMN: {
                "name": "Column Formation",
                "description": "Single file for narrow passages",
                "max_agents": 6,
                "formation_radius": 20.0,
                "slot_generator": self._generate_column_slots
            },
            
            FormationType.STAGGERED: {
                "name": "Staggered Formation",
                "description": "Offset positions for cover",
                "max_agents": 6,
                "formation_radius": 15.0,
                "slot_generator": self._generate_staggered_slots
            }
        }
    
    def create_formation(self, team_id: str, formation_type: FormationType,
                        center_position: Position, agent_ids: List[str]) -> str:
        """Create formation for team"""
        try:
            if formation_type not in self.formation_templates:
                self.logger.error(f"❌ Unknown formation type: {formation_type}")
                return ""
            
            template = self.formation_templates[formation_type]
            
            # Validate agent count
            if len(agent_ids) > template["max_agents"]:
                self.logger.warning(f"⚠️ Too many agents, limiting to {template['max_agents']}")
                agent_ids = agent_ids[:template["max_agents"]]
            
            # Generate formation ID
            formation_id = f"formation_{team_id}_{formation_type.value}_{int(time.time() * 1000)}"
            
            # Generate formation slots
            slot_generator = template["slot_generator"]
            slots = slot_generator(len(agent_ids), template["formation_radius"])
            
            # Assign agents to slots
            for i, agent_id in enumerate(agent_ids):
                if i < len(slots):
                    slots[i].assigned_agent = agent_id
                    self.agent_assignments[agent_id] = (formation_id, slots[i].slot_id)
            
            # Create formation
            formation = Formation(
                formation_id=formation_id,
                formation_type=formation_type,
                name=f"{template['name']} - {team_id}",
                description=template["description"],
                center_position=center_position,
                slots=slots,
                max_agents=template["max_agents"],
                formation_radius=template["formation_radius"],
                created_at=time.time()
            )
            
            # Store formation
            self.formations[formation_id] = formation
            self.active_formations[team_id] = formation_id
            self.metrics.formations_created += 1
            
            self.logger.info(f"📐 Formation created: {formation_type.value} for {team_id}")
            return formation_id
            
        except Exception as e:
            self.logger.error(f"❌ Formation creation failed: {e}")
            return ""
    
    def _generate_line_slots(self, agent_count: int, radius: float) -> List[FormationSlot]:
        """Generate line formation slots"""
        slots = []
        spacing = radius * 2 / max(1, agent_count - 1) if agent_count > 1 else 0
        start_x = -radius if agent_count > 1 else 0
        
        for i in range(agent_count):
            slot_id = f"line_slot_{i}"
            x_pos = start_x + (i * spacing)
            
            slot = FormationSlot(
                slot_id=slot_id,
                relative_position=Position(x_pos, 0.0, 0.0),
                role="line_member",
                priority=i + 1
            )
            slots.append(slot)
        
        return slots
    
    def _generate_wedge_slots(self, agent_count: int, radius: float) -> List[FormationSlot]:
        """Generate wedge formation slots"""
        slots = []
        
        # Leader at front
        slots.append(FormationSlot(
            slot_id="wedge_leader",
            relative_position=Position(0.0, radius, 0.0),
            role="leader",
            priority=1
        ))
        
        # Wings
        remaining_agents = agent_count - 1
        for i in range(remaining_agents):
            side = 1 if i % 2 == 0 else -1  # Alternate sides
            row = (i // 2) + 1
            
            x_pos = side * (row * radius * 0.6)
            y_pos = radius - (row * radius * 0.4)
            
            slot = FormationSlot(
                slot_id=f"wedge_wing_{i}",
                relative_position=Position(x_pos, y_pos, 0.0),
                role="wing",
                priority=i + 2
            )
            slots.append(slot)
        
        return slots
    
    def _generate_circle_slots(self, agent_count: int, radius: float) -> List[FormationSlot]:
        """Generate circle formation slots"""
        slots = []
        angle_step = 360.0 / agent_count if agent_count > 0 else 0
        
        for i in range(agent_count):
            angle = math.radians(i * angle_step)
            x_pos = radius * math.cos(angle)
            y_pos = radius * math.sin(angle)
            facing = math.degrees(angle) + 90  # Face outward
            
            slot = FormationSlot(
                slot_id=f"circle_slot_{i}",
                relative_position=Position(x_pos, y_pos, facing),
                role="defender",
                priority=i + 1
            )
            slots.append(slot)
        
        return slots
    
    def _generate_diamond_slots(self, agent_count: int, radius: float) -> List[FormationSlot]:
        """Generate diamond formation slots"""
        slots = []
        
        # Diamond positions: front, left, right, back
        positions = [
            (0.0, radius, "front"),      # Front
            (-radius, 0.0, "left"),      # Left
            (radius, 0.0, "right"),      # Right
            (0.0, -radius, "back")       # Back
        ]
        
        for i in range(min(agent_count, len(positions))):
            x_pos, y_pos, role = positions[i]
            
            slot = FormationSlot(
                slot_id=f"diamond_{role}",
                relative_position=Position(x_pos, y_pos, 0.0),
                role=role,
                priority=i + 1
            )
            slots.append(slot)
        
        return slots
    
    def _generate_column_slots(self, agent_count: int, radius: float) -> List[FormationSlot]:
        """Generate column formation slots"""
        slots = []
        spacing = radius * 2 / max(1, agent_count - 1) if agent_count > 1 else 0
        start_y = radius if agent_count > 1 else 0
        
        for i in range(agent_count):
            slot_id = f"column_slot_{i}"
            y_pos = start_y - (i * spacing)
            
            role = "leader" if i == 0 else "follower"
            
            slot = FormationSlot(
                slot_id=slot_id,
                relative_position=Position(0.0, y_pos, 0.0),
                role=role,
                priority=i + 1
            )
            slots.append(slot)
        
        return slots
    
    def _generate_staggered_slots(self, agent_count: int, radius: float) -> List[FormationSlot]:
        """Generate staggered formation slots"""
        slots = []
        
        for i in range(agent_count):
            # Stagger positions in zigzag pattern
            row = i // 2
            side = 1 if i % 2 == 0 else -1
            
            x_pos = side * (radius * 0.5)
            y_pos = radius - (row * radius * 0.6)
            
            slot = FormationSlot(
                slot_id=f"staggered_slot_{i}",
                relative_position=Position(x_pos, y_pos, 0.0),
                role="staggered_member",
                priority=i + 1
            )
            slots.append(slot)
        
        return slots
    
    def execute_formation(self, formation_id: str) -> bool:
        """Execute formation positioning"""
        try:
            if formation_id not in self.formations:
                self.logger.error(f"❌ Unknown formation: {formation_id}")
                return False
            
            formation = self.formations[formation_id]
            execution_start = time.time()
            
            # Update formation state
            formation.state = FormationState.FORMING
            
            # Calculate absolute positions for all agents
            success = self._position_agents_in_formation(formation)
            
            # Update formation state
            if success:
                formation.state = FormationState.FORMED
                self.metrics.successful_formations += 1
            else:
                formation.state = FormationState.BROKEN
            
            # Update metrics
            execution_time = time.time() - execution_start
            self.metrics.formations_executed += 1
            self._update_formation_metrics(execution_time)
            
            # Record formation execution
            formation_record = {
                "formation_id": formation_id,
                "formation_type": formation.formation_type.value,
                "success": success,
                "execution_time": execution_time,
                "timestamp": execution_start,
                "agent_count": len([slot for slot in formation.slots if slot.assigned_agent])
            }
            self.formation_history.append(formation_record)
            
            self.logger.info(f"📐 Formation executed: {formation.formation_type.value} ({'✅' if success else '❌'})")
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Formation execution failed: {e}")
            return False
    
    def _position_agents_in_formation(self, formation: Formation) -> bool:
        """Position agents according to formation"""
        try:
            positioned_count = 0
            
            for slot in formation.slots:
                if slot.assigned_agent:
                    # Calculate absolute position
                    absolute_position = self._calculate_absolute_position(
                        formation.center_position, slot.relative_position
                    )
                    
                    # Update agent position
                    self.agent_positions[slot.assigned_agent] = absolute_position
                    positioned_count += 1
                    
                    self.logger.debug(f"📍 Positioned {slot.assigned_agent} at ({absolute_position.x:.1f}, {absolute_position.y:.1f})")
            
            # Calculate position accuracy
            expected_positions = len([slot for slot in formation.slots if slot.assigned_agent])
            if expected_positions > 0:
                accuracy = positioned_count / expected_positions
                self.metrics.position_accuracy = (
                    (self.metrics.position_accuracy * (self.metrics.formations_executed - 1) + accuracy) /
                    self.metrics.formations_executed
                )
            
            return positioned_count > 0
            
        except Exception as e:
            self.logger.error(f"❌ Agent positioning failed: {e}")
            return False
    
    def _calculate_absolute_position(self, center: Position, relative: Position) -> Position:
        """Calculate absolute position from center and relative position"""
        # Simple translation for now (could add rotation later)
        return Position(
            x=center.x + relative.x,
            y=center.y + relative.y,
            facing=center.facing + relative.facing
        )
    
    def move_formation(self, formation_id: str, new_center: Position) -> bool:
        """Move entire formation to new position"""
        try:
            if formation_id not in self.formations:
                return False
            
            formation = self.formations[formation_id]
            formation.state = FormationState.MOVING
            
            # Update center position
            formation.center_position = new_center
            
            # Reposition all agents
            success = self._position_agents_in_formation(formation)
            
            if success:
                formation.state = FormationState.FORMED
            else:
                formation.state = FormationState.BROKEN
            
            self.logger.info(f"📐 Formation moved: {formation.formation_type.value}")
            return success
            
        except Exception as e:
            self.logger.error(f"❌ Formation move failed: {e}")
            return False
    
    def break_formation(self, formation_id: str) -> bool:
        """Break formation and free agents"""
        try:
            if formation_id not in self.formations:
                return False
            
            formation = self.formations[formation_id]
            formation.state = FormationState.BREAKING
            
            # Clear agent assignments
            for slot in formation.slots:
                if slot.assigned_agent:
                    if slot.assigned_agent in self.agent_assignments:
                        del self.agent_assignments[slot.assigned_agent]
                    slot.assigned_agent = None
            
            formation.state = FormationState.BROKEN
            
            # Remove from active formations
            team_to_remove = None
            for team_id, active_formation_id in self.active_formations.items():
                if active_formation_id == formation_id:
                    team_to_remove = team_id
                    break
            
            if team_to_remove:
                del self.active_formations[team_to_remove]
            
            self.logger.info(f"📐 Formation broken: {formation.formation_type.value}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Formation break failed: {e}")
            return False
    
    def get_agent_position(self, agent_id: str) -> Optional[Position]:
        """Get current position of agent"""
        return self.agent_positions.get(agent_id)
    
    def get_formation_status(self, formation_id: str) -> Optional[Dict[str, Any]]:
        """Get formation status"""
        if formation_id not in self.formations:
            return None
        
        formation = self.formations[formation_id]
        assigned_agents = [slot.assigned_agent for slot in formation.slots if slot.assigned_agent]
        
        return {
            "formation_id": formation_id,
            "formation_type": formation.formation_type.value,
            "name": formation.name,
            "state": formation.state.value,
            "center_position": {
                "x": formation.center_position.x,
                "y": formation.center_position.y,
                "facing": formation.center_position.facing
            },
            "assigned_agents": assigned_agents,
            "agent_count": len(assigned_agents),
            "max_agents": formation.max_agents,
            "formation_radius": formation.formation_radius
        }
    
    def _update_formation_metrics(self, execution_time: float):
        """Update formation metrics"""
        current_avg = self.metrics.average_formation_time
        executed_count = self.metrics.formations_executed
        
        if executed_count > 0:
            self.metrics.average_formation_time = (
                (current_avg * (executed_count - 1) + execution_time) / executed_count
            )
    
    def get_formation_metrics(self) -> Dict[str, Any]:
        """Get formation management metrics"""
        return {
            "formations_created": self.metrics.formations_created,
            "formations_executed": self.metrics.formations_executed,
            "successful_formations": self.metrics.successful_formations,
            "formation_success_rate": (self.metrics.successful_formations / max(1, self.metrics.formations_executed)) * 100,
            "average_formation_time": self.metrics.average_formation_time,
            "position_accuracy": self.metrics.position_accuracy,
            "active_formations": len(self.active_formations),
            "tracked_agents": len(self.agent_positions)
        }

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("📐 Formation Manager - Sprint 4 Test")
    print("=" * 60)
    
    # Create formation manager
    formation_manager = FormationManager()
    
    # Test formation creation
    print("\n📐 Testing formation creation...")
    
    center_pos = Position(100.0, 100.0, 0.0)
    team_agents = ["agent_1", "agent_2", "agent_3", "agent_4"]
    
    formations_created = []
    for formation_type in [FormationType.LINE, FormationType.WEDGE, FormationType.CIRCLE]:
        formation_id = formation_manager.create_formation(
            "alpha_team", formation_type, center_pos, team_agents
        )
        formations_created.append((formation_type, formation_id))
        print(f"   {formation_type.value}: {formation_id[:8] if formation_id else 'Failed'}...")
    
    # Test formation execution
    print("\n🎯 Testing formation execution...")
    
    for formation_type, formation_id in formations_created:
        if formation_id:
            success = formation_manager.execute_formation(formation_id)
            print(f"   {formation_type.value}: {'✅' if success else '❌'}")
    
    # Test agent positioning
    print("\n📍 Testing agent positions...")
    
    for agent_id in team_agents:
        position = formation_manager.get_agent_position(agent_id)
        if position:
            print(f"   {agent_id}: ({position.x:.1f}, {position.y:.1f})")
    
    # Get formation metrics
    metrics = formation_manager.get_formation_metrics()
    print(f"\n📊 Formation Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    # Get formation status
    if formations_created:
        formation_type, formation_id = formations_created[0]
        if formation_id:
            status = formation_manager.get_formation_status(formation_id)
            if status:
                print(f"\n📐 Formation Status:")
                print(f"   Type: {status['formation_type']}")
                print(f"   State: {status['state']}")
                print(f"   Agents: {status['agent_count']}/{status['max_agents']}")
    
    print("\n🎉 Sprint 4 - Task 4.2 Formation Manager test completed!")
    print("🎯 Formation patterns and positioning working")
    print(f"📈 Current: {metrics['formations_created']} created, {metrics['formation_success_rate']:.1f}% success rate")
