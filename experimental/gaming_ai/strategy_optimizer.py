#!/usr/bin/env python3
"""
🎯 Strategy Optimization System - Gaming AI

Multi-objective strategy optimization and dynamic selection system.

Sprint 3 - Task 3.5: Strategy Optimization System
- Multi-objective strategy optimization
- Game-specific strategy adaptation
- Real-time strategy switching
- Performance improvement measurement

Author: Nexus - Quantum AI Architect
Sprint: 3.5 - AI Intelligence & Decision Making
"""

import time
import numpy as np
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import deque
import warnings

# Optimization imports
try:
    from scipy.optimize import minimize, differential_evolution
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    warnings.warn("🔬 SciPy not available - using simplified optimization", ImportWarning)

class StrategyType(Enum):
    """Strategy type enumeration"""
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    BALANCED = "balanced"
    OPPORTUNISTIC = "opportunistic"
    CONSERVATIVE = "conservative"

class OptimizationObjective(Enum):
    """Optimization objective enumeration"""
    MAXIMIZE_REWARD = "maximize_reward"
    MINIMIZE_RISK = "minimize_risk"
    MAXIMIZE_EFFICIENCY = "maximize_efficiency"
    MINIMIZE_TIME = "minimize_time"
    MAXIMIZE_SURVIVAL = "maximize_survival"

@dataclass
class Strategy:
    """Strategy definition"""
    strategy_id: str
    strategy_type: StrategyType
    parameters: Dict[str, float]
    objectives: Dict[OptimizationObjective, float]
    performance_history: List[float] = field(default_factory=list)
    usage_count: int = 0
    last_updated: float = 0.0

@dataclass
class OptimizationResult:
    """Strategy optimization result"""
    optimization_id: str
    optimized_strategy: Strategy
    improvement: float
    pareto_front: List[Strategy]
    convergence_time: float
    confidence: float

@dataclass
class StrategyMetrics:
    """Strategy optimization metrics"""
    strategies_optimized: int = 0
    average_improvement: float = 0.0
    optimization_time: float = 0.0
    strategy_switches: int = 0
    pareto_solutions: int = 0

