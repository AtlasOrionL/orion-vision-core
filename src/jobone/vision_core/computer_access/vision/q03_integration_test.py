#!/usr/bin/env python3
"""
🧪 Q03 Integration Test - End-to-End Test Suite
💖 DUYGULANDIK! SEN YAPARSIN! ENTEGRASYON TESTİ!

ORION TEST APPROACH:
- Task Decomposition → Contextual Understanding → Task Flow → Verification
- "not defterini aç ve 'wake up orion' yaz" test scenario
- Deli Adam yaklaşımı ile end-to-end test

Author: Orion Vision Core Team
Status: 🧪 INTEGRATION TEST ACTIVE
"""

import logging
import time
from typing import Dict, Any, List
from datetime import datetime

# Q03 imports
try:
    from q03_task_decomposition import DeliAdamTaskDecomposer
    from q03_contextual_understanding import DeliAdamContextualAnalyzer
    from q03_task_flow_manager import AutomaticTaskFlowManager
    from q03_action_verification import ActionSuccessVerifier
    print("✅ All Q03 modules imported for integration test")
except ImportError as e:
    print(f"❌ Q03 integration import error: {e}")
    exit(1)

class Q03IntegrationTester:
    """🧪 Q03 Entegrasyon Test Sistemi"""
    
    def __init__(self):
        self.logger = logging.getLogger('q03.integration_test')
        
        # Initialize all Q03 components
        self.task_decomposer = DeliAdamTaskDecomposer()
        self.contextual_analyzer = DeliAdamContextualAnalyzer()
        self.task_flow_manager = AutomaticTaskFlowManager()
        self.action_verifier = ActionSuccessVerifier()
        
        self.test_results = []
        self.initialized = False
        
        self.logger.info("🧪 Q03 Integration Tester initialized")
    
    def initialize_all_components(self) -> bool:
        """Initialize all Q03 components"""
        try:
            self.logger.info("🚀 Initializing all Q03 components...")
            
            # Initialize each component
            components = [
                ("Task Decomposer", self.task_decomposer),
                ("Contextual Analyzer", self.contextual_analyzer),
                ("Task Flow Manager", self.task_flow_manager),
                ("Action Verifier", self.action_verifier)
            ]
            
            for name, component in components:
                if not component.initialize():
                    self.logger.error(f"❌ {name} initialization failed")
                    return False
                self.logger.info(f"✅ {name} initialized")
            
            self.initialized = True
            self.logger.info("✅ All Q03 components initialized successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Component initialization error: {e}")
            return False
    
    def run_end_to_end_test(self, test_command: str) -> Dict[str, Any]:
        """🧪 End-to-end entegrasyon testi"""
        try:
            if not self.initialized:
                return {'success': False, 'error': 'Components not initialized'}
            
            self.logger.info(f"🧪 Starting end-to-end test: '{test_command}'")
            test_start = datetime.now()
            
            # Step 1: Task Decomposition
            self.logger.info("🔥 Step 1: Task Decomposition")
            task_queue = self.task_decomposer.nehire_atla_decompose(test_command)
            if not task_queue:
                return {'success': False, 'error': 'Task decomposition failed'}
            
            decomposition_result = {
                'queue_id': task_queue.queue_id,
                'steps': len(task_queue.task_steps),
                'complexity': task_queue.total_complexity.value,
                'duration': task_queue.estimated_total_duration
            }
            self.logger.info(f"✅ Decomposition: {decomposition_result['steps']} steps")
            
            # Step 2: Contextual Understanding
            self.logger.info("🔍 Step 2: Contextual Understanding")
            screen_context = self.contextual_analyzer.ekrana_atla_analyze_context()
            if not screen_context:
                return {'success': False, 'error': 'Contextual analysis failed'}
            
            context_result = {
                'context_id': screen_context.context_id,
                'context_type': screen_context.context_type.value,
                'confidence': screen_context.context_confidence,
                'effective_mass': screen_context.higgs_mass_distribution.get('final_mass', 0)
            }
            self.logger.info(f"✅ Context: {context_result['context_type']} ({context_result['confidence']:.2f})")
            
            # Step 3: Task Flow Execution
            self.logger.info("🔄 Step 3: Task Flow Execution")
            flow_result = self.task_flow_manager.run_task_flow(task_queue, screen_context)
            if not flow_result['success']:
                return {'success': False, 'error': 'Task flow execution failed'}
            
            self.logger.info(f"✅ Flow: {flow_result['successful_steps']}/{flow_result['executions']} steps")
            
            # Step 4: Verification Summary
            self.logger.info("✅ Step 4: Verification Summary")
            verification_summary = self._summarize_verifications()
            
            # Calculate overall test result
            test_end = datetime.now()
            test_duration = (test_end - test_start).total_seconds()
            
            overall_result = {
                'success': True,
                'test_command': test_command,
                'test_duration': test_duration,
                'decomposition': decomposition_result,
                'context': context_result,
                'flow': flow_result,
                'verification': verification_summary,
                'overall_score': self._calculate_overall_score(
                    decomposition_result, context_result, flow_result, verification_summary
                ),
                'timestamp': test_end.isoformat()
            }
            
            self.test_results.append(overall_result)
            self.logger.info(f"🎉 End-to-end test completed! Score: {overall_result['overall_score']:.2f}")
            
            return overall_result
            
        except Exception as e:
            self.logger.error(f"❌ End-to-end test error: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_multiple_test_scenarios(self) -> Dict[str, Any]:
        """🧪 Çoklu test senaryoları"""
        test_scenarios = [
            "not defterini aç ve 'wake up orion' yaz",
            "tarayıcıyı aç ve google'a git",
            "WAKE UP ORION! Test command"
        ]
        
        self.logger.info(f"🧪 Running {len(test_scenarios)} test scenarios...")
        
        scenario_results = []
        for i, scenario in enumerate(test_scenarios, 1):
            self.logger.info(f"🧪 Test Scenario {i}/{len(test_scenarios)}: {scenario}")
            
            result = self.run_end_to_end_test(scenario)
            scenario_results.append(result)
            
            # Short delay between tests
            time.sleep(0.5)
        
        # Calculate summary statistics
        successful_tests = sum(1 for r in scenario_results if r.get('success', False))
        total_tests = len(scenario_results)
        average_score = sum(r.get('overall_score', 0) for r in scenario_results) / total_tests
        
        summary = {
            'total_scenarios': total_tests,
            'successful_scenarios': successful_tests,
            'success_rate': successful_tests / total_tests,
            'average_score': average_score,
            'scenario_results': scenario_results,
            'test_grade': self._calculate_test_grade(successful_tests, total_tests, average_score)
        }
        
        self.logger.info(f"🎉 Multiple scenarios completed: {successful_tests}/{total_tests} success")
        return summary
    
    def _summarize_verifications(self) -> Dict[str, Any]:
        """Verification summary"""
        verifier_status = self.action_verifier.get_verifier_status()
        stats = verifier_status['statistics']
        
        return {
            'total_verifications': stats['total_verifications'],
            'successful_verifications': stats['successful_verifications'],
            'success_rate': stats['successful_verifications'] / max(stats['total_verifications'], 1),
            'average_confidence': stats['average_confidence']
        }
    
    def _calculate_overall_score(self, decomposition: Dict, context: Dict, 
                               flow: Dict, verification: Dict) -> float:
        """Calculate overall test score"""
        # Decomposition score (25%)
        decomp_score = 1.0 if decomposition['steps'] > 0 else 0.0
        
        # Context score (25%)
        context_score = context['confidence']
        
        # Flow score (30%)
        flow_score = flow['successful_steps'] / max(flow['executions'], 1)
        
        # Verification score (20%)
        verif_score = verification['success_rate']
        
        overall = (decomp_score * 0.25 + context_score * 0.25 + 
                  flow_score * 0.30 + verif_score * 0.20)
        
        return overall
    
    def _calculate_test_grade(self, successful: int, total: int, avg_score: float) -> str:
        """Calculate test grade"""
        success_rate = successful / total
        
        if success_rate >= 0.9 and avg_score >= 0.8:
            return "A+ (Excellent)"
        elif success_rate >= 0.8 and avg_score >= 0.7:
            return "A (Very Good)"
        elif success_rate >= 0.7 and avg_score >= 0.6:
            return "B+ (Good)"
        elif success_rate >= 0.6 and avg_score >= 0.5:
            return "B (Satisfactory)"
        else:
            return "C (Needs Improvement)"
    
    def get_test_status(self) -> Dict[str, Any]:
        """Get test status"""
        return {
            'initialized': self.initialized,
            'tests_completed': len(self.test_results),
            'components_status': {
                'task_decomposer': self.task_decomposer.get_decomposer_status(),
                'contextual_analyzer': self.contextual_analyzer.get_contextual_status(),
                'task_flow_manager': self.task_flow_manager.get_flow_status(),
                'action_verifier': self.action_verifier.get_verifier_status()
            }
        }

# Main test execution
if __name__ == "__main__":
    print("🧪 Q03 Integration Test Suite")
    print("💖 DUYGULANDIK! SEN YAPARSIN! ENTEGRASYON TESTİ!")
    print("🌟 WAKE UP ORION! END-TO-END TEST ZAMANI!")
    print()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s:%(name)s:%(message)s'
    )
    
    # Create and initialize tester
    tester = Q03IntegrationTester()
    
    if tester.initialize_all_components():
        print("✅ All Q03 components initialized successfully!")
        print()
        
        # Run multiple test scenarios
        print("🧪 Running multiple test scenarios...")
        summary = tester.run_multiple_test_scenarios()
        
        print()
        print("🎉 Q03 INTEGRATION TEST RESULTS:")
        print(f"   📊 Total Scenarios: {summary['total_scenarios']}")
        print(f"   ✅ Successful: {summary['successful_scenarios']}")
        print(f"   📈 Success Rate: {summary['success_rate']:.1%}")
        print(f"   🎯 Average Score: {summary['average_score']:.2f}")
        print(f"   🏆 Test Grade: {summary['test_grade']}")
        
        # Show individual scenario results
        print()
        print("📋 Individual Scenario Results:")
        for i, result in enumerate(summary['scenario_results'], 1):
            if result.get('success'):
                print(f"   {i}. ✅ {result['test_command'][:30]}... (Score: {result['overall_score']:.2f})")
            else:
                print(f"   {i}. ❌ {result['test_command'][:30]}... (Failed)")
        
        # Show component status
        status = tester.get_test_status()
        print()
        print("📊 Component Status Summary:")
        for comp_name, comp_status in status['components_status'].items():
            if comp_status.get('initialized', False):
                print(f"   ✅ {comp_name}: Ready")
            else:
                print(f"   ❌ {comp_name}: Not Ready")
        
    else:
        print("❌ Q03 component initialization failed")
    
    print()
    print("🎉 Q03 Integration Test completed!")
    print("💖 DUYGULANDIK! ENTEGRASYON TESTİ TAMAMLANDI!")
    print("🎵 Müzik dinleme zamanı yaklaşıyor...")
