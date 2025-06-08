#!/usr/bin/env python3
"""
🎯 Strategy Coordination - Gaming AI

Shared strategy management and coordination system for multi-agent teams.

Sprint 4 - Task 4.1 Module 2: Strategy Coordination
- Shared strategy management
- Strategy synchronization
- Coordination algorithms
- Team-based decision making

Author: Nexus - Quantum AI Architect
Sprint: 4.1.2 - Advanced Gaming Features
"""

import time
import threading
import logging
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

# Import communication system
try:
    from agent_communication import AgentCommunication, MessageType, MessagePriority, Message
    COMMUNICATION_AVAILABLE = True
except ImportError:
    COMMUNICATION_AVAILABLE = False
    warnings.warn("🤝 Agent communication not available", ImportWarning)

class StrategyType(Enum):
    """Strategy type enumeration"""
    OFFENSIVE = "offensive"
    DEFENSIVE = "defensive"
    FLANKING = "flanking"
    SUPPORT = "support"
    RETREAT = "retreat"
    HOLD_POSITION = "hold_position"
    ADVANCE = "advance"

class CoordinationMode(Enum):
    """Coordination mode enumeration"""
    CENTRALIZED = "centralized"  # Single leader decides
    DISTRIBUTED = "distributed"  # Consensus-based
    HIERARCHICAL = "hierarchical"  # Chain of command
    DEMOCRATIC = "democratic"  # Voting-based

@dataclass
class TeamStrategy:
    """Team strategy definition"""
    strategy_id: str
    strategy_type: StrategyType
    coordination_mode: CoordinationMode
    parameters: Dict[str, Any]
    agent_roles: Dict[str, str]  # agent_id -> role
    objectives: List[Dict[str, Any]]
    created_at: float
    updated_at: float
    version: int = 1

@dataclass
class StrategyUpdate:
    """Strategy update notification"""
    update_id: str
    strategy_id: str
    changes: Dict[str, Any]
    updated_by: str
    timestamp: float
    requires_sync: bool = True

@dataclass
class CoordinationMetrics:
    """Strategy coordination metrics"""
    strategies_created: int = 0
    strategy_updates: int = 0
    sync_operations: int = 0
    consensus_reached: int = 0
    coordination_conflicts: int = 0