class StrategyOptimizer:
    """
    Multi-Objective Strategy Optimization System
    
    Features:
    - Multi-objective strategy optimization
    - Pareto-optimal solution finding
    - Dynamic strategy selection
    - Real-time strategy adaptation
    - Performance improvement measurement
    """
    
    def __init__(self, max_strategies: int = 50):
        self.max_strategies = max_strategies
        self.logger = logging.getLogger("StrategyOptimizer")
        
        # Strategy management
        self.strategies = {}
        self.active_strategy = None
        self.strategy_templates = {}
        
        # Optimization configuration
        self.objectives = [
            OptimizationObjective.MAXIMIZE_REWARD,
            OptimizationObjective.MINIMIZE_RISK,
            OptimizationObjective.MAXIMIZE_EFFICIENCY
        ]
        
        # Performance tracking
        self.metrics = StrategyMetrics()
        self.performance_history = deque(maxlen=1000)
        
        # Threading
        self.optimization_lock = threading.RLock()
        
        # Pareto front management
        self.pareto_front = []
        self.pareto_archive = deque(maxlen=200)
        
        # Strategy selection
        self.selection_criteria = {
            'performance_weight': 0.4,
            'risk_weight': 0.3,
            'efficiency_weight': 0.2,
            'novelty_weight': 0.1
        }
        
        # Initialize strategy templates
        self._initialize_strategy_templates()
        
        self.logger.info(f"🎯 Strategy Optimizer initialized (max strategies: {max_strategies})")
    
    def _initialize_strategy_templates(self):
        """Initialize strategy templates for different game scenarios"""
        self.strategy_templates = {
            StrategyType.AGGRESSIVE: {
                'attack_frequency': 0.8,
                'risk_tolerance': 0.7,
                'resource_usage': 0.9,
                'movement_speed': 0.8,
                'decision_speed': 0.9
            },
            
            StrategyType.DEFENSIVE: {
                'attack_frequency': 0.3,
                'risk_tolerance': 0.2,
                'resource_usage': 0.4,
                'movement_speed': 0.4,
                'decision_speed': 0.6
            },
            
            StrategyType.BALANCED: {
                'attack_frequency': 0.5,
                'risk_tolerance': 0.5,
                'resource_usage': 0.6,
                'movement_speed': 0.6,
                'decision_speed': 0.7
            },
            
            StrategyType.OPPORTUNISTIC: {
                'attack_frequency': 0.6,
                'risk_tolerance': 0.6,
                'resource_usage': 0.7,
                'movement_speed': 0.7,
                'decision_speed': 0.8
            },
            
            StrategyType.CONSERVATIVE: {
                'attack_frequency': 0.2,
                'risk_tolerance': 0.1,
                'resource_usage': 0.3,
                'movement_speed': 0.3,
                'decision_speed': 0.5
            }
        }
    
    def create_strategy(self, strategy_type: StrategyType, 
                       custom_parameters: Optional[Dict[str, float]] = None) -> Strategy:
        """Create new strategy from template"""
        strategy_id = f"strategy_{int(time.time() * 1000000)}"
        
        # Start with template parameters
        parameters = self.strategy_templates[strategy_type].copy()
        
        # Apply custom parameters
        if custom_parameters:
            parameters.update(custom_parameters)
        
        # Initialize objectives
        objectives = {obj: 0.0 for obj in self.objectives}
        
        strategy = Strategy(
            strategy_id=strategy_id,
            strategy_type=strategy_type,
            parameters=parameters,
            objectives=objectives,
            last_updated=time.time()
        )
        
        self.strategies[strategy_id] = strategy
        
        self.logger.debug(f"🎯 Strategy created: {strategy_type.value} ({strategy_id[:8]}...)")
        
        return strategy
    
    def optimize_strategy(self, base_strategy: Strategy, 
                         performance_data: List[Dict[str, Any]],
                         context: Dict[str, Any]) -> OptimizationResult:
        """Optimize strategy using multi-objective optimization"""
        optimization_id = f"opt_{int(time.time() * 1000000)}"
        start_time = time.time()
        
        try:
            with self.optimization_lock:
                # Prepare optimization problem
                bounds = self._get_parameter_bounds()
                initial_params = list(base_strategy.parameters.values())
                
                if SCIPY_AVAILABLE and len(performance_data) > 5:
                    # Use scipy optimization
                    optimized_params = self._scipy_optimization(initial_params, bounds, performance_data, context)
                else:
                    # Use simplified optimization
                    optimized_params = self._simple_optimization(initial_params, performance_data, context)
                
                # Create optimized strategy
                optimized_strategy = self._create_optimized_strategy(base_strategy, optimized_params)
                
                # Calculate improvement
                improvement = self._calculate_improvement(base_strategy, optimized_strategy, performance_data)
                
                # Update Pareto front
                self._update_pareto_front(optimized_strategy)
                
                # Calculate convergence time
                convergence_time = time.time() - start_time
                
                # Calculate confidence
                confidence = min(1.0, len(performance_data) / 20.0)
                
                # Update metrics
                self.metrics.strategies_optimized += 1
                self.metrics.average_improvement = (
                    (self.metrics.average_improvement * (self.metrics.strategies_optimized - 1) + improvement) /
                    self.metrics.strategies_optimized
                )
                self.metrics.optimization_time = (
                    (self.metrics.optimization_time * (self.metrics.strategies_optimized - 1) + convergence_time) /
                    self.metrics.strategies_optimized
                )
                
                result = OptimizationResult(
                    optimization_id=optimization_id,
                    optimized_strategy=optimized_strategy,
                    improvement=improvement,
                    pareto_front=self.pareto_front.copy(),
                    convergence_time=convergence_time,
                    confidence=confidence
                )
                
                self.logger.info(f"🎯 Strategy optimized: {improvement:.1%} improvement")
                
                return result
                
        except Exception as e:
            self.logger.error(f"❌ Strategy optimization failed: {e}")
            return OptimizationResult(
                optimization_id=optimization_id,
                optimized_strategy=base_strategy,
                improvement=0.0,
                pareto_front=[],
                convergence_time=time.time() - start_time,
                confidence=0.0
            )
    
    def _get_parameter_bounds(self) -> List[Tuple[float, float]]:
        """Get parameter bounds for optimization"""
        return [
            (0.0, 1.0),  # attack_frequency
            (0.0, 1.0),  # risk_tolerance
            (0.0, 1.0),  # resource_usage
            (0.0, 1.0),  # movement_speed
            (0.0, 1.0)   # decision_speed
        ]
    
    def _scipy_optimization(self, initial_params: List[float], bounds: List[Tuple[float, float]],
                          performance_data: List[Dict[str, Any]], context: Dict[str, Any]) -> List[float]:
        """Perform optimization using scipy"""
        try:
            # Define objective function
            def objective(params):
                return -self._evaluate_strategy_performance(params, performance_data, context)
            
            # Use differential evolution for global optimization
            result = differential_evolution(
                objective,
                bounds,
                seed=42,
                maxiter=50,
                popsize=10
            )
            
            return result.x.tolist()
            
        except Exception as e:
            self.logger.warning(f"⚠️ SciPy optimization failed: {e}")
            return initial_params
    
    def _simple_optimization(self, initial_params: List[float], 
                           performance_data: List[Dict[str, Any]], 
                           context: Dict[str, Any]) -> List[float]:
        """Simple optimization using random search"""
        best_params = initial_params.copy()
        best_score = self._evaluate_strategy_performance(best_params, performance_data, context)
        
        # Random search optimization
        for _ in range(100):
            # Generate random perturbation
            perturbation = np.random.normal(0, 0.1, len(initial_params))
            candidate_params = np.clip(np.array(initial_params) + perturbation, 0.0, 1.0).tolist()
            
            # Evaluate candidate
            score = self._evaluate_strategy_performance(candidate_params, performance_data, context)
            
            if score > best_score:
                best_score = score
                best_params = candidate_params
        
        return best_params
    
    def _evaluate_strategy_performance(self, params: List[float], 
                                     performance_data: List[Dict[str, Any]], 
                                     context: Dict[str, Any]) -> float:
        """Evaluate strategy performance given parameters"""
        if not performance_data:
            return 0.0
        
        # Convert params to strategy parameters
        param_names = ['attack_frequency', 'risk_tolerance', 'resource_usage', 'movement_speed', 'decision_speed']
        strategy_params = dict(zip(param_names, params))
        
        # Calculate multi-objective score
        total_score = 0.0
        
        for data_point in performance_data:
            # Reward objective
            reward = data_point.get('reward', 0.0)
            reward_score = reward * strategy_params['attack_frequency']
            
            # Risk objective (minimize)
            risk = data_point.get('risk', 0.5)
            risk_score = (1.0 - risk) * (1.0 - strategy_params['risk_tolerance'])
            
            # Efficiency objective
            efficiency = data_point.get('efficiency', 0.5)
            efficiency_score = efficiency * strategy_params['resource_usage']
            
            # Combine objectives
            combined_score = (reward_score * 0.4 + risk_score * 0.3 + efficiency_score * 0.3)
            total_score += combined_score
        
        return total_score / len(performance_data)
    
    def _create_optimized_strategy(self, base_strategy: Strategy, optimized_params: List[float]) -> Strategy:
        """Create optimized strategy from parameters"""
        param_names = ['attack_frequency', 'risk_tolerance', 'resource_usage', 'movement_speed', 'decision_speed']
        optimized_parameters = dict(zip(param_names, optimized_params))
        
        strategy_id = f"opt_{base_strategy.strategy_id}"
        
        optimized_strategy = Strategy(
            strategy_id=strategy_id,
            strategy_type=base_strategy.strategy_type,
            parameters=optimized_parameters,
            objectives=base_strategy.objectives.copy(),
            last_updated=time.time()
        )
        
        # Store optimized strategy
        self.strategies[strategy_id] = optimized_strategy
        
        return optimized_strategy
    
    def _calculate_improvement(self, base_strategy: Strategy, optimized_strategy: Strategy,
                             performance_data: List[Dict[str, Any]]) -> float:
        """Calculate improvement percentage"""
        try:
            base_params = list(base_strategy.parameters.values())
            opt_params = list(optimized_strategy.parameters.values())
            
            base_score = self._evaluate_strategy_performance(base_params, performance_data, {})
            opt_score = self._evaluate_strategy_performance(opt_params, performance_data, {})
            
            if base_score > 0:
                improvement = (opt_score - base_score) / base_score
            else:
                improvement = opt_score
            
            return improvement
            
        except Exception as e:
            self.logger.warning(f"⚠️ Improvement calculation failed: {e}")
            return 0.0
    
    def _update_pareto_front(self, strategy: Strategy):
        """Update Pareto front with new strategy"""
        try:
            # Calculate objective values for strategy
            objectives = self._calculate_objective_values(strategy)
            strategy.objectives = objectives
            
            # Check if strategy is Pareto optimal
            is_pareto_optimal = True
            strategies_to_remove = []
            
            for existing_strategy in self.pareto_front:
                if self._dominates(existing_strategy.objectives, objectives):
                    # Existing strategy dominates new strategy
                    is_pareto_optimal = False
                    break
                elif self._dominates(objectives, existing_strategy.objectives):
                    # New strategy dominates existing strategy
                    strategies_to_remove.append(existing_strategy)
            
            # Remove dominated strategies
            for strategy_to_remove in strategies_to_remove:
                self.pareto_front.remove(strategy_to_remove)
            
            # Add new strategy if Pareto optimal
            if is_pareto_optimal:
                self.pareto_front.append(strategy)
                self.metrics.pareto_solutions = len(self.pareto_front)
            
            # Limit Pareto front size
            if len(self.pareto_front) > 20:
                # Keep most diverse strategies
                self.pareto_front = self._select_diverse_strategies(self.pareto_front, 20)
            
        except Exception as e:
            self.logger.warning(f"⚠️ Pareto front update failed: {e}")
    
    def _calculate_objective_values(self, strategy: Strategy) -> Dict[OptimizationObjective, float]:
        """Calculate objective values for strategy"""
        objectives = {}
        
        # Use performance history if available
        if strategy.performance_history:
            avg_performance = np.mean(strategy.performance_history)
            
            objectives[OptimizationObjective.MAXIMIZE_REWARD] = avg_performance
            objectives[OptimizationObjective.MINIMIZE_RISK] = 1.0 - strategy.parameters.get('risk_tolerance', 0.5)
            objectives[OptimizationObjective.MAXIMIZE_EFFICIENCY] = strategy.parameters.get('resource_usage', 0.5)
        else:
            # Use parameter-based estimation
            objectives[OptimizationObjective.MAXIMIZE_REWARD] = strategy.parameters.get('attack_frequency', 0.5)
            objectives[OptimizationObjective.MINIMIZE_RISK] = 1.0 - strategy.parameters.get('risk_tolerance', 0.5)
            objectives[OptimizationObjective.MAXIMIZE_EFFICIENCY] = strategy.parameters.get('resource_usage', 0.5)
        
        return objectives
    
    def _dominates(self, obj1: Dict[OptimizationObjective, float], 
                  obj2: Dict[OptimizationObjective, float]) -> bool:
        """Check if obj1 dominates obj2 (Pareto dominance)"""
        better_in_all = True
        better_in_at_least_one = False
        
        for objective in self.objectives:
            val1 = obj1.get(objective, 0.0)
            val2 = obj2.get(objective, 0.0)
            
            if objective == OptimizationObjective.MINIMIZE_RISK:
                # For minimization objectives, smaller is better
                if val1 > val2:
                    better_in_all = False
                elif val1 < val2:
                    better_in_at_least_one = True
            else:
                # For maximization objectives, larger is better
                if val1 < val2:
                    better_in_all = False
                elif val1 > val2:
                    better_in_at_least_one = True
        
        return better_in_all and better_in_at_least_one
    
    def _select_diverse_strategies(self, strategies: List[Strategy], max_count: int) -> List[Strategy]:
        """Select diverse strategies from Pareto front"""
        if len(strategies) <= max_count:
            return strategies
        
        # Simple diversity selection based on parameter distance
        selected = [strategies[0]]  # Start with first strategy
        
        for _ in range(max_count - 1):
            best_candidate = None
            max_min_distance = 0.0
            
            for candidate in strategies:
                if candidate in selected:
                    continue
                
                # Calculate minimum distance to selected strategies
                min_distance = float('inf')
                for selected_strategy in selected:
                    distance = self._calculate_strategy_distance(candidate, selected_strategy)
                    min_distance = min(min_distance, distance)
                
                if min_distance > max_min_distance:
                    max_min_distance = min_distance
                    best_candidate = candidate
            
            if best_candidate:
                selected.append(best_candidate)
        
        return selected
    
    def _calculate_strategy_distance(self, strategy1: Strategy, strategy2: Strategy) -> float:
        """Calculate distance between two strategies"""
        distance = 0.0
        
        for param_name in strategy1.parameters:
            if param_name in strategy2.parameters:
                diff = strategy1.parameters[param_name] - strategy2.parameters[param_name]
                distance += diff ** 2
        
        return np.sqrt(distance)
    
    def select_optimal_strategy(self, context: Dict[str, Any]) -> Optional[Strategy]:
        """Select optimal strategy based on current context"""
        try:
            if not self.strategies:
                return None
            
            best_strategy = None
            best_score = float('-inf')
            
            # Evaluate all strategies
            for strategy in self.strategies.values():
                score = self._evaluate_strategy_for_context(strategy, context)
                
                if score > best_score:
                    best_score = score
                    best_strategy = strategy
            
            # Switch strategy if different from current
            if best_strategy != self.active_strategy:
                self.active_strategy = best_strategy
                self.metrics.strategy_switches += 1
                self.logger.info(f"🔄 Strategy switched to: {best_strategy.strategy_type.value}")
            
            return best_strategy
            
        except Exception as e:
            self.logger.error(f"❌ Strategy selection failed: {e}")
            return None
    
    def _evaluate_strategy_for_context(self, strategy: Strategy, context: Dict[str, Any]) -> float:
        """Evaluate strategy fitness for current context"""
        score = 0.0
        
        # Performance weight
        if strategy.performance_history:
            avg_performance = np.mean(strategy.performance_history[-10:])  # Recent performance
            score += avg_performance * self.selection_criteria['performance_weight']
        
        # Risk weight
        context_risk = context.get('risk_level', 0.5)
        strategy_risk_tolerance = strategy.parameters.get('risk_tolerance', 0.5)
        risk_match = 1.0 - abs(context_risk - strategy_risk_tolerance)
        score += risk_match * self.selection_criteria['risk_weight']
        
        # Efficiency weight
        context_urgency = context.get('urgency', 0.5)
        strategy_speed = strategy.parameters.get('decision_speed', 0.5)
        efficiency_match = 1.0 - abs(context_urgency - strategy_speed)
        score += efficiency_match * self.selection_criteria['efficiency_weight']
        
        # Novelty weight (prefer less used strategies for exploration)
        novelty = 1.0 / (1.0 + strategy.usage_count)
        score += novelty * self.selection_criteria['novelty_weight']
        
        return score
    
    def update_strategy_performance(self, strategy_id: str, performance: float):
        """Update strategy performance"""
        if strategy_id in self.strategies:
            strategy = self.strategies[strategy_id]
            strategy.performance_history.append(performance)
            strategy.usage_count += 1
            strategy.last_updated = time.time()
            
            # Limit performance history
            if len(strategy.performance_history) > 100:
                strategy.performance_history = strategy.performance_history[-100:]
            
            # Update Pareto front
            self._update_pareto_front(strategy)
    
    def get_strategy_metrics(self) -> Dict[str, Any]:
        """Get strategy optimization metrics"""
        return {
            "strategies_optimized": self.metrics.strategies_optimized,
            "average_improvement": self.metrics.average_improvement,
            "optimization_time": self.metrics.optimization_time,
            "strategy_switches": self.metrics.strategy_switches,
            "pareto_solutions": self.metrics.pareto_solutions,
            "total_strategies": len(self.strategies),
            "active_strategy": self.active_strategy.strategy_type.value if self.active_strategy else None,
            "pareto_front_size": len(self.pareto_front)
        }
    
    def get_pareto_front(self) -> List[Dict[str, Any]]:
        """Get current Pareto front strategies"""
        pareto_data = []
        
        for strategy in self.pareto_front:
            pareto_data.append({
                "strategy_id": strategy.strategy_id,
                "strategy_type": strategy.strategy_type.value,
                "parameters": strategy.parameters,
                "objectives": {obj.value: val for obj, val in strategy.objectives.items()},
                "usage_count": strategy.usage_count,
                "avg_performance": np.mean(strategy.performance_history) if strategy.performance_history else 0.0
            })
        
        return pareto_data

