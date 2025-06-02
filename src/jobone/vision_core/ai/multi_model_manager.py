"""
🧠 Orion Vision Core - Multi-Model AI Manager
Advanced multi-provider AI model management and integration

This module provides comprehensive multi-model AI capabilities:
- Support for multiple AI providers (OpenAI, Anthropic, Groq, local models)
- Dynamic model selection based on task requirements
- Load balancing and failover mechanisms
- Cost optimization and performance monitoring
- Unified API interface for all providers

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider(Enum):
    """Supported AI providers"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GROQ = "groq"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class ModelCapability(Enum):
    """Model capabilities for task matching"""
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CONVERSATION = "conversation"
    ANALYSIS = "analysis"
    CREATIVE_WRITING = "creative_writing"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

@dataclass
class ModelConfig:
    """Configuration for an AI model"""
    provider: AIProvider
    model_name: str
    api_key: Optional[str] = None
    api_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    capabilities: List[ModelCapability] = field(default_factory=list)
    cost_per_token: float = 0.0
    max_requests_per_minute: int = 60
    priority: int = 1  # Higher number = higher priority
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIRequest:
    """AI request with metadata"""
    request_id: str
    prompt: str
    model_config: ModelConfig
    task_type: ModelCapability
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AIResponse:
    """AI response with metadata"""
    request_id: str
    response_text: str
    model_used: str
    provider: AIProvider
    tokens_used: int
    cost: float
    response_time: float
    confidence_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