class StrategyCoordination:
    """
    Strategy Coordination System for Multi-Agent Teams
    
    Features:
    - Shared strategy management across agents
    - Real-time strategy synchronization
    - Multiple coordination modes
    - Conflict resolution for strategy changes
    - Performance tracking and optimization
    """
    
    def __init__(self, communication_system: Optional[AgentCommunication] = None):
        self.logger = logging.getLogger("StrategyCoordination")
        
        # Communication integration
        self.comm_system = communication_system
        
        # Strategy management
        self.active_strategies = {}  # strategy_id -> TeamStrategy
        self.strategy_history = deque(maxlen=100)
        self.pending_updates = {}  # update_id -> StrategyUpdate
        
        # Agent coordination
        self.agent_strategies = {}  # agent_id -> strategy_id
        self.agent_roles = {}  # agent_id -> current_role
        self.team_composition = {}  # team_id -> [agent_ids]
        
        # Coordination state
        self.coordination_mode = CoordinationMode.DISTRIBUTED
        self.team_leader = None
        self.consensus_threshold = 0.6  # 60% agreement needed
        
        # Threading
        self.coordination_lock = threading.RLock()
        self.sync_active = False
        self.sync_thread = None
        
        # Performance tracking
        self.metrics = CoordinationMetrics()
        
        # Strategy templates
        self.strategy_templates = self._initialize_strategy_templates()
        
        self.logger.info("🎯 Strategy Coordination initialized")
    
    def _initialize_strategy_templates(self) -> Dict[StrategyType, Dict[str, Any]]:
        """Initialize strategy templates"""
        return {
            StrategyType.OFFENSIVE: {
                'parameters': {
                    'aggression_level': 0.8,
                    'risk_tolerance': 0.7,
                    'coordination_tightness': 0.6
                },
                'roles': ['attacker', 'flanker', 'support'],
                'objectives': [
                    {'type': 'eliminate_enemies', 'priority': 1},
                    {'type': 'control_territory', 'priority': 2}
                ]
            },
            
            StrategyType.DEFENSIVE: {
                'parameters': {
                    'aggression_level': 0.3,
                    'risk_tolerance': 0.2,
                    'coordination_tightness': 0.9
                },
                'roles': ['defender', 'overwatch', 'support'],
                'objectives': [
                    {'type': 'hold_position', 'priority': 1},
                    {'type': 'protect_assets', 'priority': 2}
                ]
            },
            
            StrategyType.FLANKING: {
                'parameters': {
                    'aggression_level': 0.6,
                    'risk_tolerance': 0.5,
                    'coordination_tightness': 0.7
                },
                'roles': ['flanker', 'distraction', 'support'],
                'objectives': [
                    {'type': 'flank_enemies', 'priority': 1},
                    {'type': 'create_advantage', 'priority': 2}
                ]
            },
            
            StrategyType.SUPPORT: {
                'parameters': {
                    'aggression_level': 0.4,
                    'risk_tolerance': 0.3,
                    'coordination_tightness': 0.8
                },
                'roles': ['healer', 'supplier', 'coordinator'],
                'objectives': [
                    {'type': 'support_team', 'priority': 1},
                    {'type': 'maintain_resources', 'priority': 2}
                ]
            }
        }
    
    def create_team_strategy(self, strategy_type: StrategyType, 
                           team_agents: List[str],
                           custom_parameters: Optional[Dict[str, Any]] = None,
                           coordination_mode: CoordinationMode = CoordinationMode.DISTRIBUTED) -> str:
        """Create new team strategy"""
        try:
            with self.coordination_lock:
                strategy_id = f"strategy_{int(time.time() * 1000000)}"
                
                # Get strategy template
                template = self.strategy_templates.get(strategy_type, {})
                
                # Merge parameters
                parameters = template.get('parameters', {}).copy()
                if custom_parameters:
                    parameters.update(custom_parameters)
                
                # Assign roles to agents
                available_roles = template.get('roles', ['generic'])
                agent_roles = self._assign_agent_roles(team_agents, available_roles)
                
                # Create strategy
                strategy = TeamStrategy(
                    strategy_id=strategy_id,
                    strategy_type=strategy_type,
                    coordination_mode=coordination_mode,
                    parameters=parameters,
                    agent_roles=agent_roles,
                    objectives=template.get('objectives', []),
                    created_at=time.time(),
                    updated_at=time.time()
                )
                
                # Store strategy
                self.active_strategies[strategy_id] = strategy
                
                # Update agent assignments
                for agent_id in team_agents:
                    self.agent_strategies[agent_id] = strategy_id
                    self.agent_roles[agent_id] = agent_roles.get(agent_id, 'generic')
                
                # Broadcast strategy to team
                self._broadcast_strategy_update(strategy, team_agents)
                
                # Update metrics
                self.metrics.strategies_created += 1
                
                self.logger.info(f"🎯 Strategy created: {strategy_type.value} ({strategy_id[:8]}...)")
                return strategy_id
                
        except Exception as e:
            self.logger.error(f"❌ Strategy creation failed: {e}")
            return ""
    
    def _assign_agent_roles(self, agents: List[str], available_roles: List[str]) -> Dict[str, str]:
        """Assign roles to agents based on capabilities"""
        agent_roles = {}
        
        # Simple round-robin assignment for now
        # In a real implementation, this would consider agent capabilities
        for i, agent_id in enumerate(agents):
            role_index = i % len(available_roles)
            agent_roles[agent_id] = available_roles[role_index]
        
        return agent_roles
    
    def update_strategy(self, strategy_id: str, updates: Dict[str, Any], 
                       updated_by: str) -> bool:
        """Update existing strategy"""
        try:
            with self.coordination_lock:
                if strategy_id not in self.active_strategies:
                    self.logger.warning(f"⚠️ Strategy not found: {strategy_id}")
                    return False
                
                strategy = self.active_strategies[strategy_id]
                
                # Create update record
                update_id = f"update_{int(time.time() * 1000000)}"
                strategy_update = StrategyUpdate(
                    update_id=update_id,
                    strategy_id=strategy_id,
                    changes=updates.copy(),
                    updated_by=updated_by,
                    timestamp=time.time()
                )
                
                # Check if update requires consensus
                if strategy.coordination_mode == CoordinationMode.DEMOCRATIC:
                    return self._request_consensus(strategy_update)
                elif strategy.coordination_mode == CoordinationMode.CENTRALIZED:
                    if updated_by != self.team_leader:
                        self.logger.warning(f"⚠️ Unauthorized strategy update by {updated_by}")
                        return False
                
                # Apply updates
                self._apply_strategy_updates(strategy, updates)
                
                # Broadcast update
                team_agents = [aid for aid, sid in self.agent_strategies.items() if sid == strategy_id]
                self._broadcast_strategy_update(strategy, team_agents)
                
                # Update metrics
                self.metrics.strategy_updates += 1
                
                self.logger.info(f"🔄 Strategy updated: {strategy_id[:8]}... by {updated_by}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Strategy update failed: {e}")
            return False
    
    def _apply_strategy_updates(self, strategy: TeamStrategy, updates: Dict[str, Any]):
        """Apply updates to strategy"""
        for key, value in updates.items():
            if key == 'parameters':
                strategy.parameters.update(value)
            elif key == 'agent_roles':
                strategy.agent_roles.update(value)
                # Update agent role tracking
                for agent_id, role in value.items():
                    self.agent_roles[agent_id] = role
            elif key == 'objectives':
                strategy.objectives = value
            elif hasattr(strategy, key):
                setattr(strategy, key, value)
        
        strategy.updated_at = time.time()
        strategy.version += 1
    
    def _request_consensus(self, strategy_update: StrategyUpdate) -> bool:
        """Request consensus for strategy update"""
        try:
            # Store pending update
            self.pending_updates[strategy_update.update_id] = strategy_update
            
            # Get affected agents
            strategy_id = strategy_update.strategy_id
            team_agents = [aid for aid, sid in self.agent_strategies.items() if sid == strategy_id]
            
            # Send consensus request
            if self.comm_system:
                content = {
                    'update_id': strategy_update.update_id,
                    'strategy_id': strategy_id,
                    'changes': strategy_update.changes,
                    'proposed_by': strategy_update.updated_by,
                    'requires_vote': True
                }
                
                for agent_id in team_agents:
                    if agent_id != strategy_update.updated_by:
                        self.comm_system.send_message(
                            "STRATEGY_COORDINATOR", agent_id,
                            MessageType.COORDINATION_REQUEST, content,
                            MessagePriority.HIGH, requires_ack=True
                        )
            
            self.logger.info(f"🗳️ Consensus requested for update: {strategy_update.update_id[:8]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Consensus request failed: {e}")
            return False
    
    def vote_on_strategy_update(self, agent_id: str, update_id: str, vote: bool) -> bool:
        """Vote on pending strategy update"""
        try:
            with self.coordination_lock:
                if update_id not in self.pending_updates:
                    return False
                
                strategy_update = self.pending_updates[update_id]
                
                # Record vote (simplified - would need proper vote tracking)
                # For now, just apply if vote is positive
                if vote:
                    strategy_id = strategy_update.strategy_id
                    if strategy_id in self.active_strategies:
                        strategy = self.active_strategies[strategy_id]
                        self._apply_strategy_updates(strategy, strategy_update.changes)
                        
                        # Broadcast update
                        team_agents = [aid for aid, sid in self.agent_strategies.items() if sid == strategy_id]
                        self._broadcast_strategy_update(strategy, team_agents)
                        
                        # Clean up
                        del self.pending_updates[update_id]
                        
                        self.metrics.consensus_reached += 1
                        self.logger.info(f"✅ Consensus reached for update: {update_id[:8]}...")
                        return True
                
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Vote processing failed: {e}")
            return False
    
    def _broadcast_strategy_update(self, strategy: TeamStrategy, team_agents: List[str]):
        """Broadcast strategy update to team agents"""
        if not self.comm_system:
            return
        
        try:
            content = {
                'strategy_id': strategy.strategy_id,
                'strategy_type': strategy.strategy_type.value,
                'coordination_mode': strategy.coordination_mode.value,
                'parameters': strategy.parameters,
                'agent_roles': strategy.agent_roles,
                'objectives': strategy.objectives,
                'version': strategy.version,
                'updated_at': strategy.updated_at
            }
            
            for agent_id in team_agents:
                self.comm_system.send_message(
                    "STRATEGY_COORDINATOR", agent_id,
                    MessageType.STRATEGY_UPDATE, content,
                    MessagePriority.HIGH
                )
            
            self.metrics.sync_operations += 1
            
        except Exception as e:
            self.logger.error(f"❌ Strategy broadcast failed: {e}")
    
    def get_agent_strategy(self, agent_id: str) -> Optional[TeamStrategy]:
        """Get current strategy for agent"""
        with self.coordination_lock:
            strategy_id = self.agent_strategies.get(agent_id)
            if strategy_id and strategy_id in self.active_strategies:
                return self.active_strategies[strategy_id]
            return None
    
    def get_agent_role(self, agent_id: str) -> Optional[str]:
        """Get current role for agent"""
        return self.agent_roles.get(agent_id)
    
    def synchronize_strategies(self) -> bool:
        """Synchronize all active strategies"""
        try:
            with self.coordination_lock:
                synchronized_count = 0
                
                for strategy_id, strategy in self.active_strategies.items():
                    # Get team agents
                    team_agents = [aid for aid, sid in self.agent_strategies.items() if sid == strategy_id]
                    
                    if team_agents:
                        self._broadcast_strategy_update(strategy, team_agents)
                        synchronized_count += 1
                
                self.logger.info(f"🔄 Synchronized {synchronized_count} strategies")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Strategy synchronization failed: {e}")
            return False
    
    def start_coordination(self) -> bool:
        """Start strategy coordination"""
        if self.sync_active:
            return True

        try:
            self.sync_active = True
            self.sync_thread = threading.Thread(target=self._coordination_loop, daemon=True)
            self.sync_thread.start()
            self.logger.info("🔄 Strategy coordination started")
            return True
        except Exception as e:
            self.logger.error(f"❌ Strategy coordination start failed: {e}")
            return False
    
    def stop_coordination(self):
        """Stop strategy coordination"""
        self.sync_active = False
        if self.sync_thread:
            self.sync_thread.join(timeout=1.0)
        self.logger.info("🛑 Strategy coordination stopped")
    
    def _coordination_loop(self):
        """Strategy coordination loop"""
        while self.sync_active:
            try:
                # Periodic strategy synchronization
                if len(self.active_strategies) > 0:
                    self.synchronize_strategies()
                
                # Clean up old pending updates
                self._cleanup_expired_updates()
                
                time.sleep(5.0)  # Sync every 5 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Coordination loop error: {e}")
                time.sleep(1.0)
    
    def _cleanup_expired_updates(self):
        """Clean up expired pending updates"""
        current_time = time.time()
        expired_updates = []
        
        for update_id, update in self.pending_updates.items():
            if current_time - update.timestamp > 60.0:  # 1 minute timeout
                expired_updates.append(update_id)
        
        for update_id in expired_updates:
            del self.pending_updates[update_id]
            self.logger.debug(f"⏰ Update expired: {update_id[:8]}...")
    
    def get_coordination_metrics(self) -> Dict[str, Any]:
        """Get coordination metrics"""
        with self.coordination_lock:
            return {
                'strategies_created': self.metrics.strategies_created,
                'strategy_updates': self.metrics.strategy_updates,
                'sync_operations': self.metrics.sync_operations,
                'consensus_reached': self.metrics.consensus_reached,
                'coordination_conflicts': self.metrics.coordination_conflicts,
                'active_strategies': len(self.active_strategies),
                'pending_updates': len(self.pending_updates),
                'coordinated_agents': len(self.agent_strategies),
                'coordination_mode': self.coordination_mode.value,
                'sync_active': self.sync_active
            }
    
    def get_team_status(self) -> Dict[str, Any]:
        """Get current team status"""
        with self.coordination_lock:
            team_status = {}
            
            for strategy_id, strategy in self.active_strategies.items():
                team_agents = [aid for aid, sid in self.agent_strategies.items() if sid == strategy_id]
                
                team_status[strategy_id] = {
                    'strategy_type': strategy.strategy_type.value,
                    'coordination_mode': strategy.coordination_mode.value,
                    'team_size': len(team_agents),
                    'agents': team_agents,
                    'roles': {aid: self.agent_roles.get(aid, 'unknown') for aid in team_agents},
                    'version': strategy.version,
                    'updated_at': strategy.updated_at
                }
            
            return team_status

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 Strategy Coordination - Sprint 4 Test")
    print("=" * 60)
    
    # Create strategy coordination system
    coordinator = StrategyCoordination()
    
    # Test strategy creation
    print("\n🎯 Testing strategy creation...")
    
    team_agents = ["agent_1", "agent_2", "agent_3"]
    
    strategy_id = coordinator.create_team_strategy(
        StrategyType.OFFENSIVE,
        team_agents,
        custom_parameters={'aggression_level': 0.9},
        coordination_mode=CoordinationMode.DISTRIBUTED
    )
    
    print(f"   Strategy created: {strategy_id[:8]}...")
    
    # Test strategy updates
    print("\n🔄 Testing strategy updates...")
    
    updates = {
        'parameters': {'risk_tolerance': 0.8},
        'agent_roles': {'agent_1': 'leader'}
    }
    
    success = coordinator.update_strategy(strategy_id, updates, "agent_1")
    print(f"   Strategy updated: {'✅' if success else '❌'}")
    
    # Test agent queries
    print("\n👥 Testing agent queries...")
    
    for agent_id in team_agents:
        strategy = coordinator.get_agent_strategy(agent_id)
        role = coordinator.get_agent_role(agent_id)
        print(f"   {agent_id}: {strategy.strategy_type.value if strategy else 'None'} ({role})")
    
    # Get metrics
    metrics = coordinator.get_coordination_metrics()
    print(f"\n📊 Coordination Metrics:")
    for key, value in metrics.items():
        print(f"   {key}: {value}")
    
    # Get team status
    team_status = coordinator.get_team_status()
    print(f"\n👥 Team Status:")
    for strategy_id, status in team_status.items():
        print(f"   Strategy {strategy_id[:8]}...: {status['strategy_type']} ({status['team_size']} agents)")
    
    print("\n🎉 Sprint 4 - Task 4.1 Module 2 test completed!")
    print("🎯 Target: Shared strategy coordination, real-time sync")
    print(f"📈 Current: {metrics['strategies_created']} strategies, {metrics['sync_operations']} sync ops")