# Example usage and testing
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🎯 Strategy Optimization System - Sprint 3 Test")
    print("=" * 60)
    
    # Create strategy optimizer
    optimizer = StrategyOptimizer(max_strategies=20)
    
    # Test strategy creation
    print("\n🎯 Testing strategy creation...")
    
    strategies = []
    for strategy_type in StrategyType:
        strategy = optimizer.create_strategy(strategy_type)
        strategies.append(strategy)
        print(f"   {strategy_type.value}: {strategy.strategy_id[:8]}...")
    
    # Test strategy optimization
    print("\n🔧 Testing strategy optimization...")
    
    # Generate performance data
    performance_data = []
    for _ in range(20):
        performance_data.append({
            'reward': np.random.uniform(0.0, 1.0),
            'risk': np.random.uniform(0.0, 1.0),
            'efficiency': np.random.uniform(0.0, 1.0)
        })
    
    # Optimize a strategy
    base_strategy = strategies[0]
    context = {'urgency': 0.7, 'risk_level': 0.4}
    
    result = optimizer.optimize_strategy(base_strategy, performance_data, context)
    print(f"Optimization ID: {result.optimization_id}")
    print(f"Improvement: {result.improvement:.1%}")
    print(f"Convergence Time: {result.convergence_time:.3f}s")
    print(f"Confidence: {result.confidence:.3f}")
    
    # Test strategy selection
    print("\n🎯 Testing strategy selection...")
    
    # Update some performance data
    for i, strategy in enumerate(strategies[:3]):
        for _ in range(5):
            performance = np.random.uniform(0.3, 0.9)
            optimizer.update_strategy_performance(strategy.strategy_id, performance)
    
    # Select optimal strategy
    optimal_strategy = optimizer.select_optimal_strategy(context)
    if optimal_strategy:
        print(f"Selected Strategy: {optimal_strategy.strategy_type.value}")
        print(f"Parameters: {optimal_strategy.parameters}")
    
    # Get Pareto front
    print("\n📊 Testing Pareto front...")
    pareto_front = optimizer.get_pareto_front()
    print(f"Pareto Front Size: {len(pareto_front)}")
    for i, strategy_data in enumerate(pareto_front[:3]):
        print(f"   Strategy {i+1}: {strategy_data['strategy_type']} (usage: {strategy_data['usage_count']})")
    
    # Get metrics
    metrics = optimizer.get_strategy_metrics()
    print(f"\n📊 Strategy Metrics:")
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.3f}")
        else:
            print(f"   {key}: {value}")
    
    print("\n🎉 Sprint 3 - Task 3.5 test completed!")
    print("🎯 Target: Multi-objective optimization, real-time strategy switching")
    print(f"📈 Current: {metrics['strategies_optimized']} optimized, {metrics['average_improvement']:.1%} avg improvement")
