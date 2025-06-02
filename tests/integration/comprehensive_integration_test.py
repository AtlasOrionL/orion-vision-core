"""
Comprehensive Integration Test Suite for Orion Vision Core

This test suite validates the complete system integration including
all core modules working together in realistic scenarios.

Author: Atlas-orion (Augment Agent)
Date: 2 Haziran 2025
Purpose: Final system validation before 100% completion
"""

import sys
import os
import time
import asyncio
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import all core modules
from src.jobone.vision_core.agent.core.agent_manager import AgentManager, AgentState
from src.jobone.vision_core.ml.core.ml_manager import MLManager, ModelType, ModelStatus
from src.jobone.vision_core.tasks.core.task_base import TaskBase, TaskDefinition, TaskStatus
from src.jobone.vision_core.communication.core.base_protocol import BaseProtocol, ProtocolConfig, ProtocolType
from src.jobone.vision_core.agent.core.agent_logger import AgentLogger
from src.jobone.vision_core.production.readiness.production_readiness_manager import ProductionReadinessManager
from src.jobone.vision_core.production.validation.system_validator import SystemValidator
from src.jobone.vision_core.production.testing.comprehensive_tester import ComprehensiveTester


class IntegrationTestSuite:
    """Comprehensive integration test suite"""
    
    def __init__(self):
        """Initialize test suite"""
        self.logger = AgentLogger("integration_test")
        self.test_results = {}
        self.start_time = time.time()
        
        # Initialize core systems
        self.agent_manager = None
        self.ml_manager = None
        self.protocol = None
        self.production_manager = None
        self.system_validator = None
        self.comprehensive_tester = None
        
        print("🧪 COMPREHENSIVE INTEGRATION TEST SUITE")
        print("=" * 60)
    
    def setup_systems(self) -> bool:
        """Setup all core systems"""
        try:
            print("\n🔧 Setting up core systems...")
            
            # Initialize Agent Manager
            self.agent_manager = AgentManager(logger=self.logger)
            print("✅ AgentManager initialized")
            
            # Initialize ML Manager
            self.ml_manager = MLManager(logger=self.logger)
            print("✅ MLManager initialized")
            
            # Initialize Protocol
            config = ProtocolConfig(ProtocolType.HTTP, 'localhost', 8080)
            self.protocol = BaseProtocol(config, 'integration_test', self.logger)
            print("✅ BaseProtocol initialized")
            
            # Initialize Production Systems
            self.production_manager = ProductionReadinessManager(logger=self.logger)
            print("✅ ProductionReadinessManager initialized")
            
            self.system_validator = SystemValidator(logger=self.logger)
            print("✅ SystemValidator initialized")
            
            self.comprehensive_tester = ComprehensiveTester(logger=self.logger)
            print("✅ ComprehensiveTester initialized")
            
            print("🎉 All systems initialized successfully!")
            return True
            
        except Exception as e:
            print(f"❌ System setup failed: {str(e)}")
            return False
    
    def test_agent_ml_integration(self) -> bool:
        """Test Agent-ML integration"""
        try:
            print("\n🤖 Testing Agent-ML Integration...")
            
            # Create agents
            agent_ids = []
            for i in range(3):
                agent_id = self.agent_manager.create_agent(
                    f'ml_agent_{i}', 
                    'MLAgent', 
                    ['data_processing', 'model_training']
                )
                if agent_id:
                    agent_ids.append(agent_id)
            
            print(f"✅ Created {len(agent_ids)} ML agents")
            
            # Create ML models for each agent
            model_ids = []
            for i, agent_id in enumerate(agent_ids):
                model_id = self.ml_manager.create_model(
                    f'agent_{i}_model', 
                    ModelType.CLASSIFICATION,
                    {'agent_id': agent_id}
                )
                if model_id:
                    model_ids.append(model_id)
            
            print(f"✅ Created {len(model_ids)} ML models")
            
            # Start training for all models
            training_jobs = []
            for model_id in model_ids:
                job_id = self.ml_manager.start_training(
                    model_id, 
                    f'agent_data_{model_id[:8]}',
                    {'epochs': 2}
                )
                if job_id:
                    training_jobs.append(job_id)
            
            print(f"✅ Started {len(training_jobs)} training jobs")
            
            # Wait for training completion
            time.sleep(1)
            
            # Check training results
            completed_trainings = 0
            for job_id in training_jobs:
                job = self.ml_manager.get_training_job(job_id)
                if job and job.status == 'completed':
                    completed_trainings += 1
            
            print(f"✅ Completed {completed_trainings}/{len(training_jobs)} training jobs")
            
            # Test predictions
            predictions_made = 0
            for model_id in model_ids:
                prediction = self.ml_manager.predict(model_id, 'test_data')
                if prediction:
                    predictions_made += 1
            
            print(f"✅ Made {predictions_made}/{len(model_ids)} predictions")
            
            success = (len(agent_ids) >= 3 and len(model_ids) >= 3 and 
                      completed_trainings >= 2 and predictions_made >= 2)
            
            self.test_results['agent_ml_integration'] = {
                'success': success,
                'agents_created': len(agent_ids),
                'models_created': len(model_ids),
                'trainings_completed': completed_trainings,
                'predictions_made': predictions_made
            }
            
            return success
            
        except Exception as e:
            print(f"❌ Agent-ML integration test failed: {str(e)}")
            self.test_results['agent_ml_integration'] = {'success': False, 'error': str(e)}
            return False
    
    def test_task_workflow_integration(self) -> bool:
        """Test Task-Workflow integration"""
        try:
            print("\n📋 Testing Task-Workflow Integration...")
            
            # Create workflow tasks
            tasks = []
            task_definitions = [
                ('data_collection', 'collect'),
                ('data_processing', 'process'),
                ('model_training', 'train'),
                ('model_evaluation', 'evaluate'),
                ('deployment', 'deploy')
            ]
            
            for task_name, task_type in task_definitions:
                task_def = TaskDefinition(task_name=task_name, task_type=task_type)
                task = TaskBase(task_def)
                tasks.append(task)
            
            print(f"✅ Created {len(tasks)} workflow tasks")
            
            # Execute tasks in sequence
            completed_tasks = 0
            failed_tasks = 0
            
            for i, task in enumerate(tasks):
                print(f"  Executing task {i+1}: {task.definition.task_name}")
                if task.execute():
                    completed_tasks += 1
                    print(f"    ✅ Task completed in {task.get_execution_time():.4f}s")
                else:
                    failed_tasks += 1
                    print(f"    ❌ Task failed: {task.get_error()}")
            
            print(f"✅ Workflow completed: {completed_tasks}/{len(tasks)} tasks successful")
            
            # Test task serialization
            serialized_tasks = 0
            for task in tasks:
                try:
                    task_dict = task.to_dict()
                    if isinstance(task_dict, dict) and 'definition' in task_dict:
                        serialized_tasks += 1
                except:
                    pass
            
            print(f"✅ Serialized {serialized_tasks}/{len(tasks)} tasks")
            
            success = (completed_tasks >= 4 and failed_tasks == 0 and serialized_tasks >= 4)
            
            self.test_results['task_workflow_integration'] = {
                'success': success,
                'total_tasks': len(tasks),
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'serialized_tasks': serialized_tasks
            }
            
            return success
            
        except Exception as e:
            print(f"❌ Task-Workflow integration test failed: {str(e)}")
            self.test_results['task_workflow_integration'] = {'success': False, 'error': str(e)}
            return False
    
    def test_production_systems_integration(self) -> bool:
        """Test Production Systems integration"""
        try:
            print("\n🏭 Testing Production Systems Integration...")
            
            # Test Production Readiness Assessment
            assessment = self.production_manager.assess_readiness()
            print(f"✅ Production readiness assessed: {assessment.readiness_level.value}")
            
            # Test System Validation
            validation_suites = self.system_validator.list_suites()
            print(f"✅ System validator has {len(validation_suites)} validation suites")
            
            # Run a validation suite
            if validation_suites:
                suite_id = validation_suites[0]['suite_id']
                run_id = self.system_validator.run_validation(suite_id)
                if run_id:
                    print(f"✅ Validation run started: {run_id[:8]}...")
                    
                    # Wait for validation
                    time.sleep(2)
                    
                    # Check results
                    run_status = self.system_validator.get_run_status(run_id)
                    if run_status:
                        print(f"✅ Validation completed: {run_status['success_rate']:.1f}% success rate")
            
            # Test Comprehensive Tester
            test_suites = self.comprehensive_tester.list_suites()
            print(f"✅ Comprehensive tester has {len(test_suites)} test suites")
            
            # Run a test suite
            if test_suites:
                suite_id = test_suites[0]['suite_id']
                test_result = self.comprehensive_tester.run_suite(suite_id)
                if test_result:
                    print("✅ Test suite executed successfully")
                    
                    # Get results
                    results = self.comprehensive_tester.get_suite_results(suite_id)
                    if results:
                        print(f"✅ Test results: {results['pass_rate']:.1f}% pass rate")
            
            success = (assessment is not None and len(validation_suites) > 0 and len(test_suites) > 0)
            
            self.test_results['production_systems_integration'] = {
                'success': success,
                'readiness_level': assessment.readiness_level.value if assessment else 'unknown',
                'validation_suites': len(validation_suites),
                'test_suites': len(test_suites)
            }
            
            return success
            
        except Exception as e:
            print(f"❌ Production systems integration test failed: {str(e)}")
            self.test_results['production_systems_integration'] = {'success': False, 'error': str(e)}
            return False
    
    def test_cross_system_communication(self) -> bool:
        """Test cross-system communication"""
        try:
            print("\n📡 Testing Cross-System Communication...")
            
            # Test protocol statistics
            protocol_stats = self.protocol.get_stats()
            print(f"✅ Protocol stats available: {len(protocol_stats)} metrics")
            
            # Test agent-protocol integration
            agents = self.agent_manager.list_agents()
            print(f"✅ Found {len(agents)} active agents")
            
            # Test ML-agent communication
            models = self.ml_manager.list_models()
            print(f"✅ Found {len(models)} ML models")
            
            # Test statistics aggregation
            agent_stats = self.agent_manager.get_stats()
            ml_stats = self.ml_manager.get_stats()
            
            total_agents = agent_stats['stats']['current_active']
            total_models = ml_stats['current_models']
            
            print(f"✅ System statistics: {total_agents} agents, {total_models} models")
            
            success = (len(protocol_stats) > 0 and total_agents > 0 and total_models > 0)
            
            self.test_results['cross_system_communication'] = {
                'success': success,
                'protocol_metrics': len(protocol_stats),
                'active_agents': total_agents,
                'active_models': total_models
            }
            
            return success
            
        except Exception as e:
            print(f"❌ Cross-system communication test failed: {str(e)}")
            self.test_results['cross_system_communication'] = {'success': False, 'error': str(e)}
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        try:
            # Setup systems
            if not self.setup_systems():
                return {'success': False, 'error': 'System setup failed'}
            
            # Run all test categories
            tests = [
                ('Agent-ML Integration', self.test_agent_ml_integration),
                ('Task-Workflow Integration', self.test_task_workflow_integration),
                ('Production Systems Integration', self.test_production_systems_integration),
                ('Cross-System Communication', self.test_cross_system_communication)
            ]
            
            passed_tests = 0
            total_tests = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n🧪 Running {test_name}...")
                if test_func():
                    passed_tests += 1
                    print(f"✅ {test_name}: PASSED")
                else:
                    print(f"❌ {test_name}: FAILED")
            
            # Calculate overall results
            success_rate = (passed_tests / total_tests) * 100
            execution_time = time.time() - self.start_time
            
            overall_result = {
                'success': passed_tests == total_tests,
                'passed_tests': passed_tests,
                'total_tests': total_tests,
                'success_rate': success_rate,
                'execution_time_seconds': execution_time,
                'test_results': self.test_results
            }
            
            # Print final results
            print("\n" + "=" * 60)
            print("🎯 INTEGRATION TEST RESULTS")
            print("=" * 60)
            print(f"✅ Passed Tests: {passed_tests}/{total_tests}")
            print(f"📊 Success Rate: {success_rate:.1f}%")
            print(f"⏱️ Execution Time: {execution_time:.2f} seconds")
            
            if passed_tests == total_tests:
                print("\n🎉 ALL INTEGRATION TESTS PASSED!")
                print("🚀 SYSTEM IS FULLY INTEGRATED AND READY!")
            else:
                print(f"\n⚠️ {total_tests - passed_tests} tests failed")
                print("🔧 System needs attention before full deployment")
            
            return overall_result
            
        except Exception as e:
            print(f"❌ Integration test suite failed: {str(e)}")
            return {'success': False, 'error': str(e)}


def main():
    """Main test execution"""
    test_suite = IntegrationTestSuite()
    results = test_suite.run_all_tests()
    
    # Return exit code based on results
    return 0 if results.get('success', False) else 1


if __name__ == "__main__":
    exit(main())