class MultiModelManager:
    """
    Advanced multi-model AI manager for Orion Vision Core.

    Manages multiple AI providers and models with:
    - Dynamic model selection
    - Load balancing and failover
    - Cost optimization
    - Performance monitoring
    - Unified API interface
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the multi-model manager"""
        self.models: Dict[str, ModelConfig] = {}
        self.request_history: List[AIRequest] = []
        self.response_history: List[AIResponse] = []
        self.performance_metrics: Dict[str, Dict[str, float]] = {}
        self.rate_limits: Dict[str, List[datetime]] = {}

        # Load configuration
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        else:
            self._setup_default_models()

        logger.info("🧠 Multi-Model AI Manager initialized")

    def _setup_default_models(self):
        """Setup default model configurations"""
        # OpenAI models
        self.add_model(ModelConfig(
            provider=AIProvider.OPENAI,
            model_name="gpt-4",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING,
                         ModelCapability.CODE_GENERATION, ModelCapability.ANALYSIS],
            cost_per_token=0.00003,
            priority=5,
            max_requests_per_minute=60
        ))

        self.add_model(ModelConfig(
            provider=AIProvider.OPENAI,
            model_name="gpt-3.5-turbo",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CONVERSATION],
            cost_per_token=0.000002,
            priority=3,
            max_requests_per_minute=100
        ))

        # Anthropic models
        self.add_model(ModelConfig(
            provider=AIProvider.ANTHROPIC,
            model_name="claude-3-opus",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING,
                         ModelCapability.ANALYSIS, ModelCapability.CREATIVE_WRITING],
            cost_per_token=0.000015,
            priority=4,
            max_requests_per_minute=50
        ))

        # Groq models
        self.add_model(ModelConfig(
            provider=AIProvider.GROQ,
            model_name="llama2-70b-4096",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CONVERSATION],
            cost_per_token=0.0000008,
            priority=2,
            max_requests_per_minute=30
        ))

        # Local Ollama model
        self.add_model(ModelConfig(
            provider=AIProvider.OLLAMA,
            model_name="llama2",
            api_url="http://localhost:11434",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CONVERSATION],
            cost_per_token=0.0,  # Free local model
            priority=1,
            max_requests_per_minute=1000  # No API limits
        ))

        logger.info(f"📋 Setup {len(self.models)} default AI models")

    def add_model(self, model_config: ModelConfig):
        """Add a new model configuration"""
        model_key = f"{model_config.provider.value}:{model_config.model_name}"
        self.models[model_key] = model_config
        self.performance_metrics[model_key] = {
            'total_requests': 0,
            'total_tokens': 0,
            'total_cost': 0.0,
            'average_response_time': 0.0,
            'success_rate': 1.0,
            'last_used': 0.0
        }
        logger.info(f"➕ Added model: {model_key}")

    def remove_model(self, provider: AIProvider, model_name: str):
        """Remove a model configuration"""
        model_key = f"{provider.value}:{model_name}"
        if model_key in self.models:
            del self.models[model_key]
            if model_key in self.performance_metrics:
                del self.performance_metrics[model_key]
            logger.info(f"➖ Removed model: {model_key}")

    def get_available_models(self, capability: Optional[ModelCapability] = None) -> List[ModelConfig]:
        """Get available models, optionally filtered by capability"""
        available = []
        for model in self.models.values():
            if not model.enabled:
                continue
            if capability and capability not in model.capabilities:
                continue
            available.append(model)

        # Sort by priority (higher first)
        available.sort(key=lambda m: m.priority, reverse=True)
        return available

    def select_best_model(self, task_type: ModelCapability,
                         prefer_cost_optimization: bool = False) -> Optional[ModelConfig]:
        """Select the best model for a given task"""
        available_models = self.get_available_models(task_type)

        if not available_models:
            logger.warning(f"⚠️ No available models for task: {task_type}")
            return None

        # Check rate limits
        available_models = [m for m in available_models if self._check_rate_limit(m)]

        if not available_models:
            logger.warning(f"⚠️ All models rate limited for task: {task_type}")
            return None

        if prefer_cost_optimization:
            # Sort by cost (lower first), then by performance
            available_models.sort(key=lambda m: (
                m.cost_per_token,
                -self.performance_metrics.get(f"{m.provider.value}:{m.model_name}", {}).get('success_rate', 0)
            ))
        else:
            # Sort by performance, then by priority
            available_models.sort(key=lambda m: (
                -self.performance_metrics.get(f"{m.provider.value}:{m.model_name}", {}).get('success_rate', 0),
                -m.priority
            ))

        selected = available_models[0]
        logger.info(f"🎯 Selected model: {selected.provider.value}:{selected.model_name} for {task_type}")
        return selected

    def _check_rate_limit(self, model: ModelConfig) -> bool:
        """Check if model is within rate limits"""
        model_key = f"{model.provider.value}:{model.model_name}"
        now = datetime.now()

        if model_key not in self.rate_limits:
            self.rate_limits[model_key] = []

        # Remove requests older than 1 minute
        self.rate_limits[model_key] = [
            req_time for req_time in self.rate_limits[model_key]
            if now - req_time < timedelta(minutes=1)
        ]

        # Check if under limit
        return len(self.rate_limits[model_key]) < model.max_requests_per_minute

    def _record_request(self, model: ModelConfig):
        """Record a request for rate limiting"""
        model_key = f"{model.provider.value}:{model.model_name}"
        if model_key not in self.rate_limits:
            self.rate_limits[model_key] = []
        self.rate_limits[model_key].append(datetime.now())

    async def generate_response(self, prompt: str, task_type: ModelCapability,
                              prefer_cost_optimization: bool = False,
                              max_tokens: Optional[int] = None,
                              temperature: Optional[float] = None) -> Optional[AIResponse]:
        """Generate AI response using the best available model"""

        # Select best model
        model = self.select_best_model(task_type, prefer_cost_optimization)
        if not model:
            return None

        # Create request
        request = AIRequest(
            request_id=f"req_{int(time.time() * 1000)}",
            prompt=prompt,
            model_config=model,
            task_type=task_type,
            max_tokens=max_tokens or model.max_tokens,
            temperature=temperature or model.temperature
        )

        # Record request for rate limiting
        self._record_request(model)

        # Generate response
        start_time = time.time()
        try:
            response_text = await self._call_model_api(model, request)
            response_time = time.time() - start_time

            # Calculate tokens and cost (simplified)
            tokens_used = len(response_text.split()) * 1.3  # Rough estimation
            cost = tokens_used * model.cost_per_token

            # Create response
            response = AIResponse(
                request_id=request.request_id,
                response_text=response_text,
                model_used=model.model_name,
                provider=model.provider,
                tokens_used=int(tokens_used),
                cost=cost,
                response_time=response_time,
                confidence_score=0.85  # Default confidence
            )

            # Update metrics
            self._update_metrics(model, response, success=True)

            # Store history
            self.request_history.append(request)
            self.response_history.append(response)

            logger.info(f"✅ Generated response: {len(response_text)} chars, "
                       f"{response.tokens_used} tokens, ${response.cost:.4f}")

            return response

        except Exception as e:
            response_time = time.time() - start_time
            logger.error(f"❌ Model API call failed: {e}")

            # Update metrics for failure
            self._update_metrics(model, None, success=False)

            # Try fallback model
            return await self._try_fallback(prompt, task_type, model)

    async def _call_model_api(self, model: ModelConfig, request: AIRequest) -> str:
        """Call the specific model API"""
        if model.provider == AIProvider.OPENAI:
            return await self._call_openai_api(model, request)
        elif model.provider == AIProvider.ANTHROPIC:
            return await self._call_anthropic_api(model, request)
        elif model.provider == AIProvider.GROQ:
            return await self._call_groq_api(model, request)
        elif model.provider == AIProvider.OLLAMA:
            return await self._call_ollama_api(model, request)
        else:
            return self._generate_fallback_response(request.prompt)

    async def _call_openai_api(self, model: ModelConfig, request: AIRequest) -> str:
        """Call OpenAI API (placeholder - implement with actual API)"""
        await asyncio.sleep(0.5)  # Simulate API call
        return f"OpenAI {model.model_name} response to: {request.prompt[:50]}... [Enhanced multi-model response]"

    async def _call_anthropic_api(self, model: ModelConfig, request: AIRequest) -> str:
        """Call Anthropic API (placeholder - implement with actual API)"""
        await asyncio.sleep(0.7)  # Simulate API call
        return f"Anthropic {model.model_name} response to: {request.prompt[:50]}... [Enhanced multi-model response]"

    async def _call_groq_api(self, model: ModelConfig, request: AIRequest) -> str:
        """Call Groq API (placeholder - implement with actual API)"""
        await asyncio.sleep(0.3)  # Simulate API call
        return f"Groq {model.model_name} response to: {request.prompt[:50]}... [Enhanced multi-model response]"

    async def _call_ollama_api(self, model: ModelConfig, request: AIRequest) -> str:
        """Call Ollama local API (placeholder - implement with actual API)"""
        await asyncio.sleep(1.0)  # Simulate local processing
        return f"Local {model.model_name} response to: {request.prompt[:50]}... [Enhanced local response]"

    def _generate_fallback_response(self, prompt: str) -> str:
        """Generate fallback response when all models fail"""
        return f"I understand you said: '{prompt[:100]}...' However, I'm currently experiencing issues with all AI models. Please try again later or check your API configurations."

    async def _try_fallback(self, prompt: str, task_type: ModelCapability,
                           failed_model: ModelConfig) -> Optional[AIResponse]:
        """Try fallback models when primary model fails"""
        available_models = self.get_available_models(task_type)

        # Remove the failed model and try others
        fallback_models = [m for m in available_models
                          if f"{m.provider.value}:{m.model_name}" != f"{failed_model.provider.value}:{failed_model.model_name}"]

        for model in fallback_models:
            try:
                logger.info(f"🔄 Trying fallback model: {model.provider.value}:{model.model_name}")

                request = AIRequest(
                    request_id=f"fallback_{int(time.time() * 1000)}",
                    prompt=prompt,
                    model_config=model,
                    task_type=task_type
                )

                start_time = time.time()
                response_text = await self._call_model_api(model, request)
                response_time = time.time() - start_time

                # Create response
                tokens_used = len(response_text.split()) * 1.3
                cost = tokens_used * model.cost_per_token

                response = AIResponse(
                    request_id=request.request_id,
                    response_text=response_text,
                    model_used=model.model_name,
                    provider=model.provider,
                    tokens_used=int(tokens_used),
                    cost=cost,
                    response_time=response_time,
                    confidence_score=0.75  # Lower confidence for fallback
                )

                self._update_metrics(model, response, success=True)
                return response

            except Exception as e:
                logger.warning(f"⚠️ Fallback model {model.model_name} also failed: {e}")
                continue

        logger.error("❌ All fallback models failed")
        return None

    def _update_metrics(self, model: ModelConfig, response: Optional[AIResponse], success: bool):
        """Update performance metrics for a model"""
        model_key = f"{model.provider.value}:{model.model_name}"
        metrics = self.performance_metrics[model_key]

        metrics['total_requests'] += 1
        metrics['last_used'] = time.time()

        if success and response:
            metrics['total_tokens'] += response.tokens_used
            metrics['total_cost'] += response.cost

            # Update average response time
            current_avg = metrics['average_response_time']
            total_requests = metrics['total_requests']
            metrics['average_response_time'] = (
                (current_avg * (total_requests - 1) + response.response_time) / total_requests
            )

        # Update success rate
        successful_requests = metrics['total_requests'] * metrics['success_rate']
        if success:
            successful_requests += 1
        metrics['success_rate'] = successful_requests / metrics['total_requests']

    def get_performance_metrics(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics for all models"""
        return self.performance_metrics.copy()

    def get_cost_summary(self) -> Dict[str, float]:
        """Get cost summary across all models"""
        total_cost = sum(metrics['total_cost'] for metrics in self.performance_metrics.values())
        total_tokens = sum(metrics['total_tokens'] for metrics in self.performance_metrics.values())

        return {
            'total_cost': total_cost,
            'total_tokens': total_tokens,
            'average_cost_per_token': total_cost / total_tokens if total_tokens > 0 else 0.0,
            'total_requests': len(self.request_history)
        }

    def load_config(self, config_path: str):
        """Load model configurations from file"""
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)

            for model_data in config_data.get('models', []):
                model_config = ModelConfig(
                    provider=AIProvider(model_data['provider']),
                    model_name=model_data['model_name'],
                    api_key=model_data.get('api_key'),
                    api_url=model_data.get('api_url'),
                    max_tokens=model_data.get('max_tokens', 4096),
                    temperature=model_data.get('temperature', 0.7),
                    capabilities=[ModelCapability(cap) for cap in model_data.get('capabilities', [])],
                    cost_per_token=model_data.get('cost_per_token', 0.0),
                    max_requests_per_minute=model_data.get('max_requests_per_minute', 60),
                    priority=model_data.get('priority', 1),
                    enabled=model_data.get('enabled', True)
                )
                self.add_model(model_config)

            logger.info(f"📁 Loaded configuration from {config_path}")

        except Exception as e:
            logger.error(f"❌ Failed to load config from {config_path}: {e}")

    def save_config(self, config_path: str):
        """Save current model configurations to file"""
        try:
            config_data = {
                'models': []
            }

            for model in self.models.values():
                model_data = {
                    'provider': model.provider.value,
                    'model_name': model.model_name,
                    'api_key': model.api_key,
                    'api_url': model.api_url,
                    'max_tokens': model.max_tokens,
                    'temperature': model.temperature,
                    'capabilities': [cap.value for cap in model.capabilities],
                    'cost_per_token': model.cost_per_token,
                    'max_requests_per_minute': model.max_requests_per_minute,
                    'priority': model.priority,
                    'enabled': model.enabled
                }
                config_data['models'].append(model_data)

            with open(config_path, 'w') as f:
                json.dump(config_data, f, indent=2)

            logger.info(f"💾 Saved configuration to {config_path}")

        except Exception as e:
            logger.error(f"❌ Failed to save config to {config_path}: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the multi-model manager"""
        return {
            'total_models': len(self.models),
            'enabled_models': len([m for m in self.models.values() if m.enabled]),
            'total_requests': len(self.request_history),
            'total_responses': len(self.response_history),
            'performance_metrics': self.get_performance_metrics(),
            'cost_summary': self.get_cost_summary(),
            'supported_providers': [provider.value for provider in AIProvider],
            'supported_capabilities': [cap.value for cap in ModelCapability]
        }
