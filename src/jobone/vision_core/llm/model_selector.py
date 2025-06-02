#!/usr/bin/env python3
"""
Model Selector - Dynamic LLM Model Selection
Sprint 8.2 - Advanced LLM Management and Core "Brain" AI Capabilities
Orion Vision Core - Autonomous AI Operating System

This module provides intelligent model selection based on task requirements,
performance monitoring, and cost optimization for the Orion Vision Core
autonomous AI operating system.

Author: Orion Development Team
Version: 8.2.0
Date: 30 Mayıs 2025
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QObject, pyqtSignal, QTimer

from .llm_api_manager import get_llm_api_manager, ModelCapability, ProviderType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ModelSelector")

class SelectionStrategy(Enum):
    """Model selection strategy enumeration"""
    COST_OPTIMIZED = "cost_optimized"
    PERFORMANCE_OPTIMIZED = "performance_optimized"
    BALANCED = "balanced"
    LOCAL_PREFERRED = "local_preferred"
    FASTEST = "fastest"
    MOST_CAPABLE = "most_capable"

class TaskComplexity(Enum):
    """Task complexity enumeration"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    EXPERT = "expert"

@dataclass
class ModelPerformance:
    """Model performance metrics"""
    model_id: str
    success_rate: float
    average_response_time: float
    average_quality_score: float
    total_requests: int
    last_updated: datetime
    cost_efficiency: float

@dataclass
class TaskRequirements:
    """Task requirements specification"""
    capability: ModelCapability
    complexity: TaskComplexity
    max_tokens: Optional[int]
    max_cost_per_token: Optional[float]
    max_response_time: Optional[float]
    prefer_local: bool
    quality_threshold: float

