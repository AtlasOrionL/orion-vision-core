#!/usr/bin/env python3
"""
🧠 Orion Vision Core - Advanced AI Reasoning Test Suite
Comprehensive testing for Advanced AI Reasoning capabilities

This test suite covers:
- Chain-of-thought reasoning
- Problem decomposition
- Logical inference
- Decision tree analysis
- Context management
- Multi-step problem solving

Sprint 9.1: Enhanced AI Capabilities and Cloud Integration
"""

import asyncio
import logging
import sys
import os
from datetime import timedelta

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai.multi_model_manager import MultiModelManager, ModelCapability
from ai.reasoning_engine import ReasoningEngine, ReasoningType, ReasoningConfig
from ai.context_manager import ContextManager, ContextType, ContextScope, ContextQuery

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedReasoningTestSuite:
    """Test suite for Advanced AI Reasoning capabilities"""
    
    def __init__(self):
        self.manager = None
        self.reasoning_engine = None
        self.context_manager = None
        self.test_results = {}
    
    async def setup(self):
        """Setup test environment"""
        logger.info("🔧 Setting up Advanced AI Reasoning test environment...")
        
        # Initialize multi-model manager
        self.manager = MultiModelManager()
        
        # Initialize reasoning engine
        config = ReasoningConfig(
            max_steps=8,
            min_confidence_threshold=0.6,
            enable_verification=True,
            enable_self_correction=True,
            reasoning_depth=3
        )
        self.reasoning_engine = ReasoningEngine(self.manager, config)
        
        # Initialize context manager
        self.context_manager = ContextManager()
        
        logger.info("✅ Advanced AI Reasoning test environment ready")
    
    async def test_chain_of_thought_reasoning(self):
        """Test chain-of-thought reasoning capabilities"""
        logger.info("🧠 Testing Chain-of-Thought Reasoning...")
        
        test_problems = [
            "How can we reduce carbon emissions in urban transportation?",
            "What are the ethical implications of artificial general intelligence?",
            "How should a startup prioritize features for their first product release?"
        ]
        
        results = []
        
        for i, problem in enumerate(test_problems, 1):
            logger.info(f"  Problem {i}: {problem}")
            
            try:
                chain = await self.reasoning_engine.reason_through_problem(
                    problem,
                    ReasoningType.CHAIN_OF_THOUGHT
                )
                
                success = (
                    len(chain.steps) >= 3 and
                    chain.confidence_score >= 0.5 and
                    len(chain.final_conclusion) > 50
                )
                
                results.append({
                    'problem': problem,
                    'success': success,
                    'steps': len(chain.steps),
                    'confidence': chain.confidence_score,
                    'processing_time': chain.processing_time
                })
                
                logger.info(f"    ✅ Steps: {len(chain.steps)}, Confidence: {chain.confidence_score:.2f}")
                
            except Exception as e:
                logger.error(f"    ❌ Failed: {e}")
                results.append({
                    'problem': problem,
                    'success': False,
                    'error': str(e)
                })
        
        self.test_results['chain_of_thought'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        return success_rate >= 0.8
    
    async def test_problem_decomposition(self):
        """Test problem decomposition reasoning"""
        logger.info("🔧 Testing Problem Decomposition...")
        
        complex_problems = [
            "Design and implement a sustainable smart city infrastructure",
            "Create a comprehensive cybersecurity strategy for a multinational corporation",
            "Develop a plan to address climate change through technology innovation"
        ]
        
        results = []
        
        for problem in complex_problems:
            logger.info(f"  Decomposing: {problem[:50]}...")
            
            try:
                chain = await self.reasoning_engine.reason_through_problem(
                    problem,
                    ReasoningType.PROBLEM_DECOMPOSITION
                )
                
                # Check for decomposition quality
                has_subproblems = any("subproblem" in step.content.lower() for step in chain.steps)
                has_integration = any("integration" in step.content.lower() for step in chain.steps)
                
                success = (
                    len(chain.steps) >= 4 and
                    has_subproblems and
                    has_integration and
                    chain.confidence_score >= 0.5
                )
                
                results.append({
                    'problem': problem,
                    'success': success,
                    'steps': len(chain.steps),
                    'has_subproblems': has_subproblems,
                    'has_integration': has_integration,
                    'confidence': chain.confidence_score
                })
                
                logger.info(f"    ✅ Decomposed into {len(chain.steps)} steps")
                
            except Exception as e:
                logger.error(f"    ❌ Failed: {e}")
                results.append({'problem': problem, 'success': False, 'error': str(e)})
        
        self.test_results['problem_decomposition'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        return success_rate >= 0.7
    
    async def test_logical_inference(self):
        """Test logical inference reasoning"""
        logger.info("🔍 Testing Logical Inference...")
        
        logical_problems = [
            "If all AI systems require data, and privacy laws restrict data collection, what are the implications for AI development?",
            "Given that renewable energy is intermittent and energy storage is expensive, how can we achieve 100% renewable energy?",
            "If automation increases productivity but reduces employment, what economic policies should be implemented?"
        ]
        
        results = []
        
        for problem in logical_problems:
            logger.info(f"  Analyzing: {problem[:50]}...")
            
            try:
                chain = await self.reasoning_engine.reason_through_problem(
                    problem,
                    ReasoningType.LOGICAL_INFERENCE
                )
                
                # Check for logical reasoning elements
                has_premises = any("given" in step.content.lower() or "if" in step.content.lower() for step in chain.steps)
                has_inference = any("therefore" in step.content.lower() or "conclude" in step.content.lower() for step in chain.steps)
                
                success = (
                    len(chain.steps) >= 3 and
                    has_premises and
                    has_inference and
                    chain.confidence_score >= 0.5
                )
                
                results.append({
                    'problem': problem,
                    'success': success,
                    'steps': len(chain.steps),
                    'has_premises': has_premises,
                    'has_inference': has_inference,
                    'confidence': chain.confidence_score
                })
                
                logger.info(f"    ✅ Logical analysis completed")
                
            except Exception as e:
                logger.error(f"    ❌ Failed: {e}")
                results.append({'problem': problem, 'success': False, 'error': str(e)})
        
        self.test_results['logical_inference'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        return success_rate >= 0.7
    
    async def test_decision_tree_analysis(self):
        """Test decision tree reasoning"""
        logger.info("🌳 Testing Decision Tree Analysis...")
        
        decision_problems = [
            "Should a company invest in AI research or acquire an AI startup?",
            "How should a city choose between electric buses, hydrogen buses, or hybrid buses?",
            "What programming language should a team choose for a new web application?"
        ]
        
        results = []
        
        for problem in decision_problems:
            logger.info(f"  Decision: {problem[:50]}...")
            
            try:
                chain = await self.reasoning_engine.reason_through_problem(
                    problem,
                    ReasoningType.DECISION_TREE
                )
                
                # Check for decision tree elements
                has_criteria = any("criteria" in step.content.lower() for step in chain.steps)
                has_options = any("option" in step.content.lower() or "path" in step.content.lower() for step in chain.steps)
                
                success = (
                    len(chain.steps) >= 3 and
                    has_criteria and
                    has_options and
                    chain.confidence_score >= 0.5
                )
                
                results.append({
                    'problem': problem,
                    'success': success,
                    'steps': len(chain.steps),
                    'has_criteria': has_criteria,
                    'has_options': has_options,
                    'confidence': chain.confidence_score
                })
                
                logger.info(f"    ✅ Decision tree analysis completed")
                
            except Exception as e:
                logger.error(f"    ❌ Failed: {e}")
                results.append({'problem': problem, 'success': False, 'error': str(e)})
        
        self.test_results['decision_tree'] = results
        success_rate = sum(1 for r in results if r.get('success', False)) / len(results)
        return success_rate >= 0.7
    
    async def test_context_management(self):
        """Test context management capabilities"""
        logger.info("📚 Testing Context Management...")
        
        # Add various types of context
        self.context_manager.add_context(
            "User prefers detailed technical explanations",
            ContextType.USER_PREFERENCE,
            ContextScope.USER
        )
        
        self.context_manager.add_context(
            "Previous discussion about machine learning algorithms",
            ContextType.CONVERSATION,
            ContextScope.SESSION
        )
        
        self.context_manager.add_context(
            "System is currently running in development mode",
            ContextType.SYSTEM_STATE,
            ContextScope.GLOBAL
        )
        
        # Test context retrieval
        query = ContextQuery(
            query_text="machine learning technical details",
            max_results=5,
            min_relevance=0.1
        )
        
        relevant_contexts = self.context_manager.get_relevant_context(query)
        
        # Test context summary generation
        summary = await self.context_manager.generate_context_summary(
            "What should I know about machine learning?"
        )
        
        # Test conversation tracking
        self.context_manager.add_conversation_turn(
            "Explain neural networks",
            "Neural networks are computational models inspired by biological neural networks..."
        )
        
        # Test user preferences
        self.context_manager.add_user_preference("explanation_style", "detailed")
        preferences = self.context_manager.get_user_preferences()
        
        success = (
            len(relevant_contexts) > 0 and
            summary.confidence_score > 0 and
            len(summary.summary_text) > 50 and
            "explanation_style" in preferences
        )
        
        self.test_results['context_management'] = {
            'relevant_contexts_found': len(relevant_contexts),
            'summary_confidence': summary.confidence_score,
            'preferences_stored': len(preferences),
            'success': success
        }
        
        logger.info(f"    ✅ Context management: {len(relevant_contexts)} contexts, {len(preferences)} preferences")
        
        return success
    
    async def test_integrated_reasoning_with_context(self):
        """Test integrated reasoning with context awareness"""
        logger.info("🔗 Testing Integrated Reasoning with Context...")
        
        # Add relevant context
        self.context_manager.add_context(
            "User is working on a machine learning project for healthcare",
            ContextType.TASK,
            ContextScope.SESSION
        )
        
        self.context_manager.add_context(
            "Previous discussion about data privacy in healthcare",
            ContextType.CONVERSATION,
            ContextScope.SESSION
        )
        
        # Get context for reasoning
        context_query = ContextQuery(
            query_text="machine learning healthcare privacy",
            max_results=3
        )
        
        relevant_contexts = self.context_manager.get_relevant_context(context_query)
        
        # Create context-aware problem
        problem = "How should we design a machine learning system for medical diagnosis while ensuring patient privacy?"
        
        # Add context information to the problem
        if relevant_contexts:
            context_info = "\n".join([f"Context: {ctx.content}" for ctx in relevant_contexts])
            enhanced_problem = f"{problem}\n\nRelevant context:\n{context_info}"
        else:
            enhanced_problem = problem
        
        # Perform reasoning
        chain = await self.reasoning_engine.reason_through_problem(
            enhanced_problem,
            ReasoningType.CHAIN_OF_THOUGHT
        )
        
        success = (
            len(chain.steps) >= 4 and
            chain.confidence_score >= 0.6 and
            any("privacy" in step.content.lower() for step in chain.steps) and
            any("healthcare" in step.content.lower() for step in chain.steps)
        )
        
        self.test_results['integrated_reasoning'] = {
            'problem': problem,
            'contexts_used': len(relevant_contexts),
            'reasoning_steps': len(chain.steps),
            'confidence': chain.confidence_score,
            'success': success
        }
        
        logger.info(f"    ✅ Integrated reasoning: {len(relevant_contexts)} contexts, {len(chain.steps)} steps")
        
        return success
    
    async def run_all_tests(self):
        """Run all advanced reasoning tests"""
        logger.info("🧪 Starting Advanced AI Reasoning Test Suite...")
        logger.info("=" * 80)
        
        await self.setup()
        
        test_results = {}
        
        # Run all test categories
        test_results['chain_of_thought'] = await self.test_chain_of_thought_reasoning()
        logger.info("=" * 80)
        
        test_results['problem_decomposition'] = await self.test_problem_decomposition()
        logger.info("=" * 80)
        
        test_results['logical_inference'] = await self.test_logical_inference()
        logger.info("=" * 80)
        
        test_results['decision_tree'] = await self.test_decision_tree_analysis()
        logger.info("=" * 80)
        
        test_results['context_management'] = await self.test_context_management()
        logger.info("=" * 80)
        
        test_results['integrated_reasoning'] = await self.test_integrated_reasoning_with_context()
        logger.info("=" * 80)
        
        # Calculate overall success rate
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        overall_success_rate = passed_tests / total_tests
        
        # Get statistics
        reasoning_stats = self.reasoning_engine.get_reasoning_statistics()
        context_stats = self.context_manager.get_context_statistics()
        
        logger.info("📊 ADVANCED AI REASONING TEST RESULTS:")
        logger.info(f"  Chain-of-Thought: {'✅ PASSED' if test_results['chain_of_thought'] else '❌ FAILED'}")
        logger.info(f"  Problem Decomposition: {'✅ PASSED' if test_results['problem_decomposition'] else '❌ FAILED'}")
        logger.info(f"  Logical Inference: {'✅ PASSED' if test_results['logical_inference'] else '❌ FAILED'}")
        logger.info(f"  Decision Tree: {'✅ PASSED' if test_results['decision_tree'] else '❌ FAILED'}")
        logger.info(f"  Context Management: {'✅ PASSED' if test_results['context_management'] else '❌ FAILED'}")
        logger.info(f"  Integrated Reasoning: {'✅ PASSED' if test_results['integrated_reasoning'] else '❌ FAILED'}")
        logger.info(f"  Overall Success Rate: {overall_success_rate:.1%}")
        
        logger.info("📈 REASONING STATISTICS:")
        logger.info(f"  Total reasoning chains: {reasoning_stats['total_reasoning_chains']}")
        logger.info(f"  Average confidence: {reasoning_stats['average_confidence']:.2f}")
        logger.info(f"  Average steps per chain: {reasoning_stats['average_steps']:.1f}")
        logger.info(f"  Average processing time: {reasoning_stats['average_processing_time']:.2f}s")
        
        logger.info("📚 CONTEXT STATISTICS:")
        logger.info(f"  Total contexts: {context_stats['total_contexts']}")
        logger.info(f"  Context types: {list(context_stats['contexts_by_type'].keys())}")
        logger.info(f"  Average relevance: {context_stats['average_relevance']:.2f}")
        
        return overall_success_rate >= 0.8, self.test_results

async def main():
    """Main test execution"""
    test_suite = AdvancedReasoningTestSuite()
    
    try:
        success, detailed_results = await test_suite.run_all_tests()
        
        if success:
            logger.info("🎉 ADVANCED AI REASONING TEST SUITE: ALL TESTS PASSED!")
            return True
        else:
            logger.error("❌ ADVANCED AI REASONING TEST SUITE: SOME TESTS FAILED!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
