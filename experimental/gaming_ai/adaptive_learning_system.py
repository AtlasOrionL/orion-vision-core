#!/usr/bin/env python3
"""
📚 Adaptive Learning System - Gaming AI

ML-based adaptation and continuous improvement system for gaming AI.

Sprint 3 - Task 3.3: Learning System Development
- Real-time learning from gameplay
- Strategy adaptation based on performance
- Memory-efficient experience storage
- Measurable improvement over time

Author: Nexus - Quantum AI Architect
Sprint: 3.3 - AI Intelligence & Decision Making
"""

import time
import numpy as np
import threading
import logging
import pickle
import json
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
import warnings

# ML imports
try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.neural_network import MLPRegressor
    from sklearn.preprocessing import StandardScaler
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    warnings.warn("🤖 scikit-learn not available - using simplified learning", ImportWarning)

class LearningMode(Enum):
    """Learning mode enumeration"""
    EXPLORATION = "exploration"
    EXPLOITATION = "exploitation"
    BALANCED = "balanced"
    CONSERVATIVE = "conservative"

class ExperienceType(Enum):
    """Experience type enumeration"""
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    CRITICAL = "critical"

@dataclass
class Experience:
    """Gaming experience record"""
    experience_id: str
    timestamp: float
    game_state: Dict[str, Any]
    action_taken: Dict[str, Any]
    outcome: Dict[str, Any]
    reward: float
    experience_type: ExperienceType
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LearningMetrics:
    """Learning performance metrics"""
    experiences_collected: int = 0
    strategies_learned: int = 0
    performance_improvement: float = 0.0
    learning_rate: float = 0.01
    exploration_rate: float = 0.1
    average_reward: float = 0.0

@dataclass
class StrategyPattern:
    """Learned strategy pattern"""
    pattern_id: str
    conditions: Dict[str, Any]
    actions: List[Dict[str, Any]]
    success_rate: float
    usage_count: int
    last_updated: float