class ModelSelector(QObject):
    """
    Intelligent model selection system.
    
    Features:
    - Dynamic model selection based on task requirements
    - Performance monitoring and learning
    - Cost optimization strategies
    - Fallback mechanisms
    - A/B testing capabilities
    - Real-time adaptation
    """
    
    # Signals
    model_selected = pyqtSignal(str, dict)  # model_id, selection_reason
    performance_updated = pyqtSignal(str, dict)  # model_id, performance_data
    strategy_changed = pyqtSignal(str)  # new_strategy
    
    def __init__(self):
        """Initialize Model Selector"""
        super().__init__()
        
        # LLM API Manager reference
        self.llm_manager = get_llm_api_manager()
        
        # Selection strategy
        self.current_strategy = SelectionStrategy.BALANCED
        self.strategy_weights = {
            SelectionStrategy.COST_OPTIMIZED: {'cost': 0.7, 'performance': 0.2, 'quality': 0.1},
            SelectionStrategy.PERFORMANCE_OPTIMIZED: {'cost': 0.1, 'performance': 0.7, 'quality': 0.2},
            SelectionStrategy.BALANCED: {'cost': 0.3, 'performance': 0.4, 'quality': 0.3},
            SelectionStrategy.LOCAL_PREFERRED: {'cost': 0.5, 'performance': 0.3, 'quality': 0.2},
            SelectionStrategy.FASTEST: {'cost': 0.2, 'performance': 0.8, 'quality': 0.0},
            SelectionStrategy.MOST_CAPABLE: {'cost': 0.0, 'performance': 0.3, 'quality': 0.7}
        }
        
        # Performance tracking
        self.model_performance: Dict[str, ModelPerformance] = {}
        self.performance_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Task-model mapping learning
        self.task_model_success: Dict[str, Dict[str, float]] = {}
        self.learning_rate = 0.1
        
        # Fallback configuration
        self.fallback_models = ["gpt-3.5-turbo", "llama2-7b", "mistral-7b"]
        self.max_selection_attempts = 3
        
        # Performance monitoring
        self.monitoring_timer = QTimer()
        self.monitoring_timer.timeout.connect(self._update_performance_metrics)
        self.monitoring_timer.start(30000)  # Update every 30 seconds
        
        # Initialize performance tracking
        self._initialize_performance_tracking()
        
        logger.info("🎯 Model Selector initialized")
    
    def _initialize_performance_tracking(self):
        """Initialize performance tracking for available models"""
        available_models = self.llm_manager.get_available_models()
        
        for model_data in available_models:
            model_id = model_data['model_id']
            self.model_performance[model_id] = ModelPerformance(
                model_id=model_id,
                success_rate=1.0,  # Start optimistic
                average_response_time=2.0,  # Default estimate
                average_quality_score=0.8,  # Default quality
                total_requests=0,
                last_updated=datetime.now(),
                cost_efficiency=1.0 / (model_data['cost_per_token'] + 0.000001)  # Avoid division by zero
            )
        
        logger.info(f"🎯 Initialized performance tracking for {len(self.model_performance)} models")
    
    def set_selection_strategy(self, strategy: SelectionStrategy):
        """Set the model selection strategy"""
        if self.current_strategy != strategy:
            old_strategy = self.current_strategy
            self.current_strategy = strategy
            
            logger.info(f"🎯 Selection strategy changed: {old_strategy.value} → {strategy.value}")
            self.strategy_changed.emit(strategy.value)
    
    def select_model(self, task_requirements: TaskRequirements) -> Optional[str]:
        """
        Select optimal model based on task requirements and current strategy.
        
        Args:
            task_requirements: Task requirements specification
            
        Returns:
            Selected model ID or None if no suitable model found
        """
        try:
            # Get available models
            available_models = self.llm_manager.get_available_models()
            
            if not available_models:
                logger.error("❌ No models available")
                return None
            
            # Filter models by basic requirements
            suitable_models = self._filter_suitable_models(available_models, task_requirements)
            
            if not suitable_models:
                logger.warning("⚠️ No models meet basic requirements, using fallback")
                return self._select_fallback_model()
            
            # Score models based on current strategy
            scored_models = self._score_models(suitable_models, task_requirements)
            
            # Select best model
            best_model = max(scored_models, key=lambda x: x[1])
            selected_model_id = best_model[0]
            selection_score = best_model[1]
            
            # Create selection reason
            selection_reason = {
                'strategy': self.current_strategy.value,
                'score': selection_score,
                'task_complexity': task_requirements.complexity.value,
                'capability': task_requirements.capability.value,
                'alternatives_considered': len(scored_models)
            }
            
            logger.info(f"🎯 Selected model: {selected_model_id} (score: {selection_score:.3f})")
            self.model_selected.emit(selected_model_id, selection_reason)
            
            return selected_model_id
            
        except Exception as e:
            logger.error(f"❌ Error selecting model: {e}")
            return self._select_fallback_model()
    
    def _filter_suitable_models(self, available_models: List[Dict[str, Any]], 
                               requirements: TaskRequirements) -> List[Dict[str, Any]]:
        """Filter models that meet basic requirements"""
        suitable_models = []
        
        for model_data in available_models:
            # Check if model is available
            if not model_data.get('is_available', False):
                continue
            
            # Check capability
            model_capabilities = [ModelCapability(cap) for cap in model_data.get('capabilities', [])]
            if requirements.capability not in model_capabilities:
                continue
            
            # Check token limit
            if requirements.max_tokens and model_data.get('max_tokens', 0) < requirements.max_tokens:
                continue
            
            # Check cost limit
            if (requirements.max_cost_per_token and 
                model_data.get('cost_per_token', float('inf')) > requirements.max_cost_per_token):
                continue
            
            # Check local preference
            if requirements.prefer_local:
                provider = ProviderType(model_data.get('provider'))
                if provider not in [ProviderType.LOCAL, ProviderType.OLLAMA]:
                    continue
            
            suitable_models.append(model_data)
        
        return suitable_models
    
    def _score_models(self, models: List[Dict[str, Any]], 
                     requirements: TaskRequirements) -> List[Tuple[str, float]]:
        """Score models based on current strategy and requirements"""
        scored_models = []
        weights = self.strategy_weights[self.current_strategy]
        
        for model_data in models:
            model_id = model_data['model_id']
            
            # Get performance data
            performance = self.model_performance.get(model_id)
            if not performance:
                continue
            
            # Calculate component scores (0-1 scale)
            cost_score = self._calculate_cost_score(model_data, requirements)
            performance_score = self._calculate_performance_score(performance, requirements)
            quality_score = self._calculate_quality_score(performance, requirements)
            
            # Apply complexity adjustment
            complexity_multiplier = self._get_complexity_multiplier(
                model_data, requirements.complexity
            )
            
            # Calculate weighted final score
            final_score = (
                weights['cost'] * cost_score +
                weights['performance'] * performance_score +
                weights['quality'] * quality_score
            ) * complexity_multiplier
            
            scored_models.append((model_id, final_score))
        
        return scored_models
    
    def _calculate_cost_score(self, model_data: Dict[str, Any], 
                             requirements: TaskRequirements) -> float:
        """Calculate cost score (higher is better/cheaper)"""
        cost_per_token = model_data.get('cost_per_token', 0.0)
        
        if cost_per_token == 0.0:  # Free local models
            return 1.0
        
        # Normalize cost (inverse relationship - lower cost = higher score)
        max_acceptable_cost = requirements.max_cost_per_token or 0.0001
        cost_score = max(0.0, 1.0 - (cost_per_token / max_acceptable_cost))
        
        return min(1.0, cost_score)
    
    def _calculate_performance_score(self, performance: ModelPerformance, 
                                   requirements: TaskRequirements) -> float:
        """Calculate performance score based on response time and success rate"""
        # Response time score
        max_acceptable_time = requirements.max_response_time or 10.0
        time_score = max(0.0, 1.0 - (performance.average_response_time / max_acceptable_time))
        
        # Success rate score
        success_score = performance.success_rate
        
        # Combined performance score
        performance_score = (time_score * 0.6 + success_score * 0.4)
        
        return min(1.0, performance_score)
    
    def _calculate_quality_score(self, performance: ModelPerformance, 
                               requirements: TaskRequirements) -> float:
        """Calculate quality score based on historical performance"""
        quality_score = performance.average_quality_score
        
        # Apply quality threshold
        if quality_score < requirements.quality_threshold:
            quality_score *= 0.5  # Penalize models below threshold
        
        return min(1.0, quality_score)
    
    def _get_complexity_multiplier(self, model_data: Dict[str, Any], 
                                 complexity: TaskComplexity) -> float:
        """Get complexity multiplier based on model capabilities and task complexity"""
        context_window = model_data.get('context_window', 2048)
        max_tokens = model_data.get('max_tokens', 1024)
        
        # Simple heuristic based on model capacity
        if complexity == TaskComplexity.SIMPLE:
            return 1.0  # All models suitable
        elif complexity == TaskComplexity.MODERATE:
            return 1.0 if max_tokens >= 2048 else 0.8
        elif complexity == TaskComplexity.COMPLEX:
            return 1.0 if max_tokens >= 4096 else 0.6
        elif complexity == TaskComplexity.EXPERT:
            return 1.0 if max_tokens >= 8192 else 0.4
        
        return 1.0
    
    def _select_fallback_model(self) -> Optional[str]:
        """Select fallback model when no optimal model is found"""
        available_models = {m['model_id']: m for m in self.llm_manager.get_available_models()}
        
        for fallback_id in self.fallback_models:
            if fallback_id in available_models and available_models[fallback_id].get('is_available'):
                logger.info(f"🎯 Using fallback model: {fallback_id}")
                return fallback_id
        
        # Last resort - any available model
        for model_data in available_models.values():
            if model_data.get('is_available'):
                logger.warning(f"⚠️ Using last resort model: {model_data['model_id']}")
                return model_data['model_id']
        
        logger.error("❌ No fallback models available")
        return None
    
    def update_model_performance(self, model_id: str, 
                               response_time: float,
                               success: bool,
                               quality_score: Optional[float] = None):
        """Update model performance metrics"""
        try:
            if model_id not in self.model_performance:
                return
            
            performance = self.model_performance[model_id]
            
            # Update response time (exponential moving average)
            alpha = self.learning_rate
            performance.average_response_time = (
                alpha * response_time + 
                (1 - alpha) * performance.average_response_time
            )
            
            # Update success rate
            performance.total_requests += 1
            if success:
                performance.success_rate = (
                    alpha * 1.0 + 
                    (1 - alpha) * performance.success_rate
                )
            else:
                performance.success_rate = (
                    alpha * 0.0 + 
                    (1 - alpha) * performance.success_rate
                )
            
            # Update quality score if provided
            if quality_score is not None:
                performance.average_quality_score = (
                    alpha * quality_score + 
                    (1 - alpha) * performance.average_quality_score
                )
            
            # Update cost efficiency
            model_data = next((m for m in self.llm_manager.get_available_models() 
                             if m['model_id'] == model_id), None)
            if model_data:
                cost_per_token = model_data.get('cost_per_token', 0.000001)
                performance.cost_efficiency = performance.average_quality_score / cost_per_token
            
            performance.last_updated = datetime.now()
            
            # Emit performance update
            self.performance_updated.emit(model_id, {
                'success_rate': performance.success_rate,
                'average_response_time': performance.average_response_time,
                'average_quality_score': performance.average_quality_score,
                'total_requests': performance.total_requests,
                'cost_efficiency': performance.cost_efficiency
            })
            
            logger.debug(f"🎯 Updated performance for {model_id}: "
                        f"success={performance.success_rate:.3f}, "
                        f"time={performance.average_response_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Error updating model performance: {e}")
    
    def _update_performance_metrics(self):
        """Periodic performance metrics update"""
        # Clean up old performance data
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        for model_id, performance in self.model_performance.items():
            if performance.last_updated < cutoff_time and performance.total_requests == 0:
                # Reset unused models to default values
                performance.success_rate = 1.0
                performance.average_response_time = 2.0
                performance.average_quality_score = 0.8
    
    def get_model_rankings(self, task_requirements: TaskRequirements) -> List[Dict[str, Any]]:
        """Get ranked list of models for given requirements"""
        try:
            available_models = self.llm_manager.get_available_models()
            suitable_models = self._filter_suitable_models(available_models, task_requirements)
            scored_models = self._score_models(suitable_models, task_requirements)
            
            # Sort by score (descending)
            scored_models.sort(key=lambda x: x[1], reverse=True)
            
            rankings = []
            for model_id, score in scored_models:
                model_data = next(m for m in available_models if m['model_id'] == model_id)
                performance = self.model_performance.get(model_id)
                
                rankings.append({
                    'model_id': model_id,
                    'name': model_data.get('name', model_id),
                    'provider': model_data.get('provider'),
                    'score': score,
                    'success_rate': performance.success_rate if performance else 0.0,
                    'avg_response_time': performance.average_response_time if performance else 0.0,
                    'cost_per_token': model_data.get('cost_per_token', 0.0)
                })
            
            return rankings
            
        except Exception as e:
            logger.error(f"❌ Error getting model rankings: {e}")
            return []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all models"""
        summary = {
            'total_models': len(self.model_performance),
            'strategy': self.current_strategy.value,
            'models': {}
        }
        
        for model_id, performance in self.model_performance.items():
            summary['models'][model_id] = {
                'success_rate': performance.success_rate,
                'average_response_time': performance.average_response_time,
                'average_quality_score': performance.average_quality_score,
                'total_requests': performance.total_requests,
                'cost_efficiency': performance.cost_efficiency,
                'last_updated': performance.last_updated.isoformat()
            }
        
        return summary

# Singleton instance
_model_selector = None

def get_model_selector() -> ModelSelector:
    """Get the singleton Model Selector instance"""
    global _model_selector
    if _model_selector is None:
        _model_selector = ModelSelector()
    return _model_selector
