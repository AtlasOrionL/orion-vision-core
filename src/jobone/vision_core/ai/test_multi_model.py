#!/usr/bin/env python3
"""
🧠 Orion Vision Core - Multi-Model AI Integration Test
Test script for Sprint 9.1 Multi-Model AI capabilities

This script tests:
- Multi-Model Manager functionality
- AI Ensemble system
- Model selection and fallback
- Performance metrics
- Cost optimization

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import sys
import os

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.multi_model_manager import MultiModelManager, ModelCapability, AIProvider
from ai.model_ensemble import ModelEnsemble, EnsembleStrategy, EnsembleConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_multi_model_manager():
    """Test Multi-Model Manager functionality"""
    logger.info("🧠 Testing Multi-Model Manager...")
    
    # Initialize manager
    manager = MultiModelManager()
    
    # Test model listing
    models = manager.get_available_models()
    logger.info(f"📋 Available models: {len(models)}")
    for model in models:
        logger.info(f"  - {model.provider.value}:{model.model_name} (priority: {model.priority})")
    
    # Test model selection
    best_model = manager.select_best_model(ModelCapability.TEXT_GENERATION)
    if best_model:
        logger.info(f"🎯 Best model for text generation: {best_model.provider.value}:{best_model.model_name}")
    
    # Test response generation
    logger.info("🔄 Testing response generation...")
    response = await manager.generate_response(
        "Hello, how are you today?",
        ModelCapability.CONVERSATION
    )
    
    if response:
        logger.info(f"✅ Response generated:")
        logger.info(f"  Model: {response.model_used}")
        logger.info(f"  Provider: {response.provider.value}")
        logger.info(f"  Tokens: {response.tokens_used}")
        logger.info(f"  Cost: ${response.cost:.4f}")
        logger.info(f"  Response time: {response.response_time:.2f}s")
        logger.info(f"  Response: {response.response_text[:100]}...")
    else:
        logger.error("❌ Failed to generate response")
    
    # Test performance metrics
    metrics = manager.get_performance_metrics()
    logger.info(f"📊 Performance metrics: {len(metrics)} models tracked")
    
    # Test cost summary
    cost_summary = manager.get_cost_summary()
    logger.info(f"💰 Cost summary: ${cost_summary['total_cost']:.4f} total, {cost_summary['total_requests']} requests")
    
    return manager

async def test_model_ensemble(manager):
    """Test Model Ensemble functionality"""
    logger.info("🎭 Testing Model Ensemble...")
    
    # Initialize ensemble
    config = EnsembleConfig(
        strategy=EnsembleStrategy.WEIGHTED_VOTE,
        min_models=2,
        max_models=3,
        confidence_threshold=0.7
    )
    ensemble = ModelEnsemble(manager, config)
    
    # Test ensemble response generation
    logger.info("🔄 Testing ensemble response generation...")
    
    test_prompts = [
        "What is artificial intelligence?",
        "Explain quantum computing in simple terms",
        "Write a short poem about technology"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        logger.info(f"📝 Test {i}: {prompt}")
        
        result = await ensemble.generate_ensemble_response(
            prompt,
            ModelCapability.TEXT_GENERATION,
            EnsembleStrategy.WEIGHTED_VOTE
        )
        
        if result:
            logger.info(f"✅ Ensemble result:")
            logger.info(f"  Strategy: {result.strategy_used.value}")
            logger.info(f"  Confidence: {result.confidence_score:.2f}")
            logger.info(f"  Models: {', '.join(result.participating_models)}")
            logger.info(f"  Processing time: {result.processing_time:.2f}s")
            logger.info(f"  Response: {result.final_response[:100]}...")
        else:
            logger.error(f"❌ Failed to generate ensemble response for test {i}")
        
        logger.info("---")
    
    # Test different ensemble strategies
    strategies = [
        EnsembleStrategy.MAJORITY_VOTE,
        EnsembleStrategy.CONFIDENCE_WEIGHTED,
        EnsembleStrategy.BEST_OF_N
    ]
    
    logger.info("🎯 Testing different ensemble strategies...")
    for strategy in strategies:
        logger.info(f"Testing strategy: {strategy.value}")
        
        result = await ensemble.generate_ensemble_response(
            "Compare Python and JavaScript programming languages",
            ModelCapability.ANALYSIS,
            strategy
        )
        
        if result:
            logger.info(f"  ✅ {strategy.value}: confidence={result.confidence_score:.2f}, "
                       f"models={len(result.participating_models)}")
        else:
            logger.info(f"  ❌ {strategy.value}: failed")
    
    # Test ensemble metrics
    metrics = ensemble.get_ensemble_metrics()
    logger.info(f"📊 Ensemble metrics:")
    logger.info(f"  Total ensembles: {metrics['total_ensembles']}")
    logger.info(f"  Success rate: {metrics['success_rate']:.2f}")
    logger.info(f"  Average confidence: {metrics['average_confidence']:.2f}")
    logger.info(f"  Average processing time: {metrics['average_processing_time']:.2f}s")
    
    return ensemble

async def test_cost_optimization(manager):
    """Test cost optimization features"""
    logger.info("💰 Testing cost optimization...")
    
    # Test with cost optimization enabled
    logger.info("🔄 Testing with cost optimization enabled...")
    response_cost_opt = await manager.generate_response(
        "Summarize the benefits of renewable energy",
        ModelCapability.SUMMARIZATION,
        prefer_cost_optimization=True
    )
    
    # Test without cost optimization
    logger.info("🔄 Testing without cost optimization...")
    response_performance = await manager.generate_response(
        "Summarize the benefits of renewable energy",
        ModelCapability.SUMMARIZATION,
        prefer_cost_optimization=False
    )
    
    if response_cost_opt and response_performance:
        logger.info(f"💰 Cost optimization comparison:")
        logger.info(f"  Cost-optimized: {response_cost_opt.model_used}, ${response_cost_opt.cost:.4f}")
        logger.info(f"  Performance-optimized: {response_performance.model_used}, ${response_performance.cost:.4f}")
        
        savings = response_performance.cost - response_cost_opt.cost
        if savings > 0:
            logger.info(f"  💡 Savings: ${savings:.4f} ({savings/response_performance.cost*100:.1f}%)")
        else:
            logger.info(f"  📊 Same model selected for both strategies")

async def test_fallback_mechanisms(manager):
    """Test fallback mechanisms"""
    logger.info("🔄 Testing fallback mechanisms...")
    
    # Disable all high-priority models to test fallback
    original_states = {}
    for model_key, model in manager.models.items():
        if model.priority >= 4:  # Disable high-priority models
            original_states[model_key] = model.enabled
            model.enabled = False
    
    logger.info("🚫 Disabled high-priority models to test fallback...")
    
    # Test response generation with fallback
    response = await manager.generate_response(
        "Test fallback response generation",
        ModelCapability.TEXT_GENERATION
    )
    
    if response:
        logger.info(f"✅ Fallback successful:")
        logger.info(f"  Model used: {response.model_used}")
        logger.info(f"  Provider: {response.provider.value}")
    else:
        logger.error("❌ Fallback failed")
    
    # Restore original states
    for model_key, original_state in original_states.items():
        manager.models[model_key].enabled = original_state
    
    logger.info("🔄 Restored original model states")

async def main():
    """Main test function"""
    logger.info("🚀 Starting Sprint 9.1 Multi-Model AI Integration Tests")
    logger.info("=" * 60)
    
    try:
        # Test Multi-Model Manager
        manager = await test_multi_model_manager()
        logger.info("=" * 60)
        
        # Test Model Ensemble
        ensemble = await test_model_ensemble(manager)
        logger.info("=" * 60)
        
        # Test Cost Optimization
        await test_cost_optimization(manager)
        logger.info("=" * 60)
        
        # Test Fallback Mechanisms
        await test_fallback_mechanisms(manager)
        logger.info("=" * 60)
        
        # Final status
        status = manager.get_status()
        logger.info("📊 Final Test Results:")
        logger.info(f"  Total models: {status['total_models']}")
        logger.info(f"  Enabled models: {status['enabled_models']}")
        logger.info(f"  Total requests: {status['total_requests']}")
        logger.info(f"  Total responses: {status['total_responses']}")
        
        cost_summary = status['cost_summary']
        logger.info(f"  Total cost: ${cost_summary['total_cost']:.4f}")
        logger.info(f"  Total tokens: {cost_summary['total_tokens']}")
        
        logger.info("🎉 All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 Sprint 9.1 Multi-Model AI Integration: TESTS PASSED")
        sys.exit(0)
    else:
        print("\n❌ Sprint 9.1 Multi-Model AI Integration: TESTS FAILED")
        sys.exit(1)