class AdaptiveLearningSystem:
    """
    Adaptive Learning System for Gaming AI
    
    Features:
    - Real-time learning from gameplay experiences
    - Strategy adaptation based on performance feedback
    - Memory-efficient experience replay
    - Continuous improvement mechanisms
    - Multi-objective optimization
    """
    
    def __init__(self, memory_size: int = 10000, learning_rate: float = 0.01):
        self.memory_size = memory_size
        self.learning_rate = learning_rate
        self.logger = logging.getLogger("AdaptiveLearningSystem")
        
        # Experience memory
        self.experience_buffer = deque(maxlen=memory_size)
        self.priority_buffer = deque(maxlen=1000)  # High-priority experiences
        
        # Learning models
        self.models = {}
        self.scalers = {}
        self._initialize_models()
        
        # Strategy patterns
        self.learned_strategies = {}
        self.strategy_performance = {}
        
        # Learning configuration
        self.learning_mode = LearningMode.BALANCED
        self.metrics = LearningMetrics()
        
        # Threading for background learning
        self.learning_active = False
        self.learning_thread = None
        self.learning_lock = threading.RLock()
        
        # Performance tracking
        self.performance_history = deque(maxlen=1000)
        self.baseline_performance = 0.0
        
        # Adaptation parameters
        self.adaptation_threshold = 0.05  # 5% improvement threshold
        self.exploration_decay = 0.995
        self.min_exploration = 0.01
        
        self.logger.info(f"📚 Adaptive Learning System initialized (memory: {memory_size})")
    
    def _initialize_models(self):
        """Initialize machine learning models"""
        if SKLEARN_AVAILABLE:
            # Value function approximator
            self.models['value'] = RandomForestRegressor(
                n_estimators=50,
                max_depth=10,
                random_state=42
            )
            
            # Policy network
            self.models['policy'] = MLPRegressor(
                hidden_layer_sizes=(64, 32),
                learning_rate_init=self.learning_rate,
                max_iter=100,
                random_state=42
            )
            
            # Feature scalers
            self.scalers['state'] = StandardScaler()
            self.scalers['action'] = StandardScaler()
            
            self.logger.info("✅ ML models initialized")
        else:
            self.logger.warning("⚠️ Using simplified learning models")
    
    def record_experience(self, game_state: Dict[str, Any], action: Dict[str, Any], 
                         outcome: Dict[str, Any], reward: float, 
                         context: Optional[Dict[str, Any]] = None) -> str:
        """Record gaming experience for learning"""
        experience_id = f"exp_{int(time.time() * 1000000)}"
        
        # Determine experience type
        experience_type = self._classify_experience(reward, outcome)
        
        # Create experience record
        experience = Experience(
            experience_id=experience_id,
            timestamp=time.time(),
            game_state=game_state.copy(),
            action_taken=action.copy(),
            outcome=outcome.copy(),
            reward=reward,
            experience_type=experience_type,
            context=context.copy() if context else {}
        )
        
        with self.learning_lock:
            # Add to main buffer
            self.experience_buffer.append(experience)
            
            # Add to priority buffer if important
            if experience_type in [ExperienceType.SUCCESS, ExperienceType.CRITICAL]:
                self.priority_buffer.append(experience)
            
            # Update metrics
            self.metrics.experiences_collected += 1
            self._update_performance_metrics(reward)
        
        self.logger.debug(f"📝 Experience recorded: {experience_type.value} (reward: {reward:.3f})")
        return experience_id
    
    def _classify_experience(self, reward: float, outcome: Dict[str, Any]) -> ExperienceType:
        """Classify experience based on reward and outcome"""
        if reward > 0.8:
            return ExperienceType.SUCCESS
        elif reward < -0.5:
            return ExperienceType.FAILURE
        elif outcome.get("critical", False):
            return ExperienceType.CRITICAL
        else:
            return ExperienceType.NEUTRAL
    
    def _update_performance_metrics(self, reward: float):
        """Update performance tracking metrics"""
        # Update average reward
        self.metrics.average_reward = (
            (self.metrics.average_reward * (self.metrics.experiences_collected - 1) + reward) /
            self.metrics.experiences_collected
        )
        
        # Track performance history
        self.performance_history.append(reward)
        
        # Calculate improvement
        if len(self.performance_history) >= 100:
            recent_performance = np.mean(list(self.performance_history)[-50:])
            older_performance = np.mean(list(self.performance_history)[-100:-50])
            
            if older_performance != 0:
                improvement = (recent_performance - older_performance) / abs(older_performance)
                self.metrics.performance_improvement = improvement
    
    def learn_from_experiences(self, batch_size: int = 32) -> Dict[str, float]:
        """Learn from collected experiences"""
        if len(self.experience_buffer) < batch_size:
            return {"error": "insufficient_data"}
        
        try:
            with self.learning_lock:
                # Sample experiences for learning
                experiences = self._sample_experiences(batch_size)
                
                # Extract features and targets
                features, targets = self._prepare_training_data(experiences)
                
                # Train models
                learning_results = {}
                
                if SKLEARN_AVAILABLE and len(features) > 0:
                    # Train value function
                    value_loss = self._train_value_function(features, targets)
                    learning_results['value_loss'] = value_loss
                    
                    # Train policy network
                    policy_loss = self._train_policy_network(features, targets)
                    learning_results['policy_loss'] = policy_loss
                
                # Update strategy patterns
                strategy_updates = self._update_strategy_patterns(experiences)
                learning_results['strategies_updated'] = strategy_updates
                
                # Adapt learning parameters
                self._adapt_learning_parameters()
                
                return learning_results
                
        except Exception as e:
            self.logger.error(f"❌ Learning failed: {e}")
            return {"error": str(e)}
    
    def _sample_experiences(self, batch_size: int) -> List[Experience]:
        """Sample experiences for training"""
        experiences = []
        
        # Prioritized sampling
        priority_samples = min(batch_size // 3, len(self.priority_buffer))
        if priority_samples > 0:
            priority_indices = np.random.choice(len(self.priority_buffer), priority_samples, replace=False)
            experiences.extend([self.priority_buffer[i] for i in priority_indices])
        
        # Random sampling from main buffer
        remaining_samples = batch_size - len(experiences)
        if remaining_samples > 0 and len(self.experience_buffer) > 0:
            random_indices = np.random.choice(len(self.experience_buffer), 
                                            min(remaining_samples, len(self.experience_buffer)), 
                                            replace=False)
            experiences.extend([self.experience_buffer[i] for i in random_indices])
        
        return experiences
    
    def _prepare_training_data(self, experiences: List[Experience]) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
        """Prepare training data from experiences"""
        features = []
        rewards = []
        
        for exp in experiences:
            # Extract state features
            state_features = self._extract_state_features(exp.game_state)
            action_features = self._extract_action_features(exp.action_taken)
            
            # Combine features
            combined_features = np.concatenate([state_features, action_features])
            features.append(combined_features)
            rewards.append(exp.reward)
        
        if not features:
            return np.array([]), {}
        
        features_array = np.array(features)
        targets = {
            'rewards': np.array(rewards),
            'values': np.array(rewards)  # Simplified value targets
        }
        
        return features_array, targets
    
    def _extract_state_features(self, game_state: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from game state"""
        features = []
        
        # Extract numerical values
        for key, value in game_state.items():
            if isinstance(value, (int, float)):
                features.append(float(value))
            elif isinstance(value, bool):
                features.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                # Simple string encoding
                features.append(float(hash(value) % 1000) / 1000.0)
        
        # Ensure fixed size
        while len(features) < 10:
            features.append(0.0)
        
        return np.array(features[:10])  # Limit to 10 features
    
    def _extract_action_features(self, action: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from action"""
        features = []
        
        # Extract action parameters
        for key, value in action.items():
            if isinstance(value, (int, float)):
                features.append(float(value))
            elif isinstance(value, bool):
                features.append(1.0 if value else 0.0)
            elif isinstance(value, str):
                features.append(float(hash(value) % 1000) / 1000.0)
        
        # Ensure fixed size
        while len(features) < 5:
            features.append(0.0)
        
        return np.array(features[:5])  # Limit to 5 features
    
    def _train_value_function(self, features: np.ndarray, targets: Dict[str, np.ndarray]) -> float:
        """Train value function approximator"""
        try:
            if 'value' in self.models and len(features) > 0:
                # Scale features
                if hasattr(self.scalers['state'], 'n_features_in_'):
                    features_scaled = self.scalers['state'].transform(features)
                else:
                    features_scaled = self.scalers['state'].fit_transform(features)
                
                # Train model
                self.models['value'].fit(features_scaled, targets['values'])
                
                # Calculate training loss (simplified)
                predictions = self.models['value'].predict(features_scaled)
                loss = np.mean((predictions - targets['values']) ** 2)
                
                return float(loss)
        except Exception as e:
            self.logger.warning(f"⚠️ Value function training failed: {e}")
        
        return 0.0
    
    def _train_policy_network(self, features: np.ndarray, targets: Dict[str, np.ndarray]) -> float:
        """Train policy network"""
        try:
            if 'policy' in self.models and len(features) > 0:
                # Use rewards as policy targets (simplified)
                policy_targets = targets['rewards']
                
                # Scale features
                if hasattr(self.scalers['action'], 'n_features_in_'):
                    features_scaled = self.scalers['action'].transform(features)
                else:
                    features_scaled = self.scalers['action'].fit_transform(features)
                
                # Train model
                self.models['policy'].fit(features_scaled, policy_targets)
                
                # Calculate training loss
                predictions = self.models['policy'].predict(features_scaled)
                loss = np.mean((predictions - policy_targets) ** 2)
                
                return float(loss)
        except Exception as e:
            self.logger.warning(f"⚠️ Policy network training failed: {e}")
        
        return 0.0
    
    def _update_strategy_patterns(self, experiences: List[Experience]) -> int:
        """Update learned strategy patterns"""
        strategies_updated = 0
        
        try:
            for exp in experiences:
                # Extract strategy pattern
                pattern_key = self._extract_pattern_key(exp.game_state, exp.action_taken)
                
                if pattern_key not in self.learned_strategies:
                    # Create new strategy pattern
                    self.learned_strategies[pattern_key] = StrategyPattern(
                        pattern_id=pattern_key,
                        conditions=self._extract_conditions(exp.game_state),
                        actions=[exp.action_taken],
                        success_rate=1.0 if exp.reward > 0 else 0.0,
                        usage_count=1,
                        last_updated=time.time()
                    )
                    strategies_updated += 1
                else:
                    # Update existing pattern
                    pattern = self.learned_strategies[pattern_key]
                    pattern.usage_count += 1
                    
                    # Update success rate
                    success = 1.0 if exp.reward > 0 else 0.0
                    pattern.success_rate = (
                        (pattern.success_rate * (pattern.usage_count - 1) + success) /
                        pattern.usage_count
                    )
                    
                    pattern.last_updated = time.time()
                    strategies_updated += 1
            
            self.metrics.strategies_learned = len(self.learned_strategies)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Strategy pattern update failed: {e}")
        
        return strategies_updated
    
    def _extract_pattern_key(self, game_state: Dict[str, Any], action: Dict[str, Any]) -> str:
        """Extract pattern key from state and action"""
        # Simplified pattern key generation
        state_key = "_".join([f"{k}:{v}" for k, v in sorted(game_state.items())[:3]])
        action_key = "_".join([f"{k}:{v}" for k, v in sorted(action.items())[:2]])
        return f"{state_key}|{action_key}"
    
    def _extract_conditions(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """Extract conditions from game state"""
        # Simplified condition extraction
        conditions = {}
        for key, value in game_state.items():
            if isinstance(value, (int, float, bool, str)):
                conditions[key] = value
        return conditions
    
    def _adapt_learning_parameters(self):
        """Adapt learning parameters based on performance"""
        # Decay exploration rate
        self.metrics.exploration_rate = max(
            self.min_exploration,
            self.metrics.exploration_rate * self.exploration_decay
        )
        
        # Adjust learning rate based on improvement
        if self.metrics.performance_improvement > self.adaptation_threshold:
            # Good improvement - maintain learning rate
            pass
        elif self.metrics.performance_improvement < -self.adaptation_threshold:
            # Poor performance - increase learning rate
            self.metrics.learning_rate = min(0.1, self.metrics.learning_rate * 1.1)
        else:
            # Stable performance - slightly decrease learning rate
            self.metrics.learning_rate = max(0.001, self.metrics.learning_rate * 0.99)
    
    def suggest_action(self, game_state: Dict[str, Any], 
                      available_actions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
        """Suggest action based on learned patterns"""
        try:
            # Check for learned strategy patterns
            best_action, pattern_confidence = self._check_strategy_patterns(game_state, available_actions)
            
            if pattern_confidence > 0.7:
                return best_action, pattern_confidence
            
            # Use ML models if available
            if SKLEARN_AVAILABLE and 'policy' in self.models:
                ml_action, ml_confidence = self._ml_action_suggestion(game_state, available_actions)
                if ml_confidence > pattern_confidence:
                    return ml_action, ml_confidence
            
            # Exploration vs exploitation
            if np.random.random() < self.metrics.exploration_rate:
                # Explore: random action
                random_action = np.random.choice(available_actions) if available_actions else {}
                return random_action, 0.1
            else:
                # Exploit: best known action
                return best_action if best_action else {}, pattern_confidence
                
        except Exception as e:
            self.logger.error(f"❌ Action suggestion failed: {e}")
            return {}, 0.0
    
    def _check_strategy_patterns(self, game_state: Dict[str, Any], 
                               available_actions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
        """Check learned strategy patterns for matching conditions"""
        best_action = {}
        best_confidence = 0.0
        
        try:
            for pattern in self.learned_strategies.values():
                # Check if conditions match
                match_score = self._calculate_condition_match(game_state, pattern.conditions)
                
                if match_score > 0.5:  # Threshold for pattern matching
                    # Calculate confidence based on success rate and usage
                    confidence = pattern.success_rate * min(1.0, pattern.usage_count / 10.0)
                    
                    if confidence > best_confidence:
                        # Find best matching action
                        for action in pattern.actions:
                            if action in available_actions or not available_actions:
                                best_action = action
                                best_confidence = confidence
                                break
        
        except Exception as e:
            self.logger.warning(f"⚠️ Pattern matching failed: {e}")
        
        return best_action, best_confidence
    
    def _calculate_condition_match(self, game_state: Dict[str, Any], 
                                 conditions: Dict[str, Any]) -> float:
        """Calculate how well game state matches pattern conditions"""
        if not conditions:
            return 0.0
        
        matches = 0
        total = 0
        
        for key, expected_value in conditions.items():
            if key in game_state:
                actual_value = game_state[key]
                
                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    # Numerical comparison with tolerance
                    tolerance = 0.1 * abs(expected_value) if expected_value != 0 else 0.1
                    if abs(actual_value - expected_value) <= tolerance:
                        matches += 1
                elif expected_value == actual_value:
                    # Exact match
                    matches += 1
                
                total += 1
        
        return matches / total if total > 0 else 0.0
    
    def _ml_action_suggestion(self, game_state: Dict[str, Any], 
                            available_actions: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
        """Suggest action using ML models"""
        try:
            if not available_actions:
                return {}, 0.0
            
            best_action = {}
            best_value = float('-inf')
            
            # Evaluate each available action
            for action in available_actions:
                state_features = self._extract_state_features(game_state)
                action_features = self._extract_action_features(action)
                combined_features = np.concatenate([state_features, action_features]).reshape(1, -1)
                
                # Scale features
                if hasattr(self.scalers['state'], 'n_features_in_'):
                    features_scaled = self.scalers['state'].transform(combined_features)
                    
                    # Predict value
                    predicted_value = self.models['value'].predict(features_scaled)[0]
                    
                    if predicted_value > best_value:
                        best_value = predicted_value
                        best_action = action
            
            # Convert value to confidence
            confidence = min(1.0, max(0.0, (best_value + 1.0) / 2.0))  # Normalize to [0,1]
            
            return best_action, confidence
            
        except Exception as e:
            self.logger.warning(f"⚠️ ML action suggestion failed: {e}")
            return {}, 0.0
    
    def start_background_learning(self):
        """Start background learning thread"""
        if self.learning_active:
            return
        
        self.learning_active = True
        self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
        self.learning_thread.start()
        self.logger.info("🔄 Background learning started")
    
    def stop_background_learning(self):
        """Stop background learning"""
        self.learning_active = False
        if self.learning_thread:
            self.learning_thread.join(timeout=1.0)
        self.logger.info("🛑 Background learning stopped")
    
    def _learning_loop(self):
        """Background learning loop"""
        while self.learning_active:
            try:
                if len(self.experience_buffer) >= 32:
                    # Perform learning
                    results = self.learn_from_experiences(32)
                    
                    if 'error' not in results:
                        self.logger.debug(f"📚 Background learning: {results}")
                
                time.sleep(5.0)  # Learn every 5 seconds
                
            except Exception as e:
                self.logger.error(f"❌ Background learning error: {e}")
                time.sleep(10.0)
    
    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get learning performance metrics"""
        return {
            "experiences_collected": self.metrics.experiences_collected,
            "strategies_learned": self.metrics.strategies_learned,
            "performance_improvement": self.metrics.performance_improvement,
            "learning_rate": self.metrics.learning_rate,
            "exploration_rate": self.metrics.exploration_rate,
            "average_reward": self.metrics.average_reward,
            "memory_usage": len(self.experience_buffer),
            "priority_experiences": len(self.priority_buffer),
            "learning_active": self.learning_active
        }
    
    def save_learned_knowledge(self, filepath: str) -> bool:
        """Save learned knowledge to file"""
        try:
            knowledge = {
                "strategies": {k: asdict(v) for k, v in self.learned_strategies.items()},
                "metrics": asdict(self.metrics),
                "performance_history": list(self.performance_history)
            }
            
            with open(filepath, 'w') as f:
                json.dump(knowledge, f, indent=2)
            
            self.logger.info(f"💾 Knowledge saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge save failed: {e}")
            return False
    
    def load_learned_knowledge(self, filepath: str) -> bool:
        """Load learned knowledge from file"""
        try:
            with open(filepath, 'r') as f:
                knowledge = json.load(f)
            
            # Restore strategies
            for k, v in knowledge.get("strategies", {}).items():
                self.learned_strategies[k] = StrategyPattern(**v)
            
            # Restore performance history
            self.performance_history.extend(knowledge.get("performance_history", []))
            
            self.logger.info(f"📚 Knowledge loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Knowledge load failed: {e}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("📚 Adaptive Learning System - Sprint 3 Test")
    print("=" * 60)
    
    # Create learning system
    learning_system = AdaptiveLearningSystem(memory_size=1000, learning_rate=0.01)
    
    # Test experience recording
    print("\n📝 Testing experience recording...")
    
    for i in range(10):
        game_state = {
            "health": np.random.randint(50, 100),
            "ammo": np.random.randint(10, 30),
            "enemy_distance": np.random.uniform(10, 100),
            "in_cover": np.random.choice([True, False])
        }
        
        action = {
            "action_type": np.random.choice(["move", "shoot", "reload"]),
            "direction": np.random.uniform(0, 360),
            "intensity": np.random.uniform(0.5, 1.0)
        }
        
        outcome = {
            "success": np.random.choice([True, False]),
            "damage_dealt": np.random.uniform(0, 50),
            "damage_taken": np.random.uniform(0, 20)
        }
        
        reward = np.random.uniform(-1.0, 1.0)
        
        exp_id = learning_system.record_experience(game_state, action, outcome, reward)
        print(f"   Experience {i+1}: {exp_id[:8]}... (reward: {reward:.3f})")
    
    # Test learning
    print("\n🧠 Testing learning from experiences...")
    results = learning_system.learn_from_experiences(8)
    print(f"Learning results: {results}")
    
    # Test action suggestion
    print("\n💡 Testing action suggestion...")
    test_state = {
        "health": 75,
        "ammo": 20,
        "enemy_distance": 50.0,
        "in_cover": True
    }
    
    available_actions = [
        {"action_type": "shoot", "direction": 45, "intensity": 0.8},
        {"action_type": "move", "direction": 90, "intensity": 0.6},
        {"action_type": "reload", "direction": 0, "intensity": 1.0}
    ]
    
    suggested_action, confidence = learning_system.suggest_action(test_state, available_actions)
    print(f"Suggested action: {suggested_action}")
    print(f"Confidence: {confidence:.3f}")
    
    # Get learning metrics
    metrics = learning_system.get_learning_metrics()
    print(f"\n📊 Learning Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 3 - Task 3.3 test completed!")
    print("🎯 Target: Real-time learning, strategy adaptation, measurable improvement")
    print(f"📈 Current: {metrics['experiences_collected']} experiences, {metrics['strategies_learned']} strategies learned")
