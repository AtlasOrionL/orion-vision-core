"""
🧠 Orion Vision Core - AI Model Ensemble System
Advanced AI ensemble for enhanced performance and reliability

This module provides AI ensemble capabilities:
- Multiple model consensus mechanisms
- Weighted voting systems
- Confidence scoring and validation
- Ensemble optimization algorithms
- Performance comparison and analysis

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import statistics
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from .multi_model_manager import MultiModelManager, ModelCapability, AIResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnsembleStrategy(Enum):
    """Ensemble voting strategies"""
    MAJORITY_VOTE = "majority_vote"
    WEIGHTED_VOTE = "weighted_vote"
    CONFIDENCE_WEIGHTED = "confidence_weighted"
    PERFORMANCE_WEIGHTED = "performance_weighted"
    BEST_OF_N = "best_of_n"
    CONSENSUS_THRESHOLD = "consensus_threshold"

@dataclass
class ConsensusResult:
    """Result of ensemble consensus"""
    final_response: str
    confidence_score: float
    strategy_used: EnsembleStrategy
    participating_models: List[str]
    individual_responses: List[AIResponse]
    consensus_details: Dict[str, Any]
    processing_time: float
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class EnsembleConfig:
    """Configuration for ensemble processing"""
    strategy: EnsembleStrategy = EnsembleStrategy.WEIGHTED_VOTE
    min_models: int = 2
    max_models: int = 5
    confidence_threshold: float = 0.8
    consensus_threshold: float = 0.7
    timeout_seconds: float = 30.0
    enable_fallback: bool = True
    cost_optimization: bool = False

class ModelEnsemble:
    """
    Advanced AI model ensemble system for Orion Vision Core.

    Combines multiple AI models to achieve:
    - Higher accuracy through consensus
    - Better reliability through redundancy
    - Enhanced confidence scoring
    - Improved decision making
    """

    def __init__(self, multi_model_manager: MultiModelManager, config: Optional[EnsembleConfig] = None):
        """Initialize the model ensemble"""
        self.multi_model_manager = multi_model_manager
        self.config = config or EnsembleConfig()
        self.ensemble_history: List[ConsensusResult] = []
        self.performance_metrics: Dict[str, float] = {
            'total_ensembles': 0,
            'successful_consensus': 0,
            'average_confidence': 0.0,
            'average_processing_time': 0.0,
            'cost_savings': 0.0
        }

        logger.info("🎭 AI Model Ensemble initialized")

    async def generate_ensemble_response(self, prompt: str, task_type: ModelCapability,
                                       strategy: Optional[EnsembleStrategy] = None) -> Optional[ConsensusResult]:
        """Generate response using ensemble of models"""

        start_time = asyncio.get_event_loop().time()
        strategy = strategy or self.config.strategy

        logger.info(f"🎭 Starting ensemble generation with strategy: {strategy.value}")

        # Get available models for the task
        available_models = self.multi_model_manager.get_available_models(task_type)

        if len(available_models) < self.config.min_models:
            logger.warning(f"⚠️ Not enough models for ensemble: {len(available_models)} < {self.config.min_models}")
            return None

        # Select models for ensemble
        selected_models = self._select_ensemble_models(available_models, task_type)

        # Generate responses from multiple models
        responses = await self._generate_multiple_responses(prompt, task_type, selected_models)

        if len(responses) < self.config.min_models:
            logger.warning(f"⚠️ Not enough successful responses for ensemble: {len(responses)}")
            return None

        # Apply ensemble strategy
        consensus_result = await self._apply_ensemble_strategy(responses, strategy, prompt)

        # Calculate processing time
        processing_time = asyncio.get_event_loop().time() - start_time
        consensus_result.processing_time = processing_time

        # Update metrics
        self._update_ensemble_metrics(consensus_result)

        # Store history
        self.ensemble_history.append(consensus_result)

        logger.info(f"✅ Ensemble consensus achieved: confidence={consensus_result.confidence_score:.2f}, "
                   f"time={processing_time:.2f}s")

        return consensus_result

    def _select_ensemble_models(self, available_models: List, task_type: ModelCapability) -> List:
        """Select best models for ensemble based on performance and diversity"""

        # Sort by performance and priority
        sorted_models = sorted(available_models, key=lambda m: (
            -self.multi_model_manager.performance_metrics.get(
                f"{m.provider.value}:{m.model_name}", {}
            ).get('success_rate', 0),
            -m.priority
        ))

        # Select top models up to max_models
        selected = sorted_models[:self.config.max_models]

        # Ensure provider diversity if possible
        if len(sorted_models) > len(selected):
            selected = self._ensure_provider_diversity(selected, sorted_models)

        logger.info(f"📋 Selected {len(selected)} models for ensemble: "
                   f"{[f'{m.provider.value}:{m.model_name}' for m in selected]}")

        return selected

    def _ensure_provider_diversity(self, selected: List, all_models: List) -> List:
        """Ensure diversity of providers in ensemble"""
        providers_used = {m.provider for m in selected}

        # If we have room and unused providers, swap some models
        for model in all_models:
            if len(selected) >= self.config.max_models:
                break

            if model.provider not in providers_used and model not in selected:
                # Replace lowest priority model with different provider
                selected[-1] = model
                providers_used.add(model.provider)

        return selected

    async def _generate_multiple_responses(self, prompt: str, task_type: ModelCapability,
                                         models: List) -> List[AIResponse]:
        """Generate responses from multiple models concurrently"""

        tasks = []
        for model in models:
            task = asyncio.create_task(
                self.multi_model_manager.generate_response(
                    prompt, task_type, prefer_cost_optimization=self.config.cost_optimization
                )
            )
            tasks.append(task)

        # Wait for all responses with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.config.timeout_seconds
            )

            # Filter successful responses
            successful_responses = [
                resp for resp in responses
                if isinstance(resp, AIResponse) and resp is not None
            ]

            logger.info(f"📊 Generated {len(successful_responses)} successful responses from {len(models)} models")
            return successful_responses

        except asyncio.TimeoutError:
            logger.warning(f"⏰ Ensemble generation timed out after {self.config.timeout_seconds}s")

            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()

            # Return any completed responses
            completed_responses = [
                task.result() for task in tasks
                if task.done() and not task.cancelled() and isinstance(task.result(), AIResponse)
            ]

            return completed_responses

    async def _apply_ensemble_strategy(self, responses: List[AIResponse],
                                     strategy: EnsembleStrategy, prompt: str) -> ConsensusResult:
        """Apply the specified ensemble strategy to combine responses"""

        if strategy == EnsembleStrategy.MAJORITY_VOTE:
            return await self._majority_vote_consensus(responses, prompt)
        elif strategy == EnsembleStrategy.WEIGHTED_VOTE:
            return await self._weighted_vote_consensus(responses, prompt)
        elif strategy == EnsembleStrategy.CONFIDENCE_WEIGHTED:
            return await self._confidence_weighted_consensus(responses, prompt)
        elif strategy == EnsembleStrategy.PERFORMANCE_WEIGHTED:
            return await self._performance_weighted_consensus(responses, prompt)
        elif strategy == EnsembleStrategy.BEST_OF_N:
            return await self._best_of_n_consensus(responses, prompt)
        elif strategy == EnsembleStrategy.CONSENSUS_THRESHOLD:
            return await self._consensus_threshold_strategy(responses, prompt)
        else:
            # Default to weighted vote
            return await self._weighted_vote_consensus(responses, prompt)

    async def _majority_vote_consensus(self, responses: List[AIResponse], prompt: str) -> ConsensusResult:
        """Simple majority vote consensus"""

        # For text responses, we'll use the response with highest confidence
        # In a real implementation, you might use semantic similarity

        best_response = max(responses, key=lambda r: r.confidence_score)

        # Calculate consensus confidence based on agreement
        confidence_scores = [r.confidence_score for r in responses]
        consensus_confidence = statistics.mean(confidence_scores)

        return ConsensusResult(
            final_response=best_response.response_text,
            confidence_score=consensus_confidence,
            strategy_used=EnsembleStrategy.MAJORITY_VOTE,
            participating_models=[r.model_used for r in responses],
            individual_responses=responses,
            consensus_details={
                'selected_response_index': responses.index(best_response),
                'confidence_scores': confidence_scores,
                'agreement_score': min(confidence_scores) / max(confidence_scores) if confidence_scores else 0
            },
            processing_time=0.0  # Will be set by caller
        )

    async def _weighted_vote_consensus(self, responses: List[AIResponse], prompt: str) -> ConsensusResult:
        """Weighted vote consensus based on model performance"""

        # Calculate weights based on model performance
        weights = []
        for response in responses:
            model_key = f"{response.provider.value}:{response.model_used}"
            metrics = self.multi_model_manager.performance_metrics.get(model_key, {})

            # Weight based on success rate and response time
            success_rate = metrics.get('success_rate', 0.5)
            avg_response_time = metrics.get('average_response_time', 1.0)

            # Higher success rate and lower response time = higher weight
            weight = success_rate * (1.0 / (avg_response_time + 0.1))
            weights.append(weight)

        # Normalize weights
        total_weight = sum(weights)
        if total_weight > 0:
            weights = [w / total_weight for w in weights]
        else:
            weights = [1.0 / len(responses)] * len(responses)

        # Select response with highest weighted score
        weighted_scores = [
            response.confidence_score * weight
            for response, weight in zip(responses, weights)
        ]

        best_index = weighted_scores.index(max(weighted_scores))
        best_response = responses[best_index]

        # Calculate weighted confidence
        weighted_confidence = sum(
            response.confidence_score * weight
            for response, weight in zip(responses, weights)
        )

        return ConsensusResult(
            final_response=best_response.response_text,
            confidence_score=weighted_confidence,
            strategy_used=EnsembleStrategy.WEIGHTED_VOTE,
            participating_models=[r.model_used for r in responses],
            individual_responses=responses,
            consensus_details={
                'weights': weights,
                'weighted_scores': weighted_scores,
                'selected_index': best_index
            },
            processing_time=0.0
        )

    async def _confidence_weighted_consensus(self, responses: List[AIResponse], prompt: str) -> ConsensusResult:
        """Consensus weighted by individual response confidence"""

        # Weight by confidence scores
        confidence_scores = [r.confidence_score for r in responses]
        total_confidence = sum(confidence_scores)

        if total_confidence > 0:
            weights = [score / total_confidence for score in confidence_scores]
        else:
            weights = [1.0 / len(responses)] * len(responses)

        # Select highest confidence response
        best_response = max(responses, key=lambda r: r.confidence_score)

        # Calculate weighted average confidence
        weighted_confidence = sum(
            response.confidence_score * weight
            for response, weight in zip(responses, weights)
        )

        return ConsensusResult(
            final_response=best_response.response_text,
            confidence_score=weighted_confidence,
            strategy_used=EnsembleStrategy.CONFIDENCE_WEIGHTED,
            participating_models=[r.model_used for r in responses],
            individual_responses=responses,
            consensus_details={
                'confidence_weights': weights,
                'original_confidences': confidence_scores
            },
            processing_time=0.0
        )

    async def _performance_weighted_consensus(self, responses: List[AIResponse], prompt: str) -> ConsensusResult:
        """Consensus weighted by historical model performance"""

        performance_scores = []
        for response in responses:
            model_key = f"{response.provider.value}:{response.model_used}"
            metrics = self.multi_model_manager.performance_metrics.get(model_key, {})

            # Combine multiple performance factors
            success_rate = metrics.get('success_rate', 0.5)
            avg_response_time = metrics.get('average_response_time', 1.0)
            total_requests = metrics.get('total_requests', 1)

            # Performance score: success rate weighted by experience and speed
            experience_factor = min(total_requests / 100.0, 1.0)  # Cap at 100 requests
            speed_factor = 1.0 / (avg_response_time + 0.1)

            performance_score = success_rate * experience_factor * speed_factor
            performance_scores.append(performance_score)

        # Normalize performance scores as weights
        total_performance = sum(performance_scores)
        if total_performance > 0:
            weights = [score / total_performance for score in performance_scores]
        else:
            weights = [1.0 / len(responses)] * len(responses)

        # Select response with best performance-weighted score
        weighted_scores = [
            response.confidence_score * weight
            for response, weight in zip(responses, weights)
        ]

        best_index = weighted_scores.index(max(weighted_scores))
        best_response = responses[best_index]

        return ConsensusResult(
            final_response=best_response.response_text,
            confidence_score=max(weighted_scores),
            strategy_used=EnsembleStrategy.PERFORMANCE_WEIGHTED,
            participating_models=[r.model_used for r in responses],
            individual_responses=responses,
            consensus_details={
                'performance_scores': performance_scores,
                'performance_weights': weights,
                'selected_index': best_index
            },
            processing_time=0.0
        )

    async def _best_of_n_consensus(self, responses: List[AIResponse], prompt: str) -> ConsensusResult:
        """Simply select the best response based on confidence"""

        best_response = max(responses, key=lambda r: r.confidence_score)

        return ConsensusResult(
            final_response=best_response.response_text,
            confidence_score=best_response.confidence_score,
            strategy_used=EnsembleStrategy.BEST_OF_N,
            participating_models=[r.model_used for r in responses],
            individual_responses=responses,
            consensus_details={
                'selected_model': best_response.model_used,
                'all_confidences': [r.confidence_score for r in responses]
            },
            processing_time=0.0
        )

    async def _consensus_threshold_strategy(self, responses: List[AIResponse], prompt: str) -> ConsensusResult:
        """Only accept consensus if confidence threshold is met"""

        # Calculate average confidence
        confidence_scores = [r.confidence_score for r in responses]
        avg_confidence = statistics.mean(confidence_scores)

        if avg_confidence >= self.config.confidence_threshold:
            # Use weighted vote if threshold is met
            return await self._weighted_vote_consensus(responses, prompt)
        else:
            # Return best response but with lower confidence
            best_response = max(responses, key=lambda r: r.confidence_score)

            return ConsensusResult(
                final_response=best_response.response_text,
                confidence_score=avg_confidence * 0.8,  # Reduce confidence due to low consensus
                strategy_used=EnsembleStrategy.CONSENSUS_THRESHOLD,
                participating_models=[r.model_used for r in responses],
                individual_responses=responses,
                consensus_details={
                    'threshold_met': False,
                    'required_threshold': self.config.confidence_threshold,
                    'actual_confidence': avg_confidence
                },
                processing_time=0.0
            )

    def _update_ensemble_metrics(self, result: ConsensusResult):
        """Update ensemble performance metrics"""
        self.performance_metrics['total_ensembles'] += 1

        if result.confidence_score >= self.config.confidence_threshold:
            self.performance_metrics['successful_consensus'] += 1

        # Update average confidence
        total = self.performance_metrics['total_ensembles']
        current_avg = self.performance_metrics['average_confidence']
        self.performance_metrics['average_confidence'] = (
            (current_avg * (total - 1) + result.confidence_score) / total
        )

        # Update average processing time
        current_time_avg = self.performance_metrics['average_processing_time']
        self.performance_metrics['average_processing_time'] = (
            (current_time_avg * (total - 1) + result.processing_time) / total
        )

    def get_ensemble_metrics(self) -> Dict[str, Any]:
        """Get ensemble performance metrics"""
        total = self.performance_metrics['total_ensembles']
        success_rate = (
            self.performance_metrics['successful_consensus'] / total
            if total > 0 else 0.0
        )

        return {
            'total_ensembles': total,
            'success_rate': success_rate,
            'average_confidence': self.performance_metrics['average_confidence'],
            'average_processing_time': self.performance_metrics['average_processing_time'],
            'supported_strategies': [strategy.value for strategy in EnsembleStrategy]
        }

    def get_recent_results(self, limit: int = 10) -> List[ConsensusResult]:
        """Get recent ensemble results"""
        return self.ensemble_history[-limit:] if self.ensemble_history else []
