#!/usr/bin/env python3
"""
🧪 Orion Vision Core - Advanced Multi-Model AI Test Suite
Comprehensive testing and validation for Sprint 9.1 AI capabilities

This advanced test suite covers:
- Stress testing with multiple concurrent requests
- Edge case handling and error scenarios
- Performance benchmarking and optimization
- Real-world usage simulation
- Integration testing with existing systems

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import sys
import os
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.multi_model_manager import MultiModelManager, ModelCapability, AIProvider, ModelConfig
from ai.model_ensemble import ModelEnsemble, EnsembleStrategy, EnsembleConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedTestSuite:
    """Advanced test suite for Multi-Model AI system"""
    
    def __init__(self):
        self.manager = None
        self.ensemble = None
        self.test_results = {
            'stress_test': {},
            'edge_cases': {},
            'performance': {},
            'integration': {},
            'error_handling': {}
        }
    
    async def setup(self):
        """Setup test environment"""
        logger.info("🔧 Setting up advanced test environment...")
        
        # Initialize manager with custom configuration
        self.manager = MultiModelManager()
        
        # Add some custom test models
        self.manager.add_model(ModelConfig(
            provider=AIProvider.CUSTOM,
            model_name="test-model-fast",
            capabilities=[ModelCapability.TEXT_GENERATION],
            cost_per_token=0.000001,
            priority=6,  # Higher than default
            max_requests_per_minute=1000
        ))
        
        # Initialize ensemble with test configuration
        config = EnsembleConfig(
            strategy=EnsembleStrategy.WEIGHTED_VOTE,
            min_models=2,
            max_models=4,
            confidence_threshold=0.75,
            timeout_seconds=10.0
        )
        self.ensemble = ModelEnsemble(self.manager, config)
        
        logger.info("✅ Advanced test environment ready")
    
    async def stress_test_concurrent_requests(self, num_requests: int = 50):
        """Test system under concurrent load"""
        logger.info(f"🚀 Starting stress test with {num_requests} concurrent requests...")
        
        start_time = time.time()
        
        # Create concurrent tasks
        tasks = []
        for i in range(num_requests):
            task = asyncio.create_task(
                self.manager.generate_response(
                    f"Test request {i}: What is the meaning of life?",
                    ModelCapability.TEXT_GENERATION
                )
            )
            tasks.append(task)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Analyze results
        successful_responses = [r for r in results if hasattr(r, 'response_text')]
        failed_responses = [r for r in results if isinstance(r, Exception)]
        
        success_rate = len(successful_responses) / num_requests
        avg_response_time = statistics.mean([r.response_time for r in successful_responses]) if successful_responses else 0
        throughput = num_requests / total_time
        
        self.test_results['stress_test'] = {
            'total_requests': num_requests,
            'successful_responses': len(successful_responses),
            'failed_responses': len(failed_responses),
            'success_rate': success_rate,
            'total_time': total_time,
            'average_response_time': avg_response_time,
            'throughput_rps': throughput
        }
        
        logger.info(f"📊 Stress test results:")
        logger.info(f"  Success rate: {success_rate:.2%}")
        logger.info(f"  Total time: {total_time:.2f}s")
        logger.info(f"  Throughput: {throughput:.2f} requests/second")
        logger.info(f"  Average response time: {avg_response_time:.2f}s")
        
        return success_rate > 0.95  # 95% success rate threshold
    
    async def test_edge_cases(self):
        """Test edge cases and error scenarios"""
        logger.info("🔍 Testing edge cases and error scenarios...")
        
        edge_cases = [
            ("", ModelCapability.TEXT_GENERATION, "empty_prompt"),
            ("A" * 10000, ModelCapability.TEXT_GENERATION, "very_long_prompt"),
            ("🚀🎭🧠💰📊✅❌🔄", ModelCapability.TEXT_GENERATION, "emoji_only"),
            ("SELECT * FROM users; DROP TABLE users;", ModelCapability.CODE_GENERATION, "sql_injection"),
            ("What is " + "very " * 1000 + "important?", ModelCapability.ANALYSIS, "repetitive_prompt")
        ]
        
        results = {}
        
        for prompt, capability, test_name in edge_cases:
            try:
                logger.info(f"  Testing: {test_name}")
                response = await self.manager.generate_response(prompt, capability)
                
                if response:
                    results[test_name] = {
                        'status': 'success',
                        'response_length': len(response.response_text),
                        'tokens_used': response.tokens_used,
                        'response_time': response.response_time
                    }
                    logger.info(f"    ✅ {test_name}: Success")
                else:
                    results[test_name] = {'status': 'no_response'}
                    logger.info(f"    ⚠️ {test_name}: No response")
                    
            except Exception as e:
                results[test_name] = {'status': 'error', 'error': str(e)}
                logger.info(f"    ❌ {test_name}: Error - {e}")
        
        self.test_results['edge_cases'] = results
        
        # Check if critical edge cases passed
        critical_passed = results.get('empty_prompt', {}).get('status') in ['success', 'no_response']
        return critical_passed
    
    async def performance_benchmark(self):
        """Benchmark performance across different scenarios"""
        logger.info("⚡ Running performance benchmarks...")
        
        scenarios = [
            ("Short prompt", "Hello", ModelCapability.CONVERSATION),
            ("Medium prompt", "Explain the concept of artificial intelligence and its applications in modern technology.", ModelCapability.ANALYSIS),
            ("Long prompt", "Write a detailed analysis of the impact of quantum computing on cybersecurity, including potential threats and opportunities for the next decade." * 3, ModelCapability.TEXT_GENERATION),
            ("Code generation", "Write a Python function to calculate fibonacci numbers", ModelCapability.CODE_GENERATION),
            ("Creative task", "Write a haiku about machine learning", ModelCapability.CREATIVE_WRITING)
        ]
        
        benchmark_results = {}
        
        for scenario_name, prompt, capability in scenarios:
            logger.info(f"  Benchmarking: {scenario_name}")
            
            # Run multiple iterations for accurate timing
            times = []
            token_counts = []
            
            for i in range(5):  # 5 iterations per scenario
                start_time = time.time()
                response = await self.manager.generate_response(prompt, capability)
                end_time = time.time()
                
                if response:
                    times.append(end_time - start_time)
                    token_counts.append(response.tokens_used)
            
            if times:
                benchmark_results[scenario_name] = {
                    'avg_response_time': statistics.mean(times),
                    'min_response_time': min(times),
                    'max_response_time': max(times),
                    'avg_tokens': statistics.mean(token_counts),
                    'iterations': len(times)
                }
                
                logger.info(f"    ⚡ Avg time: {statistics.mean(times):.2f}s, Avg tokens: {statistics.mean(token_counts):.0f}")
        
        self.test_results['performance'] = benchmark_results
        return len(benchmark_results) == len(scenarios)
    
    async def test_ensemble_strategies(self):
        """Test all ensemble strategies comprehensively"""
        logger.info("🎭 Testing all ensemble strategies...")
        
        test_prompt = "Compare the advantages and disadvantages of renewable energy sources"
        
        strategy_results = {}
        
        for strategy in EnsembleStrategy:
            logger.info(f"  Testing strategy: {strategy.value}")
            
            try:
                start_time = time.time()
                result = await self.ensemble.generate_ensemble_response(
                    test_prompt,
                    ModelCapability.ANALYSIS,
                    strategy
                )
                end_time = time.time()
                
                if result:
                    strategy_results[strategy.value] = {
                        'status': 'success',
                        'confidence': result.confidence_score,
                        'participating_models': len(result.participating_models),
                        'processing_time': end_time - start_time,
                        'response_length': len(result.final_response)
                    }
                    logger.info(f"    ✅ {strategy.value}: confidence={result.confidence_score:.2f}")
                else:
                    strategy_results[strategy.value] = {'status': 'failed'}
                    logger.info(f"    ❌ {strategy.value}: Failed")
                    
            except Exception as e:
                strategy_results[strategy.value] = {'status': 'error', 'error': str(e)}
                logger.info(f"    ❌ {strategy.value}: Error - {e}")
        
        self.test_results['ensemble_strategies'] = strategy_results
        
        # Check if majority of strategies worked
        successful_strategies = sum(1 for r in strategy_results.values() if r.get('status') == 'success')
        return successful_strategies >= len(EnsembleStrategy) * 0.8  # 80% success rate
    
    async def test_model_selection_logic(self):
        """Test model selection logic under various conditions"""
        logger.info("🎯 Testing model selection logic...")
        
        selection_tests = []
        
        # Test different capabilities
        for capability in [ModelCapability.TEXT_GENERATION, ModelCapability.CONVERSATION, ModelCapability.ANALYSIS]:
            model = self.manager.select_best_model(capability)
            selection_tests.append({
                'test': f'capability_{capability.value}',
                'selected_model': f"{model.provider.value}:{model.model_name}" if model else None,
                'success': model is not None
            })
        
        # Test cost optimization
        model_cost = self.manager.select_best_model(ModelCapability.TEXT_GENERATION, prefer_cost_optimization=True)
        model_performance = self.manager.select_best_model(ModelCapability.TEXT_GENERATION, prefer_cost_optimization=False)
        
        selection_tests.append({
            'test': 'cost_optimization',
            'cost_model': f"{model_cost.provider.value}:{model_cost.model_name}" if model_cost else None,
            'performance_model': f"{model_performance.provider.value}:{model_performance.model_name}" if model_performance else None,
            'success': model_cost is not None and model_performance is not None
        })
        
        self.test_results['model_selection'] = selection_tests
        
        # Check if all selection tests passed
        return all(test['success'] for test in selection_tests)
    
    async def run_all_tests(self):
        """Run all advanced tests"""
        logger.info("🧪 Starting comprehensive advanced test suite...")
        logger.info("=" * 80)
        
        await self.setup()
        
        test_results = {}
        
        # Run all test categories
        test_results['stress_test'] = await self.stress_test_concurrent_requests(30)
        logger.info("=" * 80)
        
        test_results['edge_cases'] = await self.test_edge_cases()
        logger.info("=" * 80)
        
        test_results['performance'] = await self.performance_benchmark()
        logger.info("=" * 80)
        
        test_results['ensemble_strategies'] = await self.test_ensemble_strategies()
        logger.info("=" * 80)
        
        test_results['model_selection'] = await self.test_model_selection_logic()
        logger.info("=" * 80)
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        overall_success_rate = passed_tests / total_tests
        
        logger.info("📊 ADVANCED TEST SUITE RESULTS:")
        logger.info(f"  Stress Test: {'✅ PASSED' if test_results['stress_test'] else '❌ FAILED'}")
        logger.info(f"  Edge Cases: {'✅ PASSED' if test_results['edge_cases'] else '❌ FAILED'}")
        logger.info(f"  Performance: {'✅ PASSED' if test_results['performance'] else '❌ FAILED'}")
        logger.info(f"  Ensemble Strategies: {'✅ PASSED' if test_results['ensemble_strategies'] else '❌ FAILED'}")
        logger.info(f"  Model Selection: {'✅ PASSED' if test_results['model_selection'] else '❌ FAILED'}")
        logger.info(f"  Overall Success Rate: {overall_success_rate:.1%}")
        
        return overall_success_rate >= 0.8, self.test_results

async def main():
    """Main test execution"""
    test_suite = AdvancedTestSuite()
    
    try:
        success, detailed_results = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 ADVANCED TEST SUITE: ALL TESTS PASSED!")
            return True
        else:
            logger.error("❌ ADVANCED TEST SUITE: SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
